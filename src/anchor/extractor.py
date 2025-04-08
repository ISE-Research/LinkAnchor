from typing import Any
from git_wrapper import Wrapper as GitWrapper

class Extractor:
    def __init__(self, issue_link: str, git_repo_link: str):
        """Initialize the Data Extractor instance.
        Args:
            issue_link (str): The link to the issue in GitHub.
            git_repo_link (str): The link to the git repository.
        """
        self.git_wrapper = GitWrapper(git_repo_link)
        self.issue_wrapper = DummyIssueWrapper(issue_link)
        self.code_wrapper = DummyCodeWrapper()

    def __getattr__(self, name: str) -> Any:
        """Deligate to underlying wrappers if avilable."""
        for wrapper in [self.git_wrapper, self.issue_wrapper, self.code_wrapper]:
            if hasattr(wrapper, name):
                return getattr(wrapper, name)


class DummyIssueWrapper:
    def __init__(self, issue_link: str):
        self.issue_link = issue_link

    def get_issue_title(self) -> str:
        return "'pkgutil.get_loader' is removed from Python 3.14"

class DummyCodeWrapper:
    def __init__(self):
        pass
