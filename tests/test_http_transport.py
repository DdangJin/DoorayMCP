"""Test the HTTP transport functionality."""

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from dooray_mcp_server.transport.http_server_transport import create_app


@pytest.fixture
def mock_server():
    """Create a mock MCP server."""
    server = MagicMock()
    server.handle_request = AsyncMock(return_value={
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"tools": []}
    })
    return server


@pytest.fixture
def app(mock_server):
    """Create FastAPI app for testing."""
    return create_app(mock_server, "/mcp")


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestHTTPTransport:
    """Test HTTP transport layer."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy", 
            "server": "dooray-mcp-server"
        }

    def test_mcp_post_endpoint(self, client):
        """Test MCP POST endpoint."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = client.post(
            "/mcp",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1

    def test_mcp_get_endpoint(self, client):
        """Test MCP GET endpoint returns SSE headers."""
        response = client.get(
            "/mcp",
            headers={"Accept": "text/event-stream"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        assert response.headers["cache-control"] == "no-cache"