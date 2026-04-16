import Link from "next/link";
import { api, Trabalho, Trajetoria } from "@/lib/api";
import TrajetoriaChart from "@/components/TrajetoriaChart";

export default async function AlunoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const alunoId = Number(id);

  let aluno;
  let trabalhos: Trabalho[] = [];
  let trajetoria: Trajetoria | null = null;

  try {
    [aluno, trabalhos] = await Promise.all([
      api.alunos.get(alunoId),
      api.trabalhos.porAluno(alunoId),
    ]);
  } catch {
    return (
      <div className="max-w-4xl mx-auto">
        <p className="text-[#6b5c40]">Aluno não encontrado.</p>
      </div>
    );
  }

  try {
    trajetoria = await api.trajetoria.get(alunoId);
  } catch {
    // Sem textos suficientes ainda
  }

  const baselines = trabalhos.filter((t) => t.baseline);
  const naoBaseline = trabalhos.filter((t) => !t.baseline);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-2 text-sm text-[#6b5c40]">
        <Link href="/dashboard" className="hover:underline">Turmas</Link>
        {" / "}
        <Link href={`/turma/${aluno.turma_id}`} className="hover:underline">Turma</Link>
        {" / "}
        <span>{aluno.nome}</span>
      </div>

      <h1 className="text-3xl font-bold mb-1" style={{ fontFamily: "Georgia, serif" }}>
        {aluno.nome}
      </h1>
      {aluno.matricula && (
        <p className="text-[#6b5c40] text-sm mb-6">Matrícula: {aluno.matricula}</p>
      )}

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="border border-[#e8e0d0] bg-white rounded-lg p-4">
          <div className="text-2xl font-bold text-[#4a7c59]">{baselines.length}</div>
          <div className="text-sm text-[#6b5c40] mt-1">textos de baseline</div>
          {baselines.length < 3 && (
            <div className="text-xs text-[#c8860a] mt-2">
              Mínimo recomendado: 3 textos
            </div>
          )}
        </div>
        <div className="border border-[#e8e0d0] bg-white rounded-lg p-4">
          <div className="text-2xl font-bold text-[#2c2416]">{naoBaseline.length}</div>
          <div className="text-sm text-[#6b5c40] mt-1">trabalhos analisados</div>
        </div>
      </div>

      {baselines.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3" style={{ fontFamily: "Georgia, serif" }}>
            Baseline confiável
          </h2>
          <div className="space-y-2">
            {baselines.map((t) => (
              <TrabalhoCard key={t.id} trabalho={t} />
            ))}
          </div>
        </section>
      )}

      {naoBaseline.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3" style={{ fontFamily: "Georgia, serif" }}>
            Trabalhos entregues
          </h2>
          <div className="space-y-2">
            {naoBaseline.map((t) => (
              <TrabalhoCard key={t.id} trabalho={t} />
            ))}
          </div>
        </section>
      )}

      {trabalhos.length === 0 && (
        <div className="border border-[#e8e0d0] rounded-lg p-8 text-center text-[#6b5c40]">
          <p>Nenhum trabalho enviado ainda.</p>
        </div>
      )}

      {trajetoria && trajetoria.textos.length >= 2 && (
        <section className="mt-8">
          <TrajetoriaChart data={trajetoria} />
        </section>
      )}
    </div>
  );
}

function TrabalhoCard({ trabalho }: { trabalho: Trabalho }) {
  return (
    <Link href={`/trabalho/${trabalho.id}`}>
      <div className="border border-[#e8e0d0] bg-white rounded-lg px-5 py-3 flex items-center justify-between hover:border-[#4a7c59] hover:shadow-sm transition-all cursor-pointer">
        <div>
          <span className="font-medium">{trabalho.titulo}</span>
          <span className="ml-3 text-sm text-[#6b5c40]">{trabalho.tipo}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#6b5c40]">
            {new Date(trabalho.data_entrega).toLocaleDateString("pt-BR")}
          </span>
          <span className="text-xs uppercase text-[#6b5c40] font-mono">
            .{trabalho.formato_origem}
          </span>
          {trabalho.baseline && (
            <span className="text-xs bg-[#4a7c59] text-white px-2 py-0.5 rounded-full">
              baseline
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
