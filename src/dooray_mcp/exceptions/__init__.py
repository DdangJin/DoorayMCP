"""Dooray MCP exceptions module."""


class DoorayMcpError(Exception):
    """Base exception for Dooray MCP errors."""
    pass


class DoorayApiError(DoorayMcpError):
    """Exception raised when Dooray API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ToolExecutionError(DoorayMcpError):
    """Exception raised when a tool execution fails."""
    pass


class ValidationError(DoorayMcpError):
    """Exception raised when input validation fails."""
    pass


__all__ = [
    "DoorayMcpError",
    "DoorayApiError", 
    "ToolExecutionError",
    "ValidationError",
]