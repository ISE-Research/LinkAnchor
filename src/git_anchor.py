import openai
from tools import CommitAgent, CodebaseAgent, IssueAgent
import tools
from typing import Any


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
        if api_key == "":
            self.client = openai.OpenAI()
        else:
            self.client = openai.OpenAI(api_key=api_key)
        self.commit_agent = CommitAgent(git_repo_link)
        self.codebase_agent = CodebaseAgent(git_repo_link)
        self.issue_agent = IssueAgent(issue_link)

    def find_link(self) -> str:
        """Find the commit(s) that resolve(s) the issue."""

        issue_title = self.issue_agent.issue_title()

        messages = [
            {
                "role": "system",
                "content": """You are a bot in a issue tracking system that is monitoring a project. Your task is to find the commit that resolved a closed issue in an issue tracking system.
                    you are given the title of the issue as the starting point by the user. 
                    I have provided you a set of functions that grants you access to the source codes in the code base, commit history of the git repo, and the data that is available in the issue (issue description and discussions threads). you can use them to retrieve more data abouts commits and issue.
                    when you are sure that you found the commit that resolved the issue, you can return the commit hash to the user.
                    """,
            },
            {
                "role": "user",
                "content": f"Find the commit that resolves the issue with the title: {issue_title}",
            },
        ]

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            tools=[openai.pydantic_function_tool(tools.AllCommits)],
        )

        x = completion.choices[0].message.content
        while True:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                tools=[openai.pydantic_function_tool(tools.AllCommits)],
            )
            if completion.choices[0].message.content not in ["",None]:
                break
            tool_call = (completion.choices[0].message.tool_calls or [])[0]
            print(tool_call.function)

            assert isinstance(tool_call.function.parsed_arguments, tools.AllCommits)
            result = self.call(tool_call.function.parsed_arguments)
            messages.append(
                completion.choices[0].message
            )  # append model's function call message
            messages.append(
                {  # append result message
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )
        return completion.choices[0].message.content

    def call(self,arg) -> Any:
        return self.commit_agent.all_commits("main")
