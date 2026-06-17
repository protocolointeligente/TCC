"""
Filter instruments from the DB-backed table (or in-memory fallback) using
area, age_group, and objective keywords — richer than the base suggest_instruments.
"""
from services.instruments import _suggest_from_db, _suggest_from_memory, _FALLBACK


_AREA_ALIASES: dict[str, list[str]] = {
    "psicologia": ["psicologia", "psico", "saúde mental", "mental health"],
    "educação": ["educação", "educacao", "ensino", "aprendizagem", "escola"],
    "saúde": ["saúde", "saude", "saúde coletiva", "enfermagem", "medicina", "fisioterapia"],
    "educação física": ["educação física", "educacao fisica", "esporte", "atividade física", "exercício"],
    "nutrição": ["nutrição", "nutricao", "alimentação", "dieta"],
}

_AGE_KEYWORDS: dict[str, list[str]] = {
    "crianças": ["criança", "infantil", "child", "infância"],
    "adolescentes": ["adolescente", "teen", "jovem", "juvenile"],
    "adultos": ["adulto", "adult"],
    "idosos": ["idoso", "elder", "envelhecimento", "aging", "terceira idade"],
    "todos": [],
}


def _area_matches(instrument: dict, area: str) -> bool:
    inst_area = (instrument.get("area") or "").lower()
    for alias in _AREA_ALIASES.get(area.lower(), [area.lower()]):
        if alias in inst_area:
            return True
    return True  # do not exclude if area mapping unknown


def _age_matches(instrument: dict, age_group: str) -> bool:
    pop = (instrument.get("validated_population_brazil") or "").lower()
    keywords = _AGE_KEYWORDS.get(age_group.lower(), [])
    if not keywords:
        return True
    return any(kw in pop for kw in keywords) or "todos" in pop or "adulto" in pop


def filter_instruments(
    area: str,
    age_group: str,
    general_objective: str,
    specific_objectives: list[str],
    db=None,
) -> list[dict]:
    if db is not None:
        candidates = _suggest_from_db(db, general_objective, specific_objectives)
    else:
        candidates = _suggest_from_memory(general_objective, specific_objectives)

    if candidates == [_FALLBACK]:
        return candidates

    filtered = [
        inst for inst in candidates
        if _area_matches(inst, area) and _age_matches(inst, age_group)
    ]
    return filtered if filtered else candidates
