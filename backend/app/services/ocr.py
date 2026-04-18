import base64
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OCR_PROMPT = """Você é um transcritor especializado em textos escolares.
Transcreva integralmente o texto escrito na imagem, preservando:
- Parágrafos separados por linha em branco
- Pontuação e acentuação exatamente como escrito
- Eventuais erros ortográficos do aluno (não corrija)

Retorne APENAS o texto transcrito, sem comentários, sem numeração de linhas, sem markdown."""


async def extrair_texto_foto(conteudo: bytes, mime: str) -> str:
    b64 = base64.standard_b64encode(conteudo).decode("utf-8")
    resp = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {"type": "text", "text": OCR_PROMPT},
                ],
            }
        ],
        temperature=0,
        max_tokens=4096,
    )
    return resp.choices[0].message.content.strip()
