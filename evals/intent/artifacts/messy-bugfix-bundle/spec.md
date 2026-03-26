# Spec

## Intent contract
- resolution: `proceed`
- work kind: `multi`
- raw request: fix the login redirect, keep SSO working, and improve the invalid-password error copy
- direct asks:
  - `Q1`: fix the login redirect
  - `Q2`: improve the invalid-password error copy
- implied asks:
  - `I1`: keep SSO working
- acceptance criteria:
  - `A1`: successful login lands on dashboard
  - `A2`: invalid password shows the new error copy
- non-goals:
  - replace the auth provider
- constraints actually requested:
  - preserve current SSO behavior
- assumptions to proceed:
  - the redirect target should remain the dashboard after successful auth
- blocking ambiguities:
- carry-forward anchor: Restore successful login redirect and improve invalid-password copy without regressing SSO.

## Objective groups
- `O1` — Fix login redirect after successful auth; covers: `Q1 I1`; depends_on: `none`; completion: successful login lands on the dashboard without disrupting SSO sessions.
- `O2` — Improve invalid-password error copy without breaking SSO; covers: `Q2 I1`; depends_on: `none`; completion: invalid-password flow shows clearer copy and SSO login still works.

## Task map
- `T1` — Investigate redirect branch after successful auth; objectives: `O1`; scenarios: `P0-1 G1`; owner: `agent`
- `T2` — Update invalid-password copy and affected tests; objectives: `O2`; scenarios: `P0-2 G1`; owner: `agent`
