import Link from "next/link";
import { api, apiFetch, Fonte, Desfecho } from "@/lib/api";
import AnalisarButton from "@/components/AnalisarButton";
import ValidarFontesButton from "@/components/ValidarFontesButton";
import GerarRoteiroButton from "@/components/GerarRoteiroButton";
import DesfechoForm from "@/components/DesfechoForm";
import GDocsPanel from "@/components/GDocsPanel";

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
  normal:   "text-[#2d7a4f]",
  atencao:  "text-[#d97706]",
  destaque: "text-[#dc2626]",
};

const STATUS_BG: Record<string, string> = {
  normal:   "bg-[#edf7f1] border-[#2d7a4f]",
  atencao:  "bg-[#fef3c7] border-[#d97706]",
  destaque: "bg-[#fef2f2] border-[#dc2626]",
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
        <p className="text-[#78716c]">Trabalho não encontrado.</p>
      </div>
    );
  }

  let analise: Analise | null = null;
  try {
    analise = await apiFetch<Analise>(`/analise/${trabalhoId}`);
  } catch {}

  let fontes: Fonte[] = [];
  try {
    fontes = await api.fontes.get(trabalhoId);
  } catch {}

  let desfecho: Desfecho | null = null;
  try {
    desfecho = await api.desfecho.get(trabalhoId);
  } catch {}

  let gdocs = null;
  try {
    gdocs = await apiFetch(`/gdocs/${trabalhoId}`);
  } catch {}

  const paragrafosTexto = trabalho.texto
    ? trabalho.texto.split("\n\n").filter(Boolean)
    : [];

  const paragrafosDestacadosIdx = new Set(
    analise?.paragrafos_destacados.map((p) => p.indice) ?? []
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-3 text-[#78716c]">
        <Link href="/dashboard" className="hover:underline hover:text-[#2d7a4f]">Turmas</Link>
        {" / "}
        <Link href={`/aluno/${trabalho.aluno_id}`} className="hover:underline hover:text-[#2d7a4f]">Aluno</Link>
        {" / "}
        <span className="text-[#1c1917] font-medium">{trabalho.titulo}</span>
      </div>

      <div className="flex items-start justify-between mb-7">
        <div>
          <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "Georgia, serif" }}>
            {trabalho.titulo}
          </h1>
          <p className="text-[#78716c]">
            {trabalho.tipo} · .{trabalho.formato_origem} ·{" "}
            {new Date(trabalho.data_entrega).toLocaleDateString("pt-BR")}
          </p>
        </div>
        {trabalho.baseline && (
          <span className="text-sm bg-[#2d7a4f] text-white px-4 py-1.5 rounded-full font-semibold">
            baseline
          </span>
        )}
      </div>

      {/* Contadores */}
      <div className="flex gap-4 mb-7">
        {[
          { label: "Normais",   value: analise?.normais ?? "—",    color: "text-[#2d7a4f]" },
          { label: "Atenção",   value: analise?.atencao ?? "—",    color: "text-[#d97706]" },
          { label: "Conversar", value: analise?.destaque ?? "—",   color: "text-[#dc2626]" },
          {
            label: "Fontes",
            value: analise ? `${analise.fontes_verificadas}/${analise.fontes_total}` : "—",
            color: "text-[#1c1917]",
          },
        ].map((item) => (
          <div key={item.label} className="border-2 border-[#e5e1da] bg-white rounded-xl px-5 py-4 text-center min-w-[90px]">
            <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
            <div className="text-sm text-[#78716c] mt-1 font-medium">{item.label}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-3 mb-8">
        <AnalisarButton trabalhoId={trabalhoId} />
        <ValidarFontesButton trabalhoId={trabalhoId} />
        {analise && <GerarRoteiroButton trabalhoId={trabalhoId} />}
        {analise && (
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001"}/export/${trabalhoId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            download={`sume-dossie-${trabalhoId}.pdf`}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-[#1e4d2b] hover:bg-[#2d7a4f] transition-colors"
          >
            Exportar PDF
          </a>
        )}
        <DesfechoForm
          trabalhoId={trabalhoId}
          desfechoAtual={desfecho ? { status: desfecho.status, nota: desfecho.nota } : null}
        />
      </div>

      {desfecho && (
        <div className={`mb-7 border-2 rounded-xl px-5 py-4 flex items-start gap-3 ${
          desfecho.status === "esclarecido"
            ? "bg-[#edf7f1] border-[#2d7a4f]"
            : desfecho.status === "conversa_realizada"
            ? "bg-[#fef3c7] border-[#d97706]"
            : "bg-[#fef2f2] border-[#dc2626]"
        }`}>
          <div>
            <p className={`font-bold ${
              desfecho.status === "esclarecido"
                ? "text-[#2d7a4f]"
                : desfecho.status === "conversa_realizada"
                ? "text-[#d97706]"
                : "text-[#dc2626]"
            }`}>
              Desfecho:{" "}
              {desfecho.status === "esclarecido"
                ? "Esclarecido"
                : desfecho.status === "conversa_realizada"
                ? "Conversa realizada"
                : "Em acompanhamento"}
            </p>
            {desfecho.nota && (
              <p className="text-[#1c1917] mt-1">{desfecho.nota}</p>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Desvios estilométricos */}
        {analise && analise.desvios.length > 0 && (
          <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6">
            <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
              Evidências estilométricas
            </h2>
            <div className="space-y-2">
              {analise.desvios
                .filter((d) => d.status !== "normal")
                .sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score))
                .map((d) => (
                  <div
                    key={d.nome}
                    className={`border-2 rounded-lg px-4 py-3 ${STATUS_BG[d.status]}`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-[#1c1917]">{d.label}</span>
                      <span className={`font-bold ${STATUS_COR[d.status]}`}>
                        z = {d.z_score > 0 ? "+" : ""}{d.z_score}
                      </span>
                    </div>
                    <div className="text-sm text-[#78716c] mt-1">
                      valor: {d.valor.toFixed(2)} · baseline: {d.media_baseline.toFixed(2)}
                    </div>
                  </div>
                ))}
              {analise.desvios.every((d) => d.status === "normal") && (
                <p className="text-[#2d7a4f] font-medium">Todas as métricas dentro do padrão.</p>
              )}
            </div>
          </div>
        )}

        {/* Parágrafos que destoam internamente */}
        {analise && analise.paragrafos_destacados.length > 0 && (
          <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6">
            <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
              Parágrafos que destoam do próprio texto
            </h2>
            <div className="space-y-3">
              {analise.paragrafos_destacados.map((p) => (
                <div key={p.indice} className="border-2 border-[#d97706] bg-[#fef3c7] rounded-lg px-4 py-3">
                  <p className="font-bold text-[#d97706] mb-1">
                    Parágrafo {p.indice + 1}
                  </p>
                  <p className="text-sm text-[#1c1917] italic mb-2">"{p.texto_resumo}"</p>
                  <div className="flex flex-wrap gap-1">
                    {p.features_destoantes.map((f) => (
                      <span key={f.label} className="text-sm bg-white border border-[#d97706] text-[#d97706] px-2 py-0.5 rounded-full font-medium">
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

      {/* Painel de fontes */}
      {fontes.length > 0 && (
        <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6 mb-8">
          <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
            Fontes citadas —{" "}
            <span className="text-[#2d7a4f]">{fontes.filter(f => f.status === "verde").length} verificadas</span>
            {" · "}
            <span className="text-[#d97706]">{fontes.filter(f => f.status === "amarelo").length} precárias</span>
            {" · "}
            <span className="text-[#dc2626]">{fontes.filter(f => f.status === "vermelho").length} problemáticas</span>
          </h2>
          <div className="space-y-2">
            {fontes.map((f) => (
              <div
                key={f.id}
                className={`border-2 rounded-lg px-4 py-3 flex items-start gap-3 ${
                  f.status === "verde"
                    ? "bg-[#edf7f1] border-[#2d7a4f]"
                    : f.status === "vermelho"
                    ? "bg-[#fef2f2] border-[#dc2626]"
                    : "bg-[#fef3c7] border-[#d97706]"
                }`}
              >
                <span
                  className={`mt-1 w-3 h-3 rounded-full flex-shrink-0 ${
                    f.status === "verde"
                      ? "bg-[#2d7a4f]"
                      : f.status === "vermelho"
                      ? "bg-[#dc2626]"
                      : "bg-[#d97706]"
                  }`}
                />
                <div className="min-w-0">
                  <p className="font-semibold text-[#1c1917] truncate">
                    {f.texto_original}
                  </p>
                  {f.justificativa && (
                    <p className="text-sm text-[#78716c] mt-0.5">{f.justificativa}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <GDocsPanel trabalhoId={trabalhoId} dadosIniciais={gdocs} />

      {/* Texto do trabalho */}
      <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-7">
        <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-5">
          Texto completo
        </h2>
        {paragrafosTexto.length > 0 ? (
          <div className="space-y-5">
            {paragrafosTexto.map((p, i) => (
              <p
                key={i}
                className={`leading-relaxed rounded-lg px-2 -mx-2 transition-colors ${
                  paragrafosDestacadosIdx.has(i)
                    ? "bg-[#fef3c7] border-l-4 border-[#d97706] pl-4"
                    : "text-[#1c1917]"
                }`}
                style={{ fontFamily: "Georgia, serif" }}
              >
                {p}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-[#78716c] italic">Texto não disponível.</p>
        )}
      </div>
    </div>
  );
}
