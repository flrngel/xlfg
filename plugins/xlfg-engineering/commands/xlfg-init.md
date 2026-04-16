---
description: Manual bootstrap / repair for xlfg scaffolding in this repo.
argument-hint: "[no arguments]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write
effort: low
---

# xlfg init

Use this when you want to explicitly bootstrap or repair the xlfg scaffold.

`/xlfg` itself syncs scaffold quietly on every run. Use this command only when you intentionally want a manual bootstrap or repair — e.g. a fresh target repo, a repo where the scaffold was partially deleted, or to surface `.gitignore` drift.

## Safety + idempotency rules

- Do **not** overwrite existing files. If a file already exists, leave its content alone.
- Respect the tracking model:
  - `docs/xlfg/knowledge/` — tracked (durable product knowledge)
  - `docs/xlfg/runs/` — local-only (episodic run evidence)
  - `.xlfg/` — ephemeral (safe to delete)
- Do **not** modify unrelated docs, tooling, or source.
- Print every path you create and every line you add to `.gitignore`. Silent changes are forbidden.

## What to create or repair

### Directories

Tracked:
- `docs/xlfg/knowledge/`
- `docs/xlfg/knowledge/agent-memory/`
- `docs/xlfg/migrations/`

Local-only:
- `docs/xlfg/runs/`
- `.xlfg/runs/`

### Meta

Create `docs/xlfg/meta.json` if missing. A minimal valid shape:

```json
{
  "tool_version": "<plugin.json version>",
  "scaffold_schema_version": 12,
  "run_tracking": "local-only",
  "knowledge_tracking": "tracked",
  "workflow_entry": "recall-intent-context-plan-implement-verify-review-compound",
  "intent_contract": "spec-md-ssot"
}
```

Read `plugins/xlfg-engineering/.claude-plugin/plugin.json` to fill `tool_version`. If `meta.json` already exists, leave it alone.

### Gitignore (canonical set)

Ensure the repo root `.gitignore` contains **at minimum** these lines:

- `.xlfg/`
- `docs/xlfg/runs/*`
- `!docs/xlfg/runs/.gitkeep`
- `!docs/xlfg/runs/README.md`

This is the canonical set. If any line is missing, append it and print what you added.

**Drift check — flag but do not silently rewrite:**

If `.gitignore` contains a blanket `docs/xlfg/` or `docs/xlfg` line (no `/runs/*` suffix, no `!` negation), print a warning: that line ignores **all** of `docs/xlfg/`, which blocks new durable knowledge files (e.g. new role-memory docs) from being tracked. Already-tracked files keep working because `.gitignore` does not un-track. Recommend removing the blanket line unless the user explicitly intends to block new knowledge additions.

Ask the user before removing it.

### Durable knowledge files

Create these if missing (empty-but-valid skeleton; never overwrite existing content):

- `docs/xlfg/index.md`
- `docs/xlfg/knowledge/current-state.md`
- `docs/xlfg/knowledge/quality-bar.md`
- `docs/xlfg/knowledge/decision-log.md`
- `docs/xlfg/knowledge/patterns.md`
- `docs/xlfg/knowledge/testing.md`
- `docs/xlfg/knowledge/ux-flows.md`
- `docs/xlfg/knowledge/failure-memory.md`
- `docs/xlfg/knowledge/harness-rules.md`
- `docs/xlfg/knowledge/ledger.jsonl` (empty file)
- `docs/xlfg/knowledge/ledger.md`
- `docs/xlfg/knowledge/ledger-schema.md`
- `docs/xlfg/knowledge/queries.md`
- `docs/xlfg/knowledge/commands.json` (`{}` if missing)
- role memories under `docs/xlfg/knowledge/agent-memory/` (one file per specialist the repo uses; `README.md` explains the convention)

## Completion

After scaffolding is created or repaired:

1. Print a summary table of what was created, what was already present, and what was skipped.
2. Print the scaffold schema version from `docs/xlfg/meta.json`.
3. Print any `.gitignore` drift warnings.
4. Suggest running `/xlfg <your request>` to start a real run.

Do **not** stage or commit anything. The user decides what to `git add`.
