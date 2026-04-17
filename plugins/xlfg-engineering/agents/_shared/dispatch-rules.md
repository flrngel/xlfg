# xlfg dispatch rules (canonical, shared across phase skills)

This file owns the **delegation packet rules** that apply every time a phase
skill dispatches a specialist. Each phase skill's SKILL.md cites this file
instead of inlining the rules, so the rules stay cache-stable across six phase
skills and the main conductor.

Research anchor: Anthropic, *How we built our multi-agent research system*
(detailed task descriptions, scale effort to complexity, consolidate overlap)
and *Effective context engineering for AI agents* (just-in-time context,
smallest set of high-signal tokens). Cognition, *Don't Build Multi-Agents*
(share context + decisions; avoid parallel divergent actions).

---

## 1. Packet-size ladder

Scale the dispatch to the complexity of the work. **Default is epic-level**;
drop to atomic only for truly independent sub-problems, and raise to trivial
inline only when the conductor can finish without a specialist.

| Tier      | When to use                                                 | Shape                                                  |
|-----------|-------------------------------------------------------------|--------------------------------------------------------|
| trivial   | ≤3 file edits, 1 scenario, no cross-decision risk           | Conductor does it inline. No specialist.               |
| standard  | Default. One coherent decision slice / one objective group. | One specialist, one artifact, one DONE_CHECK.          |
| epic      | Spans multiple related surfaces but a single owner.         | One specialist owns the whole slice; internal task list lives inside the artifact. |
| split     | Surfaces are truly unrelated (e.g. UI + migration + server).| Split BEFORE dispatch into standard or epic packets.   |

Do not fragment a single decision into many atomic packets — that creates
parallel divergent decisions that conflict at merge. Prefer one owner per
decision.

## 2. Preseed the artifact before dispatch

The conductor creates the file named in `PRIMARY_ARTIFACT` with YAML
frontmatter `status: IN_PROGRESS`, the scoped mission, and a short checklist
so the specialist resumes a concrete work item instead of starting from an
empty chat turn. For non-markdown `ARTIFACT_KIND` (source-file, config-file,
test-file), do not preseed with YAML — leave the target file as-is or create
it in a valid empty shape for the target language; lifecycle is reported via
the `RETURN_CONTRACT` line only.

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

### 3a. CONTEXT_DIGEST contract (v5.0.0)

CONTEXT_DIGEST carries **decisions + rationale + path refs**, not just facts.
This is the principle Cognition calls "share full traces, not just messages":
a specialist that sees only facts re-decides; a specialist that sees the
upstream decision + why builds on it.

- Include the upstream decision (e.g. "solution choice: refactor middleware X,
  rejected: touch handler Y") and the one-line rationale.
- Include the false-success trap the lane must respect.
- Include file:line anchors for anything the lane may need to pull on demand;
  do **not** paste whole canonical files.
- Use `CONTEXT_DIGEST: see PRIMARY_ARTIFACT preseed` only when literally true.
- **Forbidden: digest + re-read.** If the digest carries a decision, the
  specialist must not re-read the canonical file for the same decision; it
  may pull scoped file:line ranges on demand.

### 3b. OWNERSHIP_BOUNDARY contract

Name the lane's exact ownership surface before the specialist starts.
Specialists must write only the sections this lane owns, cite prior artifacts
for adjacent facts, and avoid re-adjudicating another lane's decision unless
the packet explicitly asks for a contradiction check. Empty values are not
allowed.

### 3c. PRIOR_SIBLINGS contract

List every artifact already produced **in the same phase lane** that overlaps
the new specialist's surface. If there are no priors, write
`PRIOR_SIBLINGS: none`. Specialists must skim listed siblings and explicitly
skip ground already covered rather than re-deriving it.

## 4. Micro-packet budget

- Aim for ≤900 words per specialist packet; exceed ~1,200 only for
  genuinely high-risk work. If a packet wants more space, split the lane or
  put the extra evidence in the preseeded artifact.
- Do not paste full files, long JSX/code blocks, or exact before/after
  replacements into `CONTEXT_DIGEST`; use file:line anchors plus the
  invariant the specialist must preserve.
- Do not turn the mission into a line-by-line implementation script when
  the specialist can infer the implementation from the scoped files.

## 5. Proof budget

- `DONE_CHECK` is the cheapest honest task-local check. Full builds, full
  suites, live acceptance, and repeated expensive checks belong in verify
  phase (`fast_check`, `smoke_check`, `ship_check`) unless the task is the
  final integration lane or the changed surface specifically requires that
  broad command now.
- If an expensive command already passed for the current diff and no owned
  files changed since, cite that artifact instead of rerunning it.

## 6. Artifact compaction

After a specialist returns, promote only bounded facts into `spec.md` /
`workboard.md`: terminal status, verdict, changed files, command
names/results, first blocker, and next action. Keep full reports and logs
in the specialist artifact; do not paste whole reports back into the run
card.

## 7. Dispatch discipline

- Only the phase conductor may delegate. Never ask a specialist to spawn
  nested subagents or to fan out its own lane.
- Default to **sequential** dispatch for artifact-producing planning,
  context, implement, and verify work. Parallelize only when packets are
  truly independent, small, and read-mostly (e.g. two independent
  read-mostly investigators).
- Coding tasks have fewer parallelizable sub-problems than research tasks;
  prefer fewer, larger packets over many thin parallel workers.
- When a specialist hits a nonfatal tool failure, resume the same lane
  instead of accepting a stop. Common recoveries: use `LS` or `Glob`
  instead of `Read` on directories; use `Grep` plus chunked `Read`
  windows instead of loading an oversized file in one shot.

## 8. Resume-same-specialist before fallback

- If a specialist returns early without the artifact or only with setup
  notes, resume the **same specialist** with `SendMessage` using its
  returned agent ID so it continues from prior state.
- If no agent ID is available, re-dispatch the exact same packet once.
- Only after a second incomplete return should you mark the lane failed,
  re-split the task, or repair the gap yourself.
