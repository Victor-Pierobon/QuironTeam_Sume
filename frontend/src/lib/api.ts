const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

export const api = {
  turmas: {
    listar: () => apiFetch<Turma[]>("/turmas/"),
    get: (id: number) => apiFetch<Turma>(`/turmas/${id}`),
    criar: (data: TurmaCreate) =>
      apiFetch<Turma>("/turmas/", { method: "POST", body: JSON.stringify(data) }),
  },
  alunos: {
    porTurma: (turmaId: number) => apiFetch<Aluno[]>(`/alunos/turma/${turmaId}`),
    get: (id: number) => apiFetch<Aluno>(`/alunos/${id}`),
    criar: (data: AlunoCreate) =>
      apiFetch<Aluno>("/alunos/", { method: "POST", body: JSON.stringify(data) }),
  },
  trabalhos: {
    porAluno: (alunoId: number) => apiFetch<Trabalho[]>(`/trabalhos/aluno/${alunoId}`),
    get: (id: number) => apiFetch<Trabalho>(`/trabalhos/${id}`),
    marcarBaseline: (id: number, baseline: boolean) =>
      apiFetch<Trabalho>(`/trabalhos/${id}/baseline?baseline=${baseline}`, { method: "PATCH" }),
  },
};

// Tipos
export interface Turma {
  id: number;
  nome: string;
  disciplina: string;
  ano_serie: string;
  total_alunos: number;
}

export interface TurmaCreate {
  nome: string;
  disciplina: string;
  ano_serie: string;
}

export interface Aluno {
  id: number;
  nome: string;
  matricula: string | null;
  turma_id: number;
  total_trabalhos: number;
  status: "ok" | "atencao" | "destaque";
}

export interface AlunoCreate {
  nome: string;
  matricula?: string;
  turma_id: number;
}

export interface Trabalho {
  id: number;
  aluno_id: number;
  titulo: string;
  tipo: string;
  formato_origem: string;
  baseline: boolean;
  data_entrega: string;
  texto?: string;
}
