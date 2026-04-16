from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.schemas.trabalho import TrabalhoOut, TrabalhoDetalhe
from app.services.parser import extrair_texto
from app.services.features import extrair_features
from app.services.perfil import recalcular_perfil

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
    await db.flush()  # get trabalho.id

    # Auto-extract features on upload
    features = extrair_features(texto)
    for nome, valor in features.items():
        db.add(TrabalhoFeature(trabalho_id=trabalho.id, nome=nome, valor=valor))

    await db.commit()
    await db.refresh(trabalho)

    # If marked as baseline, recalculate student profile
    if baseline:
        await recalcular_perfil(aluno_id, db)

    return trabalho


@router.patch("/{trabalho_id}/baseline", response_model=TrabalhoOut)
async def marcar_baseline(trabalho_id: int, baseline: bool, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trabalho).where(Trabalho.id == trabalho_id))
    trabalho = result.scalar_one_or_none()
    if not trabalho:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado")
    trabalho.baseline = baseline
    await db.commit()
    await recalcular_perfil(trabalho.aluno_id, db)
    await db.refresh(trabalho)
    return trabalho
