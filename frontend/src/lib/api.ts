const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

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
  fontes: {
    get: (trabalhoId: number) => apiFetch<Fonte[]>(`/fontes/${trabalhoId}`),
  },
  trajetoria: {
    get: (alunoId: number) => apiFetch<Trajetoria>(`/alunos/${alunoId}/trajetoria`),
  },
  desfecho: {
    get: (trabalhoId: number) => apiFetch<Desfecho>(`/desfecho/${trabalhoId}`),
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

export interface Fonte {
  id: number;
  texto_original: string;
  url: string | null;
  doi: string | null;
  status: "verde" | "amarelo" | "vermelho";
  justificativa: string | null;
}

export interface Desfecho {
  status: "esclarecido" | "conversa_realizada" | "em_acompanhamento";
  nota: string | null;
  registrado_em: string;
}

export interface TextoFeatures {
  id: number;
  titulo: string;
  baseline: boolean;
  data_entrega: string;
  features: Record<string, number>;
}

export interface Trajetoria {
  textos: TextoFeatures[];
  feature_labels: Record<string, string>;
}
