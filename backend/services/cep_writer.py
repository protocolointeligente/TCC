import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_SECTION_MARKERS = {
    "# PROJETO_DE_PESQUISA": "generated_project",
    "# TCLE": "tcle",
    "# TALE": "tale",
    "# TERMO_DE_ASSENTIMENTO": "assent_term",
    "# CARTA_DE_ANUENCIA": "institution_letter",
}


def generate_cep_documents(payload, risk_analysis: dict, instruments: list, warnings: list) -> str:
    prompt = f"""
Você é um professor orientador especialista em metodologia científica, ética em pesquisa com seres humanos e submissão ao CEP/Plataforma Brasil.
Gere um projeto de pesquisa em português, adequado para submissão ao Comitê de Ética em Pesquisa.

Regras obrigatórias:
- Não prometa aprovação.
- Não invente instrumentos.
- Aponte que os instrumentos sugeridos devem ter versão validada para o público-alvo e autorização de uso quando aplicável.
- Use linguagem formal, cautelosa e juridicamente prudente.

DADOS DO ESTUDO:
Título: {payload.title}
Curso: {payload.course}
Área: {payload.area}
Tipo de estudo: {payload.study_type}
Público-alvo: {payload.target_population}
Faixa etária: {payload.age_group}
Local de coleta: {payload.collection_location}
Envolve menores: {payload.involves_minors}
Usa imagem/áudio/vídeo: {payload.uses_images}
Coleta dados sensíveis: {payload.collects_sensitive_data}
Pesquisa online: {payload.is_online_research}
Intervenção física: {payload.has_physical_intervention}
Objetivo geral: {payload.general_objective}
Objetivos específicos: {payload.specific_objectives}
Resumo da metodologia: {payload.methodology_summary}
Amostra esperada: {payload.expected_sample}

ANÁLISE DE RISCO:
{risk_analysis}

INSTRUMENTOS SUGERIDOS:
{instruments}

ALERTAS ÉTICOS:
{warnings}

Responda exatamente com as seções abaixo, iniciando cada uma pela linha de marcador correspondente:

# PROJETO_DE_PESQUISA
1. Título
2. Resumo
3. Introdução
4. Justificativa
5. Objetivo Geral
6. Objetivos Específicos
7. Metodologia
8. Participantes
9. Critérios de Inclusão
10. Critérios de Exclusão
11. Instrumentos de Coleta
12. Procedimentos de Coleta
13. Riscos
14. Medidas de Minimização dos Riscos
15. Benefícios
16. Sigilo e Confidencialidade
17. Desfechos
18. Cronograma
19. Orçamento
20. Referências a serem preenchidas pelo pesquisador

# TCLE
Gerar modelo de Termo de Consentimento Livre e Esclarecido.

# TALE
Se envolver menores, gerar modelo de termo para responsáveis. Se não envolver, escrever apenas: Não aplicável.

# TERMO_DE_ASSENTIMENTO
Se envolver menores, gerar modelo em linguagem simples para o participante menor. Se não envolver, escrever apenas: Não aplicável.

# CARTA_DE_ANUENCIA
Gerar modelo de carta de anuência institucional.
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Você gera documentos acadêmicos e éticos com linguagem formal, cautelosa e juridicamente prudente.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def split_cep_response(text: str) -> dict:
    sections = {key: "" for key in _SECTION_MARKERS.values()}
    current = None

    for line in text.splitlines():
        marker = line.strip()
        if marker in _SECTION_MARKERS:
            current = _SECTION_MARKERS[marker]
            continue
        if current is not None:
            sections[current] += line + "\n"

    return {key: value.strip() for key, value in sections.items()}
