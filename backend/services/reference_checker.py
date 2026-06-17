import requests


def _verify_doi(doi: str) -> dict:
    if not doi:
        return {"valid": False, "reason": "DOI ausente."}
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json().get("message", {})
            return {
                "valid": True,
                "title": (data.get("title") or [None])[0],
                "publisher": data.get("publisher"),
                "year": (data.get("published", {}).get("date-parts") or [[None]])[0][0],
            }
        return {"valid": False, "reason": "DOI não encontrado no Crossref."}
    except Exception as e:
        return {"valid": False, "reason": str(e)}


def check_references(articles: list[dict]) -> list[dict]:
    return [
        {
            "title": article.get("title"),
            "doi": article.get("doi"),
            "verification": _verify_doi(article.get("doi")),
        }
        for article in articles
    ]
