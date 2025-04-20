use std::io::BufRead;
use std::{fmt::Display, path::PathBuf, process::Command};

use crate::ts::{Lang, Target};

use super::{CodeError, Result};
use pyo3::{pyclass, pymethods};
use temp_dir::TempDir;

#[pyclass(str)]
pub struct Wrapper {
    dir: TempDir,
    default_branch: String,
    langs: Vec<Lang>,
}

impl Wrapper {
    fn new_from_temp_dir(dir: TempDir) -> Result<Self> {
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
                    langs: vec![Lang::go(), Lang::python(), Lang::java()],
                })
            }
        }
    }
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

        Self::new_from_temp_dir(dir)
    }

    #[staticmethod]
    pub fn from_local(local_dir_path: PathBuf) -> Result<Self> {
        let dir = TempDir::new()?;

        let dir_path = dir.path();

        let mut options = fs_extra::dir::CopyOptions::new();
        options.overwrite = true; // overwrite existing files
        options.copy_inside = true; // copy the *contents* of source_dir into dest_dir
        options.content_only = true; // if true, you'd copy contents without creating source_dir itself

        fs_extra::dir::copy(local_dir_path, dir_path, &options)?;

        Self::new_from_temp_dir(dir)
    }

    pub fn fetch_definition(
        &self,
        name: &str,
        commit: &str,
        file_path: PathBuf,
    ) -> Result<Vec<String>> {
        let target = Target::parse(name)?;
        let matches: Vec<String> = self
            .fetch(&target, commit, file_path)?
            .into_iter()
            .map(|(def, _doc)| def)
            .collect();
        Ok(matches)
    }

    pub fn fetch_documentation(
        &self,
        name: &str,
        commit: &str,
        file_path: PathBuf,
    ) -> Result<Vec<String>> {
        let target = Target::parse(name)?;
        let matches: Vec<String> = self
            .fetch(&target, commit, file_path)?
            .into_iter()
            .map(|(_def, doc)| doc)
            .collect();
        Ok(matches)
    }

    pub fn fetch_lines_of_file(
        &self,
        commit: &str,
        file_path: PathBuf,
        start: usize,
        end: usize,
    ) -> Result<Vec<String>> {
        self.checkout(commit)?;
        let full_path = self.dir.path().join(file_path);
        let file = std::fs::File::open(full_path)?;
        let reader = std::io::BufReader::new(file);
        reader
            .lines()
            .map(|line| line.map_err(CodeError::FileReadError))
            .skip(start)
            .take(end - start + 1)
            .collect::<Result<Vec<_>>>()
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

    fn fetch(
        &self,
        target: &Target,
        commit: &str,
        file_path: PathBuf,
    ) -> Result<Vec<(String, String)>> {
        self.checkout(commit)?;
        let file_path = self.dir.path().join(file_path);
        if !file_path.exists() {
            return Err(CodeError::FileNotFound(file_path));
        }
        for lang in &self.langs {
            if lang.accepts(&file_path) {
                return lang.find_in(target, &file_path);
            }
        }
        Ok(Vec::new())
    }
}

impl Display for Wrapper {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?} on branch {}", self.dir.path(), self.default_branch)
    }
}

#[cfg(test)]
mod test {
    use crate::ts::Target;

    use super::*;

    fn new_mock_wrapper() -> Result<Wrapper> {
        let dir = TempDir::new()?;
        let output = Command::new("bash")
            .arg("./scripts/setup_test_codebase.sh")
            .arg(dir.path())
            .output()?;

        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(CodeError::GitCommandErr(error_message));
        }
        Ok(Wrapper {
            dir,
            default_branch: String::from("master"),
            langs: vec![Lang::go(), Lang::python(), Lang::java()],
        })
    }

    #[test]
    fn checkout() -> Result<()> {
        let w = new_mock_wrapper()?;
        w.checkout("hello")?;
        let main_go = w.dir.path().join("main.go");
        let main_go = std::fs::File::open(main_go)?;
        let main_go = std::io::BufReader::new(main_go);
        let main_go_hello_branch = main_go
            .lines()
            .map(|l| l.map_err(CodeError::FileReadError))
            .collect::<Result<Vec<_>>>()?;

        let lines =
            w.fetch_lines_of_file("hello", PathBuf::from("./main.go"), 0, usize::MAX >> 1)?;
        assert_eq!(lines.len(), main_go_hello_branch.len());
        for (l1, l2) in lines.iter().zip(main_go_hello_branch.iter()) {
            assert_eq!(l1, l2);
        }

        let lines =
            w.fetch_lines_of_file("goodbye", PathBuf::from("./main.go"), 0, usize::MAX >> 1)?;
        assert_ne!(lines.len(), main_go_hello_branch.len());

        Ok(())
    }

    #[test]
    fn fetch() -> Result<()> {
        let w = new_mock_wrapper()?;
        let targets = [
            Target::new_method("Mamad", "SayGoodBye"),
            Target::new_function("greet"),
            Target::new_class("Mamad"),
        ];
        for target in targets.iter() {
            let matches = w.fetch(target, "goodbye", PathBuf::from("./main.go"))?;
            assert!(!matches.is_empty());
            for (def, _doc) in matches {
                assert!(!def.is_empty());
            }
        }

        // check for any documentation
        assert!(targets
            .iter()
            .filter_map(|t| { w.fetch(t, "goodbye", PathBuf::from("./main.go")).ok() })
            .flatten()
            .any(|(_def, doc)| !doc.is_empty()));

        Ok(())
    }
}
