# Voice Hotkey

Linux desktop application that binds a modifier key (default: **Right Control**) as a double-click trigger to **record voice**, **transcribe with OpenAI Whisper**, and **copy the result to your clipboard**.

**Live site:** [https://sqazi.sh/voice-key/](https://sqazi.sh/voice-key/)

## Cross-Device Communication Portfolio

This branch also tracks a Kotlin/Ktor proof of concept for LAN communication
with an Android browser client.

- Kotlin app path: `kotlin-app/`
- Server bind: `0.0.0.0:8080`
- Android discovery: `adb devices` plus `_kdeconnect._udp`
- Server log target: `[Device Signal]: Message Received from Android Client`

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
python -m app.main
```

## How it works

1. **Double-click Right Control** — starts recording from your default microphone.
2. **Double-click Right Control again** (or wait for timeout) — stops recording.
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
- `xclip` or `xsel` for clipboard (install via your package manager)
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
key = "Key.ctrl_r"          # pynput key name
double_click_ms = 400       # max interval between clicks

[recording]
sample_rate = 16000
timeout_seconds = 30

[whisper]
model = "base"              # tiny, base, small, medium, large
language = "en"             # or "auto" for detection

[output]
target = "clipboard"        # clipboard (only option for MVP)
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
