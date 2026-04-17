"use client";

import Link from "next/link";

interface ParSimilar {
  aluno_a: { id: number; nome: string; trabalho_id: number };
  aluno_b: { id: number; nome: string; trabalho_id: number };
  similaridade: number;
  features_comuns: { nome: string; label: string; z_a: number; z_b: number }[];
}

interface Props {
  pares: ParSimilar[];
}

export default function ListaParesSimilares({ pares }: Props) {
  if (pares.length === 0) {
    return (
      <div className="border-2 border-[#e5e1da] rounded-xl px-6 py-8 text-center bg-white">
        <p className="text-[#2d7a4f] font-semibold text-lg">Nenhum par com similaridade acima de 90%</p>
        <p className="text-[#78716c] mt-1">Os trabalhos da turma apresentam estilos distintos entre si.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {pares.map((par, i) => {
        const pct = Math.round(par.similaridade * 100);
        const cor = pct >= 97 ? "border-[#dc2626] bg-[#fef2f2]" : "border-[#d97706] bg-[#fef3c7]";
        const corTexto = pct >= 97 ? "text-[#dc2626]" : "text-[#d97706]";
        return (
          <div key={i} className={`border-2 rounded-xl px-6 py-5 ${cor}`}>
            <div className="flex items-center justify-between mb-3 flex-wrap gap-3">
              <div className="flex items-center gap-3 flex-wrap">
                <Link href={`/trabalho/${par.aluno_a.trabalho_id}`} className="font-bold text-[#1c1917] hover:underline hover:text-[#2d7a4f]">
                  {par.aluno_a.nome}
                </Link>
                <span className="text-[#78716c]">e</span>
                <Link href={`/trabalho/${par.aluno_b.trabalho_id}`} className="font-bold text-[#1c1917] hover:underline hover:text-[#2d7a4f]">
                  {par.aluno_b.nome}
                </Link>
              </div>
              <span className={`text-2xl font-bold ${corTexto}`}>{pct}% similar</span>
            </div>
            {par.features_comuns.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-[#78716c] mb-2">Padrões em comum:</p>
                <div className="flex flex-wrap gap-2">
                  {par.features_comuns.map((f) => (
                    <span
                      key={f.nome}
                      className="text-sm bg-white border border-current px-3 py-1 rounded-full font-medium text-[#d97706]"
                      title={`${par.aluno_a.nome}: z=${f.z_a > 0 ? "+" : ""}${f.z_a}  |  ${par.aluno_b.nome}: z=${f.z_b > 0 ? "+" : ""}${f.z_b}`}
                    >
                      {f.label}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
