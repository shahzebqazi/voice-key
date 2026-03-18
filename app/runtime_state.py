"""Runtime state tracking for tray integrations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "voice-key"
STATE_PATH = STATE_DIR / "status.json"


def write_status(state: str, **extra) -> None:
    """Persist the current voice-key runtime state for external integrations."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": state,
        "pid": os.getpid(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    payload.update(extra)
    STATE_PATH.write_text(json.dumps(payload, indent=2) + "\n")


def clear_status() -> None:
    """Remove the runtime status file when the app is no longer active."""
    try:
        STATE_PATH.unlink()
    except FileNotFoundError:
        pass
