"""Test the HTTP transport functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from dooray_mcp_server.transport.http_server_transport import HttpServerTransport


@pytest.fixture
def transport():
    """Create HTTP transport instance."""
    return HttpServerTransport()


class TestHTTPTransport:
    """Test HTTP transport layer."""

    def test_transport_initialization(self, transport):
        """Test transport initializes correctly."""
        assert transport is not None
        assert transport.host == "127.0.0.1"
        assert transport.port == 8080
        assert transport.path == "/mcp"

    def test_transport_sessions(self, transport):
        """Test session management."""
        assert hasattr(transport, 'sessions')
        assert isinstance(transport.sessions, dict)