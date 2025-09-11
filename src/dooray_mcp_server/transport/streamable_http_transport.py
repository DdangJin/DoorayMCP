"""Streamable HTTP transport implementation for MCP following official specification."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, AsyncIterator
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
import structlog
import uvicorn

from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.models import InitializationOptions

logger = structlog.get_logger(__name__)


class StreamableHttpTransport:
    """Streamable HTTP transport for MCP following official specification."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080, path: str = "/mcp"):
        self.host = host
        self.port = port
        self.path = path
        self.sessions: Dict[str, ServerSession] = {}
        self.mcp_server: Optional[Server] = None
        self.app: Optional[FastAPI] = None
        self.server_task: Optional[asyncio.Task] = None

    async def start(self, mcp_server: Server) -> None:
        """Start the streamable HTTP server with MCP server integration."""
        self.mcp_server = mcp_server

        # Create FastAPI app
        self.app = FastAPI(
            title="Dooray MCP Server",
            description="Dooray MCP Server with Streamable HTTP Transport",
            version="0.2.1"
        )

        # Add CORS middleware for security
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
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

        logger.info("Starting Streamable HTTP MCP server", 
                   host=self.host, port=self.port, path=self.path)

        # Run server in background task
        self.server_task = asyncio.create_task(server.serve())

    def setup_routes(self) -> None:
        """Setup HTTP routes for MCP protocol."""

        @self.app.post(self.path)
        async def handle_post(request: Request, response: Response):
            """Handle POST requests for MCP messages."""
            return await self._handle_post_request(request, response)

        @self.app.get(self.path)
        async def handle_get(request: Request):
            """Handle GET requests for SSE streaming."""
            return await self._handle_get_request(request)

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "server": "dooray-mcp-server"}

    async def _handle_post_request(self, request: Request, response: Response) -> Any:
        """Handle POST requests with MCP messages following specification."""
        try:
            # Validate Origin header for security
            origin = request.headers.get("origin")
            if origin and not self._is_valid_origin(origin):
                logger.warning("Invalid origin header", origin=origin)
                raise HTTPException(status_code=403, detail="Invalid origin")

            # Get or create session
            session_id = self._get_or_create_session_id(request)
            response.headers["Mcp-Session-Id"] = session_id

            # Parse request body
            body = await request.body()
            message = json.loads(body.decode('utf-8'))

            logger.debug("Received POST request", session_id=session_id, message=message)

            # Get or create session
            session = await self._get_or_create_session(session_id)

            # Process message through MCP session
            result_message = await session.handle_message(message)

            # Check if client accepts streaming response
            accept_header = request.headers.get("accept", "")
            if "text/event-stream" in accept_header and result_message.get("id"):
                # Return streaming response with proper SSE format
                return await self._create_sse_response(session_id, result_message)
            else:
                # Return simple JSON response with 202 for notifications
                if "id" not in message:  # Notification
                    response.status_code = 202
                    return {}
                else:
                    return result_message

        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON request", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid JSON")
        except Exception as e:
            logger.error("Error handling POST request", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    async def _handle_get_request(self, request: Request) -> EventSourceResponse:
        """Handle GET requests for SSE streaming following MCP specification."""
        try:
            session_id = self._get_or_create_session_id(request)
            session = await self._get_or_create_session(session_id)

            logger.debug("Starting SSE stream", session_id=session_id)

            # Check for Last-Event-ID for stream resumability
            last_event_id = request.headers.get("last-event-id")
            if last_event_id:
                logger.debug("Resuming SSE stream", session_id=session_id, last_event_id=last_event_id)

            async def event_stream():
                """Generate SSE events following MCP specification."""
                try:
                    # Send initial connection event with proper ID
                    event_id = str(uuid.uuid4())
                    yield {
                        "id": event_id,
                        "event": "message",
                        "data": json.dumps({
                            "jsonrpc": "2.0",
                            "method": "notifications/connection",
                            "params": {
                                "type": "connection_established",
                                "sessionId": session_id
                            }
                        })
                    }

                    # Keep connection alive and handle server requests
                    while session_id in self.sessions:
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

                        await asyncio.sleep(1)  # Polling interval

                except Exception as e:
                    logger.error("Error in event stream", session_id=session_id, error=str(e))
                finally:
                    # Clean up session
                    if session_id in self.sessions:
                        del self.sessions[session_id]
                    logger.debug("SSE stream ended", session_id=session_id)

            return EventSourceResponse(
                event_stream(),
                headers={
                    "Mcp-Session-Id": session_id,
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )

        except Exception as e:
            logger.error("Error handling GET request", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    async def _create_sse_response(self, session_id: str, message: Dict[str, Any]) -> StreamingResponse:
        """Create SSE response with proper formatting."""
        async def stream_generator():
            """Generate SSE stream with proper format."""
            event_id = str(uuid.uuid4())
            
            # Format as proper SSE event
            yield f"id: {event_id}\n"
            yield f"event: message\n"
            yield f"data: {json.dumps(message)}\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Mcp-Session-Id": session_id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    def _get_or_create_session_id(self, request: Request) -> str:
        """Get existing session ID or create new one."""
        session_id = request.headers.get("mcp-session-id")
        
        if session_id and session_id in self.sessions:
            return session_id

        # Create new session ID
        return str(uuid.uuid4())

    async def _get_or_create_session(self, session_id: str) -> ServerSession:
        """Get existing session or create new one."""
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Create new MCP session
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
        self.sessions[session_id] = session

        logger.debug("Created new MCP session", session_id=session_id)
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
        """Stop the HTTP server."""
        logger.info("Stopping Streamable HTTP MCP server")

        # Clean up sessions
        for session in self.sessions.values():
            # Clean up session if needed
            pass
        self.sessions.clear()

        # Stop server task
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass