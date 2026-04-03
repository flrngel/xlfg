# xlfg patterns

Reusable patterns discovered while shipping.

## Pattern: Conductor Stop hook for pipeline completion

- **When to use**: Any multi-phase skill pipeline where the model might stop before all phases complete
- **Why it works**: The model can stop at any time between turns. A Stop hook reads a phase-state file and blocks if incomplete. The model gets the block reason as context and continues.
- **Implementation notes**: Write `.xlfg/phase-state.json` after startup (all phases listed, none completed). Update `completed` array after each phase. Reset `block_count` to 0 on each advance. Hook increments `block_count` on each block. Safety valve at 3 blocks.
- **What shortcut it replaces**: Relying on the model to follow "invoke these 8 skills in order" from memory through heavy context
- **Pitfalls**: Don't register the same hook in both command frontmatter and hooks.json (double-fires). Always allow on `max_tokens`. Always allow when no state file exists.
- **Examples / links**: `standalone/.claude/hooks/xlfg-phase-gate.mjs`, run 20260403-phase-reliability

## Pattern: Plugin vs standalone hook registration

- **When to use**: When adding any hook to both plugin and standalone packs
- **Why it works**: Plugin hooks.json fires at plugin level; SKILL.md frontmatter fires at skill level. They can overlap.
- **Implementation notes**: Plugin → `hooks.json` only. Standalone → SKILL.md frontmatter only. Never both for the same event.
- **What shortcut it replaces**: Copying the hook registration to every possible location "just in case"
- **Pitfalls**: Double-registration causes double-firing, which breaks block_count-based safety valves
- **Examples / links**: `plugins/xlfg-engineering/hooks/hooks.json` (Stop + SubagentStop), `standalone/.claude/skills/xlfg/SKILL.md` (Stop in frontmatter)
