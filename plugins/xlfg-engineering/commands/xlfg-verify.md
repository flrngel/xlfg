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

## 3) Execute and log (evidence-first)

Create a timestamped log dir:

- `DX_RUN_DIR/verify/<YYYYMMDD-HHMMSS>/`

For each command:

- Run it
- Pipe full output to a log file via `tee`
- Record the exit code

Example pattern:

```bash
set -o pipefail
<cmd> 2>&1 | tee "$DX_RUN_DIR/verify/<ts>/<name>.log"
echo $? > "$DX_RUN_DIR/verify/<ts>/<name>.exitcode"
```

## 4) Write `verification.md`

In `DOCS_RUN_DIR/verification.md`, record:

- The commands run (exact)
- Exit codes
- Where logs live
- If failures occurred: the **first actionable failure** (not a flood of cascaded errors)

## 5) If failing, iterate until green

- Treat red verification as a hard stop.
- Create a short fix plan in the run folder.
- Implement the minimum fixes.
- Re-run verification.

Only declare success when the full verification set is green.
