# Sumé

**Copiloto crítico para professores analisarem produção escrita de alunos.**

Desenvolvido para o Desafio 2 do Hackathon Brasília Virtual — Inteligência Artificial e Letramento Digital na Sala de Aula.

---

## O que é

O Sumé não é um detector de IA. É um **copiloto pedagógico**: analisa a produção escrita do aluno sob múltiplos ângulos (padrão de escrita, confiabilidade das fontes, histórico de edição, evolução ao longo do tempo) e apresenta ao professor **evidências** — não vereditos — que ajudam a decidir se vale uma conversa com o aluno.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 15 + Tailwind CSS + Recharts |
| Backend | Python 3.12 + FastAPI |
| Banco de dados | PostgreSQL 16 |
| Análise estilométrica | 20 features (textstat + heurísticas PT-BR) |
| Erros gramaticais | LanguageTool (API pública → Java local → heurísticas regex) |
| Parsing de arquivos | python-docx, pypdf |
| LLM (roteiro socrático) | Groq API |
| Validação de fontes | CrossRef API, OpenAlex API |
| Export PDF | fpdf2 |
| Histórico de edição | Google Drive API v3 (Service Account) |

---

## Funcionalidades

### Análise estilométrica
Extrai 20 features de cada texto e compara com o perfil histórico do aluno (baseline):
- Comprimento médio de frase, parágrafo e palavra
- Diversidade lexical, palavras raras, palavras funcionais
- Complexidade sintática, índice de leiturabilidade
- Densidade de conectivos, uso de voz passiva, primeira pessoa
- Frequência de palavras típicas de IA
- Erros de ortografia e concordância (via LanguageTool)
- Variação de comprimento de frase, uniformidade de parágrafos

Cada feature recebe um z-score em relação ao baseline do aluno. Desvios classificados em **normal**, **atenção** e **conversar**.

### Análise intra-documento
Detecta parágrafos que destoam do próprio estilo do texto — mesmo sem baseline, identifica inserções de material externo.

### Trajetória de desenvolvimento
Gráfico de evolução com **índice normalizado 0–100** (visão geral) ou métricas individuais (modo avançado).

### Validação de fontes
Verifica referências bibliográficas via CrossRef e OpenAlex. Classifica cada fonte como verde (verificada), amarela (precária) ou vermelha (problemática).

### Roteiro socrático
Gera via LLM (Groq) um roteiro de conversa para o professor: observações sobre os dados, perguntas para o aluno e como conduzir a conversa.

### Export do dossiê em PDF
Exporta todas as evidências em PDF formatado, pronto para reunião com coordenação ou conselho de classe.

### Comparação entre alunos da turma
Detecta padrões coletivos: heatmap de z-scores, similaridade coseno entre pares e lista de alunos com estilos muito similares.

### Histórico de edição via Google Docs
Importa texto completo + histórico de revisões de um Google Doc em um único passo. Detecta padrões como colagem em bloco, ausência de revisões e tempo ativo insuficiente.

---

## Pré-requisitos

- [Node.js](https://nodejs.org/) 20+
- [Python](https://www.python.org/) **3.12** (obrigatório — 3.13+ ainda sem wheels para `asyncpg`)
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

PostgreSQL na porta `5432` com usuário `sume`, senha `sume`, banco `sume`.

### 3. Configure e inicie o backend

```bash
cd backend

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001
```

Backend disponível em `http://localhost:8001`.
Documentação interativa: `http://localhost:8001/docs`

### 4. Configure e inicie o frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend disponível em `http://localhost:3000`.

### 5. Popule o banco com dados de demonstração

```bash
cd backend
python seed.py
```

Cria 3 alunos com perfis contrastantes:
- **Ana Costa** — escrita limpa, consistente, fontes verificadas
- **Bruno Lopes** — desvios fortes, fontes fabricadas, palavras típicas de IA
- **Carla Mendes** — evolução legítima ao longo do semestre

---

## Variáveis de ambiente

### Backend (`backend/.env`)

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://sume:sume@localhost:5432/sume` | Conexão com o banco |
| `GROQ_API_KEY` | — | Chave da Groq API para geração do roteiro socrático |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | `credentials/google_service_account.json` | Credenciais para importar Google Docs (opcional) |

### Frontend (`frontend/.env.local`)

| Variável | Padrão | Descrição |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8001` | URL base do backend |

---

## Configuração do Google Docs (opcional)

Permite importar texto + histórico de edições diretamente de um Google Doc.

### 1. Criar projeto e Service Account no Google Cloud

1. Acesse [console.cloud.google.com](https://console.cloud.google.com) → crie um projeto
2. **APIs & Services → Library** → ative **Google Drive API** e **Google Docs API**
3. **APIs & Services → Credentials → + Create Credentials → Service account**
4. Na service account criada: aba **Keys → Add Key → Create new key → JSON**
5. Salve o arquivo em `backend/credentials/google_service_account.json`

### 2. Adicionar ao `.env`

```
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/google_service_account.json
```

### 3. Compartilhar o documento

No Google Doc do aluno: **Compartilhar → cole o `client_email`** do JSON → Leitor → Enviar.

O `client_email` está dentro do arquivo JSON (ex: `sume-app@meu-projeto.iam.gserviceaccount.com`).

Sem essa configuração, o sistema funciona normalmente — o botão Google Docs retorna um aviso e todas as outras funcionalidades continuam disponíveis.

---

## Estrutura do projeto

```
QuironTeam_Sume/
├── docker-compose.yml
├── sume_roadmap.md              # Especificação das features pós-hackathon
│
├── backend/
│   ├── requirements.txt
│   ├── .env
│   ├── seed.py                  # Dados de demonstração
│   ├── credentials/             # Credenciais Google (não versionado)
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models/
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   ├── trabalho.py      # Trabalho, TrabalhoFeature, Fonte, ParagrafoDestacado
│       │   ├── perfil.py        # PerfilAluno (médias, desvios, tendências)
│       │   ├── dossie.py        # Dossie, Desfecho
│       │   └── gdocs.py         # HistoricoVersao
│       ├── routers/
│       │   ├── turmas.py
│       │   ├── alunos.py
│       │   ├── trabalhos.py     # upload .docx/.pdf e Google Docs
│       │   ├── analise.py       # análise estilométrica
│       │   ├── fontes.py        # validação de referências
│       │   ├── relatorio.py     # roteiro socrático via LLM
│       │   ├── desfecho.py      # registro do resultado da conversa
│       │   ├── export.py        # exportação do dossiê em PDF
│       │   ├── comparacao.py    # comparação entre alunos da turma
│       │   └── gdocs.py         # importação/leitura do histórico Google Docs
│       ├── schemas/
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   └── trabalho.py
│       └── services/
│           ├── parser.py        # extração de texto de .docx e .pdf
│           ├── features.py      # 20 features estilométricas
│           ├── perfil.py        # baseline, z-scores, análise intra-documento
│           ├── languagetool_service.py  # erros ortográficos e de concordância
│           └── gdocs.py         # Drive API — texto + histórico de revisões
│
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── globals.css
        │   ├── dashboard/           # lista de turmas
        │   ├── turma/[id]/
        │   │   ├── page.tsx          # alunos da turma
        │   │   └── comparacao/       # comparação entre alunos
        │   ├── aluno/[id]/page.tsx   # perfil, trajetória, trabalhos
        │   └── trabalho/[id]/page.tsx # dossiê completo
        ├── components/
        │   ├── UploadTrabalhoButton.tsx    # upload .docx/.pdf ou Google Docs
        │   ├── TrajetoriaChart.tsx         # gráfico de evolução (índice + avançado)
        │   ├── AnalisarButton.tsx          # dispara análise estilométrica
        │   ├── ValidarFontesButton.tsx     # dispara validação de fontes
        │   ├── GerarRoteiroButton.tsx      # gera roteiro socrático via LLM
        │   ├── DesfechoForm.tsx            # registra resultado da conversa
        │   ├── GDocsPanel.tsx              # painel de histórico de edição
        │   ├── HeatmapTurma.tsx            # heatmap de z-scores da turma
        │   └── ListaParesSimilares.tsx     # pares com alta similaridade
        └── lib/
            └── api.ts
```

---

## API — endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/turmas/` | Lista turmas |
| `POST` | `/turmas/` | Cria turma |
| `GET` | `/alunos/turma/{id}` | Alunos de uma turma |
| `POST` | `/alunos/` | Cria aluno |
| `GET` | `/alunos/{id}/trajetoria` | Trajetória estilométrica do aluno |
| `POST` | `/trabalhos/upload` | Upload de trabalho (.docx ou .pdf) |
| `POST` | `/trabalhos/upload-gdocs` | Importa trabalho do Google Docs |
| `PATCH` | `/trabalhos/{id}/baseline` | Marca/desmarca como baseline |
| `POST` | `/analise/{id}` | Executa análise estilométrica |
| `GET` | `/analise/{id}` | Lê análise existente |
| `POST` | `/fontes/{id}` | Valida fontes do trabalho |
| `GET` | `/fontes/{id}` | Lista fontes validadas |
| `POST` | `/relatorio/{id}` | Gera roteiro socrático (LLM) |
| `POST` | `/desfecho/{id}` | Registra desfecho da conversa |
| `GET` | `/export/{id}/pdf` | Exporta dossiê em PDF |
| `GET` | `/turmas/{id}/comparacao` | Comparação estilométrica da turma |
| `POST` | `/gdocs/{id}` | (Re)importa histórico de um Google Doc |
| `GET` | `/gdocs/{id}` | Lê histórico de edição salvo |

---

## Decisões de projeto

- **Sem autenticação:** o professor é considerado logado. Sem JWT, sem tela de login.
- **Tabelas criadas automaticamente:** `Base.metadata.create_all` no startup do FastAPI.
- **Sem migrations versionadas:** para resetar o banco, apague o volume Docker e reinicie.

```bash
docker-compose down -v && docker-compose up -d
```

- **LanguageTool sem Java:** usa a API REST pública como camada primária, Java local como secundária e heurísticas regex PT-BR como fallback offline — sem dependência obrigatória de Java 17+.
- **Google Docs é opcional:** sem `GOOGLE_SERVICE_ACCOUNT_JSON`, o sistema funciona normalmente; a feature retorna 503 com mensagem clara.
- **PDF gerado com fpdf2** (sem GTK): mais simples de instalar em qualquer OS do que WeasyPrint.

---

## Time

Desenvolvido pela equipe **QuironTeam** para o Hackathon Brasília Virtual 2025.
