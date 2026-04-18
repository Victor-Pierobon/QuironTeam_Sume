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
    title: "Bem-vindo ao Sumé!",
    content:
      "Este é o seu painel de turmas. Vamos fazer um tour rápido para você conhecer o sistema.",
  },
  {
    target: "[data-tour='card-turma']",
    placement: "bottom",
    disableBeacon: true,
    title: "Suas turmas",
    content:
      "Cada cartão representa uma turma. Clique em uma turma para ver os alunos e os trabalhos deles.",
  },
  {
    target: "[data-tour='card-turma']",
    placement: "bottom",
    disableBeacon: true,
    title: "Alunos em atenção",
    content:
      "O número em vermelho mostra quantos alunos têm trabalhos que merecem uma conversa. O amarelo indica atenção moderada.",
  },
  {
    target: "header",
    placement: "bottom",
    disableBeacon: true,
    title: "Navegação",
    content:
      "Clique em \"Sumé\" no topo a qualquer momento para voltar a esta tela inicial.",
  },
];

export default function TourDashboard() {
  const { rodando, iniciar, terminar } = useTour("dashboard");
  return (
    <>
      <SumeTour steps={STEPS} rodando={rodando} onTerminar={terminar} />
      <BotaoAjuda onIniciar={iniciar} />
    </>
  );
}
