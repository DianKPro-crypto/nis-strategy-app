"""
Premium UI theme — custom CSS + helper components injected into Streamlit.

Keeps all app logic untouched; only restyles the interface (typography, colors,
cards, buttons, sidebar navigation, hero banners).
"""
from __future__ import annotations
import streamlit as st

from core.translations import t

# WHO-inspired palette
PRIMARY = "#0093D5"
DARK = "#003366"
ACCENT = "#6CB33F"
BG = "#F4F7FB"

# Per-step hero metadata: emoji + bilingual subtitle
STEP_META = {
    "nav_profile": ("🗂️", "Identifiez le pays, la langue et la période de la stratégie.",
                    "Set the country, language and strategy period."),
    "nav_upload": ("📥", "Importez les documents sources pour alimenter l’analyse.",
                   "Upload source documents to feed the analysis."),
    "nav_vision": ("🎯", "Vision à 10 ans, but et objectif général de la SNV.",
                   "10-year vision, NIS goal and overall objective."),
    "nav_swot": ("🧭", "Forces, faiblesses, opportunités et menaces par composante PEV.",
                 "Strengths, weaknesses, opportunities and threats by EPI component."),
    "nav_root": ("🔍", "Méthode des POURQUOI pour remonter aux causes profondes.",
                 "The 5-Whys method to reach the root causes."),
    "nav_obj": ("🏛️", "Obstacles principaux et objectifs stratégiques SMART.",
                "Main obstacles and SMART strategic objectives."),
    "nav_interv": ("🚀", "Interventions à fort impact et priorisation multicritère.",
                   "High-impact interventions and multi-criteria prioritization."),
    "nav_me": ("📊", "Cadre de suivi-évaluation : indicateurs, bases et cibles.",
               "M&E framework: indicators, baselines and targets."),
    "nav_act": ("🛠️", "Activités opérationnelles, niveaux et calendrier pluriannuel.",
                "Operational activities, levels and multi-year calendar."),
    "nav_qc": ("✅", "Contrôle qualité et complétude avant export.",
               "Quality control and completeness before export."),
    "nav_export": ("📦", "Générez les livrables Excel, Word, PDF et PowerPoint.",
                   "Generate the Excel, Word, PDF and PowerPoint deliverables."),
}


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(nav_key: str, lang: str) -> None:
    icon, sub_fr, sub_en = STEP_META.get(nav_key, ("•", "", ""))
    title = t(nav_key, lang)
    subtitle = sub_fr if lang == "fr" else sub_en
    st.markdown(
        f"""
        <div class="nis-hero">
          <div class="nis-hero-icon">{icon}</div>
          <div class="nis-hero-text">
            <div class="nis-hero-title">{title}</div>
            <div class="nis-hero-sub">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

:root {{
  --nis-primary: {PRIMARY};
  --nis-dark: {DARK};
  --nis-accent: {ACCENT};
}}

/* ---------- Base ---------- */
html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, input, textarea, select, button {{
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}}
.stApp {{ background: {BG}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"], .block-container {{
  padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1200px;
}}

/* ---------- Headings ---------- */
h1, h2, h3 {{ font-family: 'Poppins','Inter',sans-serif !important; color: var(--nis-dark); letter-spacing: -.01em; }}
h2 {{ font-weight: 700; }}

/* ---------- Hero banner ---------- */
.nis-hero {{
  display: flex; align-items: center; gap: 1rem;
  background: linear-gradient(120deg, var(--nis-dark) 0%, var(--nis-primary) 100%);
  color: #fff; padding: 1.25rem 1.5rem; border-radius: 18px; margin-bottom: 1.4rem;
  box-shadow: 0 12px 30px -12px rgba(0,51,102,.55);
}}
.nis-hero-icon {{
  font-size: 2rem; background: rgba(255,255,255,.15); width: 58px; height: 58px;
  display: flex; align-items: center; justify-content: center; border-radius: 14px; flex-shrink: 0;
}}
.nis-hero-title {{ font-family: 'Poppins',sans-serif; font-size: 1.5rem; font-weight: 700; line-height: 1.2; }}
.nis-hero-sub {{ font-size: .92rem; opacity: .92; margin-top: .15rem; }}

/* ---------- Content cards (expanders) ---------- */
[data-testid="stExpander"] {{
  border: 1px solid #E3EAF2; border-radius: 14px; background: #fff;
  box-shadow: 0 4px 16px -10px rgba(0,51,102,.25); overflow: hidden; margin-bottom: .6rem;
}}
[data-testid="stExpander"] summary {{ font-weight: 600; color: var(--nis-dark); padding: .35rem .25rem; }}
[data-testid="stExpander"] summary:hover {{ color: var(--nis-primary); }}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(120deg, var(--nis-primary), #00A9E0);
  color: #fff; border: none; border-radius: 11px; font-weight: 600; padding: .55rem 1.15rem;
  box-shadow: 0 8px 20px -10px rgba(0,147,213,.8); transition: transform .12s ease, box-shadow .12s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
  transform: translateY(-2px); box-shadow: 0 12px 26px -10px rgba(0,147,213,.9); color: #fff;
}}
.stButton > button:active {{ transform: translateY(0); }}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
[data-baseweb="select"] > div, .stDateInput input {{
  border-radius: 10px !important; border: 1px solid #D9E2EC !important; background: #fff !important;
}}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
  border-color: var(--nis-primary) !important; box-shadow: 0 0 0 3px rgba(0,147,213,.15) !important;
}}
label, .stTextInput label, .stSelectbox label {{ color: var(--nis-dark) !important; font-weight: 500; }}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {{
  background: #fff; border: 1px solid #E3EAF2; border-radius: 14px; padding: .8rem 1rem;
  box-shadow: 0 4px 16px -10px rgba(0,51,102,.25);
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #FFFFFF 0%, #EEF4FA 100%);
  border-right: 1px solid #E1E9F2;
}}
section[data-testid="stSidebar"] .stImage {{ margin-bottom: .25rem; }}
section[data-testid="stSidebar"] h1 {{ font-size: 1.05rem !important; line-height: 1.3; }}

/* Sidebar nav (radio groups) -> pill menu */
section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: .15rem; }}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
  border-radius: 10px; padding: .5rem .7rem; margin: .08rem 0; transition: background .15s, color .15s;
  font-weight: 500; color: #2b3b4e; cursor: pointer;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{ background: rgba(0,147,213,.10); }}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{ display: none; }}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
  background: linear-gradient(120deg, var(--nis-dark), var(--nis-primary)); color: #fff;
  box-shadow: 0 8px 18px -10px rgba(0,51,102,.7);
}}

/* ---------- Alerts a touch softer ---------- */
[data-testid="stAlert"] {{ border-radius: 12px; }}

/* ---------- Progress bar ---------- */
[data-testid="stProgress"] > div > div > div {{ background: linear-gradient(90deg, var(--nis-primary), var(--nis-accent)); }}

/* Hide default footer */
footer {{ visibility: hidden; }}
</style>
"""
