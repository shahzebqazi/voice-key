"""Persistent transcript logging."""

from __future__ import annotations

import hashlib
import json
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

from .runtime_state import STATE_DIR, append_recent_prompt

LOG_DIR = STATE_DIR
TRANSCRIPT_LOG_PATH = LOG_DIR / "transcriptions.log"
TRANSCRIPT_QUEUE_PATH = LOG_DIR / "transcript_queue.json"
RECORDINGS_DIR = LOG_DIR / "recordings"
MAX_LOG_ENTRIES = 10


def compute_audio_hash(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Build a stable hash for a recording so repeated clips can be memoized."""
    payload = np.asarray(audio, dtype=np.float32)
    digest = hashlib.sha256()
    digest.update(str(sample_rate).encode("utf-8"))
    digest.update(payload.tobytes())
    return digest.hexdigest()


def load_transcript_queue(path: Path | None = None) -> list[dict]:
    """Load the bounded transcript queue."""
    path = path or TRANSCRIPT_QUEUE_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def find_cached_transcript(audio_hash: str, path: Path | None = None) -> dict | None:
    """Return a cached transcript entry for a previously seen recording."""
    path = path or TRANSCRIPT_QUEUE_PATH
    for entry in reversed(load_transcript_queue(path)):
        if entry.get("audio_hash") == audio_hash:
            return entry
    return None


def load_latest_transcript_text(path: Path | None = None) -> str:
    """Return the most recently persisted transcript text."""
    entries = load_transcript_queue(path)
    if not entries:
        return ""

    return str(entries[-1].get("text", "")).strip()


def _write_recording(audio: np.ndarray, sample_rate: int, audio_hash: str) -> Path:
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    recording_path = RECORDINGS_DIR / f"{timestamp}-{audio_hash[:12]}.wav"
    pcm = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(str(recording_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm16.tobytes())
    return recording_path


def _persist_queue(entries: list[dict], path: Path | None = None) -> None:
    path = path or TRANSCRIPT_QUEUE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"entries": entries[-MAX_LOG_ENTRIES:]}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _rewrite_text_log(entries: list[dict], path: Path = TRANSCRIPT_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries[-MAX_LOG_ENTRIES:]:
            timestamp = entry.get("timestamp", "")
            duration_seconds = float(entry.get("duration_seconds", 0.0))
            text = str(entry.get("text", "")).strip()
            handle.write(f"[{timestamp}] ({duration_seconds:.1f}s)\n")
            handle.write(text)
            handle.write("\n\n")


def append_transcript(
    text: str,
    duration_seconds: float,
    path: Path = TRANSCRIPT_LOG_PATH,
    audio: np.ndarray | None = None,
    sample_rate: int = 16000,
    audio_hash: str | None = None,
    raw_text: str | None = None,
) -> Path:
    prompt_text = text.strip()
    raw_prompt_text = (raw_text if raw_text is not None else text).strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    queue = load_transcript_queue()
    recording_path = None

    if audio is not None:
        audio_hash = audio_hash or compute_audio_hash(audio, sample_rate)
        recording_path = _write_recording(audio, sample_rate, audio_hash)

    queue.append(
        {
            "timestamp": timestamp,
            "duration_seconds": round(duration_seconds, 1),
            "text": prompt_text,
            "raw_text": raw_prompt_text,
            "audio_hash": audio_hash or "",
            "recording_path": str(recording_path) if recording_path else "",
        }
    )

    while len(queue) > MAX_LOG_ENTRIES:
        stale = queue.pop(0)
        stale_path = str(stale.get("recording_path", "")).strip()
        if stale_path:
            try:
                Path(stale_path).unlink()
            except FileNotFoundError:
                pass

    _persist_queue(queue)
    _rewrite_text_log(queue, path)
    append_recent_prompt(prompt_text, duration_seconds)
    return path


def clear_transcript_log(path: Path = TRANSCRIPT_LOG_PATH) -> None:
    """Remove the transcript log, queue metadata, and retained recordings."""
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    try:
        TRANSCRIPT_QUEUE_PATH.unlink()
    except FileNotFoundError:
        pass
    if RECORDINGS_DIR.exists():
        for recording in RECORDINGS_DIR.glob("*.wav"):
            try:
                recording.unlink()
            except FileNotFoundError:
                pass
