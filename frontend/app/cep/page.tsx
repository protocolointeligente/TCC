"use client";
import { useState } from "react";
import { useUser } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";

interface Instrument {
  name: string;
  full_name: string;
  use: string;
  population: string;
  validation_note: string;
  requires_license: string;
}

interface ChecklistItem {
  item: string;
  status: boolean;
}

interface CepResult {
  project_id: number;
  risk_analysis: { risk_level: string; identified_risks: string[] };
  warnings: string[];
  ethical_checklist: ChecklistItem[];
  suggested_instruments: Instrument[];
  generated_project: string;
  tcle: string;
  tale: string;
  assent_term: string;
  institution_letter: string;
}

const COURSES = ["Educação Física", "Nutrição", "Fisioterapia", "Enfermagem", "Psicologia", "Pedagogia"];
const STUDY_TYPES = [
  "Estudo de campo observacional",
  "Estudo transversal",
  "Estudo experimental",
  "Entrevista",
  "Questionário online",
  "Intervenção com exercício físico",
];

const CHECKBOX_FIELDS: [string, string][] = [
  ["involves_minors", "Envolve menores de idade"],
  ["uses_images", "Usa imagem, áudio ou vídeo"],
  ["collects_sensitive_data", "Coleta dados sensíveis"],
  ["is_online_research", "Pesquisa online"],
  ["has_physical_intervention", "Tem intervenção física"],
];

type FormState = {
  title: string;
  course: string;
  area: string;
  study_type: string;
  target_population: string;
  age_group: string;
  collection_location: string;
  involves_minors: boolean;
  uses_images: boolean;
  collects_sensitive_data: boolean;
  is_online_research: boolean;
  has_physical_intervention: boolean;
  general_objective: string;
  specific_objectives: string;
  methodology_summary: string;
  expected_sample: string;
};

export default function CepPage() {
  const { user } = useUser();

  const [form, setForm] = useState<FormState>({
    title: "",
    course: "Educação Física",
    area: "Saúde",
    study_type: "Estudo de campo observacional",
    target_population: "",
    age_group: "",
    collection_location: "",
    involves_minors: false,
    uses_images: false,
    collects_sensitive_data: false,
    is_online_research: false,
    has_physical_intervention: false,
    general_objective: "",
    specific_objectives: "",
    methodology_summary: "",
    expected_sample: "",
  });

  const [result, setResult] = useState<CepResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"project" | "tcle" | "tale" | "assent" | "letter">("project");

  function update(field: keyof FormState, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function generateProject() {
    if (!user) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiFetch(
        "/cep/project",
        user.id,
        user.primaryEmailAddress?.emailAddress,
        {
          method: "POST",
          body: JSON.stringify({
            ...form,
            specific_objectives: form.specific_objectives
              .split("\n")
              .map((s) => s.trim())
              .filter(Boolean),
          }),
        }
      );
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || "Erro ao gerar projeto.");
        return;
      }
      setResult(data);
    } catch {
      setError("Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  }

  const riskColor = (level: string) =>
    level === "mínimo" ? "text-green-400" : "text-yellow-400";

  const tabs = [
    { key: "project" as const, label: "Projeto" },
    { key: "tcle" as const, label: "TCLE" },
    { key: "tale" as const, label: "TALE" },
    { key: "assent" as const, label: "Assentimento" },
    { key: "letter" as const, label: "Carta de Anuência" },
  ];

  const tabContent: Record<string, string> = result
    ? {
        project: result.generated_project,
        tcle: result.tcle,
        tale: result.tale,
        assent: result.assent_term,
        letter: result.institution_letter,
      }
    : {};

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Assistente CEP / Plataforma Brasil</h1>
        <p className="text-slate-400 mb-8">
          Gere projeto de pesquisa, TCLE, TALE, termo de assentimento, carta de anuência e checklist ético.
        </p>

        {/* Form */}
        <section className="bg-slate-900 p-6 rounded-2xl border border-slate-800 mb-8">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block mb-1 text-sm text-slate-400">Título do projeto</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700 focus:outline-none focus:border-violet-500"
                placeholder="Ex: Ansiedade competitiva em atletas juvenis de natação"
                value={form.title}
                onChange={(e) => update("title", e.target.value)}
              />
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Curso</label>
              <select
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                value={form.course}
                onChange={(e) => update("course", e.target.value)}
              >
                {COURSES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Área</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                value={form.area}
                onChange={(e) => update("area", e.target.value)}
              />
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Tipo de estudo</label>
              <select
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                value={form.study_type}
                onChange={(e) => update("study_type", e.target.value)}
              >
                {STUDY_TYPES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Público-alvo</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                placeholder="Ex: Atletas juvenis de natação"
                value={form.target_population}
                onChange={(e) => update("target_population", e.target.value)}
              />
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Faixa etária</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                placeholder="Ex: 14 a 18 anos"
                value={form.age_group}
                onChange={(e) => update("age_group", e.target.value)}
              />
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Local de coleta</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                placeholder="Ex: Academia, Escola, Hospital..."
                value={form.collection_location}
                onChange={(e) => update("collection_location", e.target.value)}
              />
            </div>

            <div>
              <label className="block mb-1 text-sm text-slate-400">Amostra esperada</label>
              <input
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700"
                placeholder="Ex: 50 participantes"
                value={form.expected_sample}
                onChange={(e) => update("expected_sample", e.target.value)}
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="grid md:grid-cols-2 gap-3 mt-5">
            {CHECKBOX_FIELDS.map(([field, label]) => (
              <label key={field} className="flex items-center gap-3 bg-slate-800 p-3 rounded-xl cursor-pointer">
                <input
                  type="checkbox"
                  checked={(form as Record<string, boolean | string>)[field] as boolean}
                  onChange={(e) => update(field as keyof FormState, e.target.checked)}
                  className="w-4 h-4 accent-violet-500"
                />
                <span className="text-sm">{label}</span>
              </label>
            ))}
          </div>

          {/* Textareas */}
          <div className="mt-5 space-y-4">
            <div>
              <label className="block mb-1 text-sm text-slate-400">Objetivo geral</label>
              <textarea
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700 h-24 focus:outline-none focus:border-violet-500 resize-none"
                value={form.general_objective}
                onChange={(e) => update("general_objective", e.target.value)}
              />
            </div>
            <div>
              <label className="block mb-1 text-sm text-slate-400">
                Objetivos específicos <span className="text-slate-500">(um por linha)</span>
              </label>
              <textarea
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700 h-28 focus:outline-none focus:border-violet-500 resize-none"
                value={form.specific_objectives}
                onChange={(e) => update("specific_objectives", e.target.value)}
              />
            </div>
            <div>
              <label className="block mb-1 text-sm text-slate-400">Resumo da metodologia</label>
              <textarea
                className="w-full p-3 bg-slate-800 rounded-xl border border-slate-700 h-36 focus:outline-none focus:border-violet-500 resize-none"
                value={form.methodology_summary}
                onChange={(e) => update("methodology_summary", e.target.value)}
              />
            </div>
          </div>

          <button
            onClick={generateProject}
            disabled={loading || !form.title.trim() || !form.general_objective.trim()}
            className="mt-6 w-full bg-violet-600 hover:bg-violet-700 disabled:bg-slate-700 disabled:cursor-not-allowed p-4 rounded-xl font-bold transition-colors"
          >
            {loading ? "Gerando projeto CEP..." : "Gerar projeto para CEP"}
          </button>
        </section>

        {error && (
          <div className="bg-red-900/40 border border-red-700 rounded-2xl p-4 mb-8 text-red-300">
            {error}
          </div>
        )}

        {result && (
          <section className="space-y-6">
            {/* Risk + Warnings */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                <h2 className="text-xl font-bold mb-3">Análise de risco</h2>
                <p className="mb-3">
                  Nível:{" "}
                  <span className={`font-bold capitalize ${riskColor(result.risk_analysis.risk_level)}`}>
                    {result.risk_analysis.risk_level}
                  </span>
                </p>
                <ul className="space-y-1 text-sm">
                  {result.risk_analysis.identified_risks.map((r, i) => (
                    <li key={i} className="flex gap-2 text-slate-300">
                      <span className="text-slate-500 mt-0.5">—</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                <h2 className="text-xl font-bold mb-3">Alertas éticos</h2>
                <ul className="space-y-1 text-sm">
                  {result.warnings.map((w, i) => (
                    <li key={i} className="flex gap-2 text-yellow-300">
                      <span className="text-yellow-600 mt-0.5">!</span>
                      {w}
                    </li>
                  ))}
                  {result.warnings.length === 0 && (
                    <li className="text-green-400">Nenhum alerta identificado.</li>
                  )}
                </ul>
              </div>
            </div>

            {/* Checklist */}
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-xl font-bold mb-3">Checklist ético</h2>
              <ul className="space-y-2">
                {result.ethical_checklist.map((item, i) => (
                  <li key={i} className="flex gap-3 items-start text-sm">
                    <span className="text-green-400 mt-0.5 shrink-0">✓</span>
                    {item.item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Instruments */}
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-xl font-bold mb-4">Instrumentos sugeridos</h2>
              <div className="space-y-3">
                {result.suggested_instruments.map((inst, i) => (
                  <div key={i} className="bg-slate-950 p-4 rounded-xl">
                    <p className="font-bold">
                      {inst.name}
                      <span className="font-normal text-slate-400 text-sm ml-2">— {inst.full_name}</span>
                    </p>
                    <p className="text-sm mt-1">{inst.use}</p>
                    <p className="text-sm text-slate-400 mt-1">{inst.validation_note}</p>
                    <p className="text-xs text-slate-500 mt-1">Licença: {inst.requires_license}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Documents with tabs */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800">
              <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <div className="flex gap-1 flex-wrap">
                  {tabs.map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        activeTab === tab.key
                          ? "bg-violet-600 text-white"
                          : "text-slate-400 hover:text-white hover:bg-slate-800"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
                <a
                  href={`${process.env.NEXT_PUBLIC_API_URL}/cep/project/${result.project_id}/export-docx`}
                  target="_blank"
                  className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-xl text-sm font-medium shrink-0"
                >
                  Exportar DOCX completo
                </a>
              </div>
              <div className="p-6">
                <div className="whitespace-pre-wrap leading-7 text-sm text-slate-100 max-h-[70vh] overflow-auto">
                  {tabContent[activeTab] || "Não aplicável."}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
