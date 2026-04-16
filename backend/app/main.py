from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import turmas, alunos, trabalhos, analise

app = FastAPI(title="Sumé API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(turmas.router, prefix="/turmas", tags=["turmas"])
app.include_router(alunos.router, prefix="/alunos", tags=["alunos"])
app.include_router(trabalhos.router, prefix="/trabalhos", tags=["trabalhos"])
app.include_router(analise.router, prefix="/analise", tags=["analise"])


@app.get("/")
async def root():
    return {"status": "ok", "app": "Sumé"}
