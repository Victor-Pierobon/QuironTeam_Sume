"""
Comparação estilométrica entre alunos de uma turma.
Endpoint: GET /turmas/{turma_id}/comparacao
"""

from __future__ import annotations

from statistics import mean, stdev

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.services.features import FEATURE_NAMES, FEATURE_LABELS

router = APIRouter()


def _cosine(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sum(a ** 2 for a in v1) ** 0.5
    n2 = sum(b ** 2 for b in v2) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return round(dot / (n1 * n2), 4)


@router.get("/{turma_id}/comparacao")
async def comparar_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    turma_r = await db.execute(select(Turma).where(Turma.id == turma_id))
    if not turma_r.scalar_one_or_none():
        raise HTTPException(404, "Turma não encontrada")

    alunos_r = await db.execute(select(Aluno).where(Aluno.turma_id == turma_id))
    alunos = alunos_r.scalars().all()
    if not alunos:
        return {"heatmap": [], "pares_similares": [], "distribuicao": {}}

    # Busca o trabalho mais recente não-baseline de cada aluno e seu vetor de features
    aluno_vectors: list[dict] = []
    for aluno in alunos:
        trab_r = await db.execute(
            select(Trabalho)
            .where(Trabalho.aluno_id == aluno.id, Trabalho.baseline == False)
            .order_by(Trabalho.data_entrega.desc())
        )
        trabalho = trab_r.scalars().first()
        if not trabalho:
            continue

        feat_r = await db.execute(
            select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == trabalho.id)
        )
        stored = {f.nome: f.valor for f in feat_r.scalars().all()}
        if not stored:
            continue

        vector = [stored.get(n, 0.0) for n in FEATURE_NAMES]
        aluno_vectors.append({
            "aluno_id": aluno.id,
            "aluno_nome": aluno.nome,
            "trabalho_id": trabalho.id,
            "trabalho_titulo": trabalho.titulo,
            "features": stored,
            "vector": vector,
        })

    if not aluno_vectors:
        return {"heatmap": [], "pares_similares": [], "distribuicao": {}}

    # Distribuição por feature (média e desvio da turma)
    distribuicao: dict[str, dict] = {}
    for nome in FEATURE_NAMES:
        vals = [av["features"].get(nome, 0.0) for av in aluno_vectors]
        avg = mean(vals)
        std = stdev(vals) if len(vals) > 1 else 0.0
        distribuicao[nome] = {
            "label": FEATURE_LABELS[nome],
            "media": round(avg, 3),
            "desvio": round(std, 3),
            "valores": [
                {"aluno_id": av["aluno_id"], "aluno_nome": av["aluno_nome"], "valor": round(av["features"].get(nome, 0.0), 3)}
                for av in aluno_vectors
            ],
        }

    # Heatmap: z-score de cada aluno em cada feature relativo à turma
    heatmap = []
    for av in aluno_vectors:
        row: dict[str, float] = {}
        for nome in FEATURE_NAMES:
            media = distribuicao[nome]["media"]
            desvio = distribuicao[nome]["desvio"]
            val = av["features"].get(nome, 0.0)
            z = (val - media) / desvio if desvio > 0 else 0.0
            row[nome] = round(z, 2)
        heatmap.append({
            "aluno_id": av["aluno_id"],
            "aluno_nome": av["aluno_nome"],
            "trabalho_id": av["trabalho_id"],
            "trabalho_titulo": av["trabalho_titulo"],
            "z_scores": row,
        })

    # Pares com alta similaridade coseno
    pares_similares = []
    n = len(aluno_vectors)
    for i in range(n):
        for j in range(i + 1, n):
            sim = _cosine(aluno_vectors[i]["vector"], aluno_vectors[j]["vector"])
            if sim >= 0.90:
                # Identifica as features com z_scores mais próximos (ambos desviando na mesma direção)
                zi = heatmap[i]["z_scores"]
                zj = heatmap[j]["z_scores"]
                features_comuns = [
                    {"nome": nome, "label": FEATURE_LABELS[nome], "z_a": zi[nome], "z_b": zj[nome]}
                    for nome in FEATURE_NAMES
                    if abs(zi[nome]) >= 1.5 and abs(zj[nome]) >= 1.5
                    and (zi[nome] * zj[nome]) > 0  # mesma direção
                ]
                features_comuns.sort(key=lambda x: abs(x["z_a"]) + abs(x["z_b"]), reverse=True)
                pares_similares.append({
                    "aluno_a": {"id": aluno_vectors[i]["aluno_id"], "nome": aluno_vectors[i]["aluno_nome"], "trabalho_id": aluno_vectors[i]["trabalho_id"]},
                    "aluno_b": {"id": aluno_vectors[j]["aluno_id"], "nome": aluno_vectors[j]["aluno_nome"], "trabalho_id": aluno_vectors[j]["trabalho_id"]},
                    "similaridade": sim,
                    "features_comuns": features_comuns[:5],
                })
    pares_similares.sort(key=lambda p: p["similaridade"], reverse=True)

    return {
        "heatmap": heatmap,
        "pares_similares": pares_similares,
        "distribuicao": distribuicao,
        "feature_labels": FEATURE_LABELS,
    }
