from typing import Any
from git_wrapper import Wrapper as GitWrapper
from code_wrapper import Wrapper as CodeWrapper
from issue_wrapper import GitHubIssueWrapper as IssueWrapper


class Extractor:
    def __init__(self, issue_url: str, git_repo_url: str):
        """Initialize the Data Extractor instance.
        Args:
            issue_link (str): The link to the issue in GitHub.
            git_repo_link (str): The link to the git repository.
        """
        self.git_wrapper = GitWrapper(git_repo_url)
        self.issue_wrapper = IssueWrapper(issue_url)
        self.code_wrapper = CodeWrapper(git_repo_url)

    def __getattr__(self, name: str) -> Any:
        """Deligate to underlying wrappers if avilable."""
        for wrapper in [self.git_wrapper, self.issue_wrapper, self.code_wrapper]:
            if hasattr(wrapper, name):
                return getattr(wrapper, name)
