"""Country dropdown list. Uses pycountry when available, with a built-in fallback."""
from __future__ import annotations


def get_countries() -> list[tuple[str, str]]:
    """Return a sorted list of (iso_alpha2, name)."""
    try:
        import pycountry
        items = [(c.alpha_2, getattr(c, "common_name", c.name)) for c in pycountry.countries]
        return sorted(items, key=lambda x: x[1])
    except Exception:
        return sorted(_FALLBACK, key=lambda x: x[1])


# Small fallback so the app still runs without pycountry (offline install).
_FALLBACK = [
    ("DJ", "Djibouti"), ("SO", "Somalia"), ("SD", "Sudan"), ("SS", "South Sudan"),
    ("ET", "Ethiopia"), ("ER", "Eritrea"), ("EG", "Egypt"), ("YE", "Yemen"),
    ("SA", "Saudi Arabia"), ("MA", "Morocco"), ("TN", "Tunisia"), ("DZ", "Algeria"),
    ("LY", "Libya"), ("JO", "Jordan"), ("LB", "Lebanon"), ("SY", "Syrian Arab Republic"),
    ("IQ", "Iraq"), ("IR", "Iran"), ("PK", "Pakistan"), ("AF", "Afghanistan"),
    ("FR", "France"), ("US", "United States"), ("GB", "United Kingdom"),
    ("NG", "Nigeria"), ("KE", "Kenya"), ("CD", "Democratic Republic of the Congo"),
]

# Common document categories offered in the upload UI (spec §5).
DOCUMENT_CATEGORIES_FR = [
    "Ancienne SNV / cMYP", "Revue du PEV", "Rapport d’analyse situationnelle",
    "Plan stratégique du secteur santé", "Plan opérationnel annuel",
    "Données de couverture vaccinale", "Rapport de surveillance des MEV",
    "Rapport MAPI", "Évaluation de la chaîne du froid", "Évaluation de la chaîne d’approvisionnement",
    "Documents Gavi", "Rapports financiers", "Engagement communautaire / génération de la demande",
    "Rapports des partenaires", "Autre document pertinent",
]
