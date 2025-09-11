"""SSE (Server-Sent Events) transport implementation for MCP."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, AsyncIterator
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
import structlog
import uvicorn

from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.models import InitializationOptions

logger = structlog.get_logger(__name__)


class SSETransport:
    """SSE-only transport for MCP following specification."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080, path: str = "/mcp"):
        self.host = host
        self.port = port
        self.path = path
        self.sessions: Dict[str, ServerSession] = {}
        self.mcp_server: Optional[Server] = None
        self.app: Optional[FastAPI] = None
        self.server_task: Optional[asyncio.Task] = None

    async def start(self, mcp_server: Server) -> None:
        """Start the SSE server with MCP server integration."""
        self.mcp_server = mcp_server

        # Create FastAPI app
        self.app = FastAPI(
            title="Dooray MCP Server (SSE)",
            description="Dooray MCP Server with SSE Transport",
            version="0.2.1"
        )

        # Add CORS middleware for security
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
            allow_credentials=True,
            allow_methods=["GET", "OPTIONS"],
            allow_headers=["*"],
        )

        # Setup routes
        self.setup_routes()

        # Start server
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)

        logger.info("Starting SSE MCP server", 
                   host=self.host, port=self.port, path=self.path)

        # Run server in background task
        self.server_task = asyncio.create_task(server.serve())

    def setup_routes(self) -> None:
        """Setup HTTP routes for SSE transport."""

        @self.app.get(self.path)
        async def handle_sse(request: Request):
            """Handle SSE connections for MCP communication."""
            return await self._handle_sse_connection(request)

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "server": "dooray-mcp-server-sse"}

    async def _handle_sse_connection(self, request: Request) -> EventSourceResponse:
        """Handle SSE connection following MCP specification."""
        try:
            # Validate Origin header for security
            origin = request.headers.get("origin")
            if origin and not self._is_valid_origin(origin):
                logger.warning("Invalid origin header", origin=origin)
                raise HTTPException(status_code=403, detail="Invalid origin")

            # Create session
            session_id = str(uuid.uuid4())
            session = await self._create_session(session_id)

            logger.info("New SSE connection established", session_id=session_id)

            # Check for Last-Event-ID for stream resumability
            last_event_id = request.headers.get("last-event-id")
            if last_event_id:
                logger.debug("Resuming SSE stream", session_id=session_id, last_event_id=last_event_id)

            async def event_stream():
                """Generate SSE events for MCP communication."""
                try:
                    # Send initial connection event
                    event_id = str(uuid.uuid4())
                    yield {
                        "id": event_id,
                        "event": "connected",
                        "data": json.dumps({
                            "jsonrpc": "2.0",
                            "method": "notifications/initialized",
                            "params": {
                                "sessionId": session_id,
                                "serverInfo": {
                                    "name": "dooray-mcp-server",
                                    "version": "0.2.1"
                                }
                            }
                        })
                    }

                    # Send available tools
                    event_id = str(uuid.uuid4())
                    if hasattr(session.server, '_tool_registry'):
                        tools = []
                        for name, tool_info in session.server._tool_registry.items():
                            tool_def = tool_info['definition']
                            tools.append({
                                "name": name,
                                "description": tool_def.description,
                                "inputSchema": tool_def.inputSchema
                            })
                        
                        yield {
                            "id": event_id,
                            "event": "tools",
                            "data": json.dumps({
                                "jsonrpc": "2.0",
                                "method": "notifications/tools_changed",
                                "params": {
                                    "tools": tools
                                }
                            })
                        }

                    # Keep connection alive and handle messages
                    while session_id in self.sessions:
                        # Send periodic heartbeat
                        event_id = str(uuid.uuid4())
                        yield {
                            "id": event_id,
                            "event": "heartbeat",
                            "data": json.dumps({
                                "type": "heartbeat",
                                "timestamp": asyncio.get_event_loop().time()
                            })
                        }

                        # Check for pending server messages
                        if hasattr(session, 'pending_messages'):
                            while session.pending_messages:
                                message = session.pending_messages.pop(0)
                                event_id = str(uuid.uuid4())
                                yield {
                                    "id": event_id,
                                    "event": "message",
                                    "data": json.dumps(message)
                                }

                        await asyncio.sleep(30)  # 30 second heartbeat

                except Exception as e:
                    logger.error("Error in SSE stream", session_id=session_id, error=str(e))
                finally:
                    # Clean up session
                    if session_id in self.sessions:
                        del self.sessions[session_id]
                    logger.info("SSE connection closed", session_id=session_id)

            return EventSourceResponse(
                event_stream(),
                headers={
                    "Mcp-Session-Id": session_id,
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )

        except Exception as e:
            logger.error("Error handling SSE connection", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    async def _create_session(self, session_id: str) -> ServerSession:
        """Create new MCP session."""
        if not self.mcp_server:
            raise RuntimeError("MCP server not initialized")

        # Create initialization options
        from mcp.server.models import NotificationOptions
        
        init_options = InitializationOptions(
            server_name="dooray-mcp-server",
            server_version="0.2.1",
            capabilities=self.mcp_server.get_capabilities(
                NotificationOptions(), {}
            )
        )

        # Create new session
        session = ServerSession(self.mcp_server, init_options)
        session.pending_messages = []  # Add message queue
        self.sessions[session_id] = session

        logger.debug("Created new SSE session", session_id=session_id)
        return session

    def _is_valid_origin(self, origin: str) -> bool:
        """Validate Origin header to prevent DNS rebinding attacks."""
        try:
            parsed = urlparse(origin)
            hostname = parsed.hostname

            # Allow localhost and 127.0.0.1 origins
            return (
                hostname in ["localhost", "127.0.0.1"] or
                (hostname and hostname.startswith("localhost")) or
                (hostname and hostname.startswith("127.0.0.1"))
            )
        except Exception:
            return False

    async def stop(self) -> None:
        """Stop the SSE server."""
        logger.info("Stopping SSE MCP server")

        # Clean up sessions
        self.sessions.clear()

        # Stop server task
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass