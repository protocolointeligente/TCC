"use client";
import { SignedIn, SignedOut, SignInButton, useUser } from "@clerk/nextjs";
import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface ArticleCard {
  title: string;
  authors: string[];
  year: number;
  journal: string;
  doi: string;
  objective: string;
  methodology: string;
  results: string;
  conclusion: string;
  relevance: string;
}

interface ReviewResult {
  research_id: number;
  theme: string;
  articles: unknown[];
  cards: ArticleCard[];
  bibliometrics: Record<string, unknown>;
  generated_review: string;
  plan: string;
  used_this_month: number;
  monthly_limit: number;
}

const COURSES = [
  "Educação Física",
  "Nutrição",
  "Fisioterapia",
  "Enfermagem",
  "Psicologia",
  "Pedagogia",
];

const REVIEW_TYPES = [
  "Revisão Narrativa",
  "Revisão Integrativa",
  "Revisão Sistemática",
  "Artigo Original",
  "Projeto de Pesquisa",
  "TCC Completo",
];

export default function Home() {
  const { user } = useUser();

  const [theme, setTheme] = useState("");
  const [course, setCourse] = useState("Educação Física");
  const [reviewType, setReviewType] = useState("Revisão Integrativa");
  const [startYear, setStartYear] = useState(2020);
  const [endYear, setEndYear] = useState(2026);
  const [minArticles, setMinArticles] = useState(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    if (!user) return;
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await apiFetch(
        "/research",
        user.id,
        user.primaryEmailAddress?.emailAddress,
        {
          method: "POST",
          body: JSON.stringify({
            theme,
            course,
            review_type: reviewType,
            start_year: startYear,
            end_year: endYear,
            min_articles: minArticles,
            language: "pt",
            format_style: "ABNT",
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || "Erro ao gerar pesquisa.");
        return;
      }
      setResult(data);
    } catch {
      setError("Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen p-6">
      <SignedOut>
        <div className="max-w-xl mx-auto bg-slate-900 p-8 rounded-2xl text-center mt-20">
          <h1 className="text-3xl font-bold mb-4">Academia IA</h1>
          <p className="text-slate-300 mb-6">
            Entre para gerar TCCs, revisões bibliográficas e fichas científicas.
          </p>
          <SignInButton>
            <button className="bg-violet-600 hover:bg-violet-700 px-6 py-3 rounded-xl font-bold">
              Entrar
            </button>
          </SignInButton>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="max-w-5xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">Pesquisa acadêmica</h1>
          <p className="text-slate-400 mb-8">
            Busca em OpenAlex, PubMed, Crossref e Semantic Scholar.
          </p>

          <section className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-8">
            <label className="block mb-2 font-medium">Tema da pesquisa</label>
            <input
              className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 mb-4 focus:outline-none focus:border-violet-500"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Ex: ansiedade pré-competitiva em atletas"
            />

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block mb-1 text-sm text-slate-400">Curso</label>
                <select
                  className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                  value={course}
                  onChange={(e) => setCourse(e.target.value)}
                >
                  {COURSES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>

              <div>
                <label className="block mb-1 text-sm text-slate-400">Tipo de revisão</label>
                <select
                  className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                  value={reviewType}
                  onChange={(e) => setReviewType(e.target.value)}
                >
                  {REVIEW_TYPES.map((r) => <option key={r}>{r}</option>)}
                </select>
              </div>

              <div>
                <label className="block mb-1 text-sm text-slate-400">Ano inicial</label>
                <input
                  type="number"
                  className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                  value={startYear}
                  onChange={(e) => setStartYear(Number(e.target.value))}
                />
              </div>

              <div>
                <label className="block mb-1 text-sm text-slate-400">Ano final</label>
                <input
                  type="number"
                  className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                  value={endYear}
                  onChange={(e) => setEndYear(Number(e.target.value))}
                />
              </div>

              <div>
                <label className="block mb-1 text-sm text-slate-400">Número de artigos</label>
                <input
                  type="number"
                  min={1}
                  max={50}
                  className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                  value={minArticles}
                  onChange={(e) => setMinArticles(Number(e.target.value))}
                />
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !theme.trim()}
              className="mt-6 w-full bg-violet-600 hover:bg-violet-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-xl p-4 font-bold transition-colors"
            >
              {loading ? "Pesquisando e gerando revisão..." : "Gerar pesquisa acadêmica"}
            </button>
          </section>

          {error && (
            <div className="bg-red-900/40 border border-red-700 rounded-2xl p-4 mb-8 text-red-300">
              {error}
            </div>
          )}

          {result && (
            <section className="space-y-8">
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Plano</p>
                  <p className="font-bold capitalize">{result.plan}</p>
                </div>
                <div className="text-right">
                  <p className="text-slate-400 text-sm">Uso mensal</p>
                  <p className="font-bold">
                    {result.used_this_month}/{result.monthly_limit}
                  </p>
                </div>
                <a href="/pricing" className="text-violet-400 text-sm hover:underline">
                  Fazer upgrade
                </a>
              </div>

              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold">Revisão gerada</h2>
                  <div className="flex gap-2">
                    <a
                      href={`${process.env.NEXT_PUBLIC_API_URL}/research/${result.research_id}/export-docx`}
                      target="_blank"
                      className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-xl text-sm font-medium"
                    >
                      Exportar DOCX
                    </a>
                    <a
                      href={`/editor/${result.research_id}`}
                      className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-xl text-sm font-medium"
                    >
                      Editar
                    </a>
                  </div>
                </div>
                <div className="whitespace-pre-wrap leading-8 text-slate-100 text-sm">
                  {result.generated_review}
                </div>
              </div>

              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                <h2 className="text-2xl font-bold mb-4">
                  Fichas dos artigos ({result.cards.length})
                </h2>
                {result.cards.map((card, i) => (
                  <div key={i} className="mb-5 p-5 rounded-xl bg-slate-950 border border-slate-800">
                    <h3 className="font-bold text-lg mb-1">{card.title}</h3>
                    <p className="text-slate-400 text-sm mb-3">
                      {card.authors?.join(", ")} — {card.year}
                      {card.journal && ` — ${card.journal}`}
                    </p>
                    <div className="space-y-1 text-sm">
                      <p><span className="text-violet-300 font-semibold">Objetivo:</span> {card.objective}</p>
                      <p><span className="text-violet-300 font-semibold">Metodologia:</span> {card.methodology}</p>
                      <p><span className="text-violet-300 font-semibold">Resultados:</span> {card.results}</p>
                      <p><span className="text-violet-300 font-semibold">Conclusão:</span> {card.conclusion}</p>
                      <p><span className="text-violet-300 font-semibold">Relevância:</span> {card.relevance}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                <h2 className="text-2xl font-bold mb-4">Bibliometria</h2>
                <pre className="bg-slate-950 p-4 rounded-xl overflow-auto text-sm text-slate-300">
                  {JSON.stringify(result.bibliometrics, null, 2)}
                </pre>
              </div>
            </section>
          )}
        </div>
      </SignedIn>
    </main>
  );
}
