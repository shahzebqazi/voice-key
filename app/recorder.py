"""Audio recorder using sounddevice with silence-based auto-stop."""

import threading
import time

import numpy as np
import sounddevice as sd


class Recorder:
    """Record audio from the default microphone into a numpy buffer."""

    def __init__(
        self,
        sample_rate: int = 16000,
        timeout_seconds: int = 10,
        voice_threshold: float = 0.015,
        monitor_interval: float = 0.2,
        time_source=time.monotonic,
        stream_factory=sd.InputStream,
    ):
        self.sample_rate = sample_rate
        self.timeout = timeout_seconds
        self.voice_threshold = voice_threshold
        self.monitor_interval = monitor_interval
        self._time_source = time_source
        self._stream_factory = stream_factory
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._recording = False
        self._lock = threading.Lock()
        self._monitor_thread: threading.Thread | None = None
        self._monitor_stop = threading.Event()
        self._speech_detected = False
        self._started_at: float = 0.0
        self._last_voice_at: float = 0.0

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _has_voice(self, indata: np.ndarray) -> bool:
        level = float(np.sqrt(np.mean(np.square(indata))))
        return level >= self.voice_threshold

    def _silence_expired(self, now: float) -> bool:
        if not self._recording or self.timeout <= 0:
            return False
        deadline = self._last_voice_at if self._speech_detected else self._started_at
        return (now - deadline) >= self.timeout

    def _callback(self, indata, frames, time_info, status):
        if self._recording:
            self._frames.append(indata.copy())
            if self._has_voice(indata):
                self._speech_detected = True
                self._last_voice_at = self._time_source()

    def start(self, on_timeout=None):
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._recording = True
            self._speech_detected = False
            self._started_at = self._time_source()
            self._last_voice_at = self._started_at
            self._monitor_stop.clear()
            self._stream = self._stream_factory(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()

            if self.timeout > 0:
                self._monitor_thread = threading.Thread(
                    target=self._monitor_silence,
                    args=(on_timeout,),
                    daemon=True,
                )
                self._monitor_thread.start()

    def _monitor_silence(self, callback):
        while not self._monitor_stop.wait(self.monitor_interval):
            with self._lock:
                should_stop = self._silence_expired(self._time_source())
            if should_stop:
                self._auto_stop(callback)
                return

    def _auto_stop(self, callback):
        audio = self.stop()
        if callback and audio is not None:
            callback(audio)

    def stop(self) -> np.ndarray | None:
        with self._lock:
            if not self._recording:
                return None
            self._recording = False
            self._monitor_stop.set()
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if not self._frames:
                return None
            return np.concatenate(self._frames, axis=0).flatten()
