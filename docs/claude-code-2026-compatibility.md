# Claude Code 2026 compatibility notes for xlfg 2.3.0

This revision aligns xlfg to the current Claude Code mental model while fixing the entrypoint breakage introduced in 2.2.0:

- custom commands and skills now share the same slash-command system, so xlfg ships **one primary entrypoint per install mode** instead of a colliding command+skill pair
- plugins are namespaced (`/plugin-name:skill`), while standalone `.claude/skills/` gives short names like `/xlfg`
- `allowed-tools` reduces per-tool permission prompts while the entrypoint is active
- `hooks` can auto-approve narrow permission prompts such as `ExitPlanMode`
- `effort` frontmatter lets a workflow set a stronger reasoning budget when invoked
- context should stay small, so xlfg keeps the run truth in `spec.md`
- plugin commands should not assume source-repo-relative plugin paths after install

Practical consequence: use the **plugin** when you want a shareable team distribution, and use the **standalone pack** when you want the exact short command `/xlfg`.
