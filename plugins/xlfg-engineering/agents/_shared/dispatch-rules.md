# xlfg dispatch rules (canonical, shared across phase skills)

This file owns the delegation packet rules that apply every time a phase
skill dispatches a specialist. Each phase skill's SKILL.md cites this file
so the rules stay cache-stable across six phase skills and the main
conductor.

Research anchors: Anthropic, *How we built our multi-agent research system*
(detailed task descriptions, scale effort to complexity, consolidate
overlap); Anthropic, *Effective context engineering for AI agents*
(just-in-time context, smallest set of high-signal tokens); Anthropic,
*Best practices for using Claude Opus 4.7 with Claude Code* (prescriptive
plans beat model discretion; positive framing; fewer subagents by default);
Cognition, *Don't Build Multi-Agents* (share decisions, not just facts;
parallel divergent actions create bad merges).

**Style rule for this file:** Opus 4.7 reads bullets literally and weights
positive directives more than negations. Prefer `spawn X for each of {Y, Z}`
over `do not try to do this in one response`.

---

## 1. Packet-size ladder

Scale the dispatch to the complexity of the work. Default tier is
`standard`. Raise to `epic` when one owner should carry a coherent
multi-surface slice. Use `trivial` inline when the conductor can finish
without a specialist. Use `split` when surfaces are truly unrelated.

| Tier      | When to use                                                 | Shape                                                  |
|-----------|-------------------------------------------------------------|--------------------------------------------------------|
| trivial   | ≤3 file edits, 1 scenario, no cross-decision risk           | Conductor does it inline. No specialist.               |
| standard  | Default. One coherent decision slice / one objective group. | One specialist, one artifact, one DONE_CHECK.          |
| epic      | Spans multiple related surfaces under a single owner.       | One specialist owns the whole slice; internal checklist lives inside the artifact. |
| split     | Surfaces are truly unrelated (e.g. UI + migration + server).| Split BEFORE dispatch into standard or epic packets.   |

One owner per decision slice. A single decision owned by one specialist
merges cleanly; the same decision fragmented across N atomic packets
produces N parallel divergent decisions that conflict at merge.

## 2. Preseed the artifact before dispatch

The conductor creates the file named in `PRIMARY_ARTIFACT` with YAML
frontmatter `status: IN_PROGRESS`, the scoped mission, and a short
checklist so the specialist resumes a concrete work item. For non-markdown
`ARTIFACT_KIND` (source-file, config-file, test-file), leave the target
file as-is or create it in a valid empty shape for the target language;
lifecycle is reported via the `RETURN_CONTRACT` line only.

## 3. Machine-readable packet headers

Every specialist packet MUST begin with:

```text
PRIMARY_ARTIFACT: <exact path>
ARTIFACT_KIND: planning-doc | source-file | config-file | test-file   # optional; default planning-doc
FILE_SCOPE: <bounded files or paths>
DONE_CHECK: <single honest check or NONE>
RETURN_CONTRACT: DONE|BLOCKED|FAILED <artifact-path> only

OWNERSHIP_BOUNDARY:
- Own: <exact decision, artifact section, code surface, or proof step this lane owns>
- Do not redo: <adjacent lane decisions or artifacts to cite instead of re-deriving>
- Consume: <prior artifacts this lane must treat as input truth unless it finds explicit contradiction>

CONTEXT_DIGEST:
- <chosen decisions and their rationale from spec.md / context.md / verification.md>
- <load-bearing invariants, false-success traps, and scenario IDs the lane must respect>
- <path refs (file:line or file) for anything the specialist may want to pull on demand>

PRIOR_SIBLINGS:
- <path/to/sibling-artifact.md>: <one-line summary of what it already covered>
```

### 3a. CONTEXT_DIGEST contract

CONTEXT_DIGEST carries **decisions + rationale + path refs**, not raw
facts. Cognition's principle: a specialist that sees only facts re-decides;
a specialist that sees the upstream decision + why builds on it.

- Include the upstream decision (e.g. "solution choice: refactor middleware
  X, rejected: touch handler Y") and the one-line rationale.
- Include the false-success trap the lane must respect.
- Include file:line anchors for anything the lane may need on demand.
- Use `CONTEXT_DIGEST: see PRIMARY_ARTIFACT preseed` only when literally
  true.
- The digest is authoritative for decisions. Pull a scoped file:line range
  only when a specific detail is missing from the digest; never re-read
  a whole canonical file the digest already summarized.
- **Digest quality is load-bearing.** Opus 4.7's long-context retrieval
  (MRCR) regressed from 4.6, so the specialist cannot recover a lossy
  digest by scanning the 1M window. When the conductor drafts the digest,
  include every decision the lane needs to finish its mission.

### 3b. OWNERSHIP_BOUNDARY contract

Name the lane's exact ownership surface before the specialist starts.
Specialists write only sections this lane owns and cite prior artifacts
for adjacent facts. Re-adjudicate another lane's decision only when the
packet explicitly asks for a contradiction check. Empty values are not
allowed.

### 3c. PRIOR_SIBLINGS contract

List every artifact already produced **in the same phase lane** that
overlaps the new specialist's surface. Write `PRIOR_SIBLINGS: none` when
there are no priors. Specialists skim listed siblings and skip ground
already covered.

## 4. Micro-packet budget

- Keep specialist packets ≤900 words. Exceed ~1,200 only for genuinely
  high-risk work; otherwise split the lane or put the extra evidence in
  the preseeded artifact.
- Use file:line anchors plus the invariant the specialist must preserve.
  Full files, long JSX/code blocks, and exact before/after replacements
  belong in the artifact or the scoped source file, not the digest.
- State the intended behavior, constraints, forbidden shortcuts, and
  acceptance signal. Let the specialist infer the implementation from the
  scoped files.

## 5. Proof budget

- `DONE_CHECK` is the cheapest honest task-local check. Broad
  `fast_check` / `smoke_check` / `ship_check` belong to verify phase
  unless the task is the final integration lane or the changed surface
  specifically requires that broad command now.
- Cite a prior artifact when an expensive command already passed for the
  current diff and no owned files changed since; rerun only when the
  surface moved.

## 6. Artifact compaction

After a specialist returns, promote only bounded facts into `spec.md` /
`workboard.md`: terminal status, verdict, changed files, command
names/results, first blocker, next action. Keep full reports and logs in
the specialist artifact.

## 7. Dispatch discipline

- Only the phase conductor delegates. Specialists are leaf workers.
- Default dispatch order is sequential for artifact-producing planning,
  context, implement, and verify work. Parallelize only when packets are
  truly independent, small, and read-mostly (e.g. two independent
  read-mostly investigators in the same phase lane).
- Prefer fewer, larger packets for coding work. Anthropic's multi-agent
  research finds coding tasks have fewer parallelizable sub-problems than
  research; Opus 4.7 is tuned to be conservative about fan-out by default.
- When a specialist hits a nonfatal tool failure, resume the same lane.
  Use `LS` or `Glob` for directories; use `Grep` plus chunked `Read`
  windows for oversized files.

## 8. Resume-same-specialist before fallback

- Resume the **same specialist** with `SendMessage` using its returned
  agent ID when the lane returned early without the artifact or with only
  setup notes.
- Re-dispatch the exact same packet once when no agent ID is available.
- After a second incomplete return, mark the lane failed, re-split the
  task, or repair the gap yourself.
