"""Step 11/12 exports:
- build_narrative_word: full AI-written NIS narrative report (prose per section + key tables).
- build_financial_word: financial report generated from NIS.COST data.
- build_qa_word: AI quality-assurance report, with issues to fix marked in RED.
All premium, with cover (WHO logo + Dian K Pro credit), auto clickable TOC and page numbers.
"""
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
from core.branding import logo_path, dk_logo_path, dk_credit
from core.ai_engine import NARRATIVE_SECTIONS

_DARK = RGBColor.from_string(INSTITUTION_DARK.lstrip("#"))
_PRIMARY = RGBColor.from_string(INSTITUTION_PRIMARY.lstrip("#"))
_GOLD = RGBColor.from_string("8A6D1B")
_RED = RGBColor.from_string("C00000")
_HEX_DARK = INSTITUTION_DARK.lstrip("#")


def _field(p, instr, placeholder=""):
    run = p.add_run()
    for kind, txt in (("begin", None), ("instr", instr), ("separate", None), ("text", placeholder), ("end", None)):
        if kind == "instr":
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = txt
        elif kind == "text":
            el = OxmlElement("w:t"); el.text = txt
        else:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), kind)
        run._r.append(el)


def _update_fields(doc):
    upd = OxmlElement("w:updateFields"); upd.set(qn("w:val"), "true")
    doc.settings.element.append(upd)


def _footer(section, txt):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(txt + "    ·    ").font.size = Pt(8)
    _field(p, "PAGE", "1")


def _cover(doc, s, title):
    fr = s.profile.language == "fr"
    lp = logo_path(s.profile.language)
    if lp:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            p.add_run().add_picture(str(lp), width=Inches(2.7))
        except Exception:
            pass
    for _ in range(3):
        doc.add_paragraph()
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title); r.bold = True; r.font.size = Pt(28); r.font.color.rgb = _DARK
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{s.profile.country_name} · {period}"); r.font.size = Pt(16); r.font.color.rgb = _PRIMARY
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"\n{s.profile.ministry_name}\n{s.profile.epi_programme_name}\n{s.profile.generation_date}").font.size = Pt(12)
    for _ in range(2):
        doc.add_paragraph()
    dk = dk_logo_path()
    if dk:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            p.add_run().add_picture(str(dk), width=Inches(0.7))
        except Exception:
            pass
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(dk_credit(s.profile.language)); r.italic = True; r.font.size = Pt(10); r.font.color.rgb = _GOLD
    doc.add_page_break()


def _H(doc, text, level, numbered_break=True):
    if level == 1 and numbered_break:
        doc.add_page_break()
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.color.rgb = _DARK if level <= 1 else _PRIMARY
    return h


def _toc(doc, fr):
    _H(doc, "Table des matières" if fr else "Table of contents", 1, numbered_break=False)
    p = doc.add_paragraph()
    _field(p, 'TOC \\o "1-2" \\h \\z \\u',
           "Se met à jour à l’ouverture (clic droit → Mettre à jour les champs)." if fr
           else "Updates on open (right-click → Update field).")
    doc.add_page_break()


def _prose(doc, text):
    for para in (text or "").split("\n"):
        if para.strip():
            doc.add_paragraph(para.strip())


def _new_doc(s):
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(11)
    fr = s.profile.language == "fr"
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    _footer(doc.sections[0], (f"SNV {s.profile.country_name} · {period}" if fr
                              else f"NIS {s.profile.country_name} · {period}"))
    return doc


def _mini_table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor.from_string("FFFFFF")
        r.font.size = Pt(9)
        tcPr = c._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), _HEX_DARK); tcPr.append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; cells[i].paragraphs[0].add_run("" if v is None else str(v)).font.size = Pt(9)


# --------------------------------------------------------------------------- #
def build_narrative_word(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    years = s.profile.years
    doc = _new_doc(s)
    _cover(doc, s, "Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy")
    _toc(doc, fr)
    for n, (key, tfr, ten) in enumerate(NARRATIVE_SECTIONS, 1):
        _H(doc, f"{n}. {tfr if fr else ten}", 1)
        _prose(doc, s.narrative.get(key, "") or ("À compléter par l’équipe pays" if fr
                                                  else "To be completed by the country team"))
        if key == "me" and s.indicators:
            cols = ["Indicateur" if fr else "Indicator", "Base" if fr else "Baseline"] + [str(y) for y in years]
            _mini_table(doc, cols, [[i.name, i.baseline] + [i.targets.get(f"Y{k+1}", "")
                        for k in range(len(years))] for i in s.indicators])
        if key == "implementation" and s.activities:
            _mini_table(doc, ["Activité" if fr else "Activity", "Niveau" if fr else "Level",
                              "Responsable" if fr else "Lead"],
                        [[a.activity, a.implementation_level, a.lead] for a in s.activities])
    if s.financial_report:
        _H(doc, "Rapport financier" if fr else "Financial report", 1)
        _prose(doc, s.financial_report)
    _update_fields(doc)
    buf = BytesIO(); doc.save(buf); return buf.getvalue()


def build_financial_word(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    doc = _new_doc(s)
    _cover(doc, s, "Rapport financier de la SNV (NIS.COST)" if fr else "NIS financial report (NIS.COST)")
    _H(doc, "Rapport financier" if fr else "Financial report", 1)
    _prose(doc, s.financial_report or ("À générer à partir du fichier NIS.COST." if fr
                                       else "To be generated from the NIS.COST file."))
    _update_fields(doc); buf = BytesIO(); doc.save(buf); return buf.getvalue()


def build_qa_word(s: NISStrategy, qa: dict) -> bytes:
    """QA report: issues to add/improve are marked in RED."""
    fr = s.profile.language == "fr"
    doc = _new_doc(s)
    _cover(doc, s, "Rapport d’assurance qualité de la SNV" if fr else "NIS quality-assurance report")
    _H(doc, ("Synthèse et score" if fr else "Summary and score"), 1)
    p = doc.add_paragraph()
    r = p.add_run(f"{'Score global' if fr else 'Overall score'} : {qa.get('score', '—')}/100")
    r.bold = True; r.font.size = Pt(14); r.font.color.rgb = _DARK
    doc.add_paragraph(qa.get("overall", ""))
    _H(doc, ("Points à ajouter / améliorer (en rouge)" if fr else "Items to add / improve (in red)"), 1)
    findings = qa.get("findings", []) or []
    order = {"critique": 0, "critical": 0, "majeur": 1, "major": 1, "mineur": 2, "minor": 2}
    for f in sorted(findings, key=lambda x: order.get(str(x.get("severity", "")).lower(), 3)):
        sev = str(f.get("severity", "")).lower()
        red = sev in ("critique", "critical", "majeur", "major")
        p = doc.add_paragraph(style="List Bullet")
        head = p.add_run(f"[{f.get('severity', '')}] {f.get('section', '')} — {f.get('issue', '')}")
        head.bold = True
        if red:
            head.font.color.rgb = _RED
        rec = doc.add_paragraph()
        rr = rec.add_run(f"→ {('Recommandation' if fr else 'Recommendation')} : {f.get('recommendation', '')}")
        if red:
            rr.font.color.rgb = _RED
    if not findings:
        doc.add_paragraph("Aucun problème majeur détecté." if fr else "No major issue detected.")
    _update_fields(doc); buf = BytesIO(); doc.save(buf); return buf.getvalue()
