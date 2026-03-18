import pytest
from evdev import ecodes

from app.config import DEFAULTS, HotkeyConfig, load_config
from app.hotkey import DoubleTapListener


def test_hotkey_default_is_right_alt(tmp_path):
    assert HotkeyConfig().key == "KEY_RIGHTALT"
    assert DEFAULTS["hotkey"]["key"] == "KEY_RIGHTALT"
    assert load_config(tmp_path / "missing-config.toml").hotkey.key == "KEY_RIGHTALT"


def test_double_tap_within_interval_triggers_callback():
    activations = []
    listener = DoubleTapListener("KEY_RIGHTALT", 400, lambda: activations.append("hit"))

    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.0) is False
    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.3) is True
    assert activations == ["hit"]


def test_double_tap_outside_interval_does_not_trigger():
    activations = []
    listener = DoubleTapListener("KEY_RIGHTALT", 400, lambda: activations.append("hit"))

    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.0) is False
    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.5) is False
    assert activations == []


def test_press_events_do_not_count_toward_double_tap():
    activations = []
    listener = DoubleTapListener("KEY_RIGHTALT", 400, lambda: activations.append("hit"))

    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 1, now=1.0) is False
    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.1) is False
    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 1, now=1.2) is False
    assert listener.process_key_event(ecodes.KEY_RIGHTALT, 0, now=1.3) is True
    assert activations == ["hit"]


def test_listener_start_reports_input_access_error():
    listener = DoubleTapListener("KEY_RIGHTALT", 400, lambda: None, keyboard_finder=lambda: [])

    with pytest.raises(RuntimeError, match=r"read access to /dev/input/event\*"):
        listener.start()
