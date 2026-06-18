from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from database import Base


class AdvancedEthicsProject(Base):
    __tablename__ = "advanced_ethics_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Input snapshot
    title = Column(String, nullable=False)
    course = Column(String)
    area = Column(String)
    study_type = Column(String)
    institution = Column(String)
    advisor = Column(String)
    target_population = Column(String)
    age_group = Column(String)
    expected_sample = Column(String)
    collection_location = Column(String)
    collection_method = Column(String)
    general_objective = Column(Text)
    specific_objectives = Column(JSON)
    methodology_summary = Column(Text)
    research_months = Column(Integer)

    # Ethics flags
    involves_minors = Column(Boolean, default=False)
    uses_images = Column(Boolean, default=False)
    collects_sensitive_data = Column(Boolean, default=False)
    is_online_research = Column(Boolean, default=False)
    has_physical_intervention = Column(Boolean, default=False)
    involves_vulnerable_population = Column(Boolean, default=False)

    # Results — structured
    validator_issues = Column(JSON)
    risk = Column(JSON)
    instruments = Column(JSON)
    objective_matrix = Column(JSON)
    statistics = Column(JSON)
    schedule = Column(JSON)
    budget = Column(JSON)
    attachments = Column(JSON)
    cep_pendency_simulator = Column(JSON)
    ethics_resolution_checks = Column(JSON)
    methodological_coherence = Column(JSON)
    pre_submission_package = Column(JSON)

    # Results — text
    smart_tcle = Column(Text)
    plataforma_brasil_tips = Column(Text)
    orientador_opinion = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
