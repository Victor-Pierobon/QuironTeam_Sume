from sqlalchemy import Integer, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class HistoricoVersao(Base):
    __tablename__ = "historico_versoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"), unique=True)

    num_sessoes: Mapped[int] = mapped_column(Integer, default=0)
    tempo_ativo_min: Mapped[float] = mapped_column(Float, default=0.0)
    maior_insercao_pct: Mapped[float] = mapped_column(Float, default=0.0)
    razao_edicao_adicao: Mapped[float] = mapped_column(Float, default=0.0)
    proporcao_final_colada: Mapped[float] = mapped_column(Float, default=0.0)

    padroes_json: Mapped[str] = mapped_column(Text, default="[]")
    revisoes_json: Mapped[str] = mapped_column(Text, default="[]")

    importado_em: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
