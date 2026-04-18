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
    title: "Página da turma",
    content:
      "Aqui você vê todos os alunos desta turma. Cada cartão mostra o nome e a situação atual do aluno.",
  },
  {
    target: "[data-tour='contadores-turma']",
    placement: "bottom",
    disableBeacon: true,
    title: "Resumo da turma",
    content:
      "Estes números mostram, de forma rápida, quantos alunos estão em cada situação.",
  },
  {
    target: "[data-tour='badge-status']",
    placement: "left",
    disableBeacon: true,
    title: "O que significa cada cor?",
    content:
      "Verde = tudo normal.\nAmarelo = vale uma olhada extra.\nVermelho = conversar com o aluno é recomendado.\n\nNenhuma cor significa acusação — são apenas sinais de alerta.",
  },
  {
    target: "[data-tour='card-aluno']",
    placement: "bottom",
    disableBeacon: true,
    title: "Ver o aluno",
    content:
      "Clique em qualquer cartão para ver os trabalhos daquele aluno e a análise detalhada.",
  },
];

export default function TourTurma() {
  const { rodando, iniciar, terminar } = useTour("turma");
  return (
    <>
      <SumeTour steps={STEPS} rodando={rodando} onTerminar={terminar} />
      <BotaoAjuda onIniciar={iniciar} />
    </>
  );
}
