"""
Integração com Google Docs — histórico de revisões e padrões de edição.

Autenticação via Service Account (Opção A do roadmap).
O professor compartilha o doc com o e-mail da service account da aplicação.
Credenciais lidas de GOOGLE_SERVICE_ACCOUNT_JSON (path para o arquivo .json).

Padrões detectados:
  - colagem_unica: >50% do texto inserido em uma revisão
  - sem_edicoes: razão edição/adição < 0.05 (texto gerado, não escrito)
  - tempo_insuficiente: tempo ativo < 0.3 min/palavra
  - sessao_unica: texto > 300 palavras escrito em uma única sessão
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_GDOCS_AVAILABLE = False
_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    _GDOCS_AVAILABLE = True
except ImportError:
    logger.info("google-api-python-client não instalado — feature Google Docs indisponível.")


def _get_service():
    """Constrói o cliente Drive API autenticado via service account."""
    cred_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError(
            "Credenciais do Google não configuradas. "
            "Defina GOOGLE_SERVICE_ACCOUNT_JSON com o caminho para o arquivo .json da service account."
        )
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=_SCOPES)
    return build("drive", "v3", credentials=creds)


def _extrair_doc_id(url: str) -> str:
    """Extrai o ID do documento a partir de qualquer URL do Google Docs."""
    patterns = [
        r"/document/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    raise ValueError(f"Não foi possível extrair o ID do documento da URL: {url}")


def _gap_minutos(t1: str, t2: str) -> float:
    """Diferença em minutos entre dois timestamps ISO."""
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    try:
        d1 = datetime.strptime(t1, fmt).replace(tzinfo=timezone.utc)
        d2 = datetime.strptime(t2, fmt).replace(tzinfo=timezone.utc)
        return abs((d2 - d1).total_seconds()) / 60
    except Exception:
        return 0.0


def _calcular_metricas(revisoes: list[dict]) -> dict:
    """
    Calcula métricas de padrão de edição a partir da lista de revisões.
    Cada revisão deve ter: timestamp, tamanho_chars, chars_adicionados, chars_deletados.
    """
    if not revisoes:
        return {
            "num_sessoes": 0,
            "tempo_ativo_min": 0.0,
            "maior_insercao_pct": 0.0,
            "razao_edicao_adicao": 0.0,
            "proporcao_final_colada": 0.0,
        }

    tamanho_final = revisoes[-1].get("tamanho_chars", 1) or 1
    total_adicionado = sum(r.get("chars_adicionados", 0) for r in revisoes)
    total_deletado = sum(r.get("chars_deletados", 0) for r in revisoes)

    # Sessões: agrupamentos com gap < 30 min
    sessoes = 1
    tempo_ativo = 0.0
    for i in range(1, len(revisoes)):
        gap = _gap_minutos(revisoes[i - 1]["timestamp"], revisoes[i]["timestamp"])
        if gap > 30:
            sessoes += 1
        else:
            tempo_ativo += gap

    # Maior inserção única como % do tamanho final
    maior_insercao = max((r.get("chars_adicionados", 0) for r in revisoes), default=0)
    maior_insercao_pct = maior_insercao / tamanho_final

    # Razão edição/adição
    razao = total_deletado / total_adicionado if total_adicionado > 0 else 0.0

    # Proporção final colada: chars da última sessão / tamanho final
    # (aproximação: soma das inserções da última sessão)
    ultima_sessao_chars = 0
    for i in range(len(revisoes) - 1, -1, -1):
        if i > 0:
            gap = _gap_minutos(revisoes[i - 1]["timestamp"], revisoes[i]["timestamp"])
            if gap > 30:
                break
        ultima_sessao_chars += revisoes[i].get("chars_adicionados", 0)
    proporcao_final = ultima_sessao_chars / tamanho_final

    return {
        "num_sessoes": sessoes,
        "tempo_ativo_min": round(tempo_ativo, 1),
        "maior_insercao_pct": round(maior_insercao_pct, 3),
        "razao_edicao_adicao": round(razao, 3),
        "proporcao_final_colada": round(proporcao_final, 3),
    }


_PADROES_CONFIG = {
    "colagem_unica": {
        "condicao": lambda m: m["maior_insercao_pct"] > 0.5,
        "mensagem": "Mais da metade do texto foi inserido em uma única edição.",
        "nivel": "destaque",
    },
    "sem_edicoes": {
        "condicao": lambda m: m["razao_edicao_adicao"] < 0.05,
        "mensagem": "Quase nenhuma revisão — o texto parece ter sido gerado, não escrito.",
        "nivel": "atencao",
    },
    "tempo_insuficiente": {
        "condicao": lambda m: m["tempo_ativo_min"] < 5 and m["num_sessoes"] > 0,
        "mensagem": "Tempo ativo muito abaixo do esperado para o tamanho do texto.",
        "nivel": "atencao",
    },
    "sessao_unica": {
        "condicao": lambda m: m["num_sessoes"] == 1,
        "mensagem": "Todo o texto foi produzido em uma única sessão contínua.",
        "nivel": "atencao",
    },
}


def detectar_padroes(metricas: dict) -> list[dict]:
    encontrados = []
    for nome, cfg in _PADROES_CONFIG.items():
        try:
            if cfg["condicao"](metricas):
                encontrados.append({
                    "nome": nome,
                    "mensagem": cfg["mensagem"],
                    "nivel": cfg["nivel"],
                })
        except Exception:
            pass
    return encontrados


def buscar_texto_gdoc(doc_url: str) -> str:
    """
    Exporta o documento Google Docs como texto simples usando a mesma Service Account.
    Retorna o conteúdo do documento como string.
    """
    if not _GDOCS_AVAILABLE:
        raise RuntimeError("Pacote google-api-python-client não instalado.")

    doc_id = _extrair_doc_id(doc_url)
    service = _get_service()

    # Drive API export — exporta como plain text
    request = service.files().export_media(fileId=doc_id, mimeType="text/plain")
    content = request.execute()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return str(content)


async def buscar_historico_gdocs(doc_url: str) -> tuple[list[dict], dict]:
    """
    Busca o histórico de revisões do Google Doc e retorna (revisoes, metricas).
    revisoes: lista com timestamp, tamanho_chars, chars_adicionados, chars_deletados
    metricas: dict com as 5 métricas calculadas
    """
    if not _GDOCS_AVAILABLE:
        raise RuntimeError("Pacote google-api-python-client não instalado.")

    doc_id = _extrair_doc_id(doc_url)
    service = _get_service()

    # Busca lista de revisões (Drive API v3)
    resp = service.revisions().list(fileId=doc_id, fields="revisions(id,modifiedTime,size)").execute()
    raw_revisions = resp.get("revisions", [])

    if not raw_revisions:
        return [], _calcular_metricas([])

    revisoes = []
    prev_size = 0
    for rev in raw_revisions:
        size = int(rev.get("size", prev_size) or prev_size)
        added = max(0, size - prev_size)
        deleted = max(0, prev_size - size)
        revisoes.append({
            "timestamp": rev.get("modifiedTime", ""),
            "tamanho_chars": size,
            "chars_adicionados": added,
            "chars_deletados": deleted,
        })
        prev_size = size

    metricas = _calcular_metricas(revisoes)
    return revisoes, metricas


async def importar_gdoc_completo(doc_url: str) -> tuple[str, list[dict], dict]:
    """
    Importação completa: texto + histórico + métricas em uma chamada.
    Retorna (texto, revisoes, metricas).
    """
    texto = buscar_texto_gdoc(doc_url)
    revisoes, metricas = await buscar_historico_gdocs(doc_url)
    return texto, revisoes, metricas
