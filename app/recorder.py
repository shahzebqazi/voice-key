"""Audio recorder using sounddevice."""

import threading
import numpy as np
import sounddevice as sd


class Recorder:
    """Record audio from the default microphone into a numpy buffer."""

    def __init__(self, sample_rate: int = 16000, timeout_seconds: int = 30):
        self.sample_rate = sample_rate
        self.timeout = timeout_seconds
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._recording = False
        self._lock = threading.Lock()
        self._timeout_timer: threading.Timer | None = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata, frames, time_info, status):
        if self._recording:
            self._frames.append(indata.copy())

    def start(self, on_timeout=None):
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._recording = True
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()

            if self.timeout > 0:
                self._timeout_timer = threading.Timer(
                    self.timeout, self._auto_stop, args=(on_timeout,)
                )
                self._timeout_timer.daemon = True
                self._timeout_timer.start()

    def _auto_stop(self, callback):
        audio = self.stop()
        if callback and audio is not None:
            callback(audio)

    def stop(self) -> np.ndarray | None:
        with self._lock:
            if not self._recording:
                return None
            self._recording = False
            if self._timeout_timer:
                self._timeout_timer.cancel()
                self._timeout_timer = None
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if not self._frames:
                return None
            return np.concatenate(self._frames, axis=0).flatten()
