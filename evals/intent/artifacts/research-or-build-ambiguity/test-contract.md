# Test contract

### P0-1 — Recommendation clearly states watch mode and CI tradeoffs
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 Q2 I1 A1`
- practical_steps:
  1. Summarize watch mode differences.
  2. Summarize CI implications.
  3. Confirm the result is a recommendation, not a migration.
- fast_check: NONE
- ship_phase: `manual`
- ship_check: NONE
- regression_check: NONE
- manual_smoke: Review the recommendation text for watch mode, CI, and non-migration scope.
- anti_monkey_probe: A generic testing-framework comparison that ignores watch mode or CI is insufficient.
- notes:
