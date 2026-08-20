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

> **RESOLVED (2026-08-20)**: user approved a SINGLE PR with `size:exception`
> (maintainer-accepted; ~1100 lines). Chained PRs were NOT created; commits
> below follow the 4 suggested work units inside the one PR.

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Foundation + ETL core + tests | PR 1 | base main |
| 2 | Aggregate + audit + tests | PR 2 | base PR 1 |
| 3 | Vendor + template + render + tests | PR 3 | base PR 2 |
| 4 | CLI gate + integration/E2E tests | PR 4 | base PR 3; merges main |

## Phase 1: Foundation

- [x] 1.1 Create `.venv`; install pandas==3.0.3, numpy==2.5.1, openpyxl, pytest
- [x] 1.2 Extend `.gitignore`: `dashboard.html`, `payload.json`, `etl/vendor/`
- [x] 1.3 Create `etl/__init__.py` + `etl/__main__.py` (entrypoint to main.main)

## Phase 2: ETL core

- [x] 2.1 `etl/ingest.py`: read-only Excel load (E1), column check, `dtype_backend='numpy_nullable'` + `string` dtypes, file-specific abort
- [x] 2.2 `etl/validate.py`: finite/no-NaN/no-text numerics (E3); ISO dates (E4); inner join on `ID Transacción` + match_rate (E2)
- [x] 2.3 `etl/sanitize.py`: strip quotes, backslashes, angle brackets, control chars (E5)
- [x] 2.4 `etl/aggregate.py`: KPIs + monthly/category/region/payment/top-product/country/age-bucket/transactions (E6)
- [x] 2.5 `etl/audit.py`: append `data_log.csv` (run_id, counts, match_rate, status, sha256, approver) (E7, R2)

## Phase 3: Rendering

- [x] 3.1 `etl/vendor.py`: pinned CDN download (Tailwind/Chart.js/DataTables), cache `etl/vendor/`, inline (D1)
- [x] 3.2 `etl/templates/dashboard_template.html`: "Ene-May 2026" header (D2), 4 KPI cards (D3), 6 canvases (D4), DataTable JS (D5), `{{PAYLOAD}}`/`{{META}}`
- [x] 3.3 `etl/render.py`: fill template; JSON via `<script type="application/json">`, escape `<`->`\u003c`; inline vendored libs (D1, E5)

## Phase 4: CLI + approval gate

- [x] 4.1 `etl/main.py`: argparse `build|approve|release`; build BLOCKs on match_rate < 90% (stderr alert, FAILED row, exit != 0, no output) (E2 edge)
- [x] 4.2 approve `--approver`: record SHA-256 + run_id (R2); release `--dest`: copy only if digest + run_id match (R1, R3, D6)

## Phase 5: Testing (stdlib unittest)

- [x] 5.1 `tests/test_validate.py`: E3 NaN/text abort, E2 <90% block, E4 date parse
- [x] 5.2 `tests/test_sanitize.py`: E5 neutralizes `<script>`/quotes/backslashes/control chars
- [x] 5.3 `tests/test_aggregate.py`: E6 100-row frame -> all groups + transactions
- [x] 5.4 `tests/test_audit.py`: E7 row fields per event
- [x] 5.5 `tests/test_gate.py`: R1 no-approval blocks; R2 logged; R3 re-run invalidates approval
- [x] 5.6 `tests/test_integration.py`: CLI build -> approve -> release on real Excels, exit codes
- [x] 5.7 E2E: offline `dashboard.html` -> 4 KPI cards, 6+ charts, DataTable search/sort/pagination (D1-D5)

> Extra: `tests/test_render.py` added so work unit 3 (vendor/template/render)
> is self-verifying (JSON embedding E5, offline inlining D1).

## Phase 6: Cleanup

- [x] 6.1 Commit per work unit (PR 1-4, tests with code); confirm generated files untracked
- [x] 6.2 Run `python -m etl build` + manual dashboard review; tick `[x]`

**Apply result (2026-08-20)**: all 22 tasks complete. 61/61 tests pass
(`python -m unittest discover -s tests`, incl. headless-Chrome E2E with
network aborted). Final build `python -m etl build` OK: 100 transactions,
match_rate=100%, dashboard.html 897 KB offline-safe, 7 charts, DataTable
search/sort/pagination verified. Commits: scaffold + 4 work units
(5 commits on `main`, single PR with `size:exception`).