"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

const STATUS_OPCOES = [
  { value: "esclarecido",        label: "Esclarecido",        cor: "text-[#2d7a4f]" },
  { value: "conversa_realizada", label: "Conversa realizada", cor: "text-[#d97706]" },
  { value: "em_acompanhamento",  label: "Em acompanhamento",  cor: "text-[#dc2626]" },
];

interface DesfechoExistente {
  status: string;
  nota: string | null;
}

export default function DesfechoForm({
  trabalhoId,
  desfechoAtual,
}: {
  trabalhoId: number;
  desfechoAtual?: DesfechoExistente | null;
}) {
  const [aberto, setAberto] = useState(false);
  const [status, setStatus] = useState(desfechoAtual?.status ?? "esclarecido");
  const [nota, setNota] = useState(desfechoAtual?.nota ?? "");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const router = useRouter();

  async function handleSalvar() {
    setLoading(true);
    setErro(null);
    try {
      const res = await fetch(`${BASE_URL}/desfecho/${trabalhoId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, nota: nota || null }),
      });
      if (!res.ok) throw new Error(await res.text());
      setAberto(false);
      router.refresh();
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao salvar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setAberto(true)}
        className="px-5 py-2.5 rounded-xl border-2 border-[#e5e1da] text-[#78716c] font-semibold hover:bg-[#f7f4ef] transition-colors"
      >
        {desfechoAtual ? "Editar desfecho" : "Registrar desfecho"}
      </button>

      {aberto && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setAberto(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-7"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ fontFamily: "Georgia, serif" }}>
                Registrar desfecho
              </h2>
              <button
                onClick={() => setAberto(false)}
                className="text-[#78716c] hover:text-[#1c1917] text-xl font-bold w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#f7f4ef] transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="mb-5">
              <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-3">
                O que aconteceu após a análise?
              </label>
              <div className="space-y-3">
                {STATUS_OPCOES.map((op) => (
                  <label key={op.value} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="radio"
                      name="status"
                      value={op.value}
                      checked={status === op.value}
                      onChange={() => setStatus(op.value)}
                      className="accent-[#2d7a4f] w-5 h-5"
                    />
                    <span className={`font-semibold ${op.cor}`}>{op.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-3">
                Anotação livre (opcional)
              </label>
              <textarea
                value={nota}
                onChange={(e) => setNota(e.target.value)}
                rows={3}
                placeholder="Como foi a conversa? O aluno explicou o trabalho?"
                className="w-full border-2 border-[#e5e1da] rounded-xl px-4 py-3 bg-white text-[#1c1917] resize-none focus:outline-none focus:border-[#2d7a4f] transition-colors"
              />
            </div>

            {erro && <p className="text-sm text-[#dc2626] mb-4">{erro}</p>}

            <div className="flex gap-3">
              <button
                onClick={handleSalvar}
                disabled={loading}
                className="flex-1 py-3 rounded-xl bg-[#2d7a4f] text-white font-bold hover:bg-[#25673e] disabled:opacity-50 transition-colors"
              >
                {loading ? "Salvando…" : "Salvar"}
              </button>
              <button
                onClick={() => setAberto(false)}
                className="px-5 py-3 rounded-xl border-2 border-[#e5e1da] text-[#78716c] font-semibold hover:bg-[#f7f4ef] transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
