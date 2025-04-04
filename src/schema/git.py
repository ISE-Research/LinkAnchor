from typing import List
from enum import Enum
from pydantic import BaseModel, Field
from git_wrapper import Author, CommitMeta, AuthorQuery, Pagination as wrapperPagination
from anchor.anchor import GitAnchor


class AuthorQueryType(str, Enum):
    EMAIL = "email"
    NAME = "name"


class Pagination(BaseModel):
    """pagination for listing commits"""

    offset: int = Field(..., description="offset starts from 0")
    limit: int = Field(..., description="limit of number of items to return")

    def to_wrapper_pagination(self) -> wrapperPagination:
        return wrapperPagination(offset=self.offset, limit=self.limit)


class ListBranches(BaseModel):
    """listing all branches in a Git repository"""

    def __call__(self, anchor: GitAnchor) -> List[str]:
        return anchor.list_branches()


class CommitsOfBranch(BaseModel):
    """listing all commits in a branch"""

    branch: str = Field(..., description="branch name")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_of_branch(
            self.branch, self.pagination.to_wrapper_pagination()
        )


class AuthorsOfBranch(BaseModel):
    """listing all authors in a branch"""

    branch: str = Field(..., description="branch name")

    def __call__(self, anchor: GitAnchor) -> List[Author]:
        return anchor.authors_of_branch(self.branch)


class CommitsOfAuthor(BaseModel):
    """listing all commits of an author in a branch"""

    branch: str = Field(..., description="branch name")
    query_type: AuthorQueryType = Field(
        ..., description="weather search by name or email"
    )
    query: str = Field(..., description="author's name or email")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        if self.query_type == AuthorQueryType.NAME:
            query = AuthorQuery.name(self.query)
        else:
            query = AuthorQuery.email(self.query)

        return anchor.commits_of_author(
            query, self.branch, self.pagination.to_wrapper_pagination()
        )


class CommitsOnFile(BaseModel):
    """listing all commits on a file in a branch"""

    branch: str = Field(..., description="branch name")
    file_path: str = Field(..., description="file path")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_on_file(
            self.branch, self.file_path, self.pagination.to_wrapper_pagination()
        )


class CommitsBetween(BaseModel):
    """listing all commits between two timestamp in a branch"""

    branch: str = Field(..., description="branch name")
    start_date: str = Field(..., description="start date in 'Y-m-d H:M:S z' format")
    end_date: str = Field(..., description="end date in 'Y-m-d H:M:S z' format")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_between(
            self.branch,
            self.start_date,
            self.end_date,
            self.pagination.to_wrapper_pagination(),
        )

class CommitDiff(BaseModel):
    """changes staged by the given commit"""
    commit_hash: str = Field(..., description="commit hash. could be short or long")

    def __call__(self, anchor: GitAnchor) -> str:
        return anchor.commit_diff(self.commit_hash)
    


TOOLS = [
    ListBranches,
    AuthorsOfBranch,
    CommitsOfAuthor,
    CommitsOfBranch,
    CommitsBetween,
    CommitsOnFile,
    CommitDiff,
]
