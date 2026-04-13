#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
  });
}

function block(reason) {
  process.stdout.write(JSON.stringify({ decision: "block", reason }));
}

const PHASE_STATE_PATH = ".xlfg/phase-state.json";
const ALL_PHASES = [
  "recall",
  "intent",
  "context",
  "plan",
  "implement",
  "verify",
  "review",
  "compound",
];
const MAX_BLOCKS = 3;

const raw = await readStdin();
// Empty stdin means this invocation carries no Claude Code stop event.
// Allow stopping instead of reading the cwd-relative phase-state file,
// which would otherwise block legitimate non-xlfg invocations.
if (!raw.trim()) {
  process.exit(0);
}
let payload = {};
try {
  payload = JSON.parse(raw);
} catch {
  process.exit(0);
}

// Always allow stopping when model hits token limit — it cannot continue.
const stopReason = String(payload.stop_reason || "").trim();
if (stopReason === "max_tokens") {
  process.exit(0);
}

// Resolve phase-state file relative to cwd.
const cwd = String(payload.cwd || process.cwd());
const stateFile = path.resolve(cwd, PHASE_STATE_PATH);

let state;
try {
  state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
} catch {
  // No phase-state file means we are not inside an /xlfg run — allow stopping.
  process.exit(0);
}

const completed = Array.isArray(state.completed) ? state.completed : [];
const phases = Array.isArray(state.phases) ? state.phases : ALL_PHASES;

// If all phases are done, allow stopping.
if (phases.every((p) => completed.includes(p))) {
  process.exit(0);
}

// Safety valve: if we have already blocked too many times in a row, allow
// stopping to prevent an infinite loop when the model cannot make progress.
const blockCount = typeof state.block_count === "number" ? state.block_count : 0;
if (blockCount >= MAX_BLOCKS) {
  process.exit(0);
}

// Find next incomplete phase.
const nextPhase = phases.find((p) => !completed.includes(p));

// Increment block_count and write back so the safety valve can trigger.
try {
  state.block_count = blockCount + 1;
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2) + "\n", "utf8");
} catch {
  // If we cannot write back, still block this time but the safety valve
  // will not advance — acceptable because the model will eventually hit
  // max_tokens or the user can intervene.
}

block(
  `The /xlfg pipeline is not complete. ${completed.length}/${phases.length} phases done. ` +
    `Run the next phase: ${nextPhase}. ` +
    `Use the Skill tool to invoke the ${nextPhase} phase skill with the current RUN_ID.`
);
