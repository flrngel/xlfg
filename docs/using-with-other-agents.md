# Using xlfg with other agents

xlfg is designed to be **tool-agnostic**:

- The *Claude Code plugin* gives you `/xlfg` as a command + subagents.
- The *file structure* (`docs/xlfg/` + `.xlfg/`) and the *CLI* (`xlfg init/start/verify`) can be used by other agents (Codex, Cursor agents, CI bots, etc.).

## Minimal workflow (agent-agnostic)

1. Initialize scaffolding:

```bash
xlfg init
```

2. Start a run:

```bash
xlfg start "your request"
```

3. Have the agent work using the run folder as its system of record:

- Write spec to `docs/xlfg/runs/<run-id>/spec.md`
- Write plan to `docs/xlfg/runs/<run-id>/plan.md`
- Capture verification output via `xlfg verify`

4. Verify and iterate:

```bash
xlfg verify --mode full
```

## Tips

- Prefer many small, isolated outputs over one giant document.
- Don’t mark work done until verification is green and recorded.
- Commit durable artifacts (`docs/xlfg/...`). Ignore raw logs (`.xlfg/...`).
