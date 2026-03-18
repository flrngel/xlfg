from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomllib


_PORT_FLAG_RE = re.compile(r"(?:--port|-p)\s+(\d+)")
_PORT_ENV_RE = re.compile(r"\bPORT=(\d+)\b")
_LOCALHOST_RE = re.compile(r"https?://(?:127\.0\.0\.1|localhost):(\d+)")


def _read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _as_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _clean_notes(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _default_dev_config() -> Dict[str, Any]:
    return {
        "command": None,
        "cwd": ".",
        "port": None,
        "healthcheck": None,
        "startup_timeout_sec": 120,
        "reuse_if_healthy": True,
    }


def _normalize_dev_config(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    cfg = _default_dev_config()
    cfg.update({k: v for k, v in value.items() if k in cfg})
    command = cfg.get("command")
    if command is not None:
        command = str(command).strip() or None
    cfg["command"] = command
    cwd = cfg.get("cwd")
    cfg["cwd"] = str(cwd).strip() if cwd else "."
    try:
        port = int(cfg["port"]) if cfg.get("port") is not None else None
    except Exception:
        port = None
    cfg["port"] = port
    healthcheck = cfg.get("healthcheck")
    cfg["healthcheck"] = str(healthcheck).strip() or None if healthcheck is not None else None
    try:
        timeout = int(cfg.get("startup_timeout_sec") or 120)
    except Exception:
        timeout = 120
    cfg["startup_timeout_sec"] = max(5, timeout)
    cfg["reuse_if_healthy"] = bool(cfg.get("reuse_if_healthy", True))
    if not any(cfg.get(k) for k in ("command", "port", "healthcheck")):
        return None
    return cfg


def _maybe_load_commands_config(root: Path) -> Optional[dict]:
    cfg_path = root / "docs" / "xlfg" / "knowledge" / "commands.json"
    if not cfg_path.exists():
        return None
    raw = _read_json(cfg_path)
    if not isinstance(raw, dict):
        return None

    cfg = {
        "install": raw.get("install"),
        "verify_fast": _as_list(raw.get("verify_fast")),
        "smoke": _as_list(raw.get("smoke")),
        "e2e": _as_list(raw.get("e2e")),
        "verify_full": _as_list(raw.get("verify_full")),
        "dev": _normalize_dev_config(raw.get("dev")),
        "notes": _clean_notes(raw.get("notes")),
    }

    active = bool(
        cfg["install"]
        or cfg["verify_fast"]
        or cfg["smoke"]
        or cfg["e2e"]
        or cfg["verify_full"]
        or cfg["dev"]
    )
    return cfg if active else None


def _detect_package_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "bun.lockb").exists():
        return "bun"
    if (root / "package-lock.json").exists():
        return "npm"
    return "npm"


def _parse_makefile_targets(makefile: Path) -> set[str]:
    targets: set[str] = set()
    try:
        for line in makefile.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.startswith("\t") or line.startswith("#"):
                continue
            if ":" in line:
                t = line.split(":", 1)[0].strip()
                if t and not any(ch in t for ch in "%$"):
                    targets.add(t)
    except Exception:
        return targets
    return targets


def _dedupe(values: List[str]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for v in values:
        s = str(v).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _pm_run(pm: str, script: str) -> str:
    if pm == "npm":
        return f"npm run {script}"
    if pm == "yarn":
        return f"yarn {script}"
    if pm == "pnpm":
        return f"pnpm {script}"
    if pm == "bun":
        return f"bun run {script}"
    return f"{pm} run {script}"


def _guess_port(script_body: str) -> Optional[int]:
    text = script_body.strip()
    for rx in (_PORT_FLAG_RE, _PORT_ENV_RE, _LOCALHOST_RE):
        m = rx.search(text)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return None

    lowered = text.lower()
    defaults = [
        ("vite", 5173),
        ("svelte-kit", 5173),
        ("storybook", 6006),
        ("astro", 4321),
        ("next dev", 3000),
        ("nuxt", 3000),
        ("react-scripts start", 3000),
        ("webpack serve", 8080),
    ]
    for needle, port in defaults:
        if needle in lowered:
            return port
    return None


def _detect_dev_config(pm: str, scripts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(scripts, dict):
        return None
    for name in ("dev", "preview"):
        body = scripts.get(name)
        if not isinstance(body, str):
            continue
        port = _guess_port(body)
        healthcheck = f"http://127.0.0.1:{port}/" if port else None
        return _normalize_dev_config(
            {
                "command": _pm_run(pm, name),
                "cwd": ".",
                "port": port,
                "healthcheck": healthcheck,
                "startup_timeout_sec": 120,
                "reuse_if_healthy": True,
            }
        )
    return None


def detect_commands(root: Path) -> Dict[str, Any]:
    """Detect canonical project verification commands.

    Returns:
      {
        "install": str|None,
        "verify_fast": list[str],
        "smoke": list[str],
        "e2e": list[str],
        "verify_full": list[str],
        "dev": dict|None,
        "notes": list[str],
      }

    If `docs/xlfg/knowledge/commands.json` is populated, it wins.
    """

    cfg = _maybe_load_commands_config(root)
    if cfg:
        return {
            "install": cfg.get("install"),
            "verify_fast": _dedupe(list(cfg.get("verify_fast") or [])),
            "smoke": _dedupe(list(cfg.get("smoke") or [])),
            "e2e": _dedupe(list(cfg.get("e2e") or [])),
            "verify_full": _dedupe(list(cfg.get("verify_full") or [])),
            "dev": cfg.get("dev"),
            "notes": ["Using docs/xlfg/knowledge/commands.json", *cfg.get("notes", [])],
        }

    notes: List[str] = []
    install: Optional[str] = None
    fast: List[str] = []
    smoke: List[str] = []
    e2e: List[str] = []
    full: List[str] = []
    dev: Optional[Dict[str, Any]] = None

    # 1) Makefile
    makefile = root / "Makefile"
    if makefile.exists():
        targets = _parse_makefile_targets(makefile)
        if "ci" in targets:
            full.append("make ci")
            notes.append("Detected Makefile target: ci")
        if "lint" in targets:
            fast.append("make lint")
            notes.append("Detected Makefile target: lint")
        if "typecheck" in targets:
            fast.append("make typecheck")
            notes.append("Detected Makefile target: typecheck")
        if "test" in targets:
            full.append("make test")
            notes.append("Detected Makefile target: test")
        if "smoke" in targets:
            smoke.append("make smoke")
            notes.append("Detected Makefile target: smoke")
        if "e2e" in targets:
            e2e.append("make e2e")
            notes.append("Detected Makefile target: e2e")
        if "dev" in targets:
            dev = _normalize_dev_config(
                {
                    "command": "make dev",
                    "cwd": ".",
                    "port": None,
                    "healthcheck": None,
                    "startup_timeout_sec": 120,
                    "reuse_if_healthy": True,
                }
            )
            notes.append("Detected Makefile target: dev (port/healthcheck not inferred)")

    # 2) Node
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pm = _detect_package_manager(root)
        pkg = _read_json(pkg_json) or {}
        scripts = (pkg.get("scripts") or {}) if isinstance(pkg, dict) else {}
        if scripts:
            notes.append(f"Detected package.json (pm={pm})")

        install = {
            "npm": "npm install",
            "yarn": "yarn install",
            "pnpm": "pnpm install",
            "bun": "bun install",
        }.get(pm, f"{pm} install")

        for s in ("lint", "format", "typecheck", "check", "check:types", "test:unit", "unit", "test:quick"):
            if isinstance(scripts, dict) and s in scripts:
                fast.append(_pm_run(pm, s))

        for s in ("smoke", "test:smoke", "smoke:test", "test:integration", "integration", "test:browser", "test:ui"):
            if isinstance(scripts, dict) and s in scripts:
                smoke.append(_pm_run(pm, s))

        for s in ("e2e", "test:e2e", "e2e:test", "playwright", "cypress", "test:acceptance", "acceptance"):
            if isinstance(scripts, dict) and s in scripts:
                e2e.append(_pm_run(pm, s))

        for s in ("test", "test:ci", "build"):
            if isinstance(scripts, dict) and s in scripts:
                full.append(_pm_run(pm, s))

        # Best-effort dev server detection; prefer explicit commands.json for stable use.
        detected_dev = _detect_dev_config(pm, scripts if isinstance(scripts, dict) else {})
        if detected_dev and not dev:
            dev = detected_dev
            port = detected_dev.get("port")
            notes.append(
                "Detected dev script"
                + (f" (best-effort port={port})" if port else " (fill port/healthcheck in commands.json)")
            )

    # 3) Python
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        notes.append("Detected pyproject.toml")
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        project = data.get("project") if isinstance(data, dict) else {}
        optional = project.get("optional-dependencies") if isinstance(project, dict) else {}
        if isinstance(optional, dict):
            test_extra = optional.get("test") or optional.get("tests")
            lint_extra = optional.get("lint")
            if test_extra or lint_extra:
                notes.append("Detected optional dependency groups for test/lint")

        if (root / "pytest.ini").exists() or (root / "tests").exists():
            full.append("pytest -q")
        # conservative defaults; use commands.json to override if the repo prefers different tools
        fast.append("python -m compileall .")

    # 4) Other language defaults
    if (root / "go.mod").exists():
        notes.append("Detected go.mod")
        fast.append("go vet ./...")
        full.append("go test ./...")

    if (root / "Cargo.toml").exists():
        notes.append("Detected Cargo.toml")
        fast.append("cargo clippy --all-targets --all-features")
        full.append("cargo test")

    if (root / "Gemfile").exists():
        notes.append("Detected Gemfile")
        if (root / "bin" / "rails").exists():
            full.append("bin/rails test")
        else:
            full.append("bundle exec rspec")

    return {
        "install": install,
        "verify_fast": _dedupe(fast),
        "smoke": _dedupe(smoke),
        "e2e": _dedupe(e2e),
        "verify_full": _dedupe(full),
        "dev": dev,
        "notes": _dedupe(notes),
    }
