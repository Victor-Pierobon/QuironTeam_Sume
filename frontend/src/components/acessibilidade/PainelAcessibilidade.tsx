"use client";

import { useState } from "react";
import { useAcessibilidade } from "./useAcessibilidade";

interface OpcaoProps {
  icone: string;
  label: string;
  ativo: boolean;
  onClick: () => void;
  disabled?: boolean;
}

function Opcao({ icone, label, ativo, onClick, disabled }: OpcaoProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-pressed={ativo}
      className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl border-2 font-semibold text-sm transition-colors text-left disabled:opacity-30 disabled:cursor-not-allowed ${
        ativo
          ? "bg-[#2d7a4f] text-white border-[#2d7a4f]"
          : "border-[#e5e1da] text-[#1c1917] hover:border-[#2d7a4f]"
      }`}
    >
      <span aria-hidden className="text-base w-5 text-center flex-shrink-0">{icone}</span>
      {label}
    </button>
  );
}

export default function PainelAcessibilidade() {
  const [aberto, setAberto] = useState(false);
  const { prefs, toggleContraste, toggleDislexia, toggleEspacamento, toggleHover, aumentarFonte, diminuirFonte, ttsDisponivel } = useAcessibilidade();

  const FONTE_LABEL: Record<string, string> = { normal: "Normal", grande: "Grande", gigante: "Extra grande" };

  return (
    <>
      {/* Skip-to-content para leitores de tela / teclado */}
      <a
        href="#conteudo-principal"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[9999] focus:bg-[#2d7a4f] focus:text-white focus:px-4 focus:py-2 focus:rounded-xl focus:font-bold"
      >
        Ir para o conteúdo principal
      </a>

      <div className="fixed bottom-6 left-6 z-40 flex flex-col items-start gap-2">
        {aberto && (
          <div
            role="dialog"
            aria-label="Painel de acessibilidade"
            className="bg-white border-2 border-[#e5e1da] rounded-2xl shadow-xl p-4 flex flex-col gap-3 w-[230px]"
          >
            <p className="text-xs font-bold text-[#78716c] uppercase tracking-wide">
              Acessibilidade
            </p>

            {/* Alto contraste */}
            <Opcao icone="◑" label="Alto contraste" ativo={prefs.altoContraste} onClick={toggleContraste} />

            {/* Fonte para dislexia */}
            <Opcao icone="𝔻" label="Fonte dislexia" ativo={prefs.fonteDislexia} onClick={toggleDislexia} />

            {/* Espaçamento */}
            <Opcao icone="↕" label="Espaçamento amplo" ativo={prefs.espacamento === "amplo"} onClick={toggleEspacamento} />

            {/* Tamanho da fonte */}
            <div>
              <p className="text-xs text-[#78716c] mb-1.5 font-medium">Tamanho do texto</p>
              <div className="flex gap-2 items-center">
                <button
                  onClick={diminuirFonte}
                  disabled={prefs.fonte === "normal"}
                  aria-label="Diminuir tamanho do texto"
                  className="w-9 h-9 rounded-xl border-2 border-[#e5e1da] font-bold text-[#1c1917] text-sm hover:border-[#2d7a4f] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  A−
                </button>
                <span className="flex-1 text-center text-xs font-semibold text-[#78716c]">
                  {FONTE_LABEL[prefs.fonte]}
                </span>
                <button
                  onClick={aumentarFonte}
                  disabled={prefs.fonte === "gigante"}
                  aria-label="Aumentar tamanho do texto"
                  className="w-9 h-9 rounded-xl border-2 border-[#e5e1da] font-bold text-[#1c1917] text-sm hover:border-[#2d7a4f] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  A+
                </button>
              </div>
            </div>

            {/* Leitura ao passar o mouse */}
            {ttsDisponivel && (
              <Opcao
                icone="🔊"
                label={prefs.leituraHover ? "Leitura: ligada" : "Ler ao passar o mouse"}
                ativo={prefs.leituraHover}
                onClick={toggleHover}
              />
            )}
            {!ttsDisponivel && (
              <p className="text-xs text-[#78716c] italic">
                Leitura em voz alta não disponível neste navegador.
              </p>
            )}

            <p className="text-xs text-[#78716c] leading-snug border-t border-[#e5e1da] pt-2 mt-1">
              Preferências salvas automaticamente.
            </p>
          </div>
        )}

        <button
          onClick={() => setAberto((v) => !v)}
          aria-label={aberto ? "Fechar painel de acessibilidade" : "Abrir painel de acessibilidade"}
          aria-expanded={aberto}
          title="Acessibilidade"
          className={`w-12 h-12 rounded-full border-2 font-bold shadow-lg transition-colors flex items-center justify-center ${
            aberto
              ? "bg-[#1c1917] text-white border-[#1c1917]"
              : "bg-white text-[#1c1917] border-[#e5e1da] hover:border-[#1c1917]"
          }`}
        >
          <span aria-hidden className="text-lg">♿</span>
        </button>
      </div>
    </>
  );
}
