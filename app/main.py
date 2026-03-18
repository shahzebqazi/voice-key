"""Voice Hotkey — main entry point."""

import signal
import sys
import threading

from .config import load_config
from .hotkey import DoubleTapListener
from .recorder import Recorder
from .transcriber import Transcriber
from .clipboard import copy_to_clipboard


def _raise_keyboard_interrupt(signum, frame):
    raise KeyboardInterrupt


class VoiceHotkey:
    def __init__(self):
        self.cfg = load_config()
        self.recorder = Recorder(
            sample_rate=self.cfg.recording.sample_rate,
            timeout_seconds=self.cfg.recording.timeout_seconds,
        )
        self.transcriber = Transcriber(
            model_name=self.cfg.whisper.model,
            language=self.cfg.whisper.language,
        )
        self._processing_lock = threading.Lock()

    def _on_recording_complete(self, audio):
        if audio is None or len(audio) == 0:
            print("[voice-hotkey] No audio captured.")
            return

        duration = len(audio) / self.cfg.recording.sample_rate
        print(f"[voice-hotkey] Transcribing {duration:.1f}s of audio...")

        text = self.transcriber.transcribe(audio, self.cfg.recording.sample_rate)
        if text:
            copy_to_clipboard(text)
            print(f"[voice-hotkey] Copied to clipboard: {text}")
        else:
            print("[voice-hotkey] No speech detected.")

    def _on_activate(self):
        with self._processing_lock:
            if self.recorder.is_recording:
                print("[voice-hotkey] Stopping recording...")
                audio = self.recorder.stop()
                threading.Thread(
                    target=self._on_recording_complete, args=(audio,), daemon=True
                ).start()
            else:
                print("[voice-hotkey] Recording... (double-tap to stop)")
                self.recorder.start(on_timeout=self._on_recording_complete)

    def run(self):
        key = self.cfg.hotkey.key
        interval = self.cfg.hotkey.double_click_ms
        signal.signal(signal.SIGINT, _raise_keyboard_interrupt)

        listener = DoubleTapListener(key, interval, self._on_activate)
        try:
            listener.start()
            print(f"[voice-hotkey] Listening for double-tap on {key} (within {interval}ms)")
            print("[voice-hotkey] Press Ctrl+C to quit.")
            listener.join()
        except (RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n[voice-hotkey] Shutting down.")
        finally:
            listener.stop()
            listener.join(timeout=1.0)


def main():
    app = VoiceHotkey()
    app.run()


if __name__ == "__main__":
    main()
