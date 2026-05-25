# Principles — Canonical Discipline for the MCP Layer

The eight load-bearing principles for designing and reviewing MCP layer changes. Authored per Plan T2.3.

## Principle 1 — Env-block indirection only

All credentials enter `.mcp.json` via env-block indirection. Never URL-query (OP-9 BLOCKER). Never argv (OP-10 BLOCKER). The env-var name appears literally in `.mcp.json`; the value comes from `containerEnv` in `devcontainer.json` which in turn sources from Codespaces secrets via `${localEnv:NAME}`.

See `KB-mcp-platform/references/credential-handling.md` for the discipline detail.

## Principle 2 — Narrow over whole-server

Per agent, prefer narrow per-tool allowlists (`mcp__<server>__<specific-tool>`) over whole-server allowlists (`mcp__<server>__*`) when:

- The server exposes more than 2 tools, AND
- The agent only needs a strict subset.

Whole-server is acceptable when the server's tool set is tight and all-relevant (e.g., actionlint-mcp's 2-tool surface, terraform-mcp's Terraform-reasoning tools — they all serve the consumer's purpose).

Examples (from this feature's design):

- `discovery-external-researcher` lists 5 tools from context7+exa explicitly — narrow per-tool (Context7's 2 tools + Exa's 3 tools, not whole-server) because the agent doesn't need Exa's experimental tools.
- `design-iac` uses whole-server `mcp__terraform-mcp__*` because all Terraform-reasoning tools are relevant.

## Principle 3 — Header-canonical per upstream README

Header-based auth uses the vendor's canonical header name, NOT a generic OAuth-style `Authorization: Bearer ...`. Per the SF-F3-AUTH-HEADER-1 resolution at cycle-3 (devcontainer-mcp-provisioning-r1):

- Context7: `CONTEXT7_API_KEY: <value>` (per Upstash README verbatim quote).
- Exa: `x-api-key: <value>` (per T-006 F1 priority-1 header form).

The generic Bearer form may work practically for some servers, but the README-canonical form is the safer posture (lower risk of silent failure if the vendor enforces canonical form).

## Principle 4 — Pin to specific versions or commit SHAs

`.devcontainer/versions.env` carries explicit pins. Never `latest`. Per-server pin types:

- npm package + version (e.g., `gitnexus@1.6.5`)
- GitHub commit SHA (e.g., `actionlint-mcp@7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef`)
- GitHub tag (e.g., `serena@v1.2.0`)
- Release version + SHA-256 (e.g., `terraform-mcp-server@0.5.2` with verification)

Use `<PIN_TBD>` placeholder ONLY during pre-pin authoring (Plan §D-2). Phase 0 verify-at-execution settles the actual values; T1.3 writes versions.env with concrete values.

## Principle 5 — Stdio-by-default for OSS-local; HTTP only when hosted

For OSS-local servers (gitnexus, serena, actionlint-mcp, terraform-mcp), prefer stdio transport. The benefits: no extra process to manage, no port to expose, less attack surface. HTTP is reserved for genuinely-hosted services (context7, exa — both Upstash-hosted endpoints).

## Principle 6 — Event surface is one file with redaction-at-source

Per ADR-0037, all MCP events emit to `.claude/runtime/mcp-events.jsonl`. Per ADR-0039, the helper at `.devcontainer/lib/log-mcp-event.sh` redacts credential-shaped values from the substrate before appending. The file is per-Codespace and never committed.

## Principle 7 — Primary/fallback at project level; per-feature scope decides

Per ADR-0007 v2.2.0, the GitNexus-primary / codebase-memory-mcp-fallback policy is documented at the project level. Per-feature scope decides whether to actually register the fallback:

- `devcontainer-mcp-provisioning-r1` (per Gate-4 OI-1 closure) ships with 7 servers, no codebase-memory-mcp fallback registered.
- A future feature can register the fallback; the `primary_degraded` schema-level provision in `mcp-events.jsonl` is preserved so wire-up is clean.

## Principle 8 — Audit-rule additions land in the same feature that adds the server

When a new MCP server is added (e.g., a future feature adds an eighth), the audit-rule additions (OP-1..OP-N) land in the same feature. This keeps the audit catalog and the registered server set in lockstep.

Exception: if the audit-rule work materially exceeds the feature's scope class (per ADR-0023), it graduates to a follow-up feature with explicit hand-off (the pattern ADR-0042 codified for the `auditing-mcp` family-graduation precedent).

## Cross-references

- **KB-mcp-platform** — platform half.
- **`auditing-mcp`** — OP-rule catalog (audit half).
- **`references/patterns-and-anti-patterns.md`** — pattern catalog with examples.
- All cited ADRs.
