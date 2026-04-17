import Link from "next/link";
import { api, Turma } from "@/lib/api";

async function getTurmas(): Promise<Turma[]> {
  try {
    return await api.turmas.listar();
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const turmas = await getTurmas();

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "Georgia, serif" }}>
        Minhas turmas
      </h1>
      <p className="text-[#78716c] mb-8">
        Selecione uma turma para ver os alunos e seus trabalhos.
      </p>

      {turmas.length === 0 ? (
        <div className="border border-[#e5e1da] rounded-xl p-10 text-center text-[#78716c] bg-white">
          <p className="text-lg mb-2">Nenhuma turma cadastrada ainda.</p>
          <p className="text-sm">Use a API para criar turmas e alunos, ou rode o script de seed.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {turmas.map((turma) => (
            <Link key={turma.id} href={`/turma/${turma.id}`}>
              <div className="border-2 border-[#e5e1da] bg-white rounded-xl p-6 hover:border-[#2d7a4f] hover:shadow-md transition-all cursor-pointer">
                <h2 className="font-bold text-xl mb-1" style={{ fontFamily: "Georgia, serif" }}>
                  {turma.nome}
                </h2>
                <p className="text-[#78716c]">{turma.disciplina}</p>
                <p className="text-[#78716c] text-sm">{turma.ano_serie}</p>
                <div className="mt-5 pt-4 border-t border-[#e5e1da] font-semibold text-[#2d7a4f]">
                  {turma.total_alunos} {turma.total_alunos === 1 ? "aluno" : "alunos"}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
