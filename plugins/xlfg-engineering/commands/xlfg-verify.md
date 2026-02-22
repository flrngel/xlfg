---
name: xlfg:verify
description: Run tests/lint/build and write evidence to docs/xlfg + .xlfg.
argument-hint: "[run-id | latest]"
---

# /xlfg:verify

Run verification commands (tests / lint / typecheck / build) and save evidence.

> Tip: If you have the `xlfg` CLI installed, `xlfg verify --mode full` writes logs and updates `docs/xlfg/runs/<run-id>/verification.md` automatically.


<input>#$ARGUMENTS</input>

## 1) Select run

- If argument is `latest` or empty: pick the newest folder under `docs/xlfg/runs/`.
- Otherwise, treat argument as the run-id folder name.

Define:

- `DOCS_RUN_DIR=docs/xlfg/runs/<run-id>`
- `DX_RUN_DIR=.xlfg/runs/<run-id>`

Ensure these exist.

## 2) Decide verification commands

Prefer repo-native commands in this order:

1. `Makefile` targets (`make test`, `make lint`, `make ci`)
2. `package.json` scripts (`test`, `lint`, `typecheck`, `build`)
3. Language defaults (only if the repo clearly matches):
   - Python: `pytest`, `ruff`, `mypy`
   - Go: `go test ./...`, `go vet ./...`
   - Rust: `cargo test`, `cargo clippy`
   - Ruby: `bundle exec rspec` or `bin/rails test`

If unclear, ask the user **once** for the canonical commands (copy from README/CONTRIBUTING).

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
