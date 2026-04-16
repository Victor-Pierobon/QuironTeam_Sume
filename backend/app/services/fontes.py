import asyncio
import re
from urllib.parse import quote, urlparse

import httpx

# ---------------------------------------------------------------------------
# Padrões de extração
# ---------------------------------------------------------------------------

DOI_PATTERN = re.compile(r'\b(10\.\d{4,}/[^\s\)\]\>,"\']+)')
URL_PATTERN = re.compile(r'https?://[^\s\)\]\>,"\'<]+')
INLINE_CITATION = re.compile(
    r'([A-ZÁÉÍÓÚÀÂÊÔÃÕÇ][a-záéíóúàâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÀÂÊÔÃÕÇ][a-záéíóúàâêôãõç]+)?'
    r'(?:\s+et\s+al\.?)?)\s*[,;]?\s*\((\d{4}[a-z]?)\)'
)

# ---------------------------------------------------------------------------
# Listas de domínios
# ---------------------------------------------------------------------------

DOMINIOS_VERDES = {
    "gov.br", "edu.br", "scielo.br", "scielo.org",
    "periodicos.capes.gov.br", "bdtd.ibict.br",
    "scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
    "arxiv.org", "jstor.org", "springer.com", "springerlink.com",
    "elsevier.com", "nature.com", "science.org", "tandfonline.com",
    "wiley.com", "academic.oup.com", "cambridge.org",
    "ibge.gov.br", "ipea.gov.br", "fiocruz.br", "embrapa.br",
    "anpec.org.br", "anpad.org.br", "sbq.org.br",
}

DOMINIOS_AMARELOS = {
    "wikipedia.org", "medium.com", "linkedin.com",
    "wordpress.com", "blogspot.com", "tumblr.com",
    "reddit.com", "quora.com", "slideshare.net",
    "academia.edu", "researchgate.net",
}

DOMINIOS_VERMELHOS = {
    "copiarcolar.com", "trabalhosescolares.com",
    "coladaweb.com", "mundovestibular.com.br",
    "resumoescolar.com.br", "passeidireto.com",
}

HEADERS = {"User-Agent": "Sume/1.0 (hackathon; contact: sume@quiron.team)"}


# ---------------------------------------------------------------------------
# Verificações assíncronas
# ---------------------------------------------------------------------------

async def _verificar_url(url: str) -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(timeout=6, follow_redirects=True) as client:
            resp = await client.head(url, headers=HEADERS)
            ok = resp.status_code < 400
            return ok, f"HTTP {resp.status_code}"
    except httpx.TimeoutException:
        return False, "Timeout ao acessar URL"
    except Exception as e:
        return False, f"Erro: {str(e)[:80]}"


async def _verificar_doi(doi: str) -> tuple[bool, str]:
    url = f"https://api.crossref.org/works/{quote(doi, safe='/')}"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            titles = data.get("message", {}).get("title", [])
            title = titles[0] if titles else "(sem título)"
            return True, f"DOI válido — {title[:80]}"
        return False, f"DOI não encontrado (HTTP {resp.status_code})"
    except Exception as e:
        return False, f"Erro CrossRef: {str(e)[:80]}"


async def _buscar_crossref(autor: str, ano: str) -> tuple[bool, str]:
    query = f"{autor} {ano}"
    url = (
        f"https://api.crossref.org/works"
        f"?query={quote(query)}&rows=3&select=title,author,published-print"
    )
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            items = resp.json().get("message", {}).get("items", [])
            if items:
                title = (items[0].get("title") or [""])[0]
                return True, f"Encontrado no CrossRef — {title[:80]}"
            return False, "Não encontrado no CrossRef"
        return False, f"CrossRef HTTP {resp.status_code}"
    except Exception as e:
        return False, f"Erro CrossRef: {str(e)[:80]}"


# ---------------------------------------------------------------------------
# Classificação de domínio
# ---------------------------------------------------------------------------

def _classificar_dominio(url: str) -> str:
    try:
        domain = urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return "amarelo"

    for d in DOMINIOS_VERDES:
        if domain == d or domain.endswith("." + d):
            return "verde"
    for d in DOMINIOS_VERMELHOS:
        if domain == d or domain.endswith("." + d):
            return "vermelho"
    for d in DOMINIOS_AMARELOS:
        if domain == d or domain.endswith("." + d):
            return "amarelo"
    return "amarelo"


# ---------------------------------------------------------------------------
# Extração de citações do texto
# ---------------------------------------------------------------------------

def extrair_citacoes(texto: str) -> list[dict]:
    citacoes: list[dict] = []
    seen: set[str] = set()

    # DOIs
    for doi in DOI_PATTERN.findall(texto):
        doi = doi.rstrip(".,;")
        if doi not in seen:
            seen.add(doi)
            citacoes.append({"tipo": "doi", "texto_original": doi, "doi": doi})

    # URLs (skip DOI resolver duplicates)
    for url in URL_PATTERN.findall(texto):
        url = url.rstrip(".,;:)")
        if url not in seen and "doi.org" not in url:
            seen.add(url)
            citacoes.append({"tipo": "url", "texto_original": url, "url": url})

    # Citações inline: Autor (ano)
    for m in INLINE_CITATION.finditer(texto):
        autor, ano = m.group(1).strip(), m.group(2)
        chave = f"{autor.lower()}_{ano}"
        if chave not in seen:
            seen.add(chave)
            citacoes.append({
                "tipo": "inline",
                "texto_original": f"{autor} ({ano})",
                "autor": autor,
                "ano": ano,
            })

    return citacoes


# ---------------------------------------------------------------------------
# Validação individual
# ---------------------------------------------------------------------------

async def _validar_citacao(citacao: dict) -> dict:
    tipo = citacao["tipo"]

    if tipo == "doi":
        encontrado, justificativa = await _verificar_doi(citacao["doi"])
        return {
            **citacao,
            "status": "verde" if encontrado else "vermelho",
            "justificativa": justificativa,
        }

    if tipo == "url":
        url = citacao["url"]
        status_dominio = _classificar_dominio(url)
        online, razao_http = await _verificar_url(url)

        if not online:
            status, justificativa = "vermelho", f"URL inacessível — {razao_http}"
        elif status_dominio == "vermelho":
            status, justificativa = "vermelho", "Domínio associado a conteúdo sem curadoria acadêmica"
        elif status_dominio == "verde":
            status, justificativa = "verde", f"Fonte institucional verificada ({razao_http})"
        else:
            status, justificativa = "amarelo", f"Fonte online, sem revisão por pares ({razao_http})"

        return {**citacao, "status": status, "justificativa": justificativa}

    if tipo == "inline":
        encontrado, justificativa = await _buscar_crossref(citacao["autor"], citacao["ano"])
        return {
            **citacao,
            "status": "verde" if encontrado else "amarelo",
            "justificativa": justificativa,
        }

    return {**citacao, "status": "amarelo", "justificativa": "Tipo não reconhecido"}


# ---------------------------------------------------------------------------
# Pipeline completo
# ---------------------------------------------------------------------------

async def validar_todas(texto: str) -> list[dict]:
    citacoes = extrair_citacoes(texto)
    if not citacoes:
        return []
    results = await asyncio.gather(*[_validar_citacao(c) for c in citacoes])
    return list(results)
