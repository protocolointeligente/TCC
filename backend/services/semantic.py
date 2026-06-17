import requests


def search_semantic_scholar(theme: str, limit: int = 20):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": theme,
        "limit": limit,
        "fields": "title,authors,year,venue,abstract,externalIds,citationCount,url",
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json().get("data", [])

    articles = []
    for item in data:
        external = item.get("externalIds") or {}
        articles.append({
            "title": item.get("title"),
            "authors": [a.get("name") for a in item.get("authors", [])],
            "year": item.get("year"),
            "journal": item.get("venue"),
            "doi": external.get("DOI"),
            "abstract": item.get("abstract"),
            "source": "Semantic Scholar",
            "url": item.get("url"),
            "citations": item.get("citationCount", 0),
        })
    return articles
