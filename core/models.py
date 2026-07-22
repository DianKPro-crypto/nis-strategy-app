"""
Structured data models for the NIS strategy.

Every AI-generated object is JSON-serializable, editable in the UI, validatable
and exportable. We use Pydantic v2 (falls back gracefully if only v1 is present).
The shape mirrors the WHO workbook sections 1-7.
"""
from __future__ import annotations
from datetime import date
from enum import Enum
from typing import ClassVar, Optional

try:
    from pydantic import BaseModel, Field, ConfigDict
    _V2 = True
except Exception:  # pragma: no cover
    from pydantic import BaseModel, Field  # type: ignore
    _V2 = False

PLACEHOLDER = "À compléter par l’équipe pays"  # FR; EN equivalent applied at render time


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriorityLevel(str, Enum):
    HIGH = "high"      # Élevé
    MEDIUM = "medium"  # Moyen / Modéré
    LOW = "low"        # Faible


class IndicatorType(str, Enum):
    IMPACT = "impact"
    OUTCOME = "outcome"
    OUTPUT = "output"
    PROCESS = "process"


class _Model(BaseModel):
    if _V2:
        model_config = ConfigDict(use_enum_values=True, extra="ignore")
    else:  # pragma: no cover
        class Config:
            use_enum_values = True


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
class EvidenceReference(_Model):
    document_name: str = ""
    locator: str = ""          # page / slide / sheet / table reference
    excerpt: str = ""          # short justification or quote
    confidence: Confidence = Confidence.LOW


# --------------------------------------------------------------------------- #
# Inputs
# --------------------------------------------------------------------------- #
class CountryProfile(_Model):
    country_name: str = ""
    iso_code: str = ""
    ministry_name: str = ""
    epi_programme_name: str = ""
    nis_start_year: int = 2026
    nis_duration_years: int = 5
    currency: str = "USD"
    focal_point: str = ""
    language: str = "fr"
    generation_date: str = Field(default_factory=lambda: date.today().isoformat())

    @property
    def years(self) -> list[int]:
        return [self.nis_start_year + i for i in range(self.nis_duration_years)]


class UploadedDocument(_Model):
    name: str
    file_type: str = ""        # docx / xlsx / pptx / pdf / csv / txt
    size_bytes: int = 0
    doc_category: str = ""     # e.g. "Previous NIS", "cMYP", "EPI review"...
    text: str = ""             # extracted full text
    tables_summary: str = ""   # short description of tables found
    metadata: dict = Field(default_factory=dict)
    n_pages: int = 0


# --------------------------------------------------------------------------- #
# Section 0 — Country vision
# --------------------------------------------------------------------------- #
class CountryVision(_Model):
    vision: str = ""             # 10-year immunization vision
    goal: str = ""               # NIS goal for the strategy period
    overall_objective: str = ""  # overall objective
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 1 — SWOT
# --------------------------------------------------------------------------- #
class SWOTItem(_Model):
    component_code: str = ""
    subcomponent_code: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 2 — Root cause analysis ("Why" method)
# --------------------------------------------------------------------------- #
class RootCauseAnalysis(_Model):
    component_code: str = ""
    subcomponent_code: str = ""
    weakness: str = ""
    whys: list[str] = Field(default_factory=list)   # Why-1, Why-2, ... (extensible)
    final_why: str = ""
    # Section 3 (méthode OMS) : les "derniers POURQUOI" d'une sous-composante sont regroupés
    # pour former UN "problème principal" (obstacle). Un seul par sous-composante -> max 26.
    main_problem: str = ""
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 3 & 4 — Obstacle, theory of change, strategic objective
# --------------------------------------------------------------------------- #
class StrategicObjective(_Model):
    obj_id: str = ""
    component_code: str = ""
    subcomponent_code: str = ""
    main_obstacle: str = ""              # Section 3 — problème/obstacle principal
    visionary_result: str = ""           # Section 4 — résultat visionnaire
    objective_text: str = ""             # SMART objective (Section 4)
    is_smart: bool = False
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 5 — Interventions + prioritization
# --------------------------------------------------------------------------- #
class PrioritizationScore(_Model):
    """Multi-criteria scores (1-3 each) per the 'How to prioritize' sheet, method 1."""
    expertise: int = 2                 # Expertise pour mettre en œuvre
    return_on_investment: int = 2      # Retour sur investissement
    effectiveness: int = 2             # Efficacité de la solution
    ease_of_implementation: int = 2    # Facilité de mise en œuvre/maintenance
    negative_consequences: int = 2     # Conséquences négatives potentielles
    legal_constraints: int = 2         # Considérations juridiques
    health_system_impact: int = 2      # Impact sur les systèmes/la santé
    feasibility: int = 2               # Faisabilité de l'intervention
    # Extra criteria requested by the spec (kept optional, default neutral):
    cost: int = 2
    urgency: int = 2
    equity_contribution: int = 2
    zero_dose_contribution: int = 2

    CORE_CRITERIA: ClassVar[tuple[str, ...]] = (
        "expertise", "return_on_investment", "effectiveness", "ease_of_implementation",
        "negative_consequences", "legal_constraints", "health_system_impact", "feasibility",
    )

    def total(self, use_extended: bool = False) -> int:
        keys = self.CORE_CRITERIA + ("cost", "urgency", "equity_contribution",
                                     "zero_dose_contribution") if use_extended else self.CORE_CRITERIA
        return sum(int(getattr(self, k)) for k in keys)

    def level(self, use_extended: bool = False) -> PriorityLevel:
        """Workbook thresholds (8 core criteria, max 24): High 17-24, Medium 9-16, Low 1-8.
        Scaled proportionally if extended criteria are used (max 36)."""
        n = len(self.CORE_CRITERIA) + (4 if use_extended else 0)
        maxv = n * 3
        score = self.total(use_extended)
        hi = round(maxv * 17 / 24)   # 17 when n=8
        mid = round(maxv * 9 / 24)   # 9  when n=8
        if score >= hi:
            return PriorityLevel.HIGH
        if score >= mid:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW


class Intervention(_Model):
    intervention_id: str = ""
    objective_id: str = ""
    component_code: str = ""
    subcomponent_code: str = ""
    title: str = ""
    rationale: str = ""
    expected_impact: str = ""
    feasibility_note: str = ""
    score: PrioritizationScore = Field(default_factory=PrioritizationScore)
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    # 2x2 matrix quadrant: "high_impact_high_feas" etc.
    matrix_quadrant: str = ""
    timeline: dict[str, bool] = Field(default_factory=dict)  # {"Y1": True, ...}
    prerequisites: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    partners: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 6 — M&E framework
# --------------------------------------------------------------------------- #
class MEIndicator(_Model):
    component_code: str = ""
    subcomponent_code: str = ""
    objective_id: str = ""
    name: str = ""
    indicator_type: IndicatorType = IndicatorType.OUTCOME
    definition: str = ""
    formula: str = ""
    numerator_source: str = ""
    denominator_source: str = ""
    data_source: str = ""
    frequency: str = ""
    responsible_measure: str = ""
    responsible_action: str = ""
    baseline: str = ""
    targets: dict[str, str] = Field(default_factory=dict)  # {"Y1": "...", ...}
    assumptions: str = ""
    measurement_risks: str = ""
    confidence: Confidence = Confidence.LOW
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Section 7 — Operational activities
# --------------------------------------------------------------------------- #
class Activity(_Model):
    component_code: str = ""
    subcomponent_code: str = ""
    objective_id: str = ""
    intervention_id: str = ""
    activity: str = ""
    implementation_level: str = ""      # National / Region / District / Facility / Community / All...
    years: dict[str, bool] = Field(default_factory=dict)  # {"Y1": True, ...}
    lead: str = ""
    partners: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Quality control & top-level package
# --------------------------------------------------------------------------- #
class QualityCheckReport(_Model):
    completion_pct: float = 0.0
    missing_fields: list[str] = Field(default_factory=list)
    critical_gaps: list[str] = Field(default_factory=list)
    needs_validation: list[str] = Field(default_factory=list)
    uncovered_components: list[str] = Field(default_factory=list)
    objectives_without_indicators: list[str] = Field(default_factory=list)
    interventions_without_activities: list[str] = Field(default_factory=list)
    indicators_without_baseline: list[str] = Field(default_factory=list)
    non_progressive_targets: list[str] = Field(default_factory=list)
    calendar_inconsistencies: list[str] = Field(default_factory=list)
    export_ready: bool = False


class NISStrategy(_Model):
    """The single source of truth held in session state and serialized to SQLite."""
    profile: CountryProfile = Field(default_factory=CountryProfile)
    documents: list[UploadedDocument] = Field(default_factory=list)
    vision: CountryVision = Field(default_factory=CountryVision)
    swot: list[SWOTItem] = Field(default_factory=list)
    root_causes: list[RootCauseAnalysis] = Field(default_factory=list)
    objectives: list[StrategicObjective] = Field(default_factory=list)
    interventions: list[Intervention] = Field(default_factory=list)
    indicators: list[MEIndicator] = Field(default_factory=list)
    activities: list[Activity] = Field(default_factory=list)
    grouping_option: str = "option1"          # option1 | option2 | option3
    validated_sections: dict[str, bool] = Field(default_factory=dict)
    # Step 11 — full AI write-up
    narrative: dict[str, str] = Field(default_factory=dict)   # section_key -> AI prose
    financial_report: str = ""                                # from NIS.COST
    niscost_text: str = ""                                    # extracted NIS.COST source
    snv_draft_text: str = ""                                  # uploaded draft NIS the AI builds upon
    # Official web sources the AI cited during the write-up (title + url) — feeds the bibliography.
    web_sources: list[dict] = Field(default_factory=list)

    # ---- serialization helpers (v1/v2 compatible) ----
    def to_dict(self) -> dict:
        return self.model_dump() if _V2 else self.dict()  # type: ignore

    def to_json(self) -> str:
        return self.model_dump_json(indent=2) if _V2 else self.json(indent=2)  # type: ignore

    @classmethod
    def from_dict(cls, data: dict) -> "NISStrategy":
        return cls.model_validate(data) if _V2 else cls.parse_obj(data)  # type: ignore
