from typing import Any, Dict, List

PROMPT_NAME = "perplexity_search_web"
DESCRIPTION = "Search the web using Perplexity AI (defaults to results from the last month)."

ARGS: List[Dict[str, Any]] = [
    {
        "name": "query",
        "description": "The search query to find information about",
        "required": True,
    }
]

def build_messages(arguments: Dict[str, Any]) -> List[Dict[str, str]]:
    query = arguments.get("query", "")
    # No recency arg; we just state the default behavior explicitly
    return [
        {"role": "user", "text": f"Find recent information about: {query}"},
        {"role": "user", "text": "Only include results from the last month."},
    ]