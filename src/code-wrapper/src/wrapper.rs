use std::{fmt::Display, path::PathBuf, process::Command};

use crate::ts::Lang;

use super::{CodeError, Result};
use pyo3::{pyclass, pymethods};
use temp_dir::TempDir;

#[pyclass(str)]
pub struct Wrapper {
    dir: TempDir,
    default_branch: String,
    langs: Vec<Lang>,
}

#[pymethods]
impl Wrapper {
    #[new]
    pub fn new(repo_url: &str) -> Result<Self> {
        let dir = TempDir::new()?;

        // Get the path to the temporary directory
        let dir_path = dir.path();

        // Run git clone command
        let output = Command::new("git")
            .arg("clone")
            .arg(repo_url)
            .arg(dir_path)
            .output()?;

        // Check if the command was successful
        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(CodeError::GitCommandErr(error_message));
        }

        // Find the default branch
        let output = Command::new("git")
            .arg("rev-parse")
            .arg("--abbrev-ref")
            .arg("HEAD")
            .current_dir(dir.path())
            .output()?;

        match output.status.success() {
            false => {
                let error_message = String::from_utf8_lossy(&output.stderr).to_string();
                Err(CodeError::GitCommandErr(error_message))
            }
            true => {
                let default_branch = String::from_utf8_lossy(&output.stdout)
                    .trim_end_matches("\n")
                    .to_string();
                Ok(Self {
                    dir,
                    default_branch,
                    langs: vec![],
                })
            }
        }
    }

    pub fn function_definition(
        &self,
        name: &str,
        commit: &str,
        file_path: PathBuf,
    ) -> Result<Vec<String>> {
        self.checkout(commit)?;
        for lang in &self.langs {
            if lang.accepts(&file_path) {
                let target = lang.parse(name);
                let matches = lang.find_in(target, &file_path)?;
                let matches = matches.iter().map(|(def, doc)| def).collect();
                Ok(matches);
            }
        }
        Ok(Vec::new())
    }
}

impl Wrapper {
    fn checkout(&self, commit: &str) -> Result<()> {
        let output = Command::new("git")
            .arg("checkout")
            .arg(commit)
            .current_dir(self.dir.path())
            .output()?;

        match output.status.success() {
            false => {
                let error_message = String::from_utf8_lossy(&output.stderr).to_string();
                Err(CodeError::GitCommandErr(error_message))
            }
            true => Ok(()),
        }
    }
}

impl Display for Wrapper {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?} on branch {}", self.dir.path(), self.default_branch)
    }
}
