#!/usr/bin/env node
// xlfg phase-tick — record a single phase boundary event into the
// run-local timings log so the post-mortem can compute per-phase wall
// time honestly, including loopbacks.
//
// Each invocation appends one JSONL line:
//   {"run":"<RUN_ID>","phase":"<name>","event":"start|end","ts":"<ISO8601Z>"}
//
// Output file: docs/xlfg/runs/<RUN_ID>/phase-timings.jsonl
//
// The conductor brackets every phase Skill call with two ticks
// (start before, end after). Loopbacks produce additional pairs for
// the same phase — the post-mortem sums them.
//
// Usage:
//   node phase-tick.mjs --run <RUN_ID> --phase <name> --event <start|end>
//
// Exits 0 on success, 2 on bad args. Never fails the conductor — write
// errors are logged to stderr but exit 0 so a missing disk does not
// block /xlfg.

import fs from "node:fs";
import path from "node:path";

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--run") { out.run = argv[++i]; continue; }
    if (k === "--phase") { out.phase = argv[++i]; continue; }
    if (k === "--event") { out.event = argv[++i]; continue; }
    throw new Error(`unexpected arg: ${k}`);
  }
  return out;
}

function isoNowZ() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

let args;
try {
  args = parseArgs(process.argv.slice(2));
} catch (err) {
  process.stderr.write(`phase-tick: ${err.message}\n`);
  process.exit(2);
}

if (!args.run || !args.phase || !args.event) {
  process.stderr.write("phase-tick: --run, --phase, --event are all required\n");
  process.exit(2);
}
if (args.event !== "start" && args.event !== "end") {
  process.stderr.write(`phase-tick: --event must be 'start' or 'end' (got '${args.event}')\n`);
  process.exit(2);
}

const line = JSON.stringify({
  run: args.run,
  phase: args.phase,
  event: args.event,
  ts: isoNowZ(),
}) + "\n";

const outDir = path.resolve(process.cwd(), "docs/xlfg/runs", args.run);
const outPath = path.join(outDir, "phase-timings.jsonl");

try {
  fs.mkdirSync(outDir, { recursive: true });
  fs.appendFileSync(outPath, line, "utf8");
} catch (err) {
  // Never block the conductor on a timings write failure.
  process.stderr.write(`phase-tick: write failed (${err.message}) — continuing\n`);
}
process.exit(0);
