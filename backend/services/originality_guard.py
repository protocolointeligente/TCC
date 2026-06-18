_GENERIC_PHRASES = [
    "nos dias atuais",
    "é de suma importância",
    "desde os primórdios",
    "a sociedade contemporânea",
    "o presente trabalho tem como objetivo",
    "é notório que",
    "diante do exposto",
    "em virtude do exposto acima",
    "com base no exposto",
    "neste sentido, faz-se necessário",
]


def originality_checklist(text: str, references: list) -> dict:
    warnings: list[str] = []

    word_count = len(text.split())
    if word_count < 300:
        warnings.append("Texto muito curto para avaliação acadêmica consistente.")

    if not references:
        warnings.append("Texto sem referências vinculadas.")

    found_phrases = [p for p in _GENERIC_PHRASES if p in text.lower()]
    if found_phrases:
        warnings.append(f"Expressões genéricas encontradas: {found_phrases}")

    if text.count("(") < 2 and word_count > 500:
        warnings.append("Poucas citações aparentes para o tamanho do texto.")

    paragraph_count = len([p for p in text.split("\n\n") if p.strip()])
    if paragraph_count > 3 and text.count("portanto") + text.count("assim") + text.count("logo") > paragraph_count:
        warnings.append("Conectivos conclusivos repetidos — varie a estrutura dos parágrafos.")

    status = "revisar" if warnings else "adequado para revisão humana"
    return {
        "status": status,
        "word_count": word_count,
        "warnings": warnings,
        "recommendation": (
            "O aluno deve revisar, inserir leitura própria, conferir citações "
            "e validar com o orientador."
        ),
    }
