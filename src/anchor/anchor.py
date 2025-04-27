from typing import List, Tuple
from pydantic import BaseModel
import openai
import logging
from src.anchor.agent import Agent
from src.anchor.extractor import Extractor
from src.anchor.extractor import GitSourceType
from src.anchor.metrics import Metrics
from src.term import Color
from src import term

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

    def __init__(self, extractor: Extractor, api_key: str = ""):
        """Initialize the GitAnchor instance.
        Args:
            api_key (str): OpenAI API key. if not provided, the default OpenAI client will be used.
            extractor (Extractor): Extractor instance for extracting data from the issue.
        """
        logger.info("Initializing OpenAI client...")
        term.log(Color.MAGENTA, "Initializing OpenAI client...")
        self.agent = Agent(api_key)
        logger.info("sucessfully connected to OpenAI")
        term.log(Color.GREEN, "sucessfully connected to OpenAI")

        self.extractor = extractor
        self.tools = []

    @classmethod
    def from_urls(
        cls,
        issue_url: str,
        git_repo_source: str,
        source_type: GitSourceType = GitSourceType.REMOTE,
        api_key: str = "",
        metrics: Metrics|None=None,

    ):
        """Initialize the GitAnchor instance.
        Args:
            api_key (str): OpenAI API key. if not provided, the default OpenAI client will be used.
            issue_url (str): The link to the issue in GitHub.
            git_repo_source (str): the source git repository.
            source_type (GitSourceType): The type of git source (remote or local).
            when using local, the git_repo_source should be a path to the local directory.
            when using remote, the git_repo_source should be a url to the remote repository.
        """
        logger.info("Initializing data Extractor...")
        term.log(Color.MAGENTA, "Initializing data Extractor...")
        extractor = Extractor.new_for_issue(
            issue_url, git_repo_source, source_type, metrics
        )
        logger.info("data source setup completed successfully")
        term.log(Color.GREEN, "data source setup completed successfully")

        return cls(extractor, api_key)

    def register_tools(self, tools: List[type[BaseModel]]):
        """Register tools for the agent.
        Args:
            tools (List[type[BaseModel]]): List of tool classes to register.
            toosl should be pydantic models that are used to define the input
            and output of the function.
            they also should implement that takes Anchor as the only argument."""
        self.tools.extend([openai.pydantic_function_tool(tool) for tool in tools])

    def find_link(self) -> Tuple[str, int]:
        """Find the commit(s) that resolve(s) the issue."""
        issue_title = self.extractor.issue_wrapper.issue_title()
        return self.agent.find_link(issue_title, self.tools, self.extractor)
