"""Institutional branding — resolves the WHO/OMS logo by language."""
from __future__ import annotations
import base64
import io
from pathlib import Path

from config.settings import BASE_DIR

ASSETS = BASE_DIR / "assets"
_HTML_CACHE: dict = {}


def _img_html(path: Path | None, render_width: int, max_px: int = 420) -> str:
    """Return a centered <img> as a base64 data-URI (renders instantly, no media server;
    fixes the WHO logo not showing until a manual refresh). Downscaled + cached."""
    if not path or not path.exists():
        return ""
    ck = (str(path), render_width, max_px)
    if ck in _HTML_CACHE:
        return _HTML_CACHE[ck]
    data = path.read_bytes()
    try:  # downscale so the inline data-URI stays small
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        if im.width > max_px:
            im = im.resize((max_px, int(max_px * im.height / im.width)))
        buf = io.BytesIO(); im.convert("RGBA").save(buf, "PNG"); data = buf.getvalue()
    except Exception:
        pass
    b64 = base64.b64encode(data).decode()
    html = (f"<div style='text-align:center'><img src='data:image/png;base64,{b64}' "
            f"width='{render_width}' style='display:block;margin:0 auto'/></div>")
    _HTML_CACHE[ck] = html
    return html


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


def logo_html(language: str = "fr", render_width: int = 210) -> str:
    """Centered WHO/OMS logo as an inline data-URI (instant render)."""
    return _img_html(logo_path(language), render_width)


def dk_logo_html(render_width: int = 130) -> str:
    """Centered Dian K Pro logo as an inline data-URI."""
    return _img_html(dk_logo_path(), render_width)
