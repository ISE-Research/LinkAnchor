from typing import List
from pydantic import BaseModel


class Commit(BaseModel): 
    commit_hash: str 
    message: str

    def __repr__(self):
        return f"Commit(hash={self.commit_hash}, message={self.message})"

class AllCommits(BaseModel):
    branch: str

class CommitAgent:
    def __init__ (self,repo_link: str):
        self.repo_link = repo_link

    def all_commits(self,input: AllCommits) -> List[Commit]:
        # This method should return a list of all commit hashes in the repository.
        # For now, we will return a placeholder list.
        return [ Commit(commit_hash="abc123", message="Fix issue with stop button color"),
                Commit(commit_hash="def456", message="Update documentation for stop button feature"),
                Commit(commit_hash="ghi789",message="Add stop button functionality") ]


class CodebaseAgent:
    def __init__ (self,repo_link: str):
        self.repo_link = repo_link

class IssueAgent:
    def __init__(self, issue_link: str):
        self.issue_link = issue_link

    def issue_title(self) -> str:
        return "users require stop button to be red"


