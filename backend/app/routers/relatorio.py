import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.aluno import Aluno
from app.models.dossie import Dossie
from app.models.perfil import PerfilAluno
from app.models.trabalho import Fonte, ParagrafoDestacado, Trabalho, TrabalhoFeature
from app.services.features import FEATURE_NAMES, FEATURE_LABELS
from app.services.perfil import analisar_desvios
from app.services.relatorio import gerar_relatorio

router = APIRouter()


@router.post("/{trabalho_id}")
async def gerar(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    # Trabalho
    trab_result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = trab_result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")

    # Aluno
    aluno_result = await db.execute(select(Aluno).where(Aluno.id == trabalho.aluno_id))
    aluno = aluno_result.scalar_one_or_none()

    # Perfil
    perfil_result = await db.execute(
        select(PerfilAluno).where(PerfilAluno.aluno_id == trabalho.aluno_id)
    )
    perfil = perfil_result.scalar_one_or_none()
    if not perfil or perfil.total_baseline == 0:
        raise HTTPException(
            status_code=400,
            detail="Sem baseline suficiente. Analise o trabalho primeiro.",
        )

    # Features do trabalho
    feat_result = await db.execute(
        select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trabalho_id)
    )
    features = {f.nome: f.valor for f in feat_result.scalars().all()}
    if not features:
        raise HTTPException(
            status_code=400,
            detail="Features não encontradas. Execute POST /analise/{id} primeiro.",
        )

    # Desvios
    desvios = analisar_desvios(features, perfil)

    # Parágrafos destacados
    para_result = await db.execute(
        select(ParagrafoDestacado).where(ParagrafoDestacado.trabalho_id == trabalho_id)
    )
    paragrafos = [
        {
            "indice": p.indice,
            "features_destoantes": json.loads(p.features_destoantes),
        }
        for p in para_result.scalars().all()
    ]

    # Fontes
    fonte_result = await db.execute(
        select(Fonte).where(Fonte.trabalho_id == trabalho_id)
    )
    fontes = [
        {
            "texto_original": f.texto_original,
            "status": f.status.value,
            "justificativa": f.justificativa,
        }
        for f in fonte_result.scalars().all()
    ]

    # Gera relatório via Groq
    resultado = gerar_relatorio(
        aluno_nome=aluno.nome if aluno else "Aluno",
        titulo=trabalho.titulo,
        n_baseline=perfil.total_baseline,
        desvios=desvios,
        paragrafos=paragrafos,
        fontes=fontes,
    )

    # Salva no dossiê
    dossie_result = await db.execute(select(Dossie).where(Dossie.trabalho_id == trabalho_id))
    dossie = dossie_result.scalar_one_or_none()
    if not dossie:
        dossie = Dossie(trabalho_id=trabalho_id)
        db.add(dossie)

    dossie.observacoes_professor = resultado.get("observacoes")
    dossie.perguntas_socraticas = json.dumps(
        resultado.get("perguntas_socraticas", []), ensure_ascii=False
    )
    dossie.roteiro_conversa = resultado.get("roteiro_conversa")

    await db.commit()
    return resultado


@router.get("/{trabalho_id}")
async def get_relatorio(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    dossie_result = await db.execute(select(Dossie).where(Dossie.trabalho_id == trabalho_id))
    dossie = dossie_result.scalar_one_or_none()

    if not dossie or not dossie.observacoes_professor:
        raise HTTPException(
            status_code=404,
            detail="Relatório não gerado. Execute POST /relatorio/{id} primeiro.",
        )

    perguntas = []
    if dossie.perguntas_socraticas:
        try:
            perguntas = json.loads(dossie.perguntas_socraticas)
        except Exception:
            perguntas = [dossie.perguntas_socraticas]

    return {
        "observacoes": dossie.observacoes_professor,
        "perguntas_socraticas": perguntas,
        "roteiro_conversa": dossie.roteiro_conversa,
    }
