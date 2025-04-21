from typing import List
import requests
from datetime import datetime

from src.issue_wrapper.wrapper import Wrapper, Pagination, CommentMeta


class JiraIssueWrapper(Wrapper):
    def __init__(self, url: str):
        response = requests.get(url)
        response.raise_for_status()
        self.issue_data = response.json()

    def issue_title(self) -> str:
        return self.issue_data["fields"]["summary"]

    def issue_description(self) -> str:
        return self.issue_data["fields"]["description"]

    def issue_created_at(self) -> datetime:
        return self.issue_data["fields"]["created"]

    def issue_closed_at(self) -> datetime:
        return self.issue_data["fields"].get("resolutiondate")

    def issue_author(self) -> str:
        return self.issue_data["fields"]["creator"].get(
            "displayName"
        ) or self.issue_data["fields"]["creator"].get("name")

    def issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        comments = self.issue_data["fields"]["comment"]["comments"]

        comments = comments[pagination.offset : pagination.offset + pagination.limit]

        comment_meta_list = []
        for comment in comments:
            comment_meta = CommentMeta(
                author=self.get_comment_author(comment),
                body=comment["body"],
                created_at=comment["created"],
            )
            comment_meta_list.append(comment_meta)
        return comment_meta_list

    def issue_participants(self) -> List[str]:
        participants = set()

        creator = self.issue_author()
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
