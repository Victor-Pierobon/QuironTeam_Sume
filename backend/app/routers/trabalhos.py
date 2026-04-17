import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.models.gdocs import HistoricoVersao
from app.schemas.trabalho import TrabalhoOut, TrabalhoDetalhe
from app.services.parser import extrair_texto
from app.services.features import extrair_features
from app.services.perfil import recalcular_perfil
from app.services.gdocs import importar_gdoc_completo, detectar_padroes

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


class GDocsUploadRequest(BaseModel):
    aluno_id: int
    titulo: str
    tipo: str = "redação"
    baseline: bool = False
    doc_url: str


@router.post("/upload-gdocs", response_model=TrabalhoOut, status_code=201)
async def upload_gdocs(body: GDocsUploadRequest, db: AsyncSession = Depends(get_db)):
    """
    Cria um trabalho a partir de um link do Google Docs.
    Importa texto completo + histórico de revisões em um único passo.
    """
    try:
        texto, revisoes, metricas = await importar_gdoc_completo(body.doc_url)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"Erro ao acessar o Google Docs: {e}")

    if not texto.strip():
        raise HTTPException(422, "Documento vazio ou sem texto extraível.")

    trabalho = Trabalho(
        aluno_id=body.aluno_id,
        titulo=body.titulo,
        tipo=body.tipo,
        texto=texto,
        formato_origem="gdocs",
        baseline=body.baseline,
    )
    db.add(trabalho)
    await db.flush()

    # Extrai features
    features = extrair_features(texto)
    for nome, valor in features.items():
        db.add(TrabalhoFeature(trabalho_id=trabalho.id, nome=nome, valor=valor))

    # Salva histórico de edição automaticamente
    padroes = detectar_padroes(metricas)
    hist = HistoricoVersao(
        trabalho_id=trabalho.id,
        num_sessoes=metricas["num_sessoes"],
        tempo_ativo_min=metricas["tempo_ativo_min"],
        maior_insercao_pct=metricas["maior_insercao_pct"],
        razao_edicao_adicao=metricas["razao_edicao_adicao"],
        proporcao_final_colada=metricas["proporcao_final_colada"],
        padroes_json=json.dumps(padroes, ensure_ascii=False),
        revisoes_json=json.dumps(revisoes, ensure_ascii=False),
    )
    db.add(hist)

    await db.commit()
    await db.refresh(trabalho)

    if body.baseline:
        await recalcular_perfil(body.aluno_id, db)

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
