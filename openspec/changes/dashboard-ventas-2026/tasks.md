# Tasks: Dashboard de Ventas 2026

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1000-1100 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 -> PR 2 -> PR 3 -> PR 4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Foundation + ETL core + tests | PR 1 | base main |
| 2 | Aggregate + audit + tests | PR 2 | base PR 1 |
| 3 | Vendor + template + render + tests | PR 3 | base PR 2 |
| 4 | CLI gate + integration/E2E tests | PR 4 | base PR 3; merges main |

## Phase 1: Foundation

- [ ] 1.1 Create `.venv`; install pandas==3.0.3, numpy==2.5.1, openpyxl, pytest
- [ ] 1.2 Extend `.gitignore`: `dashboard.html`, `payload.json`, `etl/vendor/`
- [ ] 1.3 Create `etl/__init__.py` + `etl/__main__.py` (entrypoint to main.main)

## Phase 2: ETL core

- [ ] 2.1 `etl/ingest.py`: read-only Excel load (E1), column check, `dtype_backend='numpy_nullable'` + `string` dtypes, file-specific abort
- [ ] 2.2 `etl/validate.py`: finite/no-NaN/no-text numerics (E3); ISO dates (E4); inner join on `ID Transacción` + match_rate (E2)
- [ ] 2.3 `etl/sanitize.py`: strip quotes, backslashes, angle brackets, control chars (E5)
- [ ] 2.4 `etl/aggregate.py`: KPIs + monthly/category/region/payment/top-product/country/age-bucket/transactions (E6)
- [ ] 2.5 `etl/audit.py`: append `data_log.csv` (run_id, counts, match_rate, status, sha256, approver) (E7, R2)

## Phase 3: Rendering

- [ ] 3.1 `etl/vendor.py`: pinned CDN download (Tailwind/Chart.js/DataTables), cache `etl/vendor/`, inline (D1)
- [ ] 3.2 `etl/templates/dashboard_template.html`: "Ene-May 2026" header (D2), 4 KPI cards (D3), 6 canvases (D4), DataTable JS (D5), `{{PAYLOAD}}`/`{{META}}`
- [ ] 3.3 `etl/render.py`: fill template; JSON via `<script type="application/json">`, escape `<`->`\u003c`; inline vendored libs (D1, E5)

## Phase 4: CLI + approval gate

- [ ] 4.1 `etl/main.py`: argparse `build|approve|release`; build BLOCKs on match_rate < 90% (stderr alert, FAILED row, exit != 0, no output) (E2 edge)
- [ ] 4.2 approve `--approver`: record SHA-256 + run_id (R2); release `--dest`: copy only if digest + run_id match (R1, R3, D6)

## Phase 5: Testing (stdlib unittest)

- [ ] 5.1 `tests/test_validate.py`: E3 NaN/text abort, E2 <90% block, E4 date parse
- [ ] 5.2 `tests/test_sanitize.py`: E5 neutralizes `<script>`/quotes/backslashes/control chars
- [ ] 5.3 `tests/test_aggregate.py`: E6 100-row frame -> all groups + transactions
- [ ] 5.4 `tests/test_audit.py`: E7 row fields per event
- [ ] 5.5 `tests/test_gate.py`: R1 no-approval blocks; R2 logged; R3 re-run invalidates approval
- [ ] 5.6 `tests/test_integration.py`: CLI build -> approve -> release on real Excels, exit codes
- [ ] 5.7 E2E: offline `dashboard.html` -> 4 KPI cards, 6+ charts, DataTable search/sort/pagination (D1-D5)

## Phase 6: Cleanup

- [ ] 6.1 Commit per work unit (PR 1-4, tests with code); confirm generated files untracked
- [ ] 6.2 Run `python -m etl build` + manual dashboard review; tick `[x]`