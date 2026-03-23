# xlfg-engineering-plugin

`xlfg` is a **skill-first, autonomous, proof-first SDLC harness** for Claude Code.

In 2.2.0 the harness was rebuilt around current Claude Code behavior:

- **skills first**, with legacy commands kept only as compatibility shims
- **one autonomous `/xlfg` invocation** instead of human-managed phase choreography
- **`spec.md` as the single source of truth** instead of many duplicated planning files
- **conservative permission automation** through `allowed-tools` and a narrow `ExitPlanMode` hook
- **two install forms**: plugin for team reuse and standalone `.claude/` for short `/xlfg`

## What is in this repo

1. A **Claude Code plugin** in `plugins/xlfg-engineering/`
2. A **standalone `.claude/skills/xlfg/` pack** in `standalone/`
3. A dependency-free **Python helper CLI** (`xlfg`) that can scaffold, recall, doctor, verify, and audit the same file model locally
4. Benchmarking guidance in `docs/benchmarking.md`
5. A repo handoff file in `NEXT_AGENT_CONTEXT.md`

## Quick start

### Plugin / team install

Run the plugin skill:

- `/xlfg-engineering:xlfg "what you want built"`

### Standalone / short-command install

Copy `standalone/.claude/skills/xlfg/` into your target repo’s `.claude/skills/xlfg/`, then run:

- `/xlfg "what you want built"`

## Why 2.2.0 exists

The previous revision was leaner than 2.0.10, but it still made the human do too much workflow coordination and still duplicated planning state across too many files.

This revision fixes three things:

- **Autonomy**: `/xlfg` now executes the full SDLC itself.
- **Deduplication**: `spec.md` absorbs request truth, why, harness choice, plan, and proof summary.
- **Compatibility**: the package now matches current Claude Code conventions for skills, hooks, namespacing, and effort frontmatter.

## Local helper CLI

```bash
python -m pip install -e .
xlfg start "fix login flow"
xlfg audit
xlfg verify --mode full
```

## License

MIT
