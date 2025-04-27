from typing import Any
from enum import Enum

from git_wrapper import Wrapper as GitWrapper
from code_wrapper import Wrapper as CodeWrapper

from src import issue_wrapper
from src.issue_wrapper import Wrapper as IssueWrapper

class GitSourceType(Enum):
    """Enum for Git source types."""
    REMOTE = "remote"
    LOCAL = "local"


class Extractor:
    def __init__(self,issue_wrapper: IssueWrapper, git_wrapper: GitWrapper, code_wrapper: CodeWrapper):
        """Initialize the Extractor instance.
        Args:
            issue_wrapper (IssueWrapper): The issue wrapper instance.
            git_wrapper (GitWrapper): The git wrapper instance.
            code_wrapper (CodeWrapper): The code wrapper instance.
        """
        self.issue_wrapper = issue_wrapper
        self.git_wrapper = git_wrapper
        self.code_wrapper = code_wrapper

    @classmethod
    def new_for_issue(cls,issue_url: str, git_repo_source: str, source_type: GitSourceType = GitSourceType.REMOTE):
        """Initialize the Data Extractor instance for the given issue, git repo pair.
        Args:
            issue_link (str): The link to the issue in GitHub.
            git_repo_source (str): The link to the git repository.
            source_type (GitSourceType): The type of git source (remote or local). 
            when using local, the git_repo_source should be a path to the local directory.
            when using remote, the git_repo_source should be a url to the remote repository.
        """
        if source_type == GitSourceType.LOCAL:
            git_wrapper = GitWrapper.from_local(git_repo_source)
            code_wrapper = CodeWrapper.from_local(git_repo_source)
        elif source_type == GitSourceType.REMOTE:
            git_wrapper = GitWrapper(git_repo_source)
            code_wrapper = CodeWrapper(git_repo_source)

        return cls(issue_wrapper.wrapper_for(issue_url), git_wrapper, code_wrapper)
    
    @classmethod
    def new_for_repo(cls, git_repo_source: str, source_type: GitSourceType = GitSourceType.REMOTE):
        """Initialize the Data Extractor instance for the given issue, git repo.
        Args:
            issue_link (str): The link to the issue in GitHub.
            git_repo_source (str): The link to the git repository.
            source_type (GitSourceType): The type of git source (remote or local). 
            when using local, the git_repo_source should be a path to the local directory.
            when using remote, the git_repo_source should be a url to the remote repository.
        """
        if source_type == GitSourceType.LOCAL:
            git_wrapper = GitWrapper.from_local(git_repo_source)
            code_wrapper = CodeWrapper.from_local(git_repo_source)
        elif source_type == GitSourceType.REMOTE:
            git_wrapper = GitWrapper(git_repo_source)
            code_wrapper = CodeWrapper(git_repo_source)

        return cls(None, git_wrapper, code_wrapper)

    def __getattr__(self, name: str) -> Any:
        """Deligate to underlying wrappers if avilable."""
        for wrapper in [self.git_wrapper, self.issue_wrapper, self.code_wrapper]:
            if hasattr(wrapper, name):
                return getattr(wrapper, name)
