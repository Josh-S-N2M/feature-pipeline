# Graph summary — pipeline-quickwins-hardening-r1

Generated 2026-05-26. 113 entities, ~120 edges, 201 claims (codebase 116 + T-001 47 + T-002 38).

This file is for human review only. Downstream phases (Critic, Framer, Substrate, Synthesizer) consume `02-graph.json`.

---

## Top entities by claim back-pointer count

| Entity ID | Name | Type | Claims |
|---|---|---|---|
| E-0076 | GITNEXUS_SKIP_OPTIONAL_GRAMMARS env-var contract | control | 22 |
| E-0003 | FR-3 ADR-0041 / .mcp.json parity audit | control | 19 |
| E-0001 | FR-1 verdict/findings parity guard | control | 19 |
| E-0104 | Claude Code CLI canonical documentation | standard | 14 |
| E-0059 | Verdict+findings emission contract | pattern | 13 |
| E-0075 | GitNexus v1.6.5 | service | 13 |
| E-0077 | build-tree-sitter-dart.cjs (postinstall guard) | tool | 12 |
| E-0007 | FR-7 deferral-register marker tightening | control | 11 |
| E-0002 | FR-2 single-agent fallback self-check | control | 11 |
| E-0025 | recipe-feature-pipeline | tool | 10 |
| E-0036 | .devcontainer/postCreate.sh | tool | 8 |

## Top edges by claim_ids count

| From → To | Relation | Claims |
|---|---|---|
| E-0001 (FR-1) → E-0059 (verdict+findings contract) | requires | 5 |
| E-0001 (FR-1) → E-0060 (severity taxonomy) | requires | 3 |
| E-0003 (FR-3) → E-0026 (auditing-mcp) | requires | 6 |
| E-0010 (U-3) → E-0003 (FR-3) | requires | 4 |
| E-0091 (recommended dry-run pair) → E-0089 (artifact-absence signal) | requires | 2 (but pins critical contract) |
| E-0102 (system/init event) → E-0101 (McpServerStatus enum) | requires | 3 |
| E-0105 (recommended CI invocation) → E-0094 (claude --bare -p) | requires | 2 |
| E-0029 (mcp-openapi-schema removed) → E-0028 (ADR-0041) | conflicts_with | 3 |
| E-0029 → E-0027 (.mcp.json) | conflicts_with | 3 |
| E-0086 (GitNexus README) → E-0076 (env-var contract) | conflicts_with | 3 |
| E-0092 (drift modes) → E-0076 | conflicts_with | 5 |

(Edges with ≥3 supporting claims are over-represented relative to the median; the FR-* → mechanism-target edges are typically backed by 2–6 claims each, indicating dense convergent evidence.)

---

## Identified clusters

The graph naturally separates into six topical clusters. Connected-component analysis is unnecessary at this size; clusters are hand-curated by topic and confirmed by edge density.

### Cluster A — FR-1 reviewer/verdict-findings scope (PRD's largest mechanism)

**Bridge entities:** E-0001 (FR-1), E-0059 (Verdict+findings emission contract), E-0060 (severity taxonomy), E-0061 (severity-to-verdict mapping)

**Members:**
- Reviewer agents: E-0013 shared-document-reviewer, E-0014 review-architecture-auditor, E-0015 review-cross-artifact-auditor, E-0016 execute-phase-quality-reviewer, E-0017 execute-task-quality-handler, E-0018 finalize-deliverable-packager
- Excluded but adjacent: E-0019 synth-critic, E-0020 synth-framer, E-0021 synth-synthesizer, E-0022 finalize-reconciler, E-0023 execute-finalize-reconciler
- Standards: E-0045 ADR-0017 reviewer invocation points
- Open item: E-0008 U-1 scope completeness

**Note:** all six in-scope reviewers `implements` the verdict+findings contract; FR-1 is the enforcing layer atop these report-only emitters. The U-1 open item is dominated by the execute-task-quality-handler inclusion question (US-1 contradiction precisely matches its APPROVED + blocker-finding case).

### Cluster B — FR-2 single-agent fallback / parent orchestrator nexus

**Bridge entities:** E-0025 recipe-feature-pipeline (HIGH-blast dispatch nexus), E-0002 FR-2

**Members:** E-0024 execute-orchestrator (advisor), E-0044 ADR-0044 flatten decision, E-0071 checkpoint.json, E-0072 agent frontmatter contract, E-0073 TaskUpdate logging convention, E-0108 reviewer dispatch invocation table, E-0112 checkpoint.execution_mode = parent-driven-workaround, E-0009 U-2 self-check site & config surface, E-0052 design-claude-code

**Note:** the parent orchestrator carries FOUR distinct FR-* touches per codebase-C-0072 — FR-1 check, FR-2 self-check, FR-3 audit dispatch, FR-7 metadata. The HIGH blast radius (codebase-C-0066) is structural, not pathological. U-2 forces design-claude-code to decide both site (where in the SKILL.md to place the check) and configuration surface (what FR-2 inspects).

### Cluster C — FR-3 ADR/.mcp.json parity + deprecation handling

**Bridge entities:** E-0003 FR-3, E-0027 .mcp.json, E-0028 ADR-0041, E-0029 mcp-openapi-schema (removed)

**Members:** E-0026 auditing-mcp skill, E-0030 actionlint-mcp, E-0031 context7, E-0032 exa, E-0033 gitnexus MCP server, E-0034 serena, E-0035 terraform-mcp, E-0042 ADR-0042, E-0043 ADR-0043 Gate-6, E-0046 ADR-0005 append-only, E-0049 KB-mcp-platform, E-0065 OP-rule script contract, E-0074 CLAUDE.md, E-0109 ADR-0041 invocation table, E-0111 stale ADR/KB reference posture, E-0010 U-3 deprecation handling

**Note:** the mcp-openapi-schema row is the load-bearing day-one false-positive trigger. It conflicts with E-0027 (live config has 6 servers) AND with E-0028 (the table that still names it) AND with E-0049 (KB still references it as one of seven) AND with E-0074 (CLAUDE.md acknowledges it's a stale-doc issue). U-3 picks among three options (a) in-rule marker, (b) ADR amendment, (c) script allowlist; (a) is preferred per CLAUDE.md framing + ADR-0005 append-only.

### Cluster D — FR-4 GitNexus install dry-run + env-var contract

**Bridge entities:** E-0004 FR-4, E-0036 .devcontainer/postCreate.sh, E-0075 GitNexus v1.6.5, E-0076 GITNEXUS_SKIP_OPTIONAL_GRAMMARS env-var contract, E-0083 node-gyp

**Members:**
- Build scripts: E-0077 dart guard, E-0078 proto guard
- Grammars: E-0079 dart, E-0080 proto, E-0081 swift, E-0082 kotlin
- Patterns: E-0084 npm optionalDependencies tolerated-skip, E-0091 recommended dry-run signal pair
- Signals: E-0087 stderr signal 1, E-0088 process-tree signal 2, E-0089 artifact-absence signal 3, E-0090 wall-clock signal 4
- Drift / risk findings: E-0085 issue #1024 swift binding.gyp, E-0086 GitNexus README (conflict with code), E-0092 drift modes DM-1..DM-4, E-0113 verbatim warning text fragility
- Pins: E-0037 versions.env, E-0033 gitnexus MCP server
- Infra: E-0038 log-mcp-event.sh, E-0039 ADR-0037, E-0040 ADR-0039, E-0070 MCP event types, E-0062 two-check idempotency, E-0063 sentinel-naming conventions, E-0066 set -euo pipefail
- Cross-cuts: E-0068 NFR-13, E-0006 FR-6 diagnostics, E-0064 dual-stream diagnostics, E-0011 U-4 sentinel posture, E-0053 design-codespaces

**Note:** This is the largest cluster (~25 entities) and is also the most contract-heavy. The recommended dry-run pair (E-0091) is anchored on signals 1+3 because signal 1 alone is literal-string fragile (E-0113) and signal 3 alone could be true for unrelated reasons (E-0084 npm tolerated-skip). The README/code Swift divergence (E-0086 conflicts_with E-0076) is a Gate-3 known caveat — dry-run must not assert Swift via this env var.

### Cluster E — FR-5 greenfield CI workflow + claude mcp list contract gap (T-002)

**Bridge entities:** E-0005 FR-5, E-0047 .github/workflows/ (greenfield), E-0093 claude mcp list, E-0094 claude --bare -p, E-0105 recommended CI MCP-health-check invocation, E-0104 Claude Code CLI canonical documentation

**Members:**
- CLI surfaces: E-0095 claude install, E-0096 claude auth status, E-0097 claude daemon status, E-0098 claude ultrareview, E-0099 /mcp slash, E-0100 --init-only
- SDK standards: E-0101 McpServerStatus enum, E-0102 system/init event, E-0103 Claude Code Agent SDK
- Findings: E-0106 undocumented-behavior risk, E-0107 documented version pins (v2.1.64/.111/.121/.144)
- Skill: E-0048 KB-github-actions-platform
- Controls: E-0110 KB security non-negotiables
- Designers: E-0054 design-cicd, E-0055 design-composer

**Note:** This cluster's load-bearing finding is the silence — E-0104 documents exit-code contracts for every sibling command (E-0096/97/98) but is silent on E-0093 (mcp list). The recommended substitute path (E-0105) supersedes the brittle CLI grep on E-0093 by going through E-0094 → E-0102 → E-0101. This is the only `supersedes` edge family in the graph (3 edges: E-0093→E-0099, E-0105→E-0093). FR-5 transitively requires the recommended invocation since it's the first GitHub Actions workflow in the project (E-0047 greenfield).

### Cluster F — FR-7 deferral-register tightening

**Bridge entities:** E-0007 FR-7, E-0050 deferral register, E-0067 deferral-register row update convention, E-0051 cross-artifact-divergence-detection-gap proposal

**Members:** E-0012 U-7, E-0055 design-composer, E-0052 design-claude-code

**Note:** smallest cluster; FR-7 substantive work is largely already done — U-7 confirms marker text and decides packaging.

### Cross-cluster bridge entities

- **E-0025 recipe-feature-pipeline** — bridges A (FR-1 check sites), B (FR-2 home), C (FR-3 dispatch reads), F (FR-7 metadata) — single dispatch nexus, four touches per codebase-C-0072.
- **E-0027 .mcp.json** — bridges C (FR-3 target) and D (FR-4 GitNexus row referenced)
- **E-0028 ADR-0041** — bridges C (FR-3 source) and D (FR-4 no-Dockerfile + sentinel convention origin)
- **E-0070 MCP event types** — bridges D (FR-4 emission) and E (FR-5 health-check)
- **E-0052 design-claude-code** — bridges A, B, C, F (designer carries U-1, U-2, U-3 partial, U-7 partial)
- **E-0041 ADR-0040 allowlist policy** — bridges into NFR-15 (E-0069) and binds all seven allowlisted sub-agents

---

## Provenance / coverage check

Every claim ID (codebase-C-0001..0116, t001-C-0001..0047, t002-C-0001..0038) appears in at least one entity's `claims[]` back-pointer. Spot-check: claims that frame multiple entities (e.g., codebase-C-0072 = "four touches" appears in E-0001, E-0002, E-0003, E-0007, E-0025) are correctly multi-anchored.

Edges with the strongest evidence base (5+ claims) cluster around:
- FR-1 ↔ verdict-findings emission contract (5 claims)
- FR-3 ↔ auditing-mcp skill (6 claims)
- Drift modes ↔ env-var contract (5 claims)
- mcp-openapi-schema row ↔ ADR-0041 and CLAUDE.md and KB-mcp-platform stale-doc posture (chain of 3+3+1 claims across three conflicts_with edges)

No orphan entities; no edges with empty claim_ids.
