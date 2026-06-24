"""
Quality-control checks (spec §11). Produces a QualityCheckReport used by the
QC page and to gate exports.
"""
from __future__ import annotations
from core.models import NISStrategy, QualityCheckReport
from core.epi_components import EPI_COMPONENTS
from core.translations import t

PLACEHOLDERS = {"À compléter par l’équipe pays", "To be completed by the country team"}


def _is_blank(v) -> bool:
    return not v or (isinstance(v, str) and (not v.strip() or v.strip() in PLACEHOLDERS))


def run_quality_check(s: NISStrategy) -> QualityCheckReport:
    r = QualityCheckReport()

    # --- vision ---
    for field in ("vision", "goal", "overall_objective"):
        if _is_blank(getattr(s.vision, field)):
            r.missing_fields.append(f"Vision: {field}")

    # --- component coverage (via SWOT) ---
    covered = {item.component_code for item in s.swot
               if item.strengths or item.weaknesses or item.opportunities or item.threats}
    for comp in EPI_COMPONENTS:
        if comp.code not in covered:
            r.uncovered_components.append(comp.label("fr"))

    # --- objectives without indicators ---
    obj_ids = {o.obj_id for o in s.objectives if o.obj_id}
    ind_obj = {i.objective_id for i in s.indicators}
    for o in s.objectives:
        if o.obj_id and o.obj_id not in ind_obj:
            r.objectives_without_indicators.append(o.obj_id or o.objective_text[:40])

    # --- interventions without activities ---
    act_iv = {a.intervention_id for a in s.activities}
    for iv in s.interventions:
        if iv.intervention_id and iv.intervention_id not in act_iv:
            r.interventions_without_activities.append(iv.title[:50])

    # --- indicators without baseline / non-progressive targets ---
    for ind in s.indicators:
        if _is_blank(ind.baseline):
            r.indicators_without_baseline.append(ind.name[:50])
        nums = []
        for k in sorted(ind.targets):
            try:
                nums.append(float(str(ind.targets[k]).replace("%", "").replace(",", ".").strip()))
            except Exception:
                nums = []
                break
        if nums and any(b < a for a, b in zip(nums, nums[1:])):
            r.non_progressive_targets.append(ind.name[:50])

    # --- items needing validation (low confidence / placeholders) ---
    if s.objectives and not any(o.is_smart for o in s.objectives):
        r.needs_validation.append("Objectifs stratégiques: confirmer le caractère SMART")
    for iv in s.interventions:
        if _is_blank(iv.title):
            r.critical_gaps.append("Intervention sans titre")

    # --- completion percentage (weighted by section presence) ---
    checks = [
        bool(s.profile.country_name),
        bool(s.documents),
        not any(_is_blank(getattr(s.vision, f)) for f in ("vision", "goal", "overall_objective")),
        bool(covered),
        bool(s.root_causes),
        bool(s.objectives),
        bool(s.interventions),
        bool(s.indicators),
        bool(s.activities),
    ]
    r.completion_pct = round(100 * sum(checks) / len(checks), 1)

    blocking = (r.missing_fields or r.uncovered_components or r.critical_gaps
                or r.objectives_without_indicators or r.interventions_without_activities)
    all_validated = all(s.validated_sections.get(k) for k in
                        ("vision", "swot", "objectives", "interventions", "indicators", "activities"))
    r.export_ready = (not blocking) and all_validated
    return r
