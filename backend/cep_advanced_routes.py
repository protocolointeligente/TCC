from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from cep_advanced_schemas import AdvancedCepRequest
from services.cep_validator import validate_cep_project, classify_ethics_risk
from services.advanced_instruments import filter_instruments
from services.tcle_generator import generate_smart_tcle
from services.plataforma_brasil_checklist import generate_plataforma_brasil_checklist
from services.objective_matrix import generate_objective_matrix
from services.statistics_advisor import suggest_statistics
from services.schedule_budget import generate_schedule, generate_budget
from services.attachment_library import generate_attachment_library, generate_attachment_templates
from services.orientador_mode import generate_orientador_opinion
from services.cep_pending_simulator import simulate_cep_pendencies
from services.ethics_resolution_checker import check_ethics_resolutions
from services.methodological_coherence import validate_methodological_coherence
from services.cep_response_templates import suggest_response_template
from services.pre_submission_package import generate_pre_submission_package

router = APIRouter(prefix="/cep-advanced", tags=["CEP Avançado"])


@router.post("/analyze")
def analyze_advanced_cep(
    payload: AdvancedCepRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 1. Validation + risk
    issues = validate_cep_project(payload)
    risk = classify_ethics_risk(payload)

    # 2. Instruments (DB-backed with area/age filtering)
    instruments = filter_instruments(
        area=payload.area,
        age_group=payload.age_group,
        general_objective=payload.general_objective,
        specific_objectives=payload.specific_objectives,
        db=db,
    )

    # 3. Objective → instrument → variable → analysis matrix
    matrix = generate_objective_matrix(payload, instruments)

    # 4. Statistics advisor
    statistics = suggest_statistics(payload.study_type, payload.variables or [], instruments)

    # 5. Smart TCLE
    smart_tcle = generate_smart_tcle(payload)

    # 6. Plataforma Brasil checklist
    plataforma_checklist = generate_plataforma_brasil_checklist(payload)

    # 7. Schedule + budget
    schedule = generate_schedule(payload.research_months or 12)
    budget = generate_budget(payload.budget_items or [])

    # 8. Attachment library
    attachments = generate_attachment_library(payload)
    template_names = [a["name"] for a in attachments["required"] if a.get("template_available")]
    attachment_templates = generate_attachment_templates(template_names)

    # 9. Pendency simulation
    pendencies = simulate_cep_pendencies(payload, issues, risk)

    # 10. Ethics resolution checks
    resolution_checks = check_ethics_resolutions(payload)

    # 11. Methodological coherence
    coherence = validate_methodological_coherence(payload, instruments, matrix, statistics)

    # 12. Pendency response templates
    pendency_responses = [
        {
            "pendency": p["reason"],
            "suggested_response": suggest_response_template(p["reason"]),
        }
        for p in pendencies
    ]

    # 13. Pre-submission package
    temporary_result = {"validator": {"issues": issues, "total_issues": len(issues)}}
    pre_submission = generate_pre_submission_package(payload, temporary_result)

    # 14. Orientador opinion (optional, expensive — AI call)
    orientador_opinion = None
    if payload.generate_orientador_opinion:
        orientador_opinion = generate_orientador_opinion(payload, issues, risk)

    return {
        "validator": {
            "issues": issues,
            "total_issues": len(issues),
            "errors": sum(1 for i in issues if i["severity"] == "error"),
            "warnings": sum(1 for i in issues if i["severity"] == "warning"),
        },
        "risk": risk,
        "instruments": instruments,
        "objective_matrix": matrix,
        "statistics": statistics,
        "smart_tcle": smart_tcle,
        "plataforma_brasil": plataforma_checklist,
        "schedule": schedule,
        "budget": budget,
        "attachments": attachments,
        "attachment_templates": attachment_templates,
        "cep_pendency_simulator": pendencies,
        "ethics_resolution_checks": resolution_checks,
        "methodological_coherence": coherence,
        "pendency_response_templates": pendency_responses,
        "pre_submission_package": pre_submission,
        "orientador_opinion": orientador_opinion,
    }
