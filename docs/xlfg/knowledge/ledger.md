# xlfg memory ledger

`ledger.jsonl` is the machine-readable durable memory store for xlfg.

Why it exists:
- append-only audit trail for compounded lessons
- stage- and role-aligned retrieval without prompt bloat
- deterministic recall over exact text, tags, and filters

## Schema

The authoritative shape for each line is defined in
[`ledger-schema.md`](ledger-schema.md). That file is the single source of truth
for required fields, the `type` enum, and the tag allow-list.

## Writer

All writes MUST go through `plugins/xlfg-engineering/scripts/ledger_append.py`.
Do not `echo >> ledger.jsonl` or hand-edit the file. The writer validates each
event and appends a single JSON line.

## Admission rules

Only append a memory event when the lesson is:
- concrete
- reusable
- evidenced by verification, review, or repeated real failure
- small enough to retrieve directly

Do not store vague summaries or speculative advice.
