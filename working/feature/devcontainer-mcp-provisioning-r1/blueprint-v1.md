---
id: BP-devcontainer-mcp-provisioning-r1
version: 1.0.0
status: draft
doc_type: blueprint
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
codebase_analysis: working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json
adrs_referenced:
  - ADR-0005   # append-only supersession discipline
  - ADR-0007   # GitNexus / codebase-memory-mcp primary/fallback (v2.2.0)
  - ADR-0018   # codebase-analysis schema v1.0 — superseded by ADR-0038 in this feature
  - ADR-0020   # KB structure / lowercase-hyphenated skill name
  - ADR-0022   # subagent reasoning configuration
  - ADR-0030   # pedagogical-marker justification spec
  - ADR-0031   # auditing-shared skill module
  - ADR-0033   # auditing-codespaces STUB / ADR-0029 execution extension
  - ADR-0036   # single-location ADR placement
adrs_authored:
  - ADR-0037   # mcp-events.jsonl + stderr-banner transition surfacing
  - ADR-0038   # codebase-analysis schema v1.1.0 (supersedes ADR-0018 v1.0.0)
  - ADR-0039   # credential redaction posture — redact-at-source from .mcp.json env-block
  - ADR-0040   # Serena posture — narrowed always-on; Python-audit-surface allowlist; pin pre-v1.3.0
  - ADR-0041   # install-mechanism — hybrid Features + idempotent postCreate + verified binary fetch
generated: 2026-05-23T00:00:00Z
generated_by: design-composer
---

# Devcontainer MCP Server Provisioning — Design Document

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Overview
- [x] Design Summary (Meta)
- [x] Background and Context
- [x] Acceptance Criteria (AC) - EARS Format
- [x] Existing Codebase Analysis
- [x] Design
- [x] Implementation Plan
- [x] Security Considerations
- [x] Test Boundaries
- [x] Verification Strategy
- [x] Future Extensibility
- [x] Alternative Solutions
- [x] Risks and Mitigation
- [x] References
- [x] Update History

## Overview

This feature provisions seven named MCP servers (Serena, mcp-openapi-schema, actionlint-mcp, HashiCorp Terraform MCP, Context7, Exa, GitNexus) plus the codebase-memory-mcp fallback into this project's devcontainer; wires them into seven of the project's 36 sub-agents under a least-privilege `mcp__<server>__<tool>` allowlist; adds the W/H/A trifecta halves (KB-mcp-platform, KB-mcp-design) plus an augmented audit-half (auditing-mcp) so MCP operations remain reasonable about long after this feature ships; and codifies the lifecycle health-check, runtime log, transition-surfacing, and credential-redaction posture necessary to detect and recover from MCP failures across the Codespace lifecycle.

The two layers that own the work are **Claude Code / Project Filesystem** (`.mcp.json`, the seven `tools:` allowlist edits across 36 agents, the trifecta skills, the `mcp-events.jsonl` schema) and **Dev Environment / Codespaces** (devcontainer.json features block, lifecycle hooks, install scripts, secret wiring, postStart readiness probe). The five ADRs authored in this Blueprint (ADR-0037 through ADR-0041) codify the architecturally one-way decisions; the rest are integrated per-layer subsections that compose into a single shipping unit.

### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers are marked `N/A — out of scope` without further elaboration.

- [x] **Claude Code / Project Filesystem** — `.mcp.json` (NEW), 7 `.claude/agents/*.md` `tools:` allowlist edits, `KB-mcp-platform/` (NEW), `KB-mcp-design/` (NEW), augmented `auditing-mcp/`, `.claude/runtime/mcp-events.jsonl` (NEW; gitignored)
- [ ] **Frontend** — N/A: not in scope per PRD Layer Scope
- [ ] **Backend** — N/A: not in scope per PRD Layer Scope
- [ ] **API** — N/A: not in scope per PRD Layer Scope
- [ ] **Query / Data Access** — N/A: not in scope per PRD Layer Scope
- [ ] **Database** — N/A: not in scope per PRD Layer Scope
- [ ] **CI/CD (GitHub Actions)** — N/A: not in scope per PRD Layer Scope (PRD Won't-Have: CI smoke-test for `claude mcp list`)
- [ ] **Infrastructure as Code** — N/A: not in scope per PRD Layer Scope
- [x] **Dev Environment (Codespaces / Devcontainer)** — `.devcontainer/devcontainer.json` (features block + containerEnv updates), `.devcontainer/postCreate.sh` (NEW), `.devcontainer/postStart.sh` (NEW), `.devcontainer/install/terraform-mcp.sh` (NEW), `.devcontainer/lib/mcp-ping.sh` + `mcp-auth-probe.sh` (NEW), `.devcontainer/versions.env` (NEW)

### Referenced Specifications

- **UI Spec** — N/A (no frontend)
- **API Spec** — N/A (no API)
- **Data Model Spec** — N/A (no DB)
- **Runbook / Operational Spec** — `KB-mcp-platform/references/lifecycle-hooks.md` (NEW; authored in this feature) serves the runbook role for MCP operations.

## Design Summary (Meta)

```yaml
design_type: "new_feature"
risk_level: "medium"
complexity_level: "medium"
complexity_rationale: |
  Two-layer cross-cutting work with five composing one-way architectural decisions
  (ADR-0037 through ADR-0041). The complexity is bounded by the closed seven-server
  list and the prose-only-with-audit-rule resolution to UI-15 (which avoids
  inventing a 36-agent-wide structured frontmatter convention). The augmented
  auditing-mcp skill is the project's safety-net: 10 rule families (OP-1..OP-10)
  cover static config, runtime events, and trifecta consistency.
layers_touched:
  - "Claude Code / Project Filesystem"
  - "Dev Environment (Codespaces / Devcontainer)"
blast_radius:
  runtime: "All 36 sub-agents see new .mcp.json registrations; 7 agents gain new mcp__ tool entries; the 29 untouched agents preserve the C-0445 zero-mcp__ invariant"
  build_time: "Cold-cache devcontainer build estimated ~7–12 min (NFR-1 target ~10 min); warm-cache ~1–2 min via version-pinned sentinels"
main_constraints:
  - "Base image (mcr.microsoft.com/devcontainers/python:1-3.11-bookworm) is fixed; constraints #1-4 from synthesis §8 (no Go, no Node, no DinD in base)"
  - "PRD Q4 closed list: all seven servers always-on at project scope"
  - "OWASP MCP01 Token Mismanagement is the top-ranked MCP risk (codified by ADR-0039)"
  - "Existing C-0445 zero-mcp__ invariant on the 29 non-consumer agents must be preserved"
  - "ADR-0005 append-only supersession (ADR-0018 v1.0.0 is preserved; ADR-0038 v1.1.0 is the new canonical)"
biggest_risks:
  - "Cold-cache build time sits near the NFR-1 ~10-min target upper bound; mitigation deferred to post-ship prebuild adoption"
  - "GitNexus skip-grammars smoke-test is partially_verified-medium (C-0388/C-0411 Mintlify-mirrored); fail-postCreate on smoke-test failure (AC-CS-9)"
  - "Stdio servers are not auto-reconnected by Claude Code (C-0301 verbatim Anthropic); six of seven servers fail open to operator recovery → FR-9 structured-failure-record (ADR-0037) is load-bearing"
unknowns:
  - "Whether `claude mcp ping` exists in the pinned Claude Code Feature version (OI-CS-5 verify-at-execution; ADR-0041 codifies fallback to direct JSON-RPC)"
  - "Whether the augmented auditing-mcp is a hard Gate 6 gate or a strongly-recommended check (Q-CC-9 → deferred to user; Open Items)"
  - "Exact actionlint-mcp commit SHA at install time (C-0133 no tagged releases as of 2026-05-23 — verify-at-execution)"
```

## Background and Context

### Prerequisite ADRs

- **ADR-0005** — append-only supersession discipline (this Blueprint supersedes ADR-0018 v1.0.0 via ADR-0038; both files preserved).
- **ADR-0007 v2.2.0** — GitNexus primary / codebase-memory-mcp fallback policy. This feature provisions both; it does NOT re-decide the policy.
- **ADR-0018 v1.0.0** — codebase-analysis schema (superseded in this feature by ADR-0038 v1.1.0).
- **ADR-0020** — KB structure / lowercase-hyphenated skill name convention. The two new skills (`KB-mcp-platform`, `KB-mcp-design`) conform.
- **ADR-0022** — subagent reasoning configuration. Per cc-design Principle 9, this feature does NOT modify any agent's `model:`/`effort:`/`skills:` fields; only `tools:` arrays are touched.
- **ADR-0030** — pedagogical-marker justification spec. Both new skills declare `pedagogical_sections` frontmatter.
- **ADR-0031** — auditing-shared skill module. Referenced indirectly by `auditing-mcp` augmentation.
- **ADR-0033** — auditing-codespaces STUB / ADR-0029 execution extension. The augmented auditing-mcp owns lifecycle-completeness audit (OP-5) until auditing-codespaces stub is filled.
- **ADR-0036** — single-location ADR placement. ADR-0007 relocation per ADR-0038 honors this.

**Authored in this feature:** ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041 (see ADR References below).

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|-------------------------------|-----------------------------|-------|
| Devcontainer base image | `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` | unchanged |
| Devcontainer Feature: Node | `ghcr.io/devcontainers/features/node:1` with `version: "20"` (NEW pin) | LTS major per ADR-0041 |
| Devcontainer Feature: Go | `ghcr.io/devcontainers/features/go:1` (NEW) | for `actionlint-mcp go install` per ADR-0041 |
| Devcontainer Feature: common-utils | `ghcr.io/devcontainers/features/common-utils:2` | preserved |
| Devcontainer Feature: github-cli | `ghcr.io/devcontainers/features/github-cli:1` | preserved |
| Devcontainer Feature: claude-code | `ghcr.io/anthropics/devcontainer-features/claude-code:1` | preserved; consumer of `.mcp.json` |
| MCP upstream: Serena | `git+https://github.com/oraios/serena@<PIN_PRE_V1.3.0>` via uvx | ADR-0040 narrow allowlist; pin form per ADR-0041 |
| MCP upstream: mcp-openapi-schema | `npx -y mcp-openapi-schema@0.0.1` | exact-tag pin (verify-at-execution C-0073) |
| MCP upstream: actionlint-mcp | `go install github.com/2manymws/actionlint-mcp/cmd/actionlint-mcp@<sha>` | commit-SHA pin (no tagged releases C-0133) |
| MCP upstream: Terraform MCP | `wget` release artifact from `releases.hashicorp.com`; SHA256 + GPG verify | binary-fetch path per ADR-0041 |
| MCP upstream: GitNexus | `uvx --from gitnexus@<TAG>`; `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` smoke-test | per ADR-0007 v2.2.0 |
| MCP upstream: codebase-memory-mcp | per ADR-0007 v2.2.0 fallback | 8th `.mcp.json` entry; documented fallback |
| MCP upstream: Context7 | `https://mcp.context7.com/mcp` (remote HTTP) | `CONTEXT7_API_KEY` header per ADR-0039 |
| MCP upstream: Exa | `https://mcp.exa.ai/mcp` (remote HTTP) | `x-api-key` header per ADR-0039; URL-query form REJECTED |
| Codespaces secrets | `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` (TFE_TOKEN optional) | via `${localEnv:NAME}` indirection in `containerEnv` |

### Agreement Checklist

#### Scope

- [x] `.mcp.json` (NEW at repo root) — register all 7 named servers plus codebase-memory-mcp fallback (8 mcpServers entries total; see Open Item resolution OI-1)
- [x] 7 of 36 `.claude/agents/*.md` files — add `mcp__<server>__<tool>` entries
- [x] `KB-mcp-platform/` (NEW skill) — trifecta What-half
- [x] `KB-mcp-design/` (NEW skill) — trifecta How-half
- [x] `auditing-mcp/` augmentation — 10 new rule families (OP-1..OP-10)
- [x] `.claude/runtime/mcp-events.jsonl` schema (NEW; gitignored; ADR-0037)
- [x] `.devcontainer/devcontainer.json` — Features block additions (Node 20 LTS pin; Go); containerEnv updates for three Codespaces secrets
- [x] `.devcontainer/postCreate.sh` (NEW) — idempotent install; sentinel-guarded with binary-presence check
- [x] `.devcontainer/postStart.sh` (NEW) — readiness probe writing `readiness_probe` records to `mcp-events.jsonl`
- [x] `.devcontainer/install/terraform-mcp.sh` (NEW) — wget + SHA256 + GPG verify
- [x] `.devcontainer/lib/mcp-ping.sh` + `mcp-auth-probe.sh` (NEW) — probe helpers
- [x] `.devcontainer/versions.env` (NEW) — per-server pin table

#### Non-Scope (Explicitly not changing)

- [x] No Dockerfile changes (ADR-0041 codifies)
- [x] No CI/CD layer changes (PRD Won't-Have)
- [x] No IaC layer changes (PRD Won't-Have)
- [x] No changes to pipeline stages, gates, or orchestrator (PRD Policy Decision)
- [x] No `model:`/`effort:`/`skills:` field changes on any agent (cc-design Principle 9)
- [x] Preserve C-0445 zero-`mcp__` invariant for the 29 non-consumer agents
- [x] No new CLAUDE.md (cc-design — knowledge lives in the two new skills, model-invocable)
- [x] No new `.claude/rules/` (cc-design)
- [x] No new hooks (cc-design Principle 3)
- [x] No plugin packaging in this feature (Q-CC-7 deferred to follow-up)

#### Constraints

- [x] Parallel operation: N/A (no existing MCP wiring to operate in parallel with)
- [x] Backward compatibility: Required — preserve C-0445 zero-`mcp__` invariant for non-consumer agents; preserve existing devcontainer Feature pins where not modified.
- [x] Performance measurement: Required — NFR-1 cold-cache ≤ ~10 min, warm-cache ≤ ~2 min; postStart probe ≤ ~2 s; tracked in Verification Strategy.
- [x] Zero-downtime deployment: N/A (project is operator-run; "deployment" = devcontainer rebuild)
- [x] Forward-compatible migration: Required — ADR-0038 schema v1.1.0 is additive; v1.0.0 outputs remain readable.

#### Applicable Standards

- [x] **W/H/A trifecta convention** `[explicit]` — Source: synthesis §6 / cc-design §Skill patterns / 3 existing trifecta precedents (KB-cc-*, KB-codespaces-*, KB-github-actions-*).
- [x] **ADR-0020 skill naming** `[explicit]` — lowercase-hyphenated `name:` field; `KB-` directory prefix.
- [x] **ADR-0030 pedagogical_sections** `[explicit]` — Both new skills declare entries with justifications.
- [x] **EARS acceptance criteria** `[explicit]` — All ACs use the EARS form (per KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md).
- [x] **C-0445 zero-`mcp__` invariant** `[implicit]` — Evidence: grep-verified codebase-analysis. Confirmed: Yes.
- [x] **OWASP MCP01 Token Mismanagement** `[explicit]` — Source: T-007-mcp-operational.md F4. Codified by ADR-0039.

#### Quality Assurance Mechanisms

- [x] **`auditing-mcp` skill (augmented)** — Enforces: 10 rule families (OP-1 env-block coverage; OP-2 consumer-mapping; OP-3 zero-`mcp__` preservation; OP-4 primary/fallback prose; OP-5 lifecycle completeness; OP-6 runtime log redaction; OP-7 trifecta consistency; OP-8 GitNexus-specific; OP-9 URL-credential rejection; OP-10 argv-leakage absence) — Config: `.claude/skills/auditing-mcp/` — Covers: `.mcp.json`, all 36 agent files, `mcp-events.jsonl`, devcontainer.json — Status: `adopted`.
- [x] **Per-server probe (FR-4)** — Enforces: every registered server responds to a real call — Config: each server's documented probe (JSON-RPC ping + Context7/Exa supplementary auth probe gated on env flag per D-8) — Covers: 8 mcpServers entries — Status: `adopted`.
- [x] **Lifecycle health-check (FR-8)** — Enforces: surface health at postCreate / postStart / on-demand — Config: `postStart.sh` writes to `mcp-events.jsonl` — Covers: all 8 registered servers (7 PRD-named + codebase-memory-mcp fallback) — Status: `adopted`.
- [x] **`gitignore` of `.claude/runtime/mcp-events.jsonl`** — Enforces: no credential capture into git — Config: `.gitignore` — Covers: project-wide — Status: `adopted`.
- [x] **`.devcontainer/versions.env` pin discipline** — Enforces: per-server version pin (D-0011) — Covers: 5 OSS-local servers — Status: `adopted`.

### Problem to Solve

A freshly built Codespace cannot run discovery- or design-stage sub-agents end-to-end without manually installing and registering the seven MCP servers (PRD Background). After this feature, every Codespace ships with the seven servers connected, the agent allowlists already wired, the lifecycle health-check reporting per-server status at every devcontainer boundary, and the W/H/A trifecta available so future operators can reason about MCP independently.

### Current Challenges

- `.mcp.json` is absent (C-0462 grep-verified). All 36 agents currently have zero `mcp__` entries (C-0445).
- The W/H/A trifecta for MCP is incomplete: `auditing-mcp` exists but `KB-mcp-platform` and `KB-mcp-design` do not.
- ADR-0018 v1.0.0 (in `adrs-migrated/`) drifts against downstream KB/agent references to v1.1.0 (C-0441 / C-0495).
- F5.4 NO CONSENSUS PATTERN (C-0349) on primary→fallback transition surfacing means the convention is novel — no upstream precedent to lift.
- OWASP MCP01 Token Mismanagement (C-0333) is unmitigated until ADR-0039 ships.

### Requirements

#### Functional Requirements (from PRD)

- **FR-1** Seven servers installed + registered always-on (`.mcp.json` project scope).
- **FR-2** Affected sub-agents carry the new tools in their `tools:` allowlists.
- **FR-3** Tool-to-agent wiring is expressed in human-readable repo files (no runtime mutation).
- **FR-4** Per-server probe verifies every server at acceptance.
- **FR-5** Credentials flow via Codespaces secrets only (no secret values committed).
- **FR-6** Rebuild fits NFR-1 envelope.
- **FR-8** Lifecycle health-check at postCreate / postStart / postAttach with operator-visible status.
- **FR-9** Runtime MCP failures surface with named server, layer, remediation pointer — no silent fallback.
- **FR-10** Per-server runtime log/diagnostic data sufficient for root-cause without re-running.
- **FR-11** W/H/A trifecta completed (KB-mcp-platform + KB-mcp-design; auditing-mcp augmented).

#### Non-Functional Requirements (from PRD)

- **Performance**: cold-cache build ≤ ~10 min, warm-cache ≤ ~2 min; MCP startup ≤ ~30 s per session; postStart probe ≤ ~15 s; log overhead ≤ ~5%.
- **Scalability**: per-agent context-overhead within tolerable envelope; tool schemas deferred until invoked (cc-design Principle 1).
- **Reliability**: per-server probe pass-rate 100% at acceptance; idempotent rebuild; no false-positive healthy reports; no silent runtime failures; ADR-0007 fallback is in-product but operator-visible per ADR-0037.
- **Maintainability**: W/H/A trifecta provides long-tail maintainer interface; augmented auditing-mcp is the safety-net.
- **Operability**: every MCP failure reaches a named operator surface with named server, failure layer, remediation pointer; runtime log redacts credentials per ADR-0039.

## Acceptance Criteria (AC) - EARS Format

The Blueprint inherits PRD AC-FR-* / AC-NFR-* clauses and refines them with per-layer AC-CC-* (Claude Code) and AC-CS-* (Codespaces) contributions. Two new ACs are added in this composition: **AC-X-1** addresses the secret-absent failure (resolves I-DR-CS-003); **AC-X-2** codifies the inventory disposition (resolves I-DR-001 / Q-CC-6).

### Functional ACs

#### FR-1 — Seven named MCP servers installed and registered (always-on) — Layer: claude-code + codespaces

- [ ] **AC-FR-1-a (PRD)**: When the Codespace finishes its build and lifecycle setup, the system shall have every one of the seven named MCP servers listed by `claude mcp list` as *connected*.
- [ ] **AC-FR-1-b (PRD)**: When the operator runs the agreed per-server probe, the system shall return a successful response from every one of the seven servers.
- [ ] **AC-FR-1-c (PRD)**: If any of the seven servers is missing, not registered, or not responding at probe time, then the system shall surface a clear failure in the probe tool's output naming the specific server and the layer of failure.
- [ ] **AC-CC-1 (CC-refined)**: When the operator runs `claude mcp list` after `postCreate` completes on a fresh build, the system shall list exactly the **seven named primary servers** (`serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`, `context7`, `exa`) **plus one documented fallback** (`codebase-memory-mcp` per ADR-0007 v2.2.0) — eight mcpServers entries total — all in `connected` status. (See **AC-X-2** for the inventory-count convention.)

#### FR-2 + FR-3 — Tool wiring + repo-readability — Layer: claude-code

- [ ] **AC-FR-2-a (PRD)**: When the operator inspects each affected `.claude/agents/*.md`, the system shall show the appropriate MCP tool entries present in the `tools:` allowlist.
- [ ] **AC-FR-2-b (PRD)**: When the operator runs a stage whose sub-agent was wired to a new MCP capability, the system shall make the corresponding tool callable from inside that sub-agent.
- [ ] **AC-CC-2 (CC-refined)**: When the operator inspects each of the 7 affected agent files, the system shall show the prescribed `mcp__<server>__<tool>` entries (per the consumer-mapping table in §Design / Claude Code / Project Filesystem Design) and no others.
- [ ] **AC-CC-3 (CC-invariant)**: When the operator inspects the 29 non-consumer agent files, the system shall show zero `mcp__` entries. (Preserves C-0445.)

#### FR-4 — Per-server probe verifiability at acceptance — Layer: claude-code + codespaces

- [ ] **AC-FR-4-a (PRD)**: Per-server probe returns success.
- [ ] **AC-FR-4-b (PRD)**: Probe failure surfaces server name, probe input, response/error.

#### FR-5 — Credentials via Codespaces secrets only — Layer: codespaces + claude-code

- [ ] **AC-FR-5-a (PRD)**: Credentials referenced by env-var name only; no committed secret values.
- [ ] **AC-FR-5-b (PRD)**: If a required credential's env var is unset at server start, the affected server's probe shall fail with a clearly named "missing credential" failure.
- [ ] **AC-X-1 (NEW; resolves I-DR-CS-003)**: If an env-var referenced by `.mcp.json` (`CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN`) is unset or empty at postStart probe time, then the system shall record the probe result as `result=fail` with `failure_layer=auth` and `message_redacted="missing env-var <NAME>"` in `mcp-events.jsonl` — distinguishable from transport/auth-with-key-rejected failures. The stderr banner shall additionally name the missing env-var.
- [ ] **AC-CC-4 (CC-invariant)**: When `git grep` is run over the repo, the system shall not surface any literal credential value matching credential-shape patterns in `.mcp.json`, `.claude/agents/*.md`, `.devcontainer/*`, or `.claude/runtime/mcp-events.jsonl`.
- [ ] **AC-CS-6 (CS-contributed)**: When `.mcp.json` references `${CONTEXT7_API_KEY}`, `${EXA_API_KEY}`, or `${TFE_TOKEN}`, the system shall resolve those env vars from Codespaces secrets via the `containerEnv` mapping.

#### FR-8 — Lifecycle health-check — Layer: codespaces + claude-code

- [ ] **AC-FR-8-a (PRD)**: postCreate completes; consolidated health-check output for all seven servers (refined: all eight `mcp.json` entries).
- [ ] **AC-FR-8-b (PRD)**: postStart re-runs the check.
- [ ] **AC-FR-8-c (PRD)**: postAttach surfaces the most recent result (or triggers a fresh check beyond a staleness threshold — deferred to plan-author as part of UI-10 refinement).
- [ ] **AC-FR-8-d (PRD)**: Failure at any boundary surfaces server name, failing layer, remediation hint into `KB-mcp-platform`.
- [ ] **AC-FR-8-e (PRD)**: Operator-invokable on demand.
- [ ] **AC-CS-4 (CS-contributed)**: When `postStartCommand` runs, the system shall append exactly one `readiness_probe` JSONL record per registered server to `.claude/runtime/mcp-events.jsonl` (eight records on a healthy run per AC-CC-1 + AC-X-2; I-DR-CS-004 resolved by inventory disposition).
- [ ] **AC-CS-5 (CS-contributed)**: If one or more probes returns `fail`, the system shall write the JSONL records, emit a stderr banner naming the degraded count, AND exit 0 (warn-and-continue).
- [ ] **AC-CC-6 (CC-refined)**: After a postStart cycle, `.claude/runtime/mcp-events.jsonl` contains eight `readiness_probe` records (one per registered server, including codebase-memory-mcp fallback) with `result: pass` or `result: fail` + `failure_layer`.

#### FR-9 — Runtime MCP failures surface — Layer: claude-code

- [ ] **AC-FR-9-a (PRD)**: Mid-run server failure surfaces structured failure record at the next operator-visible surface.
- [ ] **AC-FR-9-b (PRD)**: Tool-level error response includes server name, tool name, error response.
- [ ] **AC-FR-9-c (PRD)**: Healthy→unhealthy transition visible in runtime log surface with timestamp + triggering event.
- [ ] **AC-FR-9-d (PRD)**: No silent fallback. Includes the ADR-0007 GitNexus → codebase-memory-mcp fallback.
- [ ] **AC-CC-7 (CC-refined)**: When a primary→fallback transition occurs at runtime (GitNexus → codebase-memory-mcp), the system shall append a `primary_degraded` record to `.claude/runtime/mcp-events.jsonl` AND surface a stderr banner per ADR-0037; both shall be operator-readable.

#### FR-10 — Per-server runtime log/diagnostic — Layer: claude-code + codespaces

- [ ] **AC-FR-10-a (PRD)**: Per-server transport-level events captured at a documented log location.
- [ ] **AC-FR-10-b (PRD)**: Structured failure records reconstructable post-failure.
- [ ] **AC-FR-10-c (PRD)**: "Tail MCP logs" command makes per-server log content readable.
- [ ] **AC-FR-10-d (PRD)**: Credential values redacted (per ADR-0039).

#### FR-11 — W/H/A trifecta complete — Layer: claude-code

- [ ] **AC-FR-11-a (PRD)**: `KB-mcp-platform/SKILL.md` exists in trifecta shape.
- [ ] **AC-FR-11-b (PRD)**: `KB-mcp-design/SKILL.md` exists in trifecta shape.
- [ ] **AC-FR-11-c (PRD)**: `auditing-mcp` augmented; includes rules covering GitNexus; runnable end-to-end with no BLOCKER findings against the post-feature devcontainer.
- [ ] **AC-FR-11-d (PRD)**: KB-mcp-platform ↔ KB-mcp-design cross-reference explicit; both name GitNexus among the covered servers.
- [ ] **AC-CC-5 (CC-refined)**: When the augmented `auditing-mcp` skill (rule families OP-1 through OP-10) runs against the repo after Gate 6, the system shall report zero BLOCKER findings.
- [ ] **AC-CC-8 (CC-trifecta-structure)**: Both new skills conform to trifecta structural conventions: `name:` lowercase-hyphenated; `description` ends with sister-cross-reference; design half has exactly two reference files (`patterns-and-anti-patterns.md` + `principles.md`) and no `assets/`.
- [ ] **AC-CC-9 (CC-cross-reference)**: `KB-mcp-platform/references/gitnexus-and-fallback.md` names both GitNexus + codebase-memory-mcp, cites ADR-0007 v2.2.0, and links to the `mcp-events.jsonl` `primary_degraded` schema in `KB-mcp-design/references/principles.md`.

### Cross-Layer / Operational ACs

- [ ] **AC-NFR-1-a (PRD)**: Cold-cache build + lifecycle setup completes within ~10 min on 4 vCPU / 8 GB host.
- [ ] **AC-NFR-1-b (PRD)**: Warm-cache rebuild reuses cached layers; no re-download / re-compile of MCP server binaries.
- [ ] **AC-CS-1 (CS-features)**: After Feature install, Node 20 and Go are on PATH; `node --version` returns `v20.*` and `go version` returns non-error.
- [ ] **AC-CS-2 (CS-idempotence)**: Re-invoking `postCreate.sh` without intervening sentinel deletion shall observe each per-server install as already-satisfied (sentinel-present AND binary-present); the run completes in well under cold-cache time. (Per ADR-0041 sentinel naming = `<server>@<version>.installed` + binary-presence check.)
- [ ] **AC-CS-3 (CS-fail-fast)**: If any per-server install step fails inside `postCreate.sh`, the system shall surface the failing server name on the operator's terminal and shall exit non-zero, halting the lifecycle.
- [ ] **AC-CS-7 (CS-ports)**: `forwardPorts: []`; no port forwarded by default.
- [ ] **AC-CS-8 (CS-time)**: Cold-cache build within ~10 min; warm-cache within ~2 min (NFR-1).
- [ ] **AC-CS-9 (CS-GitNexus)**: `postCreate.sh` invokes GitNexus with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` and fails postCreate if the smoke-test (`--help`) fails (C-0388/C-0411).
- [ ] **AC-X-2 (NEW; resolves I-DR-001 / Q-CC-6)**: The system shall treat the closed list of seven PRD-named servers (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, GitNexus, Context7, Exa) as the **PRD-bound inventory** and shall treat codebase-memory-mcp as a **documented ADR-0007 fallback that is also registered in `.mcp.json` and probed**. The reconciliation: the PRD count of "seven named servers" refers to PRIMARY surface; `.mcp.json` carries eight `mcpServers` entries; the augmented `auditing-mcp` (rules OP-2 / OP-3 / OP-8) special-cases `codebase-memory-mcp` by name as the documented fallback. This convention is recorded in `KB-mcp-platform/references/gitnexus-and-fallback.md` per AC-CC-9.

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | New | `.mcp.json` (repo root) | Project-scoped MCP registration; 8 mcpServers entries |
| Claude Code | Existing/modified | `.claude/agents/*.md` (7 files) | Add `mcp__<server>__<tool>` to `tools:` arrays |
| Claude Code | New | `.claude/skills/KB-mcp-platform/` | Trifecta What-half |
| Claude Code | New | `.claude/skills/KB-mcp-design/` | Trifecta How-half |
| Claude Code | Existing/augmented | `.claude/skills/auditing-mcp/` | 10 new rule families OP-1..OP-10 + scripts |
| Claude Code | New | `.claude/runtime/mcp-events.jsonl` | Cross-server event surface; gitignored; bootstrapped by postCreate |
| Claude Code | New | `.gitignore` (modified) | Adds `.claude/runtime/mcp-events.jsonl` |
| Codespaces | Existing/modified | `.devcontainer/devcontainer.json` | Features additions (Node 20 LTS; Go); containerEnv updates |
| Codespaces | New | `.devcontainer/postCreate.sh` | Idempotent install with version-pinned sentinels |
| Codespaces | New | `.devcontainer/postStart.sh` | Readiness probe writer |
| Codespaces | New | `.devcontainer/install/terraform-mcp.sh` | wget + SHA256 + GPG verify |
| Codespaces | New | `.devcontainer/lib/mcp-ping.sh` | Probe helper |
| Codespaces | New | `.devcontainer/lib/mcp-auth-probe.sh` | Auth-probe helper for Context7/Exa |
| Codespaces | New | `.devcontainer/versions.env` | Per-server pin table |

### Integration Points

- **Integration Target:** Claude Code session consumes `.mcp.json`; sub-agents consume `tools:` allowlists; operators read `.claude/runtime/mcp-events.jsonl` via documented tail command; augmented `auditing-mcp` validates static config + runtime events.
- **Invocation Method:** lifecycle-driven (postCreate / postStart); operator-on-demand (audit script + tail command); session-startup (Claude Code reads `.mcp.json` on session creation).

### Code Inspection Evidence

| File/Function | Relevance |
|---------------|-----------|
| `.devcontainer/devcontainer.json` | Existing Features block; this feature adds 2 entries, modifies 1 pin, preserves 3 |
| `.devcontainer/Dockerfile` | Existing baseline; **NOT modified** per ADR-0041 (E-0081 historical fragility) |
| `.claude/skills/KB-cc-platform/`, `KB-cc-design/`, `auditing-cc-configs/` | Trifecta exemplar 1; new skills mirror verbatim per D-0010 |
| `.claude/skills/KB-codespaces-platform/`, `KB-codespaces-design/`, `auditing-codespaces/` | Trifecta exemplar 2 (auditing-codespaces is STUB per ADR-0033) |
| `.claude/skills/KB-github-actions-platform/`, `KB-github-actions-design/`, `auditing-github-actions/` | Trifecta exemplar 3 |
| `.claude/skills/auditing-mcp/SKILL.md` (line 30) | Current family-declaration: `auditing-cc-configs` family. Path B (Open Items resolution OI-2) preserves this. |
| `.claude/skills/KB-codebase-research/SKILL.md` | Names GitNexus primary / codebase-memory-mcp fallback per ADR-0007 v2.2.0 |
| `.claude/agents/discovery-codebase-researcher.md` (lines 3, 20, 29, 156) | Four prose references to primary/fallback — preserved verbatim; OP-4 audit rule (ADR-0037) makes this machine-checkable |
| `adrs/ADR-0007-code-graph-mcp-selection.md` vs `adrs-migrated/...` | Currently lives in `adrs-migrated/`; ADR-0038 relocates per ADR-0036 |
| `.claude/agents/*.md` (36 files) | C-0445 grep-verified zero `mcp__` entries; this feature adds entries to 7, preserves 29 |

### Fact Disposition Table

One row per codebase-analysis focusArea. The Disposition column states this Blueprint's commitment relative to existing behavior.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---------|------------|-------------|-----------|----------|
| C-0445 | Zero `mcp__` usage across all 36 sub-agents | preserve (for 29 of 36) | Least-privilege per cc-design Principle 5; 7 agents gain entries per consumer-mapping (ADR-0040 narrows Serena). | grep-verified, codebase-analysis Batch 5 |
| C-0462 | `.mcp.json` absent at repo root | transform | Feature creates the file per ADR-0037 / ADR-0039 schema (env-block SSOT). | grep-verified |
| C-0455 / C-0456 / C-0457 | Three W/H/A trifectas exist (CC, Codespaces, GHA) | preserve (as exemplars) | KB-mcp-platform + KB-mcp-design mirror the convention verbatim per D-0010 / cc-design §Skill patterns. | direct inspection |
| C-0458 | MCP trifecta currently audit-only (auditing-mcp exists; KB-mcp-* absent) | transform | FR-11 completes the trifecta. | grep-verified |
| C-0441 / C-0495 | ADR-0018 v1.0.0 vs KB v1.1.0 drift | transform | ADR-0038 bumps ADR-0018 to v1.1.0 (this Blueprint authors). | direct inspection |
| C-0442 / C-0497 / C-0498 | ADR-0007 in `adrs-migrated/` not `adrs/` | transform | ADR-0038 relocates per ADR-0036. | direct inspection |
| C-0447 / C-0448 | GitNexus primary / codebase-memory-mcp fallback policy per ADR-0007 v2.2.0 | preserve | Feature provisions both; does NOT re-decide. | ADR-0007 v2.2.0 |
| C-0449 | UI-8 contingency hedge (Serena fit on markdown-heavy repo) | transform | ADR-0040 narrows to Python-audit-surface allowlist (5 agents). | codebase-analysis |
| C-0484 / C-0485 | 73.8% markdown corpus | preserve (as constraint) | Constraint #8; drives ADR-0040 narrowing decision. | single-sourced-medium |
| C-0490 | Symbol density in 52 Python audit scripts | preserve (as constraint) | Constraint #8 corroborator; informs ADR-0040 5-agent list. | verified |
| C-0388 / C-0411 | GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` requirement | transform | postCreate.sh `install_gitnexus` smoke-tests this flag; AC-CS-9 codifies. | partially_verified-medium |
| C-0301 | Stdio servers not auto-reconnected | preserve (as constraint) | Drives FR-9 contract being load-bearing; ADR-0037 codifies the event surface. | verbatim Anthropic |
| C-0300 / C-0302 | HTTP/SSE retry behavior (5 attempts + 3 initial) | preserve | Context7/Exa inherit; no design action beyond awareness. | verified |
| C-0290 / C-0291 | JSON-RPC ping is canonical health primitive | preserve | ADR-0041 implementation uses ping per D-0008. | verbatim spec |
| C-0333 / C-0335 | OWASP MCP01 Token Mismanagement (top-ranked MCP risk) | transform | ADR-0039 codifies redact-at-source posture. | verified |
| C-0094 / E-0094 | argv-leakage anti-pattern | transform | ADR-0039 rule OP-10 rejects at .mcp.json validation. | verified |
| E-0095 / C-0259 / C-0260 / C-0280 | URL-embedded credential anti-pattern (Exa `exaApiKey`) | transform | ADR-0039 rule OP-9 rejects at .mcp.json validation. | verified |
| C-0349 | F5.4 NO CONSENSUS for primary→fallback transition surfacing | transform | ADR-0037 establishes the project's novel convention. | verbatim |
| E-0081 | Dockerfile-Yarn-key historical fragility | preserve (as constraint) | ADR-0041 honors "no new Dockerfile work." | codebase-analysis |
| C-0463 | Existing Yarn-list workaround in Dockerfile | preserve | Not touched. | direct inspection |
| C-0040 / C-0042 / E-0098 | Serena v1.3.0 base_modes→added_modes breaking change | transform | ADR-0040 pins pre-v1.3.0. | research note T-001 |
| C-0073 | mcp-openapi-schema 0.0.1 14-month static | preserve (with verify-at-execution) | Plan-author confirms at install time; pin form is exact-tag. | research note T-002 |
| C-0133 / C-0153 | actionlint-mcp no tagged releases | preserve (with verify-at-execution) | Plan-author selects commit SHA at install time. | research note T-003 |
| C-0157 / C-0190 / C-0193 | Terraform MCP releases.hashicorp.com with SHA256 + GPG | transform | ADR-0041 codifies binary-fetch + verify path. | research note T-004 |
| C-0037 | Context7 v1.2.0 ReplaceContentTool replaces ReplaceRegexTool | preserve (with verify-at-execution) | Allowlist entries are version-coupled; plan-author re-validates. | research note T-005 |
| C-0205 | Context7 `--api-key` CLI flag form | transform | Rejected by ADR-0039 / rule OP-10. | research note T-005 |
| C-0444 | Universal-frontmatter calibration (medium-confidence) | preserve (as constraint) | Constraint #14; plan-author validates per-agent before editing. | codebase-analysis |
| C-0460 | `auditing-mcp` family-declaration at line 30 (`auditing-cc-configs`) | preserve (Path B per OI-2) | Composer resolution: keep current family membership; the new KB-mcp-* are sibling knowledge skills with explicit cross-refs. | direct inspection |
| C-0471 / C-0535 | ADR-0020 skill naming with lone `auditing-cc-configs` deviation | preserve | Both new skills follow standard naming; auditing-mcp's bare-topic name is correct. | direct inspection |
| C-0478 / C-0479 / C-0480 / C-0481 | Trifecta structural skeleton (design half = 2 refs, no assets; platform half = many refs + assets/templates/) | preserve | KB-mcp-design conforms (2 refs, no assets); KB-mcp-platform conforms (7 refs + assets/templates/). | codebase-analysis |
| C-0482 / C-0483 / C-0528 / C-0537 | Sister-cross-reference convention; body-prose family membership; ADR-0030 pedagogical_sections | preserve | Both new skills declare per the conventions. | codebase-analysis |
| C-0484 (file-counts) | 634 total / 468 markdown | preserve | Drives ADR-0040 narrowing. | single-sourced-medium |
| C-0499 | auditing-codespaces STUB per ADR-0033 | preserve | Augmented auditing-mcp owns lifecycle audit (OP-5) until stub is filled. | direct inspection |
| OI-CS-1..5 | Verify-at-execution items | out-of-scope (deferred to plan-author) | These are not design questions; they are operational items the plan-author resolves at task time. | codespaces-design |

## Design

### Change Impact Map

```yaml
Change Target: "Devcontainer MCP server provisioning surface (2 layers)"
Direct Impact:
  frontend:    [N/A — out of scope]
  backend:     [N/A — out of scope]
  api:         [N/A — out of scope]
  query:       [N/A — out of scope]
  database:    [N/A — out of scope]
  cicd:        [N/A — out of scope]
  iac:         [N/A — out of scope]
  claude_code:
    - ".mcp.json (NEW)"
    - ".claude/agents/design-api.md, design-cicd.md, design-iac.md, discovery-external-researcher.md, discovery-codebase-researcher.md, review-architecture-auditor.md, design-cc.md, design-codespaces.md (mcp__ tools allowlist + Serena narrowing)"
    - ".claude/skills/KB-mcp-platform/ (NEW)"
    - ".claude/skills/KB-mcp-design/ (NEW)"
    - ".claude/skills/auditing-mcp/ (10 augmentation rules; 6 new scripts; 2 extended)"
    - ".claude/runtime/mcp-events.jsonl (NEW; gitignored)"
    - ".gitignore (modified)"
  codespaces:
    - ".devcontainer/devcontainer.json (Features additions + containerEnv updates)"
    - ".devcontainer/postCreate.sh (NEW)"
    - ".devcontainer/postStart.sh (NEW)"
    - ".devcontainer/install/terraform-mcp.sh (NEW)"
    - ".devcontainer/lib/mcp-ping.sh (NEW)"
    - ".devcontainer/lib/mcp-auth-probe.sh (NEW)"
    - ".devcontainer/versions.env (NEW)"
Indirect Impact:
  - "Five new ADRs ship: ADR-0037..ADR-0041 (this Blueprint authors). ADR-0007 relocates from adrs-migrated/ to adrs/ per ADR-0036."
  - "ADR-0018 v1.0.0 superseded by ADR-0038 v1.1.0 (append-only per ADR-0005). Two downstream KB/agent consumers update to v1.1.0."
  - "All 36 sub-agents see new .mcp.json on session start; tool schemas deferred until invoked (cc-design Principle 1)."
  - "Cold-cache build time grows from current baseline by ~2–4 min (postCreate per-server installs)."
No Ripple Effect:
  - "The 29 non-consumer agents' tools: arrays are NOT modified (C-0445 invariant preserved)."
  - "No model:/effort:/skills: changes on any agent (cc-design Principle 9 honored)."
  - "Pipeline stages, gates, orchestrator topology unchanged."
  - "No Dockerfile changes (ADR-0041 codifies)."
  - "No port forwarding (codespaces-design Q-CS / AC-CS-7)."
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|----------|-----|--------------------|--------------------|
| ADR-0018 v1.0.0 schema | ADR-0038 v1.1.0 schema (additive `blast_radius` field) | No (additive; v1.0.0 outputs remain valid) | Forward-compatible — readers tolerant of missing `blast_radius` per "additive schema evolution" |
| ADR-0007 at `adrs-migrated/` | ADR-0007 at `adrs/` (canonical) | No (file move, content preserved) | Relocate per ADR-0036; optional redirect stub at `adrs-migrated/` |
| `.claude/agents/*.md` with zero `mcp__` entries (36 of 36) | 7 of 36 agents gain `mcp__<server>__<tool>` entries; 29 preserved | Yes (additive `tools:` array edits) | OP-2 / OP-3 audit rules validate the consumer-mapping ↔ live-state alignment |
| `auditing-mcp` description naming sister halves that didn't exist | `auditing-mcp` description names KB-mcp-platform + KB-mcp-design | No (description update) | Skill description update per the canonical sister-cross-reference convention (C-0482) |
| `.claude/agents/discovery-codebase-researcher.md` (prose-only primary/fallback at lines 3/20/29/156) | Same prose preserved; backed by OP-4 audit rule per ADR-0037 | No | OP-4 audit rule (`/primary.*fallback/` grep on agent body) makes the prose machine-checkable |
| Sentinel naming (codespaces-design draft used unversioned) | Sentinel naming = `<server>@<version>.installed` per ADR-0041 | Yes (postCreate.sh outline reconciled) | Single canonical form across Persistence Boundaries and postCreate.sh body |
| `.mcp.json` "7 servers" (PRD count) | `.mcp.json` 8 entries (7 PRD-named primaries + codebase-memory-mcp fallback) | Yes (count convention) | AC-X-2 codifies; auditing-mcp rules special-case codebase-memory-mcp by name |

### Architecture Overview

```
                                Codespace devcontainer
                 ┌──────────────────────────────────────────────────┐
                 │                                                  │
                 │   ┌──────────────────────────────────────────┐   │
                 │   │  Codespaces Layer                        │   │
                 │   │  - devcontainer.json (Features: Node 20, │   │
                 │   │    Go, common-utils, github-cli,         │   │
                 │   │    claude-code; containerEnv: 3 secrets) │   │
                 │   │  - postCreate.sh  (install + sentinels)  │   │
                 │   │  - postStart.sh   (readiness probe)      │   │
                 │   │  - install/terraform-mcp.sh (GPG verify) │   │
                 │   │  - lib/mcp-ping.sh, mcp-auth-probe.sh    │   │
                 │   │  - versions.env (per-server pins)        │   │
                 │   └────────────┬─────────────────────────────┘   │
                 │                │ writes readiness_probe          │
                 │                ▼ records                         │
                 │   ┌──────────────────────────────────────────┐   │
                 │   │  .claude/runtime/mcp-events.jsonl        │   │
                 │   │  (JSONL; 3 event types; gitignored)      │   │
                 │   │  Per ADR-0037 + ADR-0039                 │   │
                 │   └────────────▲─────────────────────────────┘   │
                 │                │ reads / appends                 │
                 │   ┌────────────┴─────────────────────────────┐   │
                 │   │  Claude Code Layer                       │   │
                 │   │  - .mcp.json (8 mcpServers entries;      │   │
                 │   │    env: block = redaction SSOT)          │   │
                 │   │  - 7 agents w/ mcp__<svr>__<tool> tools  │   │
                 │   │    (29 agents preserved zero-mcp__)      │   │
                 │   │  - KB-mcp-platform/ (NEW; "What" half)   │   │
                 │   │  - KB-mcp-design/  (NEW; "How"  half)    │   │
                 │   │  - auditing-mcp/ (augmented; OP-1..10)   │   │
                 │   └──────────────────────────────────────────┘   │
                 │                │                                 │
                 │                ▼ MCP protocol (stdio / HTTP)    │
                 │   ┌──────────────────────────────────────────┐   │
                 │   │  MCP servers (8):                        │   │
                 │   │  - serena (stdio, narrowed per ADR-0040) │   │
                 │   │  - mcp-openapi-schema (stdio)            │   │
                 │   │  - actionlint-mcp (stdio)                │   │
                 │   │  - terraform-mcp (stdio)                 │   │
                 │   │  - gitnexus (stdio; ADR-0007 primary)    │   │
                 │   │  - codebase-memory-mcp (stdio; ADR-0007  │   │
                 │   │    fallback)                             │   │
                 │   │  - context7 (HTTP; CONTEXT7_API_KEY)     │   │
                 │   │  - exa     (HTTP; x-api-key header)      │   │
                 │   └──────────────────────────────────────────┘   │
                 │                                                  │
                 └──────────────────────────────────────────────────┘
                                  ▲
                                  │ Codespaces secrets → containerEnv
                                  │ → ${VAR} substitution in .mcp.json
                                  │
                          Operator / GitHub Codespaces UI
                                  (sets EXA_API_KEY,
                                   CONTEXT7_API_KEY, TFE_TOKEN)
```

### Data Flow

End-to-end lifecycle of the MCP surface for the primary "fresh-build" scenario:

```
1. Operator opens repo in Codespace.
2. GitHub builds base image (mcr.microsoft.com/devcontainers/python:1-3.11-bookworm).
3. Devcontainer Features run:
     common-utils:2, github-cli:1, node:1@20, go:1, claude-code:1
   Result: Node 20 + Go on PATH; Codespaces secrets exported via containerEnv.
4. onCreateCommand: `claude --version && python3 --version && node --version && gh --version`
   (existing; unchanged)
5. postCreateCommand: `.devcontainer/postCreate.sh`
     - mkdir -p .claude/runtime/install-sentinels
     - touch .claude/runtime/mcp-events.jsonl   # bootstrap per ADR-0037
     - For each server (serena, mcp-openapi-schema, actionlint-mcp,
       terraform-mcp, gitnexus, codebase-memory-mcp):
         - Read pin from versions.env
         - check_installed(): sentinel-present AND binary-present? → skip
         - install_<server>(): perform install; GPG-verify for terraform-mcp
         - touch sentinel: <server>@<version>.installed
     - First-run verify: .devcontainer/postStart.sh --first-run (non-fatal)
6. postStartCommand: `.devcontainer/postStart.sh`
     - For each registered server (8 entries from .mcp.json):
         - lib/mcp-ping.sh <server> <transport>
         - Append readiness_probe record to mcp-events.jsonl
     - If MCP_AUTH_PROBE=1: supplementary auth probes for Context7, Exa
     - Emit stderr banner: "[postStart] MCP readiness: N/8 healthy"
     - exit 0 (warn-and-continue per Q-CS-3 / AC-CS-5)
7. Operator runs Claude Code session:
     - .mcp.json loaded; 8 servers registered
     - Sub-agent dispatched; if agent's tools: contains mcp__<svr>__<tool>,
       the tool is callable; otherwise permission-denied by allowlist.
8. Runtime failure (e.g., GitNexus stdio process exits):
     - In-product fallback-detection code-site (per ADR-0037 Implementation
       Guidance — plan-author places) appends:
         a) primary_degraded record (gitnexus → codebase-memory-mcp)
         b) structured_failure record (failure_class=transport)
     - Stderr banner: "[mcp:gitnexus] primary degraded → falling back to
       codebase-memory-mcp; see .claude/runtime/mcp-events.jsonl"
     - Pipeline continues on the fallback per ADR-0007 v2.2.0 policy
9. Operator inspects mcp-events.jsonl via documented tail command:
     - Reads structured records; all credentials redacted per ADR-0039
     - Remediation pointer in structured_failure record → KB-mcp-platform
       troubleshooting section
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|-------------------|----------|-------------------|-------------------|------------------|-------------------|
| Claude Code session MCP host | session startup | (no MCP servers) | reads `.mcp.json`; loads 8 servers | natural via Claude Code's `.mcp.json` discovery | `claude mcp list` shows 8 connected |
| Sub-agent tool dispatch | per-agent `tools:` allowlist | zero `mcp__` entries | 7 agents gain entries per consumer-mapping | direct file edit | OP-2 audit + per-agent runtime invocation |
| Codespaces secrets → MCP | `.devcontainer/devcontainer.json` containerEnv | (no MCP secrets wired) | `containerEnv` exports 3 vars via `${localEnv:NAME}`; `.mcp.json` reads `${VAR}` | natural via env-var substitution | AC-CS-6 + AC-FR-5-a |
| Lifecycle health-check | postStartCommand | (no health-check) | runs `postStart.sh` ping for 8 servers | devcontainer lifecycle | AC-CS-4 + AC-CC-6 |
| Mid-run failure surfacing | in-product fallback-detection code-site | (no surface; silent) | appends to `mcp-events.jsonl` + stderr banner | per ADR-0037 | AC-CC-7 + OP-6 audit |
| `.mcp.json` ↔ agent allowlist consistency | augmented `auditing-mcp` | (no audit) | OP-2 / OP-3 rules | script-invokable | `auditing-mcp` zero-BLOCKER (AC-CC-5) |
| ADR-0018 schema consumers | `KB-codebase-research/SKILL.md` + `discovery-codebase-researcher.md` | refer to v1.1.0 by phrase | refer to v1.1.0 per ADR-0038 | direct file edit | grep for `schema_version: 1.1.0` |

### Main Components

#### Component 1: `.mcp.json` (NEW)

- **Responsibility**: Project-scoped MCP server registry. Single source of truth for (a) which servers are registered, (b) their transport + command, (c) the redaction allowlist (env-block + HTTP headers per ADR-0039).
- **Interface**: Claude Code reads at session start; augmented `auditing-mcp` reads as static config.
- **Dependencies**: Codespaces' `containerEnv` populates the env vars `${VAR}` substitutions resolve against; `postCreate.sh` installs the binaries the `command`/`args` fields reference.

#### Component 2: Per-agent `tools:` allowlist edits (7 agents)

- **Responsibility**: Wire MCP tool callability per agent per consumer-mapping. Preserve zero-`mcp__` for 29 non-consumers.
- **Interface**: Each agent's `tools:` array; OP-2 / OP-3 audit rules validate.
- **Dependencies**: `.mcp.json` (server names must match); ADR-0040 (Serena 5-agent list).

#### Component 3: `KB-mcp-platform/` (NEW skill)

- **Responsibility**: "What" half of W/H/A trifecta. MCP platform facts: transports, install paths, credential surfaces, lifecycle integration, `mcp-events.jsonl` schema usage, GitNexus + fallback.
- **Interface**: model-invocable per description match; `allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch`.
- **Dependencies**: ADR-0007 (GitNexus/codebase-memory-mcp), ADR-0037 (event schema), ADR-0039 (redaction), ADR-0041 (install paths).

#### Component 4: `KB-mcp-design/` (NEW skill)

- **Responsibility**: "How" half of W/H/A trifecta. MCP design discipline: principles (incl. `mcp-events.jsonl` schema canonical home) + patterns and anti-patterns.
- **Interface**: model-invocable; `allowed-tools: Read, Grep, Glob` (design-half-slim).
- **Dependencies**: synthesis §5 (operational discipline), ADR-0037, ADR-0039, ADR-0040, ADR-0041.

#### Component 5: `auditing-mcp/` (augmented in place)

- **Responsibility**: 10 rule families: OP-1 env-block coverage; OP-2 consumer-mapping; OP-3 zero-`mcp__` preservation; OP-4 primary/fallback prose; OP-5 lifecycle completeness; OP-6 runtime log redaction; OP-7 trifecta consistency; OP-8 GitNexus-specific; OP-9 URL-credential rejection; OP-10 argv-leakage absence.
- **Interface**: `scripts/audit_mcp.py [--with-runtime]` entry point; severity BLOCKER/MAJOR/MINOR/NIT.
- **Dependencies**: `.mcp.json` (static-config audit), `.claude/runtime/mcp-events.jsonl` (runtime audit when `--with-runtime`), the seven Trifecta exemplar skills, ADR-0007 (for OP-8), ADR-0033 (auditing-codespaces STUB context).

#### Component 6: `.claude/runtime/mcp-events.jsonl` (NEW; gitignored)

- **Responsibility**: Durable cross-server event surface. Three event types: `primary_degraded`, `readiness_probe`, `structured_failure`. Per ADR-0037.
- **Interface**: append-only JSONL; writers = postStart.sh + in-product fallback-detection code-site; readers = operator (tail), augmented `auditing-mcp --with-runtime`.
- **Dependencies**: ADR-0037 (schema canonical), ADR-0039 (redaction integrity); schema home in `KB-mcp-design/references/principles.md`.

#### Component 7: `.devcontainer/postCreate.sh` (NEW)

- **Responsibility**: Idempotent install for 6 OSS-local servers (Context7/Exa are remote HTTP — no install). Sentinel-guarded + binary-presence-checked re-run. Fail-fast on per-server failure.
- **Interface**: invoked by devcontainer `postCreateCommand`; exit codes propagate.
- **Dependencies**: `versions.env` (per-server pins), `install/terraform-mcp.sh`, Go Feature (for `go install`), Node 20 Feature (for `npx`/`uvx`).

#### Component 8: `.devcontainer/postStart.sh` (NEW)

- **Responsibility**: Fast readiness probe (JSON-RPC ping) for all 8 registered servers. Writes `readiness_probe` JSONL records. Warn-and-continue on probe failure.
- **Interface**: invoked by devcontainer `postStartCommand`; exit 0 always except infrastructure failure (per ADR-0041 Implementation Guidance on I-DR-CS-008).
- **Dependencies**: `lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`, ADR-0037 event schema, ADR-0039 redaction allowlist.

### Contract Definitions

The canonical schema for `.claude/runtime/mcp-events.jsonl` lives in `KB-mcp-design/references/principles.md` per ADR-0037. The full table (common fields + event-specific fields per event type) is reproduced verbatim from cc-design §`mcp-events.jsonl` schema and refined below to address I-DR-004 (bootstrap semantics).

**Bootstrap semantics (resolves I-DR-004):** On postCreate, the file is `touch`-ed if absent (zero records present). On postStart, exactly N `readiness_probe` records are appended where N = the number of registered servers in `.mcp.json` (currently 8 per AC-X-2). An absent file or zero records after postStart is an OP-5 BLOCKER.

### Data Contract — `mcp-events.jsonl` event records

```yaml
Input (writer perspective):
  Type: "JSON object on a single line; UTF-8; no embedded newlines"
  Preconditions: "common fields {ts, event, server} present; redaction filter applied to any reason / message_redacted field"
  Validation: "auditing-mcp rule OP-6 grep against credential shapes and against the env-block-keyed allowlist"

Output (reader perspective):
  Type: "JSONL stream; tail-friendly"
  Guarantees: "Append-only; records never rewritten; each line independently parseable"
  On Error: "Malformed line is a BLOCKER for OP-6; readers should tolerate one bad line and report position"

Invariants:
  - "No credential value in any record (ADR-0039)"
  - "`extraction_method` enum: transport_error | tool_error_response | manual_operator_invocation"
  - "Three event types only: primary_degraded | readiness_probe | structured_failure"
```

### Field Propagation Map

| Field | Boundary | Status | Detail |
|-------|----------|--------|--------|
| `CONTEXT7_API_KEY` | Codespaces secret → containerEnv → `.mcp.json ${VAR}` → Context7 HTTP header | preserved (value) | Never written to git, never logged; redaction allowlist covers per ADR-0039 |
| `EXA_API_KEY` | Codespaces secret → containerEnv → `.mcp.json ${VAR}` → Exa `x-api-key` header | preserved (value) | Same; URL-query form rejected per OP-9 |
| `TFE_TOKEN` | Codespaces secret → containerEnv → `.mcp.json ${VAR}` → Terraform MCP env | preserved (value); optional | Local-only Terraform MCP works unauthenticated |
| `extraction_method` | codebase-analysis.json (ADR-0018/0038 schema) → `mcp-events.jsonl` (ADR-0037 schema) | term-shared, separate contracts | Same field name for terminological consistency; two different files with two different schemas |
| `blast_radius` | NEW field in codebase-analysis schema v1.1.0 | added | ADR-0038 defines |

### State Transitions and Invariants

```yaml
State Definition:
  - Initial State: "Fresh Codespace; no install sentinels; no mcp-events.jsonl; no binaries"
  - Possible States: |
      - fresh (post-base-image, pre-Features)
      - features_ready (Features installed; Node, Go on PATH)
      - postCreate_in_progress (server installs running)
      - postCreate_complete (sentinels present; binaries reachable)
      - postStart_complete (readiness records in mcp-events.jsonl)
      - session_ready (Claude Code session live; .mcp.json loaded; 8 servers connected)
      - mcp_failure (one or more servers degraded; primary_degraded + structured_failure records in mcp-events.jsonl)
      - mcp_recovered (fallback in effect or primary restored)

State Transitions:
  fresh → features_ready (Features run)
  features_ready → postCreate_in_progress → postCreate_complete (postCreate.sh runs; fail-fast if any server fails)
  postCreate_complete → postStart_complete (postStart.sh runs; warn-and-continue on probe fail)
  postStart_complete → session_ready (Claude Code session starts)
  session_ready → mcp_failure (server exits or returns error)
  mcp_failure → mcp_recovered (operator fixes; or fallback exercised per ADR-0007)
  mcp_recovered → session_ready (no separate state; mcp-events.jsonl retains the history)

System Invariants:
  - "No credential value in any committed file or any line of mcp-events.jsonl (ADR-0039 + AC-NFR-2-a + AC-CC-4)"
  - "29 of 36 agents always have zero mcp__ entries (C-0445)"
  - "Every primary→fallback transition is operator-visible in mcp-events.jsonl + stderr (ADR-0037)"
  - "Every registered server in .mcp.json has a corresponding postStart probe (OP-5)"
  - "Every env-var reference in .mcp.json appears in an env: block or documented HTTP header allowlist (OP-1)"
```

---

### Claude Code / Project Filesystem Design

This subsection integrates the cc-design.md per-layer subsection by reference; the full content lives in `working/feature/devcontainer-mcp-provisioning-r1/cc-design.md`. Key reconciliations made in this Blueprint:

- **Q-CC-1 (family-coordinator)**: **Path B** — `auditing-mcp` remains in the `auditing-cc-configs` family (current line-30 declaration preserved). `KB-mcp-platform` and `KB-mcp-design` are sibling knowledge skills cross-referenced from `auditing-mcp` but not sister halves in the family sense. Rationale: minimum convention change; the three existing trifectas show inconsistent treatment, and Path B requires no body-prose change to `auditing-mcp/SKILL.md` line 30.
- **Q-CC-2 (.claude/runtime/ git-status)**: Option (a) per ADR-0037 — `.claude/runtime/` directory is committed via `.gitkeep`; `.claude/runtime/mcp-events.jsonl` is gitignored.
- **Q-CC-3 (Serena agent list)**: Resolved by ADR-0040 — 5 named agents (review-architecture-auditor, design-cc, design-cicd, design-codespaces, discovery-codebase-researcher).
- **Q-CC-4 (auditing-mcp dimension organization)**: Option (a) — expand existing dimensions. One source of truth; one audit skill; the new rules (OP-1..OP-10) extend the existing rubric.
- **Q-CC-5 (primary/fallback expression)**: prose-only with OP-4 audit rule per ADR-0037. No new structured frontmatter field.
- **Q-CC-6 (codebase-memory-mcp inventory status)**: Option (a) per AC-X-2 — the PRD's "seven named servers" refers to PRIMARY surface; `.mcp.json` carries 8 entries; auditing-mcp special-cases codebase-memory-mcp.
- **Q-CC-7 (plugin packaging future)**: deferred to follow-up feature (not authored here).
- **Q-CC-8 (ADR-authorship list)**: Resolved — ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041 all authored.
- **Q-CC-9 (auditing-mcp Gate 6 status)**: Open — see Open Items / OI-3. Default disposition: hard gate (AC-CC-5 codifies zero BLOCKER findings; whether failure halts the pipeline is a user policy decision).

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.mcp.json` (NEW) | MCP server registry | new |
| `.claude/agents/*.md` (7 files) | Sub-agent tool allowlists | modified (tools: arrays only) |
| `.claude/skills/KB-mcp-platform/` | Trifecta What half | new |
| `.claude/skills/KB-mcp-design/` | Trifecta How half | new |
| `.claude/skills/auditing-mcp/` | Trifecta Audit half | modified (augmentation; sister-cross-reference update; 10 rule families) |
| `.claude/runtime/mcp-events.jsonl` | Cross-server event surface | new; gitignored |
| `.gitignore` | Add `.claude/runtime/mcp-events.jsonl` | modified |

#### CLAUDE.md Updates

| File | Change | Rationale |
|---|---|---|
| (none) | (no CLAUDE.md introduced; no existing CLAUDE.md modified) | cc-design Principle 5: knowledge lives in model-invocable skills; CLAUDE.md would cost every session whether MCP work is in flight or not. |

#### Slash Commands

| Command Path | Trigger | Purpose | Notes |
|---|---|---|---|
| (none) | — | — | No commands; cc-design Principle 8 (skills replaced commands). |

#### Hooks

| Hook Event | Script | Behavior | Failure Mode |
|---|---|---|---|
| (none) | — | — | cc-design Principle 3: hooks are deterministic guarantees; MCP work is lifecycle/instructional, not gating. |

#### Skills

| Skill | Location | When Triggered | What It Provides |
|---|---|---|---|
| `kb-mcp-platform` | `.claude/skills/KB-mcp-platform/SKILL.md` | model-invocable on MCP-related descriptions | Transports, install paths, credential surfaces, lifecycle integration, mcp-events.jsonl schema usage, GitNexus + fallback |
| `kb-mcp-design` | `.claude/skills/KB-mcp-design/SKILL.md` | model-invocable on MCP-design questions | Principles (incl. event schema canonical home); patterns + anti-patterns |
| `auditing-mcp` (augmented) | `.claude/skills/auditing-mcp/SKILL.md` | model-invocable + script-invokable | 10 rule families: OP-1..OP-10 |

#### Sub-Agents

This feature does NOT create new sub-agents. It modifies 7 of 36 existing agents' `tools:` allowlists only. Per ADR-0040, the 5 Serena consumers are:

| Sub-Agent | New `mcp__` entries | Source |
|---|---|---|
| `design-api` | `mcp__mcp-openapi-schema__*` | C-0450 |
| `design-cicd` | `mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows` | C-0144 (2 tools) |
| `design-iac` | `mcp__terraform-mcp__*` | C-0452 |
| `discovery-external-researcher` | `mcp__context7__resolve-library-id`, `mcp__context7__get-library-docs`, `mcp__exa__web_search_exa`, `mcp__exa__company_research_exa`, `mcp__exa__crawling_exa` | C-0453, C-0454 |
| `discovery-codebase-researcher` | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*`, **`mcp__serena__*`** | ADR-0007 v2.2.0; ADR-0040 |
| `review-architecture-auditor` | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*`, **`mcp__serena__*`** | ADR-0007 v2.2.0; ADR-0040 |
| `design-cc` | `mcp__serena__*` | ADR-0040 (touches auditing-mcp/scripts/) |
| `design-cicd` | (Serena added: `mcp__serena__*`; alongside the actionlint-mcp entries above) | ADR-0040 |
| `design-codespaces` | `mcp__serena__*` | ADR-0040 (touches auditing-codespaces/scripts/ if stub fills) |

Total touched agents: **8** (the 7 consumer-mapping agents above; design-cicd is mentioned twice because it gains both `mcp__actionlint-mcp__*` and `mcp__serena__*`). The 28 untouched agents (36 − 8) preserve C-0445.

(Resolution note: the original cc-design table had row 7 as "TBD per D-13 narrowing". ADR-0040 resolves this to a 5-agent list. Three of those five agents are *not in* the original 7-agent consumer-mapping (design-cc, design-cicd already-listed, design-codespaces); so the total touched count rises by 2 to **8 agents**, resolving I-DR-002.)

#### MCP Servers

| Server | Configuration | Tools Exposed | Auth Method |
|---|---|---|---|
| serena | `.mcp.json` stdio entry; `uvx --from git+https://github.com/oraios/serena@${SERENA_TAG}` | `mcp__serena__*` (narrowed to 5 agents per ADR-0040) | none |
| mcp-openapi-schema | stdio; `npx -y mcp-openapi-schema@0.0.1` | `mcp__mcp-openapi-schema__*` | none |
| actionlint-mcp | stdio; `actionlint-mcp` (installed via Go) | 2 tools | none |
| terraform-mcp | stdio; `terraform-mcp` (binary on PATH, GPG-verified per ADR-0041) | `mcp__terraform-mcp__*` | `TFE_TOKEN` (optional; local-only is no-auth) |
| gitnexus | stdio; `uvx --from gitnexus@${GITNEXUS_TAG}`; `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` | `mcp__gitnexus__*` | none |
| codebase-memory-mcp | stdio (per ADR-0007 v2.2.0) | `mcp__codebase-memory-mcp__*` (fallback only) | none |
| context7 | HTTP; `https://mcp.context7.com/mcp` | 2 named tools | `CONTEXT7_API_KEY` header |
| exa | HTTP; `https://mcp.exa.ai/mcp` | 3 named tools | `x-api-key` header |

#### File Naming & Layout Conventions Introduced

- **`.claude/runtime/` directory**: reserved for ephemeral runtime state. New: `mcp-events.jsonl` (gitignored) + `install-sentinels/<server>@<version>.installed` (the binary-presence-checked sentinels per ADR-0041). Enforcement: convention only + augmented `auditing-mcp` OP-5 / OP-6.
- **Sentinel naming**: `<server>@<version>.installed` where `<version>` is the value in `.devcontainer/versions.env` (commit-SHA-prefix for actionlint-mcp). Enforcement: postCreate.sh logic + OP-5 audit.

#### Project Filesystem Error State Design

- **Missing `.mcp.json`**: Claude Code session starts with zero MCP servers. The augmented `auditing-mcp` OP-1 / OP-2 BLOCKER. postStart's "default-fail-closed" filter (per ADR-0039) emits `structured_failure` record with `failure_class=process_start` and refuses to write events.
- **Malformed `.mcp.json`**: same as above; Claude Code surfaces parse error in `claude mcp list`; OP-1 BLOCKER.
- **Augmented `auditing-mcp` BLOCKER finding**: pipeline disposition per Open Items / OI-3 (hard gate vs strongly-recommended).
- **`auditing-mcp` script execution failure**: surfaces in the operator's terminal; non-zero exit code; the failure is itself a BLOCKER per the augmented skill's existing contract.

### Frontend Design

N/A — Frontend not in Layer Scope.

### Backend Design

N/A — Backend not in Layer Scope.

### API Design

N/A — API not in Layer Scope.

### Query & Data Access Design

N/A — Query not in Layer Scope.

### Database Schema & Migration Design

N/A — Database not in Layer Scope.

### CI/CD Design (GitHub Actions)

N/A — CI/CD not in Layer Scope (PRD Won't-Have: CI smoke-test for `claude mcp list` and `auditing-mcp` PR-gate are explicitly deferred).

### Infrastructure as Code Design

N/A — IaC not in Layer Scope.

---

### Dev Environment (Codespaces) Design

This subsection integrates codespaces-design.md per-layer subsection by reference; the full content lives in `working/feature/devcontainer-mcp-provisioning-r1/codespaces-design.md`. Key reconciliations made in this Blueprint:

- **Q-CS-1..Q-CS-8**: all eight composer-bound questions ratified with the codespaces-design `Recommended:` posture. Specific notes:
  - **Q-CS-3 (postStart fail vs warn-and-continue)**: ratified as warn-and-continue. Cross-layer with ADR-0037 (the postStart writes `readiness_probe` records; the lifecycle does not halt on a degraded HTTP server).
  - **Q-CS-5 (sentinel mechanism)**: ratified with the version-pinned-sentinel form per ADR-0041 — resolving I-DR-CS-001 in favor of the Persistence Boundaries spec. Sentinels are paired with the binary-presence check per ADR-0041 to resolve I-DR-CS-009.
  - **Q-CS-8 (mcp-events.jsonl schema ownership / sequencing)**: ratified — design-cc authors the schema first (KB-mcp-design `principles.md`); codespaces consumes. Plan-author sequences accordingly.
- **I-DR-CS-001 (sentinel naming)**: resolved — version-pinned form is canonical per ADR-0041.
- **I-DR-CS-002 (lifecycle-table rationale)**: resolved — ADR-0041 codifies "all installs in postCreate; if prebuilds are later adopted, a follow-up ADR moves the workspace-agnostic subset." Lifecycle table now references this contingency.
- **I-DR-CS-003 (secret-absent failure AC)**: resolved by **AC-X-1** above (codespaces postStart records a `result=fail` with `failure_layer=auth` and a `message_redacted` naming the missing env-var).
- **I-DR-CS-004 (codebase-memory-mcp absent from postStart SERVERS array)**: resolved by AC-X-2 — the SERVERS array contains 8 entries; the stderr banner reports "N/8 healthy".
- **I-DR-CS-005 / 006 (helper script ownership)**: resolved — added to scope per ADR-0041 (`lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`, `install/terraform-mcp.sh` are NEW artifacts owned by the codespaces layer; contract shapes per ADR-0041).
- **I-DR-CS-007 (Go feature version)**: deferred to plan-author (recommendation, not blocker).
- **I-DR-CS-008 (postStart exit 0 always)**: refined — exit 0 only when probe loop ran; infrastructure failures (e.g., `jq` missing) propagate as non-zero. Plan-author implements.
- **I-DR-CS-009 (sentinel/binary persistence mismatch)**: resolved by ADR-0041's binary-presence check (sentinel + `command -v` / smoke-test before honoring sentinel).
- **I-DR-CS-010 (redaction code-site contingency)**: resolved by ADR-0039 — postStart wrapper is the canonical code-site for the redaction filter. The filter consumes the env-block allowlist from `.mcp.json` at startup and applies before writing to `mcp-events.jsonl`.

#### Devcontainer Configuration

| File | Change | Purpose |
|------|--------|---------|
| `.devcontainer/devcontainer.json` | modified | Features additions (Node 20 LTS pin; Go); containerEnv updates; postCreateCommand and postStartCommand declarations |
| `.devcontainer/Dockerfile` | **NOT modified** | ADR-0041 codifies "no new project Dockerfile work" |
| `.devcontainer/docker-compose.yml` | N/A | No multi-container topology |

#### Base Image & Features

- **Base image**: `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` (unchanged).
- **Features (added):** `ghcr.io/devcontainers/features/node:1` with `version: "20"` (pin), `ghcr.io/devcontainers/features/go:1`.
- **Features (preserved):** `common-utils:2`, `github-cli:1`, `claude-code:1`.
- **Rationale for image choice**: synthesis constraint #1; existing repo convention; no Yarn-key re-litigation (E-0081).

#### Lifecycle Scripts

| Hook | Script | Purpose | Idempotent |
|------|--------|---------|------------|
| `initializeCommand` | (unused) | — | N/A |
| `onCreateCommand` | existing — version checks | Tool-presence verification | Yes |
| `updateContentCommand` | (unused) | — | N/A |
| `postCreateCommand` | `.devcontainer/postCreate.sh` (NEW) | Idempotent install for 6 OSS-local servers; sentinel + binary-presence check; fail-fast | Yes (sentinel-guarded) |
| `postStartCommand` | `.devcontainer/postStart.sh` (NEW) | Readiness probe for 8 registered servers; writes `readiness_probe` records to `mcp-events.jsonl`; warn-and-continue | Yes (probe loop is read-only of state; write is append-only) |
| `postAttachCommand` | (unused per Q-CS / codespaces-design — no attach-time work warranted) | — | N/A |

#### Forwarded Ports & Services

| Port | Service | Visibility | Auto-forward |
|------|---------|------------|--------------|
| (none) | — | — | — |

`forwardPorts: []`; `portsAttributes: {}`. AC-CS-7 codifies.

#### Prebuilds

- **Prebuild config**: **NOT adopted** in this release (Q-CS-2 deferred).
- **Expected cold-start time**: ~7–12 min cold cache (within NFR-1 ~10 min target near upper bound). Warm-cache ~1–2 min via sentinel short-circuit.

#### VS Code Configuration

- No changes to existing extensions / settings / tasks / launch configs.

#### Parity with CI & Production

- **CI uses the same image?** N/A (CI/CD out of scope this feature).
- **Production parity**: N/A (no production deployment; project is operator-run).

#### Secrets in Codespaces

- **Required Codespace secrets**: `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` (TFE_TOKEN optional — local-only Terraform MCP works unauthenticated).
- **Wiring**: devcontainer.json `containerEnv` block uses `${localEnv:NAME}` indirection.
- **First-run experience**: operator must set the three Codespaces secrets before opening the Codespace (or accept degraded operation per AC-X-1).

---

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---|---|---|---|---|
| **Install-time** | `go install actionlint-mcp` fails | postCreate.sh exit code | Fail-fast; operator sees specific server name on terminal (AC-CS-3); pipeline halts | Operator rebuilds after fix |
| **Pin-bump mismatch** | New `SERENA_TAG` in versions.env doesn't invalidate old sentinel | Binary-presence check detects sentinel-present + binary-absent | postCreate deletes stale sentinel + re-installs | Transparent to operator (extra postCreate work logged) |
| **Probe failure (transient)** | Context7 HTTP returns 503 mid-probe | postStart.sh probe returns non-zero | Append `readiness_probe` record with `result=fail`, `failure_layer=transport`; emit stderr banner; exit 0 (warn-and-continue per AC-CS-5) | Operator sees banner; reviews mcp-events.jsonl |
| **Missing credential** | `EXA_API_KEY` unset | postStart.sh detects empty env-var before probe | Record `result=fail`, `failure_layer=auth`, `message_redacted="missing env-var EXA_API_KEY"` per AC-X-1; stderr banner | Operator sets Codespaces secret and reopens |
| **Primary→fallback transition** | GitNexus stdio process exits mid-session | In-product fallback-detection code-site detects | Append `primary_degraded` + `structured_failure` records; stderr banner per ADR-0037; pipeline continues on codebase-memory-mcp | Operator sees banner; pipeline runs on fallback |
| **Augmented `auditing-mcp` BLOCKER** | OP-2: consumer-mapping drifted | `audit_mcp.py` exit code | Operator runs audit; sees BLOCKER finding; resolves before Gate 6 | Pipeline gate per OI-3 |
| **Credential leak detected in mcp-events.jsonl** | OP-6 grep finds credential shape | `audit_mcp.py --with-runtime` | BLOCKER; operator rotates credential + investigates redaction filter | Pipeline halt per ADR-0039 |
| **`.mcp.json` malformed** | postStart.sh fails to parse env-block | `jq` parse failure | Default-fail-closed: empty allowlist; emit `structured_failure` with `failure_class=process_start`; warn-and-continue | Operator inspects `.mcp.json`; rebuild after fix |

### Logging and Monitoring

- **Log events**:
  - postCreate.sh: per-server install start/end + sentinel write.
  - postStart.sh: per-server probe latency + result + (on failure) failure_layer.
  - Primary→fallback transitions (ADR-0037).
  - `auditing-mcp` audit outcomes (BLOCKER / MAJOR / MINOR / NIT counts).
- **Log levels**:
  - INFO: install success, probe pass.
  - WARN: probe fail (transient).
  - ERROR: install fail (fail-fast); credential leak detected (OP-6 BLOCKER); .mcp.json parse error.
- **Sensitive data**: credential values redacted at the log-surface boundary per ADR-0039.
- **Metrics**: none (project is operator-run; no remote sink per PRD Won't-Have).
- **Traces**: none.
- **Alerts**: none (no on-call rotation per PRD NFR-8).
- **Dashboards**: none.

## Implementation Plan

### Implementation Approach

**Selected Approach**: Sequential per-layer with cross-layer reconciliation gates. Codespaces foundation (Features + containerEnv) before any postStart work; cc-layer authoring of `.mcp.json` schema and `mcp-events.jsonl` schema before codespaces postStart.sh implementation; auditing-mcp augmentation after both layers' artifacts exist.

**Selection Reason**: The two layers have tight cross-layer contracts (the `mcp-events.jsonl` schema is cc-owned + codespaces-consumed; the env-block-as-redaction-allowlist is cc-owned + codespaces-consumed at postStart). Sequencing prevents windowed inconsistencies.

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **ADR + schema authoring (this Blueprint)**
   - Layer: design-composer (this stage)
   - Technical Reason: Five ADRs and the mcp-events.jsonl schema must exist before plan-author writes per-task instructions
   - Dependent Elements: all subsequent

2. **`.devcontainer/versions.env` + devcontainer.json Features**
   - Layer: codespaces
   - Technical Reason: Plan-author needs the pin values to author postCreate.sh; the Node 20 + Go Features must exist before postCreate runs `go install` / `npx`
   - Prerequisites: ADRs authored

3. **`KB-mcp-platform/` + `KB-mcp-design/` skill authoring**
   - Layer: claude-code
   - Technical Reason: `KB-mcp-design/references/principles.md` is the canonical home for the `mcp-events.jsonl` schema (per ADR-0037). postStart.sh consumes this schema. The schema must be authored before the consumer.
   - Prerequisites: ADRs authored

4. **`.mcp.json` authoring**
   - Layer: claude-code
   - Technical Reason: postStart.sh reads `.mcp.json` to enumerate registered servers + extract redaction allowlist. The Claude Code session also reads `.mcp.json` at session start; the agent allowlist edits (next) depend on the server-name keys here.
   - Prerequisites: ADR-0037, ADR-0039, KB-mcp-platform's `.mcp.json` template (item 3)

5. **`.devcontainer/postCreate.sh` + `install/terraform-mcp.sh` + `lib/mcp-ping.sh` + `lib/mcp-auth-probe.sh`**
   - Layer: codespaces
   - Technical Reason: postCreate must succeed before postStart probes the binaries.
   - Prerequisites: items 2, 3, 4

6. **`.devcontainer/postStart.sh`**
   - Layer: codespaces
   - Technical Reason: Consumes the mcp-events.jsonl schema (from item 3) and the .mcp.json (from item 4).
   - Prerequisites: items 3, 4, 5

7. **7 of 36 `.claude/agents/*.md` edits**
   - Layer: claude-code
   - Technical Reason: Adds `mcp__<server>__<tool>` entries that reference servers registered in `.mcp.json` (item 4). Per ADR-0040 also includes 3 Serena additions to design-cc, design-cicd, design-codespaces.
   - Prerequisites: item 4

8. **`auditing-mcp/` augmentation (10 rule families + 6 new scripts)**
   - Layer: claude-code
   - Technical Reason: Validates the contracts established by items 3-7. Runnable at any time after they exist; the OP-5 lifecycle audit reads devcontainer.json (item 2); OP-6 reads mcp-events.jsonl (after item 6 runs at least once).
   - Prerequisites: items 2-7

9. **`.gitignore` update + `.claude/runtime/.gitkeep`**
   - Layer: claude-code
   - Technical Reason: Bootstraps the directory + ignores the runtime file. Resolution of Q-CC-2.
   - Prerequisites: none (independent housekeeping)

10. **ADR-0007 relocation (`adrs-migrated/` → `adrs/`)**
    - Layer: claude-code (ADR registry housekeeping)
    - Technical Reason: Per ADR-0038 / ADR-0036 single-canonical-ADR-location.
    - Prerequisites: ADR-0038 (this Blueprint)

11. **ADR-0018 v1.0.0 supersession marker + KB-codebase-research + discovery-codebase-researcher schema_version bump to 1.1.0**
    - Layer: claude-code
    - Technical Reason: ADR-0038 codifies; downstream consumers update to cite v1.1.0 + ADR-0038.
    - Prerequisites: ADR-0038

#### Cross-Layer Sequencing Notes

- **Schema before consumer**: KB-mcp-design `principles.md` (mcp-events.jsonl schema) before postStart.sh.
- **.mcp.json before agent edits**: agent allowlist entries must name registered servers.
- **devcontainer Features before postCreate**: postCreate.sh runs `go install` (needs Go feature) and `npx` (needs Node feature).
- **postCreate before postStart**: postStart probes binaries that postCreate installed.
- **All artifacts before auditing-mcp augmentation finalization**: the audit rules validate the live state; activate after the state exists.

### Migration Strategy

This feature is greenfield within its layers — there is no existing MCP wiring to migrate. The one supersession (ADR-0018 v1.0.0 → ADR-0038 v1.1.0) is additive-schema, handled by:
- Mark ADR-0018 status `Superseded by ADR-0038` (file remains in place per ADR-0005).
- Update KB-codebase-research/SKILL.md to cite ADR-0038 and `schema_version: 1.1.0`.
- Update discovery-codebase-researcher.md the same way.
- (Optional, low priority) Relocate ADR-0007 from `adrs-migrated/` to `adrs/` per ADR-0036.

### Feature Flags & Rollout

| Flag | Default | Audience Progression | Kill-Switch Behavior |
|------|---------|----------------------|----------------------|
| `MCP_AUTH_PROBE` (env var; gates Context7 + Exa supplementary auth probes per D-0008) | `0` for postStart (every-attach probe; respects API quota); `1` for postCreate (initial install verify) | n/a (operator-runtime flag) | Setting to `0` reverts to ping-only probes |

No other feature flags. The pipeline is operator-run.

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: Codespaces secrets surface (`CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN`); no other AuthN/Z surface.
- **Input Validation**: postStart.sh validates `.mcp.json` structure at startup; default-fail-closed if malformed (per ADR-0039).
- **Sensitive Data Handling**: per ADR-0039 — redact-at-source from `.mcp.json` env-block + HTTP-headers allowlist; URL-embedded credentials rejected at config-validation (OP-9); argv-leakage rejected at config-validation (OP-10); runtime log redaction validated by OP-6.

### Frontend / Backend / API / Query / Database

N/A — layers out of scope.

### CI/CD

- **Secret exposure surface**: N/A (no workflows authored).
- **Supply chain**: Terraform MCP install via `wget` + SHA256SUMS + GPG verify against HashiCorp public key (ADR-0041). Per-server pin discipline (`versions.env`) provides supply-chain reproducibility (D-0011).

### IaC

N/A — layer out of scope.

### Codespaces

- **Repo access from Codespace**: GITHUB_TOKEN scoped per existing claude-code Feature; no new scope changes.
- **Dotfiles / extension trust**: no change.
- **Codespaces secrets exposure**: secrets flow Codespaces secret store → `containerEnv` (via `${localEnv:NAME}`) → `${VAR}` substitution in `.mcp.json`. The secrets are never written to any file; the `.mcp.json` only carries the env-var NAME. Runtime log redaction (ADR-0039) defends against accidental capture in `mcp-events.jsonl`.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---------------------|-------|-----------|
| MCP upstream sources (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, GitNexus, codebase-memory-mcp) | No | These are real upstreams; the install scripts pull from them. Acceptance is the actual install + probe pass. |
| Context7 / Exa SaaS endpoints | No | Real endpoints; tests at acceptance time use the real auth + real probe. The supplementary auth probes are gated on `MCP_AUTH_PROBE=1` to respect quotas. |
| Codespaces secrets surface | No (in Codespace) / Mock-via-local-env (in local devcontainer) | The Codespace environment provides the real secrets; local devcontainer testing requires the operator to set env vars manually. |
| `claude mcp list` output parsing | No (per ADR-0041 / D-0008) | Direct JSON-RPC probe via `lib/mcp-ping.sh` is the canonical primitive; we do NOT parse `claude mcp list` (brittle). |
| `mcp-events.jsonl` event records | Synthetic fixtures for unit tests of `auditing-mcp` OP-6 | The redaction-integrity check is tested against synthetic credential-shape strings; the live file is tested end-to-end. |

### Data Layer Testing Strategy

N/A — no data layer (no DB / no ORM).

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|-------|-----------|---------|----------|
| Claude Code | static-config audit | `auditing-mcp/scripts/audit_mcp.py` (Python) | `.claude/skills/auditing-mcp/scripts/` |
| Claude Code | runtime audit | `auditing-mcp/scripts/audit_mcp.py --with-runtime` | same |
| Claude Code | per-agent allowlist consistency | OP-2 / OP-3 scripts (NEW per cc-design) | same |
| Codespaces | postCreate / postStart smoke (cold-cache) | wall-clock vs NFR-1; mcp-events.jsonl inspection | manual at Gate 6; operator workflow |
| Codespaces | rebuild idempotence (warm-cache) | rerun postCreate; sentinel + binary-presence check; expect short-circuit | manual at Gate 6 |
| Cross-layer | `claude mcp list` shows 8 connected | the canonical acceptance command | manual at Gate 6 |
| Cross-layer | per-server probe pass | the agreed probe per server (FR-4) | invoked via Claude Code session or audit-script in `--with-runtime` mode |

### Integration Verification Points

- **`claude mcp list` shows 8 of 8 connected** at postCreate completion (AC-FR-1-a + AC-CC-1).
- **Per-server probe returns success** for all 8 (AC-FR-1-b + AC-FR-4-a).
- **`mcp-events.jsonl` contains 8 `readiness_probe` records** after postStart (AC-CS-4 + AC-CC-6).
- **`auditing-mcp` zero BLOCKER findings** at Gate 6 (AC-FR-11-c + AC-CC-5 + AC-NFR-2-c).
- **`git grep` finds zero literal credentials** across the repo (AC-NFR-2-a + AC-CC-4).
- **OP-4 finds primary/fallback prose** in discovery-codebase-researcher + review-architecture-auditor (per ADR-0037).

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**:
  - All 8 mcpServers in `.mcp.json` connect at postCreate.
  - Per-server probe returns success for each.
  - 7 agent files carry the prescribed `mcp__` entries; 29 preserve zero-`mcp__`.
  - `mcp-events.jsonl` contains 8 `readiness_probe` records (one per registered server) after every postStart cycle, with `result: pass` or `result: fail` + `failure_layer`.
  - `auditing-mcp` (10 rule families) reports zero BLOCKER findings against the post-feature devcontainer.
  - W/H/A trifecta is structurally complete and cross-referenced per the universal convention.
  - No credential value in any committed file or any line of `mcp-events.jsonl`.
- **Verification method**:
  - End-to-end smoke: open a fresh Codespace; observe postCreate completes; observe postStart writes 8 records; run `claude mcp list`; run `auditing-mcp/scripts/audit_mcp.py --with-runtime`; verify zero BLOCKER.
  - Per-AC EARS-form acceptance test (authored by `test-acceptance-author` downstream).
- **Verification timing**:
  - At Gate 6 (Deliverable Packaging).
  - On every Codespace rebuild (continuous; lifecycle health-check produces fresh evidence).

### Early Verification Point

- **First verification target**: A single Codespace rebuild with `.mcp.json` + Features + postCreate.sh stub installing one server (Serena via uvx). If Serena installs and `claude mcp list` shows it connected, the install-path discipline (ADR-0041) is validated; the remaining six follow the same pattern.
- **Success criteria**: `claude mcp list` shows `serena: connected` after fresh build.
- **Failure response**: revisit ADR-0041 install-path posture; possibly reconsider Q-CS-2 (prebuild adoption) earlier.

### Output Comparison

N/A — entirely new behavior; no existing equivalent to compare against.

### Operational Verification

- **Pre-merge gates**: TBD per OI-3 (whether augmented `auditing-mcp` is a hard Gate 6 gate). Default disposition: BLOCKER findings halt the orchestrator at Gate 6.
- **Post-deploy verification**: every Codespace rebuild produces fresh `readiness_probe` records; operator inspects.
- **Migration verification**: KB-codebase-research/SKILL.md and discovery-codebase-researcher.md cite `schema_version: 1.1.0` and ADR-0038 — verified by grep at Gate 6.
- **Rollback rehearsal**: N/A (no production deployment; rollback = revert merge).

## Future Extensibility

- **Extension points**:
  - `.mcp.json` is the SSOT; adding a new MCP server = adding to `.mcp.json` `env:` block (automatically covered by redaction + audit) + per-agent allowlist (if consumed) + KB-mcp-platform reference page.
  - `mcp-events.jsonl` schema accepts additive event types; the OP-6 audit rule remains valid (it grep-matches credential shapes, not event-type names).
  - The augmented `auditing-mcp` is plan-author-extensible; adding an OP-11 rule = adding a script in `scripts/` + a row in the rule-family table.
- **Known future requirements**:
  - Plugin packaging of the trifecta (Q-CC-7) — design is plugin-compatible by following the universal trifecta conventions.
  - Prebuild adoption (Q-CS-2) — if cold-cache time becomes a felt constraint, a follow-up moves the workspace-agnostic install subset to `onCreateCommand`.
  - CI smoke-test workflow (`claude mcp list` + `auditing-mcp`) — PRD Won't-Have for this release; follow-up feature.
  - Serena post-v1.3.0 migration (`base_modes` → `added_modes`) — ADR-0040 pins pre-v1.3.0; follow-up ADR bumps.
  - Filling auditing-codespaces STUB (ADR-0033) — the augmented `auditing-mcp` OP-5 owns lifecycle audit until then; can hand back cleanly.
- **Intentional limitations**:
  - No remote log sink, metrics dashboard, alerting (PRD Won't-Have; operator-run pipeline).
  - No structured frontmatter field for primary/fallback declaration (ADR-0037 prefers prose-with-audit-rule).
  - No new sub-agents introduced.
  - No CLAUDE.md added at this stage (cc-design).

## Alternative Solutions

### Alternative 1: Dockerfile-bake everything

- **Overview**: Bake all seven MCP server installs into a custom Dockerfile layer.
- **Advantages**: All installs cached in image layers; faster cold-cache builds.
- **Disadvantages**: Re-litigates E-0081 stale-apt-key history; mixed package managers inflate complexity; pin-bumps force full Dockerfile rebuilds.
- **Reason for Rejection**: ADR-0041 codifies the "no new project Dockerfile work" posture honoring the existing fragility history.

### Alternative 2: Structured frontmatter field for primary/fallback declaration

- **Overview**: Introduce `mcp_primary:` / `mcp_fallback:` agent-file frontmatter fields.
- **Advantages**: Self-documenting at the agent file level.
- **Disadvantages**: New 36-agent-wide convention with zero precedent (C-0445); inventing a convention to address two-agents' needs violates KB-cc-design Principle 4.
- **Reason for Rejection**: ADR-0037 prefers prose-only with OP-4 audit rule; defers introducing structured field until two cases need it.

### Alternative 3: Drop Serena from .mcp.json

- **Overview**: Remove Serena entirely given the 73.8% markdown corpus.
- **Advantages**: Eliminates the v1.3.0 risk; reduces always-on count.
- **Disadvantages**: PRD Q4 Product Policy forecloses (all seven always-on); loses symbol-level value on 52 Python audit scripts.
- **Reason for Rejection**: ADR-0040 narrows the allowlist (5 agents) rather than dropping the server.

### Alternative 4: Adopt prebuilds in this release

- **Overview**: Codespaces prebuilds to reduce cold-cache rebuild time.
- **Advantages**: Lower cold-cache time.
- **Disadvantages**: Org compute budget; branch-coverage decisions; postCreate-captured installs require moving workspace-agnostic subset to onCreate (lifecycle table changes).
- **Reason for Rejection**: Q-CS-2 defers; post-ship monitoring drives the decision.

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| Cold-cache build sits at upper bound of NFR-1 ~10 min target | codespaces | Medium (annoyance) | Medium | Estimate ~7-12 min per codespaces §Rebuild-Time Estimate; mitigation deferred to post-ship Q-CS-2 (prebuild adoption); kill criterion at 2× target (PRD Rollout Plan) |
| GitNexus skip-grammars smoke-test (C-0388/C-0411 partially_verified-medium) fails on pinned tag | codespaces | Medium | Medium | AC-CS-9 codifies fail-postCreate; operator sees failing server immediately and can repin |
| Stdio servers not auto-reconnected (C-0301) — six of seven fail open to operator recovery | claude-code | High (silent surface failure) | Low (event surface is now wired) | ADR-0037 `structured_failure` + stderr banner makes failures operator-visible; FR-9 contract is load-bearing |
| Credential leak in `mcp-events.jsonl` despite redaction | claude-code | **CRITICAL** (release blocker) | Low | ADR-0039 + OP-6 grep audit; `auditing-mcp --with-runtime` runs at Gate 6; default-fail-closed if allowlist empty |
| ADR-0007 relocation surfaces deferred content questions | claude-code | Low | Low | Relocation is independent of content; v2.2.0 content unchanged |
| Per-agent context overhead with 8 always-on servers exceeds tolerable envelope across 36 agents (NFR-4) | claude-code | Medium | Medium-low (tool schemas deferred per cc-design Principle 1) | Plan-author measures in implementation; if intolerable, downscoping (conditional activation) opens as re-scope |
| The 5-agent Serena allowlist (ADR-0040) misses an agent that actually needs Serena | claude-code | Low (additive fix) | Low-medium | OP-2 audit + operator feedback in first weeks post-ship surfaces; additive ADR amendment is cheap |
| W/H/A trifecta drift over time (KB-mcp-platform and KB-mcp-design fall out of sync with `.mcp.json`) | claude-code | Medium (the maintenance interface becomes a lie) | Medium | OP-7 trifecta-consistency audit rule (every server in `.mcp.json` named in KB-mcp-platform; cross-references current); runs at every operator-invocation of `auditing-mcp` |
| Plan-author misses a sentinel/binary-persistence edge case (I-DR-CS-009 reopened by some unconsidered rebuild path) | codespaces | Medium | Low | ADR-0041 Implementation Guidance gives plan-author the binary-presence check pattern; OP-5 lifecycle audit catches sentinel-without-binary mismatches |
| Q-CC-9 / OI-3 — augmented `auditing-mcp` hard-gate vs strongly-recommended | (cross-cutting) | Medium (pipeline behavior at Gate 6) | n/a (policy decision) | Open Items → user decides; AC-CC-5 codifies zero BLOCKER as the *bar*; whether the bar halts the pipeline is the open question |
| Helper scripts (`lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`) introduce subtle JSON-RPC bugs | codespaces | Medium | Low-medium | ADR-0041 fixes contract; plan-author writes; review at Gate 5 |

## References

- **PRD**: `working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md` (v3.0.0)
- **Synthesis**: `working/feature/devcontainer-mcp-provisioning-r1/synthesis.md`
- **Codebase Analysis**: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json`
- **Per-layer Designs**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-design.md` (Claude Code / Project Filesystem)
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-design.md` (Dev Environment / Codespaces)
- **Per-layer Dependency Sidecars**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-dependencies.json`
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-dependencies.json`
- **Per-layer Review Findings (resolved/integrated in this Blueprint)**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-design-review-issues.json` (6 findings; resolution mapping below)
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-design-review-issues.json` (10 findings; resolution mapping below)
- **Research Notes**: `working/feature/devcontainer-mcp-provisioning-r1/research-notes/T-001..T-008.md`
- **ADRs authored in this Blueprint** (in `working/feature/devcontainer-mcp-provisioning-r1/adrs/`; promoted to `/workspaces/feature-pipeline/adrs/` at deliverable packaging time per ADR-0036):
  - ADR-0037 — MCP transition surfacing — `mcp-events.jsonl` + stderr banner (UI-15)
  - ADR-0038 — `codebase-analysis.json` schema v1.1.0 (supersedes ADR-0018 v1.0.0)
  - ADR-0039 — Credential redaction posture — redact-at-source from `.mcp.json` env-block
  - ADR-0040 — Serena — narrowed always-on; Python-audit-surface allowlist (5 agents); pinned pre-v1.3.0
  - ADR-0041 — Install-mechanism strategy — hybrid Features + idempotent postCreate + verified binary fetch
- **Existing ADRs referenced**: see Background and Context / Prerequisite ADRs above.
- **KBs used in composition**: KB-documentation-criteria (Blueprint + ADR templates; layer taxonomy; EARS), KB-general-coding-principles (code-block rubric for sample sketches), KB-review-disciplines (Gate 0/1 self-check), KB-cc-design + KB-cc-platform (per-layer composition), KB-codespaces-design + KB-codespaces-platform (per-layer composition).

### Open Items (deferred to user / Gate 4 disposition)

- **OI-1 (resolves Q-CC-6 / I-DR-001)**: Inventory count convention. **Resolution baked into AC-X-2 above**: PRD's "seven named servers" = primary surface; `.mcp.json` carries 8 entries (7 primary + 1 documented fallback). No PRD amendment required; the augmented auditing-mcp special-cases codebase-memory-mcp by name. **User confirms convention at Gate 4.**
- **OI-2 (resolves Q-CC-1)**: Family-coordinator path. **Composer disposition: Path B (auditing-mcp remains in auditing-cc-configs family).** Minimum convention change. **User may revisit at Gate 4 if they want auditing-mcp graduated to its own family.**
- **OI-3 (resolves Q-CC-9)**: Augmented `auditing-mcp` Gate 6 status — hard gate vs strongly-recommended. **Composer recommends: hard gate** (any BLOCKER finding halts orchestrator at Gate 6). **User decision required at Gate 4 — this affects the phase-validator plan-author writes.**
- **OI-4**: Per-agent context-overhead measurement (UI-7 from PRD). Plan-author measures during implementation; if intolerable, opens a downscoping re-scope. Not blocking Gate 4.
- **OI-5**: ADR-0007 content review post-relocation. Plan-author may file a separate review-and-update follow-up; not blocking this feature.

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial Blueprint composition. Integrates cc-design.md + codespaces-design.md; authors ADR-0037 through ADR-0041; resolves 9 Q-CC-N + 8 Q-CS-N + 16 I-DR-N items; codifies the 8-entry inventory convention (AC-X-2) and the secret-absent failure mode (AC-X-1); adopts Path B for family-coordinator (Q-CC-1). | design-composer |
