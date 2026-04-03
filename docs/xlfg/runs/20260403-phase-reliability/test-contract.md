# Test Contract — 20260403-phase-reliability

## S1: Phase-gate blocks when phases are incomplete

**Objective:** O1, O2
**Given:** `.xlfg/phase-state.json` exists with `completed: ["recall","intent"]` (only 2 of 8)
**When:** Stop hook receives `{"stop_reason": "end_turn", "cwd": "<tmpdir>"}`
**Then:** Hook outputs `{"decision": "block", "reason": "..."}` naming the next incomplete phase; block_count is incremented in the state file
**Proof method:** subprocess test calling the hook script directly (same pattern as `test_subagent_stop_guard.py`)

## S2: Phase-gate allows when all phases complete

**Objective:** O1, O2
**Given:** `.xlfg/phase-state.json` exists with all 8 phases in `completed`
**When:** Stop hook receives `{"stop_reason": "end_turn", "cwd": "<tmpdir>"}`
**Then:** Hook exits 0 with no stdout (allow)
**Proof method:** subprocess test

## S3: Phase-gate allows on max_tokens

**Objective:** O2
**Given:** `.xlfg/phase-state.json` exists with incomplete phases
**When:** Stop hook receives `{"stop_reason": "max_tokens", "cwd": "<tmpdir>"}`
**Then:** Hook exits 0 with no stdout (allow — model can't continue anyway)
**Proof method:** subprocess test

## S4: Phase-gate safety valve after 3 blocks

**Objective:** O2
**Given:** `.xlfg/phase-state.json` exists with `block_count: 3` and incomplete phases
**When:** Stop hook receives `{"stop_reason": "end_turn", "cwd": "<tmpdir>"}`
**Then:** Hook exits 0 with no stdout (safety valve — prevent infinite blocking)
**Proof method:** subprocess test

## S5: Version sync

**Objective:** O4
**Given:** All version files updated
**When:** `test_versions_are_synced_across_package_and_plugin_manifests` runs
**Then:** All manifests report 2.8.0
**Proof method:** existing test suite
