#!/usr/bin/env node
// Compat shim for cached v5.0.0 sessions.
//
// v5.0.0 wired the Stop hook to `node ${CLAUDE_PLUGIN_ROOT}/scripts/phase-gate.mjs`.
// Claude Code caches hooks.json at session start, so sessions that loaded
// the v5.0.0 wiring keep spawning this path even after the plugin upgraded
// to v5.1.0 (Python port) and then v6.0.0 (hook removed entirely).
//
// Without this file, every Stop event in those cached sessions emits a
// "Cannot find module" error. The error is non-blocking but noisy enough
// to bury real output.
//
// This shim reads stdin, ignores it, and exits 0. Safe to delete once all
// v5.0.0 sessions have cycled — but it's 11 lines; keeping it permanently
// costs nothing.
process.stdin.resume();
process.stdin.on("data", () => {});
process.stdin.on("end", () => process.exit(0));
setImmediate(() => process.exit(0));
