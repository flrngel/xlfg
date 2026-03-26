# Spec

## Intent contract
- resolution: `proceed`
- work kind: `research`
- raw request: look into whether we should move from Jest to Vitest and tell me the impact on watch mode and CI
- direct asks:
  - `Q1`: evaluate whether to move from Jest to Vitest
  - `Q2`: tell me the impact on watch mode and CI
- implied asks:
  - `I1`: do not migrate the repo unless asked
- acceptance criteria:
  - `A1`: clear tradeoffs for watch mode and CI are stated
- non-goals:
  - perform the full migration now
- constraints actually requested:
  - research first, no implementation commitment yet
- assumptions to proceed:
  - the current request is for analysis and recommendation, not repo migration
- blocking ambiguities:
- carry-forward anchor: Produce a research recommendation on Jest vs Vitest, focused on watch mode and CI, without performing the migration.

## Objective groups
- `O1` — Research Jest vs Vitest impact on watch mode and CI; covers: `Q1 Q2 I1`; depends_on: `none`; completion: the recommendation clearly explains watch mode and CI tradeoffs without migrating the repo.

## Task map
- `T1` — Compare watch mode and CI behavior between Jest and Vitest; objectives: `O1`; scenarios: `P0-1`; owner: `agent`
