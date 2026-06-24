"""
Anthropic Claude integration.

- `generate_section()` runs one workflow step and returns validated structured data.
- `generate_nis_strategy()` is the central orchestrator required by the spec (§10):
  it runs all sections in order and returns a fully populated NISStrategy.
- Strict-JSON enforcement with retry on invalid JSON.
- Offline/manual mode: when no API key is set, returns empty scaffolds so the user
  can fill everything by hand (acceptance criterion: offline mode).
"""
from __future__ import annotations
import json
import re

from config import settings
from core.models import (
    NISStrategy, CountryProfile, UploadedDocument, CountryVision, SWOTItem,
    RootCauseAnalysis, StrategicObjective, Intervention, MEIndicator, Activity,
    PrioritizationScore,
)
from core.epi_components import subcomponent_pairs
from templates.prompts import SYSTEM_PROMPT, build_generation_prompt

SECTIONS = ["vision", "swot", "root_causes", "objectives", "interventions", "indicators", "activities"]


class AIError(RuntimeError):
    pass


def _client():
    if not settings.ai_available():
        raise AIError("ANTHROPIC_API_KEY manquante")
    import anthropic
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extract_json(raw: str) -> dict:
    """Tolerantly pull the first JSON object out of a model response."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except Exception:
        start, depth = raw.find("{"), 0
        if start == -1:
            raise
        for i in range(start, len(raw)):
            depth += raw[i] == "{"
            depth -= raw[i] == "}"
            if depth == 0:
                return json.loads(raw[start:i + 1])
    raise AIError("Réponse JSON invalide")


def _call_claude(prompt: str) -> dict:
    client = _client()
    last_err = None
    for attempt in range(settings.AI_MAX_RETRIES + 1):
        suffix = "" if attempt == 0 else \
            "\n\nIMPORTANT: Your previous reply was not valid JSON. Reply with ONE valid JSON object only."
        msg = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.AI_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt + suffix}],
        )
        text = "".join(getattr(b, "text", "") for b in msg.content)
        try:
            return _extract_json(text)
        except Exception as e:
            last_err = e
    raise AIError(f"JSON invalide après {settings.AI_MAX_RETRIES + 1} tentatives: {last_err}")


# --------------------------------------------------------------------------- #
# Section-level generation
# --------------------------------------------------------------------------- #
def generate_section(section: str, profile: CountryProfile,
                     documents: list[UploadedDocument], language: str) -> dict:
    """Return the raw validated dict for a section (caller maps it onto the model)."""
    if section not in SECTIONS:
        raise ValueError(section)
    prompt = build_generation_prompt(profile, documents, language, section)
    return _call_claude(prompt)


def apply_section(strategy: NISStrategy, section: str, data: dict) -> None:
    """Map a section's JSON payload onto the NISStrategy in place."""
    if section == "vision":
        strategy.vision = CountryVision(**_clean(data, CountryVision))
    elif section == "swot":
        strategy.swot = [SWOTItem(**_clean(x, SWOTItem)) for x in data.get("items", [])]
    elif section == "root_causes":
        strategy.root_causes = [RootCauseAnalysis(**_clean(x, RootCauseAnalysis))
                                for x in data.get("items", [])]
    elif section == "objectives":
        strategy.objectives = [StrategicObjective(**_clean(x, StrategicObjective))
                               for x in data.get("items", [])]
    elif section == "interventions":
        out = []
        for x in data.get("items", []):
            sc = x.pop("score", {}) or {}
            iv = Intervention(**_clean(x, Intervention))
            iv.score = PrioritizationScore(**_clean(sc, PrioritizationScore))
            iv.priority_level = iv.score.level()
            out.append(iv)
        strategy.interventions = out
    elif section == "indicators":
        strategy.indicators = [MEIndicator(**_clean(x, MEIndicator)) for x in data.get("items", [])]
    elif section == "activities":
        strategy.activities = [Activity(**_clean(x, Activity)) for x in data.get("items", [])]


def _clean(d: dict, model_cls) -> dict:
    """Keep only known fields (schema drift tolerance)."""
    try:
        fields = set(model_cls.model_fields.keys())  # pydantic v2
    except AttributeError:
        fields = set(model_cls.__fields__.keys())    # pydantic v1
    return {k: v for k, v in (d or {}).items() if k in fields}


# --------------------------------------------------------------------------- #
# Central orchestrator (spec §10)
# --------------------------------------------------------------------------- #
def generate_nis_strategy(country_profile: CountryProfile, documents: list[UploadedDocument],
                          language: str, years: int, sections: list[str] | None = None,
                          progress=None) -> NISStrategy:
    """Generate the full strategy. `progress(section, i, n)` is an optional callback."""
    country_profile.nis_duration_years = years
    country_profile.language = language
    strategy = NISStrategy(profile=country_profile, documents=documents)
    todo = sections or SECTIONS
    if not settings.ai_available():
        return offline_scaffold(strategy)
    for i, section in enumerate(todo):
        if progress:
            progress(section, i, len(todo))
        data = generate_section(section, country_profile, documents, language)
        apply_section(strategy, section, data)
    return strategy


def offline_scaffold(strategy: NISStrategy) -> NISStrategy:
    """Build empty editable rows for all 26 subcomponents (no API key / manual mode)."""
    strategy.swot = [SWOTItem(component_code=c.code, subcomponent_code=s.code)
                     for c, s in subcomponent_pairs()]
    return strategy
