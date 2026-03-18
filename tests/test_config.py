from app.config import load_config, set_autocorrect_enabled


def test_autocorrect_defaults_to_enabled(tmp_path):
    config = load_config(tmp_path / "missing.toml")

    assert config.autocorrect.enabled is True
    assert config.autocorrect.markdown_support is False


def test_set_autocorrect_enabled_persists_value(tmp_path):
    config_path = tmp_path / "config.toml"

    set_autocorrect_enabled(False, config_path)
    disabled = load_config(config_path)
    assert disabled.autocorrect.enabled is False

    set_autocorrect_enabled(True, config_path)
    enabled = load_config(config_path)
    assert enabled.autocorrect.enabled is True
