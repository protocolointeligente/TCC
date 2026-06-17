def normalize_title(title: str):
    if not title:
        return ""
    return title.lower().strip().replace(".", "").replace(",", "")


def remove_duplicates(articles):
    seen = set()
    unique = []
    for article in articles:
        key = article.get("doi") or normalize_title(article.get("title"))
        if key and key not in seen:
            seen.add(key)
            unique.append(article)
    return unique


def rank_articles(articles):
    def score(article):
        citation_score = article.get("citations") or 0
        abstract_score = 20 if article.get("abstract") else 0
        doi_score = 10 if article.get("doi") else 0
        year_score = article.get("year") or 0
        return citation_score + abstract_score + doi_score + (year_score / 100)

    return sorted(articles, key=score, reverse=True)
