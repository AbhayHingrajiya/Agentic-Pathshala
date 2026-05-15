"""
MCP Client Utility
------------------
Provides a synchronous wrapper around the async FastMCP Client so that
regular (non-async) agent functions can call MCP tools without needing
to manage event loops themselves.

Usage:
    from utils.mcp_client import call_mcp_tool

    result = call_mcp_tool("get_assignments_for_learner", {"learner_id": "L001"})
"""

import asyncio
import json
from typing import Any

from fastmcp import Client
from config.settings import settings


def call_mcp_tool(tool_name: str, params: dict) -> Any:
    """
    Synchronous wrapper to call any MCP tool by name.

    Connects to the FastMCP SSE server, calls the tool, and returns
    the parsed result dict/list. Raises on connection or tool errors.

    Args:
        tool_name: Name of the MCP tool to call (e.g. "get_assignments_for_learner")
        params:    Dict of arguments to pass to the tool

    Returns:
        Parsed Python object from the tool's JSON response.

    Raises:
        ConnectionError: If the MCP server is not reachable.
        RuntimeError:    If the tool call fails or returns an error.
    """
    mcp_url = f"{settings.MCP_SERVER_URL}/sse"

    async def _call() -> Any:
        async with Client(mcp_url) as client:
            result = await client.call_tool(tool_name, params)
            # FastMCP 3.x returns a CallToolResult with .data and .is_error
            if result.is_error:
                raise RuntimeError(f"MCP tool returned an error: {result.content}")
            return result.data if result.data is not None else {}

    try:
        return asyncio.run(_call())
    except Exception as e:
        raise ConnectionError(
            f"MCP tool call failed [{tool_name}]: {str(e)}\n"
            f"Is the MCP server running at {mcp_url}?"
        ) from e
