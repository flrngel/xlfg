# xlfg agent output template (canonical)

This file is the single authoritative reference for the **shape of an xlfg
specialist's artifact** — the frontmatter that the `subagent-stop-guard` reads,
the preseed shape the conductor writes, and the final-status values every
specialist promises to reach.

The per-agent markdown files under `.claude/agents/**` describe the *content*
each specialist produces. The *header shape* is defined here so all 27 agents
stay in lockstep without any single one being the authority.

## Canonical frontmatter

Every xlfg artifact begins with a YAML frontmatter block. Nothing precedes the
opening fence.

```markdown
---
status: DONE | BLOCKED | FAILED
---

# <Artifact title>

<agent-specific sections>
```

- `status` MUST be lowercase key, uppercase value.
- `status` MUST be exactly one of `DONE`, `BLOCKED`, `FAILED`, or (while the
  artifact is still being written) `IN_PROGRESS`.
- No bare `Status:` line above the fence. The dual-status shape that earlier
  versions produced is a bug — pick one place, and that place is the YAML
  frontmatter.

## Preseed (conductor writes this first)

Before a specialist is dispatched, the conductor writes the `PRIMARY_ARTIFACT`
file as:

```markdown
---
status: IN_PROGRESS
---

# <Artifact title>

<short mission + checklist>
```

The specialist updates the same file in place. On completion, the specialist
flips `status: IN_PROGRESS` → `status: DONE` (or `BLOCKED` / `FAILED`) and
fills in the agent-specific sections.

## Stop-guard contract

`.claude/hooks/xlfg-subagent-stop-guard.mjs` accepts either:

1. **Canonical** — a YAML frontmatter block at the top of the file whose body
   contains `status: DONE|BLOCKED|FAILED`.
2. **Legacy** — a bare first non-empty line matching
   `Status: DONE|BLOCKED|FAILED`.

New templates and new writes MUST use (1). The stop-guard keeps (2) for
backward compatibility with artifacts produced before v3.1.0 but new agent
templates do not prescribe it.

## Final chat reply

Once the artifact exists and reaches a terminal `status:` value, the
specialist's final chat turn MUST be exactly one line:

- `DONE <artifact-path>`
- `BLOCKED <artifact-path>`
- `FAILED <artifact-path>`

Any other final reply shape is invalid and the stop-guard will block it.
