mod error;
mod ts;
mod wrapper;

use error::{CodeError, Result};
pub use ts::Target;

use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn code_wrapper(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<wrapper::Wrapper>()?;
    Ok(())
}
