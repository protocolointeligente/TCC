"use client";
import { useUser } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";

const PLANS = [
  {
    key: "free",
    name: "Grátis",
    price: "R$ 0",
    limit: "3 pesquisas/mês",
    border: "border-slate-800",
    button: null,
  },
  {
    key: "basic",
    name: "Basic",
    price: "R$ 39,90/mês",
    limit: "30 pesquisas/mês",
    border: "border-violet-700",
    button: { label: "Assinar Basic", class: "bg-violet-600 hover:bg-violet-700" },
  },
  {
    key: "pro",
    name: "Pro",
    price: "R$ 97,00/mês",
    limit: "200 pesquisas/mês",
    border: "border-green-700",
    button: { label: "Assinar Pro", class: "bg-green-600 hover:bg-green-700" },
  },
];

export default function PricingPage() {
  const { user } = useUser();

  async function checkout(plan: string) {
    if (!user) return;
    const response = await apiFetch(
      "/billing/checkout",
      user.id,
      user.primaryEmailAddress?.emailAddress,
      { method: "POST", body: JSON.stringify({ plan }) }
    );
    const data = await response.json();
    if (data.url) window.location.href = data.url;
  }

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Planos</h1>
        <p className="text-slate-400 mb-10">Escolha o plano ideal para sua pesquisa.</p>

        <div className="grid md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.key}
              className={`bg-slate-900 p-6 rounded-2xl border ${plan.border} flex flex-col`}
            >
              <h2 className="text-2xl font-bold mb-1">{plan.name}</h2>
              <p className="text-slate-400 text-sm mb-4">{plan.limit}</p>
              <p className="text-xl font-semibold mb-6">{plan.price}</p>

              {plan.button ? (
                <button
                  onClick={() => checkout(plan.key)}
                  className={`mt-auto ${plan.button.class} px-4 py-2 rounded-xl font-medium text-sm`}
                >
                  {plan.button.label}
                </button>
              ) : (
                <span className="mt-auto text-slate-500 text-sm">Plano atual (sem custo)</span>
              )}
            </div>
          ))}
        </div>

        <p className="mt-10 text-slate-500 text-sm">
          Pagamentos processados com segurança via Stripe. Cancele a qualquer momento.
        </p>
      </div>
    </main>
  );
}
