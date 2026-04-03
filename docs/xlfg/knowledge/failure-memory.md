# xlfg failure memory

Recurring unexpected failures and proven responses.

## Failure signature: Pipeline drops later phases

- **Observed symptom**: /xlfg run completes after implement or verify phase without running review or compound
- **Detection signal**: `workboard.md` shows review/compound as PENDING at end of run
- **Likely root cause**: Context pressure causes the model to generate a completion summary instead of invoking the next phase skill. No enforcement mechanism prevented stopping.
- **Immediate fix**: v2.8.0 added a Stop hook (`phase-gate.mjs`) that reads `.xlfg/phase-state.json` and blocks if incomplete phases remain
- **Prevention rule**: Always write phase-state JSON after startup and update it after each phase. The Stop hook is the hard enforcement layer.
- **Verification after fix**: 51/51 tests pass including 8 new phase-gate tests (block-when-incomplete, allow-when-done, max_tokens, safety-valve)
- **Links**: run 20260403-phase-reliability
