import Link from "next/link";
import { api, apiFetch, Fonte, Desfecho } from "@/lib/api";
import AnalisarButton from "@/components/AnalisarButton";
import ValidarFontesButton from "@/components/ValidarFontesButton";
import GerarRoteiroButton from "@/components/GerarRoteiroButton";
import DesfechoForm from "@/components/DesfechoForm";
import GDocsPanel from "@/components/GDocsPanel";
import AnaliseDonut from "@/components/AnaliseDonut";
import EvidenciasPanel from "@/components/EvidenciasPanel";
import TourTrabalho from "@/components/tour/TourTrabalho";

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
  let fontesValidadas = false;
  try {
    const resp = await api.fontes.get(trabalhoId);
    fontes = resp.fontes;
    fontesValidadas = resp.validado;
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
      {/* Breadcrumb */}
      <div className="mb-3 text-[#78716c]">
        <Link href="/dashboard" className="hover:underline hover:text-[#2d7a4f]">Turmas</Link>
        {" / "}
        <Link href={`/aluno/${trabalho.aluno_id}`} className="hover:underline hover:text-[#2d7a4f]">Aluno</Link>
        {" / "}
        <span className="text-[#1c1917] font-medium">{trabalho.titulo}</span>
      </div>

      <TourTrabalho />

      {/* Título + botões (esquerda) e gráfico (direita) */}
      <div className="flex items-start gap-5 mb-7">
        <div className="flex-1 min-w-0">
          <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "Georgia, serif" }}>
            {trabalho.titulo}
          </h1>
          <p className="text-[#78716c] mb-4">
            {trabalho.tipo} · .{trabalho.formato_origem} ·{" "}
            {new Date(trabalho.data_entrega).toLocaleDateString("pt-BR")}
            {trabalho.baseline && (
              <span className="ml-3 text-sm bg-[#2d7a4f] text-white px-3 py-0.5 rounded-full font-semibold">
                linha de base
              </span>
            )}
          </p>
          <div className="flex flex-wrap gap-3">
            <span data-tour="btn-analisar"><AnalisarButton trabalhoId={trabalhoId} /></span>
            <span data-tour="btn-validar-fontes"><ValidarFontesButton trabalhoId={trabalhoId} /></span>
            {analise && <span data-tour="btn-roteiro"><GerarRoteiroButton trabalhoId={trabalhoId} /></span>}
            {analise && (
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001"}/export/${trabalhoId}/pdf`}
                target="_blank"
                rel="noopener noreferrer"
                download={`sume-dossie-${trabalhoId}.pdf`}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-[#c0392b] hover:bg-[#a93226] transition-colors"
              >
                Exportar PDF
              </a>
            )}
            <span data-tour="btn-desfecho">
              <DesfechoForm
                trabalhoId={trabalhoId}
                desfechoAtual={desfecho ? { status: desfecho.status, nota: desfecho.nota } : null}
              />
            </span>
          </div>
        </div>
        {analise && (
          <div data-tour="donut-chart" className="flex-shrink-0 w-44 border-2 border-[#e5e1da] bg-white rounded-xl p-3">
            <AnaliseDonut
              normais={analise.normais}
              atencao={analise.atencao}
              destaque={analise.destaque}
            />
          </div>
        )}
      </div>

      {/* Banner de desfecho registrado */}
      {desfecho && (
        <div className={`mb-7 border-2 rounded-xl px-5 py-4 ${
          desfecho.status === "esclarecido"
            ? "bg-[#edf7f1] border-[#2d7a4f]"
            : desfecho.status === "conversa_realizada"
            ? "bg-[#fef3c7] border-[#d97706]"
            : "bg-[#fef2f2] border-[#dc2626]"
        }`}>
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
      )}

      {/* Fontes — sem box, inline */}
      {fontesValidadas && (
        <div className="mb-8">
          <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-3 text-sm">
            {fontes.length > 0 ? (
              <>
                Fontes citadas —{" "}
                <span className="text-[#2d7a4f]">{fontes.filter(f => f.status === "verde").length} verificadas</span>
                {" · "}
                <span className="text-[#d97706]">{fontes.filter(f => f.status === "amarelo").length} precárias</span>
                {" · "}
                <span className="text-[#dc2626]">{fontes.filter(f => f.status === "vermelho").length} problemáticas</span>
              </>
            ) : (
              "Fontes citadas"
            )}
          </h2>
          {fontes.length === 0 ? (
            <p className="text-sm text-[#78716c] italic">
              Nenhuma fonte identificada — o texto não contém URLs, DOIs ou citações no formato (Autor, ano).
            </p>
          ) : (
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
                  <span className={`mt-1 w-3 h-3 rounded-full flex-shrink-0 ${
                    f.status === "verde" ? "bg-[#2d7a4f]" : f.status === "vermelho" ? "bg-[#dc2626]" : "bg-[#d97706]"
                  }`} />
                  <div className="min-w-0">
                    <p className="font-semibold text-[#1c1917] truncate">{f.texto_original}</p>
                    {f.justificativa && (
                      <p className="text-sm text-[#78716c] mt-0.5">{f.justificativa}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {analise && (
        <div data-tour="evidencias-panel">
        <EvidenciasPanel
          desvios={analise.desvios}
          normais={analise.normais}
          atencao={analise.atencao}
          destaque={analise.destaque}
        />
        </div>
      )}

      {gdocs && <GDocsPanel trabalhoId={trabalhoId} dadosIniciais={gdocs} />}

      {/* Texto completo com parágrafos destacados */}
      <div data-tour="texto-completo" className="border-2 border-[#e5e1da] bg-white rounded-xl p-7">
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
