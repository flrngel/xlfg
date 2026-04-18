#!/usr/bin/env node
// Transitional no-op. See phase-gate.mjs for why this stub exists.
// Removed in the v6.0.0 line once cached sessions cycle.
process.stdin.resume();
process.stdin.on("data", () => {});
process.stdin.on("end", () => process.exit(0));
setImmediate(() => process.exit(0));
