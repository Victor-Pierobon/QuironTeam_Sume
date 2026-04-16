# Sumé — Cronograma de Desenvolvimento (Hackathon 5 dias)

---

## Dia 1 — Fundação ✅

**Objetivo:** ter o esqueleto funcional rodando.

> **Decisão de protótipo:** login removido do escopo. O professor já está logado — sem auth, sem JWT, sem tela de login.

**Backend**
- ✅ Setup do repositório e ambiente (FastAPI + PostgreSQL)
- ✅ Models do banco (Turma, Aluno, Trabalho, Feature, PerfilAluno, Fonte, ParagrafoDestacado, Dossie, Desfecho)
- ✅ Rotas básicas — GET/POST `/turmas`, `/alunos`, `/trabalhos`, upload de arquivo, marcação de baseline
- ✅ Parser de `.docx` e `.pdf` → extração de texto bruto, parágrafos, URLs e DOIs
- ✅ `docker-compose.yml` com PostgreSQL pronto

**Frontend**
- ✅ Setup Next.js 16 + Tailwind (paleta terrosa — papel, verde-musgo, âmbar, vermelho-terra)
- ✅ Layout global com header Sumé
- ✅ `/dashboard` — lista de turmas com contador de alunos
- ✅ `/turma/[id]` — alunos com cartões de status (normal/atenção/conversar)
- ✅ `/aluno/[id]` — trabalhos separados entre baseline e entregues
- ✅ `/trabalho/[id]` — texto completo por parágrafos, contadores placeholder

**Entregável:** professor acessa o dashboard e navega até o trabalho de um aluno. ✅

---

## Dia 2 — Inteligência estilométrica

**Objetivo:** o sistema começa a "entender" como o aluno escreve.

**Backend**
- Pipeline de extração das 20 features por texto
- Cálculo de baseline (média + desvio padrão por feature)
- Calibração com prior da turma (para baselines pequenas)
- Algoritmo de análise de tendência (regressão linear por feature)
- Análise intra-documento (parágrafos vs. parágrafos)
- Armazenamento do perfil do aluno no banco

**Entregável:** ao subir um trabalho, o sistema gera flags de desvio com magnitude.

---

## Dia 3 — Fontes e histórico de versões

**Objetivo:** validar as fontes citadas e analisar como o documento foi construído.

**Backend**
- Extração de citações, URLs e DOIs do texto
- Integração com CrossRef e OpenAlex
- Verificação de URLs (HTTP status + domínio)
- Classificação semafórica verde/amarelo/vermelho
- Integração com Google Docs API (histórico de revisões)
- Métricas de edição (saltos, proporção inserção/revisão, sessões)

**Entregável:** sistema valida fontes com cor e justificativa; detecta padrões suspeitos no histórico de edição.

> **Risco:** OAuth do Google Docs pode consumir tempo. Se travar, deixar como feature avançada e priorizar `.docx` com track changes.

---

## Dia 4 — Relatórios e interface completa

**Objetivo:** ligar tudo numa experiência coesa end-to-end.

**Backend**
- Montagem do dossiê de evidências estruturado
- Integração com a API da LLM
- Geração de relatório pedagógico + roteiro socrático
- Endpoint de registro de desfecho

**Frontend**
- Tela 1: Dashboard da turma (cartões por aluno, filtros, status)
- Tela 2: Perfil do aluno (trajetória estilométrica + lista de trabalhos)
- Tela 3: Análise do trabalho (parágrafos coloridos, evidências, fontes)
- Modais: roteiro socrático, análise de parágrafo, registro de desfecho
- Gráficos de trajetória por feature

**Entregável:** fluxo completo funcional — upload → análise → dossiê → roteiro socrático.

---

## Dia 5 — Polish e apresentação

**Objetivo:** garantir que o demo não falha ao vivo e o pitch convence.

**Técnico**
- Corrigir bugs encontrados nos testes end-to-end
- Cache de respostas da LLM (fallback se a API cair durante o demo)
- Refinamento visual (paleta terrosa, tipografia, vocabulário pedagógico)
- Processamento assíncrono com indicador de progresso

**Produto/Pitch**
- Preparar 3 casos de demonstração controlados:
  1. Trabalho limpo → sem falsos positivos
  2. Trabalho com IA + fontes fabricadas → dossiê rico
  3. Aluno com evolução legítima → trajetória funcionando
- Slides e vídeo do pitch
- Ensaio da apresentação ao vivo

**Entregável:** demo polida + pitch ensaiado + 3 casos de demo que não quebram.

---

## Paralelos ao longo dos 5 dias

| Responsabilidade | Quem carrega |
|---|---|
| Backend / Parsing | Dev 1 |
| Estilometria / ML | Dev 2 |
| Integrações (Google Docs, LLM, bases acadêmicas) | Dev 3 |
| Frontend | Dev 4 |
| Produto, demo e pitch | Dev 5 |

> **Regra de ouro:** o Dia 4 tem que terminar com tudo funcionando. O Dia 5 é exclusivo para polish e pitch — qualquer coisa que escorregue para o Dia 5 vira risco alto.
