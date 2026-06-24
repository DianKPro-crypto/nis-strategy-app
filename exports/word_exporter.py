"""Word (.docx) narrative report export — submission-ready for MoH/WHO/Gavi/UNICEF."""
from __future__ import annotations
from io import BytesIO

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from config.settings import INSTITUTION_DARK
from core.models import NISStrategy
from core.epi_components import EPI_COMPONENTS, find_subcomponent
from core.branding import logo_path

_DARK = RGBColor.from_string(INSTITUTION_DARK.lstrip("#"))


def build_word(s: NISStrategy) -> bytes:
    lang = s.profile.language
    fr = lang == "fr"
    doc = Document()
    _styles(doc)

    # ---- cover ----
    lp = logo_path(lang)
    if lp:
        lg = doc.add_paragraph(); lg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            lg.add_run().add_picture(str(lp), width=Inches(3.0))
        except Exception:
            pass
    title = "Stratégie Nationale de Vaccination (SNV)" if fr else "National Immunization Strategy (NIS)"
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title); run.bold = True; run.font.size = Pt(26); run.font.color.rgb = _DARK
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    sub.add_run(f"{s.profile.country_name} · {period}").font.size = Pt(16)
    meta = doc.add_paragraph(); meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"{s.profile.ministry_name}\n{s.profile.epi_programme_name}\n"
                 f"{'Date' if fr else 'Date'}: {s.profile.generation_date}")
    doc.add_page_break()

    # ---- table of contents (static headings) ----
    _h(doc, "Table des matières" if fr else "Table of contents", 1)
    toc = ["Résumé exécutif", "Contexte", "Méthodologie", "Vision, but et objectif",
           "Analyse FFOM", "Analyse des causes profondes", "Obstacles principaux",
           "Théorie du changement et objectifs stratégiques", "Interventions prioritaires",
           "Cadre de suivi et évaluation", "Activités opérationnelles", "Sources", "Annexes"]
    for i, item in enumerate(toc, 1):
        doc.add_paragraph(f"{i}. {item}", style="List Number" if False else None)
    doc.add_page_break()

    # ---- executive summary ----
    _h(doc, "Résumé exécutif" if fr else "Executive summary", 1)
    doc.add_paragraph(s.vision.overall_objective or _ph(fr))
    doc.add_paragraph(f"{'Objectifs stratégiques' if fr else 'Strategic objectives'}: "
                      f"{len(s.objectives)} · {'Interventions' if fr else 'Interventions'}: "
                      f"{len(s.interventions)} · {'Indicateurs' if fr else 'Indicators'}: {len(s.indicators)}.")

    # ---- background / methodology ----
    _h(doc, "Contexte" if fr else "Background", 1)
    doc.add_paragraph(_ph(fr))
    _h(doc, "Méthodologie" if fr else "Methodology", 1)
    doc.add_paragraph(
        ("Analyse situationnelle du PEV (7 composantes, 26 sous-composantes), analyse FFOM, analyse des "
         "causes profondes (méthode des POURQUOI), formulation des obstacles, théorie du changement, "
         "objectifs SMART, priorisation multicritère et cadre de S&E, conformément aux outils OMS/IA2030.")
        if fr else
        ("EPI situation analysis (7 components, 26 subcomponents), SWOT, root-cause analysis (5-Whys), "
         "obstacle formulation, theory of change, SMART objectives, multi-criteria prioritization and M&E, "
         "per WHO/IA2030 tools."))

    # ---- vision ----
    _h(doc, "Vision, but et objectif général" if fr else "Vision, goal and overall objective", 1)
    for label, val in [("Vision", s.vision.vision), ("But de la SNV" if fr else "NIS goal", s.vision.goal),
                       ("Objectif général" if fr else "Overall objective", s.vision.overall_objective)]:
        _h(doc, label, 2)
        doc.add_paragraph(val or _ph(fr))

    # ---- SWOT ----
    _h(doc, "Analyse FFOM (Forces, Faiblesses, Opportunités, Menaces)" if fr else "SWOT analysis", 1)
    sw_by = {(x.component_code, x.subcomponent_code): x for x in s.swot}
    for comp in EPI_COMPONENTS:
        _h(doc, comp.label(lang), 2)
        for sub in comp.subcomponents:
            x = sw_by.get((comp.code, sub.code))
            if not x or not any([x.strengths, x.weaknesses, x.opportunities, x.threats]):
                continue
            _h(doc, sub.label(lang), 3)
            t = doc.add_table(rows=1, cols=2); t.style = "Light Grid Accent 1"
            t.rows[0].cells[0].text = "Forces / Opportunités" if fr else "Strengths / Opportunities"
            t.rows[0].cells[1].text = "Faiblesses / Menaces" if fr else "Weaknesses / Threats"
            row = t.add_row().cells
            row[0].text = "\n".join([f"+ {w}" for w in x.strengths] + [f"O {w}" for w in x.opportunities])
            row[1].text = "\n".join([f"- {w}" for w in x.weaknesses] + [f"M {w}" for w in x.threats])

    # ---- root causes ----
    _h(doc, "Analyse des causes profondes" if fr else "Root cause analysis", 1)
    for rc in s.root_causes:
        doc.add_paragraph(f"• {rc.weakness} → {' → '.join(rc.whys)} ⇒ {rc.final_why}")

    # ---- obstacles + ToC + objectives ----
    _h(doc, "Obstacles principaux et objectifs stratégiques" if fr else
       "Main obstacles and strategic objectives", 1)
    for o in s.objectives:
        _h(doc, o.objective_text or o.obj_id, 3)
        doc.add_paragraph(f"{'Obstacle' if fr else 'Obstacle'}: {o.main_obstacle}")
        doc.add_paragraph(f"{'Résultat visionnaire' if fr else 'Visionary result'}: {o.visionary_result}")

    # ---- interventions ----
    _h(doc, "Interventions prioritaires" if fr else "Priority interventions", 1)
    t = doc.add_table(rows=1, cols=4); t.style = "Light Grid Accent 1"
    for c, h in zip(t.rows[0].cells, ["Intervention", "Objectif" if fr else "Objective",
                                      "Priorité" if fr else "Priority", "Impact"]):
        c.text = h
    for iv in s.interventions:
        cells = t.add_row().cells
        cells[0].text = iv.title; cells[1].text = iv.objective_id
        cells[2].text = getattr(iv.priority_level, "value", str(iv.priority_level))
        cells[3].text = iv.expected_impact

    # ---- M&E ----
    _h(doc, "Cadre de suivi et d’évaluation" if fr else "Monitoring & evaluation framework", 1)
    if s.indicators:
        cols = ["Indicateur", "Type", "Base" if fr else "Baseline"] + [f"{y}" for y in s.profile.years]
        t = doc.add_table(rows=1, cols=len(cols)); t.style = "Light Grid Accent 1"
        for c, h in zip(t.rows[0].cells, cols):
            c.text = str(h)
        for ind in s.indicators:
            cells = t.add_row().cells
            cells[0].text = ind.name; cells[1].text = str(ind.indicator_type)
            cells[2].text = ind.baseline
            for i in range(len(s.profile.years)):
                cells[3 + i].text = ind.targets.get(f"Y{i+1}", "")

    # ---- activities ----
    _h(doc, "Activités opérationnelles" if fr else "Operational activities", 1)
    for a in s.activities:
        doc.add_paragraph(f"• [{a.implementation_level}] {a.activity}", style=None)

    # ---- sources ----
    _h(doc, "Sources utilisées" if fr else "Sources used", 1)
    for d in s.documents:
        doc.add_paragraph(f"• {d.name} ({d.doc_category})")

    _h(doc, "Annexes" if fr else "Annexes", 1)
    doc.add_paragraph(_ph(fr))

    buf = BytesIO(); doc.save(buf)
    return buf.getvalue()


def _styles(doc):
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(11)


def _h(doc, text, level):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = _DARK
    return h


def _ph(fr):
    return "À compléter par l’équipe pays" if fr else "To be completed by the country team"
