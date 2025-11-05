"""Field mapping utilities for Jira Server 6.x compatibility.

This module provides mappers to normalize field formats between Cloud and Server 6.x:
- Cloud uses accountId, emailAddress
- Server 6.x uses name, key, displayName
"""

import logging
from typing import Any

logger = logging.getLogger("mcp-jira")


class UserFieldMapper:
    """Mapper for user-related fields between Cloud and Server 6.x."""

    @staticmethod
    def normalize_user_response(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize user response from API to Cloud format.

        Maps Server 6.x fields (name, key) to Cloud format (accountId).
        Handles missing emailAddress gracefully.

        Args:
            data: Raw user data from API

        Returns:
            Normalized user data
        """
        if not data:
            return data

        normalized = data.copy()

        # If accountId is missing, try to use name or key as fallback
        if "accountId" not in normalized or normalized["accountId"] is None:
            if "name" in normalized and normalized["name"]:
                normalized["accountId"] = normalized["name"]
                logger.debug(f"Mapped user 'name' to 'accountId': {normalized['name']}")
            elif "key" in normalized and normalized["key"]:
                normalized["accountId"] = normalized["key"]
                logger.debug(f"Mapped user 'key' to 'accountId': {normalized['key']}")

        # emailAddress may be missing in Server 6.x - handle gracefully
        if "emailAddress" not in normalized:
            normalized["emailAddress"] = None

        return normalized

    @staticmethod
    def normalize_user_request(
        data: dict[str, Any], is_server_6x: bool
    ) -> dict[str, Any]:
        """Normalize user request data for API.

        For Server 6.x, converts accountId to name format.

        Args:
            data: User data to send to API
            is_server_6x: Whether this is Server 6.x mode

        Returns:
            Normalized user data for API request
        """
        if not data:
            return data

        if not is_server_6x:
            return data

        normalized = data.copy()

        # For Server 6.x, convert accountId to name
        if "accountId" in normalized:
            normalized["name"] = normalized["accountId"]
            # Remove accountId as Server 6.x doesn't support it
            del normalized["accountId"]
            logger.debug(
                f"Converted accountId to name for Server 6.x: {normalized['name']}"
            )

        return normalized


class IssueFieldMapper:
    """Mapper for issue-related fields between Cloud and Server 6.x."""

    @staticmethod
    def normalize_issue_response(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize issue response from API.

        Normalizes assignee and reporter fields in issue data.

        Args:
            data: Raw issue data from API

        Returns:
            Normalized issue data
        """
        if not data:
            return data

        normalized = data.copy()

        # Normalize fields dict
        if "fields" in normalized and isinstance(normalized["fields"], dict):
            fields = normalized["fields"].copy()

            # Normalize assignee
            if "assignee" in fields and isinstance(fields["assignee"], dict):
                fields["assignee"] = UserFieldMapper.normalize_user_response(
                    fields["assignee"]
                )

            # Normalize reporter
            if "reporter" in fields and isinstance(fields["reporter"], dict):
                fields["reporter"] = UserFieldMapper.normalize_user_response(
                    fields["reporter"]
                )

            # Normalize creator (if present)
            if "creator" in fields and isinstance(fields["creator"], dict):
                fields["creator"] = UserFieldMapper.normalize_user_response(
                    fields["creator"]
                )

            normalized["fields"] = fields

        return normalized

    @staticmethod
    def normalize_issue_request(
        data: dict[str, Any], is_server_6x: bool
    ) -> dict[str, Any]:
        """Normalize issue request data for API.

        For Server 6.x, converts assignee/reporter from accountId to name format.

        Args:
            data: Issue data to send to API
            is_server_6x: Whether this is Server 6.x mode

        Returns:
            Normalized issue data for API request
        """
        if not data:
            return data

        if not is_server_6x:
            return data

        normalized = data.copy()

        # Normalize fields dict
        if "fields" in normalized and isinstance(normalized["fields"], dict):
            fields = normalized["fields"].copy()

            # Normalize assignee
            if "assignee" in fields and isinstance(fields["assignee"], dict):
                fields["assignee"] = UserFieldMapper.normalize_user_request(
                    fields["assignee"], is_server_6x=True
                )

            # Normalize reporter
            if "reporter" in fields and isinstance(fields["reporter"], dict):
                fields["reporter"] = UserFieldMapper.normalize_user_request(
                    fields["reporter"], is_server_6x=True
                )

            normalized["fields"] = fields

        return normalized


class CommentFieldMapper:
    """Mapper for comment-related fields between Cloud and Server 6.x."""

    @staticmethod
    def normalize_comment_response(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize comment response from API.

        Normalizes author and updateAuthor fields in comment data.

        Args:
            data: Raw comment data from API

        Returns:
            Normalized comment data
        """
        if not data:
            return data

        normalized = data.copy()

        # Normalize author
        if "author" in normalized and isinstance(normalized["author"], dict):
            normalized["author"] = UserFieldMapper.normalize_user_response(
                normalized["author"]
            )

        # Normalize updateAuthor
        if "updateAuthor" in normalized and isinstance(
            normalized["updateAuthor"], dict
        ):
            normalized["updateAuthor"] = UserFieldMapper.normalize_user_response(
                normalized["updateAuthor"]
            )

        return normalized

    @staticmethod
    def normalize_comments_list(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize a list of comments.

        Args:
            comments: List of raw comment data

        Returns:
            List of normalized comment data
        """
        return [
            CommentFieldMapper.normalize_comment_response(comment)
            for comment in comments
        ]


class MapperRegistry:
    """Registry for field mappers based on mode."""

    _user_mapper = UserFieldMapper()
    _issue_mapper = IssueFieldMapper()
    _comment_mapper = CommentFieldMapper()

    @classmethod
    def get_user_mapper(cls) -> UserFieldMapper:
        """Get the user field mapper.

        Returns:
            UserFieldMapper instance
        """
        return cls._user_mapper

    @classmethod
    def get_issue_mapper(cls) -> IssueFieldMapper:
        """Get the issue field mapper.

        Returns:
            IssueFieldMapper instance
        """
        return cls._issue_mapper

    @classmethod
    def get_comment_mapper(cls) -> CommentFieldMapper:
        """Get the comment field mapper.

        Returns:
            CommentFieldMapper instance
        """
        return cls._comment_mapper
