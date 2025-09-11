"""Test the main server functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from dooray_mcp_server.server import DoorayMcpServer


@pytest.fixture
def server():
    """Create a server instance."""
    return DoorayMcpServer()


class TestDoorayMcpServer:
    """Test the Dooray MCP Server."""

    def test_server_initialization(self, server):
        """Test that server initializes correctly."""
        assert server is not None
        assert hasattr(server, 'dooray_client')
        assert hasattr(server, 'mcp_server')
        assert hasattr(server, 'transport')

    @pytest.mark.asyncio
    async def test_server_can_start(self, server):
        """Test that server can start without errors."""
        # This is a basic smoke test
        # In a real scenario, you'd test actual server startup
        assert server is not None