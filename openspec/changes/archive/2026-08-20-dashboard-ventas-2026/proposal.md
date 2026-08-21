# Proposal: Dashboard de Ventas 2026

## Intent

User needs a read-only 2026 sales dashboard; no implementation exists. Build the blueprint's hybrid cell: pandas ETL -> single-file HTML (Tailwind/Chart.js/DataTables) -> human approval. Exploration proved blueprint's file names and join key (`Ventas.xlsx`/`Inventario.xlsx`, `ID_Producto`) are wrong; codify reality: `Usuarios_Ventas_2026.xlsx` + `Ventas_Productos_2026.xlsx` joined on `ID Transacción`.

## Scope

### In Scope
- pandas ETL, read-only over both Excels; inner join on `ID Transacción`, 90% match-rate alert
- Dtype validation (no NaN/text in Total (USD)), sanitization before JS injection, `data_log.csv` audit
- Aggregations: KPIs, monthly, category, region, payment, top products, country, age buckets, transactions
- Single-file HTML: CDN Tailwind/Chart.js/DataTables, embedded JSON, label "Ene-May 2026", no YoY
- Human-in-the-loop approval before release; local file, no public exposure

### Out of Scope
- Inventory/stock module, reorder alerts (no inventory dataset - confirmed)
- Full-year/YoY reporting (data is Jan-May 2026 only)
- Auth/multi-user, live updates, backend services

## Capabilities

`openspec/specs/` is empty (greenfield); all NEW.

### New Capabilities
- `sales-etl`: Excel ingest, `ID Transacción` join (90% threshold alert), dtype validation, sanitization, `data_log.csv` audit, ISO date parsing, JSON aggregation
- `sales-dashboard`: single-file HTML with embedded JSON, Tailwind/Chart.js/DataTables CDN, period labeling, KPI cards, charts, transaction DataTable
- `release-approval`: human-in-the-loop approval gate before dashboard release

### Modified Capabilities
None

## Approach

Blueprint-faithful (Approach 1 + 3): (1) pandas ETL, explicit dtypes (pandas 3 string migration): read -> validate + sanitize -> inner join -> parse ISO dates -> aggregate -> JSON + `data_log.csv`. (2) Generate single-file HTML embedding payload; client-side filtering. (3) Human approval gate; only approved output released. (4) Project venv in apply (`.gitignore` already excludes `.venv/`, `data_log.csv`).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `etl/` scripts | New | pandas pipeline, validation, JSON + audit |
| `dashboard.html` | New | generated single-file report |
| `data_log.csv` | New | audit trail (gitignored) |
| `blueprint.md` | None | reference only; corrected facts in specs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Future data breaches guardrails | Med | Hard validation gates with alerts despite pristine data |
| CDN unavailable | Low | Open question: offline fallback |
| Blueprint names vs reality drift | Low | Real names + join key codified in proposal/specs |

## Rollback Plan

No production system: delete `dashboard.html` + `data_log.csv`, re-run ETL from Excels (read-only, never mutated). Git revert if committed.

## Dependencies

- Python 3.13.5, pandas 3.0.3, numpy 2.5.1 (global); venv recommended in apply
- CDN Tailwind/Chart.js/DataTables (internet on first load)

## Success Criteria

- [ ] ETL end-to-end on both Excels, emits JSON + `data_log.csv` without errors
- [ ] Join match rate >= 90% (100% today); alert on breach
- [ ] No NaN/text in numerics; sanitization passes; Excels untouched
- [ ] Dashboard labels "Ene-May 2026"; KPIs, 6+ charts, transaction DataTable render
- [ ] Human approval recorded before release