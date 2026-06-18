def _format_author_abnt(author: str) -> str:
    parts = author.strip().split()
    if len(parts) < 2:
        return author.upper()
    last_name = parts[-1].upper()
    initials = " ".join(parts[:-1])
    return f"{last_name}, {initials}"


def generate_abnt_reference(article: dict) -> str:
    authors = article.get("authors") or []
    title = article.get("title") or "Título não informado"
    journal = article.get("journal") or "Periódico não informado"
    year = article.get("year") or "s.d."
    doi = article.get("doi")

    if authors:
        formatted = "; ".join([_format_author_abnt(a) for a in authors[:3]])
        if len(authors) > 3:
            formatted += " et al."
    else:
        formatted = "AUTORIA NÃO INFORMADA"

    reference = f"{formatted}. {title}. {journal}, {year}."
    if doi:
        reference += f" DOI: {doi}."
    return reference


def generate_abnt_references(articles: list[dict]) -> list[str]:
    return sorted(generate_abnt_reference(a) for a in articles)
