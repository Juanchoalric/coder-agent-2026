"""Read-only Excel ingestion (E1).

Guarantees:
- Source Excels are opened read-only via the openpyxl engine and never written to.
- Explicit pandas 3 dtypes: ``dtype_backend="numpy_nullable"`` + explicit
  ``string`` dtype for text columns (avoids ``Pandas4Warning`` and
  ``select_dtypes("object")``).
- Aborts with a file-specific, clear error when a file is missing, unreadable,
  or lacks a required column.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# Source files (codified reality from exploration - NOT the blueprint's
# Ventas.xlsx / Inventario.xlsx names).
USUARIOS_FILE = "Usuarios_Ventas_2026.xlsx"
VENTAS_FILE = "Ventas_Productos_2026.xlsx"

# Required columns per source.
USUARIOS_COLUMNS = [
    "ID Transacción",
    "Nombre Cliente",
    "Correo Electrónico",
    "País",
    "Edad",
    "Fecha Registro",
]

VENTAS_COLUMNS = [
    "ID Transacción",
    "Fecha",
    "Producto",
    "Categoría",
    "Cantidad",
    "Precio Unitario (USD)",
    "Total (USD)",
    "Región",
    "Método de Pago",
]

# Text columns that MUST be read with the explicit pandas `string` dtype
# (pandas 3 migration; never treat as numpy object dtype).
STRING_COLUMNS = [
    "ID Transacción",
    "Nombre Cliente",
    "Correo Electrónico",
    "País",
    "Fecha Registro",
    "Fecha",
    "Producto",
    "Categoría",
    "Región",
    "Método de Pago",
]

# Numeric columns (guardrail E3: must stay numeric - no NaN, no text).
NUMERIC_COLUMNS = [
    "Edad",
    "Cantidad",
    "Precio Unitario (USD)",
    "Total (USD)",
]


class IngestError(Exception):
    """Raised when a source Excel cannot be loaded (E1 edge)."""


def _read_sheet(path: str | Path, required_columns: list[str], label: str) -> pd.DataFrame:
    """Load one Excel read-only and enforce schema + explicit dtypes."""
    path = Path(path)
    if not path.exists():
        raise IngestError(f"{label}: archivo no encontrado: {path.name}")
    if not path.is_file():
        raise IngestError(f"{label}: no es un archivo regular: {path.name}")
    try:
        df = pd.read_excel(path, engine="openpyxl", dtype_backend="numpy_nullable")
    except Exception as exc:  # corrupt/unreadable workbook
        raise IngestError(f"{label}: no se pudo leer el archivo {path.name}: {exc}") from exc

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise IngestError(
            f"{label}: faltan columnas requeridas: {', '.join(missing)} (en {path.name})"
        )

    # Explicit pandas `string` dtype for text columns.
    for col in STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Explicit numeric coercion: text in a numeric column raises here,
    # which satisfies the E3 abort contract at the earliest stage.
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="raise")
            except (TypeError, ValueError) as exc:
                raise IngestError(
                    f"{label}: la columna numérica '{col}' contiene texto no numérico "
                    f"(en {path.name})"
                ) from exc

    return df


def load_usuarios(path: str | Path = USUARIOS_FILE) -> pd.DataFrame:
    """Load the customer/transaction dimension read-only (E1)."""
    return _read_sheet(path, USUARIOS_COLUMNS, "Usuarios")


def load_ventas(path: str | Path = VENTAS_FILE) -> pd.DataFrame:
    """Load the sales facts read-only (E1)."""
    return _read_sheet(path, VENTAS_COLUMNS, "Ventas")


def source_files_exist() -> bool:
    """True when both source Excels are present in the working directory."""
    return os.path.isfile(USUARIOS_FILE) and os.path.isfile(VENTAS_FILE)