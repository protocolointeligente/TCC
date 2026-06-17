from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from cep_advanced_schemas import AdvancedCepRequest
from advanced_cep_models import AdvancedEthicsProject
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
from services.cep_advanced_docx_export import export_advanced_cep_to_docx

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

    # 2. Instruments
    instruments = filter_instruments(
        area=payload.area,
        age_group=payload.age_group,
        general_objective=payload.general_objective,
        specific_objectives=payload.specific_objectives,
        db=db,
    )

    # 3. Objective matrix
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

    # 14. Orientador opinion
    orientador_opinion = None
    if payload.generate_orientador_opinion:
        orientador_opinion = generate_orientador_opinion(payload, issues, risk)

    result = {
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

    # ── Persist to PostgreSQL ──────────────────────────────────────────────
    project = AdvancedEthicsProject(
        user_id=user.id,
        title=payload.title,
        course=payload.course,
        area=payload.area,
        study_type=payload.study_type,
        institution=payload.institution,
        advisor=payload.advisor,
        target_population=payload.target_population,
        age_group=payload.age_group,
        expected_sample=payload.expected_sample,
        collection_location=payload.collection_location,
        collection_method=payload.collection_method,
        general_objective=payload.general_objective,
        specific_objectives=payload.specific_objectives,
        methodology_summary=payload.methodology_summary,
        research_months=payload.research_months,
        involves_minors=payload.involves_minors,
        uses_images=payload.uses_images,
        collects_sensitive_data=payload.collects_sensitive_data,
        is_online_research=payload.is_online_research,
        has_physical_intervention=payload.has_physical_intervention,
        involves_vulnerable_population=payload.involves_vulnerable_population,
        validator_issues=issues,
        risk=risk,
        instruments=instruments,
        objective_matrix=matrix,
        statistics=statistics,
        schedule=schedule,
        budget=budget,
        attachments=attachments,
        cep_pendency_simulator=pendencies,
        ethics_resolution_checks=resolution_checks,
        methodological_coherence=coherence,
        pre_submission_package=pre_submission,
        smart_tcle=smart_tcle,
        plataforma_brasil_tips=plataforma_checklist.get("plataforma_brasil_tips"),
        orientador_opinion=orientador_opinion,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {"project_id": project.id, **result}


@router.get("/projects")
def list_advanced_projects(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    projects = (
        db.query(AdvancedEthicsProject)
        .filter(AdvancedEthicsProject.user_id == user.id)
        .order_by(AdvancedEthicsProject.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "title": p.title,
            "course": p.course,
            "study_type": p.study_type,
            "risk_level": (p.risk or {}).get("risk_level"),
            "created_at": p.created_at,
        }
        for p in projects
    ]


@router.get("/project/{project_id}")
def get_advanced_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = (
        db.query(AdvancedEthicsProject)
        .filter(
            AdvancedEthicsProject.id == project_id,
            AdvancedEthicsProject.user_id == user.id,
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    return {
        "id": project.id,
        "title": project.title,
        "course": project.course,
        "area": project.area,
        "study_type": project.study_type,
        "institution": project.institution,
        "advisor": project.advisor,
        "target_population": project.target_population,
        "age_group": project.age_group,
        "general_objective": project.general_objective,
        "specific_objectives": project.specific_objectives,
        "methodology_summary": project.methodology_summary,
        "created_at": project.created_at,
        "validator": {
            "issues": project.validator_issues or [],
            "total_issues": len(project.validator_issues or []),
        },
        "risk": project.risk,
        "instruments": project.instruments,
        "objective_matrix": project.objective_matrix,
        "statistics": project.statistics,
        "smart_tcle": project.smart_tcle,
        "plataforma_brasil": {
            "plataforma_brasil_tips": project.plataforma_brasil_tips,
        },
        "schedule": project.schedule,
        "budget": project.budget,
        "attachments": project.attachments,
        "cep_pendency_simulator": project.cep_pendency_simulator,
        "ethics_resolution_checks": project.ethics_resolution_checks,
        "methodological_coherence": project.methodological_coherence,
        "pre_submission_package": project.pre_submission_package,
        "orientador_opinion": project.orientador_opinion,
    }


@router.get("/project/{project_id}/export-docx")
def export_advanced_docx(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = (
        db.query(AdvancedEthicsProject)
        .filter(
            AdvancedEthicsProject.id == project_id,
            AdvancedEthicsProject.user_id == user.id,
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    result = {
        "risk": project.risk or {},
        "validator": {"issues": project.validator_issues or []},
        "ethics_resolution_checks": project.ethics_resolution_checks or [],
        "methodological_coherence": project.methodological_coherence or {},
        "objective_matrix": project.objective_matrix or [],
        "instruments": project.instruments or [],
        "statistics": project.statistics or {},
        "smart_tcle": project.smart_tcle,
        "plataforma_brasil": {"plataforma_brasil_tips": project.plataforma_brasil_tips},
        "schedule": project.schedule or [],
        "budget": project.budget or [],
        "attachments": project.attachments or {},
        "cep_pendency_simulator": project.cep_pendency_simulator or [],
        "pre_submission_package": project.pre_submission_package or {},
        "orientador_opinion": project.orientador_opinion,
    }

    filename = f"cep_avancado_{project.id}.docx"
    export_advanced_cep_to_docx(project, result, filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )
