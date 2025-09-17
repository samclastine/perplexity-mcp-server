import asyncio
import os
import atexit
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

AVAILABLE_MODELS: Dict[str, str] = {
    "sonar-deep-research": "128k context - Enhanced research capabilities",
    "sonar-reasoning-pro": "128k context - Advanced reasoning (pro)",
    "sonar-reasoning": "128k context - Enhanced reasoning",
    "sonar-pro": "200k context - Professional grade",
    "sonar": "128k context - Default",
    "r1-1776": "128k context - Alternative architecture",
}

_PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

# Default recency window (fixed)
RECENCY_DEFAULT = "month"

_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session
    async with _session_lock:
        if _session and not _session.closed:
            return _session
        timeout = aiohttp.ClientTimeout(total=60)
        _session = aiohttp.ClientSession(timeout=timeout)
        # Register cleanup function
        atexit.register(lambda: asyncio.create_task(_cleanup_session()) if _session and not _session.closed else None)
    return _session


async def _cleanup_session():
    """Clean up the aiohttp session."""
    global _session
    if _session and not _session.closed:
        await _session.close()


def _build_payload(query: str) -> Dict[str, Any]:
    model = os.getenv("PERPLEXITY_MODEL", "sonar")
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ],
        "max_tokens": 512,  # int (not string)
        "temperature": 0.2,
        "top_p": 0.9,
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": RECENCY_DEFAULT,  # fixed default
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "return_citations": True,
        "search_context_size": "low",
    }


def _extract_content_and_citations(data: Dict[str, Any]) -> Tuple[str, List[str]]:
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("Perplexity API returned no choices")
    message = choices[0].get("message", {}) or {}
    content = message.get("content", "")
    if not content:
        raise ValueError("Perplexity API returned empty content")
    citations = data.get("citations") or message.get("citations") or []
    citations = [str(c) for c in citations if c]
    return content, citations


async def call_perplexity(query: str) -> str:
    """
    Public API for Perplexity chat completion with a fixed default recency window.
    Returns: text (+ Citations: ... if available).
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY is not set")

    session = await _get_session()
    payload = _build_payload(query)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with session.post(_PERPLEXITY_URL, json=payload, headers=headers) as resp:
            if not (200 <= resp.status < 300):
                text = await resp.text()
                raise RuntimeError(f"Perplexity HTTP {resp.status}: {text[:500]}")
            data = await resp.json()
    except asyncio.TimeoutError as e:
        raise RuntimeError("Perplexity request timed out") from e
    except aiohttp.ClientError as e:
        raise RuntimeError(f"Network error calling Perplexity: {e}") from e

    content, citations = _extract_content_and_citations(data)
    if citations:
        lines = [f"[{i+1}] {url}" for i, url in enumerate(citations)]
        return content + "\n\nCitations:\n" + "\n".join(lines)
    return content