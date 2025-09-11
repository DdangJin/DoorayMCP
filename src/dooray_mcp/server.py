"""Dooray MCP Server implementation with multi-transport support."""

import logging
from typing import Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from dooray_mcp.client.dooray_client import DoorayHttpClient


class DoorayMcpServer:
    """Dooray MCP Server with support for stdio, HTTP, and SSE transports."""

    def __init__(self, api_key: str, base_url: str) -> None:
        """Initialize the Dooray MCP Server.
        
        Args:
            api_key: Dooray API key
            base_url: Dooray API base URL
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize HTTP client
        self.client = DoorayHttpClient(base_url=base_url, api_key=api_key)
        
        # Initialize servers for different transports
        self._init_servers()
        
        # Register tools for both server types
        self._register_tools()

    def _init_servers(self) -> None:
        """Initialize both low-level and FastMCP servers."""
        # Low-level server for stdio transport
        self.server = Server("dooray-mcp-server")
        
        # FastMCP server for HTTP transports
        self.fastmcp = FastMCP(
            "dooray-mcp-server",
            streamable_http_path="/mcp"
        )

    def _register_tools(self) -> None:
        """Register tools for both server implementations."""
        # Import here to avoid circular imports
        from dooray_mcp.tools import register_lowlevel_tools, register_fastmcp_tools
        
        # Register tools for low-level server (stdio)
        register_lowlevel_tools(self.server, self.client)
        
        # Register tools for FastMCP server (HTTP/SSE)
        register_fastmcp_tools(self.fastmcp, self.client)
        
        self.logger.info("Successfully registered 28 tools for all transports")

    async def run_stdio(self) -> None:
        """Run server with stdio transport (MCP standard)."""
        self.logger.info("Starting MCP server with stdio transport...")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dooray-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    async def run_streamable_http(self, port: int = 8000) -> None:
        """Run server with streamable HTTP transport.
        
        Args:
            port: Port to bind the HTTP server
        """
        self.logger.info(f"Starting MCP server with streamable-http transport on port {port}...")
        await self.fastmcp.run(transport="streamable-http", port=port)

    async def run_sse(self, port: int = 8001) -> None:
        """Run server with SSE transport.
        
        Args:
            port: Port to bind the SSE server
        """
        self.logger.info(f"Starting MCP server with SSE transport on port {port}...")
        await self.fastmcp.run(transport="sse", port=port)