import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dossie import Dossie
from app.models.perfil import PerfilAluno
from app.models.trabalho import ParagrafoDestacado, Trabalho, TrabalhoFeature
from app.services.features import extrair_features
from app.services.perfil import (
    analisar_desvios,
    analisar_intra_documento,
    classificar_status_aluno,
    recalcular_perfil,
)

router = APIRouter()


@router.post("/{trabalho_id}")
async def analisar_trabalho(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")

    # 1. Extrair e salvar features
    features = extrair_features(trabalho.texto)
    await db.execute(
        delete(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trabalho_id)
    )
    for nome, valor in features.items():
        db.add(TrabalhoFeature(trabalho_id=trabalho_id, nome=nome, valor=valor))
    await db.flush()

    # 2. Buscar perfil do aluno
    perfil_result = await db.execute(
        select(PerfilAluno).where(PerfilAluno.aluno_id == trabalho.aluno_id)
    )
    perfil = perfil_result.scalar_one_or_none()

    if not perfil or perfil.total_baseline == 0:
        await db.commit()
        return {
            "status": "features_extraidas",
            "aviso": "Sem baseline suficiente para análise de desvios.",
            "features": features,
        }

    # 3. Análise de desvios contra o perfil
    desvios = analisar_desvios(features, perfil)
    normais = sum(1 for d in desvios if d["status"] == "normal")
    n_atencao = sum(1 for d in desvios if d["status"] == "atencao")
    n_destaque = sum(1 for d in desvios if d["status"] == "destaque")

    # 4. Análise intra-documento
    paragrafos_destacados = analisar_intra_documento(trabalho.texto)
    await db.execute(
        delete(ParagrafoDestacado).where(ParagrafoDestacado.trabalho_id == trabalho_id)
    )
    for para in paragrafos_destacados:
        db.add(
            ParagrafoDestacado(
                trabalho_id=trabalho_id,
                indice=para["indice"],
                texto=para["texto_resumo"],
                features_destoantes=json.dumps(
                    para["features_destoantes"], ensure_ascii=False
                ),
            )
        )

    # 5. Salvar / atualizar dossiê
    dossie_result = await db.execute(
        select(Dossie).where(Dossie.trabalho_id == trabalho_id)
    )
    dossie = dossie_result.scalar_one_or_none()
    if not dossie:
        dossie = Dossie(trabalho_id=trabalho_id)
        db.add(dossie)

    dossie.normais = normais
    dossie.atencao = n_atencao
    dossie.destaque = n_destaque

    await db.commit()

    return {
        "status": "ok",
        "normais": normais,
        "atencao": n_atencao,
        "destaque": n_destaque,
        "status_aluno": classificar_status_aluno(desvios),
        "desvios": desvios,
        "paragrafos_destacados": paragrafos_destacados,
    }


@router.get("/{trabalho_id}")
async def get_analise(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    dossie_result = await db.execute(
        select(Dossie).where(Dossie.trabalho_id == trabalho_id)
    )
    dossie = dossie_result.scalar_one_or_none()
    if not dossie:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada. Execute POST /analise/{id} primeiro.",
        )

    trabalho_result = await db.execute(
        select(Trabalho).where(Trabalho.id == trabalho_id)
    )
    trabalho = trabalho_result.scalar_one_or_none()

    features_result = await db.execute(
        select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trabalho_id)
    )
    features = {f.nome: f.valor for f in features_result.scalars().all()}

    perfil_result = await db.execute(
        select(PerfilAluno).where(PerfilAluno.aluno_id == trabalho.aluno_id)
    )
    perfil = perfil_result.scalar_one_or_none()

    desvios = (
        analisar_desvios(features, perfil)
        if perfil and perfil.total_baseline > 0
        else []
    )

    para_result = await db.execute(
        select(ParagrafoDestacado).where(ParagrafoDestacado.trabalho_id == trabalho_id)
    )
    paragrafos_out = [
        {
            "indice": p.indice,
            "texto_resumo": p.texto,
            "features_destoantes": json.loads(p.features_destoantes),
        }
        for p in para_result.scalars().all()
    ]

    return {
        "normais": dossie.normais,
        "atencao": dossie.atencao,
        "destaque": dossie.destaque,
        "fontes_verificadas": dossie.fontes_verificadas,
        "fontes_total": dossie.fontes_total,
        "status_aluno": classificar_status_aluno(desvios),
        "desvios": desvios,
        "paragrafos_destacados": paragrafos_out,
    }
