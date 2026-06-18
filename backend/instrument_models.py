from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from database import Base


class ResearchInstrument(Base):
    __tablename__ = "research_instruments"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    full_name = Column(String)
    area = Column(String)
    construct = Column(String)
    objective_keywords = Column(JSON)
    original_reference = Column(JSON)
    brazilian_validation_reference = Column(JSON)
    validated_population_brazil = Column(Text)
    license_use = Column(Text)
    scoring = Column(Text)
    application_mode = Column(JSON)
    ethical_notes = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
