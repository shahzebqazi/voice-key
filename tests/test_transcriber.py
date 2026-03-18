import numpy as np

from app.transcriber import Transcriber


class FakeModel:
    def __init__(self):
        self.calls = []

    def transcribe(self, audio, **opts):
        self.calls.append((audio, opts))
        return {"text": "hello world"}


def test_transcriber_disables_fp16_and_passes_language():
    transcriber = Transcriber(model_name="base", language="en")
    model = FakeModel()
    transcriber._model = model

    result = transcriber.transcribe(np.zeros(16000, dtype=np.float32))

    assert result == "hello world"
    _, opts = model.calls[0]
    assert opts["language"] == "en"
    assert opts["fp16"] is False
