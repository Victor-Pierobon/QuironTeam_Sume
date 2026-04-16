from sqlalchemy import Integer, ForeignKey, Float, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PerfilAluno(Base):
    __tablename__ = "perfis_aluno"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), unique=True)

    # Média de cada feature nos textos de baseline (JSON: {nome: valor})
    medias: Mapped[dict] = mapped_column(JSON, default=dict)
    # Desvio padrão de cada feature (JSON: {nome: valor})
    desvios: Mapped[dict] = mapped_column(JSON, default=dict)
    # Inclinação da tendência por feature (JSON: {nome: valor})
    tendencias: Mapped[dict] = mapped_column(JSON, default=dict)

    total_baseline: Mapped[int] = mapped_column(Integer, default=0)

    aluno: Mapped["Aluno"] = relationship("Aluno", back_populates="perfil")
