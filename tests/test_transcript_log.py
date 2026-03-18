from app.transcript_log import append_transcript


def test_append_transcript_writes_timestamp_duration_and_text(tmp_path):
    log_path = tmp_path / "transcriptions.log"

    returned_path = append_transcript("hello world", 2.5, path=log_path)

    assert returned_path == log_path
    content = log_path.read_text(encoding="utf-8")
    assert "(2.5s)" in content
    assert "hello world" in content
