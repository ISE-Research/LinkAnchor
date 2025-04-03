mod error;
mod wrapper;

use pyo3::prelude::*;

pub use error::Result;
pub use error::GitError;

/// A Python module implemented in Rust.
#[pymodule]
fn git_wrapper(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<wrapper::Wrapper>()?;
    m.add_class::<wrapper::CommitMeta>()?;
    m.add_class::<wrapper::Author>()?;
    m.add_class::<wrapper::AuthorQuery>()?;
    m.add_class::<wrapper::Pagination>()?;

    Ok(())
}
