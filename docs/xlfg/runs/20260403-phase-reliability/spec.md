# Spec — 20260403-phase-reliability

## Intent contract

**Request:** Fix the /xlfg phase-skipping problem: the 8-phase pipeline sometimes does not run all phases because the conductor can stop with no enforcement. Implement a solution confined to the conductor layer with no side effects on specialists or phase skills. Bump version to 2.8.0.

**Resolution:** proceed

### Direct asks
- Q1: Add a Stop hook on the main conductor to block premature pipeline termination
- Q2: Add a machine-readable phase-progression state file that the Stop hook reads
- Q3: Cap loopback iterations (verify RED, review must-fix) to prevent unbounded context growth
- Q4: Bump version to 2.8.0 across all version files

### Implied asks
- I1: No side effects — existing specialist agents, subagent stop guard, and phase skill content must remain unchanged
- I2: The fix must work in both standalone and plugin packs (keep them synchronized)
- I3: Changes confined to conductor layer only: main SKILL.md + new hook file(s) + version files

### Acceptance criteria
- A1: Stop hook blocks the conductor from ending before all 8 phases complete (reads phase state file)
- A2: Phase state file is written by the conductor after each phase skill returns (JSON in `.xlfg/`)
- A3: Loopback cycles have max 2 iterations with escalation to user after cap
- A4: All version files read 2.8.0
- A5: Existing tests pass; no existing specialist or phase skill behavior changes
- A6: New tests cover the new hook and state file logic

### Non-goals
- Changing specialist agent behavior, turn budgets, or tool allowlists
- Changing phase skill SKILL.md content
- Adding database-backed state or external dependencies
- Changing the foreground specialist execution model
- Changing the subagent stop guard

### Requested constraints
- "Think carefully that it should not make a side-effect" — the user explicitly wants a non-invasive fix
- The existing `xlfg-subagent-stop-guard.mjs` pattern is the proven hook mechanism — follow it

### Assumptions
- Claude Code Stop hooks in skill frontmatter use the same block/allow JSON protocol as SubagentStop hooks
- The conductor can write a phase-state JSON file between phase skill invocations
- Phase skills don't need to know about the state file — only the conductor and Stop hook interact with it

### Blocking ambiguities
None.

### Carry-forward anchor
The fix adds two things to the conductor: (1) a Stop hook that reads a phase-state file and blocks if incomplete, (2) instructions to write that state file after each phase. Plus a loopback cap in the internal loop rules. Nothing else changes.

## Objective groups

- O1: Phase-progression state file — covers Q2, A2
- O2: Stop hook for conductor — covers Q1, A1. depends_on: O1
- O3: Loopback iteration cap — covers Q3, A3
- O4: Version bump to 2.8.0 — covers Q4, A4

## Outcome / why

The /xlfg pipeline sometimes silently drops later phases (review, compound) because the model can stop at any time with no enforcement. The v2.7.x arc hardened specialists; v2.8.0 hardens the conductor itself.

## False-success trap

Claiming the fix works because tests pass, when in reality the Stop hook never fires during a real run or the phase state file is never read by the hook.

## Recall summary

- No prior runs or durable knowledge exists. First real xlfg run.
- SubagentStop hook pattern (`xlfg-subagent-stop-guard.mjs`) is established — reuse for conductor Stop hook.

## Research and context

- Stop hooks use same block/allow JSON protocol as SubagentStop
- Stop hooks CAN be registered in skill/command frontmatter (only active while skill is loaded)
- `stop_reason` field: `"end_turn"` (normal stop), `"max_tokens"` (hard limit), `"tool_use"` (about to use tool)
- No `stop_hook_active` for Stop hooks — need own safety valve via block_count in phase-state file
- Plugin hooks go in `hooks/hooks.json` + `scripts/`. Standalone hooks go in `.claude/hooks/`
- Must always allow stopping on `stop_reason: "max_tokens"`
- Audit module needs new feature flag for conductor stop gate

## Chosen solution

### Phase-state file (`.xlfg/phase-state.json`)

The conductor writes this JSON after startup and updates it after each phase:

```json
{
  "run_id": "20260403-example",
  "phases": ["recall","intent","context","plan","implement","verify","review","compound"],
  "completed": ["recall","intent"],
  "loopback_count": 0,
  "max_loopbacks": 2,
  "block_count": 0
}
```

### Stop hook (`xlfg-phase-gate.mjs`)

Reads stdin payload → reads `.xlfg/phase-state.json` → decides:
1. If `stop_reason` is `"max_tokens"` → always allow (exit 0)
2. If no phase-state file → allow (not in an xlfg run)
3. If all 8 phases in `completed` → allow (run is done)
4. If `block_count >= 3` → allow (safety valve to prevent infinite loop)
5. Otherwise → increment `block_count`, write back, block with reason naming the next incomplete phase

### Loopback cap

Internal loop rules get `(max 2 loopbacks)` after each loop instruction. After 2 loops, escalate to user.

### Rejected shortcuts
- Inline hook logic in SKILL.md frontmatter: too complex for a one-liner echo command
- hooks.json-only registration: would fire for ALL stops, not just during /xlfg runs
- Modifying phase skills to write state: violates the conductor-only constraint

## Execution shape

Sequential tasks. No parallelism needed — each file change is small and depends on the shared design.

## Verify mode

Automated: `python -m pytest tests/` must pass. Manual: verify new hook script blocks correctly via test.

## Task map

| Task | Objective | Scope | primary_artifact | done_check |
|---|---|---|---|---|
| T1: Create phase-gate hook script | O1, O2 | `standalone/.claude/hooks/xlfg-phase-gate.mjs`, `plugins/xlfg-engineering/scripts/phase-gate.mjs` | `standalone/.claude/hooks/xlfg-phase-gate.mjs` | Script exists, reads stdin, reads phase-state, blocks/allows correctly |
| T2: Update standalone SKILL.md | O1, O2, O3 | `standalone/.claude/skills/xlfg/SKILL.md` | same | Frontmatter has Stop hook; body has phase-state tracking + loopback cap |
| T3: Update plugin command xlfg.md | O1, O2, O3 | `plugins/xlfg-engineering/commands/xlfg.md` | same | Same changes as T2, plugin paths |
| T4: Update plugin hooks.json | O2 | `plugins/xlfg-engineering/hooks/hooks.json` | same | Stop hook entry exists |
| T5: Update audit.py | O2 | `xlfg/audit.py` | same | `conductor_stop_gate` feature detected |
| T6: Version bump | O4 | 8 version files | `xlfg/__init__.py` | All files show 2.8.0, version sync test passes |
| T7: Add phase-gate tests | O1, O2 | `tests/test_phase_gate.py` | same | Tests cover block-when-incomplete, allow-when-done, allow-on-max-tokens, safety-valve |
| T8: Update existing tests | O2, O4 | `tests/test_xlfg.py` | same | New audit feature + entrypoint checks pass |

## Proof summary

**GREEN** — 51/51 tests pass. All 5 scenario contracts proved. Review found and fixed one must-fix (plugin double-registration). Re-verified after fix.

## PM / UX / Engineering / QA / Release notes

- **PM**: Pipeline reliability improvement — /xlfg now has hard enforcement against dropping phases
- **Engineering**: New files: `phase-gate.mjs` (standalone + plugin), updated conductors, hooks.json, audit.py. No phase skill or specialist changes.
- **QA**: 8 new tests for phase-gate hook, 43 existing tests unchanged. 51/51 green.
- **Release**: v2.8.0. Backwards compatible — no existing behavior changes. The Stop hook is purely additive.
