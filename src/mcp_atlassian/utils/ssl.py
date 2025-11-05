"""SSL-related utility functions for MCP Atlassian."""

import logging
import os
import ssl
from typing import Any
from urllib.parse import urlparse

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from urllib3.poolmanager import PoolManager

logger = logging.getLogger("mcp-atlassian")


class SSLIgnoreAdapter(HTTPAdapter):
    """HTTP adapter that ignores SSL verification.

    A custom transport adapter that disables SSL certificate verification for specific domains.
    This implementation ensures that both verify_mode is set to CERT_NONE and check_hostname
    is disabled, which is required for properly ignoring SSL certificates.

    This adapter also enables legacy SSL renegotiation which may be required for some older servers.
    Note that this reduces security and should only be used when absolutely necessary.
    """

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        """Initialize the connection pool manager with SSL verification disabled.

        This method is called when the adapter is created, and it's the proper place to
        disable SSL verification completely.

        Args:
            connections: Number of connections to save in the pool
            maxsize: Maximum number of connections in the pool
            block: Whether to block when the pool is full
            pool_kwargs: Additional arguments for the pool manager
        """
        # Configure SSL context to disable verification completely
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Enable legacy SSL renegotiation
        context.options |= 0x4  # SSL_OP_LEGACY_SERVER_CONNECT
        context.options |= 0x40000  # SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs,
        )

    def cert_verify(self, conn: Any, url: str, verify: bool, cert: Any | None) -> None:
        """Override cert verification to disable SSL verification.

        This method is still included for backward compatibility, but the main
        SSL disabling happens in init_poolmanager.

        Args:
            conn: The connection
            url: The URL being requested
            verify: The original verify parameter (ignored)
            cert: Client certificate path
        """
        super().cert_verify(conn, url, verify=False, cert=cert)


def configure_ssl_verification(
    service_name: str,
    url: str,
    session: Session,
    ssl_verify: bool,
    client_cert: str | None = None,
    client_key: str | None = None,
    client_key_password: str | None = None,
    ca_file: str | None = None,
) -> None:
    """Configure SSL verification and client certificates for a specific service.

    If SSL verification is disabled, this function will configure the session
    to use a custom SSL adapter that bypasses certificate validation for the
    service's domain.

    If client certificate paths are provided, they will be configured for
    mutual TLS authentication.

    If a CA file is provided, it will be used to verify SSL certificates.
    The CA file can be specified via environment variable (e.g., JIRA_TLS_INSECURE)
    or passed directly as a parameter.

    Args:
        service_name: Name of the service for logging (e.g., "Confluence", "Jira")
        url: The base URL of the service
        session: The requests session to configure
        ssl_verify: Whether SSL verification should be enabled
        client_cert: Path to client certificate file (.pem)
        client_key: Path to client private key file (.pem)
        client_key_password: Password for encrypted private key (optional)
        ca_file: Optional path to CA bundle file for SSL verification
    """
    # Configure client certificate if provided (must be actual string paths)
    if isinstance(client_cert, str) and isinstance(client_key, str):
        # Encrypted private keys are not supported by the requests library
        if isinstance(client_key_password, str) and client_key_password:
            raise ValueError(
                f"{service_name} client certificate authentication with encrypted "
                "private keys is not supported. Please decrypt your private key first "
                "(e.g., using 'openssl rsa -in encrypted.key -out decrypted.key')."
            )

        # Set the client certificate on the session
        session.cert = (client_cert, client_key)
        logger.info(
            f"{service_name} client certificate authentication configured "
            f"with cert: {client_cert}"
        )

    # Check for TLS insecure flag (default: false/secure)
    tls_insecure_env = os.getenv(
        f"{service_name.upper()}_TLS_INSECURE", "false"
    ).lower()
    if tls_insecure_env in ("true", "1", "yes"):
        ssl_verify = False
        logger.warning(
            f"{service_name} TLS verification disabled via {service_name.upper()}_TLS_INSECURE. "
            "This is insecure and should only be used in testing environments."
        )

    if not ssl_verify:
        # Get the domain from the configured URL
        domain = urlparse(url).netloc

        # Mount the adapter to handle requests to this domain
        adapter = SSLIgnoreAdapter()
        session.mount(f"https://{domain}", adapter)
        session.mount(f"http://{domain}", adapter)
    elif ca_file:
        # Use custom CA bundle if provided
        if not os.path.exists(ca_file):
            logger.warning(
                f"CA file specified for {service_name} does not exist: {ca_file}. "
                "Falling back to default SSL verification."
            )
        else:
            logger.info(f"Using custom CA bundle for {service_name}: {ca_file}")
            session.verify = ca_file
