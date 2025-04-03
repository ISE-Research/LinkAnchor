from typing import List
from enum import Enum
from pydantic import BaseModel
from git_wrapper import Author, CommitMeta, AuthorQuery
from anchor.anchor import GitAnchor


class AuthorQueryType(str, Enum):
    EMAIL = "email"
    NAME = "name"


class ListBranches(BaseModel):
    def __call__(self, anchor: GitAnchor) -> List[str]:
        return anchor.list_branches()


class CommitsOfBranch(BaseModel):
    branch: str

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_of_branch(self.branch)


class AuthorsOfBranch(BaseModel):
    branch: str

    def __call__(self, anchor: GitAnchor) -> List[Author]:
        return anchor.authors_of_branch(self.branch)


class CommitsOfAuthor(BaseModel):
    branch: str
    query_type: AuthorQueryType
    query: str

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        if self.query_type == AuthorQueryType.NAME:
            query = AuthorQuery.name(self.query)
        else:
            query = AuthorQuery.email(self.query)

        return anchor.commits_of_author(query, self.branch)


class CommitsOnFile(BaseModel):
    branch: str
    file_path: str

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_on_file(self.branch, self.file_path)


class CommitsBetween(BaseModel):
    branch: str
    start_date: str
    end_date: str

    def __call__(self, anchor: GitAnchor) -> List[CommitMeta]:
        return anchor.commits_between(self.branch, self.start_date, self.end_date)


TOOLS = [
    CommitsBetween,
    CommitsOnFile,
    CommitsOfAuthor,
    AuthorsOfBranch,
    CommitsOfBranch,
    ListBranches,
]
