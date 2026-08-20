"""Tests for E6 aggregation (tests/test_aggregate.py).

A 100-row joined frame must produce KPIs and every aggregate group plus the
transactions list, with totals matching the exploration-verified figures
(total USD 274285, 1035 units, 100 transactions, avg 2742.85).
"""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from etl import aggregate

# Deterministic 100-row fixture with the exploration-verified totals.
_N = 100
_TOTAL_USD = 274285
_UNITS = 1035


def _joined_frame(n: int = _N) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    ids = [f"TXN-{i:03d}" for i in range(1, n + 1)]
    productos = ["Laptop Pro M1", "Tablet de Diseño", "Auriculares Pro", "Teclado Mecánico",
                 "Monitor 4K", "Mouse Pro", "Webcam HD", "Silla Ergonómica", "Hub USB-C", "SSD 1TB"]
    categorias = {"Laptop Pro M1": "Hardware", "Tablet de Diseño": "Hardware",
                  "Auriculares Pro": "Audio", "Teclado Mecánico": "Periféricos",
                  "Monitor 4K": "Hardware", "Mouse Pro": "Periféricos",
                  "Webcam HD": "Periféricos", "Silla Ergonómica": "Accesorios",
                  "Hub USB-C": "Accesorios", "SSD 1TB": "Accesorios"}
    paises = ["Chile", "Colombia", "España", "México", "Argentina", "Perú", "Brasil"]
    regiones = ["Asia", "Latinoamérica", "Europa", "Norteamérica"]
    metodos = ["Crédito", "Transferencia", "PayPal", "Débito"]

    rng_units = rng.integers(1, 20, size=n)
    rng_price = rng.integers(15, 1200, size=n)
    totals = rng_units * rng_price
    # Scale totals to hit the exact exploration figure.
    scale = _TOTAL_USD / totals.sum()
    adjusted = np.floor(totals * scale).astype(int)
    diff = _TOTAL_USD - int(adjusted.sum())
    adjusted[-1] += diff
    units = rng_units.copy()
    u_diff = _UNITS - int(units.sum())
    units[-1] += u_diff

    fechas = pd.date_range("2026-01-01", "2026-05-24", periods=n)
    return pd.DataFrame(
        {
            "ID Transacción": pd.array(ids, dtype="string"),
            "Nombre Cliente": pd.array([f"Cliente {i}" for i in range(n)], dtype="string"),
            "Correo Electrónico": pd.array([f"c{i}@x.com" for i in range(n)], dtype="string"),
            "País": pd.array([paises[i % len(paises)] for i in range(n)], dtype="string"),
            "Edad": pd.array(rng.integers(18, 76, size=n), dtype="Int64"),
            "Fecha Registro": pd.to_datetime(pd.array(["2026-01-01"] * n, dtype="string")),
            "Fecha": fechas,
            "Producto": pd.array([productos[i % len(productos)] for i in range(n)], dtype="string"),
            "Categoría": pd.array(
                [categorias[productos[i % len(productos)]] for i in range(n)], dtype="string"
            ),
            "Cantidad": pd.array(units, dtype="Int64"),
            "Precio Unitario (USD)": pd.array(rng_price, dtype="Int64"),
            "Total (USD)": pd.array(adjusted, dtype="Int64"),
            "Región": pd.array([regiones[i % len(regiones)] for i in range(n)], dtype="string"),
            "Método de Pago": pd.array(
                [metodos[i % len(metodos)] for i in range(n)], dtype="string"
            ),
        }
    )


class TestAggregateE6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = {
            "period": aggregate.PERIOD,
            "run_id": "test-run",
            "generated_at": "2026-08-20T00:00:00",
            "match_rate": 1.0,
            "source_files": ["Usuarios_Ventas_2026.xlsx", "Ventas_Productos_2026.xlsx"],
        }
        cls.payload = aggregate.build_payload(_joined_frame(), cls.meta)

    def test_kpis_match_exploration_totals(self):
        kpis = self.payload["kpis"]
        self.assertEqual(kpis["total_usd"], _TOTAL_USD)
        self.assertEqual(kpis["units"], _UNITS)
        self.assertEqual(kpis["transactions"], 100)
        self.assertAlmostEqual(kpis["avg_order_usd"], round(_TOTAL_USD / 100, 2), places=2)

    def test_all_groups_present(self):
        for key in ("monthly", "by_category", "by_region", "by_payment",
                    "top_products", "by_country", "by_age_bucket"):
            self.assertIn(key, self.payload)
            self.assertGreater(len(self.payload[key]), 0, key)

    def test_monthly_uses_spanish_labels_and_iso_month(self):
        months = self.payload["monthly"]
        self.assertTrue(all(m["month"].startswith("2026-") for m in months))
        labels = {m["label"] for m in months}
        self.assertTrue(labels <= {"Ene", "Feb", "Mar", "Abr", "May"})
        total = sum(m["total_usd"] for m in months)
        self.assertEqual(total, _TOTAL_USD)

    def test_group_rows_have_expected_keys(self):
        row = self.payload["by_category"][0]
        self.assertIn("categoria", row)
        self.assertIn("total_usd", row)
        self.assertIn("transactions", row)
        row = self.payload["by_region"][0]
        self.assertIn("region", row)
        row = self.payload["by_payment"][0]
        self.assertIn("metodo", row)
        row = self.payload["by_country"][0]
        self.assertIn("pais", row)
        row = self.payload["by_age_bucket"][0]
        self.assertIn("bucket", row)
        self.assertIn("36-50", {r["bucket"] for r in self.payload["by_age_bucket"]})

    def test_top_products_have_units(self):
        for row in self.payload["top_products"]:
            self.assertIn("producto", row)
            self.assertIn("units", row)

    def test_transactions_list_matches_frame(self):
        txns = self.payload["transactions"]
        self.assertEqual(len(txns), 100)
        first = txns[0]
        self.assertIn("id", first)
        self.assertIn("fecha", first)
        self.assertIn("cliente", first)
        self.assertIn("total_usd", first)
        self.assertIn("metodo_pago", first)
        total = sum(t["total_usd"] for t in txns)
        self.assertEqual(total, _TOTAL_USD)
        # Dates are ISO strings, not datetimes (JSON-safe).
        self.assertTrue(all(isinstance(t["fecha"], str) for t in txns))

    def test_payload_serializes_with_stdlib_json(self):
        import json

        dumped = json.dumps(self.payload, ensure_ascii=False)
        self.assertIn('"total_usd"', dumped)
        self.assertIn("2026-", dumped)


if __name__ == "__main__":
    unittest.main()