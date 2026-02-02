"""Module for Jira comment operations."""

import logging
from typing import Any

from ..utils import parse_date
from .client import JiraClient
from .mappers import MapperRegistry

logger = logging.getLogger("mcp-jira")


class CommentsMixin(JiraClient):
    """Mixin for Jira comment operations."""

    def get_issue_comments(
        self, issue_key: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get comments for a specific issue.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            limit: Maximum number of comments to return

        Returns:
            List of comments with author, creation date, and content

        Raises:
            Exception: If there is an error getting comments
        """
        try:
            comments = self.jira.issue_get_comments(issue_key)

            if not isinstance(comments, dict):
                msg = f"Unexpected return value type from `jira.issue_get_comments`: {type(comments)}"
                logger.error(msg)
                raise TypeError(msg)

            # Normalize comments for Server 6.x compatibility
            raw_comments = comments.get("comments", [])[:limit]
            is_server_6x = self.config.jira_mode == "server_6x"
            if is_server_6x:
                raw_comments = (
                    MapperRegistry.get_comment_mapper().normalize_comments_list(
                        raw_comments
                    )
                )

            processed_comments = []
            for comment in raw_comments:
                # Get author name - handle both Cloud (accountId) and Server 6.x (name) formats
                author = comment.get("author", {})
                author_name = (
                    author.get("displayName")
                    or author.get("name")
                    or author.get("accountId")
                    or "Unknown"
                )

                processed_comment = {
                    "id": comment.get("id"),
                    "body": self._clean_text(comment.get("body", "")),
                    "created": str(parse_date(comment.get("created"))),
                    "updated": str(parse_date(comment.get("updated"))),
                    "author": author_name,
                }
                processed_comments.append(processed_comment)

            return processed_comments
        except Exception as e:
            logger.error(f"Error getting comments for issue {issue_key}: {str(e)}")
            raise Exception(f"Error getting comments: {str(e)}") from e

    def get_comment(self, issue_key: str, comment_id: str) -> dict[str, Any]:
        """
        Получить конкретный комментарий задачи по ID.

        Args:
            issue_key: Ключ задачи (например 'PROJ-123')
            comment_id: ID комментария

        Returns:
            Словарь с данными комментария

        Raises:
            Exception: Если комментарий не найден или ошибка API
        """
        try:
            # Для Server 6.x APIv2Adapter перепишет в /rest/api/2/
            url = f"/rest/api/3/issue/{issue_key}/comment/{comment_id}"
            response = self.jira.get(url)

            if not isinstance(response, dict):
                msg = f"Unexpected return value type: {type(response)}"
                logger.error(msg)
                raise TypeError(msg)

            # Normalize for Server 6.x
            is_server_6x = self.config.jira_mode == "server_6x"
            if is_server_6x:
                mapper = MapperRegistry.get_comment_mapper()
                response = mapper.normalize_comment_response(response)

            author = response.get("author", {})
            author_name = (
                author.get("displayName")
                or author.get("name")
                or author.get("accountId")
                or "Unknown"
            )

            return {
                "id": response.get("id"),
                "body": self._clean_text(response.get("body", "")),
                "created": str(parse_date(response.get("created"))),
                "updated": str(parse_date(response.get("updated"))),
                "author": author_name,
            }
        except Exception as e:
            msg = f"Error getting comment {comment_id} for issue {issue_key}: {str(e)}"
            logger.error(msg)
            err_msg = f"Error getting comment {comment_id}: {str(e)}"
            raise Exception(err_msg) from e

    def add_comment(
        self, issue_key: str, comment: str, visibility: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            comment: Comment text to add (in Markdown format)
            visibility: (optional) Restrict comment visibility (e.g. {"type":"group","value:"jira-users"})

        Returns:
            The created comment details

        Raises:
            Exception: If there is an error adding the comment
        """
        try:
            # Convert Markdown to Jira's markup format
            jira_formatted_comment = self._markdown_to_jira(comment)

            result = self.jira.issue_add_comment(
                issue_key, jira_formatted_comment, visibility
            )
            if not isinstance(result, dict):
                msg = f"Unexpected return value type from `jira.issue_add_comment`: {type(result)}"
                logger.error(msg)
                raise TypeError(msg)

            # Normalize comment response for Server 6.x compatibility
            is_server_6x = self.config.jira_mode == "server_6x"
            if is_server_6x:
                result = MapperRegistry.get_comment_mapper().normalize_comment_response(
                    result
                )

            # Get author name - handle both Cloud (accountId) and Server 6.x (name) formats
            author = result.get("author", {})
            author_name = (
                author.get("displayName")
                or author.get("name")
                or author.get("accountId")
                or "Unknown"
            )

            return {
                "id": result.get("id"),
                "body": self._clean_text(result.get("body", "")),
                "created": str(parse_date(result.get("created"))),
                "author": author_name,
            }
        except Exception as e:
            logger.error(f"Error adding comment to issue {issue_key}: {str(e)}")
            raise Exception(f"Error adding comment: {str(e)}") from e

    def edit_comment(
        self,
        issue_key: str,
        comment_id: str,
        comment: str,
        visibility: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Edit an existing comment on an issue.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            comment_id: The ID of the comment to edit
            comment: Updated comment text (in Markdown format)
            visibility: (optional) Restrict comment visibility (e.g. {"type":"group","value":"jira-users"})

        Returns:
            The updated comment details

        Raises:
            Exception: If there is an error editing the comment
        """
        try:
            # Convert Markdown to Jira's markup format
            jira_formatted_comment = self._markdown_to_jira(comment)

            result = self.jira.issue_edit_comment(
                issue_key, comment_id, jira_formatted_comment, visibility
            )
            if not isinstance(result, dict):
                msg = f"Unexpected return value type from `jira.issue_edit_comment`: {type(result)}"
                logger.error(msg)
                raise TypeError(msg)

            return {
                "id": result.get("id"),
                "body": self._clean_text(result.get("body", "")),
                "updated": str(parse_date(result.get("updated"))),
                "author": result.get("author", {}).get("displayName", "Unknown"),
            }
        except Exception as e:
            logger.error(
                f"Error editing comment {comment_id} on issue {issue_key}: {str(e)}"
            )
            raise Exception(f"Error editing comment: {str(e)}") from e

    def _markdown_to_jira(self, markdown_text: str) -> str:
        """
        Convert Markdown syntax to Jira markup syntax.

        This method uses the TextPreprocessor implementation for consistent
        conversion between Markdown and Jira markup.

        Args:
            markdown_text: Text in Markdown format

        Returns:
            Text in Jira markup format
        """
        if not markdown_text:
            return ""

        # Use the existing preprocessor
        try:
            return self.preprocessor.markdown_to_jira(markdown_text)
        except Exception as e:
            logger.warning(f"Error converting markdown to Jira format: {str(e)}")
            # Return the original text if conversion fails
            return markdown_text
