```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:fb871d076702462b3413718435e59c34ba5a684a02c880fb1c86fac0defbd3b0
verdict: pass
blockers: 0
critical_findings: 0
requirements: 16/16
scenarios: 20/20
test_command: .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:d2df43027290f6247b9747c820f81c0634b6b01ffb591c2014f23ac74b92166b
build_command: .venv/bin/python -m etl build
build_exit_code: 0
build_output_hash: sha256:9e1b963c2d7c9a4584745f9b4e23aba2468e44d0e9189b28c768c68166cb7077
```

## Verification Report

**Change**: dashboard-ventas-2026
**Version**: baseline delta specs (2026-08-20), E1-E7 / D1-D6 / R1-R3
**Mode**: Standard (strict_tdd=false; stdlib unittest runner `.venv/bin/python -m unittest discover -s tests`)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 22 |
| Tasks complete | 22 |
| Tasks incomplete | 0 |

### Build & Tests Execution
**Build**: ✅ Passed
```text
$ .venv/bin/python -m etl build
[OK] build 20260820-202107-409201: 100 transacciones, match_rate=100.00%
     dashboard.html (6b314d6e9c14...) · payload.json · auditado en data_log.csv
exit=0
```

**Tests**: ✅ 61 passed / 0 failed / 0 skipped (two independent runs: 33.7s and 43.5s)
```text
$ .venv/bin/python -m unittest discover -s tests
Ran 61 tests
OK
```
Zero skips means the headless-Chrome E2E layer actually executed (playwright + real Chrome `channel=chrome`), not merely the static layer. Re-ran independently with network aborted: 0 external requests, 0 console errors, 0 page errors.

**Coverage**: ➖ Not available (no coverage tooling configured; `openspec/config.yaml` threshold 0). Static review + 61 behavioral tests + browser E2E used instead.

### Spec Compliance Matrix (16 requirements / 20 scenarios)
| Requirement | Scenario | Covering test(s) | Result |
|-------------|----------|------------------|--------|
| E1 read-only ingest, file-specific abort | E1 happy: both Excels load, sources unchanged | `test_gate.TestBuildBlocking.test_build_appends_ok_audit_row`, `test_integration.test_full_build_approve_release_flow`; sources unchanged independently proven (SHA-256 of both Excels identical before/after all runs) | ✅ COMPLIANT |
| E1 (edge) missing/corrupt | E1 edge: missing/corrupt -> file-specific abort | `test_gate.TestBuildBlocking.test_e1_missing_file_aborts` (missing). Corrupt branch manually executed: `[BLOQUEADO] Ventas: no se pudo leer el archivo corrupt.xlsx: File is not a zip file`, exit 2, FAILED row | ✅ COMPLIANT (corrupt branch: runtime-verified manually, see SUGGESTION 2) |
| E2 join + 90% threshold | E2 happy: 100% overlap -> clean frame, rate recorded | `test_validate.TestJoinE2.test_full_overlap_100_percent`, `test_partial_orphans_on_one_side`, `test_gate.TestBuildBlocking.test_build_appends_ok_audit_row` (match_rate 1.000000) | ✅ COMPLIANT |
| E2 (edge) <90% blocks | E2 edge: alert, run flagged failed | `test_validate.TestJoinE2.test_overlap_below_90_blocks`, `test_gate.TestBuildBlocking.test_e2_edge_below_90_percent_blocks`; independently re-run (80% ventas): stderr alert, exit 2, FAILED row with match_rate=0.800000, no dashboard written | ✅ COMPLIANT |
| E3 numerics finite/no-NaN/no-text | E3 happy: int64 passes | `test_validate.TestNumericsE3.test_clean_numerics_pass` | ✅ COMPLIANT |
| E3 (edge) NaN/text aborts | E3 edge: run aborts, violation logged | `test_validate.TestNumericsE3.test_nan_in_total_aborts`, `test_text_in_total_aborts`, `test_non_finite_aborts`, `test_gate.TestBuildBlocking.test_e3_text_in_total_aborts` (exit 2, no output) | ✅ COMPLIANT |
| E4 ISO date parsing | E4: YYYY-MM-DD -> datetime before month agg | `test_validate.TestDatesE4.test_iso_dates_parse` (dt.month asserts), `test_non_iso_date_aborts` | ✅ COMPLIANT |
| E5 sanitization before JS injection | E5: quotes+`<script>` -> JSON-safe, no markup | `test_sanitize.*` (script neutralized, quotes/backslashes/control chars, frame report), `test_render.TestJsonEmbed.test_angle_brackets_escaped` (round-trip via JSON.parse), `test_e2e.test_payload_transactions_are_sanitized`; raw `<`/`>` absent from payload region of built file | ✅ COMPLIANT |
| E6 KPIs + 8 aggregates | E6: 100-row frame -> all groups + transactions | `test_aggregate.*` (KPIs 274285/1035/100/2742.85, all 8 groups, 100 txns, stdlib json.dumps OK); real build payload: 5 monthly, 4 category, 4 region, 4 payment, 10 top, 7 country, 5 age-bucket, 100 transactions | ✅ COMPLIANT |
| E7 audit row per run | E7: successful run -> row appended | `test_audit.*` (14 contract columns, header once, latest filters, invalid event rejected), `test_gate.test_build_appends_ok_audit_row`; FAILED rows carry match_rate + validation message | ✅ COMPLIANT |
| D1 single-file offline, no runtime fetch | D1: opened without network -> renders from embedded payload | `test_render.test_vendored_libs_inlined_no_external_refs`, `test_e2e.test_d1_single_file_offline_safe` + `test_d1_json_embedded_via_script_tag`, `test_e2e.TestDashboardBrowserE2E.test_renders_kpis_and_charts_offline` (external requests == []); independently re-verified: 0 external refs, 0 network requests, payload parses | ✅ COMPLIANT |
| D2 "Ene-May 2026", no YoY | D2: header labels period, no YoY | `test_e2e.test_d2_period_label_no_yoy` (label present, meta.period correct, no "YoY"/"vs 2025"); only textual match for "año completo" is the template comment explicitly stating no full-year claims | ✅ COMPLIANT |
| D3 four KPI cards | D3: cards show aggregated values | `test_e2e.test_d3_four_kpi_cards` + browser asserts: `$274,285 / 1,035 / 100 / $2,742.85` rendered | ✅ COMPLIANT |
| D4 6+ Chart.js charts | D4: 6+ charts with datasets | `test_e2e.test_d4_six_plus_charts` (7 canvases: monthly/category/region/payment/top-products/country/age), browser: 7 `<canvas>` with positive bounding boxes | ✅ COMPLIANT |
| D5 DataTable search/sort/pagination | D5: search filters without reload | `test_e2e.test_d5_datatable_configured` (static) + `test_datatable_search_sort_pagination` (browser: 10/page, search "Laptop" -> 8 rows, sort Producto -> sorting_asc, Siguiente -> 11-20); independently re-verified against real DOM | ✅ COMPLIANT |
| D6 local-only delivery | D6: approved dashboard copied to local destination | `test_gate.test_r1_full_flow_releases`, `test_integration.test_full_build_approve_release_flow`; independently: `release --dest /tmp/.../out2` copied 897124-byte file locally; no server/deploy code anywhere in `etl/` | ✅ COMPLIANT |
| R1 gate: no release without approval | R1 happy: build+approve -> released | `test_gate.test_r1_full_flow_releases`, `test_integration.test_full_build_approve_release_flow`; independently: release after approve -> exit 0 | ✅ COMPLIANT |
| R1 (edge) no approval blocks | R1 edge: dashboard, no approval -> blocked | `test_gate.test_r1_no_approval_blocks_release`, `test_integration.test_release_without_approval_blocks`; independently: exit 1, `[BLOQUEADO] ... (R1)`, no dest created | ✅ COMPLIANT |
| R2 approver/timestamp/fingerprint | R2: approval logged with 3 fields | `test_audit.test_approval_row_records_approver_timestamp_fingerprint`, `test_gate.test_r2_approval_records_approver_timestamp_fingerprint` (64-hex sha256 equals live file digest) | ✅ COMPLIANT |
| R3 fresh approval per run | R3: new run invalidates old approval | `test_gate.test_r3_rerun_invalidates_prior_approval`, `test_integration.test_rerun_invalidates_approval_at_cli_level`; independently: rebuild -> release blocked with run_id mismatch -> re-approve unblocks; tamper-after-approval also blocked (digest mismatch) | ✅ COMPLIANT |

**Compliance summary**: 20/20 scenarios compliant

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| E1 read-only | ✅ Implemented | `ingest._read_sheet`: openpyxl engine, existence + is_file checks, `IngestError` per file; missing AND corrupt branches abort with file-specific message; pandas 3 explicit dtypes (`dtype_backend="numpy_nullable"` + `astype("string")`, `pd.to_numeric(errors="raise")`) |
| E2 join + gate | ✅ Implemented | `validate.inner_join` on `ID Transacción` (set-intersection rate = matched/max(unique)); `check_match_rate` raises `JoinBreachError` < 0.90; main maps it to stderr alert + FAILED row + exit 2 |
| E3 numerics | ✅ Implemented | `validate_numerics`: numeric-dtype check, NaN count, non-finite detection on floats; violations raise `ValidationError` (aborts run, logged) |
| E4 dates | ✅ Implemented | `pd.to_datetime(format="ISO8601", errors="coerce")` + unparsed-count abort, before month aggregation |
| E5 sanitize | ✅ Implemented | quotes/backslashes stripped, angle brackets -> parens, control chars removed, per-column report for audit; defense-in-depth: render escapes `<` `>` `&` to `\uXXXX` inside `<script type="application/json">` |
| E6 aggregates | ✅ Implemented | KPIs + monthly/category/region/payment/top-products/country/age-bucket/transactions; numpy_nullable -> native types before `json.dumps`; payload keys match design contract exactly (categoria, region, metodo, producto, pais, bucket) |
| E7 audit | ✅ Implemented | `data_log.csv` one row/event, 14 columns exactly per design contract; header-once; approve/release rows carry approver/approval_ts/artifact_sha256 |
| D1 offline single file | ✅ Implemented | vendored jQuery/DataTables/Chart.js/Tailwind inlined (etl/vendor.py, pinned versions); zero external src/href; payload via JSON script tag |
| D2 label | ✅ Implemented | "Ene-May 2026" in title, header badge, footer; `aggregate.PERIOD` constant; no YoY claims |
| D3 KPIs | ✅ Implemented | 4 `kpi-*` cards fed from payload; `Intl.NumberFormat` USD |
| D4 charts | ✅ Implemented | 7 Chart.js instances (bar/doughnut) over all E6 aggregates |
| D5 DataTable | ✅ Implemented | `$("#transactions-table").DataTable(...)` client-side data, search/sort/pagination, Spanish labels |
| D6 local only | ✅ Implemented | `release --dest` = `shutil.copy2` to local dir; no network/HTTP code exists |
| R1 gate | ✅ Implemented | release requires latest OK approval row; exit 1 otherwise |
| R2 fingerprint | ✅ Implemented | approve records SHA-256 of current dashboard.html + run_id; blocks if digest != build digest |
| R3 freshness | ✅ Implemented | release compares approval.run_id vs latest build.run_id; digest re-checked on release |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Join breach < 90% -> BLOCK fail-stop | ✅ Yes | abort, stderr alert, FAILED row with match_rate, exit 2, no output written |
| SHA-256 fingerprint (R2) | ✅ Yes | hex digest of dashboard.html bound to run_id; recomputed on approve and release |
| Vendor-and-inline (D1) | ✅ Yes | pinned CDN fetched once at build, cached in etl/vendor/ (gitignored), inlined; runtime offline proven |
| JSON script tag + `\u003c` escaping | ✅ Yes | `<script type="application/json" id="payload">`, `<` `>` `&` escaped; never raw `const PAYLOAD` |
| numpy_nullable + explicit string dtypes | ✅ Yes | pandas 3 migration honored in ingest.py |
| ETL/template separation | ✅ Yes | etl/*.py pipeline vs etl/templates/dashboard_template.html |
| argparse CLI build/approve/release | ✅ Yes | exit codes 0/1/2 as designed |
| `.venv` in apply | ✅ Yes | .venv present, deps installed, requirements.txt pinned |

Documented deviations (apply-progress, none break a spec): 7 chart canvases (>= 6 per D4); source accents preserved in values (keys match contract); jQuery added as DataTables dependency (not named in design vendor list); `tests/test_render.py` added beyond tasks.md.

### Issues Found
**CRITICAL**: None

**WARNING**: None

**SUGGESTION**:
1. Blocked builds (E2/E3/E1 edges) leave a stale `dashboard.html` from a previous successful run in place. The failing run writes no output (spec satisfied) and the audit trail + stderr message disambiguate, but consider removing the stale file on a blocked build or printing its run_id so the current artifact is never mistaken for fresh output.
2. The E1 edge "corrupt/unreadable Excel" branch has no automated unit test (only the missing-file branch is covered; I verified the corrupt branch manually: `[BLOQUEADO] Ventas: no se pudo leer el archivo corrupt.xlsx: File is not a zip file`, exit 2). Add a corrupt-file test (write garbage bytes, assert `IngestError`).
3. `openspec/config.yaml` `verify.test_command`, `apply.test_command`, and `testing.*` are empty/stale (bootstrapped before the suite existed). Populate with `.venv/bin/python -m unittest discover -s tests`. Note `python` is not on PATH on this machine; the venv interpreter is required (apply report's own evidence used it).
4. The design's File Changes table says sanitize.py "strips" angle brackets; the implementation replaces `<`/`>` with parentheses (keeps content readable, still markup-proof, documented in module docstring). Update design wording for accuracy.
5. Add jQuery to the design's vendor asset list (it is a hard DataTables dependency inlined by vendor.py but not named in the design).

### Verdict
**PASS**
All 22 tasks complete; 61/61 tests pass (0 skips, incl. real headless-Chrome offline E2E); 16/16 requirements and 20/20 scenarios COMPLIANT; independent CLI flow re-exercise of build/approve/release plus negative gates (no approval, tamper, stale run, missing/corrupt files, <90% match) all behave per spec/design; no CRITICAL or WARNING findings.
