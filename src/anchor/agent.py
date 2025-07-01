from typing import Any, Callable, List, Tuple
from openai.types.chat import ChatCompletionToolParam as Tool
from openai.types.chat import ChatCompletionMessageParam as Message
from openai.types.chat import ParsedChatCompletion
from openai import NotGiven, NOT_GIVEN
import openai
import logging

from git_wrapper import CommitMeta
from src import prompt
from src.anchor.extractor import Extractor
from src.term import Color
from src import term
from src.schema.control import Control, Finish, Next,GiveUp

# Configure logger for this module
logger = logging.getLogger(__name__)


class Agent:
    """
    Agent class is responsible for communicating with the LLM API.
    It has one public method `find_link` that takes an issue title and a list of tools.
    It returns the commit hash that resolves the issue.
    """

    def __init__(self, api_key: str = ""):
        """Initialize the Agent instance.
        Args:
            api_key (str): OpenAI API key. if not provided, the default OpenAI client will be used.
        """
        if api_key == "":
            self.client = openai.OpenAI()
        else:
            self.client = openai.OpenAI(api_key=api_key)

    def communicate(
        self,
        messages: List[Message],
        tools: List[Tool] | NotGiven = NOT_GIVEN,
    ) -> ParsedChatCompletion:
        """Communicate with the OpenAI API."""

        return self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )

    def communicate_commits(
        self, commits: List[CommitMeta], messages: List[Message], tools: List[Tool]
    ) -> ParsedChatCompletion:
        new_messages: List[Message] = [prompt.show_commits(commits)]
        new_messages.extend(messages)
        return self.communicate(new_messages, tools)

    def find_link(
        self, issue_title: str, tools: List[Tool], extractor: Extractor
    ) -> Tuple[str, int]:
        """Find the commit(s) that resolve(s) the issue.
        Args:
            issue_title (str): The title of the issue.
            tools (List[Tool]): List of tools to use.
            extractor (Extractor): Extractor instance to extract information for the LLM.
        """

        total_tokens = 0

        messages = [
            prompt.problem_explanation(),
            prompt.user_initial_prompt(issue_title),
        ]
        commits_iterator = extractor.commit_iterator()
        current_commits = next(commits_iterator)

        for _ in range(prompt.MAX_ITERATIONS):
            completion = self.communicate_commits(current_commits, messages, tools)
            if completion.usage:
                total_tokens += completion.usage.total_tokens or 0
            response = completion.choices[0].message
            logger.info(f"Response: {response.content}")

            term.wait()
            term.clear()
            term.log(Color.WHITE, f"commits #{len(current_commits)}")
            term.log(Color.WHITE, current_commits)
            term.log(Color.YELLOW, "Response:")
            term.log(Color.YELLOW, response.content)

            messages.append(response)

            # check if LLM found the link
            # no function call means that LLM found the link
            if response.tool_calls is None or len(response.tool_calls) == 0:
                logger.info("LLM didn't call any function")
                term.log(Color.GREEN, "LLM didn't call any function")
                messages.append(prompt.should_call_function())
                continue

            logger.info(f"{len(response.tool_calls)} tool called")
            term.log(Color.GREEN, f"{len(response.tool_calls)} tool called")
            for tool_call in response.tool_calls:
                functionn = tool_call.function.parsed_arguments
                if functionn is None:
                    logger.error(f"message that caused error: {messages[-1]}")
                    raise ValueError("Function not found in tool call")

                # just to saticfy type checking
                function: Callable[[Extractor], Any] = functionn  # type: ignore
                logger.info(f"LLM calling: {function.__repr__()}")
                term.log(Color.GREEN, f"LLM calling: {function.__repr__()}")

                result=""
                if isinstance(function, Control):
                    if isinstance(function, Finish) or isinstance(function, GiveUp):
                        commit_hash = function(extractor)
                        return (commit_hash, total_tokens)
                    elif isinstance(function, Next):
                        try:
                            current_commits = next(commits_iterator)
                            result = function(extractor)
                        except StopIteration:
                            term.log(Color.YELLOW, "No more commits to show")
                            result = "iterator exhausted"
                else:
                    try:
                        result = function(extractor)
                    except Exception as e:
                        result = f"encountered the following error: {e}"
                logger.debug(f"Call result: {result.__repr__()}")
                term.log(Color.BLUE, "Call result:")
                term.log(Color.BLUE, result)
                messages.append(prompt.function_call_result(tool_call, result))

        return ("FFFFFFFFFFFFF", total_tokens)
