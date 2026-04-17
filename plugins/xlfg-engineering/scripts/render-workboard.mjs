#!/usr/bin/env node
// xlfg render-workboard — regenerate the "## Phase status" section of
// docs/xlfg/runs/<RUN_ID>/workboard.md from .xlfg/phase-state.json.
//
// workboard.md is authored in layers: this renderer owns the
// `## Phase status` block only. Task tables, blockers, and the next-action
// line remain authored by the phase skill that runs each phase. That split
// means two writers of one file — but only one writer per section, which is
// the point: phase-status stops being dual-written.
//
// Usage:
//   node render-workboard.mjs           # reads .xlfg/phase-state.json under cwd
//   node render-workboard.mjs --state <path> --out <workboard.md>
//   node render-workboard.mjs --dry-run # prints to stdout
//
// Exits 0 when it rendered, 0 when no phase-state.json exists (no-op), and 2
// on malformed state.

import fs from "node:fs";
import path from "node:path";

const MARK_BEGIN = "<!-- BEGIN: rendered-phase-status (render-workboard.mjs) -->";
const MARK_END = "<!-- END: rendered-phase-status -->";
// Match any BEGIN variant, including a placeholder `<!-- BEGIN: rendered-phase-status -->`
// (no script-attribution suffix) left by a run-skeleton template. Without this, a
// placeholder would not match the exact MARK_BEGIN, the script would take the
// "no markers" path, and a second ## Phase status block would be appended.
const MARK_BEGIN_PREFIX = "<!-- BEGIN: rendered-phase-status";

function parseArgs(argv) {
  const out = { dryRun: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--dry-run") {
      out.dryRun = true;
      continue;
    }
    if (k === "--state") {
      out.state = argv[++i];
      continue;
    }
    if (k === "--out") {
      out.out = argv[++i];
      continue;
    }
    throw new Error(`unexpected arg: ${k}`);
  }
  return out;
}

function renderBlock(state) {
  const phases = Array.isArray(state.phases) ? state.phases : [];
  const completed = new Set(Array.isArray(state.completed) ? state.completed : []);
  const lines = [];
  lines.push(MARK_BEGIN);
  lines.push("## Phase status");
  lines.push("");
  lines.push(`Run: \`${state.run_id || "(unknown)"}\``);
  const lc = typeof state.loopback_count === "number" ? state.loopback_count : 0;
  const mx = typeof state.max_loopbacks === "number" ? state.max_loopbacks : 2;
  lines.push(`Loopbacks: ${lc}/${mx}`);
  lines.push("");
  lines.push("| Phase | Status |");
  lines.push("|---|---|");
  let activeSeen = false;
  for (const p of phases) {
    let status;
    if (completed.has(p)) {
      status = "DONE";
    } else if (!activeSeen) {
      status = "IN_PROGRESS";
      activeSeen = true;
    } else {
      status = "pending";
    }
    lines.push(`| ${p} | ${status} |`);
  }
  lines.push("");
  lines.push(MARK_END);
  return lines.join("\n") + "\n";
}

function spliceBlock(original, rendered) {
  const body = String(original || "");
  // Prefix match so placeholders without the script-attribution suffix
  // are recognized as the existing block and replaced in place.
  const beginIdx = body.indexOf(MARK_BEGIN_PREFIX);
  const endIdx = body.indexOf(MARK_END);
  if (beginIdx !== -1 && endIdx !== -1 && endIdx > beginIdx) {
    return (
      body.slice(0, beginIdx) +
      rendered.trimEnd() +
      "\n" +
      body.slice(endIdx + MARK_END.length).replace(/^\r?\n/, "")
    );
  }
  // No markers yet — prepend after the first top-level heading, or at the top
  // if no heading exists.
  const headingMatch = body.match(/^# [^\n]*\n/);
  if (headingMatch) {
    const insertAt = headingMatch.index + headingMatch[0].length;
    return body.slice(0, insertAt) + "\n" + rendered + body.slice(insertAt);
  }
  return rendered + body;
}

function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (err) {
    process.stderr.write(`render-workboard: ${err.message}\n`);
    process.exit(2);
  }

  const statePath = args.state
    ? path.resolve(args.state)
    : path.resolve(process.cwd(), ".xlfg/phase-state.json");

  let state;
  try {
    state = JSON.parse(fs.readFileSync(statePath, "utf8"));
  } catch (err) {
    if (err.code === "ENOENT") {
      // No phase-state — not in an xlfg run. No-op.
      process.exit(0);
    }
    process.stderr.write(`render-workboard: cannot read state ${statePath}: ${err.message}\n`);
    process.exit(2);
  }

  if (!state.run_id) {
    process.stderr.write(`render-workboard: state missing run_id\n`);
    process.exit(2);
  }

  const rendered = renderBlock(state);

  const outPath = args.out
    ? path.resolve(args.out)
    : path.resolve(process.cwd(), "docs/xlfg/runs", state.run_id, "workboard.md");

  if (args.dryRun) {
    process.stdout.write(rendered);
    return;
  }

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  let existing = "";
  try {
    existing = fs.readFileSync(outPath, "utf8");
  } catch {
    existing = `# Workboard\n\n`;
  }
  fs.writeFileSync(outPath, spliceBlock(existing, rendered), "utf8");
  process.stdout.write(`${outPath}\n`);
}

main();
