"""Configuration loader for voice-hotkey."""

import os
import pwd
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

def _user_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and os.geteuid() == 0:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    return Path.home()


CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", _user_home() / ".config")) / "voice-hotkey"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULTS = {
    "hotkey": {"key": "KEY_RIGHTALT", "double_click_ms": 400},
    "recording": {"sample_rate": 16000, "timeout_seconds": 10},
    "whisper": {"model": "base", "language": "en"},
    "output": {"target": "clipboard"},
    "autocorrect": {"enabled": True, "markdown_support": False},
}


@dataclass
class HotkeyConfig:
    key: str = "KEY_RIGHTALT"
    double_click_ms: int = 400


@dataclass
class RecordingConfig:
    sample_rate: int = 16000
    timeout_seconds: int = 10


@dataclass
class WhisperConfig:
    model: str = "base"
    language: str = "en"


@dataclass
class OutputConfig:
    target: str = "clipboard"


@dataclass
class AutocorrectConfig:
    enabled: bool = True
    markdown_support: bool = False


@dataclass
class AppConfig:
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    recording: RecordingConfig = field(default_factory=RecordingConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    autocorrect: AutocorrectConfig = field(default_factory=AutocorrectConfig)


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
        autocorrect=AutocorrectConfig(**raw.get("autocorrect", {})),
    )


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def write_config(config: AppConfig, path: Path | None = None) -> Path:
    cfg_path = path or CONFIG_PATH
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "[hotkey]",
            f'key = "{config.hotkey.key}"',
            f"double_click_ms = {config.hotkey.double_click_ms}",
            "",
            "[recording]",
            f"sample_rate = {config.recording.sample_rate}",
            f"timeout_seconds = {config.recording.timeout_seconds}",
            "",
            "[whisper]",
            f'model = "{config.whisper.model}"',
            f'language = "{config.whisper.language}"',
            "",
            "[output]",
            f'target = "{config.output.target}"',
            "",
            "[autocorrect]",
            f"enabled = {_bool_text(config.autocorrect.enabled)}",
            f"markdown_support = {_bool_text(config.autocorrect.markdown_support)}",
            "",
        ]
    )
    cfg_path.write_text(content, encoding="utf-8")
    return cfg_path


def set_autocorrect_enabled(enabled: bool, path: Path | None = None) -> Path:
    config = load_config(path)
    config.autocorrect.enabled = bool(enabled)
    return write_config(config, path)
