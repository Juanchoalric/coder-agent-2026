# Archive Report: dashboard-ventas-2026

- **Archived on**: 2026-08-20
- **Archived to**: `openspec/changes/archive/2026-08-20-dashboard-ventas-2026/`
- **Verify verdict**: PASS - 16/16 requirements, 20/20 scenarios compliant, 0 CRITICAL, 0 WARNING (5 non-blocking suggestions)
- **Artifact store mode**: hybrid (OpenSpec files + Engram)
- **Language**: English

## Specs Synced

Baseline `openspec/specs/` was empty (greenfield). All three delta specs were FULL specs (not deltas), so they were copied byte-identical to baseline per the sdd-archive convention. No merge was required and no destructive delta was applied (archive rule checked).

| Domain | Action | Details |
|--------|--------|---------|
| sales-etl | Created | E1-E7: 7 requirements, 10 scenarios (ingest, join, validation, sanitization, aggregation, audit) |
| sales-dashboard | Created | D1-D6: 6 requirements, 6 scenarios (single-file HTML, labeling, KPIs, charts, DataTable, local delivery) |
| release-approval | Created | R1-R3: 3 requirements, 4 scenarios (approval gate, fingerprint, freshness) |

Baseline spec paths (source of truth):
- `openspec/specs/sales-etl/spec.md`
- `openspec/specs/sales-dashboard/spec.md`
- `openspec/specs/release-approval/spec.md`

## Final State

- **Baseline specs**: all 3 capabilities synced to `openspec/specs/{domain}/spec.md` (verified byte-identical to the archived delta specs).
- **Archived change folder**: `openspec/changes/archive/2026-08-20-dashboard-ventas-2026/` containing proposal.md, exploration.md, design.md, tasks.md, verify-report.md, and specs/ (3 domains).
- **Active changes**: `openspec/changes/` now holds only `archive/` and `.gitkeep` - no active changes remain.
- **Config**: `openspec/config.yaml` updated (verify suggestion 3): `apply.test_command`, `verify.test_command`, and `verify.build_command` populated with `.venv/bin/python -m unittest discover -s tests` and `.venv/bin/python -m etl build`; `testing.*` section reflects the active stdlib unittest suite (unit/integration/e2e true, runner set, coverage false).
- **Implementation delivered**: `etl/` package (main, ingest, validate, sanitize, aggregate, audit, render, vendor, templates), generated `dashboard.html` (offline-safe single file), `data_log.csv` audit trail. 22/22 tasks complete; 61/61 tests passing (0 skips, incl. headless-Chrome E2E with network aborted).

## Engram Lineage (observation IDs)

| Artifact | Topic | Observation ID |
|----------|-------|----------------|
| proposal | `sdd/dashboard-ventas-2026/proposal` | #355 |
| spec | `sdd/dashboard-ventas-2026/spec` | #356 |
| design | `sdd/dashboard-ventas-2026/design` | #358 |
| tasks | `sdd/dashboard-ventas-2026/tasks` | #359 |
| apply-progress | `sdd/dashboard-ventas-2026/apply-progress` | #360 |
| verify-report | `sdd/dashboard-ventas-2026/verify-report` | #362 |
| archive-report | `sdd/dashboard-ventas-2026/archive-report` | #363 |

## Follow-ups (non-blocking, from verify-report suggestions)

1. **Stale dashboard.html on blocked build**: a blocked build (E1/E2/E3 edges) leaves a stale `dashboard.html` from a previous successful run in place. Spec is satisfied (no output written) and the audit trail + stderr disambiguate, but consider removing the stale file on a blocked build or printing its run_id.
2. **E1 corrupt-file branch coverage**: the missing-file branch has an automated unit test; the corrupt/unreadable-file branch was verified manually only. Add a corrupt-file test (write garbage bytes, assert `IngestError`).
3. **Config test commands** - DONE in this archive: `openspec/config.yaml` test/build commands and `testing.*` populated (see Final State).
4. **Design wording**: design File Changes says sanitize.py "strips" angle brackets; implementation replaces `<`/`>` with parentheses (content kept readable, still markup-proof). Archived design is an audit trail and was NOT modified; update wording if the design is ever re-issued.
5. **jQuery in vendor list**: jQuery is a hard DataTables dependency inlined by `etl/vendor.py` but not named in the design's vendor asset list. Archived design was NOT modified; note for any future design revision.

## SDD Cycle Complete

The change has been fully planned, explored, proposed, specified, designed, implemented, verified (PASS), and archived. Ready for the next change.
