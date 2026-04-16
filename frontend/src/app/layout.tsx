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
      <body className="min-h-full flex flex-col bg-[#f5f0e8] text-[#2c2416]">
        <header className="border-b border-[#e8e0d0] px-8 py-4 flex items-center gap-3">
          <span className="text-2xl font-bold tracking-tight" style={{ fontFamily: "Georgia, serif" }}>
            Sumé
          </span>
          <span className="text-sm text-[#6b5c40]">copiloto pedagógico</span>
        </header>
        <main className="flex-1 px-8 py-6">{children}</main>
      </body>
    </html>
  );
}
