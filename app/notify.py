"""Notification sound playback for successful hotkey activation."""

from __future__ import annotations

import shutil
import subprocess
import threading
from pathlib import Path

FREEDESKTOP_MESSAGE_SOUND = Path("/usr/share/sounds/freedesktop/stereo/message.oga")


class NotificationSound:
    """Play a short confirmation sound with a system-first fallback chain."""

    def __init__(self, which=shutil.which, run=subprocess.run, sound_exists=None):
        self._which = which
        self._run = run
        self._sound_exists = sound_exists or FREEDESKTOP_MESSAGE_SOUND.exists
        self.backend, self.command = self._detect_backend()

    def _detect_backend(self) -> tuple[str, list[str] | None]:
        if self._which("canberra-gtk-play"):
            return "canberra", ["canberra-gtk-play", "-i", "message"]
        if self._which("paplay") and self._sound_exists():
            return "paplay", ["paplay", str(FREEDESKTOP_MESSAGE_SOUND)]
        return "generated", None

    def play_async(self):
        threading.Thread(target=self.play, daemon=True).start()

    def play(self):
        if self.command is not None:
            try:
                self._run(
                    self.command,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except (FileNotFoundError, PermissionError, subprocess.SubprocessError):
                pass

        self._play_generated_chime()

    @staticmethod
    def _play_generated_chime():
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError:
            return

        sample_rate = 44100
        duration = 0.16
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        attack = np.linspace(0.0, 1.0, max(1, int(sample_rate * 0.01)), endpoint=True)
        sustain = np.ones(max(1, len(t) - len(attack)))
        envelope = np.concatenate((attack, sustain))[: len(t)]
        fade = np.linspace(1.0, 0.0, len(t), endpoint=True)

        tone_a = np.sin(2 * np.pi * 880 * t)
        tone_b = 0.6 * np.sin(2 * np.pi * 1320 * t)
        chime = 0.18 * (tone_a + tone_b) * envelope * fade

        try:
            sd.play(chime.astype(np.float32), sample_rate, blocking=False)
        except Exception:
            pass


def send_desktop_notification(
    title: str,
    message: str,
    urgency: str = "normal",
    which=shutil.which,
    run=subprocess.run,
) -> bool:
    """Send a desktop notification when a notification daemon is available."""
    command = which("notify-send")
    if not command:
        return False

    try:
        run(
            [command, "--urgency", urgency, title, message],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (FileNotFoundError, PermissionError, subprocess.SubprocessError):
        return False


def send_desktop_notification_async(title: str, message: str, urgency: str = "normal") -> None:
    """Dispatch a desktop notification in the background."""
    threading.Thread(
        target=send_desktop_notification,
        args=(title, message, urgency),
        daemon=True,
    ).start()
