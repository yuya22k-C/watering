"""SQLite access layer for basil-ai.

See docs/db-schema.md for the table definitions (sensors / decisions /
api_logs / watering_history). This module owns all DB I/O for the Pi side;
other modules never touch sqlite3 directly.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Open (or create) the SQLite DB and ensure all tables/indexes exist.

    TODO: execute the CREATE TABLE / CREATE INDEX statements from
    docs/db-schema.md. Enable WAL mode for concurrent read during long runs.
    """
    raise NotImplementedError


def insert_sensor(
    conn: sqlite3.Connection,
    ts: str,
    individual: str,
    kind: str,
    raw_json: str,
    **fields: Any,
) -> int:
    """Insert one row into `sensors` and return the rowid.

    TODO: flatten the kind-specific fields (temperature_c, soil_pct, ...) from
    **fields and always store the original payload in raw_json.
    """
    raise NotImplementedError


def insert_decision(
    conn: sqlite3.Connection,
    ts: str,
    request_id: str,
    source: str,
    final_water: bool,
    final_ml: int,
    *,
    claude_water: bool | None = None,
    claude_ml: int | None = None,
    claude_reason: str | None = None,
    clipped: bool = False,
    guard_reason: str | None = None,
    image_path: str | None = None,
    notes: str | None = None,
) -> int:
    """Insert one row into `decisions`."""
    raise NotImplementedError


def insert_api_log(
    conn: sqlite3.Connection,
    ts: str,
    request_id: str,
    model: str,
    prompt_text: str,
    *,
    latency_ms: int | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cache_read: int | None = None,
    cache_creation: int | None = None,
    image_path: str | None = None,
    response_text: str | None = None,
    parsed_json: str | None = None,
    error: str | None = None,
) -> int:
    """Insert one row into `api_logs`. Always store prompt and response verbatim."""
    raise NotImplementedError


def insert_watering(
    conn: sqlite3.Connection,
    ts: str,
    individual: str,
    ml: int,
    source: str,
    *,
    request_id: str | None = None,
    notes: str | None = None,
) -> int:
    """Insert one row into `watering_history`.

    Used for both AI-individual auto watering and control-individual manual
    watering (recorded for video comparison).
    """
    raise NotImplementedError


def recent_sensors(
    conn: sqlite3.Connection,
    individual: str,
    since_iso: str,
) -> list[dict[str, Any]]:
    """Return sensor rows for one individual since the given timestamp (ascending)."""
    raise NotImplementedError


def last_watering(
    conn: sqlite3.Connection,
    individual: str,
) -> dict[str, Any] | None:
    """Return the most recent watering_history row for the individual, or None."""
    raise NotImplementedError


def last_decision(conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Return the most recent decisions row, or None (used to give Claude prior context)."""
    raise NotImplementedError
