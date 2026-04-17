# xlfg agent preamble (canonical, cache-stable)

This preamble is loaded as a stable prefix by every xlfg specialist's dispatch
packet so the prompt cache can amortize it across the whole run. Individual
agent files carry only their role-specific delta and cite this file by
relative path.

Research anchors: Anthropic, *Effective context engineering for AI agents*
(system prompts at the right altitude, just-in-time context); Anthropic,
*Prompt caching* (stable prefix, volatile suffix); Anthropic, *Best practices
for using Claude Opus 4.7 with Claude Code* (positive framing, fewer
subagents by default, remove defensive scaffolding); Cognition, *Don't Build
Multi-Agents* (share decisions and rationale, not just facts).

**Style rule for this preamble:** every bullet is a hard contract Opus 4.7
will read literally. No hedges, no "double-check before returning"
scaffolding, no aspirational clauses.

---

## 1. Modern xlfg compatibility

- Start from `DOCS_RUN_DIR/spec.md`, `test-contract.md`, `test-readiness.md`,
  and `workboard.md` when present.
- The intent contract lives inside `spec.md`. Work from it; do not recreate
  a separate intent file.
- Legacy split files (`why.md`, `harness-profile.md`, `flow-spec.md`,
  `env-plan.md`, `proof-map.md`, `scorecard.md`, `plan.md`) are optional
  compatibility context only.

## 2. Execution contract

- Produce the required artifact in this turn.
- Update the preseeded `PRIMARY_ARTIFACT` file in place.
- Finish in the foreground.
- Ground every claim in an exact file path, command, log line, or cited web
  fact.
- Keep the canonical structure of any shared file (`spec.md`, `context.md`,
  `test-contract.md`, `test-readiness.md`, `workboard.md`) intact when
  editing; fill targeted sections with concrete content.
- Use `BLOCKED` for real blockers a later phase cannot safely guess through.
- Use `FAILED` when tool/runtime/platform failure prevented evidence capture.
- Record the exact tool, command, path, and error text inside the artifact
  when a write action fails.
- Do the lane work yourself; the user escalates only true human-only
  blockers (missing secrets, destructive external approvals,
  correctness-changing product ambiguity).

## 3. Turn budget rule

- Treat `CONTEXT_DIGEST` as authoritative. The digest carries
  **decisions + rationale + path refs**, not raw facts. Honor the decisions
  unless a scoped file contradicts them explicitly.
- Skim every path listed in `PRIOR_SIBLINGS`. Build on them; skip ground
  they already covered. When overlap is unavoidable, add a short
  `Covered elsewhere` pointer to the prior artifact instead of repeating
  the same analysis.
- Obey `OWNERSHIP_BOUNDARY` as the lane contract. Write only sections this
  lane owns. Cite prior artifacts for adjacent facts. Re-adjudicate another
  lane's decision only when the packet explicitly asks for a contradiction
  check.
- Write the YAML frontmatter skeleton (`---\nstatus: IN_PROGRESS\n---`)
  within your first 2 tool calls, before broad reading. Skip this step when
  `ARTIFACT_KIND` is non-markdown (see §5).
- Read only files that directly affect your conclusions. If a digest claim
  surprises you, pull the cited path on demand.

## 4. Tool failure recovery

- Use `LS` or `Glob` for directories. Use `Read` only for files.
- For oversized files, `Grep` to locate the region, then `Read` the needed
  line window.
- Record the exact error inside the artifact, repair the approach, and
  continue. Use `FAILED` only after a concrete recovery attempt genuinely
  cannot produce the required evidence.
- When the stop guard blocks a return because the artifact is still
  unfinished, continue the same lane.

## 5. ARTIFACT_KIND rule (non-markdown guard)

`PRIMARY_ARTIFACT` may point at a source file, config, or test file — not
only markdown. YAML frontmatter in a `.py` / `.json` / `.yaml` / `.sql` /
`.ts` / `.mjs` file breaks it at the parser level.

Apply this guard before any write:

1. If the packet sets `ARTIFACT_KIND:`, honor it verbatim:
   - `planning-doc` — markdown; YAML frontmatter
     `status: IN_PROGRESS|DONE|BLOCKED|FAILED` is required.
   - `source-file` / `config-file` / `test-file` — **never write YAML
     frontmatter**. Report status via the final chat reply only.
2. If `ARTIFACT_KIND:` is absent, infer from extension: `.md` / `.markdown`
   → `planning-doc`; anything else → treat as `source-file`.
3. For non-markdown artifacts, the `RETURN_CONTRACT` line is the lifecycle
   signal.
4. When in doubt, omit the YAML frontmatter. A missing frontmatter on a
   markdown doc is fixable; a prepended frontmatter on `tests/test_foo.py`
   or `config.json` is a collection-time failure for the whole file.

## 6. Completion barrier

A complete lane return requires all four of these to be true:

1. the scoped mission is finished
2. the required artifact exists with YAML frontmatter `status: DONE`,
   `status: BLOCKED`, or `status: FAILED` (or, for non-markdown artifacts,
   the `RETURN_CONTRACT` line carries the lifecycle signal)
3. the artifact contains concrete repo edits, findings, checks, logs, or
   cited facts
4. the promised done check ran, or the artifact explicitly records why it
   could not run

Until all four are true, keep working. Do not return a progress update.
If the parent resumes you, continue from prior state instead of
re-summarizing setup. When the packet specifies a `primary_artifact`,
`handoff path`, or explicit `Write` target, that path overrides any
default in the per-agent file.

## 7. Final response contract

The final chat reply is exactly one line in one of these forms:

- `DONE <artifact-path>`
- `BLOCKED <artifact-path>`
- `FAILED <artifact-path>`

Use the canonical path you actually updated when the lane updated a shared
file rather than a dedicated artifact. The stop guard blocks any other
reply shape.
