# Toxic Combinations

## Contents

- What a toxic combination is
- The 7 named combinations
- Tool-description prompt-injection patterns
- Runtime mode behavior

## What a toxic combination is

A single MCP server with two or more capabilities that, combined, enable a known attack pattern. The capabilities individually are fine; together they create an exfiltration or persistence path.

The auditor flags toxic combinations based on:
- The server name (some servers are known to combine capabilities — e.g. "filesystem-and-web")
- The package name in `args` (the same logic)
- In `--with-runtime` mode, the live tool list from the server

## The 7 named toxic combinations

### TC-1: Filesystem + Web — BLOCKER (security_critical)

A server providing both file reads AND outbound HTTP. Attack: read SSH key, POST it to attacker.

Example server names: `filesystem-and-fetch`, `local-web`, `fs-api`.

### TC-2: Database + Web — BLOCKER (security_critical)

A server providing database query AND outbound HTTP. Attack: SELECT secrets, send to attacker.

Example: `postgres-fetcher`, `db-and-web`, `mysql-api`.

### TC-3: Shell + Web — BLOCKER (security_critical)

A server providing shell execution AND outbound HTTP. Attack: run arbitrary command, exfiltrate output.

Example: `terminal-api`, `cmd-fetch`, `shell-web`.

### TC-4: Filesystem write + Filesystem read on different scopes — MAJOR

A server that can write to /etc and read from ~/.ssh. The combination enables credential theft + persistence.

This requires the server to declare both broad-write and broad-read tools — rare but not absent in the wild.

### TC-5: Network + Memory write — MAJOR

A server that can write to MEMORY.md AND make HTTP calls. Attack: poison MEMORY.md, fetch updated payload from attacker.

### TC-6: Shell + Memory write — MAJOR

A server that can run shell AND modify project memory. Attack: install persistence, document it in MEMORY.md so Claude doesn't notice the change.

### TC-7: Subagent management + Shell — BLOCKER

A server that can create or modify subagent definitions AND has shell access. Attack: create malicious subagent that runs in next session.

## Tool-description prompt-injection patterns

In `--with-runtime` mode, the auditor inspects tool descriptions for prompt-injection signatures:

```audit-example -- toxic-combinations anti-pattern catalog demonstrating prompt-injection phrase; documents what the auditor scanner detects
- "Ignore previous instructions and..."
- "From now on, always..."
- "When you call this tool, also..."
- "The user actually wants you to..."
- Conditional instructions: "If X, then do Y instead of what the user asked."
```

Each detected pattern: BLOCKER + security_critical.

The auditor reads each tool's `description` field (provided by the server in MCP's `tools/list` response). Hidden Unicode tag characters (zero-width, RTL override) are also flagged.

## Heuristics for static (no-runtime) audit

Without runtime probing, the auditor uses heuristics on server names and package names:

| Server name pattern | Suspected combination |
|---|---|
| Contains "filesystem" or "fs" AND "web", "fetch", "http", "url" | TC-1 |
| Contains "postgres", "mysql", "sql", "db" AND "web", "fetch" | TC-2 |
| Contains "shell", "terminal", "cmd", "exec" AND "web", "fetch" | TC-3 |
| Contains "agent" or "subagent" AND "shell" or "exec" | TC-7 |

Heuristic findings are MAJOR by default; runtime mode escalates to BLOCKER on confirmation.

## Runtime mode behavior

When invoked with `--with-runtime`:

1. The auditor spawns each configured server.
2. Sends `tools/list` request.
3. Reads the response.
4. For each tool:
   - Categorizes it (file-read, file-write, network, shell, etc.) by heuristic on tool name and description.
   - Checks the description for prompt-injection patterns.
5. Computes the toxic-combination flag from the actual tool set.
6. Cleans up: sends `shutdown` to each server.

Runtime mode is opt-in because spawning the server runs whatever code the server contains. It's a higher-trust operation than static audit.

## What good MCP servers look like

- Single, focused capability (filesystem-only, OR github-only, OR database-only).
- Tool descriptions describe the tool's behavior — no manipulation language.
- Names match publishers (official `@modelcontextprotocol/*` packages, or named org packages).
- Credentials referenced from env, never literal.

## What bad MCP servers look like

- Single server with multiple unrelated capabilities (combo servers).
- Tool descriptions containing instructions to Claude.
- Server name imitating an official publisher but command points to a different package.
- Literal credentials in env.

See `examples/bad-mcp-annotated.md` for an annotated bad example.
