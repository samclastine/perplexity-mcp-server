# Perplexity MCP Server

An MCP (Model Context Protocol) server that exposes a single tool to search the web using Perplexity AI. The server wraps Perplexity's Chat Completions API and returns concise answers with citations. Results default to the last month for recency.

## Overview

- Protocol: MCP over STDIO (via FastMCP 2.x)
- Tool: `perplexity_search_web`
- Default recency window: last month
- Output: text response with citations appended when available

## Requirements

- Python 3.13+
- A Perplexity API key (environment variable `PERPLEXITY_API_KEY`)
- Windows, macOS, or Linux

## Project structure

```
perplexity-mcp-server/
├─ server.py                 # MCP server entrypoint (FastMCP)
├─ src/
│  ├─ model/
│  │  └─ perplexity.py       # Perplexity API client and payload shaping
│  └─ tools/
│     ├─ func/
│     │  └─ perplexity_search_web.py  # Tool implementation (async)
│     └─ prompt/
│        └─ perplexity_search_web.py  # Prompt definition (for future use)
├─ .env.example             # Example env file (no secrets)
├─ pyproject.toml           # Dependencies
└─ README.md                # This file
```

## Quick start (Windows PowerShell)

1) Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip
pip install "mcp[cli]>=1.14.0" "fastmcp>=2.12.0" aiohttp python-dotenv
```

2) Configure your environment file

```powershell
Copy-Item .env.example .env
# Then edit .env and set your key
# PERPLEXITY_API_KEY=your_api_key_here
# PERPLEXITY_MODEL=sonar   # optional, defaults to "sonar"
```

3) Integrate with an MCP client (Claude Desktop example)

Add an entry to your Claude Desktop config (replace paths to match your machine). You can point directly to the Python file, as FastMCP CLI will run it:

```json
{
	"mcpServers": {
		"perplexity-mcp-server": {
			"command": "E:\\mcp-servers\\perplexity-mcp-server\\.venv\\Scripts\\python.exe",
		"args": ["E:\\mcp-servers\\perplexity-mcp-server\\server.py"]
		}
	}
}
```

Restart Claude Desktop. The tool `perplexity_search_web` will be available to your assistant when connected to this server.

> Note: You can also run locally with the CLI:
>
> ```powershell
> fastmcp run .\server.py --transport stdio --no-banner
> ```
> This should run without the "Already running asyncio" error, thanks to the FastMCP 2.x runtime.

## Configuration

Set the following environment variables (via `.env` or your shell):

- `PERPLEXITY_API_KEY` (required): Your Perplexity API key.
- `PERPLEXITY_MODEL` (optional, default: `sonar`): Choose from:
	- `sonar` — 128k context (default)
	- `sonar-pro` — 200k context (professional grade)
	- `sonar-reasoning` — 128k context (enhanced reasoning)
	- `sonar-reasoning-pro` — 128k context (advanced reasoning pro)
	- `sonar-deep-research` — 128k context (enhanced research)
	- `r1-1776` — 128k context (alternative architecture)

Other client defaults (fixed in code):

- `max_tokens=512`
- `temperature=0.2`, `top_p=0.9`
- `search_recency_filter=month` (results from the last month)
- `return_citations=true`

## Tool API

- Name: `perplexity_search_web`
- Description: Search the web using Perplexity AI (defaults to results from the last month)
- Input schema:
	- `query` (string, required): The search query
- Return: A string containing the answer. If citations are returned, they are appended as numbered links.

### Contract

- Input: `{ "query": "<your question>" }`
- Success: Non-empty string response (may include trailing "Citations:" block)
- Errors:
	- `PERPLEXITY_API_KEY is not set` if key missing
	- `Perplexity HTTP <status>:` on non-2xx responses
	- `Perplexity request timed out` on timeout
	- `Network error calling Perplexity: ...` on client/network issues

## Examples

Ask about recent developments:

```text
Tool: perplexity_search_web
Args: { "query": "What are the latest updates on the Model Context Protocol?" }
```

Example output shape:

```
<answer text>

Citations:
[1] https://example.com/source-1
[2] https://example.com/source-2
```

## Troubleshooting

- Missing API key: Ensure `PERPLEXITY_API_KEY` is set in `.env` and you restarted your client.
- 401 Unauthorized: Verify the API key is valid and not expired/rotated.
- 429 Rate limited: Wait and retry; consider reducing request frequency.
- Timeouts/Network: Check connectivity and firewall; the client uses `aiohttp` with a 60s total timeout.
- Windows PowerShell venv activation: If blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the same PowerShell session, then activate again.

## Security

- Do NOT commit your `.env` file. The repo is configured to ignore it; use `.env.example` as a template.
- If you accidentally committed a secret, rotate the key immediately in your Perplexity account and rewrite the commit history if necessary.
- GitHub Push Protection may block pushes that contain secrets—fix locally rather than bypassing unless you have fully rotated the secret.

## License

MIT License. See `LICENSE`.

