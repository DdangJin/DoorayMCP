"""Main entry point for Dooray MCP Server with uvx execution support."""

import asyncio
import os
import sys
import logging
from typing import Optional

def configure_logging() -> None:
    """Configure logging to stderr to avoid stdout pollution for MCP protocol."""
    # Get log level from environment or default to WARNING
    log_level = os.getenv("DOORAY_LOG_LEVEL", "WARNING").upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        stream=sys.stderr,  # Critical: MCP uses stdin/stdout
        force=True,
    )
    
    # Set HTTP client logging level
    http_log_level = os.getenv("DOORAY_HTTP_LOG_LEVEL", "WARNING").upper()
    logging.getLogger("aiohttp").setLevel(getattr(logging, http_log_level, logging.WARNING))

def validate_environment() -> tuple[str, str]:
    """Validate required environment variables."""
    api_key = os.getenv("DOORAY_API_KEY")
    base_url = os.getenv("DOORAY_BASE_URL")
    
    if not api_key:
        print("Error: DOORAY_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)
        
    if not base_url:
        print("Error: DOORAY_BASE_URL environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    return api_key, base_url

async def run_server(transport: str = "stdio", port: Optional[int] = None) -> None:
    """Run the Dooray MCP server with specified transport."""
    configure_logging()
    logger = logging.getLogger(__name__)
    
    # Load environment variables from .env file if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, skip
    
    # Validate environment
    api_key, base_url = validate_environment()
    
    logger.info(f"🚀 Dooray MCP Server v0.1.0 starting with {transport} transport...")
    
    # Import here to avoid circular imports
    from dooray_mcp.server import DoorayMcpServer
    
    server = DoorayMcpServer(api_key=api_key, base_url=base_url)
    
    try:
        if transport == "stdio":
            await server.run_stdio()
        elif transport == "streamable-http":
            await server.run_streamable_http(port or 8000)
        elif transport == "sse":
            await server.run_sse(port or 8001)
        else:
            logger.error(f"Unknown transport: {transport}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

def main() -> None:
    """uvx dooray-mcp entry point (stdio transport)."""
    asyncio.run(run_server(transport="stdio"))

def main_stdio() -> None:
    """uvx dooray-mcp-stdio entry point."""
    asyncio.run(run_server(transport="stdio"))

def main_http() -> None:
    """uvx dooray-mcp-http entry point."""
    asyncio.run(run_server(transport="streamable-http", port=8000))

def main_sse() -> None:
    """uvx dooray-mcp-sse entry point."""
    asyncio.run(run_server(transport="sse", port=8001))

def create_server():
    """MCP server factory function for uvx mcp compatibility."""
    api_key, base_url = validate_environment()
    from dooray_mcp.server import DoorayMcpServer
    return DoorayMcpServer(api_key=api_key, base_url=base_url)

if __name__ == "__main__":
    main()