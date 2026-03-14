# using xlfg with other agents

The file protocol is tool-agnostic.

Even if you are not using Claude Code, keep the same durable run artifacts:

- `why.md`
- `memory-recall.md`
- `diagnosis.md`
- `solution-decision.md`
- `harness-profile.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `plan.md`
- `workboard.md`
- `proof-map.md`
- `scorecard.md`

The important rule is that the **same contract drives implementation and verification**.
A different agent can pick up the run later because the reasoning lives in the repo, not in chat history.

When integrating another agent harness, preserve these properties:

- read `current-state.md` first
- use deterministic recall before wide scanning
- keep per-run state in `docs/xlfg/runs/<run-id>/`
- keep durable lessons in `docs/xlfg/knowledge/`
- treat `workboard.md` as execution truth
- treat `proof-map.md` as proof truth
