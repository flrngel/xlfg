# xlfg architecture (4.0.0)

`/xlfg` is intentionally simple at the top level:

```text
/xlfg
  └─ one autonomous run
       recall -> intent -> context -> plan -> implement -> verify -> review -> compound
```

There are two supported install modes:

- **Claude Code plugin**: `/xlfg-engineering:xlfg` with `/xlfg` alias
- **Codex plugin**: `$xlfg`

The Claude plugin form is for shared team distribution and is namespaced; the `/xlfg` short alias is registered via `name:` frontmatter. The Codex form is an installable skill plugin because Codex plugins distribute skills, MCP config, apps, and metadata.

## Run-state architecture

### Core files (always seeded)

- `context.md`
- `memory-recall.md`
- `spec.md`
- `test-contract.md`
- `test-readiness.md`
- `workboard.md`

### Optional files (only when they change a decision)

- `research.md`
- `diagnosis.md`
- `solution-decision.md`
- `flow-spec.md`
- `env-plan.md`
- `proof-map.md`
- `risk.md`
- `review-summary.md`
- `run-summary.md`
- `compound-summary.md`

`verification.md` is written during verification, not seeded up front.

## Architectural rules

- `spec.md` is the run card and single source of truth, including the intent contract and objective groups.
- The main entrypoint owns the whole SDLC run; it should not ask the user to run manual phase slash commands.
- The helper CLI may be used when installed to make scaffold sync, run creation, recall, doctoring, and verification deterministic.
- Support skills exist only as background helpers. They should not compete with the main `/xlfg` entrypoint.
- Entry-point correctness matters: no command+skill collisions for the same slash name, and no repo-relative plugin path assumptions.
- The Codex surface is separate from the Claude hidden-skill surface because Codex skills require `name` and `description` metadata.
