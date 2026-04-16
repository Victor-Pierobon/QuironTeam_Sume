# Sumé — MVP

**Copiloto crítico para professores analisarem produção escrita de alunos.**

Desafio 2 — Hackathon Brasília Virtual
Inteligência Artificial e Letramento Digital na Sala de Aula

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Problema](#2-problema)
3. [Proposta de solução](#3-proposta-de-solução)
4. [Princípios do produto](#4-princípios-do-produto)
5. [Funcionalidades do MVP](#5-funcionalidades-do-mvp)
6. [Arquitetura técnica](#6-arquitetura-técnica)
7. [Perfil estilométrico do aluno](#7-perfil-estilométrico-do-aluno)
8. [Análise de trajetória — lidando com evolução natural](#8-análise-de-trajetória--lidando-com-evolução-natural)
9. [Validação de fontes](#9-validação-de-fontes)
10. [Análise de versões do documento](#10-análise-de-versões-do-documento)
11. [Geração de relatórios pedagógicos](#11-geração-de-relatórios-pedagógicos)
12. [Modelo de dados](#12-modelo-de-dados)
13. [Interface do professor](#13-interface-do-professor)
14. [Cronograma de 5 dias](#14-cronograma-de-5-dias)
15. [Divisão de time](#15-divisão-de-time)
16. [Riscos e mitigações](#16-riscos-e-mitigações)
17. [Fora de escopo do MVP](#17-fora-de-escopo-do-mvp)
18. [Considerações éticas](#18-considerações-éticas)

---

## 1. Visão geral

O **Sumé** é uma ferramenta web que ajuda professores do ensino fundamental e médio a avaliarem trabalhos escritos de forma mais justa e pedagógica, em um contexto onde o uso de IA generativa e a cópia de conteúdo online se tornaram acessíveis a qualquer estudante.

A ferramenta **não é um detector de IA**. É um **copiloto crítico**: um assistente que analisa a produção do aluno sob múltiplos ângulos (padrão de escrita, confiabilidade das fontes, evolução do documento) e apresenta ao professor **evidências** que ajudam a decidir se vale uma conversa com o aluno — conversa essa que é o verdadeiro momento pedagógico.

O sistema funciona construindo um **perfil estilométrico** de cada aluno a partir de trabalhos marcados como confiáveis (feitos em sala, provas, manuscritos), e comparando cada novo trabalho com esse perfil, considerando a evolução natural do aluno ao longo do tempo.

O nome **Sumé** vem do deus egípcio da visão e da observação atenta, frequentemente representado pelo olho que enxerga o que está escondido — uma metáfora para a missão da ferramenta: trazer luz ao processo de produção do trabalho, sem julgamento prévio.

---

## 2. Problema

O processo de aprendizagem escolar virou uma "caixa-preta". O professor recebe um arquivo pronto e perdeu visibilidade sobre como ele foi construído. Os sintomas:

- **Textos impecáveis sem reflexão real.** Estudantes entregam produções elaboradas que não conseguem explicar ou aprofundar.
- **Fontes inexistentes ou duvidosas.** Citações fabricadas por LLMs, sites sem autoria, blogs sem evidência.
- **Detectores de IA atuais são um desastre.** Dão verdict binário com baixa acurácia, geram falsos positivos (especialmente contra alunos com escrita mais formal ou não-nativos) e transformam a avaliação em caça às bruxas.
- **Professor sem tempo.** Analisar trabalho por trabalho, verificar fontes, comparar com o que o aluno escrevia antes — é inviável para uma turma de 30+ alunos.

O resultado: avaliação injusta, ensino esvaziado, aluno que finge aprender, professor frustrado.

---

## 3. Proposta de solução

Uma plataforma web com três capacidades centrais:

### Capacidade 1 — Perfil de escrita por aluno
Para cada aluno, o sistema mantém um "retrato estatístico" de como aquela pessoa escreve: comprimento típico de frase, vocabulário, pontuação, erros ortográficos, uso de conectivos. Esse perfil é construído a partir de textos confiáveis (produzidos em sala ou sob supervisão).

### Capacidade 2 — Análise por trajetória
O sistema não compara o trabalho novo com uma média estática. Ele projeta a **trajetória de evolução** do aluno (aprendizagem é crescimento) e verifica se o trabalho atual está dentro ou fora dessa trajetória. Assim, um aluno que está aprendendo e melhorando não dispara falsos alertas.

### Capacidade 3 — Validação de fontes e evolução do documento
Para cada trabalho, o sistema verifica se as fontes citadas existem e são confiáveis (consultando bases acadêmicas e verificando URLs) e, quando possível, analisa o histórico de versões do documento para identificar padrões suspeitos (colagens grandes de uma vez só, ausência de edições, crescimento não-linear).

### Saída final
Um painel com **evidências categorizadas** (normal / atenção / destaque / evoluções a celebrar), que o professor usa para decidir se vale conversar com o aluno. A ferramenta também gera **roteiros de conversa socrática** que o professor pode usar para dialogar com o estudante sem tom acusatório.

---

## 4. Princípios do produto

Estes princípios guiam toda decisão de design e engenharia:

1. **Evidência, nunca veredito.** O sistema nunca diz "isso foi feito por IA" ou "isso é plágio". Apresenta observações e deixa o professor decidir.
2. **Apoio pedagógico, não polícia.** Cada saída da ferramenta leva a um diálogo educativo, não a uma punição.
3. **Reconhecer evolução.** Alunos aprendem e mudam — o sistema precisa ver isso como positivo, não como suspeita.
4. **Celebrar o que está bem.** Relatórios destacam também evoluções legítimas, não só problemas.
5. **Simplicidade para o professor.** Interface acessível para docentes sem familiaridade com tecnologia.
6. **Transparência algorítmica.** Cada flag mostra *por que* foi levantada, com números compreensíveis.
7. **Integração com o que já existe.** Aceita PDF, Word e Google Docs sem exigir mudança de rotina.

---

## 5. Funcionalidades do MVP

### 5.1 Autenticação e gestão de turmas
- Login do professor (email + senha ou OAuth Google)
- Criação de turmas e cadastro de alunos (upload de CSV ou entrada manual)
- Cada turma tem uma disciplina associada

### 5.2 Upload e parsing de trabalhos
- Aceita `.docx`, `.pdf` e link de Google Docs
- Para Google Docs: acessa histórico de revisões via API (requer OAuth do aluno ou compartilhamento)
- Extrai texto limpo, metadados, citações e links

### 5.3 Marcação de baseline
- O professor pode marcar trabalhos como "baseline confiável" (produzidos em sala, provas, manuscritos)
- Mínimo recomendado: 3 textos de 300+ palavras
- Baseline atualiza automaticamente o perfil do aluno

### 5.4 Extração de features estilométricas
- 20 features por texto (detalhadas na seção 7)
- Processamento automático ao fazer upload

### 5.5 Análise de desvios
- **Análise global:** comparação com perfil histórico
- **Análise de trajetória:** comparação com tendência projetada (seção 8)
- **Análise intra-documento:** comparação de parágrafos entre si

### 5.6 Validação de fontes
- Extração automática de citações e URLs do texto
- Verificação em bases acadêmicas e checagem de URLs
- Classificação em verde/amarelo/vermelho com justificativa

### 5.7 Linha do tempo de escrita (Google Docs)
- Visualização da evolução do documento ao longo do tempo
- Detecção de inserções grandes de texto em momento único
- Marcação de saltos suspeitos

### 5.8 Dossiê de evidências
- Painel com todas as evidências coletadas, categorizadas
- Contadores rápidos (features normais, atenção, destaque)
- Parágrafos com marcações de cor quando destoantes

### 5.9 Roteiro de conversa socrática
- Gerado pela API de uma LLM a partir das evidências
- 3 perguntas pedagógicas sem tom acusatório
- Sugestão de abordagem para o professor

### 5.10 Registro de desfecho
- Professor registra como foi a conversa com o aluno
- Histórico preservado para calibração futura

---

## 6. Arquitetura técnica

### 6.1 Stack

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Frontend | Next.js + Tailwind CSS | Rápido de desenvolver, responsivo, familiar à maioria dos hackers |
| Backend | Python + FastAPI | Ideal para processamento de texto e ML; async nativo |
| Banco de dados | PostgreSQL | Modelo hierárquico (professor → turma → aluno → trabalho) é naturalmente tabular |
| LLM | API de modelo de linguagem | Apenas para geração de relatórios pedagógicos |
| NLP | spaCy (pt_core_news_sm), nltk, textstat | Bibliotecas maduras para português |
| Parsing | python-docx, pypdf, Google Docs API | Cobertura dos três formatos aceitos |
| Correção gramatical | language-tool-python | Detecta erros em PT-BR para contagem de features |
| Validação de fontes | requests + APIs acadêmicas (CrossRef, OpenAlex) | Sem dependências pesadas |
| Auth | Auth.js (frontend) + JWT (backend) | Setup rápido |

### 6.2 Diagrama de arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│  Upload · Dashboard turma · Perfil aluno · Análise trabalho │
└────────────────────────────┬────────────────────────────────┘
                             │ REST/JSON
┌────────────────────────────┴────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                                                             │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────────┐     │
│  │  Auth    │  │  Parsing   │  │  Feature Extractor   │     │
│  │  (JWT)   │  │ (docx/pdf) │  │  (spaCy + métricas)  │     │
│  └──────────┘  └────────────┘  └──────────────────────┘     │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Trajectory Engine│  │ Source Validator │                 │
│  │ (regressão+z)    │  │ (CrossRef/HTTP)  │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                             │
│  ┌─────────────────────────────────────────┐                │
│  │  Report Generator (LLM API)             │                │
│  └─────────────────────────────────────────┘                │
└────────────┬─────────────────────────────┬──────────────────┘
             │                             │
┌────────────┴────────────┐    ┌───────────┴─────────────────┐
│    PostgreSQL           │    │   APIs externas             │
│  (alunos, trabalhos,    │    │   · CrossRef                │
│   features, perfis,     │    │   · OpenAlex                │
│   fontes, evidências)   │    │   · Google Docs             │
└─────────────────────────┘    │   · LLM (relatórios)        │
                               └─────────────────────────────┘
```

---

## 7. Perfil estilométrico do aluno

### 7.1 O que é o perfil

O perfil **não é** uma LLM treinada no aluno. É um vetor numérico de cerca de 20 dimensões que descreve como aquela pessoa escreve. Pense nisso como uma "impressão digital de escrita".

Cada pessoa tem padrões de escrita razoavelmente estáveis — comprimento típico de frase, vocabulário preferido, modo de pontuar, quantidade de erros, escolhas de conectivos. Quando esses padrões mudam bruscamente, é evidência (não prova) de que algo aconteceu: o aluno amadureceu, copiou, usou IA, ou teve ajuda externa.

### 7.2 Composição

Para cada aluno, o sistema armazena:

1. **Vetor de baseline** — média de cada feature nos textos confiáveis
2. **Vetor de variabilidade** — desvio padrão de cada feature (o quanto aquele aluno naturalmente varia)

Sem o segundo, haveria muitos falsos positivos — um aluno que naturalmente varia seria sempre flagado.

### 7.3 Features extraídas (20 no total)

#### Estrutura da frase (4 features)
- Comprimento médio de frase (palavras por sentença)
- Desvio padrão do comprimento de frase
- Comprimento médio de parágrafo
- Profundidade sintática média

#### Vocabulário (4 features)
- Diversidade lexical normalizada (medida do quanto o aluno usa palavras variadas)
- Comprimento médio de palavra em caracteres
- Porcentagem de palavras raras (fora das 5000 mais comuns do PT-BR)
- Frequência de palavras funcionais (artigos, preposições, conjunções)

#### Pontuação e mecânica (5 features)
- Vírgulas por 100 palavras
- Ponto-e-vírgula por 1000 palavras
- Travessões e parênteses por 1000 palavras
- Erros ortográficos por 1000 palavras
- Erros de concordância por 1000 palavras

#### Discurso e legibilidade (4 features)
- Índice de legibilidade adaptado para PT-BR
- Densidade de conectivos discursivos formais
- Razão de voz passiva
- Uso de primeira pessoa

#### Pegadas de IA (3 features)
- Frequência de palavras características de IA ("ademais", "outrossim", "crucial", "fundamental", "em suma")
- Variação local de comprimento de frase (humanos alternam mais)
- Uniformidade estrutural entre parágrafos

### 7.4 Construção do perfil

**Etapa 1 — Coleta de baseline**
O professor marca, na interface, trabalhos como "baseline confiável". Idealmente: textos produzidos em sala (manuscritos digitalizados ou sob supervisão), provas, trabalhos antigos pré-ChatGPT. Mínimo prático: 3 textos de 300+ palavras.

**Etapa 2 — Extração**
Cada texto passa por um pipeline que produz o vetor de 20 números representando aquele texto.

**Etapa 3 — Cálculo de baseline e variabilidade**
A partir dos vetores dos textos confiáveis, o sistema calcula a média e o desvio padrão de cada feature. Esses valores formam o perfil do aluno.

**Etapa 4 — Calibração para poucos dados**
Com só 3 textos, o desvio padrão é instável. O sistema mistura a variabilidade individual do aluno com a variabilidade típica da turma toda, evitando que uma baseline pequena gere alertas absurdos. Conforme mais textos confiáveis são adicionados, o peso do aluno individual aumenta.

---

## 8. Análise de trajetória — lidando com evolução natural

### 8.1 Por que isso é crítico

Estudantes do ensino fundamental **mudam dramaticamente** em pouco tempo:
- Vocabulário cresce
- Estruturas sintáticas amadurecem
- Conectivos formais aparecem
- Erros caem
- Registro fica mais formal

Repare: **todas essas evoluções legítimas se parecem exatamente com os sinais que o sistema usa para detectar IA**. Um sistema mal calibrado flaga o aluno que mais aprendeu como o mais suspeito. Isso é catastrófico.

### 8.2 A solução: regressão de tendência

Para cada feature, o sistema ajusta uma reta de tendência sobre os textos do aluno ao longo do tempo e compara o trabalho atual com o **valor esperado pela tendência**, não com a média estática.

Isso significa que:
- Se o aluno vinha melhorando consistentemente, a melhoria é projetada e considerada normal
- Só desvios *acima* da trajetória esperada disparam alertas
- O sistema reconhece o aluno como ele é hoje, não como ele era no início do ano

Textos mais recentes pesam mais no cálculo (decaimento por recência), de forma que a baseline acompanha a evolução naturalmente.

### 8.3 Limiares assimétricos

Features têm direções de evolução esperadas:

| Feature | Direção esperada | Tipo |
|---|---|---|
| Comprimento médio de frase | crescer | evolutiva |
| Vocabulário raro | crescer | evolutiva |
| Erros ortográficos | decrescer | evolutiva |
| Densidade de conectivos | crescer | evolutiva |
| Palavras funcionais | estável | estilística |
| Vírgulas por 100 palavras | estável | estilística |
| Ponto-e-vírgula | estável | estilística |

**Regra:**
- Se a mudança vai na direção esperada: dar benefício da dúvida (exigir desvio muito grande para flagar)
- Se vai na direção inversa: mais sensível
- Para features estilísticas (que não deveriam mudar muito): sensível em qualquer direção

### 8.4 Análise intra-documento (a parte mais valiosa)

A evidência mais forte vem de comparar parágrafos **dentro do mesmo trabalho**. Não há razão para um aluno mudar drasticamente de estilo entre parágrafos de uma mesma redação.

Saída típica: *"o parágrafo 3 tem comprimento de frase, vocabulário e densidade de conectivos muito diferentes dos outros parágrafos deste mesmo trabalho"*. Isso é evidência muito mais forte que comparação global, porque elimina a hipótese "o aluno mudou".

### 8.5 Comparação com a turma como controle

Se toda a turma melhorou 25% em diversidade lexical neste bimestre, um aluno que melhorou 30% é normal — todos estão evoluindo juntos por causa do ensino. O sistema calcula trajetória média da turma como linha de base adicional.

Flag vira: *"evolução muito superior à esperada para o ritmo da turma"*, muito mais defensável.

---

## 9. Validação de fontes

### 9.1 Extração

O parser busca no texto:
- Referências em formato ABNT/APA (ex: "Silva, 2023")
- URLs completas
- DOIs explícitos
- Menções a autores + ano

### 9.2 Verificação

Para cada citação identificada:

| Verificação | Método | Resultado |
|---|---|---|
| DOI existe? | API CrossRef | válido/inválido |
| Artigo existe por título/autor? | API OpenAlex | encontrado/não encontrado |
| URL retorna HTTP 200? | Requisição HTTP | online/offline/404 |
| Domínio é confiável? | Lista curada | .gov/.edu/periódicos vs. blogs anônimos |
| Tem autoria identificável? | Análise da página | sim/não |
| Citação no texto corresponde à fonte? | Comparação semântica | consistente/inconsistente |

### 9.3 Classificação

**Verde (confiável):** periódico indexado, DOI verificado, domínio institucional
**Amarelo (precária):** sem revisão por pares, autoria incerta, blog sem curadoria
**Vermelho (problemática):** não localizada em bases, URL 404, domínio inexistente

### 9.4 Lista de domínios

O sistema mantém listas curadas:
- **Verde:** `.gov.br`, `.edu.br`, SciELO, periódicos indexados, organizações reconhecidas
- **Amarelo:** Wikipedia, blogs corporativos, portais sem peer-review
- **Vermelho:** sites de "resumos prontos", agregadores sem autoria, domínios conhecidos por conteúdo fabricado

---

## 10. Análise de versões do documento

**Este é o diferencial mais forte da ferramenta** — e está explicitamente no desafio ("enxergar a evolução do trabalho desde o rascunho até a entrega final").

### 10.1 Para Google Docs (via API)

O Google Docs mantém histórico completo de revisões. A API permite acessar:
- Timestamp de cada revisão
- Conteúdo de cada versão
- Identidade do autor de cada mudança

### 10.2 Métricas derivadas

- **Tempo total ativo no documento** (soma das sessões de edição)
- **Número de sessões distintas**
- **Maior inserção única** (suspeito se for >30% do texto final)
- **Curva de crescimento** (linear? saltos?)
- **Proporção de edição vs. adição** (escrita real tem muita revisão; geração tem pouca)

### 10.3 Padrões suspeitos

| Padrão | Interpretação |
|---|---|
| 95% do texto inserido em uma sessão | possível cópia/colagem |
| Zero edições, só inserções | possível geração direta |
| Tempo ativo <10% do esperado para o tamanho | trabalho não foi escrito de fato |
| Inserção grande de texto formatado diferente | colagem de fonte externa |

### 10.4 Para .docx

O formato `.docx` suporta track changes. Se ativado, o parser extrai histórico. Se não, essa análise fica indisponível e o sistema avisa.

### 10.5 Visualização

Gráfico de linha mostrando "tamanho do documento ao longo do tempo", com marcadores nos saltos. Professor vê visualmente se o trabalho foi construído gradualmente ou apareceu de uma vez.

---

## 11. Geração de relatórios pedagógicos

### 11.1 Fluxo

Toda análise produz um **dossiê de evidências** estruturado com tudo que foi descoberto: desvios estatísticos, parágrafos destoantes, fontes problemáticas, evoluções positivas. Esse dossiê é enviado para uma LLM (modelo de linguagem) que o transforma em texto pedagógico.

**A LLM não tem acesso ao texto bruto do aluno nem ao perfil completo.** Só ao dossiê de evidências já calculado. Isso elimina risco de alucinação: a LLM não pode inventar padrões que não estão nos dados — só comunica o que o sistema estatístico encontrou.

### 11.2 Conteúdo do dossiê

O dossiê contém:
- Identificação do aluno e do trabalho
- Tamanho da baseline e período coberto
- Lista de desvios globais por feature, com magnitude e se excede a trajetória esperada
- Parágrafos destoantes do próprio documento
- Fontes problemáticas com motivo
- Evoluções positivas a celebrar

### 11.3 Tarefas da LLM

A LLM recebe instruções para produzir três coisas:

1. **Observações para o professor** — 3 a 5 frases em linguagem acessível, sem jargão estatístico, traduzindo as evidências numéricas
2. **Perguntas socráticas** — 3 perguntas abertas que o professor pode fazer ao aluno para verificar compreensão e autoria, focadas nos trechos destoantes, sem tom acusatório
3. **Roteiro de conversa** — 5 a 7 linhas sugerindo como conduzir o diálogo, reforçando também os pontos positivos

### 11.4 Tom obrigatório

A LLM é instruída a manter tom pedagógico, não forense — linguagem que um professor usaria com um aluno que ele respeita. Não pode usar palavras como "fraude", "plágio", "trapaça", "suspeita", "acusação". O objetivo da conversa gerada é educar e dialogar, não confrontar.

---

## 12. Modelo de dados

O sistema organiza informação em torno de uma hierarquia simples: professor possui turmas, turmas possuem alunos, alunos possuem trabalhos, e trabalhos têm features, fontes, parágrafos e versões associados.

### 12.1 Entidades principais

**Professor:** dados de autenticação e identificação do docente.

**Turma:** vinculada a um professor, com nome, disciplina e ano/série.

**Aluno:** vinculado a uma turma, com nome e matrícula opcional.

**Trabalho:** vinculado a um aluno. Armazena título, tipo (redação, relatório, resenha etc.), texto completo, formato de origem, marcador de baseline, data de entrega.

**Features do trabalho:** os 20 valores numéricos extraídos de cada texto, armazenados em formato chave-valor.

**Perfil do aluno:** dados derivados (recalculados quando a baseline muda) — média, desvio padrão, inclinação da tendência e qualidade do ajuste para cada feature.

**Fontes:** citações encontradas no trabalho, com URL ou DOI quando aplicável, status semafórico (verde/amarelo/vermelho) e justificativa.

**Parágrafos destoantes:** parágrafos identificados como anômalos dentro do próprio documento, com índice, texto e features que destoaram.

**Versões do documento:** série temporal das edições (apenas para Google Docs), com timestamp, tamanho e identificação de autor.

**Dossiê:** cache da análise completa do trabalho em formato estruturado, mais o relatório pedagógico gerado.

**Desfecho:** registro do que o professor fez após a análise — esclarecido, em acompanhamento, conversa realizada — e nota livre.

### 12.2 Princípios do modelo

- **Dados derivados são recalculáveis.** Perfil e dossiê podem ser apagados e refeitos a partir dos dados primários (trabalhos e features).
- **Histórico é preservado.** Trabalhos anteriores nunca são perdidos, mesmo que o aluno saia da turma.
- **Anonimização possível.** Estrutura permite separar identidade do aluno dos dados estilométricos para análises agregadas ou exportação.
- **Auditoria.** Todas as ações do professor (marcar baseline, registrar desfecho) ficam datadas e atribuídas.

---

## 13. Interface do professor

### 13.1 Princípios de UI

- Estética editorial, não corporativa (afasta do "painel de vigilância")
- Tipografia serif em títulos (tom acadêmico)
- Paleta em tons terrosos (papel, verde musgo, âmbar) — não azul tech
- Vocabulário pedagógico: "pontos para conversar", "atenção", "destaque", "esclarecer", "celebrar"
- **Nunca** usar: "plágio", "fraude", "IA detectada", "suspeito"

### 13.2 Telas principais

**Tela 1 — Dashboard da turma**
- Lista de alunos com cartões
- Cada cartão mostra: nome, status (ok/atenção/destaque), sparkline do histórico
- Contadores no topo (total, normais, em atenção, em destaque)
- Filtros: "todos", "requerem atenção", "baseline curta"
- Busca por nome

**Tela 2 — Perfil do aluno**
- Dados do aluno
- Gráfico de trajetórias estilométricas (com seletor de feature)
- Resumo do perfil adaptado ao status
- Lista cronológica de trabalhos (baseline destacados)

**Tela 3 — Análise do trabalho**
- Cabeçalho com metadados do trabalho
- 4 contadores: normais / atenção / destaque / fontes verificadas
- Gráfico de trajetória da feature mais relevante
- Texto do trabalho com parágrafos coloridos por nível de desvio
- Painel lateral com evidências categorizadas
- Classificação semafórica das fontes
- Botões: "Gerar roteiro de conversa", "Analisar parágrafo", "Marcar como esclarecido"

**Tela 4 — Modais**
- Roteiro socrático (gerado pela LLM)
- Análise intra-documento de parágrafo específico
- Formulário de registro de desfecho

### 13.3 Estados visuais

| Status | Cor | Uso |
|---|---|---|
| Normal | verde musgo | dentro do padrão e da trajetória |
| Atenção | âmbar | variação moderada, acompanhar |
| Destaque | vermelho terra | conversar com o aluno |
| Celebrar | verde claro | evolução positiva |

---

## 14. Cronograma de 5 dias

### Dia 1 — Fundação
- Setup de repositórios (frontend + backend)
- Setup do banco de dados com migrations
- Autenticação básica (login/cadastro de professor)
- Parsing de .docx e .pdf (extração de texto bruto)
- Schema inicial preenchido
- Frontend com roteamento básico e layout
- **Entregável:** professor consegue fazer login e subir um arquivo

### Dia 2 — Inteligência estilométrica
- Pipeline de extração de features (20 métricas)
- Cálculo e armazenamento de baseline
- Algoritmo de análise de tendência
- Análise intra-documento (parágrafos vs. parágrafos)
- **Entregável:** sistema identifica desvios e gera flags

### Dia 3 — Fontes e versões
- Extração de citações do texto
- Integração com bases acadêmicas
- Verificação de URLs e classificação semafórica
- Integração com Google Docs API (histórico de revisões)
- Análise de padrões suspeitos de edição
- **Entregável:** sistema valida fontes e analisa versões

### Dia 4 — Relatórios e UI
- Integração com API da LLM
- Geração do dossiê
- Geração de relatório pedagógico e roteiro socrático
- Implementação das três telas principais
- Gráficos de trajetória
- **Entregável:** fluxo completo funcional end-to-end

### Dia 5 — Polish e apresentação
- Casos de demonstração preparados:
  - Trabalho "limpo" (mostra ausência de falsos positivos)
  - Trabalho com IA + fontes fabricadas (mostra detecção)
  - Aluno com evolução legítima (mostra trajetória funcionando)
- Refinamento visual
- Vídeo/slides do pitch
- Ensaio da apresentação
- **Entregável:** demo polida e pitch ensaiado

---

## 15. Divisão de time

Time ideal: **4-5 pessoas**

| Papel | Responsabilidades |
|---|---|
| Backend / Parsing | FastAPI, banco, parsers de .docx/.pdf, auth |
| Estilometria / ML | Feature extraction, regressão, análise intra-documento |
| Integrações | Google Docs API, bases acadêmicas, LLM |
| Frontend | Next.js, Tailwind, gráficos, UX |
| Produto / Pitch | Casos de demo, pitch, apresentação, produto owner |

**Importante:** o papel de "produto/pitch" é essencial em hackathon. Alguém precisa ensaiar a apresentação, preparar casos de demo que funcionem ao vivo, e defender a solução. Ter 5 codadores e ninguém cuidando da narrativa é erro comum.

---

## 16. Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Google Docs API com OAuth consome dia inteiro | alta | médio | Deixar como feature avançada; priorizar .docx |
| Falsos positivos no demo ao vivo | média | alta | Preparar casos controlados; sempre enquadrar como evidência |
| Baseline pequena gera alertas espúrios | alta | médio | Calibração com prior da turma; comunicar incerteza |
| API da LLM fora do ar durante demo | baixa | alta | Ter respostas pré-geradas em cache |
| LanguageTool pesado demais | média | baixo | Usar versão embarcada ou fallback para regex |
| Parsing de PDFs escaneados falha | alta | médio | Avisar no upload; exigir PDFs com texto nativo |
| Tempo de processamento >30s | média | médio | Processamento assíncrono com indicador de progresso |

---

## 17. Fora de escopo do MVP

Explicitamente **não vai estar** na versão de 5 dias:

- Fine-tuning de LLM por aluno (inviável e desnecessário)
- App mobile nativo
- Integração com LMS (Moodle, Google Classroom)
- Notificações em tempo real
- OCR para PDFs escaneados
- Análise de imagens/gráficos inseridos no trabalho
- Sistema de turmas colaborativas entre professores
- Exportação de relatórios em PDF

Essas ficam no roadmap para versões futuras se o produto for adiante.

---

## 18. Considerações éticas

### 18.1 Viés algorítmico

Features estilométricas podem ter viés contra alunos:
- Não-nativos ou bilíngues
- Com dislexia ou outras condições
- De contextos socioeconômicos diversos (acesso a livros, apoio familiar)

**Mitigação:** comparação sempre intra-individual (cada aluno com ele mesmo, não com padrão universal). Isso anula grande parte do viés demográfico.

### 18.2 Privacidade

Dados de menores de idade exigem cuidado especial (LGPD + ECA).

**Mitigação:**
- Dados criptografados em repouso e em trânsito
- Retenção limitada (dados deletados ao final do ano letivo)
- Nenhum dado enviado para a LLM sem anonimização
- Consentimento dos responsáveis explicitado
- Relatório de transparência disponível

### 18.3 Uso punitivo

Se a ferramenta for usada para acusar alunos, causa mais dano que benefício.

**Mitigação:**
- Linguagem do produto orientada a diálogo, não a acusação
- Treinamento incluído para professores adotantes
- Logs de uso auditáveis
- Termos de uso que proíbem uso punitivo direto

### 18.4 Papel do professor

A ferramenta **nunca substitui** o julgamento pedagógico. É um assistente. O professor mantém total autonomia.

---

## Apêndice A — Exemplo de evidências num trabalho real

Para um trabalho da aluna "Maria Silva" (fictícia, 8º ano) sobre mineração no cerrado, o sistema retornaria:

**Contadores:** 12 normais · 5 atenção · 3 destaque · 6/8 fontes verificadas

**Evidências destaque:**
1. Parágrafo 3 destoa do próprio trabalho
2. Duas fontes não localizadas em bases acadêmicas
3. Padrão de pontuação mudou (6 ponto-e-vírgulas; baseline 0-1)

**Evidências atenção:**
- Salto de 65% no uso de conectivos formais acima da trajetória esperada
- Aparição de palavras atípicas ("ademais", "outrossim", "perpassa")

**Evoluções a celebrar:**
- Diversidade lexical segue trajetória de crescimento desde fevereiro
- Erros ortográficos em queda consistente (de 9 para 2 por 1000 palavras)

**Roteiro socrático gerado:**
1. "Maria, gostei muito do seu terceiro parágrafo. Você pode me contar com suas palavras o que significa 'vetor multifacetado de degradação ambiental'?"
2. "Esse parágrafo ficou com um tom bem diferente dos outros. Me conta como você chegou nesse jeito de escrever — leu algum artigo, conversou com alguém?"
3. "Sobre as fontes do Souza (2023) e do Cerrado em Dados — consegue lembrar onde encontrou? Podemos procurar juntas para confirmar."

---

## Apêndice B — Métricas de sucesso

Para avaliar se o MVP cumpre seu papel na apresentação:

- **Funcionalidade end-to-end:** upload → análise → relatório em menos de 60 segundos
- **Precisão qualitativa:** casos preparados mostram evidências coerentes
- **Ausência de falsos positivos:** trabalho limpo não dispara alertas
- **Identificação correta:** trabalho com IA + fontes fabricadas produz dossiê rico
- **Comunicação pedagógica:** roteiros socráticos são usáveis diretamente pelo professor

Para produção futura, métricas adicionais:
- Taxa de adoção por professores (% que usam após teste)
- Taxa de conversas geradas que levam a feedback positivo do aluno
- Redução do tempo de avaliação reportada pelos docentes
- Tempo médio entre upload e decisão pedagógica

---

**Documento vivo — atualizar ao longo do desenvolvimento.**
