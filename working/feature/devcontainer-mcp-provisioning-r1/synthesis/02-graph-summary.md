# Entity Graph Summary — devcontainer-mcp-provisioning-r1

**Generated:** 2026-05-23
**Source:** `01-claims.json` (545 merged claims, 9 sources)
**Output:** `02-graph.json`
**Entities:** 111
**Edges:** 117
**Communities identified:** 7

## Top entities by claim count

| Rank | Entity | Type | Claims |
|------|--------|------|--------|
| 1 | mcp-openapi-schema (E-0002) | service | 63 |
| 2 | Serena (E-0001) | service | 59 |
| 3 | GitNexus (E-0007) | service | 57 |
| 4 | Context7 (E-0005) | service | 49 |
| 5 | Terraform MCP Server (E-0004) | service | 47 |
| 6 | Exa MCP Server (E-0006) | service | 38 |
| 7 | npm/npx install mechanism (E-0012) | tool | 28 |
| 8 | actionlint-mcp (E-0003) | service | 27 |
| 9 | remote HTTP transport (E-0010) | pattern | 26 |
| 10 | stdio transport (E-0009) | pattern | 25 |

## Top edges by claim count

| Rank | From → To | Relation | Claim count |
|------|-----------|----------|-------------|
| 1 | codebase-memory-mcp (E-0008) → GitNexus (E-0007) | supersedes (fallback-for) | 10 |
| 2 | Serena (E-0001) → markdown-heavy repo (E-0056) | conflicts_with | 4 |
| 3 | Node.js runtime (E-0016) → Debian-bookworm base (E-0015) | conflicts_with | 5 |
| 4 | Exa MCP (E-0006) → EXA_API_KEY (E-0018) | requires | 7 |
| 5 | Context7 (E-0005) → CONTEXT7_API_KEY (E-0019) | requires | 8 |
| 6 | Terraform MCP (E-0004) → TFE_TOKEN (E-0020) | requires | 6 |
| 7 | GitNexus (E-0007) → npm/npx (E-0012) | requires | 8 |
| 8 | Terraform MCP (E-0004) → no-DinD (E-0017) | conflicts_with | 4 |
| 9 | version-pinning (E-0073) → supply-chain review (E-0074) | implements | 7 |
| 10 | abandonment risk (E-0101) → mcp-openapi-schema (E-0002) | instance_of | 6 |

## Identified clusters (hand-curated, ≤120 entities)

### Cluster A: Seven MCP Servers (hub-and-spoke around each server)

**Hub entities:** E-0001 Serena, E-0002 mcp-openapi-schema, E-0003 actionlint-mcp, E-0004 Terraform MCP, E-0005 Context7, E-0006 Exa, E-0007 GitNexus, E-0008 codebase-memory-mcp (fallback for E-0007)

Each server fans out to transport (stdio/HTTP), install mechanism (uvx/npm/Go/binary/npx), auth surface (none / EXA_API_KEY / CONTEXT7_API_KEY / TFE_TOKEN), and consuming agent. The most heavily connected sub-cluster is the GitNexus / codebase-memory-mcp pair, which carries the load-bearing primary/fallback relationship referenced from ADR-0007, ADR-0018, KB-codebase-research, and discovery-codebase-researcher.

### Cluster B: Transports & Install Mechanisms

**Hub entities:** E-0009 stdio, E-0010 remote HTTP, E-0011 uvx, E-0012 npm/npx, E-0013 Go install, E-0014 pre-built binary

Bridges Cluster A (servers) to Cluster C (base image constraints) via `requires` and `conflicts_with` edges. Six of seven servers settle on stdio for the devcontainer; only Context7 and Exa have remote-HTTP variants.

### Cluster C: Base Image Constraints

**Hub entities:** E-0015 Debian-bookworm Python 3.11 base, E-0016 Node.js runtime, E-0066 C++ toolchain, E-0017 no-DinD, E-0072 Node devcontainer feature, E-0067 GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1

Captures the toolchain-fit dimension. Three high-stakes `conflicts_with` edges land here: Node ↔ base image, Go toolchain ↔ base image, C++ toolchain ↔ base image. The skip-grammars flag (E-0067) is the GitNexus-specific workaround that eliminates the C++ dependency.

### Cluster D: Auth & Credential Hygiene

**Hub entities:** E-0018 EXA_API_KEY, E-0019 CONTEXT7_API_KEY, E-0020 TFE_TOKEN, E-0022 Codespaces secrets, E-0030 credential redaction, E-0031 OWASP MCP01, E-0094 argv leakage anti-pattern, E-0095 URL-embedded credential anti-pattern, E-0021 no-auth pattern

The `conflicts_with` edges between credential-bearing env vars and the two anti-patterns (argv leakage, URL embedding) are load-bearing for the FR-4 probe and the redaction-list-equals-env-vars invariant proposed in F4.4 / OQ-B.

### Cluster E: MCP Operational Discipline

**Hub entities:** E-0027 ping primitive, E-0028 notifications/message logging, E-0029 stderr-only logging, E-0030 credential redaction, E-0032 Anthropic MCP spec, E-0086 /health & /ready, E-0087 structured JSON logs, E-0088 MCP_TIMEOUT, E-0089 Claude Code reconnect, E-0107 Fast.io patterns

Bridge to Cluster A through `implements` and `requires`. The `supersedes` edge from E-0027 (ping) to E-0086 (/health) records the spec-canonical-vs-HTTP-convention reality: ping works uniformly across stdio and HTTP, while /health is HTTP-only.

### Cluster F: Failure-Feedback Pattern Space (UI-15 / FR-9)

**Hub entities:** E-0035 mcp-events.jsonl, E-0036 primary-to-fallback transition pattern, E-0037 circuit-breaker, E-0082 stderr banner option, E-0083 agent-level acknowledgement option, E-0084 active ping-loop, E-0085 ToolHive proxy pattern, E-0111 extraction_method field

This cluster is the most greenfield in the graph — Synthesizer should flag that F5.4 explicitly declares no-consensus across surveyed literature. The `supersedes` edge from E-0036 to E-0089 (Claude Code reconnect) records that the project is augmenting baseline Claude Code observability with a structured-event-file convention that does not exist by default.

### Cluster G: W/H/A Trifecta + Adjacent Skills

**Hub entities:** E-0042 KB-mcp-platform (greenfield), E-0043 KB-mcp-design (greenfield), E-0044 auditing-mcp (existing, augmented), E-0045 auditing-cc-configs family coordinator, E-0046 auditing-codespaces (stub), E-0047 auditing-github-actions, E-0048 auditing-shared, E-0049 KB-cc-platform, E-0050 KB-codespaces-platform, E-0051 KB-github-actions-platform, E-0052/53/54/55 trifectas

Three existing trifectas (CC, Codespaces, GHA) plus the new MCP trifecta. The `conflicts_with` edge between E-0044 (auditing-mcp) and E-0046 (auditing-codespaces stub) records that the latter is a stub-per-ADR-0033, leaving the devcontainer-layer changes without a family-auditor backstop. The `conflicts_with` edge between E-0044 and E-0049 (KB-cc-platform) records the UI-13 duplicate-template question — KB-cc-platform already owns an `mcp-config.json.example`.

## Bridge entities (cross-cluster, high PageRank)

- **E-0009 stdio transport** — bridges Cluster A (servers) to Cluster B (transports) to Cluster E (operational discipline; ping/stderr).
- **E-0033 Claude Code MCP host** — bridges every server to E-0034 .mcp.json, E-0032 MCP spec, E-0088 MCP_TIMEOUT, E-0089 reconnect behavior. Load-bearing for design composition.
- **E-0034 .mcp.json config schema** — bridges Clusters A, D, E, G. Receives `implements` edges from E-0049 (template), E-0033 (host), E-0030 (redaction reads env block), E-0088 (timeout field).
- **E-0007 GitNexus** and **E-0008 codebase-memory-mcp** — bridge Cluster A and Cluster F via the primary/fallback `supersedes` edge and the four-layer prose-only documentation chain (E-0038, E-0039, E-0040, E-0041).

## Wardley-stage observations (for memory)

The graph-construction substrate has no Louvain modularity available, so community detection here is hand-curated. This is consistent with the SKILL.md note that Louvain is `genesis`-stage and falls back to manual clustering for now. Graph size (111 entities) sits just above the "≤100 hand-curated is fine" threshold; clustering effort was still tractable.

## Schema-drift note

ADR-0018 (v1.0.0) ↔ KB-codebase-research / discovery-codebase-researcher (v1.1.0) drift is represented in this graph by the explicit finding entity E-0079 with a `conflicts_with` edge to E-0039 (ADR-0018). This makes the dissent visible to downstream Critic / Framer / Substrate / Synthesizer without their needing to re-extract it from the codebase claims.

## Cross-references

- Critic, Framer, Substrate, Synthesizer consume the canonical `02-graph.json`.
- This summary file is for human review only.
