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

function samePathish(a, b, cwd) {
  if (!a || !b) return false;
  try {
    const ra = path.resolve(cwd || process.cwd(), a.trim());
    const rb = path.resolve(cwd || process.cwd(), b.trim());
    return ra === rb;
  } catch {
    return a.trim() === b.trim();
  }
}

function firstNonEmptyLine(text) {
  for (const line of String(text || "").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (trimmed) return trimmed;
  }
  return "";
}

// Canonical shape (v3.1.0+): YAML frontmatter at the top of the file with
// `status: DONE|BLOCKED|FAILED`. Legacy shape: bare `Status: DONE|BLOCKED|FAILED`
// as the first non-empty line. Accept both for backward compatibility.
function hasTerminalStatus(text) {
  const body = String(text || "");
  const yaml = body.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*(?:\r?\n|$)/);
  if (yaml && /^status:\s*(DONE|BLOCKED|FAILED)\s*$/m.test(yaml[1])) {
    return true;
  }
  return /^Status:\s*(DONE|BLOCKED|FAILED)\b/.test(firstNonEmptyLine(body));
}

function artifactHasFinalStatus(filePath, cwd) {
  if (!filePath) return false;
  try {
    const resolved = path.resolve(cwd || process.cwd(), filePath.trim());
    const stat = fs.statSync(resolved);
    if (!stat.isFile() || stat.size === 0) return false;
    const text = fs.readFileSync(resolved, "utf8");
    return hasTerminalStatus(text);
  } catch {
    return false;
  }
}

function extractExpectedArtifact(transcriptText) {
  const hay = String(transcriptText || "");

  // Pass 1: scan FULL transcript for PRIMARY_ARTIFACT lines that look like absolute paths.
  // This survives long transcripts where the tail window misses the dispatch packet.
  const primaryPat = /PRIMARY_ARTIFACT:\s*([^\n\r"}`\\]+)/gi;
  let primaryLast = null;
  let m;
  while ((m = primaryPat.exec(hay)) !== null) {
    const candidate = (m[1] || "").trim().replace(/^['"`{]+|['"`}]+$/g, "").trim();
    // Must look like an absolute path (starts with / or ~) and have no backslashes
    if (candidate && /^[/~]/.test(candidate) && !candidate.includes("\\") && candidate.length <= 300) {
      primaryLast = candidate;
    }
  }
  if (primaryLast) return primaryLast;

  // Pass 2: fall back to tail-based heuristics for other patterns
  const tail = hay.slice(-40000);
  const patterns = [
    /primary_artifact:\s*`?([^\n\r`;]+)`?/gi,
    /(?:Write(?:[^\n\r]{0,120})? to|write(?:[^\n\r]{0,120})? to)\s+([~/.A-Za-z0-9_:\-]+\.(?:md|json|txt|log))/g,
    /handoff path:\s*`?([^\n\r`;]+)`?/gi,
  ];
  let last = null;
  for (const pattern of patterns) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(tail)) !== null) {
      const raw = (match[1] || "").replace(/\\[nrt].*/s, "").trim();
      const candidate = raw.replace(/^['"`{]+|['"`}]+$/g, "").trim();
      if (candidate && candidate.length <= 300 && !candidate.includes("\\") && /[/.]/.test(candidate)) last = candidate;
    }
    if (last) return last;
  }
  return null;
}

function block(reason) {
  process.stdout.write(JSON.stringify({ decision: "block", reason }));
}

const raw = await readStdin();
let payload = {};
try {
  payload = raw.trim() ? JSON.parse(raw) : {};
} catch {
  process.exit(0);
}

const agentType = String(payload.agent_type || "").trim();
if (!/^xlfg-/.test(agentType)) {
  process.exit(0);
}

const cwd = String(payload.cwd || process.cwd());
const last = String(payload.last_assistant_message || "").trim();
const transcriptPath = String(payload.agent_transcript_path || "").trim();

let transcript = "";
if (transcriptPath) {
  try {
    transcript = fs.readFileSync(transcriptPath, "utf8");
  } catch {
    transcript = "";
  }
}

const expectedArtifact = extractExpectedArtifact(transcript);
const finalMatch = last.match(/^(DONE|BLOCKED|FAILED)\s+(.+)$/s);
if (finalMatch) {
  const reportedArtifact = finalMatch[2].trim();
  const reportedOk = artifactHasFinalStatus(reportedArtifact, cwd);
  const expectedOk = expectedArtifact ? artifactHasFinalStatus(expectedArtifact, cwd) : false;
  if (reportedOk && (!expectedArtifact || samePathish(reportedArtifact, expectedArtifact, cwd))) {
    process.exit(0);
  }
  if (!expectedArtifact && reportedOk) {
    process.exit(0);
  }
  if (expectedOk && samePathish(reportedArtifact, expectedArtifact, cwd)) {
    process.exit(0);
  }
}

const artifactHint = expectedArtifact ? ` Finalize ${expectedArtifact} first.` : " Finalize the promised artifact first.";
block(`xlfg specialists may not stop on setup or progress chatter.${artifactHint} Reply exactly DONE <artifact-path>, BLOCKED <artifact-path>, or FAILED <artifact-path> after the artifact carries YAML frontmatter with status: DONE|BLOCKED|FAILED (or the legacy bare-Status first line). If a tool failed, record the failure in the artifact instead of returning early.`);
