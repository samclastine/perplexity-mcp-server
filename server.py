"""MCP server exposing a Perplexity web search tool via STDIO.

This uses FastMCP to register a single tool that searches the web using Perplexity AI.
Logs go to STDERR; do not print to STDOUT.
"""

from __future__ import annotations

import sys
import logging
import asyncio
from typing import Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastmcp.server.server import FastMCP

# Ensure repo root is on sys.path so `uv run server.py` works
import sys as _sys
from pathlib import Path as _Path

_REPO_ROOT = _Path(__file__).resolve().parent
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from src.tools.func.perplexity_search_web import execute as perplexity_search_execute


# ── logging to STDERR ─────────────────────────────────────────────────────────
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("mcp-perplexity-server")


# ── MCP server ───────────────────────────────────────────────────────────────
mcp = FastMCP("perplexity-search")


@mcp.tool()
async def perplexity_search_web(query: str) -> str:
    """Search the web using Perplexity AI with enhanced research capabilities.
    
    Uses a fixed default recency window of the last month for results.
    Returns comprehensive search results with citations when available.
    
    Args:
        query: The search query to find information about
        
    Returns:
        Search results with citations appended if available
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")
    
    # FastMCP 2.x manages the event loop; return/await coroutines directly.
    try:
        return await perplexity_search_execute({"query": query})
    except Exception as e:
        log.error(f"Error executing Perplexity search: {e}")
        raise RuntimeError(f"Failed to execute search: {str(e)}") from e


# Export aliases expected by some runners
app = mcp


if __name__ == "__main__":
    # IMPORTANT: Do not print to STDOUT; FastMCP owns the protocol stream.
    log.info("Starting Perplexity MCP server...")
    mcp.run()
