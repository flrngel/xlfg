# Using xlfg with other agents

xlfg is designed to be **tool-agnostic**:

- the *Claude Code plugin* gives you `/xlfg` as a command + subagents
- the *file structure* (`docs/xlfg/` + `.xlfg/`) and the *CLI* (`xlfg init/start/doctor/verify`) can be used by other agents (Codex, Cursor agents, CI bots, etc.)

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

- write `flow-spec.md` first
- write `test-contract.md` next
- write `env-plan.md` next
- then write `plan.md`
- capture verification output via `xlfg verify`

4. Inspect the repo’s execution contract:

```bash
xlfg detect
xlfg doctor
```

5. Verify and iterate:

```bash
xlfg verify --mode full
```

## Tips

- Prefer many small, isolated outputs over one giant document.
- Do not mark work done until the contracts are written and verification is green.
- Commit durable artifacts (`docs/xlfg/...`). Ignore raw logs (`.xlfg/...`).
- Put canonical commands, dev ports, and healthchecks in `docs/xlfg/knowledge/commands.json`.
