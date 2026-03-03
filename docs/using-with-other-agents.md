# using xlfg with other agents

The file protocol is tool-agnostic.

Even if you are not using Claude Code, keep the same durable run artifacts:

- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `test-contract.md`
- `env-plan.md`
- `plan.md`
- `scorecard.md`

The important rule is that the **same contract drives implementation and verification**.
A different agent can pick up the run later because the reasoning lives in the repo, not in chat history.
