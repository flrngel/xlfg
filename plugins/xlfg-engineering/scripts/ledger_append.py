#!/usr/bin/env python3
"""xlfg ledger-append — validates an event against docs/xlfg/knowledge/ledger-schema.md
and appends a single JSON line to docs/xlfg/knowledge/ledger.jsonl.

Usage:
  ledger_append.py --ts ... --run ... --type ... --version ... --summary ...
or pipe a JSON object on stdin:
  echo '{...}' | ledger_append.py

Optional flags: --id, --tags (comma-separated), --stage, --role, --status, --supersedes,
  --symptom, --root_cause, --action, --prevention, --lex, --evidence (comma-separated).

Extra options:
  --ledger <path>   Override ledger.jsonl location (default docs/xlfg/knowledge/ledger.jsonl
                    relative to cwd).
  --dry-run         Validate only; do not write.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED = ("ts", "run", "type", "version", "summary")
TYPE_ENUM = frozenset(
    (
        "feature",
        "fix",
        "pattern",
        "decision",
        "incident",
        "memory.added",
        "memory.superseded",
        "memory.invalidated",
    )
)
STAGE_ENUM = frozenset(
    (
        "recall",
        "intent",
        "context",
        "plan",
        "implement",
        "verify",
        "review",
        "compound",
        "debug",
    )
)
STATUS_ENUM = frozenset(("active", "superseded", "invalidated"))
TAG_ALLOWLIST = frozenset(
    (
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
    )
)
ALLOWED_KEYS = frozenset(
    (
        *REQUIRED,
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
    )
)

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
RUN_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9][a-z0-9-]*$")

_FLAGS = {"--dry-run": "dryRun"}


def _parse_args(argv: list[str]) -> dict[str, object]:
    out: dict[str, object] = {}
    i = 0
    while i < len(argv):
        key = argv[i]
        if key in _FLAGS:
            out[_FLAGS[key]] = True
            i += 1
            continue
        if not key.startswith("--"):
            raise ValueError(f"unexpected positional arg: {key}")
        name = key[2:]
        if i + 1 >= len(argv):
            raise ValueError(f"flag {key} requires a value")
        val = argv[i + 1]
        if val.startswith("--"):
            raise ValueError(f"flag {key} requires a value")
        out[name] = val
        i += 2
    return out


def _coerce_from_args(args: dict[str, object]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for k, v in args.items():
        if k in ("dryRun", "ledger"):
            continue
        if k in ("tags", "evidence"):
            obj[k] = [s.strip() for s in str(v).split(",") if s.strip()]
        else:
            obj[k] = v
    return obj


def _validate(event: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for k in REQUIRED:
        val = event.get(k)
        if val is None or val == "":
            errors.append(f"missing required field: {k}")
    for k in event:
        if k not in ALLOWED_KEYS:
            errors.append(f"unknown field: {k}")
    if isinstance(event.get("ts"), str) and not TS_RE.match(event["ts"]):
        errors.append(f"ts must be ISO 8601 UTC (e.g. 2026-04-15T14:33:07Z), got: {event['ts']}")
    if isinstance(event.get("run"), str) and not RUN_RE.match(event["run"]):
        errors.append(f"run must match <YYYYMMDD>-<HHMMSS>-<slug>, got: {event['run']}")
    if isinstance(event.get("type"), str) and event["type"] not in TYPE_ENUM:
        errors.append(f"type must be one of {'|'.join(sorted(TYPE_ENUM))}, got: {event['type']}")
    if isinstance(event.get("version"), str) and not SEMVER_RE.match(event["version"]):
        errors.append(f"version must be semver major.minor.patch, got: {event['version']}")
    if isinstance(event.get("summary"), str) and len(event["summary"]) > 280:
        errors.append(f"summary too long ({len(event['summary'])} chars, max 280)")
    if event.get("stage") is not None and event["stage"] not in STAGE_ENUM:
        errors.append(f"stage must be one of {'|'.join(sorted(STAGE_ENUM))}, got: {event['stage']}")
    if event.get("status") is not None and event["status"] not in STATUS_ENUM:
        errors.append(
            f"status must be one of {'|'.join(sorted(STATUS_ENUM))}, got: {event['status']}"
        )
    if event.get("tags") is not None:
        if not isinstance(event["tags"], list):
            errors.append("tags must be an array")
        else:
            for t in event["tags"]:
                if not isinstance(t, str) or t not in TAG_ALLOWLIST:
                    errors.append(f"tag not in allow-list: {json.dumps(t)}")
    if event.get("evidence") is not None and not isinstance(event["evidence"], list):
        errors.append("evidence must be an array")
    return errors


def main(argv: list[str]) -> int:
    try:
        args = _parse_args(argv)
    except ValueError as err:
        sys.stderr.write(f"ledger-append: {err}\n")
        return 2

    stdin_data = "" if sys.stdin.isatty() else sys.stdin.read()
    if stdin_data.strip():
        try:
            event = json.loads(stdin_data)
        except json.JSONDecodeError as err:
            sys.stderr.write(f"ledger-append: invalid JSON on stdin: {err}\n")
            return 2
    else:
        event = _coerce_from_args(args)

    errors = _validate(event)
    if errors:
        sys.stderr.write("ledger-append: rejected event\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        return 1

    if args.get("dryRun"):
        sys.stdout.write(json.dumps(event) + "\n")
        return 0

    ledger_path = (
        Path(str(args["ledger"])).resolve()
        if args.get("ledger")
        else Path.cwd() / "docs/xlfg/knowledge/ledger.jsonl"
    )
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")
    sys.stdout.write(f"{ledger_path}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception as err:  # noqa: BLE001
        sys.stderr.write(f"ledger-append: {err}\n")
        sys.exit(2)
