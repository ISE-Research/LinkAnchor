import re
from typing import List
from github import Github
from datetime import datetime

from src.issue_wrapper.wrapper import Wrapper, Pagination, CommentMeta


class GitHubIssueWrapper(Wrapper):
    def __init__(self, url: str):
        match = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url)
        if not match:
            raise ValueError("Invalid GitHub issue URL format.")

        owner = match.group(1)
        repo_name = match.group(2)
        issue_number = int(match.group(3))

        self.issue_data = (
            Github().get_repo(f"{owner}/{repo_name}").get_issue(number=issue_number)
        )

    def issue_title(self) -> str:
        return self.issue_data.title

    def issue_key(self) -> str:
        return str(self.issue_data.number)

    def issue_description(self) -> str:
        return self.issue_data.body

    def issue_author(self) -> str:
        return self.issue_data.user.login

    def issue_created_at(self) -> datetime:
        return self.issue_data.created_at

    def issue_closed_at(self) -> datetime:
        return self.issue_data.closed_at

    def issue_comments(self, pagination: Pagination) -> List[CommentMeta]:
        comments = self.issue_data.get_comments()
        comments = comments[pagination.offset : pagination.offset + pagination.limit]
        comment_meta_list = []
        for comment in comments:
            comment_meta = CommentMeta(
                author=comment.user.login,
                body=comment.body,
                created_at=str(comment.created_at),
            )
            comment_meta_list.append(comment_meta)
        return comment_meta_list

    def issue_participants(self) -> List[str]:
        participants = set()
        for assignee in self.issue_data.assignees:
            participants.add(assignee.login)
        for comment in self.issue_data.get_comments():
            participants.add(comment.user.login)
        participants.add(self.issue_author())
        return list(participants)
