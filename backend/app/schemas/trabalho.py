from pydantic import BaseModel
from datetime import datetime


class TrabalhoOut(BaseModel):
    id: int
    aluno_id: int
    titulo: str
    tipo: str
    formato_origem: str
    baseline: bool
    data_entrega: datetime

    model_config = {"from_attributes": True}


class TrabalhoDetalhe(TrabalhoOut):
    texto: str
