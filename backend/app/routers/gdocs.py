"""
Histórico de edição via Google Docs.
Endpoints:
  POST /gdocs/{trabalho_id}  — importa histórico do Google Doc
  GET  /gdocs/{trabalho_id}  — retorna métricas e série temporal
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.gdocs import HistoricoVersao
from app.models.trabalho import Trabalho
from app.services.gdocs import buscar_historico_gdocs, detectar_padroes

router = APIRouter()


class GDocsImportRequest(BaseModel):
    doc_url: str


@router.post("/{trabalho_id}")
async def importar_gdocs(
    trabalho_id: int,
    body: GDocsImportRequest,
    db: AsyncSession = Depends(get_db),
):
    trab_r = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    if not trab_r.scalar_one_or_none():
        raise HTTPException(404, "Trabalho não encontrado")

    try:
        revisoes, metricas = await buscar_historico_gdocs(body.doc_url)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"Erro ao acessar o Google Docs: {e}")

    padroes = detectar_padroes(metricas)

    hist_r = await db.execute(select(HistoricoVersao).where(HistoricoVersao.trabalho_id == trabalho_id))
    hist = hist_r.scalar_one_or_none()
    if not hist:
        hist = HistoricoVersao(trabalho_id=trabalho_id)
        db.add(hist)

    hist.num_sessoes = metricas["num_sessoes"]
    hist.tempo_ativo_min = metricas["tempo_ativo_min"]
    hist.maior_insercao_pct = metricas["maior_insercao_pct"]
    hist.razao_edicao_adicao = metricas["razao_edicao_adicao"]
    hist.proporcao_final_colada = metricas["proporcao_final_colada"]
    hist.padroes_json = json.dumps(padroes, ensure_ascii=False)
    hist.revisoes_json = json.dumps(revisoes, ensure_ascii=False)

    await db.commit()

    return {
        "status": "ok",
        "metricas": metricas,
        "padroes": padroes,
        "total_revisoes": len(revisoes),
    }


@router.get("/{trabalho_id}")
async def get_gdocs(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    hist_r = await db.execute(select(HistoricoVersao).where(HistoricoVersao.trabalho_id == trabalho_id))
    hist = hist_r.scalar_one_or_none()
    if not hist:
        raise HTTPException(404, "Histórico de edição não encontrado. Execute POST /gdocs/{id} primeiro.")

    return {
        "num_sessoes": hist.num_sessoes,
        "tempo_ativo_min": hist.tempo_ativo_min,
        "maior_insercao_pct": hist.maior_insercao_pct,
        "razao_edicao_adicao": hist.razao_edicao_adicao,
        "proporcao_final_colada": hist.proporcao_final_colada,
        "padroes": json.loads(hist.padroes_json),
        "revisoes": json.loads(hist.revisoes_json),
        "importado_em": str(hist.importado_em),
    }
