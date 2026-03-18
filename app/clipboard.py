"""Clipboard output for transcribed text."""

import base64
import shutil
import subprocess

import pyperclip


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


def copy_to_clipboard(
    text: str,
    which=shutil.which,
    run=subprocess.run,
    pyperclip_copy=pyperclip.copy,
    osc52_copy=copy_via_osc52,
) -> bool:
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
            )
            return True
        except (FileNotFoundError, PermissionError, subprocess.SubprocessError):
            continue

    try:
        pyperclip_copy(text)
        return True
    except pyperclip.PyperclipException:
        pass

    return osc52_copy(text)
