"""Configuration loader for voice-hotkey."""

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "voice-hotkey"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULTS = {
    "hotkey": {"key": "Key.ctrl_r", "double_click_ms": 400},
    "recording": {"sample_rate": 16000, "timeout_seconds": 30},
    "whisper": {"model": "base", "language": "en"},
    "output": {"target": "clipboard"},
}


@dataclass
class HotkeyConfig:
    key: str = "Key.ctrl_r"
    double_click_ms: int = 400


@dataclass
class RecordingConfig:
    sample_rate: int = 16000
    timeout_seconds: int = 30


@dataclass
class WhisperConfig:
    model: str = "base"
    language: str = "en"


@dataclass
class OutputConfig:
    target: str = "clipboard"


@dataclass
class AppConfig:
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    recording: RecordingConfig = field(default_factory=RecordingConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def _merge(defaults: dict, overrides: dict) -> dict:
    merged = dict(defaults)
    for k, v in overrides.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def load_config(path: Path | None = None) -> AppConfig:
    cfg_path = path or CONFIG_PATH
    raw = dict(DEFAULTS)

    if cfg_path.exists():
        with open(cfg_path, "rb") as f:
            user = tomllib.load(f)
        raw = _merge(raw, user)

    return AppConfig(
        hotkey=HotkeyConfig(**raw.get("hotkey", {})),
        recording=RecordingConfig(**raw.get("recording", {})),
        whisper=WhisperConfig(**raw.get("whisper", {})),
        output=OutputConfig(**raw.get("output", {})),
    )
