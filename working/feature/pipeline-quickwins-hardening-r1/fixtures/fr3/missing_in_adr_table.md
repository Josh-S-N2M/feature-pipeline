# Fixture: server in .mcp.json with no ADR row (expected exit 1)

The .mcp.json fixture contains 'unknown-server' which has no row in this table.
Expected finding: missing-in-adr-0041 (BLOCKER) for unknown-server.

| Server | Mechanism | Form |
|---|---|---|
| actionlint-mcp | `go install` (binary on PATH) | `actionlint-mcp` |
