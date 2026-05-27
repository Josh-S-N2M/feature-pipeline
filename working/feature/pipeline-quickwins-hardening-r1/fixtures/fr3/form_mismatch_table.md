# Fixture: invocation form mismatch (expected exit 1)

The .mcp.json fixture uses 'actionlint-mcp --wrong-flag' but the ADR documents
'actionlint-mcp' with no args. Expected finding: invocation-form-mismatch (BLOCKER).

| Server | Mechanism | Form |
|---|---|---|
| actionlint-mcp | `go install` (binary on PATH) | `actionlint-mcp` |
