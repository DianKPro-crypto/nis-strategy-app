"""
Durable cloud storage via Supabase (PostgREST REST API).

Persists each project (by name) to a Postgres table so work survives app reboots
on Streamlit Community Cloud. Configured via SUPABASE_URL + SUPABASE_KEY secrets.
Falls back silently (cloud_available() == False) when not configured — the app then
uses the local SQLite store.

One-time setup (run in Supabase → SQL editor):

    create table if not exists nis_projects (
        name text primary key,
        country text,
        language text,
        updated_at timestamptz default now(),
        payload jsonb
    );
    alter table nis_projects enable row level security;
    create policy "nis_all" on nis_projects for all using (true) with check (true);
"""
from __future__ import annotations
import re
from datetime import datetime, timezone

from config import settings
from core.models import NISStrategy

TABLE = "nis_projects"
_TIMEOUT = 15


def _project_url() -> str:
    """Normalize SUPABASE_URL to the project API base (https://<ref>.supabase.co).

    Self-heals the common mistake of pasting the dashboard URL
    (https://supabase.com/dashboard/project/<ref>/...) instead of the API URL.
    """
    raw = (settings.SUPABASE_URL or "").strip().rstrip("/")
    m = re.search(r"/project/([a-z0-9]{16,})", raw)
    if m:
        return f"https://{m.group(1)}.supabase.co"
    m2 = re.match(r"(https?://[A-Za-z0-9.\-]+)", raw)
    return m2.group(1) if m2 else raw


def cloud_available() -> bool:
    return bool(getattr(settings, "SUPABASE_URL", "") and getattr(settings, "SUPABASE_KEY", ""))


def _headers(extra: dict | None = None) -> dict:
    h = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def _base() -> str:
    return _project_url() + f"/rest/v1/{TABLE}"


def save_project(name: str, strategy: NISStrategy) -> bool:
    """Upsert a project by name. Returns True on success."""
    import requests
    row = {
        "name": name,
        "country": strategy.profile.country_name,
        "language": strategy.profile.language,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "payload": strategy.to_dict(),
    }
    r = requests.post(
        _base() + "?on_conflict=name",
        headers=_headers({"Prefer": "resolution=merge-duplicates,return=minimal"}),
        json=row, timeout=_TIMEOUT,
    )
    r.raise_for_status()
    return True


def list_projects() -> list[tuple[str, str, str]]:
    """Return [(name, country, updated_at)] ordered by most recent."""
    import requests
    r = requests.get(
        _base() + "?select=name,country,updated_at&order=updated_at.desc",
        headers=_headers(), timeout=_TIMEOUT,
    )
    r.raise_for_status()
    return [(x.get("name", ""), x.get("country", ""), x.get("updated_at", "")) for x in r.json()]


def load_project(name: str) -> NISStrategy | None:
    import requests
    r = requests.get(
        _base() + f"?name=eq.{requests.utils.quote(name)}&select=payload&limit=1",
        headers=_headers(), timeout=_TIMEOUT,
    )
    r.raise_for_status()
    rows = r.json()
    if not rows:
        return None
    return NISStrategy.from_dict(rows[0]["payload"])
