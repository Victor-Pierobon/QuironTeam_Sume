# Sumé — Checklist de Testes (Dia 5)

> Executar na ordem abaixo. Pré-requisito: Docker rodando, backend na porta 8001,
> frontend na porta 3000. Banco populado com `python seed.py`.

---

## 0. Setup

- [ ] `docker-compose up -d` — PostgreSQL subiu sem erro
- [ ] `uvicorn app.main:app --reload --port 8001` — backend iniciou, tabelas criadas
- [ ] `npm run dev` — frontend iniciou sem erros de compilação
- [ ] `python seed.py` — seed executou; imprimiu ids dos 3 trabalhos de TESTE
- [ ] `GET /` → `{"status": "ok", "app": "Sumé"}` ✓

---

## 1. CRUD — Turmas

| # | Ação | Endpoint | Esperado |
|---|------|----------|---------|
| 1.1 | Listar turmas | `GET /turmas/` | Array com 1 turma "8º Ano A", `total_alunos=3` |
| 1.2 | Buscar turma | `GET /turmas/1` | Objeto com `nome`, `disciplina`, `ano_serie`, `total_alunos` |
| 1.3 | Criar turma | `POST /turmas/` `{"nome":"Teste","disciplina":"Matemática","ano_serie":"9º Ano"}` | 201, id novo |
| 1.4 | Turma inexistente | `GET /turmas/9999` | 404 |

---

## 2. CRUD — Alunos

| # | Ação | Endpoint | Esperado |
|---|------|----------|---------|
| 2.1 | Listar alunos da turma | `GET /alunos/turma/1` | Array com Ana, Bruno, Carla |
| 2.2 | Status inicial dos alunos | (mesmo endpoint) | Todos `status: "ok"` antes de analisar |
| 2.3 | Criar aluno | `POST /alunos/` `{"nome":"Novo","turma_id":1}` | 201, `total_trabalhos=0`, `status:"ok"` |
| 2.4 | Buscar aluno | `GET /alunos/{id_ana}` | `nome:"Ana Costa"`, `total_trabalhos:4` |
| 2.5 | Aluno inexistente | `GET /alunos/9999` | 404 |
| 2.6 | Trajetória | `GET /alunos/{id_carla}/trajetoria` | 5 pontos ordenados por data, `feature_labels` presentes |

---

## 3. CRUD — Trabalhos

| # | Ação | Endpoint | Esperado |
|---|------|----------|---------|
| 3.1 | Listar trabalhos do aluno | `GET /trabalhos/aluno/{id_bruno}` | 4 trabalhos, 3 com `baseline:true` |
| 3.2 | Buscar trabalho | `GET /trabalhos/{id_teste_bruno}` | Objeto com `texto`, `paragrafos` |
| 3.3 | Upload .docx | `POST /trabalhos/upload` (multipart) | 201, features extraídas automaticamente |
| 3.4 | Upload .pdf | `POST /trabalhos/upload` (multipart) | 201 |
| 3.5 | Upload formato inválido | `POST /trabalhos/upload` com .txt | 400 "Formato não suportado" |
| 3.6 | Marcar como baseline | `PATCH /trabalhos/{id}/baseline?baseline=true` | Perfil recalculado |
| 3.7 | Desmarcar baseline | `PATCH /trabalhos/{id}/baseline?baseline=false` | Perfil recalculado |
| 3.8 | Trabalho inexistente | `GET /trabalhos/9999` | 404 |

---

## 4. Análise estilométrica

### 4.1 Caso 1 — Ana Costa (trabalho limpo)

- [ ] `POST /analise/{id_teste_ana}` → status 200
- [ ] `normais` ≥ 15 de 20 features
- [ ] `destaque` = 0 (zero falsos positivos)
- [ ] `status_aluno: "ok"` ou `"atencao"` (nunca "destaque")
- [ ] `paragrafos_destacados` vazio ou com poucos parágrafos
- [ ] `GET /analise/{id_teste_ana}` → retorna o mesmo resultado persistido

### 4.2 Caso 2 — Bruno Lopes (IA + fontes fabricadas)

- [ ] `POST /analise/{id_teste_bruno}` → status 200
- [ ] `destaque` ≥ 3 features com desvio alto
- [ ] `atencao` ≥ 2 features adicionais
- [ ] `status_aluno: "destaque"`
- [ ] `paragrafos_destacados` com ≥ 1 parágrafo listado
- [ ] Desvios incluem `ai_words_freq`, `avg_sentence_length`, `connective_density`
- [ ] `GET /analise/{id_teste_bruno}` → retorna resultado persistido

### 4.3 Caso 3 — Carla Mendes (evolução legítima)

- [ ] `POST /analise/{id_teste_carla}` → status 200
- [ ] `destaque` = 0 (evolução reconhecida como normal)
- [ ] Features evolutivas (`avg_sentence_length`, `lexical_diversity`) podem ter z positivo mas abaixo do limiar de destaque
- [ ] `status_aluno: "ok"` ou `"atencao"`

### 4.4 Casos de borda

- [ ] Análise sem baseline → `POST /analise/{id_sem_baseline}` retorna `status:"features_extraidas"` + aviso
- [ ] Re-análise (POST duas vezes) → não duplica features, atualiza dossiê
- [ ] `POST /analise/9999` → 404

---

## 5. Validação de fontes

### 5.1 Bruno (fontes fabricadas)

- [ ] `POST /fontes/{id_teste_bruno}` → status 200
- [ ] DOI `10.9999/amazonia-ficticia.2023.001` → `status:"vermelho"`, justificativa menciona CrossRef
- [ ] URL `https://www.relatorio-amazonia-inexistente.com.br/dados2023` → `status:"vermelho"`, URL inacessível
- [ ] Citação inline `Silva, João Carlos (2023)` → `status:"amarelo"` (não encontrado no CrossRef)
- [ ] `fontes_total` = 3, `fontes_verificadas` ≤ 1
- [ ] Dossiê atualizado: `fontes_total` e `fontes_verificadas` refletem resultado

### 5.2 Ana (sem fontes no texto)

- [ ] `POST /fontes/{id_teste_ana}` → retorna `{"total":0, "verificadas":0, "fontes":[]}`

### 5.3 Casos de borda

- [ ] `GET /fontes/{id_sem_analise}` → 404 "Nenhuma fonte validada"
- [ ] Re-validação (POST duas vezes) → fontes antigas deletadas, novas salvas
- [ ] `POST /fontes/9999` → 404

---

## 6. Relatório pedagógico (Groq)

- [ ] `POST /relatorio/{id_teste_bruno}` → status 200 (requer análise + baseline feitos)
- [ ] Resposta contém `observacoes`, `perguntas_socraticas` (lista de 3), `roteiro_conversa`
- [ ] `observacoes` não contém as palavras proibidas: "plágio", "fraude", "IA", "ChatGPT", "suspeita"
- [ ] `perguntas_socraticas` tem exatamente 3 itens
- [ ] Resultado salvo no dossiê: `GET /relatorio/{id_teste_bruno}` retorna o mesmo
- [ ] Sem baseline: `POST /relatorio/{id_sem_baseline}` → 400 "Sem baseline suficiente"
- [ ] Sem features: `POST /relatorio/{id_sem_analise}` → 400 "Features não encontradas"
- [ ] `POST /relatorio/9999` → 404

---

## 7. Desfecho

- [ ] `POST /desfecho/{id_teste_bruno}` `{"status":"conversa_realizada","nota":"Aluno explicou as fontes"}` → 200
- [ ] `GET /desfecho/{id_teste_bruno}` → retorna status, nota e `registrado_em`
- [ ] Atualizar desfecho (POST novamente com novo status) → sobrescreve, não duplica
- [ ] Status inválido `{"status":"inventado"}` → 400 com lista de valores válidos
- [ ] `GET /desfecho/{id_sem_desfecho}` → 404
- [ ] `POST /desfecho/9999` → 404

---

## 8. Frontend — fluxo completo

### Navegação

- [ ] `/` redireciona para `/dashboard`
- [ ] Dashboard exibe card da turma "8º Ano A" com contador de alunos
- [ ] Clicar na turma abre `/turma/1` com os 3 alunos

### Página de turma (`/turma/[id]`)

- [ ] 3 cards de aluno exibidos com nome e status
- [ ] Status inicial: todos "ok" (antes de analisar)
- [ ] Após analisar Bruno: card muda para "destaque" (vermelho)
- [ ] Clicar em aluno navega para `/aluno/{id}`

### Página de aluno (`/aluno/[id]`)

- [ ] Nome e matrícula exibidos
- [ ] Lista de trabalhos separada: "Baselines" e "Trabalhos entregues"
- [ ] Gráfico de trajetória exibido para Carla (4+ pontos)
- [ ] Seletor de feature no gráfico funciona (troca a linha)
- [ ] Baselines marcados visualmente diferente
- [ ] Clicar em trabalho navega para `/trabalho/{id}`

### Página de trabalho (`/trabalho/[id]`)

- [ ] Cabeçalho com título, tipo e data do trabalho
- [ ] Contadores de normais/atenção/conversar/fontes (inicialmente zerados)
- [ ] Texto completo exibido por parágrafos
- [ ] Botão "Analisar trabalho" visível

#### Sub-fluxo: Analisar

- [ ] Clicar "Analisar" dispara loading → resultado aparece
- [ ] Contadores atualizam após análise
- [ ] Para Bruno: parágrafos com desvio ganham borda âmbar
- [ ] Lista de evidências estilométricas com z-score e cor
- [ ] Painel de parágrafos destoantes aparece (Bruno)

#### Sub-fluxo: Validar fontes

- [ ] Botão "Validar fontes" aparece (ou após análise)
- [ ] Para Bruno: 3 fontes listadas com bolinhas coloridas
- [ ] DOI e URL fabricados aparecem com bolinha vermelha e justificativa
- [ ] Contador de fontes atualiza no cabeçalho

#### Sub-fluxo: Gerar roteiro

- [ ] Botão "Gerar roteiro de conversa" disponível após análise
- [ ] Clique abre modal com loading
- [ ] Modal exibe observações, 3 perguntas numeradas e roteiro
- [ ] Fechar modal funciona

#### Sub-fluxo: Desfecho

- [ ] Botão "Registrar desfecho" disponível
- [ ] Modal com radio buttons: esclarecido / conversa realizada / em acompanhamento
- [ ] Campo de nota livre
- [ ] Após salvar: banner de desfecho aparece na página

---

## 9. Casos especiais e robustez

- [ ] Texto muito curto (< 20 palavras) — features retornam zeros, não lança exceção
- [ ] Texto sem parágrafos duplos — `analisar_intra_documento` retorna lista vazia (< 3 parágrafos)
- [ ] Texto sem citações — `validar_todas` retorna `[]`
- [ ] API Groq fora do ar — `gerar_relatorio` usa fallback com perguntas padrão
- [ ] Re-análise de trabalho com dossiê existente — atualiza, não cria duplicata
- [ ] Re-validação de fontes — apaga as anteriores, salva novas

---

## 10. Demo ao vivo — 3 casos controlados

### Caso 1 — Trabalho limpo (Ana Costa)

1. Abrir página do trabalho "O bioma Cerrado" (Ana)
2. Clicar "Analisar trabalho"
3. **Esperado:** nenhum item em "conversar", poucos ou nenhum em "atenção"
4. Mostrar ao júri: _"o sistema não acusa quem escreve de forma honesta"_

### Caso 2 — Trabalho com marcadores de IA + fontes fabricadas (Bruno Lopes)

1. Abrir página do trabalho "Desmatamento da Amazônia" (Bruno)
2. Clicar "Analisar trabalho"
3. **Esperado:** vários itens em "conversar", parágrafo(s) destacado(s) em âmbar
4. Clicar "Validar fontes"
5. **Esperado:** DOI e URL vermelhos, citação amarela
6. Clicar "Gerar roteiro de conversa"
7. **Esperado:** 3 perguntas socráticas sem tom acusatório
8. Mostrar ao júri: _"o professor vê evidências, não veredito — e tem um roteiro de conversa"_

### Caso 3 — Evolução legítima (Carla Mendes)

1. Abrir perfil da Carla
2. Mostrar gráfico de trajetória (lexical_diversity crescendo ao longo de 4 baselines)
3. Abrir trabalho mais recente e analisar
4. **Esperado:** poucos alertas, sistema reconhece melhora como natural
5. Mostrar ao júri: _"aluno que mais aprendeu não é flagado como suspeito"_
