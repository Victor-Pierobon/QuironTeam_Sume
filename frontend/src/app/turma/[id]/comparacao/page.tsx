import Link from "next/link";
import { apiFetch } from "@/lib/api";
import HeatmapTurma from "@/components/HeatmapTurma";
import ListaParesSimilares from "@/components/ListaParesSimilares";

interface ComparacaoData {
  heatmap: {
    aluno_id: number;
    aluno_nome: string;
    trabalho_id: number;
    trabalho_titulo: string;
    z_scores: Record<string, number>;
  }[];
  pares_similares: {
    aluno_a: { id: number; nome: string; trabalho_id: number };
    aluno_b: { id: number; nome: string; trabalho_id: number };
    similaridade: number;
    features_comuns: { nome: string; label: string; z_a: number; z_b: number }[];
  }[];
  feature_labels: Record<string, string>;
}

export default async function ComparacaoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const turmaId = Number(id);

  let dados: ComparacaoData | null = null;
  try {
    dados = await apiFetch<ComparacaoData>(`/turmas/${turmaId}/comparacao`);
  } catch {}

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-3 text-[#78716c]">
        <Link href="/dashboard" className="hover:underline hover:text-[#2d7a4f]">Turmas</Link>
        {" / "}
        <Link href={`/turma/${turmaId}`} className="hover:underline hover:text-[#2d7a4f]">Turma</Link>
        {" / "}
        <span className="text-[#1c1917] font-medium">Comparação</span>
      </div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "Georgia, serif" }}>
          Comparação entre alunos
        </h1>
        <p className="text-[#78716c]">
          Padrões estilométricos coletivos — baseado no trabalho mais recente não-baseline de cada aluno.
        </p>
      </div>

      {!dados || dados.heatmap.length === 0 ? (
        <div className="border-2 border-[#e5e1da] rounded-xl px-6 py-10 text-center bg-white">
          <p className="text-[#78716c] text-lg">Nenhum dado disponível.</p>
          <p className="text-[#78716c] mt-1">
            Execute a análise dos trabalhos dos alunos primeiro.
          </p>
        </div>
      ) : (
        <>
          {/* Pares similares */}
          <section className="mb-10">
            <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
              Pares com padrão similar
            </h2>
            <ListaParesSimilares pares={dados.pares_similares} />
          </section>

          {/* Heatmap */}
          <section className="mb-10">
            <h2 className="font-bold text-[#78716c] uppercase tracking-wide mb-4">
              Mapa de desvios por aluno
            </h2>
            <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6">
              <HeatmapTurma
                heatmap={dados.heatmap}
                featureLabels={dados.feature_labels}
              />
            </div>
          </section>

          <p className="text-sm text-[#78716c] italic border-l-4 border-[#e5e1da] pl-4">
            Esta análise identifica padrões coletivos, não acusa individualmente.
            Use os pares similares como ponto de partida para uma conversa pedagógica,
            não como prova formal.
          </p>
        </>
      )}
    </div>
  );
}
