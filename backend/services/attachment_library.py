"""
Lists required and optional attachments for a CEP/Plataforma Brasil submission.
"""


_ALWAYS_REQUIRED = [
    {
        "name": "Projeto de pesquisa completo",
        "description": "Introdução, justificativa, objetivos, metodologia, riscos e benefícios.",
        "template_available": False,
    },
    {
        "name": "TCLE (Termo de Consentimento Livre e Esclarecido)",
        "description": "Para todos os participantes adultos capazes.",
        "template_available": True,
    },
    {
        "name": "Cronograma de execução",
        "description": "Tabela com fases e datas previstas.",
        "template_available": True,
    },
    {
        "name": "Orçamento detalhado",
        "description": "Planilha com itens e estimativas de custo.",
        "template_available": True,
    },
    {
        "name": "Currículo Lattes do(s) pesquisador(es)",
        "description": "CV atualizado do pesquisador responsável e do orientador.",
        "template_available": False,
    },
]

_CONDITIONAL: list[dict] = [
    {
        "condition": "involves_minors",
        "name": "Termo de Assentimento (TALE)",
        "description": "Para participantes entre 7–17 anos, com linguagem adequada à faixa etária.",
        "template_available": True,
    },
    {
        "condition": "involves_minors",
        "name": "TCLE para responsável legal",
        "description": "Consentimento do responsável pelo menor de idade.",
        "template_available": True,
    },
    {
        "condition": "collection_location_institution",
        "name": "Carta de Anuência da Instituição",
        "description": "Autorização formal do local onde ocorrerá a coleta de dados.",
        "template_available": True,
    },
    {
        "condition": "uses_images",
        "name": "Autorização de uso de imagem/áudio/vídeo",
        "description": "Cláusula específica ou documento separado para gravações.",
        "template_available": True,
    },
    {
        "condition": "involves_vulnerable_population",
        "name": "Justificativa para inclusão de população vulnerável",
        "description": "Documento explicando a necessidade de incluir população vulnerável.",
        "template_available": False,
    },
    {
        "condition": "has_physical_intervention",
        "name": "Protocolo de segurança para intervenção física",
        "description": "Critérios de interrupção, seguro e medidas de emergência.",
        "template_available": False,
    },
]

_INSTITUTION_KEYWORDS = {"escola", "academia", "clínica", "clinica", "hospital", "universidade", "ubs", "creche"}


def generate_attachment_library(payload) -> dict:
    required = list(_ALWAYS_REQUIRED)
    optional: list[dict] = []

    loc = payload.collection_location.lower()
    is_institution = any(kw in loc for kw in _INSTITUTION_KEYWORDS)

    for cond_item in _CONDITIONAL:
        cond = cond_item["condition"]
        matches = (
            (cond == "involves_minors" and payload.involves_minors)
            or (cond == "collection_location_institution" and is_institution)
            or (cond == "uses_images" and payload.uses_images)
            or (cond == "involves_vulnerable_population" and payload.involves_vulnerable_population)
            or (cond == "has_physical_intervention" and payload.has_physical_intervention)
        )
        item = {k: v for k, v in cond_item.items() if k != "condition"}
        if matches:
            required.append(item)
        else:
            optional.append(item)

    return {"required": required, "optional": optional}


_TEMPLATES: dict[str, str] = {
    "TCLE (Termo de Consentimento Livre e Esclarecido)": (
        "TERMO DE CONSENTIMENTO LIVRE E ESCLARECIDO\n\n"
        "Você está sendo convidado(a) a participar da pesquisa intitulada \"[TÍTULO]\", "
        "desenvolvida por [PESQUISADOR], sob orientação de [ORIENTADOR], da [INSTITUIÇÃO].\n\n"
        "OBJETIVO: [OBJETIVO GERAL].\n\n"
        "PROCEDIMENTOS: [DESCREVER PROCEDIMENTOS].\n\n"
        "RISCOS: [DESCREVER RISCOS].\n\n"
        "BENEFÍCIOS: [DESCREVER BENEFÍCIOS].\n\n"
        "SIGILO: Suas informações serão tratadas com total confidencialidade. "
        "Os dados serão armazenados por 5 anos e, após, descartados com segurança.\n\n"
        "VOLUNTARIEDADE: Sua participação é voluntária. Você pode retirar o consentimento a qualquer momento.\n\n"
        "CONTATO: [NOME], [E-MAIL], [TELEFONE]. CEP: [CONTATO CEP].\n\n"
        "Ao assinar abaixo, você declara que leu, compreendeu e concorda em participar.\n\n"
        "Nome do participante: _______________________  Data: ___/___/______\n"
        "Assinatura: _______________________\n\n"
        "Nome do pesquisador: _______________________  Data: ___/___/______\n"
        "Assinatura: _______________________"
    ),
    "Termo de Assentimento (TALE)": (
        "TERMO DE ASSENTIMENTO LIVRE E ESCLARECIDO\n\n"
        "Olá! Você está sendo convidado(a) a participar de uma pesquisa. "
        "Isso significa que vamos fazer [DESCREVER ATIVIDADE] com você.\n\n"
        "Nós queremos aprender sobre [OBJETIVO SIMPLIFICADO].\n\n"
        "Você não é obrigado(a) a participar. Se você não quiser, está tudo bem. "
        "Se quiser parar no meio, também pode.\n\n"
        "Se tiver alguma dúvida, pode perguntar para [NOME DO PESQUISADOR].\n\n"
        "Se você quiser participar, escreva seu nome abaixo:\n\n"
        "Nome: _______________________  Data: ___/___/______\n"
        "Assinatura ou impressão dactiloscópica: _______________________"
    ),
    "Carta de Anuência da Instituição": (
        "CARTA DE ANUÊNCIA\n\n"
        "Eu, [NOME DO RESPONSÁVEL], [CARGO], da [NOME DA INSTITUIÇÃO], "
        "declaro estar ciente da realização da pesquisa intitulada \"[TÍTULO]\", "
        "coordenada por [PESQUISADOR], sob orientação de [ORIENTADOR], "
        "da [INSTITUIÇÃO PROPONENTE].\n\n"
        "Autorizo a realização da pesquisa nas dependências desta instituição, "
        "no período de [DATA INÍCIO] a [DATA FIM].\n\n"
        "Estou ciente de que a pesquisa não acarretará custos ou ônus para esta instituição "
        "e que os dados serão utilizados exclusivamente para fins científicos.\n\n"
        "[LOCAL], ___/___/______\n\n"
        "___________________________________\n"
        "[NOME DO RESPONSÁVEL]\n"
        "[CARGO] — [NOME DA INSTITUIÇÃO]"
    ),
    "Cronograma de execução": (
        "CRONOGRAMA DE EXECUÇÃO\n\n"
        "Pesquisa: [TÍTULO]\n\n"
        "Fase | Mês início | Mês fim | Responsável\n"
        "-----|-----------|---------|------------\n"
        "Revisão bibliográfica | 1 | 2 | Pesquisador\n"
        "Elaboração e submissão CEP | 3 | 3 | Pesquisador\n"
        "Aguardar aprovação | 4 | 4 | —\n"
        "Coleta de dados | 5 | 7 | Pesquisador\n"
        "Análise dos dados | 8 | 9 | Pesquisador\n"
        "Redação do TCC | 10 | 11 | Pesquisador\n"
        "Entrega final | 12 | 12 | Pesquisador"
    ),
    "Orçamento detalhado": (
        "ORÇAMENTO DETALHADO\n\n"
        "Item | Quantidade | Custo unitário | Total\n"
        "-----|-----------|----------------|------\n"
        "Impressão de formulários | 100 | R$ 0,10 | R$ 10,00\n"
        "Transporte | — | — | R$ 100,00\n"
        "Encadernação | 3 | R$ 15,00 | R$ 45,00\n"
        "Total estimado: R$ 155,00"
    ),
}


def generate_attachment_templates(names: list[str]) -> dict[str, str]:
    return {name: _TEMPLATES[name] for name in names if name in _TEMPLATES}
