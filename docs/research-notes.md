# Research notes behind xlfg 2.0.2

This revision tightened four ideas.

## 1) Bootstrap should be cheap; long runs should carry the cost
A repo that is already prepared should not pay a full init tax every run. xlfg now prefers a fast **prepare / migrate** check and only applies scaffold changes when the version drifts.

## 2) Dual-set verification must be defined from the requirement doc, not improvised late
The testing contract should explicitly map new requirements (F2P) and preserved behavior (P2P) before implementation. That is why flow specs, test contracts, and scorecards are seeded before coding.

## 3) Role memory beats one giant summary file
Certain roles hit the same failures repeatedly: diagnosis, test strategy, env setup, reduction of failures, and UX review. xlfg now keeps compact, role-specific memory files so those lessons remain retrievable without bloating every agent prompt.

## 4) Runs are episodic memory, not durable knowledge
Run folders are valuable locally, but the durable artifact should be the promoted lesson in `knowledge/`, not the full run log. That is why `docs/xlfg/runs/` is local-only by default.
