"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { useState } from "react";

interface TextoFeatures {
  id: number;
  titulo: string;
  baseline: boolean;
  data_entrega: string;
  features: Record<string, number>;
}

interface TrajetoriaData {
  textos: TextoFeatures[];
  feature_labels: Record<string, string>;
}

// Features que indicam desenvolvimento — direção positiva (1) ou negativa (-1)
const DEVELOPMENTAL: Record<string, 1 | -1> = {
  avg_sentence_length:      1,
  avg_paragraph_length:     1,
  syntactic_depth:          1,
  lexical_diversity:        1,
  avg_word_length:          1,
  rare_words_pct:           1,
  connective_density:       1,
  spelling_errors_per_1000: -1,
  agreement_errors_per_1000: -1,
};

const CORES_AVANCADO = [
  "#2d7a4f", "#d97706", "#dc2626", "#2563eb",
  "#7c3aed", "#0891b2", "#db2777", "#059669",
];

// Features destacadas no modo avançado por padrão
const FEATURES_PADRAO = [
  "lexical_diversity",
  "avg_sentence_length",
  "connective_density",
  "readability_index",
];

/** Calcula o índice de desenvolvimento (0-100) para cada texto */
function calcularIndice(textos: TextoFeatures[]): number[] {
  if (textos.length === 0) return [];

  const feats = Object.keys(DEVELOPMENTAL) as Array<keyof typeof DEVELOPMENTAL>;

  // Intervalo de cada feature em todos os textos
  const ranges: Record<string, { min: number; max: number }> = {};
  for (const f of feats) {
    const vals = textos.map((t) => t.features[f] ?? 0);
    ranges[f] = { min: Math.min(...vals), max: Math.max(...vals) };
  }

  return textos.map((t) => {
    const scores = feats.map((f) => {
      const { min, max } = ranges[f];
      if (max === min) return 50;
      const norm = ((t.features[f] ?? min) - min) / (max - min) * 100;
      return DEVELOPMENTAL[f] === 1 ? norm : 100 - norm;
    });
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  });
}

export default function TrajetoriaChart({ data }: { data: TrajetoriaData }) {
  const { textos, feature_labels } = data;
  const [avancado, setAvancado] = useState(false);
  const [selecionadas, setSelecionadas] = useState<string[]>(
    FEATURES_PADRAO.filter((f) => Object.keys(feature_labels).includes(f))
  );

  if (textos.length < 2) {
    return (
      <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6">
        <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-2">
          Trajetória de desenvolvimento
        </h2>
        <p className="text-[#78716c] italic">
          São necessários pelo menos 2 textos para exibir a trajetória.
        </p>
      </div>
    );
  }

  const textosOrdenados = textos
    .slice()
    .sort((a, b) => new Date(a.data_entrega).getTime() - new Date(b.data_entrega).getTime());

  const indices = calcularIndice(textosOrdenados);

  // Dados para o modo simples (nota média)
  const dadosSimples = textosOrdenados.map((t, i) => ({
    name: t.titulo.length > 20 ? t.titulo.slice(0, 20) + "…" : t.titulo,
    baseline: t.baseline,
    indice: indices[i],
  }));

  // Dados para o modo avançado (features individuais)
  const dadosAvancado = textosOrdenados.map((t) => ({
    name: t.titulo.length > 20 ? t.titulo.slice(0, 20) + "…" : t.titulo,
    baseline: t.baseline,
    ...selecionadas.reduce(
      (acc, feat) => ({ ...acc, [feat]: t.features[feat] ?? null }),
      {} as Record<string, number | null>
    ),
  }));

  function toggleFeature(feat: string) {
    setSelecionadas((prev) =>
      prev.includes(feat)
        ? prev.length > 1 ? prev.filter((f) => f !== feat) : prev
        : [...prev, feat]
    );
  }

  const todasFeatures = Object.keys(feature_labels);

  return (
    <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6">
      {/* Cabeçalho */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h2 className="font-bold text-xl mb-1" style={{ fontFamily: "Georgia, serif" }}>
            {avancado ? "Trajetória — métricas individuais" : "Índice de desenvolvimento da escrita"}
          </h2>
          <p className="text-sm text-[#78716c]">
            {avancado
              ? "Selecione as métricas que deseja comparar abaixo."
              : "Média de 9 indicadores de maturidade textual (escala 0–100)."}
          </p>
        </div>
        <button
          onClick={() => setAvancado((v) => !v)}
          className="ml-4 flex-shrink-0 text-sm px-4 py-2 rounded-lg border-2 border-[#2d7a4f] text-[#2d7a4f] font-semibold hover:bg-[#edf7f1] transition-colors"
        >
          {avancado ? "← Visão geral" : "Métricas detalhadas →"}
        </button>
      </div>

      {/* Seletor de features (modo avançado) */}
      {avancado && (
        <div className="flex flex-wrap gap-2 mb-5">
          {todasFeatures.map((feat, i) => {
            const ativo = selecionadas.includes(feat);
            const cor = CORES_AVANCADO[selecionadas.indexOf(feat) % CORES_AVANCADO.length];
            return (
              <button
                key={feat}
                onClick={() => toggleFeature(feat)}
                className={`text-sm px-3 py-1 rounded-full border-2 font-medium transition-colors ${
                  ativo
                    ? "text-white border-transparent"
                    : "text-[#78716c] border-[#e5e1da] hover:border-[#2d7a4f]"
                }`}
                style={ativo ? { backgroundColor: cor, borderColor: cor } : {}}
              >
                {feature_labels[feat]}
              </button>
            );
          })}
        </div>
      )}

      {/* Gráfico */}
      <ResponsiveContainer width="100%" height={400}>
        {avancado ? (
          <LineChart data={dadosAvancado} margin={{ top: 5, right: 20, left: 0, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e1da" />
            <XAxis dataKey="name" tick={{ fontSize: 15, fill: "#78716c" }} angle={-35} textAnchor="end" />
            <YAxis tick={{ fontSize: 15, fill: "#78716c" }} width={52} />
            <Tooltip
              contentStyle={{ backgroundColor: "#fff", border: "2px solid #e5e1da", borderRadius: 10, fontSize: 15 }}
              formatter={(value, name) => [
                typeof value === "number" ? value.toFixed(3) : String(value),
                feature_labels[String(name)] ?? String(name),
              ]}
            />
            <Legend formatter={(v) => feature_labels[v] ?? v} wrapperStyle={{ fontSize: 15, paddingTop: 12 }} />
            {selecionadas.map((feat, i) => (
              <Line
                key={feat}
                type="monotone"
                dataKey={feat}
                stroke={CORES_AVANCADO[i % CORES_AVANCADO.length]}
                strokeWidth={2.5}
                dot={(props) => {
                  const { cx, cy, payload } = props;
                  return (
                    <circle
                      key={`dot-${feat}-${cx}-${cy}`}
                      cx={cx} cy={cy}
                      r={payload.baseline ? 7 : 5}
                      fill={CORES_AVANCADO[i % CORES_AVANCADO.length]}
                      stroke={payload.baseline ? "#1c1917" : "none"}
                      strokeWidth={payload.baseline ? 2.5 : 0}
                    />
                  );
                }}
                connectNulls
              />
            ))}
          </LineChart>
        ) : (
          <LineChart data={dadosSimples} margin={{ top: 5, right: 20, left: 0, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e1da" />
            <XAxis dataKey="name" tick={{ fontSize: 15, fill: "#78716c" }} angle={-35} textAnchor="end" />
            <YAxis domain={[0, 100]} tick={{ fontSize: 15, fill: "#78716c" }} width={52} />
            <ReferenceLine y={50} stroke="#e5e1da" strokeDasharray="4 4" />
            <Tooltip
              contentStyle={{ backgroundColor: "#fff", border: "2px solid #e5e1da", borderRadius: 10, fontSize: 15 }}
              formatter={(value) => [`${value} / 100`, "Índice de desenvolvimento"]}
            />
            <Line
              type="monotone"
              dataKey="indice"
              stroke="#2d7a4f"
              strokeWidth={3}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return (
                  <circle
                    key={`dot-simples-${cx}-${cy}`}
                    cx={cx} cy={cy}
                    r={payload.baseline ? 8 : 6}
                    fill="#2d7a4f"
                    stroke={payload.baseline ? "#1c1917" : "#fff"}
                    strokeWidth={payload.baseline ? 2.5 : 2}
                  />
                );
              }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>

      <p className="text-sm text-[#78716c] mt-3">
        {avancado
          ? "Pontos com borda escura = textos de baseline."
          : "Pontos com borda escura = textos de baseline. Quanto maior o índice, mais desenvolvida a escrita."}
      </p>
    </div>
  );
}
