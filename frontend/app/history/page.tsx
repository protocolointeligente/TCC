"use client";
import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";

interface HistoryItem {
  id: number;
  theme: string;
  course: string;
  review_type: string;
  created_at: string;
}

export default function HistoryPage() {
  const { user } = useUser();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    apiFetch("/history", user.id, user.primaryEmailAddress?.emailAddress)
      .then((r) => r.json())
      .then((data) => setHistory(data))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Histórico de pesquisas</h1>

        {loading && <p className="text-slate-400">Carregando...</p>}

        {!loading && history.length === 0 && (
          <p className="text-slate-400">Nenhuma pesquisa ainda. <a href="/" className="text-violet-400 hover:underline">Gerar primeira pesquisa</a>.</p>
        )}

        <div className="space-y-4">
          {history.map((item) => (
            <a
              key={item.id}
              href={`/editor/${item.id}`}
              className="block bg-slate-900 p-5 rounded-xl border border-slate-800 hover:border-slate-600 transition-colors"
            >
              <h2 className="font-bold text-xl mb-1">{item.theme}</h2>
              <p className="text-slate-400 text-sm">
                {item.course} — {item.review_type}
              </p>
              <p className="text-slate-500 text-xs mt-1">
                {new Date(item.created_at).toLocaleDateString("pt-BR", {
                  day: "2-digit",
                  month: "long",
                  year: "numeric",
                })}
              </p>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}
