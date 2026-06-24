"""PDF export (ReportLab) — paginated report with header/footer and page numbers."""
from __future__ import annotations
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak)

from config.settings import INSTITUTION_DARK, INSTITUTION_PRIMARY
from core.models import NISStrategy
from core.epi_components import EPI_COMPONENTS
from core.branding import logo_path

_DARK = colors.HexColor(INSTITUTION_DARK)
_PRIMARY = colors.HexColor(INSTITUTION_PRIMARY)


def build_pdf(s: NISStrategy) -> bytes:
    fr = s.profile.language == "fr"
    buf = BytesIO()
    period = f"{s.profile.nis_start_year}–{s.profile.nis_start_year + s.profile.nis_duration_years - 1}"
    header = f"SNV {s.profile.country_name} {period}" if fr else f"NIS {s.profile.country_name} {period}"
    lp = logo_path(s.profile.language)

    def _decorate(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_DARK)
        if lp:
            try:
                canvas.drawImage(str(lp), 2 * cm, A4[1] - 2.0 * cm, width=3.4 * cm,
                                 height=0.9 * cm, preserveAspectRatio=True, mask="auto")
            except Exception:
                pass
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.15 * cm, header)
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.55 * cm, s.profile.generation_date)
        canvas.setStrokeColor(_PRIMARY)
        canvas.line(2 * cm, A4[1] - 1.8 * cm, A4[0] - 2 * cm, A4[1] - 1.8 * cm)
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"{doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2.4 * cm, bottomMargin=2 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm, title=header)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=_DARK)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=_PRIMARY)
    body = styles["BodyText"]
    story = []

    title = "Stratégie Nationale de Vaccination" if fr else "National Immunization Strategy"
    story += [Spacer(1, 6 * cm),
              Paragraph(f"<b>{title}</b>", ParagraphStyle("t", parent=h1, fontSize=24, alignment=1)),
              Spacer(1, 0.5 * cm),
              Paragraph(f"{s.profile.country_name} · {period}",
                        ParagraphStyle("t2", parent=body, fontSize=14, alignment=1)),
              Spacer(1, 0.3 * cm),
              Paragraph(f"{s.profile.ministry_name}<br/>{s.profile.epi_programme_name}",
                        ParagraphStyle("t3", parent=body, alignment=1)),
              PageBreak()]

    def sec(t):
        story.append(Paragraph(t, h1))

    sec("Vision, but et objectif" if fr else "Vision, goal & objective")
    for lbl, v in [("Vision", s.vision.vision), ("But" if fr else "Goal", s.vision.goal),
                   ("Objectif général" if fr else "Overall objective", s.vision.overall_objective)]:
        story += [Paragraph(lbl, h2), Paragraph(_esc(v) or _ph(fr), body), Spacer(1, 0.2 * cm)]

    sec("Objectifs stratégiques prioritaires" if fr else "Priority strategic objectives")
    for o in s.objectives:
        story += [Paragraph(f"• {_esc(o.objective_text)}", body)]
    story.append(PageBreak())

    sec("Interventions prioritaires" if fr else "Priority interventions")
    data = [["Intervention", "Priorité" if fr else "Priority", "Impact"]]
    for iv in s.interventions:
        data.append([_esc(iv.title), getattr(iv.priority_level, "value", str(iv.priority_level)),
                     _esc(iv.expected_impact[:120])])
    if len(data) > 1:
        story.append(_table(data, [8 * cm, 2.5 * cm, 6 * cm]))
    story.append(PageBreak())

    sec("Cadre de S&E" if fr else "M&E framework")
    cols = ["Indicateur", "Base" if fr else "Baseline"] + [str(y) for y in s.profile.years]
    data = [cols]
    for ind in s.indicators:
        data.append([_esc(ind.name), _esc(ind.baseline)] +
                    [ind.targets.get(f"Y{i+1}", "") for i in range(len(s.profile.years))])
    if len(data) > 1:
        story.append(_table(data, None))

    sec("Sources" if fr else "Sources")
    for d in s.documents:
        story.append(Paragraph(f"• {_esc(d.name)} ({_esc(d.doc_category)})", body))

    doc.build(story, onFirstPage=_decorate, onLaterPages=_decorate)
    return buf.getvalue()


def _table(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F8")]),
    ]))
    return t


def _esc(v):
    return (str(v or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _ph(fr):
    return "À compléter par l’équipe pays" if fr else "To be completed by the country team"
