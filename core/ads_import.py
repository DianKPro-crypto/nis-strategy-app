"""
Import an ADS situation-analysis CSV (codes 3.X.Y) and ALIGN it to the tool's
WHO structure (components 1-7, subcomponents 1.1-7.3).

- Component = the 2nd digit of the ADS code (3.X.Y -> tool component "X").
- Subcomponent = matched from the obstacle's theme (text before ':') to the tool's
  subcomponents, via a per-component keyword table (fallback = 1st subcomponent).
- "État" = "Point fort" -> strengths; otherwise -> weaknesses.

Expected CSV columns (header may carry a BOM): Code, Composante, Obstacle / faiblesse,
État, Priorité, Constatations, Limites des données.
"""
from __future__ import annotations
import csv
import io
import re
import unicodedata

from core.models import SWOTItem
from core.epi_components import EPI_COMPONENTS, find_subcomponent

# Ordered (most specific first) keyword -> subcomponent code, per component code.
SUBMAP: dict[str, list[tuple[str, str]]] = {
    "1": [("politiques et orientations", "1.1"), ("gouvernance", "1.2"),
          ("planification et approvisionnement", "1.3"), ("coordination des partenaires", "1.4"),
          ("budget", "1.5"), ("financement", "1.5"), ("communaut", "1.5")],
    "2": [("planification des ressources", "2.1"), ("motivation", "2.1"),
          ("renforcement des capacites", "2.2"), ("formation", "2.2"),
          ("supervision", "2.3"), ("communaut", "2.1")],
    "3": [("chaine du froid", "3.1"), ("approvisionnement", "3.2"), ("transport", "3.3"),
          ("dechets", "3.4"), ("communaut", "3.2")],
    "4": [("integration", "4.3"), ("qualite", "4.2"), ("session", "4.2"), ("seance", "4.2"),
          ("rh", "4.1"), ("strateg", "4.1"), ("communaut", "4.1")],
    "5": [("rh et systeme", "5.1"), ("systeme", "5.1"), ("qualite des donnees", "5.3"),
          ("enregistrement", "5.2"), ("notification", "5.2"), ("mapi", "5.5"),
          ("suivi de la couverture", "5.4"), ("couverture", "5.4"), ("communaut", "5.4")],
    "6": [("notification et intervention", "6.2"), ("rougeole", "6.1"), ("poliomyelite", "6.1"),
          ("surveillance des maladies", "6.1"), ("performance", "6.3"), ("communaut", "6.1")],
    "7": [("connaissances et attitudes", "7.2"), ("communication", "7.2"), ("plaidoyer", "7.2"),
          ("processus sociaux", "7.3"), ("engagement", "7.3"), ("communaut", "7.3"),
          ("opinions", "7.1"), ("questions pratiques", "7.1"), ("reticence", "7.1"),
          ("intention", "7.1"), ("rumeurs", "7.1"), ("confiance", "7.1")],
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def _col(row: dict, *names: str) -> str:
    """Fetch a column value tolerant to BOM / accents / casing."""
    for k, v in row.items():
        kn = _norm(k).lstrip("﻿")
        if any(kn == _norm(n) for n in names):
            return (v or "").strip()
    return ""


def _first_sub(comp_code: str) -> str:
    for c in EPI_COMPONENTS:
        if c.code == comp_code and c.subcomponents:
            return c.subcomponents[0].code
    return f"{comp_code}.1"


def _resolve_subcomponent(comp_code: str, obstacle: str) -> str:
    theme = obstacle.split(":", 1)[0] if ":" in obstacle[:70] else obstacle[:60]
    theme_n = _norm(theme)
    for kw, code in SUBMAP.get(comp_code, []):
        if kw in theme_n:
            return code
    # try the full text as a last resort before falling back
    full_n = _norm(obstacle)
    for kw, code in SUBMAP.get(comp_code, []):
        if kw in full_n:
            return code
    return _first_sub(comp_code)


def _pick_delimiter(header_line: str) -> str:
    """French Excel exports often use ';'. Pick the delimiter that exposes a 'Code' column."""
    best, best_score = ",", -1
    for d in (",", ";", "\t"):
        cols = [_norm(c) for c in header_line.split(d)]
        score = (1 if any(c == "code" for c in cols) else 0) + len(cols)
        if score > best_score:
            best, best_score = d, score
    return best


def import_ads_csv(file_bytes: bytes) -> tuple[list[SWOTItem], dict]:
    """Return (swot_items, stats). Items are merged per subcomponent."""
    text = file_bytes.decode("utf-8-sig", errors="replace")
    first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
    delim = _pick_delimiter(first_line)
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    buckets: dict[str, SWOTItem] = {}
    stats = {"rows": 0, "mapped": 0, "strengths": 0, "weaknesses": 0, "skipped": 0,
             "delimiter": delim, "columns": [c for c in (reader.fieldnames or [])]}

    for row in reader:
        code = _col(row, "Code")
        m = re.match(r"\d+\.(\d+)\.\d+", code)
        obstacle = _col(row, "Obstacle / faiblesse", "Obstacle/faiblesse", "Obstacle")
        if not m or not obstacle:
            stats["skipped"] += 1
            continue
        stats["rows"] += 1
        comp_code = m.group(1)
        if not any(c.code == comp_code for c in EPI_COMPONENTS):
            stats["skipped"] += 1
            continue
        sub_code = _resolve_subcomponent(comp_code, obstacle)
        item = buckets.setdefault(sub_code, SWOTItem(component_code=comp_code, subcomponent_code=sub_code))

        etat = _norm(_col(row, "État", "Etat", "Etat de l'obstacle"))
        constat = _col(row, "Constatations")
        line = obstacle.strip()
        if len(line) > 220:
            line = line[:217] + "…"
        if constat:
            c = constat.strip().replace("\n", " ")
            line += f" — Constat : {c[:160]}" + ("…" if len(c) > 160 else "")

        if etat.startswith("point fort"):
            item.strengths.append(line)
            stats["strengths"] += 1
        else:
            item.weaknesses.append(line)
            stats["weaknesses"] += 1
        stats["mapped"] += 1

    return list(buckets.values()), stats


def merge_into(strategy, items: list[SWOTItem]) -> None:
    """Merge imported SWOT items into the strategy (append to existing subcomponents)."""
    by = {x.subcomponent_code: x for x in strategy.swot}
    for it in items:
        cs = find_subcomponent(it.subcomponent_code)
        if not cs:
            continue
        existing = by.get(it.subcomponent_code)
        if existing is None:
            existing = SWOTItem(component_code=it.component_code, subcomponent_code=it.subcomponent_code)
            by[it.subcomponent_code] = existing
        existing.strengths += it.strengths
        existing.weaknesses += it.weaknesses
    strategy.swot = list(by.values())
