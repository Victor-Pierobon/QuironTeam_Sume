"use client";

import Link from "next/link";

interface ZScoreRow {
  aluno_id: number;
  aluno_nome: string;
  trabalho_id: number;
  trabalho_titulo: string;
  z_scores: Record<string, number>;
}

interface Props {
  heatmap: ZScoreRow[];
  featureLabels: Record<string, string>;
}

const FEATURED_FEATURES = [
  "lexical_diversity",
  "ai_words_freq",
  "connective_density",
  "avg_sentence_length",
  "spelling_errors_per_1000",
  "agreement_errors_per_1000",
  "readability_index",
  "passive_voice_ratio",
];

function cellColor(z: number): string {
  const abs = Math.abs(z);
  if (abs >= 2.5) return z > 0 ? "bg-[#fef2f2] text-[#dc2626] font-bold" : "bg-[#edf7f1] text-[#2d7a4f] font-bold";
  if (abs >= 1.5) return z > 0 ? "bg-[#fef3c7] text-[#d97706]" : "bg-[#f0fdf4] text-[#16a34a]";
  return "bg-white text-[#78716c]";
}

export default function HeatmapTurma({ heatmap, featureLabels }: Props) {
  if (heatmap.length === 0) {
    return <p className="text-[#78716c] italic">Nenhum dado disponível. Execute as análises dos trabalhos primeiro.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="text-left px-3 py-2 font-semibold text-[#78716c] border-b-2 border-[#e5e1da] min-w-[140px]">
              Aluno
            </th>
            {FEATURED_FEATURES.map((nome) => (
              <th
                key={nome}
                className="px-2 py-2 font-semibold text-[#78716c] border-b-2 border-[#e5e1da] text-center min-w-[90px] whitespace-nowrap"
                title={featureLabels[nome]}
              >
                <span className="text-xs">{(featureLabels[nome] ?? nome).split(" ").slice(0, 2).join(" ")}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {heatmap.map((row) => (
            <tr key={row.aluno_id} className="border-b border-[#e5e1da]">
              <td className="px-3 py-2">
                <Link
                  href={`/trabalho/${row.trabalho_id}`}
                  className="font-semibold text-[#1c1917] hover:text-[#2d7a4f] hover:underline"
                >
                  {row.aluno_nome}
                </Link>
                <p className="text-xs text-[#78716c] truncate max-w-[130px]">{row.trabalho_titulo}</p>
              </td>
              {FEATURED_FEATURES.map((nome) => {
                const z = row.z_scores[nome] ?? 0;
                return (
                  <td key={nome} className={`px-2 py-2 text-center rounded ${cellColor(z)}`} title={`z = ${z > 0 ? "+" : ""}${z}`}>
                    {z > 0 ? "+" : ""}{z.toFixed(1)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-[#78716c] mt-3">
        Valores são z-scores em relação à média da turma. Vermelho = desvio alto; verde = abaixo da média.
      </p>
    </div>
  );
}
