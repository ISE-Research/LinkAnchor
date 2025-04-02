use super::{GitError, Result};
use chrono::{DateTime, FixedOffset};
use std::{ffi::OsStr, process::Command};
use temp_dir::TempDir;

const COMMIT_SEPARATOR_GIT: &str = "%x1e";
const COMMIT_SEPARATOR_CHAR: char = '\x1e';
const ATTRIBUTE_SEPARATOR_GIT: &str = "%x1d";
const ATTRIBUTE_SEPARATOR_CHAR: char = '\x1d';
const DATETIME_FORMAT: &str = "%Y-%m-%d %H:%M:%S %z";

pub struct Wrapper {
    dir: TempDir,
    default_branch: String,
}

impl Wrapper {
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
            return Err(GitError::GitCommandErr(error_message));
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
                Err(GitError::GitCommandErr(error_message))
            }
            true => {
                let default_branch = String::from_utf8_lossy(&output.stdout)
                    .trim_end_matches("\n")
                    .to_string();
                Ok(Self {
                    dir,
                    default_branch,
                })
            }
        }
    }
}

impl Wrapper {
    pub fn list_branchs(&self) -> Result<Vec<String>> {
        // List all remote branches
        let output = Command::new("git")
            .arg("branch")
            .arg("-r")
            .current_dir(self.dir.path())
            .output()?;

        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(GitError::GitCommandErr(error_message));
        }

        let branches_output = String::from_utf8_lossy(&output.stdout);
        let branches_output = branches_output.trim_end_matches("\n");

        let branches: Vec<String> = branches_output
            .lines()
            .filter(|line| !line.is_empty())
            .filter(|line| !line.contains("HEAD"))
            // lines might be in the format of "origin/HEAD -> origin/master"
            .map(|line| line.split("->").next().unwrap_or(line).trim())
            .map(|line| line.to_string())
            .collect();

        Ok(branches)
    }

    pub fn authors_of_branch(&self, branch: &str) -> Result<Vec<Author>> {
        let authors: Vec<Author> = self
            .commits_of_branch(branch)?
            .into_iter()
            .map(|commit| commit.author)
            .collect();
        Ok(authors)
    }

    pub fn commits_of_branch(&self, branch: &str) -> Result<Vec<CommitMeta>> {
        if branch == self.default_branch {
            self.commits_from_git_log(vec![&self.default_branch])
        } else {
            let output = Command::new("git")
                .arg("merge-base")
                .arg(&self.default_branch)
                .arg(branch)
                .current_dir(self.dir.path())
                .output()?;

            // Get the commit hash of the first commit in the branch
            if !output.status.success() {
                let error_message = String::from_utf8_lossy(&output.stderr).to_string();
                return Err(GitError::GitCommandErr(error_message));
            }

            let first_commit_hash = String::from_utf8_lossy(&output.stdout);
            let first_commit_hash = first_commit_hash.trim_end_matches("\n");

            self.commits_from_git_log(vec![format!("{first_commit_hash}..{branch}")])
        }
    }

    pub fn get_commit_diff(&self, commit_hash: String) -> Result<String> {
        let output = Command::new("git")
            .arg("diff")
            .arg(format!("{commit_hash}^ {commit_hash}"))
            .current_dir(self.dir.path())
            .output()?;

        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(GitError::GitCommandErr(error_message));
        }

        let diff = String::from_utf8_lossy(&output.stdout)
            .trim_end_matches("\n")
            .to_string();
        Ok(diff)
    }

    pub fn get_commit_metadata(&self, commit_hash: &str) -> Result<CommitMeta> {
        self.commits_from_git_log(vec!["-1", commit_hash])?
            .into_iter()
            .next()
            .ok_or(GitError::MalFormedData(commit_hash.to_string()))
    }

    pub fn get_commits_of(&self, author_query: AuthorQuery) -> Result<Vec<CommitMeta>> {
        match author_query {
            AuthorQuery::Name(query) => self.commits_from_git_log(vec!["--author", &query]),
            AuthorQuery::Email(query) => self.commits_from_git_log(vec!["--author", &query]),
        }
    }

    pub fn get_commits_between(
        &self,
        from: DateTime<FixedOffset>,
        to: DateTime<FixedOffset>,
    ) -> Result<Vec<CommitMeta>> {
        self.commits_from_git_log(vec![
            format!("--since={}", from.format(DATETIME_FORMAT).to_string()),
            format!("--until={}", to.format(DATETIME_FORMAT).to_string()),
        ])
    }

    pub fn get_commits_on_file(&self, file_path: &str) -> Result<Vec<CommitMeta>> {
        self.commits_from_git_log(vec!["--", file_path])
    }
}

impl Wrapper {
    fn commits_from_git_log<S: AsRef<OsStr>>(
        &self,
        git_log_extra_args: Vec<S>,
    ) -> Result<Vec<CommitMeta>> {
        let output = git_log_formatted()
            .args(git_log_extra_args)
            .current_dir(self.dir.path())
            .output()?;

        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(GitError::GitCommandErr(error_message));
        }

        let log = String::from_utf8_lossy(&output.stdout);
        let log = log.trim_end_matches("\n");

        // list all commits between the first commit and the branch
        // using the format: %H %an %ae %ad %B to get the hash, author name, author email, date, and message
        // in a parsable format.
        // The separator between each commit is COMMIT_SEPARATOR_GIT
        // The separator between each attribute is ATTRIBUTE_SEPARATOR_GIT
        let commits: Vec<CommitMeta> = log
            .split(COMMIT_SEPARATOR_CHAR)
            .filter(|line| !line.is_empty())
            .map(CommitMeta::parse)
            .collect::<Result<_, _>>()?;
        Ok(commits)
    }
}

#[derive(Debug, Clone)]
pub struct Author {
    pub name: String,
    pub email: String,
}

#[derive(Debug, Clone)]
pub struct CommitMeta {
    pub hash: String,
    pub author: Author,
    pub date: DateTime<chrono::FixedOffset>,
    pub message: String,
}

impl CommitMeta {
    fn parse(log: &str) -> Result<Self> {
        let attributes: Vec<&str> = log.split(ATTRIBUTE_SEPARATOR_CHAR).collect();
        if attributes.len() != 5 {
            return Err(GitError::MalFormedData(format!(
                "faled to parse commit metadata: [{log}]"
            )));
        }
        let hash = attributes[0].to_string();
        let author = Author {
            name: attributes[1].to_string(),
            email: attributes[2].to_string(),
        };

        let date = attributes[3];
        // trim for extra quotes
        let date = date.trim_matches('\'');
        let date: DateTime<chrono::FixedOffset> = DateTime::parse_from_str(date, DATETIME_FORMAT)?;

        let message = attributes[4].trim().to_string();
        let commit = CommitMeta {
            hash,
            author,
            date,
            message,
        };
        Ok(commit)
    }
}

fn git_log_formatted() -> Command {
    let mut cmd = Command::new("git");
    cmd.arg("log")
        .arg(format!("--date=format:'{DATETIME_FORMAT}'"))
        .arg(format!(
            "--pretty={}{COMMIT_SEPARATOR_GIT}",
            ["format:%H", "%an", "%ae", "%ad", "%B"].join(ATTRIBUTE_SEPARATOR_GIT)
        ));
    cmd
}

pub enum AuthorQuery {
    Name(String),
    Email(String),
}

#[cfg(test)]
mod test {
    use std::process::Command;

    use temp_dir::TempDir;

    use super::Wrapper;
    use crate::{GitError, Result};
    const REPO_URL: &str = "git@github.com:ArshiAAkhavan/test.git";

    fn new_mock_wrapper() -> Result<Wrapper> {
        let dir = TempDir::new()?;
        let output = Command::new("bash")
            .arg("./setup_test_repo.sh")
            .arg(dir.path())
            .output()?;

        if !output.status.success() {
            let error_message = String::from_utf8_lossy(&output.stderr).to_string();
            return Err(GitError::GitCommandErr(error_message));
        }
        Ok(Wrapper {
            dir,
            default_branch: String::from("master"),
        })
    }

    #[test]
    fn list_branches() -> Result<()> {
        let w = Wrapper::new(REPO_URL)?;
        let branches = w.list_branchs()?;
        assert!(branches.contains(&"origin/b1".into()));
        assert!(branches.contains(&"origin/master".into()));
        Ok(())
    }
    #[test]
    fn list_commits() -> Result<()> {
        let w = new_mock_wrapper()?;

        let commits = w.commits_of_branch("master")?;
        assert_eq!(commits.len(), 3);
        let commit_messages = ["fifth commit", "second commit", "first commit"];
        assert_eq!(
            commits.iter().map(|c| &c.message).collect::<Vec<_>>(),
            commit_messages
        );

        let commits = w.commits_of_branch("branch1")?;
        assert_eq!(commits.len(), 2);
        let commit_messages =  ["fourth commit", "third commit"];
        assert_eq!(
            commits.iter().map(|c| &c.message).collect::<Vec<_>>(),
            commit_messages
        );

        Ok(())
    }
}
