"""
kubectl-mcp-tool package.

This package provides MCP-based tools for kubectl operations.
"""

__version__ = "0.1.0"

from .mcp_server import MCPServer

__all__ = ["MCPServer"]
