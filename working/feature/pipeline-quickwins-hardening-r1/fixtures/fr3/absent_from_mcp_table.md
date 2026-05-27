# Fixture: active ADR row with no matching .mcp.json entry (expected exit 1)

The ADR table has an active row for 'gitnexus', but the .mcp.json fixture only
contains 'actionlint-mcp'. Expected finding: absent-from-mcp-json (BLOCKER) for gitnexus.

| Server | Mechanism | Form |
|---|---|---|
| actionlint-mcp | `go install` (binary on PATH) | `actionlint-mcp` |
| gitnexus | `npm install -g` + `npx -y` | `npx -y "gitnexus@${GITNEXUS_TAG}" mcp` |
