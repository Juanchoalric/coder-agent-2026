"""Audit trail: append one row per event to ``data_log.csv`` (E7, R2).

Columns (design contract):
``run_id, timestamp, event, rows_usuarios, rows_ventas, joined_rows,
match_rate, validation_status, sanitization_status, outputs, status,
approver, approval_ts, artifact_sha256``

- ``event`` is one of ``build`` | ``approve`` | ``release``.
- ``approve`` rows additionally record ``approver``, ``approval_ts`` and the
  SHA-256 hex digest of the approved artifact (R2).
- Failed builds append a ``status=FAILED`` row carrying the match rate (E2 edge).
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_LOG = "data_log.csv"

LOG_COLUMNS = [
    "run_id",
    "timestamp",
    "event",
    "rows_usuarios",
    "rows_ventas",
    "joined_rows",
    "match_rate",
    "validation_status",
    "sanitization_status",
    "outputs",
    "status",
    "approver",
    "approval_ts",
    "artifact_sha256",
]

_EVENTS = {"build", "approve", "release"}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log_event(
    path: str | Path = DATA_LOG,
    *,
    run_id: str,
    event: str,
    rows_usuarios: int | None = None,
    rows_ventas: int | None = None,
    joined_rows: int | None = None,
    match_rate: float | None = None,
    validation_status: str = "",
    sanitization_status: str = "",
    outputs: str = "",
    status: str = "OK",
    approver: str = "",
    approval_ts: str = "",
    artifact_sha256: str = "",
) -> None:
    """Append one audit row (E7). Creates the header when the log is new."""
    if event not in _EVENTS:
        raise ValueError(f"event desconocido: {event!r} (esperado: {sorted(_EVENTS)})")
    path = Path(path)
    exists = path.exists()
    row: dict[str, Any] = {
        "run_id": run_id,
        "timestamp": _now_iso(),
        "event": event,
        "rows_usuarios": rows_usuarios,
        "rows_ventas": rows_ventas,
        "joined_rows": joined_rows,
        "match_rate": f"{match_rate:.6f}" if match_rate is not None else "",
        "validation_status": validation_status,
        "sanitization_status": sanitization_status,
        "outputs": outputs,
        "status": status,
        "approver": approver,
        "approval_ts": approval_ts,
        "artifact_sha256": artifact_sha256,
    }
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def read_latest_event(
    path: str | Path = DATA_LOG,
    *,
    event: str,
    status: str = "OK",
) -> dict[str, str] | None:
    """Return the most recent log row for *event* (optionally filtered by *status*)."""
    path = Path(path)
    if not path.exists():
        return None
    latest: dict[str, str] | None = None
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("event") == event and row.get("status") == status:
                latest = row
    return latest


def all_events(path: str | Path = DATA_LOG) -> list[dict[str, str]]:
    """Return every audit row (used by tests and manual review)."""
    path = Path(path)
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return [row for row in csv.DictReader(fh)]