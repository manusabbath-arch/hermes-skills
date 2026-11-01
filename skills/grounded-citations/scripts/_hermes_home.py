"""Resolve HERMES_HOME for standalone skill scripts (stdlib only).

When HERMES_HOME is set, use it. Otherwise default to ~/.hermes.
"""
from __future__ import annotations

import os
from pathlib import Path


def get_hermes_home() -> Path:
    val = os.environ.get("HERMES_HOME", "").strip()
    return Path(val) if val else Path.home() / ".hermes"
