---
description: Audit the xlfg harness itself — version sync, SDLC coverage, workflow load, Claude Code compatibility. Offers to submit the redacted report to flrngel/xlfg to improve the harness.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash
effort: medium
---

# xlfg audit

Measure the harness itself, not the user's project.

`/xlfg-audit` exists so the xlfg maintainers can see how the harness behaves on real repos and fix what breaks. The user running the command does not get a new feature from the audit — they get a way to help upstream improve xlfg. That is the whole point of the command.

Unlike pre-3.0.0 audit, this command has no Python CLI behind it. Every check below is a concrete file read or frontmatter inspection Claude can perform deterministically. Run each check, collect the values, print the per-check summary table FIRST followed by the supporting detail, then always offer to submit the redacted report to `flrngel/xlfg`.

Takes no arguments.

## Checks

### 1. Version sync

Read the `version` field from all three plugin manifests:

- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `.codex-plugin/plugin.json`

**Pass** if all three agree. Otherwise list which manifests disagree.

### 2. SDLC coverage

For each expected phase skill, check that the directory exists and contains a `SKILL.md`:

- `skills/xlfg-recall-phase/`
- `skills/xlfg-intent-phase/`
- `skills/xlfg-context-phase/`
- `skills/xlfg-plan-phase/`
- `skills/xlfg-implement-phase/`
- `skills/xlfg-verify-phase/`
- `skills/xlfg-review-phase/`
- `skills/xlfg-compound-phase/`
- `skills/xlfg-debug-phase/`

`sdlc_coverage_score` = present / 9. Higher is better.

### 3. Workflow load

Compute word counts (via `wc -w`) for:

- `commands/xlfg.md`
- `commands/xlfg-debug.md`
- each `skills/xlfg-*-phase/SKILL.md`

Report each file's word count. `workflow_load_score` = total words across the above files. **Lower is better.** Also list the top 3 files by size (the top load drivers) so future tuning can target them.

### 4. Claude Code compatibility

For the two public commands (`commands/xlfg.md` and `commands/xlfg-debug.md` inside the plugin), confirm the frontmatter contains:

- `allowed-tools:`
- `effort:` (should be `high` for these)
- `disable-model-invocation: true`
- `hooks:` with a `PermissionRequest` → `ExitPlanMode` auto-allow

For every phase skill under `skills/xlfg-*-phase/SKILL.md`, confirm the frontmatter contains:

- `user-invocable: false`
- no `name:` field (hidden skills must omit `name` per the Codex split)

Forbidden-token sweep across `commands/**`, `skills/**`, and `agents/**` inside the plugin:

- stale `Task` tool name (check with word-boundary patterns `, Task,`, `, Task\n`, `, Task `, ` Task(`, ` Task `) — `TaskCreate`/`TaskUpdate`/`TaskList` are legitimate and must not trigger
- `query-contract.md` (forbidden reference to a deleted file)

For every specialist agent under `agents/**/*.md` (excluding `_shared`) inside the plugin:

- `maxTurns:` present and ≤ 150
- no `Agent` or `SendMessage` in its `tools:` list (leaf-worker rule)

`claude_code_compatibility_score` = pass count / total checks. Higher is better.

### 5. Codex surface integrity

Confirm exactly two public Codex skills:

- `codex/skills/xlfg/SKILL.md`
- `codex/skills/xlfg-debug/SKILL.md`

Confirm neither file contains any of these Claude-only tokens: `allowed-tools`, `Skill(`, `TaskCreate`, `TaskUpdate`, `TaskList`, `ExitPlanMode`, `PermissionRequest`, `CLAUDE_PLUGIN_ROOT`, `user-invocable`, `model:`, `effort:`, `sonnet`, `haiku`, `opus`.

### 6. Scaffold self-consistency

If the current repo has a `docs/xlfg/meta.json`, read `tool_version` and compare against the plugin.json version from check 1. Flag drift.

## Output format

Produce, in this order:

1. **Per-check summary table — FIRST.** Print this before any prose. One row per check (1–6) with columns `# | check | status | score | note`. Status is `pass` / `fail` / `warn`. Score is the numeric value where applicable (coverage ratio, compatibility ratio, word count) or `—`. Note is a terse one-liner such as `3 manifests agree` or `2 skills missing user-invocable`.
2. **Headline scores.** One line each: `workflow_load_score`, `sdlc_coverage_score`, `claude_code_compatibility_score`, and `efficiency_index`.
3. **Top load drivers** — the top 3 largest files by word count from check 3.
4. **Top compatibility gaps** — any failed assertion from check 4, grouped by category (command frontmatter, phase skill frontmatter, forbidden tokens, specialist tools, `maxTurns`).
5. **Best cost-to-confidence improvements** — if any check failed, the one-line fix per failure. If everything passed, say so explicitly.
6. **Verdict** — one sentence on whether the current harness is lighter, parity, or heavier than a strong vanilla Claude Code path for small, medium, and large tasks. Base this on `workflow_load_score` and the density of specialist + hook machinery, not on vibes.

## Rules

- `workflow_load_score`: lower is better
- `sdlc_coverage_score`: higher is better (max 1.0)
- `claude_code_compatibility_score`: higher is better (max 1.0)
- `efficiency_index` = `sdlc_coverage_score × claude_code_compatibility_score / max(1, workflow_load_score / 10000)`. Report to 2 decimals.
- No network calls during check execution. Everything is a deterministic read of files already in the repo.
- If a check cannot be performed because a file is missing, report `fail` with the missing path, not `skip`.

## Feedback submission (after every audit)

After printing the full chat report, always offer to submit a redacted copy to the xlfg maintainers' tracker at `flrngel/xlfg` so they can act on the audit. The target repo is fixed — it is always `flrngel/xlfg`, never the user's own repo. That is the point of the feedback loop.

Flow:

1. Run the audit and print the full report to chat (summary table first, detail after).
2. Ask the user one yes/no question, verbatim: `Submit this redacted audit to the xlfg maintainers at flrngel/xlfg so they can improve the harness? (y/n)`
3. Wait for the user's answer.
4. On `n` (or any non-`y` response): print `ok, not submitting.` and stop.
5. On `y`: check `gh auth status`. If it fails, print one warning line (`gh not authenticated — skipping submission`) and stop. Otherwise run the redaction contract, then file the issue. Do not retry on failure; print `gh` stderr verbatim and stop.

Never run step 2 in a non-interactive context where prompting is impossible (e.g., a scripted pipeline with no stdin). If the model cannot ask the user, skip submission silently and end on the chat report.

### Redaction contract (mandatory before filing)

Before handing any text to `gh issue create`, scrub personal information from the report body. The chat output can stay verbose; the issue body must be portable. Apply every rule below:

1. **Home and user paths.** Replace any absolute path that matches `/Users/<name>/...`, `/home/<name>/...`, or `C:\\Users\\<name>\\...` with a repo-relative form. If the path is inside the current repo, strip the prefix up to the repo root (so `/Users/alice/project/xlfg/plugins/...` becomes `plugins/...`). If the path is outside the repo, replace just the user segment: `/Users/<redacted>/...`.
2. **Emails.** Replace any `token@token.tld` with `<email-redacted>`.
3. **Git identity.** Do not include the output of `git config user.name`, `git config user.email`, `git log --format=%an`, `%ae`, `%cn`, `%ce`, or any committer / author string. If the audit body would naturally embed these, drop the field.
4. **Hostnames and machines.** Replace any `hostname`, `uname -n`, or machine-id style string with `<host-redacted>`.
5. **Tokens and secrets.** Reject any line containing `ghp_`, `github_pat_`, `xox[baprs]-`, `sk-`, `AIza`, `AKIA`, `-----BEGIN`, or anything that looks like an API key. If a candidate line is detected, abort the `gh` call and print a warning — do not try to "clean" it; the audit body should not contain secrets in the first place, so a hit means something leaked.
6. **Signed-off-by / Co-authored-by lines.** Strip these entirely.
7. **Repo URLs with user segments.** Leave canonical `github.com/<owner>/<repo>` URLs in place — those are public. Strip any SSH remotes that include a username (`git@host:user/...` other than `git@github.com:...`).

Do the redaction in a scratch variable before invoking `gh`. Show the user a one-line summary of what was redacted (e.g. `redacted: 2 home paths, 1 email, 0 tokens`).

### Issue shape

- title: `xlfg-audit report — v<plugin_version> — <YYYY-MM-DD>`
- body: the full Markdown report from the chat output, AFTER redaction, with the per-check summary table at the top unchanged
- labels: `audit`, `xlfg` (only add labels that already exist in the target repo; let `gh` fail silently on missing labels rather than creating them)

### Invocation

Always file into `flrngel/xlfg`. The target is hardcoded; there is no per-user override. Use `gh issue create` with a heredoc so the body preserves Markdown:

```bash
gh issue create \
  --repo flrngel/xlfg \
  --title "xlfg-audit report — v<version> — <date>" \
  --body-file <(cat <<'EOF'
<redacted report>
EOF
) \
  --label audit --label xlfg
```

On success, print the issue URL that `gh` returns so the user can see where the feedback went. On failure, print the `gh` stderr verbatim and keep the chat report — do not retry.
