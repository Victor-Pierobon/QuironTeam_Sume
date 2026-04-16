from sqlalchemy import Integer, ForeignKey, Text, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class StatusDesfecho(str, enum.Enum):
    pendente = "pendente"
    esclarecido = "esclarecido"
    em_acompanhamento = "em_acompanhamento"
    conversa_realizada = "conversa_realizada"


class Dossie(Base):
    __tablename__ = "dossies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"), unique=True)

    # Contadores
    normais: Mapped[int] = mapped_column(Integer, default=0)
    atencao: Mapped[int] = mapped_column(Integer, default=0)
    destaque: Mapped[int] = mapped_column(Integer, default=0)
    fontes_verificadas: Mapped[int] = mapped_column(Integer, default=0)
    fontes_total: Mapped[int] = mapped_column(Integer, default=0)

    # Conteúdo gerado pela LLM
    observacoes_professor: Mapped[str | None] = mapped_column(Text, nullable=True)
    perguntas_socraticas: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    roteiro_conversa: Mapped[str | None] = mapped_column(Text, nullable=True)

    criado_em: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    trabalho: Mapped["Trabalho"] = relationship("Trabalho", back_populates="dossie")


class Desfecho(Base):
    __tablename__ = "desfechos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"), unique=True)
    status: Mapped[StatusDesfecho] = mapped_column(Enum(StatusDesfecho), default=StatusDesfecho.pendente)
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_em: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    trabalho: Mapped["Trabalho"] = relationship("Trabalho", back_populates="desfecho")
