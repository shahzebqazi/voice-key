"""Global double-click hotkey listener."""

import time
import threading
from pynput import keyboard


class DoubleTapListener:
    """Detect double-tap of a configurable modifier key.

    Calls `on_activate()` each time a valid double-tap is detected.
    """

    def __init__(self, key_name: str, interval_ms: int, on_activate):
        self.target_key = self._resolve_key(key_name)
        self.interval = interval_ms / 1000.0
        self.on_activate = on_activate
        self._last_release: float = 0.0
        self._listener: keyboard.Listener | None = None
        self._lock = threading.Lock()

    @staticmethod
    def _resolve_key(name: str):
        if name.startswith("Key."):
            attr = name[4:]
            return getattr(keyboard.Key, attr)
        if len(name) == 1:
            return keyboard.KeyCode.from_char(name)
        return getattr(keyboard.Key, name)

    def _on_release(self, key):
        if key != self.target_key:
            return
        now = time.monotonic()
        with self._lock:
            elapsed = now - self._last_release
            self._last_release = now
        if elapsed <= self.interval:
            self.on_activate()

    def start(self):
        self._listener = keyboard.Listener(on_release=self._on_release)
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def join(self):
        if self._listener:
            self._listener.join()
