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
      <h1 className="text-3xl font-bold mb-1" style={{ fontFamily: "Georgia, serif" }}>
        Minhas turmas
      </h1>
      <p className="text-[#6b5c40] mb-8 text-sm">
        Selecione uma turma para ver os alunos e seus trabalhos.
      </p>

      {turmas.length === 0 ? (
        <div className="border border-[#e8e0d0] rounded-lg p-8 text-center text-[#6b5c40]">
          <p className="text-lg mb-2">Nenhuma turma cadastrada ainda.</p>
          <p className="text-sm">Use a API para criar turmas e alunos, ou rode o script de seed.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {turmas.map((turma) => (
            <Link key={turma.id} href={`/turma/${turma.id}`}>
              <div className="border border-[#e8e0d0] bg-white rounded-lg p-5 hover:border-[#4a7c59] hover:shadow-sm transition-all cursor-pointer">
                <h2 className="font-semibold text-lg mb-1" style={{ fontFamily: "Georgia, serif" }}>
                  {turma.nome}
                </h2>
                <p className="text-[#6b5c40] text-sm">{turma.disciplina}</p>
                <p className="text-[#6b5c40] text-sm">{turma.ano_serie}</p>
                <div className="mt-4 pt-4 border-t border-[#e8e0d0] text-sm text-[#4a7c59] font-medium">
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
