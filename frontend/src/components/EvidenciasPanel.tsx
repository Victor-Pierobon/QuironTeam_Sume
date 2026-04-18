"use client";

import { useState } from "react";

interface Desvio {
  nome: string;
  label: string;
  valor: number;
  media_baseline: number;
  z_score: number;
  status: "normal" | "atencao" | "destaque";
}

interface Props {
  desvios: Desvio[];
  normais: number;
  atencao: number;
  destaque: number;
}

const STATUS_BG: Record<string, string> = {
  normal:   "bg-[#edf7f1] border-[#2d7a4f]",
  atencao:  "bg-[#fef3c7] border-[#d97706]",
  destaque: "bg-[#fef2f2] border-[#dc2626]",
};

const STATUS_DOT: Record<string, string> = {
  normal:   "bg-[#2d7a4f]",
  atencao:  "bg-[#d97706]",
  destaque: "bg-[#dc2626]",
};

const FILTROS = [
  { key: "destaque", label: "Conversar", cor: "#dc2626", bgAtivo: "#fef2f2", bordaAtivo: "#dc2626", bgInativo: "white", textoCor: "#dc2626" },
  { key: "atencao",  label: "Atenção",   cor: "#d97706", bgAtivo: "#fef3c7", bordaAtivo: "#d97706", bgInativo: "white", textoCor: "#d97706" },
  { key: "normal",   label: "Normais",   cor: "#2d7a4f", bgAtivo: "#edf7f1", bordaAtivo: "#2d7a4f", bgInativo: "white", textoCor: "#2d7a4f" },
] as const;

export default function EvidenciasPanel({ desvios, normais, atencao, destaque }: Props) {
  const [ativos, setAtivos] = useState<Set<string>>(new Set(["destaque"]));

  const contagens: Record<string, number> = { normal: normais, atencao: atencao, destaque: destaque };

  function toggle(key: string) {
    setAtivos((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  }

  const visiveis = desvios
    .filter((d) => ativos.has(d.status))
    .sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score));

  return (
    <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6 mb-8">
      {/* Botões-toggle */}
      <div className="flex gap-3 mb-5">
        {FILTROS.map((f) => {
          const ativo = ativos.has(f.key);
          return (
            <button
              key={f.key}
              onClick={() => toggle(f.key)}
              className="flex-1 rounded-xl border-2 px-4 py-3 text-center transition-all"
              style={{
                borderColor: ativo ? f.bordaAtivo : "#e5e1da",
                backgroundColor: ativo ? f.bgAtivo : "white",
              }}
            >
              <div
                className="text-2xl font-bold"
                style={{ color: f.textoCor }}
              >
                {contagens[f.key]}
              </div>
              <div className="text-sm font-semibold mt-0.5" style={{ color: ativo ? f.cor : "#78716c" }}>
                {f.label}
              </div>
            </button>
          );
        })}
      </div>

      {/* Lista filtrada */}
      <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-3 text-sm">
        Evidências estilométricas
      </h2>

      {visiveis.length === 0 ? (
        <p className="text-[#2d7a4f] font-medium text-sm">
          Nenhuma métrica nesta categoria.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {visiveis.map((d) => (
            <div
              key={d.nome}
              className={`border-2 rounded-lg px-3 py-2.5 ${STATUS_BG[d.status]}`}
            >
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${STATUS_DOT[d.status]}`} />
                <span className="font-semibold text-[#1c1917] text-sm leading-tight">{d.label}</span>
              </div>
              <div className="text-xs text-[#78716c] mt-1.5 pl-4">
                valor: {d.valor.toFixed(2)} · linha de base: {d.media_baseline.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
