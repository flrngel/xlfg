# Test contract

### P0-1 — Mobile checkout remains completable after the targeted clarity fix
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 I1 A1`
- practical_steps:
  1. Exercise the selected mobile checkout confusion point.
  2. Confirm the flow is clearer and still completes.
- fast_check: npm test -- checkout-mobile
- ship_phase: `manual`
- ship_check: NONE
- regression_check: npm test -- checkout
- manual_smoke: Run a real mobile viewport checkout flow from cart to submit.
- anti_monkey_probe: Cosmetic-only copy changes that do not address the confusing step should fail review.
- notes:
