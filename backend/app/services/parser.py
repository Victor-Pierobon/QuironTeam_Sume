import io
import re


def extrair_texto(conteudo: bytes, extensao: str) -> str:
    if extensao == "docx":
        return _extrair_docx(conteudo)
    elif extensao == "pdf":
        return _extrair_pdf(conteudo)
    raise ValueError(f"Extensão não suportada: {extensao}")


def _extrair_docx(conteudo: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(conteudo))
    paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragrafos)


def _extrair_pdf(conteudo: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(conteudo))
    paginas = []
    for page in reader.pages:
        texto = page.extract_text()
        if texto:
            paginas.append(texto.strip())
    return "\n\n".join(paginas)


def extrair_paragrafos(texto: str) -> list[str]:
    """Divide o texto em parágrafos não-vazios."""
    return [p.strip() for p in texto.split("\n\n") if p.strip()]


def extrair_urls(texto: str) -> list[str]:
    padrao = r'https?://[^\s\)\]\>"]+'
    return re.findall(padrao, texto)


def extrair_dois(texto: str) -> list[str]:
    padrao = r'\b10\.\d{4,}/\S+'
    return re.findall(padrao, texto)
