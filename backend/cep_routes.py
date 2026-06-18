from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from dependencies import get_current_user
from cep_models import EthicsProject
from cep_schemas import EthicsProjectRequest, EthicsProjectUpdateText
from instrument_models import ResearchInstrument
from services.ethics_engine import classify_risk, generate_ethics_warnings, generate_ethical_checklist
from services.instruments import suggest_instruments
from services.cep_writer import generate_cep_documents, split_cep_response
from services.cep_docx_export import export_cep_project_to_docx

router = APIRouter(prefix="/cep", tags=["CEP / Plataforma Brasil"])


class InstrumentUpdate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    area: Optional[str] = None
    construct: Optional[str] = None
    objective_keywords: Optional[list[str]] = None
    validated_population_brazil: Optional[str] = None
    license_use: Optional[str] = None
    scoring: Optional[str] = None
    ethical_notes: Optional[list[str]] = None
    is_active: Optional[bool] = None


@router.post("/project")
def create_cep_project(
    payload: EthicsProjectRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    risk_analysis = classify_risk(payload)
    warnings = generate_ethics_warnings(payload)
    checklist = generate_ethical_checklist(payload)
    instruments = suggest_instruments(payload.general_objective, payload.specific_objectives, db=db)

    ai_response = generate_cep_documents(
        payload=payload,
        risk_analysis=risk_analysis,
        instruments=instruments,
        warnings=warnings,
    )
    sections = split_cep_response(ai_response)

    project = EthicsProject(
        user_id=user.id,
        title=payload.title,
        course=payload.course,
        area=payload.area,
        study_type=payload.study_type,
        target_population=payload.target_population,
        age_group=payload.age_group,
        collection_location=payload.collection_location,
        involves_minors="yes" if payload.involves_minors else "no",
        uses_images="yes" if payload.uses_images else "no",
        collects_sensitive_data="yes" if payload.collects_sensitive_data else "no",
        is_online_research="yes" if payload.is_online_research else "no",
        has_physical_intervention="yes" if payload.has_physical_intervention else "no",
        general_objective=payload.general_objective,
        specific_objectives=payload.specific_objectives,
        methodology=payload.methodology_summary,
        suggested_instruments=instruments,
        ethical_checklist=checklist,
        warnings=warnings,
        risks="\n".join(risk_analysis["identified_risks"]),
        generated_project=sections["generated_project"],
        tcle=sections["tcle"],
        tale=sections["tale"],
        assent_term=sections["assent_term"],
        institution_letter=sections["institution_letter"],
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "project_id": project.id,
        "risk_analysis": risk_analysis,
        "warnings": warnings,
        "ethical_checklist": checklist,
        "suggested_instruments": instruments,
        "generated_project": project.generated_project,
        "tcle": project.tcle,
        "tale": project.tale,
        "assent_term": project.assent_term,
        "institution_letter": project.institution_letter,
    }


@router.get("/projects")
def list_cep_projects(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    projects = (
        db.query(EthicsProject)
        .filter(EthicsProject.user_id == user.id)
        .order_by(EthicsProject.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "title": p.title,
            "course": p.course,
            "study_type": p.study_type,
            "created_at": p.created_at,
        }
        for p in projects
    ]


@router.get("/project/{project_id}")
def get_cep_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = (
        db.query(EthicsProject)
        .filter(EthicsProject.id == project_id, EthicsProject.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto CEP não encontrado.")
    return {
        "id": project.id,
        "title": project.title,
        "course": project.course,
        "area": project.area,
        "study_type": project.study_type,
        "target_population": project.target_population,
        "age_group": project.age_group,
        "collection_location": project.collection_location,
        "suggested_instruments": project.suggested_instruments,
        "ethical_checklist": project.ethical_checklist,
        "warnings": project.warnings,
        "generated_project": project.generated_project,
        "tcle": project.tcle,
        "tale": project.tale,
        "assent_term": project.assent_term,
        "institution_letter": project.institution_letter,
    }


@router.put("/project/{project_id}/text")
def update_cep_project_text(
    project_id: int,
    payload: EthicsProjectUpdateText,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = (
        db.query(EthicsProject)
        .filter(EthicsProject.id == project_id, EthicsProject.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto CEP não encontrado.")
    project.generated_project = payload.generated_project
    if payload.tcle is not None:
        project.tcle = payload.tcle
    if payload.tale is not None:
        project.tale = payload.tale
    if payload.assent_term is not None:
        project.assent_term = payload.assent_term
    if payload.institution_letter is not None:
        project.institution_letter = payload.institution_letter
    db.commit()
    return {"status": "Projeto CEP atualizado com sucesso."}


@router.get("/project/{project_id}/export-docx")
def export_cep_docx(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = (
        db.query(EthicsProject)
        .filter(EthicsProject.id == project_id, EthicsProject.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Projeto CEP não encontrado.")
    filename = f"projeto_cep_{project.id}.docx"
    export_cep_project_to_docx(project, filename)
    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


# ---------------------------------------------------------------------------
# Instrument admin endpoints
# ---------------------------------------------------------------------------

@router.get("/instruments")
def list_instruments(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    instruments = (
        db.query(ResearchInstrument)
        .order_by(ResearchInstrument.name)
        .all()
    )
    return [
        {
            "id": inst.id,
            "name": inst.name,
            "full_name": inst.full_name,
            "area": inst.area,
            "construct": inst.construct,
            "objective_keywords": inst.objective_keywords,
            "validated_population_brazil": inst.validated_population_brazil,
            "license_use": inst.license_use,
            "scoring": inst.scoring,
            "application_mode": inst.application_mode,
            "ethical_notes": inst.ethical_notes,
            "original_reference": inst.original_reference,
            "brazilian_validation_reference": inst.brazilian_validation_reference,
            "is_active": inst.is_active,
        }
        for inst in instruments
    ]


@router.patch("/instruments/{instrument_id}")
def update_instrument(
    instrument_id: str,
    payload: InstrumentUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    instrument = db.query(ResearchInstrument).filter(ResearchInstrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrumento não encontrado.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(instrument, field, value)
    db.commit()
    db.refresh(instrument)
    return {"status": "Instrumento atualizado.", "id": instrument.id}
