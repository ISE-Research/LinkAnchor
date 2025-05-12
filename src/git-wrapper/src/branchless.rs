use itertools::Itertools;
use std::fmt::Display;
use std::path::PathBuf;

use crate::wrapper::PaginationExt;
use crate::wrapper::TimePeriodExt;
use crate::wrapper::{Author, AuthorQuery, CommitMeta, Pagination, Wrapper};
use crate::Result;
use pyo3::{pyclass, pymethods};

const DATETIME_FORMAT: &str = "%Y-%m-%d %H:%M:%S %z";

#[pyclass(str)]
pub struct Branchless {
    wrapper: Wrapper,
    commits: Vec<CommitMeta>,
}
impl Display for Branchless {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Branchless {{ {} }}", self.wrapper)
    }
}

impl Branchless {
    fn commits_on_all_branchs(wrapper: &Wrapper) -> Result<Vec<CommitMeta>> {
        wrapper
            .list_branches()
            .iter()
            .map(|branch| wrapper.commits_of_branch(branch, Pagination::all()))
            .try_fold(Vec::new(), |acc, commits| {
                Ok(acc
                    .into_iter()
                    .merge(commits?.into_iter().rev())
                    .dedup()
                    .collect())
            })
            .map(|commits| commits.into_iter().rev().collect())
    }
}

#[pymethods]
impl Branchless {
    #[new]
    pub fn new(repo_url: &str) -> Result<Self> {
        let wrapper = Wrapper::new(repo_url)?;
        let commits = Self::commits_on_all_branchs(&wrapper)?;

        Ok(Branchless { wrapper, commits })
    }

    #[staticmethod]
    pub fn from_local(local_dir_path: PathBuf) -> Result<Self> {
        let wrapper = Wrapper::from_local(local_dir_path)?;
        let commits = Self::commits_on_all_branchs(&wrapper)?;
        Ok(Branchless { wrapper, commits })
    }

    pub fn default_branch(&self) -> &str {
        self.wrapper.default_branch()
    }

    pub fn list_branches(&self) -> Vec<String> {
        self.wrapper.list_branches()
    }

    pub fn list_authors(&self) -> Result<Vec<Author>> {
        self.list_branches()
            .iter()
            .map(|branch| self.wrapper.authors_of_branch(branch))
            .try_fold(Vec::new(), |mut acc, authors| {
                acc.extend(authors?);
                Ok(acc)
            })
    }

    pub fn list_commits(&self, pagination: Pagination) -> Vec<CommitMeta> {
        self.commits
            .iter()
            .with_pagination(pagination)
            .cloned()
            .collect()
    }

    pub fn commit_diff(&self, commit_hash: String) -> Result<String> {
        self.wrapper.commit_diff(commit_hash)
    }

    pub fn commit_metadata(&self, commit_hash: &str) -> Result<CommitMeta> {
        self.wrapper.commit_metadata(commit_hash)
    }

    pub fn commits_of(
        &self,
        author_query: AuthorQuery,
        interval: (String, String),
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let (from, to) = interval;
        let from = chrono::DateTime::parse_from_str(&from, DATETIME_FORMAT)?;
        let to = chrono::DateTime::parse_from_str(&to, DATETIME_FORMAT)?;

        Ok(self
            .commits
            .iter()
            .within_period(from, to)
            .filter(|c| author_query.matches(c))
            .with_pagination(pagination)
            .cloned()
            .collect())
    }

    pub fn commits_between(
        &self,
        from: &str,
        to: &str,
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let from = chrono::DateTime::parse_from_str(from, DATETIME_FORMAT)?;
        let to = chrono::DateTime::parse_from_str(to, DATETIME_FORMAT)?;
        Ok(self
            .commits
            .iter()
            .within_period(from, to)
            .with_pagination(pagination)
            .cloned()
            .collect())
    }

    pub fn ancestral_distance(&self, from_commit: &str, to_commit: &str) -> Result<usize> {
        self.wrapper.ancestral_distance(from_commit, to_commit)
    }

    pub fn has_commit(&self, commit_hash: &str) -> bool {
        self.commits.iter().any(|c| c.hash == commit_hash)
    }

    pub fn commits_on_file(
        &self,
        file_path: &str,
        interval: (String, String),
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let commits: Vec<CommitMeta> = self
            .wrapper
            .list_branches()
            .iter()
            .map(|branch| {
                self.wrapper
                    .commits_on_file(file_path, branch, Pagination::all())
            })
            .try_fold(Vec::new(), |acc, commits| {
                Result::<Vec<CommitMeta>>::Ok(
                    acc.into_iter()
                        .merge(commits?.into_iter().rev())
                        .dedup()
                        .collect(),
                )
            })?;

        let (from, to) = interval;
        let from = chrono::DateTime::parse_from_str(&from, DATETIME_FORMAT)?;
        let to = chrono::DateTime::parse_from_str(&to, DATETIME_FORMAT)?;

        Ok(commits
            .into_iter()
            .rev()
            .within_period(from, to)
            .with_pagination(pagination)
            .collect())
    }
}
