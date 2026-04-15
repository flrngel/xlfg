# Claude Code hooks (optional)

Claude Code supports **hooks** that run when a teammate becomes idle or completes a task.
These can be used as quality gates.

xlfg intentionally treats hooks as opt-in because they can be repo- and org-specific.

## Suggested hooks

### Task completion hook

Run fast verification and reject completion if it fails.

Recommended sequence:

1. ensure the teammate updated `flow-spec.md` / `test-contract.md` / `env-plan.md` if the task changed scope
2. run fast verification
3. reject completion if it fails

### Idle hook

When a teammate goes idle, ensure they wrote findings to the run folder and updated the plan.

## Minimal example

Create `.claude/hooks/task_complete.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Run your project's test command directly. Example:
python3 -m unittest discover tests/ -v
```

Then make it executable:

```bash
chmod +x .claude/hooks/task_complete.sh
```

(Exact hook configuration depends on your Claude Code setup.)
