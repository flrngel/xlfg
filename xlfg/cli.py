from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from . import __version__
from .detect import detect_commands
from .runs import create_run
from .scaffold import init_scaffold
from .util import repo_root
from .verify import verify


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, sort_keys=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xlfg", description="Extreme LFG: file-based SDLC harness")
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    subparsers = parser.add_subparsers(dest="command")

    p_init = subparsers.add_parser("init", help="Initialize docs/xlfg + .xlfg scaffolding")
    p_init.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_start = subparsers.add_parser("start", help="Start a new run and write initial context")
    p_start.add_argument("request", help="Feature/bugfix request")
    p_start.add_argument("--root", default=None, help="Repo root (default: auto-detect)")
    p_start.add_argument("--run-id", default=None, help="Optional explicit run id")

    p_detect = subparsers.add_parser("detect", help="Detect verification commands")
    p_detect.add_argument("--root", default=None, help="Repo root (default: auto-detect)")

    p_verify = subparsers.add_parser("verify", help="Run verification and write evidence")
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

    if args.command == "init":
        result = init_scaffold(root)
        _print_json({"root": str(root), **result})
        return 0

    if args.command == "start":
        init_scaffold(root)
        result = create_run(root, request=args.request, run_id=args.run_id)
        _print_json({"root": str(root), **result})
        return 0

    if args.command == "detect":
        detected = detect_commands(root)
        _print_json({"root": str(root), **detected})
        return 0

    if args.command == "verify":
        init_scaffold(root)
        result = verify(root, run_id=args.run_id, mode=args.mode)
        _print_json({"root": str(root), **result})
        return 0 if result.get("ok") else 2

    parser.print_help()
    return 1
