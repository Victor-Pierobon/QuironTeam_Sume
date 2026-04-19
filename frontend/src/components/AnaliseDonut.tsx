"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface Props {
  normais: number;
  atencao: number;
  destaque: number;
}

const CORES = ["#2d7a4f", "#d97706", "#dc2626"];
const LABELS = ["Normais", "Atenção", "Conversar"];

export default function AnaliseDonut({ normais, atencao, destaque }: Props) {
  const dados = [
    { name: "Normais",   value: normais },
    { name: "Atenção",   value: atencao },
    { name: "Conversar", value: destaque },
  ].filter((d) => d.value > 0);

  if (dados.length === 0) return null;

  return (
    <div className="flex flex-col items-center w-full gap-3">
      <ResponsiveContainer width="100%" height={160}>
        <PieChart>
          <Pie
            data={dados}
            cx="50%"
            cy="50%"
            innerRadius={42}
            outerRadius={64}
            paddingAngle={3}
            dataKey="value"
            label={false}
            labelLine={false}
          >
            {dados.map((entry) => (
              <Cell key={entry.name} fill={CORES[LABELS.indexOf(entry.name)]} />
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
      <div className="flex justify-center gap-4 flex-wrap">
        {dados.map((entry) => (
          <div key={entry.name} className="flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: CORES[LABELS.indexOf(entry.name)] }}
            />
            <span className="text-sm text-[#78716c] font-medium">{entry.value} {entry.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
