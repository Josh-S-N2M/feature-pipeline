# MCP Specification

## Contents

- What MCP is
- Config shape
- Transports (stdio, sse, http)
- Credential handling
- Server-name precedence and uniqueness
- Supply-chain considerations

## Source

`modelcontextprotocol.io` and `code.claude.com/docs/en/mcp`, last verified 2026-05.

## What MCP is

The Model Context Protocol is a standard for extending Claude Code with custom tools. An MCP server is a separate process that Claude Code launches; the server exposes tools via the MCP wire protocol. Claude Code's tool list grows by however many tools the server declares.

The risk surface: each MCP server is an independently-developed process running locally with the user's permissions. A malicious server can read files, write files, exfiltrate via network, or inject prompts via tool descriptions.

## Config shape

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"],
      "env": {
        "DEBUG": "*"
      }
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Per-server fields:

| Field | Required | Notes |
|---|---|---|
| `type` | optional | `stdio` (default), `sse`, or `http` |
| `command` | yes (for stdio) | Executable path |
| `args` | optional | List of args |
| `env` | optional | Env vars for the server subprocess |
| `url` | yes (for sse/http) | Server endpoint |
| `headers` | optional (sse/http) | HTTP headers |
| `timeout` | optional | Per-request timeout (seconds) |

## Transports

### stdio

The most common. Claude Code spawns the server as a subprocess and talks over its stdin/stdout. Examples: `npx -y @modelcontextprotocol/server-filesystem`, `python3 -m my_server`.

Audit checks:
- `command` field present (BLOCKER if absent for stdio).
- `command` is executable (or `npx`/`uvx` which install on first run).
- `args` is a list (not a comma-separated string — common mistake).

### sse (Server-Sent Events)

Claude Code connects to a URL serving SSE. Example: `https://my-mcp.example.com/sse`.

Audit checks:
- `url` field present.
- URL uses `https://` (MAJOR if `http://` and not localhost).
- If `headers` includes credentials, they should be `${VAR}` references.

### http

Standard HTTP request/response. Same checks as sse.

## Credential handling

The most common credential-leak pattern in MCP configs:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_actualValueHere..."
      }
    }
  }
}
```

Audit: BLOCKER + security_critical (same as ST-2 in settings).

Correct form:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Server-name uniqueness and precedence

Server names are keys in the `mcpServers` object. Across scopes (managed > local > project > user), the same server name resolves with override semantics — the highest-scope config wins.

Audit: when the auditor sees the same name at multiple scopes (in project mode), it emits INFO "server config shadowed by higher scope."

Within a single scope, JSON parsing forbids duplicate keys (or the last value wins) — so name collisions within a file are silently resolved by the parser.

## Supply-chain considerations

The `command` field is shell-executed (typically `npx`, `uvx`, `python3 -m`, or a path to a script). The auditor's recommendations:

| Pattern | Severity |
|---|---|
| `command: "npx", args: ["-y", "@org/server-x"]` from a known publisher | OK |
| `command: "npx", args: ["-y", "some-package"]` from unknown publisher | MINOR — warn |
| `command: "curl", args: [...]` (downloads and runs) | BLOCKER — supply chain |
| `command: "/abs/path/to/binary"` (bundled binary) | MAJOR — verify integrity |
| Server name matches a well-known publisher but command points elsewhere | BLOCKER — typo-squat indicator |

## .mcp.json files

A `.mcp.json` file at project root is an alternate way to declare servers, used by some MCP tooling. The schema is the same as the `mcpServers` block.

Audit: file parses as JSON. Each server entry validates the same as in settings.json.

## Diagnostic commands

```
/mcp
```

Lists configured servers and their connection status. Reveals: parse errors, missing executables, failed connections, available tools.

```
/mcp tools <server-name>
```

Lists tools exposed by a specific server. Useful for verifying a server matches its description.
