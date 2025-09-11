# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dooray MCP Server** - a Model Context Protocol server that provides integration with NHN Dooray services. It's built using Kotlin and the MCP SDK, offering 28 tools for managing Wiki pages, projects, tasks, comments, messenger, and calendar functionalities.

## Key Development Commands

### Build & Run
```bash
# Clean build and create JAR
./gradlew clean shadowJar

# Run locally with .env file
./gradlew runLocal

# Run tests (CI automatically excludes integration tests)
./gradlew test

# Run tests in CI mode (excludes integration tests)
CI=true ./gradlew test

# Direct JAR execution
java -jar build/libs/dooray-mcp-server-{version}-all.jar
```

### Docker Operations
```bash
# Build Docker image
docker build -t dooray-mcp:local --build-arg VERSION=0.2.1 .

# Run with Docker
docker run -e DOORAY_API_KEY="your_key" -e DOORAY_BASE_URL="https://api.dooray.com" dooray-mcp:local
```

## Architecture Overview

### Core Components
- **Main.kt**: Entry point with logging configuration to prevent stdout pollution (MCP uses stdin/stdout)
- **DoorayMcpServer.kt**: Main server class that initializes MCP server with all tools
- **DoorayHttpClient.kt**: HTTP client for Dooray API communication
- **Tools Directory**: 28 individual tool implementations, each handling specific Dooray operations

### Package Structure
```
com.bifos.dooray.mcp/
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

## Development Guidelines

### Environment Setup
Required environment variables:
- `DOORAY_API_KEY`: Your Dooray API key
- `DOORAY_BASE_URL`: Dooray API base URL (typically https://api.dooray.com)

Optional logging controls:
- `DOORAY_LOG_LEVEL`: DEBUG, INFO, WARN, ERROR (default: WARN)
- `DOORAY_HTTP_LOG_LEVEL`: HTTP client logging level (default: WARN)

### Testing Strategy
- Unit tests in `src/test/kotlin/`
- Integration tests (excluded in CI with `CI=true`)
- Mocked HTTP client tests using MockK
- Test utilities in `TestUtil.kt`

### Key Technical Considerations
- **MCP Protocol**: Uses stdin/stdout for communication - all logs go to stderr
- **Kotlin Coroutines**: Async operations with proper exception handling
- **Ktor Client**: HTTP communication with content negotiation and logging
- **Serialization**: Kotlinx.serialization for JSON handling
- **Shadow JAR**: Fat JAR packaging for distribution

### Tool Implementation Pattern
Each tool follows a consistent pattern:
1. Extends MCP tool interface
2. Validates input parameters
3. Makes HTTP request via DoorayHttpClient
4. Handles responses with standardized error handling
5. Returns structured JSON responses

### Error Handling
- Custom exceptions in `exception/` package
- Standardized API error types in `types/DoorayApiErrorType.kt`
- Tool-specific error handling with proper MCP error responses

## Important Notes
- **Java 21 required**: Project uses JVM toolchain 21
- **ARM64 builds disabled**: Currently only AMD64 Docker builds due to QEMU issues
- **Logging to stderr**: Critical for MCP protocol compatibility
- **Environment-based configuration**: Uses .env file for local development