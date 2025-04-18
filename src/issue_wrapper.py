import re
from typing import List
import requests
import abc
from github import Github
from pydantic import BaseModel, Field
from datetime import datetime


class Pagination(BaseModel):
    """pagination for listing commits"""

    offset: int = Field(..., description="offset starts from 0")
    limit: int = Field(..., description="limit of number of items to return")


class CommentMeta(BaseModel):
    author: str = Field(..., description="offset starts from 0")
    body: str = Field(..., description="textual body of the comment")
    created_at: str = Field(..., description="creation date of the comment")


class IssueWrapper(abc.ABC):
    def __init__(self, issue_link: str):
        self.issue_data = self.get_issue_data(issue_link)

    @abc.abstractmethod
    def get_issue_data(self, issue_link: str):
        """
        Query REST API for the issue data.
        """
        pass

    @abc.abstractmethod
    def get_issue_title(self) -> str:
        """
        Extract and return the issue title.
        """
        pass

    @abc.abstractmethod
    def get_issue_description(self) -> str:
        """
        Extract and return the issue description.
        """
        pass

    @abc.abstractmethod
    def get_issue_author(self) -> str:
        """
        Extract and return the username of the issue creator.
        """
        pass

    @abc.abstractmethod
    def get_issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        """
        Extract and return a list of comment metadata.
        """
        pass

    @staticmethod
    def handle_pagination(pagination: Pagination, items):
        return items[pagination.offset: pagination.offset + pagination.limit]

    @abc.abstractmethod
    def get_issue_participants(self) -> List[str]:
        """
        Gather a list of unique users who participated in the issue thread.
        This includes the issue creator and all comment authors.
        """
        pass

    @classmethod
    def create_retriever(cls, url: str) -> 'IssueWrapper':
        """
        Factory method to inspect the issue URL. If it contains 'jira',
        instantiate a JiraIssueRetriever; if 'github.com', instantiate a GitHubIssueRetriever.
        """
        if "jira" in url.lower():
            return JiraIssueWrapper(url)
        elif "github.com" in url.lower():
            return GitHubIssueWrapper(url)
        else:
            raise ValueError("Unsupported issue URL format.")


class JiraIssueWrapper(IssueWrapper):

    def get_issue_data(self, issue_link: str):
        response = requests.get(issue_link)
        print(response)
        response.raise_for_status()
        return response.json()

    def get_issue_title(self) -> str:
        return self.issue_data["fields"]["summary"]

    def get_issue_description(self) -> str:
        return self.issue_data["fields"]["description"]

    def get_issue_author(self) -> str:
        return self.issue_data["fields"]["creator"].get("displayName") or \
               self.issue_data["fields"]["creator"].get("name")

    def get_issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        comments = self.issue_data["fields"]["comment"]["comments"]

        comments = self.handle_pagination(
            pagination=pagination,
            items=comments
        )

        comment_meta_list = []
        for comment in comments:
            comment_meta = CommentMeta(
                author=self.get_comment_author(comment),
                body=comment["body"],
                created_at=comment["created"]
            )
            comment_meta_list.append(comment_meta)
        return comment_meta_list

    def get_issue_participants(self) -> List[str]:
        participants = set()

        creator = self.get_issue_author()
        if creator:
            participants.add(creator)

        for comment in self.issue_data["fields"]["comment"]["comments"]:
            author = self.get_comment_author(comment)
            if author:
                participants.add(author)

        assignee = self.issue_data["fields"].get("assignee")
        if assignee:
            name = assignee.get("displayName") or assignee.get("name")
            if name:
                participants.add(name)

        return list(participants)

    @staticmethod
    def get_comment_author(comment) -> str:
        return comment["author"].get("displayName") or comment["author"].get("name")


class GitHubIssueWrapper(IssueWrapper):
    def get_issue_data(self, issue_link: str):
        match = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", issue_link)
        if not match:
            raise ValueError("Invalid GitHub issue URL format.")

        owner = match.group(1)
        repo_name = match.group(2)
        issue_number = int(match.group(3))

        return Github().get_repo(f"{owner}/{repo_name}").get_issue(number=issue_number)

    def get_issue_title(self) -> str:
        return self.issue_data.title

    def get_issue_description(self) -> str:
        return self.issue_data.body

    def get_issue_author(self) -> str:
        return self.issue_data.user.login

    def get_issue_created_at(self) -> datetime:
        return self.issue_data.created_at

    def get_issue_closed_at(self) -> datetime:
        return self.issue_data.closed_at

    def get_issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        comments = self.handle_pagination(pagination, self.issue_data.get_comments())
        comment_meta_list = []
        for comment in comments:
            comment_meta = CommentMeta(
                author=comment.user.login,
                body=comment.body,
                created_at=str(comment.created_at)
            )
            comment_meta_list.append(comment_meta)
        return comment_meta_list

    def get_issue_participants(self) -> List[str]:
        participants = set()
        for assignee in self.issue_data.assignees:
            participants.add(assignee.login)
        for comment in self.issue_data.get_comments():
            participants.add(comment.user.login)
        participants.add(self.get_issue_author())
        return list(participants)
