"use client";

import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

interface Padrao {
  nome: string;
  mensagem: string;
  nivel: "atencao" | "destaque";
}

interface Revisao {
  timestamp: string;
  tamanho_chars: number;
  chars_adicionados: number;
  chars_deletados: number;
}

interface GDocsData {
  num_sessoes: number;
  tempo_ativo_min: number;
  maior_insercao_pct: number;
  razao_edicao_adicao: number;
  proporcao_final_colada: number;
  padroes: Padrao[];
  revisoes: Revisao[];
  importado_em: string;
}

interface Props {
  trabalhoId: number;
  dadosIniciais: GDocsData | null;
}

export default function GDocsPanel({ trabalhoId, dadosIniciais }: Props) {
  const [dados, setDados] = useState<GDocsData | null>(dadosIniciais);
  const [url, setUrl] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [mostrarImport, setMostrarImport] = useState(!dadosIniciais);

  async function importar() {
    if (!url.trim()) return;
    setCarregando(true);
    setErro(null);
    try {
      const res = await fetch(`${BASE_URL}/gdocs/${trabalhoId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_url: url.trim() }),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt);
      }
      const result = await res.json();
      // Busca dados completos após importar
      const full = await fetch(`${BASE_URL}/gdocs/${trabalhoId}`);
      setDados(await full.json());
      setMostrarImport(false);
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao importar.");
    } finally {
      setCarregando(false);
    }
  }

  const nivelCor = (nivel: string) =>
    nivel === "destaque"
      ? "bg-[#fef2f2] border-[#dc2626] text-[#dc2626]"
      : "bg-[#fef3c7] border-[#d97706] text-[#d97706]";

  return (
    <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-[#78716c] uppercase tracking-wide">
          Histórico de edição (Google Docs)
        </h2>
        {dados && (
          <button
            onClick={() => setMostrarImport(!mostrarImport)}
            className="text-sm text-[#78716c] hover:text-[#2d7a4f] underline"
          >
            {mostrarImport ? "Cancelar" : "Reimportar"}
          </button>
        )}
      </div>

      {mostrarImport && (
        <div className="mb-5">
          <p className="text-sm text-[#78716c] mb-3">
            Compartilhe o Google Doc com a service account da aplicação e cole o link abaixo.
          </p>
          <div className="flex gap-2">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://docs.google.com/document/d/..."
              className="flex-1 border-2 border-[#e5e1da] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2d7a4f]"
            />
            <button
              onClick={importar}
              disabled={carregando || !url.trim()}
              className="px-5 py-2 rounded-xl font-semibold text-white bg-[#1e4d2b] hover:bg-[#2d7a4f] disabled:opacity-50 transition-colors"
            >
              {carregando ? "Importando…" : "Importar"}
            </button>
          </div>
          {erro && <p className="text-sm text-[#dc2626] mt-2">{erro}</p>}
        </div>
      )}

      {dados ? (
        <>
          {/* Métricas resumo */}
          <div className="flex flex-wrap gap-3 mb-5">
            {[
              { label: "Sessões", value: String(dados.num_sessoes), color: "text-[#1c1917]" },
              { label: "Tempo ativo", value: `${dados.tempo_ativo_min} min`, color: "text-[#1c1917]" },
              {
                label: "Maior inserção",
                value: `${Math.round(dados.maior_insercao_pct * 100)}%`,
                color: dados.maior_insercao_pct > 0.5 ? "text-[#dc2626]" : "text-[#1c1917]",
              },
              {
                label: "Edição/Adição",
                value: dados.razao_edicao_adicao.toFixed(2),
                color: dados.razao_edicao_adicao < 0.05 ? "text-[#d97706]" : "text-[#2d7a4f]",
              },
              {
                label: "Última sessão",
                value: `${Math.round(dados.proporcao_final_colada * 100)}%`,
                color: dados.proporcao_final_colada > 0.6 ? "text-[#dc2626]" : "text-[#1c1917]",
              },
            ].map((item) => (
              <div key={item.label} className="border-2 border-[#e5e1da] rounded-xl px-4 py-3 text-center min-w-[90px]">
                <div className={`text-xl font-bold ${item.color}`}>{item.value}</div>
                <div className="text-xs text-[#78716c] mt-0.5 font-medium">{item.label}</div>
              </div>
            ))}
          </div>

          {/* Padrões detectados */}
          {dados.padroes.length > 0 && (
            <div className="space-y-2 mb-4">
              {dados.padroes.map((p) => (
                <div key={p.nome} className={`border-2 rounded-lg px-4 py-3 ${nivelCor(p.nivel)}`}>
                  <p className="font-semibold">{p.mensagem}</p>
                </div>
              ))}
            </div>
          )}

          {dados.padroes.length === 0 && (
            <p className="text-[#2d7a4f] font-medium">Nenhum padrão suspeito detectado no histórico de edição.</p>
          )}

          <p className="text-xs text-[#78716c] mt-3">
            Importado em {new Date(dados.importado_em).toLocaleDateString("pt-BR")} · {dados.revisoes.length} revisões
          </p>
        </>
      ) : !mostrarImport ? (
        <p className="text-[#78716c] italic text-sm">
          Nenhum histórico importado.{" "}
          <button onClick={() => setMostrarImport(true)} className="underline hover:text-[#2d7a4f]">
            Importar agora
          </button>
        </p>
      ) : null}
    </div>
  );
}
