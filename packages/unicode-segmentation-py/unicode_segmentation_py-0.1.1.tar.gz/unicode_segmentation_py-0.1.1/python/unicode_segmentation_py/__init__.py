"""Python bindings for Rust library `unicode-segmentation`.

Please refer to [`unicode-segmentation`](https://docs.rs/unicode-segmentation/)
and [UAX #29](https://www.unicode.org/reports/tr29/) for detailed explanation.
"""

from ._lowlevel import (
    UNICODE_VERSION,
    split_sentence_bounds,
    split_word_bounds,
    to_graphemes,
    to_sentences,
    to_words,
)
from .with_indices import (
    split_sentence_bound_indices,
    split_word_bound_indices,
    to_grapheme_indices,
    to_sentence_indices,
    to_word_indices,
)

__all__ = [
    "UNICODE_VERSION",
    "to_graphemes",
    "to_grapheme_indices",
    "to_words",
    "to_word_indices",
    "split_word_bounds",
    "split_word_bound_indices",
    "to_sentences",
    "to_sentence_indices",
    "split_sentence_bounds",
    "split_sentence_bound_indices",
]
