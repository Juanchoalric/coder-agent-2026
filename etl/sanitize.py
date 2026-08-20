"""String sanitization before JSON embedding (E5).

Neutralizes the characters that can break HTML/JS embedding:
- surrounding quotes and ALL quote characters (``"`` and ``'``) are stripped,
- backslashes are stripped,
- angle brackets are replaced with parentheses so no value can look like
  markup (``<script>`` becomes ``(script)``),
- control characters (C0 + DEL) are removed.

Applied to every string column of the joined frame before aggregation and
JSON embedding. On top of this, :mod:`etl.render` escapes ``<``/``>``/``&``
to ``\\uXXXX`` inside the JSON script tag (defense-in-depth over E5).
"""

from __future__ import annotations

import re

import pandas as pd

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
# Remove quotes and backslashes; replace angle brackets with parentheses.
_DANGEROUS = str.maketrans(
    {
        '"': "",
        "'": "",
        "\\": "",
        "<": "(",
        ">": ")",
    }
)

# String columns of the joined frame (from both sources).
STRING_COLUMNS = [
    "ID Transacción",
    "Nombre Cliente",
    "Correo Electrónico",
    "País",
    "Producto",
    "Categoría",
    "Región",
    "Método de Pago",
]


def sanitize_text(value: object) -> str:
    """Return a JSON/JS-safe rendering of *value* (E5)."""
    if value is None:
        return ""
    text = str(value).strip()
    text = text.translate(_DANGEROUS)
    text = _CONTROL_CHARS.sub("", text)
    return text


def sanitize_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Sanitize all string columns of the joined frame (E5).

    Returns ``(frame, report)`` where report carries the number of cells
    modified per column for the E7 audit trail.
    """
    report: dict[str, int] = {}
    for col in STRING_COLUMNS:
        if col not in df.columns:
            continue
        original = df[col].astype("string")
        cleaned = original.map(sanitize_text).astype("string")
        modified = int((original != cleaned).sum())
        report[col] = modified
        df[col] = cleaned
    total = sum(report.values())
    return df, {"columns": report, "cells_modified": total, "status": "OK"}