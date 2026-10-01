"""Configuration validation for a self-hosted OpenClaw gateway.

The package is intentionally dependency-free: the checks run on the standard
library alone, so they behave the same on a workstation, inside WSL2, and in CI.
"""

from __future__ import annotations

from .validate import (
    Violation,
    check_controls,
    check_secret_placeholders,
    load_config,
    main,
    validate_config,
)

__all__ = [
    "Violation",
    "check_controls",
    "check_secret_placeholders",
    "load_config",
    "main",
    "validate_config",
]
