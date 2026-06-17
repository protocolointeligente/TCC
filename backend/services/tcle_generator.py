import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_smart_tcle(payload) -> str:
    """Generate a TCLE adapted to the population's age group and research characteristics."""

    age_note = ""
    if payload.involves_minors:
        age_note = (
            "O público inclui menores de idade. Gere TAMBÉM um TCLE para responsável legal "
            "e um TALE (Termo de Assentimento) com linguagem acessível para a faixa etária. "
            "Separe os documentos com os marcadores '## TCLE_RESPONSAVEL' e '## TALE'."
        )

    online_note = ""
    if payload.is_online_research:
        online_note = (
            "A pesquisa é realizada online. Inclua: plataforma utilizada, como os dados são "
            "armazenados, conformidade com a LGPD e forma de consentimento eletrônico."
        )

    sensitive_note = ""
    if payload.collects_sensitive_data:
        sensitive_note = (
            "A pesquisa coleta dados sensíveis. Descreva anonimização, sigilo, prazo de guarda "
            "(5 anos conforme Resolução CNS 510/2016) e destino dos dados após o estudo."
        )

    physical_note = ""
    if payload.has_physical_intervention:
        physical_note = (
            "Há intervenção física. Detalhe os riscos específicos, critérios de interrupção, "
            "seguro/cobertura em caso de dano e forma de contato em emergências."
        )

    prompt = f"""
Você é especialista em ética em pesquisa e Plataforma Brasil. Gere um TCLE completo, em português,
conforme a Resolução CNS 466/2012, para a seguinte pesquisa.

TÍTULO: {payload.title}
INSTITUIÇÃO: {payload.institution}
PESQUISADOR: a definir (estudante de graduação/pós-graduação)
ORIENTADOR: {payload.advisor}
OBJETIVO GERAL: {payload.general_objective}
MÉTODO: {payload.methodology_summary}
POPULAÇÃO: {payload.target_population} | Faixa etária: {payload.age_group}
LOCAL DE COLETA: {payload.collection_location}
DURAÇÃO ESTIMADA: {payload.estimated_duration or "a definir"}

{age_note}
{online_note}
{sensitive_note}
{physical_note}

Estrutura obrigatória do TCLE:
1. Identificação e convite
2. Objetivo da pesquisa
3. Procedimentos / o que será pedido ao participante
4. Riscos e desconfortos
5. Benefícios
6. Sigilo e confidencialidade dos dados
7. Voluntariedade e direito de retirada
8. Contatos (pesquisador e CEP)
9. Campos de assinatura (participante e pesquisador, com data e local)

Escreva em linguagem clara e acessível. Não utilize jargões técnicos desnecessários.
""".strip()

    response = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content
