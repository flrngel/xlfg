# Next agent context

## Current state (3.3.1)

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
