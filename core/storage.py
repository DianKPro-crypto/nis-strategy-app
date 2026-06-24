"""Lightweight SQLite persistence for MVP local storage (one row per project)."""
from __future__ import annotations
import json
import sqlite3
from contextlib import closing

from config.settings import DB_PATH
from core.models import NISStrategy


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, country TEXT, updated TEXT, payload TEXT)""")
    return c


def save_project(name: str, strategy: NISStrategy) -> int:
    payload = strategy.to_json()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    with closing(_conn()) as c:
        cur = c.execute("SELECT id FROM projects WHERE name=?", (name,))
        row = cur.fetchone()
        if row:
            c.execute("UPDATE projects SET payload=?, updated=?, country=? WHERE id=?",
                      (payload, now, strategy.profile.country_name, row[0]))
            pid = row[0]
        else:
            cur = c.execute("INSERT INTO projects(name,country,updated,payload) VALUES(?,?,?,?)",
                            (name, strategy.profile.country_name, now, payload))
            pid = cur.lastrowid
        c.commit()
    return pid


def list_projects() -> list[tuple[int, str, str, str]]:
    with closing(_conn()) as c:
        return list(c.execute("SELECT id,name,country,updated FROM projects ORDER BY updated DESC"))


def load_project(name: str) -> NISStrategy | None:
    with closing(_conn()) as c:
        row = c.execute("SELECT payload FROM projects WHERE name=?", (name,)).fetchone()
    return NISStrategy.from_dict(json.loads(row[0])) if row else None
