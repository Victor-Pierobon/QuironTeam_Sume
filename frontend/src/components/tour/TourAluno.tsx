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
    title: "Perfil do aluno",
    content:
      "Esta página mostra todos os trabalhos de um aluno e como a escrita dele evoluiu ao longo do tempo.",
  },
  {
    target: "[data-tour='baseline-section']",
    placement: "bottom",
    disableBeacon: true,
    title: "Linha de base",
    content:
      "São os textos usados como referência para o estilo do aluno — geralmente redações feitas em sala. Quanto mais, melhor a análise.",
  },
  {
    target: "[data-tour='baseline-aviso']",
    placement: "bottom",
    disableBeacon: true,
    title: "Mínimo recomendado",
    content:
      "Para que a análise seja confiável, adicione pelo menos 3 textos de linha de base. O sistema avisará se houver menos.",
  },
  {
    target: "[data-tour='botao-upload']",
    placement: "bottom",
    disableBeacon: true,
    title: "Enviar um trabalho",
    content:
      "Clique aqui para adicionar um novo trabalho. Você pode enviar um arquivo Word ou PDF, tirar uma foto do papel, ou colar um link do Google Docs.",
  },
  {
    target: "[data-tour='trajetoria-chart']",
    placement: "top",
    disableBeacon: true,
    title: "Gráfico de evolução",
    content:
      "Este gráfico mostra como o estilo de escrita do aluno mudou de um trabalho para o outro. Clique em \"Métricas detalhadas\" para ver indicadores individuais.",
  },
];

export default function TourAluno() {
  const { rodando, iniciar, terminar } = useTour("aluno");
  return (
    <>
      <SumeTour steps={STEPS} rodando={rodando} onTerminar={terminar} />
      <BotaoAjuda onIniciar={iniciar} />
    </>
  );
}
