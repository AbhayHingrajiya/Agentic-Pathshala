"""
MCP Client Utility
------------------
Provides a synchronous wrapper around the async FastMCP Client so that
regular (non-async) agent functions can call MCP tools without managing
event loops themselves.

Usage:
    from utils.mcp_client import call_mcp_tool

    result = call_mcp_tool("get_assignments_for_learner", {"learner_id": "L001"})
    # result -> {"learner_id": "L001", "count": 3, "assignments": [...]}
"""

import asyncio
import json
from typing import Any

from fastmcp import Client
from config.settings import settings


def call_mcp_tool(tool_name: str, params: dict) -> Any:
    """
    Synchronous wrapper to call any MCP tool by name via the FastMCP SSE client.

    Args:
        tool_name: Name of the registered MCP tool (e.g. "get_assignments_for_learner")
        params:    Dict of arguments to pass to the tool

    Returns:
        Parsed Python dict/list from the tool's JSON response.

    Raises:
        ConnectionError: If the MCP server is not reachable or call fails.
    """
    mcp_url = f"{settings.MCP_SERVER_URL}/sse"

    async def _call() -> Any:
        async with Client(mcp_url) as client:
            result = await client.call_tool(tool_name, params)
            # FastMCP 3.x returns a CallToolResult with:
            #   .data            -> already-parsed Python dict (use this)
            #   .is_error        -> True if the tool raised an exception
            #   .content         -> list of TextContent objects (raw)
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
