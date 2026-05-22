# Common Failures — MCP

## Contents

- Silent failure: server name typo
- Silent failure: missing command/url
- Silent failure: credential in literal value
- Silent failure: http instead of https
- Runtime-mode considerations
- Diagnostic flow

## Silent failure: server name typo

A typo in the `mcpServers` key results in an unknown server name. The server config is treated as a separate (unused) entry; the intended-named server isn't configured.

Symptom: server doesn't appear in `/mcp` listing.

Audit: not detected statically (typo is in the key, not in a recognized field); but `/mcp` is the diagnostic.

## Silent failure: missing command for stdio

If `type` is omitted (defaults to `stdio`) and `command` is missing, the server fails to launch. The user sees a connection error in `/mcp`.

Audit: MC-8 BLOCKER.

## Silent failure: credential leaked in literal value

Common: developer pastes a token directly into the config "just to test." Now the token is committed.

Audit: MC-1 BLOCKER + security_critical.

## Silent failure: http instead of https for sse/http transport

The server "works" locally but credentials in headers go over plaintext network.

Audit: MC-6 MAJOR.

## Silent failure: args is a single string

```audit-example -- common-failures catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "command": "npx",
  "args": "-y @org/server foo"
}
```

This passes one big string to `npx`, which fails. The user sees a launch error.

Audit: MC-9 MAJOR.

## Runtime-mode considerations

When running `--with-runtime`, the auditor spawns the server. This means:

- Any malicious server code runs.
- Credentials referenced from env (`${VAR}`) are resolved and passed.
- Network connections may be established.

**Always run static audit first.** Only opt into runtime audit if the static audit shows nothing alarming.

## Cross-scope behavior

MCP server names use the same precedence as settings fields: managed > local > project > user. A user-scope `github` server is hidden by a project-scope `github` server with the same name.

If the user is surprised by behavior of a named server, check `/mcp` for which scope is active.

## The "my server isn't connecting" diagnostic flow

1. `/mcp` — what state is the server in?
   - **Missing:** name typo, parse error in settings.json, or missing required field.
   - **Failed to start:** command path wrong, args wrong, or executable missing.
   - **Connected but no tools:** server is up but its `tools/list` returned nothing.
2. Run the server's command manually in a shell — does it start without errors?
3. For stdio: does it write valid MCP wire protocol to stdout?
4. For sse/http: is the URL reachable?

## Diagnostic commands

```
/mcp                   # Server status
/mcp tools <server>    # Tools exposed by a server
/doctor                # General config validation
```
