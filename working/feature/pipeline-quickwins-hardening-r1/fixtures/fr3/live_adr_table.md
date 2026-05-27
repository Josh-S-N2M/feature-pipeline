# Fixture: live repo state (expected exit 0)

This is a representative extract of ADR-0041's per-server invocation table matching
the current live .mcp.json (live_mcp.json). Both deprecated rows are annotated,
so serena and mcp-openapi-schema do not trigger absent-from-mcp-json. All active
rows match their .mcp.json counterparts. Expected: exit 0.

| Server | Mechanism | Form |
|---|---|---|
| Serena | `uvx --from` (Python; uv-managed; ephemeral) | `uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server` `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is serena start-mcp-server from PATH after uv tool install. Annotation added 2026-05-26.]` |
| mcp-openapi-schema | `npx -y` (Node ephemeral via npm cache) | `npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path>` `[DEPRECATED INVOCATION FORM — server removed from .mcp.json and postCreate.sh on 2026-05-24. Row preserved for audit-trail per ADR-0005.]` |
| actionlint-mcp | `go install` (Go-built binary on PATH) | `go install "github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}"` (upstream identifier corrected at cycle-3 D-3.2 F1) |
| terraform-mcp | binary `wget` + SHA256 + GPG verify | see `.devcontainer/install/terraform-mcp.sh` |
| **gitnexus** | **`npm install -g` (persistent) + `npx -y` (MCP server invocation in .mcp.json)** | **Persistent install in postCreate.sh: `npm install -g "gitnexus@${GITNEXUS_TAG}"`. MCP server invocation in .mcp.json: `npx -y "gitnexus@${GITNEXUS_TAG}" mcp`. Smoke-test in postCreate.sh: `npx -y "gitnexus@${GITNEXUS_TAG}" --help`.** |
| Context7 | no install (remote HTTP) | `https://mcp.context7.com/mcp` via `.mcp.json` `type: http` |
| Exa | no install (remote HTTP) | `https://mcp.exa.ai/mcp` via `.mcp.json` `type: http` |
