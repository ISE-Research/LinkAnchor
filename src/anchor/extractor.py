from typing import Any
from enum import Enum

from git_wrapper import Wrapper as GitWrapper
from code_wrapper import Wrapper as CodeWrapper

from src import issue_wrapper

class GitSourceType(Enum):
    """Enum for Git source types."""
    REMOTE = "remote"
    LOCAL = "local"


class Extractor:
    def __init__(self, issue_url: str, git_repo_source: str, source_type: GitSourceType = GitSourceType.REMOTE):
        """Initialize the Data Extractor instance.
        Args:
            issue_link (str): The link to the issue in GitHub.
            git_repo_source (str): The link to the git repository.
            source_type (GitSourceType): The type of git source (remote or local). 
            when using local, the git_repo_source should be a path to the local directory.
            when using remote, the git_repo_source should be a url to the remote repository.
        """
        self.issue_wrapper = issue_wrapper.wrapper_for(issue_url)
        if source_type == GitSourceType.LOCAL:
            self.git_wrapper = GitWrapper.from_local(git_repo_source)
            self.code_wrapper = CodeWrapper.from_local(git_repo_source)
        elif source_type == GitSourceType.REMOTE:
            self.git_wrapper = GitWrapper(git_repo_source)
            self.code_wrapper = CodeWrapper(git_repo_source)

    def __getattr__(self, name: str) -> Any:
        """Deligate to underlying wrappers if avilable."""
        for wrapper in [self.git_wrapper, self.issue_wrapper, self.code_wrapper]:
            if hasattr(wrapper, name):
                return getattr(wrapper, name)
