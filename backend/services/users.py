from sqlalchemy.orm import Session
from db_models import User

PLAN_LIMITS = {
    "free": 3,
    "basic": 30,
    "pro": 200,
}


def get_or_create_user(db: Session, clerk_user_id: str, email: str | None = None):
    user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    if user:
        return user
    user = User(
        clerk_user_id=clerk_user_id,
        email=email,
        plan="free",
        monthly_limit=PLAN_LIMITS["free"],
        used_this_month=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def can_use_research(user: User) -> bool:
    return user.used_this_month < user.monthly_limit


def increment_usage(db: Session, user: User) -> User:
    user.used_this_month += 1
    db.commit()
    db.refresh(user)
    return user


def update_user_plan(
    db: Session,
    clerk_user_id: str,
    plan: str,
    stripe_customer_id: str | None = None,
) -> User | None:
    user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    if not user:
        return None
    user.plan = plan
    user.monthly_limit = PLAN_LIMITS.get(plan, 3)
    if stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
    db.commit()
    db.refresh(user)
    return user
