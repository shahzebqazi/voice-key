import base64
from unittest.mock import MagicMock

import pyperclip

from app.clipboard import copy_to_clipboard, copy_via_osc52, deliver_transcript


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
        gtk_direct_copy=lambda text: False,
        gtk_copy=lambda text: False,
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
        gtk_direct_copy=lambda text: False,
        gtk_copy=lambda text: False,
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


def test_deliver_transcript_retries_local_paste_when_session_paste_fails(monkeypatch):
    monkeypatch.setattr("app.clipboard.request_session_output", lambda text, paste: (True, False))
    local_paste = MagicMock(return_value=True)
    monkeypatch.setattr("app.clipboard.paste_after_copy", local_paste)
    monkeypatch.setattr("app.clipboard.copy_to_clipboard", lambda text: False)

    copied, pasted = deliver_transcript("hello", paste=True)

    assert copied is True
    assert pasted is True
    local_paste.assert_called_once_with()


def test_deliver_transcript_falls_back_to_local_copy_when_session_copy_fails(monkeypatch):
    monkeypatch.setattr("app.clipboard.request_session_output", lambda text, paste: (False, False))
    monkeypatch.setattr("app.clipboard.copy_to_clipboard", lambda text: True)
    monkeypatch.setattr("app.clipboard.paste_after_copy", lambda: True)

    copied, pasted = deliver_transcript("hello", paste=True)

    assert copied is True
    assert pasted is True


def test_deliver_transcript_types_text_when_paste_shortcut_fails(monkeypatch):
    monkeypatch.setattr("app.clipboard.request_session_output", lambda text, paste: (True, False))
    monkeypatch.setattr("app.clipboard.paste_after_copy", lambda: False)
    typer = MagicMock(return_value=True)
    monkeypatch.setattr("app.clipboard.type_via_pynput", typer)

    copied, pasted = deliver_transcript("hello cosmic", paste=True)

    assert copied is True
    assert pasted is True
    typer.assert_called_once_with("hello cosmic")
