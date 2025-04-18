from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from anchor.extractor import Extractor
from issue_wrapper.wrapper import Pagination, CommentMeta


class IssueTitle(BaseModel):
    """Retrieving the issue title"""

    def __call__(self, extractor: Extractor) -> str:
        return extractor.issue_title()


class IssueDescription(BaseModel):
    """Retrieving the issue description"""

    def __call__(self, extractor: Extractor) -> str:
        return extractor.issue_description()


class IssueAuthor(BaseModel):
    """Retrieving the issue author"""

    def __call__(self, extractor: Extractor) -> str:
        return extractor.issue_author()


class IssueCreationTimestamp(BaseModel):
    """Retrieving the issue creation timestamp"""

    def __call__(self, extractor: Extractor) -> datetime:
        return extractor.issue_created_at()


class IssueClosedTimestamp(BaseModel):
    """Retrieving the issue closed timestamp"""

    def __call__(self, extractor: Extractor) -> datetime:
        return extractor.issue_closed_at()


class IssueComments(BaseModel):
    """Retrieving all the issue comments"""

    pagination: Pagination = Field(
        ..., description="pagination from offset to at least offset + limit"
    )

    def __call__(self, extractor: Extractor) -> List[CommentMeta]:
        return extractor.issue_comments(self.pagination)


class IssueParticipants(BaseModel):
    """
    Gather a list of unique users who participated in the issue thread.
    This includes the issue creator and all comment authors.
    """

    def __call__(self, extractor: Extractor) -> List[str]:
        return extractor.issue_participants()


TOOLS = [
    IssueTitle,
    IssueDescription,
    IssueAuthor,
    IssueComments,
    IssueCreationTimestamp,
    IssueClosedTimestamp,
]
