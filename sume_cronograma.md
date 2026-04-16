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

## Dia 2 — Inteligência estilométrica ✅

**Objetivo:** o sistema começa a "entender" como o aluno escreve.

**Backend**
- ✅ Pipeline de extração das 20 features por texto (`services/features.py`)
- ✅ Cálculo de baseline — média, desvio padrão e tendência por feature (`services/perfil.py`)
- ✅ Calibração com fallback mínimo para evitar falsos positivos com baseline pequena
- ✅ Algoritmo de análise de tendência — regressão linear com decaimento por recência
- ✅ Análise intra-documento — parágrafos comparados entre si, destaque com ≥ 2 features destoantes
- ✅ Router `POST /analise/{id}` e `GET /analise/{id}` — extração + desvios + intra-doc + dossiê
- ✅ Auto-extração de features no upload; recálculo de perfil ao marcar/desmarcar baseline
- ✅ Status do aluno (ok/atenção/conversar) calculado dinamicamente a partir dos dossiês

**Frontend**
- ✅ Botão "Analisar trabalho" (`AnalisarButton` client component)
- ✅ Contadores reais de normais/atenção/conversar/fontes
- ✅ Lista de evidências estilométricas com z-score e código de cor
- ✅ Painel de parágrafos que destoam do próprio texto
- ✅ Parágrafos destacados com borda âmbar no texto completo

**Entregável:** ao subir um trabalho e clicar em "Analisar", o sistema exibe desvios com magnitude e destaca parágrafos suspeitos. ✅

---

## Dia 3 — Fontes e histórico de versões ✅

**Objetivo:** validar as fontes citadas e analisar como o documento foi construído.

**Backend**
- ✅ Extração de citações, URLs e DOIs do texto (`services/fontes.py`)
- ✅ Verificação de DOIs via CrossRef API
- ✅ Verificação de URLs via HTTP (status code + timeout)
- ✅ Classificação semafórica verde/amarelo/vermelho com listas curadas de domínios
- ✅ Busca de citações inline (Autor, ano) no CrossRef
- ✅ Router `POST /fontes/{id}` e `GET /fontes/{id}` — validação + persistência + atualização do dossiê
- ⏭ Google Docs API (OAuth descartado conforme risco — fora do escopo do MVP de 5 dias)

**Frontend**
- ✅ `ValidarFontesButton` — client component com loading state
- ✅ Painel semafórico de fontes com bolinha verde/âmbar/vermelho e justificativa
- ✅ Contador de fontes verificadas/precárias/problemáticas no cabeçalho do painel
- ✅ Contador de fontes atualizado nos cards de resumo (normais/atenção/conversar/fontes)

**Entregável:** ao clicar em "Validar fontes", o sistema classifica cada citação com cor e justificativa. ✅

> **Decisão:** OAuth do Google Docs descartado conforme risco previsto. Foco em validação de fontes que é o diferencial mais visível no demo.

---

## Dia 4 — Relatórios e interface completa ✅

**Objetivo:** ligar tudo numa experiência coesa end-to-end.

**Backend**
- ✅ Montagem do dossiê de evidências estruturado
- ✅ Integração com Groq API (llama-3.3-70b-versatile)
- ✅ Geração de relatório pedagógico + roteiro socrático (`services/relatorio.py`)
- ✅ Endpoint `POST /relatorio/{id}` e `GET /relatorio/{id}` — geração + persistência no dossiê
- ✅ Endpoint `POST /desfecho/{id}` e `GET /desfecho/{id}` — registro de desfecho com status e nota
- ✅ Endpoint `GET /alunos/{id}/trajetoria` — features por texto ordenados por data + labels

**Frontend**
- ✅ `GerarRoteiroButton` — modal com observações, 3 perguntas socráticas numeradas e roteiro (Groq)
- ✅ `DesfechoForm` — modal com radio buttons (esclarecido/conversa realizada/em acompanhamento) + nota livre
- ✅ `TrajetoriaChart` — gráfico de linhas recharts com seletor de features e dots destacando baselines
- ✅ Tela de perfil do aluno — trajetória estilométrica integrada abaixo da lista de trabalhos
- ✅ Tela de análise do trabalho — botões reais (GerarRoteiro + DesfechoForm), banner de desfecho registrado

**Entregável:** fluxo completo funcional — upload → análise → dossiê → roteiro socrático. ✅

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
