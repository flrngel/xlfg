#!/usr/bin/env node
// xlfg phase-gate — Stop hook that blocks the conductor from ending the
// /xlfg pipeline before all phases complete.
//
// Write discipline: this hook only ever mutates `block_count`. The
// read-modify-write cycle preserves every other field (`completed`,
// `loopback_count`, `in_progress_phase`, `run_id`, `phases`, ...) exactly
// as read. Treat the hook as monotonic-for-block_count; it must never
// reset lifecycle state written by the conductor.
//
// Known limitation (not concurrency-safe): the read-modify-write is not
// atomic. If the conductor writes the state file between the hook's
// read and the hook's write, the hook's write clobbers the conductor's
// update. The suppression branch above narrows the window (hook exits
// without writing while a phase is in progress), but the race is not
// eliminated. A real fix would require file-locking or a separate
// ledger for block_count — intentionally out of scope here.
//
// Noise suppression: if the conductor has set `in_progress_phase` to a
// non-empty string, the hook exits 0 without writing. That covers the
// case where a long-running foreground phase (e.g. verify with live LLM
// proof) legitimately parks the conversation awaiting a background task
// or the next sub-packet. Without this guard, every parked turn would
// fire the hook, increment block_count, and trip the safety valve.
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

// Noise suppression: if the conductor has set `in_progress_phase` to a
// non-empty string, a long phase is legitimately running (verify parked
// on bg LLM work, implement parked between sub-packets, etc.). Exit 0
// without writing — do not increment block_count, do not trip the
// safety valve. The conductor clears the field on phase completion.
const inProgress =
  typeof state.in_progress_phase === "string"
    ? state.in_progress_phase.trim()
    : "";
if (inProgress) {
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
