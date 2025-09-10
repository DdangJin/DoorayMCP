"""Main MCP server implementation."""

import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
import structlog

from .client.dooray_http_client import DoorayHttpClient
from .constants import *
from .tools import *
from .transport.http_server_transport import HttpServerTransport

logger = structlog.get_logger(__name__)


class DoorayMcpServer:
    """Main Dooray MCP Server class."""

    def __init__(self):
        self.dooray_client: Optional[DoorayHttpClient] = None
        self.mcp_server: Optional[Server] = None
        self.transport: Optional[HttpServerTransport] = None

    async def start_http_server(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        path: str = DEFAULT_PATH
    ) -> None:
        """Start HTTP MCP server."""
        logger.info("Starting Dooray HTTP MCP server",
                   host=host, port=port, path=path, version=SERVER_VERSION)

        # Initialize environment and clients
        await self._initialize()

        # Create MCP server
        self.mcp_server = Server(SERVER_NAME)

        # Register all tools
        await self._register_tools()

        # Create and start HTTP transport
        self.transport = HttpServerTransport(host, port, path)
        await self.transport.start(self.mcp_server)

        logger.info("Dooray HTTP MCP server started successfully",
                   host=host, port=port, path=path)

    async def start_stdio_server(self) -> None:
        """Start STDIO MCP server (traditional mode)."""
        from mcp.server.stdio import stdio_server

        logger.info("Starting Dooray STDIO MCP server", version=SERVER_VERSION)

        # Initialize environment and clients
        await self._initialize()

        # Create MCP server
        self.mcp_server = Server(SERVER_NAME)

        # Register all tools
        await self._register_tools()

        # Run STDIO server
        async with stdio_server(self.mcp_server) as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream, write_stream,
                self.mcp_server.create_initialization_options()
            )

    async def _initialize(self) -> None:
        """Initialize environment and clients."""
        # Get environment variables
        env = self._get_environment()

        # Initialize Dooray HTTP client
        self.dooray_client = DoorayHttpClient(
            base_url=env[DOORAY_BASE_URL],
            dooray_api_key=env[DOORAY_API_KEY]
        )

        logger.info("Dooray HTTP client initialized",
                   base_url=env[DOORAY_BASE_URL])

    async def _register_tools(self) -> None:
        """Register all MCP tools."""
        if not self.mcp_server or not self.dooray_client:
            raise RuntimeError("Server or client not initialized")

        logger.info("Registering MCP tools...")

        tool_count = 0

        # Wiki tools (5 tools)
        await self._register_tool("dooray_wiki_list_projects", get_wikis_tool(), get_wikis_handler)
        await self._register_tool("dooray_wiki_list_pages", get_wiki_pages_tool(), get_wiki_pages_handler)
        await self._register_tool("dooray_wiki_get_page", get_wiki_page_tool(), get_wiki_page_handler)
        await self._register_tool("dooray_wiki_create_page", create_wiki_page_tool(), create_wiki_page_handler)
        await self._register_tool("dooray_wiki_update_page", update_wiki_page_tool(), update_wiki_page_handler)
        tool_count += 5

        # Project tools (7 tools)
        await self._register_tool("dooray_project_list_projects", get_projects_tool(), get_projects_handler)
        await self._register_tool("dooray_project_list_posts", get_project_posts_tool(), get_project_posts_handler)
        await self._register_tool("dooray_project_get_post", get_project_post_tool(), get_project_post_handler)
        await self._register_tool("dooray_project_create_post", create_project_post_tool(), create_project_post_handler)
        await self._register_tool("dooray_project_update_post", update_project_post_tool(), update_project_post_handler)
        await self._register_tool("dooray_project_set_post_workflow", set_project_post_workflow_tool(), set_project_post_workflow_handler)
        await self._register_tool("dooray_project_set_post_done", set_project_post_done_tool(), set_project_post_done_handler)
        tool_count += 7

        # Comment tools (4 tools)
        await self._register_tool("dooray_project_create_post_comment", create_post_comment_tool(), create_post_comment_handler)
        await self._register_tool("dooray_project_get_post_comments", get_post_comments_tool(), get_post_comments_handler)
        await self._register_tool("dooray_project_update_post_comment", update_post_comment_tool(), update_post_comment_handler)
        await self._register_tool("dooray_project_delete_post_comment", delete_post_comment_tool(), delete_post_comment_handler)
        tool_count += 4

        # Messenger tools (7 tools)
        await self._register_tool("dooray_messenger_search_members", search_members_tool(), search_members_handler)
        await self._register_tool("dooray_messenger_send_direct_message", send_direct_message_tool(), send_direct_message_handler)
        await self._register_tool("dooray_messenger_get_channels", get_channels_tool(), get_channels_handler)
        await self._register_tool("dooray_messenger_get_simple_channels", get_simple_channels_tool(), get_simple_channels_handler)
        await self._register_tool("dooray_messenger_get_channel", get_channel_tool(), get_channel_handler)
        await self._register_tool("dooray_messenger_create_channel", create_channel_tool(), create_channel_handler)
        await self._register_tool("dooray_messenger_send_channel_message", send_channel_message_tool(), send_channel_message_handler)
        tool_count += 7

        # Calendar tools (5 tools)
        await self._register_tool("dooray_calendar_list", get_calendars_tool(), get_calendars_handler)
        await self._register_tool("dooray_calendar_detail", get_calendar_detail_tool(), get_calendar_detail_handler)
        await self._register_tool("dooray_calendar_events", get_calendar_events_tool(), get_calendar_events_handler)
        await self._register_tool("dooray_calendar_event_detail", get_calendar_event_detail_tool(), get_calendar_event_detail_handler)
        await self._register_tool("dooray_calendar_create_event", create_calendar_event_tool(), create_calendar_event_handler)
        tool_count += 5

        logger.info("Successfully registered MCP tools", tool_count=tool_count)

    async def _register_tool(self, name: str, tool: Any, handler: Any) -> None:
        """Register a single MCP tool."""
        if not self.mcp_server or not self.dooray_client:
            raise RuntimeError("Server or client not initialized")

        # Create handler wrapper that passes dooray_client
        async def tool_handler(arguments: Dict[str, Any]):
            return await handler(self.dooray_client, arguments)

        # Register tool with MCP server
        if not hasattr(self.mcp_server, '_tools'):
            self.mcp_server._tools = {}

        self.mcp_server._tools[name] = {
            "description": tool.description,
            "inputSchema": tool.inputSchema,
            "handler": tool_handler
        }

    def _get_environment(self) -> Dict[str, str]:
        """Get required environment variables."""
        base_url = os.getenv(DOORAY_BASE_URL)
        if not base_url:
            raise ValueError(f"{DOORAY_BASE_URL} environment variable is required")

        api_key = os.getenv(DOORAY_API_KEY)
        if not api_key:
            raise ValueError(f"{DOORAY_API_KEY} environment variable is required")

        return {
            DOORAY_BASE_URL: base_url,
            DOORAY_API_KEY: api_key
        }

    async def stop(self) -> None:
        """Stop the server."""
        logger.info("Stopping Dooray MCP server...")

        if self.transport:
            await self.transport.stop()

        if self.dooray_client:
            await self.dooray_client.__aexit__(None, None, None)

        logger.info("Dooray MCP server stopped")
