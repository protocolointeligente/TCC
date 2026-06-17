_INSTITUTION_KEYWORDS = {"escola", "academia", "clínica", "clinica", "hospital", "universidade", "ubs", "creche"}

_BASE_DOCS = [
    "Projeto de pesquisa completo",
    "TCLE",
    "Instrumentos de coleta",
    "Cronograma",
    "Orçamento",
    "Folha de rosto Plataforma Brasil",
]


def generate_pre_submission_package(payload, result: dict) -> dict:
    required_docs = list(_BASE_DOCS)

    if payload.involves_minors:
        required_docs += ["TCLE dos responsáveis", "Termo de Assentimento (TALE)"]

    if payload.uses_images:
        required_docs.append("Autorização de uso de imagem/áudio/voz")

    loc = payload.collection_location.lower()
    if any(kw in loc for kw in _INSTITUTION_KEYWORDS):
        required_docs.append("Carta de Anuência institucional")

    collection_method = getattr(payload, "collection_method", "").lower()
    if "online" in collection_method or payload.is_online_research:
        required_docs.append("Convite eletrônico ao participante / formulário online")

    missing: list[str] = []
    total_issues = result.get("validator", {}).get("total_issues", 0)
    if total_issues > 0:
        missing.append(
            f"Corrigir {total_issues} pendência(s) do validador antes da submissão."
        )

    status = "pronto para pré-submissão" if not missing else "incompleto"

    return {
        "status": status,
        "required_documents": required_docs,
        "missing_or_pending": missing,
        "final_instruction": (
            "Revisar todos os documentos com o orientador antes de submeter na Plataforma Brasil."
        ),
    }
