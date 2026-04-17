"""
Detecção de erros ortográficos e de concordância via LanguageTool.

Estratégia em três camadas (mais confiável → menos):
  1. API pública do LanguageTool (HTTPS, sem Java, gratuita com rate limit)
  2. Instância local do LanguageTool (se Java 17+ disponível)
  3. Heurísticas regex para PT-BR (fallback offline, sem dependências)
"""

from __future__ import annotations

import logging
import re

import httpx

logger = logging.getLogger(__name__)

_LT_PUBLIC_URL = "https://api.languagetool.org/v2/check"
_TIMEOUT = 8  # segundos

# IDs de regras para classificar os matches
_SPELL_RULES = {"MORFOLOGIK_RULE_PT_BR", "HUNSPELL_RULE", "HUNSPELL_NO_SUGGEST_RULE"}
_AGREEMENT_FRAGMENTS = {"CONCORDANCIA", "AGREEMENT", "GENDER", "NUMBER"}


def _e_spelling(match: dict) -> bool:
    rule_id = match.get("rule", {}).get("id", "")
    return rule_id in _SPELL_RULES or match.get("rule", {}).get("category", {}).get("id") == "TYPOS"


def _e_agreement(match: dict) -> bool:
    rule_id = match.get("rule", {}).get("id", "").upper()
    return any(f in rule_id for f in _AGREEMENT_FRAGMENTS)


# ---------------------------------------------------------------------------
# Camada 1 — API pública do LanguageTool
# ---------------------------------------------------------------------------

async def _via_api_publica(texto: str, n_palavras: int) -> tuple[float, float] | None:
    """Chama a API REST do LanguageTool. Retorna None se falhar."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                _LT_PUBLIC_URL,
                data={"text": texto, "language": "pt-BR"},
                headers={"Accept": "application/json"},
            )
        if resp.status_code != 200:
            return None
        matches = resp.json().get("matches", [])
        spelling  = sum(1 for m in matches if _e_spelling(m))
        agreement = sum(1 for m in matches if _e_agreement(m))
        return (
            round(spelling  / n_palavras * 1000, 3),
            round(agreement / n_palavras * 1000, 3),
        )
    except Exception as e:
        logger.debug(f"API pública LanguageTool falhou: {e}")
        return None


# ---------------------------------------------------------------------------
# Camada 2 — instância local (Java 17+)
# ---------------------------------------------------------------------------

_lt_local = None
_lt_local_falhou = False


def _get_lt_local():
    global _lt_local, _lt_local_falhou
    if _lt_local_falhou or _lt_local is not None:
        return _lt_local
    try:
        import language_tool_python
        _lt_local = language_tool_python.LanguageTool("pt-BR")
        logger.info("LanguageTool local pronto.")
    except Exception as e:
        logger.debug(f"LanguageTool local indisponível: {e}")
        _lt_local_falhou = True
    return _lt_local


def _via_local(texto: str, n_palavras: int) -> tuple[float, float] | None:
    lt = _get_lt_local()
    if lt is None:
        return None
    try:
        matches = lt.check(texto)
        # matches locais têm ruleId como atributo, não dict
        def spell_local(m) -> bool:
            return getattr(m, "ruleId", "") in _SPELL_RULES

        def agree_local(m) -> bool:
            return any(f in getattr(m, "ruleId", "").upper() for f in _AGREEMENT_FRAGMENTS)

        spelling  = sum(1 for m in matches if spell_local(m))
        agreement = sum(1 for m in matches if agree_local(m))
        return (
            round(spelling  / n_palavras * 1000, 3),
            round(agreement / n_palavras * 1000, 3),
        )
    except Exception as e:
        logger.debug(f"Erro no LanguageTool local: {e}")
        return None


# ---------------------------------------------------------------------------
# Camada 3 — heurísticas regex para PT-BR
# ---------------------------------------------------------------------------

# Palavras sem acento que deveriam tê-lo (muito comuns em textos escolares)
_SEM_ACENTO = re.compile(
    r'\b(voce|tambem|entao|nao|porem|assim|alem|atras|tres|eles|ela'
    r'|pos|sao|vao|dao|estao|irao|serao|caem|veem|crem|lem'
    r'|aqui|ali|la|ca|so|ja|ate|ha|e\b|e\.g\.'
    r')\b',
    re.IGNORECASE,
)

# Erros comuns de grafia
_ERROS_GRAFIA = re.compile(
    r'\b(atravez|menas|proximo|seje|mim mesmo|a gente (?:fomos|foram|fizemos|fizeram)'
    r'|por isso que\b|haja visto|ao invéz|ao invez|acertar a conta'
    r'|haver de|porisso|pra mim fazer|afim de\b'
    r')\b',
    re.IGNORECASE,
)

# Concordância de gênero grosseira: artigo masculino antes de terminação feminina
# e vice-versa (detecta casos óbvios sem parser morfológico completo)
_CONCORDANCIA_GENERO = re.compile(
    r'\b(?:o|um|esse|aquele|todo|meu|seu|nosso)\s+\w+(?:agem|ção|são|dade|tude|eza|ice|ise|ude)\b'
    r'|\b(?:a|uma|essa|aquela|toda|minha|sua|nossa)\s+\w+(?:ção|mento|ismo|ado|ido)\b',
    re.IGNORECASE,
)

# Verb-subject disagreement patterns (most common in student writing)
_CONCORDANCIA_VERBAL = re.compile(
    r'\b(?:eu\s+(?:foram|fomos|fizeram|fizemos|vieram|viemos|disseram|dissemos)'
    r'|eles?\s+(?:fui|foi|fiz|fez|vim|veio|disse|falou|disse)\b)',
    re.IGNORECASE,
)


def _via_heuristica(texto: str, n_palavras: int) -> tuple[float, float]:
    spelling = (
        len(_SEM_ACENTO.findall(texto)) +
        len(_ERROS_GRAFIA.findall(texto))
    )
    agreement = (
        len(_CONCORDANCIA_GENERO.findall(texto)) +
        len(_CONCORDANCIA_VERBAL.findall(texto))
    )
    return (
        round(spelling  / n_palavras * 1000, 3),
        round(agreement / n_palavras * 1000, 3),
    )


# ---------------------------------------------------------------------------
# API pública do módulo
# ---------------------------------------------------------------------------

async def contar_erros_async(texto: str, n_palavras: int) -> tuple[float, float]:
    """
    Versão assíncrona — tenta API pública, depois local, depois heurística.
    Use esta nos routers async do FastAPI.
    """
    if n_palavras == 0:
        return 0.0, 0.0

    resultado = await _via_api_publica(texto, n_palavras)
    if resultado is not None:
        return resultado

    resultado = _via_local(texto, n_palavras)
    if resultado is not None:
        return resultado

    return _via_heuristica(texto, n_palavras)


def contar_erros(texto: str, n_palavras: int) -> tuple[float, float]:
    """
    Versão síncrona — usa instância local ou heurística.
    Use esta em contextos síncronos (recalcular_perfil, seed).
    """
    if n_palavras == 0:
        return 0.0, 0.0

    resultado = _via_local(texto, n_palavras)
    if resultado is not None:
        return resultado

    return _via_heuristica(texto, n_palavras)
