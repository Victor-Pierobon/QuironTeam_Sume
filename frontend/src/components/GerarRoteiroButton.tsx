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
      <div className="flex flex-col gap-2">
        <button
          onClick={relatorio ? () => setAberto(true) : handleGerar}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-[#1c1917] text-white font-semibold hover:bg-[#374151] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Gerando roteiro…" : relatorio ? "Ver roteiro de conversa" : "Gerar roteiro de conversa"}
        </button>
        {erro && <p className="text-sm text-[#dc2626]">{erro}</p>}
      </div>

      {aberto && relatorio && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setAberto(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[88vh] overflow-y-auto p-7"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ fontFamily: "Georgia, serif" }}>
                Roteiro de conversa
              </h2>
              <button
                onClick={() => setAberto(false)}
                className="text-[#78716c] hover:text-[#1c1917] text-xl font-bold w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#f7f4ef] transition-colors"
              >
                ✕
              </button>
            </div>

            <section className="mb-6">
              <h3 className="font-bold text-[#78716c] uppercase tracking-wide mb-3">
                O que os dados mostram
              </h3>
              <p className="text-[#1c1917] leading-relaxed" style={{ fontFamily: "Georgia, serif" }}>
                {relatorio.observacoes}
              </p>
            </section>

            <section className="mb-6">
              <h3 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
                Perguntas para fazer ao aluno
              </h3>
              <ol className="space-y-4">
                {relatorio.perguntas_socraticas.map((p, i) => (
                  <li key={i} className="flex gap-4">
                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2d7a4f] text-white text-sm flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    <p className="text-[#1c1917] leading-relaxed" style={{ fontFamily: "Georgia, serif" }}>
                      {p}
                    </p>
                  </li>
                ))}
              </ol>
            </section>

            <section className="bg-[#f7f4ef] border-2 border-[#e5e1da] rounded-xl p-5">
              <h3 className="font-bold text-[#78716c] uppercase tracking-wide mb-3">
                Como conduzir a conversa
              </h3>
              <p className="text-[#1c1917] leading-relaxed" style={{ fontFamily: "Georgia, serif" }}>
                {relatorio.roteiro_conversa}
              </p>
            </section>

            <div className="mt-6 text-center">
              <button
                onClick={() => setAberto(false)}
                className="px-8 py-2.5 rounded-xl border-2 border-[#e5e1da] text-[#78716c] font-semibold hover:bg-[#f7f4ef] transition-colors"
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
