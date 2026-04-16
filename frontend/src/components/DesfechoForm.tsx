"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

const STATUS_OPCOES = [
  { value: "esclarecido", label: "Esclarecido", cor: "text-[#4a7c59]" },
  { value: "conversa_realizada", label: "Conversa realizada", cor: "text-[#c8860a]" },
  { value: "em_acompanhamento", label: "Em acompanhamento", cor: "text-[#8b3a2a]" },
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
        className="px-4 py-2 rounded-lg border border-[#e8e0d0] text-[#6b5c40] text-sm font-medium hover:bg-[#e8e0d0] transition-colors"
      >
        {desfechoAtual ? "Editar desfecho" : "Registrar desfecho"}
      </button>

      {aberto && (
        <div
          className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
          onClick={() => setAberto(false)}
        >
          <div
            className="bg-[#f5f0e8] rounded-xl shadow-2xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-xl font-bold" style={{ fontFamily: "Georgia, serif" }}>
                Registrar desfecho
              </h2>
              <button onClick={() => setAberto(false)} className="text-[#6b5c40] hover:text-[#2c2416] font-bold">
                ✕
              </button>
            </div>

            <div className="mb-4">
              <label className="text-xs font-semibold text-[#6b5c40] uppercase tracking-wide block mb-2">
                O que aconteceu após a análise?
              </label>
              <div className="space-y-2">
                {STATUS_OPCOES.map((op) => (
                  <label key={op.value} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="radio"
                      name="status"
                      value={op.value}
                      checked={status === op.value}
                      onChange={() => setStatus(op.value)}
                      className="accent-[#4a7c59]"
                    />
                    <span className={`text-sm font-medium ${op.cor}`}>{op.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-5">
              <label className="text-xs font-semibold text-[#6b5c40] uppercase tracking-wide block mb-2">
                Anotação livre (opcional)
              </label>
              <textarea
                value={nota}
                onChange={(e) => setNota(e.target.value)}
                rows={3}
                placeholder="Como foi a conversa? O aluno explicou o trabalho?"
                className="w-full border border-[#e8e0d0] rounded-lg px-3 py-2 text-sm bg-white text-[#2c2416] resize-none focus:outline-none focus:border-[#4a7c59]"
              />
            </div>

            {erro && <p className="text-xs text-[#8b3a2a] mb-3">{erro}</p>}

            <div className="flex gap-3">
              <button
                onClick={handleSalvar}
                disabled={loading}
                className="flex-1 py-2 rounded-lg bg-[#4a7c59] text-white text-sm font-medium hover:bg-[#3d6b4a] disabled:opacity-50 transition-colors"
              >
                {loading ? "Salvando…" : "Salvar"}
              </button>
              <button
                onClick={() => setAberto(false)}
                className="px-4 py-2 rounded-lg border border-[#e8e0d0] text-[#6b5c40] text-sm hover:bg-[#e8e0d0] transition-colors"
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
