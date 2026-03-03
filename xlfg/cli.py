from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import __version__
from .detect import detect_commands
from .doctor import cleanup_dev_server, ensure_dev_server
from .runs import create_run
from .scaffold import ensure_scaffold, scaffold_status
from .util import repo_root
from .verify import verify


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, sort_keys=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="xlfg",
        description="XLFG: diagnosis-first SDLC harness",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    subparsers = parser.add_subparsers(dest="command")

    p_prepare = subparsers.add_parser("prepare", help="Fast scaffold/version check with auto-migration")
    p_prepare.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_init = subparsers.add_parser("init", help="Bootstrap or repair docs/xlfg + .xlfg scaffolding")
    p_init.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_status = subparsers.add_parser("status", help="Show scaffold version status")
    p_status.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_start = subparsers.add_parser("start", help="Start a new run and write initial context")
    p_start.add_argument("request", help="Feature/bugfix request")
    p_start.add_argument("--root", default=None, help="Repo root (default: auto-detect)")
    p_start.add_argument("--run-id", default=None, help="Optional explicit run id")

    p_detect = subparsers.add_parser("detect", help="Detect verification commands")
    p_detect.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_doctor = subparsers.add_parser("doctor", help="Check or start the configured dev server")
    p_doctor.add_argument("--root", default=None, help="Repo root (default: auto-detect)")
    p_doctor.add_argument("--run", dest="run_id", default=None, help="Run id (default: latest)")

    p_verify = subparsers.add_parser("verify", help="Run layered verification and write evidence")
    p_verify.add_argument("--root", default=None, help="Repo root (default: auto-detect)")
    p_verify.add_argument("--run", dest="run_id", default=None, help="Run id (default: latest)")
    p_verify.add_argument("--mode", choices=["fast", "full"], default="full")

    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if not args.command:
        parser.print_help()
        return 1

    root = Path(args.root).resolve() if getattr(args, "root", None) else repo_root()

    if args.command == "status":
        _print_json({"root": str(root), **scaffold_status(root, __version__)})
        return 0

    if args.command in {"prepare", "init"}:
        result = ensure_scaffold(root, __version__)
        _print_json({"root": str(root), **result})
        return 0

    if args.command == "start":
        prep = ensure_scaffold(root, __version__)
        result = create_run(root, request=args.request, run_id=args.run_id)
        _print_json({"root": str(root), "prepare": prep, **result})
        return 0

    if args.command == "detect":
        ensure_scaffold(root, __version__)
        detected = detect_commands(root)
        _print_json({"root": str(root), **detected})
        return 0

    if args.command == "doctor":
        ensure_scaffold(root, __version__)
        from .runs import latest_run_id

        rid = args.run_id or latest_run_id(root)
        if rid is None:
            raise RuntimeError("No run found. Run `xlfg start ...` first.")
        detected = detect_commands(root)
        report, handle = ensure_dev_server(root, rid, detected.get("dev"))
        cleanup = cleanup_dev_server(handle) if handle is not None else None
        _print_json({"root": str(root), "run_id": rid, "report": report, "cleanup": cleanup})
        return 0 if report.get("status") in {"reused", "started", "no-config"} else 2

    if args.command == "verify":
        ensure_scaffold(root, __version__)
        result = verify(root, run_id=args.run_id, mode=args.mode)
        _print_json({"root": str(root), **result})
        return 0 if result.get("ok") else 2

    parser.print_help()
    return 1
