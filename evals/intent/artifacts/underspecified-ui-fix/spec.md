# Spec

## Intent contract
- resolution: `needs-user-answer`
- work kind: `build`
- raw request: make the checkout less confusing on mobile
- direct asks:
  - `Q1`: make checkout less confusing on mobile
- implied asks:
  - `I1`: preserve current checkout completion behavior
- acceptance criteria:
  - `A1`: the mobile checkout flow is clearer
- non-goals:
  - redesign the whole checkout architecture
- constraints actually requested:
- assumptions to proceed:
  - if the user does not answer, prioritize removing the most confusing mobile friction that blocks order completion
- blocking ambiguities:
  - Which mobile confusion is most important to fix first?
- carry-forward anchor: Reduce mobile checkout confusion without breaking completion, and ask only the minimal blocking product question.

## Objective groups
- `O1` — Reduce mobile checkout confusion without breaking completion; covers: `Q1 I1`; depends_on: `none`; completion: the top confusing mobile step is clarified or improved while completion still works.

## Task map
- `T1` — Capture the top mobile confusion area and confirm guardrails before implementation; objectives: `O1`; scenarios: `P0-1`; owner: `agent`
