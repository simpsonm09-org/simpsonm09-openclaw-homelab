"""Validate the hardened OpenClaw configuration against the deployment posture.

Every check maps to a control named in ``docs/threat-model.md`` and required by
``docs/runbooks/exposure.md``. Two families of check run:

``check_controls``
    The hardening invariants. The template configuration holds all of them, and
    CI fails when a change weakens one.

``check_secret_placeholders``
    Guards against committing a live secret. This repository holds a template,
    never a real token.

The module has no third-party dependencies on purpose, so it runs the same way
on this Windows machine, inside WSL2, and in CI.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "openclaw.json"

#: The placeholder every token field must hold in this repository.
TOKEN_PLACEHOLDER = "REPLACE_ME_GATEWAY_TOKEN"

#: dmScope values that keep direct messages isolated between peers.
_DM_SCOPES = frozenset({"per-channel-peer", "per-account-channel-peer"})

#: Sandbox modes that actually move tool execution off the host.
_SANDBOX_MODES = frozenset({"non-main", "all"})


@dataclass(frozen=True)
class Violation:
    """A single failed check, named by the configuration key it concerns."""

    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Read a configuration file as JSON and return it as a mapping."""
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: configuration must be a JSON object")
    return data


def _get(config: dict[str, Any], dotted: str, default: Any = None) -> Any:
    """Return the value at a dotted path, or ``default`` when it is absent."""
    node: Any = config
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def check_controls(config: dict[str, Any]) -> list[Violation]:
    """Return the hardening invariants that ``config`` violates."""
    violations: list[Violation] = []

    def require(condition: bool, key: str, message: str) -> None:
        if not condition:
            violations.append(Violation(key, message))

    require(
        _get(config, "gateway.bind") == "loopback",
        "gateway.bind",
        "must be 'loopback'; a wildcard bind exposes the Gateway on the network",
    )
    require(
        _get(config, "gateway.auth.mode") == "token",
        "gateway.auth.mode",
        "must be 'token'",
    )
    require(
        _get(config, "session.dmScope") in _DM_SCOPES,
        "session.dmScope",
        f"must be one of {sorted(_DM_SCOPES)} so DM sessions do not share context",
    )
    require(
        _get(config, "agents.defaults.sandbox.mode") in _SANDBOX_MODES,
        "agents.defaults.sandbox.mode",
        f"must be one of {sorted(_SANDBOX_MODES)}; sandboxing is off by default",
    )
    require(
        _get(config, "agents.defaults.sandbox.workspaceAccess") == "none",
        "agents.defaults.sandbox.workspaceAccess",
        "must be 'none' so the sandbox cannot read the host workspace",
    )
    require(
        _get(config, "tools.profile") == "messaging",
        "tools.profile",
        "must start at the 'messaging' profile",
    )
    require(
        _get(config, "tools.exec.security") == "deny",
        "tools.exec.security",
        "must be 'deny' until exec is widened deliberately",
    )
    require(
        _get(config, "tools.exec.ask") == "always",
        "tools.exec.ask",
        "must be 'always' so no exec runs without approval",
    )
    require(
        _get(config, "tools.elevated.enabled") is False,
        "tools.elevated.enabled",
        "must be false; the sandbox escape hatch stays closed",
    )
    return violations


def check_secret_placeholders(config: dict[str, Any]) -> list[Violation]:
    """Return violations where a token field no longer holds the placeholder."""
    token = _get(config, "gateway.auth.token")
    if token != TOKEN_PLACEHOLDER:
        return [
            Violation(
                "gateway.auth.token",
                f"must stay {TOKEN_PLACEHOLDER!r} in the repository; "
                "inject the real token at deploy time (docs/secrets.md)",
            )
        ]
    return []


def validate_config(config: dict[str, Any]) -> list[Violation]:
    """Return every violation found in ``config``."""
    return [*check_controls(config), *check_secret_placeholders(config)]


def main(argv: list[str] | None = None) -> int:
    """Validate a config file. Return ``0`` when it passes, ``1`` otherwise."""
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(args[0]) if args else DEFAULT_CONFIG
    violations = validate_config(load_config(path))
    if violations:
        print(f"{path}: {len(violations)} violation(s)", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    print(f"{path}: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
