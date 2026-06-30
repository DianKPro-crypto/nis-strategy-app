"""Word (.docx) export — premium narrative report with an automatic, clickable Table of
Contents (TOC field, hyperlinked, auto-updates on open), cover page, headers/footers with
page numbers, acronyms, and all NIS sections. Submission-ready for MoH/WHO/Gavi/UNICEF."""
from __future__ import annotations
from io import BytesIO

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from config.settings import INSTITUTION_DARK, INSTITUTION_PRIMARY
from core.models import NISStrategy
from core.epi_components import EPI_COMPONENTS
from core.branding import logo_path

_DARK = RGBColor.from_string(INSTITUTION_DARK.lstrip("#"))
_PRIMARY = RGBColor.from_string(INSTITUTION_PRIMARY.lstrip("#"))
_HEX_DARK = INSTITUTION_DARK.lstrip("#")


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _shade(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _field(paragraph, instr: str, placeholder: str = ""):
    """Insert a Word field (e.g. TOC, PAGE) that the app/Word evaluates."""
    run = paragraph.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = placeholder
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (b, it, sep, t, end):
        run._r.append(el)


def _enable_update_fields(doc):
    """Make Word refresh the TOC (and page fields) automatically when the file opens."""
    settings = doc.settings.element
    upd = OxmlElement("w:updateFields"); upd.set(qn("w:val"), "true")
    settings.append(upd)


def _heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = _DARK if level <= 1 else _PRIMARY
    return h


def _table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        run = c.paragraphs[0].add_run(h); run.bold = True; run.font.color.rgb = RGBColor.from_string("FFFFFF")
        run.font.size = Pt(9)
        _shade(c, _HEX_DARK)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            run = p.add_run("" if val is None else str(val)); run.font.size = Pt(9)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    return t


def _page_footer(section, left_text):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(left_text + "    ·    ").font.size = Pt(8)
    _field(p, "PAGE", "1")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def build_word(s: NISStrategy) -> bytes:
    lang = s.profile.language
    fr = lang == "fr"
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    years = s.profile.years
    ph = "À compléter par l’équipe pays" if fr else "To be completed by the country team"
    _page_footer(doc.sections[0], f"SNV {s.profile.country_name} {period}" if fr
                 else f"NIS {s.profile.country_name} {period}")

    # ---- Cover ----
    lp = logo_path(lang)
    if lp:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            p.add_run().add_picture(str(lp), width=Inches(2.8))
        except Exception:
            pass
    for _ in range(3):
        doc.add_paragraph()
    title = "Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy"
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title); r.bold = True; r.font.size = Pt(30); r.font.color.rgb = _DARK
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{s.profile.country_name} · {period}"); r.font.size = Pt(18); r.font.color.rgb = _PRIMARY
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"\n{s.profile.ministry_name}\n{s.profile.epi_programme_name}\n"
              f"{'Date' if fr else 'Date'} : {s.profile.generation_date}").font.size = Pt(12)
    doc.add_page_break()

    # ---- Table of contents (automatic + clickable) ----
    _heading(doc, "Table des matières" if fr else "Table of contents", 1)
    p = doc.add_paragraph()
    _field(p, 'TOC \\o "1-3" \\h \\z \\u',
           "La table des matières se met à jour à l’ouverture (sinon : clic droit → Mettre à jour les champs)."
           if fr else "The table of contents updates on open (else: right-click → Update field).")
    doc.add_page_break()

    # ---- Acronyms ----
    _heading(doc, "Acronymes" if fr else "Acronyms", 1)
    acro = [("PEV", "Programme Élargi de Vaccination"), ("SNV", "Stratégie Nationale de Vaccination"),
            ("FFOM", "Forces, Faiblesses, Opportunités, Menaces"), ("S&E", "Suivi et Évaluation"),
            ("IA2030", "Immunization Agenda 2030"), ("MAPI", "Manifestation Post-Immunisation"),
            ("MEV", "Maladie Évitable par la Vaccination")] if fr else \
           [("EPI", "Expanded Programme on Immunization"), ("NIS", "National Immunization Strategy"),
            ("SWOT", "Strengths, Weaknesses, Opportunities, Threats"), ("M&E", "Monitoring & Evaluation"),
            ("IA2030", "Immunization Agenda 2030"), ("AEFI", "Adverse Event Following Immunization"),
            ("VPD", "Vaccine-Preventable Disease")]
    _table(doc, ["Acronyme" if fr else "Acronym", "Signification" if fr else "Meaning"], acro,
           widths=[1.5, 4.5])
    doc.add_page_break()

    # ---- Executive summary / background / methodology ----
    _heading(doc, "Résumé exécutif" if fr else "Executive summary", 1)
    doc.add_paragraph(s.vision.overall_objective or ph)
    doc.add_paragraph(f"{'Objectifs stratégiques' if fr else 'Strategic objectives'} : {len(s.objectives)} · "
                      f"{'Interventions' if fr else 'Interventions'} : {len(s.interventions)} · "
                      f"{'Indicateurs' if fr else 'Indicators'} : {len(s.indicators)} · "
                      f"{'Activités' if fr else 'Activities'} : {len(s.activities)}")
    _heading(doc, "Contexte" if fr else "Background", 1)
    doc.add_paragraph(ph)
    _heading(doc, "Méthodologie" if fr else "Methodology", 1)
    doc.add_paragraph(
        ("Analyse situationnelle du PEV (7 composantes, 26 sous-composantes), analyse FFOM, analyse des "
         "causes profondes (méthode des POURQUOI), formulation des obstacles, théorie du changement, "
         "objectifs SMART, priorisation multicritère et cadre de S&E, conformément aux outils OMS/IA2030.")
        if fr else
        ("EPI situation analysis (7 components, 26 subcomponents), SWOT, root-cause analysis (5-Whys), "
         "obstacle formulation, theory of change, SMART objectives, multi-criteria prioritization and M&E, "
         "per WHO/IA2030 tools."))

    # ---- Vision ----
    _heading(doc, "Vision, but et objectif général" if fr else "Vision, goal and overall objective", 1)
    for label, val in [("Vision", s.vision.vision), ("But de la SNV" if fr else "NIS goal", s.vision.goal),
                       ("Objectif général" if fr else "Overall objective", s.vision.overall_objective)]:
        _heading(doc, label, 2)
        doc.add_paragraph(val or ph)

    # ---- SWOT ----
    _heading(doc, "Analyse FFOM (FFOM/SWOT)" if fr else "SWOT analysis", 1)
    sw_by = {x.subcomponent_code: x for x in s.swot}
    quad = [("Forces" if fr else "Strengths", "strengths"),
            ("Faiblesses" if fr else "Weaknesses", "weaknesses"),
            ("Opportunités" if fr else "Opportunities", "opportunities"),
            ("Menaces" if fr else "Threats", "threats")]
    for comp in EPI_COMPONENTS:
        subs_with = [sub for sub in comp.subcomponents
                     if (it := sw_by.get(sub.code)) and any([it.strengths, it.weaknesses,
                                                             it.opportunities, it.threats])]
        if not subs_with:
            continue
        _heading(doc, comp.label(lang), 2)
        for sub in subs_with:
            it = sw_by[sub.code]
            _heading(doc, sub.label(lang), 3)
            for label, attr in quad:
                vals = getattr(it, attr)
                if vals:
                    p = doc.add_paragraph()
                    p.add_run(f"{label} : ").bold = True
                    p.add_run("; ".join(vals))

    # ---- Root causes ----
    _heading(doc, "Analyse des causes profondes" if fr else "Root cause analysis", 1)
    for rc in s.root_causes:
        doc.add_paragraph(f"{rc.weakness} → {' → '.join(rc.whys)} ⇒ {rc.final_why}", style="List Bullet")
    if not s.root_causes:
        doc.add_paragraph(ph)

    # ---- Obstacles & objectives ----
    _heading(doc, "Obstacles et objectifs stratégiques" if fr else "Obstacles & strategic objectives", 1)
    for o in s.objectives:
        _heading(doc, o.objective_text or o.obj_id, 3)
        doc.add_paragraph(f"{'Obstacle' if fr else 'Obstacle'} : {o.main_obstacle}")
        doc.add_paragraph(f"{'Résultat visionnaire' if fr else 'Visionary result'} : {o.visionary_result}")
    if not s.objectives:
        doc.add_paragraph(ph)

    # ---- Interventions ----
    _heading(doc, "Interventions prioritaires" if fr else "Priority interventions", 1)
    for iv in s.interventions:
        _heading(doc, f"{iv.title}  [{getattr(iv.priority_level, 'value', iv.priority_level)}]", 3)
        for label, val in [("Objectif lié" if fr else "Linked objective", iv.objective_id),
                           ("Justification" if fr else "Rationale", iv.rationale),
                           ("Impact attendu" if fr else "Expected impact", iv.expected_impact),
                           ("Faisabilité" if fr else "Feasibility", iv.feasibility_note),
                           ("Prérequis" if fr else "Prerequisites", "; ".join(iv.prerequisites)),
                           ("Risques" if fr else "Risks", "; ".join(iv.risks)),
                           ("Partenaires" if fr else "Partners", "; ".join(iv.partners))]:
            if val:
                p = doc.add_paragraph(); p.add_run(f"{label} : ").bold = True; p.add_run(str(val))
    if not s.interventions:
        doc.add_paragraph(ph)

    # ---- M&E ----
    _heading(doc, "Cadre de suivi et d’évaluation" if fr else "Monitoring & evaluation framework", 1)
    if s.indicators:
        cols = ["Indicateur" if fr else "Indicator", "Type", "Base" if fr else "Baseline"] + [str(y) for y in years]
        rows = []
        for ind in s.indicators:
            rows.append([ind.name, str(ind.indicator_type), ind.baseline]
                        + [ind.targets.get(f"Y{i+1}", "") for i in range(len(years))])
        _table(doc, cols, rows)
    else:
        doc.add_paragraph(ph)

    # ---- Activities ----
    _heading(doc, "Activités opérationnelles" if fr else "Operational activities", 1)
    if s.activities:
        rows = []
        for a in s.activities:
            yrs = ", ".join(str(years[i]) for i in range(len(years)) if a.years.get(f"Y{i+1}"))
            rows.append([a.activity, a.implementation_level, a.lead, yrs])
        _table(doc, ["Activité clé" if fr else "Key activity", "Niveau" if fr else "Level",
                     "Responsable" if fr else "Lead", "Années" if fr else "Years"],
               rows, widths=[3.0, 1.6, 1.4, 1.0])
    else:
        doc.add_paragraph(ph)

    # ---- Sources & annexes ----
    _heading(doc, "Sources utilisées" if fr else "Sources used", 1)
    for d in s.documents:
        doc.add_paragraph(f"{d.name} ({d.doc_category})", style="List Bullet")
    if not s.documents:
        doc.add_paragraph(ph)
    _heading(doc, "Annexes" if fr else "Annexes", 1)
    doc.add_paragraph(ph)

    _enable_update_fields(doc)
    buf = BytesIO(); doc.save(buf)
    return buf.getvalue()
