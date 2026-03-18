"""Runtime state tracking for tray integrations."""

from __future__ import annotations

import json
import os
import pwd
from datetime import datetime, timezone
from pathlib import Path


def _user_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and os.geteuid() == 0:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    return Path.home()


STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", _user_home() / ".local" / "state")) / "voice-key"
STATE_PATH = STATE_DIR / "status.json"
RECENT_PROMPTS_PATH = STATE_DIR / "recent_prompts.json"
MAX_RECENT_PROMPTS = 10


def _coerce_duration_seconds(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if text.endswith("s"):
        text = text[:-1]

    try:
        return float(text)
    except ValueError:
        return 0.0


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


def load_recent_prompts(limit: int = MAX_RECENT_PROMPTS) -> list[dict]:
    """Load the recent prompt history for tray integrations."""
    try:
        payload = json.loads(RECENT_PROMPTS_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    prompts = payload.get("prompts", [])
    if not isinstance(prompts, list):
        return []

    cleaned: list[dict] = []
    for prompt in prompts:
        if not isinstance(prompt, dict):
            continue
        text = str(prompt.get("text", "")).strip()
        if not text:
            continue
        cleaned.append(
            {
                "text": text,
                "timestamp": str(prompt.get("timestamp", "")),
                "duration_seconds": _coerce_duration_seconds(prompt.get("duration_seconds", 0.0)),
            }
        )

    return cleaned[:limit]


def append_recent_prompt(text: str, duration_seconds: float) -> None:
    """Persist the newest transcript and retain only the last 10 entries."""
    prompt_text = text.strip()
    if not prompt_text:
        return

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    prompts = load_recent_prompts(limit=MAX_RECENT_PROMPTS)
    prompts.insert(
        0,
        {
            "text": prompt_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration_seconds, 1),
        },
    )
    payload = {"prompts": prompts[:MAX_RECENT_PROMPTS]}
    RECENT_PROMPTS_PATH.write_text(json.dumps(payload, indent=2) + "\n")


def clear_recent_prompts() -> None:
    """Remove saved prompt history."""
    try:
        RECENT_PROMPTS_PATH.unlink()
    except FileNotFoundError:
        pass


def clear_status() -> None:
    """Remove the runtime status file when the app is no longer active."""
    try:
        STATE_PATH.unlink()
    except FileNotFoundError:
        pass
