from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from openclaw_homelab import validate as v


@pytest.fixture()
def template() -> dict[str, Any]:
    return json.loads(Path(v.DEFAULT_CONFIG).read_text(encoding="utf-8"))


def test_shipped_template_passes(template: dict[str, Any]) -> None:
    assert v.validate_config(template) == []


@pytest.mark.parametrize(
    ("path", "weakened_value"),
    [
        ("gateway.bind", "0.0.0.0"),
        ("gateway.auth.mode", "none"),
        ("session.dmScope", "shared"),
        ("agents.defaults.sandbox.mode", "off"),
        ("agents.defaults.sandbox.workspaceAccess", "read"),
        ("tools.profile", "full"),
        ("tools.exec.security", "allow"),
        ("tools.exec.ask", "never"),
        ("tools.elevated.enabled", True),
    ],
)
def test_weakened_control_is_detected(
    template: dict[str, Any], path: str, weakened_value: object
) -> None:
    weakened = copy.deepcopy(template)
    _set(weakened, path, weakened_value)
    violations = v.check_controls(weakened)
    assert any(item.key == path for item in violations), violations


def test_removed_control_is_detected(template: dict[str, Any]) -> None:
    del template["gateway"]["bind"]
    assert any(item.key == "gateway.bind" for item in v.check_controls(template))


def test_committed_token_must_be_placeholder(template: dict[str, Any]) -> None:
    template["gateway"]["auth"]["token"] = "sk-live-not-a-placeholder"
    violations = v.check_secret_placeholders(template)
    assert [item.key for item in violations] == ["gateway.auth.token"]


def test_placeholder_token_passes(template: dict[str, Any]) -> None:
    assert v.check_secret_placeholders(template) == []


def test_main_returns_one_on_violation(tmp_path: Path, template: dict[str, Any]) -> None:
    template["gateway"]["bind"] = "0.0.0.0"
    broken = tmp_path / "openclaw.json"
    broken.write_text(json.dumps(template), encoding="utf-8")
    assert v.main([str(broken)]) == 1


def test_main_returns_zero_on_valid_config(tmp_path: Path, template: dict[str, Any]) -> None:
    good = tmp_path / "openclaw.json"
    good.write_text(json.dumps(template), encoding="utf-8")
    assert v.main([str(good)]) == 0


def _set(config: dict[str, Any], dotted: str, value: object) -> None:
    parts = dotted.split(".")
    node = config
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value
