"""Aggregations over the joined, validated, sanitized frame (E6).

Emit KPIs plus monthly, category, region, payment, top-product, country,
age-bucket and transaction aggregates. All numpy nullable values are
converted to native Python types so the payload serializes with ``json.dumps``
(pandas 3 ``numpy_nullable`` arrays hold ``pd.NA``/numpy scalars otherwise).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

PERIOD = "Ene-May 2026"  # D2: explicit partial-year label, NO YoY claims.

_MONTH_LABELS = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

_AGE_BUCKETS = [
    (18, 25, "18-25"),
    (26, 35, "26-35"),
    (36, 50, "36-50"),
    (51, 65, "51-65"),
    (66, 150, "66+"),
]

# Keys of the embedded JSON payload (Spanish, matching source columns).
TRANSACTION_KEYS = [
    ("ID Transacción", "id"),
    ("Fecha", "fecha"),
    ("Nombre Cliente", "cliente"),
    ("País", "pais"),
    ("Edad", "edad"),
    ("Producto", "producto"),
    ("Categoría", "categoria"),
    ("Cantidad", "cantidad"),
    ("Precio Unitario (USD)", "precio_unitario_usd"),
    ("Total (USD)", "total_usd"),
    ("Región", "region"),
    ("Método de Pago", "metodo_pago"),
]


def _jnum(value: Any) -> int | float | None:
    """Convert a numpy_nullable scalar to a JSON-safe native number."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return float(value)


def _jstr(value: Any) -> str:
    return "" if value is None or pd.isna(value) else str(value)


def age_bucket(age: Any) -> str:
    """Bucket an age into one of the 5 dashboard buckets (E6)."""
    if age is None or pd.isna(age):
        return "Sin dato"
    for lo, hi, label in _AGE_BUCKETS:
        if lo <= int(age) <= hi:
            return label
    return "Otro"


def _group_totals(
    df: pd.DataFrame,
    by: str,
    out_key: str,
    money_col: str = "Total (USD)",
    count_col: str = "ID Transacción",
) -> list[dict]:
    """Group by a column and return [{out_key: value, total_usd, transactions}] sorted desc."""
    grouped = (
        df.groupby(by, observed=True)
        .agg(total_usd=(money_col, "sum"), transactions=(count_col, "count"))
        .reset_index()
    )
    grouped = grouped.sort_values("total_usd", ascending=False)
    rows: list[dict] = []
    for _, row in grouped.iterrows():
        rows.append(
            {
                out_key: _jstr(row[by]),
                "total_usd": _jnum(row["total_usd"]),
                "transactions": _jnum(row["transactions"]),
            }
        )
    return rows


def build_payload(df: pd.DataFrame, meta: dict) -> dict:
    """Build the full dashboard payload from the joined frame (E6)."""
    total_usd = _jnum(df["Total (USD)"].sum())
    units = _jnum(df["Cantidad"].sum())
    transactions = len(df)
    avg_order_usd = round(total_usd / transactions, 2) if transactions else 0.0

    # --- Monthly (E4: Fecha must already be datetime) -----------------------
    monthly_rows: list[dict] = []
    if len(df):
        by_month = (
            df.groupby(df["Fecha"].dt.to_period("M"))
            .agg(total_usd=("Total (USD)", "sum"), transactions=("ID Transacción", "count"))
            .reset_index()
        )
        by_month = by_month.sort_values("Fecha")
        for _, row in by_month.iterrows():
            period = row["Fecha"]  # pd.Period like 2026-01
            monthly_rows.append(
                {
                    "month": str(period),
                    "label": _MONTH_LABELS[period.month - 1],
                    "total_usd": _jnum(row["total_usd"]),
                    "transactions": _jnum(row["transactions"]),
                }
            )

    # --- Top products (units included, limit 10) ----------------------------
    top_rows: list[dict] = []
    if len(df):
        top = (
            df.groupby("Producto", observed=True)
            .agg(
                total_usd=("Total (USD)", "sum"),
                units=("Cantidad", "sum"),
                transactions=("ID Transacción", "count"),
            )
            .reset_index()
            .sort_values("total_usd", ascending=False)
            .head(10)
        )
        for _, row in top.iterrows():
            top_rows.append(
                {
                    "producto": _jstr(row["Producto"]),
                    "total_usd": _jnum(row["total_usd"]),
                    "units": _jnum(row["units"]),
                }
            )

    # --- Age buckets ---------------------------------------------------------
    age_rows: list[dict] = []
    if len(df):
        ages = df.assign(bucket=df["Edad"].map(age_bucket))
        age_rows = _group_totals(ages, "bucket", "bucket")

    transactions_rows: list[dict] = []
    for _, row in df.iterrows():
        item: dict[str, Any] = {}
        for src_key, out_key in TRANSACTION_KEYS:
            value = row[src_key]
            if out_key in ("edad", "cantidad", "precio_unitario_usd", "total_usd"):
                item[out_key] = _jnum(value)
            elif out_key == "fecha":
                item[out_key] = (
                    value.strftime("%Y-%m-%d") if isinstance(value, datetime) else _jstr(value)
                )
            else:
                item[out_key] = _jstr(value)
        transactions_rows.append(item)

    return {
        "meta": meta,
        "kpis": {
            "total_usd": total_usd,
            "units": units,
            "transactions": transactions,
            "avg_order_usd": avg_order_usd,
        },
        "monthly": monthly_rows,
        "by_category": _group_totals(df, "Categoría", "categoria"),
        "by_region": _group_totals(df, "Región", "region"),
        "by_payment": _group_totals(df, "Método de Pago", "metodo"),
        "top_products": top_rows,
        "by_country": _group_totals(df, "País", "pais"),
        "by_age_bucket": age_rows,
        "transactions": transactions_rows,
    }