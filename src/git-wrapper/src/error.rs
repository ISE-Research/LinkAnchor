use pyo3::{
    create_exception,
    exceptions::{PyException, PyValueError},
    PyErr,
};
use thiserror::Error;

create_exception!(git_wrapper, BranchNotFoundErr, PyException);

#[derive(Error, Debug)]
pub enum GitError {
    #[error("expected format: artifact::package::class::function(args)->output")]
    MalFormedMethodUrlErr,
    #[error("failed to perform IO operation: {0}")]
    IoErr(#[from] std::io::Error),
    #[error("git command failed: {0}")]
    GitCommandErr(String),
    #[error("malformed data incountered: {0}")]
    MalFormedData(String),
    #[error("failed to parse date: {0}")]
    DatetimeError(#[from] chrono::ParseError),
    #[error("commit not found for hash: {0}")]
    CommitNotFound(String),
    #[error("failed to copy directory: {0}")]
    CopyDirErr(#[from] fs_extra::error::Error),
    #[error("branch not found: {0}")]
    BranchNotFound(String),
    #[error("No Author matched for this Author Query: {0}")]
    AuthorNotFound(String),
}
pub type Result<T, E = GitError> = core::result::Result<T, E>;

impl From<GitError> for PyErr {
    fn from(value: GitError) -> Self {
        match value {
            GitError::BranchNotFound(branch) => {
                BranchNotFoundErr::new_err(format!("Branch not found: {}", branch))
            }
            _ => PyValueError::new_err(value.to_string()),
        }
    }
}
