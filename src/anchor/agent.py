from ast import match_case
import logging
import sys
from typing import Any, Callable, List, Tuple

import openai
from git_wrapper import CommitMeta
from openai import NOT_GIVEN, NotGiven
from openai.types.chat import (
    ChatCompletionMessageParam as Message,
    ParsedFunctionToolCall,
)
from openai.types.chat import ChatCompletionToolParam as Tool
from openai.types.chat import ParsedChatCompletion

from src import prompt, term
from src.anchor.extractor import Extractor
from src.schema.control import Control, Feedback, Finish, GiveUp
from src.term import Color

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
        feedback_requests = []

        for i in range(prompt.MAX_ITERATIONS):
            # write all messages into the {i}_messages.text file for debugging
            with open(f"{i}_messages.txt", "w") as f:
                for m in messages:
                    f.write(f"{m}\n")


            completion = self.communicate(messages + feedback_requests, tools)
            feedback_requests = []

            if completion.usage:
                total_tokens += completion.usage.total_tokens or 0
            response = completion.choices[0].message
            logger.info(f"Response: {response.content}")

            term.wait()
            term.clear()
            term.log(Color.YELLOW, "Response:")
            term.log(Color.YELLOW, response.content)

            messages.append(response)

            # check if LLM found the link
            # no function call means that LLM didn't find the link
            if response.tool_calls is None or len(response.tool_calls) == 0:
                logger.info("LLM didn't call any function")
                term.log(Color.GREEN, "LLM didn't call any function")
                messages.append(prompt.should_call_function())
                continue

            logger.info(f"{len(response.tool_calls)} tool called")
            term.log(Color.GREEN, f"{len(response.tool_calls)} tool called")
            feedback_calls=[]
            for tool_call in response.tool_calls:
                functionn = tool_call.function.parsed_arguments
                if functionn is None:
                    logger.error(f"message that caused error: {messages[-1]}")
                    raise ValueError("Function not found in tool call")

                # just to saticfy type checking
                function: Callable[[Extractor], Any] = functionn  # type: ignore
                logger.info(f"LLM calling: {function.__repr__()}")
                term.log(Color.GREEN, f"LLM calling: {function.__repr__()}")

                result = ""
                # special case handing for control tools, since they can change the code flow
                if isinstance(function, Control):
                    if isinstance(function, Finish) or isinstance(function, GiveUp):
                        commit_hash = function(extractor)
                        return (commit_hash, total_tokens)
                    elif isinstance(function, Feedback):
                        messages = function.apply_feedback(messages)
                        term.log(Color.WHITE, f"Recieved Feedback {function.Value}")
                try:
                    term.log(
                        Color.WHITE,
                        f"Calling function {function.__repr__()} with extractor",
                    )
                    # just to saticfy type checking
                    function: Callable[[Extractor], Any] = functionn  # type: ignore
                    result = function(extractor)
                    # check if feedback is required
                    if sys.getsizeof(result) > prompt.SIZE_THRESHOLD:
                        term.log(
                            Color.WHITE,
                            f"The output of {tool_call.id} is too large, asking for feedback",
                        )
                        feedback_requests.append(prompt.feedback_for(tool_call))

                except Exception as e:
                    result = f"encountered the following error: {e}"
                logger.debug(f"Call result: {result.__repr__()}")
                term.log(Color.BLUE, f"Call result: {sys.getsizeof(result)} bytes")
                term.log(Color.BLUE, result)
                messages.append(prompt.function_call_result(tool_call, result))
                    


        return ("FFFFFFFFFFFFF", total_tokens)
