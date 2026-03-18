#!/usr/bin/env python3
"""Keyboard Tester — print every key press/release in real time using evdev.

Works on both X11 and Wayland. Requires read access to /dev/input/*
(run with sudo if not in the 'input' group).

Usage:
    sudo python -u tools/keyboard_tester.py             # stdout only
    sudo python -u tools/keyboard_tester.py --log       # also write to timestamped file
    sudo python -u tools/keyboard_tester.py --log out.log  # write to specific file

Press Escape or Ctrl+C to quit.
"""

import sys
import os
import argparse
import signal
import selectors
import time
from datetime import datetime, timezone
import evdev
from evdev import ecodes

KEY_STATE = {0: "RELEASE", 1: "PRESS  ", 2: "HOLD   "}

FRIENDLY_NAMES = {
    "KEY_LEFTCTRL": "Ctrl (Left)",
    "KEY_RIGHTCTRL": "Ctrl (Right)",
    "KEY_LEFTSHIFT": "Shift (Left)",
    "KEY_RIGHTSHIFT": "Shift (Right)",
    "KEY_LEFTALT": "Alt (Left)",
    "KEY_RIGHTALT": "Alt (Right)",
    "KEY_LEFTMETA": "Super / Windows (Left)",
    "KEY_RIGHTMETA": "Super / Windows (Right)",
    "KEY_CAPSLOCK": "Caps Lock",
    "KEY_NUMLOCK": "Num Lock",
    "KEY_SCROLLLOCK": "Scroll Lock",
    "KEY_TAB": "Tab",
    "KEY_ENTER": "Enter",
    "KEY_BACKSPACE": "Backspace",
    "KEY_SPACE": "Space",
    "KEY_ESC": "Escape",
    "KEY_DELETE": "Delete",
    "KEY_INSERT": "Insert",
    "KEY_HOME": "Home",
    "KEY_END": "End",
    "KEY_PAGEUP": "Page Up",
    "KEY_PAGEDOWN": "Page Down",
    "KEY_UP": "Up Arrow",
    "KEY_DOWN": "Down Arrow",
    "KEY_LEFT": "Left Arrow",
    "KEY_RIGHT": "Right Arrow",
    "KEY_FN": "Fn",
}

PYNPUT_MAP = {
    "KEY_LEFTCTRL": "Key.ctrl_l",
    "KEY_RIGHTCTRL": "Key.ctrl_r",
    "KEY_LEFTSHIFT": "Key.shift_l",
    "KEY_RIGHTSHIFT": "Key.shift_r",
    "KEY_LEFTALT": "Key.alt_l",
    "KEY_RIGHTALT": "Key.alt_r",
    "KEY_LEFTMETA": "Key.cmd_l",
    "KEY_RIGHTMETA": "Key.cmd_r",
    "KEY_CAPSLOCK": "Key.caps_lock",
    "KEY_NUMLOCK": "Key.num_lock",
    "KEY_SCROLLLOCK": "Key.scroll_lock",
    "KEY_TAB": "Key.tab",
    "KEY_ENTER": "Key.enter",
    "KEY_BACKSPACE": "Key.backspace",
    "KEY_SPACE": "Key.space",
    "KEY_ESC": "Key.esc",
    "KEY_DELETE": "Key.delete",
    "KEY_INSERT": "Key.insert",
    "KEY_HOME": "Key.home",
    "KEY_END": "Key.end",
    "KEY_PAGEUP": "Key.page_up",
    "KEY_PAGEDOWN": "Key.page_down",
    "KEY_UP": "Key.up",
    "KEY_DOWN": "Key.down",
    "KEY_LEFT": "Key.left",
    "KEY_RIGHT": "Key.right",
    "KEY_FN": "Key.fn",
}

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")


def friendly(code_name: str) -> str:
    if code_name in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[code_name]
    if code_name.startswith("KEY_F") and code_name[5:].isdigit():
        return code_name[4:]
    if code_name.startswith("KEY_"):
        raw = code_name[4:]
        return raw if len(raw) == 1 else raw.replace("_", " ").title()
    return code_name


def code_name(code: int) -> str:
    name = ecodes.KEY.get(code, None)
    if isinstance(name, list):
        return name[0]
    return name or f"KEY_{code}"


def find_keyboards() -> list[evdev.InputDevice]:
    keyboards = []
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        caps = dev.capabilities()
        if ecodes.EV_KEY not in caps:
            continue
        key_codes = set(caps[ecodes.EV_KEY])
        modifiers = {
            ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
            ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT,
            ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
            ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA,
        }
        alpha = (
            set(range(ecodes.KEY_Q, ecodes.KEY_P + 1))
            | set(range(ecodes.KEY_A, ecodes.KEY_L + 1))
            | set(range(ecodes.KEY_Z, ecodes.KEY_M + 1))
        )
        if (key_codes & modifiers and key_codes & alpha) or len(key_codes) > 60:
            keyboards.append(dev)
    return keyboards


def tw() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def center(text: str, width: int) -> str:
    pad = max((width - len(text)) // 2, 0)
    return " " * pad + text


def default_log_path() -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(LOG_DIR, f"keyboard-{ts}.log")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Keyboard Tester — print every key event in real time.",
    )
    p.add_argument(
        "--log", nargs="?", const="auto", default=None, metavar="FILE",
        help="Log output to a file. Omit FILE for auto-timestamped log in logs/.",
    )
    return p.parse_args()


class Output:
    """Write to stdout and optionally to a log file."""

    def __init__(self, log_path: str | None = None):
        self._log = None
        self.log_path = None
        if log_path:
            self.log_path = log_path
            os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
            self._log = open(log_path, "w")

    def write(self, text: str):
        print(text, flush=True)
        if self._log:
            self._log.write(text + "\n")
            self._log.flush()

    def write_log_only(self, text: str):
        if self._log:
            self._log.write(text + "\n")
            self._log.flush()

    def close(self):
        if self._log:
            self._log.close()
            self._log = None


def banner(keyboards: list[evdev.InputDevice], out: Output):
    w = tw()
    box_w = 52
    sp = " " * max((w - box_w) // 2, 0)

    out.write("")
    out.write(f"{sp}┌{'─' * (box_w - 2)}┐")
    out.write(f"{sp}│{'Keyboard Tester':^{box_w - 2}}│")
    out.write(f"{sp}│{'':^{box_w - 2}}│")
    out.write(f"{sp}│{'Press any key to see its name.':^{box_w - 2}}│")
    out.write(f"{sp}│{'Escape or Ctrl+C to quit.':^{box_w - 2}}│")
    out.write(f"{sp}└{'─' * (box_w - 2)}┘")
    out.write("")
    for kb in keyboards:
        out.write(center(f"↠ {kb.name} ({kb.path})", w))
    out.write("")
    if out.log_path:
        out.write(center(f"Logging to: {out.log_path}", w))
        out.write("")
        out.write_log_only(f"# Session started: {datetime.now(timezone.utc).isoformat()}")
        for kb in keyboards:
            out.write_log_only(f"# Device: {kb.name} ({kb.path})")
        out.write_log_only("")


def main():
    args = parse_args()
    keyboards = find_keyboards()
    if not keyboards:
        print("No keyboard devices found.", file=sys.stderr)
        print(file=sys.stderr)
        print("  evdev needs read access to /dev/input/event*.", file=sys.stderr)
        print("  Run with sudo:", file=sys.stderr)
        print(file=sys.stderr)
        print("    sudo python -u tools/keyboard_tester.py", file=sys.stderr)
        print(file=sys.stderr)
        print("  Or add yourself to the input group (permanent):", file=sys.stderr)
        print("    sudo usermod -aG input $USER", file=sys.stderr)
        print("    # then log out and back in", file=sys.stderr)
        sys.exit(1)

    log_path = None
    if args.log == "auto":
        log_path = default_log_path()
    elif args.log:
        log_path = args.log

    out = Output(log_path)

    def _sigint_handler(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint_handler)

    banner(keyboards, out)

    width = tw()
    ctrl_held = False
    t0 = time.monotonic()
    sel = selectors.DefaultSelector()
    for kb in keyboards:
        sel.register(kb, selectors.EVENT_READ)

    try:
        while True:
            for key, _ in sel.select():
                dev = key.fileobj
                for event in dev.read():
                    if event.type != ecodes.EV_KEY:
                        continue

                    ke = evdev.categorize(event)
                    cn = code_name(ke.scancode)
                    label = friendly(cn)
                    state = KEY_STATE.get(ke.keystate, "?")
                    arrow = "↑" if ke.keystate == 0 else ("↓" if ke.keystate == 1 else "⟳")
                    hint = PYNPUT_MAP.get(cn, "")
                    extra = f"  (config: {hint})" if hint else ""
                    elapsed = time.monotonic() - t0
                    ts = f"{elapsed:8.3f}s"

                    display_line = f"  {arrow} {state}  {label:<30}  [{cn}]{extra}"
                    out.write(center(display_line, width))
                    out.write_log_only(f"  {ts}  {arrow} {state}  {label:<30}  [{cn}]{extra}  device={dev.name}")

                    if cn in ("KEY_LEFTCTRL", "KEY_RIGHTCTRL"):
                        ctrl_held = ke.keystate != 0

                    if ke.keystate == 1 and cn == "KEY_ESC":
                        raise KeyboardInterrupt

                    if ke.keystate == 1 and cn == "KEY_C" and ctrl_held:
                        raise KeyboardInterrupt

    except KeyboardInterrupt:
        out.write("")
        out.write(center("Done.", width))
        duration = time.monotonic() - t0
        out.write_log_only(f"\n# Session ended: {datetime.now(timezone.utc).isoformat()}")
        out.write_log_only(f"# Duration: {duration:.1f}s")
    finally:
        sel.close()
        out.close()
        for kb in keyboards:
            try:
                kb.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
