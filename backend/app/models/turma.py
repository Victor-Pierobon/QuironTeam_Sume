from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Turma(Base):
    __tablename__ = "turmas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    disciplina: Mapped[str] = mapped_column(String(100))
    ano_serie: Mapped[str] = mapped_column(String(20))

    alunos: Mapped[list["Aluno"]] = relationship("Aluno", back_populates="turma", cascade="all, delete-orphan")
