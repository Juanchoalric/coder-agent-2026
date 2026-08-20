"""ETL package for the Business Dashboard (dashboard-ventas-2026).

Pipeline: ingest (read-only Excels) -> validate (E2-E4) -> sanitize (E5)
-> aggregate (E6) -> render dashboard.html (D1-D5) -> audit (E7),
gated by a human-in-the-loop approve/release CLI (R1-R3).
"""

__version__ = "1.0.0"