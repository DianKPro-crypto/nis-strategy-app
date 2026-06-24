"""
Prompt templates for the Anthropic Claude API.

Design principles enforced here (spec §6, §10):
  - The AI must NEVER invent information.
  - Every element carries source + locator + excerpt + confidence.
  - Missing info -> the literal placeholder string.
  - Strict JSON output validated against an explicit schema.
"""
from __future__ import annotations
import json
from core.epi_components import EPI_COMPONENTS, COUNTRY_SPECIFIC
from core.models import CountryProfile, UploadedDocument

PLACEHOLDER_FR = "À compléter par l’équipe pays"
PLACEHOLDER_EN = "To be completed by the country team"

SYSTEM_PROMPT = """You are a Senior Public Health Expert in immunization strategy (EPI, NIS, IA2030, \
Gavi, WHO planning tools, M&E) AND a meticulous evidence analyst.

ABSOLUTE RULES (anti-hallucination):
1. Use ONLY information found in the provided country documents. Never invent facts, figures or names.
2. For every generated element, cite: source document name, a locator (page/slide/sheet/table), a short \
evidence excerpt, and a confidence level (high|medium|low).
3. If information for a field is NOT present in the documents, output the exact placeholder string \
provided in the user message (do not guess).
4. Clearly separate evidence-based findings from AI recommendations and from assumptions needing validation.
5. Strengths and weaknesses are INTERNAL to the EPI programme; opportunities and threats are EXTERNAL.
6. Strategic objectives must be SMART and written in formal public-health language.
7. Respond with a SINGLE valid JSON object that conforms exactly to the requested schema. No prose, \
no markdown fences, no comments. Use the requested output language for all human-readable text."""


def _components_block(lang: str) -> str:
    lines = []
    for comp in EPI_COMPONENTS + [COUNTRY_SPECIFIC]:
        lines.append(comp.label(lang))
        for sub in comp.subcomponents:
            ex = f"  — ex.: {sub.examples_fr}" if sub.examples_fr else ""
            lines.append(f"   {sub.label(lang)}{ex}")
    return "\n".join(lines)


def _documents_block(documents: list[UploadedDocument], budget_chars: int = 45000) -> str:
    if not documents:
        return "(Aucun document fourni / No documents provided.)"
    per = max(1500, budget_chars // max(1, len(documents)))
    blocks = []
    for d in documents:
        body = (d.text or "").strip()[:per]
        blocks.append(
            f"### DOCUMENT: {d.name} (type={d.file_type}, pages/slides={d.n_pages}, "
            f"catégorie={d.doc_category})\n{d.tables_summary}\n{body}"
        )
    return "\n\n".join(blocks)


def build_generation_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                            language: str, section: str) -> str:
    """Build the user message for a given workflow `section`."""
    placeholder = PLACEHOLDER_FR if language == "fr" else PLACEHOLDER_EN
    schema = SCHEMAS[section]
    lang_name = "français" if language == "fr" else "English"
    return f"""CONTEXTE PAYS / COUNTRY CONTEXT
- Country: {profile.country_name} ({profile.iso_code})
- Ministry: {profile.ministry_name}
- EPI programme: {profile.epi_programme_name}
- NIS period: {profile.nis_start_year}..{profile.nis_start_year + profile.nis_duration_years - 1} \
({profile.nis_duration_years} years)
- Currency: {profile.currency} · Focal point: {profile.focal_point}

OUTPUT LANGUAGE: {lang_name}
MISSING-INFO PLACEHOLDER (use verbatim when documents lack the information): "{placeholder}"

EPI COMPONENTS & SUBCOMPONENTS (cover ALL of them where relevant):
{_components_block(language)}

SOURCE DOCUMENTS (your only source of truth):
{_documents_block(documents)}

TASK: {SECTION_INSTRUCTIONS[section]}

REQUIRED JSON SCHEMA (return exactly this shape, nothing else):
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


# --------------------------------------------------------------------------- #
# Per-section instructions + JSON schemas (kept compact; validated downstream).
# --------------------------------------------------------------------------- #
SECTION_INSTRUCTIONS = {
    "vision": "Generate the country's 10-year immunization vision, the NIS goal for the period, and the "
              "overall objective, aligned with IA2030, equity, zero-dose/under-immunized children, PHC, "
              "health-system resilience, life-course vaccination and sustainable financing.",
    "swot": "For EACH EPI subcomponent (code like '1.1'), list strengths, weaknesses (INTERNAL) and "
            "opportunities, threats (EXTERNAL). Empty lists are allowed where evidence is absent.",
    "root_causes": "For each documented weakness, apply the '5 Whys'. Provide an array 'whys' (Why-1..n) and "
                   "a 'final_why' (root cause). Add as many whys as the evidence supports.",
    "objectives": "From the final whys, formulate the main obstacle, the visionary change result, and ONE "
                   "SMART strategic objective per item. Respect the requested grouping option.",
    "interventions": "For each strategic objective, propose 3-5 high-impact, feasible interventions with "
                      "rationale, expected impact, feasibility, prerequisites, risks, partners and a Y1..Yn "
                      "timeline. Score each on the 8 criteria (1-3).",
    "indicators": "For each strategic objective, define preferably 1 IMPACT or OUTPUT indicator with full "
                  "M&E metadata and progressive yearly targets. If no baseline -> baseline placeholder.",
    "activities": "Break each intervention into key activities with implementation level, Y1..Yn calendar, "
                  "lead, partners, prerequisites, risks and deliverables (NIS.COST-compatible).",
}

_EVIDENCE = {"document_name": "str", "locator": "str", "excerpt": "str", "confidence": "high|medium|low"}

SCHEMAS: dict[str, dict] = {
    "vision": {"vision": "str", "goal": "str", "overall_objective": "str", "evidence": [_EVIDENCE]},
    "swot": {"items": [{
        "component_code": "str", "subcomponent_code": "str",
        "strengths": ["str"], "weaknesses": ["str"], "opportunities": ["str"], "threats": ["str"],
        "evidence": [_EVIDENCE]}]},
    "root_causes": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "weakness": "str",
        "whys": ["str"], "final_why": "str", "evidence": [_EVIDENCE]}]},
    "objectives": {"items": [{
        "obj_id": "str", "component_code": "str", "subcomponent_code": "str",
        "main_obstacle": "str", "visionary_result": "str", "objective_text": "str",
        "is_smart": True, "evidence": [_EVIDENCE]}]},
    "interventions": {"items": [{
        "intervention_id": "str", "objective_id": "str", "component_code": "str", "subcomponent_code": "str",
        "title": "str", "rationale": "str", "expected_impact": "str", "feasibility_note": "str",
        "score": {"expertise": "1-3", "return_on_investment": "1-3", "effectiveness": "1-3",
                  "ease_of_implementation": "1-3", "negative_consequences": "1-3", "legal_constraints": "1-3",
                  "health_system_impact": "1-3", "feasibility": "1-3"},
        "timeline": {"Y1": True, "Y2": False}, "prerequisites": ["str"], "risks": ["str"],
        "partners": ["str"], "evidence": [_EVIDENCE]}]},
    "indicators": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "objective_id": "str", "name": "str",
        "indicator_type": "impact|outcome|output|process", "definition": "str", "formula": "str",
        "numerator_source": "str", "denominator_source": "str", "data_source": "str", "frequency": "str",
        "responsible_measure": "str", "responsible_action": "str", "baseline": "str",
        "targets": {"Y1": "str", "Y2": "str"}, "assumptions": "str", "measurement_risks": "str",
        "confidence": "high|medium|low", "evidence": [_EVIDENCE]}]},
    "activities": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "objective_id": "str", "intervention_id": "str",
        "activity": "str", "implementation_level": "str", "years": {"Y1": True, "Y2": False},
        "lead": "str", "partners": ["str"], "prerequisites": ["str"], "risks": ["str"],
        "deliverables": ["str"], "evidence": [_EVIDENCE]}]},
}
