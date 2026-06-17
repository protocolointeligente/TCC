import os
import json
import shutil

import stripe
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from db_models import Research, UploadedPDF
from models import SearchRequest
from services.openalex import search_openalex
from services.pubmed import search_pubmed
from services.crossref import search_crossref
from services.semantic import search_semantic_scholar
from services.merge import remove_duplicates, rank_articles
from services.bibliometrics import generate_bibliometrics
from services.ai_writer import generate_article_card, generate_review
from services.users import get_or_create_user, can_use_research, increment_usage, update_user_plan
from dependencies import get_current_user
from services.docx_export import export_review_to_docx
from services.pdf_reader import extract_text_from_pdf
from services.reference_checker import check_references
from services.stripe_service import create_checkout_session
from cep_routes import router as cep_router
from cep_advanced_routes import router as cep_advanced_router

app = FastAPI(title="Academia IA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "Academia IA backend online"}


# ---------------------------------------------------------------------------
# Research
# ---------------------------------------------------------------------------

@app.post("/research")
def research(
    request: SearchRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not can_use_research(user):
        raise HTTPException(
            status_code=403,
            detail=f"Limite mensal atingido. Plano atual: {user.plan}.",
        )

    all_articles = []

    for fn, name in [
        (lambda: search_openalex(request.theme, request.start_year, request.end_year, request.min_articles), "OpenAlex"),
        (lambda: search_pubmed(request.theme, request.start_year, request.end_year, request.min_articles), "PubMed"),
        (lambda: search_crossref(request.theme, request.start_year, request.end_year, request.min_articles), "Crossref"),
        (lambda: search_semantic_scholar(request.theme, request.min_articles), "Semantic Scholar"),
    ]:
        try:
            all_articles.extend(fn())
        except Exception as e:
            print(f"Erro {name}:", e)

    unique_articles = remove_duplicates(all_articles)
    ranked_articles = rank_articles(unique_articles)
    selected_articles = ranked_articles[: request.min_articles]

    bibliometrics = generate_bibliometrics(selected_articles)

    cards = []
    for article in selected_articles:
        try:
            card = json.loads(generate_article_card(article))
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
            print("Erro ficha:", e)

    review = generate_review(
        request.theme,
        request.review_type,
        request.course,
        selected_articles,
        cards,
        request.format_style,
    )

    db_research = Research(
        user_id=user.id,
        theme=request.theme,
        course=request.course,
        review_type=request.review_type,
        start_year=request.start_year,
        end_year=request.end_year,
        articles=selected_articles,
        cards=cards,
        bibliometrics=bibliometrics,
        generated_review=review,
    )
    db.add(db_research)
    increment_usage(db, user)
    db.commit()
    db.refresh(db_research)

    return {
        "research_id": db_research.id,
        "theme": request.theme,
        "articles": selected_articles,
        "cards": cards,
        "bibliometrics": bibliometrics,
        "generated_review": review,
        "plan": user.plan,
        "used_this_month": user.used_this_month,
        "monthly_limit": user.monthly_limit,
    }


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

@app.get("/history")
def get_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    researches = (
        db.query(Research)
        .filter(Research.user_id == user.id)
        .order_by(Research.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "theme": r.theme,
            "course": r.course,
            "review_type": r.review_type,
            "created_at": r.created_at,
        }
        for r in researches
    ]


@app.get("/research/{research_id}")
def get_research(
    research_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    research = (
        db.query(Research)
        .filter(Research.id == research_id, Research.user_id == user.id)
        .first()
    )
    if not research:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")
    return {
        "id": research.id,
        "theme": research.theme,
        "course": research.course,
        "review_type": research.review_type,
        "articles": research.articles,
        "cards": research.cards,
        "bibliometrics": research.bibliometrics,
        "generated_review": research.generated_review,
    }


@app.put("/research/{research_id}/text")
def update_research_text(
    research_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    research = (
        db.query(Research)
        .filter(Research.id == research_id, Research.user_id == user.id)
        .first()
    )
    if not research:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")
    research.generated_review = payload.get("generated_review", research.generated_review)
    db.commit()
    return {"status": "Texto atualizado com sucesso."}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@app.get("/research/{research_id}/export-docx")
def export_docx(
    research_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    research = (
        db.query(Research)
        .filter(Research.id == research_id, Research.user_id == user.id)
        .first()
    )
    if not research:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")
    filename = f"tcc_revisao_{research.id}.docx"
    export_review_to_docx(
        title=research.theme,
        review_text=research.generated_review,
        articles=research.articles or [],
        filename=filename,
    )
    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


# ---------------------------------------------------------------------------
# PDF Upload
# ---------------------------------------------------------------------------

@app.post("/upload-pdf")
def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(file_path)

    pdf = UploadedPDF(
        user_id=user.id,
        filename=file.filename,
        extracted_text=extracted_text,
    )
    db.add(pdf)
    db.commit()
    db.refresh(pdf)

    return {
        "pdf_id": pdf.id,
        "filename": pdf.filename,
        "preview": extracted_text[:1500],
    }


# ---------------------------------------------------------------------------
# Reference check
# ---------------------------------------------------------------------------

@app.post("/research/{research_id}/check-references")
def verify_references(
    research_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    research = (
        db.query(Research)
        .filter(Research.id == research_id, Research.user_id == user.id)
        .first()
    )
    if not research:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")
    return check_references(research.articles or [])


# ---------------------------------------------------------------------------
# Billing
# ---------------------------------------------------------------------------

@app.post("/billing/checkout")
def billing_checkout(
    payload: dict,
    user=Depends(get_current_user),
):
    plan = payload.get("plan")
    try:
        checkout_url = create_checkout_session(user.clerk_user_id, plan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"url": checkout_url}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Webhook inválido.")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata") or {}
        clerk_user_id = metadata.get("clerk_user_id")
        plan = metadata.get("plan")
        customer_id = session.get("customer")
        if clerk_user_id and plan:
            update_user_plan(db, clerk_user_id, plan, customer_id)

    return {"received": True}


app.include_router(cep_router)
app.include_router(cep_advanced_router)
