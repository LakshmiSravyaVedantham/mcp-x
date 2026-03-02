# mcp-x

**One command to turn any CLI tool or REST API into an MCP server for Claude.**

```bash
pip install mcp-x

mcp-x run git           # Claude can now use git
mcp-x run psql          # Claude can now query your database
mcp-x run https://api.stripe.com/openapi.json  # Claude can use the Stripe API
```

## How it works

1. Parses `--help` output (CLI tools) or OpenAPI spec (REST APIs) to discover capabilities
2. Optionally enhances tool schemas using Claude for better descriptions (set `ANTHROPIC_API_KEY`)
3. Starts an MCP server on a free local port
4. Auto-registers it in `~/.claude.json` — Claude sees the new tools immediately, no config needed

## Install

```bash
pip install mcp-x
```

## Usage

```bash
# CLI tools — any tool with --help output
mcp-x run git
mcp-x run ffmpeg
mcp-x run kubectl
mcp-x run aws

# REST APIs — OpenAPI spec URL or local file
mcp-x run openapi.json
mcp-x run https://api.example.com/openapi.json

# Options
mcp-x run git --no-llm       # skip Claude schema enhancement
mcp-x run git --eject        # print generated schemas as JSON, don't run
mcp-x run git --port 9000    # use a specific port

# Manage registered servers
mcp-x list                   # show all registered mcp-x servers
mcp-x remove git             # unregister a server
```

## How auto-registration works

`mcp-x run git` starts an SSE MCP server and immediately writes to `~/.claude.json`:

```json
{
  "mcpServers": {
    "mcp-x-git": {
      "url": "http://localhost:8742",
      "type": "sse"
    }
  }
}
```

Claude Code picks this up automatically. When you Ctrl+C, mcp-x removes the entry cleanly.

## Schema enhancement

If `ANTHROPIC_API_KEY` is set, mcp-x sends raw help-text schemas to `claude-haiku` for cleanup — better descriptions, proper parameter names, cleaner tool definitions.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
mcp-x run git   # schemas enhanced automatically
```

Use `--no-llm` to skip this and use raw parsed schemas.

## Requirements

- Python 3.10+
- Claude Code (for auto-registration to work)

## License

MIT
