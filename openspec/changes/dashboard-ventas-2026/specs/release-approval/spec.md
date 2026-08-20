# Release Approval Specification

## Purpose

Human-in-the-loop gate: release only after explicit human approval; decision recorded in audit trail.

## Requirements

| ID | Requirement |
|----|-------------|
| R1 | MUST NOT release until human explicitly approves generated output. |
| R2 | MUST record approver, timestamp, artifact fingerprint in `data_log.csv` on approval. |
| R3 | Prior approval MUST NOT apply to output from a later ETL run; fresh approval required. |

## Scenarios

- R1 happy: GIVEN dashboard and explicit approval WHEN gate evaluated THEN released
- R1 edge: GIVEN dashboard, no approval WHEN gate evaluated THEN release blocked
- R2: GIVEN human approves WHEN recorded THEN log has approver, timestamp, fingerprint
- R3: GIVEN new ETL run after prior approval WHEN release attempted with old approval THEN blocked until re-approval