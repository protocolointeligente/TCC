"use client";
import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Research {
  id: number;
  theme: string;
  course: string;
  review_type: string;
  generated_review: string;
  articles: unknown[];
}

export default function EditorPage() {
  const { user } = useUser();
  const params = useParams();
  const id = params.id as string;

  const [research, setResearch] = useState<Research | null>(null);
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState<unknown[] | null>(null);

  useEffect(() => {
    if (!user) return;
    apiFetch(`/research/${id}`, user.id, user.primaryEmailAddress?.emailAddress)
      .then((r) => r.json())
      .then((data) => {
        setResearch(data);
        setText(data.generated_review ?? "");
      });
  }, [user, id]);

  async function saveText() {
    if (!user) return;
    setSaving(true);
    await apiFetch(
      `/research/${id}/text`,
      user.id,
      user.primaryEmailAddress?.emailAddress,
      {
        method: "PUT",
        body: JSON.stringify({ generated_review: text }),
      }
    );
    setSaving(false);
  }

  async function checkReferences() {
    if (!user) return;
    setChecking(true);
    const response = await apiFetch(
      `/research/${id}/check-references`,
      user.id,
      user.primaryEmailAddress?.emailAddress,
      { method: "POST" }
    );
    const data = await response.json();
    setCheckResult(data);
    setChecking(false);
  }

  if (!research) {
    return (
      <main className="min-h-screen p-6">
        <p className="text-slate-400">Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-4">
          <h1 className="text-3xl font-bold">{research.theme}</h1>
          <p className="text-slate-400 text-sm mt-1">
            {research.course} — {research.review_type}
          </p>
        </div>

        <div className="flex flex-wrap gap-3 mb-4">
          <button
            onClick={saveText}
            disabled={saving}
            className="bg-violet-600 hover:bg-violet-700 disabled:bg-slate-700 px-4 py-2 rounded-xl text-sm font-medium"
          >
            {saving ? "Salvando..." : "Salvar alterações"}
          </button>

          <a
            href={`${process.env.NEXT_PUBLIC_API_URL}/research/${id}/export-docx`}
            target="_blank"
            className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-xl text-sm font-medium"
          >
            Exportar DOCX
          </a>

          <button
            onClick={checkReferences}
            disabled={checking}
            className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-slate-700 px-4 py-2 rounded-xl text-sm font-medium"
          >
            {checking ? "Verificando..." : "Verificar referências"}
          </button>

          <a href="/history" className="text-slate-400 hover:text-white px-4 py-2 text-sm">
            ← Histórico
          </a>
        </div>

        <textarea
          className="w-full h-[72vh] bg-slate-900 border border-slate-800 rounded-xl p-5 leading-8 text-sm focus:outline-none focus:border-violet-500 resize-none"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        {checkResult && (
          <div className="mt-6 bg-slate-900 rounded-2xl p-6 border border-slate-800">
            <h2 className="text-xl font-bold mb-4">Resultado da verificação</h2>
            <div className="space-y-3">
              {(checkResult as Array<{ title: string; doi: string; verification: { valid: boolean; reason?: string; title?: string } }>).map((item, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-xl border text-sm ${
                    item.verification.valid
                      ? "border-green-700 bg-green-900/20"
                      : "border-red-700 bg-red-900/20"
                  }`}
                >
                  <p className="font-semibold">{item.title}</p>
                  <p className="text-slate-400 text-xs mt-1">DOI: {item.doi || "Sem DOI"}</p>
                  <p className="mt-1">
                    {item.verification.valid ? (
                      <span className="text-green-400">Verificado no Crossref</span>
                    ) : (
                      <span className="text-red-400">{item.verification.reason}</span>
                    )}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
