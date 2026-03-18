"""Persistent transcript logging."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
TRANSCRIPT_LOG_PATH = LOG_DIR / "transcriptions.log"


def append_transcript(text: str, duration_seconds: float, path: Path = TRANSCRIPT_LOG_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] ({duration_seconds:.1f}s)\n")
        handle.write(text.strip())
        handle.write("\n\n")
    return path
