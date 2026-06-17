import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


_STATIC_FIELDS = [
    {
        "section": "Identificação do projeto",
        "fields": [
            "Título do projeto",
            "Área temática",
            "Área de conhecimento (CNPq)",
            "Tipo de financiamento",
            "Número de participantes",
            "Data de início prevista",
            "Data de encerramento prevista",
        ],
    },
    {
        "section": "Pesquisador responsável",
        "fields": [
            "Nome completo",
            "Número do CPF",
            "Número do Lattes",
            "Instituição proponente",
            "Endereço institucional",
            "Telefone e e-mail",
        ],
    },
    {
        "section": "Documentos obrigatórios",
        "fields": [
            "Folha de rosto assinada",
            "Projeto de pesquisa completo",
            "TCLE",
            "Cronograma",
            "Orçamento",
        ],
    },
    {
        "section": "Aspectos éticos declarados",
        "fields": [
            "Declaração de que os riscos foram minimizados",
            "Declaração de inexistência de conflito de interesses",
            "Declaração de responsabilidade do pesquisador",
        ],
    },
]


def generate_plataforma_brasil_checklist(payload) -> dict:
    sections = [s.copy() for s in _STATIC_FIELDS]

    conditional_docs: list[str] = []
    if payload.involves_minors:
        conditional_docs.extend(["TCLE dos responsáveis legais", "Termo de Assentimento (TALE)"])
    if payload.uses_images:
        conditional_docs.append("Autorização de uso de imagem/áudio/vídeo")

    loc = payload.collection_location.lower()
    institution_kws = {"escola", "academia", "clínica", "clinica", "hospital", "universidade", "ubs", "creche"}
    if any(kw in loc for kw in institution_kws):
        conditional_docs.append("Carta de Anuência da instituição coparticipante")
    if payload.involves_vulnerable_population:
        conditional_docs.append("Justificativa para inclusão de população vulnerável")
    if payload.is_online_research:
        conditional_docs.append("Convite eletrônico ao participante / formulário online")

    if conditional_docs:
        sections.append({
            "section": "Documentos condicionais (obrigatórios para esta pesquisa)",
            "fields": conditional_docs,
        })

    prompt = f"""
Você é especialista em Plataforma Brasil e CEP. Para o projeto abaixo, liste observações importantes
sobre o preenchimento de cada campo do sistema Plataforma Brasil, em formato de lista.

TÍTULO: {payload.title}
TIPO DE ESTUDO: {payload.study_type}
POPULAÇÃO: {payload.target_population} | {payload.age_group}
ÁREA: {payload.area}
OBJETIVO: {payload.general_objective}
ENVOLVE MENORES: {payload.involves_minors}
DADOS SENSÍVEIS: {payload.collects_sensitive_data}
PESQUISA ONLINE: {payload.is_online_research}

Gere alertas práticos e objetivos (máximo 8 itens) sobre armadilhas comuns no preenchimento
da Plataforma Brasil para este tipo de pesquisa.
""".strip()

    response = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    ai_tips = response.choices[0].message.content

    return {"checklist_sections": sections, "plataforma_brasil_tips": ai_tips}
