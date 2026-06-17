import requests
import xml.etree.ElementTree as ET


def search_pubmed(theme: str, start_year: int, end_year: int, limit: int = 20):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": f'{theme} AND ("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])',
        "retmode": "json",
        "retmax": limit,
    }
    search_response = requests.get(search_url, params=search_params, timeout=20)
    search_response.raise_for_status()
    ids = search_response.json()["esearchresult"].get("idlist", [])
    if not ids:
        return []

    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
    }
    fetch_response = requests.get(fetch_url, params=fetch_params, timeout=20)
    fetch_response.raise_for_status()
    root = ET.fromstring(fetch_response.text)

    articles = []
    for article in root.findall(".//PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        abstract_el = article.find(".//AbstractText")
        journal_el = article.find(".//Journal/Title")
        year_el = article.find(".//PubDate/Year")
        doi_el = article.find(".//ArticleId[@IdType='doi']")

        authors = []
        for author in article.findall(".//Author"):
            lastname = author.findtext("LastName")
            forename = author.findtext("ForeName")
            if lastname:
                authors.append(f"{forename or ''} {lastname}".strip())

        articles.append({
            "title": title_el.text if title_el is not None else None,
            "authors": authors,
            "year": int(year_el.text) if year_el is not None and year_el.text else None,
            "journal": journal_el.text if journal_el is not None else None,
            "doi": doi_el.text if doi_el is not None else None,
            "abstract": abstract_el.text if abstract_el is not None else None,
            "source": "PubMed",
            "url": None,
            "citations": 0,
        })
    return articles
