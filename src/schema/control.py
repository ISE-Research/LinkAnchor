from pydantic import BaseModel, Field
from src.anchor.extractor import Extractor
from enum import Enum
from typing import List
from openai.types.chat import ChatCompletionMessageParam as Message


class Control:
    """Base class for all control classes"""

    def is_control_tool(self) -> bool:
        """Check if the class is a control tool"""
        return True


class Finish(BaseModel, Control):
    """Finishes the process by returning the commit hash of the commit that resolves the issue"""

    commit_hash: str = Field(
        ..., description="commit hash of the commit that resolves the issue"
    )

    def __call__(self, _: Extractor) -> str:
        return self.commit_hash


class GiveUp(BaseModel, Control):
    """Finishes the process by returning None"""

    def __call__(self, _: Extractor) -> str:
        return "LLM gave up, no commit hash found"


class Next(BaseModel, Control):
    """Returns the next batch of commits to be analyzed"""

    def __call__(self, _: Extractor) -> str:
        return "next system message would contain the next batch of commits"


class FeedbackValue(str, Enum):
    DISCARD = "discard"
    USEFUL = "useful"

class Feedback(BaseModel):
    """
    Feedback about the previous tool call.
    """

    call_id: str = Field(..., description="id of the tool call to discard")
    Value: FeedbackValue = Field(..., description="either DISCARD or USEFUL")

    def __call__(self, messages: List[Message]) -> List[Message]:
        for m in messages:
            if "tool_call_id" in m and m["tool_call_id"] == self.call_id:
                m["content"] = "<USELESS_OUTPUT>"
                break
        return messages


TOOLS = [Finish, Next, GiveUp]
