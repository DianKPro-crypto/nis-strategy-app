"""
Built-in reference documents fed to the AI on EVERY step so the analysis is
systematically aligned with IA2030 and the Gavi 6.0 (2026-2030) strategy.

- Important_Info_Tables_FR.xlsx: IA2030 priorities/indicators, Gavi 6.0 objectives &
  interventions (2026), aligned EPI components, main-intervention catalogue, scorecard.
- The EMR narrative template drives the Word report structure (see word_exporter), not the AI.
"""
from __future__ import annotations
from pathlib import Path

from config.settings import BASE_DIR
from core.models import UploadedDocument

REFERENCE_DIR = BASE_DIR / "reference_docs"

# The reference sheets most useful to ground objectives / interventions / indicators.
KEY_SHEETS = [
    "Gavi 6.0 Obj-Intervtns 2026", "IA2030 aligned EPI comp", "RegIA2030", "Gavi & IA2030",
    "Main interventions", "IA2030SP_SPO_Indicators", "IA2030 focus areas_Objs", "Scorecard",
]
_CAP = 16000            # total chars of reference text passed to the AI (cost control)
_cache: list[UploadedDocument] | None = None


def _extract_key_sheets(path: Path, cap: int) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    parts, used = [], 0
    names = [s for s in KEY_SHEETS if s in wb.sheetnames] or wb.sheetnames
    for name in names:
        ws = wb[name]
        parts.append(f"\n=== {name} ===")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i > 120:
                break
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if not cells:
                continue
            line = " | ".join(cells)
            parts.append(line)
            used += len(line)
            if used > cap:
                parts.append("… (référence tronquée)")
                return "\n".join(parts)
    return "\n".join(parts)


def get_reference_documents() -> list[UploadedDocument]:
    """Return the bundled reference documents as UploadedDocuments (cached)."""
    global _cache
    if _cache is not None:
        return _cache
    docs: list[UploadedDocument] = []
    xlsx = REFERENCE_DIR / "Important_Info_Tables_FR.xlsx"
    if xlsx.exists():
        try:
            text = _extract_key_sheets(xlsx, _CAP)
            docs.append(UploadedDocument(
                name="Référence IA2030 & Gavi 6.0 — tableaux (objectifs, interventions, indicateurs)",
                file_type="xlsx", doc_category="Référence méthodologique OMS/IA2030/Gavi",
                text=text, tables_summary="[Référence intégrée: IA2030 & Gavi 6.0]"))
        except Exception:
            pass
    _cache = docs
    return docs
