# Sumé

**Copiloto pedagógico para professores analisarem produção escrita de alunos.**

Desenvolvido para o Desafio 2 do Hackathon Brasília Virtual — Inteligência Artificial e Letramento Digital na Sala de Aula.

---

## O que é

O Sumé não é um detector de IA. É um **copiloto pedagógico**: analisa a produção escrita do aluno sob múltiplos ângulos (padrão de escrita, confiabilidade das fontes, histórico de edição, evolução ao longo do tempo) e apresenta ao professor **evidências** — não vereditos — que ajudam a decidir se vale uma conversa com o aluno.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 16 + React 19 + Tailwind CSS v4 + Recharts |
| Backend | Python 3.12 + FastAPI + SQLAlchemy async |
| Banco de dados | PostgreSQL 16 (via Docker) |
| Análise estilométrica | 20 features (textstat + heurísticas PT-BR) |
| Erros gramaticais | LanguageTool (API pública → heurísticas regex) |
| Parsing de arquivos | python-docx, pypdf |
| LLM (roteiro socrático) | Groq API — `llama-3.3-70b-versatile` |
| OCR de fotos | Groq Vision — `meta-llama/llama-4-scout-17b-16e-instruct` |
| Validação de fontes | CrossRef API, OpenAlex API |
| Export PDF | fpdf2 |
| Histórico de edição | Google Drive API v3 (Service Account) |
| Tutorial interativo | react-joyride |

---

## Funcionalidades

### Análise estilométrica
Extrai 20 features de cada texto e compara com o perfil histórico do aluno (linha de base):
- Comprimento médio de frase, parágrafo e palavra
- Diversidade lexical, palavras raras, palavras funcionais
- Complexidade sintática, índice de legibilidade
- Densidade de conectivos, uso de voz passiva, primeira pessoa
- Frequência de palavras típicas de IA
- Erros de ortografia e concordância (via LanguageTool)
- Variação de comprimento de frase, uniformidade de parágrafos

Desvios classificados em **normal**, **atenção** e **conversar**, exibidos como botões de filtro interativos.

### Trajetória de desenvolvimento
Gráfico de evolução com **índice normalizado 0–100** (visão geral) ou métricas individuais (modo avançado). Exibido no perfil do aluno com dados de todos os trabalhos.

### Validação de fontes
Verifica referências bibliográficas via CrossRef e OpenAlex. Classifica cada fonte como verde (verificada), amarela (precária) ou vermelha (problemática). Exibe "nenhuma fonte encontrada" quando validado sem resultados.

### Roteiro socrático
Gera via LLM (Groq) um roteiro de conversa para o professor: observações sobre os dados, perguntas abertas para o aluno e como conduzir a conversa sem tom acusatório.

### OCR por foto
O professor tira uma foto do trabalho manuscrito ou impresso. A imagem é enviada para o modelo de visão da Groq, que transcreve o texto preservando erros de ortografia do aluno. A transcrição entra no pipeline de análise normalmente.

### Export do dossiê em PDF
Exporta todas as evidências em PDF formatado, pronto para reunião com coordenação ou conselho de classe.

### Histórico de edição via Google Docs
Importa texto completo + histórico de revisões de um Google Doc. Detecta padrões como colagem em bloco, ausência de revisões e tempo ativo insuficiente. O painel só aparece quando há dados importados.

### Tutorial interativo
Tutorial passo a passo (react-joyride) nas 4 telas principais. Guia o professor nas funcionalidades com linguagem pedagógica. Pode ser desativado ou reativado a qualquer momento via botão `?` (canto inferior direito).

### Painel de acessibilidade
Botão ♿ fixo (canto inferior esquerdo) com:
- **Alto contraste** — fundo preto, texto branco, links amarelos
- **Fonte para dislexia** — OpenDyslexic com espaçamento ampliado
- **Espaçamento amplo** — maior altura de linha e espaçamento entre palavras
- **Tamanho do texto** — escala A− / Normal / Grande / Extra grande
- **Leitura ao cursor** — Web Speech API: lê em voz alta o elemento sob o cursor (pt-BR)
- **Skip-to-content** — link oculto para usuários de teclado/leitores de tela
- Respeita `prefers-reduced-motion` do sistema operacional
- Preferências salvas em localStorage

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
| `GROQ_API_KEY` | — | Chave da Groq API (roteiro socrático + OCR de fotos) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | `credentials/google_service_account.json` | Credenciais Google Drive (opcional) |

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

Sem essa configuração, o sistema funciona normalmente — a aba Google Docs retorna um aviso e todas as outras funcionalidades continuam disponíveis.

---

## Estrutura do projeto

```
QuironTeam_Sume/
├── docker-compose.yml
├── sume_mvp.md                  # Especificação completa do produto
│
├── backend/
│   ├── requirements.txt
│   ├── .env
│   ├── seed.py                  # Dados de demonstração (3 alunos)
│   ├── seed_dados.py            # Seed alternativo com mais dados
│   ├── credentials/             # Credenciais Google (não versionado)
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models/
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   ├── trabalho.py      # Trabalho, TrabalhoFeature, Fonte
│       │   ├── perfil.py        # PerfilAluno (médias, desvios, tendências)
│       │   ├── dossie.py        # Dossie, Desfecho
│       │   └── gdocs.py         # HistoricoVersao
│       ├── routers/
│       │   ├── turmas.py
│       │   ├── alunos.py
│       │   ├── trabalhos.py     # upload .docx/.pdf, Google Docs e foto (OCR)
│       │   ├── analise.py       # análise estilométrica
│       │   ├── fontes.py        # validação de referências
│       │   ├── relatorio.py     # roteiro socrático via LLM
│       │   ├── desfecho.py      # registro do resultado da conversa
│       │   ├── export.py        # exportação do dossiê em PDF
│       │   ├── comparacao.py    # comparação estilométrica entre alunos
│       │   └── gdocs.py         # importação/leitura do histórico Google Docs
│       ├── schemas/
│       │   ├── turma.py
│       │   ├── aluno.py
│       │   └── trabalho.py
│       └── services/
│           ├── parser.py        # extração de texto de .docx e .pdf
│           ├── features.py      # 20 features estilométricas
│           ├── perfil.py        # baseline, z-scores, análise intra-documento
│           ├── ocr.py           # transcrição de fotos via Groq Vision
│           ├── languagetool_service.py  # erros ortográficos e de concordância
│           ├── relatorio.py     # prompt e chamada LLM para roteiro socrático
│           └── gdocs.py         # Drive API — texto + histórico de revisões
│
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx            # header + PainelAcessibilidade global
        │   ├── globals.css           # classes de acessibilidade CSS
        │   ├── page.tsx              # redirect para /dashboard
        │   ├── dashboard/page.tsx    # lista de turmas
        │   ├── turma/[id]/
        │   │   └── page.tsx          # alunos da turma com status e contadores
        │   ├── aluno/[id]/page.tsx   # perfil, trajetória e lista de trabalhos
        │   └── trabalho/[id]/page.tsx # dossiê completo do trabalho
        ├── components/
        │   ├── AnalisarButton.tsx         # dispara análise estilométrica
        │   ├── AnaliseDonut.tsx           # gráfico donut (normais/atenção/conversar)
        │   ├── DesfechoForm.tsx           # registra resultado da conversa
        │   ├── EvidenciasPanel.tsx        # painel de evidências com filtros por categoria
        │   ├── GDocsPanel.tsx             # painel de histórico de edição Google Docs
        │   ├── GerarRoteiroButton.tsx     # gera roteiro socrático via LLM
        │   ├── HeatmapTurma.tsx           # heatmap de z-scores da turma
        │   ├── ListaParesSimilares.tsx    # pares de alunos com alta similaridade
        │   ├── TrajetoriaChart.tsx        # gráfico de evolução (índice + métricas)
        │   ├── UploadTrabalhoButton.tsx   # upload .docx/.pdf, foto (OCR) ou Google Docs
        │   ├── ValidarFontesButton.tsx    # dispara validação de fontes
        │   ├── acessibilidade/
        │   │   ├── PainelAcessibilidade.tsx  # painel ♿ com todas as opções
        │   │   └── useAcessibilidade.ts      # hook: preferências + TTS hover
        │   └── tour/
        │       ├── SumeTour.tsx           # componente Joyride com estilos PT-BR
        │       ├── useTour.ts             # hook: estado, localStorage, desativar
        │       ├── BotaoAjuda.tsx         # botão ? fixo + toggle desativar/reativar
        │       ├── TourDashboard.tsx      # passos do tutorial — tela de turmas
        │       ├── TourTurma.tsx          # passos do tutorial — tela de alunos
        │       ├── TourAluno.tsx          # passos do tutorial — perfil do aluno
        │       └── TourTrabalho.tsx       # passos do tutorial — análise do trabalho
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
| `POST` | `/trabalhos/upload-foto` | Upload de foto — OCR via Groq Vision |
| `PATCH` | `/trabalhos/{id}/baseline` | Marca/desmarca como linha de base |
| `POST` | `/analise/{id}` | Executa análise estilométrica |
| `GET` | `/analise/{id}` | Lê análise existente |
| `POST` | `/fontes/{id}` | Valida fontes do trabalho |
| `GET` | `/fontes/{id}` | Lista fontes validadas (200 mesmo se vazio) |
| `POST` | `/relatorio/{id}` | Gera roteiro socrático (LLM) |
| `POST` | `/desfecho/{id}` | Registra desfecho da conversa |
| `GET` | `/export/{id}/pdf` | Exporta dossiê em PDF |
| `GET` | `/turmas/{id}/comparacao` | Comparação estilométrica da turma |
| `POST` | `/gdocs/{id}` | (Re)importa histórico de um Google Doc |
| `GET` | `/gdocs/{id}` | Lê histórico de edição salvo |

---

## Decisões de projeto

```bash
docker-compose down -v && docker-compose up -d
```

- **OCR via LLM de visão:** a Groq Vision preserva erros de ortografia intencionalmente, tornando o texto da foto comparável ao estilo real do aluno.
- **Google Docs é opcional:** sem `GOOGLE_SERVICE_ACCOUNT_JSON`, o sistema funciona normalmente; a feature retorna 503 com mensagem clara. O painel GDocs só é exibido quando há dados.
- **PDF gerado com fpdf2** (sem GTK): mais simples de instalar em qualquer OS do que WeasyPrint.
- **Acessibilidade:** classes CSS no elemento `<html>` para alto contraste, escala de fonte, OpenDyslexic e espaçamento. TTS via Web Speech API (nativo do navegador, sem dependência externa). Todas as preferências persistem em localStorage.
- **Tutorial:** estado por página em localStorage (`sume_tour_*`). Um flag global (`sume_tour_desativado`) permite desabilitar sem apagar o histórico, e reativar recomeça do zero.

---

## Time

Desenvolvido pela equipe **QuironTeam** para o Hackathon Brasília Virtual 2026.