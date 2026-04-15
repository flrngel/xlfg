# xlfg ledger schema (v1)

`docs/xlfg/knowledge/ledger.jsonl` is the canonical append-only log of durable xlfg events.
This schema is the single source of truth for the shape of each line.

## One event per line

Each line MUST be a single self-contained JSON object. Do not pretty-print across lines. No trailing commas.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `ts` | string (ISO 8601) | Event timestamp, e.g. `2026-04-15T14:33:07Z`. Always UTC, always `Z`-suffixed, second precision minimum. |
| `run` | string | The originating `RUN_ID` (`<YYYYMMDD>-<HHMMSS>-<slug>`). |
| `type` | enum | See `type` enum below. |
| `version` | string (semver) | The plugin version at write time, e.g. `3.1.0`. |
| `summary` | string | One-sentence human-readable lesson. Keep ≤ 200 chars. |

## Type enum

Exactly one of:

- `feature` — a net-new capability landed
- `fix` — a defect repaired
- `pattern` — a durable reusable pattern extracted from a run
- `decision` — an explicit architectural or policy decision
- `incident` — a production or workflow failure worth remembering
- `memory.added` — a new memory lesson admitted
- `memory.superseded` — an existing memory replaced by a newer one
- `memory.invalidated` — a previously admitted memory marked wrong

Any other value is rejected by the writer.

## Optional fields

The writer accepts any of these when present. Unknown keys are rejected.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable identifier (e.g. `mem-20260306-01`). Monotonic per run is fine. |
| `tags` | string[] | Short lowercase tokens drawn from the allow-list below. |
| `stage` | enum | One of `recall`, `intent`, `context`, `plan`, `implement`, `verify`, `review`, `compound`, `debug`. |
| `role` | string | Specialist agent name that produced the lesson (e.g. `env-doctor`). |
| `evidence` | string[] | File paths inside the run (e.g. `docs/xlfg/runs/<run>/verification.md`). |
| `symptom` | string | What went wrong. |
| `root_cause` | string | The invariant or capability that was missing. |
| `action` | string | What the fix was. |
| `prevention` | string | What would stop this in the future. |
| `lex` | string | Free-text lexical surface for grep/retrieval. |
| `status` | enum | `active`, `superseded`, `invalidated`. Default `active`. |
| `supersedes` | string | For `memory.superseded`, the prior id. |

## Tag allow-list

Tags are optional. When present, each tag MUST come from this list (extend the list via a PR, not ad hoc):

```
plugin, skill, agent, harness, hook, stop-guard, phase-gate, ledger,
recall, intent, context, plan, implement, verify, review, compound, debug,
ui, backend, cli, test, docs, workflow, scale, dispatch, security
```

## Timestamp format

- Always UTC, suffixed `Z`.
- Use ISO 8601, at least second precision: `YYYY-MM-DDTHH:MM:SSZ`.
- Do NOT use the legacy `date` field (`YYYY-MM-DD`) — the writer migrates existing lines on read but rejects new writes that use `date`.

## Writer

All writes MUST go through `plugins/xlfg-engineering/scripts/ledger-append.mjs`.
The writer validates against this schema and appends a single JSON line.
Direct `echo >> ledger.jsonl` or inline edits are forbidden.

Usage:

```bash
node plugins/xlfg-engineering/scripts/ledger-append.mjs \
  --ts 2026-04-15T14:33:07Z \
  --run 20260415-143307-example \
  --type feature \
  --version 3.1.0 \
  --summary "One-sentence lesson"
```

Or pipe a JSON object on stdin:

```bash
echo '{"ts":"2026-04-15T14:33:07Z","run":"...","type":"feature","version":"3.1.0","summary":"..."}' \
  | node plugins/xlfg-engineering/scripts/ledger-append.mjs
```

The writer exits non-zero and prints the first validation failure when the input is invalid.

## Legacy events

Events written before v3.1.0 use `date` (not `ts`) and `event` (not `type`).
The writer does NOT rewrite history. Readers (recall, compound) should accept both shapes when reading
but only produce new-shape writes.
