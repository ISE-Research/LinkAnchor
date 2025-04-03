from typing import List
from enum import Enum
from pydantic import BaseModel
from git_wrapper import Author, CommitMeta, AuthorQuery,Pagination as wrapperPagination
from anchor.anchor import GitAnchor


class AuthorQueryType(str, Enum):
    EMAIL = "email"
    NAME = "name"

class Pagination(BaseModel):
    offset: int = 0
    limit: int = 10

    def to_wrapper_pagination(self) -> wrapperPagination:
        return wrapperPagination(offset=self.offset, limit=self.limit)
        



class ListBranches(BaseModel):
    def __call__(self, anchor: GitAnchor) -> List[str]:
        return anchor.list_branches()


class CommitsOfBranch(BaseModel):
    branch: str
    pagination: Pagination

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_of_branch(self.branch,self.pagination.to_wrapper_pagination())


class AuthorsOfBranch(BaseModel):
    branch: str

    def __call__(self, anchor: GitAnchor) -> List[Author]:
        return anchor.authors_of_branch(self.branch)


class CommitsOfAuthor(BaseModel):
    branch: str
    query_type: AuthorQueryType
    query: str
    pagination: Pagination

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        if self.query_type == AuthorQueryType.NAME:
            query = AuthorQuery.name(self.query)
        else:
            query = AuthorQuery.email(self.query)

        return anchor.commits_of_author(query, self.branch, self.pagination.to_wrapper_pagination())


class CommitsOnFile(BaseModel):
    branch: str
    file_path: str
    pagination: Pagination

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_on_file(self.branch, self.file_path, self.pagination.to_wrapper_pagination())


class CommitsBetween(BaseModel):
    branch: str
    start_date: str
    end_date: str
    pagination: Pagination

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_between(self.branch, self.start_date, self.end_date, self.pagination.to_wrapper_pagination())


TOOLS = [
    CommitsBetween,
    CommitsOnFile,
    CommitsOfAuthor,
    AuthorsOfBranch,
    CommitsOfBranch,
    ListBranches,
]
