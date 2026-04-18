"use client";

import { useEffect, useRef, useState } from "react";

export type Fonte = "normal" | "grande" | "gigante";
export type Espacamento = "normal" | "amplo";

export interface Preferencias {
  altoContraste: boolean;
  fonte: Fonte;
  espacamento: Espacamento;
  leituraHover: boolean;
  fonteDislexia: boolean;
}

const CHAVE = "sume_acessibilidade";

// Seletores de elementos que devem ser lidos ao passar o mouse
const SELETORES_LEGIVEIS = [
  "p", "h1", "h2", "h3", "h4", "li", "span", "label",
  "button:not([aria-hidden])", "a", "[data-tour]", "th", "td",
].join(",");

function carregar(): Preferencias {
  try {
    const raw = localStorage.getItem(CHAVE);
    if (raw) return { ...padroes(), ...JSON.parse(raw) };
  } catch {}
  return padroes();
}

function padroes(): Preferencias {
  return { altoContraste: false, fonte: "normal", espacamento: "normal", leituraHover: false, fonteDislexia: false };
}

function salvar(p: Preferencias) {
  localStorage.setItem(CHAVE, JSON.stringify(p));
}

function aplicarClasses(p: Preferencias) {
  const html = document.documentElement;
  html.classList.toggle("alto-contraste", p.altoContraste);
  html.classList.remove("fonte-grande", "fonte-gigante");
  if (p.fonte === "grande") html.classList.add("fonte-grande");
  if (p.fonte === "gigante") html.classList.add("fonte-gigante");
  html.classList.toggle("espacamento-amplo", p.espacamento === "amplo");
  html.classList.toggle("fonte-dislexia", p.fonteDislexia);
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

function lerElemento(el: Element) {
  if (!("speechSynthesis" in window)) return;
  const texto =
    el.getAttribute("aria-label") ||
    el.getAttribute("alt") ||
    (el as HTMLElement).innerText ||
    el.textContent ||
    "";
  const limpo = texto.replace(/\s+/g, " ").trim().slice(0, 300);
  if (!limpo || limpo.length < 2) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(limpo);
  utterance.lang = "pt-BR";
  utterance.rate = 0.95;
  const vozes = window.speechSynthesis.getVoices();
  const voz = vozes.find((v) => v.lang.startsWith("pt"));
  if (voz) utterance.voice = voz;
  window.speechSynthesis.speak(utterance);
}

export function useAcessibilidade() {
  const [prefs, setPrefs] = useState<Preferencias>(padroes);
  const prefsRef = useRef(prefs);
  prefsRef.current = prefs;

  // Carrega preferências salvas
  useEffect(() => {
    const p = carregar();
    setPrefs(p);
    aplicarClasses(p);
  }, []);

  // Listener global de hover para TTS
  useEffect(() => {
    function onMouseEnter(e: MouseEvent) {
      if (!prefsRef.current.leituraHover) return;
      const el = (e.target as Element).closest(SELETORES_LEGIVEIS);
      if (!el) return;
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => lerElemento(el), 350);
    }

    document.addEventListener("mouseenter", onMouseEnter, true);
    return () => document.removeEventListener("mouseenter", onMouseEnter, true);
  }, []);

  function atualizar(nova: Partial<Preferencias>) {
    const p = { ...prefsRef.current, ...nova };
    setPrefs(p);
    prefsRef.current = p;
    salvar(p);
    aplicarClasses(p);
  }

  const toggleContraste   = () => atualizar({ altoContraste: !prefs.altoContraste });
  const toggleDislexia    = () => atualizar({ fonteDislexia: !prefs.fonteDislexia });
  const toggleEspacamento = () => atualizar({ espacamento: prefs.espacamento === "normal" ? "amplo" : "normal" });
  const toggleHover       = () => {
    if (prefs.leituraHover) window.speechSynthesis?.cancel();
    atualizar({ leituraHover: !prefs.leituraHover });
  };

  function aumentarFonte() {
    const ordem: Fonte[] = ["normal", "grande", "gigante"];
    const idx = ordem.indexOf(prefs.fonte);
    if (idx < ordem.length - 1) atualizar({ fonte: ordem[idx + 1] });
  }

  function diminuirFonte() {
    const ordem: Fonte[] = ["normal", "grande", "gigante"];
    const idx = ordem.indexOf(prefs.fonte);
    if (idx > 0) atualizar({ fonte: ordem[idx - 1] });
  }

  const ttsDisponivel = typeof window !== "undefined" && "speechSynthesis" in window;

  return { prefs, toggleContraste, toggleDislexia, toggleEspacamento, toggleHover, aumentarFonte, diminuirFonte, ttsDisponivel };
}
