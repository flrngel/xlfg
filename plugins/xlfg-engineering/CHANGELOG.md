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
