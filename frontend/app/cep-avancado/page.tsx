"use client";

import { useState } from "react";
import { useUser } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";

type Section = "form" | "validator" | "matrix" | "tcle" | "plataforma" | "schedule" | "attachments" | "pendencies" | "orientador";

const TABS: { id: Section; label: string }[] = [
  { id: "validator", label: "Validador" },
  { id: "matrix", label: "Matriz Metodológica" },
  { id: "tcle", label: "TCLE Inteligente" },
  { id: "plataforma", label: "Plataforma Brasil" },
  { id: "schedule", label: "Cronograma / Orçamento" },
  { id: "attachments", label: "Documentos" },
  { id: "pendencies", label: "Pendências CEP" },
  { id: "orientador", label: "Parecer Orientador" },
];

const SEVERITY_COLORS: Record<string, string> = {
  error: "bg-red-900/40 border-red-700 text-red-200",
  warning: "bg-yellow-900/40 border-yellow-700 text-yellow-200",
  info: "bg-blue-900/40 border-blue-700 text-blue-200",
};

const RISK_COLORS: Record<string, string> = {
  mínimo: "text-green-400",
  baixo: "text-yellow-400",
  moderado: "text-orange-400",
  elevado: "text-red-400",
};

const COHERENCE_COLORS: Record<string, string> = {
  coerente: "text-green-400",
  "precisa ajustes": "text-yellow-400",
};

export default function CepAvancadoPage() {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState<Section>("form");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    title: "",
    course: "",
    area: "",
    study_type: "quantitativo",
    institution: "",
    advisor: "",
    target_population: "",
    age_group: "adultos",
    expected_sample: "",
    sampling_method: "",
    collection_location: "",
    collection_method: "",
    estimated_duration: "",
    involves_minors: false,
    uses_images: false,
    collects_sensitive_data: false,
    is_online_research: false,
    has_physical_intervention: false,
    involves_vulnerable_population: false,
    general_objective: "",
    specific_objectives: "",
    methodology_summary: "",
    variables: "",
    budget_items: "",
    research_months: 12,
    generate_orientador_opinion: false,
  });

  const set = (k: string, v: any) => setForm((p) => ({ ...p, [k]: v }));

  const handleSubmit = async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const body = {
        ...form,
        specific_objectives: form.specific_objectives
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        variables: form.variables
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        budget_items: form.budget_items
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        research_months: Number(form.research_months),
      };
      const res = await apiFetch(
        "/cep-advanced/analyze",
        user.id,
        user.primaryEmailAddress?.emailAddress,
        { method: "POST", body: JSON.stringify(body) }
      );
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      const data = await res.json();
      setResult(data);
      setActiveTab("validator");
    } catch (e: any) {
      setError(e.message || "Erro ao processar análise.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">CEP Avançado</h1>
      <p className="text-slate-400 mb-8">
        Validador ético, matriz metodológica, TCLE inteligente, checklist Plataforma Brasil e mais.
      </p>

      {/* Form */}
      {(activeTab === "form" || !result) && (
        <div className="space-y-6">
          <Section title="Identificação do projeto">
            <Field label="Título" value={form.title} onChange={(v) => set("title", v)} />
            <Field label="Curso" value={form.course} onChange={(v) => set("course", v)} />
            <Field label="Área" value={form.area} onChange={(v) => set("area", v)} placeholder="Ex: psicologia, educação física, saúde" />
            <Select label="Tipo de estudo" value={form.study_type} onChange={(v) => set("study_type", v)}
              options={["quantitativo", "qualitativo", "misto", "descritivo", "experimental", "quasi-experimental"]} />
            <Field label="Instituição" value={form.institution} onChange={(v) => set("institution", v)} />
            <Field label="Orientador" value={form.advisor} onChange={(v) => set("advisor", v)} />
          </Section>

          <Section title="Participantes">
            <Field label="População-alvo" value={form.target_population} onChange={(v) => set("target_population", v)} />
            <Select label="Faixa etária" value={form.age_group} onChange={(v) => set("age_group", v)}
              options={["crianças", "adolescentes", "adultos", "idosos", "todos"]} />
            <Field label="Amostra prevista" value={form.expected_sample} onChange={(v) => set("expected_sample", v)} placeholder="Ex: 80 participantes" />
            <Field label="Método de amostragem" value={form.sampling_method} onChange={(v) => set("sampling_method", v)} placeholder="Ex: conveniência, probabilístico" />
          </Section>

          <Section title="Coleta de dados">
            <Field label="Local de coleta" value={form.collection_location} onChange={(v) => set("collection_location", v)} />
            <Field label="Método de coleta" value={form.collection_method} onChange={(v) => set("collection_method", v)} placeholder="Ex: questionário, entrevista" />
            <Field label="Duração estimada (por participante)" value={form.estimated_duration} onChange={(v) => set("estimated_duration", v)} placeholder="Ex: 20 minutos" />
          </Section>

          <Section title="Características éticas">
            <div className="grid grid-cols-2 gap-3">
              {[
                ["involves_minors", "Envolve menores de idade"],
                ["uses_images", "Usa imagens / áudio / vídeo"],
                ["collects_sensitive_data", "Coleta dados sensíveis"],
                ["is_online_research", "Pesquisa online"],
                ["has_physical_intervention", "Intervenção física"],
                ["involves_vulnerable_population", "População vulnerável"],
              ].map(([key, label]) => (
                <label key={key} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(form as any)[key]}
                    onChange={(e) => set(key, e.target.checked)}
                    className="rounded"
                  />
                  {label}
                </label>
              ))}
            </div>
          </Section>

          <Section title="Objetivos">
            <Field label="Objetivo geral" value={form.general_objective} onChange={(v) => set("general_objective", v)} multiline />
            <label className="block text-sm text-slate-300 mb-1">
              Objetivos específicos (um por linha)
            </label>
            <textarea
              value={form.specific_objectives}
              onChange={(e) => set("specific_objectives", e.target.value)}
              rows={4}
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm resize-none"
              placeholder="Avaliar o nível de atividade física...&#10;Comparar o estresse entre grupos..."
            />
          </Section>

          <Section title="Metodologia">
            <Field label="Resumo da metodologia" value={form.methodology_summary} onChange={(v) => set("methodology_summary", v)} multiline rows={5} />
            <Field label="Variáveis (separadas por vírgula)" value={form.variables} onChange={(v) => set("variables", v)} placeholder="atividade física, qualidade de vida, ansiedade" />
          </Section>

          <Section title="Cronograma e Orçamento">
            <Field label="Duração total da pesquisa (meses)" value={String(form.research_months)} onChange={(v) => set("research_months", v)} />
            <Field label="Itens de orçamento adicionais (vírgula)" value={form.budget_items} onChange={(v) => set("budget_items", v)} placeholder="software SPSS, passagens, material de escritório" />
          </Section>

          <Section title="Extras">
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={form.generate_orientador_opinion}
                onChange={(e) => set("generate_orientador_opinion", e.target.checked)}
                className="rounded"
              />
              Gerar parecer do orientador (usa IA — demora alguns segundos a mais)
            </label>
          </Section>

          <div className="bg-yellow-950/40 border border-yellow-700 rounded-xl p-4 text-yellow-200 text-sm">
            A plataforma gera rascunhos acadêmicos assistidos por IA. O usuário deve revisar,
            conferir fontes, inserir análise própria e validar com o orientador.
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading || !form.title || !form.general_objective}
            className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 py-3 rounded-xl font-bold"
          >
            {loading ? "Analisando..." : "Analisar Projeto"}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8">
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => setActiveTab("form")}
              className="text-sm text-slate-400 hover:text-white mr-4"
            >
              ← Editar formulário
            </button>
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === t.id
                    ? "bg-violet-600 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Validator */}
          {activeTab === "validator" && (
            <div className="space-y-4">
              <div className="flex items-center gap-4 mb-4">
                <h2 className="text-xl font-bold">Validador Ético</h2>
                <span className={`font-bold ${RISK_COLORS[result.risk?.risk_level] || "text-slate-300"}`}>
                  Risco: {result.risk?.risk_level} (score {result.risk?.risk_score})
                </span>
                <span className={`font-semibold ${COHERENCE_COLORS[result.methodological_coherence?.status] || ""}`}>
                  Coerência: {result.methodological_coherence?.status}
                </span>
              </div>

              {result.risk?.identified_risks?.map((r: string, i: number) => (
                <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-300">
                  {r}
                </div>
              ))}

              {result.validator?.issues?.length === 0 ? (
                <p className="text-green-400">Nenhum problema crítico encontrado.</p>
              ) : (
                result.validator.issues.map((issue: any, i: number) => (
                  <div key={i} className={`rounded-lg px-4 py-3 border text-sm ${SEVERITY_COLORS[issue.severity]}`}>
                    <span className="font-bold uppercase">[{issue.severity}]</span>{" "}
                    <span className="text-slate-400">{issue.field}:</span> {issue.message}
                  </div>
                ))
              )}

              {result.methodological_coherence?.problems?.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2 text-yellow-300">Problemas de coerência metodológica</h3>
                  {result.methodological_coherence.problems.map((p: string, i: number) => (
                    <div key={i} className="bg-yellow-900/30 border border-yellow-700 rounded-lg px-4 py-2 text-sm text-yellow-200 mb-2">
                      {p}
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-4">
                <h3 className="font-semibold mb-2">Resoluções éticas aplicáveis</h3>
                <div className="space-y-2">
                  {result.ethics_resolution_checks?.map((c: any, i: number) => (
                    <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm">
                      <span className="font-bold text-violet-300">{c.resolution}</span>
                      {" — "}
                      <span className={`font-semibold ${c.status === "crítico" ? "text-red-400" : c.status === "aplicável" ? "text-yellow-400" : "text-slate-400"}`}>
                        {c.status}
                      </span>
                      <p className="text-slate-400 mt-1">{c.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Matrix */}
          {activeTab === "matrix" && (
            <div>
              <h2 className="text-xl font-bold mb-4">Matriz Objetivo → Instrumento → Variável → Análise</h2>
              {result.instruments?.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2 text-violet-300">Instrumentos sugeridos</h3>
                  <div className="grid gap-3">
                    {result.instruments.map((inst: any, i: number) => (
                      <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm">
                        <span className="font-bold">{inst.name}</span>
                        {inst.construct && <span className="text-slate-400"> — {inst.construct}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-800">
                      <th className="border border-slate-700 px-3 py-2 text-left">Objetivo específico</th>
                      <th className="border border-slate-700 px-3 py-2 text-left">Instrumento</th>
                      <th className="border border-slate-700 px-3 py-2 text-left">Variável</th>
                      <th className="border border-slate-700 px-3 py-2 text-left">Análise</th>
                      <th className="border border-slate-700 px-3 py-2 text-left">Desfecho</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.objective_matrix?.map((row: any, i: number) => (
                      <tr key={i} className="odd:bg-slate-900 even:bg-slate-800/50">
                        <td className="border border-slate-700 px-3 py-2">{row.objective}</td>
                        <td className="border border-slate-700 px-3 py-2 text-violet-300">{row.instrument}</td>
                        <td className="border border-slate-700 px-3 py-2">{row.variable}</td>
                        <td className="border border-slate-700 px-3 py-2 text-yellow-300">{row.analysis}</td>
                        <td className="border border-slate-700 px-3 py-2 text-slate-400">{row.outcome}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-6">
                <h3 className="font-semibold mb-2">Análises sugeridas</h3>
                <div className="space-y-2">
                  {result.statistics?.suggestions?.map((s: any, i: number) => (
                    <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm">
                      <span className="font-bold text-green-300">{s.test}</span>
                      <span className="text-slate-400"> — {s.use}</span>
                    </div>
                  ))}
                </div>
                {result.statistics?.software?.length > 0 && (
                  <p className="text-sm text-slate-400 mt-3">
                    Softwares sugeridos: {result.statistics.software.join(", ")}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* TCLE */}
          {activeTab === "tcle" && (
            <div>
              <h2 className="text-xl font-bold mb-4">TCLE Inteligente</h2>
              <pre className="bg-slate-900 border border-slate-700 rounded-xl p-6 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                {result.smart_tcle}
              </pre>
            </div>
          )}

          {/* Plataforma Brasil */}
          {activeTab === "plataforma" && (
            <div>
              <h2 className="text-xl font-bold mb-4">Checklist Plataforma Brasil</h2>
              <div className="space-y-6 mb-6">
                {result.plataforma_brasil?.checklist_sections?.map((section: any, i: number) => (
                  <div key={i}>
                    <h3 className="font-semibold text-violet-300 mb-2">{section.section}</h3>
                    <ul className="space-y-1">
                      {section.fields.map((field: string, j: number) => (
                        <li key={j} className="flex items-center gap-2 text-sm text-slate-300">
                          <span className="text-green-400">✓</span> {field}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              {result.plataforma_brasil?.plataforma_brasil_tips && (
                <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-4">
                  <h3 className="font-semibold text-blue-300 mb-2">Dicas de preenchimento</h3>
                  <pre className="text-sm text-blue-100 whitespace-pre-wrap font-sans">
                    {result.plataforma_brasil.plataforma_brasil_tips}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Schedule / Budget */}
          {activeTab === "schedule" && (
            <div className="space-y-8">
              <div>
                <h2 className="text-xl font-bold mb-4">Cronograma</h2>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-800">
                      <th className="border border-slate-700 px-3 py-2 text-left">Fase</th>
                      <th className="border border-slate-700 px-3 py-2 text-center">Mês início</th>
                      <th className="border border-slate-700 px-3 py-2 text-center">Mês fim</th>
                      <th className="border border-slate-700 px-3 py-2 text-center">Duração</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.schedule?.map((row: any, i: number) => (
                      <tr key={i} className="odd:bg-slate-900 even:bg-slate-800/50">
                        <td className="border border-slate-700 px-3 py-2">{row.phase}</td>
                        <td className="border border-slate-700 px-3 py-2 text-center">{row.start_month}</td>
                        <td className="border border-slate-700 px-3 py-2 text-center">{row.end_month}</td>
                        <td className="border border-slate-700 px-3 py-2 text-center">{row.duration_months} mês(es)</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div>
                <h2 className="text-xl font-bold mb-4">Orçamento</h2>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-800">
                      <th className="border border-slate-700 px-3 py-2 text-left">Item</th>
                      <th className="border border-slate-700 px-3 py-2 text-right">Custo estimado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.budget?.map((row: any, i: number) => (
                      <tr key={i} className="odd:bg-slate-900 even:bg-slate-800/50">
                        <td className="border border-slate-700 px-3 py-2">{row.item}</td>
                        <td className="border border-slate-700 px-3 py-2 text-right text-green-300">{row.estimated_cost}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Attachments */}
          {activeTab === "attachments" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold mb-4">Biblioteca de Anexos</h2>

              <div>
                <h3 className="font-semibold text-red-300 mb-3">Obrigatórios</h3>
                <div className="space-y-2">
                  {result.attachments?.required?.map((a: any, i: number) => (
                    <div key={i} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-bold">{a.name}</span>
                        {a.template_available && (
                          <button
                            className="text-xs text-violet-400 hover:text-violet-300"
                            onClick={() => {
                              const tmpl = result.attachment_templates?.[a.name];
                              if (tmpl) alert(tmpl);
                            }}
                          >
                            Ver modelo
                          </button>
                        )}
                      </div>
                      <p className="text-slate-400 mt-1">{a.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {result.attachments?.optional?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-slate-400 mb-3">Opcionais / não aplicáveis a esta pesquisa</h3>
                  <div className="space-y-2">
                    {result.attachments.optional.map((a: any, i: number) => (
                      <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 text-sm text-slate-500">
                        <span className="font-medium">{a.name}</span>
                        <span className="text-slate-600"> — {a.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="font-semibold mb-3">Pacote de pré-submissão</h3>
                <div className={`rounded-xl border p-4 text-sm ${
                  result.pre_submission_package?.status === "pronto para pré-submissão"
                    ? "bg-green-900/30 border-green-700 text-green-200"
                    : "bg-yellow-900/30 border-yellow-700 text-yellow-200"
                }`}>
                  <p className="font-bold mb-2">Status: {result.pre_submission_package?.status}</p>
                  {result.pre_submission_package?.missing_or_pending?.map((m: string, i: number) => (
                    <p key={i} className="text-sm opacity-80">⚠ {m}</p>
                  ))}
                  <p className="text-xs mt-2 opacity-70">{result.pre_submission_package?.final_instruction}</p>
                </div>
              </div>
            </div>
          )}

          {/* Pendencies */}
          {activeTab === "pendencies" && (
            <div>
              <h2 className="text-xl font-bold mb-4">Simulador de Pendências CEP</h2>
              {result.cep_pendency_simulator?.length === 0 ? (
                <p className="text-green-400">Nenhuma pendência simulada. Projeto em boa forma para submissão.</p>
              ) : (
                <div className="space-y-4">
                  {result.cep_pendency_simulator?.map((p: any, i: number) => (
                    <div key={i} className="bg-slate-800 border border-slate-700 rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                          p.probability === "alta" ? "bg-red-800 text-red-200" : "bg-yellow-800 text-yellow-200"
                        }`}>
                          {p.probability}
                        </span>
                        <span className="text-sm text-slate-300 font-semibold">{p.type}</span>
                      </div>
                      <p className="text-sm text-slate-300 mb-1"><strong>Motivo:</strong> {p.reason}</p>
                      <p className="text-sm text-slate-400 mb-1"><strong>Comentário CEP esperado:</strong> {p.cep_possible_comment}</p>
                      <p className="text-sm text-green-300"><strong>Como corrigir:</strong> {p.how_to_fix}</p>
                    </div>
                  ))}
                </div>
              )}

              {result.pendency_response_templates?.length > 0 && (
                <div className="mt-8">
                  <h3 className="font-semibold mb-3">Modelos de resposta a pendências</h3>
                  <div className="space-y-3">
                    {result.pendency_response_templates.map((t: any, i: number) => (
                      <div key={i} className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm">
                        <p className="text-slate-400 mb-2 text-xs">Pendência: {t.pendency}</p>
                        <p className="text-slate-300 italic">"{t.suggested_response}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Orientador */}
          {activeTab === "orientador" && (
            <div>
              <h2 className="text-xl font-bold mb-4">Parecer do Orientador</h2>
              {result.orientador_opinion ? (
                <pre className="bg-slate-900 border border-slate-700 rounded-xl p-6 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                  {result.orientador_opinion}
                </pre>
              ) : (
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 text-slate-400">
                  <p className="mb-3">O parecer do orientador não foi solicitado nesta análise.</p>
                  <p className="text-sm">Marque "Gerar parecer do orientador" no formulário e reenvie.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <h2 className="font-semibold text-slate-200 mb-4">{title}</h2>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  multiline,
  rows,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
}) {
  const cls = "w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm";
  return (
    <div>
      <label className="block text-sm text-slate-300 mb-1">{label}</label>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={rows || 3}
          className={cls + " resize-none"}
          placeholder={placeholder}
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cls}
          placeholder={placeholder}
        />
      )}
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <div>
      <label className="block text-sm text-slate-300 mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}
