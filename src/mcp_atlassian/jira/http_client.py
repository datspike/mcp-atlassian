"""HTTP client wrapper for Jira API with version normalization.

This module provides utilities to normalize API paths for Server 6.x compatibility,
ensuring all requests use /rest/api/2 endpoints when in server_6x mode.
"""

import logging
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import PreparedRequest, Response

logger = logging.getLogger("mcp-jira")


class APIv2Adapter(HTTPAdapter):
    """HTTP adapter that normalizes API paths to v2 for Server 6.x.

    Intercepts requests and rewrites /rest/api/3 paths to /rest/api/2
    when the client is in server_6x mode.
    """

    def __init__(self, force_v2: bool = False) -> None:
        """Initialize the API v2 adapter.

        Args:
            force_v2: If True, force all /rest/api/3 paths to /rest/api/2
        """
        super().__init__()
        self.force_v2 = force_v2

    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,
        cert: bytes | str | tuple[bytes | str, bytes | str] | None = None,
        proxies: Mapping[str, str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Response:
        """Send request with path normalization.

        Args:
            request: The prepared request
            stream: Whether to stream the response
            timeout: Request timeout
            verify: SSL verification setting
            cert: Client certificate
            proxies: Proxy configuration
            **kwargs: Additional arguments

        Returns:
            The response from the server
        """
        if self.force_v2 and request.url:
            # Normalize /rest/api/3 to /rest/api/2
            if "/rest/api/3/" in request.url:
                normalized_url = request.url.replace("/rest/api/3/", "/rest/api/2/")
                logger.debug(f"Normalizing API path: {request.url} -> {normalized_url}")
                request.url = normalized_url

        return super().send(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
            **kwargs,
        )


def normalize_api_path(url: str, force_v2: bool = False) -> str:
    """Normalize API path to v2 if needed.

    Args:
        url: The original URL
        force_v2: If True, force v2 paths

    Returns:
        Normalized URL
    """
    if force_v2 and "/rest/api/3/" in url:
        return url.replace("/rest/api/3/", "/rest/api/2/")
    return url


def configure_api_version(
    session: Session, base_url: str, force_v2: bool = False
) -> None:
    """Configure session to use API v2 for Server 6.x.

    Args:
        session: The requests session
        base_url: Base URL of the Jira instance
        force_v2: If True, force all requests to use /rest/api/2
    """
    if force_v2:
        logger.info("Configuring Jira client to use API v2 endpoints")
        adapter = APIv2Adapter(force_v2=True)
        # Mount adapter for all HTTPS and HTTP requests
        parsed = urlparse(base_url)
        scheme = parsed.scheme or "https"
        domain = parsed.netloc
        session.mount(f"{scheme}://{domain}", adapter)
