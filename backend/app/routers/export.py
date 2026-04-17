"""
Export do dossiê completo de um trabalho em PDF.
Endpoint: GET /export/{trabalho_id}/pdf
"""

from __future__ import annotations

import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fpdf import FPDF
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.aluno import Aluno
from app.models.dossie import Desfecho, Dossie
from app.models.perfil import PerfilAluno
from app.models.trabalho import Fonte, ParagrafoDestacado, Trabalho, TrabalhoFeature
from app.services.features import FEATURE_LABELS
from app.services.perfil import analisar_desvios

router = APIRouter()

# ---------------------------------------------------------------------------
# Paleta e constantes
# ---------------------------------------------------------------------------

COR_VERDE    = (45, 122, 79)
COR_AMBAR    = (217, 119, 6)
COR_VERMELHO = (220, 38, 38)
COR_TEXTO    = (28, 25, 23)
COR_MUTED    = (120, 113, 108)
COR_BORDA    = (229, 225, 218)
COR_BG       = (247, 244, 239)
COR_HEADER   = (30, 77, 43)

EMOJI_MAP = {
    "verde":    "[V]",
    "amarelo":  "[!]",
    "vermelho": "[X]",
    "normal":   "[ ]",
    "atencao":  "[!]",
    "destaque": "[X]",
}

def _ascii(texto: str) -> str:
    """Remove ou substitui caracteres não suportados por Latin-1 (fpdf2 padrão)."""
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--", "\u2026": "...",
        "\u00e7": "c", "\u00c7": "C",
        # Mantém acentos comuns — fpdf2 com latin-1 suporta ISO 8859-1
    }
    for orig, sub in replacements.items():
        texto = texto.replace(orig, sub)
    # Remove qualquer caractere fora de Latin-1
    return texto.encode("latin-1", errors="replace").decode("latin-1")


# ---------------------------------------------------------------------------
# Classe PDF
# ---------------------------------------------------------------------------

class DossiePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_fill_color(*COR_HEADER)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 3)
        self.cell(0, 8, "SUME - Dossie Pedagogico", ln=False)
        self.set_xy(0, 3)
        self.cell(200, 8, _ascii(datetime.now().strftime("%d/%m/%Y")), align="R")
        self.ln(12)
        self.set_text_color(*COR_TEXTO)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*COR_MUTED)
        self.cell(0, 8, f"Sume  |  Uso pedagogico - nao constitui prova formal  |  Pag. {self.page_no()}", align="C")
        self.set_text_color(*COR_TEXTO)

    # --- Helpers ---

    def section_title(self, titulo: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*COR_MUTED)
        self.cell(0, 6, _ascii(titulo.upper()), ln=True)
        self.set_draw_color(*COR_BORDA)
        self.line(self.get_x(), self.get_y(), self.get_x() + 170, self.get_y())
        self.ln(3)
        self.set_text_color(*COR_TEXTO)

    def badge(self, texto: str, cor: tuple):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*cor)
        self.cell(12, 6, _ascii(EMOJI_MAP.get(texto, "[?]")))
        self.set_text_color(*COR_TEXTO)

    def kv_row(self, chave: str, valor: str):
        self.set_font("Helvetica", "B", 9)
        self.cell(55, 6, _ascii(chave + ":"))
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, _ascii(str(valor)), ln=True)

    def contador_box(self, label: str, valor, cor: tuple):
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*COR_BG)
        self.rect(x, y, 38, 16, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*cor)
        self.set_xy(x, y + 1)
        self.cell(38, 8, str(valor), align="C")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*COR_MUTED)
        self.set_xy(x, y + 9)
        self.cell(38, 6, _ascii(label), align="C")
        self.set_xy(x + 40, y)
        self.set_text_color(*COR_TEXTO)

    def multiline(self, texto: str, size: int = 9):
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, 5, _ascii(texto))
        self.ln(1)


# ---------------------------------------------------------------------------
# Montagem do PDF
# ---------------------------------------------------------------------------

async def _montar_pdf(trabalho_id: int, db: AsyncSession) -> bytes:
    # --- Busca dados ---
    trab_r  = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = trab_r.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(404, "Trabalho não encontrado")

    aluno_r = await db.execute(select(Aluno).where(Aluno.id == trabalho.aluno_id))
    aluno   = aluno_r.scalar_one_or_none()

    perfil_r = await db.execute(select(PerfilAluno).where(PerfilAluno.aluno_id == trabalho.aluno_id))
    perfil   = perfil_r.scalar_one_or_none()

    feat_r   = await db.execute(select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trabalho_id))
    features = {f.nome: f.valor for f in feat_r.scalars().all()}

    dossie_r = await db.execute(select(Dossie).where(Dossie.trabalho_id == trabalho_id))
    dossie   = dossie_r.scalar_one_or_none()

    fonte_r  = await db.execute(select(Fonte).where(Fonte.trabalho_id == trabalho_id))
    fontes   = fonte_r.scalars().all()

    para_r   = await db.execute(select(ParagrafoDestacado).where(ParagrafoDestacado.trabalho_id == trabalho_id))
    paragrafos = para_r.scalars().all()

    desfecho_r = await db.execute(select(Desfecho).where(Desfecho.trabalho_id == trabalho_id))
    desfecho   = desfecho_r.scalar_one_or_none()

    desvios = analisar_desvios(features, perfil) if perfil and perfil.total_baseline > 0 else []

    # --- Monta PDF ---
    pdf = DossiePDF()
    pdf.add_page()

    # Identificação
    pdf.section_title("Identificação")
    nome_aluno = aluno.nome if aluno else "Aluno"
    pdf.kv_row("Aluno", nome_aluno)
    if aluno and aluno.matricula:
        pdf.kv_row("Matrícula", aluno.matricula)
    pdf.kv_row("Trabalho", trabalho.titulo)
    pdf.kv_row("Tipo", trabalho.tipo)
    pdf.kv_row("Entrega", datetime.fromisoformat(str(trabalho.data_entrega)).strftime("%d/%m/%Y"))
    pdf.kv_row("Formato", f".{trabalho.formato_origem}")
    pdf.kv_row("Baseline", "Sim" if trabalho.baseline else "Não")
    n_base = perfil.total_baseline if perfil else 0
    pdf.kv_row("Textos no perfil", str(n_base))
    pdf.ln(2)

    # Contadores
    if dossie:
        pdf.section_title("Resumo")
        pdf.set_xy(20, pdf.get_y())
        pdf.contador_box("Normais",   dossie.normais,   COR_VERDE)
        pdf.contador_box("Atencao",   dossie.atencao,   COR_AMBAR)
        pdf.contador_box("Conversar", dossie.destaque,  COR_VERMELHO)
        pdf.contador_box(f"Fontes {dossie.fontes_verificadas}/{dossie.fontes_total}",
                         f"{dossie.fontes_verificadas}/{dossie.fontes_total}", COR_TEXTO)
        pdf.ln(18)

    # Evidências estilométricas
    flagados = [d for d in desvios if d["status"] != "normal"]
    if flagados:
        pdf.section_title("Evidências estilométricas")
        flagados_sorted = sorted(flagados, key=lambda x: abs(x["z_score"]), reverse=True)
        for d in flagados_sorted:
            cor = COR_VERMELHO if d["status"] == "destaque" else COR_AMBAR
            pdf.badge(d["status"], cor)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*cor)
            pdf.cell(80, 6, _ascii(d["label"]))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*COR_MUTED)
            z = d["z_score"]
            pdf.cell(0, 6, f"z = {z:+.1f}   valor: {d['valor']:.2f}   baseline: {d['media_baseline']:.2f}", ln=True)
            pdf.set_text_color(*COR_TEXTO)
        pdf.ln(2)

    # Parágrafos destoantes
    if paragrafos:
        pdf.section_title("Parágrafos que destoam do próprio texto")
        for p in paragrafos:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*COR_AMBAR)
            pdf.cell(0, 6, f"Paragrafo {p.indice + 1}", ln=True)
            pdf.set_text_color(*COR_TEXTO)
            pdf.set_font("Helvetica", "I", 8)
            resumo = (p.texto[:180] + "...") if len(p.texto) > 180 else p.texto
            pdf.multi_cell(0, 4, f'"{_ascii(resumo)}"')
            try:
                feats = json.loads(p.features_destoantes)
                labels = ", ".join(f.get("label", "") for f in feats)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*COR_MUTED)
                pdf.cell(0, 5, _ascii("Metricas: " + labels), ln=True)
                pdf.set_text_color(*COR_TEXTO)
            except Exception:
                pass
            pdf.ln(1)

    # Fontes
    if fontes:
        pdf.section_title("Fontes citadas")
        for f in fontes:
            cor = COR_VERDE if f.status.value == "verde" else (COR_VERMELHO if f.status.value == "vermelho" else COR_AMBAR)
            pdf.badge(f.status.value, cor)
            pdf.set_font("Helvetica", "", 9)
            trunc = f.texto_original[:70] + ("..." if len(f.texto_original) > 70 else "")
            pdf.cell(0, 6, _ascii(trunc), ln=True)
            if f.justificativa:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(*COR_MUTED)
                pdf.cell(12)
                pdf.cell(0, 5, _ascii(f.justificativa[:90]), ln=True)
                pdf.set_text_color(*COR_TEXTO)
        pdf.ln(2)

    # Roteiro socrático
    if dossie and dossie.observacoes_professor:
        pdf.section_title("Roteiro de conversa")

        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "O que os dados mostram:", ln=True)
        pdf.multiline(dossie.observacoes_professor)

        try:
            perguntas = json.loads(dossie.perguntas_socraticas or "[]")
        except Exception:
            perguntas = []

        if perguntas:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 6, "Perguntas para o aluno:", ln=True)
            for i, p in enumerate(perguntas, 1):
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(8, 5, f"{i}.")
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(0, 5, _ascii(p))
                pdf.ln(1)

        if dossie.roteiro_conversa:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 6, "Como conduzir:", ln=True)
            pdf.multiline(dossie.roteiro_conversa)

    # Desfecho
    if desfecho:
        pdf.section_title("Desfecho registrado")
        status_labels = {
            "esclarecido":        "Esclarecido",
            "conversa_realizada": "Conversa realizada",
            "em_acompanhamento":  "Em acompanhamento",
        }
        pdf.kv_row("Status", status_labels.get(desfecho.status.value, desfecho.status.value))
        if desfecho.nota:
            pdf.kv_row("Nota", desfecho.nota)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/{trabalho_id}/pdf")
async def exportar_pdf(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    pdf_bytes = await _montar_pdf(trabalho_id, db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="sume-dossie-{trabalho_id}.pdf"'
        },
    )
