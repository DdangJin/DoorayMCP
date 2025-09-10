"""Main entry point for Dooray MCP server (HTTP mode)."""

import argparse
import asyncio
import os
import signal
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv

from .constants import *
from .server import DoorayMcpServer


def configure_logging():
    """Configure structured logging."""
    log_level = os.getenv(DOORAY_LOG_LEVEL, DEFAULT_LOG_LEVEL).upper()
    
    # Map string levels to structlog levels
    level_mapping = {
        "DEBUG": structlog.stdlib.DEBUG,
        "INFO": structlog.stdlib.INFO,
        "WARN": structlog.stdlib.WARNING,
        "WARNING": structlog.stdlib.WARNING,
        "ERROR": structlog.stdlib.ERROR
    }
    
    level = level_mapping.get(log_level, structlog.stdlib.WARNING)
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        level=level,
        cache_logger_on_first_use=True,
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dooray MCP Server with Streamable HTTP Transport"
    )
    
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind to (default: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help=f"MCP endpoint path (default: {DEFAULT_PATH})"
    )
    
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to .env file (default: .env)"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point for HTTP MCP server."""
    args = parse_arguments()
    
    # Load environment variables from .env file if it exists
    if args.env_file.exists():
        load_dotenv(args.env_file)
        print(f"📄 Loaded environment variables from {args.env_file}", file=sys.stderr)
    
    # Configure logging
    configure_logging()
    
    logger = structlog.get_logger(__name__)
    logger.info("🚀 Starting Dooray HTTP MCP Server", 
               version=SERVER_VERSION,
               host=args.host,
               port=args.port,
               path=args.path)
    
    # Create server instance
    server = DoorayMcpServer()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal", signal=signum)
        asyncio.create_task(server.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start HTTP server
        await server.start_http_server(
            host=args.host,
            port=args.port,
            path=args.path
        )
        
        # Keep the server running
        logger.info("🌐 Server is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error("Failed to start server", error=str(e))
        sys.exit(1)
    finally:
        await server.stop()


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 HTTP server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()