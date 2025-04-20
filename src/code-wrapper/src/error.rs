use std::path::PathBuf;

use pyo3::{PyErr, exceptions::PyValueError};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CodeError {
    #[error("expected to have a type or a function, but got none")]
    TargetCanNotBeEmpty,
    #[error("failed to read the file")]
    FileReadError(#[from] std::io::Error),
    #[error("tree-sitter parse failed")]
    TSParseError,
    #[error("query population failed: {0}")]
    QueryPopulationError(#[from] strfmt::FmtError),
    #[error("failed to execute git command: {0}")]
    GitCommandErr(String),
    #[error("file not found: {0}")]
    FileNotFound(PathBuf),
    #[error("failed to copy directory: {0}")]
    CopyDirErr(#[from] fs_extra::error::Error),
}
pub type Result<T, E = CodeError> = core::result::Result<T, E>;

impl From<CodeError> for PyErr {
    fn from(value: CodeError) -> Self {
        PyValueError::new_err(value.to_string())
    }
}

