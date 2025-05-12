from pydantic import BaseModel, Field
from src.anchor.extractor import Extractor


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


TOOLS = [Finish, Next, GiveUp]
