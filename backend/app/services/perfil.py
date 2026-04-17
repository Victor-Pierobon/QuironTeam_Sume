from statistics import mean, stdev
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.trabalho import Trabalho, TrabalhoFeature
from app.models.perfil import PerfilAluno
from app.services.features import (
    extrair_features,
    extrair_features_paragrafos,
    FEATURE_NAMES,
    FEATURE_LABELS,
)

# ---------------------------------------------------------------------------
# Direção esperada de cada feature com a evolução do aluno
#  1 = cresce com aprendizado
# -1 = decresce com aprendizado
#  0 = estilística, não deve mudar muito
# ---------------------------------------------------------------------------
FEATURE_DIRECTION: dict[str, int] = {
    "avg_sentence_length": 1,
    "std_sentence_length": 0,
    "avg_paragraph_length": 1,
    "syntactic_depth": 1,
    "lexical_diversity": 1,
    "avg_word_length": 1,
    "rare_words_pct": 1,
    "function_words_freq": 0,
    "commas_per_100": 0,
    "semicolons_per_1000": 0,
    "dashes_parens_per_1000": 0,
    "spelling_errors_per_1000": -1,
    "agreement_errors_per_1000": -1,
    "readability_index": -1,
    "connective_density": 1,
    "passive_voice_ratio": 0,
    "first_person_usage": 0,
    "ai_words_freq": 0,
    "sentence_length_variation": 0,
    "paragraph_uniformity": 0,
}


# ---------------------------------------------------------------------------
# Linear regression helper
# ---------------------------------------------------------------------------

def _linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Returns (slope, intercept)."""
    n = len(xs)
    if n < 2:
        return 0.0, (sum(ys) / n if n else 0.0)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return 0.0, y_mean
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    return slope, y_mean - slope * x_mean


# ---------------------------------------------------------------------------
# Recalculate profile from baseline texts
# ---------------------------------------------------------------------------

async def recalcular_perfil(aluno_id: int, db: AsyncSession) -> PerfilAluno | None:
    result = await db.execute(
        select(Trabalho)
        .where(Trabalho.aluno_id == aluno_id, Trabalho.baseline == True)
        .order_by(Trabalho.data_entrega)
    )
    baselines = result.scalars().all()

    if not baselines:
        return None

    # Collect feature values per baseline text
    feature_series: dict[str, list[float]] = {name: [] for name in FEATURE_NAMES}

    for trab in baselines:
        feat_result = await db.execute(
            select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trab.id)
        )
        stored = {f.nome: f.valor for f in feat_result.scalars().all()}

        # If features not yet extracted for this baseline, extract now
        if not stored:
            from re import findall as _findall
            from app.services.languagetool_service import contar_erros
            extracted = extrair_features(trab.texto)
            n_words = len(_findall(r'\b[a-záéíóúàâêôãõçñü]+\b', trab.texto.lower()))
            sp, ag = contar_erros(trab.texto, n_words)
            extracted["spelling_errors_per_1000"] = sp
            extracted["agreement_errors_per_1000"] = ag
            for nome, valor in extracted.items():
                db.add(TrabalhoFeature(trabalho_id=trab.id, nome=nome, valor=valor))
            stored = extracted

        for name in FEATURE_NAMES:
            feature_series[name].append(stored.get(name, 0.0))

    n = len(baselines)
    xs = [float(i) for i in range(n)]

    medias: dict[str, float] = {}
    desvios: dict[str, float] = {}
    tendencias: dict[str, float] = {}

    for name in FEATURE_NAMES:
        vals = feature_series[name]
        medias[name] = mean(vals)
        # Blend individual std with a minimum to avoid zero-std false positives
        ind_std = stdev(vals) if n > 1 else 0.0
        medias_val = medias[name]
        fallback = abs(medias_val) * 0.15 if medias_val != 0 else 0.1
        desvios[name] = max(ind_std, fallback * 0.5)
        slope, _ = _linear_regression(xs, vals)
        tendencias[name] = slope

    result = await db.execute(
        select(PerfilAluno).where(PerfilAluno.aluno_id == aluno_id)
    )
    perfil = result.scalar_one_or_none()

    if not perfil:
        perfil = PerfilAluno(aluno_id=aluno_id)
        db.add(perfil)

    perfil.medias = medias
    perfil.desvios = desvios
    perfil.tendencias = tendencias
    perfil.total_baseline = n

    await db.commit()
    await db.refresh(perfil)
    return perfil


# ---------------------------------------------------------------------------
# Deviation analysis
# ---------------------------------------------------------------------------

def _z_score_ajustado(
    valor: float,
    media: float,
    desvio: float,
    tendencia: float,
    n_baseline: int,
) -> float:
    if desvio == 0:
        return 0.0
    esperado = media + tendencia * n_baseline
    return (valor - esperado) / desvio


def _classificar(z: float, nome: str) -> str:
    direction = FEATURE_DIRECTION.get(nome, 0)
    abs_z = abs(z)

    if direction != 0:
        # Benefit of the doubt in the expected learning direction
        if (direction == 1 and z > 0) or (direction == -1 and z < 0):
            thr_atencao, thr_destaque = 2.5, 3.5
        else:
            thr_atencao, thr_destaque = 1.5, 2.5
    else:
        thr_atencao, thr_destaque = 1.5, 2.5

    if abs_z >= thr_destaque:
        return "destaque"
    elif abs_z >= thr_atencao:
        return "atencao"
    return "normal"


def analisar_desvios(features: dict[str, float], perfil: PerfilAluno) -> list[dict]:
    desvios = []
    for nome in FEATURE_NAMES:
        valor = features.get(nome, 0.0)
        media = perfil.medias.get(nome, 0.0)
        desvio = perfil.desvios.get(nome, 0.1)
        tendencia = perfil.tendencias.get(nome, 0.0)
        z = _z_score_ajustado(valor, media, desvio, tendencia, perfil.total_baseline)
        desvios.append({
            "nome": nome,
            "label": FEATURE_LABELS[nome],
            "valor": round(valor, 3),
            "media_baseline": round(media, 3),
            "z_score": round(z, 2),
            "status": _classificar(z, nome),
        })
    return desvios


def classificar_status_aluno(desvios: list[dict]) -> str:
    if any(d["status"] == "destaque" for d in desvios):
        return "destaque"
    if any(d["status"] == "atencao" for d in desvios):
        return "atencao"
    return "ok"


# ---------------------------------------------------------------------------
# Intra-document analysis
# ---------------------------------------------------------------------------

def analisar_intra_documento(texto: str) -> list[dict]:
    """Flag paragraphs that differ significantly from the document's own style."""
    para_features = extrair_features_paragrafos(texto)

    if len(para_features) < 3:
        return []

    # Compute mean and std of each feature across all paragraphs
    para_stats: dict[str, dict] = {}
    for nome in FEATURE_NAMES:
        vals = [feats[nome] for _, feats in para_features]
        avg = mean(vals)
        std = stdev(vals) if len(vals) > 1 else 0.1
        para_stats[nome] = {"media": avg, "desvio": max(std, 0.01)}

    destacados = []
    for idx, (para_texto, feats) in enumerate(para_features):
        destoantes = []
        for nome in FEATURE_NAMES:
            media = para_stats[nome]["media"]
            desvio = para_stats[nome]["desvio"]
            z = (feats[nome] - media) / desvio
            if abs(z) >= 2.0:
                destoantes.append({
                    "nome": nome,
                    "label": FEATURE_LABELS[nome],
                    "z_score": round(z, 2),
                })
        if len(destoantes) >= 2:
            destacados.append({
                "indice": idx,
                "texto_resumo": para_texto[:200] + ("…" if len(para_texto) > 200 else ""),
                "features_destoantes": destoantes,
            })

    return destacados
