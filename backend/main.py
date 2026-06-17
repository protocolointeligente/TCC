import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest
from services.openalex import search_openalex
from services.pubmed import search_pubmed
from services.crossref import search_crossref
from services.semantic import search_semantic_scholar
from services.merge import remove_duplicates, rank_articles
from services.bibliometrics import generate_bibliometrics
from services.ai_writer import generate_article_card, generate_review

app = FastAPI(title="Academia IA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "Academia IA backend online"}


@app.post("/research")
def research(request: SearchRequest):
    all_articles = []

    try:
        all_articles.extend(
            search_openalex(request.theme, request.start_year, request.end_year, request.min_articles)
        )
    except Exception as e:
        print("Erro OpenAlex:", e)

    try:
        all_articles.extend(
            search_pubmed(request.theme, request.start_year, request.end_year, request.min_articles)
        )
    except Exception as e:
        print("Erro PubMed:", e)

    try:
        all_articles.extend(
            search_crossref(request.theme, request.start_year, request.end_year, request.min_articles)
        )
    except Exception as e:
        print("Erro Crossref:", e)

    try:
        all_articles.extend(
            search_semantic_scholar(request.theme, request.min_articles)
        )
    except Exception as e:
        print("Erro Semantic Scholar:", e)

    unique_articles = remove_duplicates(all_articles)
    ranked_articles = rank_articles(unique_articles)
    selected_articles = ranked_articles[: request.min_articles]

    bibliometrics = generate_bibliometrics(selected_articles)

    cards = []
    for article in selected_articles:
        try:
            card_json = generate_article_card(article)
            card = json.loads(card_json)
            cards.append({
                "title": article.get("title"),
                "authors": article.get("authors"),
                "year": article.get("year"),
                "journal": article.get("journal"),
                "doi": article.get("doi"),
                "objective": card.get("objective"),
                "methodology": card.get("methodology"),
                "results": card.get("results"),
                "conclusion": card.get("conclusion"),
                "relevance": card.get("relevance"),
            })
        except Exception as e:
            print("Erro IA ficha:", e)

    review = generate_review(
        request.theme,
        request.review_type,
        request.course,
        selected_articles,
        cards,
        request.format_style,
    )

    return {
        "theme": request.theme,
        "articles": selected_articles,
        "cards": cards,
        "bibliometrics": bibliometrics,
        "generated_review": review,
    }
