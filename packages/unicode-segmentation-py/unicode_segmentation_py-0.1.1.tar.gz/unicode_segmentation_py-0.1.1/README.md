# unicode-segmentation-py

Python bindings for Rust library `unicode-segmentation`.

Note that the `*_indices` functions return Python character offsets,
not byte offsets as in the original Rust library.

## Usage

```py
>>> import unicode_segmentation_py
>>> text = "Hello world!"
>>> unicode_segmentation_py.to_words(text)
['Hello', 'world']
>>> unicode_segmentation_py.to_word_indices(text)
[(0, 'Hello'), (6, 'world')]
>>> unicode_segmentation_py.split_word_bounds(text)
['Hello', ' ', 'world', '!']
>>> unicode_segmentation_py.split_word_bound_indices(text)
[(0, 'Hello'), (5, ' '), (6, 'world'), (11, '!')]
```

Other functions with similar signatures:

- `to_graphemes`
- `to_grapheme_indices`
- `to_sentences`
- `to_sentence_indices`
- `split_sentence_bounds`
- `split_sentence_bound_indices`

The underlying Unicode version used by `unicode-segmentation`
can be inspected through the constant `UNICODE_VERSION`,
which takes the form of a tuple of three integers.
