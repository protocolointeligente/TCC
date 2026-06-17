from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    theme: str
    course: str
    review_type: str
    start_year: int
    end_year: int
    min_articles: int
    language: str = "pt"
    format_style: str = "ABNT"


class Article(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]
    abstract: Optional[str]
    source: str
    url: Optional[str]
    citations: Optional[int] = 0


class ArticleCard(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]
    objective: str
    methodology: str
    results: str
    conclusion: str
    relevance: str


class ReviewResponse(BaseModel):
    theme: str
    articles: List[Article]
    cards: List[ArticleCard]
    bibliometrics: dict
    generated_review: str
