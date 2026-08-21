# Sales ETL Specification

## Purpose

Read-only pandas ETL: ingest both Excels, join on `ID Transacción`, validate dtypes, parse ISO dates, sanitize strings, aggregate, emit JSON payload plus `data_log.csv` audit.

## Requirements

| ID | Requirement |
|----|-------------|
| E1 | MUST read both Excels read-only; abort with clear error if missing or unreadable. |
| E2 | MUST inner-join on `ID Transacción`, compute match rate, alert if below 90%. |
| E3 | MUST validate numerics (e.g. `Total (USD)`) are finite, no NaN or text; else fail run. |
| E4 | MUST parse ISO dates (`Fecha`, `Fecha Registro`) before month aggregation. |
| E5 | MUST sanitize string fields (quotes, backslashes, angle brackets, control chars) before JSON embedding. |
| E6 | MUST emit KPIs (total USD, units, transactions, avg order) and monthly, category, region, payment, top-product, country, age-bucket, transaction aggregates. |
| E7 | MUST append `data_log.csv` row per run: timestamp, row counts, match rate, validation/sanitization results, outputs. |

## Scenarios

- E1 happy: GIVEN both Excels exist WHEN ETL runs THEN sheets load, sources unchanged
- E1 edge: GIVEN one Excel missing/corrupt WHEN ETL runs THEN abort with file-specific error
- E2 happy: GIVEN 100% overlap WHEN join runs THEN clean frame, match rate recorded
- E2 edge: GIVEN overlap below 90% WHEN join runs THEN alert emitted, run flagged failed
- E3 happy: GIVEN `Total (USD)` int64 WHEN validation runs THEN pass logged
- E3 edge: GIVEN NaN/text in `Total (USD)` WHEN validation runs THEN run aborts, violation logged
- E4: GIVEN `YYYY-MM-DD` cells WHEN parsing runs THEN month aggregation uses datetimes
- E5: GIVEN name with quotes and `<script>` WHEN payload generated THEN JSON-safe, no markup executes
- E6: GIVEN joined 100-row frame WHEN aggregation runs THEN payload has all groups plus transactions
- E7: GIVEN successful run WHEN finished THEN audit row appended