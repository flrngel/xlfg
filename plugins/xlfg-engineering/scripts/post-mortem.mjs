#!/usr/bin/env node
// xlfg post-mortem — deterministic per-run breakdown.
//
// Reads docs/xlfg/runs/<RUN_ID>/phase-timings.jsonl, the run's artifact
// listing, and the global ledger.jsonl (filtered by run id) to answer
// the question: "what did this run actually do, and where did the time go?"
//
// The script is deterministic and side-effect free. The /xlfg-audit
// slash command shells out to it, prints the table, and then asks the
// user whether to submit the redacted report to flrngel/xlfg.
//
// Usage:
//   node post-mortem.mjs                # latest run under docs/xlfg/runs/
//   node post-mortem.mjs --run <RUN_ID> # specific run
//   node post-mortem.mjs --json         # machine-readable instead of markdown
//
// Exits 0 on success, 2 on bad args, 3 if no run dir exists.

import fs from "node:fs";
import path from "node:path";

const ALL_PHASES_FULL = ["recall", "intent", "context", "plan", "implement", "verify", "review", "compound"];
const ALL_PHASES_DEBUG = ["recall", "intent", "context", "debug"];

function parseArgs(argv) {
  const out = { json: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--run") { out.run = argv[++i]; continue; }
    if (k === "--json") { out.json = true; continue; }
    if (k === "--root") { out.root = argv[++i]; continue; }
    throw new Error(`unexpected arg: ${k}`);
  }
  return out;
}

function pickLatestRun(runsDir) {
  let entries;
  try {
    entries = fs.readdirSync(runsDir, { withFileTypes: true });
  } catch {
    return null;
  }
  const dirs = entries
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .filter((n) => /^\d{8}-\d{6}-/.test(n))
    .sort();
  return dirs.length ? dirs[dirs.length - 1] : null;
}

function readJsonl(p) {
  let text;
  try { text = fs.readFileSync(p, "utf8"); } catch { return []; }
  const out = [];
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { out.push(JSON.parse(trimmed)); } catch { /* skip malformed */ }
  }
  return out;
}

function diffSeconds(startIso, endIso) {
  const a = Date.parse(startIso);
  const b = Date.parse(endIso);
  if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) return null;
  return Math.round((b - a) / 1000);
}

function fmtDuration(seconds) {
  if (seconds == null) return "—";
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return s ? `${m}m${s}s` : `${m}m`;
}

function fmtBytes(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function buildPhaseRows(timings, phaseOrder) {
  // Pair start/end events per phase. Loopbacks produce multiple pairs.
  const byPhase = new Map();
  for (const phase of phaseOrder) byPhase.set(phase, { invocations: 0, totalSeconds: 0, hasTiming: false, openStart: null });
  for (const ev of timings) {
    if (!byPhase.has(ev.phase)) byPhase.set(ev.phase, { invocations: 0, totalSeconds: 0, hasTiming: false, openStart: null });
    const row = byPhase.get(ev.phase);
    if (ev.event === "start") {
      row.openStart = ev.ts;
    } else if (ev.event === "end" && row.openStart) {
      const d = diffSeconds(row.openStart, ev.ts);
      if (d != null) {
        row.totalSeconds += d;
        row.invocations += 1;
        row.hasTiming = true;
      }
      row.openStart = null;
    }
  }
  return byPhase;
}

function listRunArtifacts(runDir) {
  const out = [];
  function walk(dir, rel) {
    let entries = [];
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      const childRel = rel ? path.join(rel, e.name) : e.name;
      if (e.isDirectory()) {
        walk(full, childRel);
      } else if (e.isFile()) {
        let size = 0;
        try { size = fs.statSync(full).size; } catch { /* ignore */ }
        out.push({ rel: childRel, bytes: size });
      }
    }
  }
  walk(runDir, "");
  return out;
}

function artifactsByPhase(artifacts) {
  // Heuristic mapping of artifact filename → phase, matching the conventions
  // the phase skills already use. Anything unmatched goes to "other".
  const map = {
    "memory-recall.md": "recall",
    "intent-refinement.md": "intent",
    "intent-refiner-report.md": "intent",
    "context.md": "context",
    "repo-map.md": "context",
    "spec.md": "intent",
    "task-division.md": "plan",
    "test-contract.md": "plan",
    "test-readiness.md": "plan",
    "solution-decision.md": "plan",
    "workboard.md": "plan",
    "verification.md": "verify",
    "verify-runner.md": "verify",
    "verify-fix-plan.md": "verify",
    "review-summary.md": "review",
    "compound-summary.md": "compound",
    "run-summary.md": "compound",
    "diagnosis.md": "debug",
    "debug-report.md": "debug",
    "phase-timings.jsonl": "_meta",
    "phase-state.json": "_meta",
  };
  const grouped = new Map();
  for (const a of artifacts) {
    const base = path.basename(a.rel);
    let phase = map[base];
    if (!phase) {
      if (a.rel.startsWith("tasks/")) phase = "implement";
      else if (a.rel.startsWith("reviews/")) phase = "review";
      else phase = "other";
    }
    if (!grouped.has(phase)) grouped.set(phase, { count: 0, bytes: 0 });
    const row = grouped.get(phase);
    row.count += 1;
    row.bytes += a.bytes;
  }
  return grouped;
}

function buildSuggestions(phaseRows, phaseState, artifactStats, ledgerEntries, hasTimings) {
  const suggestions = [];

  // Sort phases by wall time descending.
  const ranked = [...phaseRows.entries()]
    .filter(([, v]) => v.hasTiming)
    .sort((a, b) => b[1].totalSeconds - a[1].totalSeconds);

  if (hasTimings && ranked.length) {
    const [slowestPhase, slowestRow] = ranked[0];
    if (slowestRow.totalSeconds >= 600) {
      suggestions.push(
        `slowest phase \`${slowestPhase}\` took ${fmtDuration(slowestRow.totalSeconds)} ` +
        `across ${slowestRow.invocations} invocation(s); consider splitting the lane or ` +
        `tightening the atomic packet so the specialist does less per turn.`
      );
    }
    if (ranked.length >= 2) {
      const [secondPhase, secondRow] = ranked[1];
      if (secondRow.hasTiming && slowestRow.totalSeconds > 0 &&
          secondRow.totalSeconds / slowestRow.totalSeconds < 0.25) {
        suggestions.push(
          `time is concentrated in \`${slowestPhase}\` (${fmtDuration(slowestRow.totalSeconds)}); ` +
          `next phase \`${secondPhase}\` was ${fmtDuration(secondRow.totalSeconds)} — ` +
          `the bottleneck is real, not noise.`
        );
      }
    }
  }

  const loopbacks = typeof phaseState?.loopback_count === "number" ? phaseState.loopback_count : 0;
  if (loopbacks > 0) {
    suggestions.push(
      `${loopbacks} loopback(s) occurred; check the workboard's blockers section to see ` +
      `which phase rejected its predecessor and whether the test contract was the cause.`
    );
  }

  for (const [phase, row] of phaseRows) {
    if (row.invocations > 1) {
      suggestions.push(
        `phase \`${phase}\` ran ${row.invocations} times — a re-run usually means a downstream ` +
        `phase rejected its output; tighten the upstream done-check to fail earlier.`
      );
    }
  }

  for (const [phase, stats] of artifactStats) {
    if (phase === "_meta" || phase === "other") continue;
    if (stats.bytes > 80 * 1024) {
      suggestions.push(
        `phase \`${phase}\` produced ${fmtBytes(stats.bytes)} across ${stats.count} file(s) — ` +
        `large artifacts inflate context cost on later phases; consider summarizing.`
      );
    }
  }

  if (!hasTimings) {
    suggestions.push(
      `no \`phase-timings.jsonl\` recorded for this run — wall-time analysis unavailable. ` +
      `New runs (>= v4.2.0) record timings automatically; older runs only show artifact shape.`
    );
  }

  if (!suggestions.length) {
    suggestions.push("no obvious cost driver detected — this run was lean.");
  }
  return suggestions;
}

function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); }
  catch (err) {
    process.stderr.write(`post-mortem: ${err.message}\n`);
    process.exit(2);
  }
  const root = path.resolve(args.root || process.cwd());
  const runsRoot = path.join(root, "docs/xlfg/runs");

  const runId = args.run || pickLatestRun(runsRoot);
  if (!runId) {
    process.stderr.write(`post-mortem: no runs found under ${runsRoot}\n`);
    process.exit(3);
  }

  const runDir = path.join(runsRoot, runId);
  if (!fs.existsSync(runDir)) {
    process.stderr.write(`post-mortem: run dir not found: ${runDir}\n`);
    process.exit(3);
  }

  const timings = readJsonl(path.join(runDir, "phase-timings.jsonl"));
  const ledger = readJsonl(path.join(root, "docs/xlfg/knowledge/ledger.jsonl"))
    .filter((e) => e.run === runId);

  // phase-state.json lives at the global .xlfg/ path while the run is live;
  // for historical runs it may be absent. Both locations are checked.
  let phaseState = null;
  for (const candidate of [
    path.join(root, ".xlfg/phase-state.json"),
    path.join(runDir, "phase-state.json"),
  ]) {
    try {
      const txt = fs.readFileSync(candidate, "utf8");
      const parsed = JSON.parse(txt);
      if (parsed.run_id === runId) { phaseState = parsed; break; }
    } catch { /* keep looking */ }
  }

  const phaseOrder = phaseState?.phases
    || (timings.length ? [...new Set(timings.map((t) => t.phase))] : ALL_PHASES_FULL);

  const phaseRows = buildPhaseRows(timings, phaseOrder);
  const artifacts = listRunArtifacts(runDir);
  const artStats = artifactsByPhase(artifacts);

  const hasTimings = timings.length > 0;

  const completedSet = new Set(phaseState?.completed || []);

  const tableRows = [];
  for (const phase of phaseOrder) {
    const r = phaseRows.get(phase) || { invocations: 0, totalSeconds: 0, hasTiming: false };
    const a = artStats.get(phase) || { count: 0, bytes: 0 };
    let status = "—";
    if (phaseState) status = completedSet.has(phase) ? "DONE" : "INCOMPLETE";
    tableRows.push({
      phase,
      status,
      wall: fmtDuration(r.hasTiming ? r.totalSeconds : null),
      invocations: r.invocations,
      artifacts: a.count,
      artifactBytes: fmtBytes(a.bytes),
    });
  }

  const totalSeconds = [...phaseRows.values()]
    .filter((r) => r.hasTiming)
    .reduce((acc, r) => acc + r.totalSeconds, 0);
  const totalArtifacts = artifacts.length;
  const totalBytes = artifacts.reduce((acc, a) => acc + a.bytes, 0);
  const loopbacks = phaseState?.loopback_count ?? 0;
  const ledgerCounts = ledger.reduce((acc, e) => {
    acc[e.type] = (acc[e.type] || 0) + 1;
    return acc;
  }, {});

  const suggestions = buildSuggestions(phaseRows, phaseState, artStats, ledger, hasTimings);

  if (args.json) {
    process.stdout.write(JSON.stringify({
      run_id: runId,
      run_dir: runDir,
      total_seconds: totalSeconds,
      total_artifacts: totalArtifacts,
      total_bytes: totalBytes,
      loopbacks,
      has_timings: hasTimings,
      phases: tableRows,
      ledger_counts: ledgerCounts,
      suggestions,
    }, null, 2) + "\n");
    return;
  }

  // Markdown output.
  const lines = [];
  lines.push(`# xlfg post-mortem — \`${runId}\``);
  lines.push("");
  lines.push("## Summary");
  lines.push("");
  lines.push(`- run dir: \`${path.relative(root, runDir)}\``);
  lines.push(`- total wall time: ${hasTimings ? fmtDuration(totalSeconds) : "n/a (no phase-timings.jsonl)"}`);
  lines.push(`- total artifacts: ${totalArtifacts} files, ${fmtBytes(totalBytes)}`);
  lines.push(`- loopbacks: ${loopbacks}`);
  if (Object.keys(ledgerCounts).length) {
    const parts = Object.entries(ledgerCounts).map(([k, v]) => `${k}=${v}`).join(", ");
    lines.push(`- ledger entries for this run: ${parts}`);
  } else {
    lines.push(`- ledger entries for this run: none`);
  }
  lines.push("");
  lines.push("## Phase breakdown");
  lines.push("");
  lines.push("| Phase | Status | Wall time | Invocations | Artifacts | Bytes |");
  lines.push("|---|---|---|---|---|---|");
  for (const r of tableRows) {
    lines.push(`| ${r.phase} | ${r.status} | ${r.wall} | ${r.invocations} | ${r.artifacts} | ${r.artifactBytes} |`);
  }
  lines.push("");
  lines.push("## How xlfg can be better (based on this run)");
  lines.push("");
  for (const s of suggestions) lines.push(`- ${s}`);
  lines.push("");

  process.stdout.write(lines.join("\n"));
}

main();
