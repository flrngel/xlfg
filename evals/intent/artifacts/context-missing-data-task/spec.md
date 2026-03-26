# Spec

## Intent contract
- resolution: `proceed-with-assumptions`
- work kind: `multi`
- raw request: speed up imports and make errors easier to debug
- direct asks:
  - `Q1`: speed up imports
  - `Q2`: make errors easier to debug
- implied asks:
  - `I1`: do not reduce import correctness
- acceptance criteria:
  - `A1`: import latency improves
  - `A2`: operators can identify failing rows or causes faster
- non-goals:
  - drop validation to make imports faster
- constraints actually requested:
  - preserve import correctness
- assumptions to proceed:
  - optimize batch sizing, parsing, or logging rather than weakening validation
- blocking ambiguities:
- carry-forward anchor: Improve import performance and diagnosability without trading away correctness.

## Objective groups
- `O1` — Improve import performance; covers: `Q1 I1`; depends_on: `none`; completion: import latency improves without skipping validation.
- `O2` — Improve import error diagnosability; covers: `Q2 I1`; depends_on: `none`; completion: operators can identify failing rows or causes faster.

## Task map
- `T1` — Profile import hotspots and choose a safe performance improvement; objectives: `O1`; scenarios: `P0-1 G1`; owner: `agent`
- `T2` — Add clearer import error surfaces and traceability; objectives: `O2`; scenarios: `P0-2 G1`; owner: `agent`
