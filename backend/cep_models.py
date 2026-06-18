from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class EthicsProject(Base):
    __tablename__ = "ethics_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    course = Column(String)
    area = Column(String)
    study_type = Column(String)
    target_population = Column(String)
    age_group = Column(String)
    collection_location = Column(String)
    involves_minors = Column(String, default="no")
    uses_images = Column(String, default="no")
    collects_sensitive_data = Column(String, default="no")
    is_online_research = Column(String, default="no")
    has_physical_intervention = Column(String, default="no")
    general_objective = Column(Text)
    specific_objectives = Column(JSON)
    methodology = Column(Text)
    inclusion_criteria = Column(Text)
    exclusion_criteria = Column(Text)
    risks = Column(Text)
    risk_minimization = Column(Text)
    benefits = Column(Text)
    suggested_instruments = Column(JSON)
    ethical_checklist = Column(JSON)
    warnings = Column(JSON)
    generated_project = Column(Text)
    tcle = Column(Text)
    tale = Column(Text)
    assent_term = Column(Text)
    institution_letter = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
