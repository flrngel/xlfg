#!/usr/bin/env node
// xlfg ledger-append — validates an event against docs/xlfg/knowledge/ledger-schema.md
// and appends a single JSON line to docs/xlfg/knowledge/ledger.jsonl.
//
// Usage:
//   node ledger-append.mjs --ts ... --run ... --type ... --version ... --summary ...
// or pipe a JSON object on stdin:
//   echo '{...}' | node ledger-append.mjs
//
// Optional flags: --id, --tags (comma-separated), --stage, --role, --status, --supersedes,
//   --symptom, --root_cause, --action, --prevention, --lex, --evidence (comma-separated).
//
// Extra options:
//   --ledger <path>   Override ledger.jsonl location (default docs/xlfg/knowledge/ledger.jsonl
//                     relative to cwd).
//   --dry-run         Validate only; do not write.

import fs from "node:fs";
import path from "node:path";

const REQUIRED = ["ts", "run", "type", "version", "summary"];
const TYPE_ENUM = new Set([
  "feature",
  "fix",
  "pattern",
  "decision",
  "incident",
  "memory.added",
  "memory.superseded",
  "memory.invalidated",
]);
const STAGE_ENUM = new Set([
  "recall",
  "intent",
  "context",
  "plan",
  "implement",
  "verify",
  "review",
  "compound",
  "debug",
]);
const STATUS_ENUM = new Set(["active", "superseded", "invalidated"]);
const TAG_ALLOWLIST = new Set([
  "plugin",
  "skill",
  "agent",
  "harness",
  "hook",
  "stop-guard",
  "phase-gate",
  "ledger",
  "recall",
  "intent",
  "context",
  "plan",
  "implement",
  "verify",
  "review",
  "compound",
  "debug",
  "ui",
  "backend",
  "cli",
  "test",
  "docs",
  "workflow",
  "scale",
  "dispatch",
  "security",
]);
const ALLOWED_KEYS = new Set([
  ...REQUIRED,
  "id",
  "tags",
  "stage",
  "role",
  "evidence",
  "symptom",
  "root_cause",
  "action",
  "prevention",
  "lex",
  "status",
  "supersedes",
]);

const TS_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;
const SEMVER_RE = /^\d+\.\d+\.\d+$/;
const RUN_RE = /^\d{8}-\d{6}-[a-z0-9][a-z0-9-]*$/;

function readStdin() {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve("");
      return;
    }
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
  });
}

function parseArgs(argv) {
  const out = {};
  const flags = { "--dry-run": "dryRun" };
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    if (flags[key]) {
      out[flags[key]] = true;
      continue;
    }
    if (!key.startsWith("--")) {
      throw new Error(`unexpected positional arg: ${key}`);
    }
    const name = key.slice(2);
    const val = argv[i + 1];
    if (val === undefined || val.startsWith("--")) {
      throw new Error(`flag ${key} requires a value`);
    }
    out[name] = val;
    i += 1;
  }
  return out;
}

function coerceFromArgs(args) {
  const obj = {};
  for (const k of Object.keys(args)) {
    if (k === "dryRun" || k === "ledger") continue;
    if (k === "tags" || k === "evidence") {
      obj[k] = String(args[k])
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    } else {
      obj[k] = args[k];
    }
  }
  return obj;
}

function validate(event) {
  const errors = [];
  for (const k of REQUIRED) {
    if (event[k] === undefined || event[k] === null || event[k] === "") {
      errors.push(`missing required field: ${k}`);
    }
  }
  for (const k of Object.keys(event)) {
    if (!ALLOWED_KEYS.has(k)) {
      errors.push(`unknown field: ${k}`);
    }
  }
  if (typeof event.ts === "string" && !TS_RE.test(event.ts)) {
    errors.push(`ts must be ISO 8601 UTC (e.g. 2026-04-15T14:33:07Z), got: ${event.ts}`);
  }
  if (typeof event.run === "string" && !RUN_RE.test(event.run)) {
    errors.push(`run must match <YYYYMMDD>-<HHMMSS>-<slug>, got: ${event.run}`);
  }
  if (typeof event.type === "string" && !TYPE_ENUM.has(event.type)) {
    errors.push(`type must be one of ${[...TYPE_ENUM].join("|")}, got: ${event.type}`);
  }
  if (typeof event.version === "string" && !SEMVER_RE.test(event.version)) {
    errors.push(`version must be semver major.minor.patch, got: ${event.version}`);
  }
  if (typeof event.summary === "string" && event.summary.length > 280) {
    errors.push(`summary too long (${event.summary.length} chars, max 280)`);
  }
  if (event.stage !== undefined && !STAGE_ENUM.has(event.stage)) {
    errors.push(`stage must be one of ${[...STAGE_ENUM].join("|")}, got: ${event.stage}`);
  }
  if (event.status !== undefined && !STATUS_ENUM.has(event.status)) {
    errors.push(`status must be one of ${[...STATUS_ENUM].join("|")}, got: ${event.status}`);
  }
  if (event.tags !== undefined) {
    if (!Array.isArray(event.tags)) {
      errors.push(`tags must be an array`);
    } else {
      for (const t of event.tags) {
        if (typeof t !== "string" || !TAG_ALLOWLIST.has(t)) {
          errors.push(`tag not in allow-list: ${JSON.stringify(t)}`);
        }
      }
    }
  }
  if (event.evidence !== undefined) {
    if (!Array.isArray(event.evidence)) {
      errors.push(`evidence must be an array`);
    }
  }
  return errors;
}

async function main() {
  const argv = process.argv.slice(2);
  let args;
  try {
    args = parseArgs(argv);
  } catch (err) {
    process.stderr.write(`ledger-append: ${err.message}\n`);
    process.exit(2);
  }

  const stdin = await readStdin();
  let event;
  if (stdin.trim()) {
    try {
      event = JSON.parse(stdin);
    } catch (err) {
      process.stderr.write(`ledger-append: invalid JSON on stdin: ${err.message}\n`);
      process.exit(2);
    }
  } else {
    event = coerceFromArgs(args);
  }

  const errors = validate(event);
  if (errors.length > 0) {
    process.stderr.write(`ledger-append: rejected event\n`);
    for (const e of errors) process.stderr.write(`  - ${e}\n`);
    process.exit(1);
  }

  if (args.dryRun) {
    process.stdout.write(JSON.stringify(event) + "\n");
    return;
  }

  const ledgerPath = args.ledger
    ? path.resolve(args.ledger)
    : path.resolve(process.cwd(), "docs/xlfg/knowledge/ledger.jsonl");
  fs.mkdirSync(path.dirname(ledgerPath), { recursive: true });
  fs.appendFileSync(ledgerPath, JSON.stringify(event) + "\n", "utf8");
  process.stdout.write(`${ledgerPath}\n`);
}

main().catch((err) => {
  process.stderr.write(`ledger-append: ${err.stack || err.message}\n`);
  process.exit(2);
});
