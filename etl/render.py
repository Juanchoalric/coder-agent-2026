"""Render the single-file dashboard (D1-D5).

- Fills ``dashboard_template.html`` placeholders ``{{META}}`` / ``{{PAYLOAD}}``
  with JSON embedded in ``<script type="application/json">`` tags.
- Escapes ``<`` ``>`` ``&`` to ``\\uXXXX`` inside the JSON text so nothing can
  close the script tag or be interpreted as markup (defense-in-depth over E5).
- Inlines the vendored Tailwind/Chart.js/jQuery/DataTables assets (D1) so the
  file is fully offline-safe with no runtime data fetch.
- Also writes ``payload.json`` (pretty) as a human-reviewable intermediate
  (gitignored).
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from etl import vendor

TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent / "templates"
DEFAULT_TEMPLATE = TEMPLATE_DIR / "dashboard_template.html"
DASHBOARD_OUT = "dashboard.html"
PAYLOAD_OUT = "payload.json"


def json_embed(data: Any) -> str:
    """Serialize *data* for a ``<script type="application/json">`` tag (E5/D1).

    ``json.dumps`` already escapes quotes/backslashes/control chars; we
    additionally escape ``<`` ``>`` ``&`` as ``\\uXXXX`` so the text can never
    terminate the script tag or look like markup. ``JSON.parse`` restores the
    original characters, so the payload round-trips losslessly.
    """
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return text


def _read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def render_dashboard(
    payload: dict,
    template_path: str | pathlib.Path = DEFAULT_TEMPLATE,
    out_path: str | pathlib.Path = DASHBOARD_OUT,
    write_payload: bool = True,
    vendored: dict[str, pathlib.Path] | None = None,
) -> pathlib.Path:
    """Render ``dashboard.html`` (and optionally ``payload.json``).

    Order of replacement matters: vendored assets are injected FIRST so a
    literal ``{{PAYLOAD}}`` sequence inside a library cannot be substituted.
    """
    template = _read_text(pathlib.Path(template_path))
    vendored = vendored or vendor.ensure_vendored()

    html = template
    html = html.replace("{{VENDOR_CSS}}", vendor.vendor_css_block(vendored))
    html = html.replace("{{VENDOR_JS}}", vendor.vendor_js_block(vendored))
    html = html.replace("{{META}}", json_embed(payload.get("meta", {})))
    html = html.replace("{{PAYLOAD}}", json_embed(payload))

    out = pathlib.Path(out_path)
    out.write_text(html, encoding="utf-8")

    if write_payload:
        pathlib.Path(PAYLOAD_OUT).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return out