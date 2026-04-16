# Claude Code 2026 compatibility notes for xlfg 2.6.0

This revision keeps xlfg aligned to the current Claude Code mental model while strengthening the input side of the workflow:

- custom commands and skills share the same slash-command surface, so xlfg still ships a **single public entrypoint** (`/xlfg`, registered by the plugin command's `name:` frontmatter so the short alias is available without the `xlfg-engineering:` namespace) instead of a colliding command+skill pair
- the `Skill` tool can execute hidden skills inside the main conversation, so `/xlfg` batches hidden phase skills just in time instead of flattening the whole workflow into one giant prompt
- `allowed-tools` reduces per-tool permission prompts while the entrypoint is active
- `hooks` can auto-approve narrow permission prompts such as `ExitPlanMode`
- `effort` frontmatter lets the workflow set a stronger reasoning budget when invoked
- current tool names matter: `Skill`, `WebSearch`, and `WebFetch` are the right modern primitives; the old `Task` wording is stale and confusing
- skills should load progressively, so xlfg now resolves messy intent first and keeps the active run truth in `spec.md`
- plugin commands should not assume source-repo-relative plugin paths after install

Practical consequence: install the plugin through Claude Code's marketplace for the full `/xlfg` + `/xlfg-debug` surface; the short `/xlfg` alias is registered by the plugin command's `name:` frontmatter.
