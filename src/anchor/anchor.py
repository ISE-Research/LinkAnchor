from typing import List
from pydantic import BaseModel
import openai
from .agent import Agent
from .extractor import Extractor
import logging
from term import Color
import term

# Configure logger for this module
logger = logging.getLogger(__name__)


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

        logger.info("Initializing OpenAI client...")
        term.log(Color.MAGENTA, "Initializing OpenAI client...")
        self.agent = Agent(api_key)
        logger.info("sucessfully connected to OpenAI")
        term.log(Color.GREEN, "sucessfully connected to OpenAI")

        logger.info("Initializing data Extractor...")
        term.log(Color.MAGENTA, "INitializing data Extractor...")
        self.extractor = Extractor(issue_link, git_repo_link)
        logger.info("data source setup completed successfully")
        term.log(Color.GREEN, "data source setup completed successfully")

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
        issue_title = self.extractor.issue_wrapper.issue_title()
        return self.agent.find_link(issue_title, self.tools, self.extractor)
