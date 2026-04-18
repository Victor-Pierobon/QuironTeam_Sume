"use client";

import { useState, useEffect } from "react";
import { desativarTutorial, reativarTutorial, tutorialDesativado } from "./useTour";

interface Props {
  onIniciar: () => void;
}

export default function BotaoAjuda({ onIniciar }: Props) {
  const [desativado, setDesativado] = useState(false);

  useEffect(() => {
    setDesativado(tutorialDesativado());
  }, []);

  function handleDesativar() {
    desativarTutorial();
    setDesativado(true);
  }

  function handleReativar() {
    reativarTutorial();
    setDesativado(false);
  }

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2">
      {!desativado && (
        <button
          onClick={handleDesativar}
          className="text-xs text-[#78716c] bg-white border border-[#e5e1da] rounded-full px-3 py-1 shadow hover:bg-[#fef2f2] hover:text-[#dc2626] hover:border-[#dc2626] transition-colors"
        >
          Desativar tutorial
        </button>
      )}
      {desativado && (
        <button
          onClick={handleReativar}
          className="text-xs text-[#78716c] bg-white border border-[#e5e1da] rounded-full px-3 py-1 shadow hover:bg-[#edf7f1] hover:text-[#2d7a4f] hover:border-[#2d7a4f] transition-colors"
        >
          Reativar tutorial
        </button>
      )}
      <button
        onClick={onIniciar}
        title="Ver tutorial desta página"
        className="w-12 h-12 rounded-full bg-[#2d7a4f] text-white text-xl font-bold shadow-lg hover:bg-[#25673e] transition-colors flex items-center justify-center"
      >
        ?
      </button>
    </div>
  );
}
