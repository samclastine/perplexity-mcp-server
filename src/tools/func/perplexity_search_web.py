from typing import Any, Dict
import sys
import os

# Add the src directory to the path so we can import from model
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from model import call_perplexity  # model/perplexity.py

TOOL_NAME = "perplexity_search_web"

TOOL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Search the web using Perplexity AI (fixed default recency window: last month)"

async def execute(arguments: Dict[str, Any]) -> str:
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Missing required 'query' (string)")
    # No recency arg anymore; uses model default internally
    return await call_perplexity(query)