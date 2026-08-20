"""Tests for the approval gate (R1/R2/R3) and build blocking (E2 edge).

Runs the real CLI logic (``etl.main.main``) inside a temporary working
directory with copies of the source Excels, so the repo is never polluted.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from etl import audit, main as etl_main
from etl.main import EXIT_BUILD_FAIL, EXIT_GATE_BLOCK, EXIT_OK

PROJECT_ROOT = Path(__file__).resolve().parent.parent
USUARIOS = PROJECT_ROOT / "Usuarios_Ventas_2026.xlsx"
VENTAS = PROJECT_ROOT / "Ventas_Productos_2026.xlsx"


class GateTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        shutil.copy2(USUARIOS, self.dir / "Usuarios_Ventas_2026.xlsx")
        shutil.copy2(VENTAS, self.dir / "Ventas_Productos_2026.xlsx")
        self._old_cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        os.chdir(self._old_cwd)
        self._tmp.cleanup()

    def run_cli(self, *argv: str) -> int:
        return etl_main.main(list(argv))


class TestReleaseGate(GateTestBase):
    def test_r1_no_approval_blocks_release(self):
        # R1 edge: dashboard exists, no approval -> release blocked.
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        dest = self.dir / "out"
        self.assertEqual(self.run_cli("release", "--dest", str(dest)), EXIT_GATE_BLOCK)
        self.assertFalse(dest.exists())

    def test_r1_full_flow_releases(self):
        # R1 happy: build + approve + release.
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_OK)
        dest = self.dir / "out"
        self.assertEqual(self.run_cli("release", "--dest", str(dest)), EXIT_OK)
        self.assertTrue((dest / "dashboard.html").exists())
        # Release is audited.
        release = audit.read_latest_event(audit.DATA_LOG, event="release")
        self.assertIsNotNone(release)
        self.assertEqual(release["status"], "OK")
        self.assertEqual(release["approver"], "Jane Doe")

    def test_r2_approval_records_approver_timestamp_fingerprint(self):
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_OK)
        approval = audit.read_latest_event(audit.DATA_LOG, event="approve")
        self.assertIsNotNone(approval)
        self.assertEqual(approval["approver"], "Jane Doe")
        self.assertTrue(approval["approval_ts"])
        self.assertEqual(len(approval["artifact_sha256"]), 64)  # SHA-256 hex
        # Fingerprint equals the current file digest.
        from etl.main import sha256_file

        self.assertEqual(approval["artifact_sha256"], sha256_file("dashboard.html"))

    def test_r3_rerun_invalidates_prior_approval(self):
        # R3: new ETL run -> old approval no longer applies.
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_OK)
        self.assertEqual(self.run_cli("build"), EXIT_OK)  # new run_id
        dest = self.dir / "out"
        self.assertEqual(self.run_cli("release", "--dest", str(dest)), EXIT_GATE_BLOCK)
        self.assertFalse(dest.exists())
        # Fresh approval unblocks.
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_OK)
        self.assertEqual(self.run_cli("release", "--dest", str(dest)), EXIT_OK)
        self.assertTrue((dest / "dashboard.html").exists())

    def test_approve_blocks_when_artifact_modified(self):
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        with open("dashboard.html", "a", encoding="utf-8") as fh:
            fh.write("<!-- tamper -->")
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_GATE_BLOCK)

    def test_approve_blocks_without_build(self):
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_GATE_BLOCK)

    def test_release_blocks_when_artifact_modified_after_approval(self):
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        self.assertEqual(self.run_cli("approve", "--approver", "Jane Doe"), EXIT_OK)
        with open("dashboard.html", "a", encoding="utf-8") as fh:
            fh.write("<!-- tamper -->")
        dest = self.dir / "out"
        self.assertEqual(self.run_cli("release", "--dest", str(dest)), EXIT_GATE_BLOCK)


class TestBuildBlocking(GateTestBase):
    def test_e2_edge_below_90_percent_blocks(self):
        # Tampered ventas with only 80% overlap -> exit != 0, FAILED row, no output.
        ventas = pd.read_excel(VENTAS, engine="openpyxl", dtype_backend="numpy_nullable")
        ventas80 = ventas.head(80).copy()
        ventas80.to_excel(self.dir / "ventas80.xlsx", index=False)
        code = self.run_cli("build", "--ventas", "ventas80.xlsx")
        self.assertEqual(code, EXIT_BUILD_FAIL)
        self.assertFalse((self.dir / "dashboard.html").exists())
        failed = audit.read_latest_event(audit.DATA_LOG, event="build", status="FAILED")
        self.assertIsNotNone(failed)
        self.assertAlmostEqual(float(failed["match_rate"]), 0.8, places=4)

    def test_e1_missing_file_aborts(self):
        code = self.run_cli("build", "--usuarios", "missing.xlsx")
        self.assertEqual(code, EXIT_BUILD_FAIL)
        self.assertFalse((self.dir / "dashboard.html").exists())

    def test_e3_text_in_total_aborts(self):
        # Corrupt one Total (USD) cell with text -> build aborts (exit 2).
        ventas = pd.read_excel(VENTAS, engine="openpyxl", dtype_backend="numpy_nullable")
        totals = ventas["Total (USD)"].astype(object).copy()
        totals.iloc[0] = "texto-mal"
        ventas["Total (USD)"] = totals
        ventas.to_excel(self.dir / "ventas_bad.xlsx", index=False)
        code = self.run_cli("build", "--ventas", "ventas_bad.xlsx")
        self.assertEqual(code, EXIT_BUILD_FAIL)
        self.assertFalse((self.dir / "dashboard.html").exists())

    def test_build_appends_ok_audit_row(self):
        self.assertEqual(self.run_cli("build"), EXIT_OK)
        row = audit.read_latest_event(audit.DATA_LOG, event="build", status="OK")
        self.assertIsNotNone(row)
        self.assertEqual(row["rows_usuarios"], "100")
        self.assertEqual(row["rows_ventas"], "100")
        self.assertEqual(row["joined_rows"], "100")
        self.assertAlmostEqual(float(row["match_rate"]), 1.0, places=6)
        self.assertEqual(row["outputs"], "dashboard.html,payload.json")


if __name__ == "__main__":
    unittest.main()