import base64
from unittest.mock import MagicMock

import pyperclip

from app.clipboard import copy_to_clipboard, copy_via_osc52


def test_prefers_wl_copy_when_available():
    run = MagicMock()

    copied = copy_to_clipboard(
        "hello",
        which=lambda name: "/usr/bin/wl-copy" if name == "wl-copy" else None,
        run=run,
    )

    assert copied is True
    run.assert_called_once()


def test_returns_false_when_all_clipboard_backends_fail():
    def raise_clipboard_error(text):
        raise pyperclip.PyperclipException("no clipboard")

    copied = copy_to_clipboard(
        "hello",
        which=lambda name: None,
        pyperclip_copy=raise_clipboard_error,
        osc52_copy=lambda text: False,
    )

    assert copied is False


def test_falls_back_to_osc52_when_clipboard_backends_fail():
    def raise_clipboard_error(text):
        raise pyperclip.PyperclipException("no clipboard")

    osc52_copy = MagicMock(return_value=True)

    copied = copy_to_clipboard(
        "hello",
        which=lambda name: None,
        pyperclip_copy=raise_clipboard_error,
        osc52_copy=osc52_copy,
    )

    assert copied is True
    osc52_copy.assert_called_once_with("hello")


def test_copy_via_osc52_writes_terminal_sequence(tmp_path):
    tty_path = tmp_path / "tty"
    tty_path.write_text("", encoding="utf-8")

    copied = copy_via_osc52("hello", tty_path=str(tty_path))

    assert copied is True
    payload = base64.b64encode(b"hello").decode("ascii")
    assert tty_path.read_text(encoding="utf-8") == f"\033]52;c;{payload}\a"
