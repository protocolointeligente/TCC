def check_ethics_resolutions(payload) -> list[dict]:
    checks = []

    checks.append({
        "resolution": "CNS 466/2012",
        "requirement": "Respeito à autonomia, beneficência, não maleficência, justiça e equidade.",
        "status": "verificar",
        "recommendation": (
            "Garantir TCLE, sigilo, riscos, benefícios e liberdade de desistência."
        ),
    })

    qualitative_types = {"entrevista", "questionário online", "estudo qualitativo", "qualitativo", "misto"}
    checks.append({
        "resolution": "CNS 510/2016",
        "requirement": "Aplicável especialmente às Ciências Humanas e Sociais.",
        "status": (
            "aplicável"
            if payload.study_type.lower() in qualitative_types
            else "verificar"
        ),
        "recommendation": (
            "Descrever abordagem, participantes, consentimento e tratamento dos dados."
        ),
    })

    checks.append({
        "resolution": "LGPD (Lei 13.709/2018)",
        "requirement": "Proteção de dados pessoais e sensíveis.",
        "status": "crítico" if payload.collects_sensitive_data else "verificar",
        "recommendation": (
            "Informar base ética, finalidade, anonimização, armazenamento, acesso e descarte."
        ),
    })

    if payload.involves_minors:
        checks.append({
            "resolution": "CNS 466/2012 — Art. 14",
            "requirement": "Proteção de participantes vulneráveis.",
            "status": "crítico",
            "recommendation": (
                "Inserir TCLE dos responsáveis e Termo de Assentimento em linguagem adequada."
            ),
        })

    if payload.is_online_research:
        checks.append({
            "resolution": "CNS 510/2016 — Art. 2º",
            "requirement": "Pesquisa realizada por meios digitais.",
            "status": "aplicável",
            "recommendation": (
                "Mencionar plataforma, forma de consentimento eletrônico, "
                "segurança dos dados e conformidade com a LGPD."
            ),
        })

    return checks
