# Fixture: clean matching pair (expected exit 0)

This fixture has two servers in .mcp.json, each with a matching active ADR row and
a form that matches after canonicalization and opaque-token comparison.

| Server | Mechanism | Form |
|---|---|---|
| actionlint-mcp | `go install` (binary on PATH) | `actionlint-mcp` |
| gitnexus | `npm install -g` (persistent) + `npx -y` (MCP invocation) | `npx -y "gitnexus@${GITNEXUS_TAG}" mcp` |
