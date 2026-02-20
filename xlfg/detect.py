from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tomllib


def _read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _maybe_load_commands_config(root: Path) -> Optional[dict]:
    cfg_path = root / "docs" / "xlfg" / "knowledge" / "commands.json"
    if not cfg_path.exists():
        return None
    cfg = _read_json(cfg_path)
    if not isinstance(cfg, dict):
        return None
    # Treat a config as "active" if it sets any commands.
    install = cfg.get("install")
    fast = cfg.get("verify_fast")
    full = cfg.get("verify_full")
    if install or (isinstance(fast, list) and fast) or (isinstance(full, list) and full):
        return cfg
    return None


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
                # Skip pattern rules
                if t and not any(ch in t for ch in "%$"):
                    targets.add(t)
    except Exception:
        return targets
    return targets


def detect_commands(root: Path) -> Dict[str, Any]:
    """Detect canonical project verification commands.

    Returns:
      {
        "install": str|None,
        "verify_fast": list[str],
        "verify_full": list[str],
        "notes": list[str],
      }

    If `docs/xlfg/knowledge/commands.json` is populated, it wins.
    """

    cfg = _maybe_load_commands_config(root)
    if cfg:
        return {
            "install": cfg.get("install"),
            "verify_fast": list(cfg.get("verify_fast") or []),
            "verify_full": list(cfg.get("verify_full") or []),
            "notes": ["Using docs/xlfg/knowledge/commands.json"],
        }

    notes: List[str] = []
    install: Optional[str] = None
    fast: List[str] = []
    full: List[str] = []

    # 1) Makefile
    makefile = root / "Makefile"
    if makefile.exists():
        targets = _parse_makefile_targets(makefile)
        if "ci" in targets:
            full.append("make ci")
            notes.append("Detected Makefile target: ci")
        if "test" in targets and "make test" not in full:
            full.append("make test")
            notes.append("Detected Makefile target: test")
        if "lint" in targets:
            fast.append("make lint")
            if "make lint" not in full:
                full.append("make lint")

    # 2) Node
    pkg_json = root / "package.json"
    if pkg_json.exists():
        pm = _detect_package_manager(root)
        pkg = _read_json(pkg_json) or {}
        scripts = (pkg.get("scripts") or {}) if isinstance(pkg, dict) else {}
        if scripts:
            notes.append(f"Detected package.json (pm={pm})")

        def run(script: str) -> str:
            # yarn doesn't require `run` for many scripts, but it's fine.
            if pm == "npm":
                return f"npm run {script}"
            if pm == "yarn":
                return f"yarn {script}"
            if pm == "pnpm":
                return f"pnpm {script}"
            if pm == "bun":
                return f"bun run {script}"
            return f"{pm} run {script}"

        install = {
            "npm": "npm install",
            "yarn": "yarn install",
            "pnpm": "pnpm install",
            "bun": "bun install",
        }.get(pm, f"{pm} install")

        # Order: fastest checks first
        for s in ("lint", "format", "typecheck"):
            if isinstance(scripts, dict) and s in scripts:
                fast.append(run(s))

        if isinstance(scripts, dict) and "test" in scripts:
            # tests are usually slower; keep in full
            full.append(run("test"))

        for s in ("build",):
            if isinstance(scripts, dict) and s in scripts:
                full.append(run(s))

    # 3) Python
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        notes.append("Detected pyproject.toml")
        tool_prefix = "python -m"
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except Exception:
            data = {}

        is_poetry = isinstance(data.get("tool"), dict) and "poetry" in (data.get("tool") or {})
        if is_poetry:
            install = install or "poetry install"
            tool_prefix = "poetry run python -m"

        def has_dep(name: str) -> bool:
            # Look in common locations
            for path in [
                ("project", "dependencies"),
                ("project", "optional-dependencies"),
                ("tool", "poetry", "dependencies"),
                ("tool", "poetry", "group"),
            ]:
                cur: Any = data
                ok = True
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        ok = False
                        break
                    cur = cur[key]
                if not ok:
                    continue
                # dependencies list
                if isinstance(cur, list) and any(str(dep).startswith(name) for dep in cur):
                    return True
                if isinstance(cur, dict):
                    if name in cur:
                        return True
                    # poetry groups
                    if path == ("tool", "poetry", "group"):
                        for grp in cur.values():
                            if isinstance(grp, dict) and isinstance(grp.get("dependencies"), dict) and name in grp["dependencies"]:
                                return True
            return False

        # ruff / mypy / pytest
        if has_dep("ruff") or (root / ".ruff.toml").exists() or (root / "ruff.toml").exists():
            fast.append(f"{tool_prefix} ruff check .")

        if has_dep("mypy"):
            fast.append(f"{tool_prefix} mypy .")
            full.append(f"{tool_prefix} mypy .")

        if has_dep("pytest") or (root / "pytest.ini").exists() or (root / "tests").exists():
            full.append(f"{tool_prefix} pytest")

    # 4) Go
    if (root / "go.mod").exists():
        notes.append("Detected go.mod")
        full.append("go test ./...")
        fast.append("go test ./...")

    # 5) Rust
    if (root / "Cargo.toml").exists():
        notes.append("Detected Cargo.toml")
        full.append("cargo test")
        fast.append("cargo test")

    # 6) Java / Gradle / Maven
    if (root / "gradlew").exists():
        notes.append("Detected gradlew")
        full.append("./gradlew test")
    if (root / "mvnw").exists():
        notes.append("Detected mvnw")
        full.append("./mvnw test")

    # De-dupe while preserving order
    def dedupe(cmds: List[str]) -> List[str]:
        out: List[str] = []
        seen = set()
        for c in cmds:
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
        return out

    fast = dedupe([c for c in fast if c])
    full = dedupe([c for c in full if c])

    if not full:
        notes.append("No verification commands detected. Populate docs/xlfg/knowledge/commands.json.")

    return {
        "install": install,
        "verify_fast": fast,
        "verify_full": full,
        "notes": notes,
    }
