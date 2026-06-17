import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_orientador_opinion(payload, issues: list[dict], risk: dict) -> str:
    """Generate an advisor-perspective opinion on the research project."""

    issue_summary = ""
    if issues:
        lines = [f"- [{i['severity'].upper()}] {i['field']}: {i['message']}" for i in issues[:10]]
        issue_summary = "PROBLEMAS IDENTIFICADOS NO VALIDADOR:\n" + "\n".join(lines)
    else:
        issue_summary = "Nenhum problema crítico identificado pelo validador automático."

    prompt = f"""
Você é um professor orientador de TCC experiente em pesquisa científica brasileira.
Escreva um parecer técnico sobre o projeto abaixo, como se estivesse dando feedback ao aluno.

Tom: construtivo, direto, acadêmico, sem jargão excessivo.
Extensão: 3 a 5 parágrafos.

TÍTULO: {payload.title}
CURSO: {payload.course}
ÁREA: {payload.area}
TIPO DE ESTUDO: {payload.study_type}
OBJETIVO GERAL: {payload.general_objective}
OBJETIVOS ESPECÍFICOS:
{chr(10).join(f"- {o}" for o in payload.specific_objectives)}
METODOLOGIA: {payload.methodology_summary}
POPULAÇÃO: {payload.target_population} | Faixa etária: {payload.age_group}
AMOSTRA PREVISTA: {payload.expected_sample}
LOCAL: {payload.collection_location}
NÍVEL DE RISCO ÉTICO: {risk["risk_level"]} (score: {risk.get("risk_score", "?")})

{issue_summary}

Avalie:
1. Coerência entre objetivo geral e específicos.
2. Adequação metodológica ao tipo de estudo.
3. Clareza da justificativa implícita.
4. Pontos que precisam de atenção antes de submeter ao CEP.
5. Sugestão geral para o aluno.

Finalize com uma nota de 1 a 10 sobre o estado atual do projeto, com justificativa.
""".strip()

    response = _client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Você é um professor orientador de TCC rigoroso, justo e experiente."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
