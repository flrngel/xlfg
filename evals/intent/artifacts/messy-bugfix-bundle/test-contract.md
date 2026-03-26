# Test contract

### P0-1 — Successful login redirects to dashboard
- objective: `O1`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q1 I1 A1`
- practical_steps:
  1. Sign in with a valid non-SSO account.
  2. Confirm the post-auth redirect target.
- fast_check: npm test -- login-redirect
- ship_phase: `fast`
- ship_check: npm test -- login-redirect
- regression_check: npm test -- sso
- manual_smoke: NONE
- anti_monkey_probe: A shallow patch that hardcodes the route but breaks SSO callbacks should fail.
- notes:

### P0-2 — Invalid password shows improved copy
- objective: `O2`
- requirement_kind: `F2P`
- priority: `P0`
- query_ids: `Q2 A2`
- practical_steps:
  1. Submit a valid email with an invalid password.
  2. Confirm the revised copy appears.
- fast_check: npm test -- login-copy
- ship_phase: `fast`
- ship_check: npm test -- login-copy
- regression_check: npm test -- sso
- manual_smoke: NONE
- anti_monkey_probe: A string-only change that hides a real auth regression should fail the SSO guard.
- notes:

### G1 — SSO login still works
- objective: `O1`
- requirement_kind: `P2P`
- priority: `P1`
- query_ids: `I1`
- practical_steps:
  1. Trigger a normal SSO sign-in flow.
- fast_check: npm test -- sso
- ship_phase: `fast`
- ship_check: npm test -- sso
- regression_check: npm test -- auth
- manual_smoke: NONE
- anti_monkey_probe: Redirect fixes must not break callback handling.
- notes:
