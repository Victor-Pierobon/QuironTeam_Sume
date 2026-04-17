import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sumé",
  description: "Copiloto crítico para professores analisarem produção escrita de alunos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full">
      <body className="min-h-full flex flex-col bg-[#f7f4ef] text-[#1c1917]">
        <header className="bg-[#1e4d2b] px-8 py-4 flex items-center gap-4 shadow-md">
          <span className="text-3xl font-bold tracking-tight text-white" style={{ fontFamily: "Georgia, serif" }}>
            Sumé
          </span>
          <span className="text-sm text-[#a7d4b8] font-medium">copiloto pedagógico</span>
        </header>
        <main className="flex-1 px-8 py-8">{children}</main>
      </body>
    </html>
  );
}
