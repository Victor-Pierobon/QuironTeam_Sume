import Link from "next/link";
import { api } from "@/lib/api";

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

  const paragrafos = trabalho.texto
    ? trabalho.texto.split("\n\n").filter(Boolean)
    : [];

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

      {/* Contadores — serão preenchidos quando a análise estilométrica estiver pronta */}
      <div className="flex gap-3 mb-8">
        {[
          { label: "Normais", value: "—", color: "text-[#4a7c59]" },
          { label: "Atenção", value: "—", color: "text-[#c8860a]" },
          { label: "Conversar", value: "—", color: "text-[#8b3a2a]" },
          { label: "Fontes", value: "—", color: "text-[#2c2416]" },
        ].map((item) => (
          <div key={item.label} className="border border-[#e8e0d0] bg-white rounded-lg px-4 py-3 text-center min-w-[80px]">
            <div className={`text-xl font-bold ${item.color}`}>{item.value}</div>
            <div className="text-xs text-[#6b5c40] mt-1">{item.label}</div>
          </div>
        ))}
      </div>

      {/* Texto do trabalho */}
      <div className="border border-[#e8e0d0] bg-white rounded-lg p-6">
        <h2 className="text-sm font-semibold text-[#6b5c40] uppercase tracking-wide mb-4">
          Texto completo
        </h2>
        {paragrafos.length > 0 ? (
          <div className="space-y-4">
            {paragrafos.map((p, i) => (
              <p
                key={i}
                className="text-[#2c2416] leading-relaxed"
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

      {/* Ações — serão expandidas nos próximos dias */}
      <div className="mt-6 flex gap-3">
        <button
          disabled
          className="px-4 py-2 rounded-lg bg-[#4a7c59] text-white text-sm font-medium opacity-40 cursor-not-allowed"
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
    </div>
  );
}
