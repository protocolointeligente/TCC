from pydantic import BaseModel
from typing import List, Optional


class AdvancedCepRequest(BaseModel):
    # Project identity
    title: str
    course: str
    area: str
    study_type: str
    institution: str
    advisor: str

    # Population
    target_population: str
    age_group: str
    expected_sample: str
    sampling_method: Optional[str] = None

    # Collection
    collection_location: str
    collection_method: str
    estimated_duration: Optional[str] = None

    # Ethics flags
    involves_minors: bool = False
    uses_images: bool = False
    collects_sensitive_data: bool = False
    is_online_research: bool = False
    has_physical_intervention: bool = False
    involves_vulnerable_population: bool = False

    # Research design
    general_objective: str
    specific_objectives: List[str]
    methodology_summary: str
    variables: Optional[List[str]] = []

    # Budget / schedule
    budget_items: Optional[List[str]] = []
    research_months: Optional[int] = 12

    # Modes
    generate_orientador_opinion: bool = False
