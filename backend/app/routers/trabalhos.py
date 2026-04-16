from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.trabalho import Trabalho
from app.schemas.trabalho import TrabalhoOut, TrabalhoDetalhe
from app.services.parser import extrair_texto

router = APIRouter()


@router.get("/aluno/{aluno_id}", response_model=list[TrabalhoOut])
async def listar_trabalhos_do_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.aluno_id == aluno_id))
    return result.scalars().all()


@router.get("/{trabalho_id}", response_model=TrabalhoDetalhe)
async def get_trabalho(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")
    return trabalho


@router.post("/upload", response_model=TrabalhoOut, status_code=201)
async def upload_trabalho(
    aluno_id: int = Form(...),
    titulo: str = Form(...),
    tipo: str = Form("redação"),
    baseline: bool = Form(False),
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    conteudo = await arquivo.read()
    extensao = arquivo.filename.rsplit(".", 1)[-1].lower()

    if extensao not in ("docx", "pdf"):
        raise HTTPException(status_code=400, detail="Formato não suportado. Use .docx ou .pdf")

    texto = extrair_texto(conteudo, extensao)

    trabalho = Trabalho(
        aluno_id=aluno_id,
        titulo=titulo,
        tipo=tipo,
        texto=texto,
        formato_origem=extensao,
        baseline=baseline,
    )
    db.add(trabalho)
    await db.commit()
    await db.refresh(trabalho)
    return trabalho


@router.patch("/{trabalho_id}/baseline", response_model=TrabalhoOut)
async def marcar_baseline(trabalho_id: int, baseline: bool, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")
    trabalho.baseline = baseline
    await db.commit()
    await db.refresh(trabalho)
    return trabalho
