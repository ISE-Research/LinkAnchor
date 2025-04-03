from typing import List, Any
from pydantic import BaseModel
import openai
from git_wrapper import Wrapper as GitWrapper
from anchor.agent import Agent


class GitAnchor:
    """GitAnchor is a LLM-base agent for linking GitHub issues to the commits that resolve them.

    Attributes:
        client : OpenAI client instance.
        commit_agent : CommitAgent instance for accessing commit history.
        codebase_agent : CodebaseAgent instance for accessing source code.
        issue_agent : IssueAgent instance for accessing issue data.
    """

    def __init__(self, issue_link: str, git_repo_link: str, api_key: str = ""):
        """Initialize the GitAnchor instance.
        Args:
            api_key (str): OpenAI API key. if not provided, the default OpenAI client will be used.
            issue_link (str): The link to the issue in GitHub.
            git_repo_link (str): The link to the git repository.
        """
        self.agent = Agent(api_key)
        self.git_wrapper = GitWrapper(git_repo_link)
        self.issue_wrapper = DummyIssueWrapper(issue_link)
        self.code_wrapper = DummyCodeWrapper()

        self.tools = []

    def register_tools(self, tools: List[type[BaseModel]]):
        """Register tools for the agent.
        Args:
            tools (List[type[BaseModel]]): List of tool classes to register.
            toosl should be pydantic models that are used to define the input
            and output of the function.
            they also should implement that takes Anchor as the only argument."""
        self.tools.extend([openai.pydantic_function_tool(tool) for tool in tools])

    def find_link(self) -> str:
        """Find the commit(s) that resolve(s) the issue."""
        issue_title = self.issue_wrapper.get_issue_title()
        return self.agent.find_link(issue_title, self.tools, lambda f: f(self))

    def __getattr__(self, name: str) -> Any:
        """Deligate to wrappers if avilable."""
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
