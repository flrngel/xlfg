#!/usr/bin/env node
// Compat shim for cached v5.0.0 sessions. See phase-gate.mjs for the full
// rationale. Keep this file until all v5.0.0-era cached sessions have
// cycled — it's 11 lines and it silently unblocks anyone still running one.
process.stdin.resume();
process.stdin.on("data", () => {});
process.stdin.on("end", () => process.exit(0));
setImmediate(() => process.exit(0));
