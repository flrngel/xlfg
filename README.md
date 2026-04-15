# xlfg-engineering

`xlfg` is an autonomous, proof-first SDLC harness for Claude Code.

Version 3.1.0 tightens inter-agent communication: artifacts carry exactly one canonical `status:` field inside YAML frontmatter (replacing the dual `Status:` + `status:` write), `workboard.md`'s phase-status block is rendered from `.xlfg/phase-state.json` instead of hand-written by each phase, the Claude Code task pane now mirrors xlfg's phase list via a startup `TaskCreate` bridge, and `ledger.jsonl` gets a canonical schema (`docs/xlfg/knowledge/ledger-schema.md`) with a single validating writer (`scripts/ledger-append.mjs`). Two redundant specialist lanes are gated: context-phase skips `xlfg-repo-mapper` when `memory-recall.md` already grep-cites the surface, and verify-phase skips `xlfg-ui-designer` when implement-phase task-checker already proved every DA.

Version 3.0.0 removed the `xlfg` Python CLI package entirely. Install via the plugin marketplace only — no Python package installation needed or supported.

- `/xlfg` and `/xlfg-debug` are the public entrypoints, each **batching hidden phase skills**
- the plugin commands keep short aliases (`/xlfg`, `/xlfg-debug`) via `name:` frontmatter, while the namespaced forms remain `/xlfg-engineering:xlfg` and `/xlfg-engineering:xlfg-debug`
- the batch now includes a mandatory **intent phase** before context gathering and planning
- `spec.md` is now the only active home for the **intent contract** and objective groups
- bundled / messy requests are split into stable objective groups (`O1`, `O2`, ...)
- hidden phase skills still load **just in time**, matching Claude Code’s skills model while keeping context small
- every plugin specialist now has an explicit tool allowlist, proactive delegation description, foreground-only bias, stronger execution contract, and bounded turn budget
- review specialists now write lane artifacts under `reviews/`, and the standalone pack now includes `.claude/agents/` parity

## What is in this repo

1. A Claude Code plugin in `plugins/xlfg-engineering/`
2. A standalone `.claude/skills/` pack in `standalone/`
3. Research notes on recent subagent / harness hardening in `docs/subagent-hardening-2026.md`
4. A repo handoff file in `NEXT_AGENT_CONTEXT.md`


## Quick start

### Install via the plugin marketplace (recommended)

Inside Claude Code, add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add flrngel/xlfg
/plugin install xlfg-engineering@xlfg
```

Claude Code fetches the marketplace manifest from `.claude-plugin/marketplace.json`, resolves the plugin at `./plugins/xlfg-engineering`, and caches it under `~/.claude/plugins/`. Commands, skills, hooks, specialist agents, and the `context7` MCP server all activate together. After install:

- `/xlfg "what you want built"` — full SDLC run
- `/xlfg-debug "what is broken"` — diagnosis-only run (no source edits)

Both short forms are aliases of `/xlfg-engineering:xlfg` and `/xlfg-engineering:xlfg-debug`, registered via `name:` frontmatter on the plugin commands.

Update with `/plugin marketplace update xlfg`.

### Manual standalone install

For environments where the plugin loader is unavailable, copy the full `standalone/.claude/` directory into your target repo’s `.claude/`, then run `/xlfg` or `/xlfg-debug`.

## Entry model

- `/xlfg` owns the whole SDLC run and loads hidden phase skills just in time: recall, intent, context, plan, implement, verify, review, compound.
- `/xlfg-debug` is the diagnosis-only sibling: recall → intent → context → debug. It finds the deep root cause and names the likely repair surface without touching source, tests, fixtures, migrations, or configs.
- Neither command asks the user to run phase subcommands or internal skills.
- `spec.md` is the run card and single source of truth.
- Optional docs exist only when they change a decision or proof.
## License

MIT


## 2.7.5 note

- xlfg specialists are now documented and audited as **leaf workers**: no nested subagent delegation inside specialist lanes.
- Plugin and standalone agent packs now share the same bounded `maxTurns` budgets again, so stalled lanes fail faster instead of looking hung.
- Review fan-out is leaner by default, and conductor guidance now says waiting is valid only when a preseeded `PRIMARY_ARTIFACT` and explicit `RETURN_CONTRACT` exist.


## 2.7.1 note

- Main conductor now dispatches specialists with an atomic task packet: one mission, one required artifact, one done check.
- Progress-only specialist replies are treated as incomplete; the conductor resumes the same specialist once before accepting failure or repairing the lane.


## 2.7.2 hardening note

The plugin build now ships a plugin-level `SubagentStop` guard. In plugin mode, xlfg specialists are not allowed to stop on setup chatter or missing artifacts; the hook blocks the stop once and forces the specialist to finish the promised artifact or write an explicit `BLOCKED` / `FAILED` artifact instead.
