# Sales Dashboard Specification

## Purpose

Single-file HTML dashboard with embedded JSON payload, CDN Tailwind/Chart.js/DataTables, labeled Ene-May 2026, local file only.

## Requirements

| ID | Requirement |
|----|-------------|
| D1 | MUST be single HTML file with embedded JSON; no runtime data fetch. |
| D2 | MUST label period "Ene-May 2026"; no full-year or YoY claims. |
| D3 | MUST render KPI cards: total USD, units, transactions, average order. |
| D4 | MUST render 6+ Chart.js charts: monthly, category, region, payment, top products, country. |
| D5 | MUST render transactions as DataTable with client-side search, sort, pagination. |
| D6 | MUST deliver local file only; no public deployment. |

## Scenarios

- D1: GIVEN HTML opened without data network WHEN page loads THEN charts and table render from embedded payload
- D2: GIVEN Jan-May 2026 data WHEN page renders THEN header shows "Ene-May 2026", no YoY
- D3: GIVEN payload WHEN page loads THEN four KPI cards show aggregated values
- D4: GIVEN payload WHEN page loads THEN 6+ charts render with datasets
- D5: GIVEN table loaded WHEN user searches THEN table filters without reload
- D6: GIVEN approved dashboard WHEN released THEN copied to local destination only