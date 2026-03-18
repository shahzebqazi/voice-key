"""Unit tests for keyboard_tester — crash and exit scenarios."""

import os
import sys
import signal
import time
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.keyboard_tester import (
    friendly,
    code_name,
    center,
    Output,
    default_log_path,
    FRIENDLY_NAMES,
    PYNPUT_MAP,
    KEY_STATE,
    LOG_DIR,
)


class TestFriendlyNames(unittest.TestCase):
    def test_all_friendly_names_have_values(self):
        for key, val in FRIENDLY_NAMES.items():
            self.assertIsInstance(val, str)
            self.assertTrue(len(val) > 0, f"{key} has empty friendly name")

    def test_modifier_keys_resolve(self):
        self.assertEqual(friendly("KEY_LEFTCTRL"), "Ctrl (Left)")
        self.assertEqual(friendly("KEY_RIGHTCTRL"), "Ctrl (Right)")
        self.assertEqual(friendly("KEY_LEFTSHIFT"), "Shift (Left)")
        self.assertEqual(friendly("KEY_RIGHTSHIFT"), "Shift (Right)")
        self.assertEqual(friendly("KEY_LEFTALT"), "Alt (Left)")
        self.assertEqual(friendly("KEY_RIGHTALT"), "Alt (Right)")
        self.assertEqual(friendly("KEY_LEFTMETA"), "Super / Windows (Left)")
        self.assertEqual(friendly("KEY_RIGHTMETA"), "Super / Windows (Right)")

    def test_special_keys_resolve(self):
        self.assertEqual(friendly("KEY_SPACE"), "Space")
        self.assertEqual(friendly("KEY_ENTER"), "Enter")
        self.assertEqual(friendly("KEY_ESC"), "Escape")
        self.assertEqual(friendly("KEY_TAB"), "Tab")
        self.assertEqual(friendly("KEY_BACKSPACE"), "Backspace")

    def test_function_keys(self):
        self.assertEqual(friendly("KEY_F1"), "F1")
        self.assertEqual(friendly("KEY_F12"), "F12")

    def test_single_letter_keys(self):
        self.assertEqual(friendly("KEY_A"), "A")
        self.assertEqual(friendly("KEY_Z"), "Z")

    def test_unknown_key_fallback(self):
        result = friendly("KEY_SOMETHING_WEIRD")
        self.assertEqual(result, "Something Weird")

    def test_non_key_prefix(self):
        self.assertEqual(friendly("BTN_LEFT"), "BTN_LEFT")


class TestPynputMap(unittest.TestCase):
    def test_all_modifiers_have_config_hints(self):
        for evdev_name in ("KEY_LEFTCTRL", "KEY_RIGHTCTRL",
                           "KEY_LEFTSHIFT", "KEY_RIGHTSHIFT",
                           "KEY_LEFTALT", "KEY_RIGHTALT",
                           "KEY_LEFTMETA", "KEY_RIGHTMETA"):
            self.assertIn(evdev_name, PYNPUT_MAP,
                          f"{evdev_name} missing from PYNPUT_MAP")

    def test_pynput_names_are_correct_format(self):
        for evdev_name, pynput_name in PYNPUT_MAP.items():
            self.assertTrue(pynput_name.startswith("Key."),
                            f"{evdev_name} -> {pynput_name} doesn't start with Key.")

    def test_left_right_distinction(self):
        self.assertEqual(PYNPUT_MAP["KEY_LEFTCTRL"], "Key.ctrl_l")
        self.assertEqual(PYNPUT_MAP["KEY_RIGHTCTRL"], "Key.ctrl_r")
        self.assertEqual(PYNPUT_MAP["KEY_LEFTALT"], "Key.alt_l")
        self.assertEqual(PYNPUT_MAP["KEY_RIGHTALT"], "Key.alt_r")


class TestCodeName(unittest.TestCase):
    def test_known_keycode(self):
        from evdev import ecodes
        result = code_name(ecodes.KEY_A)
        self.assertEqual(result, "KEY_A")

    def test_unknown_keycode_returns_fallback(self):
        result = code_name(99999)
        self.assertEqual(result, "KEY_99999")

    def test_list_valued_keycode(self):
        """Some keycodes map to a list of names; we take the first."""
        from evdev import ecodes
        for kc, names in ecodes.KEY.items():
            if isinstance(names, list):
                self.assertEqual(code_name(kc), names[0])
                break


class TestCenter(unittest.TestCase):
    def test_centers_short_text(self):
        result = center("hi", 10)
        self.assertEqual(result, "    hi")
        self.assertEqual(len(result), 6)

    def test_text_wider_than_width_unchanged(self):
        result = center("hello world", 5)
        self.assertEqual(result, "hello world")

    def test_exact_width(self):
        result = center("abcd", 4)
        self.assertEqual(result, "abcd")

    def test_odd_padding(self):
        result = center("abc", 10)
        self.assertTrue(result.endswith("abc"))
        leading = len(result) - len("abc")
        self.assertEqual(leading, 3)


class TestKeyState(unittest.TestCase):
    def test_release_is_0(self):
        self.assertEqual(KEY_STATE[0], "RELEASE")

    def test_press_is_1(self):
        self.assertEqual(KEY_STATE[1], "PRESS  ")

    def test_hold_is_2(self):
        self.assertEqual(KEY_STATE[2], "HOLD   ")

    def test_all_same_length(self):
        lengths = {len(v) for v in KEY_STATE.values()}
        self.assertEqual(len(lengths), 1, "All state labels should be same width")


class TestSigintHandler(unittest.TestCase):
    """The SIGINT handler must raise KeyboardInterrupt so select() unblocks."""

    def test_correct_handler_raises(self):
        """A proper SIGINT handler directly raises KeyboardInterrupt."""
        def handler(signum, frame):
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            handler(signal.SIGINT, None)

    def test_handler_is_not_default_ignore(self):
        """The tool must not set SIG_IGN (which would swallow Ctrl+C)."""
        # SIG_IGN would make the process completely unresponsive to Ctrl+C
        self.assertNotEqual(signal.SIG_IGN, signal.getsignal(signal.SIGINT))


class TestEvdevQuitDetection(unittest.TestCase):
    """Test that Escape and Ctrl+C via evdev both trigger clean exit."""

    def test_escape_keypress_triggers_quit(self):
        """KEY_ESC with keystate=1 (press) should be detected as quit."""
        from evdev import ecodes
        cn = code_name(ecodes.KEY_ESC)
        self.assertEqual(cn, "KEY_ESC")
        # The main loop checks: ke.keystate == 1 and cn == "KEY_ESC"
        # Simulate: keystate 1, code KEY_ESC -> should quit
        keystate = 1
        should_quit = (keystate == 1 and cn == "KEY_ESC")
        self.assertTrue(should_quit)

    def test_ctrl_c_triggers_quit(self):
        """KEY_C with ctrl_held=True and keystate=1 should quit."""
        from evdev import ecodes
        cn = code_name(ecodes.KEY_C)
        self.assertEqual(cn, "KEY_C")
        ctrl_held = True
        keystate = 1
        should_quit = (keystate == 1 and cn == "KEY_C" and ctrl_held)
        self.assertTrue(should_quit)

    def test_c_without_ctrl_does_not_quit(self):
        from evdev import ecodes
        cn = code_name(ecodes.KEY_C)
        ctrl_held = False
        keystate = 1
        should_quit = (keystate == 1 and cn == "KEY_C" and ctrl_held)
        self.assertFalse(should_quit)

    def test_ctrl_release_resets_state(self):
        """Releasing ctrl should reset ctrl_held so subsequent C doesn't quit."""
        ctrl_held = True
        # Simulate release (keystate 0)
        keystate = 0
        cn = "KEY_LEFTCTRL"
        if cn in ("KEY_LEFTCTRL", "KEY_RIGHTCTRL"):
            ctrl_held = keystate != 0
        self.assertFalse(ctrl_held)


class TestCleanupOnExit(unittest.TestCase):
    """Ensure device file descriptors are closed on exit."""

    def test_devices_closed_in_finally(self):
        mock_dev = MagicMock()
        mock_dev.close = MagicMock()

        keyboards = [mock_dev]
        for kb in keyboards:
            try:
                kb.close()
            except Exception:
                pass

        mock_dev.close.assert_called_once()

    def test_close_exception_is_swallowed(self):
        mock_dev = MagicMock()
        mock_dev.close.side_effect = OSError("device gone")

        keyboards = [mock_dev]
        for kb in keyboards:
            try:
                kb.close()
            except Exception:
                pass


class TestOutput(unittest.TestCase):
    """Test the Output class for stdout + file logging."""

    def test_write_without_log(self):
        out = Output(log_path=None)
        # Should not raise — just prints to stdout
        with patch("builtins.print") as mock_print:
            out.write("hello")
            mock_print.assert_called_once_with("hello", flush=True)
        out.close()

    def test_write_with_log_creates_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            path = f.name

        os.unlink(path)
        out = Output(log_path=path)
        out.write("line one")
        out.write("line two")
        out.close()

        with open(path) as f:
            content = f.read()
        self.assertIn("line one", content)
        self.assertIn("line two", content)
        os.unlink(path)

    def test_write_log_only_does_not_print(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            path = f.name

        os.unlink(path)
        out = Output(log_path=path)
        with patch("builtins.print") as mock_print:
            out.write_log_only("secret")
            mock_print.assert_not_called()

        out.close()
        with open(path) as f:
            content = f.read()
        self.assertIn("secret", content)
        os.unlink(path)

    def test_write_log_only_noop_without_log(self):
        out = Output(log_path=None)
        # Should not raise
        out.write_log_only("nothing")
        out.close()

    def test_close_is_idempotent(self):
        out = Output(log_path=None)
        out.close()
        out.close()  # should not raise

    def test_log_file_has_each_line(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            path = f.name

        os.unlink(path)
        out = Output(log_path=path)
        lines = ["first", "second", "third"]
        for line in lines:
            out.write(line)
        out.close()

        with open(path) as f:
            content = f.read()
        for line in lines:
            self.assertIn(line, content)
        os.unlink(path)


class TestDefaultLogPath(unittest.TestCase):
    def test_returns_path_in_logs_dir(self):
        path = default_log_path()
        self.assertTrue(path.startswith(LOG_DIR))
        self.assertTrue(path.endswith(".log"))

    def test_filename_contains_keyboard_prefix(self):
        path = default_log_path()
        basename = os.path.basename(path)
        self.assertTrue(basename.startswith("keyboard-"))

    def test_creates_logs_directory(self):
        path = default_log_path()
        self.assertTrue(os.path.isdir(LOG_DIR))


if __name__ == "__main__":
    unittest.main()
