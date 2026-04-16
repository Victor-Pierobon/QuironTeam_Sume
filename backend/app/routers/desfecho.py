from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dossie import Desfecho, StatusDesfecho
from app.models.trabalho import Trabalho

router = APIRouter()


class DesfechoCreate(BaseModel):
    status: str  # esclarecido | em_acompanhamento | conversa_realizada
    nota: str | None = None


@router.post("/{trabalho_id}")
async def registrar_desfecho(
    trabalho_id: int,
    data: DesfechoCreate,
    db: AsyncSession = Depends(get_db),
):
    trab = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    if not trab.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")

    try:
        status_enum = StatusDesfecho(data.status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Use: {[s.value for s in StatusDesfecho]}",
        )

    result = await db.execute(select(Desfecho).where(Desfecho.trabalho_id == trabalho_id))
    desfecho = result.scalar_one_or_none()

    if not desfecho:
        desfecho = Desfecho(trabalho_id=trabalho_id)
        db.add(desfecho)

    desfecho.status = status_enum
    desfecho.nota = data.nota
    await db.commit()

    return {"status": desfecho.status.value, "nota": desfecho.nota}


@router.get("/{trabalho_id}")
async def get_desfecho(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Desfecho).where(Desfecho.trabalho_id == trabalho_id))
    desfecho = result.scalar_one_or_none()
    if not desfecho:
        raise HTTPException(status_code=404, detail="Nenhum desfecho registrado.")
    return {
        "status": desfecho.status.value,
        "nota": desfecho.nota,
        "registrado_em": desfecho.registrado_em,
    }
