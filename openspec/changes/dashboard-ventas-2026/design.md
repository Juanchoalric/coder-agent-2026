# Design: Dashboard de Ventas 2026

## Technical Approach

Greenfield hybrid cell per `blueprint.md`: read-only pandas ETL (`etl/`) validates dtypes, inner-joins on `ID Transacción`, sanitizes strings, aggregates, and renders a single-file `dashboard.html` with an embedded JSON payload (vendored Tailwind/Chart.js/DataTables inlined at build). A human-in-the-loop CLI gate (`approve`/`release`) controls local release. Satisfies E1-E7, D1-D6, R1-R3. Config rule honored: ETL (Python) strictly separated from template/JS generation.

## Architecture Decisions

| Decision | Options considered | Tradeoff | Choice |
|---|---|---|---|
| Join breach < 90% (E2) | CONTINUE with flagged output vs BLOCK | Continuing ships partial financial data that may be mistaken for complete | **BLOCK (fail-stop)**: abort run, no `dashboard.html`, alert printed, `data_log.csv` row `status=FAILED` with `match_rate`, non-zero exit. Blueprint: "se detiene el procesamiento y se levanta una alerta"; spec E2 edge already flags the run failed. Contract for sdd-tasks |
| Artifact fingerprint (R2) | SHA-256 of HTML bytes vs MD5 vs payload hash | SHA-256 collision-safe, stdlib `hashlib`, fingerprints the exact released artifact | **SHA-256 hex digest of `dashboard.html`**; recorded in approval event row (`artifact_sha256`) with `approver`, `approval_ts`, `run_id`. `release` recomputes digest and compares |
| Library delivery (D1) | CDN-only vs vendor-and-inline | CDN fails spec D1 ("opened without data network ... charts render") and blueprint's portability | **Vendor pinned Tailwind/Chart.js/DataTables at build** (`etl/vendor.py`, cached, gitignored), inline CSS/JS into the single file. Runtime fully offline; build needs internet once |
| JSON embedding (E5/D1) | Raw `const PAYLOAD = {...}` vs JSON script tag | Raw injection is a JS-injection vector | `<script type="application/json" id="payload">` + `json.dumps(ensure_ascii=False)` then escape `<` to `\u003c`; parsed with `JSON.parse`. Defense-in-depth over E5 |
| dtypes (E3) | Default inference vs explicit | pandas 3 emits `Pandas4Warning` on `select_dtypes('object')` | Read with `dtype_backend='numpy_nullable'` + explicit pandas `string` dtype for text columns |
| ETL/template separation | One script vs package | Config rule mandates separation | `etl/*.py` pipeline + `etl/templates/dashboard_template.html` skeleton with `{{PAYLOAD}}`/`{{META}}` placeholders |
| CLI surface | Ad-hoc scripts vs commands | Reproducible gate flow | `python -m etl build|approve|release` (stdlib `argparse`) |
| Venv | Skip vs create | Reproducibility | Create `.venv` in apply (already gitignored); pytest optional per config |

## Data Flow

```
Usuarios_Ventas_2026.xlsx ─┐
                          ├─ ingest read-only (E1) -> validate numerics/dates (E3,E4)
Ventas_Productos_2026.xlsx ┘        |
                     inner join on ID Transacción (E2) -> match_rate >= 90%?
                          NO -> BLOCK: alert, exit != 0, FAILED audit row (no dashboard)
                          YES -> sanitize strings (E5) -> aggregate (E6) -> payload JSON
                                -> render dashboard.html (vendored libs inlined) -> audit row (E7)
human: approve --approver X -> sha256 recorded (R2) | release --dest <dir>
       -> copy ONLY if current sha256 == approval sha256 AND same run_id (R1, R3, D6)
```

## File Changes

| File | Action | Description |
|---|---|---|
| `etl/main.py` | Create | CLI build/approve/release; approval gate logic (R1-R3, D6) |
| `etl/ingest.py` | Create | Read-only Excel load, column-presence check, explicit dtypes (E1) |
| `etl/validate.py` | Create | Numeric finite/NaN/text checks, ISO date parse, join + match rate (E2-E4) |
| `etl/sanitize.py` | Create | Strip quotes, backslashes, angle brackets, control chars (E5) |
| `etl/aggregate.py` | Create | KPIs + monthly/category/region/payment/top-product/country/age/transactions (E6) |
| `etl/audit.py` | Create | Append `data_log.csv` events: build, approve, release (E7, R2) |
| `etl/render.py` | Create | Template fill, JSON embedding, inline vendored libs (D1-D5) |
| `etl/vendor.py` | Create | Pinned CDN download + cache + inline |
| `etl/templates/dashboard_template.html` | Create | Skeleton: header "Ene-May 2026" (D2), 4 KPI cards (D3), 6 chart canvases (D4), DataTable (D5) |
| `dashboard.html` | Generated | Deliverable, gitignored |
| `data_log.csv` | Generated | Audit trail (already gitignored) |
| `.gitignore` | Modify | Add `dashboard.html`, `payload.json`, `etl/vendor/` |

## Interfaces / Contracts

JSON payload (embedded; keys in Spanish match source columns):

```json
{"meta":{"period":"Ene-May 2026","run_id":"...","generated_at":"...","match_rate":1.0,"source_files":["Usuarios_Ventas_2026.xlsx","Ventas_Productos_2026.xlsx"]},
 "kpis":{"total_usd":274285,"units":1035,"transactions":100,"avg_order_usd":2742.85},
 "monthly":[{"month":"2026-01","label":"Ene","total_usd":55785,"transactions":23}],
 "by_category":[{"categoria":"Hardware","total_usd":178000,"transactions":22}],
 "by_region":[{"region":"Asia","total_usd":88980,"transactions":26}],
 "by_payment":[{"metodo":"Credito","total_usd":123175,"transactions":21}],
 "top_products":[{"producto":"Laptop Pro M1","total_usd":100800,"units":8}],
 "by_country":[{"pais":"Chile","total_usd":53650,"transactions":12}],
 "by_age_bucket":[{"bucket":"36-50","total_usd":75575,"transactions":32}],
 "transactions":[{"id":"TXN-001","fecha":"2026-01-09","cliente":"...","pais":"...","edad":34,"producto":"...","categoria":"...","cantidad":2,"precio_unitario_usd":1200,"total_usd":2400,"region":"...","metodo_pago":"..."}]}
```

`data_log.csv` columns (one row per event): `run_id,timestamp,event(build|approve|release),rows_usuarios,rows_ventas,joined_rows,match_rate,validation_status,sanitization_status,outputs,status,approver,approval_ts,artifact_sha256`.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | NaN/text in Total aborts (E3); match rate < 90% blocks (E2); sanitizer neutralizes `<script>`/quotes (E5); aggregation equals exploration totals (E6); gate fingerprint mismatch blocks (R1/R3) | `tests/test_*.py`, stdlib `unittest` (no pytest yet) |
| Integration | build -> approve -> release end-to-end on real Excels; run_id + fingerprint binding; re-run invalidates old approval (R3) | CLI subprocess calls |
| E2E | Open `dashboard.html` with network off: 4 KPI cards, 6+ charts, DataTable search/sort/pagination from embedded payload (D1-D5) | Parse payload + headless render check |

## Migration / Rollout

No migration. Apply creates `.venv` (pandas 3.0.3 already global). First build needs one-time network to vendor libs; runtime is offline-safe. Rollback: delete `dashboard.html` + `data_log.csv`, re-run ETL from Excels (never mutated).

## Open Questions

None blocking. Note for sdd-tasks: vendored library versions pinned at build time; alert output must be human-visible (stderr + audit row).