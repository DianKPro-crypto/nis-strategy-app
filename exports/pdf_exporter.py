"""PDF export (ReportLab) — complete paginated report with header/footer, page numbers,
logo, and properly-wrapping table cells (no overlapping text)."""
from __future__ import annotations
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, ListFlowable, ListItem)

from config.settings import INSTITUTION_DARK, INSTITUTION_PRIMARY
from core.models import NISStrategy
from core.epi_components import EPI_COMPONENTS, find_subcomponent
from core.branding import logo_path

_DARK = colors.HexColor(INSTITUTION_DARK)
_PRIMARY = colors.HexColor(INSTITUTION_PRIMARY)
_AVAIL = A4[0] - 4 * cm  # usable width (2cm margins)


def _esc(v) -> str:
    return (str(v if v is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_pdf(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    buf = BytesIO()
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    header = (f"SNV {s.profile.country_name} {period}" if fr else f"NIS {s.profile.country_name} {period}")
    lp = logo_path(s.profile.language)
    years = s.profile.years

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=_DARK, spaceBefore=10, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=_PRIMARY, spaceBefore=8, spaceAfter=4)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], textColor=_DARK, fontSize=10,
                        spaceBefore=5, spaceAfter=2)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=4)
    cell = ParagraphStyle("cell", parent=styles["BodyText"], fontSize=8, leading=10, spaceAfter=0)
    cellh = ParagraphStyle("cellh", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")
    ph = "À compléter par l’équipe pays" if fr else "To be completed by the country team"

    def P(text, st=body):
        return Paragraph(_esc(text) or "", st)

    def cellpar(text_or_list, st=cell):
        if isinstance(text_or_list, (list, tuple)):
            txt = "<br/>".join(f"• {_esc(str(x)[:240])}" for x in list(text_or_list)[:8] if x)
        else:
            txt = _esc(str(text_or_list)[:600])
        return Paragraph(txt or "—", st)

    def table(header_cells, rows, widths):
        data = [[Paragraph(_esc(h), cellh) for h in header_cells]]
        data += rows
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _DARK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B9C6D4")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F8")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return t

    def _decorate(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_DARK)
        if lp:
            try:
                canvas.drawImage(str(lp), 2 * cm, A4[1] - 1.9 * cm, width=3.2 * cm, height=0.85 * cm,
                                 preserveAspectRatio=True, mask="auto")
            except Exception:
                pass
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.15 * cm, header)
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.5 * cm, s.profile.generation_date)
        canvas.setStrokeColor(_PRIMARY)
        canvas.line(2 * cm, A4[1] - 2.0 * cm, A4[0] - 2 * cm, A4[1] - 2.0 * cm)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"{doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2.6 * cm, bottomMargin=2 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm, title=header)
    story = []

    def sec(t):
        story.append(Paragraph(t, h1))

    def bullets(items):
        items = [x for x in items if x and str(x).strip()]
        if not items:
            story.append(P(ph)); return
        story.append(ListFlowable([ListItem(P(x), leftIndent=10) for x in items],
                                  bulletType="bullet", start="•"))

    # ---- Cover ----
    story += [Spacer(1, 5 * cm),
              Paragraph(("Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy"),
                        ParagraphStyle("t", parent=h1, fontSize=24, alignment=1, textColor=_DARK)),
              Spacer(1, 0.4 * cm),
              Paragraph(f"{_esc(s.profile.country_name)} · {period}",
                        ParagraphStyle("t2", parent=body, fontSize=14, alignment=1)),
              Spacer(1, 0.3 * cm),
              Paragraph(f"{_esc(s.profile.ministry_name)}<br/>{_esc(s.profile.epi_programme_name)}"
                        f"<br/>{_esc(s.profile.generation_date)}",
                        ParagraphStyle("t3", parent=body, alignment=1)),
              PageBreak()]

    # ---- Executive summary ----
    sec("Résumé exécutif" if fr else "Executive summary")
    story.append(P(s.vision.overall_objective or ph))
    story.append(P(f"{'Objectifs' if fr else 'Objectives'}: {len(s.objectives)} · "
                   f"{'Interventions' if fr else 'Interventions'}: {len(s.interventions)} · "
                   f"{'Indicateurs' if fr else 'Indicators'}: {len(s.indicators)} · "
                   f"{'Activités' if fr else 'Activities'}: {len(s.activities)}"))

    # ---- Vision ----
    sec("Vision, but et objectif" if fr else "Vision, goal & objective")
    for lbl, v in [("Vision", s.vision.vision), ("But de la SNV" if fr else "NIS goal", s.vision.goal),
                   ("Objectif général" if fr else "Overall objective", s.vision.overall_objective)]:
        story += [Paragraph(lbl, h2), P(v or ph)]

    # ---- SWOT (flowing text per subcomponent — wraps and splits safely across pages) ----
    sec("Analyse FFOM (FFOM/SWOT)" if fr else "SWOT analysis")
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
        story.append(Paragraph(comp.label(s.profile.language), h2))
        for sub in subs_with:
            it = sw_by[sub.code]
            story.append(Paragraph(_esc(sub.label(s.profile.language)), h3))
            for label, attr in quad:
                vals = getattr(it, attr)
                if vals:
                    story.append(Paragraph(f"<b>{label} :</b> " + "; ".join(_esc(v) for v in vals), body))

    # ---- Root causes ----
    story.append(PageBreak())
    sec("Analyse des causes profondes" if fr else "Root cause analysis")
    if s.root_causes:
        bullets([f"{rc.weakness} → {' → '.join(rc.whys)} ⇒ {rc.final_why}" for rc in s.root_causes])
    else:
        story.append(P(ph))

    # ---- Obstacles & objectives ----
    sec("Obstacles et objectifs stratégiques" if fr else "Obstacles & strategic objectives")
    for o in s.objectives:
        story += [Paragraph(_esc(o.objective_text) or o.obj_id, h2)]
        story.append(P(f"{'Obstacle' if fr else 'Obstacle'} : {o.main_obstacle}"))
        story.append(P(f"{'Résultat visionnaire' if fr else 'Visionary result'} : {o.visionary_result}"))
    if not s.objectives:
        story.append(P(ph))

    # ---- Interventions ----
    story.append(PageBreak())
    sec("Interventions prioritaires" if fr else "Priority interventions")
    if s.interventions:
        cols_iv = [5.0 * cm, 2.2 * cm, _AVAIL - 7.2 * cm]
        rows = [[cellpar(iv.title), cellpar(getattr(iv.priority_level, "value", str(iv.priority_level))),
                 cellpar(iv.rationale or iv.expected_impact)] for iv in s.interventions]
        story.append(table(["Intervention", "Priorité" if fr else "Priority",
                            "Justification / impact" if fr else "Rationale / impact"], rows, cols_iv))
    else:
        story.append(P(ph))

    # ---- M&E ----
    story.append(PageBreak())
    sec("Cadre de suivi et d’évaluation" if fr else "M&E framework")
    if s.indicators:
        base_cols = ["Indicateur", "Type", "Base" if fr else "Baseline"]
        ycols = [str(y) for y in years]
        nyear = len(ycols)
        wfix = 6.0 * cm + 1.8 * cm + 2.2 * cm
        yw = max(1.1 * cm, (_AVAIL - wfix) / max(1, nyear))
        cols_me = [6.0 * cm, 1.8 * cm, 2.2 * cm] + [yw] * nyear
        rows = []
        for ind in s.indicators:
            row = [cellpar(ind.name), cellpar(str(ind.indicator_type)), cellpar(ind.baseline)]
            row += [cellpar(ind.targets.get(f"Y{i+1}", "")) for i in range(nyear)]
            rows.append(row)
        story.append(table(base_cols + ycols, rows, cols_me))
    else:
        story.append(P(ph))

    # ---- Activities ----
    story.append(PageBreak())
    sec("Activités opérationnelles" if fr else "Operational activities")
    if s.activities:
        cols_a = [9.0 * cm, 3.5 * cm, _AVAIL - 12.5 * cm]
        rows = []
        for a in s.activities:
            yrs = ", ".join(str(years[i]) for i in range(len(years)) if a.years.get(f"Y{i+1}"))
            rows.append([cellpar(a.activity), cellpar(a.implementation_level), cellpar(yrs or "—")])
        story.append(table(["Activité clé" if fr else "Key activity",
                            "Niveau" if fr else "Level", "Années" if fr else "Years"], rows, cols_a))
    else:
        story.append(P(ph))

    # ---- Sources ----
    sec("Sources utilisées" if fr else "Sources used")
    bullets([f"{d.name} ({d.doc_category})" for d in s.documents])

    doc.build(story, onFirstPage=_decorate, onLaterPages=_decorate)
    return buf.getvalue()
