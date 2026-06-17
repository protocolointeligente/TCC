import pandas as pd
from collections import Counter


def generate_bibliometrics(articles):
    df = pd.DataFrame(articles)

    by_year = {}
    by_journal = {}
    by_source = {}

    if not df.empty:
        if "year" in df.columns:
            by_year = df["year"].dropna().value_counts().sort_index().to_dict()
        if "journal" in df.columns:
            by_journal = df["journal"].dropna().value_counts().head(10).to_dict()
        if "source" in df.columns:
            by_source = df["source"].dropna().value_counts().to_dict()

    authors = []
    for article in articles:
        authors.extend(article.get("authors") or [])
    top_authors = dict(Counter(authors).most_common(10))

    return {
        "total_articles": len(articles),
        "articles_by_year": {str(k): int(v) for k, v in by_year.items()},
        "articles_by_journal": {str(k): int(v) for k, v in by_journal.items()},
        "articles_by_source": {str(k): int(v) for k, v in by_source.items()},
        "top_authors": top_authors,
    }
