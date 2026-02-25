---
name: xlfg:verify
description: Run tests/lint/build and write evidence to docs/xlfg + .xlfg.
argument-hint: "[run-id | latest] [fast|full]"
---

# /xlfg:verify

Run verification commands (tests / lint / typecheck / build) and save evidence.

> Tip: If you have the `xlfg` CLI installed, `xlfg verify --mode full` writes logs and updates `docs/xlfg/runs/<run-id>/verification.md` automatically.


<input>#$ARGUMENTS</input>

## 0) Parse arguments

Treat arguments as:

- First token: `run-id` (or `latest`)
- Optional second token: `fast` or `full`

Default mode: `full`.

## 1) Select run

- If argument is `latest` or empty: pick the newest folder under `docs/xlfg/runs/`.
- Otherwise, treat argument as the run-id folder name.

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Ensure these exist.

## 2) Decide verification commands

### Non-interactive / anti-hang rules (important)

Some test runners default to **watch mode** or wait forever for user input. This is the most common reason `/xlfg` runs exceed 30 minutes.

When running Node-based verification, prefer setting `CI=1` (disables watch mode in many frameworks). If a command still hangs, switch to an explicit non-watch flag if supported (e.g., `--watch=false`, `--watchAll=false`).

If your environment supports it, wrap long-running commands with a timeout (example: `timeout 20m <cmd>`).

### Fast vs full

- **fast:** lint/format/typecheck only (tight iteration loop)
- **full:** fast + unit/integration tests + build

Prefer repo-native commands in this order:

1. `Makefile` targets (`make test`, `make lint`, `make ci`)
2. `package.json` scripts (`test`, `lint`, `typecheck`, `build`)
3. Language defaults (only if the repo clearly matches):
   - Python: `pytest`, `ruff`, `mypy`
   - Go: `go test ./...`, `go vet ./...`
   - Rust: `cargo test`, `cargo clippy`
   - Ruby: `bundle exec rspec` or `bin/rails test`

If unclear, ask the user **once** for the canonical commands (copy from README/CONTRIBUTING).

If you discover the canonical commands, consider recording them in `docs/xlfg/knowledge/commands.json` so future runs are deterministic.

## 3) Map phase: execute via verify runner subagent

Run Task `xlfg-verify-runner` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- Ordered verification commands (exact strings)

Runner responsibilities:

- Create `DX_RUN_DIR/verify/<YYYYMMDD-HHMMSS>/`
- Execute commands with `set -o pipefail` + `tee`
- Write per-command logs and exitcodes
- Write aggregate artifacts:
  - `DX_RUN_DIR/verify/<ts>/results.json`
  - `DX_RUN_DIR/verify/<ts>/summary.md`

Runner execution pattern:

```bash
set -o pipefail
<cmd> 2>&1 | tee "$DX_RUN_DIR/verify/<ts>/<name>.log"
echo $? > "$DX_RUN_DIR/verify/<ts>/<name>.exitcode"
```

## 4) Reduce phase: write canonical verification artifacts

Run Task `xlfg-verify-reducer` with:

- `DOCS_RUN_DIR`
- `DX_RUN_DIR`
- Runner timestamp or results path

Reducer responsibilities:

- Read `results.json` + summary + referenced logs as needed
- Write `DOCS_RUN_DIR/verification.md`
- If RED, also write `DOCS_RUN_DIR/verify-fix-plan.md` with the first actionable failure and minimum fix steps

Lead-agent rule:

- Do not parse full raw logs unless reducer output is insufficient.

## 5) If failing, iterate until green

- Treat red verification as a hard stop.
- Use `DOCS_RUN_DIR/verify-fix-plan.md` as the default fix plan.
- Implement the minimum fixes.
- Re-run verification.

Only declare success when the full verification set is green.
