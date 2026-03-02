---
title: I built a tool that turns any CLI into an MCP server in one command
published: true
tags: python, ai, mcp, devtools
cover_image: https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder.png
---

MCP (Model Context Protocol) is exploding right now. Everyone wants to give Claude more tools. But every MCP server I've seen requires writing boilerplate, setting up a server, figuring out the protocol, and manually editing config files.

I got tired of it. So I built `mcp-x`.

```bash
pip install mcp-x
mcp-x run git
```

That's it. Claude can now use git.

## What's actually happening

When you run `mcp-x run git`, here's what happens in about 2 seconds:

1. Runs `git --help` and parses every subcommand and description
2. Converts them into proper MCP tool schemas
3. Starts an SSE MCP server on a free local port
4. Automatically writes to `~/.claude.json`:

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

Claude Code picks it up immediately. No restart. No manual config.

When you Ctrl+C, the entry is removed cleanly.

## It works on REST APIs too

Point it at any OpenAPI spec:

```bash
mcp-x run https://api.stripe.com/openapi.json
# → Claude can now call Stripe endpoints directly
```

Or a local file:

```bash
mcp-x run ./myapi.yaml
# → 47 tools available to Claude in 3 seconds
```

## The --eject flag

Not ready to run it live? See exactly what schemas it generates first:

```bash
mcp-x run git --eject --no-llm
```

Output:
```json
[
  {
    "name": "git_clone",
    "description": "Clone a repository into a new directory",
    "command": ["git", "clone"],
    "parameters": {}
  },
  {
    "name": "git_add",
    "description": "Add file contents to the index",
    "command": ["git", "add"],
    "parameters": {}
  },
  ...
]
```

## Optional: Claude makes schemas smarter

Raw `--help` output is often terse. If you set `ANTHROPIC_API_KEY`, mcp-x sends the schemas to `claude-haiku` for cleanup — better descriptions, inferred parameters, cleaner tool definitions.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
mcp-x run kubectl
# → schemas enhanced automatically, use --no-llm to skip
```

## Under the hood

The architecture is simpler than you'd think:

```
mcp-x run <target>
    │
    ├── detect: CLI tool or OpenAPI spec?
    │
    ├── parse: --help output → ToolDefinition[]
    │          or OpenAPI spec → ToolDefinition[]
    │
    ├── enhance (optional): Claude cleans up schemas
    │
    ├── MCP server: spins up on free port via Anthropic's Python MCP SDK
    │
    └── config: writes to ~/.claude.json, cleans up on exit
```

The core is ~400 lines of Python. No magic.

## What I tried before this

Before building this, I tried:
- Writing MCP servers by hand for each tool (tedious, lots of boilerplate)
- Using the official MCP SDK examples (good foundation, but still per-tool work)
- Hoping someone else had already built a generic wrapper (they hadn't)

The insight that unlocked it: every CLI tool already documents itself via `--help`. Every REST API already documents itself via OpenAPI. I wasn't missing data — I was missing a bridge.

## Try it

```bash
pip install mcp-x

# Try any tool you already have
mcp-x run git
mcp-x run ffmpeg
mcp-x run kubectl
mcp-x run aws
```

Source: [github.com/LakshmiSravyaVedantham/mcp-x](https://github.com/LakshmiSravyaVedantham/mcp-x)

PRs welcome — especially for better CLI help parsing (some tools use non-standard help formats) and OpenAPI v2 (Swagger) support.

---

*What tool would you MCP-ify first? Drop it in the comments.*
