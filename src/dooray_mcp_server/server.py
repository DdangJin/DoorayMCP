"""Main MCP server implementation."""

import os
from typing import Any, Dict, List, Optional, Callable

from mcp.server import Server
from mcp.types import Tool, CallToolResult, TextContent
from mcp.server.session import ServerSession
from mcp.server.models import InitializationOptions
import structlog

from .client.dooray_http_client import DoorayHttpClient
from .constants import *
from .tools import *
from .transport.http_server_transport import HttpServerTransport
from .transport.streamable_http_transport import StreamableHttpTransport
from .transport.sse_transport import SSETransport

logger = structlog.get_logger(__name__)


class DoorayMcpServer:
    """Main Dooray MCP Server class."""

    def __init__(self):
        self.dooray_client: Optional[DoorayHttpClient] = None
        self.mcp_server: Optional[Server] = None
        self.transport: Optional[Any] = None

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

        # Register all tools using standard MCP SDK approach
        await self._register_mcp_tools()

        # Setup tool and list handlers
        self._setup_mcp_handlers()

        # Create and start HTTP transport
        self.transport = HttpServerTransport(host, port, path)
        await self.transport.start(self.mcp_server)

        logger.info("Dooray HTTP MCP server started successfully",
                   host=host, port=port, path=path)

    async def start_streamable_http_server(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        path: str = DEFAULT_PATH
    ) -> None:
        """Start Streamable HTTP MCP server (MCP standard compliant)."""
        logger.info("Starting Dooray Streamable HTTP MCP server",
                   host=host, port=port, path=path, version=SERVER_VERSION)

        # Initialize environment and clients
        await self._initialize()

        # Create MCP server
        self.mcp_server = Server(SERVER_NAME)

        # Register all tools using standard MCP SDK approach
        await self._register_mcp_tools()

        # Setup tool and list handlers
        self._setup_mcp_handlers()

        # Create and start Streamable HTTP transport
        self.transport = StreamableHttpTransport(host, port, path)
        await self.transport.start(self.mcp_server)

        logger.info("Dooray Streamable HTTP MCP server started successfully",
                   host=host, port=port, path=path)

    async def start_sse_server(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        path: str = DEFAULT_PATH
    ) -> None:
        """Start SSE MCP server."""
        logger.info("Starting Dooray SSE MCP server",
                   host=host, port=port, path=path, version=SERVER_VERSION)

        # Initialize environment and clients
        await self._initialize()

        # Create MCP server
        self.mcp_server = Server(SERVER_NAME)

        # Register all tools using standard MCP SDK approach
        await self._register_mcp_tools()

        # Setup tool and list handlers
        self._setup_mcp_handlers()

        # Create and start SSE transport
        self.transport = SSETransport(host, port, path)
        await self.transport.start(self.mcp_server)

        logger.info("Dooray SSE MCP server started successfully",
                   host=host, port=port, path=path)

    async def start_stdio_server(self) -> None:
        """Start STDIO MCP server using standard MCP SDK."""
        from mcp.server.stdio import stdio_server

        logger.info("Starting Dooray STDIO MCP server", version=SERVER_VERSION)

        # Initialize environment and clients
        await self._initialize()

        # Create MCP server with proper capabilities
        self.mcp_server = Server(SERVER_NAME)

        # Register all tools using standard MCP SDK approach
        await self._register_mcp_tools()

        # Setup tool and list handlers
        self._setup_mcp_handlers()

        # Create initialization options
        from mcp.server.models import NotificationOptions
        
        init_options = InitializationOptions(
            server_name=SERVER_NAME,
            server_version=SERVER_VERSION,
            capabilities=self.mcp_server.get_capabilities(
                NotificationOptions(), {}
            )
        )

        # Run STDIO server
        async with stdio_server(self.mcp_server) as (read_stream, write_stream):
            await self.mcp_server.run(read_stream, write_stream, init_options)

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

    async def _register_mcp_tools(self) -> None:
        """Register all MCP tools using standard MCP SDK approach."""
        if not self.mcp_server or not self.dooray_client:
            raise RuntimeError("Server or client not initialized")

        logger.info("Registering MCP tools...")

        tool_count = 0

        # Wiki tools (5 tools)
        self._register_mcp_tool("dooray_wiki_list_projects", get_wikis_tool(), get_wikis_handler)
        self._register_mcp_tool("dooray_wiki_list_pages", get_wiki_pages_tool(), get_wiki_pages_handler)
        self._register_mcp_tool("dooray_wiki_get_page", get_wiki_page_tool(), get_wiki_page_handler)
        self._register_mcp_tool("dooray_wiki_create_page", create_wiki_page_tool(), create_wiki_page_handler)
        self._register_mcp_tool("dooray_wiki_update_page", update_wiki_page_tool(), update_wiki_page_handler)
        tool_count += 5

        # Project tools (7 tools)
        self._register_mcp_tool("dooray_project_list_projects", get_projects_tool(), get_projects_handler)
        self._register_mcp_tool("dooray_project_list_posts", get_project_posts_tool(), get_project_posts_handler)
        self._register_mcp_tool("dooray_project_get_post", get_project_post_tool(), get_project_post_handler)
        self._register_mcp_tool("dooray_project_create_post", create_project_post_tool(), create_project_post_handler)
        self._register_mcp_tool("dooray_project_update_post", update_project_post_tool(), update_project_post_handler)
        self._register_mcp_tool("dooray_project_set_post_workflow", set_project_post_workflow_tool(), set_project_post_workflow_handler)
        self._register_mcp_tool("dooray_project_set_post_done", set_project_post_done_tool(), set_project_post_done_handler)
        tool_count += 7

        # Comment tools (4 tools)
        self._register_mcp_tool("dooray_project_create_post_comment", create_post_comment_tool(), create_post_comment_handler)
        self._register_mcp_tool("dooray_project_get_post_comments", get_post_comments_tool(), get_post_comments_handler)
        self._register_mcp_tool("dooray_project_update_post_comment", update_post_comment_tool(), update_post_comment_handler)
        self._register_mcp_tool("dooray_project_delete_post_comment", delete_post_comment_tool(), delete_post_comment_handler)
        tool_count += 4

        # Messenger tools (7 tools)
        self._register_mcp_tool("dooray_messenger_search_members", search_members_tool(), search_members_handler)
        self._register_mcp_tool("dooray_messenger_send_direct_message", send_direct_message_tool(), send_direct_message_handler)
        self._register_mcp_tool("dooray_messenger_get_channels", get_channels_tool(), get_channels_handler)
        self._register_mcp_tool("dooray_messenger_get_simple_channels", get_simple_channels_tool(), get_simple_channels_handler)
        self._register_mcp_tool("dooray_messenger_get_channel", get_channel_tool(), get_channel_handler)
        self._register_mcp_tool("dooray_messenger_create_channel", create_channel_tool(), create_channel_handler)
        self._register_mcp_tool("dooray_messenger_send_channel_message", send_channel_message_tool(), send_channel_message_handler)
        tool_count += 7

        # Calendar tools (5 tools)
        self._register_mcp_tool("dooray_calendar_list", get_calendars_tool(), get_calendars_handler)
        self._register_mcp_tool("dooray_calendar_detail", get_calendar_detail_tool(), get_calendar_detail_handler)
        self._register_mcp_tool("dooray_calendar_events", get_calendar_events_tool(), get_calendar_events_handler)
        self._register_mcp_tool("dooray_calendar_event_detail", get_calendar_event_detail_tool(), get_calendar_event_detail_handler)
        self._register_mcp_tool("dooray_calendar_create_event", create_calendar_event_tool(), create_calendar_event_handler)
        tool_count += 5

        logger.info("Successfully registered MCP tools", tool_count=tool_count)

    def _register_mcp_tool(self, name: str, tool_def: Any, handler: Callable) -> None:
        """Register a single MCP tool using standard MCP SDK approach."""
        if not self.mcp_server or not self.dooray_client:
            raise RuntimeError("Server or client not initialized")

        # Create tool wrapper for this specific tool
        async def tool_wrapper(arguments: Dict[str, Any]) -> CallToolResult:
            try:
                result = await handler(self.dooray_client, arguments)
                
                # Convert result to proper MCP format
                if isinstance(result, str):
                    content = [TextContent(type="text", text=result)]
                elif isinstance(result, list):
                    content = result
                else:
                    content = [TextContent(type="text", text=str(result))]
                
                return CallToolResult(content=content)
            except Exception as e:
                logger.error("Tool execution failed", tool=name, error=str(e))
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

        # Store tool registration info for later use
        if not hasattr(self, '_tool_registry'):
            self._tool_registry = {}
        
        self._tool_registry[name] = {
            'definition': tool_def,
            'handler': tool_wrapper
        }

    def _setup_mcp_handlers(self) -> None:
        """Setup MCP server handlers for tools and lists."""
        if not self.mcp_server:
            raise RuntimeError("MCP server not initialized")

        # Setup list_tools handler
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            tools = []
            if hasattr(self, '_tool_registry'):
                for name, tool_info in self._tool_registry.items():
                    tool_def = tool_info['definition']
                    tools.append(Tool(
                        name=name,
                        description=tool_def.description,
                        inputSchema=tool_def.inputSchema
                    ))
            return tools

        # Setup call_tool handler
        @self.mcp_server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            if hasattr(self, '_tool_registry') and name in self._tool_registry:
                handler = self._tool_registry[name]['handler']
                return await handler(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                )

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
