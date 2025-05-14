from typing import Any, List
from git_wrapper import CommitMeta
from openai.types.chat import ChatCompletionSystemMessageParam as SystemMessage
from openai.types.chat import ChatCompletionUserMessageParam as UserMessage
from openai.types.chat import ChatCompletionToolMessageParam as ToolMessage
from openai.types.chat import ParsedFunctionToolCall as ToolCall


def problem_explanation() -> SystemMessage:
    """
    The initial prompt that explains the role of the agent and its goals.
    """
    return SystemMessage(role="system", content=PROBLEM_EXPLANATION_PROMPT_TEXT)


def show_commits(commits: List[CommitMeta]) -> SystemMessage:
    """
    Show the commits to the agent.
    """
    return SystemMessage(
        role="system",
        content=f"current batch of commits to be analyzed consisting of {len(commits)} items:\n{commits}",
    )


def should_call_function() -> SystemMessage:
    """
    The prompt that tells the agent that it should call a function.
    """
    return SystemMessage(
        role="system",
        content="You should call at least one function in each iteration. "
        "If you don't call any function, user will assume that you can not find the commit.",
    )


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


def extract_commit_hash(content: str) -> str | None:
    """
    Try to extract commit_hash from the message given by the agent.
    """
    last_line = content.split("\n")[-1]
    if last_line.startswith(COMMIT_FOUND_MESSAGE):
        commit_hash = last_line.split(f"{COMMIT_FOUND_MESSAGE}: ")[-1].strip()
        return commit_hash


COMMIT_FOUND_MESSAGE = "found commit resolving this issue"

MAX_ITERATIONS = 2000

# Note that the iterative process only lasts for at most {MAX_ITERATIONS} iterations. If you reach the last iteration and you have not provided any commit_hash, the user assumes that you can not find the link

PROBLEM_EXPLANATION_PROMPT_TEXT = """
Role & Goals:
You are an intelligent agent specialized in identifying and linking software issues directly to the specific commit hashes that resolve them. Your primary objective is to determine and provide the exact commit hash responsible for resolving a given issue.
To accomplish this goal, you will iteratively leverage the provided functions to gather relevant repository information. 

At each iteration (except the first one) you are provided with a list of 100 commits. 
Each time you can use the data extraction tools provided to you to gather data about commits that you suspect might be the target commit and analyze them. 
When you are done analyzing you can either:
1. Call `Finish` function with the commit_hash of the commit that resolves the issue to signal the end of the process 
2. Call `Next` function to get the next batch of 100 commits and you can start from the first step again.

you keep the above steps until you either find the commit that you are fully sure it resolves the commit or the iteration finishes and there are no commits returned by calling the `Next` function.


At each interaction, you should:
1. Call at least one of the available functions.
2. Carefully analyze its response.
3. Decide the subsequent function call based on this analysis.

Repeat this iterative process systematically until you accurately pinpoint the commit hash resolving the issue.
Maintain explicit, logical, and transparent reasoning at each step, clearly outlining your decision-making process, function selection rationale, and the insights obtained from each function's response.
For each interaction, also provide your reasoning and the function you intend to call next.


Rules you SHOULD follow:
1. Remember to call AT LEAST ONE function in each iteration. if you don't call any function, user will assume that you found the commit and searches for the commit hash in your response.

2. YOU CAN NOT ASK QUESTIONS FROM THE USER.

3. Calling a function with the same inputs twice WONT CHANGE the output (except for the `Next` function) so YOU SHOULD NOT call a function with the same input twice. instead, use the output generated from the previous calls.

4. Only the project's source code is important. Therefore, if you find yourself needing to call one of the codebase functions related to a dependency or external library, avoid making such calls. Instead, rely on your existing knowledge about the dependency or library.

5. Some functions have a pagination parameter. You can use it to limit the number of results returned by the function. You can use limits upto 100 in the pagination.

6. sometimes the description in issue title is not enough, make sure to incorporate the issue description and comments in your reasoning. You can use the `IssueDescription` and `IssueComments` function to get the description and comments of the issue.

7. When calling the `CommitsOnFile` function, if the result was empty, you can call the `ListFiles` function to ensure that you passed the correct file name.

8. Keep in mind that the issue tracker and the issue are used for several artifacts distributed across several repositories. So it might be the case that the issue requires fixes in more than one repository. So if you find a commit hash in the issue comments indecating that this commit fixes the issue, it might be from another repository and you need to continue your search until you find a commit hash from the repository we are working with. inorder to make sure the commit you found is present in the repository, you MUST CALL the `CommitMetadata` function on that and see wether it returns an error or an actual commit. 
If you found out that the commit is from another repository, you can try to find a similar commit or a commit from the same author from the commit batch already provided to you or from the next batches

Note: 
If you are unable to find the commit hash, and you are sure that no more attempts will yield results, you can call the `GiveUp` function.
"""
# 3. Sometimes the difference between `IssueCreationTimestamp` and `IssueClosedTimestamp` is very large (more than a year). In these cases Issue was probably resolved close to the `IssueCreationTimestamp` but it was marked as closed years later. In these cases, First call `commits_between` with smallests pagination possible just to get the total number of commits in the time period, then, using pagination, start iterating over commits from the `IssueCreationTimestamp` end of the range.
# For example, lets say after calling:
# `commits_between(start_date=IssueCreationTimestamp, end_date=IssueClosedTimestamp, pagination=Pagination(offset=0, limit=1))`
# you get the following response:
# `
# 12345
# <first commit metadata>
# `
# you can then call:
# `commits_between(start_date=IssueCreationTimestamp, end_date=IssueClosedTimestamp, pagination=Pagination(offset=12245, limit=100))`
# to fetch the first 10 commits that were pushed after the `IssueCreationTimestamp`.
# if you didn't find the commit in the first 10 commits, you can call:
# `commits_between(start_date=IssueCreationTimestamp, end_date=IssueClosedTimestamp, pagination=Pagination(offset=12145, limit=100))`
# and so on until you find the commit or reach the last iteration.


USER_INITIAL_PROMPT_TEXT = "Find the commit that resolves the issue with the title"
