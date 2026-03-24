# NEXT_AGENT_CONTEXT

## Current state (2.3.0)

The main 2.3.0 fix is **entrypoint correctness**.

2.2.0 improved autonomy and deduplication, but it accidentally broke `/xlfg` in real Claude Code installs by doing two unsafe things:

1. shipping a plugin `command + skill` pair with the same slash name (`xlfg`)
2. making the command act as a shim that pointed Claude at `plugins/xlfg-engineering/skills/xlfg/SKILL.md`, which is a source-repo path and not a safe assumption after plugin install

2.3.0 fixes both:

- the plugin now exposes a **single self-contained command** at `/xlfg-engineering:xlfg`
- the standalone pack remains the canonical short-name install at `/xlfg`
- the colliding plugin `skills/xlfg/` entrypoint was removed
- support skills were kept, but hidden from the slash menu with `user-invocable: false`
- plugin commands/skills no longer use `name:` frontmatter, which reduces current namespace edge-case risk
- lint, audit, and tests now explicitly guard against entrypoint collisions and broken repo-relative plugin references

## What xlfg should be

A serious but lean SDLC exoskeleton for Claude Code:

- one invocation
- one owner
- one run card (`spec.md`)
- deterministic recall
- explicit proof
- optional research
- proportional review
- durable compounding only when verified

## Product truths to preserve

- `/xlfg` should execute the entire workflow itself. Do not make the user run `/xlfg:plan`, `/xlfg:implement`, `/xlfg:verify`, etc.
- `spec.md` is the single source of truth; optional docs exist only when they change a decision.
- The helper CLI is optional but valuable. When available, the main entrypoint should prefer it for scaffold sync, run creation, recall, and verification.
- The plugin form is for team reuse and therefore namespaced.
- The standalone `.claude/skills/xlfg/` pack is the best short-name UX and the most reliable path when users want direct `/xlfg`.

## Main files to understand first

1. `plugins/xlfg-engineering/commands/xlfg.md`
2. `standalone/.claude/skills/xlfg/SKILL.md`
3. `xlfg/runs.py`
4. `xlfg/verify.py`
5. `xlfg/audit.py`
6. `tests/test_xlfg.py`

## Regression triggers

Treat any of the following as regressions:

- `/xlfg` asking the user to run or sequence internal phase commands
- plugin command and plugin skill shipping with the same slash name
- commands or skills that reference `plugins/xlfg-engineering/...` as if that path exists inside the target repo
- plugin support skills cluttering the slash menu instead of staying hidden helpers
- reintroducing duplicated planning state that competes with `spec.md`
- claiming green without scenario-targeted proof
