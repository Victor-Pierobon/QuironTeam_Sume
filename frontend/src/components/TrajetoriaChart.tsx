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

// Features more pedagogically interesting to show by default
const FEATURES_PADRAO = [
  "lexical_diversity",
  "avg_sentence_length",
  "connective_density",
  "readability_index",
];

const CORES = [
  "#4a7c59",
  "#c8860a",
  "#8b3a2a",
  "#2c6b8a",
  "#6b2c8a",
  "#2c8a6b",
];

export default function TrajetoriaChart({ data }: { data: TrajetoriaData }) {
  const { textos, feature_labels } = data;

  const todasFeatures = Object.keys(feature_labels);
  const [selecionadas, setSelecionadas] = useState<string[]>(
    FEATURES_PADRAO.filter((f) => todasFeatures.includes(f))
  );

  if (textos.length < 2) {
    return (
      <div className="border border-[#e8e0d0] bg-white rounded-lg p-5">
        <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-2">
          Trajetória estilométrica
        </h2>
        <p className="text-sm text-[#6b5c40] italic">
          São necessários pelo menos 2 textos para exibir a trajetória.
        </p>
      </div>
    );
  }

  // Build chart data: one entry per text, sorted by date
  const chartData = textos
    .slice()
    .sort(
      (a, b) =>
        new Date(a.data_entrega).getTime() - new Date(b.data_entrega).getTime()
    )
    .map((t) => ({
      name:
        t.titulo.length > 18 ? t.titulo.slice(0, 18) + "…" : t.titulo,
      baseline: t.baseline,
      ...selecionadas.reduce(
        (acc, feat) => ({ ...acc, [feat]: t.features[feat] ?? null }),
        {} as Record<string, number | null>
      ),
    }));

  function toggleFeature(feat: string) {
    setSelecionadas((prev) =>
      prev.includes(feat)
        ? prev.length > 1
          ? prev.filter((f) => f !== feat)
          : prev
        : [...prev, feat]
    );
  }

  return (
    <div className="border border-[#e8e0d0] bg-white rounded-lg p-5">
      <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-4">
        Trajetória estilométrica
      </h2>

      {/* Feature selector */}
      <div className="flex flex-wrap gap-2 mb-5">
        {todasFeatures.map((feat, i) => {
          const ativo = selecionadas.includes(feat);
          const cor = CORES[selecionadas.indexOf(feat) % CORES.length];
          return (
            <button
              key={feat}
              onClick={() => toggleFeature(feat)}
              className={`text-xs px-2 py-1 rounded-full border transition-colors ${
                ativo
                  ? "text-white border-transparent"
                  : "text-[#6b5c40] border-[#e8e0d0] hover:border-[#4a7c59]"
              }`}
              style={ativo ? { backgroundColor: cor, borderColor: cor } : {}}
            >
              {feature_labels[feat]}
            </button>
          );
        })}
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 20, left: 0, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e8e0d0" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 10, fill: "#6b5c40" }}
            angle={-35}
            textAnchor="end"
          />
          <YAxis tick={{ fontSize: 10, fill: "#6b5c40" }} width={40} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#f5f0e8",
              border: "1px solid #e8e0d0",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => [
              typeof value === "number" ? value.toFixed(3) : value,
              feature_labels[name] ?? name,
            ]}
          />
          <Legend
            formatter={(value) => feature_labels[value] ?? value}
            wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
          />
          {selecionadas.map((feat, i) => (
            <Line
              key={feat}
              type="monotone"
              dataKey={feat}
              stroke={CORES[i % CORES.length]}
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return (
                  <circle
                    key={`dot-${feat}-${cx}-${cy}`}
                    cx={cx}
                    cy={cy}
                    r={payload.baseline ? 6 : 4}
                    fill={CORES[i % CORES.length]}
                    stroke={payload.baseline ? "#2c2416" : "none"}
                    strokeWidth={payload.baseline ? 2 : 0}
                  />
                );
              }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <p className="text-xs text-[#6b5c40] mt-2">
        Pontos com borda escura = textos de baseline.
      </p>
    </div>
  );
}
