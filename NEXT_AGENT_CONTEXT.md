# Next agent context

## Current state (6.2.0)

v6.2.0 is the **conductor + phase-skills** architecture. v6.0 had collapsed all phase guidance into monolithic command bodies (~3000 words each) that loaded in full on every invocation. v5 had split phases into hidden skills loaded just-in-time via the `Skill` tool; the context-budget win of that architecture is real and v6.2 brings it back — without any of the v5 sub-agent baggage.

### The architecture

- Two **conductors** (`commands/xlfg.md`, `commands/xlfg-debug.md`), each ~500–600 words. Frontmatter grants the phase skills via `Skill(xlfg-engineering:xlfg-<phase>-phase *)`. Body carries: startup (RUN_ID creation), pipeline order, loopback rules (cap 2 for /xlfg, 1 for /xlfg-debug), operating contract, completion summary template. No phase bodies inline.
- Nine **phase skills** under `skills/xlfg-<phase>-phase/SKILL.md`. Each is hidden (`user-invocable: false`), describes one phase's purpose/lens/how-to-work-it/done-signal/stop-traps, and carries its own `allowed-tools`. Three are shared between conductors (recall, intent, context); five are `/xlfg`-only (plan, implement, verify, review, compound); one is `/xlfg-debug`-only (debug).
- Durable archive conventions from v6.1 are unchanged: `docs/xlfg/current-state.md` read by recall, `docs/xlfg/runs/<RUN_ID>/run-summary.md` written by compound, `docs/xlfg/runs/<RUN_ID>/diagnosis.md` written by debug.

### What survives from v6.0/v6.1 (unchanged)

v6.2 keeps the v6 philosophy cut intact:

- No sub-agents. Tests assert no `Agent` or `SendMessage` in any command or skill's `allowed-tools`.
- No dispatch-packet contract tokens (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`). Forbidden in commands AND in skill bodies.
- No v5 coordination files (`spec.md`, `workboard.md`, `phase-state.json`, `verification.md`, `test-contract.md`, etc.). Phases share the conductor's context; they don't pass state through files.
- No `.xlfg/` directory. No Stop or SubagentStop hooks.
- No Codex surface (`codex/`, `.codex-plugin/`, `.agents/`).
- No `/xlfg-audit`, `/xlfg-status`, `/xlfg-init`.

### Why the skill split came back

Claude Code loads slash-command bodies on every invocation; it loads `Skill` bodies only when the tool fires. Keeping 3000 words of phase guidance in the command means every `/xlfg` invocation pays that token cost up front, even for trivial runs. Splitting phases into skills moves ~95% of the content behind just-in-time loading. While the model runs phase 3, only the context skill body is loaded — not all 8 phases simultaneously.

### The 9 phase skills

Shared (used by both `/xlfg` and `/xlfg-debug`):
- `xlfg-recall-phase` — deterministic recall over git history, durable archive, lexical repo scan
- `xlfg-intent-phase` — resolve ambiguity, name blockers, split bundled asks
- `xlfg-context-phase` — gather repo + runtime facts, bounded reads

`/xlfg`-only:
- `xlfg-plan-phase` — solution choice, task split, test contract (fast/smoke/ship), risk pass
- `xlfg-implement-phase` — edit-not-rewrite, tests-alongside-source, failure-mode check
- `xlfg-verify-phase` — run the proof, classify GREEN / RED / FAILED
- `xlfg-review-phase` — pick one lens (architecture / security / performance / UX)
- `xlfg-compound-phase` — write `run-summary.md`, consider promoting to `current-state.md`

`/xlfg-debug`-only:
- `xlfg-debug-phase` — scientific debugging, write `diagnosis.md`, no source edits

Each skill carries its own `allowed-tools`, tuned to its phase. The debug skill is the only skill that grants `Write` — and its body specifies the sanctioned path is `docs/xlfg/runs/<RUN_ID>/diagnosis.md`.

### Durable archive (unchanged from v6.1)

- `docs/xlfg/current-state.md` — optional, tracked, one-page (~300 words max). The "read this first" handoff. Updated sparingly in compound.
- `docs/xlfg/runs/<RUN_ID>/run-summary.md` — written by every `/xlfg` run. Fixed template: Ask / What changed / Proof / Residual risk / Durable lesson.
- `docs/xlfg/runs/<RUN_ID>/diagnosis.md` — written by every `/xlfg-debug` run. Fixed template: Mechanism / Strongest evidence / Likely repair surface / Fake fixes rejected / No-code-change guarantee / Residual unknowns / Next safest proof step.

`RUN_ID = <YYYYMMDD>-<HHMMSS>-<kebab-slug>`, computed once at startup.

### What v6.2 ships

- `plugins/xlfg-engineering/commands/xlfg.md` — conductor (~600 words), dispatches 8 phase skills
- `plugins/xlfg-engineering/commands/xlfg-debug.md` — conductor (~500 words), dispatches 4 phase skills
- `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md` — 9 phase skills, each hidden (`user-invocable: false`)
- `plugins/xlfg-engineering/scripts/audit_harness.py` — CI self-audit, 5 checks (adds `_check_skill_surface`)
- `plugins/xlfg-engineering/scripts/phase-gate.mjs` + `subagent-stop-guard.mjs` — byte-capped compat shims for cached v5.0.0 hook sessions
- `plugins/xlfg-engineering/hooks/hooks.json` — ExitPlanMode auto-allow only
- `tests/test_xlfg_v6.py` — 32 tests covering plugin shape, manifests, commands, skills, hooks, audit, conductor discipline

### What NOT to reintroduce

The test suite catches these drifts:
- Files under `plugins/xlfg-engineering/agents/**` (sub-agents — gone for good)
- Skill directories under `skills/` beyond the 9 named `xlfg-<phase>-phase/` (if you have a case for a new one, expand `EXPECTED_SKILLS` in both `audit_harness.py` and the test suite first)
- A `codex/` tree or `.codex-plugin/` manifest
- Any script under `scripts/` besides `audit_harness.py` and the two `.mjs` shims (byte-capped by test)
- `Agent` or `SendMessage` in any command or skill `allowed-tools` (no nested delegation)
- Dispatch-contract tokens in commands OR skills: `PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`
- Stop or SubagentStop hook registrations
- `.xlfg/` directory use (the `/xlfg` body contains an explicit disclaimer the test asserts on)

### Migration (v6.1.0 → v6.2.0)

Users see no change: `/xlfg` and `/xlfg-debug` still take `$ARGUMENTS` and do the same thing. The architectural change is internal:

- Phase bodies moved from the monolithic command into 9 `SKILL.md` files.
- If you had local edits to the v6.0/v6.1 command bodies, port them into the matching `skills/xlfg-<phase>-phase/SKILL.md`.
- The audit harness gained a 5th check. The test suite grew from 23 to 32 tests.

### Migration (v5.x → v6.x)

- Public entry surface shrank: `/xlfg` and `/xlfg-debug` only. `/xlfg-audit`, `/xlfg-status`, `/xlfg-init`, and the Codex `$xlfg`/`$xlfg-debug` skills were removed in 6.0.0.
- In-progress v5 runs: finish under v5 or abandon. Delete `.xlfg/` and the old `docs/xlfg/runs/<RUN_ID>/` tree (with the full v5 artifact set) before upgrading.
- If you had a v5 `ledger.jsonl`: there is no ledger in v6. Promote anything still load-bearing into `docs/xlfg/current-state.md` manually.
- Runtime: `python3` on PATH (for CI audit). No Node.

## Previous state (6.1.0)

v6.1.0 restored the `docs/xlfg/` durable archive that v6.0.0 deleted. Same archive is present in v6.2.0; the 6.2 change is the conductor/skills split, not the archive.

## Previous state (6.0.0)

v6.0.0 was the philosophy cut. xlfg is now a single inline guide, not an orchestration graph. The v5 scaffolding — 27 specialist agents, 9 hidden phase skills, file-based run state (`spec.md`, `workboard.md`, `phase-state.json`, the whole `docs/xlfg/runs/<RUN_ID>/` tree), Stop / SubagentStop hooks, a durable JSONL ledger, and a parallel Codex surface — is all gone. Opus 4.7-class models hold a multi-phase SDLC run in their own context; the scaffolding was paying serialization cost for state the model no longer externalizes.

### What v6 ships

- `plugins/xlfg-engineering/commands/xlfg.md` — ~3000-word inline guide covering all 8 phases (recall → intent → context → plan → implement → verify → review → compound). Specialist lenses (PM, architect, security, perf, UX, test strategist, runner/reducer, reviewer) appear as mental passes the main model adopts in-line, not as dispatch targets.
- `plugins/xlfg-engineering/commands/xlfg-debug.md` — diagnosis-only guide (recall → intent → context → debug). `allowed-tools` intentionally excludes `Edit`, `MultiEdit`, `Write`.
- `plugins/xlfg-engineering/scripts/audit_harness.py` — four-check self-audit for CI (version sync, command surface, command frontmatter, forbidden-token sweep).
- `plugins/xlfg-engineering/hooks/hooks.json` — just the `PermissionRequest` `ExitPlanMode` auto-allow.
- `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` — manifests (version 6.0.0). Codex manifest removed.
- `tests/test_xlfg_v6.py` — 20 focused tests that guard the plugin shape, command frontmatter, and load-bearing philosophy tokens.

Everything else from v5 is deleted. See `plugins/xlfg-engineering/CHANGELOG.md` for the full "removed" list.

### What NOT to reintroduce

The test suite catches these drifts; don't try:
- Files under `plugins/xlfg-engineering/agents/**` or `skills/**`
- A `codex/` tree or `.codex-plugin/` manifest
- More than `audit_harness.py` under `scripts/`
- Dispatch-contract tokens in command bodies (`PRIMARY_ARTIFACT`, `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`, `RETURN_CONTRACT:`, `DONE_CHECK:`)
- Stop or SubagentStop hook registrations
- `Skill(...)`, `Agent`, or `SendMessage` in command `allowed-tools`

If you have a real case for re-adding any of those, open a discussion. The removal was intentional.

### Migration (v5.1.0 → v6.0.0)

- Public entry surface is smaller: only `/xlfg` and `/xlfg-debug` remain. `/xlfg-audit`, `/xlfg-status`, `/xlfg-init`, and the Codex `$xlfg` / `$xlfg-debug` skills were all removed.
- In-progress v5 runs: finish under v5 or abandon. The v5 phase-state format is unused in v6. Delete `docs/xlfg/runs/` and `.xlfg/` before upgrading.
- If you relied on the ledger for cross-run memory: promote durable lessons to the target project's `CLAUDE.md` before upgrading. v6 has no ledger.
- Runtime: `python3` on PATH (for the CI audit only). No Node. Zero runtime deps for end users.

## Previous state (5.1.0)

5.1.0 ported every runtime helper from Node to Python. Previously the plugin
shipped 7 `.mjs` scripts (stopped hooks, phase tick, ledger append, workboard
render, audit harness, post-mortem) plus a parallel Python test suite that
spawned them via `node`. CI required both runtimes. The new layout collapses
everything to one language:

- `plugins/xlfg-engineering/scripts/phase_gate.py`
- `plugins/xlfg-engineering/scripts/subagent_stop_guard.py`
- `plugins/xlfg-engineering/scripts/phase_tick.py`
- `plugins/xlfg-engineering/scripts/ledger_append.py`
- `plugins/xlfg-engineering/scripts/render_workboard.py`
- `plugins/xlfg-engineering/scripts/audit_harness.py`
- `plugins/xlfg-engineering/scripts/post_mortem.py`

The CLI contracts (flags, exit codes, stdout/stderr shapes), hook behavior,
and file formats are preserved exactly. `hooks.json` now invokes
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"`. Every reference in the
slash commands, skills, agent templates, tests, and CI workflow was updated
in lockstep. No `.mjs` files remain in the repo. Node is no longer a runtime
dependency.

Migration note for operators: ensure `python3` is on PATH (Python 3.11+ is
what CI tests against, but the scripts use stdlib only and should run on any
3.9+). No public entry surface changed: `/xlfg`, `/xlfg-debug`, `/xlfg-audit`,
and `/xlfg-status` behave identically.

## Previous state (5.0.0)

5.0.0 is the dedup + cache-stable-prefix release. The 4.4–4.6 dedup fields
(`OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, `PRIOR_SIBLINGS`) stay. The change is
that the boilerplate that every agent and every phase skill repeated is now
extracted into two shared files. Each agent and each phase skill references
the shared file instead of duplicating the rules.

The trigger was four pain points surfaced by the user, all confirmed by
Anthropic / Cognition guidance:

1. Tasks divided per atomic-task instead of per epic.
2. Artifacts too detailed, criteria overlap.
3. Sub-agent prompts too specific AND dispatch packets also instruct them to
   read detailed instructions — duplication with the agent definition.
4. Too many read/writes slow every run.

What changed:

- New `agents/_shared/agent-preamble.md` owns the 7 boilerplate sections every
  specialist carried: compatibility, execution contract, turn budget rule,
  tool failure recovery, ARTIFACT_KIND, completion barrier, final response
  contract. All 27 specialists shrunk to role-delta only (frontmatter +
  identity + inputs/outputs + rules + handoff format) and cite the preamble.
- New `agents/_shared/dispatch-rules.md` owns the delegation packet contract:
  packet-size ladder, preseed rule, machine-readable headers, CONTEXT_DIGEST
  decisions+paths shape, micro-packet budget, proof budget, compaction,
  sequential dispatch default, resume-same-specialist rule. All 6 phase
  skills replaced their ~40-line duplicated Delegation packet rules block
  with a pointer.
- Packet-size ladder introduced: `trivial` / `standard` / `epic` / `split`.
  `xlfg-task-divider` default is now **epic** — one packet per objective
  group `O1`, `O2`, ... — not per atomic task. Atomic sub-division only when
  surfaces are truly unrelated or genuinely read-mostly independent.
- `CONTEXT_DIGEST` now carries **decisions + rationale + path refs**, not
  just raw facts. Digest + re-read is explicitly forbidden: if the digest
  summarizes a decision, the specialist pulls scoped file:line on demand
  instead of re-reading the canonical file.
- Tests migrated: boilerplate assertions check the preamble + each agent
  references it; packet-contract assertions accept either inline contract
  or a reference to `_shared/dispatch-rules.md`.

Research anchors (cited in CHANGELOG): Anthropic, *How we built our
multi-agent research system*; Anthropic, *Effective context engineering for
AI agents*; Anthropic, *Writing effective tools for AI agents*; Anthropic,
*Building effective agents*; Anthropic, *Prompt caching*; Cognition, *Don't
Build Multi-Agents*.

If you continue from here:

- Do **not** add back boilerplate to individual agent files. The preamble is
  the single authoritative source. New agents must cite it.
- Do **not** split an epic packet into many atomic packets just because the
  scope "feels big". Prefer one owner per decision slice; Cognition's
  principle — parallel divergent actions create bad merges — applies.
- Do **not** pass a digest and *also* tell the specialist to re-read the
  canonical file for the same decision. Pick one.
- When adding a new phase skill or command that delegates, reference
  `_shared/dispatch-rules.md` rather than inlining the full rule block.
- Deferred work (tracked for a follow-up release): agent merges (3 context
  investigators → 1; `xlfg-test-readiness-checker` → `xlfg-test-strategist`;
  `xlfg-repo-mapper` + `xlfg-harness-profiler` → one); full optional-artifact
  collapse into `spec.md` / `context.md` sections. Both were scoped out of
  5.0.0 to limit test-assertion churn; they should come back with a careful
  test migration.

## Previous state (4.6.0)

4.6.0 optimizes the dispatch shape that 4.4.0 and 4.5.0 made mandatory. The
dedup fields stay: every specialist packet still needs `OWNERSHIP_BOUNDARY`,
`CONTEXT_DIGEST`, and `PRIOR_SIBLINGS`. The new rule is that those fields must
stay lean. Packets are contracts, not implementation recipes.

The trigger was a real run log where an implementation packet grew into a
near-line-by-line coding script, repeated `yarn tsc --noEmit && yarn test ...`
for task-local work, and then pushed report/artifact details back through the
run card. That shape burns tokens twice: once in the dispatch prompt, then again
when the conductor reads/synthesizes the artifacts.

What changed:

- `agents/_shared/output-template.md` now defines v4.6.0 micro-packet,
  proof-budget, and artifact-compaction rules.
- `/xlfg`, `/xlfg-debug`, and every delegating phase skill repeat the rule where
  conductors draft packets: aim for <=900 words, use file:line/evidence anchors,
  avoid long code/log excerpts, and do not dictate import placement, variable
  names, or line-by-line edits when scoped files contain the local pattern.
- Task-level `DONE_CHECK` now means the cheapest honest local proof. Broad
  build/full-suite/live acceptance proof belongs to verify-phase `fast_check`,
  `smoke_check`, or `ship_check` unless the task is a final integration lane or
  touched shared type/schema/config surfaces that require the broad command now.
- Conductors must compact returned specialist artifacts before updating
  `spec.md`, `workboard.md`, `context.md`, `verification.md`, or summaries:
  promote status, verdict, changed files, command names/results, blockers, and
  next action only. Full reports and long logs stay in lane artifacts.
- `xlfg-task-implementer` now explicitly refuses to patch out-of-scope files
  just to satisfy a failing `DONE_CHECK`. If the failure comes from an
  out-of-scope file, fixture, test, hook, or dependency, it records evidence and
  returns `BLOCKED` or `FAILED` unless the parent packet widens `FILE_SCOPE` and
  `OWNERSHIP_BOUNDARY`.
- `$xlfg` and `$xlfg-debug` carry the same micro-packet guidance for Codex runs.

If you continue from here:

- Do **not** remove `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, or
  `PRIOR_SIBLINGS`; make them smaller and more factual.
- Do **not** put full code blocks, long logs, or exact before/after recipes in a
  specialist packet unless the task is literally a mechanical rewrite.
- Do **not** add generic full build + full suite chains to every task
  `DONE_CHECK`. Put broad proof in verify phase unless a task truly needs it.
- Do **not** paste full specialist reports into canonical run files. Canonical
  files carry compact state; lane artifacts carry detail.
- When bumping versions, remember `tests/test_codex_plugin.py`,
  `docs/xlfg/meta.json`, `README.md`, plugin README, `CHANGELOG.md`, and this
  file in addition to the three plugin manifests.

## Previous state (4.5.0)

4.5.0 adds the missing ownership half of the 4.4.0 dedup story. `CONTEXT_DIGEST` stopped specialists from re-reading canonical files; `PRIOR_SIBLINGS` stopped same-phase siblings from re-finding the same facts. The remaining waste was decision overlap: adjacent specialists still had enough freedom to re-adjudicate work another lane owned (e.g. flow spec vs test proof, source implementer vs test implementer, verify runner vs reducer, UI verification vs UX review).

The new mandatory packet field is:

- `OWNERSHIP_BOUNDARY` — the conductor names what the specialist owns, what it must not redo, and which artifacts it consumes as input truth.

Single source of truth lives in `agents/_shared/output-template.md` alongside the packet shape. Every delegating entrypoint repeats it inline: `commands/xlfg.md` and the phase skills `intent`, `context`, `plan`, `implement`, `verify`, `review`, and `debug`. All 27 specialist agents now honor `OWNERSHIP_BOUNDARY` in the Turn budget rule and use a `Covered elsewhere` pointer instead of repeating adjacent-lane analysis.

High-risk boundaries now have explicit prompt text:

- context: repo-map owns command/structure inventory; harness-profiler owns profile/budget; env-doctor owns runnable environment health; researcher owns only external facts repo truth cannot provide.
- plan: why owns user value; root-cause owns mechanism; solution owns option choice; spec-author owns behavior; UI designer owns `DA*`; test-strategist owns proof commands; readiness owns the gate; task-divider owns task packets; risk owns release/safety pressure.
- implement: task-implementer owns source changes unless the packet explicitly includes test ownership; test-implementer owns test/proof files; task-checker owns task-local ACCEPT/REVISE and must not rerun full scenario proof.
- verify: verify-runner executes and records evidence; verify-reducer judges run truth and must not rerun commands unless runner artifacts are missing/corrupt; UI verify only covers unresolved/contradictory DA evidence.
- review: each reviewer reports net-new lens findings only after filling "Already covered by verification"; UX cites `ui-verification.md` and DA coverage instead of repeating it.

Codex `$xlfg` / `$xlfg-debug` packet examples and phase references now carry the same dedup semantics. Version is bumped to 4.5.0 across all three plugin manifests and `docs/xlfg/meta.json`.

If you continue from here:

- Do **not** add a new delegating phase skill, command, or Codex specialist packet shape without `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and `PRIOR_SIBLINGS`.
- Do **not** let an agent solve adjacent lanes just because it has the context. Cite the owning artifact and record `Covered elsewhere` unless the packet explicitly asks for contradiction analysis.
- Keep the boundaries concrete in packets. Weak ownership text like "do the planning" will recreate the overlap this release removed.
- When adding a new specialist, decide its lane ownership against the existing phase boundaries before writing its output format.

This supersedes nothing in 4.4.0. The 4.4.0 digest/sibling dedup fields remain mandatory; 4.5.0 adds the ownership decision boundary on top.

## Previous state (4.4.0)

4.4.0 generalizes a sub-agent dedup contract that previously existed only in `xlfg-review-phase`. Sub-agents in xlfg already communicate exclusively through files — the conductor preseeds a `PRIMARY_ARTIFACT` with `status: IN_PROGRESS`, the specialist updates that exact file in place, and the final chat reply is a single `DONE|BLOCKED|FAILED <path>` line enforced by `subagent-stop-guard.mjs`. There is no chat-based synthesis between siblings.

The remaining waste was on the read side. Each specialist's "Input you will receive" list named ~10 canonical files (`spec.md`, `context.md`, `current-state.md`, …) and the specialist re-read each one even when the conductor had just synthesized them. Sibling specialists in the same phase lane (e.g., the three context investigators; the planning specialists; the multi-lens reviewers; implementer→checker) re-derived overlapping findings because the dispatch packet did not list prior siblings.

**The fix is two new mandatory packet fields, not new agents:**

- `CONTEXT_DIGEST` — the conductor inlines the canonical excerpts the specialist actually needs. Specialists treat the digest as authoritative and only re-read source files when it is explicitly insufficient.
- `PRIOR_SIBLINGS` — the conductor lists every artifact already produced in the same phase lane that overlaps the new specialist's surface. The new specialist skims listed siblings and explicitly skips covered ground.

Single source of truth lives in `agents/_shared/output-template.md` (`## Dispatch packet shape (canonical)`). Every delegating entrypoint references it: `commands/xlfg.md` (conductor) and seven phase skills — `intent`, `context`, `plan`, `implement`, `verify`, `review`, `debug`. All 27 specialist agents had their Turn budget rule expanded to honor both fields, making the contract two-sided.

**If you continue from here:**

- Do **not** treat the agent's "Input you will receive" file lists as the primary contract. They are a fallback. The dispatch packet's `CONTEXT_DIGEST` is the primary input; specialists re-read source files only when the digest is explicitly insufficient.
- Do **not** add a new delegating phase skill or entrypoint without including `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` in its Delegation packet rules. The two new tests in `tests/test_xlfg.py` (`test_all_delegating_entrypoints_require_context_digest_and_prior_siblings`, `test_specialist_agents_honor_context_digest_and_prior_siblings`) will catch missing coverage.
- Do **not** centralize the packet rule into a single template-include. Each phase skill keeps its own copy because phase-specific examples (`xlfg-root-cause-analyst → xlfg-solution-architect`, `xlfg-verify-runner → xlfg-verify-reducer`, etc.) belong inline where the conductor reads them. The canonical template owns the *shape*; the phase skills own the *examples*.
- The two `none` / `see PRIMARY_ARTIFACT preseed` escape hatches exist for the genuinely-empty case (intent phase has no priors; some specialists need only the artifact preseed). Use them honestly — never fabricate `PRIOR_SIBLINGS` content to satisfy the contract.
- `xlfg-review-phase`'s pre-existing `CONTEXT_DIGEST` rule was rewritten to match the canonical shape rather than left as a one-off. The 4.3.0 review-phase wording is gone.

This supersedes nothing in 4.3.0 — speed-of-run optimizations, `ARTIFACT_KIND`, `in_progress_phase`, smoke-first verify, `APPROVE-WITH-NOTES-FIXED`, and `/xlfg-status` are all unchanged. 4.4.0 is purely a "specialists stop redoing each other's reads and findings" pass.

## Previous state (4.2.0)

4.2.0 splits the audit surface into two commands serving two audiences. The previous `/xlfg-audit` was a category error: every "check" it ran (version sync, SDLC coverage, word counts, frontmatter regex, forbidden-token sweep) was a deterministic file read pretending to need an LLM. It also gave the user running it nothing — the report only existed to be phoned home to upstream maintainers. 4.1.1 fixed a path-anchoring bug inside that wrong shape; 4.2.0 fixes the shape itself.

**The split:**

- **`scripts/audit-harness.mjs` (new)** — port of all 6 former audit checks as a deterministic Node CLI. Wired into `.github/workflows/ci.yml` so every PR runs it. Exit 1 on any failure. Maintainer concern, runs without an LLM. Stale-`Task` sweep was tightened to inspect only the frontmatter `tools:` field (the previous regex flagged "## Task decomposition" headings in agent files as false positives).
- **`/xlfg-audit` slash command (rewritten body)** — per-run post-mortem for the user who just ran `/xlfg`. Delegates to `scripts/post-mortem.mjs`, which reads the latest run dir's `phase-timings.jsonl`, lists artifacts and ledger entries, and emits a per-phase wall-time table plus heuristic suggestions for what could be faster or leaner. Submission to `flrngel/xlfg` is preserved with the same redaction contract plus a new rule for `RUN_ID` slug content.
- **`scripts/phase-tick.mjs` (new)** — every phase Skill call in `commands/xlfg.md` and `commands/xlfg-debug.md` is now bracketed by two `phase-tick` invocations (start before, end after). Loopbacks emit fresh start/end pairs that the post-mortem sums. Best-effort writes — failures exit 0 so the conductor is never blocked.

**Why this matters:**

- The new `/xlfg-audit` answers the question users actually ask after a long run ("where did the time go?"). The old one answered a question only maintainers cared about, and answered it badly enough that the 4.1.1 anchoring bug shipped unnoticed.
- The submitted-upstream report now contains real run data (per-phase wall time, loopback counts, which lane was slow). That's actionable feedback for the harness; the static manifest checks the old audit submitted were not.
- `phase-timings.jsonl` is also useful outside `/xlfg-audit` — any future tooling that wants per-phase cost analysis (parallelization opportunities, retry budgets, specialist dispatch tuning) can read it.

**If you continue from here:**

- Do **not** put computation into `commands/xlfg-audit.md` — the body is intentionally a thin orchestrator. All data work lives in `scripts/post-mortem.mjs`. If you need a new metric, add it to the script (and a test under `tests/test_post_mortem.py`), not to the markdown.
- Do **not** re-add manifest/frontmatter checks to the slash command. Those belong in `scripts/audit-harness.mjs` and CI. The slash command and the harness audit MUST stay separate.
- Do **not** drop the `phase-tick` calls from the conductors. Without them, the post-mortem can only show artifact shape, not wall time, and the user's "why so slow" question goes unanswered. The phase-tick script is best-effort by design — write failures must never block the conductor, but the conductor must always emit the call.
- Do **not** widen the stale-`Task` sweep back to body text. The frontmatter-only scope is the correct one; the previous body sweep had false positives on every legitimate use of the English word "Task".
- The `flrngel/xlfg` submission target stays hardcoded. Same rule as 4.1.0 — no per-user override, no `--issue` flag, no `gh repo view` runtime resolution.

This supersedes the 4.1.1 path-anchor work in the slash command (the body has been replaced) but the architectural principle behind 4.1.1 — that an audit reads the right files for what it is auditing — is preserved by the new split. `audit-harness.mjs` reads the plugin; `post-mortem.mjs` reads the cwd's run dir. The two never overlap, so the anchor bug class can't return.

## Previous state (4.1.1)

4.1.1 fixes a real bug in `/xlfg-audit`: it never anchored its file reads to the installed plugin location, so when run from any target repo the dispatched agents scanned the user's cwd instead. The audit's own opening line says "Measure the harness itself, not the user's project" — and yet the implementation did the opposite anywhere outside the xlfg source repo.

The fix is a `## Locate the plugin (run this FIRST)` preamble that resolves `PLUGIN="${CLAUDE_PLUGIN_ROOT:-}"`, falls back to `./plugins/xlfg-engineering` when invoked from the source repo (detected via the presence of `./plugins/xlfg-engineering/.claude-plugin/`), and aborts with `fail: cannot locate plugin root` if neither resolves. Every path in checks 1–5 (manifests, phase skills, public commands, agents, codex skills) is now prefixed with `$PLUGIN/`. Check 6 (scaffold self-consistency) remains the only check that reads from cwd, because that's where the user's `docs/xlfg/meta.json` actually lives — and its missing-file outcome was downgraded from `fail` to `warn` because invoking the audit outside an xlfg-initialized project is a legitimate use of the command.

If you continue from here:
- Do **not** drop the `$PLUGIN/` prefix from any check 1–5 path. The regression test `test_xlfg_audit_anchors_plugin_paths_to_plugin_root` will catch that, but the architectural intent matters more than the test: the audit inspects the plugin, not the user's repo.
- Do **not** add `$PLUGIN/` to check 6. That check is **about** the user's project (it reads `./docs/xlfg/meta.json` to detect scaffold drift). Anchoring it to `$PLUGIN` would silently turn the check into a no-op.
- Do **not** remove the source-repo fallback. `CLAUDE_PLUGIN_ROOT` is unset when developers run the audit against the xlfg source itself; the fallback is the only thing that keeps the audit usable during plugin development.
- If a future audit grows a new check, decide explicitly which side it lives on (plugin vs. cwd) and document it in the same way as checks 1–5 vs. check 6.

This supersedes nothing in the 4.1.0 guidance — the `flrngel/xlfg` feedback loop, the prompt-every-time submission flow, and the redaction contract are all unchanged. 4.1.1 is purely a "the audit now reads the right files" fix.

## Previous state (4.1.0)

4.1.0 makes `/xlfg-audit` a feedback loop to the xlfg maintainers. The command takes no arguments. After every audit:

1. Print the full chat report (summary table first, detail after).
2. Ask the user verbatim: `Submit this redacted audit to the xlfg maintainers at flrngel/xlfg so they can improve the harness? (y/n)`
3. On `y`: run the redaction contract, then `gh issue create --repo flrngel/xlfg …`. On `n` (or any non-`y`): print `ok, not submitting.` and stop. On non-interactive contexts: skip submission silently.

The target is **always `flrngel/xlfg`**. There is no per-user override, no `--issue` flag, and no `gh repo view` runtime resolution. The point of `/xlfg-audit` is not to help the user running it — they get no new capability from auditing xlfg itself. It exists so the maintainers can see how the harness behaves on real repos and fix what breaks. The v3.3.1 design (opt-in flag defaulting to the user's own repo) broke that loop; 4.1.0 flips it into a phone-home feedback path where the answer is the submission itself.

Why this matters:
- A feature that only runs behind a flag the user has to know yields zero submissions in practice. Maintainers see nothing. Burying the feedback path defeats the command.
- Filing into the user's own repo is actively wrong — the audit is about xlfg, not about the user's project, so the user's own tracker is the wrong destination.
- The prompt-every-time design means the user is always in the loop about the submission; there is no silent phone-home.

If you continue from here:
- Do **not** re-introduce a `--issue` flag or any per-user target override. The target is `flrngel/xlfg`, hardcoded. If someone asks to file into their own repo, tell them to copy the chat report manually.
- Do **not** re-introduce `gh repo view --json nameWithOwner` resolution. 3.3.1's "default to the user's cwd repo" behavior is gone and must not return.
- Do **not** remove the prompt. Always-submit-silently is a phone-home without consent, which is worse than the 3.3.1 opt-in design.
- Keep the redaction contract intact. Home paths, emails, git identity, hostnames, Signed-off-by, Co-authored-by — all still stripped before filing. Token-shape detection still **aborts** filing rather than trying to clean.
- If the audit grows new sections, the summary-table row count must still match the section count, same rule as 3.3.1.
- This supersedes the 3.3.1 guidance that said "Do not turn `/xlfg-audit --issue` into a prompt-before-filing flow." That rule applied to the old CI-friendly opt-in design. The command's purpose has since been clarified: it is a feedback tool, not a CI artifact producer. The prompt-always design is the correct shape for the clarified purpose.

## Previous state (3.3.1)

3.3.1 is a pure-prompt upgrade to `/xlfg-audit`. Two behaviors changed and nothing else:

1. **Summary table leads.** The report now prints a per-check table (one row per check 1–7 with `status` / `score` / `note`) as the very first block. Headline scores, load drivers, gaps, improvements, and verdict come after. The old layout buried the table between the checks and the prose; a reader could not see pass/fail at a glance without scrolling.
2. **Optional GitHub issue filing with redaction.** `/xlfg-audit --issue` (or `/xlfg-audit --issue <owner>/<repo>`) files the redacted report as a `gh issue create` call. Preconditions are checked up front (`gh auth status`, inside a git repo or explicit `<owner>/<repo>`) and on failure the command prints a single warning and keeps the chat report — it does not prompt, does not retry. The redaction contract strips home paths (`/Users/<name>/…`, `/home/<name>/…`, `C:\Users\<name>\…`), emails, git identity, hostnames, `Signed-off-by` / `Co-authored-by` lines, and **aborts** the `gh` call if any token-shape string appears (`ghp_`, `github_pat_`, `xox[baprs]-`, `sk-`, `AIza`, `AKIA`, `-----BEGIN`).

Why this matters:
- The per-check summary table was already in the output format, but buried. Moving it to the top makes the audit scannable in the same way that `gh pr checks` is — a reader sees the verdict before the detail.
- Filing the audit as an issue is how harness regressions get prioritized on real repos. Doing it via the command (rather than copy-paste) lets the redaction contract run deterministically every time instead of depending on the user to remember to scrub paths.
- The redaction rules are *conservative*: if a secret-shape string leaks into the audit body, we abort filing rather than try to clean it, because a leak means something upstream is broken and filing it to GitHub would make it worse.

If you continue from here:
- Do **not** turn `/xlfg-audit --issue` into a prompt-before-filing flow. It is a deliberate "quiet if preconditions fail, file if they hold" design. Adding a confirmation prompt would break its usefulness inside a non-interactive CI / run loop.
- If the audit grows new sections, keep the summary table row count aligned with the section count. New checks must add a row.
- Keep the redaction list a **hard-coded set** inside the command prompt. Do not delegate redaction to a helper script — the prompt is the only place the rules are actually enforced right now, and splitting them into a script would re-introduce the Python-CLI surface that 3.0.0 removed.
- When adding labels to the issue, never auto-create them on the target repo; the current shape lets `gh` fail silently on missing labels, which is correct behavior for a third-party tool filing into someone else's repo.

## Previous state (3.3.0)

3.3.0 restores `/xlfg-init` and `/xlfg-audit`, two plugin commands deleted in v3.0.0 as part of the Python CLI removal. The v3.0.0 cleanup was over-broad: `xlfg-init.md` was always a pure-prompt markdown file with zero CLI calls (it just told the model to create directories with Write), so bundling it with the CLI removal was an accident. `xlfg-audit.md` did have a Python scoring pipeline behind it, but the markdown-only fallback is salvageable as a deterministic self-audit if every numeric check is rewritten to concrete file reads and frontmatter inspections.

What changed:
- `plugins/xlfg-engineering/commands/xlfg-init.md` — idempotent scaffold repair. Creates missing tracked directories (`docs/xlfg/knowledge/`, `docs/xlfg/knowledge/agent-memory/`, `docs/xlfg/migrations/`), local-only directories (`docs/xlfg/runs/`, `.xlfg/runs/`), and missing durable knowledge files without overwriting any existing file. Ensures `.gitignore` has the canonical four-line xlfg ignore set. Flags blanket `docs/xlfg/` ignore lines as drift and asks before removing.
- `plugins/xlfg-engineering/commands/xlfg-audit.md` — every check is a file read Claude can perform: version sync across the three manifests, SDLC coverage (9 phase-skill directories), workflow load (wc -w on the main command + phase skills, with top-3 load drivers called out), Claude Code compatibility (command + phase-skill frontmatter, forbidden-token sweep for stale `Task` tool name and `query-contract.md`, specialist `maxTurns` ≤ 150 + leaf-worker rule), Codex surface integrity (exactly two public skills, no Claude-only tokens), and scaffold self-consistency (`meta.json.tool_version` vs `plugin.json.version`).
- `.gitignore` — removed the blanket `docs/xlfg/` line. That line was added 2026-04-13 in `dadb737` and silently blocked `git add` for new durable knowledge files (e.g. new role-memory docs). Already-tracked knowledge files were never affected because `.gitignore` does not un-track. Canonical ignore set: `.xlfg/`, `docs/xlfg/runs/*`, `!docs/xlfg/runs/.gitkeep`, `!docs/xlfg/runs/README.md`.
- `plugins/xlfg-engineering/CLAUDE.md:49` — fixed stale `/xlfg:init` → `/xlfg-init`, and added a line for the new read-only `/xlfg-audit`.
- `tests/test_codex_plugin.py` — version assertions bumped to `3.3.0`.

Why this matters:
- The repo's own living docs (`plugins/xlfg-engineering/CLAUDE.md`, `docs/planning-autonomy-2026-refresh.md`) still referenced `/xlfg-init` as a maintenance command, so the deletion left a dangling contract. Restore makes the docs honest.
- `/xlfg-audit` is the only deterministic way to catch harness regressions (version drift, frontmatter rot) without running a full `/xlfg` cycle. v3.0.0 lost that safety net; this restores it without re-introducing Python.
- The blanket-ignore drift was silently hostile to knowledge-tracking runs. Fixing it is part of the "smart scaffold" story.

If you continue from here:
- Do **not** re-introduce a Python CLI. Both restored commands are pure-prompt markdown; they must stay that way.
- If the audit checks grow, keep them deterministic (file reads, grep, frontmatter parsing). No shelling to a CLI, no network calls.
- If the scaffold gains new durable knowledge files, add them to the `xlfg-init.md` create-if-missing list AND the audit's coverage check.
- When touching `.gitignore` in the xlfg scaffold, keep the canonical set intact. If you need to add a new ignore, add it *above* or *below* the canonical block with a comment, not inside it.

## Previous state (3.2.2)

3.2.2 is a startup-hygiene bug fix. Before this, every repeat `/xlfg` or
`/xlfg-debug` run on a project that already had a `.xlfg/phase-state.json`
from a prior run died on the first `Write(.xlfg/phase-state.json)` with
`File has not been read yet. Read it first before writing to it.` — Claude
Code's Write tool refuses to overwrite an existing file the current session
has never read, and the conductor's very first Write was against a stale
file from the previous run.

The fix is a single instruction in each conductor entrypoint: run
`rm -f .xlfg/phase-state.json` in the same shell step that syncs the
scaffold directories, so the initial Write always sees an absent target.
The phase-gate Stop hook already tolerates a missing `phase-state.json`
(exits 0), and the conductor writes the initial state immediately after,
so the removal window is trivial. The same `rm -f` guidance was added to
the Codex `$xlfg` and `$xlfg-debug` skills for consistency.

Do not roll this back into a "Read first if present, then Write" pattern.
The reset semantics are intentional: each run starts from a clean phase
ledger, which also prevents the Stop hook from carrying forward
`completed` entries from a previous run.

## Previous state (3.2.1)

3.2.1 removes the Context7 MCP dependency. Nothing in the runtime actually
called into it, so keeping the server wired up was just a surface risk. The
public entry model is unchanged — `/xlfg`, `/xlfg-debug`, `$xlfg`,
`$xlfg-debug` still run end to end.

What changed:
- Deleted `plugins/xlfg-engineering/.mcp.json`.
- Removed the `mcpServers` block from `.claude-plugin/plugin.json` and the
  `mcpServers` key from `.codex-plugin/plugin.json`.
- `xlfg-researcher` no longer advertises the Context7
  tool. Research now goes through `WebSearch` / `WebFetch` only.
- `tests/test_codex_plugin.py` no longer asserts on `mcpServers`.

If you continue from here: do not re-introduce an MCP server dependency unless
a specialist lane actually calls into it. The researcher agent's tool list is
the canonical signal — add the server only if that agent uses it.

## Previous state (3.2.0)

3.2.0 adds first-class Codex support without changing the existing Claude Code
entry model. The new Codex surface is intentionally separate:

- `plugins/xlfg-engineering/.codex-plugin/plugin.json` is the Codex manifest.
  It points at `./codex/skills/`.
- `.agents/plugins/marketplace.json` exposes the local plugin to Codex from
  `./plugins/xlfg-engineering`.
- `plugins/xlfg-engineering/codex/skills/xlfg/SKILL.md` and
  `plugins/xlfg-engineering/codex/skills/xlfg-debug/SKILL.md` are the only
  public Codex skills. They invoke as `$xlfg` and `$xlfg-debug`.
- `plugins/xlfg-engineering/codex/references/phases/` holds the Codex internal
  phase guidance. Do not add extra public Codex phase skills unless the entry
  model deliberately changes.
- `plugins/xlfg-engineering/codex/references/model-policy.md` states that
  Codex must not load the Claude specialist definitions under
  `plugins/xlfg-engineering/agents/**`; their `model` / `effort` frontmatter is
  Claude Code-only.

Why the split matters:
- Codex skills require `name` and `description` frontmatter, while the existing
  Claude plugin hidden phase skills intentionally omit `name:` and stay
  `user-invocable: false`.
- Codex plugins currently package skills, MCP config, apps, and metadata. This
  release does not attempt hard hook parity; the Codex skills use prompt-level
  barriers plus `.xlfg/phase-state.json` and file-backed artifacts.
- Codex uses the active session model/effort by default and selects built-in
  Codex roles (`explorer`, `worker`, `default`) by lane shape unless the user or
  project config supplies a Codex custom agent.
- The current Claude Code `/xlfg` and `/xlfg-debug` command surfaces are
  unchanged.

If you continue from here:
- Bump **all three** manifests for behavior changes:
  `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and
  `.codex-plugin/plugin.json`.
- Keep the Codex public skill count at exactly two unless the public Codex
  entry model changes.
- Keep Claude-only concepts out of `plugins/xlfg-engineering/codex/**`
  (`allowed-tools`, `Skill(...)`, `TaskCreate`, `TaskUpdate`, `TaskList`,
  `ExitPlanMode`, `PermissionRequest`, `CLAUDE_PLUGIN_ROOT`,
  `user-invocable`).
- Run `python3 scripts/lint_plugin.py` and `python3 -m unittest discover tests/`.

## Previous state (3.1.1)

3.1.1 is a CI/tooling patch on top of 3.1.0. `scripts/lint_plugin.py` walked every markdown file under `plugins/xlfg-engineering/agents/**` expecting agent frontmatter, so the new shared reference at `agents/_shared/output-template.md` (shipped in 3.1.0) failed the frontmatter check and broke CI. The linter now skips any path containing `_shared`, which is the home for cross-agent reference material rather than agent definitions. Also resyncs `plugin.json` / `.cursor-plugin/plugin.json` — 3.1.0 shipped without bumping them.

If you continue from here: when adding new cross-agent reference docs, keep them under `agents/_shared/` so the linter knows to skip them. Real agents still live under `agents/{planning,implementation,verify,review}/` and must keep YAML frontmatter.

## Previous state (3.1.0)

3.1.0 targets inter-agent communication waste. The run artifacts now carry a single canonical `status:` field (inside YAML frontmatter), phase-status in `workboard.md` is rendered from `.xlfg/phase-state.json` instead of hand-written per phase, the Claude Code task pane is kept in sync with xlfg's phase list via a startup `TaskCreate` bridge, `ledger.jsonl` has a real schema and a single validating writer, and two specialist lanes (`xlfg-repo-mapper` in context-phase; verify-phase `xlfg-ui-designer` re-fire) are gated instead of unconditional.

What changed:
- `plugins/xlfg-engineering/scripts/subagent-stop-guard.mjs` parses YAML frontmatter `status:` first, falls back to the legacy bare `Status:` first line for backward compatibility. New templates prescribe YAML only.
- 54 agent files (27 × 2 packs) converted from bare `Status: DONE | BLOCKED | FAILED` to YAML frontmatter. Completion-barrier prose, turn-budget rule, and preseed convention all point at the YAML shape.
- `plugins/xlfg-engineering/agents/_shared/output-template.md` is the single reference for frontmatter / preseed / final-chat shape.
- `plugins/xlfg-engineering/skills/xlfg-context-phase/SKILL.md:29` replaces `always run xlfg-repo-mapper` with a conditional skip when `memory-recall.md` already grep-cites coverage.
- `plugins/xlfg-engineering/skills/xlfg-verify-phase/SKILL.md:34` adds a task-checker-DA-coverage gate to the UI-designer re-fire.
- `plugins/xlfg-engineering/scripts/render-workboard.mjs` renders the `## Phase status` block from `.xlfg/phase-state.json` between HTML-comment markers. Phase skills no longer write phase-completion rows.
- `plugins/xlfg-engineering/commands/xlfg.md` adds `TaskCreate`/`TaskUpdate`/`TaskList` to `allowed-tools`, and a "Harness task bridge" startup step that creates `xlfg: <phase>` tasks.
- `docs/xlfg/knowledge/ledger-schema.md` is the canonical shape. `plugins/xlfg-engineering/scripts/ledger-append.mjs` is the only allowed writer.

Why this matters:
- Artifact bytes-per-run drop: one status line per artifact instead of two, phase-status rendered once per boundary instead of hand-re-described each phase.
- Harness-task-pane nag is silenced without making `workboard.md` a second source of truth.
- Ledger events stop drifting across runs — schema rejects unknown shapes at write time.
- Specialist theater removed on two common axes (recall vs repo-mapper; UI-designer plan + task-checker + UI-designer verify).

If you continue from here:
- Keep YAML frontmatter as the canonical artifact header shape. The stop-guard's bare-Status fallback is a transition branch, not a long-term contract — future breaking release can remove it.
- When creating a new agent, copy the scaffold from `agents/_shared/output-template.md`; don't reinvent it.
- When appending to `ledger.jsonl`, always go through `scripts/ledger-append.mjs`. Direct `echo >>` is forbidden and will drift again.
- Phase skills still own the task / objective / blocker sections of `workboard.md`. They MUST NOT hand-write phase-status rows — the renderer owns that region.
- The `TaskCreate` bridge is startup-only and completion-only. Do NOT create harness tasks for specialists or sub-packets.
- Historical note: before Codex support, behavior changes bumped both `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`. Current changes must also bump `.codex-plugin/plugin.json` per the 3.2.0 section above.
- Keep the plugin agent pack consistent across updates. CI enforces frontmatter and structure checks on every agent.

Intentionally not done in 3.1.0 (known-open):
- Phase B from the plan (CONTEXT_DIGEST per phase + shared delegation-rules doc) — user deferred.
- O1 scale-tier redesign (XS/S/M/L, SKIPPED terminal state, specialist "lite" variants) — belongs in its own RFC.
- Cost observability (tokens / wall-time / specialist count) and auto run-summary.

## Earlier state (3.0.0) — for reference

The main 3.0.0 change was removal of the `xlfg` Python CLI package. The repo is plugin-only — no `pip install`, no console-script entrypoints. Install exclusively via the Claude Code marketplace manifest.

What changed:
- `xlfg/` directory (13 Python source files, ~4700 LoC) deleted entirely
- `pyproject.toml` deleted — no Python packaging surface remains
- `/xlfg-audit` and `/xlfg-init` plugin commands deleted (CLI wrappers)
- `docs/benchmarking.md` and `evals/intent/` deleted (CLI-fed fixtures)
- "prefer the local xlfg helper CLI" wording removed from all commands and phase skills
- `tests/test_xlfg.py` pruned to ~20 plugin shape tests; `test_versions_are_synced` rewritten to read from plugin.json only
- Historical version tracking at 3.0.0 moved from Python package files to the Claude/Cursor plugin manifests; 3.2.0 adds the Codex manifest to that sync set

Why this matters:
- Single authoritative install path; no dual-track CLI-or-manual ambiguity in run flow
- Phase skills own the scaffold, recall, and verify work directly via Read/Grep/Glob/Write
- Test suite is leaner and honest; no CLI-import coupling

If you continue from here:
- Do **not** recreate a Python package or pyproject.toml. The plugin-only architecture is intentional.
- Historical note: before Codex support, behavior changes bumped both `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`. Current changes must also bump `.codex-plugin/plugin.json` per the 3.2.0 section above.
- Keep the plugin skills, agents, hooks, and scripts consistent across updates.

## Previous state (2.9.0) — for reference

2.8.2 closes two residual risks from the 2.8.1 follow-up work:

- `phase-gate.mjs` now exits 0 immediately on empty stdin. Before this change, the hook would read the cwd-relative `.xlfg/phase-state.json` even when no stop-event payload was present, which caused `test_allows_on_empty_stdin` to flake inside an active /xlfg run and, more importantly, let the hook block legitimate non-xlfg invocations that happened to share the cwd.
- The phase-gate fix (2.8.2) and xlfg-debug alias (2.8.1) remain in effect.

2.8.1 added the `/xlfg-debug` short alias. 2.8.1 also introduced `xlfg-ui-designer` (conditional plan-phase + verify-phase specialist for UI-related work).

The main 2.8.0 change (still in effect) is **hardening the conductor itself** — the 2.7.x arc hardened specialists, but the conductor could still silently drop later phases.

What changed:
- a Stop hook (`phase-gate.mjs`) now blocks the conductor from ending before all 8 phases complete
- `.xlfg/phase-state.json` tracks which phases have completed; the Stop hook reads this file to decide block/allow
- verify-fix and review-fix loopback cycles are now capped at 2 iterations to prevent unbounded context growth
- the Stop hook is registered in plugin `hooks.json` and conductor frontmatter
- audit module detects `conductor_stop_gate` as a new feature flag

Why this matters:
- production runs were sometimes dropping later phases (review, compound) because the model could stop at any time with no enforcement
- unbounded loopback cycles between verify and implement consumed context without advancing to later phases
- the phase-state file survives context compaction, giving the Stop hook a reliable source of truth

If you continue from here:
- preserve the **one public conductor + hidden phase skills + separated specialists** architecture
- do not flatten back into one monolithic prompt
- do not reintroduce duplicated intent docs
- keep conductor frontmatter, hooks, and scripts consistent across updates
- the phase-gate hook has a safety valve (max 3 blocks) — do not remove it or the model may hang when it genuinely cannot make progress


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.

## 2.7.3 note

- Production run found agents exhausting maxTurns: 8 on speculative reads, never writing artifacts. Root cause: bloated "Read first" lists (14 files), no turn budget guidance, and stopHookActive escape hatch letting agents bypass the guard.
- Fix: maxTurns raised to 12 for review + heavy-analysis agents. "Turn budget rule" added to all 26 specialists. Review agents get lean "Context sources" (3+3 files). stopHookActive escape removed. CONTEXT_DIGEST added to review-phase dispatch.
- If you continue from here: preserve the turn budget rule in all new agents, keep maxTurns proportional to workload, and always embed context digests in dispatch packets for read-heavy specialists.

## 2.8.0 note

- Stop hook (`phase-gate.mjs`) reads `.xlfg/phase-state.json` and blocks the conductor from stopping before all 8 phases complete. Safety valve: allows after 3 consecutive blocks or on `max_tokens`.
- Conductor now writes phase-state JSON after startup and updates it after each phase. `block_count` resets to 0 on each phase advance.
- Loopback cap: verify-fix and review-fix loops limited to 2 iterations. After that, escalate to user.
- Registered in plugin `hooks.json` (Stop section) and both conductor frontmatter files.

## 2.7.5 note

- A later drift had plugin specialists back at `maxTurns: 100` when bounded budgets were intended. This patch restores the bounded budgets and adds tests so that mismatch is easier to catch.
- Conductors and phase skills now say the quiet rule out loud: specialists are leaf workers, nested delegation is not allowed, and lean fan-out wins by default.
