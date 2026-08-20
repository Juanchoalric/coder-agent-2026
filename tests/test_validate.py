"""Tests for E2/E3/E4 validation gates (tests/test_validate.py).

- E3: NaN/text in numeric columns aborts the run.
- E2: inner join on ID Transacción; match rate < 90% blocks.
- E4: ISO date parsing before month aggregation.
"""

from __future__ import annotations

import unittest

import pandas as pd

from etl import validate
from etl.validate import JoinBreachError, ValidationError


def _usuarios(ids, ages=None) -> pd.DataFrame:
    n = len(ids)
    return pd.DataFrame(
        {
            "ID Transacción": pd.array(ids, dtype="string"),
            "Nombre Cliente": pd.array([f"C{i}" for i in range(n)], dtype="string"),
            "Correo Electrónico": pd.array([f"c{i}@x.com" for i in range(n)], dtype="string"),
            "País": pd.array(["Chile"] * n, dtype="string"),
            "Edad": pd.array(ages if ages is not None else [30] * n, dtype="Int64"),
            "Fecha Registro": pd.array(["2026-01-01"] * n, dtype="string"),
        }
    )


def _ventas(ids, totals=None, fechas=None) -> pd.DataFrame:
    n = len(ids)
    return pd.DataFrame(
        {
            "ID Transacción": pd.array(ids, dtype="string"),
            "Fecha": pd.array(fechas if fechas is not None else ["2026-01-09"] * n, dtype="string"),
            "Producto": pd.array(["Laptop Pro M1"] * n, dtype="string"),
            "Categoría": pd.array(["Hardware"] * n, dtype="string"),
            "Cantidad": pd.array([2] * n, dtype="Int64"),
            "Precio Unitario (USD)": pd.array([1200] * n, dtype="Int64"),
            "Total (USD)": pd.array(totals if totals is not None else [2400] * n, dtype="Int64"),
            "Región": pd.array(["Asia"] * n, dtype="string"),
            "Método de Pago": pd.array(["Crédito"] * n, dtype="string"),
        }
    )


class TestNumericsE3(unittest.TestCase):
    def test_clean_numerics_pass(self):
        df = _ventas([f"T-{i}" for i in range(5)])
        self.assertEqual(validate.validate_numerics(df, validate.VENTAS_NUMERIC, "Ventas"), "OK")

    def test_nan_in_total_aborts(self):
        # E3 edge: NaN in Total (USD) -> run aborts, violation logged.
        df = _ventas([f"T-{i}" for i in range(5)], totals=[100, 200, None, 400, 500])
        with self.assertRaises(ValidationError) as ctx:
            validate.validate_numerics(df, validate.VENTAS_NUMERIC, "Ventas")
        self.assertIn("Total (USD)", str(ctx.exception))
        self.assertIn("NaN", str(ctx.exception))

    def test_text_in_total_aborts(self):
        # E3 edge: text in Total (USD) -> not numeric dtype -> abort.
        df = _ventas([f"T-{i}" for i in range(3)])
        df["Total (USD)"] = pd.array(["100", "abc", "300"], dtype="string")
        with self.assertRaises(ValidationError):
            validate.validate_numerics(df, ["Total (USD)"], "Ventas")

    def test_non_finite_aborts(self):
        df = _ventas([f"T-{i}" for i in range(3)])
        df["Total (USD)"] = pd.array([100.0, float("inf"), 300.0], dtype="Float64")
        with self.assertRaises(ValidationError) as ctx:
            validate.validate_numerics(df, ["Total (USD)"], "Ventas")
        self.assertIn("no finito", str(ctx.exception))


class TestJoinE2(unittest.TestCase):
    def test_full_overlap_100_percent(self):
        ids = [f"T-{i}" for i in range(100)]
        joined, match_rate = validate.inner_join(_usuarios(ids), _ventas(ids))
        self.assertEqual(len(joined), 100)
        self.assertAlmostEqual(match_rate, 1.0)
        validate.check_match_rate(match_rate)  # must not raise

    def test_overlap_below_90_blocks(self):
        # E2 edge: only 80/100 overlap -> alert emitted, run flagged failed.
        all_ids = [f"T-{i}" for i in range(100)]
        ventas_ids = all_ids[:80] + [f"X-{i}" for i in range(20)]  # 20 orphans
        joined, match_rate = validate.inner_join(_usuarios(all_ids), _ventas(ventas_ids))
        self.assertAlmostEqual(match_rate, 0.8)
        with self.assertRaises(JoinBreachError) as ctx:
            validate.check_match_rate(match_rate)
        self.assertIn("0.8000", str(ctx.exception))
        self.assertIn("0.90", str(ctx.exception))

    def test_partial_orphans_on_one_side(self):
        ids = [f"T-{i}" for i in range(100)]
        usuarios_ids = ids + ["U-extra-1", "U-extra-2"]  # users without sales
        joined, match_rate = validate.inner_join(_usuarios(usuarios_ids), _ventas(ids))
        self.assertEqual(len(joined), 100)
        self.assertAlmostEqual(match_rate, 100 / 102, places=4)


class TestDatesE4(unittest.TestCase):
    def test_iso_dates_parse(self):
        df = _ventas(
            [f"T-{i}" for i in range(3)],
            fechas=["2026-01-09", "2026-05-24", "2026-03-15"],
        )
        validate.parse_dates(df, validate.VENTAS_DATES)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["Fecha"]))
        self.assertEqual(df["Fecha"].dt.month.tolist(), [1, 5, 3])

    def test_non_iso_date_aborts(self):
        df = _ventas([f"T-{i}" for i in range(3)], fechas=["2026-01-09", "09/01/2026", "2026-03-15"])
        with self.assertRaises(ValidationError) as ctx:
            validate.parse_dates(df, validate.VENTAS_DATES)
        self.assertIn("no ISO", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()