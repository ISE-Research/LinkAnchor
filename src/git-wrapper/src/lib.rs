mod error;
mod wrapper;
mod branchless;

use error::BranchNotFoundErr;
use pyo3::prelude::*;

pub use error::Result;
pub use error::GitError;
pub use branchless::Branchless;
pub use wrapper::Wrapper;
pub use wrapper::Pagination;
pub use wrapper::PaginationExt;
pub use wrapper::CommitMeta;

/// A Python module implemented in Rust.
#[pymodule]
fn git_wrapper(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<wrapper::Wrapper>()?;
    m.add_class::<wrapper::CommitMeta>()?;
    m.add_class::<wrapper::Author>()?;
    m.add_class::<wrapper::AuthorQuery>()?;
    m.add_class::<wrapper::Pagination>()?;
    m.add_class::<branchless::Branchless>()?;
    m.add("BranchNotFoundErr", py.get_type::<BranchNotFoundErr>())?;

    Ok(())
}
