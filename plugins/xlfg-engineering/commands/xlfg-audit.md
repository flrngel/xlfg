---
description: Audit the xlfg harness itself — version sync, SDLC coverage, workflow load, and Claude Code compatibility.
argument-hint: "[no arguments]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash
effort: medium
---

# xlfg audit

Measure the harness itself, not the user's project.

Unlike pre-3.0.0 audit, this command has no Python CLI behind it. Every check below is a concrete file read or frontmatter inspection Claude can perform deterministically. Run each check, collect the values, then produce the scores and tables described at the bottom.

## Checks

### 1. Version sync

Read the `version` field from all three plugin manifests:

- `plugins/xlfg-engineering/.claude-plugin/plugin.json`
- `plugins/xlfg-engineering/.cursor-plugin/plugin.json`
- `plugins/xlfg-engineering/.codex-plugin/plugin.json`

**Pass** if all three agree. Otherwise list which manifests disagree.

### 2. SDLC coverage

For each expected phase skill, check that the directory exists and contains a `SKILL.md`:

- `plugins/xlfg-engineering/skills/xlfg-recall-phase/`
- `plugins/xlfg-engineering/skills/xlfg-intent-phase/`
- `plugins/xlfg-engineering/skills/xlfg-context-phase/`
- `plugins/xlfg-engineering/skills/xlfg-plan-phase/`
- `plugins/xlfg-engineering/skills/xlfg-implement-phase/`
- `plugins/xlfg-engineering/skills/xlfg-verify-phase/`
- `plugins/xlfg-engineering/skills/xlfg-review-phase/`
- `plugins/xlfg-engineering/skills/xlfg-compound-phase/`
- `plugins/xlfg-engineering/skills/xlfg-debug-phase/`

`sdlc_coverage_score` = present / 9. Higher is better.

### 3. Workflow load

Compute word counts (via `wc -w`) for:

- `plugins/xlfg-engineering/commands/xlfg.md`
- `plugins/xlfg-engineering/commands/xlfg-debug.md`
- each `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`

Report each file's word count. `workflow_load_score` = total words across the above files. **Lower is better.** Also list the top 3 files by size (the top load drivers) so future tuning can target them.

### 4. Claude Code compatibility

For the two public commands (`commands/xlfg.md` and `commands/xlfg-debug.md`), confirm the frontmatter contains:

- `allowed-tools:`
- `effort:` (should be `high` for these)
- `disable-model-invocation: true`
- `hooks:` with a `PermissionRequest` → `ExitPlanMode` auto-allow

For every phase skill under `plugins/xlfg-engineering/skills/xlfg-*-phase/SKILL.md`, confirm the frontmatter contains:

- `user-invocable: false`
- no `name:` field (hidden skills must omit `name` per the Codex split)

Forbidden-token sweep across `plugins/xlfg-engineering/commands/**`, `plugins/xlfg-engineering/skills/**`, and `plugins/xlfg-engineering/agents/**`:

- stale `Task` tool name (check with word-boundary patterns `, Task,`, `, Task\n`, `, Task `, ` Task(`, ` Task `) — `TaskCreate`/`TaskUpdate`/`TaskList` are legitimate and must not trigger
- `query-contract.md` (forbidden reference to a deleted file)

For every specialist agent under `plugins/xlfg-engineering/agents/**/*.md` (excluding `_shared`):

- `maxTurns:` present and ≤ 150
- no `Agent` or `SendMessage` in its `tools:` list (leaf-worker rule)

`claude_code_compatibility_score` = pass count / total checks. Higher is better.

### 5. Standalone parity

Count `*.md` files under:

- `plugins/xlfg-engineering/agents/`
- `standalone/.claude/agents/`

`parity_ok` = counts are equal.

### 6. Codex surface integrity

Confirm exactly two public Codex skills:

- `plugins/xlfg-engineering/codex/skills/xlfg/SKILL.md`
- `plugins/xlfg-engineering/codex/skills/xlfg-debug/SKILL.md`

Confirm neither file contains any of these Claude-only tokens: `allowed-tools`, `Skill(`, `TaskCreate`, `TaskUpdate`, `TaskList`, `ExitPlanMode`, `PermissionRequest`, `CLAUDE_PLUGIN_ROOT`, `user-invocable`, `model:`, `effort:`, `sonnet`, `haiku`, `opus`.

### 7. Scaffold self-consistency

If the current repo has a `docs/xlfg/meta.json`, read `tool_version` and compare against the plugin.json version from check 1. Flag drift.

## Output format

Produce, in this order:

1. **Comparison table** — one row per check above with `pass / fail / score`.
2. **Top load drivers** — the top 3 largest files by word count from check 3.
3. **Top compatibility gaps** — any failed assertion from check 4, grouped by category (command frontmatter, phase skill frontmatter, forbidden tokens, specialist tools, `maxTurns`).
4. **Best cost-to-confidence improvements** — if any check failed, the one-line fix per failure. If everything passed, say so explicitly.
5. **Verdict** — one sentence on whether the current harness is lighter, parity, or heavier than a strong vanilla Claude Code path for small, medium, and large tasks. Base this on `workflow_load_score` and the density of specialist + hook machinery, not on vibes.

## Rules

- `workflow_load_score`: lower is better
- `sdlc_coverage_score`: higher is better (max 1.0)
- `claude_code_compatibility_score`: higher is better (max 1.0)
- `efficiency_index` = `sdlc_coverage_score × claude_code_compatibility_score / max(1, workflow_load_score / 10000)`. Report to 2 decimals.
- No network calls. Everything is a deterministic read of files already in the repo.
- If a check cannot be performed because a file is missing, report `fail` with the missing path, not `skip`.
