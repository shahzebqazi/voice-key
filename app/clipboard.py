"""Clipboard output for transcribed text."""

import base64
import json
import os
import pwd
import shutil
import subprocess
import time
from pathlib import Path

import pyperclip

try:
    from pynput.keyboard import Controller, Key
except Exception:
    Controller = None
    Key = None

DEFAULT_REQUEST_TIMEOUT = 5.0


def _user_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and os.geteuid() == 0:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    return Path.home()


STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", _user_home() / ".local" / "state")) / "voice-key"
CLIPBOARD_REQUEST_PATH = STATE_DIR / "clipboard_request.json"
CLIPBOARD_RESULT_PATH = STATE_DIR / "clipboard_result.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _load_json(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def copy_via_osc52(
    text: str,
    tty_path: str = "/dev/tty",
) -> bool:
    """Send an OSC 52 clipboard sequence to the active terminal."""
    payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
    sequence = f"\033]52;c;{payload}\a"

    try:
        with open(tty_path, "w", encoding="utf-8") as tty:
            tty.write(sequence)
            tty.flush()
        return True
    except OSError:
        return False


def copy_via_gtk_bridge(
    text: str,
    popen=subprocess.Popen,
) -> bool:
    """Use a longer-lived system GTK clipboard bridge process."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and os.geteuid() == 0:
        try:
            helper_home = Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            helper_home = Path.home()
    else:
        helper_home = Path.home()

    helper_path = helper_home / ".local" / "bin" / "voice-key-clipboard-bridge"
    try:
        proc = popen(
            [str(helper_path)],
            stdin=subprocess.PIPE,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        if proc.stdin is None:
            return False
        proc.stdin.write(text)
        proc.stdin.close()
        try:
            proc.wait(timeout=0.15)
            return proc.returncode == 0
        except subprocess.TimeoutExpired:
            # Bridge holds clipboard ownership for a short window; still running is success.
            return True
    except (FileNotFoundError, PermissionError, OSError, subprocess.SubprocessError):
        return False


def copy_via_gtk_direct(text: str) -> bool:
    """Try copying through GTK directly in the current process."""
    try:
        import gi

        gi.require_version("Gdk", "3.0")
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gdk, Gtk

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()

        primary = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        primary.set_text(text, -1)
        primary.store()
        return True
    except Exception:
        return False


def paste_via_pynput(
    controller_factory=Controller,
    sleep=time.sleep,
) -> bool:
    """Best-effort paste into the currently focused app."""
    if controller_factory is None or Key is None:
        return False
    try:
        controller = controller_factory()
        sleep(0.05)
        with controller.pressed(Key.ctrl):
            controller.press("v")
            controller.release("v")
        return True
    except Exception:
        return False


def type_via_pynput(
    text: str,
    controller_factory=Controller,
    sleep=time.sleep,
) -> bool:
    """Fallback for compositors/apps that reject paste shortcuts."""
    if controller_factory is None:
        return False
    try:
        controller = controller_factory()
        sleep(0.05)
        controller.type(text)
        return True
    except Exception:
        return False


def request_session_output(
    text: str,
    paste: bool = False,
    timeout: float = DEFAULT_REQUEST_TIMEOUT,
    monotonic=time.monotonic,
    sleep=time.sleep,
) -> tuple[bool, bool]:
    """Ask the long-lived tray process to own clipboard and optional paste."""
    request_id = f"{time.time_ns()}"
    _write_json(
        CLIPBOARD_REQUEST_PATH,
        {
            "request_id": request_id,
            "text": text,
            "paste": paste,
            "requested_at": time.time(),
        },
    )

    deadline = monotonic() + timeout
    while monotonic() < deadline:
        payload = _load_json(CLIPBOARD_RESULT_PATH)
        if payload and payload.get("request_id") == request_id:
            copied = bool(payload.get("copied"))
            pasted = bool(payload.get("pasted"))
            return copied, pasted
        sleep(0.05)

    return False, False


def copy_to_clipboard(
    text: str,
    which=shutil.which,
    run=subprocess.run,
    pyperclip_copy=pyperclip.copy,
    gtk_direct_copy=copy_via_gtk_direct,
    gtk_copy=copy_via_gtk_bridge,
    osc52_copy=copy_via_osc52,
) -> bool:
    env = dict(os.environ)
    env.setdefault("COSMIC_DATA_CONTROL_ENABLED", "1")

    commands = [
        ("wl-copy", ["wl-copy"]),
        ("xclip", ["xclip", "-selection", "clipboard"]),
        ("xsel", ["xsel", "--clipboard", "--input"]),
    ]

    for command_name, command in commands:
        if not which(command_name):
            continue
        try:
            run(
                command,
                input=text,
                text=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            return True
        except (FileNotFoundError, PermissionError, subprocess.SubprocessError):
            continue

    if gtk_direct_copy(text):
        return True

    try:
        pyperclip_copy(text)
        return True
    except pyperclip.PyperclipException:
        pass

    if gtk_copy(text):
        return True

    return osc52_copy(text)


def paste_after_copy() -> bool:
    """Attempt to paste the freshly copied clipboard contents."""
    return paste_via_pynput()


def deliver_transcript(text: str, paste: bool = True) -> tuple[bool, bool]:
    """Copy the transcript and optionally paste it into the focused app."""
    session_copied, session_pasted = request_session_output(text, paste=paste)
    if session_copied and (session_pasted or not paste):
        return session_copied, session_pasted

    if session_copied and paste:
        # If session copy worked but paste failed, retry locally.
        pasted = paste_after_copy()
        if pasted:
            return True, True
        return True, type_via_pynput(text)

    copied = copy_to_clipboard(text)
    if not copied:
        return False, False

    if not paste:
        return True, False

    pasted = paste_after_copy()
    if pasted:
        return True, True
    return True, type_via_pynput(text)
