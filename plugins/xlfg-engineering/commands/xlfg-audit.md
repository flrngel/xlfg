---
description: Post-mortem of the latest /xlfg run. Shows local phase timing detail, then offers to submit a project-free xlfg efficiency report to flrngel/xlfg.
disable-model-invocation: true
allowed-tools: Read, Bash
effort: medium
---

# xlfg audit (per-run post-mortem)

`/xlfg-audit` answers two questions about the **most recent `/xlfg` or `/xlfg-debug` run** in this project:

1. Where did the time go? (per-phase wall time, loopbacks, artifact volume)
2. How could xlfg have been faster or leaner here? (concrete suggestions tied to actual data)

This command does **not** run the harness self-check — that lives in `scripts/audit-harness.mjs` and runs in CI on every PR. The local post-mortem is for the user who just spent 45 minutes on a run and wants to know why. The upstream submission is a separate public xlfg efficiency report derived from the same metrics.

Takes one optional argument: a specific `RUN_ID`. Defaults to the latest run in `docs/xlfg/runs/`.

INPUT: `$ARGUMENTS`

## Step 1 — Run the post-mortem script

The whole report is produced by a deterministic script. Do not attempt to compute timings, totals, or suggestions from prose — invoke the script and print its output verbatim.

```bash
if [ -n "$ARGUMENTS" ]; then
  node "${CLAUDE_PLUGIN_ROOT}/scripts/post-mortem.mjs" --run "$ARGUMENTS"
else
  node "${CLAUDE_PLUGIN_ROOT}/scripts/post-mortem.mjs"
fi
```

The script:

- finds the latest run dir (or the one named in `$ARGUMENTS`)
- reads `phase-timings.jsonl` (recorded by the conductor on every phase boundary; absent on runs older than v4.2.0)
- reads `phase-state.json` (when still present from a live or recently-completed run)
- lists every artifact in the run dir with its size
- pulls ledger entries whose `run` matches this run id
- emits a Markdown report with: summary, per-phase table (status / wall time / invocations / artifact count / bytes), and a "How xlfg can be better" list driven by deterministic heuristics over the data

If the script exits 3, no run dir exists — print a one-liner saying so and stop.

## Step 2 — Offer to submit public xlfg efficiency feedback

After the post-mortem prints, ask the user verbatim:

```
Submit a project-free xlfg efficiency report to the xlfg maintainers at flrngel/xlfg so they can improve the harness? (y/n)
```

Wait for the answer.

- On `n` (or any non-`y` response): print `ok, not submitting.` and stop.
- On `y`: check `gh auth status`. If it fails, print one warning line (`gh not authenticated — skipping submission`) and stop. Otherwise generate the public report, apply the safety contract below, then file the issue. Do not retry on failure; print `gh` stderr verbatim and stop.

Skip step 2 silently in non-interactive contexts where prompting is impossible.

The submission target is **always `flrngel/xlfg`**. There is no per-user override. The point of submitting is to give the xlfg maintainers concrete run-shape data — phase timings, slow lanes, loopback counts, artifact volume — so they can tune xlfg without seeing or debugging the user's project.

## Public report generation

Do **not** file the local chat report. Generate a purpose-built public report from the deterministic script:

```bash
if [ -n "$ARGUMENTS" ]; then
  node "${CLAUDE_PLUGIN_ROOT}/scripts/post-mortem.mjs" --public --run "$ARGUMENTS"
else
  node "${CLAUDE_PLUGIN_ROOT}/scripts/post-mortem.mjs" --public
fi
```

The public report is the only allowed issue body. It intentionally contains only:

- xlfg run timestamp without the request slug
- command mode (`/xlfg` or `/xlfg-debug`)
- total wall time, loopback count, timing presence
- phase names, status, wall time, invocation count, artifact count, and artifact byte totals
- ledger event counts by enum
- deterministic harness feedback categories such as `slow_phase`, `dominant_phase`, `phase_rerun`, `loopback`, `large_artifacts`, `missing_timings`, and `incomplete_phase_state`

It must not contain user request text, the `RUN_ID` slug, repo names, branch names, remotes, paths, artifact filenames, artifact contents, source filenames, command text, command output, test output, product names, customer names, ledger summaries, ledger symptoms, ledger root causes, ledger evidence paths, or any free text copied from run artifacts.

## Redaction contract (mandatory safety net before filing)

The public report should be privacy-by-construction. Before handing any text to `gh issue create`, still run this safety check. If any rule finds a forbidden value, prefer aborting the `gh` call over trying to clean it. The local chat output can stay verbose; the issue body must be portable. Apply every rule below:

1. **Run slug.** The issue body and title must never include the slug from `RUN_ID` (`<YYYYMMDD>-<HHMMSS>-<slug>`). Use only `<YYYYMMDD>-<HHMMSS>` or `<slug-redacted>`.
2. **Paths.** Reject any absolute path matching `/Users/<name>/...`, `/home/<name>/...`, or `C:\\Users\\<name>\\...`. Reject repo-relative paths such as `docs/xlfg/runs/...`, source paths, test paths, and artifact paths. The public report should not need paths.
3. **Emails.** Reject any `token@token.tld`.
4. **Git identity.** Do not include the output of `git config user.name`, `git config user.email`, `git log --format=%an`, `%ae`, `%cn`, `%ce`, or any committer / author string. If the report would naturally embed these, drop the field.
5. **Hostnames and machines.** Reject any `hostname`, `uname -n`, or machine-id style string.
6. **Tokens and secrets.** Reject any line containing `ghp_`, `github_pat_`, `xox[baprs]-`, `sk-`, `AIza`, `AKIA`, `-----BEGIN`, or anything that looks like an API key. If a candidate line is detected, abort the `gh` call and print a warning — do not try to "clean" it.
7. **Signed-off-by / Co-authored-by lines.** Strip these entirely.
8. **Repo URLs and remotes.** Reject `github.com/`, `git@`, `ssh://`, and `https://` remote-looking strings. The public report should not include repository identity.

Do the safety check in a scratch variable before invoking `gh`. Show the user a one-line summary (for example, `public report checked: slug omitted, 0 paths, 0 emails, 0 tokens`).

## Issue shape

- title: `xlfg efficiency report — v<plugin_version> — <YYYYMMDD-HHMMSS>`
- body: the full Markdown output from `post-mortem.mjs --public`, after the safety check, with the per-phase table unchanged
- labels: `audit`, `xlfg` (only add labels that already exist in the target repo; let `gh` fail silently on missing labels rather than creating them)

## Invocation

Always file into `flrngel/xlfg`. The target is hardcoded. Use a heredoc so the body preserves Markdown:

```bash
gh issue create \
  --repo flrngel/xlfg \
  --title "xlfg efficiency report — v<version> — <YYYYMMDD-HHMMSS>" \
  --body-file <(cat <<'EOF'
<public report>
EOF
) \
  --label audit --label xlfg
```

On success, print the issue URL that `gh` returns. On failure, print the `gh` stderr verbatim and keep the chat report — do not retry.
