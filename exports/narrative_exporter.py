"""Step 11/12 exports:
- build_narrative_word: full AI-written NIS narrative report (prose per section + key tables).
- build_financial_word: financial report generated from NIS.COST data.
- build_qa_word: AI quality-assurance report, with issues to fix marked in RED.
All premium, with cover (WHO logo + Dian K Pro credit), auto clickable TOC and page numbers.
"""
from __future__ import annotations
import re
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


def _add_rich(paragraph, text):
    """Add text to a paragraph, rendering **bold** markdown as real bold runs."""
    for part in re.split(r"(\*\*.+?\*\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            paragraph.add_run(part[2:-2]).bold = True
        else:
            paragraph.add_run(part.replace("**", ""))


def _clean_head(t):
    return t.strip().lstrip("#").strip().replace("**", "").strip("* ")


def _prose(doc, text):
    """Render AI prose: '## '/'### ' -> Heading 2/3, '- ' -> bullets, **bold** -> bold runs."""
    for raw in (text or "").split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#### ") or line.startswith("### "):
            _H(doc, _clean_head(line), 3, numbered_break=False)
        elif line.startswith("## ") or line.startswith("# "):
            _H(doc, _clean_head(line), 2, numbered_break=False)
        elif line[:2] in ("- ", "* ") or line.startswith("• "):
            _add_rich(doc.add_paragraph(style="List Bullet"), line[2:].strip())
        else:
            _add_rich(doc.add_paragraph(), line)


def _caption(doc, text):
    p = doc.add_paragraph(); r = p.add_run(text)
    r.italic = True; r.font.size = Pt(9); r.font.color.rgb = _PRIMARY
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _num(v):
    try:
        return float(str(v).replace("%", "").replace(",", ".").strip())
    except Exception:
        return None


def _chart(doc, kind, s, fr):
    """Embed a matplotlib chart (guarded — skipped if matplotlib is unavailable)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    years = s.profile.years
    fig = None
    try:
        if kind == "targets":
            inds = [i for i in s.indicators if any(_num(i.targets.get(f"Y{k+1}")) is not None
                                                   for k in range(len(years)))][:4]
            if not inds:
                return
            fig, ax = plt.subplots(figsize=(6.6, 3.2))
            for i in inds:
                ys = [_num(i.targets.get(f"Y{k+1}")) for k in range(len(years))]
                ax.plot(years, ys, marker="o", label=(i.name[:32] + ("…" if len(i.name) > 32 else "")))
            ax.set_title("Cibles des indicateurs par année" if fr else "Indicator targets by year")
            ax.legend(fontsize=7, loc="best"); ax.grid(alpha=.3)
        elif kind == "priority":
            from collections import Counter
            c = Counter(str(getattr(iv.priority_level, "value", iv.priority_level)) for iv in s.interventions)
            if not c:
                return
            labels = {"high": "Élevée", "medium": "Moyenne", "low": "Faible"} if fr else \
                     {"high": "High", "medium": "Medium", "low": "Low"}
            keys = [k for k in ("high", "medium", "low") if c.get(k)]
            fig, ax = plt.subplots(figsize=(5.2, 3.0))
            ax.bar([labels.get(k, k) for k in keys], [c[k] for k in keys],
                   color=["#2E7D32", "#EF6C00", "#909CA8"][:len(keys)])
            ax.set_title("Interventions par niveau de priorité" if fr else "Interventions by priority")
        elif kind == "activities":
            counts = [sum(1 for a in s.activities if a.years.get(f"Y{k+1}")) for k in range(len(years))]
            if not any(counts):
                return
            fig, ax = plt.subplots(figsize=(5.6, 3.0))
            ax.bar([str(y) for y in years], counts, color="#0093D5")
            ax.set_title("Activités par année" if fr else "Activities by year")
        if fig is None:
            return
        fig.tight_layout()
        buf = BytesIO(); fig.savefig(buf, format="png", dpi=130); plt.close(fig); buf.seek(0)
        doc.add_picture(buf, width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    except Exception:
        try:
            plt.close("all")
        except Exception:
            pass


def _new_doc(s):
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(11)
    for sec in doc.sections:   # 1-inch margins on all four sides
        sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Inches(1)
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


def _seq_caption(doc, label, title):
    """Numbered caption ('Tableau 1. …' / 'Figure 1. …') via a SEQ field, so Word can build
    the lists of tables/figures automatically."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles["Caption"]
    except Exception:
        pass
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{label} "); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = _PRIMARY
    _field(p, f"SEQ {label} \\* ARABIC", "1")
    r2 = p.add_run(f". {title}"); r2.font.size = Pt(9); r2.italic = True
    return p


def _list_of(doc, heading, label):
    _H(doc, heading, 2, numbered_break=False)
    p = doc.add_paragraph()
    _field(p, f'TOC \\h \\z \\c "{label}"', "(se met à jour à l’ouverture)")


def _titled_table(doc, title, headers, rows):
    _seq_caption(doc, "Tableau", title)
    _mini_table(doc, headers, rows)


# --------------------------------------------------------------------------- #
def build_narrative_word(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    years = s.profile.years
    doc = _new_doc(s)
    _cover(doc, s, "Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy")
    _toc(doc, fr)
    # ---- Front matter: abbreviations/glossary + lists of tables & figures ----
    _H(doc, "Sigles et abréviations" if fr else "Abbreviations", 1)
    _mini_table(doc, ["Sigle" if fr else "Acronym", "Signification" if fr else "Meaning"],
                [("PEV", "Programme Élargi de Vaccination"), ("SNV", "Stratégie Nationale de Vaccination"),
                 ("FFOM", "Forces, Faiblesses, Opportunités, Menaces"), ("S&E", "Suivi et Évaluation"),
                 ("IA2030", "Immunization Agenda 2030"), ("Gavi", "Alliance mondiale pour les vaccins"),
                 ("MAPI", "Manifestation Post-Immunisation"), ("MEV", "Maladie Évitable par la Vaccination"),
                 ("SSP", "Soins de Santé Primaires"), ("OPS", "Objectif Prioritaire Stratégique"),
                 ("POA", "Plan Opérationnel Annuel"), ("RSS", "Renforcement du Système de Santé")]
                if fr else
                [("EPI", "Expanded Programme on Immunization"), ("NIS", "National Immunization Strategy"),
                 ("SWOT", "Strengths, Weaknesses, Opportunities, Threats"), ("M&E", "Monitoring & Evaluation"),
                 ("IA2030", "Immunization Agenda 2030"), ("Gavi", "Global Alliance for Vaccines"),
                 ("AEFI", "Adverse Event Following Immunization"), ("VPD", "Vaccine-Preventable Disease"),
                 ("PHC", "Primary Health Care"), ("AOP", "Annual Operational Plan")])
    _list_of(doc, "Liste des tableaux" if fr else "List of tables", "Tableau")
    _list_of(doc, "Liste des figures" if fr else "List of figures", "Figure")
    doc.add_page_break()
    from core.epi_components import EPI_COMPONENTS, find_subcomponent
    sw_by = {x.subcomponent_code: x for x in s.swot}
    fig_n = [0]

    def figure(kind, cap):
        before = len(doc.inline_shapes)
        _chart(doc, kind, s, fr)
        if len(doc.inline_shapes) > before:
            _seq_caption(doc, "Figure", cap)

    for n, (key, tfr, ten) in enumerate(NARRATIVE_SECTIONS, 1):
        _H(doc, f"{n}. {tfr if fr else ten}", 1)
        _prose(doc, s.narrative.get(key, "") or ("À compléter par l’équipe pays" if fr
                                                  else "To be completed by the country team"))
        # ---- section tables & figures ----
        if key == "situation" and s.swot:
            def _cell(items):  # all items, joined; capped only to avoid an oversized cell
                txt = " ; ".join(x for x in items if x)
                return (txt[:600] + "…") if len(txt) > 600 else (txt or "—")
            rows = []
            for c in EPI_COMPONENTS:
                for sub in c.subcomponents:   # ALL 26 subcomponents (complete)
                    it = sw_by.get(sub.code)
                    rows.append([sub.label(s.profile.language),
                                 _cell(it.strengths) if it else "—", _cell(it.weaknesses) if it else "—",
                                 _cell(it.opportunities) if it else "—", _cell(it.threats) if it else "—"])
            _titled_table(doc, "Synthèse FFOM par sous-composante" if fr else "SWOT summary by subcomponent",
                          ["Sous-composante" if fr else "Subcomponent", "Forces", "Faiblesses",
                           "Opportunités", "Menaces"], rows)
        if key == "objectives" and s.objectives:
            _titled_table(doc, "Objectifs stratégiques prioritaires" if fr else "Priority strategic objectives",
                          ["ID", "Objectif" if fr else "Objective", "Obstacle principal" if fr else "Main obstacle"],
                          [[o.obj_id, o.objective_text, o.main_obstacle] for o in s.objectives])
        if key == "interventions" and s.interventions:
            _titled_table(doc, "Interventions prioritaires et calendrier" if fr else "Priority interventions",
                          ["Intervention", "Priorité" if fr else "Priority", "Calendrier" if fr else "Timeline"],
                          [[iv.title, getattr(iv.priority_level, "value", iv.priority_level),
                            ", ".join(str(years[k]) for k in range(len(years)) if iv.timeline.get(f"Y{k+1}"))]
                           for iv in s.interventions])
            figure("priority", "Répartition des interventions par priorité" if fr
                   else "Interventions by priority")
        if key == "me" and s.indicators:
            cols = ["Indicateur" if fr else "Indicator", "Base" if fr else "Baseline"] + [str(y) for y in years]
            _titled_table(doc, "Indicateurs de suivi-évaluation et cibles" if fr else "M&E indicators and targets",
                          cols, [[i.name, i.baseline] + [i.targets.get(f"Y{k+1}", "")
                                 for k in range(len(years))] for i in s.indicators])
            figure("targets", "Évolution des cibles par année" if fr else "Targets by year")
        if key == "implementation" and s.activities:
            figure("activities", "Activités programmées par année" if fr else "Activities by year")

    if s.financial_report:
        _H(doc, f"{len(NARRATIVE_SECTIONS)+1}. " + ("Rapport financier" if fr else "Financial report"), 1)
        _prose(doc, s.financial_report)

    # ===================== ANNEXES =====================
    _H(doc, ("Annexes" if fr else "Annexes"), 1)
    _H(doc, "Annexe A — Chronogramme des activités" if fr else "Annex A — Activity timeline", 2)
    if s.activities:
        _titled_table(doc, "Chronogramme des activités" if fr else "Activity timeline",
                      ["Activité" if fr else "Activity", "Niveau" if fr else "Level",
                       "Responsable" if fr else "Lead", "Années" if fr else "Years"],
                      [[a.activity, a.implementation_level, a.lead,
                        ", ".join(str(years[k]) for k in range(len(years)) if a.years.get(f"Y{k+1}"))]
                       for a in s.activities])
    else:
        doc.add_paragraph("À compléter." if fr else "To be completed.")
    _H(doc, "Annexe B — Cadre de S&E détaillé" if fr else "Annex B — Detailed M&E framework", 2)
    if s.indicators:
        _titled_table(doc, "Cadre de S&E détaillé" if fr else "Detailed M&E framework",
                      ["Indicateur" if fr else "Indicator", "Type", "Définition" if fr else "Definition",
                       "Source" if fr else "Source", "Fréquence" if fr else "Frequency"],
                      [[i.name, str(i.indicator_type), i.definition, i.data_source, i.frequency]
                       for i in s.indicators])
    else:
        doc.add_paragraph("À compléter." if fr else "To be completed.")
    _H(doc, "Annexe C — Analyse des causes profondes" if fr else "Annex C — Root-cause analysis", 2)
    if s.root_causes:
        _titled_table(doc, "Analyse des causes profondes" if fr else "Root-cause analysis",
                      ["Faiblesse" if fr else "Weakness", "POURQUOI" if fr else "WHYs",
                       "Cause profonde" if fr else "Root cause"],
                      [[rc.weakness, " → ".join(rc.whys), rc.final_why] for rc in s.root_causes[:40]])
    else:
        doc.add_paragraph("À compléter." if fr else "To be completed.")
    _H(doc, "Annexe D — Sources et références" if fr else "Annex D — Sources and references", 2)
    for d in s.documents:
        doc.add_paragraph(f"{d.name} ({d.doc_category})", style="List Bullet")
    if not s.documents:
        doc.add_paragraph("À compléter." if fr else "To be completed.")

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
