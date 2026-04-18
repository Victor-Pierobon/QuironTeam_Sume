"use client";

import { useState, useEffect } from "react";

export type TourPage = "dashboard" | "turma" | "aluno" | "trabalho";

const CHAVE = (page: TourPage) => `sume_tour_${page}`;
const CHAVE_DESATIVADO = "sume_tour_desativado";

export function tutorialDesativado(): boolean {
  return localStorage.getItem(CHAVE_DESATIVADO) === "true";
}

export function desativarTutorial() {
  localStorage.setItem(CHAVE_DESATIVADO, "true");
}

export function reativarTutorial() {
  localStorage.removeItem(CHAVE_DESATIVADO);
  (["dashboard", "turma", "aluno", "trabalho"] as TourPage[]).forEach((p) =>
    localStorage.removeItem(CHAVE(p))
  );
}

export function useTour(page: TourPage) {
  const [rodando, setRodando] = useState(false);

  useEffect(() => {
    if (tutorialDesativado()) return;
    const visto = localStorage.getItem(CHAVE(page));
    if (!visto) {
      const t = setTimeout(() => setRodando(true), 600);
      return () => clearTimeout(t);
    }
  }, [page]);

  function iniciar() {
    setRodando(true);
  }

  function terminar() {
    setRodando(false);
    localStorage.setItem(CHAVE(page), "true");
  }

  return { rodando, iniciar, terminar };
}
