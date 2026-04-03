# Review Summary — 20260403-phase-reliability

## Review lens: Architecture (quick / low risk)

### Finding: Plugin double-registration of Stop hook (P1, FIXED)

The Stop hook was initially registered in both `plugins/xlfg-engineering/commands/xlfg.md` frontmatter AND `plugins/xlfg-engineering/hooks/hooks.json`. If Claude Code fires both, the hook would execute twice per stop, incrementing `block_count` by 2 instead of 1 and halving the safety valve threshold.

**Fix applied:** Removed Stop hook from plugin command frontmatter. It now lives only in `hooks.json` (matching the existing SubagentStop pattern). The standalone SKILL.md keeps its frontmatter registration since there is no hooks.json for standalone packs.

### Accepted residual risk

1. **Skill-level Stop hooks are a relatively new Claude Code feature.** If they don't fire for skill frontmatter registrations, the standalone hook would be inert. The plugin hooks.json registration is more reliable since it's at the plugin level. The hook is harmless when inert (no side effect).

2. **The loopback cap is a prompt instruction, not enforced by code.** The model may exceed 2 loopbacks. The Stop hook's safety valve (3 blocks) provides the hard enforcement layer underneath.

3. **The hooks.json Stop hook fires for ALL stops, not just during /xlfg runs.** The hook exits 0 immediately if `.xlfg/phase-state.json` doesn't exist, so the cost is one filesystem stat per stop. Negligible.

### No must-fix findings remaining

The double-registration issue was the only finding. It has been fixed and re-verified (51/51 tests pass).
