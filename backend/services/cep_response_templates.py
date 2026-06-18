_TEMPLATES: dict[str, str] = {
    "riscos": (
        "Em atendimento à pendência, a seção de riscos foi revisada. "
        "Foram detalhados os possíveis desconfortos, bem como as medidas de minimização, "
        "incluindo sigilo, liberdade de desistência, interrupção da coleta/intervenção "
        "e encaminhamento quando necessário."
    ),
    "tcle": (
        "Em atendimento à pendência, o TCLE foi revisado para apresentar linguagem mais clara, "
        "explicitar objetivos, procedimentos, riscos, benefícios, voluntariedade, sigilo "
        "e contato dos pesquisadores."
    ),
    "menores": (
        "Em atendimento à pendência, foram incluídos o TCLE para os responsáveis legais "
        "e o Termo de Assentimento em linguagem adequada à faixa etária dos participantes menores."
    ),
    "anuencia": (
        "Em atendimento à pendência, foi anexada a Carta de Anuência da instituição coparticipante, "
        "autorizando a realização da coleta após aprovação do CEP."
    ),
    "dados": (
        "Em atendimento à pendência, foi detalhado o plano de proteção de dados, "
        "incluindo anonimização, armazenamento seguro, acesso restrito, "
        "finalidade científica e descarte após o período previsto."
    ),
    "metodologia": (
        "Em atendimento à pendência, a metodologia foi complementada com descrição detalhada "
        "do tipo de estudo, local de coleta, critérios de inclusão/exclusão, "
        "instrumentos utilizados, procedimentos e método de análise dos dados."
    ),
}

_DEFAULT = (
    "Em atendimento à pendência, o projeto foi revisado conforme a solicitação do CEP, "
    "com ajustes metodológicos, éticos e documentais indicados."
)


def suggest_response_template(pendency_text: str) -> str:
    text = pendency_text.lower()
    if "risco" in text:
        return _TEMPLATES["riscos"]
    if "tcle" in text or "consentimento" in text:
        return _TEMPLATES["tcle"]
    if "menor" in text or "assentimento" in text:
        return _TEMPLATES["menores"]
    if "anuência" in text or "anuencia" in text or "instituição" in text:
        return _TEMPLATES["anuencia"]
    if "dados" in text or "lgpd" in text or "sensív" in text:
        return _TEMPLATES["dados"]
    if "metodolog" in text or "procedimento" in text:
        return _TEMPLATES["metodologia"]
    return _DEFAULT
