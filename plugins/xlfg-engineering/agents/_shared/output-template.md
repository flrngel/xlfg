# xlfg agent output template (canonical)

This file is the single authoritative reference for the **shape of an xlfg
specialist's artifact** — the frontmatter that the `subagent-stop-guard` reads,
the preseed shape the conductor writes, and the final-status values every
specialist promises to reach.

The per-agent markdown files under `plugins/xlfg-engineering/agents/**` describe
the *content* each specialist produces. The *header shape* is defined here so
all 27 agents stay in lockstep without any single one being the authority.

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

## Dispatch packet shape (canonical)

Sub-agents in xlfg communicate **through files only** — never chat. Each
specialist receives one packet, updates one preseeded artifact, and replies
with one final-status line. To stop sibling specialists from re-reading the
same canonical files and re-deriving the same findings, every dispatch packet
MUST begin with these machine-readable lines:

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
- <quoted excerpt or bullet from spec.md / context.md / verification.md / etc.>
- <only the fields the specialist actually needs to do its job>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered>
```

- `OWNERSHIP_BOUNDARY` is **mandatory**. The conductor names the lane's exact
  ownership surface before the specialist starts. Specialists must write only
  the sections this lane owns, cite prior artifacts for adjacent facts, and
  avoid re-adjudicating another lane's decision unless the packet explicitly
  asks for a contradiction check. If overlap is unavoidable, add a short
  "Covered elsewhere" pointer instead of repeating the same analysis.
- `CONTEXT_DIGEST` is **mandatory**. The conductor inlines the excerpts the
  specialist needs from canonical files (`spec.md`, `context.md`,
  `verification.md`, prior phase outputs). If the lane truly needs no extra
  context beyond the artifact preseed, write `CONTEXT_DIGEST: see PRIMARY_ARTIFACT preseed`.
  Specialists treat the digest as **authoritative** and must not re-read the
  source files unless the digest is explicitly insufficient.
- `PRIOR_SIBLINGS` is **mandatory**. The conductor lists every artifact
  already produced **in the same phase lane** that overlaps the new
  specialist's surface (e.g., `context/adjacent.md` when dispatching
  `xlfg-context-constraints-investigator`; `tasks/T1/implementer-report.md`
  when dispatching `xlfg-task-checker`). If there are no priors, write
  `PRIOR_SIBLINGS: none`. Specialists must skim listed siblings and
  explicitly skip ground already covered rather than re-deriving it.
- Empty values are not allowed. Both blocks are how xlfg minimizes duplicate
  reads, duplicate findings, and duplicate file rewrites across siblings.

## Micro-packet, proof-budget, and compaction rules (v4.6.0+)

Dispatch packets are contracts, not implementation recipes.

- **Micro-packet budget:** aim for <=900 words per specialist packet and exceed
  ~1,200 words only for genuinely high-risk work. If a packet wants more space,
  split the lane or put the extra evidence in the preseeded artifact. Do not paste
  full files, long JSX/code blocks, or exact before/after replacements into
  `CONTEXT_DIGEST`; use file:line anchors plus the invariant the specialist must
  preserve.
- **No code-script packets:** the mission may name the intended behavior,
  constraints, forbidden shortcuts, and acceptance signal. It should not dictate
  import placement, local variable names, or line-by-line edits when the
  specialist can infer the implementation from the scoped files.
- **Proof budget:** `DONE_CHECK` is the cheapest honest task-local check. Full
  builds, full suites, live acceptance, and repeated expensive checks belong in
  verify phase (`fast_check`, `smoke_check`, `ship_check`) unless the task is the
  final integration lane or the changed surface specifically requires that broad
  command now. If an expensive command already passed for the current diff and no
  owned files changed since, cite that artifact instead of rerunning it.
- **Artifact compaction:** after a specialist returns, promote only bounded facts
  into `spec.md` / `workboard.md`: terminal status, verdict, changed files,
  command names/results, first blocker, and next action. Keep full reports and
  logs in the specialist artifact; do not paste whole reports back into the run
  card.

## Stop-guard contract

`plugins/xlfg-engineering/scripts/subagent-stop-guard.mjs` accepts either:

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
