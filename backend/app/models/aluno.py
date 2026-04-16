from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150))
    matricula: Mapped[str | None] = mapped_column(String(50), nullable=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("turmas.id"))

    turma: Mapped["Turma"] = relationship("Turma", back_populates="alunos")
    trabalhos: Mapped[list["Trabalho"]] = relationship("Trabalho", back_populates="aluno", cascade="all, delete-orphan")
    perfil: Mapped["PerfilAluno | None"] = relationship("PerfilAluno", back_populates="aluno", uselist=False, cascade="all, delete-orphan")
