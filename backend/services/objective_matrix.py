import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_objective_matrix(payload, instruments: list[dict]) -> list[dict]:
    """
    Returns a matrix mapping each specific objective to instruments, variables,
    and suggested analyses.
    """
    if not payload.specific_objectives:
        return []

    instruments_summary = "\n".join(
        f"- {inst.get('name', inst.get('id'))}: mede {inst.get('construct', 'não informado')} "
        f"(área: {inst.get('area', '?')})"
        for inst in instruments[:8]
    )

    objectives_text = "\n".join(
        f"{i + 1}. {obj}" for i, obj in enumerate(payload.specific_objectives)
    )

    prompt = f"""
Você é metodologista especialista em pesquisa acadêmica brasileira.
Crie uma matriz metodológica para a pesquisa abaixo.

TIPO DE ESTUDO: {payload.study_type}
ÁREA: {payload.area}

OBJETIVO GERAL: {payload.general_objective}

OBJETIVOS ESPECÍFICOS:
{objectives_text}

INSTRUMENTOS DISPONÍVEIS:
{instruments_summary or "Nenhum instrumento identificado automaticamente."}

VARIÁVEIS DECLARADAS:
{", ".join(payload.variables or []) or "Não informadas."}

Para cada objetivo específico, gere um objeto JSON com:
- "objective": texto do objetivo específico
- "instrument": instrumento mais adequado para medi-lo (nome ou "Não identificado")
- "variable": variável principal mensurada
- "analysis": análise estatística/qualitativa recomendada
- "outcome": desfecho esperado (o que o resultado vai revelar)

Responda em formato JSON array. Exemplo:
[
  {{
    "objective": "Avaliar o nível de atividade física...",
    "instrument": "IPAQ",
    "variable": "Nível de atividade física (METs)",
    "analysis": "Escore de METs + ANOVA",
    "outcome": "Classificação em sedentário, irregularmente ativo, ativo ou muito ativo"
  }}
]

Responda APENAS com o JSON, sem texto adicional.
""".strip()

    response = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    import json
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [{"objective": obj, "instrument": "?", "variable": "?", "analysis": "?", "outcome": "?"} for obj in payload.specific_objectives]
