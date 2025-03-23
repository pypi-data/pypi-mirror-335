use pyo3::prelude::*;
use unicode_segmentation::{UnicodeSegmentation as _, UNICODE_VERSION};

#[pyfunction]
#[pyo3(signature=(text, extended=true))]
fn to_graphemes(text: &str, extended: bool) -> PyResult<Vec<&str>> {
    Ok(text.graphemes(extended).collect::<Vec<_>>())
}

#[pyfunction]
fn to_words(text: &str) -> PyResult<Vec<&str>> {
    Ok(text.unicode_words().collect::<Vec<_>>())
}

#[pyfunction]
fn split_word_bounds(text: &str) -> PyResult<Vec<&str>> {
    Ok(text.split_word_bounds().collect::<Vec<_>>())
}

#[pyfunction]
fn to_sentences(text: &str) -> PyResult<Vec<&str>> {
    Ok(text.unicode_sentences().collect::<Vec<_>>())
}

#[pyfunction]
fn split_sentence_bounds(text: &str) -> PyResult<Vec<&str>> {
    Ok(text.split_sentence_bounds().collect::<Vec<_>>())
}

#[pymodule]
fn _lowlevel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("UNICODE_VERSION", UNICODE_VERSION)?;
    m.add_function(wrap_pyfunction!(to_graphemes, m)?)?;
    m.add_function(wrap_pyfunction!(to_words, m)?)?;
    m.add_function(wrap_pyfunction!(split_word_bounds, m)?)?;
    m.add_function(wrap_pyfunction!(to_sentences, m)?)?;
    m.add_function(wrap_pyfunction!(split_sentence_bounds, m)?)?;
    Ok(())
}
