from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dossie import Dossie
from app.models.trabalho import Fonte, StatusFonte, Trabalho
from app.services.fontes import validar_todas

router = APIRouter()


@router.post("/{trabalho_id}")
async def validar_fontes(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")

    # Valida todas as fontes do texto (chamadas externas feitas aqui)
    fontes_validadas = await validar_todas(trabalho.texto)

    # Remove fontes anteriores e salva as novas
    await db.execute(delete(Fonte).where(Fonte.trabalho_id == trabalho_id))
    for f in fontes_validadas:
        db.add(Fonte(
            trabalho_id=trabalho_id,
            texto_original=f["texto_original"][:500],
            url=f.get("url"),
            doi=f.get("doi"),
            status=StatusFonte(f["status"]),
            justificativa=f.get("justificativa"),
        ))

    # Atualiza contadores no dossiê
    total = len(fontes_validadas)
    verificadas = sum(1 for f in fontes_validadas if f["status"] in ("verde", "amarelo"))

    dossie_result = await db.execute(select(Dossie).where(Dossie.trabalho_id == trabalho_id))
    dossie = dossie_result.scalar_one_or_none()
    if not dossie:
        dossie = Dossie(trabalho_id=trabalho_id)
        db.add(dossie)

    dossie.fontes_total = total
    dossie.fontes_verificadas = verificadas

    await db.commit()

    return {
        "total": total,
        "verificadas": verificadas,
        "fontes": fontes_validadas,
    }


@router.get("/{trabalho_id}")
async def get_fontes(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    # Verifica se o dossiê existe (indica que validação já foi executada)
    dossie_result = await db.execute(select(Dossie).where(Dossie.trabalho_id == trabalho_id))
    dossie = dossie_result.scalar_one_or_none()
    if not dossie or dossie.fontes_total is None:
        raise HTTPException(status_code=404, detail="Fontes ainda não validadas.")

    result = await db.execute(select(Fonte).where(Fonte.trabalho_id == trabalho_id))
    fontes = result.scalars().all()

    return {
        "validado": True,
        "fontes": [
            {
                "id": f.id,
                "texto_original": f.texto_original,
                "url": f.url,
                "doi": f.doi,
                "status": f.status.value,
                "justificativa": f.justificativa,
            }
            for f in fontes
        ],
    }
