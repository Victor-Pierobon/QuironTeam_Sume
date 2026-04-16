from pydantic import BaseModel


class TurmaCreate(BaseModel):
    nome: str
    disciplina: str
    ano_serie: str


class TurmaOut(BaseModel):
    id: int
    nome: str
    disciplina: str
    ano_serie: str
    total_alunos: int = 0

    model_config = {"from_attributes": True}
