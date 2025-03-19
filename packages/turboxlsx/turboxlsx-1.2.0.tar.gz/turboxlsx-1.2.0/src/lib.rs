use pyo3::prelude::*;
mod book;
mod sheet;

/// A Python module implemented in Rust.
#[pymodule]
fn turboxlsx(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<book::BookWriter>()?;
    Ok(())
}
