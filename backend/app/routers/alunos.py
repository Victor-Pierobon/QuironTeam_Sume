from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.aluno import Aluno
from app.models.trabalho import Trabalho
from app.schemas.aluno import AlunoCreate, AlunoOut

router = APIRouter()


@router.get("/turma/{turma_id}", response_model=list[AlunoOut])
async def listar_alunos_da_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aluno).where(Aluno.turma_id == turma_id))
    alunos = result.scalars().all()

    out = []
    for aluno in alunos:
        count = await db.execute(select(func.count()).where(Trabalho.aluno_id == aluno.id))
        out.append(AlunoOut(
            id=aluno.id,
            nome=aluno.nome,
            matricula=aluno.matricula,
            turma_id=aluno.turma_id,
            total_trabalhos=count.scalar(),
        ))
    return out


@router.get("/{aluno_id}", response_model=AlunoOut)
async def get_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aluno).where(Aluno.id == aluno_id))
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    count = await db.execute(select(func.count()).where(Trabalho.aluno_id == aluno_id))
    return AlunoOut(
        id=aluno.id,
        nome=aluno.nome,
        matricula=aluno.matricula,
        turma_id=aluno.turma_id,
        total_trabalhos=count.scalar(),
    )


@router.post("/", response_model=AlunoOut, status_code=201)
async def criar_aluno(data: AlunoCreate, db: AsyncSession = Depends(get_db)):
    aluno = Aluno(**data.model_dump())
    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)
    return AlunoOut(id=aluno.id, nome=aluno.nome, matricula=aluno.matricula, turma_id=aluno.turma_id, total_trabalhos=0)
