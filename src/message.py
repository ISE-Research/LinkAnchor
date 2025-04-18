from typing import Any
from openai.types.chat import ChatCompletionSystemMessageParam as SystemMessage
from openai.types.chat import ChatCompletionUserMessageParam as UserMessage
from openai.types.chat import ChatCompletionToolMessageParam as ToolMessage
from openai.types.chat import ParsedFunctionToolCall as ToolCall


def problem_explanation() -> SystemMessage:
    """
    The initial prompt that explains the role of the agent and its goals.
    """
    return SystemMessage(role="system", content=PROBLEM_EXPLANATION_PROMPT_TEXT)


def user_initial_prompt(issue_title: str) -> UserMessage:
    """
    The initial prompt that user provides to the agent.
    """
    return UserMessage(
        role="user", content=f"{USER_INITIAL_PROMPT_TEXT}: {issue_title}"
    )


def function_call_result(tool_call: ToolCall, result: Any) -> ToolMessage:
    """
    Prompt for sending the results of a tool call back to the agent.
    """
    return ToolMessage(
        role="tool",
        tool_call_id=tool_call.id,
        content=f"{result}",
    )

def extract_commit_hash(content: str) -> str| None:
    """
    Try to extract commit_hash from the message given by the agent.
    """
    last_line = content.split("\n")[-1]
    if last_line.startswith(COMMIT_FOUND_MESSAGE):
        commit_hash = last_line.split(f"{COMMIT_FOUND_MESSAGE}: ")[-1].strip()
        return commit_hash

COMMIT_FOUND_MESSAGE = "found commit resolving this issue"

PROBLEM_EXPLANATION_PROMPT_TEXT = f"""
Role & Goals:
You are an intelligent agent specialized in identifying and linking software issues directly to the specific commit hashes that resolve them. Your primary objective is to determine and provide the exact commit hash responsible for resolving a given issue.
To accomplish this goal, you will iteratively leverage the provided functions to gather relevant repository information. At each interaction, you should:
1. Call at least one of the available functions.
2. Carefully analyze its response.
3. Decide the subsequent function call based on this analysis.

Remember to call at least one function in each iteration. if you don't call any function, user will assume that you found the commit and searches for the commit hash in your response.

YOU CAN NOT ASK QUESTIONS FROM THE USER.

Repeat this iterative process systematically until you accurately pinpoint the commit hash resolving the issue.
Maintain explicit, logical, and transparent reasoning at each step, clearly outlining your decision-making process, function selection rationale, and the insights obtained from each function's response.
For each interaction, also provide your reasoning and the function you intend to call next.

Whenever you are assured that you found the commit that resolves the issue, have the following line as the last line of your response where <commit_hash> is the commit hash of the commit you found:
{COMMIT_FOUND_MESSAGE}: <commit_hash>

Guidelines:
Only the project's source code is important. Therefore, if you find yourself needing to call one of the codebase functions related to a dependency or external library, avoid making such calls. Instead, rely on your existing knowledge about the dependency or library.
"""

USER_INITIAL_PROMPT_TEXT = "Find the commit that resolves the issue with the title"

