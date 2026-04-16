from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.aluno import Aluno
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.models.dossie import Dossie
from app.schemas.aluno import AlunoCreate, AlunoOut
from app.services.features import FEATURE_LABELS

router = APIRouter()


async def _status_aluno(aluno_id: int, db: AsyncSession) -> str:
    """Return worst status across all non-baseline dossies for this student."""
    result = await db.execute(
        select(Dossie)
        .join(Trabalho, Trabalho.id == Dossie.trabalho_id)
        .where(Trabalho.aluno_id == aluno_id, Trabalho.baseline == False)
    )
    dossies = result.scalars().all()
    if any(d.destaque > 0 for d in dossies):
        return "destaque"
    if any(d.atencao > 0 for d in dossies):
        return "atencao"
    return "ok"


@router.get("/turma/{turma_id}", response_model=list[AlunoOut])
async def listar_alunos_da_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aluno).where(Aluno.turma_id == turma_id))
    alunos = result.scalars().all()

    out = []
    for aluno in alunos:
        count = await db.execute(select(func.count()).where(Trabalho.aluno_id == aluno.id))
        status = await _status_aluno(aluno.id, db)
        out.append(AlunoOut(
            id=aluno.id,
            nome=aluno.nome,
            matricula=aluno.matricula,
            turma_id=aluno.turma_id,
            total_trabalhos=count.scalar(),
            status=status,
        ))
    return out


@router.get("/{aluno_id}", response_model=AlunoOut)
async def get_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aluno).where(Aluno.id == aluno_id))
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    count = await db.execute(select(func.count()).where(Trabalho.aluno_id == aluno_id))
    status = await _status_aluno(aluno_id, db)
    return AlunoOut(
        id=aluno.id,
        nome=aluno.nome,
        matricula=aluno.matricula,
        turma_id=aluno.turma_id,
        total_trabalhos=count.scalar(),
        status=status,
    )


@router.get("/{aluno_id}/trajetoria")
async def get_trajetoria(aluno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trabalho)
        .where(Trabalho.aluno_id == aluno_id)
        .order_by(Trabalho.data_entrega)
    )
    trabalhos = result.scalars().all()

    textos = []
    for trab in trabalhos:
        feat_result = await db.execute(
            select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trab.id)
        )
        features = {f.nome: round(f.valor, 3) for f in feat_result.scalars().all()}
        textos.append({
            "id": trab.id,
            "titulo": trab.titulo,
            "baseline": trab.baseline,
            "data_entrega": trab.data_entrega,
            "features": features,
        })

    feature_labels = FEATURE_LABELS
    return {"textos": textos, "feature_labels": feature_labels}


@router.post("/", response_model=AlunoOut, status_code=201)
async def criar_aluno(data: AlunoCreate, db: AsyncSession = Depends(get_db)):
    aluno = Aluno(**data.model_dump())
    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)
    return AlunoOut(id=aluno.id, nome=aluno.nome, matricula=aluno.matricula, turma_id=aluno.turma_id, total_trabalhos=0)
