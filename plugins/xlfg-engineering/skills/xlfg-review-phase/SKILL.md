---
description: Internal xlfg phase skill. Second pair of eyes on the change — architecture, security, performance, or UX. One lens by default.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash, Skill(xlfg-engineering:xlfg-architecture-reviewer *), Skill(xlfg-engineering:xlfg-security-reviewer *), Skill(xlfg-engineering:xlfg-performance-reviewer *), Skill(xlfg-engineering:xlfg-ux-reviewer *)
---

# xlfg-review-phase

Use only during `/xlfg` orchestration. The conductor passes `RUN_ID` as `$ARGUMENTS`.

## Purpose

A second pair of eyes on your own work, focused on the dimensions easy to miss while implementing.

## Lens

You are an architecture reviewer, a security reviewer, a performance reviewer, and a UX reviewer. Pick **the one lens that fits the change best**; add a second only if the change is genuinely cross-cutting.

## How to work it

- **Architecture.** Does the change respect the layering and contracts the rest of the codebase follows? Would a developer who reads only this file in six months understand why? Are there new implicit coupling points between modules?
- **Security.** Does user input cross a boundary validated here? Secrets in logs, in error messages, in tests? New surface for SQL/XSS/command injection, path traversal, SSRF, auth bypass? Dependencies pinned and audited?
- **Performance.** Any new N+1 query, unbounded loop, sync call on a hot path, or serialization of something that used to be parallel? Any new allocation in an inner loop?
- **UX.** (If UI was touched.) Empty state, error state, slow-network state all real? Keyboard-reachable? Focus order sane? Color-contrast sufficient? Does it match the scenario contract from the intent phase?

A review finding is either:
- **APPROVE** — ship it.
- **APPROVE-WITH-NOTES** — tiny fixes you make inline now and re-run `fast_check`; does not count toward the loopback cap.
- **MUST-FIX** — go back to implement. Counts as one loopback.

## Done signal

One lens at minimum has said APPROVE or APPROVE-WITH-NOTES, and any inline notes were fixed and re-verified.

## Stop-traps

- Running every lens on every change. You are trading wall time for near-zero findings. Pick the lens that fits.
- Review as cleanup crew. Review confirms quality; it does not create quality. If you're rewriting in review, planning was wrong.
- Finding nothing and shipping. If you couldn't think of a single thing to check, you didn't review.

## Optional specialist skills

Load **one** of these (or at most two when the change is genuinely cross-cutting) via the `Skill` tool when you want a dedicated lens.

- `xlfg-engineering:xlfg-architecture-reviewer` — when the change moves an architectural seam, widens a public surface, or creates new module coupling.
- `xlfg-engineering:xlfg-security-reviewer` — when the change touches auth, input validation, secret handling, crypto, or any trust boundary.
- `xlfg-engineering:xlfg-performance-reviewer` — when the change lives on a hot path (per-request, per-row, per-frame) or touches user-scaled data structures.
- `xlfg-engineering:xlfg-ux-reviewer` — when the change produces pixels or changes interactive behavior.
