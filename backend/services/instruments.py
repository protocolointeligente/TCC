INSTRUMENT_DATABASE = [
    {
        "objective_keywords": ["ansiedade", "competição", "esporte"],
        "name": "CSAI-2",
        "full_name": "Competitive State Anxiety Inventory-2",
        "use": "Avaliação da ansiedade competitiva em atletas.",
        "population": "Atletas adolescentes e adultos.",
        "validation_note": "Verificar versão brasileira validada antes da aplicação.",
        "requires_license": "Verificar direitos de uso.",
    },
    {
        "objective_keywords": ["atividade física", "nível de atividade", "sedentarismo"],
        "name": "IPAQ",
        "full_name": "International Physical Activity Questionnaire",
        "use": "Avaliação do nível de atividade física.",
        "population": "Adolescentes e adultos.",
        "validation_note": "Possui versões utilizadas no Brasil.",
        "requires_license": "Geralmente livre para uso acadêmico, mas conferir versão oficial.",
    },
    {
        "objective_keywords": ["qualidade de vida", "saúde geral"],
        "name": "WHOQOL-bref",
        "full_name": "World Health Organization Quality of Life - Bref",
        "use": "Avaliação da qualidade de vida.",
        "population": "Adultos.",
        "validation_note": "Possui versão brasileira validada.",
        "requires_license": "Verificar orientações da OMS.",
    },
    {
        "objective_keywords": ["sono", "qualidade do sono"],
        "name": "PSQI",
        "full_name": "Pittsburgh Sleep Quality Index",
        "use": "Avaliação da qualidade do sono.",
        "population": "Adultos.",
        "validation_note": "Verificar versão brasileira validada.",
        "requires_license": "Pode exigir permissão de uso.",
    },
    {
        "objective_keywords": ["dor", "percepção de dor"],
        "name": "EVA",
        "full_name": "Escala Visual Analógica",
        "use": "Mensuração subjetiva da dor.",
        "population": "Diversas populações.",
        "validation_note": "Instrumento amplamente utilizado.",
        "requires_license": "Geralmente livre.",
    },
    {
        "objective_keywords": ["depressão", "ansiedade", "estresse"],
        "name": "DASS-21",
        "full_name": "Depression, Anxiety and Stress Scale - 21",
        "use": "Avaliação de sintomas de depressão, ansiedade e estresse.",
        "population": "Adolescentes e adultos.",
        "validation_note": "Verificar versão brasileira validada.",
        "requires_license": "Verificar direitos de uso.",
    },
    {
        "objective_keywords": ["imagem corporal", "insatisfação corporal"],
        "name": "BSQ",
        "full_name": "Body Shape Questionnaire",
        "use": "Avaliação da preocupação com a forma corporal.",
        "population": "Adolescentes e adultos.",
        "validation_note": "Verificar versão brasileira validada.",
        "requires_license": "Verificar direitos de uso.",
    },
    {
        "objective_keywords": ["esforço", "intensidade", "treino"],
        "name": "Escala de Borg",
        "full_name": "Rating of Perceived Exertion",
        "use": "Avaliação subjetiva da percepção de esforço.",
        "population": "Atletas, praticantes e pacientes.",
        "validation_note": "Amplamente utilizada em exercício físico.",
        "requires_license": "Verificar versão utilizada.",
    },
]

_FALLBACK = {
    "name": "Instrumento não definido automaticamente",
    "full_name": "Revisão manual necessária",
    "use": "Não foi possível sugerir instrumento com segurança.",
    "population": "Depende do objetivo.",
    "validation_note": "Recomenda-se buscar instrumento validado para o público-alvo.",
    "requires_license": "Verificar.",
}


def suggest_instruments(general_objective: str, specific_objectives: list[str]) -> list[dict]:
    text = (general_objective + " " + " ".join(specific_objectives)).lower()
    suggestions = [
        {k: v for k, v in inst.items() if k != "objective_keywords"}
        for inst in INSTRUMENT_DATABASE
        if any(kw in text for kw in inst["objective_keywords"])
    ]
    return suggestions if suggestions else [_FALLBACK]
