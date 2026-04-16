---
description: Post-mortem of the latest /xlfg run. Per-phase breakdown of wall time, loopbacks, artifacts, and concrete suggestions for how xlfg can be better. Offers to submit the redacted report to flrngel/xlfg.
disable-model-invocation: true
allowed-tools: Read, Bash
effort: medium
---

# xlfg audit (per-run post-mortem)

`/xlfg-audit` answers two questions about the **most recent `/xlfg` or `/xlfg-debug` run** in this project:

1. Where did the time go? (per-phase wall time, loopbacks, artifact volume)
2. How could xlfg have been faster or leaner here? (concrete suggestions tied to actual data)

This command does **not** audit the harness itself — that lives in `scripts/audit-harness.mjs` and runs in CI on every PR. The harness self-check is a maintainer concern; the post-mortem is for the user who just spent 45 minutes on a run and wants to know why.

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

## Step 2 — Offer to submit the report to the xlfg maintainers

After the post-mortem prints, ask the user verbatim:

```
Submit this redacted post-mortem to the xlfg maintainers at flrngel/xlfg so they can improve the harness? (y/n)
```

Wait for the answer.

- On `n` (or any non-`y` response): print `ok, not submitting.` and stop.
- On `y`: check `gh auth status`. If it fails, print one warning line (`gh not authenticated — skipping submission`) and stop. Otherwise apply the redaction contract below, then file the issue. Do not retry on failure; print `gh` stderr verbatim and stop.

Skip step 2 silently in non-interactive contexts where prompting is impossible.

The submission target is **always `flrngel/xlfg`**. There is no per-user override. The point of submitting is to give the xlfg maintainers concrete real-run data — phase timings, slow lanes, loopback counts — so they can tune the harness for the workloads it actually sees.

## Redaction contract (mandatory before filing)

Before handing any text to `gh issue create`, scrub personal information from the report body. The chat output can stay verbose; the issue body must be portable. Apply every rule below:

1. **Home and user paths.** Replace any absolute path that matches `/Users/<name>/...`, `/home/<name>/...`, or `C:\\Users\\<name>\\...` with a repo-relative form. If the path is inside the current repo, strip the prefix up to the repo root. If the path is outside the repo, replace just the user segment: `/Users/<redacted>/...`.
2. **Emails.** Replace any `token@token.tld` with `<email-redacted>`.
3. **Git identity.** Do not include the output of `git config user.name`, `git config user.email`, `git log --format=%an`, `%ae`, `%cn`, `%ce`, or any committer / author string. If the report would naturally embed these, drop the field.
4. **Hostnames and machines.** Replace any `hostname`, `uname -n`, or machine-id style string with `<host-redacted>`.
5. **Tokens and secrets.** Reject any line containing `ghp_`, `github_pat_`, `xox[baprs]-`, `sk-`, `AIza`, `AKIA`, `-----BEGIN`, or anything that looks like an API key. If a candidate line is detected, abort the `gh` call and print a warning — do not try to "clean" it; the post-mortem body should not contain secrets in the first place, so a hit means something leaked from a run artifact.
6. **Signed-off-by / Co-authored-by lines.** Strip these entirely.
7. **Run-slug content.** The `RUN_ID` is `<YYYYMMDD>-<HHMMSS>-<slug>`. The slug came from the user's request and may contain product names or identifiers. If the slug looks sensitive (contains words like `secret`, `internal`, `prod`, `customer`, a likely email/username token, or a hyphen-separated string >40 chars), replace it with `<slug-redacted>` in the title and body. When in doubt, redact.
8. **Repo URLs with user segments.** Leave canonical `github.com/<owner>/<repo>` URLs in place — those are public. Strip any SSH remotes that include a username (`git@host:user/...` other than `git@github.com:...`).

Do the redaction in a scratch variable before invoking `gh`. Show the user a one-line summary of what was redacted (e.g. `redacted: 1 home path, 0 emails, 0 tokens, slug kept`).

## Issue shape

- title: `xlfg post-mortem — v<plugin_version> — <RUN_ID-or-redacted-slug>`
- body: the full Markdown report from the post-mortem, AFTER redaction, with the per-phase table at the top unchanged
- labels: `audit`, `xlfg` (only add labels that already exist in the target repo; let `gh` fail silently on missing labels rather than creating them)

## Invocation

Always file into `flrngel/xlfg`. The target is hardcoded. Use a heredoc so the body preserves Markdown:

```bash
gh issue create \
  --repo flrngel/xlfg \
  --title "xlfg post-mortem — v<version> — <run-id-or-redacted>" \
  --body-file <(cat <<'EOF'
<redacted report>
EOF
) \
  --label audit --label xlfg
```

On success, print the issue URL that `gh` returns. On failure, print the `gh` stderr verbatim and keep the chat report — do not retry.
