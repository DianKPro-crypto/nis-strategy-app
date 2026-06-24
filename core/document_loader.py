"""
Document ingestion: extract text, tables, metadata and locators (page/slide/sheet)
from .docx / .xlsx / .pptx / .pdf / .csv / .txt files.

Each extractor is defensive: a corrupted or unreadable file yields an
UploadedDocument with an error note rather than crashing the app.
"""
from __future__ import annotations
import csv
import io
from pathlib import Path

from config.settings import ALLOWED_EXTENSIONS, MAX_TEXT_CHARS_PER_DOC
from core.models import UploadedDocument


def extract_document(file_bytes: bytes, filename: str, doc_category: str = "") -> UploadedDocument:
    ext = Path(filename).suffix.lower().lstrip(".")
    doc = UploadedDocument(name=filename, file_type=ext, size_bytes=len(file_bytes),
                           doc_category=doc_category)
    if ext not in ALLOWED_EXTENSIONS:
        doc.text = f"[Type de fichier non pris en charge: .{ext}]"
        return doc
    try:
        if ext == "txt":
            _txt(file_bytes, doc)
        elif ext == "csv":
            _csv(file_bytes, doc)
        elif ext == "docx":
            _docx(file_bytes, doc)
        elif ext == "xlsx":
            _xlsx(file_bytes, doc)
        elif ext == "pptx":
            _pptx(file_bytes, doc)
        elif ext == "pdf":
            _pdf(file_bytes, doc)
    except Exception as e:  # never let one bad file break ingestion
        doc.text = (doc.text or "") + f"\n[Erreur d’extraction: {e}]"
        doc.metadata["extraction_error"] = str(e)
    doc.text = (doc.text or "")[:MAX_TEXT_CHARS_PER_DOC]
    return doc


def _txt(b: bytes, doc: UploadedDocument) -> None:
    doc.text = b.decode("utf-8", errors="replace")


def _csv(b: bytes, doc: UploadedDocument) -> None:
    text = b.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    doc.text = "\n".join("\t".join(r) for r in rows[:500])
    doc.tables_summary = f"[CSV: {len(rows)} lignes, {len(rows[0]) if rows else 0} colonnes]"
    doc.metadata["rows"] = len(rows)


def _docx(b: bytes, doc: UploadedDocument) -> None:
    import docx  # python-docx
    d = docx.Document(io.BytesIO(b))
    parts = [p.text for p in d.paragraphs if p.text.strip()]
    n_tables = len(d.tables)
    for ti, table in enumerate(d.tables, 1):
        parts.append(f"[Tableau {ti}]")
        for row in table.rows:
            parts.append(" | ".join(c.text for c in row.cells))
    doc.text = "\n".join(parts)
    doc.tables_summary = f"[Word: {len(d.paragraphs)} paragraphes, {n_tables} tableaux]"
    doc.metadata["tables"] = n_tables


def _xlsx(b: bytes, doc: UploadedDocument) -> None:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(b), data_only=True, read_only=True)
    parts, sheets = [], []
    for ws in wb.worksheets:
        sheets.append(ws.title)
        parts.append(f"=== FEUILLE: {ws.title} ===")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i > 200:
                parts.append("... (tronqué)")
                break
            cells = [str(c) for c in row if c is not None]
            if cells:
                parts.append("\t".join(cells))
    doc.text = "\n".join(parts)
    doc.tables_summary = f"[Excel: feuilles = {', '.join(sheets)}]"
    doc.metadata["sheets"] = sheets


def _pptx(b: bytes, doc: UploadedDocument) -> None:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(b))
    parts = []
    for si, slide in enumerate(prs.slides, 1):
        parts.append(f"=== DIAPOSITIVE {si} ===")
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                parts.append(shape.text_frame.text)
            if shape.has_table:
                for row in shape.table.rows:
                    parts.append(" | ".join(c.text for c in row.cells))
    doc.n_pages = len(prs.slides)
    doc.text = "\n".join(parts)
    doc.tables_summary = f"[PowerPoint: {doc.n_pages} diapositives]"


def _pdf(b: bytes, doc: UploadedDocument) -> None:
    text = ""
    # Prefer PyMuPDF (fitz); fall back to pdfplumber.
    try:
        import fitz  # PyMuPDF
        pdf = fitz.open(stream=b, filetype="pdf")
        pages = [f"[Page {i+1}]\n{pg.get_text()}" for i, pg in enumerate(pdf)]
        doc.n_pages = pdf.page_count
        text = "\n".join(pages)
    except Exception:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(b)) as pdf:
            pages = [f"[Page {i+1}]\n{(pg.extract_text() or '')}" for i, pg in enumerate(pdf.pages)]
            doc.n_pages = len(pdf.pages)
            text = "\n".join(pages)
    doc.text = text
    doc.tables_summary = f"[PDF: {doc.n_pages} pages]"
