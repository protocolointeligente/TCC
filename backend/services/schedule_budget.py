"""
Generates a research schedule (cronograma) and budget estimate.
"""


_PHASES = [
    ("Revisão bibliográfica", 2),
    ("Elaboração do projeto e submissão ao CEP", 1),
    ("Aguardar aprovação do CEP", 1),
    ("Coleta de dados", 3),
    ("Análise dos dados", 2),
    ("Redação do relatório / TCC", 2),
    ("Revisão e entrega final", 1),
]

_DEFAULT_BUDGET_ITEMS = [
    {"item": "Impressão de formulários / TCLEs", "estimated_cost": "R$ 30–80"},
    {"item": "Transporte para coleta", "estimated_cost": "R$ 50–200"},
    {"item": "Encadernação do TCC", "estimated_cost": "R$ 20–50"},
    {"item": "Taxas de publicação (opcional)", "estimated_cost": "R$ 0–500"},
]


def generate_schedule(research_months: int = 12) -> list[dict]:
    phases = list(_PHASES)
    total_default = sum(d for _, d in phases)
    scale = research_months / total_default

    schedule = []
    start_month = 1
    for name, duration_default in phases:
        duration = max(1, round(duration_default * scale))
        end_month = min(start_month + duration - 1, research_months)
        schedule.append({
            "phase": name,
            "start_month": start_month,
            "end_month": end_month,
            "duration_months": end_month - start_month + 1,
        })
        start_month = end_month + 1
        if start_month > research_months:
            break

    return schedule


def generate_budget(extra_items: list[str] | None = None) -> list[dict]:
    budget = list(_DEFAULT_BUDGET_ITEMS)
    for item_name in (extra_items or []):
        budget.append({"item": item_name, "estimated_cost": "A definir"})
    return budget
