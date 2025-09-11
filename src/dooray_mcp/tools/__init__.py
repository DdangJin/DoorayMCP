"""Dooray MCP tools module with dual registration system."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.lowlevel import Server
    from dooray_mcp.client.dooray_client import DoorayHttpClient


def register_lowlevel_tools(server: "Server", client: "DoorayHttpClient") -> None:
    """Register tools for low-level server (stdio transport).
    
    Args:
        server: Low-level MCP server instance
        client: Dooray HTTP client
    """
    # TODO: Implement low-level tool registration
    # This will be implemented with @server.list_tools() and @server.call_tool() decorators
    pass


def register_fastmcp_tools(mcp: "FastMCP", client: "DoorayHttpClient") -> None:
    """Register tools for FastMCP server (HTTP/SSE transports).
    
    Args:
        mcp: FastMCP server instance
        client: Dooray HTTP client
    """
    # TODO: Implement FastMCP tool registration
    # This will be implemented with @mcp.tool() decorators
    pass