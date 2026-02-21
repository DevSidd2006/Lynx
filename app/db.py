from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import settings


Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                full_name TEXT DEFAULT '',
                role TEXT DEFAULT '',
                preferred_tone TEXT DEFAULT 'professional',
                default_language TEXT DEFAULT 'en',
                writing_rules_json TEXT DEFAULT '[]',
                custom_dictionary_json TEXT DEFAULT '[]',
                working_context TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # Handle schema upgrades (add columns if missing)
        try:
            conn.execute("ALTER TABLE profile ADD COLUMN working_context TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE profile ADD COLUMN default_language TEXT DEFAULT 'en'")
        except sqlite3.OperationalError:
            pass
        
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                rewritten_text TEXT,
                style TEXT,
                language TEXT,
                context TEXT,
                transcript_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.execute(
            """
            INSERT INTO profile (id)
            VALUES (1)
            ON CONFLICT(id) DO NOTHING;
            """
        )

        for key, value in {
            "auto_copy": "true",
            "auto_rewrite": "true",
            "default_style": "professional",
        }.items():
            conn.execute(
                """
                INSERT INTO app_settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO NOTHING;
                """,
                (key, value),
            )

        conn.commit()


def fetch_profile() -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if row is None:
        raise RuntimeError("Profile record missing")

    # Safely convert sqlite3.Row to dict
    data = dict(row)

    return {
        "full_name": data.get("full_name", ""),
        "role": data.get("role", ""),
        "preferred_tone": data.get("preferred_tone", "professional"),
        "default_language": data.get("default_language", "en"),
        "writing_rules": json.loads(data.get("writing_rules_json", "[]")),
        "custom_dictionary": json.loads(data.get("custom_dictionary_json", "[]")),
        "working_context": data.get("working_context", ""),
    }


def upsert_profile(
    full_name: str,
    role: str,
    preferred_tone: str,
    writing_rules: list[str],
    custom_dictionary: list[str],
    working_context: str = "",
    default_language: str = "en",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE profile
            SET full_name = ?,
                role = ?,
                preferred_tone = ?,
                default_language = ?,
                writing_rules_json = ?,
                custom_dictionary_json = ?,
                working_context = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
            """,
            (
                full_name,
                role,
                preferred_tone,
                default_language,
                json.dumps(writing_rules),
                json.dumps(custom_dictionary),
                working_context,
            ),
        )
        conn.commit()


def list_entries(limit: int = 25) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, source_text, rewritten_text, style, language, context, created_at
            FROM entries
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_session_entries(
    context: str, minutes: int = 30, limit: int = 5
) -> list[dict[str, Any]]:
    """Return recent entries matching *context* from the last *minutes*."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, source_text, rewritten_text, style, language, context, created_at
            FROM entries
            WHERE context = ?
              AND created_at >= datetime('now', ? || ' minutes')
            ORDER BY id DESC
            LIMIT ?
            """,
            (context, f"-{minutes}", limit),
        ).fetchall()

    return [dict(row) for row in rows]


def add_entry(
    source_text: str,
    rewritten_text: str,
    style: str,
    language: str,
    context: str,
    transcript_path: str | None = None,
) -> int:
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO entries (source_text, rewritten_text, style, language, context, transcript_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (source_text, rewritten_text, style, language, context, transcript_path),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_app_settings() -> dict[str, str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


def set_app_setting(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
            """,
            (key, value),
        )
        conn.commit()
