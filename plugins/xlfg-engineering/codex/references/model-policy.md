# Codex Model And Effort Policy

## Rule

Do not load `plugins/xlfg-engineering/agents/**` as Codex agent configuration. Those files are Claude Code specialist definitions and their `model` / `effort` frontmatter is not portable.

## Codex Defaults

- Use the active Codex session model and reasoning effort unless the user or a trusted project `.codex/agents/*.toml` file explicitly sets another value.
- Do not translate Claude model labels into OpenAI model names inside this plugin.
- When spawning supported Codex subagents, choose the role by task shape:
  - `explorer` for read-only repo mapping, context gathering, and evidence collection
  - `worker` for bounded implementation or test edits
  - `default` for mixed orchestration or synthesis
- Keep each spawned lane bounded by one artifact, one file scope, and one done check.
- If a configured Codex custom agent is available, use it only when its description matches the lane and it preserves the artifact contract.

## Recording

When model choice affects risk, cost, or proof quality, record the actual Codex role or custom agent used in `workboard.md` or the lane artifact.
