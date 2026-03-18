import numpy as np

from app.transcript_log import (
    append_transcript,
    clear_transcript_log,
    load_latest_transcript_text,
    load_transcript_queue,
)


def test_append_transcript_writes_timestamp_duration_and_text(tmp_path):
    log_path = tmp_path / "transcriptions.log"

    returned_path = append_transcript("hello world", 2.5, path=log_path)

    assert returned_path == log_path
    content = log_path.read_text(encoding="utf-8")
    assert "(2.5s)" in content
    assert "hello world" in content


def test_clear_transcript_log_removes_file(tmp_path):
    log_path = tmp_path / "transcriptions.log"
    log_path.write_text("hello world\n", encoding="utf-8")

    clear_transcript_log(log_path)

    assert not log_path.exists()


def test_append_transcript_keeps_queue_bounded_to_last_ten(tmp_path, monkeypatch):
    queue_path = tmp_path / "transcript_queue.json"
    recordings_dir = tmp_path / "recordings"
    monkeypatch.setattr("app.transcript_log.TRANSCRIPT_QUEUE_PATH", queue_path)
    monkeypatch.setattr("app.transcript_log.RECORDINGS_DIR", recordings_dir)

    for idx in range(12):
        append_transcript(
            f"hello {idx}",
            1.0,
            path=tmp_path / "transcriptions.log",
            audio=np.zeros(1600, dtype=np.float32),
            audio_hash=f"hash-{idx}",
        )

    entries = load_transcript_queue(queue_path)
    assert len(entries) == 10
    assert entries[0]["text"] == "hello 2"
    assert entries[-1]["text"] == "hello 11"


def test_load_latest_transcript_text_returns_newest_persisted_entry(tmp_path, monkeypatch):
    queue_path = tmp_path / "transcript_queue.json"
    monkeypatch.setattr("app.transcript_log.TRANSCRIPT_QUEUE_PATH", queue_path)

    append_transcript("first entry", 1.0, path=tmp_path / "transcriptions.log")
    append_transcript("latest entry", 1.5, path=tmp_path / "transcriptions.log")

    assert load_latest_transcript_text(queue_path) == "latest entry"


def test_load_latest_transcript_text_returns_empty_string_when_queue_missing(tmp_path):
    assert load_latest_transcript_text(tmp_path / "missing.json") == ""
