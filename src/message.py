from typing import Any
from openai.types.chat import ChatCompletionSystemMessageParam as SystemMessage
from openai.types.chat import ChatCompletionUserMessageParam as UserMessage
from openai.types.chat import ChatCompletionToolMessageParam as ToolMessage
from openai.types.chat import ParsedFunctionToolCall as ToolCall


def problem_explanation() -> SystemMessage:
    return SystemMessage(role="system", content=PROBLEM_EXPLANATION_PROMPT_TEXT)


def user_initial_prompt(issue_title: str) -> UserMessage:
    return UserMessage(
        role="user", content=f"{USER_INITIAL_PROMPT_TEXT}: {issue_title}"
    )


def function_call_result(tool_call: ToolCall, result: Any) -> ToolMessage:
    return ToolMessage(
        role="tool",
        tool_call_id=tool_call.id,
        content=f"{result}",
    )


PROBLEM_EXPLANATION_PROMPT_TEXT = """
You are a bot in a issue tracking system that is monitoring a project. Your task is to find the commit that resolved a closed issue in an issue tracking system.
you are given the title of the issue as the starting point by the user. 
I have provided you a set of functions that grants you access to the source codes in the code base, commit history of the git repo, and the data that is available in the issue (issue description and discussions threads). you can use them to retrieve more data abouts commits and issue.
when you are sure that you found the commit that resolved the issue, you can return the commit hash to the user.
"""
USER_INITIAL_PROMPT_TEXT = "Find the commit that resolves the issue with the title"
