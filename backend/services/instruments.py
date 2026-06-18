from services.instruments_database import INSTRUMENT_DATABASE

_FALLBACK = {
    "id": "manual_review_required",
    "name": "Revisão manual necessária",
    "full_name": "Instrumento não definido automaticamente",
    "area": "Indefinida",
    "construct": "Indefinido",
    "validated_population_brazil": "Não identificado.",
    "license_use": "Verificar instrumento adequado, validação brasileira e autorização de uso.",
    "scoring": "Não aplicável.",
    "ethical_notes": [
        "O sistema não encontrou instrumento compatível com segurança.",
        "Exigir busca manual em bases científicas.",
    ],
}


def suggest_instruments(
    general_objective: str,
    specific_objectives: list[str],
    db=None,
) -> list[dict]:
    """Return instruments matching the research objectives.

    When a SQLAlchemy session is provided, queries the database so edits
    made via the admin panel take effect without a code deploy.
    Falls back to the in-memory list when db is None (e.g. during tests).
    """
    if db is not None:
        return _suggest_from_db(db, general_objective, specific_objectives)
    return _suggest_from_memory(general_objective, specific_objectives)


# ---------------------------------------------------------------------------
# DB-backed search
# ---------------------------------------------------------------------------

def _suggest_from_db(db, general_objective: str, specific_objectives: list[str]) -> list[dict]:
    from instrument_models import ResearchInstrument

    text = (general_objective + " " + " ".join(specific_objectives)).lower()
    all_instruments = (
        db.query(ResearchInstrument)
        .filter(ResearchInstrument.is_active.is_(True))
        .all()
    )
    matches = [
        _to_dict(inst)
        for inst in all_instruments
        if any(kw.lower() in text for kw in (inst.objective_keywords or []))
    ]
    return matches if matches else [_FALLBACK]


def _to_dict(inst) -> dict:
    return {
        "id": inst.id,
        "name": inst.name,
        "full_name": inst.full_name,
        "area": inst.area,
        "construct": inst.construct,
        "original_reference": inst.original_reference,
        "brazilian_validation_reference": inst.brazilian_validation_reference,
        "validated_population_brazil": inst.validated_population_brazil,
        "license_use": inst.license_use,
        "scoring": inst.scoring,
        "application_mode": inst.application_mode,
        "ethical_notes": inst.ethical_notes,
    }


# ---------------------------------------------------------------------------
# In-memory fallback
# ---------------------------------------------------------------------------

def _suggest_from_memory(general_objective: str, specific_objectives: list[str]) -> list[dict]:
    text = (general_objective + " " + " ".join(specific_objectives)).lower()
    matches = [
        {k: v for k, v in inst.items() if k != "objective_keywords"}
        for inst in INSTRUMENT_DATABASE
        if any(kw.lower() in text for kw in inst.get("objective_keywords", []))
    ]
    return matches if matches else [_FALLBACK]
