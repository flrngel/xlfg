# Context — 20260403-phase-reliability

## Repo structure relevant to this change

### Conductor files (the ONLY files that need modification for O1-O3)
- `standalone/.claude/skills/xlfg/SKILL.md` — standalone conductor (SKILL frontmatter + body)
- `plugins/xlfg-engineering/commands/xlfg.md` — plugin conductor (command frontmatter + body)

### Hook files
- `standalone/.claude/hooks/xlfg-subagent-stop-guard.mjs` — existing SubagentStop hook (reference pattern)
- `plugins/xlfg-engineering/hooks/hooks.json` — plugin hook registry (has SubagentStop, needs Stop)
- `plugins/xlfg-engineering/scripts/subagent-stop-guard.mjs` — plugin equivalent of standalone hook

### Version files (for O4)
- `xlfg/__init__.py` — `__version__`
- `pyproject.toml` — `version =`
- `plugins/xlfg-engineering/.claude-plugin/plugin.json` — `"version"`
- `plugins/xlfg-engineering/.cursor-plugin/plugin.json` — `"version"`
- `README.md` — version mentions
- `NEXT_AGENT_CONTEXT.md` — version context
- `plugins/xlfg-engineering/CHANGELOG.md` — changelog entries
- `plugins/xlfg-engineering/README.md` — plugin readme

### Test files
- `tests/test_xlfg.py` — main test suite (validates version sync, audit features, entrypoint structure)
- `tests/test_subagent_stop_guard.py` — existing hook tests (reference pattern)

### Audit module
- `xlfg/audit.py` — `audit_repo()` reports features; needs new `conductor_stop_gate` feature

## Hard constraints

1. **Stop hook protocol**: stdin receives `{"stop_reason": "end_turn"|"max_tokens"|"tool_use", "cwd": "...", ...}`. Block via stdout `{"decision": "block", "reason": "..."}`. Allow via `exit 0`.
2. **Skill frontmatter hooks**: Can register Stop hooks same as PermissionRequest. Only active while the skill is loaded.
3. **Plugin vs standalone symmetry**: Plugin uses `${CLAUDE_PLUGIN_ROOT}/scripts/` for script paths. Standalone uses `.claude/hooks/` relative to project root.
4. **No `stop_hook_active` for Stop hooks**: Only SubagentStop has this field. Must implement our own safety valve (block count in phase-state file).
5. **`stop_reason: "max_tokens"` must always be allowed** — the model physically can't continue.

## Known unknowns

1. Whether `stop_reason: "tool_use"` is possible during skill execution — probably not relevant since the model is about to use a tool, not stop.
2. Exact cwd during Stop hook execution — likely the project root, same as other hooks.

## Harness / environment facts

- Tests use `python -m pytest tests/` — no dev server needed
- Version sync test reads `__version__` from `xlfg/__init__.py` and checks all manifests match
- Audit test checks feature flags in `report["metrics"]["features"]`
