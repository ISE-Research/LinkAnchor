from typing import List
import abc
from pydantic import BaseModel, Field
from datetime import datetime


class Pagination(BaseModel):
    """pagination for listing comments"""

    offset: int = Field(..., description="offset starts from 0")
    limit: int = Field(
        ...,
        description="limit of number of items to return. limit should not be less than 10",
    )


class CommentMeta(BaseModel):
    author: str = Field(..., description="offset starts from 0")
    body: str = Field(..., description="textual body of the comment")
    created_at: str = Field(..., description="creation date of the comment")

    def __str__(self):
        return f"{self.author} {self.created_at}\nMessage:\n{self.body})"


class Wrapper(abc.ABC):
    @abc.abstractmethod
    def issue_title(self) -> str:
        """
        Extract the issue title.
        """
        pass

    @abc.abstractmethod
    def issue_created_at(self) -> datetime:
        """
        Extract the issue creation timestamp
        """
        pass

    @abc.abstractmethod
    def issue_closed_at(self) -> datetime:
        """
        Extract the issue closed_at timestamp
        """
        pass

    @abc.abstractmethod
    def issue_description(self) -> str:
        """
        Extract the issue description.
        """
        pass

    @abc.abstractmethod
    def issue_author(self) -> str:
        """
        Extract the username of the issue creator.
        """
        pass

    @abc.abstractmethod
    def issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        """
        Extract a list of comment metadata.
        """
        pass

    @abc.abstractmethod
    def issue_participants(self) -> List[str]:
        """
        Gather a list of unique users who participated in the issue thread.
        This includes the issue creator and all comment authors.
        """
        pass
