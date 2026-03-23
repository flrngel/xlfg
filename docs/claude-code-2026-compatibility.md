# Claude Code 2026 compatibility notes for xlfg 2.2.0

This revision aligns xlfg to the current Claude Code mental model:

- skills are primary; legacy commands are still supported but are no longer the main UX
- plugins are namespaced (`/plugin-name:skill`), while standalone `.claude/skills/` gives short names like `/xlfg`
- `allowed-tools` reduces per-tool permission prompts while a skill is active
- `hooks` can auto-approve narrow permission prompts such as `ExitPlanMode`
- `effort` frontmatter lets a workflow set a stronger reasoning budget when invoked
- context should stay small, so xlfg now keeps the run truth in `spec.md`

Practical consequence: use the **plugin** when you want a shareable team distribution, and use the **standalone pack** when you want the exact short command `/xlfg`.
