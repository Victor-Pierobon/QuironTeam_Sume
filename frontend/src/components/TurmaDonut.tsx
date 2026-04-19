"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

interface Props {
  ok: number;
  atencao: number;
  destaque: number;
}

const FATIAS = [
  { key: "ok",       label: "Normal",    cor: "#2d7a4f" },
  { key: "atencao",  label: "Atenção",   cor: "#d97706" },
  { key: "destaque", label: "Conversar", cor: "#dc2626" },
] as const;

export default function TurmaDonut({ ok, atencao, destaque }: Props) {
  const valores = { ok, atencao, destaque };
  const total = ok + atencao + destaque;

  const dados = FATIAS.filter((f) => valores[f.key] > 0).map((f) => ({
    name: f.label,
    value: valores[f.key],
    cor: f.cor,
  }));

  if (total === 0) return null;

  return (
    <div className="flex items-center gap-8">
      <div className="relative" style={{ width: 160, height: 160 }}>
        <ResponsiveContainer width={160} height={160}>
          <PieChart>
            <Pie
              data={dados}
              cx="50%"
              cy="50%"
              innerRadius={46}
              outerRadius={68}
              paddingAngle={3}
              dataKey="value"
              label={false}
              labelLine={false}
            >
              {dados.map((entry) => (
                <Cell key={entry.name} fill={entry.cor} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e1da",
                borderRadius: 6,
                fontSize: 11,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-3xl font-bold text-[#1c1917]">{total}</span>
          <span className="text-xs text-[#78716c] leading-none mt-0.5">alunos</span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {FATIAS.map((f) => (
          <div key={f.key} className="flex items-center gap-2.5">
            <span className="w-3.5 h-3.5 rounded-full flex-shrink-0" style={{ backgroundColor: f.cor }} />
            <span className="text-base font-bold" style={{ color: f.cor }}>{valores[f.key]}</span>
            <span className="text-base text-[#78716c]">{f.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
