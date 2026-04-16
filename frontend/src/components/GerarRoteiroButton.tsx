"use client";

import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

interface Relatorio {
  observacoes: string;
  perguntas_socraticas: string[];
  roteiro_conversa: string;
}

export default function GerarRoteiroButton({ trabalhoId }: { trabalhoId: number }) {
  const [loading, setLoading] = useState(false);
  const [relatorio, setRelatorio] = useState<Relatorio | null>(null);
  const [aberto, setAberto] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function handleGerar() {
    setLoading(true);
    setErro(null);
    try {
      const res = await fetch(`${BASE_URL}/relatorio/${trabalhoId}`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setRelatorio(data);
      setAberto(true);
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao gerar roteiro.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="flex flex-col gap-1">
        <button
          onClick={relatorio ? () => setAberto(true) : handleGerar}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-[#2c2416] text-[#f5f0e8] text-sm font-medium hover:bg-[#4a3828] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Gerando roteiro…" : relatorio ? "Ver roteiro de conversa" : "Gerar roteiro de conversa"}
        </button>
        {erro && <p className="text-xs text-[#8b3a2a]">{erro}</p>}
      </div>

      {/* Modal */}
      {aberto && relatorio && (
        <div
          className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
          onClick={() => setAberto(false)}
        >
          <div
            className="bg-[#f5f0e8] rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-xl font-bold" style={{ fontFamily: "Georgia, serif" }}>
                Roteiro de conversa
              </h2>
              <button
                onClick={() => setAberto(false)}
                className="text-[#6b5c40] hover:text-[#2c2416] text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {/* Observações */}
            <section className="mb-6">
              <h3 className="text-xs font-semibold text-[#6b5c40] uppercase tracking-wide mb-2">
                O que os dados mostram
              </h3>
              <p className="text-[#2c2416] leading-relaxed" style={{ fontFamily: "Georgia, serif" }}>
                {relatorio.observacoes}
              </p>
            </section>

            {/* Perguntas socráticas */}
            <section className="mb-6">
              <h3 className="text-xs font-semibold text-[#6b5c40] uppercase tracking-wide mb-3">
                Perguntas para fazer ao aluno
              </h3>
              <ol className="space-y-3">
                {relatorio.perguntas_socraticas.map((p, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[#4a7c59] text-white text-xs flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    <p
                      className="text-[#2c2416] leading-relaxed"
                      style={{ fontFamily: "Georgia, serif" }}
                    >
                      {p}
                    </p>
                  </li>
                ))}
              </ol>
            </section>

            {/* Roteiro */}
            <section className="bg-white border border-[#e8e0d0] rounded-lg p-4">
              <h3 className="text-xs font-semibold text-[#6b5c40] uppercase tracking-wide mb-2">
                Como conduzir a conversa
              </h3>
              <p className="text-[#2c2416] leading-relaxed text-sm" style={{ fontFamily: "Georgia, serif" }}>
                {relatorio.roteiro_conversa}
              </p>
            </section>

            <div className="mt-5 text-center">
              <button
                onClick={() => setAberto(false)}
                className="px-6 py-2 rounded-lg border border-[#e8e0d0] text-[#6b5c40] text-sm hover:bg-[#e8e0d0] transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
