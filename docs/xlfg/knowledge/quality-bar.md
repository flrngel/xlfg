# xlfg quality bar

Nothing is "done" unless:

- **The run card is explicit** (`spec.md` exists and keeps the intent contract, objective groups, non-goals, outcome, risks, and proof commitments visible)
- **Recall is honest** (`memory-recall.md` records real hits or a clear no-hit)
- **Test intent is shared** (`test-contract.md` maps concise scenario contracts to practical fast proof and ship proof)
- **Test readiness is explicit** (`test-readiness.md` is `READY` before coding or clearly explains why planning must be revised)
- **New behavior is proven** by scenario-targeted checks that were defined before implementation (Fail → Pass)
- **Existing behavior is preserved** with relevant guard coverage (Pass → Pass)
- **Lint / typecheck / build** pass when applicable
- **User-facing flows are validated** (happy path, alternates, failure path, a11y)
- **Workboard is current** (`workboard.md` reflects stage / task truth and reminds the agent it owns the work)
- **Verification is honest** (`verification.md` records exact commands, artifacts, and the first actionable failure when red)
- **Unexpected failures are compounded** into failure memory / harness rules / role memory when warranted
- **No monkey fix is misrepresented as the final solution** (bounded workarounds are labeled honestly)
- **Operational plan exists** (monitoring + rollback notes)

Optional files such as `research.md`, `diagnosis.md`, `flow-spec.md`, `env-plan.md`, `proof-map.md`, and `review-summary.md` should exist only when they materially reduce risk or ambiguity.
