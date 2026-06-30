"""PowerPoint (.pptx) export — sober institutional decision-maker deck."""
from __future__ import annotations
from io import BytesIO

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from config.settings import INSTITUTION_DARK, INSTITUTION_PRIMARY
from core.models import NISStrategy
from core.branding import logo_path

_DARK = RGBColor.from_string(INSTITUTION_DARK.lstrip("#"))
_PRIMARY = RGBColor.from_string(INSTITUTION_PRIMARY.lstrip("#"))
_WHITE = RGBColor.from_string("FFFFFF")


def build_ppt(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"

    lp = logo_path(s.profile.language)

    def title_slide():
        sl = prs.slides.add_slide(blank)
        if lp:
            try:
                sl.shapes.add_picture(str(lp), Inches(0.6), Inches(0.5), height=Inches(0.9))
            except Exception:
                pass
        _band(sl, 0, Inches(2.4), Inches(2.7), _DARK)
        _text(sl, "Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy",
              Inches(0.8), Inches(2.7), Inches(11.7), Inches(1.2), 40, _WHITE, bold=True)
        _text(sl, f"{s.profile.country_name} · {period}", Inches(0.8), Inches(4.0),
              Inches(11.7), Inches(0.8), 24, _DARK)
        _text(sl, f"{s.profile.ministry_name} — {s.profile.generation_date}", Inches(0.8),
              Inches(6.6), Inches(11.7), Inches(0.5), 14, _PRIMARY)

    def bullets(title, items, sub=""):
        sl = prs.slides.add_slide(blank)
        _band(sl, 0, 0, Inches(1.1), _DARK)
        _text(sl, title, Inches(0.6), Inches(0.2), Inches(12), Inches(0.8), 28, _WHITE, bold=True)
        if sub:
            _text(sl, sub, Inches(0.6), Inches(1.2), Inches(12), Inches(0.5), 16, _PRIMARY)
        box = sl.shapes.add_textbox(Inches(0.7), Inches(1.8), Inches(12), Inches(5.3))
        tf = box.text_frame; tf.word_wrap = True
        for i, it in enumerate(items[:8] or ["—"]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"• {it}"; p.font.size = Pt(18); p.font.color.rgb = _DARK

    title_slide()
    bullets("Sommaire" if fr else "Agenda",
            ["1. " + ("Vision, but et objectif" if fr else "Vision, goal & objective"),
             "2. " + ("Analyse FFOM (forces, faiblesses, opportunités, menaces)" if fr
                      else "SWOT analysis"),
             "3. " + ("Causes profondes et obstacles" if fr else "Root causes & obstacles"),
             "4. " + ("Objectifs stratégiques prioritaires" if fr else "Priority strategic objectives"),
             "5. " + ("Interventions prioritaires" if fr else "Priority interventions"),
             "6. " + ("Cadre de suivi et évaluation" if fr else "M&E framework"),
             "7. " + ("Calendrier et activités" if fr else "Timeline & activities"),
             "8. " + ("Conditions de succès et prochaines étapes" if fr else "Success factors & next steps")])
    bullets("Résumé exécutif" if fr else "Executive summary",
            [s.vision.overall_objective or "—",
             f"{len(s.objectives)} {'objectifs' if fr else 'objectives'} · "
             f"{len(s.interventions)} {'interventions' if fr else 'interventions'}"])
    bullets("Vision, but et objectif" if fr else "Vision, goal & objective",
            [f"Vision: {s.vision.vision}", f"{'But' if fr else 'Goal'}: {s.vision.goal}",
             f"{'Objectif' if fr else 'Objective'}: {s.vision.overall_objective}"])

    strengths, weaknesses, opps, threats = [], [], [], []
    for x in s.swot:
        strengths += x.strengths; weaknesses += x.weaknesses
        opps += x.opportunities; threats += x.threats
    bullets("Principales forces et faiblesses" if fr else "Key strengths & weaknesses",
            [f"+ {w}" for w in strengths[:4]] + [f"- {w}" for w in weaknesses[:4]])
    bullets("Opportunités et menaces" if fr else "Opportunities & threats",
            [f"O {w}" for w in opps[:4]] + [f"M {w}" for w in threats[:4]])
    bullets("Obstacles et objectifs stratégiques" if fr else "Obstacles & strategic objectives",
            [o.objective_text for o in s.objectives])
    bullets("Interventions prioritaires" if fr else "Priority interventions",
            [f"[{getattr(iv.priority_level,'value',iv.priority_level)}] {iv.title}"
             for iv in s.interventions])
    bullets("Cadre de suivi et évaluation" if fr else "M&E framework",
            [f"{ind.name} — base: {ind.baseline}" for ind in s.indicators])
    bullets("Calendrier stratégique sur 5 ans" if fr else "5-year strategic timeline",
            [f"{y}: {sum(1 for a in s.activities if a.years.get(f'Y{i+1}'))} "
             f"{'activités' if fr else 'activities'}" for i, y in enumerate(s.profile.years)])
    bullets("Conditions de succès" if fr else "Conditions for success",
            ["Engagement politique et financement durable" if fr else "Political commitment & sustainable financing",
             "Coordination des partenaires" if fr else "Partner coordination",
             "Données de qualité et suivi" if fr else "Quality data & monitoring"])
    bullets("Prochaines étapes" if fr else "Next steps",
            ["Validation par le Ministère de la Santé" if fr else "MoH validation",
             "Chiffrage (NIS.COST)" if fr else "Costing (NIS.COST)",
             "Plan opérationnel annuel" if fr else "Annual operational plan"])

    buf = BytesIO(); prs.save(buf)
    return buf.getvalue()


def _band(sl, x, y, h, color):
    shape = sl.shapes.add_shape(1, Inches(0) if x == 0 else x, y, Inches(13.333), h)
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def _text(sl, text, x, y, w, h, size, color, bold=False, align=PP_ALIGN.LEFT):
    box = sl.shapes.add_textbox(x, y, w, h); tf = box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return box
