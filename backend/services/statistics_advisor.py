"""
Suggests statistical analyses based on study design, objectives, and instruments.
"""


_STAT_RULES: list[dict] = [
    {
        "conditions": {"study_type": ["quantitativo", "experimental", "quasi-experimental"]},
        "tests": [
            {"test": "Teste t de Student", "use": "Comparação de médias entre dois grupos independentes."},
            {"test": "ANOVA one-way", "use": "Comparação de médias entre três ou mais grupos."},
            {"test": "Qui-quadrado (χ²)", "use": "Associação entre variáveis categóricas."},
            {"test": "Correlação de Pearson", "use": "Relação linear entre duas variáveis contínuas."},
        ],
    },
    {
        "conditions": {"study_type": ["qualitativo"]},
        "tests": [
            {"test": "Análise de Conteúdo (Bardin)", "use": "Categorização temática de dados textuais."},
            {"test": "Análise Temática (Braun & Clarke)", "use": "Identificação de padrões semânticos em entrevistas."},
            {"test": "Análise de Discurso", "use": "Investigação de construções discursivas e ideológicas."},
        ],
    },
    {
        "conditions": {"study_type": ["misto"]},
        "tests": [
            {"test": "Triangulação de dados", "use": "Integração de dados qualitativos e quantitativos."},
            {"test": "Análise de Conteúdo + Estatística Descritiva", "use": "Complementação quanti-quali."},
        ],
    },
]

_INSTRUMENT_EXTRAS: dict[str, list[dict]] = {
    "ipaq": [
        {"test": "Escore de METs", "use": "Cálculo de nível de atividade física pelo IPAQ."},
    ],
    "whoqol_bref": [
        {"test": "Análise de domínios WHOQOL-bref", "use": "Comparação dos quatro domínios de QV."},
    ],
    "dass_21": [
        {"test": "Ponto de corte DASS-21", "use": "Classificação de severidade de depressão/ansiedade/estresse."},
    ],
    "psqi": [
        {"test": "Escore global PSQI", "use": "Boa qualidade (≤5) vs. má qualidade de sono (>5)."},
    ],
    "bsq": [
        {"test": "Ponto de corte BSQ", "use": "Classificação de preocupação com imagem corporal."},
    ],
    "abq": [
        {"test": "Escore de burnout ABQ", "use": "Dimensões de exaustão, desvalorização e redução de eficácia."},
    ],
    "borg": [
        {"test": "Correlação PSE-Borg × FC/VO2", "use": "Relação entre percepção de esforço e parâmetros fisiológicos."},
    ],
}


def suggest_statistics(
    study_type: str,
    variables: list[str],
    instruments: list[dict],
) -> dict:
    suggestions: list[dict] = []

    for rule in _STAT_RULES:
        if study_type.lower() in rule["conditions"].get("study_type", []):
            suggestions.extend(rule["tests"])

    instrument_ids = {inst.get("id", "") for inst in instruments}
    for inst_id, extras in _INSTRUMENT_EXTRAS.items():
        if inst_id in instrument_ids:
            suggestions.extend(extras)

    if not suggestions:
        suggestions.append({
            "test": "Estatística descritiva (média, DP, frequência)",
            "use": "Descrição das variáveis do estudo.",
        })

    software = _suggest_software(study_type)
    return {"suggestions": suggestions, "software": software}


def _suggest_software(study_type: str) -> list[str]:
    if study_type.lower() == "qualitativo":
        return ["MAXQDA", "NVivo", "Atlas.ti"]
    if study_type.lower() in {"quantitativo", "experimental", "quasi-experimental"}:
        return ["SPSS", "R", "Python (SciPy/Pingouin)", "Jamovi"]
    return ["SPSS", "R", "MAXQDA"]
