# Sumé — Plano de Tutorial Interativo

**Público-alvo:** Professores com baixo letramento digital, possivelmente acima de 40 anos, pouco habituados a softwares de análise.

**Princípio central:** O tutorial deve ensinar O QUE FAZER, não o que as coisas são. Frases de ação simples, sem jargão técnico.

---

## Biblioteca escolhida: `react-joyride`

**Por quê:**
- Funciona nativamente com React/Next.js (client components)
- Highlight automático do elemento alvo com overlay escuro
- Suporte a TypeScript e customização visual total
- Bem mantida, zero dependências extras

**Instalação:** `npm install react-joyride`

---

## Estratégia de persistência

Sem login, o controle de "já viu o tutorial" será feito via **localStorage**:

```
sume_tour_dashboard     → true/false
sume_tour_turma         → true/false
sume_tour_aluno         → true/false
sume_tour_trabalho      → true/false
```

- Na primeira visita a cada página: tour inicia automaticamente
- Botão **"?"** fixo no canto inferior direito reinicia o tour da página atual
- Opção "Pular tutorial" sempre visível

---

## Tours por página

### Tour 1 — Dashboard (3 passos)

| Passo | Alvo | Mensagem |
|---|---|---|
| 1 | Card de turma | "Esta é uma das suas turmas. Clique nela para ver os alunos." |
| 2 | Contador de alunos | "Aqui você vê quantos alunos estão na turma e quantos precisam de atenção." |
| 3 | — | "Sempre que quiser voltar ao início, clique em **Sumé** no topo da página." |

---

### Tour 2 — Página da turma (4 passos)

| Passo | Alvo | Mensagem |
|---|---|---|
| 1 | Card de aluno | "Cada cartão representa um aluno. A cor indica se há algo para verificar." |
| 2 | Badge verde "Normal" | "Verde significa que os trabalhos do aluno estão dentro do esperado." |
| 3 | Badge amarelo "Atenção" | "Amarelo indica que vale uma olhada mais cuidadosa nos trabalhos recentes." |
| 4 | Badge vermelho "Conversar" | "Vermelho sugere uma conversa com o aluno — não é acusação, é um sinal de alerta." |

---

### Tour 3 — Perfil do aluno (4 passos)

| Passo | Alvo | Mensagem |
|---|---|---|
| 1 | Seção "Linha de base" | "Estes são os textos usados como referência do estilo deste aluno." |
| 2 | Aviso de baseline < 3 | "Para uma análise confiável, adicione pelo menos 3 textos de linha de base." |
| 3 | Botão "Enviar trabalho" | "Aqui você envia um trabalho novo. Pode ser um arquivo, uma foto ou um link do Google Docs." |
| 4 | Gráfico de trajetória | "Este gráfico mostra como a escrita do aluno evoluiu ao longo do tempo." |

---

### Tour 4 — Análise do trabalho (6 passos)

| Passo | Alvo | Mensagem |
|---|---|---|
| 1 | Botão "Analisar trabalho" | "Clique aqui primeiro. O sistema irá comparar este texto com o perfil do aluno." |
| 2 | Gráfico de pizza | "Esta pizza mostra quantas métricas estão normais, em atenção ou merecem conversa." |
| 3 | Painel de evidências (toggle) | "Estes botões filtram o que você quer ver. Por padrão mostra só o que merece atenção." |
| 4 | Botão "Validar fontes" | "Clique para verificar automaticamente se as fontes citadas existem e são confiáveis." |
| 5 | Botão "Gerar roteiro" | "Este botão cria um roteiro de conversa pedagógica para você usar com o aluno." |
| 6 | Botão "Registrar desfecho" | "Após conversar com o aluno, registre aqui o que aconteceu para manter o histórico." |

---

## Componentes a criar

```
frontend/src/components/tour/
  TourDashboard.tsx      → steps do dashboard
  TourTurma.tsx          → steps da turma
  TourAluno.tsx          → steps do aluno
  TourTrabalho.tsx       → steps do trabalho
  BotaoAjuda.tsx         → botão "?" fixo que reinicia o tour
  useTour.ts             → hook: lê/escreve localStorage, controla estado
```

---

## Estilo visual

- Overlay: `bg-black/50`
- Tooltip: fundo `#f5f0e8` (papel), borda `#2d7a4f`, fonte Georgia
- Botão "Próximo": `bg-[#2d7a4f] text-white`
- Botão "Pular": `text-[#78716c]` underline
- Botão anterior: `border-[#e5e1da]`
- Posição preferida: `bottom` (não tampa o elemento)

---

## Linguagem — regras para os textos

1. Frases curtas (máx. 2 linhas)
2. Verbo no imperativo: "Clique", "Veja", "Use"
3. Sem siglas ou termos técnicos (z-score, baseline → "linha de base")
4. Sempre dizer O QUE vai acontecer depois de clicar
5. Nunca usar a palavra "algoritmo", "IA", "machine learning"

---

## Ordem de implementação

- [ ] Instalar `react-joyride`
- [ ] Criar `useTour.ts` com lógica de localStorage
- [ ] Criar `BotaoAjuda.tsx` (botão "?" fixo)
- [ ] `TourTrabalho.tsx` (mais rico, mais importante para o demo)
- [ ] `TourAluno.tsx`
- [ ] `TourTurma.tsx`
- [ ] `TourDashboard.tsx`
- [ ] Integrar em cada página
