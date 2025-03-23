import unicode_segmentation_py


def test_unicode_version():
    major, minor, patch = unicode_segmentation_py.UNICODE_VERSION
    assert major >= 0 and minor >= 0 and patch >= 0


def test_graphemes():
    text = "a\u0310e\u0301o\u0308\u0332\r\ni\U0001f1f7\U0001f1fa\U0001f1f8\U0001f1f9"
    graphemes = ["a\u0310", "e\u0301", "o\u0308\u0332", "\r\n", "i", "\U0001f1f7\U0001f1fa", "\U0001f1f8\U0001f1f9"]
    assert unicode_segmentation_py.to_graphemes(text) == graphemes
    grapheme_indices = [
        (0, "a\u0310"),
        (2, "e\u0301"),
        (4, "o\u0308\u0332"),
        (7, "\r\n"),
        (9, "i"),
        (10, "\U0001f1f7\U0001f1fa"),
        (12, "\U0001f1f8\U0001f1f9"),
    ]
    assert unicode_segmentation_py.to_grapheme_indices(text) == grapheme_indices


def test_words():
    text = """The quick ("brown") fox can't jump 32.3 feet, right?"""
    words = ["The", "quick", "brown", "fox", "can't", "jump", "32.3", "feet", "right"]
    assert unicode_segmentation_py.to_words(text) == words
    word_indices = [
        (0, "The"),
        (4, "quick"),
        (12, "brown"),
        (20, "fox"),
        (24, "can't"),
        (30, "jump"),
        (35, "32.3"),
        (40, "feet"),
        (46, "right"),
    ]
    assert unicode_segmentation_py.to_word_indices(text) == word_indices
    substrs = [
        "The",
        " ",
        "quick",
        " ",
        "(",
        '"',
        "brown",
        '"',
        ")",
        " ",
        "fox",
        " ",
        "can't",
        " ",
        "jump",
        " ",
        "32.3",
        " ",
        "feet",
        ",",
        " ",
        "right",
        "?",
    ]
    assert unicode_segmentation_py.split_word_bounds(text) == substrs
    assert "".join(substrs) == text
    substr_indices = [
        (0, "The"),
        (3, " "),
        (4, "quick"),
        (9, " "),
        (10, "("),
        (11, '"'),
        (12, "brown"),
        (17, '"'),
        (18, ")"),
        (19, " "),
        (20, "fox"),
        (23, " "),
        (24, "can't"),
        (29, " "),
        (30, "jump"),
        (34, " "),
        (35, "32.3"),
        (39, " "),
        (40, "feet"),
        (44, ","),
        (45, " "),
        (46, "right"),
        (51, "?"),
    ]
    assert unicode_segmentation_py.split_word_bound_indices(text) == substr_indices
    assert "".join(p[1] for p in substr_indices) == text


def test_sentences():
    text = "Mr. Fox jumped. [...] The dog was too lazy."
    sentences = ["Mr. ", "Fox jumped. ", "The dog was too lazy."]
    assert unicode_segmentation_py.to_sentences(text) == sentences
    sentence_indices = [(0, "Mr. "), (4, "Fox jumped. "), (22, "The dog was too lazy.")]
    assert unicode_segmentation_py.to_sentence_indices(text) == sentence_indices
    substrs = ["Mr. ", "Fox jumped. ", "[...] ", "The dog was too lazy."]
    assert unicode_segmentation_py.split_sentence_bounds(text) == substrs
    assert "".join(substrs) == text
    substr_indices = [(0, "Mr. "), (4, "Fox jumped. "), (16, "[...] "), (22, "The dog was too lazy.")]
    assert unicode_segmentation_py.split_sentence_bound_indices(text) == substr_indices
    assert "".join(p[1] for p in substr_indices) == text
