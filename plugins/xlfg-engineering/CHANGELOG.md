## 5.0.0

**Agent preamble + dispatch-rules extraction; cache-stable prefix; epic-default packets; decision-bearing CONTEXT_DIGEST.** A major refactor motivated by four pain points: (1) tasks divided per-atomic-task instead of per-epic, (2) artifacts too detailed with overlapping criteria, (3) sub-agent prompts both too specific and duplicating boilerplate the dispatch packet already carries, (4) too many read/writes slowing runs.

Research anchors: Anthropic, *How we built our multi-agent research system* (sizing by complexity; subagents need complete self-sufficient instructions; consolidate overlap); Anthropic, *Effective context engineering for AI agents* ("smallest set of high-signal tokens"; just-in-time context; system prompts at the right altitude); Anthropic, *Writing effective tools for AI agents* (overlapping tools distract agents); Anthropic, *Building effective agents* (start simple; add agentic complexity only when simpler fails); Cognition, *Don't Build Multi-Agents* (share full traces including decisions, not just facts; parallel divergent actions create bad merges); Anthropic, *Prompt caching* (stable prefixes cache).

### Changed

**Shared preamble (cache-stable prefix)**
- New `agents/_shared/agent-preamble.md` owns the single authoritative copy of: §1 compatibility note, §2 Execution contract, §3 Turn budget rule, §4 Tool failure recovery, §5 ARTIFACT_KIND guard, §6 Completion barrier, §7 Final response contract.
- All 27 specialist agent files shrunk to role-delta only (frontmatter, role identity, inputs/outputs, rules, handoff format). Each agent cites the preamble by relative path instead of duplicating ~70 lines of boilerplate. Net reduction: per-agent file size −60 to −70%.
- Prompt caching win: the preamble is identical across every dispatch, so the Anthropic prompt cache can amortize it. Prior 27-file-specific boilerplate broke caching entirely.

**Shared dispatch rules**
- New `agents/_shared/dispatch-rules.md` owns the single authoritative copy of: packet-size ladder, preseed rule, machine-readable packet headers, CONTEXT_DIGEST decisions+paths shape, OWNERSHIP_BOUNDARY contract, PRIOR_SIBLINGS contract, micro-packet budget, proof budget, compaction, dispatch discipline, resume-same-specialist rule.
- All 6 phase skills (intent/context/plan/implement/verify/review) replaced their duplicated ~40-line "Delegation packet rules" block with a pointer to `_shared/dispatch-rules.md` plus their phase-specific ownership boundaries.

**Packet-size ladder (new explicit tiers)**
- `trivial` → conductor inline, no specialist. `standard` → one specialist, one artifact, one decision slice (default). `epic` → one specialist owns a multi-surface slice under a single decision. `split` → truly unrelated surfaces, split before dispatch.
- `xlfg-task-divider` default is now **epic** (one packet per objective group `O1`, `O2`, ...) instead of per-atomic-task. Atomic sub-division only when surfaces are truly unrelated or genuinely independent/read-mostly. Rationale: Anthropic finds coding tasks have fewer parallelizable sub-problems than research; Cognition finds many atomic packets create parallel divergent decisions that conflict at merge.

**CONTEXT_DIGEST carries decisions + rationale + path refs**
- The digest now carries the chosen decision, its one-line rationale, the false-success trap, and file:line anchors — not just raw facts.
- Forbidden: "digest + re-read" (the specialist re-reading canonical files the digest already summarized). The digest is authoritative for decisions; specialists pull scoped file:line ranges on demand.

**Output template updated**
- `agents/_shared/output-template.md` documents the new packet-size ladder and the revised CONTEXT_DIGEST shape. Points at the preamble and dispatch-rules for rules that belong there.

**Tests updated for the new shape**
- `test_all_agents_have_completion_barrier_and_resume_rule` now checks the preamble for boilerplate strings + each agent references the preamble.
- `test_all_delegating_entrypoints_repeat_atomic_packet_contract` now accepts either inlined contract or a reference to `_shared/dispatch-rules.md`; the shared file must carry the canonical tokens.

### Deferred (explicit non-goals of this release)

- **Agent merges** (e.g., collapsing 3 context investigators into 1; folding `xlfg-test-readiness-checker` into `xlfg-test-strategist`) were scoped out because they require ~15–20 test-assertion rewrites for marginal gain over the core refactor. The "human routing test" from Anthropic's context-engineering guidance still applies and the merge set is tracked for a follow-up release.
- **Optional artifact collapse** (e.g., folding `diagnosis.md`, `flow-spec.md`, etc. into sections of `spec.md`) deferred for the same reason. Optional docs remain opt-in per `_shared/output-template.md` guidance.

### Migration

No breaking change for run consumers:
- Existing runs continue to work. Preamble and dispatch-rules files are new additions; they do not change the canonical artifact shape.
- New runs benefit from: cache-stable dispatch prefixes, fewer per-dispatch tokens, decision-bearing digests, and (when `xlfg-task-divider` routes tasks by objective group) fewer parallel divergent decisions.

## 4.6.0

**Micro-packet and proof-budget optimization pass.** Real run logs showed the
4.4/4.5 dedup fields were working, but the next bottleneck was self-inflicted:
dispatch packets could balloon into line-by-line coding recipes, task-level
`DONE_CHECK` commands could repeat full build/full-suite proof for every
sibling, and canonical run files could grow by reabsorbing full specialist
artifacts. 4.6.0 keeps the packet fields but makes them leaner.

### Changed

**Canonical packet discipline**
- `agents/_shared/output-template.md` adds v4.6.0 micro-packet rules: packets are
  contracts, not implementation recipes; aim for <=900 words; use file:line
  anchors instead of full code blocks; avoid dictating import placement,
  variable names, or line-by-line edits when scoped files contain the pattern.
- `/xlfg`, `/xlfg-debug`, and every delegating phase skill now repeat the
  micro-packet and artifact-compaction rules inline where conductors draft
  packets.

**Proof budget**
- Task packets now treat `DONE_CHECK` as the cheapest honest task-local proof.
  Broad builds, full suites, live acceptance, and repeated expensive checks
  belong to verify phase `fast_check` / `smoke_check` / `ship_check` unless the
  task is the final integration lane or touched shared type/schema/config
  surfaces that require broad proof immediately.
- `xlfg-task-divider`, `xlfg-test-strategist`, `xlfg-implement-phase`, and
  `xlfg-verify-phase` all carry the same split so planners do not accidentally
  make every implementer pay the ship-proof cost.
- `xlfg-verify-runner` runs each declared command once per verify invocation and
  retries only for classified harness/flaky failures.

**Artifact compaction**
- Conductors now promote only bounded facts from specialist artifacts into
  `spec.md`, `workboard.md`, `context.md`, `verification.md`, and summaries:
  status, verdict, changed files, command results, blockers, and next action.
  Full reports and long logs stay in the specialist artifacts.

**Scope safety**
- `xlfg-task-implementer` now explicitly forbids patching out-of-scope files
  just to make `DONE_CHECK` green. If a failure is caused by an out-of-scope
  file, fixture, test, hook, or dependency, it records the evidence and returns
  `BLOCKED` or `FAILED` unless the parent packet widens `FILE_SCOPE` and
  `OWNERSHIP_BOUNDARY`.
- Over-specified packet recipes are treated as non-normative when they conflict
  with local code patterns; behavior, constraints, and proof remain normative.

**Codex surface**
- `$xlfg` and `$xlfg-debug` now carry the same micro-packet, proof-budget, and
  artifact-compaction guidance.

**Tests**
- `tests/test_xlfg.py` adds v4.6.0 shape assertions for micro-packet
  compaction, proof-budget separation, and out-of-scope `DONE_CHECK` repair.
- `tests/test_codex_plugin.py` pins 4.6.0 and verifies the Codex public skills
  include micro-packet guidance.

**Manifests**
- `plugin.json` bumped to **4.6.0** across `.claude-plugin/`,
  `.cursor-plugin/`, `.codex-plugin/`, and `docs/xlfg/meta.json`.

### Migration

- **For users:** no breaking runtime change. New runs should spend fewer tokens
  on giant specialist prompts, repeat expensive proof less often, and keep
  canonical run files smaller.
- **For packet authors:** keep `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and
  `PRIOR_SIBLINGS`, but keep the digest factual and short. If the packet starts
  looking like a patch script, split or compact it before dispatch.

## 4.5.0

**Ownership-boundary dedup pass.** 4.4.0 stopped specialists from repeating reads and sibling findings with `CONTEXT_DIGEST` and `PRIOR_SIBLINGS`; 4.5.0 closes the next overlap class: adjacent specialists re-adjudicating each other's decisions. Every dispatch packet now carries an explicit `OWNERSHIP_BOUNDARY` that names what the lane owns, what it must not redo, and which artifacts it consumes as input truth.

### Changed

**Canonical packet shape**
- `agents/_shared/output-template.md` adds mandatory `OWNERSHIP_BOUNDARY` with `Own`, `Do not redo`, and `Consume` fields.
- `commands/xlfg.md` and every delegating phase skill (`intent`, `context`, `plan`, `implement`, `verify`, `review`, `debug`) now repeat the field in their packet examples and explain how it prevents adjacent-lane rework.

**Phase ownership rules**
- `context` separates repo mapping, harness profile, adjacent requirements, constraints, unknowns, env health, and external research.
- `plan` separates why, diagnosis, solution choice, flow spec, UI design, proof commands, readiness gate, task packets, and risk.
- `implement` separates source ownership, test ownership, and task-local checker verdicts.
- `verify` separates runner execution, reducer judgment, env classification, and UI DA conformance.
- `review` keeps each lens to net-new findings and requires "Already covered by verification" before findings.

**Specialist agents**
- All 27 specialist agents now honor `OWNERSHIP_BOUNDARY` in the Turn budget rule and use a `Covered elsewhere` pointer instead of repeating adjacent analysis.
- High-overlap agents gained explicit boundaries: `xlfg-task-implementer` vs `xlfg-test-implementer`, `xlfg-task-checker` vs verify, `xlfg-verify-runner` vs `xlfg-verify-reducer`, `xlfg-ui-designer` vs `xlfg-ux-reviewer`, and flow/spec/test/UI planning lanes.

**Codex surface**
- `$xlfg` and `$xlfg-debug` packet shapes now include `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and `PRIOR_SIBLINGS`.
- Codex phase references now describe the same lane-ownership splits so Codex runs do not regress to duplicate specialist work.

**Tests**
- `tests/test_xlfg.py` adds ownership-boundary coverage for delegating entrypoints, specialist agents, the canonical packet template, phase overlap rules, and high-risk agent-pair boundaries.
- `tests/test_codex_plugin.py` pins 4.5.0 and verifies the Codex skill packet shape includes the dedup fields.

**Manifests**
- `plugin.json` bumped to **4.5.0** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.

### Migration

- **For users:** no breaking runtime change. New runs get clearer specialist lane ownership and should spend fewer turns on duplicate reads, duplicate findings, and unnecessary cross-lane rework.
- **For specialist authors:** when adding or editing a delegating phase, write the ownership boundary before dispatching. If a lane needs to mention adjacent work, cite the owning artifact instead of copying its reasoning.

## 4.4.0

**Sub-agent dedup contract: `CONTEXT_DIGEST` + `PRIOR_SIBLINGS` are now mandatory in every dispatch packet.** Sub-agents in xlfg already communicate exclusively through files (preseeded artifact in, terminal-status reply out — never chat synthesis). The remaining waste was on the read side: each new specialist re-read ~10 canonical files because dispatch packets did not embed excerpts, and sibling specialists in the same phase lane re-derived overlapping findings because the packet did not list prior siblings. Only `xlfg-review-phase` had a `CONTEXT_DIGEST` rule; this release generalizes it across the conductor and all delegating phase skills.

### Why

Three observable redundancies in real `/xlfg` runs:

1. **Canonical re-reads.** Every specialist agent file lists "Input you will receive: spec.md, context.md, current-state.md, …" — and the specialist dutifully re-reads each one even when the conductor just synthesized them. Token cost compounds across 5–8 specialists per phase.
2. **Sibling overlap.** `xlfg-context-adjacent-investigator`, `xlfg-context-constraints-investigator`, and `xlfg-context-unknowns-investigator` all read the same `context.md` and produce overlapping findings (assumptions vs. unknowns vs. acceptance criteria addenda). Same shape with `xlfg-root-cause-analyst` → `xlfg-solution-architect` and with multi-lens reviewers.
3. **Implementer→checker re-derivation.** `xlfg-task-checker` re-reads the same source files `xlfg-task-implementer` just touched instead of consuming the implementer's report.

The fix is two new mandatory packet fields, not new agents:

- `CONTEXT_DIGEST` — the conductor inlines the canonical excerpts the specialist actually needs. Specialists treat it as authoritative and only re-read source files when the digest is explicitly insufficient.
- `PRIOR_SIBLINGS` — the conductor lists every artifact already produced **in the same phase lane** that overlaps the new specialist's surface. The new specialist skims listed siblings and explicitly skips covered ground.

Together they make sibling-to-sibling deduplication mechanical instead of accidental.

### Changed

**Canonical packet shape**
- `agents/_shared/output-template.md` — new `## Dispatch packet shape (canonical)` section. Defines `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` as mandatory packet fields with explicit `none` / `see PRIMARY_ARTIFACT preseed` escape hatches when truly empty. Single source of truth that every phase skill and agent now references.

**Conductor**
- `commands/xlfg.md` — `## Atomic packet format` extended with the two new lines and a one-paragraph reference to the canonical template.

**Phase skills** (every delegating phase skill now requires the same packet shape)
- `skills/xlfg-intent-phase/SKILL.md`
- `skills/xlfg-context-phase/SKILL.md`
- `skills/xlfg-plan-phase/SKILL.md`
- `skills/xlfg-implement-phase/SKILL.md`
- `skills/xlfg-verify-phase/SKILL.md`
- `skills/xlfg-review-phase/SKILL.md` — pre-existing `CONTEXT_DIGEST` block converted to canonical shape and joined by `PRIOR_SIBLINGS` (a second reviewer no longer re-flags findings the first reviewer already raised).
- `skills/xlfg-debug-phase/SKILL.md` — same packet rule applied to `/xlfg-debug`.

**Specialist agents** (all 27 files; one-line Turn budget rule extension)
- `agents/**/*.md` — Turn budget rule's "if the dispatch packet includes a context digest, use it instead of re-reading those files" expanded into two explicit rules: trust `CONTEXT_DIGEST` over re-reading canonical files, and skim `PRIOR_SIBLINGS` to skip covered ground. The dedup contract is now two-sided: conductor populates, specialist honors.

**Tests**
- `tests/test_xlfg.py` (+3): `test_all_delegating_entrypoints_require_context_digest_and_prior_siblings` covers the conductor + every phase skill; `test_specialist_agents_honor_context_digest_and_prior_siblings` covers all 27 agent files; `test_canonical_template_documents_dispatch_packet_shape` locks the shared template as the source of truth.

**Manifests**
- `plugin.json` bumped to **4.4.0** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.

### Migration

- **For users:** no breaking changes. Runs already in flight under 4.3.0 continue to work — packets that omit the new fields still dispatch successfully (the contract is enforced at the prompt level, not by a runtime gate). New runs under 4.4.0 produce smaller per-specialist context.
- **For specialist authors:** the agent's "Input you will receive" lists are now treated as a fallback. Prefer the dispatch packet's `CONTEXT_DIGEST` and `PRIOR_SIBLINGS` excerpts. Re-read source files only when the digest is explicitly insufficient.

## 4.3.0

**Speed-of-run optimization pass based on `/tmp/hey-xlfg-authors.md`.** Seven surgical fixes to specialist narrative, hook noise, and skill contracts. Net effect on a comparable future run: the author estimates ~40% reduction from fixing the top three alone; this release ships all seven.

### Why

A contributor's one-page memo after a slow Python run isolated the highest-ROI inefficiencies: the implementer agent prepending YAML frontmatter to `.py` / `.json` files and breaking collection; the Stop hook firing on every parked turn during long-running verify phases; and recall promoting a prior "fix class" without checking whether the diagnosed surface has moved. Each finding had a <10-line fix; shipping them together keeps the scope reviewable.

### Changed

**Specialist narrative**
- `agents/implementation/xlfg-task-implementer.md` — new `## ARTIFACT_KIND rule` section: when `PRIMARY_ARTIFACT` is non-markdown (or the packet declares `ARTIFACT_KIND: source-file|config-file|test-file`), never prepend YAML frontmatter. Status is reported via the `RETURN_CONTRACT` line only. Turn-budget rule branches on the same kind.
- `commands/xlfg.md` atomic packet format gains optional `ARTIFACT_KIND: planning-doc|source-file|config-file|test-file` header with explicit default (`planning-doc`) and preseed rule.

**Hook noise + concurrent-writer discipline**
- `scripts/phase-gate.mjs` — reads `in_progress_phase` from phase-state; exits 0 without writing when a long foreground phase legitimately parks the conversation. Read-modify-write cycle now documented as monotonic-for-`block_count`-only; never resets `completed`, `loopback_count`, or any conductor-written field.
- `commands/xlfg.md` phase-state contract — initial state adds `in_progress_phase: ""`; new conductor contract requires setting it before every phase Skill call and clearing it after the return.

**Recall staleness guard**
- `skills/xlfg-recall-phase/SKILL.md` — guardrail upgraded from advisory ("run `git log --since`") to mandatory with a normative `Git-recency guard` section. When promoting a prior fix class, conductors MUST record the git-log output in `memory-recall.md`; any commit in the window marks the carry-forward `HYPOTHESIS-ONLY` with a `Verify-before-use:` line.

**Renderer placeholder match**
- `scripts/render-workboard.mjs` — BEGIN marker match relaxed from exact-string (required script attribution) to prefix `<!-- BEGIN: rendered-phase-status`. A pre-seeded placeholder block is now replaced in place instead of leaving a duplicate `## Phase status` section on first render.

**Smoke-before-acceptance tier**
- `agents/planning/xlfg-test-strategist.md` — `ship_phase` enum extended with `acceptance`; new required `smoke_check` field when acceptance is declared; new `## ship_phase: acceptance tier` section describing the smoke-first contract.
- `skills/xlfg-verify-phase/SKILL.md` — new smoke-first rule: if any scenario declares `ship_phase: acceptance`, verify runs `smoke_check` first and stops on deterministic smoke failure without paying the full acceptance cost.

**Loopback arithmetic + review fast-fix**
- `commands/xlfg.md` — new `### loopback_count arithmetic` section formalizing which transitions count (`{verify|review} → implement`, verify→plan re-diagnosis) and which do not (plan repairs, `APPROVE-WITH-NOTES-FIXED`, harness FAILED retries).
- `skills/xlfg-review-phase/SKILL.md` — new `## Verdicts` section adds `APPROVE-WITH-NOTES-FIXED`: a <a few-line fix applied in-run with a re-run of the deterministic proof subset, recorded under "Fixed in-run" in `review-summary.md`. Does not consume a loopback.

**Current-state cap + `/xlfg-status`**
- `skills/xlfg-compound-phase/SKILL.md` — new `## current-state.md size cap` section enforcing ~200 words per run; overflow moves to `compound-summary.md`.
- `commands/xlfg-status.md` (new) — read-only slash command emitting `RUN_ID`, current phase, loopback count, latest artifact, verification verdict, and next action from `.xlfg/phase-state.json` plus the latest run dir. Safe mid-run; no file mutations. Useful after a stale `ScheduleWakeup` or context compaction.

**Tests**
- `tests/test_phase_gate.py` (+2): `test_phase_gate_in_progress_suppression` covers both branches (populated field suppress; empty field resumes normal write). `test_phase_gate_monotonic_for_block_count_only` verifies `loopback_count` and `completed` are preserved verbatim across a hook write.
- `tests/test_render_workboard.py` (+1): `test_begin_marker_prefix_match` renders over a placeholder BEGIN marker (no attribution) and asserts exactly one `## Phase status` heading and one BEGIN marker in the output.
- `tests/test_xlfg.py` (+8): shape assertions for each objective — implementer ARTIFACT_KIND branch, recall git-recency MUST, test-strategist smoke tier, verify-phase smoke-first, loopback arithmetic, `APPROVE-WITH-NOTES-FIXED` verdict, compound 200-word cap, `xlfg-status` command existence.

**Manifests**
- `plugin.json` bumped to **4.3.0** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.

### Migration

- **For users:** no breaking changes. New `/xlfg-status` slash command is read-only and optional. `ARTIFACT_KIND` is additive — existing packets without it continue to work (default: `planning-doc`, preserving current behavior for markdown artifacts; inferred kind for non-markdown).
- **For runs in progress:** the `in_progress_phase` field is optional. Runs started under 4.2.0 without the field continue to work; the hook treats missing/empty as "no phase running" and writes as before. New runs under 4.3.0 benefit from the noise suppression immediately.
- **For the acceptance tier:** adopting `ship_phase: acceptance` is opt-in. Existing `fast | smoke | e2e | manual` scenarios are unaffected.

## 4.2.0

**`/xlfg-audit` is now the per-run user post-mortem.** The harness self-check (manifests, frontmatter, word counts) moved to `scripts/audit-harness.mjs` and runs in CI on every PR. Phase boundaries are now timed: every `/xlfg` and `/xlfg-debug` run records a `phase-timings.jsonl` in its run dir, and `/xlfg-audit` reads it to produce a per-phase wall-time table plus concrete, data-driven suggestions for how the harness can be faster or leaner. The `flrngel/xlfg` submission flow is preserved — but now what gets submitted is real run data, not static manifest checks.

### Why

The previous `/xlfg-audit` was a category error. Every check was a deterministic file read (`jq .version`, `wc -w`, regex on frontmatter) wearing a slash-command costume. It needed no LLM and gave the user running it nothing — it existed only to phone home harness shape to upstream maintainers. The 4.1.1 path-anchor bug was exactly the kind of bug that doesn't happen when an actual script with a hardcoded `__dirname` is doing the work.

Meanwhile, the question users actually ask after a 45-minute `/xlfg` run is "what did this run do, and why was it slow?" — and the harness had no answer because it never recorded per-phase timings.

4.2.0 splits the two concerns:

- **Maintainer concern → script + CI.** `scripts/audit-harness.mjs` runs all 6 checks deterministically. Wired into `.github/workflows/ci.yml`. Exits 1 on any check fail, so PR review surfaces drift automatically.
- **User concern → slash command.** `/xlfg-audit` reads the latest run dir, computes per-phase wall time from `phase-timings.jsonl`, lists artifacts and ledger entries, and emits suggestions tied to the data (loopback count, slow-phase identification, oversized artifacts). Submission to `flrngel/xlfg` is preserved with the same redaction contract plus a new rule for run-slug content.

### Changed

- `plugins/xlfg-engineering/scripts/phase-tick.mjs` (new): writes `{run, phase, event, ts}` to `docs/xlfg/runs/<RUN_ID>/phase-timings.jsonl`. Best-effort: write failures exit 0 so the conductor is never blocked.
- `plugins/xlfg-engineering/scripts/post-mortem.mjs` (new): deterministic per-run report. Reads timings, run artifacts, and ledger entries; emits Markdown or JSON. Heuristic suggestions for slow phases, loopbacks, and oversized artifacts.
- `plugins/xlfg-engineering/scripts/audit-harness.mjs` (new): port of all 6 former audit checks (version sync, SDLC coverage, workflow load, Claude Code compat, Codex surface integrity, scaffold consistency). Deterministic. Stale-`Task`-token sweep tightened to inspect only the frontmatter `tools:` field, fixing two false positives on `## Task decomposition` headings in agent files.
- `plugins/xlfg-engineering/commands/xlfg-audit.md`: body completely rewritten as the per-run post-mortem orchestrator. Delegates to `scripts/post-mortem.mjs`, prints output, asks the user about submission, redacts, files into `flrngel/xlfg`. New redaction rule covers `RUN_ID` slug content (titles can carry product names).
- `plugins/xlfg-engineering/commands/xlfg.md` and `xlfg-debug.md`: each phase Skill call is now bracketed by two `phase-tick` invocations (start before, end after). Loopbacks emit fresh start/end pairs. Best-effort writes never block the conductor.
- `.github/workflows/ci.yml`: adds a Node 20 step that runs `node plugins/xlfg-engineering/scripts/audit-harness.mjs`. Failing audit fails CI.
- `docs/xlfg/meta.json`: `tool_version` synced to `4.2.0` (was stale at `2.7.1` and surfaced by the new audit-harness check 6).
- `plugin.json` manifests bumped to **4.2.0** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.
- `tests/test_phase_tick.py`, `tests/test_post_mortem.py`, `tests/test_audit_harness.py` (new): 13 new tests covering JSONL output, wall-time computation, loopback handling, exit codes, and the false-positive regression on the stale-`Task` sweep.
- `tests/test_xlfg.py`: replaced `test_xlfg_audit_anchors_plugin_paths_to_plugin_root` (no longer relevant — the audit body is now a thin orchestrator) with `test_xlfg_audit_is_per_run_post_mortem_not_harness_self_check`.
- `tests/test_codex_plugin.py`: version pins bumped to `4.2.0`.

### Migration

- **For users:** `/xlfg-audit` now reports on your latest run instead of the harness. If you ran `/xlfg` before installing 4.2.0, that run will say `n/a (no phase-timings.jsonl)` because timings only start being recorded from 4.2.0 onward. The next `/xlfg` you start will produce a fully timed post-mortem.
- **For maintainers:** the harness self-check now runs in CI automatically. To run it locally: `node plugins/xlfg-engineering/scripts/audit-harness.mjs`. JSON output is available with `--json` for tooling.
- **No breaking changes** for consumers of the slash command surface — `/xlfg-audit` is still the right command to run after a long run; the report it produces is just useful now.

## 4.1.1

**`/xlfg-audit` now anchors every check to `$CLAUDE_PLUGIN_ROOT` instead of guessing.** Previously the command said "read the plugin manifests" without naming a path, so when run from a target repo the dispatched agents scanned the user's cwd and either found nothing or conflated user-project files with plugin files. The audit was effectively broken outside the xlfg source repo.

### Why

Every other entrypoint (`commands/xlfg.md`, `hooks/hooks.json`) uses `${CLAUDE_PLUGIN_ROOT}/...` to locate plugin-internal scripts. The audit was the lone exception. With no anchor, the `Bash`/`Grep`/`Glob` calls inside the audit defaulted to the current working directory, which is the user's project — exactly the thing the audit is *not* supposed to inspect (per the command's own opening line: "Measure the harness itself, not the user's project."). In the xlfg source repo it accidentally worked because `plugins/xlfg-engineering/` happens to live in cwd; in any installed-plugin context it failed.

### Changed

- `plugins/xlfg-engineering/commands/xlfg-audit.md`:
  - added a `## Locate the plugin (run this FIRST)` preamble that resolves `PLUGIN="${CLAUDE_PLUGIN_ROOT:-}"` with a source-repo fallback (`./plugins/xlfg-engineering` if the `.claude-plugin/` dir is present in cwd) and aborts with a `fail:` line if neither resolves
  - prefixed every path in checks 1–5 with `$PLUGIN/` (manifests, phase skills, public commands, agents, codex skills)
  - clarified that check 6 (scaffold self-consistency) is the **only** check that reads from cwd, and downgraded its missing-file outcome from `fail` to `warn: no scaffold in cwd` because invoking the audit outside an xlfg-initialized project is legitimate
  - explicit instruction that any delegated Agent prompt must include the absolute `$PLUGIN` path and the directive "do not look outside this directory"
- `plugin.json` manifests bumped to **4.1.1** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.
- `tests/test_codex_plugin.py` version assertions bumped to `4.1.1`.
- `tests/test_xlfg.py` adds `test_xlfg_audit_anchors_plugin_paths_to_plugin_root` to lock the anchor pattern so the next refactor cannot silently drop it.

### Migration

No user-visible behavior change for the audit's output — same checks, same scoring, same submission flow. The fix is invisible when you happen to be in the xlfg source repo (the fallback catches it) and visible everywhere else as "the audit now actually inspects the installed plugin instead of your project."

## 4.1.0

**`/xlfg-audit` is now a feedback loop to the xlfg maintainers.** The optional `--issue` flag is gone. After every audit, the command asks the user whether to submit the redacted report to `flrngel/xlfg` so the maintainers can act on real-world audits. There is no per-user target override — the target is always `flrngel/xlfg`.

### Why

v3.3.1 mis-framed the feature: it shipped `--issue` as an opt-in that defaulted to the user's OWN repo, which is useless for upstream feedback. The point of `/xlfg-audit` is not to help the user running it (they get no new capability from auditing xlfg itself) — it's to let maintainers see how the harness behaves on real repos. Sending the issue into the user's own repo breaks that loop. Requiring the user to know the flag buries the feedback path.

### Changed

- `plugins/xlfg-engineering/commands/xlfg-audit.md`:
  - removed `argument-hint` frontmatter; the command takes no arguments
  - removed the `## Arguments` section (no `--issue`, no `--issue <owner>/<repo>`)
  - added a short header explaining the command's purpose (upstream feedback, not user tooling)
  - renamed `## GitHub issue filing (only when --issue is requested)` → `## Feedback submission (after every audit)` with a single interactive flow: print report → ask `Submit this redacted audit to the xlfg maintainers at flrngel/xlfg so they can improve the harness? (y/n)` → run redaction + `gh issue create --repo flrngel/xlfg` on `y`, stop on `n`
  - hardcoded `--repo flrngel/xlfg` in the `gh issue create` invocation; removed the `gh repo view --json nameWithOwner` runtime resolution
  - added a non-interactive bail-out (if no stdin, skip submission silently)
- Redaction contract (`xlfg-audit.md:132-144`) is unchanged — same seven rules, same abort-on-token-leak behavior.
- `plugin.json` manifests bumped to **4.1.0** across `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`.
- `tests/test_codex_plugin.py` version assertions bumped to `4.1.0`.

### Migration

- If you were invoking `/xlfg-audit --issue`: drop the flag. The command will now prompt for submission every time.
- If you were invoking `/xlfg-audit --issue <owner>/<repo>`: that path is gone. The target is always `flrngel/xlfg`. If you want an audit report into your own repo, copy it out of chat manually.
- Non-interactive runs (e.g., CI pipelines) get the chat report only — submission is skipped when there's no stdin for the prompt.

Bumped to **4.1.0** (minor) — removing a public flag and changing the default flow materially changes the public entry model, but the flag is 4 days old and the command's purpose is clarified, not broken. No breaking changes to `/xlfg` or `/xlfg-debug`.

## 4.0.0

**Breaking — removed the `standalone/` pack.** For users who followed README's "Manual standalone install" path, switch to the plugin marketplace (`/plugin install xlfg-engineering`) or clone the repo and `cp -r plugins/xlfg-engineering/ ~/.claude/plugins/xlfg-engineering/` for offline installs.

### Why

The pack had silently drifted from `plugins/xlfg-engineering/`:

- 3 minor versions behind by the start of this run (`standalone/` last touched at v3.1.0 / v2.8.1 while the plugin was at v3.3.1).
- Missing `hooks.json` wiring, so `phase-gate.mjs` and `subagent-stop-guard.mjs` were silently disabled on copy-paste installs — the exact proof gates `/xlfg` relies on.
- Missing `/xlfg-audit` and `/xlfg-init` (restored in v3.3.0 plugin-side).
- Specialist `effort: medium` vs. plugin's `effort: high` — a behavioral drift, not cosmetic.
- The original "plugin loader unavailable" rationale is obsolete now that Claude Code's plugin marketplace is generally available.

Keeping parity had failed repeatedly (v3.1.0's "standalone pack now includes `.claude/agents/` parity" bullet was itself a drift-patch that went stale again). Auto-generating from the plugin was rejected as unneeded complexity for a user base whose existence is unverified in 2026.

### Removed

- `standalone/` directory and everything under it.
- `scripts/lint_plugin.py` standalone-parity check (four-line block at the old line 178-181).
- 5 test methods that only asserted parity: `test_standalone_agent_pack_matches_plugin_agents`, `test_standalone_stop_guard_matches_plugin`, `test_standalone_renderer_matches_plugin`, `test_standalone_script_exists`, and `test_ui_designer_agent_exists_in_both_packs_with_dual_mode` (replaced by a plugin-only existence check).
- Standalone-path arms inside 9 additional test methods across `tests/test_xlfg.py` and `tests/test_xlfg_debug.py`.
- The "Standalone parity" audit check (previously check 5) in `plugins/xlfg-engineering/commands/xlfg-audit.md`; downstream sections renumbered (old 6 → 5, old 7 → 6). The `parity_ok` headline score is gone.
- Active-policy standalone references in `README.md`, `docs/architecture.md`, `AGENTS.md`, `NEXT_AGENT_CONTEXT.md`, `plugins/xlfg-engineering/README.md`, and `plugins/xlfg-engineering/CLAUDE.md`.

### Fixed (drive-by)

- `plugins/xlfg-engineering/commands/xlfg-audit.md` and `plugins/xlfg-engineering/commands/xlfg-init.md` had ~21 combined `plugins/xlfg-engineering/...` literal path references that had been tripping the linter's `BROKEN_PLUGIN_PATH_RE` rule since v3.3.0 (commit 41693af restored both commands with the broken paths). Rewrote each to drop the repo-relative prefix (e.g., `plugins/xlfg-engineering/agents/` → `agents/`). The audit logic still targets the same files; only the wording changed. `python3 scripts/lint_plugin.py` now exits 0 on a clean checkout.

### Preserved (not rewritten)

- `plugins/xlfg-engineering/CHANGELOG.md` history — every prior release entry that mentioned "both packs" stays as record.
- `docs/xlfg/knowledge/decision-log.md`, `docs/xlfg/knowledge/ledger.jsonl`, `docs/xlfg/migrations/**`, `docs/xlfg/runs/**`.

Bumped to **4.0.0** (major) — withdrawing a publicly-documented install path is the same breaking-change shape as v3.0.0's Python CLI removal.

## 3.3.1

`/xlfg-audit` upgrade — lead with a per-check summary table, and optionally file the report as a GitHub issue with personal-info redaction baked in. Pure-prompt change; no new runtime.

- `plugins/xlfg-engineering/commands/xlfg-audit.md` now prints a **per-check summary table first** (one row per check 1–7 with `status`, `score`, `note`). Headline scores, top load drivers, compatibility gaps, improvements, and verdict follow the table. This inverts the old order so a reader can see pass/fail at a glance before scrolling into detail.
- `xlfg-audit` accepts `--issue` (file into the current repo via `gh repo view`) or `--issue <owner>/<repo>` (file into a named repo). Preconditions: `gh auth status` succeeds, we are in a git repo or a `<owner>/<repo>` was given. If a precondition fails, the command warns once and still prints the chat report — it never prompts, never retries.
- Added a **redaction contract** that runs before any `gh issue create` call: strip `/Users/<name>/…`, `/home/<name>/…`, `C:\\Users\\<name>\\…` paths (inside-repo paths collapse to repo-relative; outside-repo paths get `<redacted>`), replace emails with `<email-redacted>`, drop git identity / hostname / `Signed-off-by` / `Co-authored-by` lines, and **abort** the `gh` call if any token-shape string (`ghp_`, `github_pat_`, `xox[baprs]-`, `sk-`, `AIza`, `AKIA`, `-----BEGIN`) appears — the audit body should never contain secrets, so a hit means something leaked.
- Issue shape: title `xlfg-audit report — v<plugin_version> — <YYYY-MM-DD>`, body is the redacted Markdown report (summary table on top), labels `audit` and `xlfg` (added non-fatal — `gh` fails silently if the target repo doesn't have them).
- `argument-hint` updated from `[no arguments]` to `[--issue | --issue <owner/repo>]`; command `description` now mentions the optional GitHub issue filing.
- `tests/test_codex_plugin.py` version assertions bumped to `3.3.1`.

Bumped to **3.3.1** (patch) — public entry model unchanged; the default `/xlfg-audit` invocation stays local-only.

## 3.3.0

Restore `/xlfg-init` and `/xlfg-audit` — both were deleted in v3.0.0 as part of the Python CLI removal. That deletion was over-broad: `xlfg-init.md` was always a pure-prompt markdown command with zero CLI calls, and `xlfg-audit.md` was salvageable as a deterministic harness self-audit without the Python scoring pipeline. Living docs (`plugins/xlfg-engineering/CLAUDE.md:49`, `docs/planning-autonomy-2026-refresh.md:113`) still named both as maintenance commands, so the deletion broke its own contract.

- Added `plugins/xlfg-engineering/commands/xlfg-init.md`. Idempotent scaffold repair. Creates missing directories (`docs/xlfg/knowledge/`, `docs/xlfg/knowledge/agent-memory/`, `docs/xlfg/migrations/`, `docs/xlfg/runs/`, `.xlfg/runs/`), creates missing durable knowledge files without overwriting, and ensures `.gitignore` carries the canonical four-line xlfg ignore set. Includes a drift warning that flags blanket `docs/xlfg/` ignore lines (they block new knowledge additions from `git add`).
- Added `plugins/xlfg-engineering/commands/xlfg-audit.md`. Deterministic rewrite: every check is a concrete file read or frontmatter inspection Claude can perform, not a Python call. Covers version sync across the three manifests, SDLC phase-skill coverage, workflow load (word count), Claude Code compatibility (command + phase-skill frontmatter, forbidden-token sweep, specialist `maxTurns` + leaf-worker tool check), standalone parity, Codex surface integrity, and scaffold self-consistency. Output format: comparison table, top load drivers, top compatibility gaps, best cost-to-confidence improvements, verdict.
- Fixed `.gitignore` drift. Removed the blanket `docs/xlfg/` line (added 2026-04-13 in `dadb737`) that silently blocked new durable knowledge files from staging. Canonical ignore set is now `.xlfg/`, `docs/xlfg/runs/*`, and the two `!docs/xlfg/runs/...` unignores. Already-tracked knowledge files were unaffected; the blanket only hit untracked paths.
- `plugins/xlfg-engineering/CLAUDE.md` safety section refers to `/xlfg-init` (was stale `/xlfg:init`) and adds a line for `/xlfg-audit`.
- `tests/test_codex_plugin.py` version assertions updated to `3.3.0`.

Bumped to **3.3.0** (minor) — restoring two public commands is more than a patch but does not change the default run flow. `/xlfg` and `/xlfg-debug` behavior is unchanged.

## 3.2.2

Bug fix — every `/xlfg` or `/xlfg-debug` run on a project that had previously
invoked xlfg hit `File has not been read yet. Read it first before writing to
it.` on the very first `Write(.xlfg/phase-state.json)`. Claude Code's Write
tool refuses to overwrite an existing file the current session has not read,
so the stale `phase-state.json` left by the prior run was effectively a
poison pill for the next conductor.

- `plugins/xlfg-engineering/commands/xlfg.md` and `xlfg-debug.md` startup
  step 1 now tells the conductor to `rm -f .xlfg/phase-state.json` in the
  same shell step that creates the scaffold directories, and explains why.
- Standalone mirrors (`standalone/.claude/skills/xlfg/SKILL.md` and
  `standalone/.claude/skills/xlfg-debug/SKILL.md`) got the same update.
- Codex conductors (`plugins/xlfg-engineering/codex/skills/xlfg/SKILL.md`
  and `xlfg-debug/SKILL.md`) got the same `rm -f` guidance so Codex runs
  also always start from a fresh phase-state file.
- `tests/test_xlfg.py` asserts the `rm -f .xlfg/phase-state.json` instruction
  is present in both Claude entrypoints so this regression can't silently
  come back.

Bumped to **3.2.2** (patch) — public entry model unchanged.

## 3.2.1

Dependency removal — Context7 MCP was wired into the plugin manifests but no
runtime code or specialist lane actually called into it, so the server was
pure install-surface risk. Removing it.

- Deleted `plugins/xlfg-engineering/.mcp.json`.
- Removed the `mcpServers` block from `.claude-plugin/plugin.json` and the
  `mcpServers` key from `.codex-plugin/plugin.json`.
- `plugins/xlfg-engineering/agents/planning/xlfg-researcher.md` and its
  standalone mirror no longer advertise Context7; they use WebSearch +
  WebFetch for external facts.
- `tests/test_codex_plugin.py` no longer asserts on `mcpServers` and pins all
  three manifests at 3.2.1.
- README and NEXT_AGENT_CONTEXT.md no longer reference Context7.

Bumped to **3.2.1** (patch) — public entry model unchanged.

## 3.2.0

Codex support release - adds a first-class Codex plugin surface beside the
existing Claude Code and Cursor manifests without changing the Claude entry
model.

- Added `plugins/xlfg-engineering/.codex-plugin/plugin.json` with Codex
  install metadata, `skills: "./codex/skills/"`, and `mcpServers: "./.mcp.json"`.
- Added repo-scoped Codex marketplace metadata at
  `.agents/plugins/marketplace.json`, pointing Codex at
  `./plugins/xlfg-engineering`.
- Added two public Codex skills under `plugins/xlfg-engineering/codex/skills/`:
  `$xlfg` for the full SDLC run and `$xlfg-debug` for diagnosis-only runs.
  These are separate from the Claude hidden phase skills because Codex requires
  `name` and `description` frontmatter on every public skill.
- Added shared Codex phase references under
  `plugins/xlfg-engineering/codex/references/phases/`, preserving the
  recall -> intent -> context -> plan -> implement -> verify -> review ->
  compound run and the recall -> intent -> context -> debug diagnosis run.
- Added a Codex model/effort policy that forbids treating Claude specialist
  `model` / `effort` frontmatter as Codex configuration. Codex defaults to the
  active session model/effort and built-in roles by lane shape unless explicit
  Codex custom agents are configured.
- Codex v1 uses prompt-level phase barriers and file-backed state rather than
  trying to clone Claude plugin lifecycle hooks. Hard hook parity can be
  considered later as a separate `.codex/` install pack.
- Added `tests/test_codex_plugin.py` and updated version sync coverage so the
  Claude, Cursor, and Codex manifests must agree on 3.2.0.

Bumped to **3.2.0** (minor) because this adds a new public distribution
surface while preserving the existing Claude Code and Cursor surfaces.

## 3.1.1

CI fix — `scripts/lint_plugin.py` treated every markdown file under
`plugins/xlfg-engineering/agents/**` as an agent, so the new shared reference
at `agents/_shared/output-template.md` (added in 3.1.0) failed the
frontmatter check. The linter and the standalone-parity counter now skip the
`_shared/` directory, since it holds cross-agent reference material rather
than agent definitions. No runtime behavior changes; this is a tooling-only
patch. Plugin manifests are also resynced — 3.1.0 shipped without updating
`plugin.json` / `.cursor-plugin/plugin.json`, so 3.1.1 rolls them forward
alongside the lint fix.

## 3.1.0

Inter-agent communication cleanup — removes dual-write status, surfaces a
canonical ledger writer, gates two redundant specialist re-runs, and makes the
Claude Code task pane track xlfg's file-based phase list.

### A — Kill structural duplication inside each artifact

- **A1. Single canonical `status:` location.** Every xlfg artifact now carries
  exactly one status marker, inside a YAML frontmatter block. The bare
  `Status: DONE | BLOCKED | FAILED` line that used to sit above the frontmatter
  is removed from all 27 agent output templates in both packs. `subagent-stop-guard.mjs`
  parses YAML frontmatter first and falls back to the legacy bare-Status line
  only for artifacts produced before this release.
- **A2. Shared output-template reference.** `plugins/xlfg-engineering/agents/_shared/output-template.md`
  (mirrored to standalone) is the single authoritative description of artifact
  frontmatter, preseed shape, and the specialist's final-chat contract. Per-agent
  files describe only their agent-specific sections.

### C — Remove cross-agent content overlap

- **C1. Context-phase: gate `xlfg-repo-mapper`.** The `always run` directive is
  replaced with "run unless `memory-recall.md` already grep-cites `file:line`
  coverage of every objective in `spec.md`." When skipped, the conductor
  appends a one-line rationale to `context.md`. Prevents recall + repo-mapper
  from both enumerating the same surface.
- **C2. Verify-phase: gate `xlfg-ui-designer` re-fire.** The UI-designer
  verify-phase lane now requires task-checker to have left at least one DA id
  unresolved, or to have marked a DA `fail`, or to have not run. When every DA
  is already `pass` in the implement-phase checker reports, the verify lane is
  skipped with a one-line rationale in `verification.md`.

### D — Normalize phase-state writes

- **D1. `workboard.md` phase-status is rendered, not hand-written.**
  `plugins/xlfg-engineering/scripts/render-workboard.mjs` (mirrored to
  `standalone/.claude/hooks/xlfg-render-workboard.mjs`) re-renders the
  `## Phase status` block from `.xlfg/phase-state.json` after each phase
  completes. Rendered region is bounded by HTML comment markers so the rest of
  `workboard.md` (task tables, blockers, next-action) remains human-authored.
  Every phase skill's "Update workboard.md" instruction now explicitly excludes
  the phase-status table.
- **D2. Harness TaskCreate bridge.** `/xlfg` startup now emits eight synthetic
  `TaskCreate` calls (one per phase, subject `xlfg: <phase>`) and calls
  `TaskUpdate` as each phase completes. Silences the Claude Code task-pane nag
  without turning `workboard.md` into a second source of truth. `TaskCreate`,
  `TaskUpdate`, and `TaskList` are added to the `/xlfg` command's `allowed-tools`
  frontmatter in both packs.

### E — Canonical ledger schema + single writer

- **E1. `docs/xlfg/knowledge/ledger-schema.md`.** Declares required fields
  (`ts`, `run`, `type`, `version`, `summary`), the `type` enum, the tag
  allow-list, and the ISO 8601 `Z`-suffixed timestamp rule. Existing 4-event
  `ledger.jsonl` uses legacy `date`/`event` keys — the writer keeps history
  intact but rejects new writes in the legacy shape.
- **E2. `plugins/xlfg-engineering/scripts/ledger-append.mjs`.** The single
  writer. Validates against the schema and appends one JSON line. Rejects
  unknown fields, out-of-enum types, bad semver, disallowed tags, and malformed
  timestamps. `ledger.md` now references the schema and the writer instead of
  documenting its own shape.

### Tests

- `tests/test_subagent_stop_guard.py` gains `test_allows_done_when_artifact_has_yaml_frontmatter_status`,
  `test_blocks_when_yaml_status_still_in_progress`, and
  `test_standalone_stop_guard_matches_plugin`.
- `tests/test_ledger_append.py` covers schema presence, well-formed dry-run,
  and every validator rejection path.
- `tests/test_render_workboard.py` covers no-op on absent state, dry-run,
  idempotent re-render preserving human-authored content, missing-`run_id`
  failure, and plugin↔standalone byte-identity.
- Updated `test_review_agents_write_artifacts_under_reviews_dir`,
  `test_all_agents_have_completion_barrier_and_resume_rule`,
  `test_all_agents_have_turn_budget_rule`,
  `test_all_delegating_entrypoints_repeat_atomic_packet_contract`, and
  `test_xlfg_debug_phase_requires_scientific_debugging_and_forbids_edits` to
  assert the new YAML frontmatter strings.
- Relaxed the `" Task"` substring guard in
  `test_main_xlfg_entrypoints_are_self_contained_and_batch_phase_driven` to
  reject only the stale standalone `Task` tool name, not the new
  `TaskCreate` / `TaskUpdate` / `TaskList` harness tools.

Total: 51 tests (was 35). All green.

### Risks accepted

- The stop-guard accepts both YAML-frontmatter status and the legacy bare
  `Status:` first line. This is deliberate backward compatibility for artifacts
  produced before 3.1.0; removing the legacy branch is a future breaking change
  that will need a separate bump.
- The workboard renderer only rewrites the region between its own markers.
  Pre-3.1.0 `workboard.md` files without markers get the rendered block
  prepended on first run. Legacy phase-status prose elsewhere in those files is
  not cleaned up automatically.

### Intentionally not in this release

- Phase B from the plan (CONTEXT_DIGEST per phase + shared delegation-rules
  doc) — deferred by the user.
- O1 scale-tier redesign (XS/S/M/L, SKIPPED terminal state) — out of scope for
  communication-surface dedup; belongs in its own RFC.
- Specialist "lite" variants (N13) and cost observability (S9) — separate
  tracks that do not block this release.

Bumped to **3.1.0** (minor) because this changes the canonical artifact shape
and the authoritative writer for `ledger.jsonl`, while remaining backward
compatible on read for existing artifacts and events.

## 3.0.0

- **Breaking**: Removed the `xlfg` Python CLI package (`xlfg/` directory, ~4700 LoC) and `pyproject.toml` entirely. The Python console-script entry point (`xlfg init`, `xlfg start`, `xlfg audit`, `xlfg recall`, `xlfg verify`, `xlfg eval-intent`, `xlfg doctor`, `xlfg detect`, `xlfg status`) no longer exists. The plugin is now installed exclusively via the Claude Code marketplace manifest — no `pip install` required or supported.
- Removed `/xlfg-audit` and `/xlfg-init` plugin commands (direct CLI wrappers with no standalone function after CLI removal).
- Stripped "prefer the local xlfg helper CLI when available" wording from `commands/xlfg.md`, `commands/xlfg-debug.md`, `skills/xlfg-recall-phase/SKILL.md`, `skills/xlfg-verify-phase/SKILL.md`, and `skills/xlfg-recall/SKILL.md` (plugin + standalone mirrors). Phase skills now do equivalent work directly with Read/Grep/Glob/Write tools.
- Deleted orphaned CLI artifacts: `docs/benchmarking.md` (entirely about `xlfg audit` / `xlfg eval-intent`), `evals/intent/` directory (fixtures only consumed by `xlfg eval-intent`).
- Pruned `tests/test_xlfg.py` to remove the ~20 test functions that imported `xlfg.*` modules; ~20 plugin/standalone shape tests are preserved. Rewrote `test_versions_are_synced_across_package_and_plugin_manifests` to read versions from both `plugin.json` manifests instead of `xlfg.__version__`.
- Updated version tracking: `xlfg/__init__.py` and `pyproject.toml` are deleted; canonical version now lives in `plugins/xlfg-engineering/.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` only. Updated `CLAUDE.md` versioning checklist accordingly.
- Updated `README.md` to remove the "Local helper CLI" section and the pip install example. Plugin-only install remains the single supported path.
- Bumped to **3.0.0** (major, breaking) because removing a public console-script entry point is a breaking change for any user who installed the Python package.

## 2.9.0

- Raised every specialist agent's `maxTurns` to **150** in both the plugin pack (27 agents) and the standalone pack (27 agents). The cap is a generous safety ceiling, not a target — most lanes still finish in far fewer turns. Prompt-side write-first / leaf-worker / atomic-packet rules now carry the forcing-function load that the small numeric bound previously shared.
- Updated the audit predicate (`xlfg/audit.py:_short_turn_budget`) and the test assertion (`tests/test_xlfg.py`) to assert the new bound (`<= 150`). The predicate's *meaning* is unchanged — coverage remains; only the numeric bound rose. The fallback recommendation text in `audit.py` stays generic ("cap turn budgets aggressively") so a future drift to unbounded values is still flagged.
- Rewrote `docs/xlfg/knowledge/current-state.md` and the lead text of `plugins/xlfg-engineering/README.md` so durable framing matches: leaf workers under a generous safety ceiling, with prompt-side rules carrying the forcing function, instead of "short turn budgets (`maxTurns ≤ 12`)".
- Added the first real entry to `docs/xlfg/knowledge/decision-log.md` — captures the 2.7.3 → 2.7.4 → 2.7.5 → 2.9.0 history, the rationale for treating 150 as a ceiling, and the explicit rejected shortcuts (delete the audit predicate; bump only the plugin pack; patch instead of minor).
- Bumped to **2.9.0** (minor, not patch) because reversing the v2.7.5 bounded-budget design contract changes a load-bearing rule, not a numeric tweak.
- Risks accepted (per the `/xlfg-debug` predecessor run `docs/xlfg/runs/20260414-073242-maxturns-decision/`): a stuck specialist looping on speculative reads will appear hung longer before failing; mitigation lives in the prompt-side rules + SubagentStop guard, not in the cap.

## 2.8.2

- Fixed `phase-gate.mjs` (plugin + standalone) to exit 0 immediately on empty stdin instead of reading the cwd-relative `.xlfg/phase-state.json`. Prevents `test_allows_on_empty_stdin` from flaking inside an active /xlfg run and, more importantly, stops the hook from blocking legitimate non-xlfg invocations that happen to share the cwd.
- Added a scoped diagnostic in `xlfg verify`: when a planned `python -m unittest` / `unittest discover` command uses pytest-style `-k "not ..."` negation and exits 5 (NO TESTS RAN), the helper now appends a one-line hint to `contract_issues` explaining that unittest's `-k` is substring-match only. No change to pass/fail semantics; pytest commands with the same filter are never annotated.
- Added `xlfg-ui-designer` specialist agent (conditional plan-phase + verify-phase dispatch for UI-related work) — carried from 2.8.1 follow-up work.

## 2.8.1

- Registered `/xlfg-debug` as a short alias for the plugin command via `name: xlfg-debug` frontmatter, matching the `/xlfg` alias pattern so users can run `/xlfg-debug` without the `xlfg-engineering:` prefix.

## 2.8.0

- Added a Stop hook (`phase-gate.mjs`) on the main conductor that blocks the pipeline from ending before all 8 phases complete.
- Added phase-state tracking (`.xlfg/phase-state.json`) so the Stop hook and conductor know which phases have completed; survives context compaction.
- Capped verify-fix and review-fix loopback cycles at 2 iterations to prevent unbounded context growth; exceeding the cap escalates to the user.
- Registered the Stop hook in both plugin `hooks.json` and standalone/plugin conductor frontmatter.
- Added `conductor_stop_gate` feature detection to the audit module.

## 2.7.5

- Restored bounded specialist turn budgets in the plugin agent pack to match the standalone pack, so phase-critical lanes are foregrounded and short-lived again.
- Declared specialists to be leaf workers in the conductor and all delegating phase skills; nested subagent fan-out is now explicitly forbidden.
- Tightened fan-out guidance so context, planning, verification, and review stay sequential or lean by default, with review capped at one standard lens and two deep lenses.
- Clarified that waiting on a specialist is valid only when a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT` exist.
- Added audit and test coverage for short turn budgets, leaf-worker specialist tools, atomic packet headers across delegating entrypoints, and lean review fan-out.

## 2.7.3

- Fixed sub-agent turn-budget starvation: raised maxTurns from 8 to 12 for review and heavy-analysis planning agents, and to 10 for test-implementer and verify-reducer.
- Replaced the bloated "Read first" imperative lists in review agents with lean "Context sources" blocks, cutting speculative reads from 14 to 3 core files.
- Added a "Turn budget rule" section to every specialist's execution contract, enforcing write-first behavior and prohibiting speculative file reads.
- Removed the stopHookActive escape hatch from the SubagentStop guard so agents cannot bypass artifact completion after a single block.
- Added CONTEXT_DIGEST to the review-phase dispatch protocol so conductors embed pre-digested context instead of expecting reviewers to re-read everything.

## 2.7.2

- Added a plugin-level `SubagentStop` guard that blocks xlfg specialists from stopping on progress chatter or missing artifacts, using a bundled hook script instead of prompt text alone.
- Tightened the conductor and phase skills around artifact-first atomic packets: preseed the lane artifact, pass machine-readable `PRIMARY_ARTIFACT` / `FILE_SCOPE` / `DONE_CHECK` headers, and default planning lanes to sequential dispatch unless packets are truly independent.
- Hardened every specialist with explicit tool-error recovery rules so directory-read failures, oversized-file reads, and similar nonfatal errors are repaired in-lane instead of being surfaced as premature chat replies.
- Added tests and audit checks for the stop guard, packet header discipline, and plugin hook wiring.

## 2.7.1

- Hardened specialist completion with an explicit completion barrier: progress-only returns are not accepted as done.
- Added atomic task packets and the `xlfg-task-divider` planner so delegation uses one mission, one artifact, and one honest done check.
- Updated main and phase orchestration to resume the same specialist once before accepting failure or repairing the lane.

# Changelog

## 2.6.0

- Hardened specialist agents with clearer expert personas, explicit tool allowlists, proactive delegation descriptions, and `background: false` for phase-critical work.
- Updated the main `/xlfg` conductor and phase skills to treat specialists as lane owners whose artifacts should drive synthesis, not optional advisors.
- Added explicit artifact-writing review lanes under `docs/xlfg/runs/<run>/reviews/` so architecture, security, performance, and UX review can no longer vanish into summary-only subagent replies.
- Added standalone `.claude/agents/` parity for the standalone skill pack.
- Extended audit, lint, docs, and tests to score and enforce subagent hardening, foreground execution, review artifacts, and standalone agent parity.
- Kept the intent-contract improvements from 2.5.x intact while strengthening the next weak layer in the workflow.

## 2.4.0

- Restored the intended architecture: `/xlfg` now batches separated hidden phase skills instead of flattening the whole workflow into one monolithic prompt.
- Added hidden phase skills for recall, context, planning, implementation, verification, review, and compounding in both the plugin and standalone packs.
- Kept exactly one public plugin entrypoint (`/xlfg-engineering:xlfg`) and one public standalone entrypoint (`/xlfg`).
- Switched the entrypoints to current Claude Code tool names, using `Skill` orchestration plus `WebSearch` / `WebFetch` instead of the stale `Task` wording.
- Updated linting, audit rules, and tests to catch missing phase skills, stale tool names, and loss of batch-skill orchestration.
- Updated docs and handoff notes so future revisions preserve the public-entrypoint + hidden-phase-skills model.

## 2.3.0

- Fixed the broken `/xlfg` entrypoint introduced by 2.2.0.
- Removed the colliding plugin `command + skill` pair named `xlfg`.
- Removed the repo-relative command shim that pointed Claude at `plugins/xlfg-engineering/skills/xlfg/SKILL.md`.
- Made `/xlfg-engineering:xlfg` self-contained so the command itself executes the full SDLC workflow.
- Hid support skills from the slash menu so the main entrypoint is clearer.
- Kept the standalone `.claude/skills/xlfg/` pack as the canonical short `/xlfg` install.
- Updated linting, audit rules, and tests to catch entrypoint collisions and repo-relative plugin path references.

## 2.2.0

- Collapsed duplicated planning state into a lean six-file core. `spec.md` is now the single source of truth for request truth, why, harness choice, solution, task map, and proof summary.
- Added a first-class standalone `.claude/skills/xlfg/` pack so users can get direct `/xlfg` without plugin namespaces.
- Added `allowed-tools`, `effort`, and a narrow `ExitPlanMode` auto-approval hook to reduce internal workflow friction.
- Added `xlfg audit` plus `docs/benchmarking.md` to score workflow load, SDLC coverage, and Claude Code compatibility.
- Routed cheap/read-only helper agents to Haiku.

## 2.1.0

- Reworked `/xlfg:plan` to be why-first and progressively load optional agents.
- Reworked `/xlfg:implement` to use harness-profile budgets and maintain the workboard / proof map.
- Added a more explicit research lane, lean artifact model, and updated tests.
