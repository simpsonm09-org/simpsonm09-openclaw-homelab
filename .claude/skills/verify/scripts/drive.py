#!/usr/bin/env python
"""Drive the openclaw-homelab validator and capture evidence.

Start from the repository root with the project's Python, then run:

    .venv\\Scripts\\python.exe .claude/skills/verify/scripts/drive.py \
        --repo-root . \
        --out artifacts/verify/validator

(The WSL equivalent interpreter is ``.venv/bin/python``.)

The helper runs the real CLI over four inputs and records the exit code,
stdout, and stderr of each: the shipped config (pass), the shipped config with
``gateway.bind`` widened (one hardening violation), the shipped config with a
non-placeholder token (one secret violation), and the default config invoked
with no path argument (pass). It writes ``evidence.json``, prints it, and
returns non-zero when any expected outcome is wrong.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_validator(repo_root: Path, args: list[str]) -> dict[str, Any]:
    """Run ``python -m openclaw_homelab`` with ``args`` and capture the result."""
    env = dict(os.environ)
    src = str(repo_root / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src + (os.pathsep + existing if existing else "")
    completed = subprocess.run(
        [sys.executable, "-m", "openclaw_homelab", *args],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {
        "argv": ["openclaw_homelab", *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def drive(repo_root: Path, out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    fixtures = out / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)

    template = json.loads((repo_root / "config" / "openclaw.json").read_text(encoding="utf-8"))

    widened = copy.deepcopy(template)
    widened["gateway"]["bind"] = "0.0.0.0"
    widened_path = fixtures / "widened-bind.json"
    widened_path.write_text(json.dumps(widened, indent=2), encoding="utf-8")

    # A value that is deliberately not the placeholder. It is not a real token
    # and is never sent anywhere; it exists only to trip the guard.
    unplaced = copy.deepcopy(template)
    unplaced["gateway"]["auth"]["token"] = "not-a-placeholder"
    unplaced_path = fixtures / "non-placeholder-token.json"
    unplaced_path.write_text(json.dumps(unplaced, indent=2), encoding="utf-8")

    evidence: dict[str, Any] = {
        "python": sys.version.split()[0],
        "repo_root": ".",
        "shipped_config": run_validator(repo_root, ["config/openclaw.json"]),
        "default_config": run_validator(repo_root, []),
        "widened_bind": run_validator(repo_root, [str(widened_path)]),
        "non_placeholder_token": run_validator(repo_root, [str(unplaced_path)]),
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return evidence


def check(evidence: dict[str, Any]) -> bool:
    shipped = evidence["shipped_config"]
    default = evidence["default_config"]
    widened = evidence["widened_bind"]
    unplaced = evidence["non_placeholder_token"]
    return (
        shipped["exit_code"] == 0
        and ": ok" in shipped["stdout"]
        and shipped["stderr"] == ""
        and default["exit_code"] == 0
        and ": ok" in default["stdout"]
        and widened["exit_code"] == 1
        and "gateway.bind" in widened["stderr"]
        and unplaced["exit_code"] == 1
        and "gateway.auth.token" in unplaced["stderr"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--out", default="artifacts/verify/validator", type=Path)
    args = parser.parse_args()

    evidence = drive(args.repo_root.resolve(), (args.repo_root / args.out).resolve())
    print(json.dumps(evidence, indent=2))

    ok = check(evidence)
    print("verify: pass" if ok else "verify: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
