"""Central configuration. Secrets come only from the environment (.env)."""
from __future__ import annotations
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # dotenv optional
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
TEMP_DIR = DATA_DIR / "temp"
for d in (UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR):
    d.mkdir(parents=True, exist_ok=True)

def _secret(key: str, default: str = "") -> str:
    """Read from env first, then Streamlit secrets (for Streamlit Cloud deployment)."""
    val = os.getenv(key)
    if val:
        return val.strip()
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass
    return default


# ---- AI ----
ANTHROPIC_API_KEY = _secret("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = _secret("ANTHROPIC_MODEL", "claude-sonnet-5")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "16000"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "2"))
# Effort for prose writing (Sonnet 5 / Opus): low|medium|high — 'low' is fastest, prose stays good.
AI_EFFORT = _secret("AI_EFFORT", "low")
# How many narrative sections to write concurrently (parallel API calls).
AI_CONCURRENCY = int(_secret("AI_CONCURRENCY", "4"))

# ---- Storage ----
DB_PATH = os.getenv("NIS_DB_PATH", str(DATA_DIR / "nis.db"))
# Durable cloud storage (optional) — Supabase
SUPABASE_URL = _secret("SUPABASE_URL", "")
SUPABASE_KEY = _secret("SUPABASE_KEY", "")

# ---- Uploads ----
ALLOWED_EXTENSIONS = {"docx", "xlsx", "pptx", "pdf", "csv", "txt"}
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "25"))
# 130k so a full completed WHO workbook (7 components × FFOM/POURQUOI/problème principal) is
# not truncated mid-analysis (the sequence sheet spans all 7 EPI components).
MAX_TEXT_CHARS_PER_DOC = int(os.getenv("MAX_TEXT_CHARS_PER_DOC", "130000"))

# ---- Branding ----
INSTITUTION_PRIMARY = "#0093D5"   # WHO blue
INSTITUTION_DARK = "#003366"
INSTITUTION_ACCENT = "#6CB33F"

DEFAULT_LANGUAGE = "fr"


def ai_available() -> bool:
    return bool(ANTHROPIC_API_KEY)
