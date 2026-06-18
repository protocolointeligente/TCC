from sqlalchemy.orm import Session

CREDIT_COSTS: dict[str, int] = {
    "search_articles": 5,
    "article_card": 2,
    "simple_review": 25,
    "complete_tcc": 120,
    "cep_project": 60,
    "cep_advanced_analysis": 35,
    "docx_export": 5,
    "bibliometrics": 15,
}

CREDIT_PACKAGES: dict[str, dict] = {
    "starter": {"price": 29, "credits": 50},
    "academico": {"price": 59, "credits": 140},
    "tcc_pro": {"price": 97, "credits": 300},
    "cep_completo": {"price": 87, "credits": 250},
    "combo": {"price": 147, "credits": 500},
    "orientador": {"price": 197, "credits": 800},
}


def calculate_credit_cost(action: str, quantity: int = 1) -> int:
    return CREDIT_COSTS.get(action, 0) * quantity


def has_enough_credits(user, required: int) -> bool:
    credits = getattr(user, "credits", None)
    if credits is None:
        return True  # credits column not yet migrated — skip check
    return credits >= required


def debit_credits(db: Session, user, amount: int, description: str) -> dict:
    if not hasattr(user, "credits") or user.credits is None:
        return {"remaining_credits": None, "debited": 0, "description": description}
    if user.credits < amount:
        raise ValueError("Créditos insuficientes.")
    user.credits -= amount
    db.commit()
    db.refresh(user)
    return {
        "remaining_credits": user.credits,
        "debited": amount,
        "description": description,
    }
