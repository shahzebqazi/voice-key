from app.autocorrect import autocorrect_spelling, autocorrect_transcript, finalize_grammar_and_formatting


def test_spelling_correction_keeps_proper_nouns():
    text = "i met Shahzeb adn alex at teh office"

    corrected = autocorrect_spelling(text)

    assert "Shahzeb" in corrected
    assert "and" in corrected
    assert "the office" in corrected


def test_finalize_grammar_capitalizes_and_punctuates():
    text = "hello world this is a test"

    corrected = finalize_grammar_and_formatting(text)

    assert corrected == "Hello world this is a test."


def test_autocorrect_transcript_combines_spelling_and_formatting():
    text = "im fixing teh launcher for Shahzeb"

    corrected = autocorrect_transcript(text)

    assert corrected == "I'm fixing the launcher for Shahzeb."


def test_autocorrect_transcript_skips_command_like_text():
    text = "run ./venv/bin/python -m app.main --debug"

    corrected = autocorrect_transcript(text)

    assert corrected == text
