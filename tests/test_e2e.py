"""E2E: offline dashboard.html verification (5.7, D1-D5).

Static layer (always runs): build the dashboard from the real Excels and
assert the single file is offline-safe with 4 KPI cards, 6+ chart canvases,
embedded JSON payload, and DataTable configuration.

Browser layer (skips gracefully when Chrome/playwright are unavailable):
load the file with all network requests aborted and exercise DataTables
search, sort and pagination against the real DOM.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = PROJECT_ROOT / "dashboard.html"

KPI_IDS = ("kpi-total", "kpi-units", "kpi-transactions", "kpi-avg")
CANVAS_IDS = (
    "chart-monthly", "chart-category", "chart-region", "chart-payment",
    "chart-top-products", "chart-country", "chart-age",
)


def build_dashboard() -> None:
    """Run the real CLI build in the project root (idempotent)."""
    result = subprocess.run(
        [sys.executable, "-m", "etl", "build"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"build falló: {result.stderr}")


def extract_payload(html: str) -> dict:
    start = html.index('<script type="application/json" id="payload">')
    end = html.index("</script>", start)
    return json.loads(html[start:end].split(">", 1)[1])


class TestDashboardE2EStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_dashboard()
        cls.html = DASHBOARD.read_text(encoding="utf-8")
        cls.payload = extract_payload(cls.html)

    def test_d1_single_file_offline_safe(self):
        # No external resource references -> opens without any data network.
        for needle in ('src="http', "src='http", 'href="http', "href='http",
                       '<link rel="stylesheet" href=', '<script src='):
            self.assertNotIn(needle, self.html)
        self.assertGreater(DASHBOARD.stat().st_size, 100_000)  # vendored libs inlined

    def test_d1_json_embedded_via_script_tag(self):
        self.assertIn('<script type="application/json" id="payload">', self.html)
        self.assertNotIn("const PAYLOAD", self.html)
        # Every raw "<" inside the payload region is escaped to \u003c (E5).
        # (The current dataset contains no angle brackets, so the escaped form
        # may be absent; the escaping itself is covered in test_render.py.)
        start = self.html.index('<script type="application/json" id="payload">')
        end = self.html.index("</script>", start)
        payload_region = self.html[start:end].split(">", 1)[1]
        self.assertNotIn("<", payload_region)

    def test_d2_period_label_no_yoy(self):
        self.assertIn("Ene-May 2026", self.html)
        self.assertEqual(self.payload["meta"]["period"], "Ene-May 2026")
        self.assertNotIn("YoY", self.html)
        self.assertNotIn("vs 2025", self.html)

    def test_d3_four_kpi_cards(self):
        for kpi in KPI_IDS:
            self.assertIn(f'id="{kpi}"', self.html)
        kpis = self.payload["kpis"]
        # Exploration-verified totals.
        self.assertEqual(kpis["total_usd"], 274285)
        self.assertEqual(kpis["units"], 1035)
        self.assertEqual(kpis["transactions"], 100)
        self.assertAlmostEqual(kpis["avg_order_usd"], 2742.85, places=2)

    def test_d4_six_plus_charts(self):
        for cid in CANVAS_IDS:
            self.assertIn(f'id="{cid}"', self.html)
        self.assertGreaterEqual(len(CANVAS_IDS), 6)
        self.assertTrue(self.payload["monthly"])
        self.assertTrue(self.payload["by_category"])
        self.assertTrue(self.payload["by_region"])
        self.assertTrue(self.payload["by_payment"])
        self.assertTrue(self.payload["top_products"])
        self.assertTrue(self.payload["by_country"])

    def test_d5_datatable_configured(self):
        self.assertIn('id="transactions-table"', self.html)
        self.assertIn(".DataTable(", self.html)
        self.assertIn("pageLength: 10", self.html)
        self.assertIn("lengthMenu", self.html)
        self.assertIn("order:", self.html)
        self.assertIn("Buscar", self.html)  # Spanish search label
        self.assertEqual(len(self.payload["transactions"]), 100)

    def test_payload_transactions_are_sanitized(self):
        for txn in self.payload["transactions"]:
            self.assertNotIn("<", txn["cliente"])
            self.assertNotIn('"', txn["cliente"])


class TestDashboardBrowserE2E(unittest.TestCase):
    """Real headless-Chrome interaction: search, sort, pagination (D5)."""

    @classmethod
    def setUpClass(cls):
        build_dashboard()
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise unittest.SkipTest("playwright no instalado en el venv")
        cls._pw = sync_playwright().start()
        try:
            cls.browser = cls._pw.chromium.launch(channel="chrome", headless=True)
        except Exception as exc:
            cls._pw.stop()
            raise unittest.SkipTest(f"Chrome headless no disponible: {exc}")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls._pw.stop()

    def _load_offline(self):
        """Load dashboard.html aborting every http(s) request (proves D1)."""
        context = self.browser.new_context()
        external = []

        def _route(route, request):
            if request.url.startswith(("http://", "https://")):
                external.append(request.url)
                route.abort()
            else:
                route.continue_()

        context.route("**/*", _route)
        page = context.new_page()
        page.goto(DASHBOARD.as_uri(), wait_until="load")
        page.wait_for_selector(".dataTables_wrapper", timeout=15000)
        return page, context, external

    def test_renders_kpis_and_charts_offline(self):
        page, context, external = self._load_offline()
        try:
            self.assertEqual(external, [])  # zero network requests (D1)
            self.assertEqual(page.title(), "Dashboard de Ventas 2026 | Ene-May 2026")
            # D3: KPI values rendered (exploration-verified).
            self.assertEqual(page.locator("#kpi-total").inner_text(), "$274,285")
            self.assertEqual(page.locator("#kpi-units").inner_text(), "1,035")
            self.assertEqual(page.locator("#kpi-transactions").inner_text(), "100")
            self.assertEqual(page.locator("#kpi-avg").inner_text(), "$2,742.85")
            # D2: period badge visible, no YoY.
            self.assertIn("Ene-May 2026", page.locator("header").inner_text())
            # D4: 7 chart canvases created by Chart.js.
            self.assertEqual(page.locator("canvas").count(), len(CANVAS_IDS))
            for cid in CANVAS_IDS:
                box = page.locator(f"#{cid}").bounding_box()
                self.assertIsNotNone(box, cid)
                self.assertGreater(box["width"], 0, cid)
        finally:
            context.close()

    def test_datatable_search_sort_pagination(self):
        page, context, _external = self._load_offline()
        try:
            table = page.locator("#transactions-table")
            # Pagination: 100 rows, 10 per page.
            self.assertEqual(page.locator("#transactions-table tbody tr").count(), 10)
            info = page.locator(".dataTables_info").inner_text()
            self.assertIn("Mostrando 1 a 10 de 100 transacciones", info)
            # Search (D5): "Laptop" -> Laptop Pro M1 (8 transactions).
            page.fill(".dataTables_filter input", "Laptop")
            page.wait_for_function(
                "document.querySelectorAll('#transactions-table tbody tr').length === 8",
                timeout=10000,
            )
            self.assertEqual(page.locator("#transactions-table tbody tr").count(), 8)
            info = page.locator(".dataTables_info").inner_text()
            self.assertIn("filtrado de 100 en total", info)
            # Sort (D5): click the "Producto" header -> column sorts ascending.
            page.fill(".dataTables_filter input", "")
            page.wait_for_function(
                "document.querySelectorAll('#transactions-table tbody tr').length === 10",
                timeout=10000,
            )
            header = page.locator("#transactions-table thead th", has_text="Producto")
            header.click()
            page.wait_for_timeout(400)  # DataTables sort animation
            self.assertIn(
                "sorting_asc",
                header.get_attribute("class") or "",
            )
            # Pagination next (D5): page 2 shows rows 11-20.
            page.locator(".dataTables_paginate .paginate_button", has_text="Siguiente").click()
            page.wait_for_timeout(400)
            info = page.locator(".dataTables_info").inner_text()
            self.assertIn("Mostrando 11 a 20 de 100 transacciones", info)
            # Payload embedded (D1): parseable, exploration totals intact.
            payload = page.evaluate(
                "JSON.parse(document.getElementById('payload').textContent)"
            )
            self.assertEqual(payload["kpis"]["total_usd"], 274285)
        finally:
            context.close()


if __name__ == "__main__":
    unittest.main()