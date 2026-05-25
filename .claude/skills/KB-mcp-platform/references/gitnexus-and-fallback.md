# GitNexus Primary + codebase-memory-mcp Fallback Policy

Per **ADR-0007 v2.2.0**: GitNexus is the primary code-graph MCP server; codebase-memory-mcp is the documented fallback. The policy is preserved at the project level; the fallback's `.mcp.json` registration is **NOT** provisioned in this feature per Gate-4 OI-1 closure (devcontainer-mcp-provisioning-r1).

## Why GitNexus is primary

Per ADR-0007 v2.2.0 + the synthesis cluster around D-0005 / D-0011: GitNexus offers a richer symbol-level code-graph surface than codebase-memory-mcp, particularly for blast-radius analysis at the Discovery Research stage. codebase-memory-mcp was the v1.0 primary; ADR-0007 v2.0 flipped to GitNexus-primary on the basis of broader symbol coverage and the additive surface.

## Why codebase-memory-mcp is fallback

Two reasons:

1. **Capability redundancy**: codebase-memory-mcp covers the core "find symbol", "find references", "structural query" surface that GitNexus offers — though with less depth. If GitNexus is unavailable (process crash, network failure, runtime degradation), the fallback preserves Discovery's ability to produce a `codebase-analysis.json` even if at reduced fidelity.

2. **Operational continuity**: ADR-0007 v2.2.0 documents that the fallback emits a `primary_degraded → falling back to <fallback>` event marker on the `.claude/runtime/mcp-events.jsonl` event surface (per ADR-0037). This signal is consumed by `discovery-codebase-researcher` to know when its output should carry a `extraction_method: "codebase-memory-mcp"` annotation instead of `"gitnexus"` or `"mixed"`.

## Why NOT provisioned in this feature

Per Gate-4 OI-1 closure (user verbatim: *"Lets move forward with 7 MCP the codebase-memory-mcp was an earlier assessment that is now stall."*). The feature originally shipped seven named servers; the 2026-05-24 postmortem then removed `mcp-openapi-schema`, leaving six. Either way, codebase-memory-mcp is registered nowhere. The policy at ADR-0007 v2.2.0 stays in force at the project level; the `primary_degraded` schema-level provision is preserved (so a future feature that registers the fallback can wire it up cleanly), but no code is shipped for it in `.mcp.json`, `postCreate.sh`, or any consumer agent's `tools:` allowlist.

## `primary_degraded` schema-level provision (per ADR-0037)

Per ADR-0037, `.claude/runtime/mcp-events.jsonl` schema includes a `structured_failure` event type with a `primary_degraded` sub-field. The schema preserves this even though no fallback is currently wired:

```jsonl
{
  "event": "structured_failure",
  "timestamp": "<ISO 8601>",
  "server": "gitnexus",
  "failure_layer": "transport|auth|tool|...",
  "primary_degraded": true,
  "fallback_invoked": false,
  "fallback_server": null,
  "message": "<one-line summary>"
}
```

When the codebase-memory-mcp fallback gets provisioned in a future feature, the same schema gains:

```jsonl
{
  "event": "structured_failure",
  "primary_degraded": true,
  "fallback_invoked": true,
  "fallback_server": "codebase-memory-mcp",
  ...
}
```

The discovery-codebase-researcher agent reads the most recent `mcp-events.jsonl` records before invoking its code-graph traversals; if `primary_degraded: true` and `fallback_invoked: true` for `server: "gitnexus"` (within a configurable freshness window), the agent updates its `codebase-analysis.json` output's `extraction_method` field to `"codebase-memory-mcp"` for the affected operation.

## Audit rule coverage

`auditing-mcp` OP-4 (the audit family with this fallback in scope) does NOT currently audit codebase-memory-mcp registration because it isn't registered. If a future feature adds the fallback, the OP-4 rule's coverage list extends to include it (per ADR-0042 family-graduation precedent; the audit rule modification lands in the feature that registers the server).

## Consumer agents

- `discovery-codebase-researcher` — primary consumer; reads `primary_degraded` markers; updates `extraction_method` field.
- `review-architecture-auditor` — secondary consumer; receives the same code-graph surface for blast-radius analysis.

Both currently carry `mcp__gitnexus__*` in their `tools:` allowlists (no `mcp__codebase-memory-mcp__*` per Gate-4 OI-1).

## Cross-references

- **ADR-0007 v2.2.0** — primary/fallback policy at project level.
- **ADR-0037** — `mcp-events.jsonl` schema including `primary_degraded`.
- **ADR-0038** — codebase-analysis JSON schema v1.1.0 (consumes `extraction_method`).
- **Blueprint OI-1 closure** — Gate-4 user-disposition to drop fallback for this feature.
- **research-notes/T-007-gitnexus.md** — Discovery research note for GitNexus.
