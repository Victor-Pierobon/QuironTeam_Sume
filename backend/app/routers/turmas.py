from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.schemas.turma import TurmaCreate, TurmaOut

router = APIRouter()


@router.get("/", response_model=list[TurmaOut])
async def listar_turmas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Turma))
    turmas = result.scalars().all()

    out = []
    for turma in turmas:
        count = await db.execute(
            select(func.count()).where(Aluno.turma_id == turma.id)
        )
        total = count.scalar()
        out.append(TurmaOut(
            id=turma.id,
            nome=turma.nome,
            disciplina=turma.disciplina,
            ano_serie=turma.ano_serie,
            total_alunos=total,
        ))
    return out


@router.get("/{turma_id}", response_model=TurmaOut)
async def get_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Turma).where(Turma.id == turma_id))
    turma = result.scalar_one_or_none()
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    count = await db.execute(select(func.count()).where(Aluno.turma_id == turma_id))
    return TurmaOut(
        id=turma.id,
        nome=turma.nome,
        disciplina=turma.disciplina,
        ano_serie=turma.ano_serie,
        total_alunos=count.scalar(),
    )


@router.post("/", response_model=TurmaOut, status_code=201)
async def criar_turma(data: TurmaCreate, db: AsyncSession = Depends(get_db)):
    turma = Turma(**data.model_dump())
    db.add(turma)
    await db.commit()
    await db.refresh(turma)
    return TurmaOut(id=turma.id, nome=turma.nome, disciplina=turma.disciplina, ano_serie=turma.ano_serie, total_alunos=0)
