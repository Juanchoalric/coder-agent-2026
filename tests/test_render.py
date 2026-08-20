"""Tests for D1/E5 rendering (tests/test_render.py).

- JSON is embedded in a ``<script type="application/json">`` tag with
  ``<``/``>``/``&`` escaped to ``\\uXXXX`` (never raw ``const PAYLOAD``).
- Vendored libraries are inlined -> the file has no external resource refs.
- Template placeholders are fully substituted.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from etl import render, vendor


class TestJsonEmbed(unittest.TestCase):
    def test_angle_brackets_escaped(self):
        text = render.json_embed({"nombre": "<script>alert('x')</script> & más"})
        self.assertNotIn("<script", text)
        self.assertNotIn("&", text)
        self.assertIn("\\u003c", text)
        self.assertIn("\\u003e", text)
        self.assertIn("\\u0026", text)
        # Round-trips losslessly through JSON.parse.
        self.assertEqual(json.loads(text)["nombre"], "<script>alert('x')</script> & más")

    def test_no_raw_const_payload(self):
        html = _render_fixture()
        self.assertNotIn("const PAYLOAD", html)
        self.assertIn('<script type="application/json" id="payload">', html)
        self.assertIn('<script type="application/json" id="meta">', html)


def _render_fixture() -> str:
    payload = {
        "meta": {"period": "Ene-May 2026", "run_id": "RUN-X", "generated_at": "2026-08-20",
                 "match_rate": 1.0, "source_files": ["a.xlsx"]},
        "kpis": {"total_usd": 100, "units": 5, "transactions": 1, "avg_order_usd": 100.0},
        "monthly": [], "by_category": [], "by_region": [], "by_payment": [],
        "top_products": [], "by_country": [], "by_age_bucket": [], "transactions": [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dashboard.html"
        render.render_dashboard(payload, out_path=out, write_payload=False)
        return out.read_text(encoding="utf-8")


class TestRenderDashboard(unittest.TestCase):
    def test_placeholders_fully_substituted(self):
        html = _render_fixture()
        for placeholder in ("{{PAYLOAD}}", "{{META}}", "{{VENDOR_CSS}}", "{{VENDOR_JS}}"):
            self.assertNotIn(placeholder, html)

    def test_vendored_libs_inlined_no_external_refs(self):
        html = _render_fixture()
        # D1: no external <script src>/<link href> -> runtime fully offline.
        self.assertNotIn('src="http', html)
        self.assertNotIn("src='http", html)
        self.assertNotIn('href="http', html)
        self.assertNotIn("href='http", html)
        # Each pinned asset was inlined (4 vendored <script> blocks + app + 2
        # JSON script tags).
        self.assertGreaterEqual(html.count("<script"), 6)

    def test_embedded_payload_parses(self):
        html = _render_fixture()
        start = html.index('<script type="application/json" id="payload">')
        end = html.index("</script>", start)
        raw = html[start:end].split(">", 1)[1]
        payload = json.loads(raw)
        self.assertEqual(payload["kpis"]["total_usd"], 100)
        self.assertEqual(payload["meta"]["period"], "Ene-May 2026")

    def test_vendor_assets_are_pinned_and_cached(self):
        paths = vendor.ensure_vendored()
        for name, path in paths.items():
            self.assertTrue(path.exists(), name)
            self.assertGreater(path.stat().st_size, 0, name)


if __name__ == "__main__":
    unittest.main()