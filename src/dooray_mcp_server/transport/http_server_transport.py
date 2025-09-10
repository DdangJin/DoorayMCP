"""HTTP server transport implementation for MCP streamable HTTP protocol."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional, Set
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
import structlog
import uvicorn

from mcp.server import Server

logger = structlog.get_logger(__name__)


class HttpServerTransport:
    """HTTP server transport for MCP streamable HTTP protocol."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, path: str = "/mcp"):
        self.host = host
        self.port = port
        self.path = path
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.mcp_server: Optional[Server] = None
        self.app: Optional[FastAPI] = None
        
    async def start(self, mcp_server: Server) -> None:
        """Start the HTTP server with MCP server integration."""
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
        
        logger.info("Starting HTTP MCP server", host=self.host, port=self.port, path=self.path)
        
        # Run server in background task
        asyncio.create_task(server.serve())
        
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
        """Handle POST requests with MCP messages."""
        try:
            # Validate Origin header for security
            origin = request.headers.get("origin")
            if origin and not self._is_valid_origin(origin):
                logger.warning("Invalid origin header", origin=origin)
                raise HTTPException(status_code=403, detail="Invalid origin")
            
            # Get or create session
            session_id = self._get_or_create_session(request)
            response.headers["Mcp-Session-Id"] = session_id
            
            # Parse request body
            body = await request.body()
            message = json.loads(body.decode('utf-8'))
            
            logger.debug("Received POST request", session_id=session_id, message=message)
            
            # Process message with MCP server
            if self.mcp_server:
                result = await self._process_mcp_message(message)
                
                # Check if client accepts streaming response
                accept_header = request.headers.get("accept", "")
                if "text/event-stream" in accept_header:
                    # Return streaming response
                    return await self._create_streaming_response(session_id, result)
                else:
                    # Return simple JSON response
                    return result
            else:
                raise HTTPException(status_code=500, detail="MCP server not initialized")
                
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON request", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid JSON")
        except Exception as e:
            logger.error("Error handling POST request", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_get_request(self, request: Request) -> StreamingResponse:
        """Handle GET requests for SSE streaming."""
        try:
            session_id = self._get_or_create_session(request)
            
            logger.debug("Starting SSE stream", session_id=session_id)
            
            async def event_stream():
                """Generate SSE events."""
                try:
                    # Send initial connection message
                    yield {
                        "event": "connected",
                        "data": json.dumps({
                            "type": "connection",
                            "sessionId": session_id,
                            "message": "MCP server connected"
                        })
                    }
                    
                    # Keep connection alive with periodic heartbeats
                    while session_id in self.sessions:
                        await asyncio.sleep(30)  # 30 second heartbeat
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({
                                "type": "heartbeat",
                                "timestamp": asyncio.get_event_loop().time()
                            })
                        }
                        
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
    
    async def _process_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP message and return response."""
        try:
            if not self.mcp_server:
                raise ValueError("MCP server not initialized")
            
            # Handle different MCP message types
            method = message.get("method")
            
            if method == "tools/list":
                # List available tools
                tools = []
                for tool_name, tool_info in self.mcp_server._tools.items():
                    tools.append({
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "inputSchema": tool_info.get("inputSchema", {})
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "tools": tools
                    }
                }
                
            elif method == "tools/call":
                # Call a tool
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.mcp_server._tools:
                    tool_handler = self.mcp_server._tools[tool_name]["handler"]
                    result = await tool_handler(arguments)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {
                            "content": result
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                    
            elif method == "initialize":
                # Initialize MCP session
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                        },
                        "serverInfo": {
                            "name": "dooray-mcp-server",
                            "version": "0.2.1"
                        }
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error("Error processing MCP message", error=str(e))
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _create_streaming_response(self, session_id: str, result: Dict[str, Any]) -> StreamingResponse:
        """Create streaming response with result."""
        async def stream_generator():
            """Generate streaming response."""
            # Send the result as SSE
            yield f"data: {json.dumps(result)}\n\n"
            
            # Send end of stream marker
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={
                "Mcp-Session-Id": session_id,
                "Cache-Control": "no-cache"
            }
        )
    
    def _get_or_create_session(self, request: Request) -> str:
        """Get existing session or create new one."""
        session_id = request.headers.get("mcp-session-id")
        
        if session_id and session_id in self.sessions:
            return session_id
        
        # Create new session
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": asyncio.get_event_loop().time(),
            "last_activity": asyncio.get_event_loop().time()
        }
        
        logger.debug("Created new session", session_id=session_id)
        return session_id
    
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
        logger.info("Stopping HTTP MCP server")
        
        # Clean up sessions
        self.sessions.clear()
        
        # The server will be stopped by the uvicorn server lifecycle