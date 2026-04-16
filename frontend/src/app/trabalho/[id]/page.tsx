import Link from "next/link";
import { api, apiFetch } from "@/lib/api";
import AnalisarButton from "@/components/AnalisarButton";

interface Desvio {
  nome: string;
  label: string;
  valor: number;
  media_baseline: number;
  z_score: number;
  status: "normal" | "atencao" | "destaque";
}

interface ParagrafoDestacado {
  indice: number;
  texto_resumo: string;
  features_destoantes: { label: string; z_score: number }[];
}

interface Analise {
  normais: number;
  atencao: number;
  destaque: number;
  fontes_verificadas: number;
  fontes_total: number;
  desvios: Desvio[];
  paragrafos_destacados: ParagrafoDestacado[];
}

const STATUS_COR: Record<string, string> = {
  normal: "text-[#4a7c59]",
  atencao: "text-[#c8860a]",
  destaque: "text-[#8b3a2a]",
};

const STATUS_BG: Record<string, string> = {
  normal: "bg-[#f0f7f2] border-[#4a7c59]",
  atencao: "bg-[#fdf6e8] border-[#c8860a]",
  destaque: "bg-[#fdf0ee] border-[#8b3a2a]",
};

export default async function TrabalhoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const trabalhoId = Number(id);

  let trabalho;
  try {
    trabalho = await api.trabalhos.get(trabalhoId);
  } catch {
    return (
      <div className="max-w-4xl mx-auto">
        <p className="text-[#6b5c40]">Trabalho não encontrado.</p>
      </div>
    );
  }

  let analise: Analise | null = null;
  try {
    analise = await apiFetch<Analise>(`/analise/${trabalhoId}`);
  } catch {
    // No analysis yet
  }

  const paragrafosTexto = trabalho.texto
    ? trabalho.texto.split("\n\n").filter(Boolean)
    : [];

  const paragrafosDestacadosIdx = new Set(
    analise?.paragrafos_destacados.map((p) => p.indice) ?? []
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-2 text-sm text-[#6b5c40]">
        <Link href="/dashboard" className="hover:underline">Turmas</Link>
        {" / "}
        <Link href={`/aluno/${trabalho.aluno_id}`} className="hover:underline">Aluno</Link>
        {" / "}
        <span>{trabalho.titulo}</span>
      </div>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-1" style={{ fontFamily: "Georgia, serif" }}>
            {trabalho.titulo}
          </h1>
          <p className="text-[#6b5c40] text-sm">
            {trabalho.tipo} · .{trabalho.formato_origem} ·{" "}
            {new Date(trabalho.data_entrega).toLocaleDateString("pt-BR")}
          </p>
        </div>
        {trabalho.baseline && (
          <span className="text-sm bg-[#4a7c59] text-white px-3 py-1 rounded-full">
            baseline
          </span>
        )}
      </div>

      {/* Contadores */}
      <div className="flex gap-3 mb-6">
        {[
          { label: "Normais", value: analise?.normais ?? "—", color: "text-[#4a7c59]" },
          { label: "Atenção", value: analise?.atencao ?? "—", color: "text-[#c8860a]" },
          { label: "Conversar", value: analise?.destaque ?? "—", color: "text-[#8b3a2a]" },
          {
            label: "Fontes",
            value: analise ? `${analise.fontes_verificadas}/${analise.fontes_total}` : "—",
            color: "text-[#2c2416]",
          },
        ].map((item) => (
          <div key={item.label} className="border border-[#e8e0d0] bg-white rounded-lg px-4 py-3 text-center min-w-[80px]">
            <div className={`text-xl font-bold ${item.color}`}>{item.value}</div>
            <div className="text-xs text-[#6b5c40] mt-1">{item.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mb-8">
        <AnalisarButton trabalhoId={trabalhoId} />
        <button
          disabled
          className="px-4 py-2 rounded-lg border border-[#e8e0d0] text-[#6b5c40] text-sm font-medium opacity-40 cursor-not-allowed"
        >
          Gerar roteiro de conversa
        </button>
        <button
          disabled
          className="px-4 py-2 rounded-lg border border-[#e8e0d0] text-[#6b5c40] text-sm font-medium opacity-40 cursor-not-allowed"
        >
          Registrar desfecho
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Desvios estilométricos */}
        {analise && analise.desvios.length > 0 && (
          <div className="border border-[#e8e0d0] bg-white rounded-lg p-5">
            <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-4">
              Evidências estilométricas
            </h2>
            <div className="space-y-2">
              {analise.desvios
                .filter((d) => d.status !== "normal")
                .sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score))
                .map((d) => (
                  <div
                    key={d.nome}
                    className={`border rounded-md px-3 py-2 ${STATUS_BG[d.status]}`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-[#2c2416]">{d.label}</span>
                      <span className={`text-xs font-bold ${STATUS_COR[d.status]}`}>
                        z = {d.z_score > 0 ? "+" : ""}{d.z_score}
                      </span>
                    </div>
                    <div className="text-xs text-[#6b5c40] mt-0.5">
                      valor: {d.valor.toFixed(2)} · baseline: {d.media_baseline.toFixed(2)}
                    </div>
                  </div>
                ))}
              {analise.desvios.every((d) => d.status === "normal") && (
                <p className="text-sm text-[#4a7c59]">Todas as features dentro do padrão.</p>
              )}
            </div>
          </div>
        )}

        {/* Parágrafos que destoam internamente */}
        {analise && analise.paragrafos_destacados.length > 0 && (
          <div className="border border-[#e8e0d0] bg-white rounded-lg p-5">
            <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-4">
              Parágrafos que destoam do próprio texto
            </h2>
            <div className="space-y-3">
              {analise.paragrafos_destacados.map((p) => (
                <div key={p.indice} className="border border-[#c8860a] bg-[#fdf6e8] rounded-md px-3 py-2">
                  <p className="text-xs font-semibold text-[#c8860a] mb-1">
                    Parágrafo {p.indice + 1}
                  </p>
                  <p className="text-xs text-[#2c2416] italic mb-2">"{p.texto_resumo}"</p>
                  <div className="flex flex-wrap gap-1">
                    {p.features_destoantes.map((f) => (
                      <span key={f.label} className="text-xs bg-white border border-[#c8860a] text-[#c8860a] px-1.5 py-0.5 rounded">
                        {f.label}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Texto do trabalho com parágrafos destacados */}
      <div className="border border-[#e8e0d0] bg-white rounded-lg p-6">
        <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-4">
          Texto completo
        </h2>
        {paragrafosTexto.length > 0 ? (
          <div className="space-y-4">
            {paragrafosTexto.map((p, i) => (
              <p
                key={i}
                className={`leading-relaxed rounded px-1 -mx-1 transition-colors ${
                  paragrafosDestacadosIdx.has(i)
                    ? "bg-[#fdf6e8] border-l-2 border-[#c8860a] pl-3"
                    : "text-[#2c2416]"
                }`}
                style={{ fontFamily: "Georgia, serif" }}
              >
                {p}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-[#6b5c40] italic">Texto não disponível.</p>
        )}
      </div>
    </div>
  );
}
