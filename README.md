# Dooray MCP Server (Python)

A Model Context Protocol server that provides integration with NHN Dooray services. Originally built in Kotlin, now reimplemented in Python with enhanced deployment simplicity through uvx.

## Features

- **28 MCP Tools** for complete Dooray integration:
  - **Wiki Tools (8)**: Page management, creation, editing
  - **Project Tools (7)**: Task management, comments, status updates  
  - **Messenger Tools (7)**: Member search, direct messages, channels
  - **Calendar Tools (5)**: Events, scheduling, calendar management
  - **Utility Tool (1)**: Project listing

- **Multi-Transport Support**:
  - **Stdio**: Default MCP standard (stdin/stdout)
  - **Streamable HTTP**: HTTP-based transport for web integration
  - **SSE**: Server-Sent Events for real-time communication

- **Simple Deployment**: No Docker required, just uvx

## Quick Start

### Prerequisites

- Python 3.10 or higher
- uvx installed (`pip install uvx` or `pipx install uvx`)

### Installation & Usage

```bash
# Set required environment variables
export DOORAY_API_KEY="your_dooray_api_key"
export DOORAY_BASE_URL="https://api.dooray.com"

# Run with different transports
uvx dooray-mcp                    # stdio transport (default)
uvx dooray-mcp-http              # streamable-http transport (port 8000)
uvx dooray-mcp-sse               # sse transport (port 8001)
```

### Local Development

```bash
# Clone repository
git clone https://github.com/sungmin-koo-ai/DoorayMCP.git
cd DoorayMCP

# Copy and configure environment
cp .env.example .env
# Edit .env with your API credentials

# Install in development mode
uv add --dev .

# Run locally
uvx --from . dooray-mcp

# Run tests
uv run pytest

# Lint code
uv run ruff check
uv run ruff format
```

## Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "dooray": {
      "command": "uvx",
      "args": ["dooray-mcp"],
      "env": {
        "DOORAY_API_KEY": "your_api_key",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DOORAY_API_KEY` | Your Dooray API key | Yes |
| `DOORAY_BASE_URL` | Dooray API base URL | Yes |
| `DOORAY_LOG_LEVEL` | Logging level (DEBUG, INFO, WARN, ERROR) | No (default: WARN) |
| `DOORAY_HTTP_LOG_LEVEL` | HTTP client logging level | No (default: WARN) |

## Available Tools

### Wiki Management (8 tools)
- `dooray_wiki_list_projects` - List accessible Wiki projects
- `dooray_wiki_list_pages` - List pages in a Wiki project
- `dooray_wiki_get_page` - Get detailed page information
- `dooray_wiki_create_page` - Create new Wiki page
- `dooray_wiki_update_page` - Update existing page
- `dooray_wiki_update_page_title` - Update page title only
- `dooray_wiki_update_page_content` - Update page content only
- `dooray_wiki_update_page_referrers` - Update page referrers

### Project & Task Management (7 tools)
- `dooray_project_list_projects` - List accessible projects
- `dooray_project_list_posts` - List tasks in a project
- `dooray_project_get_post` - Get detailed task information
- `dooray_project_create_post` - Create new task
- `dooray_project_update_post` - Update existing task
- `dooray_project_set_post_workflow` - Change task status
- `dooray_project_set_post_done` - Mark task as complete

### Task Comments (4 tools)
- `dooray_project_create_post_comment` - Create task comment
- `dooray_project_get_post_comments` - List task comments
- `dooray_project_update_post_comment` - Update comment
- `dooray_project_delete_post_comment` - Delete comment

### Messenger (7 tools)
- `dooray_messenger_search_members` - Search organization members
- `dooray_messenger_send_direct_message` - Send direct message
- `dooray_messenger_get_channels` - List accessible channels
- `dooray_messenger_get_simple_channels` - List channels (simplified)
- `dooray_messenger_get_channel` - Get channel details
- `dooray_messenger_create_channel` - Create new channel
- `dooray_messenger_send_channel_message` - Send channel message

### Calendar (5 tools)
- `dooray_calendar_list` - List accessible calendars
- `dooray_calendar_detail` - Get calendar details
- `dooray_calendar_events` - List calendar events
- `dooray_calendar_event_detail` - Get event details
- `dooray_calendar_create_event` - Create new event

## Development

### Project Structure

```
src/
└── dooray_mcp/
    ├── main.py              # uvx entry points
    ├── server.py            # Multi-transport MCP server
    ├── client/
    │   └── dooray_client.py # aiohttp-based API client
    ├── tools/               # 28 MCP tools implementation
    ├── types/               # Pydantic models
    └── exceptions/          # Custom exceptions
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest -m stdio      # stdio transport tests
uv run pytest -m http       # HTTP transport tests
uv run pytest -m integration # integration tests (requires API keys)

# Run with coverage
uv run pytest --cov=dooray_mcp
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/
```

## Legacy Kotlin Version

The original Kotlin implementation is preserved in the `/old` directory for reference. To run the legacy version:

```bash
cd old && ./gradlew runLocal
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

- [GitHub Issues](https://github.com/sungmin-koo-ai/DoorayMCP/issues)
- [Dooray API Documentation](https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)