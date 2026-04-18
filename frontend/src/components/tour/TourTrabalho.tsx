"use client";

import { Step } from "react-joyride";
import dynamic from "next/dynamic";
const SumeTour = dynamic(() => import("./SumeTour"), { ssr: false });
import BotaoAjuda from "./BotaoAjuda";
import { useTour } from "./useTour";

const STEPS: Step[] = [
  {
    target: "body",
    placement: "center",
    disableBeacon: true,
    title: "Análise do trabalho",
    content:
      "Aqui você analisa um trabalho específico e vê tudo o que o sistema identificou. Vamos percorrer cada parte.",
  },
  {
    target: "[data-tour='btn-analisar']",
    placement: "bottom",
    disableBeacon: true,
    title: "1. Analisar o trabalho",
    content:
      "Sempre comece por aqui. O sistema vai comparar este texto com os trabalhos anteriores do aluno e identificar o que mudou.",
  },
  {
    target: "[data-tour='donut-chart']",
    placement: "left",
    disableBeacon: true,
    title: "2. Visão geral",
    content:
      "Esta pizza mostra, em um relance, quantas métricas estão normais (verde), merecem atenção (amarelo) ou sugerem uma conversa (vermelho).",
  },
  {
    target: "[data-tour='evidencias-panel']",
    placement: "top",
    disableBeacon: true,
    title: "3. Evidências detalhadas",
    content:
      "Use os botões Conversar, Atenção e Normais para filtrar quais métricas quer ver. Por padrão, só as mais importantes aparecem.",
  },
  {
    target: "[data-tour='btn-validar-fontes']",
    placement: "bottom",
    disableBeacon: true,
    title: "4. Verificar as fontes",
    content:
      "Clique para verificar automaticamente se os livros, sites e artigos citados no texto existem e são confiáveis.",
  },
  {
    target: "[data-tour='btn-roteiro']",
    placement: "bottom",
    disableBeacon: true,
    title: "5. Gerar roteiro de conversa",
    content:
      "O sistema prepara um roteiro com perguntas para você fazer ao aluno em uma conversa — sem acusações, apenas para entender melhor o trabalho.",
  },
  {
    target: "[data-tour='btn-desfecho']",
    placement: "bottom",
    disableBeacon: true,
    title: "6. Registrar o desfecho",
    content:
      "Após conversar com o aluno, use este botão para registrar o que aconteceu. Isso fica salvo no histórico do trabalho.",
  },
  {
    target: "[data-tour='texto-completo']",
    placement: "top",
    disableBeacon: true,
    title: "7. Texto do trabalho",
    content:
      "O texto completo fica aqui. Parágrafos com fundo amarelo foram identificados como diferentes do restante do texto.",
  },
];

export default function TourTrabalho() {
  const { rodando, iniciar, terminar } = useTour("trabalho");
  return (
    <>
      <SumeTour steps={STEPS} rodando={rodando} onTerminar={terminar} />
      <BotaoAjuda onIniciar={iniciar} />
    </>
  );
}
