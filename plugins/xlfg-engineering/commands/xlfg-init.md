---
name: xlfg-init
description: One-shot scaffold for a project adopting xlfg. Idempotently patches the CWD's .gitignore and creates docs/xlfg/runs/ with .gitkeep and README.
argument-hint: "[no arguments]"
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Bash, Glob, LS
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

# /xlfg-init — scaffold a project to adopt xlfg

Use this **once, in the user's own project**, right after they install the plugin. This is not a conductor and not an SDLC run; it is a small idempotent scaffold step.

## What this command is for

xlfg v6 stores its durable memory under `docs/xlfg/` in the project that's using it. Two pieces need to exist for that archive to behave correctly:

1. The project's `.gitignore` must mark individual run directories as local-only (run summaries are per-machine scratch, not shared code).
2. `docs/xlfg/runs/` must exist and be committable even when empty, so the archive layout is present on a fresh clone.

Neither the `/xlfg` nor `/xlfg-debug` conductor touches `.gitignore`, and the runs directory is only created lazily inside a specific `RUN_ID` subdirectory during compound. Without `/xlfg-init`, a fresh adopter risks `git add .` sweeping up per-run summaries that were never meant to be committed.

`/xlfg-init` fixes that — and nothing else. It is not an onboarding wizard, not a project template, not a content generator.

## Where this command runs

**In the user's current working directory.** That is almost never this plugin's own repo; it is whatever project is adopting xlfg. Do not read any context from the xlfg plugin source; do not assume any particular prior state of `docs/xlfg/` or `.gitignore`. Work from what exists in the CWD at invocation time, and make the minimum idempotent change that brings that CWD up to the v6 scaffold standard.

If the user invokes this inside the xlfg meta-repo itself, the command will detect that everything is already in place and exit with a no-op notice. That is correct behavior.

## What to do

Perform these steps in order. Every step is idempotent; re-running the command on an already-scaffolded project must be a safe no-op.

### 1. Confirm you're working in a real project, not the xlfg plugin

Run `pwd` once via `Bash` and read the output. Also check whether a `.git` directory exists at the CWD root (via `LS` or `Bash: git rev-parse --show-toplevel`). If the CWD is not the root of a git repository, stop and tell the user — they should run this from their project root. Do not try to initialize git for them.

### 2. Patch `.gitignore`

Read the CWD's `.gitignore` (create it empty if missing). The canonical v6 xlfg block is exactly three lines, plus an optional leading comment:

```
# xlfg run artifacts (per-machine scratch; committed scaffold is .gitkeep + README.md)
docs/xlfg/runs/*
!docs/xlfg/runs/.gitkeep
!docs/xlfg/runs/README.md
```

- If every one of the three non-comment lines is already present anywhere in the file, in any order, do not modify the file. Report "`.gitignore` already has the canonical xlfg block".
- If none of the three lines are present, append the whole block (comment + three rules) to the end of the file, separated from existing content by a blank line.
- If only some of the three lines are present (partial/drift state), report this to the user as a warning and ask before appending the missing rules. Do not delete or reorder anything that's already there.

**Do not** add a `.xlfg/` ignore line — `.xlfg/` is not a v6 directory and writing to it is explicitly a regression (see `docs/xlfg/current-state.md` in this plugin for the rationale). A project upgrading from v5 should remove its `.xlfg/` directory manually; `xlfg-init` does not delete files.

**Do not** add a blanket `docs/xlfg/` ignore — that would swallow `docs/xlfg/current-state.md`, which is the tracked handoff file the compound phase writes sparingly. If you find such a line already present in the user's `.gitignore`, flag it as drift and ask before editing.

### 3. Create `docs/xlfg/runs/.gitkeep`

If `docs/xlfg/runs/` does not exist, create it via `Bash: mkdir -p docs/xlfg/runs`. Then create an empty file at `docs/xlfg/runs/.gitkeep` if it doesn't already exist. This is what the `!docs/xlfg/runs/.gitkeep` exception in `.gitignore` refers to — it lets the directory itself be tracked while the `<RUN_ID>/` subdirectories stay local.

### 4. Create `docs/xlfg/runs/README.md`

If `docs/xlfg/runs/README.md` does not exist, write exactly this content:

```markdown
# xlfg run archives

Per-run durable artifacts from `/xlfg` (`run-summary.md`) and `/xlfg-debug` (`diagnosis.md`) land under `<RUN_ID>/` subdirectories here. Individual run directories are gitignored by design — they are per-machine scratch, useful for one engineer's recall on one workstation. Only this README and `.gitkeep` are tracked.

Durable knowledge a future session actually needs to share across machines belongs in `../current-state.md`, which the compound phase updates sparingly. Run summaries are a log, not a spec.
```

If the file already exists, do not overwrite it. The user may have customized it.

### 5. Report

Print a short summary of what you did. Three categories:

- **Created**: files and directories that did not exist before and are now in place.
- **Already correct**: files or rules that were already present and needed no change.
- **Warnings**: partial/drift states the user should look at manually (e.g. only two of three `.gitignore` rules were present, or a blanket `docs/xlfg/` ignore line exists).

Do not commit. Leave the staging decision to the user — they may want to bundle this scaffold with other project changes.

## What this command does NOT do

- Does not create `docs/xlfg/current-state.md`. That file holds project-specific load-bearing truths and is authored by the compound phase when a `/xlfg` run earns a promotion. Scaffolding it empty would invite noise.
- Does not create `docs/xlfg/knowledge/`, `docs/xlfg/migrations/`, `.xlfg/`, or any other v5-era directory. Those surfaces are gone in v6.
- Does not run `/xlfg` or any phase skill.
- Does not commit, push, or invoke git hooks.
- Does not touch files outside `.gitignore` and `docs/xlfg/runs/`.

## Completion

Write a one-paragraph summary for the user listing exactly what changed (or that nothing changed, if the project was already scaffolded). If you issued any warnings in step 5, repeat them at the top of the summary so they are the first thing the user reads.
