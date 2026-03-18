"""Whisper transcription wrapper."""

import numpy as np
import whisper


class Transcriber:
    """Thin wrapper around openai-whisper for local transcription."""

    def __init__(self, model_name: str = "base", language: str = "en"):
        self.model_name = model_name
        self.language = language
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            print(f"[voice-hotkey] Loading Whisper model '{self.model_name}'...")
            self._model = whisper.load_model(self.model_name)

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        self._ensure_model()

        audio_f32 = audio.astype(np.float32)
        if sample_rate != 16000:
            import whisper.audio
            audio_f32 = whisper.audio.resample(audio_f32, sample_rate, 16000)

        opts = {}
        if self.language and self.language != "auto":
            opts["language"] = self.language
        opts["fp16"] = False

        result = self._model.transcribe(audio_f32, **opts)
        return result.get("text", "").strip()
