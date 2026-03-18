# Product requirements — Voice Hotkey

## 1. Product overview

Voice Hotkey is a Linux desktop application that captures voice input via a configurable keyboard shortcut and transcribes it to text using OpenAI Whisper.

**Live site:** [https://sqazi.sh/voice-key/](https://sqazi.sh/voice-key/)  
**Repository:** [github.com/sqazi/voice-key](https://github.com/sqazi/voice-key)

---

## 2. MVP scope

### 2.1 Core features

| Feature | Description | Priority |
|---------|-------------|----------|
| Double-click trigger | Right Control key, double-click within 400 ms | MUST |
| Audio recording | Capture from default microphone at 16 kHz | MUST |
| Whisper transcription | Local inference using `openai-whisper` (base model) | MUST |
| Clipboard output | Copy transcribed text via `pyperclip` | MUST |
| Config file | TOML at `~/.config/voice-hotkey/config.toml` | MUST |
| Timeout | Auto-stop recording after 30 seconds | MUST |

### 2.2 Non-goals (MVP)

- No GUI or system tray
- No cloud API integration
- No active-window text injection
- No Windows or macOS support

---

## 3. Future scope

| Feature | Description | Phase |
|---------|-------------|-------|
| Configurable keys | Right Alt, Super, Fn, Copilot key | 2 |
| Model selection | Runtime model switching | 2 |
| Language detection | Auto-detect spoken language | 2 |
| Text-to-speech | Generate voice from text | 3 |
| Autocomplete | AI suggestions on transcribed text | 3 |
| Autocorrect | Grammar/spelling correction | 3 |
| Active window injection | Type into focused app via xdotool/wtype | 3 |
| Multi-platform | Windows and macOS support | 4 |

---

## 4. Platform requirements

- **OS:** Linux (kernel 5.x+)
- **Display:** X11 or Wayland with XWayland
- **Python:** 3.9+
- **Audio:** PulseAudio or PipeWire (via PortAudio)
- **Clipboard:** `xclip`, `xsel`, or `wl-copy`
- **FFmpeg:** Required by Whisper

---

## 5. Architecture

```
User → [Double-tap key] → pynput listener
  → sounddevice (record audio)
  → openai-whisper (transcribe)
  → pyperclip (copy to clipboard)
```

All components run in a single Python process. Recording and transcription use background threads to avoid blocking the key listener.

---

## 6. Security

- No secrets in repository (API keys in config/env only)
- Audio recorded to memory, not disk
- No network access required for local Whisper
- Requires input device access (`input` group)

---

## 7. Configuration

See `app/config.example.toml` for the full schema. Config respects `$XDG_CONFIG_HOME`.

---

## 8. Success criteria

1. Double-click Right Control reliably starts/stops recording
2. Whisper transcribes captured audio with reasonable accuracy
3. Transcribed text appears in system clipboard within 5 seconds of stopping
4. Application runs as a background daemon without GUI
