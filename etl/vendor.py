"""Pin, download, cache and inline vendored frontend libraries (D1).

The build requires network exactly ONCE (the first run downloads the pinned
assets into ``etl/vendor/``). Subsequent builds are fully offline-safe: the
cached assets are inlined into the single ``dashboard.html`` file, so the
dashboard renders with no data network at runtime.

Pinned assets (versioned URLs; content is immutable per URL):
- Tailwind CSS play CDN 3.4.16
- Chart.js 4.4.7 (UMD)
- jQuery 3.7.1 (DataTables dependency)
- DataTables 1.13.8 (CSS + JS)
"""

from __future__ import annotations

import pathlib
import urllib.request

VENDOR_DIR = pathlib.Path(__file__).resolve().parent / "vendor"

# name -> (pinned URL, kind). Kind drives how the asset is inlined.
ASSETS: dict[str, tuple[str, str]] = {
    "tailwind.js": ("https://cdn.tailwindcss.com/3.4.16", "js"),
    "chart.js": ("https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js", "js"),
    "jquery.js": ("https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js", "js"),
    "datatables.css": (
        "https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css",
        "css",
    ),
    "datatables.js": (
        "https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js",
        "js",
    ),
}


class VendorError(RuntimeError):
    """Raised when a pinned asset cannot be downloaded."""


def _download(url: str, dest: pathlib.Path) -> None:
    """Download *url* to *dest* (one-time network fetch at build time)."""
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
    except Exception as exc:
        raise VendorError(f"no se pudo descargar el asset vendored {url}: {exc}") from exc
    if not data:
        raise VendorError(f"asset vacío descargado desde {url}")
    dest.write_bytes(data)


def ensure_vendored(force: bool = False) -> dict[str, pathlib.Path]:
    """Download missing pinned assets into ``etl/vendor/`` and return their paths.

    ``force=True`` re-downloads everything (used by tests and manual refresh).
    """
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, pathlib.Path] = {}
    for name, (url, _kind) in ASSETS.items():
        dest = VENDOR_DIR / name
        if force or not dest.exists() or dest.stat().st_size == 0:
            _download(url, dest)
        paths[name] = dest
    return paths


def vendor_css_block(paths: dict[str, pathlib.Path] | None = None) -> str:
    """Return inlined ``<style>`` blocks for the CSS assets (D1)."""
    paths = paths or ensure_vendored()
    blocks = []
    for name, _url, kind in _asset_meta():
        if kind != "css":
            continue
        blocks.append(f"<style>\n{paths[name].read_text(encoding='utf-8')}\n</style>")
    return "\n".join(blocks)


def vendor_js_block(paths: dict[str, pathlib.Path] | None = None) -> str:
    """Return inlined ``<script>`` blocks for the JS assets, in load order (D1).

    Order matters: jQuery first (DataTables depends on it), then DataTables,
    then Chart.js, then the Tailwind play-CDN runtime.
    """
    paths = paths or ensure_vendored()
    blocks = []
    for name, _url, kind in _asset_meta():
        if kind != "js":
            continue
        blocks.append(f"<script>\n{paths[name].read_text(encoding='utf-8')}\n</script>")
    return "\n".join(blocks)


def _asset_meta() -> list[tuple[str, str, str]]:
    """[(name, url, kind)] in the order assets must appear in the HTML."""
    return [
        (name, ASSETS[name][0], ASSETS[name][1])
        for name in ("jquery.js", "datatables.js", "datatables.css", "chart.js", "tailwind.js")
    ]