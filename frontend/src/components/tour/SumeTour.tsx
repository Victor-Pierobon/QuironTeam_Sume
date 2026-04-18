"use client";

// react-joyride não tem default export no ESM; usar named export via require
// eslint-disable-next-line @typescript-eslint/no-require-imports
const { Joyride, STATUS } = require("react-joyride") as typeof import("react-joyride");
import type { CallBackProps, Step, Styles } from "react-joyride";

const estilos: Partial<Styles> = {
  options: {
    backgroundColor: "#f5f0e8",
    primaryColor: "#2d7a4f",
    textColor: "#1c1917",
    overlayColor: "rgba(0,0,0,0.55)",
    zIndex: 9999,
    arrowColor: "#f5f0e8",
  },
  tooltip: {
    borderRadius: 16,
    padding: "20px 24px",
    fontFamily: "Georgia, serif",
    fontSize: 15,
    maxWidth: 340,
    boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
  },
  tooltipTitle: {
    fontFamily: "Georgia, serif",
    fontSize: 17,
    fontWeight: "bold",
    marginBottom: 8,
    color: "#1c1917",
  },
  tooltipContent: {
    lineHeight: 1.6,
    padding: "4px 0",
  },
  buttonNext: {
    backgroundColor: "#2d7a4f",
    borderRadius: 10,
    padding: "8px 20px",
    fontWeight: "bold",
    fontSize: 14,
  },
  buttonBack: {
    color: "#78716c",
    marginRight: 8,
    fontSize: 14,
  },
  buttonSkip: {
    color: "#78716c",
    fontSize: 13,
    textDecoration: "underline",
  },
};

const locale = {
  back: "Voltar",
  close: "Fechar",
  last: "Concluir",
  next: "Próximo →",
  skip: "Pular tutorial",
};

interface Props {
  steps: Step[];
  rodando: boolean;
  onTerminar: () => void;
}

export default function SumeTour({ steps, rodando, onTerminar }: Props) {
  function handleCallback(data: CallBackProps) {
    const { status, type } = data;
    const encerrado = ([STATUS.FINISHED, STATUS.SKIPPED] as string[]).includes(status);
    if (encerrado) onTerminar();
  }

  return (
    <Joyride
      steps={steps}
      run={rodando}
      continuous
      showSkipButton
      showProgress
      scrollToFirstStep
      disableScrollParentFix
      locale={locale}
      styles={estilos}
      callback={handleCallback}
    />
  );
}
