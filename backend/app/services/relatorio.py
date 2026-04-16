import json
import os

from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não configurada no .env")
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# Montagem do dossiê textual (sem texto bruto do aluno)
# ---------------------------------------------------------------------------

def _montar_dossie(
    aluno_nome: str,
    titulo: str,
    n_baseline: int,
    desvios: list[dict],
    paragrafos: list[dict],
    fontes: list[dict],
) -> str:
    linhas = [
        f"ALUNO: {aluno_nome}",
        f"TRABALHO: {titulo}",
        f"BASELINE: {n_baseline} texto(s) confiável(is)",
        "",
    ]

    flagados = [d for d in desvios if d["status"] != "normal"]
    linhas.append("DESVIOS ESTILOMÉTRICOS:")
    if flagados:
        for d in sorted(flagados, key=lambda x: abs(x["z_score"]), reverse=True):
            nivel = "⚠ ATENÇÃO" if d["status"] == "atencao" else "🔴 DESTAQUE"
            linhas.append(
                f"  {nivel} {d['label']}: z={d['z_score']:+.1f} "
                f"(valor={d['valor']:.2f}, média do aluno={d['media_baseline']:.2f})"
            )
    else:
        linhas.append("  Nenhum desvio significativo.")

    linhas.append("")
    linhas.append("PARÁGRAFOS QUE DESTOAM DO PRÓPRIO TEXTO:")
    if paragrafos:
        for p in paragrafos:
            feats = ", ".join(f["label"] for f in p.get("features_destoantes", []))
            linhas.append(f"  Parágrafo {p['indice'] + 1}: {feats}")
    else:
        linhas.append("  Nenhum.")

    linhas.append("")
    linhas.append("FONTES CITADAS COM PROBLEMAS:")
    prob = [f for f in fontes if f["status"] in ("vermelho", "amarelo")]
    if prob:
        for f in prob:
            linhas.append(
                f"  [{f['status'].upper()}] {f['texto_original'][:80]} — {f.get('justificativa', '')}"
            )
    else:
        linhas.append("  Nenhuma.")

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um assistente pedagógico que ajuda professores a entenderem
a produção escrita de seus alunos. Você recebe evidências estatísticas sobre o trabalho
de um aluno e as transforma em linguagem pedagógica acessível.

REGRAS ABSOLUTAS:
- Nunca use as palavras: plágio, fraude, trapaça, suspeita, acusação, cola, cópia, IA,
  inteligência artificial, ChatGPT, gerado, detector.
- Linguagem sempre curiosa e acolhedora, nunca acusatória.
- O professor é quem decide — você apenas apresenta evidências e sugere perguntas.
- Sempre destaque também pontos positivos quando existirem.

Retorne SOMENTE um JSON válido com esta estrutura:
{
  "observacoes": "3 a 5 frases para o professor, em linguagem simples, descrevendo o que os dados mostram",
  "perguntas_socraticas": ["pergunta 1", "pergunta 2", "pergunta 3"],
  "roteiro_conversa": "5 a 7 linhas sugerindo como o professor pode conduzir a conversa com o aluno"
}"""


# ---------------------------------------------------------------------------
# Geração
# ---------------------------------------------------------------------------

def gerar_relatorio(
    aluno_nome: str,
    titulo: str,
    n_baseline: int,
    desvios: list[dict],
    paragrafos: list[dict],
    fontes: list[dict],
) -> dict:
    dossie = _montar_dossie(aluno_nome, titulo, n_baseline, desvios, paragrafos, fontes)

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Gere o relatório pedagógico para o dossiê a seguir:\n\n{dossie}"},
            ],
            temperature=0.4,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        conteudo = resp.choices[0].message.content
        return json.loads(conteudo)

    except ValueError as e:
        return _fallback(str(e))
    except Exception as e:
        return _fallback(f"Erro ao chamar a API Groq: {e}")


def _fallback(motivo: str) -> dict:
    return {
        "observacoes": f"[Relatório indisponível — {motivo}]",
        "perguntas_socraticas": [
            "Como você organizou suas ideias para escrever esse trabalho?",
            "Quais fontes você consultou e como as encontrou?",
            "Tem alguma parte do texto que você gostaria de explicar com mais detalhes?",
        ],
        "roteiro_conversa": (
            "Comece elogiando o esforço do aluno. "
            "Pergunte sobre o processo de escrita de forma aberta. "
            "Explore as fontes citadas com curiosidade, não com desconfiança. "
            "Peça que o aluno explique trechos com suas próprias palavras. "
            "Encerre reforçando o que foi bem feito."
        ),
    }
