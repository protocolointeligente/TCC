from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    clerk_user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    plan = Column(String, default="free")
    monthly_limit = Column(Integer, default=3)
    used_this_month = Column(Integer, default=0)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Research(Base):
    __tablename__ = "researches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme = Column(String, nullable=False)
    course = Column(String)
    review_type = Column(String)
    start_year = Column(Integer)
    end_year = Column(Integer)
    articles = Column(JSON)
    cards = Column(JSON)
    bibliometrics = Column(JSON)
    generated_review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UploadedPDF(Base):
    __tablename__ = "uploaded_pdfs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    extracted_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
