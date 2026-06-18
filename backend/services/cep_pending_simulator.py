def simulate_cep_pendencies(payload, issues: list[dict], risk: dict) -> list[dict]:
    pendencies = []

    for issue in issues:
        severity = issue.get("severity", "info")
        probability = "alta" if severity == "error" else "moderada"
        pendencies.append({
            "type": "pendência documental/metodológica",
            "probability": probability,
            "reason": issue["message"],
            "cep_possible_comment": f"Solicita-se adequação no item: {issue['field']}.",
            "how_to_fix": _suggest_fix(issue["field"], issue["message"]),
        })

    if risk["risk_level"] in ["moderado", "elevado"]:
        pendencies.append({
            "type": "pendência ética",
            "probability": "alta",
            "reason": "Riscos não suficientemente minimizados.",
            "cep_possible_comment": "Detalhar riscos, benefícios e medidas de minimização.",
            "how_to_fix": (
                "Reescrever seção de riscos com medidas preventivas, "
                "encaminhamento e confidencialidade."
            ),
        })

    if not payload.methodology_summary or len(payload.methodology_summary) < 120:
        pendencies.append({
            "type": "pendência metodológica",
            "probability": "alta",
            "reason": "Metodologia pouco detalhada.",
            "cep_possible_comment": (
                "Descrever claramente procedimentos, instrumentos, amostra e análise dos dados."
            ),
            "how_to_fix": (
                "Adicionar tipo de estudo, local, participantes, instrumentos, "
                "coleta, análise e aspectos éticos."
            ),
        })

    return pendencies


def _suggest_fix(field: str, message: str) -> str:
    field = field.lower()
    if "title" in field:
        return "Reescreva o título de forma clara e descritiva com pelo menos 10 palavras."
    if "objective" in field:
        return "Reformule o objetivo iniciando com verbo no infinitivo e indicando população, variável e contexto."
    if "methodology" in field:
        return "Detalhe tipo de estudo, local, participantes, instrumentos e procedimentos de análise."
    if "sample" in field or "amostr" in message.lower():
        return "Informe o n esperado e justifique o cálculo amostral ou critério de seleção."
    if "minor" in field or "menor" in message.lower():
        return "Inclua TCLE para responsáveis e Termo de Assentimento para os participantes menores."
    if "sensitive" in field or "sensív" in message.lower():
        return "Descreva anonimização, sigilo, armazenamento seguro e descarte dos dados sensíveis."
    return "Revisar e complementar o item conforme a Resolução CNS 466/2012."
