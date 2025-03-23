"""Utilities to return substrings with start indices."""

from collections.abc import Iterator

from ._lowlevel import (
    split_sentence_bounds,
    split_word_bounds,
    to_graphemes,
    to_sentences,
    to_words,
)


def _yield_substr_indices(text: str, substrs: list[str]) -> Iterator[int]:
    if not substrs:
        return
    offset = 0
    for substr in substrs:
        offset = text.find(substr, offset)
        assert offset != -1
        yield offset


def _with_substr_indices(text: str, substrs: list[str]) -> list[tuple[int, str]]:
    indices = _yield_substr_indices(text, substrs)
    return list(zip(indices, substrs))


def to_grapheme_indices(text: str, extended: bool = True) -> list[tuple[int, str]]:
    """Return grapheme clusters with character offsets of a string.

    Args:
        text: The string to analyze.
        extended: Whether are extended grapheme clusters. Defaults to true.

    Returns:
        Pairs of grapheme clusters and their character offsets.
    """
    substrs = to_graphemes(text, extended)
    return _with_substr_indices(text, substrs)


def to_word_indices(text: str) -> list[tuple[int, str]]:
    """Split a string on word boundaries and return "words" with character offsets.

    A "word" is a substring that contains at least one alphanumeric character.

    Args:
        text: The string to analyze.

    Returns:
        Pairs of "words" and their character offsets.
    """
    substrs = to_words(text)
    return _with_substr_indices(text, substrs)


def split_word_bound_indices(text: str) -> list[tuple[int, str]]:
    """Return substrings seperated on word boundaries with character offsets.

    The concatenation of the substrings is exactly the original string.

    Args:
        text: The string to analyze.

    Returns:
        Pairs of substrings and their character offsets.
    """
    substrs = split_word_bounds(text)
    return _with_substr_indices(text, substrs)


def to_sentence_indices(text: str) -> list[tuple[int, str]]:
    """Split a string on sentence boundaries and return "sentences" with character offsets.

    A "sentence" is a substring that contains at least one alphanumeric character.

    Args:
        text: The string to analyze.

    Returns:
        Pairs of "sentences" and their character offsets.
    """
    substrs = to_sentences(text)
    return _with_substr_indices(text, substrs)


def split_sentence_bound_indices(text: str) -> list[tuple[int, str]]:
    """Return substrings seperated on sentence boundaries with character offsets.

    The concatenation of the substrings is exactly the original string.

    Args:
        text: The string to analyze.

    Returns:
        Pairs of substrings and their character offsets.
    """
    substrs = split_sentence_bounds(text)
    return _with_substr_indices(text, substrs)
