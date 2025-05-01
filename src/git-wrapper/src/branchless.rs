use itertools::Itertools;
use std::fmt::Display;
use std::path::PathBuf;

use crate::wrapper::PaginationExt;
use crate::wrapper::{Author, AuthorQuery, CommitMeta, Pagination, Wrapper};
use crate::Result;
use pyo3::{pyclass, pymethods};

#[pyclass(str)]
pub struct Branchless {
    wrapper: Wrapper,
}
impl Display for Branchless {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Branchless {{ {} }}", self.wrapper)
    }
}

impl Branchless {
    fn commits_on_all_branchs<F>(&self, commits_retriever: F) -> Result<Vec<CommitMeta>>
    where
        F: Fn(&str) -> Result<Vec<CommitMeta>>,
    {
        self.list_branches()
            .iter()
            .map(|branch| commits_retriever(branch))
            .try_fold(Vec::new(), |acc, commits| {
                Ok(acc.into_iter().merge(commits?.into_iter().rev()).collect())
            })
            .map(|commits| commits.into_iter().rev().collect())
    }
}

#[pymethods]
impl Branchless {
    #[new]
    pub fn new(repo_url: &str) -> Result<Self> {
        let wrapper = Wrapper::new(repo_url)?;
        Ok(Branchless { wrapper })
    }

    #[staticmethod]
    pub fn from_local(local_dir_path: PathBuf) -> Result<Self> {
        let wrapper = Wrapper::from_local(local_dir_path)?;
        Ok(Branchless { wrapper })
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

    pub fn list_commits(&self, pagination: Pagination) -> Result<Vec<CommitMeta>> {
        let res = self.commits_on_all_branchs(|branch| {
            self.wrapper.commits_of_branch(branch, Pagination::all())
        });
        res.map(|commits| commits.with_pagination(pagination).collect())
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
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let res = self.commits_on_all_branchs(|branch| {
            self.wrapper
                .commits_of(author_query.clone(), branch, Pagination::all())
        });
        res.map(|commits| commits.with_pagination(pagination).collect())
    }

    pub fn commits_between(
        &self,
        from: &str,
        to: &str,
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let res = self.commits_on_all_branchs(|branch| {
            self.wrapper
                .commits_between(branch, from, to, Pagination::all())
        });
        res.map(|commits| commits.with_pagination(pagination).collect())
    }

    pub fn ancestral_distance(&self, from_commit: &str, to_commit: &str) -> Result<usize> {
        self.wrapper.ancestral_distance(from_commit, to_commit)
    }
    pub fn commits_on_file(
        &self,
        file_path: &str,
        pagination: Pagination,
    ) -> Result<Vec<CommitMeta>> {
        let res = self.commits_on_all_branchs(|branch| {
            self.wrapper
                .commits_on_file(file_path, branch, Pagination::all())
        });
        res.map(|commits| commits.with_pagination(pagination).collect())
    }
}
