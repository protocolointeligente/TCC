"use client";
import { useState } from "react";

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
  theme: string;
  articles: unknown[];
  cards: ArticleCard[];
  bibliometrics: Record<string, unknown>;
  generated_review: string;
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
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
      });
      if (!response.ok) throw new Error(`Erro ${response.status}: ${response.statusText}`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-5xl mx-auto">
        <section className="mb-10">
          <h1 className="text-4xl font-bold mb-3">Academia IA</h1>
          <p className="text-slate-300">
            Ferramenta para TCC, revisão bibliográfica e pesquisa científica em português.
          </p>
        </section>

        <section className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-8">
          <label className="block mb-2 font-medium">Tema da pesquisa</label>
          <input
            className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 mb-4 focus:outline-none focus:border-violet-500"
            placeholder="Ex: ansiedade pré-competitiva em atletas"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          />

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 font-medium">Curso</label>
              <select
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-violet-500"
                value={course}
                onChange={(e) => setCourse(e.target.value)}
              >
                {COURSES.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block mb-2 font-medium">Tipo de revisão</label>
              <select
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-violet-500"
                value={reviewType}
                onChange={(e) => setReviewType(e.target.value)}
              >
                {REVIEW_TYPES.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block mb-2 font-medium">Ano inicial</label>
              <input
                type="number"
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-violet-500"
                value={startYear}
                onChange={(e) => setStartYear(Number(e.target.value))}
              />
            </div>

            <div>
              <label className="block mb-2 font-medium">Ano final</label>
              <input
                type="number"
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-violet-500"
                value={endYear}
                onChange={(e) => setEndYear(Number(e.target.value))}
              />
            </div>

            <div>
              <label className="block mb-2 font-medium">Número de artigos</label>
              <input
                type="number"
                min={1}
                max={50}
                className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-violet-500"
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
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-2xl font-bold mb-4">Bibliometria</h2>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-950 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Total de artigos</p>
                  <p className="text-3xl font-bold text-violet-400">
                    {result.bibliometrics.total_articles as number}
                  </p>
                </div>
                <div className="bg-slate-950 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Fontes consultadas</p>
                  <p className="text-sm mt-1">
                    {Object.entries(
                      (result.bibliometrics.articles_by_source as Record<string, number>) || {}
                    ).map(([src, count]) => (
                      <span key={src} className="inline-block bg-slate-800 rounded px-2 py-1 mr-1 mb-1 text-xs">
                        {src}: {count}
                      </span>
                    ))}
                  </p>
                </div>
              </div>
              <pre className="bg-slate-950 p-4 rounded-xl overflow-auto text-sm text-slate-300">
                {JSON.stringify(result.bibliometrics, null, 2)}
              </pre>
            </div>

            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-2xl font-bold mb-4">
                Fichas dos artigos ({result.cards.length})
              </h2>
              {result.cards.map((card, index) => (
                <div
                  key={index}
                  className="mb-6 p-5 rounded-xl bg-slate-950 border border-slate-800"
                >
                  <h3 className="text-lg font-bold mb-1">{card.title}</h3>
                  <p className="text-slate-400 text-sm mb-3">
                    {card.authors?.join(", ")} — {card.year}
                    {card.journal && ` — ${card.journal}`}
                    {card.doi && (
                      <span className="ml-2 text-violet-400 text-xs">DOI: {card.doi}</span>
                    )}
                  </p>
                  <div className="space-y-2 text-sm">
                    <p><span className="font-semibold text-violet-300">Objetivo:</span> {card.objective}</p>
                    <p><span className="font-semibold text-violet-300">Metodologia:</span> {card.methodology}</p>
                    <p><span className="font-semibold text-violet-300">Resultados:</span> {card.results}</p>
                    <p><span className="font-semibold text-violet-300">Conclusão:</span> {card.conclusion}</p>
                    <p><span className="font-semibold text-violet-300">Relevância:</span> {card.relevance}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-2xl font-bold mb-4">Revisão gerada</h2>
              <div className="whitespace-pre-wrap leading-8 text-slate-100 text-sm">
                {result.generated_review}
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
