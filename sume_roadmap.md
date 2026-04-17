# Sumé — Roadmap pós-hackathon

Especificação das próximas quatro funcionalidades prioritárias,
ordenadas por impacto no produto.

---

## Feature 1 — LanguageTool: erros reais de ortografia e concordância ✅ CONCLUÍDO

> **Implementado em:** `backend/app/services/languagetool_service.py`
>
> Estratégia de 3 camadas: API pública REST do LanguageTool → instância local Java 17+ → heurísticas regex PT-BR.
> As features `spelling_errors_per_1000` e `agreement_errors_per_1000` agora retornam valores reais em
> `routers/analise.py` (versão async) e `services/perfil.py` (versão sync para recalcular perfil).
> Java 1.8 não é suportado pela biblioteca local — a camada 1 (API REST pública) resolve isso sem Java.

### Contexto

As features `spelling_errors_per_1000` e `agreement_errors_per_1000` são hoje
**placeholders que retornam 0.0**. São dois dos sinais mais valiosos do perfil
estilométrico: um aluno que normalmente erra 8 vezes por mil palavras e de repente
erra 0 é um desvio muito mais concreto do que variação em comprimento de frase.

### O que fazer

Integrar o **LanguageTool** (`language-tool-python`) ao pipeline de extração de
features. A biblioteca pode rodar em modo embarcado (sem servidor externo) com as
regras de português brasileiro.

### Implementação

**Backend — `services/features.py`**

Substituir os dois placeholders:

```python
# Adicionar no topo
import language_tool_python

_lt: language_tool_python.LanguageTool | None = None

def _get_lt() -> language_tool_python.LanguageTool:
    global _lt
    if _lt is None:
        _lt = language_tool_python.LanguageTool("pt-BR")
    return _lt


def _contar_erros(texto: str, n_palavras: int) -> tuple[float, float]:
    """Retorna (spelling_per_1000, agreement_per_1000)."""
    if n_palavras == 0:
        return 0.0, 0.0
    try:
        lt = _get_lt()
        matches = lt.check(texto)
        spelling   = sum(1 for m in matches if m.ruleId.startswith("SPELL"))
        agreement  = sum(1 for m in matches if "CONCORDANCIA" in m.ruleId
                         or "AGREEMENT" in m.ruleId)
        return spelling / n_palavras * 1000, agreement / n_palavras * 1000
    except Exception:
        return 0.0, 0.0
```

Chamar `_contar_erros(texto, n_words)` dentro de `extrair_features()` e substituir
os valores `0.0` pelos retornos reais.

**Performance**

O LanguageTool é lento (~1–3 s por texto). Para não travar o upload:

- Extrair as outras 18 features imediatamente no upload (síncrono).
- Disparar a extração das 2 features do LanguageTool em background
  (`asyncio.create_task` ou Celery) e atualizar o banco quando concluir.
- No frontend, mostrar um indicador "verificando gramática…" nas duas features
  enquanto o valor ainda for `0.0` e o trabalho for recente (< 5 min).

**Alternativa leve**

Se o LanguageTool for pesado demais em produção, substituir por um dicionário
de formas erradas comuns do PT-BR (lista curada de ~5 000 erros frequentes) para
a feature de ortografia, e heurísticas de concordância de gênero/número para
a outra. Isso sacrifica precisão mas mantém velocidade.

### Impacto esperado

Com as duas features funcionando, o desvio estilométrico de textos gerados por IA
(que têm erros próximos de zero) ficará muito mais pronunciado nos casos do demo.
Também melhora a proteção contra falsos positivos: alunos que normalmente erram
muito e de repente acertam tudo chamam mais atenção; alunos que já escrevem bem
não são penalizados.

---

## Feature 2 — Google Docs: histórico de versões e padrões de edição ✅ CONCLUÍDO

> **Implementado em:** `backend/app/services/gdocs.py`, `backend/app/routers/gdocs.py`, `backend/app/models/gdocs.py`
>
> Autenticação via Service Account (configure `GOOGLE_SERVICE_ACCOUNT_JSON` no `.env`).
> Endpoints `POST /gdocs/{id}` (importar) e `GET /gdocs/{id}` (ler). Detecta 4 padrões suspeitos:
> colagem_unica, sem_edicoes, tempo_insuficiente, sessao_unica.
> Frontend: componente `GDocsPanel` na página do trabalho com import form, 5 métricas e lista de padrões.
> Graceful degradation: se `google-api-python-client` não estiver instalado, retorna 503 com mensagem clara.

### Contexto

O desafio do hackathon pede explicitamente que a ferramenta "enxergue a evolução
do trabalho desde o rascunho até a entrega final". O Google Docs mantém histórico
completo e auditável de todas as edições. Nenhum outro dado revela tão claramente
se um texto foi escrito ou colado.

### Fluxo de usuário

1. Professor pede ao aluno que compartilhe o link do Google Doc (ou que adicione
   uma conta de serviço como leitor).
2. Na tela de upload, o professor escolhe "Google Docs" como origem e cola o link.
3. O sistema autentica, busca o histórico de revisões e calcula as métricas.
4. A tela de análise do trabalho exibe uma linha do tempo visual e os padrões detectados.

### Autenticação

Duas opções — implementar a mais simples primeiro:

**Opção A — Service Account (recomendada para MVP)**
O professor compartilha o doc com um e-mail de service account da aplicação
(`sume@sume-project.iam.gserviceaccount.com`). Sem OAuth do aluno, sem popup.
Funciona para qualquer doc compartilhado. Limitação: o doc precisa ter sido
compartilhado explicitamente.

**Opção B — OAuth do professor**
O professor autentica sua conta Google uma vez. O sistema acessa os docs da turma
via Drive API. Mais poderoso, mais complexo de implementar.

### Métricas a extrair

| Métrica | Como calcular | O que indica |
|---|---|---|
| Tempo total ativo | Soma das diferenças entre revisões com gap < 30 min | Quanto tempo o aluno realmente passou escrevendo |
| Número de sessões | Grupos de revisões separados por gap > 30 min | Escrita em etapas (saudável) vs. de uma vez |
| Maior inserção única | Max de caracteres adicionados em uma revisão | Colagem grande de uma só vez |
| Razão edição/adição | Deletions / total changes | Escrita real tem muita revisão; geração tem pouca |
| Curva de crescimento | Tamanho do doc por revisão | Linear (saudável) vs. saltos (suspeito) |
| Proporção final colada | Chars da última sessão / tamanho final | > 60% numa sessão final é sinal forte |

### Padrões suspeitos e seus limiares

```python
PADROES = {
    "colagem_unica": {
        "condicao": "maior_insercao / tamanho_final > 0.5",
        "mensagem": "Mais da metade do texto foi inserido em uma única edição.",
        "nivel": "destaque",
    },
    "sem_edicoes": {
        "condicao": "razao_edicao_adicao < 0.05",
        "mensagem": "Quase nenhuma revisão — o texto parece ter sido gerado, não escrito.",
        "nivel": "atencao",
    },
    "tempo_insuficiente": {
        "condicao": "tempo_ativo_min < tamanho_palavras * 0.3",
        "mensagem": "Tempo ativo muito abaixo do esperado para o tamanho do texto.",
        "nivel": "atencao",
    },
    "sessao_unica": {
        "condicao": "num_sessoes == 1 and tamanho_palavras > 300",
        "mensagem": "Todo o texto foi produzido em uma única sessão contínua.",
        "nivel": "atencao",
    },
}
```

### Implementação

**Backend**

Novo serviço `services/gdocs.py`:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

async def buscar_historico(doc_id: str) -> dict:
    """Retorna métricas de edição extraídas do histórico do Google Doc."""
    ...

async def calcular_metricas_edicao(revisoes: list[dict]) -> dict:
    """Calcula as 6 métricas de padrão de edição."""
    ...

async def detectar_padroes(metricas: dict) -> list[dict]:
    """Retorna lista de padrões suspeitos encontrados."""
    ...
```

Novo modelo `HistoricoVersao` no banco:
- `trabalho_id`
- `num_sessoes`, `tempo_ativo_min`, `maior_insercao_pct`
- `razao_edicao_adicao`, `proporcao_final_colada`
- `padroes_json` (lista serializada dos padrões detectados)
- `revisoes_json` (série temporal para o gráfico)

Novo router `routers/gdocs.py`:
- `POST /gdocs/{trabalho_id}` — recebe link do doc, busca histórico, salva métricas
- `GET /gdocs/{trabalho_id}` — retorna métricas e série temporal

**Frontend**

Na tela de upload: opção "Google Docs" além de .docx e .pdf, com campo para colar o link.

Na tela de análise do trabalho: novo painel "Histórico de edição" com:
- Gráfico de linha: tamanho do documento ao longo do tempo (recharts, já instalado)
- Marcadores nos saltos grandes
- Lista de padrões detectados com cor (âmbar/vermelho)
- Linha do tempo resumida: "3 sessões · 47 min ativos · maior inserção: 23%"

### Notas de privacidade

- O conteúdo das revisões intermediárias **não é armazenado**, só as métricas.
- O aluno deve ser informado de que o histórico do doc será analisado.
- Sugerir que o professor informe isso no enunciado do trabalho.

---

## Feature 3 — Comparação entre alunos da turma ✅ CONCLUÍDO

> **Implementado em:** `backend/app/routers/comparacao.py` (registrado em `main.py` como prefixo `/turmas`)
>
> Endpoint `GET /turmas/{turma_id}/comparacao` retorna heatmap de z-scores, pares similares (similaridade coseno ≥ 90%)
> e distribuição por feature. Frontend: página `/turma/[id]/comparacao` com `HeatmapTurma` (tabela colorida)
> e `ListaParesSimilares` (cards com % de similaridade e features em comum). Botão "Comparar trabalhos da turma"
> adicionado à página da turma.

### Contexto

Quando vários alunos da mesma turma entregam trabalhos sobre o mesmo tema com
perfis estilométricos muito similares, isso é uma evidência coletiva que nenhuma
análise individual captura. Pode indicar que usaram o mesmo gerador, que copiaram
uns dos outros, ou que colaboraram de forma não declarada.

A análise é sempre apresentada como **evidência de padrão coletivo**, nunca como
acusação individual.

### Fluxo de usuário

1. Professor está na tela da turma.
2. Clica em "Comparar trabalhos da turma".
3. Seleciona um período ou uma atividade (ex: "redações de setembro").
4. O sistema exibe o painel de comparação.

### Visualizações

**Mapa de calor de features**

Tabela com alunos nas linhas e features nas colunas. Cada célula colorida pelo
z-score daquele aluno naquela feature em relação à média da turma. Permite ver
de relance se um grupo de alunos tem o mesmo padrão incomum.

```
              | Div. lexical | Conect. | Frases | Palavras IA |
|-------------|-------------|---------|--------|-------------|
| Ana Costa   |   normal    | normal  | normal |   normal    |
| Bruno Lopes |  ⚠ alto    | 🔴 alto | 🔴 alto|  🔴 muito   |
| Carla Mendes|   normal    | normal  | ↑ alto |   normal    |
| Diego F.    |  ⚠ alto    | 🔴 alto | 🔴 alto|  🔴 muito   |
```

Bruno e Diego com padrão similar → evidência para conversa com os dois.

**Gráfico de dispersão por feature**

Dois eixos selecionáveis (ex: diversidade lexical × densidade de conectivos).
Cada aluno é um ponto. Pontos próximos = escrita similar nessas duas dimensões.
Clusters visíveis indicam trabalhos que se parecem demais.

**Índice de similaridade entre pares**

Para cada par de alunos, calcular similaridade coseno entre os vetores de features.
Listar os pares com similaridade > limiar (ex: > 0.92) com destaque visual.
O professor clica em um par e vai direto para os dois trabalhos.

### Implementação

**Backend**

Novo endpoint `GET /turmas/{id}/comparacao?periodo=2024-09`:

```python
# Busca todos os trabalhos não-baseline da turma no período
# Para cada trabalho, recupera o vetor de features do banco
# Calcula:
#   - z-score de cada aluno em cada feature relativo à média da turma
#   - Similaridade coseno entre todos os pares
# Retorna estrutura com:
#   - heatmap_data: list[{aluno, features: {nome: z_score}}]
#   - pares_similares: list[{aluno_a, aluno_b, similaridade, features_comuns}]
#   - distribuicao: {feature: {media, std, valores: list[{aluno, valor}]}}
```

Função de similaridade coseno (puro Python, sem dependências extras):

```python
def similaridade_coseno(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a ** 2 for a in v1) ** 0.5
    norm2 = sum(b ** 2 for b in v2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)
```

**Frontend**

Nova página `turma/[id]/comparacao` ou painel lateral na página da turma.

Componentes novos:
- `HeatmapTurma` — tabela colorida com z-scores
- `ScatterTurma` — dispersão com recharts (ScatterChart já disponível)
- `ListaParesSimilares` — cards com par de alunos e botão para abrir os dois trabalhos

### Notas pedagógicas

- Os títulos das visualizações usam linguagem de "padrão" e "similaridade", nunca "cópia" ou "plágio".
- A análise de similaridade entre pares só é exibida se ambos os alunos tiverem ao menos 1 baseline cadastrado (sem baseline, o vetor de features do trabalho pode ser enganoso).
- Sugerir ao professor que use os pares similares para uma conversa em grupo, não para confronto individual.

---

## Feature 4 — Export do dossiê em PDF ✅ CONCLUÍDO

> **Implementado em:** `backend/app/routers/export.py` (registrado em `main.py`)
>
> Usa `fpdf2` (não WeasyPrint) para evitar dependência GTK. Gera PDF com cabeçalho verde, rodapé com
> número de página, 7 seções: Identificação, Resumo (contadores coloridos), Evidências estilométricas,
> Parágrafos destoantes, Fontes, Roteiro socrático, Desfecho.
> Encoding Latin-1 via helper `_ascii()`. Endpoint: `GET /export/{trabalho_id}/pdf`.
> Frontend: botão "Exportar PDF" aparece na página do trabalho quando a análise existe.

### Contexto

O professor precisa levar as evidências para uma reunião com a coordenação,
para o conselho de classe ou para uma conversa com os responsáveis do aluno.
Um PDF formatado e legível vale mais do que uma screenshot da tela.

### Conteúdo do PDF

O documento segue a mesma estrutura do dossiê digital:

```
SUMÉ — Dossiê pedagógico
────────────────────────────────────────────
Aluno:        Bruno Lopes               Matrícula: 2024002
Trabalho:     Desmatamento da Amazônia  Tipo: redação
Data entrega: 18/09/2024                Baseline: 3 textos

RESUMO
  ● 4 métricas em destaque · 3 em atenção · 13 normais
  ● 1 parágrafo que destoa do próprio texto
  ● 3 fontes verificadas · 2 problemáticas · 1 precária

EVIDÊNCIAS ESTILOMÉTRICAS
  🔴 Palavras típicas de IA          z = +4.2  (valor: 8.1 · baseline: 0.0)
  🔴 Comprimento médio de frase      z = +3.8  (valor: 28.4 · baseline: 10.2)
  ⚠  Densidade de conectivos         z = +2.1  (valor: 4.3 · baseline: 0.8)
  ...

PARÁGRAFO QUE DESTOA (parágrafo 3)
  "A problemática ambiental que perpassa a questão do desmatamento..."
  Métricas destoantes: Palavras de IA · Comprimento de frase · Conectivos

FONTES CITADAS
  🔴 10.9999/amazonia-ficticia.2023.001 — DOI não encontrado (CrossRef)
  🔴 https://www.relatorio-amazonia... — URL inacessível (404)
  ⚠  Silva, João Carlos (2023)       — Não encontrado no CrossRef

ROTEIRO DE CONVERSA (gerado em 18/09/2024)
  Observações: [texto das observações]

  Perguntas sugeridas:
  1. [pergunta 1]
  2. [pergunta 2]
  3. [pergunta 3]

  Como conduzir: [roteiro]

DESFECHO REGISTRADO
  Status: Conversa realizada
  Nota: Aluno explicou as fontes mas não soube desenvolver os argumentos.
────────────────────────────────────────────
Gerado pelo Sumé em 20/09/2024 · Uso pedagógico — não constitui prova formal.
```

### Implementação

**Opção A — Geração no backend com WeasyPrint (recomendada)**

WeasyPrint converte HTML/CSS para PDF com alta fidelidade.
O backend monta um template HTML com os dados do dossiê e gera o PDF em memória.

```python
# routers/export.py
from weasyprint import HTML
from jinja2 import Template

@router.get("/{trabalho_id}/pdf")
async def exportar_pdf(trabalho_id: int, db: AsyncSession = Depends(get_db)):
    # Busca todos os dados do dossiê
    dados = await montar_dossie_completo(trabalho_id, db)
    # Renderiza template HTML
    html = Template(TEMPLATE_PDF).render(**dados)
    # Gera PDF
    pdf = HTML(string=html).write_pdf()
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="sume-dossie-{trabalho_id}.pdf"'},
    )
```

O template HTML do PDF segue a paleta do produto (verde escuro, âmbar, vermelho)
e usa fontes serif nos títulos para manter a identidade visual.

**Opção B — Geração no frontend com `@react-pdf/renderer`**

Monta o PDF diretamente no browser a partir dos dados já carregados na página.
Vantagem: sem dependência nova no backend.
Desvantagem: o pacote é ~500 KB e aumenta o bundle.

**Recomendação:** começar com a Opção A. O backend já tem todos os dados
consolidados e o WeasyPrint produz PDFs mais bonitos e consistentes.

### Dependência nova

```
# requirements.txt
weasyprint>=62.0
jinja2>=3.1       # provavelmente já instalado via FastAPI
```

WeasyPrint requer GTK no Linux/macOS e pode precisar de DLLs no Windows.
Para deployment em Docker, usar a imagem `ghcr.io/weasyprint/weasyprint` como base.

### Frontend

Na tela de análise do trabalho, adicionar botão ao lado dos botões existentes:

```tsx
<a
  href={`${BASE_URL}/export/${trabalhoId}/pdf`}
  download
  className="px-5 py-2.5 rounded-xl border-2 border-[#e5e1da] text-[#78716c] font-semibold hover:bg-[#f7f4ef] transition-colors"
>
  Exportar PDF
</a>
```

O link `download` dispara o download direto, sem abrir nova aba.
O botão só aparece se o dossiê já tiver sido gerado (i.e., `analise !== null`).

---

## Dependências a adicionar

| Feature | Pacote | Versão mínima | Onde |
|---|---|---|---|
| LanguageTool | `language-tool-python` | 2.8 | backend |
| Google Docs | `google-api-python-client` | 2.x | backend |
| Google Docs | `google-auth` | 2.x | backend |
| Export PDF | `weasyprint` | 62.0 | backend |
| Export PDF | `jinja2` | 3.1 | backend |

---

## Ordem de desenvolvimento sugerida

1. **LanguageTool** — menor esforço, maior impacto imediato nos desvios. Não exige UI nova.
2. **Export PDF** — muito pedido por professores, baixo risco técnico. Valor de demonstração alto.
3. **Comparação entre alunos** — requer UI mais elaborada mas usa dados já existentes no banco.
4. **Google Docs** — maior impacto do produto mas maior complexidade (OAuth, API externa). Deixar para quando as outras três estiverem estáveis.
