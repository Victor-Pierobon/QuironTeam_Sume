"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

const TIPOS = ["redação", "relatório", "resenha", "artigo", "resumo", "outro"];
const ACCEPT = ".docx,.pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf";

type Aba = "arquivo" | "gdocs";

interface Props {
  alunoId: number;
}

export default function UploadTrabalhoButton({ alunoId }: Props) {
  const [aberto, setAberto] = useState(false);
  const [aba, setAba] = useState<Aba>("arquivo");
  const [titulo, setTitulo] = useState("");
  const [tipo, setTipo] = useState("redação");
  const [baseline, setBaseline] = useState(false);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [docUrl, setDocUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  function resetForm() {
    setTitulo("");
    setTipo("redação");
    setBaseline(false);
    setArquivo(null);
    setDocUrl("");
    setErro(null);
    if (fileRef.current) fileRef.current.value = "";
  }

  function handleFechar() {
    setAberto(false);
    resetForm();
  }

  function handleArquivo(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setArquivo(file);
    if (file && !titulo.trim()) {
      const nome = file.name.replace(/\.(docx|pdf)$/i, "").replace(/[-_]/g, " ");
      setTitulo(nome);
    }
  }

  async function handleEnviarArquivo(e: React.FormEvent) {
    e.preventDefault();
    if (!arquivo) { setErro("Selecione um arquivo."); return; }
    if (!titulo.trim()) { setErro("Informe o título do trabalho."); return; }

    const ext = arquivo.name.split(".").pop()?.toLowerCase();
    if (ext !== "docx" && ext !== "pdf") {
      setErro("Formato não suportado. Use .docx ou .pdf.");
      return;
    }

    setLoading(true);
    setErro(null);

    const form = new FormData();
    form.append("aluno_id", String(alunoId));
    form.append("titulo", titulo.trim());
    form.append("tipo", tipo);
    form.append("baseline", String(baseline));
    form.append("arquivo", arquivo);

    try {
      const res = await fetch(`${BASE_URL}/trabalhos/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      handleFechar();
      router.refresh();
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao enviar trabalho.");
    } finally {
      setLoading(false);
    }
  }

  async function handleEnviarGDocs(e: React.FormEvent) {
    e.preventDefault();
    if (!docUrl.trim()) { setErro("Cole o link do Google Docs."); return; }
    if (!titulo.trim()) { setErro("Informe o título do trabalho."); return; }

    setLoading(true);
    setErro(null);

    try {
      const res = await fetch(`${BASE_URL}/trabalhos/upload-gdocs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          aluno_id: alunoId,
          titulo: titulo.trim(),
          tipo,
          baseline,
          doc_url: docUrl.trim(),
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      handleFechar();
      router.refresh();
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Erro ao importar do Google Docs.");
    } finally {
      setLoading(false);
    }
  }

  const podeSalvar = aba === "arquivo" ? !!arquivo && !!titulo.trim() : !!docUrl.trim() && !!titulo.trim();

  return (
    <>
      <button
        onClick={() => setAberto(true)}
        className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2d7a4f] text-white font-semibold hover:bg-[#25673e] transition-colors"
      >
        <span className="text-lg leading-none">+</span>
        Enviar trabalho
      </button>

      {aberto && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={handleFechar}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-7" onClick={(e) => e.stopPropagation()}>

            <div className="flex items-center justify-between mb-5">
              <h2 className="text-2xl font-bold" style={{ fontFamily: "Georgia, serif" }}>
                Enviar trabalho
              </h2>
              <button
                onClick={handleFechar}
                className="text-[#78716c] hover:text-[#1c1917] text-xl font-bold w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#f7f4ef] transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Abas */}
            <div className="flex gap-1 mb-6 bg-[#f7f4ef] rounded-xl p-1">
              {(["arquivo", "gdocs"] as Aba[]).map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() => { setAba(a); setErro(null); }}
                  className={`flex-1 py-2 rounded-lg font-semibold text-sm transition-colors ${
                    aba === a
                      ? "bg-white text-[#1c1917] shadow-sm"
                      : "text-[#78716c] hover:text-[#1c1917]"
                  }`}
                >
                  {a === "arquivo" ? "📄 Arquivo (.docx / .pdf)" : "🔗 Google Docs"}
                </button>
              ))}
            </div>

            <form onSubmit={aba === "arquivo" ? handleEnviarArquivo : handleEnviarGDocs} className="space-y-5">

              {/* Conteúdo da aba */}
              {aba === "arquivo" ? (
                <div>
                  <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-2">Arquivo</label>
                  <div
                    className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-colors ${
                      arquivo ? "border-[#2d7a4f] bg-[#edf7f1]" : "border-[#e5e1da] hover:border-[#2d7a4f] hover:bg-[#f7f4ef]"
                    }`}
                    onClick={() => fileRef.current?.click()}
                  >
                    {arquivo ? (
                      <div className="flex items-center justify-center gap-3">
                        <span className="text-2xl">{arquivo.name.toLowerCase().endsWith(".pdf") ? "📄" : "📝"}</span>
                        <div className="text-left">
                          <p className="font-semibold text-[#1c1917]">{arquivo.name}</p>
                          <p className="text-sm text-[#78716c]">
                            {(arquivo.size / 1024).toFixed(0)} KB · {arquivo.name.split(".").pop()?.toUpperCase()}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setArquivo(null); if (fileRef.current) fileRef.current.value = ""; }}
                          className="ml-auto text-[#78716c] hover:text-[#dc2626] font-bold text-lg"
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div>
                        <p className="text-4xl mb-2">📂</p>
                        <p className="font-semibold text-[#1c1917]">Clique para selecionar</p>
                        <p className="text-sm text-[#78716c] mt-1">Aceita .docx e .pdf</p>
                      </div>
                    )}
                  </div>
                  <input ref={fileRef} type="file" accept={ACCEPT} onChange={handleArquivo} className="hidden" />
                </div>
              ) : (
                <div>
                  <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-2">Link do Google Docs</label>
                  <input
                    type="url"
                    value={docUrl}
                    onChange={(e) => setDocUrl(e.target.value)}
                    placeholder="https://docs.google.com/document/d/..."
                    className="w-full border-2 border-[#e5e1da] rounded-xl px-4 py-3 text-[#1c1917] focus:outline-none focus:border-[#2d7a4f] transition-colors"
                  />
                  <p className="text-sm text-[#78716c] mt-2">
                    Compartilhe o documento com a service account da aplicação.
                    O sistema importará o texto completo e o histórico de edições automaticamente.
                  </p>
                </div>
              )}

              {/* Título */}
              <div>
                <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-2">Título</label>
                <input
                  type="text"
                  value={titulo}
                  onChange={(e) => setTitulo(e.target.value)}
                  placeholder="Ex: Redação sobre o Cerrado"
                  className="w-full border-2 border-[#e5e1da] rounded-xl px-4 py-3 text-[#1c1917] focus:outline-none focus:border-[#2d7a4f] transition-colors"
                />
              </div>

              {/* Tipo */}
              <div>
                <label className="font-bold text-[#78716c] uppercase tracking-wide block mb-2">Tipo de texto</label>
                <div className="flex flex-wrap gap-2">
                  {TIPOS.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setTipo(t)}
                      className={`px-4 py-2 rounded-xl border-2 font-semibold transition-colors capitalize ${
                        tipo === t
                          ? "bg-[#2d7a4f] border-[#2d7a4f] text-white"
                          : "border-[#e5e1da] text-[#78716c] hover:border-[#2d7a4f]"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Baseline */}
              <label className="flex items-start gap-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={baseline}
                  onChange={(e) => setBaseline(e.target.checked)}
                  className="mt-1 w-5 h-5 accent-[#2d7a4f] flex-shrink-0"
                />
                <div>
                  <span className="font-semibold text-[#1c1917]">Marcar como baseline confiável</span>
                  <p className="text-sm text-[#78716c] mt-0.5">
                    Use para textos produzidos em sala ou sob supervisão direta.
                    O perfil do aluno será atualizado automaticamente.
                  </p>
                </div>
              </label>

              {erro && (
                <p className="text-sm text-[#dc2626] font-medium bg-[#fef2f2] border border-[#dc2626] rounded-lg px-4 py-2">
                  {erro}
                </p>
              )}

              <div className="flex gap-3 pt-1">
                <button
                  type="submit"
                  disabled={loading || !podeSalvar}
                  className="flex-1 py-3 rounded-xl bg-[#2d7a4f] text-white font-bold hover:bg-[#25673e] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading
                    ? (aba === "gdocs" ? "Importando do Google Docs…" : "Enviando…")
                    : (aba === "gdocs" ? "Importar e analisar" : "Enviar")}
                </button>
                <button
                  type="button"
                  onClick={handleFechar}
                  className="px-5 py-3 rounded-xl border-2 border-[#e5e1da] text-[#78716c] font-semibold hover:bg-[#f7f4ef] transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
