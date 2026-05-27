# Fixture: deprecated row skip (expected exit 0)

The ADR table has an active row for 'actionlint-mcp' (matches .mcp.json) and a
deprecated row for 'old-server' (removed from .mcp.json). The deprecated row must
NOT trigger absent-from-mcp-json. Expected: exit 0 (no findings).

| Server | Mechanism | Form |
|---|---|---|
| actionlint-mcp | `go install` (binary on PATH) | `actionlint-mcp` |
| old-server | `npx -y` (Node ephemeral) | `npx -y "old-server@${OLD_SERVER_VERSION}"` `[DEPRECATED INVOCATION FORM — server removed 2026-01-01; row preserved for audit-trail per ADR-0005.]` |
