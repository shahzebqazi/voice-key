"""Local autocorrect helpers for transcript cleanup."""

from __future__ import annotations

import re

COMMON_CORRECTIONS = {
    "adn": "and",
    "becuase": "because",
    "cant": "can't",
    "didnt": "didn't",
    "doesnt": "doesn't",
    "dont": "don't",
    "im": "I'm",
    "ive": "I've",
    "lets": "let's",
    "recieve": "receive",
    "teh": "the",
    "thier": "their",
    "theyre": "they're",
    "wasnt": "wasn't",
    "wont": "won't",
}

TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[^A-Za-z]+")


def _looks_like_proper_noun(token: str, sentence_start: bool) -> bool:
    if not token or not token[0].isalpha():
        return False
    if any(ch.isupper() for ch in token[1:]):
        return True
    return token[0].isupper() and not sentence_start


def _looks_like_markup_or_code(token: str) -> bool:
    return any(ch in token for ch in ("`", "#", "*", "_", "/", "\\", "[", "]", "(", ")", ":"))


def _looks_like_literal_or_code_text(text: str) -> bool:
    """Avoid mutating command/code-like transcripts."""
    if not text.strip():
        return False

    command_markers = (
        "`",
        "$",
        "&&",
        "||",
        "::",
        "->",
        "=>",
        "--",
        "~/",
        "./",
        "/",
        "\\",
        ".py",
        ".ts",
        ".js",
        ".md",
        ".json",
        ".toml",
    )
    if any(marker in text for marker in command_markers):
        return True

    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\(", text):
        return True

    letter_count = sum(1 for ch in text if ch.isalpha())
    symbol_count = sum(1 for ch in text if not ch.isalnum() and not ch.isspace())
    if letter_count and symbol_count / letter_count > 0.2:
        return True

    return False


def autocorrect_spelling(text: str) -> str:
    """Apply lightweight word-level corrections while avoiding proper nouns."""
    parts: list[str] = []
    sentence_start = True

    for token in TOKEN_RE.findall(text):
        if token.isalpha() or "'" in token:
            lower = token.lower()
            if not _looks_like_markup_or_code(token) and not _looks_like_proper_noun(token, sentence_start):
                token = COMMON_CORRECTIONS.get(lower, token)
            parts.append(token)
            sentence_start = False
        else:
            parts.append(token)
            if any(ch in token for ch in ".!?"):
                sentence_start = True

    return "".join(parts)


def finalize_grammar_and_formatting(text: str, markdown_support: bool = False) -> str:
    """Normalize transcript punctuation and capitalization.

    `markdown_support` is reserved for future markdown-aware formatting.
    """
    normalized = re.sub(r"[ \t]+", " ", text.strip())
    normalized = re.sub(r"\s+([,.;:!?])", r"\1", normalized)
    normalized = re.sub(r"\bi\b", "I", normalized)

    chars = list(normalized)
    sentence_start = True
    for idx, ch in enumerate(chars):
        if sentence_start and ch.isalpha():
            chars[idx] = ch.upper()
            sentence_start = False
        elif ch in ".!?":
            sentence_start = True
        elif not ch.isspace():
            sentence_start = False

    result = "".join(chars)
    if result and result[-1].isalnum() and not markdown_support:
        result += "."
    return result


def autocorrect_transcript(text: str, markdown_support: bool = False) -> str:
    """Run the transcript through lightweight local autocorrect stages."""
    if _looks_like_literal_or_code_text(text):
        return text.strip()

    corrected = autocorrect_spelling(text)
    return finalize_grammar_and_formatting(corrected, markdown_support=markdown_support)
