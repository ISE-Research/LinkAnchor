from typing import Any, Callable, List
from openai.types.chat import ChatCompletionToolParam as Tool
from openai.types.chat import ChatCompletionMessageParam as Message
from openai.types.chat import ParsedChatCompletion
from openai import NotGiven, NOT_GIVEN
import openai
import message


class Agent:
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
        return self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )

    def find_link(
        self, issue_title: str, tools: List[Tool], call: Callable[[Any], Any]
    ) -> str:
        """Find the commit(s) that resolve(s) the issue."""

        messages = [
            message.problem_explanation(),
            message.user_initial_prompt(issue_title),
        ]

        while True:
            completion = self.communicate(messages, tools)
            response = completion.choices[0].message

            # check if LLM found the link
            content = response.content
            if content is not None and content != "":
                return content

            # must call a function
            if response.tool_calls is None or len(response.tool_calls) == 0:
                print(messages)
                raise ValueError("No tool call found in the message")

            tool_call = response.tool_calls[0]

            function = tool_call.function.parsed_arguments
            if function is None:
                print(messages)
                raise ValueError("Function not found in tool call")

            result = call(function)

            messages.append(response)
            messages.append(message.function_call_result(tool_call, result))
