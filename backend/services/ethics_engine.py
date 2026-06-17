from cep_schemas import EthicsProjectRequest

_INSTITUTION_LOCATIONS = {"escola", "academia", "clínica", "hospital", "universidade"}


def classify_risk(payload: EthicsProjectRequest) -> dict:
    risks = []
    level = "mínimo"

    if payload.collects_sensitive_data:
        risks.append("Coleta de dados sensíveis ou identificáveis.")
        level = "moderado"
    if payload.uses_images:
        risks.append("Uso de imagem, áudio ou vídeo dos participantes.")
        level = "moderado"
    if payload.involves_minors:
        risks.append("Participação de menores de idade.")
        level = "moderado"
    if payload.has_physical_intervention:
        risks.append("Intervenção física ou teste corporal com possível desconforto.")
        level = "moderado"
    if payload.is_online_research:
        risks.append("Coleta em ambiente virtual, com risco de exposição de dados digitais.")

    if not risks:
        risks.append("Risco mínimo, relacionado a possível desconforto ao responder perguntas.")

    return {"risk_level": level, "identified_risks": risks}


def generate_ethics_warnings(payload: EthicsProjectRequest) -> list[str]:
    warnings = []

    if payload.involves_minors:
        warnings.append("Exigir TCLE dos responsáveis e Termo de Assentimento para menores.")
    if payload.collection_location.lower() in _INSTITUTION_LOCATIONS:
        warnings.append("Solicitar carta de anuência da instituição onde ocorrerá a coleta.")
    if payload.uses_images:
        warnings.append("Inserir autorização específica para uso de imagem, áudio ou vídeo.")
    if payload.collects_sensitive_data:
        warnings.append("Descrever claramente sigilo, anonimização, armazenamento e descarte dos dados.")
    if payload.is_online_research:
        warnings.append("Informar plataforma utilizada, segurança dos dados, convite eletrônico e forma de consentimento.")
    if payload.has_physical_intervention:
        warnings.append("Descrever riscos físicos, critérios de interrupção e medidas de segurança.")
    if not payload.specific_objectives:
        warnings.append("Inserir objetivos específicos coerentes com o objetivo geral.")

    return warnings


def generate_ethical_checklist(payload: EthicsProjectRequest) -> list[dict]:
    checklist = [
        {"item": "Projeto apresenta introdução, justificativa, objetivos e metodologia.", "status": True},
        {"item": "Critérios de inclusão e exclusão definidos.", "status": True},
        {"item": "Riscos e benefícios descritos.", "status": True},
        {"item": "TCLE necessário.", "status": True},
        {"item": "Carta de anuência necessária quando houver coleta em instituição.", "status": True},
    ]

    if payload.involves_minors:
        checklist.append({
            "item": "TALE/Termo de Assentimento necessário para participantes menores.",
            "status": True,
        })
    if payload.uses_images:
        checklist.append({
            "item": "Termo de autorização de imagem necessário.",
            "status": True,
        })
    if payload.is_online_research:
        checklist.append({
            "item": "Metodologia deve detalhar coleta virtual e proteção de dados.",
            "status": True,
        })

    return checklist
