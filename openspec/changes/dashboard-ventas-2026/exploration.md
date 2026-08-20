# Exploration: dashboard-ventas-2026

Date: 2026-08-20
Phase: sdd-explore (executor)

## Current State

- Repo `/Users/jacintabeccarvarela/code/Business Dashboard` has NO implementation code yet. Git repo initialized on `main`, no commits. Files present: `blueprint.md`, `.gitignore`, `openspec/` (config.yaml, specs/, changes/archive/), and the two source Excels.
- `openspec/config.yaml` is bootstrapped with detected context: Python 3.13.5, pandas 3.0.3, numpy 2.5.1 (global interpreter `/opt/homebrew/bin/python3`, NO venv yet), join key `ID Transacción`, hybrid cell from `blueprint.md`.
- Blueprint (`blueprint.md`, Spanish) defines a hybrid agentic cell: ingest Excels -> consolidate with Python/Pandas -> generate single-file HTML dashboard (Tailwind CSS, Chart.js, DataTables via CDN) -> human-in-the-loop approval. Guardrails: read-only over Excels, dtype validation (no NaN/text in "Total (USD)"), sanitization before JS injection, 90% join-match threshold with alert, `data_log.csv` audit trail.
- Blueprint named the inputs `Ventas.xlsx` + `Inventario.xlsx`. The ACTUAL files on disk are `Usuarios_Ventas_2026.xlsx` and `Ventas_Productos_2026.xlsx` - the blueprint file names do not exist. There is NO inventory/stock dataset on disk.

## Data Schema Mapping (verified on disk)

### `Usuarios_Ventas_2026.xlsx` - customer/transaction dimension (Sheet1, 100 rows x 6 cols)
| Column | dtype | Notes |
|---|---|---|
| ID Transacción | str | Unique (100/100), format `TXN-001` |
| Nombre Cliente | str | 64 unique - repeat customers exist (Carlos Lopez x5) |
| Correo Electrónico | str | 100 unique |
| País | str | 7 values (Mexico top, 16) |
| Edad | int64 | 18-75, mean 46.7 |
| Fecha Registro | str | ISO `YYYY-MM-DD`, NOT datetime. Range 2024-01-01..2026-11-23 |

### `Ventas_Productos_2026.xlsx` - sales facts (Sheet1, 100 rows x 9 cols)
| Column | dtype | Notes |
|---|---|---|
| ID Transacción | str | Unique (100/100) - JOIN KEY |
| Fecha | str | ISO `YYYY-MM-DD`, NOT datetime. Range 2026-01-09..2026-05-24 |
| Producto | str | 10 unique (Laptop Pro M1 top by $) |
| Categoría | str | 4 values: Hardware, Audio, Periféricos, Accesorios |
| Cantidad | int64 | 1-20, total 1,035 units |
| Precio Unitario (USD) | int64 | 15-1200 |
| Total (USD) | int64 | 45-22,800 |
| Región | str | 4 values: Asia, Latinoamérica, Europa, Norteamérica |
| Método de Pago | str | 4 values: Crédito, Transferencia, PayPal, Débito |

## Data Quality Findings

- **Zero nulls/NaNs** in every column of both files. No empty strings, no whitespace-only cells.
- **All numerics are int64** - no strings-as-numbers, no currency symbols, no thousand commas, no `$` prefixes. The blueprint's dtype guardrail (no NaN/text in Total (USD)) passes trivially on THIS dataset, but must still be implemented as a validation step for future files.
- **Internal consistency**: `Total (USD) == Cantidad x Precio Unitario (USD)` for all 100 rows. No reconciliation issues.
- **Dates are ISO strings**, must be parsed with `pd.to_datetime` in ETL for month/day aggregations.
- **Sanitization probe**: 0 cells in string columns contain quotes, backslashes, angle brackets, or control chars. Data is JSON/JS-injection safe today; sanitization guardrail still needed for future files.
- **Partial year**: sales data spans only Jan-May 2026 (5 months). Dashboard must label period explicitly (e.g. "Ene-May 2026"), not imply full year.
- **Registro vs sales year**: 61 registrations predate 2026; 39 in 2026. Fine for customer acquisition trend chart.
- pandas 3.0.3 emits `Pandas4Warning` for `select_dtypes(include='object')` - string dtype migration in pandas 3; ETL code should use `include='string'` or explicit dtypes.

## Join Strategy

- **Actual join key: `ID Transacción`** - NOT `ID_Producto` as the blueprint claims. No `ID_Producto` column exists in either file. Blueprint's stated join (`buscar correspondencias de ID_Producto`) does not match reality and should be corrected in proposal/spec.
- Overlap: 100/100 (100% match rate, well above the 90% threshold). Both directions empty (no orphan TXNs on either side).
- Inner join yields a clean 100-row x 14-col frame with zero nulls.
- Merge mode: `inner` is correct here; keep the 90% threshold alert as a guardrail for future data drops.

## Candidate Metrics and Charts for the Dashboard

Verified aggregates (inner join, 100 rows):
- **Total sales: USD 274,285** | 1,035 units | 100 transactions | avg order USD 2,742.85
- **By category (USD)**: Hardware 178,000 (22 tx), Audio 40,800 (12), Periféricos 35,730 (31), Accesorios 19,755 (35)
- **By region (USD)**: Asia 88,980 (26), Latinoamérica 87,270 (26), Europa 63,435 (26), Norteamérica 34,600 (22)
- **By month (USD)**: May 98,090 (21) > Apr 62,200 (27) > Jan 55,785 (23) > Mar 49,390 (19) > Feb 8,820 (10)
- **By payment (USD)**: Crédito 123,175 (21) > Transferencia 73,630 (25) > PayPal 47,560 (23) > Débito 29,920 (31)
- **Top product**: Laptop Pro M1 100,800 (8 tx); Tablet de Diseño 68,800 (8); Auriculares Pro 40,800 (12)
- **By country (USD)**: Chile 53,650 (12) > Colombia 49,340 (11) > España 43,750 (14) > México 38,845 (16) > Argentina 35,900 (15) > Perú 28,965 (16) > Brasil 23,835 (16)
- **Age buckets**: 36-50 highest spend 75,575 (32 tx); 18-25 41,965 (15); 66+ 56,410 (16)
- **Repeat customers**: Carlos López (5 tx), Ana Torres / Gabriela Rodríguez (4)

Recommended dashboard composition:
1. KPI cards: Total ventas, unidades vendidas, transacciones, ticket promedio
2. Line/bar: ventas por mes (Ene-May 2026)
3. Bar: ventas por categoría (USD) + units by category
4. Donut/pie: ventas por región; ventas por método de pago
5. Horizontal bar: top productos por ventas
6. Country breakdown (bar or map-free table)
7. DataTable (DataTables.js): transacciones individuales with search/sort/filter (client-side from embedded JSON)
8. Optional: customer age distribution histogram (Chart.js bar)

## Tech Approach Validation

Pipeline: Python/Pandas ETL -> aggregated JSON payload embedded in single-file HTML -> Tailwind CSS + Chart.js + DataTables via CDN.

- **Validated OK**: pandas 3.0.3 + numpy 2.5.1 installed and functional on Python 3.13.5; Excel reading works without openpyxl issues (pandas built-in xlsx driver).
- **Validated OK**: all aggregation targets computable with a few groupby calls; no exotic operations needed.
- **Validated OK**: JSON payload will be small (100 transactions + small aggregate tables) - embeds trivially.
- **Watch**: no venv exists; `.gitignore` already excludes `.venv/` and `data_log.csv`. Recommend creating a project venv during apply (pandas already available globally, so venv is optional but recommended for reproducibility).
- **Watch**: pandas 3 string-dtype migration warnings; use explicit dtypes in ETL.
- **Watch**: CDN-based Tailwind/Chart.js/DataTables means the dashboard needs internet on first load (aligns with blueprint's CDN decision; document offline fallback as a question).

## Approaches

1. **Pandas-only ETL -> static JSON -> single HTML file (blueprint's approach)**
   - Pros: zero build tooling, portable single file, matches blueprint exactly, human-reviewable intermediate `data_log.csv`, fastest path to the <60s latency KPI
   - Cons: no reactivity (regenerate on data change), CDN dependency
   - Effort: Low-Medium

2. **Python ETL -> JSON + Next.js/React dashboard**
   - Pros: scalable, interactive filters without regeneration
   - Cons: contradicts blueprint's single-file portability goal, heavier setup, slower first render, overkill for 100 rows
   - Effort: High

3. **Python ETL -> static HTML with embedded JSON + client-side filtering only (DataTables/Chart.js)**
   - Pros: keeps single-file deliverable, adds in-browser filtering without backend
   - Cons: slightly larger file; still regenerate for new data
   - Effort: Medium

## Recommendation

Approach 1 (blueprint-faithful) with approach 3's client-side filtering via DataTables - the blueprint already lists DataTables, so this is a single-file HTML with embedded JSON, KPI cards, Chart.js charts, and a DataTables transaction table. Pure pandas ETL with a `data_log.csv` intermediate, dtype validation + sanitization guardrails, and human approval gate. This matches the blueprint's portability and hybrid human-in-the-loop goals with the least risk.

## Risks

- **Blueprint vs. reality mismatch on file names and join key**: blueprint says `Ventas.xlsx`/`Inventario.xlsx` and join on `ID_Producto`; actual files are `Usuarios_Ventas_2026.xlsx`/`Ventas_Productos_2026.xlsx` and the join key is `ID Transacción`. Proposal/spec MUST codify the real names and key, and drop the `ID_Producto` assumption.
- **No inventory/stock data exists**: the "Inventario" file is absent; `Ventas_Productos` provides product/category/qty sales data but NO stock levels, so "inventory status" dashboards (stock on hand, reorder alerts) are impossible with current inputs. Scope must be re-confirmed with the user.
- **Partial-year data**: Jan-May 2026 only. Dashboard period labeling must be explicit; no YoY or full-year claims.
- **Dates stored as strings**: ETL must parse `Fecha`/`Fecha Registro` to datetime; otherwise month aggregation silently breaks.
- **Future data drops may violate guardrails**: current files are pristine, but dtype validation (Total (USD) no NaN/text), sanitization, and the 90% join threshold with alert must be implemented regardless.
- **No venv / no test infra**: pytest not installed; recommend venv + pytest during apply if strict TDD is desired (openspec config already notes this).

## Ready for Proposal

Yes. The orchestrator should tell the user: actual data files are `Usuarios_Ventas_2026.xlsx` + `Ventas_Productos_2026.xlsx`, join key is `ID Transacción` (100% match, not the blueprint's `ID_Producto`), data is pristine (no NaNs, int64 numerics, consistent totals), totals = USD 274,285 over Jan-May 2026, and there is NO inventory/stock file - scope question to resolve before sdd-propose.