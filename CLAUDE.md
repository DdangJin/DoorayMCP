# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dooray MCP Server** - a Model Context Protocol server that provides integration with NHN Dooray services. Originally built in Kotlin (now moved to `/old` directory), the project is being **converted to Python** with uvx-based execution, offering 28 tools for managing Wiki pages, projects, tasks, comments, messenger, and calendar functionalities.

## Migration Status

**Current State**: Converting from Kotlin to Python
- **Kotlin Implementation**: Moved to `/old` directory (preserved for reference)
- **Python Implementation**: Being developed with uvx execution model
- **Target**: Full feature parity with enhanced deployment simplicity

## Python Implementation (Current Development)

### uvx Execution (Primary Method)
```bash
# Direct execution from PyPI (when published)
uvx dooray-mcp                    # stdio transport (default)
uvx dooray-mcp-http              # streamable-http transport (port 8000)
uvx dooray-mcp-sse               # sse transport (port 8001)

# Local development execution
uvx --from . dooray-mcp          # from current directory
uvx --from git+https://github.com/user/dooray-mcp-python.git dooray-mcp

# Environment variables
DOORAY_API_KEY=xxx DOORAY_BASE_URL=https://api.dooray.com uvx dooray-mcp
```

### Development Commands
```bash
# Setup and test locally
uv run mcp dev src/dooray_mcp/main.py

# Run tests
uv run pytest

# Lint and format
uv run ruff check
uv run ruff format

# Build package
uv build
```

### Legacy Kotlin Commands (in /old directory)
```bash
# To run old Kotlin version (for reference)
cd old && ./gradlew runLocal
```

## Architecture Overview

### Python Implementation Structure
```
src/
└── dooray_mcp/
    ├── __init__.py
    ├── main.py              # uvx entry points with transport selection
    ├── server.py            # Multi-transport MCP server (stdio/http/sse)
    ├── client/
    │   ├── __init__.py
    │   └── dooray_client.py # aiohttp-based Dooray API client
    ├── tools/
    │   ├── __init__.py      # Dual registration system (lowlevel/fastmcp)
    │   ├── wiki_tools.py    # 8 Wiki management tools
    │   ├── project_tools.py # 7 Project/task management tools  
    │   ├── messenger_tools.py # 7 Messenger tools
    │   └── calendar_tools.py  # 5 Calendar tools
    ├── types/
    │   ├── __init__.py
    │   ├── wiki_types.py    # Pydantic models for Wiki
    │   ├── project_types.py # Pydantic models for Projects
    │   └── common_types.py  # Shared type definitions
    └── exceptions/
        ├── __init__.py
        └── custom_exceptions.py
```

### Legacy Kotlin Structure (in /old directory)
```
old/src/main/kotlin/com/bifos/dooray/mcp/
├── client/           # HTTP client for Dooray API
├── constants/        # Environment variables and version constants
├── exception/        # Custom exceptions and error handling
├── tools/           # 28 MCP tools (Wiki, Project, Task, Messenger, Calendar)
├── types/           # Data classes for API responses
└── utils/           # JSON utilities
```

### Tool Categories
- **Wiki Tools (8)**: Page management, creation, editing
- **Project Tools (7)**: Task management, comments, status updates  
- **Messenger Tools (7)**: Member search, direct messages, channels
- **Calendar Tools (5)**: Events, scheduling, calendar management
- **Utility Tool (1)**: Project listing

## Python Development Guidelines

### Environment Setup
Required environment variables:
- `DOORAY_API_KEY`: Your Dooray API key
- `DOORAY_BASE_URL`: Dooray API base URL (typically https://api.dooray.com)

Optional logging controls:
- `DOORAY_LOG_LEVEL`: DEBUG, INFO, WARN, ERROR (default: WARN)
- `DOORAY_HTTP_LOG_LEVEL`: HTTP client logging level (default: WARN)

### MCP Transport Support

- **Stdio Transport**: Default MCP standard, uses stdin/stdout
- **Streamable HTTP**: HTTP-based transport for web integration
- **SSE Transport**: Server-Sent Events for real-time communication

### Testing Strategy

- Unit tests in `tests/` using pytest
- Integration tests with aioresponses for HTTP mocking
- Transport-specific tests for stdio/http/sse
- uvx execution tests

### Key Technical Considerations

- **MCP Protocol**: Uses stdin/stdout for communication - all logs go to stderr
- **Python Asyncio**: Async operations with proper exception handling
- **aiohttp Client**: HTTP communication with session management
- **Pydantic**: Data validation and serialization
- **uvx Packaging**: Simple execution model without Docker

### Tool Implementation Pattern (Python)

Each tool follows dual registration:

1. **FastMCP decorators** for HTTP transports (`@mcp.tool()`)
2. **Low-level handlers** for stdio transport
3. **Pydantic validation** for input parameters
4. **aiohttp requests** via DoorayHttpClient
5. **Structured responses** with proper error handling

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "dooray": {
      "command": "uvx",
      "args": ["dooray-mcp"],
      "env": {
        "DOORAY_API_KEY": "your_key",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

## Important Notes

- **Python 3.10+ required**: Compatible with Python 3.10 and above
- **uvx execution**: Primary deployment method, no Docker needed
- **Logging to stderr**: Critical for MCP protocol compatibility  
- **Environment-based configuration**: Uses .env file for local development
- **Cross-platform**: Works on macOS, Linux, Windows with uvx