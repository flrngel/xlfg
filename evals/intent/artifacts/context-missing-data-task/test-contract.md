# Test contract

### P0-1 — Imports complete faster on a representative batch
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 I1 A1`
- practical_steps:
  1. Run the representative import benchmark.
  2. Compare latency before and after.
- fast_check: pytest tests/imports/test_perf.py -q
- ship_phase: `fast`
- ship_check: pytest tests/imports/test_perf.py -q
- regression_check: pytest tests/imports/test_validation.py -q
- manual_smoke: NONE
- anti_monkey_probe: Faster imports that quietly skip validation must fail.
- notes:

### P0-2 — Import failures are easier to diagnose
- objective: `O2`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q2 A2`
- practical_steps:
  1. Trigger a representative bad-row import.
  2. Confirm the operator can identify row/cause details quickly.
- fast_check: pytest tests/imports/test_errors.py -q
- ship_phase: `fast`
- ship_check: pytest tests/imports/test_errors.py -q
- regression_check: pytest tests/imports/test_validation.py -q
- manual_smoke: NONE
- anti_monkey_probe: Generic failure messages that hide the row/cause are not enough.
- notes:

### G1 — Validation correctness remains intact
- objective: `O1`
- requirement_kind: `P2P`
- priority: `P1`
- query_ids: `I1`
- practical_steps:
  1. Run validation regression checks.
- fast_check: pytest tests/imports/test_validation.py -q
- ship_phase: `fast`
- ship_check: pytest tests/imports/test_validation.py -q
- regression_check: pytest tests/imports/test_validation.py -q
- manual_smoke: NONE
- anti_monkey_probe: Performance changes must not weaken correctness.
- notes:
