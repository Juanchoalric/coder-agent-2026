"""Validation gates: numerics (E3), ISO dates (E4), join + match rate (E2).

The E2 breach gate is fail-stop: when the ``ID Transacción`` match rate falls
below 90% the build is blocked (design decision "BLOCK (fail-stop)").
"""

from __future__ import annotations

import numpy as np
import pandas as pd

JOIN_KEY = "ID Transacción"
MATCH_RATE_THRESHOLD = 0.90  # E2: alert/block below 90%

# Numeric columns per source (E3 guardrail).
USUARIOS_NUMERIC = ["Edad"]
VENTAS_NUMERIC = ["Cantidad", "Precio Unitario (USD)", "Total (USD)"]

# ISO date columns (E4), parsed before any month aggregation.
USUARIOS_DATES = ["Fecha Registro"]
VENTAS_DATES = ["Fecha"]


class ValidationError(Exception):
    """A validation gate failed (E3/E4)."""


class JoinBreachError(Exception):
    """Join match rate fell below the 90% threshold (E2 edge)."""


def validate_numerics(df: pd.DataFrame, columns: list[str], label: str) -> str:
    """Verify numeric columns are numeric, finite, and free of NaN/text (E3).

    Returns "OK" on success; raises :class:`ValidationError` on any violation
    (which aborts the run and is logged in the audit trail).
    """
    violations: list[str] = []
    for col in columns:
        series = df[col]
        if not pd.api.types.is_numeric_dtype(series):
            violations.append(f"{label}.{col}: dtype no numérico ({series.dtype})")
            continue
        nulls = int(series.isna().sum())
        if nulls:
            violations.append(f"{label}.{col}: {nulls} valor(es) NaN/nulo(s)")
        if pd.api.types.is_float_dtype(series):
            non_finite = int(
                series.dropna().astype("float64").apply(np.isfinite).eq(False).sum()
            )
            if non_finite:
                violations.append(f"{label}.{col}: {non_finite} valor(es) no finito(s)")
    if violations:
        raise ValidationError("; ".join(violations))
    return "OK"


def parse_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Parse ISO ``YYYY-MM-DD`` columns to datetime in place (E4).

    Raises :class:`ValidationError` when any cell is not ISO-8601 compliant.
    """
    for col in columns:
        parsed = pd.to_datetime(df[col], errors="coerce", format="ISO8601")
        unparsed = int(parsed.isna().sum())
        if unparsed:
            raise ValidationError(
                f"{col}: {unparsed} celda(s) no ISO 8601 (se esperaba YYYY-MM-DD)"
            )
        df[col] = parsed
    return df


def inner_join(usuarios: pd.DataFrame, ventas: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Inner join on ``ID Transacción`` and compute the match rate (E2).

    Match rate is defined as the number of transaction IDs present on BOTH
    sides divided by the larger side's unique ID count. With unique IDs this
    equals ``len(inner) / max(len(left), len(right))``.
    """
    left_ids = set(usuarios[JOIN_KEY])
    right_ids = set(ventas[JOIN_KEY])
    matched = len(left_ids & right_ids)
    max_side = max(len(left_ids), len(right_ids))
    match_rate = matched / max_side if max_side else 0.0
    merged = pd.merge(usuarios, ventas, on=JOIN_KEY, how="inner")
    return merged, match_rate


def check_match_rate(match_rate: float) -> float:
    """Fail-stop gate for E2: raise :class:`JoinBreachError` below 90%."""
    if match_rate < MATCH_RATE_THRESHOLD:
        raise JoinBreachError(
            f"match_rate={match_rate:.4f} < umbral {MATCH_RATE_THRESHOLD:.2f}: "
            f"se detiene el procesamiento (E2)"
        )
    return match_rate