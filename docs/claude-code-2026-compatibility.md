# Claude Code 2026 compatibility notes for xlfg 2.4.0

This revision aligns xlfg to the current Claude Code mental model while fixing the architectural regression from 2.3.0:

- custom commands and skills now share the same slash-command system, so xlfg still ships **one public entrypoint per install mode** instead of a colliding command+skill pair
- plugin skills stay namespaced, while standalone `.claude/skills/` still gives short names like `/xlfg`
- the `Skill` tool can execute hidden skills inside the main conversation, so `/xlfg` now batches hidden phase skills just in time instead of flattening the whole workflow into one giant prompt
- `allowed-tools` reduces per-tool permission prompts while the entrypoint is active
- `hooks` can auto-approve narrow permission prompts such as `ExitPlanMode`
- `effort` frontmatter lets the workflow set a stronger reasoning budget when invoked
- current tool names matter: `Skill`, `WebSearch`, and `WebFetch` are the right modern primitives; the old `Task` wording is stale and confusing
- context should stay small, so xlfg still keeps the run truth in `spec.md`
- plugin commands should not assume source-repo-relative plugin paths after install

Practical consequence: use the **plugin** when you want a shareable team distribution, and use the **standalone pack** when you want the exact short command `/xlfg` plus its matching hidden phase skills.
