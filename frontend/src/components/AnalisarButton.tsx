"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export default function AnalisarButton({ trabalhoId }: { trabalhoId: number }) {
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const router = useRouter();

  async function handleAnalisar() {
    setLoading(true);
    setErro(null);
    try {
      const res = await fetch(`${BASE_URL}/analise/${trabalhoId}`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      router.refresh();
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao analisar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <button
        onClick={handleAnalisar}
        disabled={loading}
        className="px-5 py-2.5 rounded-xl bg-[#2d7a4f] text-white font-semibold hover:bg-[#25673e] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Analisando…" : "Analisar trabalho"}
      </button>
      {erro && <p className="text-sm text-[#dc2626]">{erro}</p>}
    </div>
  );
}
