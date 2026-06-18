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
        <LandingPage />
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

function LandingPage() {
  return (
    <div className="min-h-screen bg-[#020817] text-white">
      <section className="px-6 py-20 max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <p className="text-violet-400 font-semibold mb-4">
            IA acadêmica para TCC, revisão bibliográfica e CEP
          </p>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            Da ideia inicial ao projeto pronto para revisão do orientador.
          </h1>
          <p className="text-slate-300 text-lg mb-8">
            Busque artigos científicos, gere fichas, revisão bibliográfica,
            projeto de TCC, documentos para Plataforma Brasil, TCLE, checklist ético
            e matriz metodológica em português.
          </p>
          <div className="flex gap-4">
            <SignInButton>
              <button className="bg-violet-600 hover:bg-violet-700 px-6 py-4 rounded-xl font-bold">
                Começar agora
              </button>
            </SignInButton>
            <a href="#planos" className="border border-slate-600 px-6 py-4 rounded-xl hover:border-slate-400">
              Ver planos
            </a>
          </div>
        </div>
        <div className="bg-slate-900 rounded-3xl p-8 border border-slate-800 shadow-2xl space-y-3">
          {[
            "✓ Busca em OpenAlex, PubMed e Crossref",
            "✓ Fichas acadêmicas com objetivo, método e conclusão",
            "✓ Revisão bibliográfica completa em ABNT",
            "✓ TCLE, TALE e documentos CEP",
            "✓ Validador ético com pendências simuladas",
            "✓ Matriz metodológica e advisor estatístico",
            "✓ Exportação DOCX editável",
          ].map((item) => (
            <div key={item} className="text-slate-300 text-sm">{item}</div>
          ))}
        </div>
      </section>

      <section className="px-6 py-16 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">O que a plataforma entrega</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            ["Busca científica", "OpenAlex, PubMed, Crossref e Semantic Scholar em uma só consulta."],
            ["Fichas de artigos", "Objetivo, método, resultados, conclusão e relevância para o seu TCC."],
            ["Revisão bibliográfica", "Texto estruturado com introdução, justificativa e discussão em ABNT."],
            ["Assistente CEP", "TCLE, TALE, carta de anuência e Plataforma Brasil gerados automaticamente."],
            ["Validador ético avançado", "Detecta riscos, simula pendências do CEP e verifica coerência metodológica."],
            ["Exportação Word", "Arquivo DOCX formatado com referências ABNT para edição final."],
          ].map(([title, text]) => (
            <div key={title} className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-2">{title}</h3>
              <p className="text-slate-400 text-sm">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="planos" className="px-6 py-20 max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-4">Planos</h2>
        <p className="text-slate-400 text-center mb-12">
          Pague pelo que usa. Cada geração consome créditos proporcionais ao custo real de IA.
        </p>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { name: "Starter", price: "R$ 29", credits: "50 créditos", highlight: false, items: ["5 buscas acadêmicas", "5 fichas completas", "1 revisão simples", "Exportação DOCX"] },
            { name: "Acadêmico", price: "R$ 59", credits: "140 créditos", highlight: true, items: ["15 buscas acadêmicas", "15 fichas completas", "3 revisões", "1 projeto CEP"] },
            { name: "TCC Pro", price: "R$ 97", credits: "300 créditos", highlight: false, items: ["TCC completo", "Revisão + bibliometria", "CEP avançado", "DOCX completo"] },
            { name: "Orientador", price: "R$ 197", credits: "800 créditos", highlight: false, items: ["Uso com vários alunos", "Histórico completo", "Parecer orientador", "Pré-submissão CEP"] },
          ].map(({ name, price, credits, highlight, items }) => (
            <div key={name} className={`rounded-2xl p-6 border ${highlight ? "border-violet-500 bg-violet-950/30" : "border-slate-800 bg-slate-900"}`}>
              <h3 className="text-2xl font-bold">{name}</h3>
              <p className="text-4xl font-bold mt-4">{price}</p>
              <p className="text-violet-300 mt-2 text-sm">{credits}</p>
              <ul className="mt-6 space-y-2 text-slate-300 text-sm">
                {items.map((item) => <li key={item}>✓ {item}</li>)}
              </ul>
              <SignInButton>
                <button className="mt-6 w-full bg-violet-600 hover:bg-violet-700 py-3 rounded-xl font-bold text-sm">
                  Começar
                </button>
              </SignInButton>
            </div>
          ))}
        </div>
      </section>

      <section className="px-6 py-20 max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Não é só escrever. É organizar a pesquisa do jeito certo.</h2>
        <p className="text-slate-300 text-lg mb-4">
          A plataforma não substitui o orientador. Ela reduz retrabalho,
          organiza metodologia, evita referências falsas e ajuda o aluno a
          entregar um material editável, coerente e revisável.
        </p>
        <p className="text-yellow-300/80 text-sm mb-8">
          Os textos gerados são rascunhos acadêmicos assistidos por IA. O aluno deve revisar,
          conferir fontes, inserir análise própria e validar com o orientador.
        </p>
        <SignInButton>
          <button className="bg-violet-600 hover:bg-violet-700 px-8 py-4 rounded-xl font-bold">
            Criar minha primeira pesquisa
          </button>
        </SignInButton>
      </section>
    </div>
  );
}
