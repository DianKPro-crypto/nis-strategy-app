"""Minimal i18n layer (English / French). Use t(key, lang)."""
from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "app_title": {"fr": "Plateforme d’élaboration de la Stratégie Nationale de Vaccination (SNV)",
                  "en": "National Immunization Strategy (NIS) Builder"},
    "language": {"fr": "Langue", "en": "Language"},
    "country": {"fr": "Pays", "en": "Country"},
    "step": {"fr": "Étape", "en": "Step"},
    "nav_profile": {"fr": "0 · Profil du pays", "en": "0 · Country profile"},
    "nav_upload": {"fr": "1 · Documents sources", "en": "1 · Source documents"},
    "nav_vision": {"fr": "2 · Vision du pays", "en": "2 · Country vision"},
    "nav_swot": {"fr": "3 · Analyse FFOM/SWOT", "en": "3 · SWOT analysis"},
    "nav_root": {"fr": "4 · Causes profondes", "en": "4 · Root cause analysis"},
    "nav_obj": {"fr": "5 · Obstacles & objectifs", "en": "5 · Obstacles & objectives"},
    "nav_interv": {"fr": "6 · Interventions & priorisation", "en": "6 · Interventions & prioritization"},
    "nav_me": {"fr": "7 · Cadre de S&E", "en": "7 · M&E framework"},
    "nav_act": {"fr": "8 · Activités opérationnelles", "en": "8 · Operational activities"},
    "nav_qc": {"fr": "9 · Contrôle qualité", "en": "9 · Quality control"},
    "nav_export": {"fr": "10 · Exports", "en": "10 · Exports"},
    "nav_help": {"fr": "❓ Aide / Guide", "en": "❓ Help / Guide"},
    "generate": {"fr": "Générer avec l’IA", "en": "Generate with AI"},
    "regenerate": {"fr": "Régénérer", "en": "Regenerate"},
    "validate_section": {"fr": "Valider cette section", "en": "Validate this section"},
    "validated": {"fr": "Section validée ✅", "en": "Section validated ✅"},
    "save": {"fr": "Enregistrer", "en": "Save"},
    "placeholder": {"fr": "À compléter par l’équipe pays",
                    "en": "To be completed by the country team"},
    "baseline_tbc": {"fr": "Situation de référence à confirmer par l’équipe pays",
                     "en": "Baseline to be confirmed by the country team"},
    "confidence": {"fr": "Niveau de confiance", "en": "Confidence level"},
    "evidence": {"fr": "Sources / preuves", "en": "Evidence / sources"},
    "no_api": {"fr": "Clé API Anthropic absente — mode hors-ligne (saisie manuelle).",
               "en": "Anthropic API key missing — offline mode (manual entry)."},
    "strengths": {"fr": "Forces", "en": "Strengths"},
    "weaknesses": {"fr": "Faiblesses", "en": "Weaknesses"},
    "opportunities": {"fr": "Opportunités", "en": "Opportunities"},
    "threats": {"fr": "Menaces", "en": "Threats"},
}


def t(key: str, lang: str = "fr") -> str:
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("fr") or key
