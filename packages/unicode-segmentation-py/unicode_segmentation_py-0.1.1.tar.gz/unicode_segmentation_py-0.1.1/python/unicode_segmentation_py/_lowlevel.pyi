UNICODE_VERSION: tuple[int, int, int]
"""The underlying Unicode version used by `unicode-segmentation`."""

def to_graphemes(text: str, extended: bool = True) -> list[str]:
    """Return grapheme clusters of a string.

    Args:
        text: The string to analyze.
        extended: Whether are extended grapheme clusters. Defaults to true.

    Returns:
        The grapheme clusters.
    """

def to_words(text: str) -> list[str]:
    """Split a string on word boundaries and return "words".

    A "word" is a substring that contains at least one alphanumeric character.

    Args:
        text: The string to analyze.

    Returns:
        The "words".
    """

def split_word_bounds(text: str) -> list[str]:
    """Return substrings seperated on word boundaries.

    The concatenation is exactly the original string.

    Args:
        text: The string to analyze.

    Returns:
        The substrings.
    """

def to_sentences(text: str) -> list[str]:
    """Split a string on sentence boundaries and return "sentences".

    A "sentence" is a substring that contains at least one alphanumeric character.

    Args:
        text: The string to analyze.

    Returns:
        The "sentences".
    """

def split_sentence_bounds(text: str) -> list[str]:
    """Return substrings seperated on sentence boundaries.

    The concatenation is exactly the original string.

    Args:
        text: The string to analyze.

    Returns:
        The substrings.
    """
