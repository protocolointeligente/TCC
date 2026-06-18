import requests


def search_crossref(theme: str, start_year: int, end_year: int, limit: int = 20):
    url = "https://api.crossref.org/works"
    params = {
        "query": theme,
        "filter": f"from-pub-date:{start_year},until-pub-date:{end_year}",
        "rows": limit,
        "sort": "is-referenced-by-count",
        "order": "desc",
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])

    articles = []
    for item in items:
        authors = []
        for a in item.get("author", []):
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)

        year = None
        date_parts = (
            item.get("published-print", item.get("published-online", {}))
            .get("date-parts", [])
        )
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        articles.append({
            "title": item.get("title", [None])[0],
            "authors": authors,
            "year": year,
            "journal": item.get("container-title", [None])[0],
            "doi": item.get("DOI"),
            "abstract": item.get("abstract"),
            "source": "Crossref",
            "url": item.get("URL"),
            "citations": item.get("is-referenced-by-count", 0),
        })
    return articles
