#!/usr/bin/env node
// Transitional no-op. Existing Claude Code sessions cached the v5.0.0
// hooks.json wiring that spawned this file via `node ...phase-gate.mjs`.
// v5.1.0 moved the hook to python3 ...phase_gate.py; v6.0.0 removes the
// Stop hook entirely. This stub exists so cached sessions do not keep
// erroring with "Cannot find module" until they restart and reload
// hooks.json. Safe to delete after users have cycled their sessions.
process.stdin.resume();
process.stdin.on("data", () => {});
process.stdin.on("end", () => process.exit(0));
// Fallback for runtimes that never emit data: still exit cleanly.
setImmediate(() => process.exit(0));
