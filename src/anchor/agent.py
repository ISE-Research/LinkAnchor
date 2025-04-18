from typing import Any, Callable, List
from openai.types.chat import ChatCompletionToolParam as Tool
from openai.types.chat import ChatCompletionMessageParam as Message
from openai.types.chat import ParsedChatCompletion
from openai import NotGiven, NOT_GIVEN
import openai
import message
import logging

from .extractor import Extractor

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
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )

    def find_link(
        self, issue_title: str, tools: List[Tool], extractor: Extractor
    ) -> str:
        """Find the commit(s) that resolve(s) the issue.
        Args:
            issue_title (str): The title of the issue.
            tools (List[Tool]): List of tools to use.
            extractor (Extractor): Extractor instance to extract information for the LLM.
        """

        messages = [
            message.problem_explanation(),
            message.user_initial_prompt(issue_title),
        ]

        while True:
            completion = self.communicate(messages, tools)
            response = completion.choices[0].message
            logger.info(f"Response: {response.content}")

            # check if LLM found the link
            # no function call means that LLM found the link
            if response.tool_calls is None or len(response.tool_calls) == 0:
                content = response.content or ""
                commit_hash = message.extract_commit_hash(content)
                return commit_hash or ""

            logger.info(f"{len(response.tool_calls)} tool called")
            messages.append(response)
            for tool_call in response.tool_calls:
                functionn = tool_call.function.parsed_arguments
                if functionn is None:
                    logger.error(f"message that caused error: {messages[-1]}")
                    raise ValueError("Function not found in tool call")

                # just to saticfy type checking
                function: Callable[[Extractor], Any] = functionn  # type: ignore
                logger.info(f"LLM calling: {function.__repr__()}")

                result = function(extractor)
                logger.info(f"Call result: {result.__repr__()}")
                messages.append(message.function_call_result(tool_call, result))
