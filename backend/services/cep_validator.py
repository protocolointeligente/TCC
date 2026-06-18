"""
Validates an AdvancedCepRequest and returns severity-classified issues.
Severity: "error" | "warning" | "info"
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal


@dataclass
class ValidationIssue:
    severity: Literal["error", "warning", "info"]
    field: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


_VALID_STUDY_TYPES = {"quantitativo", "qualitativo", "misto", "descritivo", "experimental", "quasi-experimental"}
_VALID_AGE_GROUPS = {"crianças", "adolescentes", "adultos", "idosos", "todos"}
_INSTITUTION_LOCATIONS = {"escola", "academia", "clínica", "clinica", "hospital", "universidade", "ubs", "creche"}


def validate_cep_project(payload) -> list[dict]:
    issues: list[ValidationIssue] = []

    # --- Errors (blocking) ---
    if not payload.title or len(payload.title.strip()) < 10:
        issues.append(ValidationIssue("error", "title", "Título muito curto (mínimo 10 caracteres)."))

    if not payload.general_objective or len(payload.general_objective.strip()) < 20:
        issues.append(ValidationIssue("error", "general_objective", "Objetivo geral muito curto ou ausente."))

    if not payload.specific_objectives:
        issues.append(ValidationIssue("error", "specific_objectives", "Ao menos um objetivo específico é obrigatório."))

    if not payload.methodology_summary or len(payload.methodology_summary.strip()) < 30:
        issues.append(ValidationIssue("error", "methodology_summary", "Metodologia muito curta ou ausente."))

    if payload.study_type.lower() not in _VALID_STUDY_TYPES:
        issues.append(ValidationIssue(
            "warning", "study_type",
            f"Tipo de estudo '{payload.study_type}' incomum. Verifique se está correto.",
        ))

    if not payload.expected_sample:
        issues.append(ValidationIssue("error", "expected_sample", "Tamanho amostral esperado não informado."))

    # --- Warnings ---
    if payload.involves_minors and not payload.involves_vulnerable_population:
        issues.append(ValidationIssue(
            "warning", "involves_minors",
            "Menores de idade são considerados população vulnerável. Marque 'população vulnerável'.",
        ))

    loc = payload.collection_location.lower()
    if any(kw in loc for kw in _INSTITUTION_LOCATIONS):
        issues.append(ValidationIssue(
            "warning", "collection_location",
            "Coleta em instituição exige Carta de Anuência — certifique-se de incluir no processo.",
        ))

    if payload.collects_sensitive_data and not any(
        kw in payload.methodology_summary.lower()
        for kw in ["anoni", "sigil", "confidenci", "proteg"]
    ):
        issues.append(ValidationIssue(
            "warning", "collects_sensitive_data",
            "Dados sensíveis exigem descrição de anonimização e sigilo na metodologia.",
        ))

    if payload.is_online_research and not any(
        kw in payload.methodology_summary.lower()
        for kw in ["plataforma", "formulário", "google", "surveymonkey", "privacidade", "lgpd"]
    ):
        issues.append(ValidationIssue(
            "warning", "is_online_research",
            "Pesquisa online deve mencionar plataforma, privacidade e conformidade com a LGPD.",
        ))

    if payload.has_physical_intervention:
        issues.append(ValidationIssue(
            "warning", "has_physical_intervention",
            "Intervenção física requer descrição de riscos, critérios de interrupção e seguros.",
        ))

    if not payload.variables:
        issues.append(ValidationIssue(
            "info", "variables",
            "Informe as variáveis do estudo para gerar a matriz objetivo→instrumento→variável→análise.",
        ))

    if not payload.sampling_method:
        issues.append(ValidationIssue(
            "info", "sampling_method",
            "Especifique o método de amostragem (probabilístico, conveniência, intencional etc.).",
        ))

    if len(payload.specific_objectives) == 1:
        issues.append(ValidationIssue(
            "info", "specific_objectives",
            "Apenas um objetivo específico pode ser insuficiente para justificar múltiplos instrumentos.",
        ))

    return [i.to_dict() for i in issues]


def classify_ethics_risk(payload) -> dict:
    """Extended risk classifier with numeric score and level."""
    score = 0
    details: list[str] = []

    if payload.involves_minors:
        score += 3
        details.append("Participação de menores de idade.")
    if payload.involves_vulnerable_population:
        score += 3
        details.append("População vulnerável (idosos, presos, pacientes, etc.).")
    if payload.collects_sensitive_data:
        score += 2
        details.append("Coleta de dados sensíveis ou identificáveis.")
    if payload.has_physical_intervention:
        score += 2
        details.append("Intervenção física com possível desconforto ou risco.")
    if payload.uses_images:
        score += 1
        details.append("Uso de imagem, áudio ou vídeo dos participantes.")
    if payload.is_online_research:
        score += 1
        details.append("Coleta online com risco de exposição de dados digitais.")

    if score == 0:
        details.append("Risco mínimo: possível desconforto ao responder perguntas.")

    if score <= 1:
        level = "mínimo"
    elif score <= 3:
        level = "baixo"
    elif score <= 5:
        level = "moderado"
    else:
        level = "elevado"

    return {"risk_level": level, "risk_score": score, "identified_risks": details}
