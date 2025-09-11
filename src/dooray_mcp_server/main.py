"""Main entry point for Dooray MCP server (STDIO mode)."""

import asyncio
import os
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv

from .constants import *
from .server import DoorayMcpServer


def configure_logging():
    """Configure structured logging."""
    log_level = os.getenv(DOORAY_LOG_LEVEL, DEFAULT_LOG_LEVEL).upper()

    # Map string levels to logging levels
    import logging
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }

    level = level_mapping.get(log_level, logging.WARNING)

    # Configure Python logging first
    import logging
    logging.basicConfig(level=level, format='%(message)s')
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


async def main():
    """Main entry point for STDIO MCP server."""
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        print(f"📄 Loaded environment variables from {env_file}", file=sys.stderr)

    # Configure logging
    configure_logging()

    logger = structlog.get_logger(__name__)
    logger.info("🚀 Starting Dooray MCP Server (STDIO mode)", version=SERVER_VERSION)

    try:
        # Create and start server
        server = DoorayMcpServer()
        await server.start_stdio_server()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error("Failed to start server", error=str(e))
        sys.exit(1)


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
