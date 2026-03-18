import numpy as np

from app.recorder import Recorder


def test_voice_chunk_updates_last_voice_timestamp():
    current_time = {"value": 3.0}
    recorder = Recorder(
        timeout_seconds=10,
        voice_threshold=0.01,
        time_source=lambda: current_time["value"],
    )
    recorder._recording = True
    recorder._started_at = 0.0
    recorder._last_voice_at = 0.0

    recorder._callback(np.full((160, 1), 0.1, dtype=np.float32), None, None, None)

    assert recorder._speech_detected is True
    assert recorder._last_voice_at == 3.0


def test_silence_timeout_is_based_on_last_detected_voice():
    recorder = Recorder(timeout_seconds=10)
    recorder._recording = True
    recorder._speech_detected = True
    recorder._last_voice_at = 5.0

    assert recorder._silence_expired(14.9) is False
    assert recorder._silence_expired(15.0) is True


def test_silence_timeout_starts_from_recording_start_before_speech():
    recorder = Recorder(timeout_seconds=10)
    recorder._recording = True
    recorder._speech_detected = False
    recorder._started_at = 2.0

    assert recorder._silence_expired(11.9) is False
    assert recorder._silence_expired(12.0) is True
