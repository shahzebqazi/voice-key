"""Voice Hotkey — main entry point."""

import signal
import sys
import threading

from .clipboard import copy_to_clipboard
from .config import load_config
from .hotkey import DoubleTapListener
from .notify import NotificationSound
from .recorder import Recorder
from .runtime_state import clear_status, write_status
from .transcript_log import TRANSCRIPT_LOG_PATH, append_transcript
from .transcriber import Transcriber


def _raise_keyboard_interrupt(signum, frame):
    raise KeyboardInterrupt


class VoiceHotkey:
    def __init__(self):
        write_status("starting")
        self.cfg = load_config()
        self.recorder = Recorder(
            sample_rate=self.cfg.recording.sample_rate,
            timeout_seconds=self.cfg.recording.timeout_seconds,
        )
        self.transcriber = Transcriber(
            model_name=self.cfg.whisper.model,
            language=self.cfg.whisper.language,
        )
        self.notifier = NotificationSound()
        self._processing_lock = threading.Lock()
        write_status("idle", hotkey=self.cfg.hotkey.key)

    def _on_recording_complete(self, audio):
        write_status("processing", hotkey=self.cfg.hotkey.key)
        if audio is None or len(audio) == 0:
            print("[voice-hotkey] No audio captured.")
            write_status("idle", hotkey=self.cfg.hotkey.key)
            return

        duration = len(audio) / self.cfg.recording.sample_rate
        print(f"[voice-hotkey] Transcribing {duration:.1f}s of audio...")

        text = self.transcriber.transcribe(audio, self.cfg.recording.sample_rate)
        if text:
            log_path = append_transcript(text, duration)
            print(f"[voice-hotkey] Logged transcript to {log_path}")
            if copy_to_clipboard(text):
                print(f"[voice-hotkey] Copied to clipboard: {text}")
            else:
                print(f"[voice-hotkey] Clipboard unavailable. Transcript: {text}")
        else:
            print("[voice-hotkey] No speech detected.")
        write_status("idle", hotkey=self.cfg.hotkey.key)

    def _on_activate(self):
        with self._processing_lock:
            self.notifier.play_async()
            if self.recorder.is_recording:
                print("[voice-hotkey] Stopping recording...")
                write_status("processing", hotkey=self.cfg.hotkey.key)
                audio = self.recorder.stop()
                threading.Thread(
                    target=self._on_recording_complete, args=(audio,), daemon=True
                ).start()
            else:
                print(
                    f"[voice-hotkey] Recording... (double-tap to stop or pause for {self.cfg.recording.timeout_seconds}s)"
                )
                write_status("recording", hotkey=self.cfg.hotkey.key)
                self.recorder.start(on_timeout=self._on_recording_complete)

    def run(self):
        key = self.cfg.hotkey.key
        interval = self.cfg.hotkey.double_click_ms
        signal.signal(signal.SIGINT, _raise_keyboard_interrupt)

        listener = DoubleTapListener(key, interval, self._on_activate)
        try:
            listener.start()
            print(f"[voice-hotkey] Listening for double-tap on {key} (within {interval}ms)")
            print("[voice-hotkey] Bound keyboard devices:")
            for label in listener.device_labels():
                print(f"[voice-hotkey]   - {label}")
            print("[voice-hotkey] Press Ctrl+C to quit.")
            print(f"[voice-hotkey] Transcript log: {TRANSCRIPT_LOG_PATH}")
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
    try:
        app = VoiceHotkey()
        app.run()
    finally:
        clear_status()


if __name__ == "__main__":
    main()
