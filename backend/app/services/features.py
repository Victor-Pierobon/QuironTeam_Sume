import re
import math
from statistics import mean, stdev

# ---------------------------------------------------------------------------
# Vocabulários
# ---------------------------------------------------------------------------

CONECTIVOS = {
    "ademais", "outrossim", "portanto", "contudo", "todavia", "entretanto",
    "no entanto", "por conseguinte", "assim sendo", "logo", "pois",
    "visto que", "dado que", "haja vista", "destarte", "doravante",
    "nesse sentido", "desse modo", "dessa forma", "nesse contexto",
    "em suma", "em síntese", "por fim", "além disso", "de fato",
    "com efeito", "por outro lado", "em contrapartida", "sobretudo",
}

AI_PALAVRAS = {
    "ademais", "outrossim", "crucial", "fundamental", "essencial",
    "perpassa", "nortear", "norteado", "viés", "basilar", "fulcral",
    "hodierno", "mister", "corrobora", "corroborar", "elucida",
    "elucidação", "intrínseco", "intrínseca", "multifacetado",
    "indubitavelmente", "inequivocamente", "sobretudo", "primordial",
    "inegável", "imprescindível",
}

PALAVRAS_FUNCIONAIS = {
    "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "e", "ou",
    "mas", "se", "que", "com", "por", "para", "pelo", "pela",
    "pelos", "pelas", "ao", "à", "aos", "às",
}

PRIMEIRA_PESSOA = {
    "eu", "me", "mim", "meu", "minha", "meus", "minhas",
    "nós", "nos", "nosso", "nossa", "nossos", "nossas",
}

PALAVRAS_COMUNS_PT = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com",
    "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como",
    "mas", "ao", "ele", "das", "seu", "sua", "ou", "quando", "muito",
    "nos", "já", "eu", "também", "só", "pelo", "pela", "até", "isso",
    "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "seus",
    "quem", "nas", "me", "esse", "eles", "você", "essa", "num", "nem",
    "suas", "meu", "às", "minha", "numa", "pelos", "elas", "havia",
    "seja", "qual", "será", "nós", "lhe", "deles", "essas", "esses",
    "pelas", "este", "dele", "tu", "te", "vocês", "lhes", "meus",
    "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa",
    "nossos", "nossas", "dela", "delas",
}

VOZ_PASSIVA = re.compile(
    r'\b(é|são|foi|foram|será|serão|seria|seriam|tem sido|têm sido)\s+\w+[ao]s?\b',
    re.IGNORECASE,
)

SUBORDINADORES = re.compile(
    r'\b(que|como|quando|porque|pois|embora|apesar|se|caso|para que|'
    r'ainda que|mesmo que|desde que|a fim de|visto que|dado que)\b',
    re.IGNORECASE,
)

FEATURE_NAMES: list[str] = [
    "avg_sentence_length",
    "std_sentence_length",
    "avg_paragraph_length",
    "syntactic_depth",
    "lexical_diversity",
    "avg_word_length",
    "rare_words_pct",
    "function_words_freq",
    "commas_per_100",
    "semicolons_per_1000",
    "dashes_parens_per_1000",
    "spelling_errors_per_1000",
    "agreement_errors_per_1000",
    "readability_index",
    "connective_density",
    "passive_voice_ratio",
    "first_person_usage",
    "ai_words_freq",
    "sentence_length_variation",
    "paragraph_uniformity",
]

FEATURE_LABELS: dict[str, str] = {
    "avg_sentence_length": "Comprimento médio de frase",
    "std_sentence_length": "Variação no comprimento de frase",
    "avg_paragraph_length": "Comprimento médio de parágrafo",
    "syntactic_depth": "Complexidade sintática",
    "lexical_diversity": "Diversidade lexical",
    "avg_word_length": "Comprimento médio de palavra",
    "rare_words_pct": "Uso de palavras raras",
    "function_words_freq": "Frequência de palavras funcionais",
    "commas_per_100": "Vírgulas por 100 palavras",
    "semicolons_per_1000": "Ponto-e-vírgula por 1000 palavras",
    "dashes_parens_per_1000": "Travessões e parênteses",
    "spelling_errors_per_1000": "Erros ortográficos estimados",
    "agreement_errors_per_1000": "Erros de concordância estimados",
    "readability_index": "Índice de legibilidade",
    "connective_density": "Densidade de conectivos formais",
    "passive_voice_ratio": "Uso de voz passiva",
    "first_person_usage": "Uso de primeira pessoa",
    "ai_words_freq": "Palavras típicas de IA",
    "sentence_length_variation": "Variação local de comprimento de frase",
    "paragraph_uniformity": "Uniformidade entre parágrafos",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_sentences(texto: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÀÂÊÔÃÕÇ])', texto)
    return [s.strip() for s in sentences if s.strip() and len(s.split()) >= 2]


def _split_words(texto: str) -> list[str]:
    return re.findall(r'\b[a-záéíóúàâêôãõçñü]+\b', texto.lower())


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _safe_stdev(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


# ---------------------------------------------------------------------------
# Feature helpers
# ---------------------------------------------------------------------------

def _lexical_diversity(words: list[str]) -> float:
    if not words:
        return 0.0
    return len(set(words)) / math.sqrt(len(words))


def _rare_words_pct(words: list[str]) -> float:
    if not words:
        return 0.0
    raras = [w for w in words if w not in PALAVRAS_COMUNS_PT and len(w) > 3]
    return len(raras) / len(words)


def _function_words_freq(words: list[str]) -> float:
    if not words:
        return 0.0
    return sum(1 for w in words if w in PALAVRAS_FUNCIONAIS) / len(words)


def _connective_density(texto: str, n_words: int) -> float:
    if n_words == 0:
        return 0.0
    texto_lower = texto.lower()
    count = sum(1 for c in CONECTIVOS if c in texto_lower)
    return count / n_words * 100


def _passive_voice_ratio(texto: str, n_sentences: int) -> float:
    if n_sentences == 0:
        return 0.0
    return len(VOZ_PASSIVA.findall(texto)) / n_sentences


def _first_person_usage(words: list[str], n_words: int) -> float:
    if n_words == 0:
        return 0.0
    return sum(1 for w in words if w in PRIMEIRA_PESSOA) / n_words * 100


def _ai_words_freq(words: list[str], n_words: int) -> float:
    if n_words == 0:
        return 0.0
    return sum(1 for w in words if w in AI_PALAVRAS) / n_words * 1000


def _sentence_length_variation(lengths: list[int]) -> float:
    if len(lengths) < 2:
        return 0.0
    diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, len(lengths))]
    return _safe_mean([float(d) for d in diffs])


def _paragraph_uniformity(paragrafos: list[str]) -> float:
    """High value = paragraphs are very similar in length (suspicious for AI)."""
    if len(paragrafos) < 2:
        return 0.0
    lengths = [len(_split_words(p)) for p in paragrafos]
    avg = _safe_mean([float(l) for l in lengths])
    if avg == 0:
        return 0.0
    cv = _safe_stdev([float(l) for l in lengths]) / avg
    return round(1.0 - min(cv, 1.0), 4)


def _syntactic_depth(sentences: list[str]) -> float:
    if not sentences:
        return 0.0
    depths = [len(SUBORDINADORES.findall(s)) for s in sentences]
    return _safe_mean([float(d) for d in depths])


def _readability(texto: str, words: list[str], sentences: list[str]) -> float:
    try:
        import textstat
        textstat.set_lang("pt_BR")
        return float(textstat.flesch_reading_ease(texto))
    except Exception:
        if not sentences or not words:
            return 50.0
        avg_sent = len(words) / len(sentences)
        syl_counts = [
            max(1, len(re.findall(r'[aeiouáéíóúàâêôãõ]', w)))
            for w in words
        ]
        avg_syl = _safe_mean([float(s) for s in syl_counts])
        return round(206.835 - 1.015 * avg_sent - 84.6 * avg_syl, 2)


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extrair_features(texto: str) -> dict[str, float]:
    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    if not paragrafos:
        paragrafos = [texto]

    words = _split_words(texto)
    sentences = _split_sentences(texto) or [texto]
    n_words = len(words)

    if not words:
        return {k: 0.0 for k in FEATURE_NAMES}

    sentence_lengths = [len(_split_words(s)) for s in sentences]
    para_lengths = [len(_split_words(p)) for p in paragrafos]

    return {
        # Estrutura da frase
        "avg_sentence_length": _safe_mean([float(l) for l in sentence_lengths]),
        "std_sentence_length": _safe_stdev([float(l) for l in sentence_lengths]),
        "avg_paragraph_length": _safe_mean([float(l) for l in para_lengths]),
        "syntactic_depth": _syntactic_depth(sentences),
        # Vocabulário
        "lexical_diversity": _lexical_diversity(words),
        "avg_word_length": _safe_mean([float(len(w)) for w in words]),
        "rare_words_pct": _rare_words_pct(words),
        "function_words_freq": _function_words_freq(words),
        # Pontuação e mecânica
        "commas_per_100": texto.count(",") / n_words * 100,
        "semicolons_per_1000": texto.count(";") / n_words * 1000,
        "dashes_parens_per_1000": (
            texto.count("—") + texto.count("–") + texto.count("(") + texto.count(")")
        ) / n_words * 1000,
        "spelling_errors_per_1000": 0.0,   # placeholder — language-tool no Dia 2+
        "agreement_errors_per_1000": 0.0,  # placeholder
        # Discurso e legibilidade
        "readability_index": _readability(texto, words, sentences),
        "connective_density": _connective_density(texto, n_words),
        "passive_voice_ratio": _passive_voice_ratio(texto, len(sentences)),
        "first_person_usage": _first_person_usage(words, n_words),
        # Pegadas de IA
        "ai_words_freq": _ai_words_freq(words, n_words),
        "sentence_length_variation": _sentence_length_variation(sentence_lengths),
        "paragraph_uniformity": _paragraph_uniformity(paragrafos),
    }


def extrair_features_paragrafos(texto: str) -> list[tuple[str, dict[str, float]]]:
    """Return (paragraph_text, features) for each paragraph with >= 20 words."""
    paragrafos = [
        p.strip()
        for p in texto.split("\n\n")
        if p.strip() and len(p.split()) >= 20
    ]
    return [(p, extrair_features(p)) for p in paragrafos]
