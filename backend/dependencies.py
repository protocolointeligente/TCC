from fastapi import Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from services.users import get_or_create_user


def get_current_user(
    db: Session = Depends(get_db),
    x_clerk_user_id: str = Header(...),
    x_user_email: str | None = Header(default=None),
):
    return get_or_create_user(db, x_clerk_user_id, x_user_email)
