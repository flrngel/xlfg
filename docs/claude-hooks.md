# Claude Code hooks (optional)

Claude Code supports **hooks** that run when a teammate becomes idle or completes a task.
These can be used as quality gates (e.g., block task completion if tests are failing).

xlfg intentionally treats hooks as opt-in because they can be repo- and org-specific.

## Suggested hooks

### Task completion hook

Run verification and reject completion if it fails.

- Run: `xlfg verify --mode fast`
- If exit code is non-zero, exit 2 (Claude Code will ask the teammate to keep working)

### Idle hook

When a teammate goes idle, ensure they wrote their findings to the run folder and updated the plan.

## Minimal example

Create `.claude/hooks/task_complete.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Fast checks. Prefer repo-specific overrides in docs/xlfg/knowledge/commands.json
xlfg verify --mode fast
```

Then make it executable:

```bash
chmod +x .claude/hooks/task_complete.sh
```

(Exact hook configuration depends on your Claude Code setup.)
