# Sumé

**Copiloto crítico para professores analisarem produção escrita de alunos.**

Desenvolvido para o Desafio 2 do Hackathon Brasília Virtual — Inteligência Artificial e Letramento Digital na Sala de Aula.

---

## O que é

O Sumé não é um detector de IA. É um **copiloto pedagógico**: analisa a produção escrita do aluno sob múltiplos ângulos (padrão de escrita, confiabilidade das fontes, evolução do documento) e apresenta ao professor **evidências** — não vereditos — que ajudam a decidir se vale uma conversa com o aluno.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 16 + Tailwind CSS |
| Backend | Python + FastAPI |
| Banco de dados | PostgreSQL 16 |
| NLP | spaCy (pt_core_news_sm), nltk, textstat |
| Parsing | python-docx, pypdf |
| LLM | API de modelo de linguagem (relatórios pedagógicos) |
| Validação de fontes | CrossRef API, OpenAlex API |

---

## Pré-requisitos

- [Node.js](https://nodejs.org/) 20+
- [Python](https://www.python.org/) 3.11+
- [Docker](https://www.docker.com/) (para o banco de dados)

---

## Instalação e execução

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd QuironTeam_Sume
```

### 2. Suba o banco de dados

```bash
docker-compose up -d
```

Isso inicia um PostgreSQL na porta `5432` com:
- Usuário: `sume`
- Senha: `sume`
- Banco: `sume`

### 3. Configure e inicie o backend

```bash
cd backend

# Crie o ambiente virtual
python -m venv .venv

# Ative (Linux/macOS)
source .venv/bin/activate

# Ative (Windows)
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo de variáveis de ambiente
cp .env.example .env

# Inicie o servidor
uvicorn app.main:app --reload
```

O backend estará disponível em `http://localhost:8000`.

Documentação interativa da API: `http://localhost:8000/docs`

### 4. Configure e inicie o frontend

```bash
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:3000`.

---

## Estrutura do projeto

```
QuironTeam_Sume/
├── docker-compose.yml          # PostgreSQL
├── sume_mvp.md                 # Documento completo do produto
├── sume_cronograma.md          # Cronograma de 5 dias
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py             # Entrypoint FastAPI
│       ├── database.py         # Conexão com o banco
│       ├── models/             # Entidades SQLAlchemy
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   ├── trabalho.py     # Trabalho, Feature, Fonte, Parágrafo
│       │   ├── perfil.py       # Perfil estilométrico do aluno
│       │   └── dossie.py       # Dossiê de evidências e desfecho
│       ├── routers/            # Endpoints da API
│       │   ├── turmas.py
│       │   ├── alunos.py
│       │   └── trabalhos.py
│       ├── schemas/            # Schemas Pydantic (request/response)
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   └── trabalho.py
│       └── services/
│           └── parser.py       # Extração de texto de .docx e .pdf
│
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx      # Layout global (header Sumé)
        │   ├── globals.css     # Paleta terrosa
        │   ├── page.tsx        # Redireciona para /dashboard
        │   ├── dashboard/      # Lista de turmas
        │   ├── turma/[id]/     # Alunos da turma
        │   ├── aluno/[id]/     # Perfil e trabalhos do aluno
        │   └── trabalho/[id]/  # Análise do trabalho
        └── lib/
            └── api.ts          # Client da API + tipos TypeScript
```

---

## API — principais endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/turmas/` | Lista todas as turmas |
| `POST` | `/turmas/` | Cria uma turma |
| `GET` | `/turmas/{id}` | Detalhe de uma turma |
| `GET` | `/alunos/turma/{id}` | Alunos de uma turma |
| `POST` | `/alunos/` | Cria um aluno |
| `GET` | `/alunos/{id}` | Detalhe de um aluno |
| `GET` | `/trabalhos/aluno/{id}` | Trabalhos de um aluno |
| `POST` | `/trabalhos/upload` | Upload de trabalho (.docx ou .pdf) |
| `GET` | `/trabalhos/{id}` | Detalhe de um trabalho |
| `PATCH` | `/trabalhos/{id}/baseline` | Marca/desmarca como baseline |

### Exemplo — upload de trabalho

```bash
curl -X POST http://localhost:8000/trabalhos/upload \
  -F "aluno_id=1" \
  -F "titulo=Redação sobre o cerrado" \
  -F "tipo=redação" \
  -F "baseline=false" \
  -F "arquivo=@meu_arquivo.docx"
```

---

## Populando o banco com dados de demo

> Em desenvolvimento. Um script `seed.py` será adicionado com 30 alunos e trabalhos gerados para os 3 casos de demonstração.

Por enquanto, use a API diretamente ou o Swagger em `http://localhost:8000/docs`.

---

## Variáveis de ambiente

### Backend (`backend/.env`)

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://sume:sume@localhost:5432/sume` | URL de conexão com o banco |

### Frontend (`frontend/.env.local`)

| Variável | Padrão | Descrição |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL base do backend |

---

## Desenvolvimento — cronograma dos 5 dias

| Dia | Foco | Status |
|---|---|---|
| Dia 1 | Fundação — estrutura, banco, parser, páginas base | Concluído |
| Dia 2 | Inteligência estilométrica — 20 features, baseline, trajetória | Pendente |
| Dia 3 | Fontes e histórico de versões — CrossRef, OpenAlex, Google Docs | Pendente |
| Dia 4 | Relatórios e UI completa — dossiê, LLM, telas finais | Pendente |
| Dia 5 | Polish e apresentação — demo, pitch, casos controlados | Pendente |

Detalhes completos em [`sume_cronograma.md`](./sume_cronograma.md).

---

## Decisões de protótipo

- **Sem autenticação:** o professor é considerado logado. Nenhum JWT, nenhuma tela de login.
- **Banco criado automaticamente:** as tabelas são criadas no startup do FastAPI via `Base.metadata.create_all`.
- **Sem migrations versionadas:** para o hackathon, o Alembic não é necessário. Se o schema mudar, apague o volume do Docker e reinicie.

```bash
# Resetar o banco do zero
docker-compose down -v && docker-compose up -d
```

---

## Time

Desenvolvido pela equipe **QuironTeam** para o Hackathon Brasília Virtual 2025.
