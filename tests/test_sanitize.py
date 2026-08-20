"""Tests for E5 string sanitization (tests/test_sanitize.py).

Asserts the sanitizer neutralizes script markup, quotes, backslashes and
control characters before JSON embedding.
"""

from __future__ import annotations

import json
import unittest

import pandas as pd

from etl.sanitize import sanitize_frame, sanitize_text


class TestSanitizeText(unittest.TestCase):
    def test_script_tag_neutralized(self):
        # E5: <script> must never survive as markup.
        out = sanitize_text('<script>alert("x")</script>')
        self.assertNotIn("<", out)
        self.assertNotIn(">", out)
        self.assertNotIn('"', out)
        self.assertIn("script", out)  # text content preserved, not markup

    def test_quotes_stripped(self):
        self.assertEqual(sanitize_text('"Juan"'), "Juan")
        self.assertEqual(sanitize_text("'Ana'"), "Ana")
        self.assertEqual(sanitize_text('O\'Brien'), "OBrien")

    def test_backslashes_stripped(self):
        self.assertEqual(sanitize_text("C:\\Temp\\x"), "C:Tempx")

    def test_control_chars_removed(self):
        self.assertEqual(sanitize_text("line1\nline2\tend"), "line1line2end")
        self.assertEqual(sanitize_text("a\x00b\x1fc"), "abc")

    def test_none_becomes_empty(self):
        self.assertEqual(sanitize_text(None), "")

    def test_roundtrip_via_json_embedding(self):
        # Sanitized value must serialize and parse back losslessly through the
        # exact embedding pipeline used by etl.render.
        from etl.render import json_embed

        raw = 'Juan <script>"quoted"\\\n'
        payload = {"nombre": sanitize_text(raw)}
        embedded = json_embed(payload)
        self.assertNotIn("<script", embedded)
        parsed = json.loads(embedded)
        self.assertEqual(parsed["nombre"], sanitize_text(raw))


class TestSanitizeFrame(unittest.TestCase):
    def test_frame_sanitizes_all_string_columns(self):
        df = pd.DataFrame(
            {
                "ID Transacción": pd.array(["T-1", "T-2"], dtype="string"),
                "Nombre Cliente": pd.array(['Juan "El Grande"', "Ana <script>"], dtype="string"),
                "País": pd.array(["Chile", "Perú"], dtype="string"),
                "Producto": pd.array(["Laptop Pro M1", "Auriculares"], dtype="string"),
                "Categoría": pd.array(["Hardware", "Audio"], dtype="string"),
                "Región": pd.array(["Asia", "Europa"], dtype="string"),
                "Método de Pago": pd.array(["Crédito", "Débito"], dtype="string"),
            }
        )
        cleaned, report = sanitize_frame(df)
        self.assertEqual(report["status"], "OK")
        self.assertGreaterEqual(report["cells_modified"], 2)
        self.assertEqual(cleaned["Nombre Cliente"].iloc[0], "Juan El Grande")
        self.assertNotIn("<", cleaned["Nombre Cliente"].iloc[1])
        self.assertNotIn("<", cleaned["Nombre Cliente"].iloc[1])

    def test_report_counts_modified_cells(self):
        df = pd.DataFrame(
            {
                "Nombre Cliente": pd.array(['"A"', "B", "C"], dtype="string"),
                "País": pd.array(["Chile", "Chile", "Chile"], dtype="string"),
            }
        )
        _, report = sanitize_frame(df)
        self.assertEqual(report["columns"]["Nombre Cliente"], 1)
        self.assertEqual(report["columns"]["País"], 0)
        self.assertEqual(report["cells_modified"], 1)


if __name__ == "__main__":
    unittest.main()