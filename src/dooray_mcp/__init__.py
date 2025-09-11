"""Dooray MCP Server - Python implementation.

A Model Context Protocol server that provides integration with NHN Dooray services.
Offers 28 tools for managing Wiki pages, projects, tasks, comments, messenger, and calendar functionalities.
"""

__version__ = "0.1.0"
__author__ = "NHN"
__email__ = "dooray@nhn.com"

from dooray_mcp.server import DoorayMcpServer

__all__ = ["DoorayMcpServer"]