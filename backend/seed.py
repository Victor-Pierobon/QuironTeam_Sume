"""
Script de seed para popular o banco com dados de demonstração.
Cria 1 turma com 6 alunos.

Uso:
    python seed.py
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sume:sume@localhost:5432/sume")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Import models so create_all knows about them
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.trabalho import Trabalho, TrabalhoFeature, Fonte, ParagrafoDestacado
from app.models.perfil import PerfilAluno
from app.models.dossie import Dossie, Desfecho
from app.database import Base


TURMA = {
    "nome": "8º Ano A",
    "disciplina": "Língua Portuguesa",
    "ano_serie": "8º Ano",
}

ALUNOS = [
    {"nome": "Ana Souza",       "matricula": "2024001"},
    {"nome": "Bruno Lima",      "matricula": "2024002"},
    {"nome": "Carla Mendes",    "matricula": "2024003"},
    {"nome": "Diego Ferreira",  "matricula": "2024004"},
    {"nome": "Elisa Ramos",     "matricula": "2024005"},
    {"nome": "Felipe Costa",    "matricula": "2024006"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Evita duplicar se já existir
        from sqlalchemy import select
        result = await db.execute(select(Turma).where(Turma.nome == TURMA["nome"]))
        if result.scalar_one_or_none():
            print("Seed já aplicado — turma já existe.")
            return

        turma = Turma(**TURMA)
        db.add(turma)
        await db.flush()

        for dados in ALUNOS:
            aluno = Aluno(**dados, turma_id=turma.id)
            db.add(aluno)

        await db.commit()
        print(f"✓ Turma '{TURMA['nome']}' criada com {len(ALUNOS)} alunos.")
        print("  Acesse http://localhost:3000 para ver.")


if __name__ == "__main__":
    asyncio.run(seed())
