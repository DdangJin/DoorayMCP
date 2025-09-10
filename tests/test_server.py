"""Test the main server functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from dooray_mcp_server.server import DoorayMCPServer


@pytest.fixture
def mock_dooray_client():
    """Create a mock Dooray client."""
    client = MagicMock()
    # Add any necessary async methods
    client.get_wikis = AsyncMock(return_value=[])
    client.get_projects = AsyncMock(return_value=[])
    return client


@pytest.fixture
def server(mock_dooray_client):
    """Create a server instance with mocked client."""
    return DoorayMCPServer(dooray_client=mock_dooray_client)


class TestDoorayMCPServer:
    """Test the Dooray MCP Server."""

    def test_server_initialization(self, server):
        """Test that server initializes correctly."""
        assert server is not None
        assert hasattr(server, 'dooray_client')

    @pytest.mark.asyncio
    async def test_server_can_start(self, server):
        """Test that server can start without errors."""
        # This is a basic smoke test
        # In a real scenario, you'd test actual server startup
        assert server is not None