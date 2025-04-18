from .wrapper import Wrapper
from .jira import JiraIssueWrapper
from .github import GitHubIssueWrapper


def wrapper_for(url: str) -> Wrapper:
    """
    creates a new Wrapper based on the given url
    """
    if "jira" in url.lower():
        return JiraIssueWrapper(url)
    elif "github.com" in url.lower():
        return GitHubIssueWrapper(url)
    else:
        raise ValueError("Unsupported issue URL format.")
