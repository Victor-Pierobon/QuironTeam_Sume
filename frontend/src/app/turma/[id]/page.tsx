import Link from "next/link";
import { api, Aluno } from "@/lib/api";

const STATUS_CONFIG = {
  ok:       { label: "Normal",    color: "bg-[#2d7a4f] text-white" },
  atencao:  { label: "Atenção",   color: "bg-[#d97706] text-white" },
  destaque: { label: "Conversar", color: "bg-[#dc2626] text-white" },
};

export default async function TurmaPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const turmaId = Number(id);

  let turma;
  let alunos: Aluno[] = [];

  try {
    [turma, alunos] = await Promise.all([
      api.turmas.get(turmaId),
      api.alunos.porTurma(turmaId),
    ]);
  } catch {
    return (
      <div className="max-w-4xl mx-auto">
        <p className="text-[#78716c]">Turma não encontrada.</p>
      </div>
    );
  }

  const totais = {
    ok:       alunos.filter((a) => a.status === "ok").length,
    atencao:  alunos.filter((a) => a.status === "atencao").length,
    destaque: alunos.filter((a) => a.status === "destaque").length,
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-3 text-[#78716c]">
        <Link href="/dashboard" className="hover:underline hover:text-[#2d7a4f]">Turmas</Link>
        {" / "}
        <span className="text-[#1c1917] font-medium">{turma.nome}</span>
      </div>

      <h1 className="text-4xl font-bold mb-1" style={{ fontFamily: "Georgia, serif" }}>
        {turma.nome}
      </h1>
      <p className="text-[#78716c] mb-7">
        {turma.disciplina} · {turma.ano_serie}
      </p>

      <div className="flex gap-4 mb-9">
        {[
          { label: "Total",     value: alunos.length,    color: "text-[#1c1917]" },
          { label: "Normal",    value: totais.ok,         color: "text-[#2d7a4f]" },
          { label: "Atenção",   value: totais.atencao,    color: "text-[#d97706]" },
          { label: "Conversar", value: totais.destaque,   color: "text-[#dc2626]" },
        ].map((item) => (
          <div key={item.label} className="border-2 border-[#e5e1da] bg-white rounded-xl px-6 py-4 text-center min-w-[90px]">
            <div className={`text-3xl font-bold ${item.color}`}>{item.value}</div>
            <div className="text-sm text-[#78716c] mt-1 font-medium">{item.label}</div>
          </div>
        ))}
      </div>

      {alunos.length === 0 ? (
        <div className="border border-[#e5e1da] rounded-xl p-10 text-center text-[#78716c] bg-white">
          <p>Nenhum aluno cadastrado nesta turma.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {alunos.map((aluno) => {
            const st = STATUS_CONFIG[aluno.status] ?? STATUS_CONFIG.ok;
            return (
              <Link key={aluno.id} href={`/aluno/${aluno.id}`}>
                <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6 hover:border-[#2d7a4f] hover:shadow-md transition-all cursor-pointer">
                  <div className="flex items-start justify-between mb-3">
                    <h2 className="font-bold text-lg" style={{ fontFamily: "Georgia, serif" }}>
                      {aluno.nome}
                    </h2>
                    <span className={`text-sm px-3 py-1 rounded-full font-semibold ${st.color}`}>
                      {st.label}
                    </span>
                  </div>
                  {aluno.matricula && (
                    <p className="text-sm text-[#78716c] mb-3">Matrícula: {aluno.matricula}</p>
                  )}
                  <p className="text-[#78716c]">
                    {aluno.total_trabalhos} {aluno.total_trabalhos === 1 ? "trabalho" : "trabalhos"}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
