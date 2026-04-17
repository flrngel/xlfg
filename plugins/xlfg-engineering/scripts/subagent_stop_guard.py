#!/usr/bin/env python3
"""xlfg SubagentStop guard — blocks xlfg specialists from stopping before
their promised artifact exists and carries a terminal status.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_PRIMARY_ARTIFACT_RE = re.compile(r"PRIMARY_ARTIFACT:\s*([^\n\r\"}`\\]+)", re.IGNORECASE)
_PRIMARY_LOWER_RE = re.compile(r"primary_artifact:\s*`?([^\n\r`;]+)`?", re.IGNORECASE)
_HANDOFF_RE = re.compile(r"handoff path:\s*`?([^\n\r`;]+)`?", re.IGNORECASE)
_WRITE_TO_RE = re.compile(
    r"(?:Write(?:[^\n\r]{0,120})? to|write(?:[^\n\r]{0,120})? to)\s+([~/.A-Za-z0-9_:\-]+\.(?:md|json|txt|log))"
)
_YAML_FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", re.DOTALL)
_YAML_STATUS_RE = re.compile(r"^status:\s*(DONE|BLOCKED|FAILED)\s*$", re.MULTILINE)
_BARE_STATUS_RE = re.compile(r"^Status:\s*(DONE|BLOCKED|FAILED)\b")
_FINAL_REPLY_RE = re.compile(r"^(DONE|BLOCKED|FAILED)\s+(.+)$", re.DOTALL)


def _same_pathish(a: str, b: str, cwd: str) -> bool:
    if not a or not b:
        return False
    try:
        ra = (Path(cwd or os.getcwd()) / a.strip()).resolve()
        rb = (Path(cwd or os.getcwd()) / b.strip()).resolve()
        return ra == rb
    except OSError:
        return a.strip() == b.strip()


def _first_nonempty_line(text: str) -> str:
    for line in str(text or "").splitlines():
        trimmed = line.strip()
        if trimmed:
            return trimmed
    return ""


def _has_terminal_status(text: str) -> bool:
    body = str(text or "")
    yaml = _YAML_FRONTMATTER_RE.match(body)
    if yaml and _YAML_STATUS_RE.search(yaml.group(1)):
        return True
    return bool(_BARE_STATUS_RE.match(_first_nonempty_line(body)))


def _artifact_has_final_status(file_path: str, cwd: str) -> bool:
    if not file_path:
        return False
    try:
        resolved = (Path(cwd or os.getcwd()) / file_path.strip()).resolve()
        if not resolved.is_file() or resolved.stat().st_size == 0:
            return False
        return _has_terminal_status(resolved.read_text(encoding="utf-8"))
    except OSError:
        return False


def _strip_candidate(raw: str) -> str:
    return raw.strip().strip("'\"`{").strip("'\"`}").strip()


def _extract_expected_artifact(transcript_text: str) -> str | None:
    hay = str(transcript_text or "")

    # Pass 1: scan FULL transcript for PRIMARY_ARTIFACT lines that look like absolute paths.
    primary_last: str | None = None
    for match in _PRIMARY_ARTIFACT_RE.finditer(hay):
        candidate = _strip_candidate(match.group(1) or "")
        if (
            candidate
            and re.match(r"^[/~]", candidate)
            and "\\" not in candidate
            and len(candidate) <= 300
        ):
            primary_last = candidate
    if primary_last:
        return primary_last

    # Pass 2: fall back to tail-based heuristics for other patterns
    tail = hay[-40000:]
    last: str | None = None
    for pattern in (_PRIMARY_LOWER_RE, _WRITE_TO_RE, _HANDOFF_RE):
        for match in pattern.finditer(tail):
            raw = re.sub(r"\\[nrt].*", "", (match.group(1) or ""), flags=re.DOTALL).strip()
            candidate = _strip_candidate(raw)
            if (
                candidate
                and len(candidate) <= 300
                and "\\" not in candidate
                and re.search(r"[/.]", candidate)
            ):
                last = candidate
        if last:
            return last
    return None


def _block(reason: str) -> None:
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    agent_type = str(payload.get("agent_type") or "").strip()
    if not re.match(r"^xlfg-", agent_type):
        return 0

    cwd = str(payload.get("cwd") or os.getcwd())
    last = str(payload.get("last_assistant_message") or "").strip()
    transcript_path = str(payload.get("agent_transcript_path") or "").strip()

    transcript = ""
    if transcript_path:
        try:
            transcript = Path(transcript_path).read_text(encoding="utf-8")
        except OSError:
            transcript = ""

    expected_artifact = _extract_expected_artifact(transcript)
    final_match = _FINAL_REPLY_RE.match(last)
    if final_match:
        reported_artifact = final_match.group(2).strip()
        reported_ok = _artifact_has_final_status(reported_artifact, cwd)
        expected_ok = (
            _artifact_has_final_status(expected_artifact, cwd) if expected_artifact else False
        )
        if reported_ok and (
            not expected_artifact or _same_pathish(reported_artifact, expected_artifact, cwd)
        ):
            return 0
        if not expected_artifact and reported_ok:
            return 0
        if expected_ok and _same_pathish(reported_artifact, expected_artifact, cwd):
            return 0

    artifact_hint = (
        f" Finalize {expected_artifact} first."
        if expected_artifact
        else " Finalize the promised artifact first."
    )
    _block(
        "xlfg specialists may not stop on setup or progress chatter."
        f"{artifact_hint} Reply exactly DONE <artifact-path>, BLOCKED <artifact-path>, "
        "or FAILED <artifact-path> after the artifact carries YAML frontmatter with "
        "status: DONE|BLOCKED|FAILED (or the legacy bare-Status first line). "
        "If a tool failed, record the failure in the artifact instead of returning early."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
