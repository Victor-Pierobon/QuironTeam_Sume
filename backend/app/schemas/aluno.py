from pydantic import BaseModel


class AlunoCreate(BaseModel):
    nome: str
    matricula: str | None = None
    turma_id: int


class AlunoOut(BaseModel):
    id: int
    nome: str
    matricula: str | None
    turma_id: int
    total_trabalhos: int = 0
    status: str = "ok"  # ok | atencao | destaque

    model_config = {"from_attributes": True}
