# xlfg patterns

Reusable patterns discovered while shipping.

## Pattern: Conductor Stop hook for pipeline completion

- **When to use**: Any multi-phase skill pipeline where the model might stop before all phases complete
- **Why it works**: The model can stop at any time between turns. A Stop hook reads a phase-state file and blocks if incomplete. The model gets the block reason as context and continues.
- **Implementation notes**: Write `.xlfg/phase-state.json` after startup (all phases listed, none completed). Update `completed` array after each phase. Reset `block_count` to 0 on each advance. Hook increments `block_count` on each block. Safety valve at 3 blocks.
- **What shortcut it replaces**: Relying on the model to follow "invoke these 8 skills in order" from memory through heavy context
- **Pitfalls**: Don't register the same hook in both command frontmatter and hooks.json (double-fires). Always allow on `max_tokens`. Always allow when no state file exists.
- **Examples / links**: `plugins/xlfg-engineering/scripts/phase-gate.mjs`, run 20260403-phase-reliability

## Pattern: Version-bump sweep

- **When to use**: Every time the plugin version string changes.
- **Why it works**: The three `plugin.json` manifests (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`) are explicitly asserted equal by `test_versions_are_synced_across_plugin_manifests`, but hardcoded version strings elsewhere (e.g. `tests/test_codex_plugin.py`'s `self.assertEqual(manifest["version"], "X.Y.Z")`) have also failed at least twice when missed.
- **Implementation notes**: Before bumping, `rg -n "\\"X\\.Y\\.Z\\"" --type py` for the outgoing version across the repo. Bump every hit, not just the three manifests. `docs/xlfg/meta.json` has a `tool_version` field too — worth checking.
- **What shortcut it replaces**: "Bump the three manifests and run tests" (the test failure from a missed hardcoded assertion reads as a sync bug, not a missed file).
- **Pitfalls**: CHANGELOG entries that say "bumped tests/test_codex_plugin.py version assertions to X.Y.Z" are evidence the file has been a recurring trap (v3.3.0 and v3.3.1 entries both named it).
- **Examples / links**: run 20260416-delete-standalone-bump caught it at implement-phase harness failure; v3.3.1 CHANGELOG explicitly documents the same bookkeeping. Retroactively promoted as a pattern.
