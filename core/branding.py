"""Institutional branding — resolves the WHO/OMS logo by language."""
from __future__ import annotations
from pathlib import Path

from config.settings import BASE_DIR

ASSETS = BASE_DIR / "assets"


def logo_path(language: str = "fr") -> Path | None:
    """Return the WHO logo path for the language (FR = OMS, EN = WHO), or None if absent."""
    name = "who_logo_fr.png" if language == "fr" else "who_logo_en.png"
    p = ASSETS / name
    if p.exists():
        return p
    # fall back to the other language if only one logo is present
    other = ASSETS / ("who_logo_en.png" if language == "fr" else "who_logo_fr.png")
    return other if other.exists() else None


def logo_bytes(language: str = "fr") -> bytes | None:
    p = logo_path(language)
    return p.read_bytes() if p else None


# ---- Dian K Pro branding ----
def dk_logo_path() -> Path | None:
    p = ASSETS / "dk_pro_logo.png"
    return p if p.exists() else None


def dk_logo_bytes() -> bytes | None:
    p = dk_logo_path()
    return p.read_bytes() if p else None


def dk_credit(language: str = "fr") -> str:
    return ("Conçu par Dian K Pro · Public Health & Digital Strategist" if language == "fr"
            else "Designed by Dian K Pro · Public Health & Digital Strategist")
