"""Global double-tap hotkey listener using evdev."""

import os
import selectors
import threading
import time

import evdev
from evdev import ecodes

INPUT_ACCESS_ERROR = """[voice-hotkey] No keyboard devices found.
[voice-hotkey] evdev needs read access to /dev/input/event*.
[voice-hotkey] Run with sudo, for example:
[voice-hotkey]   sudo python -u -m app.main
[voice-hotkey] Or add yourself to the input group and log back in."""


def code_name(code: int) -> str:
    name = ecodes.KEY.get(code, None)
    if isinstance(name, list):
        return name[0]
    return name or f"KEY_{code}"


def find_keyboards() -> list[evdev.InputDevice]:
    keyboards = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()
        except OSError:
            continue

        if ecodes.EV_KEY not in caps:
            dev.close()
            continue

        key_codes = set(caps[ecodes.EV_KEY])
        modifiers = {
            ecodes.KEY_LEFTCTRL,
            ecodes.KEY_RIGHTCTRL,
            ecodes.KEY_LEFTSHIFT,
            ecodes.KEY_RIGHTSHIFT,
            ecodes.KEY_LEFTALT,
            ecodes.KEY_RIGHTALT,
            ecodes.KEY_LEFTMETA,
            ecodes.KEY_RIGHTMETA,
        }
        alpha = (
            set(range(ecodes.KEY_Q, ecodes.KEY_P + 1))
            | set(range(ecodes.KEY_A, ecodes.KEY_L + 1))
            | set(range(ecodes.KEY_Z, ecodes.KEY_M + 1))
        )
        if (key_codes & modifiers and key_codes & alpha) or len(key_codes) > 60:
            keyboards.append(dev)
        else:
            dev.close()
    return keyboards


class DoubleTapListener:
    """Detect double-tap of a configurable key from evdev events."""

    def __init__(
        self,
        key_name: str,
        interval_ms: int,
        on_activate,
        keyboard_finder=find_keyboards,
        selector_factory=selectors.DefaultSelector,
        time_source=time.monotonic,
    ):
        self.key_name = key_name
        self.target_code = self._resolve_key_code(key_name)
        self.interval = interval_ms / 1000.0
        self.on_activate = on_activate
        self._keyboard_finder = keyboard_finder
        self._selector_factory = selector_factory
        self._time_source = time_source
        self._last_release: float = 0.0
        self._keyboards: list[evdev.InputDevice] = []
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._wakeup_r: int | None = None
        self._wakeup_w: int | None = None

    @staticmethod
    def _resolve_key_code(name: str) -> int:
        try:
            return ecodes.ecodes[name]
        except KeyError as exc:
            raise ValueError(f"Unsupported evdev key name: {name}") from exc

    def process_key_event(self, key_code: int | str, keystate: int, now: float | None = None) -> bool:
        if keystate != 0:
            return False

        if isinstance(key_code, int):
            if key_code != self.target_code:
                return False
        elif key_code != self.key_name:
            return False

        timestamp = self._time_source() if now is None else now
        with self._lock:
            elapsed = timestamp - self._last_release if self._last_release else None
            self._last_release = timestamp

        if elapsed is not None and elapsed <= self.interval:
            self.on_activate()
            return True
        return False

    def _run(self):
        selector = self._selector_factory()
        try:
            if self._wakeup_r is None:
                return

            selector.register(self._wakeup_r, selectors.EVENT_READ)
            for kb in self._keyboards:
                selector.register(kb, selectors.EVENT_READ)

            while not self._stop_event.is_set():
                for key, _ in selector.select():
                    if key.fileobj == self._wakeup_r:
                        try:
                            os.read(self._wakeup_r, 4096)
                        except OSError:
                            pass
                        continue

                    dev = key.fileobj
                    try:
                        events = dev.read()
                    except OSError:
                        continue

                    for event in events:
                        if event.type != ecodes.EV_KEY:
                            continue
                        ke = evdev.categorize(event)
                        self.process_key_event(ke.scancode, ke.keystate)
        finally:
            selector.close()
            for kb in self._keyboards:
                try:
                    kb.close()
                except OSError:
                    pass
            self._keyboards = []
            self._close_wakeup_pipe()

    def _close_wakeup_pipe(self):
        for fd_name in ("_wakeup_r", "_wakeup_w"):
            fd = getattr(self, fd_name)
            if fd is None:
                continue
            try:
                os.close(fd)
            except OSError:
                pass
            setattr(self, fd_name, None)

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._keyboards = self._keyboard_finder()
        if not self._keyboards:
            raise RuntimeError(INPUT_ACCESS_ERROR)

        self._stop_event.clear()
        self._last_release = 0.0
        self._wakeup_r, self._wakeup_w = os.pipe()
        os.set_blocking(self._wakeup_r, False)
        os.set_blocking(self._wakeup_w, False)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._wakeup_w is not None:
            try:
                os.write(self._wakeup_w, b"\0")
            except OSError:
                pass

    def join(self, timeout: float | None = None):
        if self._thread:
            self._thread.join(timeout=timeout)
