from typing import List, Tuple
from enum import Enum
from dateutil.parser import parse as date_parse
from pydantic import BaseModel, Field
from git_wrapper import (
    Author,
    CommitMeta,
    AuthorQuery,
    Pagination as wrapperPagination,
)
from src.anchor.extractor import Extractor


class AuthorQueryType(str, Enum):
    EMAIL = "email"
    NAME = "name"


class Pagination(BaseModel):
    """pagination for listing commits"""

    offset: int = Field(..., description="offset starts from 0")
    limit: int = Field(
        ...,
        description="limit of number of items to return. limit should not be less than 10",
    )

    def to_wrapper_pagination(self) -> wrapperPagination:
        return wrapperPagination(offset=self.offset, limit=self.limit)


class ListCommits(BaseModel):
    """listing all commits in the repo.
    Returns a paginated list of commits as well as the total number of commits
    """

    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, extractor: Extractor) -> Tuple[int, List[CommitMeta]]:
        return extractor.list_commits(self.pagination.to_wrapper_pagination())


class ListAuthors(BaseModel):
    """listing all authors in the repo"""

    def __call__(self, extractor: Extractor) -> List[Author]:
        return extractor.list_authors()


class CommitsOfAuthor(BaseModel):
    """listing all commits of an author in the repo.
    Returns a paginated list of commits as well as the total number of commits
    """

    query_type: AuthorQueryType = Field(
        ..., description="weather search by name or email"
    )
    query: str = Field(..., description="author's name or email")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, extractor: Extractor) -> Tuple[int, List[CommitMeta]]:
        if self.query_type == AuthorQueryType.NAME:
            query = AuthorQuery.Name(self.query)
        else:
            query = AuthorQuery.Email(self.query)

        start_date = extractor.issue_created_at()
        end_date = extractor.issue_closed_at()
        start_date = date_parse(start_date)
        start_str = start_date.strftime("%Y-%m-%d %H:%M:%S %z")
        end_date = date_parse(end_date)
        end_str = end_date.strftime("%Y-%m-%d %H:%M:%S %z")
        return extractor.commits_of(
            query, (start_str, end_str), self.pagination.to_wrapper_pagination()
        )


class CommitsOnFile(BaseModel):
    """listing all commits on a file path.
    Returns a paginated list of commits as well as the total number of commits
    """

    file_path: str = Field(..., description="file path")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, extractor: Extractor) -> Tuple[int, List[CommitMeta]]:
        start_date = extractor.issue_created_at()
        end_date = extractor.issue_closed_at()
        start_date = date_parse(start_date)
        start_str = start_date.strftime("%Y-%m-%d %H:%M:%S %z")
        end_date = date_parse(end_date)
        end_str = end_date.strftime("%Y-%m-%d %H:%M:%S %z")

        return extractor.commits_on_file(
            self.file_path,
            (start_str, end_str),
            self.pagination.to_wrapper_pagination(),
        )


class CommitsBetween(BaseModel):
    """listing all commits between two timestamps.
    Returns a paginated list of commits as well as the total number of commits
    """

    start_date: str = Field(..., description="start date in 'Y-m-d H:M:S z' format")
    end_date: str = Field(..., description="end date in 'Y-m-d H:M:S z' format")
    pagination: Pagination = Field(
        ..., description="pagination from offset to atleast offset + limit"
    )

    def __call__(self, extractor: Extractor) -> Tuple[int, List[CommitMeta]]:
        start = date_parse(self.start_date).strftime("%Y-%m-%d %H:%M:%S %z")
        end = date_parse(self.end_date).strftime("%Y-%m-%d %H:%M:%S %z")
        return extractor.commits_between(
            start, end, self.pagination.to_wrapper_pagination()
        )


class CommitDiff(BaseModel):
    """changes staged by the given commit"""

    commit_hash: str = Field(..., description="commit hash. could be short or long")

    def __call__(self, extractor: Extractor) -> str:
        return extractor.commit_diff(self.commit_hash)


TOOLS = [
    ListAuthors,
    CommitsOfAuthor,
    # ListCommits,
    # CommitsBetween,
    CommitsOnFile,
    CommitDiff,
]
