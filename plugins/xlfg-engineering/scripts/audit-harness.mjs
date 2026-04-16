#!/usr/bin/env node
// xlfg audit-harness — deterministic self-check of the xlfg plugin.
//
// Replaces the previous /xlfg-audit slash command body. Every check
// here is a file read, regex match, JSON parse, or word count — none
// of it needed an LLM, and none of it should pretend it did.
//
// Maintainer tool. Wire into pre-push, npm scripts, or CI. The
// /xlfg-audit slash command is now reserved for the per-run user
// post-mortem (see post-mortem.mjs).
//
// Usage:
//   node audit-harness.mjs                 # auto-detects plugin root
//   node audit-harness.mjs --plugin <path> # explicit
//   node audit-harness.mjs --json          # machine-readable
//
// Exit code: 0 = every check passed, 1 = any check failed.

import fs from "node:fs";
import path from "node:path";

const EXPECTED_PHASE_SKILLS = [
  "xlfg-recall-phase",
  "xlfg-intent-phase",
  "xlfg-context-phase",
  "xlfg-plan-phase",
  "xlfg-implement-phase",
  "xlfg-verify-phase",
  "xlfg-review-phase",
  "xlfg-compound-phase",
  "xlfg-debug-phase",
];

const PUBLIC_COMMANDS = ["xlfg.md", "xlfg-debug.md"];

const CODEX_PUBLIC_SKILLS = ["xlfg/SKILL.md", "xlfg-debug/SKILL.md"];

const CODEX_FORBIDDEN_TOKENS = [
  "allowed-tools", "Skill(", "TaskCreate", "TaskUpdate", "TaskList",
  "ExitPlanMode", "PermissionRequest", "CLAUDE_PLUGIN_ROOT",
  "user-invocable", "model:", "effort:", "sonnet", "haiku", "opus",
];

function parseArgs(argv) {
  const out = { json: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--plugin") { out.plugin = argv[++i]; continue; }
    if (k === "--json") { out.json = true; continue; }
    if (k === "--help" || k === "-h") { out.help = true; continue; }
    throw new Error(`unexpected arg: ${k}`);
  }
  return out;
}

function resolvePlugin(explicit) {
  if (explicit) return path.resolve(explicit);
  const cwdGuess = path.resolve(process.cwd(), "plugins/xlfg-engineering");
  if (fs.existsSync(path.join(cwdGuess, ".claude-plugin/plugin.json"))) return cwdGuess;
  // Walk up from this script in case it's invoked from elsewhere.
  let here = path.dirname(new URL(import.meta.url).pathname);
  for (let i = 0; i < 6; i++) {
    if (fs.existsSync(path.join(here, ".claude-plugin/plugin.json"))) return here;
    here = path.dirname(here);
  }
  throw new Error("cannot locate plugin root; pass --plugin <path>");
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function readText(p) {
  return fs.readFileSync(p, "utf8");
}

function frontmatter(text) {
  const lines = text.split(/\r?\n/);
  if (lines[0]?.trim() !== "---") return { raw: "", fields: {} };
  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === "---") { end = i; break; }
  }
  if (end < 0) return { raw: "", fields: {} };
  const raw = lines.slice(1, end).join("\n");
  const fields = {};
  for (const line of lines.slice(1, end)) {
    const m = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (m) fields[m[1]] = m[2].trim();
  }
  return { raw, fields };
}

function wordCount(p) {
  try {
    const text = readText(p);
    const matches = text.match(/\S+/g);
    return matches ? matches.length : 0;
  } catch { return 0; }
}

function listAgentFiles(pluginRoot) {
  const root = path.join(pluginRoot, "agents");
  if (!fs.existsSync(root)) return [];
  const out = [];
  function walk(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name === "_shared") continue;
        walk(full);
      } else if (e.isFile() && e.name.endsWith(".md")) {
        out.push(full);
      }
    }
  }
  walk(root);
  return out;
}

function listRuntimeMarkdown(pluginRoot) {
  const out = [];
  for (const sub of ["commands", "skills", "agents"]) {
    const root = path.join(pluginRoot, sub);
    if (!fs.existsSync(root)) continue;
    function walk(dir) {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, e.name);
        if (e.isDirectory()) walk(full);
        else if (e.isFile() && (e.name.endsWith(".md") || e.name === "SKILL.md")) out.push(full);
      }
    }
    walk(root);
  }
  return out;
}

// ---------- checks ----------

function checkVersionSync(pluginRoot) {
  const manifests = [
    [".claude-plugin/plugin.json", null],
    [".cursor-plugin/plugin.json", null],
    [".codex-plugin/plugin.json", null],
  ];
  const versions = {};
  for (const m of manifests) {
    const p = path.join(pluginRoot, m[0]);
    try { versions[m[0]] = readJson(p).version; }
    catch { versions[m[0]] = null; }
  }
  const distinct = new Set(Object.values(versions).filter(Boolean));
  const allPresent = Object.values(versions).every(Boolean);
  const pass = allPresent && distinct.size === 1;
  return {
    id: 1, name: "version sync",
    pass,
    score: pass ? 1 : 0,
    note: pass
      ? `${distinct.size} version across ${Object.keys(versions).length} manifests: ${[...distinct][0]}`
      : `versions: ${JSON.stringify(versions)}`,
    detail: { versions },
  };
}

function checkSdlcCoverage(pluginRoot) {
  const present = [];
  const missing = [];
  for (const phase of EXPECTED_PHASE_SKILLS) {
    const skillPath = path.join(pluginRoot, "skills", phase, "SKILL.md");
    if (fs.existsSync(skillPath)) present.push(phase); else missing.push(phase);
  }
  const score = present.length / EXPECTED_PHASE_SKILLS.length;
  return {
    id: 2, name: "SDLC coverage",
    pass: missing.length === 0,
    score,
    note: missing.length ? `missing: ${missing.join(", ")}` : `${present.length}/${EXPECTED_PHASE_SKILLS.length} phases present`,
    detail: { present, missing },
  };
}

function checkWorkflowLoad(pluginRoot) {
  const counts = {};
  for (const cmd of PUBLIC_COMMANDS) {
    const p = path.join(pluginRoot, "commands", cmd);
    counts[`commands/${cmd}`] = wordCount(p);
  }
  for (const phase of EXPECTED_PHASE_SKILLS) {
    const p = path.join(pluginRoot, "skills", phase, "SKILL.md");
    counts[`skills/${phase}/SKILL.md`] = wordCount(p);
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const ranked = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const top3 = ranked.slice(0, 3);
  return {
    id: 3, name: "workflow load",
    pass: true, // informational
    score: total,
    note: `${total} total words; top driver: ${top3[0]?.[0]} (${top3[0]?.[1]})`,
    detail: { counts, total, top3 },
  };
}

function checkClaudeCodeCompat(pluginRoot) {
  const failures = [];
  let assertions = 0;
  let passes = 0;

  // Public command frontmatter.
  for (const cmd of PUBLIC_COMMANDS) {
    const p = path.join(pluginRoot, "commands", cmd);
    let text;
    try { text = readText(p); }
    catch { failures.push(`${cmd}: missing`); assertions += 4; continue; }
    const fm = frontmatter(text);
    const checks = {
      "allowed-tools present": "allowed-tools" in fm.fields,
      "effort=high": fm.fields.effort === "high",
      "disable-model-invocation=true": fm.fields["disable-model-invocation"] === "true",
      "PermissionRequest→ExitPlanMode auto-allow":
        /PermissionRequest:\s*\n[\s\S]*?matcher:\s*"ExitPlanMode"[\s\S]*?behavior":\s*"allow"/.test(text),
    };
    for (const [label, ok] of Object.entries(checks)) {
      assertions += 1;
      if (ok) passes += 1; else failures.push(`commands/${cmd}: ${label} missing`);
    }
  }

  // Phase skill frontmatter.
  for (const phase of EXPECTED_PHASE_SKILLS) {
    const p = path.join(pluginRoot, "skills", phase, "SKILL.md");
    let text;
    try { text = readText(p); }
    catch { failures.push(`skills/${phase}: missing`); assertions += 2; continue; }
    const fm = frontmatter(text);
    assertions += 1;
    if (fm.fields["user-invocable"] === "false") passes += 1;
    else failures.push(`skills/${phase}: user-invocable!=false`);
    assertions += 1;
    if (!("name" in fm.fields)) passes += 1;
    else failures.push(`skills/${phase}: name field present (must be omitted for hidden skills)`);
  }

  // Forbidden token sweep across commands/, skills/, agents/.
  // The audit's own command is allowed to mention these strings.
  // Stale `Task` is checked ONLY inside the frontmatter `tools:` field
  // (where it would actually break) — not in body prose, where "Task"
  // legitimately appears as English (e.g. "## Task decomposition").
  const auditCmd = path.join(pluginRoot, "commands", "xlfg-audit.md");
  for (const file of listRuntimeMarkdown(pluginRoot)) {
    if (path.resolve(file) === path.resolve(auditCmd)) continue;
    const text = readText(file);
    const fm = frontmatter(text);
    assertions += 1;
    const toolsField = fm.fields.tools || fm.fields["allowed-tools"] || "";
    // Reject bare `Task` as a tool name; allow TaskCreate / TaskUpdate / TaskList / etc.
    const toolList = toolsField.split(",").map((s) => s.trim());
    const hasStaleTask = toolList.some((t) => /^Task(\s*\(|$)/.test(t));
    if (!hasStaleTask) passes += 1;
    else failures.push(`${path.relative(pluginRoot, file)}: stale bare 'Task' in tools field`);
    assertions += 1;
    if (!text.includes("query-contract.md")) passes += 1;
    else failures.push(`${path.relative(pluginRoot, file)}: forbidden 'query-contract.md' reference`);
  }

  // Specialist agent contract.
  for (const agentPath of listAgentFiles(pluginRoot)) {
    const text = readText(agentPath);
    const fm = frontmatter(text);
    assertions += 1;
    const turns = parseInt(fm.fields.maxTurns, 10);
    if (Number.isFinite(turns) && turns <= 150) passes += 1;
    else failures.push(`${path.relative(pluginRoot, agentPath)}: maxTurns missing or > 150 (got ${fm.fields.maxTurns})`);
    assertions += 1;
    const tools = fm.fields.tools || "";
    if (!/\bAgent\b/.test(tools) && !/\bSendMessage\b/.test(tools)) passes += 1;
    else failures.push(`${path.relative(pluginRoot, agentPath)}: leaf-worker rule violated (Agent/SendMessage in tools)`);
  }

  const score = assertions ? passes / assertions : 1;
  return {
    id: 4, name: "Claude Code compatibility",
    pass: failures.length === 0,
    score,
    note: failures.length
      ? `${passes}/${assertions} assertions pass; ${failures.length} failure(s)`
      : `${passes}/${assertions} assertions pass`,
    detail: { failures, assertions, passes },
  };
}

function checkCodexSurface(pluginRoot) {
  const failures = [];
  for (const rel of CODEX_PUBLIC_SKILLS) {
    const p = path.join(pluginRoot, "codex", "skills", rel);
    if (!fs.existsSync(p)) {
      failures.push(`missing codex/skills/${rel}`);
      continue;
    }
    const text = readText(p);
    for (const tok of CODEX_FORBIDDEN_TOKENS) {
      if (text.includes(tok)) {
        failures.push(`codex/skills/${rel}: contains Claude-only token '${tok}'`);
      }
    }
  }
  return {
    id: 5, name: "Codex surface integrity",
    pass: failures.length === 0,
    score: failures.length === 0 ? 1 : 0,
    note: failures.length ? `${failures.length} issue(s)` : `2 codex skills clean`,
    detail: { failures },
  };
}

function checkScaffoldConsistency(pluginRoot, cwd) {
  const metaPath = path.join(cwd, "docs/xlfg/meta.json");
  if (!fs.existsSync(metaPath)) {
    return {
      id: 6, name: "scaffold self-consistency",
      pass: true, // not a failure — invoked outside an xlfg-initialized project
      score: 1,
      note: "no scaffold in cwd (not an xlfg-initialized project)",
      detail: { metaPath, present: false },
    };
  }
  let toolVersion = null;
  try { toolVersion = readJson(metaPath).tool_version; } catch { /* ignore */ }
  const claudePluginVersion = readJson(path.join(pluginRoot, ".claude-plugin/plugin.json")).version;
  const pass = toolVersion === claudePluginVersion;
  return {
    id: 6, name: "scaffold self-consistency",
    pass,
    score: pass ? 1 : 0,
    note: pass
      ? `meta.tool_version matches plugin (${claudePluginVersion})`
      : `drift: meta.tool_version=${toolVersion}, plugin=${claudePluginVersion}`,
    detail: { toolVersion, claudePluginVersion },
  };
}

// ---------- main ----------

function fmtMarkdown(results, pluginRoot) {
  const lines = [];
  lines.push(`# xlfg audit-harness`);
  lines.push("");
  lines.push(`Plugin: \`${pluginRoot}\``);
  lines.push("");
  lines.push("| # | Check | Status | Score | Note |");
  lines.push("|---|---|---|---|---|");
  for (const r of results) {
    const status = r.pass ? "pass" : "fail";
    const score = typeof r.score === "number" && r.score <= 1 && r.score >= 0
      ? r.score.toFixed(2)
      : String(r.score);
    lines.push(`| ${r.id} | ${r.name} | ${status} | ${score} | ${r.note} |`);
  }
  lines.push("");
  const failed = results.filter((r) => !r.pass);
  if (failed.length) {
    lines.push("## Failures");
    lines.push("");
    for (const r of failed) {
      lines.push(`### ${r.id}. ${r.name}`);
      lines.push("");
      const detailFailures = r.detail?.failures || [];
      if (detailFailures.length) {
        for (const f of detailFailures) lines.push(`- ${f}`);
      } else {
        lines.push(`- ${r.note}`);
      }
      lines.push("");
    }
  } else {
    lines.push("All checks passed.");
    lines.push("");
  }
  return lines.join("\n");
}

function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); }
  catch (err) {
    process.stderr.write(`audit-harness: ${err.message}\n`);
    process.exit(2);
  }
  if (args.help) {
    process.stdout.write("Usage: node audit-harness.mjs [--plugin <path>] [--json]\n");
    process.exit(0);
  }

  let pluginRoot;
  try { pluginRoot = resolvePlugin(args.plugin); }
  catch (err) {
    process.stderr.write(`audit-harness: ${err.message}\n`);
    process.exit(2);
  }

  const cwd = process.cwd();
  const results = [
    checkVersionSync(pluginRoot),
    checkSdlcCoverage(pluginRoot),
    checkWorkflowLoad(pluginRoot),
    checkClaudeCodeCompat(pluginRoot),
    checkCodexSurface(pluginRoot),
    checkScaffoldConsistency(pluginRoot, cwd),
  ];

  if (args.json) {
    process.stdout.write(JSON.stringify({ plugin: pluginRoot, results }, null, 2) + "\n");
  } else {
    process.stdout.write(fmtMarkdown(results, pluginRoot));
  }
  const anyFail = results.some((r) => !r.pass);
  process.exit(anyFail ? 1 : 0);
}

main();
