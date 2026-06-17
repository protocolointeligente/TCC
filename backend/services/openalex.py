import requests


def search_openalex(theme: str, start_year: int, end_year: int, limit: int = 20):
    url = "https://api.openalex.org/works"
    params = {
        "search": theme,
        "filter": f"from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31",
        "per-page": limit,
        "sort": "cited_by_count:desc",
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("results", []):
        authors = [
            a["author"]["display_name"]
            for a in item.get("authorships", [])
            if a.get("author")
        ]
        articles.append({
            "title": item.get("title"),
            "authors": authors,
            "year": item.get("publication_year"),
            "journal": (
                item.get("primary_location", {}).get("source", {}).get("display_name")
                if item.get("primary_location")
                else None
            ),
            "doi": item.get("doi"),
            "abstract": _reconstruct_abstract(item.get("abstract_inverted_index")),
            "source": "OpenAlex",
            "url": item.get("id"),
            "citations": item.get("cited_by_count", 0),
        })
    return articles


def _reconstruct_abstract(inverted_index):
    if not inverted_index:
        return None
    words = []
    for word, positions in inverted_index.items():
        for position in positions:
            words.append((position, word))
    words = sorted(words)
    return " ".join([word for _, word in words])
