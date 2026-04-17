# xlfg agent output template (canonical)

This file is the single authoritative reference for **the shape of an xlfg
specialist's artifact**. It owns: the frontmatter the stop-guard reads, the
preseed shape the conductor writes, the dispatch packet shape the conductor
emits, and the final-status values every specialist promises to reach.

Companion files:

- `agents/_shared/agent-preamble.md` — the cache-stable preamble every
  specialist obeys (execution contract, turn budget, tool recovery,
  completion barrier, final response contract, ARTIFACT_KIND rule). Each
  agent file cites this preamble instead of duplicating the rules.
- `agents/_shared/dispatch-rules.md` — the phase-skill dispatch rules
  (packet-size ladder, preseed contract, CONTEXT_DIGEST decisions+paths
  shape, micro-packet budget, proof budget, compaction, resume rule).

Per-agent markdown files under `plugins/xlfg-engineering/agents/**` describe
the *content* each specialist produces. The *header shape* lives here.

## Canonical frontmatter

Every xlfg artifact begins with a YAML frontmatter block. Nothing precedes
the opening fence.

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

Before a specialist is dispatched, the conductor writes the
`PRIMARY_ARTIFACT` file as:

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

## Dispatch packet shape (canonical)

Sub-agents in xlfg communicate **through files only** — never chat. Each
specialist receives one packet, updates one preseeded artifact, and replies
with one final-status line. See `_shared/dispatch-rules.md` for the full
packet contract. Every dispatch packet MUST begin with:

```text
PRIMARY_ARTIFACT: <exact path>
ARTIFACT_KIND: planning-doc | source-file | config-file | test-file   # optional; default planning-doc
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

OWNERSHIP_BOUNDARY:
- Own: <the exact decision, artifact section, code surface, or proof step this lane owns>
- Do not redo: <adjacent lane decisions or artifacts to cite instead of re-deriving>
- Consume: <prior artifacts this lane must treat as input truth unless it finds explicit contradiction>

CONTEXT_DIGEST:
- <chosen decisions and their rationale from spec.md / context.md / verification.md>
- <load-bearing invariants, false-success traps, and scenario IDs the lane must respect>
- <path refs (file:line or file) for anything the specialist may want to pull on demand>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered>
```

- `OWNERSHIP_BOUNDARY`, `CONTEXT_DIGEST`, and `PRIOR_SIBLINGS` are all
  mandatory. Empty values are not allowed. They are how xlfg minimizes
  duplicate reads, duplicate findings, and duplicate file rewrites across
  siblings.
- `CONTEXT_DIGEST` carries **decisions + rationale + path refs**, not just
  raw facts. If the digest carries a decision, the specialist must not
  re-read the canonical source for the same decision.
- Use `CONTEXT_DIGEST: see PRIMARY_ARTIFACT preseed` and
  `PRIOR_SIBLINGS: none` only when literally true.

## Packet-size ladder (v5.0.0)

Scale the dispatch to the complexity of the work. Default is `standard`;
drop to `trivial` inline only when the conductor can finish without a
specialist; use `epic` when a single owner should carry a coherent
multi-surface slice.

- `trivial` — conductor inline, no specialist.
- `standard` — one specialist, one artifact, one coherent decision slice.
- `epic` — one specialist owns the slice; internal checklist lives inside
  the artifact.
- `split` — the surfaces are truly unrelated; split before dispatch.

Fragmenting a single decision into many atomic packets is the failure mode
to avoid: it creates parallel divergent decisions that conflict at merge.

## Micro-packet, proof-budget, and compaction rules

Dispatch packets are contracts, not implementation recipes.

- **Micro-packet budget:** aim ≤900 words per specialist packet; exceed
  ~1,200 only for genuinely high-risk work. No full files, no long
  before/after replacements, no line-by-line implementation scripts when
  the specialist can read the scoped files.
- **Proof budget:** `DONE_CHECK` is the cheapest honest task-local check.
  Broad `fast_check` / `smoke_check` / `ship_check` proof belongs in verify
  phase.
- **Artifact compaction:** after a specialist returns, promote only bounded
  facts into `spec.md` / `workboard.md`: terminal status, verdict, changed
  files, command names/results, first blocker, next action. Keep full
  reports and logs in the specialist artifact.

## Stop-guard contract

`plugins/xlfg-engineering/scripts/subagent-stop-guard.mjs` accepts either:

1. **Canonical** — a YAML frontmatter block at the top of the file whose
   body contains `status: DONE|BLOCKED|FAILED`.
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
