# xlfg-engineering

`xlfg` is an autonomous, proof-first SDLC harness for Claude Code and Codex.

Version 5.1.0 ports the plugin's runtime helpers from Node to Python 3. The 7 `.mjs` scripts that powered hooks, phase timing, ledger writes, workboard rendering, audit, and post-mortem are now Python (`phase_gate.py`, `subagent_stop_guard.py`, `phase_tick.py`, `ledger_append.py`, `render_workboard.py`, `audit_harness.py`, `post_mortem.py`). CLI contracts and hook behavior are preserved exactly; the port unifies the plugin on a single runtime so CI, tests, and automation share one language. Node is no longer a runtime dependency — `python3` is.

Version 5.0.0 is a major dedup + cache-stable-prefix refactor. Two new shared files own the duplicated boilerplate and delegation rules: `agents/_shared/agent-preamble.md` holds the 7 boilerplate sections every specialist obeyed (compatibility, execution contract, turn budget, tool failure recovery, ARTIFACT_KIND, completion barrier, final response contract), and `agents/_shared/dispatch-rules.md` holds the packet contract every phase skill repeated. All 27 specialist agent files shrunk to role-delta only — each references the preamble instead of carrying ~70 lines of identical boilerplate. All 6 phase skills replaced their ~40-line duplicated "Delegation packet rules" block with a pointer. The shared preamble now acts as a **cache-stable prompt prefix** the Anthropic prompt cache can amortize across every dispatch, which prior 27-file-specific boilerplate broke entirely. New packet-size ladder (`trivial`/`standard`/`epic`/`split`) makes **epic the default** task-divider tier — one packet per objective group instead of per atomic task, matching Anthropic's finding that coding tasks have fewer parallelizable sub-problems than research, and Cognition's finding that many atomic packets create parallel divergent decisions that conflict at merge. `CONTEXT_DIGEST` now carries decisions + rationale + path refs (not just raw facts) so specialists build on the decision instead of re-deriving it; digest + re-read is forbidden. Research anchors: Anthropic's multi-agent research, effective context engineering, writing effective tools, building effective agents, prompt caching; Cognition's *Don't Build Multi-Agents*.

Version 4.6.0 adds a micro-packet and proof-budget pass for faster delegated runs. Specialist packets now have to stay contracts rather than line-by-line coding recipes: short scoped context, file/evidence anchors, constraints, and the proof signal. Task `DONE_CHECK` guidance now favors the cheapest honest task-local check, leaving full builds, full suites, live acceptance, and repeated expensive proof to verify-phase `fast_check` / `smoke_check` / `ship_check` unless the current task really touches shared integration surfaces. Conductors also compact specialist artifacts before updating canonical run files, carrying forward status, verdict, changed files, command results, blockers, and next action instead of pasting full reports back into `spec.md` or `workboard.md`. `xlfg-task-implementer` now explicitly refuses to patch out-of-scope files just to make a task check green.

Version 4.5.0 adds explicit specialist ownership boundaries to every delegated lane. Dispatch packets now require `OWNERSHIP_BOUNDARY` alongside `CONTEXT_DIGEST` and `PRIOR_SIBLINGS`, so the conductor states what a specialist owns, what it must not redo, and which artifacts it consumes. Phase skills now document the risky handoffs (flow vs test proof, source vs tests, runner vs reducer, UI verification vs UX review), all 27 specialist agents cite adjacent artifacts instead of repeating them, and the Codex `$xlfg` / `$xlfg-debug` surface carries the same packet shape.

Version 4.3.0 ships seven speed-of-run optimizations isolated by a contributor memo after a slow production run. The highest-impact fixes: the `xlfg-task-implementer` no longer prepends YAML frontmatter to non-markdown artifacts (new `ARTIFACT_KIND` packet header; inferred from extension when absent), so source and config files no longer break at parse time; the Stop hook's `phase-gate.mjs` reads a new `in_progress_phase` field and exits silently when a long foreground phase is legitimately parked waiting on a background task, eliminating the noisy per-turn block-count churn during verify; and `xlfg-recall-phase` now enforces a `git log --since=<baseline-date>` check before promoting a prior fix class as carry-forward, marking the rule `HYPOTHESIS-ONLY` when the diagnosed surface has moved. Smaller improvements: `render-workboard.mjs` handles pre-seeded placeholder blocks without duplicating the `## Phase status` section; `xlfg-test-strategist` gains a `ship_phase: acceptance` tier with a required `smoke_check` that verify-phase runs first (stop on deterministic smoke failure instead of paying the full acceptance cost); the conductor documents explicit `loopback_count` arithmetic and a new `APPROVE-WITH-NOTES-FIXED` review verdict for <a few-line inline fixes that don't consume a loopback; `xlfg-compound-phase` caps `current-state.md` at ~200 words per run; and a new read-only `/xlfg-status` slash command emits a 5–8 line run summary for orientation after stale wakeups or context compactions.

Version 4.2.0 splits the audit surface in two. `/xlfg-audit` is now the **per-run user post-mortem** — it reads the latest `/xlfg` or `/xlfg-debug` run from `docs/xlfg/runs/<RUN_ID>/`, computes per-phase wall time from a new `phase-timings.jsonl` (recorded automatically by the conductor), and emits a phase-breakdown table plus concrete suggestions ("phase X took Yh because Z ran twice; consider splitting the lane"). The harness self-check (manifests, frontmatter, word counts, forbidden tokens) moved to `scripts/audit-harness.mjs` and now runs in CI on every PR. The `flrngel/xlfg` upstream submission flow is preserved, but GitHub filing uses a separate project-free efficiency report with run-shape metrics only: phase timings, loopbacks, artifact counts, byte totals, and generic harness feedback. As a side effect, the stale-`Task` token sweep was tightened to inspect only frontmatter `tools:` fields, fixing two false positives on legitimate `## Task decomposition` headings.

Version 4.1.1 fixes `/xlfg-audit` so every check is anchored to `$CLAUDE_PLUGIN_ROOT` (with a fallback for the xlfg source repo). Before this fix, the audit had no path anchor and the dispatched agents scanned the user's cwd instead of the installed plugin — meaning the audit either inspected the wrong files or conflated user-project state with plugin state. Only check 6 (scaffold self-consistency) still reads from cwd; that's the only check that's *supposed* to look at the user's project. Output, scoring, and the `flrngel/xlfg` submission flow from 4.1.0 are unchanged.

Version 4.1.0 makes `/xlfg-audit` a feedback loop to the xlfg maintainers. The command takes no arguments: run it, see the per-check summary table and report in chat, then answer `y` when asked `Submit this redacted audit to the xlfg maintainers at flrngel/xlfg so they can improve the harness?`. On `y` the redacted report is filed as a GitHub issue in `flrngel/xlfg` via `gh issue create --repo flrngel/xlfg`; on `n` the run ends. The target is always `flrngel/xlfg` — there is no per-user override, because the command exists for upstream feedback, not user tooling. The redaction contract from 3.3.1 (home paths, emails, git identity, hostnames, signed-off / co-authored lines; abort on any token-shape string) still runs before filing.

Version 3.3.1 upgraded `/xlfg-audit`'s output order (per-check summary table first) and introduced the optional `--issue` flag. The flag is removed in 4.1.0; the summary-table-first output is retained.

Version 3.2.2 fixes a startup regression where every repeat `/xlfg` or `/xlfg-debug` run on a project errored with `File has not been read yet. Read it first before writing to it.` on the first `Write(.xlfg/phase-state.json)`. Conductors now clear any stale `phase-state.json` left by the previous run in the same shell step that syncs the scaffold directories, so the fresh initial Write always succeeds. All three conductor surfaces (Claude plugin, Codex `$xlfg`, Codex `$xlfg-debug`) got the guidance.

Version 3.2.0 adds first-class Codex support. Codex installs through
`.codex-plugin/plugin.json` and the repo marketplace at
`.agents/plugins/marketplace.json`, exposing `$xlfg` and `$xlfg-debug` as
public Codex skills backed by Codex-specific phase references. The existing
Claude Code `/xlfg` and `/xlfg-debug` entrypoints are unchanged.

Version 3.1.1 is a tooling-only patch: the plugin frontmatter linter now skips `agents/_shared/` (which holds cross-agent reference material like `output-template.md`, not agent definitions), so CI no longer fails on the shared template introduced in 3.1.0. Plugin manifests are also resynced to match the shipped version.

Version 3.1.0 tightens inter-agent communication: artifacts carry exactly one canonical `status:` field inside YAML frontmatter (replacing the dual `Status:` + `status:` write), `workboard.md`'s phase-status block is rendered from `.xlfg/phase-state.json` instead of hand-written by each phase, the Claude Code task pane now mirrors xlfg's phase list via a startup `TaskCreate` bridge, and `ledger.jsonl` gets a canonical schema (`docs/xlfg/knowledge/ledger-schema.md`) with a single validating writer (`scripts/ledger-append.mjs`). Two redundant specialist lanes are gated: context-phase skips `xlfg-repo-mapper` when `memory-recall.md` already grep-cites the surface, and verify-phase skips `xlfg-ui-designer` when implement-phase task-checker already proved every DA.

Version 3.0.0 removed the `xlfg` Python CLI package entirely. Install via the plugin marketplace only — no Python package installation needed or supported.

- `/xlfg` and `/xlfg-debug` are the public entrypoints, each **batching hidden phase skills**
- the plugin commands keep short aliases (`/xlfg`, `/xlfg-debug`) via `name:` frontmatter, while the namespaced forms remain `/xlfg-engineering:xlfg` and `/xlfg-engineering:xlfg-debug`
- the batch now includes a mandatory **intent phase** before context gathering and planning
- `spec.md` is now the only active home for the **intent contract** and objective groups
- bundled / messy requests are split into stable objective groups (`O1`, `O2`, ...)
- hidden phase skills still load **just in time**, matching Claude Code’s skills model while keeping context small
- every plugin specialist now has an explicit tool allowlist, proactive delegation description, foreground-only bias, stronger execution contract, and bounded turn budget
- review specialists now write lane artifacts under `reviews/`

## What is in this repo

1. A Claude Code plugin in `plugins/xlfg-engineering/`
2. A Codex plugin surface in `plugins/xlfg-engineering/.codex-plugin/` and `plugins/xlfg-engineering/codex/`
3. Research notes on recent subagent / harness hardening in `docs/subagent-hardening-2026.md`
4. A repo handoff file in `NEXT_AGENT_CONTEXT.md`


## Quick start

### Install via the plugin marketplace (recommended)

Inside Claude Code, add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@xlfg
```

Claude Code fetches the marketplace manifest from `.claude-plugin/marketplace.json`, resolves the plugin at `./plugins/xlfg-engineering`, and caches it under `~/.claude/plugins/`. Commands, skills, hooks, and specialist agents all activate together. After install:

- `/xlfg "what you want built"` — full SDLC run
- `/xlfg-debug "what is broken"` — diagnosis-only run (no source edits)

Both short forms are aliases of `/xlfg-engineering:xlfg` and `/xlfg-engineering:xlfg-debug`, registered via `name:` frontmatter on the plugin commands.

Update with `/plugin marketplace update xlfg`.

### Install in Codex

Codex reads the repo marketplace at `.agents/plugins/marketplace.json`, which
points to `./plugins/xlfg-engineering`. Restart Codex after checkout, open the
plugin directory, choose the local xlfg marketplace, and install
`xlfg-engineering`. After install:

- `$xlfg "what you want built"` - full SDLC run
- `$xlfg-debug "what is broken"` - diagnosis-only run (no source edits)

Codex uses skill invocation rather than the Claude Code slash-command aliases.

## Entry model

- `/xlfg` owns the whole SDLC run and loads hidden phase skills just in time: recall, intent, context, plan, implement, verify, review, compound.
- `/xlfg-debug` is the diagnosis-only sibling: recall → intent → context → debug. It finds the deep root cause and names the likely repair surface without touching source, tests, fixtures, migrations, or configs.
- `$xlfg` and `$xlfg-debug` are the Codex public skill forms. They use Codex-specific public skills plus shared phase references instead of the Claude command/hidden-skill surface.
- Neither command asks the user to run phase subcommands or internal skills.
- `spec.md` is the run card and single source of truth.
- Optional docs exist only when they change a decision or proof.
## License

MIT


## 2.7.5 note

- xlfg specialists are now documented and audited as **leaf workers**: no nested subagent delegation inside specialist lanes.
- Specialists now use bounded `maxTurns` budgets, so stalled lanes fail faster instead of looking hung.
- Review fan-out is leaner by default, and conductor guidance now says waiting is valid only when a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT` exist.


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.


## 2.7.2 hardening note

The plugin build now ships a plugin-level `SubagentStop` guard. In plugin mode, xlfg specialists are not allowed to stop on setup chatter or missing artifacts; the hook blocks the stop once and forces the specialist to finish the promised artifact or write an explicit `BLOCKED` / `FAILED` artifact instead.
