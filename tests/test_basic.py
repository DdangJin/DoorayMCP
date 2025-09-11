"""Basic tests to verify project setup."""

import pytest

from dooray_mcp import DoorayMcpServer


def test_version_import():
    """Test that version can be imported."""
    from dooray_mcp import __version__
    assert __version__ == "0.1.0"


def test_server_creation():
    """Test that server can be created."""
    server = DoorayMcpServer(api_key="test", base_url="https://test.com")
    assert server is not None
    assert server.client is not None


@pytest.mark.asyncio
async def test_server_validation():
    """Test server environment validation."""
    from dooray_mcp.main import validate_environment
    import os
    
    # Save original environment
    original_api_key = os.environ.get("DOORAY_API_KEY")
    original_base_url = os.environ.get("DOORAY_BASE_URL")
    
    try:
        # Set test environment
        os.environ["DOORAY_API_KEY"] = "test_key"
        os.environ["DOORAY_BASE_URL"] = "https://test.com"
        
        api_key, base_url = validate_environment()
        assert api_key == "test_key"
        assert base_url == "https://test.com"
        
    finally:
        # Restore original environment
        if original_api_key:
            os.environ["DOORAY_API_KEY"] = original_api_key
        else:
            os.environ.pop("DOORAY_API_KEY", None)
            
        if original_base_url:
            os.environ["DOORAY_BASE_URL"] = original_base_url
        else:
            os.environ.pop("DOORAY_BASE_URL", None)