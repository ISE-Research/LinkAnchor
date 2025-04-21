from src.issue_wrapper.wrapper import Wrapper
from src.issue_wrapper.jira import JiraIssueWrapper
from src.issue_wrapper.github import GitHubIssueWrapper


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
