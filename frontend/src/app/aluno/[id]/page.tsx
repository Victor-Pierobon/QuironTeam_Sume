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
        <p className="text-[#78716c]">Aluno não encontrado.</p>
      </div>
    );
  }

  try {
    trajetoria = await api.trajetoria.get(alunoId);
  } catch {
    // Sem textos suficientes ainda
  }

  const baselines  = trabalhos.filter((t) => t.baseline);
  const naoBaseline = trabalhos.filter((t) => !t.baseline);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-3 text-[#78716c]">
        <Link href="/dashboard" className="hover:underline hover:text-[#2d7a4f]">Turmas</Link>
        {" / "}
        <Link href={`/turma/${aluno.turma_id}`} className="hover:underline hover:text-[#2d7a4f]">Turma</Link>
        {" / "}
        <span className="text-[#1c1917] font-medium">{aluno.nome}</span>
      </div>

      <h1 className="text-4xl font-bold mb-1" style={{ fontFamily: "Georgia, serif" }}>
        {aluno.nome}
      </h1>
      {aluno.matricula && (
        <p className="text-[#78716c] mb-7">Matrícula: {aluno.matricula}</p>
      )}

      <div className="grid grid-cols-2 gap-5 mb-9">
        <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-5">
          <div className="text-3xl font-bold text-[#2d7a4f]">{baselines.length}</div>
          <div className="text-[#78716c] mt-1 font-medium">textos de baseline</div>
          {baselines.length < 3 && (
            <div className="text-sm text-[#d97706] mt-2 font-medium">
              Mínimo recomendado: 3 textos
            </div>
          )}
        </div>
        <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-5">
          <div className="text-3xl font-bold text-[#1c1917]">{naoBaseline.length}</div>
          <div className="text-[#78716c] mt-1 font-medium">trabalhos entregues</div>
        </div>
      </div>

      {trajetoria && trajetoria.textos.length >= 2 && (
        <section className="mb-9">
          <TrajetoriaChart data={trajetoria} />
        </section>
      )}

      {baselines.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "Georgia, serif" }}>
            Baseline confiável
          </h2>
          <div className="space-y-3">
            {baselines.map((t) => (
              <TrabalhoCard key={t.id} trabalho={t} />
            ))}
          </div>
        </section>
      )}

      {naoBaseline.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "Georgia, serif" }}>
            Trabalhos entregues
          </h2>
          <div className="space-y-3">
            {naoBaseline.map((t) => (
              <TrabalhoCard key={t.id} trabalho={t} />
            ))}
          </div>
        </section>
      )}

      {trabalhos.length === 0 && (
        <div className="border border-[#e5e1da] rounded-xl p-10 text-center text-[#78716c] bg-white">
          <p>Nenhum trabalho enviado ainda.</p>
        </div>
      )}
    </div>
  );
}

function TrabalhoCard({ trabalho }: { trabalho: Trabalho }) {
  return (
    <Link href={`/trabalho/${trabalho.id}`}>
      <div className="border-2 border-[#e5e1da] bg-white rounded-xl px-6 py-4 flex items-center justify-between hover:border-[#2d7a4f] hover:shadow-md transition-all cursor-pointer">
        <div>
          <span className="font-semibold text-lg">{trabalho.titulo}</span>
          <span className="ml-3 text-[#78716c]">{trabalho.tipo}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-[#78716c]">
            {new Date(trabalho.data_entrega).toLocaleDateString("pt-BR")}
          </span>
          <span className="text-sm uppercase text-[#78716c] font-mono">
            .{trabalho.formato_origem}
          </span>
          {trabalho.baseline && (
            <span className="text-sm bg-[#2d7a4f] text-white px-3 py-1 rounded-full font-medium">
              baseline
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
