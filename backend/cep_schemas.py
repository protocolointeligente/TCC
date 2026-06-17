from pydantic import BaseModel
from typing import List, Optional


class EthicsProjectRequest(BaseModel):
    title: str
    course: str
    area: str
    study_type: str
    target_population: str
    age_group: str
    collection_location: str
    involves_minors: bool = False
    uses_images: bool = False
    collects_sensitive_data: bool = False
    is_online_research: bool = False
    has_physical_intervention: bool = False
    general_objective: str
    specific_objectives: List[str]
    methodology_summary: str
    expected_sample: Optional[str] = None
    instruments_needed: Optional[List[str]] = []


class EthicsProjectUpdateText(BaseModel):
    generated_project: str
    tcle: Optional[str] = None
    tale: Optional[str] = None
    assent_term: Optional[str] = None
    institution_letter: Optional[str] = None
