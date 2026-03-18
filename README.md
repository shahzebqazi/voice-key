# Voice Hotkey

Linux desktop application that binds a modifier key (default: **Right Alt**) as a double-click trigger to **record voice**, **transcribe with OpenAI Whisper**, and **copy the result to your clipboard**.

**Live site:** [https://sqazi.sh/voice-key/](https://sqazi.sh/voice-key/)

## Quick start

```bash
# 1. Clone
git clone https://github.com/sqazi/voice-key.git
cd voice-key

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure
mkdir -p ~/.config/voice-hotkey
cp app/config.example.toml ~/.config/voice-hotkey/config.toml
# Edit config.toml to set your preferred key, Whisper model, timeout, etc.

# 5. Run
sudo --preserve-env=DISPLAY,WAYLAND_DISPLAY,XDG_RUNTIME_DIR,DBUS_SESSION_BUS_ADDRESS,PULSE_SERVER \
  ./venv/bin/python -u -m app.main
```

On Wayland and on systems using external keyboards, the hotkey listener may need `sudo` so it can read `/dev/input/event*`. Preserving the desktop session variables keeps notification sounds, audio, and clipboard access working while the process runs as root.

## How it works

1. **Double-click Right Alt** — starts recording from your default microphone.
2. **Double-click Right Alt again** (or wait for timeout) — stops recording.
3. Audio is transcribed locally using OpenAI Whisper.
4. Transcribed text is copied to your clipboard.

## Dependencies

| Package | Purpose |
|---------|---------|
| `pynput` | Global keyboard listener |
| `sounddevice` + `numpy` | Audio capture |
| `openai-whisper` | Local speech-to-text |
| `pyperclip` | Clipboard access |
| `tomli` | Config file parsing (Python < 3.11) |

### System requirements

- **Linux** (X11 or Wayland with XWayland)
- **Python 3.9+**
- `xclip`, `xsel`, or `wl-copy` for clipboard (install via your package manager)
- `ffmpeg` (required by Whisper)
- PortAudio (`libportaudio2` on Debian/Ubuntu)

```bash
# Debian / Ubuntu
sudo apt install xclip ffmpeg libportaudio2 portaudio19-dev

# Arch
sudo pacman -S xclip ffmpeg portaudio
```

## Configuration

Config file: `~/.config/voice-hotkey/config.toml`

```toml
[hotkey]
key = "KEY_RIGHTALT"        # evdev key name
double_click_ms = 400       # max interval between clicks

[recording]
sample_rate = 16000
timeout_seconds = 10

[whisper]
model = "base"              # tiny, base, small, medium, large
language = "en"             # or "auto" for detection

[output]
target = "clipboard"        # clipboard with terminal OSC 52 fallback when available
```

## Project structure

```
voice-key/
├── app/                    # Application source
│   ├── main.py             # Entry point
│   ├── hotkey.py           # Double-click key listener
│   ├── recorder.py         # Audio capture
│   ├── transcriber.py      # Whisper integration
│   ├── clipboard.py        # Output to clipboard
│   ├── config.py           # Config loader
│   └── config.example.toml # Example config
├── docs/                   # Markdown documentation
├── documents/              # HTML documents (GitHub Pages)
├── mockups/                # HTML mockups (GitHub Pages)
├── styles/                 # CSS (GitHub Pages)
├── scripts/                # JS (GitHub Pages)
├── index.html              # GitHub Pages landing page
├── requirements.txt
├── PLAYBOOK.md
└── README.md
```

## License

MIT
