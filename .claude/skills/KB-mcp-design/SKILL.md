---
name: kb-mcp-design
description: >-
  Design discipline for the MCP (Model Context Protocol) layer in
  feature-pipeline projects. Covers when to add an MCP server vs. when to
  refuse, narrow per-tool allowlists vs. whole-server allowlists per agent,
  the OP-rule catalog (OP-1..OP-10) for the augmented `auditing-mcp` family,
  the canonical event-surface schema choices (per ADR-0037), credential
  indirection patterns (per ADR-0039), the primary/fallback decision
  framework for code-graph servers (per ADR-0007 v2.2.0), and the
  anti-pattern catalog (URL-query credentials, argv-leaked credentials).
  Pairs with KB-mcp-platform (the platform half) and the augmented
  `auditing-mcp` family (the audit half — graduated to its own family per
  ADR-0042). Loaded when a feature touches `.mcp.json` at repo root,
  per-agent `mcp__<server>__*` tool allowlists, or any of the six named
  servers' configuration surface (originally seven; `mcp-openapi-schema`
  removed 2026-05-24 per postmortem — see KB-mcp-platform deprecation note).
allowed-tools: Read, Grep, Glob, Edit, Write
family: kb-mcp
---

# KB-mcp-design — MCP Layer Design Discipline

Design knowledge for the MCP layer. The PLATFORM half (facts, install forms, schemas, lifecycle wiring) lives in **KB-mcp-platform**. The AUDIT half (OP-rule catalog, audit script) lives in the **`auditing-mcp`** skill family (graduated to its own family per ADR-0042).

## Contents

- When to load this KB
- Principles (canonical)
- Patterns and anti-patterns
- Cross-references

## When to load this KB

Load when authoring or reviewing:

- `.mcp.json` entries (the six mcpServers block)
- Per-agent `mcp__<server>__*` `tools:` allowlists in `.claude/agents/*.md`
- The augmented `auditing-mcp` skill's OP-1..OP-10 rules
- ADRs that affect MCP layer posture (ADR-0007, ADR-0037, ADR-0039, ADR-0040, ADR-0041, ADR-0042, ADR-0043)
- Per-layer Design subsections during a feature run that touches MCP

Pairs with **KB-mcp-platform** for the platform facts and **`auditing-mcp`** for the audit rule catalog.

## Principles

See `references/principles.md` for the canonical principle catalog. Eight principles:

1. Env-block indirection only — never URL-query, never argv (per ADR-0039 / OP-9 / OP-10).
2. Narrow over whole-server when the tool set has > 2 tools.
3. Header-canonical per upstream README (Context7 = `CONTEXT7_API_KEY`; Exa = `x-api-key`).
4. Pin to specific versions or commit SHAs; `<PIN_TBD>` only as transitional placeholder.
5. Stdio-by-default for OSS-local; HTTP only when the upstream is a hosted service.
6. Event surface is one file (`.claude/runtime/mcp-events.jsonl`) with redaction-at-source.
7. Primary/fallback policy stays at the project level (ADR-0007 v2.2.0); per-feature scope decides whether to register the fallback.
8. Audit-rule additions land in the same feature that adds the server (or graduate to a follow-up if scope-creep).

## Patterns and anti-patterns

See `references/patterns-and-anti-patterns.md` for the catalog. Key patterns:

- **`.mcp.json` env-block credential indirection** (per ADR-0039) — the canonical credential-passing pattern.
- **Narrowed per-tool allowlist** — used when a server exposes a tool surface broader than the agent needs.
- **Whole-server allowlist** — used only when the server exposes a tight, all-relevant tool set (e.g., actionlint-mcp's 2 tools, terraform-mcp's tight Terraform-reasoning set).
- **Primary/fallback registration** (per ADR-0007 v2.2.0) — when an MCP server has known instability, register a fallback with `primary_degraded` event-surface support.

Key anti-patterns (the audit catalog flags):

- **URL-query embedded credentials** (per OP-9) — BLOCKER.
- **argv-passed credentials** (per OP-10) — BLOCKER.
- **Whole-server allowlist when narrow is feasible** — MAJOR finding.
- **Pinning to `latest`** (vs explicit version / SHA) — MAJOR finding.
- **Mixing transports** in a single server entry (stdio + HTTP) — BLOCKER (`.mcp.json` schema rejects).

## Cross-references

- **KB-mcp-platform** — the platform half (facts, install forms, lifecycle, event schema).
- **`auditing-mcp`** — the audit half (graduated family per ADR-0042; OP-1..OP-10 rules).
- **ADR-0007 v2.2.0** — code-graph primary/fallback policy.
- **ADR-0037** — `mcp-events.jsonl` event surface.
- **ADR-0039** — credential redaction posture.
- **ADR-0040** — Serena narrowed always-on (5-agent allowlist precedent).
- **ADR-0041** — install-mechanism hybrid.
- **ADR-0042** — auditing-mcp family graduation.
- **ADR-0043** — auditing-mcp Gate-6 hard gate.
