# xlfg decision log

Record durable architectural and product decisions made during `/xlfg` runs.

## Template

- **Date**:
- **Decision**:
- **Context**:
- **Alternatives considered**:
- **Rejected shortcut**:
- **Consequences**:
- **Links**: (run folder, PR, issues)

---

## 2026-04-14 — Specialist `maxTurns` raised from 12 to 150 (ceiling, not target)

- **Date**: 2026-04-14
- **Decision**: Set every specialist agent's `maxTurns` to `150` across both the plugin pack (`plugins/xlfg-engineering/agents/`) and the standalone pack (`standalone/.claude/agents/`). Update the audit predicate (`xlfg/audit.py:_short_turn_budget`) and the test assertion (`tests/test_xlfg.py`) to assert the new ceiling. Bump version to **2.9.0**.
- **Context**: A previous `/xlfg-debug` run (`docs/xlfg/runs/20260414-073242-maxturns-decision/`) reconstructed the maxTurns history:
  - `050f0e0` v2.7.3 (2026-03-30) — established bounded-budget design (8 → 12), with prompt-side "write-first" rule and lean Context sources.
  - `b386280` v2.7.4 (2026-03-31) — plugin pack only bumped to `maxTurns: 100` and `effort: high`. Empty commit body. No CHANGELOG entry. Reverted next day.
  - `9ec40a2` v2.7.5 (2026-04-01) — rolled plugin pack back to bounded values (8/10/12), declared specialists leaf workers, added audit + tests asserting short turn budgets.
  After hearing the documented risks of removing the bounded-budget forcing function, the user explicitly chose to override the v2.7.5 design: *"go with option 1 and make ci not break it. okay? it's not 'min turns', sub-agents will figure it out in most cases, and they are sonnet, so much cheaper. okay?"*
- **Alternatives considered**:
  - Targeted raise (only the few lanes that actually need more headroom) — kept the forcing function where it mattered. **Rejected** by user in favor of a uniform ceiling for simplicity.
  - Cancel and only document history — preserved the v2.7.5 design. **Rejected**: the user wanted the headroom.
  - Patch bump (2.8.3) — **rejected**: the bounded-budget rationale was load-bearing in v2.7.5; reversing it changes the design contract, so a minor bump (2.9.0) is more honest.
- **Rejected shortcut**: deleting the audit `_short_turn_budget` predicate to silence the failing CI assertion. Would have falsely greened `short_lived_specialists` in the audit forever. The predicate's *meaning* stays (specialists are bounded); only the numeric bound rises.
- **Consequences**:
  - 150 is a **ceiling, not a target**. Specialists are still expected to finish in far fewer turns most of the time. The prompt-side write-first / leaf-worker / atomic-packet rules now carry the full forcing-function load that the small numeric cap previously shared.
  - At 150, a stuck specialist looping on speculative reads will appear hung for far longer before failing. Mitigation: prompt-side rules + SubagentStop guard + missing-artifact detection. If real runs surface a 100+ turn lane, that is a signal the lane was scoped wrong, not a signal to raise the cap further.
  - Cost: worst-case Sonnet specialist invocation can now consume up to ~12.5× more turns than at the previous 12-turn cap. Acceptable per the user's framing ("they are sonnet, so much cheaper").
  - CI stays green via the predicate/test bound update, not via removing coverage.
  - Plugin and standalone packs remain in sync (no recurrence of the v2.7.4 plugin-only drift).
- **Links**: run `docs/xlfg/runs/20260414-074853-maxturns-150/`; predecessor diagnosis `docs/xlfg/runs/20260414-073242-maxturns-decision/debug-report.md`; commits `050f0e0`, `b386280`, `9ec40a2` (history) and the 2.9.0 commit for this change.
