from sqlalchemy import String, Integer, ForeignKey, Text, Boolean, DateTime, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class StatusFonte(str, enum.Enum):
    verde = "verde"
    amarelo = "amarelo"
    vermelho = "vermelho"


class Trabalho(Base):
    __tablename__ = "trabalhos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"))
    titulo: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[str] = mapped_column(String(50))  # redação, relatório, resenha
    texto: Mapped[str] = mapped_column(Text)
    formato_origem: Mapped[str] = mapped_column(String(10))  # docx, pdf
    baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    data_entrega: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    aluno: Mapped["Aluno"] = relationship("Aluno", back_populates="trabalhos")
    features: Mapped[list["TrabalhoFeature"]] = relationship("TrabalhoFeature", back_populates="trabalho", cascade="all, delete-orphan")
    fontes: Mapped[list["Fonte"]] = relationship("Fonte", back_populates="trabalho", cascade="all, delete-orphan")
    paragrafos_destacados: Mapped[list["ParagrafoDestacado"]] = relationship("ParagrafoDestacado", back_populates="trabalho", cascade="all, delete-orphan")
    dossie: Mapped["Dossie | None"] = relationship("Dossie", back_populates="trabalho", uselist=False, cascade="all, delete-orphan")
    desfecho: Mapped["Desfecho | None"] = relationship("Desfecho", back_populates="trabalho", uselist=False, cascade="all, delete-orphan")


class TrabalhoFeature(Base):
    __tablename__ = "trabalho_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"))
    nome: Mapped[str] = mapped_column(String(100))
    valor: Mapped[float] = mapped_column(Float)

    trabalho: Mapped["Trabalho"] = relationship("Trabalho", back_populates="features")


class Fonte(Base):
    __tablename__ = "fontes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"))
    texto_original: Mapped[str] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[StatusFonte] = mapped_column(Enum(StatusFonte), default=StatusFonte.amarelo)
    justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)

    trabalho: Mapped["Trabalho"] = relationship("Trabalho", back_populates="fontes")


class ParagrafoDestacado(Base):
    __tablename__ = "paragrafos_destacados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trabalho_id: Mapped[int] = mapped_column(ForeignKey("trabalhos.id"))
    indice: Mapped[int] = mapped_column(Integer)
    texto: Mapped[str] = mapped_column(Text)
    features_destoantes: Mapped[str] = mapped_column(Text)  # JSON list de features

    trabalho: Mapped["Trabalho"] = relationship("Trabalho", back_populates="paragrafos_destacados")
