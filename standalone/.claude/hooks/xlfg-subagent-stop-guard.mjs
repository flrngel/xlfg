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

function artifactHasFinalStatus(filePath, cwd) {
  if (!filePath) return false;
  try {
    const resolved = path.resolve(cwd || process.cwd(), filePath.trim());
    const stat = fs.statSync(resolved);
    if (!stat.isFile() || stat.size === 0) return false;
    const text = fs.readFileSync(resolved, "utf8");
    return /^Status:\s*(DONE|BLOCKED|FAILED)\b/.test(firstNonEmptyLine(text));
  } catch {
    return false;
  }
}

function extractExpectedArtifact(transcriptText) {
  const hay = String(transcriptText || "");
  const tail = hay.slice(-40000);
  const patterns = [
    /PRIMARY_ARTIFACT:\s*([^\n\r"}]+)/gi,
    /primary_artifact:\s*`?([^\n\r`;]+)`?/gi,
    /(?:Write(?:[^\n\r]{0,120})? to|write(?:[^\n\r]{0,120})? to)\s+([~/.A-Za-z0-9_:\-]+\.(?:md|json|txt|log))/g,
    /handoff path:\s*`?([^\n\r`;]+)`?/gi,
  ];
  let last = null;
  for (const pattern of patterns) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(tail)) !== null) {
      const candidate = (match[1] || "").trim().replace(/^['"`{]+|['"`}]+$/g, "");
      if (candidate) last = candidate;
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
const stopHookActive = Boolean(payload.stop_hook_active);

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

if (stopHookActive) {
  process.exit(0);
}

const artifactHint = expectedArtifact ? ` Finalize ${expectedArtifact} first.` : " Finalize the promised artifact first.";
block(`xlfg specialists may not stop on setup or progress chatter.${artifactHint} Reply exactly DONE <artifact-path>, BLOCKED <artifact-path>, or FAILED <artifact-path> after the artifact exists with Status: DONE|BLOCKED|FAILED. If a tool failed, record the failure in the artifact instead of returning early.`);
