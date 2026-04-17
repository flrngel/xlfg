#!/usr/bin/env python3
"""xlfg post-mortem — deterministic per-run breakdown.

Reads docs/xlfg/runs/<RUN_ID>/phase-timings.jsonl, the run's artifact
listing, and the global ledger.jsonl (filtered by run id) to answer
the question: "what did this run actually do, and where did the time go?"

The script is deterministic and side-effect free. The /xlfg-audit
slash command shells out to it, prints the table, and then asks the
user whether to submit the redacted report to flrngel/xlfg.

Usage:
  post_mortem.py                # latest run under docs/xlfg/runs/
  post_mortem.py --run <RUN_ID> # specific run
  post_mortem.py --json         # machine-readable instead of markdown
  post_mortem.py --public       # privacy-safe report for flrngel/xlfg

Exits 0 on success, 2 on bad args, 3 if no run dir exists.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ALL_PHASES_FULL = (
    "recall",
    "intent",
    "context",
    "plan",
    "implement",
    "verify",
    "review",
    "compound",
)
ALL_PHASES_DEBUG = ("recall", "intent", "context", "debug")

_RUN_DIR_RE = re.compile(r"^\d{8}-\d{6}-")
_RUN_TS_RE = re.compile(r"^(\d{8})-(\d{6})-")


def _parse_args(argv: list[str]) -> dict[str, object]:
    out: dict[str, object] = {"json": False, "public": False}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--run" and i + 1 < len(argv):
            out["run"] = argv[i + 1]
            i += 2
            continue
        if k == "--json":
            out["json"] = True
            i += 1
            continue
        if k == "--public":
            out["public"] = True
            i += 1
            continue
        if k == "--root" and i + 1 < len(argv):
            out["root"] = argv[i + 1]
            i += 2
            continue
        raise ValueError(f"unexpected arg: {k}")
    return out


def _pick_latest_run(runs_dir: Path) -> str | None:
    try:
        entries = list(runs_dir.iterdir())
    except OSError:
        return None
    dirs = sorted(e.name for e in entries if e.is_dir() and _RUN_DIR_RE.match(e.name))
    return dirs[-1] if dirs else None


def _read_jsonl(p: Path) -> list[dict[str, object]]:
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    out: list[dict[str, object]] = []
    for line in text.split("\n"):
        trimmed = line.strip()
        if not trimmed:
            continue
        try:
            out.append(json.loads(trimmed))
        except json.JSONDecodeError:
            continue
    return out


def _parse_iso(ts: str) -> float | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            dt = datetime.fromisoformat(ts[:-1] + "+00:00")
        else:
            dt = datetime.fromisoformat(ts)
        return dt.timestamp()
    except ValueError:
        return None


def _diff_seconds(start_iso: str, end_iso: str) -> int | None:
    a = _parse_iso(start_iso)
    b = _parse_iso(end_iso)
    if a is None or b is None or b < a:
        return None
    return round(b - a)


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    return f"{m}m{s}s" if s else f"{m}m"


def _fmt_bytes(b: int) -> str:
    if b < 1024:
        return f"{b}B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f}KB"
    return f"{b / (1024 * 1024):.1f}MB"


def _run_timestamp(run_id: str) -> str:
    m = _RUN_TS_RE.match(run_id)
    return f"{m.group(1)}-{m.group(2)}" if m else "<unknown-run>"


def _run_mode(phase_order: list[str], artifact_stats: dict[str, dict[str, int]] | None) -> str:
    if "debug" in phase_order or (artifact_stats and "debug" in artifact_stats):
        return "/xlfg-debug"
    return "/xlfg"


def _build_phase_rows(
    timings: list[dict[str, object]], phase_order: list[str]
) -> dict[str, dict[str, object]]:
    by_phase: dict[str, dict[str, object]] = {}
    for phase in phase_order:
        by_phase[phase] = {
            "invocations": 0,
            "totalSeconds": 0,
            "hasTiming": False,
            "openStart": None,
        }
    for ev in timings:
        phase = str(ev.get("phase") or "")
        if phase not in by_phase:
            by_phase[phase] = {
                "invocations": 0,
                "totalSeconds": 0,
                "hasTiming": False,
                "openStart": None,
            }
        row = by_phase[phase]
        if ev.get("event") == "start":
            row["openStart"] = ev.get("ts")
        elif ev.get("event") == "end" and row["openStart"]:
            d = _diff_seconds(str(row["openStart"]), str(ev.get("ts") or ""))
            if d is not None:
                row["totalSeconds"] = int(row["totalSeconds"]) + d  # type: ignore[operator]
                row["invocations"] = int(row["invocations"]) + 1  # type: ignore[operator]
                row["hasTiming"] = True
            row["openStart"] = None
    return by_phase


def _list_run_artifacts(run_dir: Path) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    if not run_dir.exists():
        return out
    for path in run_dir.rglob("*"):
        if path.is_file():
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            rel = path.relative_to(run_dir).as_posix()
            out.append({"rel": rel, "bytes": size})
    return out


def _artifacts_by_phase(artifacts: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    mapping = {
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
    }
    grouped: dict[str, dict[str, int]] = {}
    for a in artifacts:
        rel = str(a["rel"])
        base = Path(rel).name
        phase = mapping.get(base)
        if not phase:
            if rel.startswith("tasks/"):
                phase = "implement"
            elif rel.startswith("reviews/"):
                phase = "review"
            else:
                phase = "other"
        row = grouped.setdefault(phase, {"count": 0, "bytes": 0})
        row["count"] += 1
        row["bytes"] += int(a["bytes"])
    return grouped


def _build_suggestions(
    phase_rows: dict[str, dict[str, object]],
    phase_state: dict[str, object] | None,
    artifact_stats: dict[str, dict[str, int]],
    ledger_entries: list[dict[str, object]],
    has_timings: bool,
) -> list[str]:
    suggestions: list[str] = []
    ranked = sorted(
        (item for item in phase_rows.items() if item[1]["hasTiming"]),
        key=lambda item: int(item[1]["totalSeconds"]),
        reverse=True,
    )

    if has_timings and ranked:
        slowest_phase, slowest_row = ranked[0]
        if int(slowest_row["totalSeconds"]) >= 600:
            suggestions.append(
                f"slowest phase `{slowest_phase}` took {_fmt_duration(int(slowest_row['totalSeconds']))} "
                f"across {slowest_row['invocations']} invocation(s); consider splitting the lane or "
                "tightening the atomic packet so the specialist does less per turn."
            )
        if len(ranked) >= 2:
            second_phase, second_row = ranked[1]
            if (
                second_row["hasTiming"]
                and int(slowest_row["totalSeconds"]) > 0
                and int(second_row["totalSeconds"]) / int(slowest_row["totalSeconds"]) < 0.25
            ):
                suggestions.append(
                    f"time is concentrated in `{slowest_phase}` ({_fmt_duration(int(slowest_row['totalSeconds']))}); "
                    f"next phase `{second_phase}` was {_fmt_duration(int(second_row['totalSeconds']))} — "
                    "the bottleneck is real, not noise."
                )

    loopbacks = int(
        phase_state.get("loopback_count", 0) if phase_state else 0  # type: ignore[arg-type]
    )
    if loopbacks > 0:
        suggestions.append(
            f"{loopbacks} loopback(s) occurred; check the workboard's blockers section to see "
            "which phase rejected its predecessor and whether the test contract was the cause."
        )

    for phase, row in phase_rows.items():
        if int(row["invocations"]) > 1:
            suggestions.append(
                f"phase `{phase}` ran {row['invocations']} times — a re-run usually means a downstream "
                "phase rejected its output; tighten the upstream done-check to fail earlier."
            )

    for phase, stats in artifact_stats.items():
        if phase in ("_meta", "other"):
            continue
        if stats["bytes"] > 80 * 1024:
            suggestions.append(
                f"phase `{phase}` produced {_fmt_bytes(stats['bytes'])} across {stats['count']} file(s) — "
                "large artifacts inflate context cost on later phases; consider summarizing."
            )

    if not has_timings:
        suggestions.append(
            "no `phase-timings.jsonl` recorded for this run — wall-time analysis unavailable. "
            "New runs (>= v4.2.0) record timings automatically; older runs only show artifact shape."
        )

    if not suggestions:
        suggestions.append("no obvious cost driver detected — this run was lean.")
    return suggestions


def _build_public_feedback(
    phase_rows: dict[str, dict[str, object]],
    phase_state: dict[str, object] | None,
    artifact_stats: dict[str, dict[str, int]],
    table_rows: list[dict[str, object]],
    has_timings: bool,
) -> list[str]:
    feedback: list[str] = []
    ranked = sorted(
        (item for item in phase_rows.items() if item[1]["hasTiming"]),
        key=lambda item: int(item[1]["totalSeconds"]),
        reverse=True,
    )

    if has_timings and ranked:
        slowest_phase, slowest_row = ranked[0]
        if int(slowest_row["totalSeconds"]) >= 600:
            feedback.append(
                f"slow_phase: `{slowest_phase}` took {_fmt_duration(int(slowest_row['totalSeconds']))} "
                f"across {slowest_row['invocations']} invocation(s); consider splitting the lane or "
                "tightening the specialist packet."
            )
        if len(ranked) >= 2:
            second_phase, second_row = ranked[1]
            if (
                second_row["hasTiming"]
                and int(slowest_row["totalSeconds"]) > 0
                and int(second_row["totalSeconds"]) / int(slowest_row["totalSeconds"]) < 0.25
            ):
                feedback.append(
                    f"dominant_phase: `{slowest_phase}` dominated runtime at "
                    f"{_fmt_duration(int(slowest_row['totalSeconds']))}; next phase `{second_phase}` was "
                    f"{_fmt_duration(int(second_row['totalSeconds']))}."
                )

    loopbacks = int(
        phase_state.get("loopback_count", 0) if phase_state else 0  # type: ignore[arg-type]
    )
    if loopbacks > 0:
        feedback.append(
            f"loopback: {loopbacks} loopback(s) occurred; xlfg may need stronger upstream "
            "done checks or clearer phase rejection signals."
        )

    for phase, row in phase_rows.items():
        if int(row["invocations"]) > 1:
            feedback.append(
                f"phase_rerun: `{phase}` ran {row['invocations']} times; a downstream gate likely "
                "rejected earlier output."
            )

    for phase, stats in artifact_stats.items():
        if phase in ("_meta", "other"):
            continue
        if stats["bytes"] > 80 * 1024:
            feedback.append(
                f"large_artifacts: `{phase}` produced {_fmt_bytes(stats['bytes'])} across "
                f"{stats['count']} file(s); later phases may pay unnecessary context cost."
            )

    incomplete_phases = [r["phase"] for r in table_rows if r["status"] == "INCOMPLETE"]
    if incomplete_phases:
        feedback.append(
            f"incomplete_phase_state: {len(incomplete_phases)} phase(s) were not marked DONE "
            "when the run state was read."
        )

    if not has_timings:
        feedback.append(
            "missing_timings: no `phase-timings.jsonl` was recorded, so wall-time analysis "
            "is unavailable."
        )

    if not feedback:
        feedback.append("no_cost_driver: no obvious harness cost driver was detected.")
    return feedback


def _render_local_markdown(ctx: dict[str, object]) -> str:
    run_id = ctx["run_id"]
    root = ctx["root"]
    run_dir = ctx["run_dir"]
    has_timings = ctx["has_timings"]
    total_seconds = ctx["total_seconds"]
    total_artifacts = ctx["total_artifacts"]
    total_bytes = ctx["total_bytes"]
    loopbacks = ctx["loopbacks"]
    ledger_counts: dict[str, int] = ctx["ledger_counts"]  # type: ignore[assignment]
    table_rows: list[dict[str, object]] = ctx["table_rows"]  # type: ignore[assignment]
    suggestions: list[str] = ctx["suggestions"]  # type: ignore[assignment]

    lines: list[str] = []
    lines.append(f"# xlfg post-mortem — `{run_id}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- run dir: `{Path(str(run_dir)).relative_to(Path(str(root)))}`")
    lines.append(
        f"- total wall time: {_fmt_duration(int(total_seconds)) if has_timings else 'n/a (no phase-timings.jsonl)'}"
    )
    lines.append(f"- total artifacts: {total_artifacts} files, {_fmt_bytes(int(total_bytes))}")
    lines.append(f"- loopbacks: {loopbacks}")
    if ledger_counts:
        parts = ", ".join(f"{k}={v}" for k, v in ledger_counts.items())
        lines.append(f"- ledger entries for this run: {parts}")
    else:
        lines.append("- ledger entries for this run: none")
    lines.append("")
    lines.append("## Phase breakdown")
    lines.append("")
    lines.append("| Phase | Status | Wall time | Invocations | Artifacts | Bytes |")
    lines.append("|---|---|---|---|---|---|")
    for r in table_rows:
        lines.append(
            f"| {r['phase']} | {r['status']} | {r['wall']} | {r['invocations']} "
            f"| {r['artifacts']} | {r['artifactBytes']} |"
        )
    lines.append("")
    lines.append("## How xlfg can be better (based on this run)")
    lines.append("")
    for s in suggestions:
        lines.append(f"- {s}")
    lines.append("")
    return "\n".join(lines)


def _render_public_markdown(ctx: dict[str, object]) -> str:
    run_id = str(ctx["run_id"])
    phase_order: list[str] = ctx["phase_order"]  # type: ignore[assignment]
    artifact_stats: dict[str, dict[str, int]] = ctx["artifact_stats"]  # type: ignore[assignment]
    has_timings = ctx["has_timings"]
    total_seconds = ctx["total_seconds"]
    total_artifacts = ctx["total_artifacts"]
    total_bytes = ctx["total_bytes"]
    loopbacks = ctx["loopbacks"]
    ledger_counts: dict[str, int] = ctx["ledger_counts"]  # type: ignore[assignment]
    table_rows: list[dict[str, object]] = ctx["table_rows"]  # type: ignore[assignment]
    feedback: list[str] = ctx["feedback"]  # type: ignore[assignment]

    lines: list[str] = []
    lines.append(f"# xlfg efficiency report — `{_run_timestamp(run_id)}`")
    lines.append("")
    lines.append(
        "This public report is intentionally limited to xlfg harness behavior. It omits the "
        "user request, run slug, repository paths, artifact names, artifact contents, command "
        "output, and project-specific text."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- run timestamp: `{_run_timestamp(run_id)}`")
    lines.append(f"- command mode: `{_run_mode(phase_order, artifact_stats)}`")
    lines.append(
        f"- total wall time: {_fmt_duration(int(total_seconds)) if has_timings else 'n/a (no phase-timings.jsonl)'}"
    )
    lines.append(f"- total artifacts: {total_artifacts} files, {_fmt_bytes(int(total_bytes))}")
    lines.append(f"- loopbacks: {loopbacks}")
    lines.append(f"- timing data: {'present' if has_timings else 'missing'}")
    if ledger_counts:
        parts = ", ".join(f"{k}={v}" for k, v in ledger_counts.items())
        lines.append(f"- ledger event counts: {parts}")
    else:
        lines.append("- ledger event counts: none")
    lines.append("")
    lines.append("## Phase breakdown")
    lines.append("")
    lines.append("| Phase | Status | Wall time | Invocations | Artifacts | Bytes |")
    lines.append("|---|---|---|---|---|---|")
    for r in table_rows:
        lines.append(
            f"| {r['phase']} | {r['status']} | {r['wall']} | {r['invocations']} "
            f"| {r['artifacts']} | {r['artifactBytes']} |"
        )
    lines.append("")
    lines.append("## Harness feedback")
    lines.append("")
    for item in feedback:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    try:
        args = _parse_args(argv)
    except ValueError as err:
        sys.stderr.write(f"post-mortem: {err}\n")
        return 2

    root = Path(str(args.get("root") or Path.cwd())).resolve()
    runs_root = root / "docs/xlfg/runs"

    run_id = args.get("run") or _pick_latest_run(runs_root)
    if not run_id:
        sys.stderr.write(f"post-mortem: no runs found under {runs_root}\n")
        return 3
    run_id = str(run_id)

    run_dir = runs_root / run_id
    if not run_dir.exists():
        sys.stderr.write(f"post-mortem: run dir not found: {run_dir}\n")
        return 3

    timings = _read_jsonl(run_dir / "phase-timings.jsonl")
    ledger = [
        e
        for e in _read_jsonl(root / "docs/xlfg/knowledge/ledger.jsonl")
        if e.get("run") == run_id
    ]

    phase_state: dict[str, object] | None = None
    for candidate in (root / ".xlfg/phase-state.json", run_dir / "phase-state.json"):
        try:
            parsed = json.loads(candidate.read_text(encoding="utf-8"))
            if parsed.get("run_id") == run_id:
                phase_state = parsed
                break
        except (OSError, json.JSONDecodeError):
            continue

    if phase_state and isinstance(phase_state.get("phases"), list):
        phase_order = list(phase_state["phases"])
    elif timings:
        seen: list[str] = []
        for t in timings:
            p = str(t.get("phase") or "")
            if p and p not in seen:
                seen.append(p)
        phase_order = seen
    else:
        phase_order = list(ALL_PHASES_FULL)

    phase_rows = _build_phase_rows(timings, phase_order)
    artifacts = _list_run_artifacts(run_dir)
    art_stats = _artifacts_by_phase(artifacts)

    has_timings = len(timings) > 0

    completed_set = set((phase_state or {}).get("completed") or [])

    table_rows: list[dict[str, object]] = []
    for phase in phase_order:
        r = phase_rows.get(phase) or {"invocations": 0, "totalSeconds": 0, "hasTiming": False}
        a = art_stats.get(phase) or {"count": 0, "bytes": 0}
        if phase_state:
            status = "DONE" if phase in completed_set else "INCOMPLETE"
        else:
            status = "—"
        table_rows.append(
            {
                "phase": phase,
                "status": status,
                "wall": _fmt_duration(int(r["totalSeconds"])) if r["hasTiming"] else _fmt_duration(None),
                "invocations": int(r["invocations"]),
                "artifacts": int(a["count"]),
                "artifactBytes": _fmt_bytes(int(a["bytes"])),
            }
        )

    total_seconds = sum(
        int(r["totalSeconds"]) for r in phase_rows.values() if r["hasTiming"]
    )
    total_artifacts = len(artifacts)
    total_bytes = sum(int(a["bytes"]) for a in artifacts)
    loopbacks = int((phase_state or {}).get("loopback_count", 0))
    ledger_counts: dict[str, int] = {}
    for e in ledger:
        t = e.get("type")
        if isinstance(t, str) and t:
            ledger_counts[t] = ledger_counts.get(t, 0) + 1

    suggestions = _build_suggestions(phase_rows, phase_state, art_stats, ledger, has_timings)
    feedback = _build_public_feedback(phase_rows, phase_state, art_stats, table_rows, has_timings)

    if args.get("json"):
        if args.get("public"):
            sys.stdout.write(
                json.dumps(
                    {
                        "run_timestamp": _run_timestamp(run_id),
                        "command_mode": _run_mode(phase_order, art_stats),
                        "total_seconds": total_seconds,
                        "total_artifacts": total_artifacts,
                        "total_bytes": total_bytes,
                        "loopbacks": loopbacks,
                        "has_timings": has_timings,
                        "phases": table_rows,
                        "ledger_counts": ledger_counts,
                        "feedback": feedback,
                    },
                    indent=2,
                )
                + "\n"
            )
        else:
            sys.stdout.write(
                json.dumps(
                    {
                        "run_id": run_id,
                        "run_dir": str(run_dir),
                        "total_seconds": total_seconds,
                        "total_artifacts": total_artifacts,
                        "total_bytes": total_bytes,
                        "loopbacks": loopbacks,
                        "has_timings": has_timings,
                        "phases": table_rows,
                        "ledger_counts": ledger_counts,
                        "suggestions": suggestions,
                    },
                    indent=2,
                )
                + "\n"
            )
        return 0

    ctx = {
        "run_id": run_id,
        "root": str(root),
        "run_dir": str(run_dir),
        "phase_order": phase_order,
        "artifact_stats": art_stats,
        "has_timings": has_timings,
        "total_seconds": total_seconds,
        "total_artifacts": total_artifacts,
        "total_bytes": total_bytes,
        "loopbacks": loopbacks,
        "ledger_counts": ledger_counts,
        "table_rows": table_rows,
        "suggestions": suggestions,
        "feedback": feedback,
    }
    report = _render_public_markdown(ctx) if args.get("public") else _render_local_markdown(ctx)
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
