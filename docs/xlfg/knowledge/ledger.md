# xlfg memory ledger

`ledger.jsonl` is the machine-readable durable memory store for xlfg.

Why it exists:
- append-only audit trail for compounded lessons
- stage- and role-aligned retrieval without prompt bloat
- deterministic recall over exact text, tags, and filters

## Event shape

One JSON object per line. Preferred event types:
- `memory.added`
- `memory.superseded`
- `memory.invalidated`

Recommended fields for `memory.added`:

```json
{
  "id": "mem-20260306-01",
  "event": "memory.added",
  "created_at": "2026-03-06T12:34:56Z",
  "run_id": "20260306-123456-login-flow",
  "kind": "harness-rule",
  "stage": "verify",
  "role": "env-doctor",
  "title": "Reuse healthy dev server before starting another one",
  "summary": "Check the configured health endpoint first and reuse a healthy process.",
  "symptom": "`yarn dev` started twice and the second process failed with EADDRINUSE.",
  "root_cause": "The harness assumed no existing server and skipped readiness reuse.",
  "action": "Probe health, reuse if healthy, otherwise kill stale PID and restart once.",
  "prevention": "Never spawn a second dev server without a health check.",
  "lex": "yarn dev EADDRINUSE duplicate server port already in use healthcheck reuse",
  "tags": ["yarn", "dev-server", "port", "healthcheck"],
  "evidence": ["docs/xlfg/runs/<run-id>/verification.md"],
  "status": "active"
}
```

## Admission rules

Only append a memory event when the lesson is:
- concrete
- reusable
- evidenced by verification, review, or repeated real failure
- small enough to retrieve directly

Do not store vague summaries or speculative advice.
