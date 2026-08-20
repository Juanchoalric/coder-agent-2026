"""Tests for the E7 audit trail (tests/test_audit.py).

One row per event (build/approve/release) with all contract columns;
approval rows carry approver, approval_ts and artifact_sha256 (R2).
"""

from __future__ import annotations

import os
import tempfile
import unittest

from etl import audit


class AuditLogTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self._tmp.name, "data_log.csv")

    def tearDown(self):
        self._tmp.cleanup()


class TestAuditLog(AuditLogTestBase):
    def test_build_row_has_all_columns(self):
        audit.log_event(
            self.log,
            run_id="RUN-1",
            event="build",
            rows_usuarios=100,
            rows_ventas=100,
            joined_rows=100,
            match_rate=1.0,
            validation_status="OK",
            sanitization_status="0",
            outputs="dashboard.html,payload.json",
            status="OK",
            artifact_sha256="a" * 64,
        )
        rows = audit.all_events(self.log)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        # E7: every contract column present.
        for col in audit.LOG_COLUMNS:
            self.assertIn(col, row, col)
        self.assertEqual(row["event"], "build")
        self.assertEqual(row["status"], "OK")
        self.assertEqual(row["run_id"], "RUN-1")
        self.assertEqual(row["joined_rows"], "100")
        self.assertEqual(row["match_rate"], "1.000000")
        self.assertIn("dashboard.html", row["outputs"])

    def test_approval_row_records_approver_timestamp_fingerprint(self):
        # R2: approver, timestamp and artifact fingerprint recorded.
        audit.log_event(
            self.log, run_id="RUN-1", event="build", status="OK", artifact_sha256="b" * 64
        )
        audit.log_event(
            self.log,
            run_id="RUN-1",
            event="approve",
            approver="Jane Doe",
            approval_ts="2026-08-20T10:00:00",
            artifact_sha256="b" * 64,
            outputs="dashboard.html",
            status="OK",
        )
        approval = audit.read_latest_event(self.log, event="approve")
        self.assertIsNotNone(approval)
        self.assertEqual(approval["approver"], "Jane Doe")
        self.assertEqual(approval["approval_ts"], "2026-08-20T10:00:00")
        self.assertEqual(approval["artifact_sha256"], "b" * 64)
        self.assertEqual(approval["run_id"], "RUN-1")

    def test_header_written_once(self):
        audit.log_event(self.log, run_id="R1", event="build")
        audit.log_event(self.log, run_id="R2", event="build")
        with open(self.log, encoding="utf-8") as fh:
            content = fh.read()
        self.assertEqual(content.count("run_id,timestamp,event"), 1)

    def test_read_latest_event_returns_most_recent(self):
        audit.log_event(self.log, run_id="R1", event="build", status="OK")
        audit.log_event(self.log, run_id="R2", event="build", status="OK")
        latest = audit.read_latest_event(self.log, event="build")
        self.assertEqual(latest["run_id"], "R2")

    def test_read_latest_filters_by_status(self):
        audit.log_event(self.log, run_id="R1", event="build", status="FAILED")
        audit.log_event(self.log, run_id="R2", event="build", status="OK")
        ok = audit.read_latest_event(self.log, event="build", status="OK")
        self.assertEqual(ok["run_id"], "R2")
        failed = audit.read_latest_event(self.log, event="build", status="FAILED")
        self.assertEqual(failed["run_id"], "R1")

    def test_invalid_event_rejected(self):
        with self.assertRaises(ValueError):
            audit.log_event(self.log, run_id="R1", event="deploy")

    def test_missing_log_returns_none(self):
        self.assertIsNone(audit.read_latest_event(self.log, event="build"))
        self.assertEqual(audit.all_events(self.log), [])


if __name__ == "__main__":
    unittest.main()