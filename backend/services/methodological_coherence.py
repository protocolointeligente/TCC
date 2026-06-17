def validate_methodological_coherence(
    payload,
    instruments: list[dict],
    matrix: list[dict],
    statistics: dict,
) -> dict:
    problems = []

    if not payload.general_objective:
        problems.append("Objetivo geral ausente.")

    if not payload.specific_objectives:
        problems.append("Objetivos específicos ausentes.")

    if not instruments:
        problems.append(
            "Nenhum instrumento compatível foi encontrado para os objetivos e população."
        )

    if not matrix:
        problems.append(
            "Não foi possível montar a matriz objetivo → instrumento → variável → análise."
        )

    if (
        "experimental" in payload.study_type.lower()
        and not payload.has_physical_intervention
    ):
        problems.append(
            "Estudo marcado como experimental, mas nenhuma intervenção física foi definida."
        )

    if (
        payload.has_physical_intervention
        and "intervenção" not in payload.methodology_summary.lower()
        and "protocolo" not in payload.methodology_summary.lower()
    ):
        problems.append(
            "Intervenção física marcada, mas metodologia não descreve o protocolo."
        )

    if payload.collects_sensitive_data and not any(
        kw in payload.methodology_summary.lower()
        for kw in ["anoni", "sigil", "confidenci", "proteg", "lgpd"]
    ):
        problems.append(
            "Coleta de dados sensíveis sem menção a anonimização ou proteção de dados na metodologia."
        )

    suggestions = statistics.get("suggestions", [])
    if not suggestions:
        problems.append("Nenhuma análise estatística/qualitativa foi identificada para o estudo.")

    status = "coerente" if not problems else "precisa ajustes"
    return {
        "status": status,
        "problems": problems,
        "recommendation": (
            "Ajustar objetivo, instrumento, variável, desfecho e análise "
            "até que todos estejam alinhados entre si."
        ),
    }
