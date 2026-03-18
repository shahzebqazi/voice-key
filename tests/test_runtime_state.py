from app.runtime_state import RECENT_PROMPTS_PATH, append_recent_prompt, clear_recent_prompts, load_recent_prompts


def test_clear_recent_prompts_removes_saved_history(tmp_path, monkeypatch):
    history_path = tmp_path / "recent_prompts.json"
    monkeypatch.setattr("app.runtime_state.RECENT_PROMPTS_PATH", history_path)

    append_recent_prompt("hello world", 2.5)
    assert load_recent_prompts() != []

    clear_recent_prompts()

    assert load_recent_prompts() == []
    assert not history_path.exists()
