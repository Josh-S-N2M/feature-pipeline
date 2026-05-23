---
id: BP-devcontainer-mcp-provisioning-r1
version: 3.0.2
status: draft
doc_type: blueprint
feature_slug: devcontainer-mcp-provisioning-r1
supersedes: blueprint-v2.md
predecessor: working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
codebase_analysis: working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json
change_summary: >-
  Focused propagation of three Gate-4 user decisions on Blueprint v2 Open
  Items. (1) OI-1 — inventory convention drops codebase-memory-mcp fallback;
  the design now carries 7 named MCP servers, 7 .mcp.json entries, 7
  readiness_probe records (was 7+1 fallback). Companion ADR-0037 edit
  reverts "eight" to "seven". (2) OI-2 — Path A graduation: auditing-mcp
  becomes its own family-coordinator (was Path B preserving auditing-cc-configs
  family). ADR-0042 authored to codify the precedent. (3) OI-3 — hard gate:
  any BLOCKER finding from augmented auditing-mcp halts the orchestrator at
  Gate 6 (was TBD). ADR-0043 authored to codify the policy. All other v2
  content preserved verbatim. Section count remains 15.
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
  - ADR-0037   # mcp-events.jsonl + stderr-banner transition surfacing (Implementation Guidance edited in v3 per OI-1 closure)
  - ADR-0038   # codebase-analysis schema v1.1.0 (supersedes ADR-0018 v1.0.0)
  - ADR-0039   # credential redaction posture — redact-at-source from .mcp.json env-block
  - ADR-0040   # Serena posture — narrowed always-on; Python-audit-surface allowlist; pin pre-v1.3.0
  - ADR-0041   # install-mechanism — hybrid Features + idempotent postCreate + verified binary fetch
  - ADR-0042   # auditing-mcp family graduation (NEW; codifies OI-2 Path A user override)
  - ADR-0043   # auditing-mcp Gate-6 hard gate (NEW; codifies OI-3 user resolution)
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

This feature provisions seven named MCP servers (Serena, mcp-openapi-schema, actionlint-mcp, HashiCorp Terraform MCP, Context7, Exa, GitNexus) into this project's devcontainer; wires them into eight of the project's 36 sub-agents under a least-privilege `mcp__<server>__<tool>` allowlist; adds the W/H/A trifecta halves (KB-mcp-platform, KB-mcp-design) plus an augmented audit-half (auditing-mcp) so MCP operations remain reasonable about long after this feature ships; and codifies the lifecycle health-check, runtime log, transition-surfacing, and credential-redaction posture necessary to detect and recover from MCP failures across the Codespace lifecycle. Per Blueprint v3 Gate-4 OI-1 closure, the codebase-memory-mcp fallback (previously the 8th `.mcp.json` entry) is **dropped** from this feature's inventory — the design now carries exactly 7 named MCP servers with no fallback entry.

The two layers that own the work are **Claude Code / Project Filesystem** (`.mcp.json`, the eight `tools:` allowlist edits across 36 agents, the trifecta skills, the `mcp-events.jsonl` schema) and **Dev Environment / Codespaces** (devcontainer.json features block, lifecycle hooks, install scripts, secret wiring, postStart readiness probe). The seven ADRs authored in this Blueprint (ADR-0037 through ADR-0041 from v2, plus ADR-0042 and ADR-0043 newly authored at v3 to codify the Gate-4 user decisions) capture the architecturally one-way decisions; the rest are integrated per-layer subsections that compose into a single shipping unit.

### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers are marked `N/A — out of scope` without further elaboration.

- [x] **Claude Code / Project Filesystem** — `.mcp.json` (NEW), 8 `.claude/agents/*.md` `tools:` allowlist edits, `KB-mcp-platform/` (NEW), `KB-mcp-design/` (NEW), augmented `auditing-mcp/` (graduated to its own family per ADR-0042; `auditing-cc-configs/SKILL.md` family list updated; `auditing-shared/SKILL.md` consumer-list updated), `.claude/runtime/mcp-events.jsonl` (NEW; gitignored)
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
  Two-layer cross-cutting work with seven composing one-way architectural decisions
  (ADR-0037 through ADR-0043). The complexity is bounded by the closed seven-server
  list (per Gate-4 OI-1 closure: codebase-memory-mcp fallback dropped) and the
  prose-only-with-audit-rule resolution to UI-15 (which avoids inventing a
  36-agent-wide structured frontmatter convention). The augmented auditing-mcp
  skill is the project's safety-net (now graduated to its own family per
  ADR-0042; hard-gating per ADR-0043): 10 rule families (OP-1..OP-10) cover
  static config, runtime events, and trifecta consistency.
layers_touched:
  - "Claude Code / Project Filesystem"
  - "Dev Environment (Codespaces / Devcontainer)"
blast_radius:
  runtime: "All 36 sub-agents see new .mcp.json registrations; 8 agents gain new mcp__ tool entries; the 28 untouched agents preserve the C-0445 zero-mcp__ invariant. Inventory: 7 named MCP servers (no fallback), 7 .mcp.json entries, 7 readiness_probe records per postStart cycle, per Gate-4 OI-1 closure."
  build_time: "Cold-cache devcontainer build estimated ~7–12 min (NFR-1 target ~10 min); warm-cache ~1–2 min via version-pinned sentinels"
main_constraints:
  - "Base image (mcr.microsoft.com/devcontainers/python:1-3.11-bookworm) is fixed; constraints #1-4 from synthesis §8 (no Go, no Node, no DinD in base)"
  - "PRD Q4 closed list: all seven servers always-on at project scope"
  - "OWASP MCP01 Token Mismanagement is the top-ranked MCP risk (codified by ADR-0039)"
  - "Existing C-0445 zero-mcp__ invariant on the 28 non-consumer agents must be preserved"
  - "ADR-0005 append-only supersession (ADR-0018 v1.0.0 is preserved; ADR-0038 v1.1.0 is the new canonical)"
  - "Gate-4 user decisions (OI-1/OI-2/OI-3) closed and codified by ADR-0042 + ADR-0043; no fallback entry in .mcp.json (OI-1); auditing-mcp graduated to its own family (OI-2); auditing-mcp Gate-6 is a hard gate (OI-3)"
biggest_risks:
  - "Cold-cache build time sits near the NFR-1 ~10-min target upper bound; mitigation deferred to post-ship prebuild adoption"
  - "GitNexus skip-grammars smoke-test is partially_verified-medium (C-0388/C-0411 Mintlify-mirrored); fail-postCreate on smoke-test failure (AC-CS-9)"
  - "Stdio servers are not auto-reconnected by Claude Code (C-0301 verbatim Anthropic); seven servers fail open to operator recovery → FR-9 structured-failure-record (ADR-0037) is load-bearing"
unknowns:
  - "Whether `claude mcp ping` exists in the pinned Claude Code Feature version (OI-CS-5 verify-at-execution; ADR-0041 codifies fallback to direct JSON-RPC)"
  - "Exact actionlint-mcp commit SHA at install time (C-0133 no tagged releases as of 2026-05-23 — verify-at-execution)"
  - "Whether design-codespaces's ADR-0040 Serena allowlist entry actually fires within 90 days post-ship — depends on whether auditing-codespaces ADR-0033 stub is filled (see OI-6)"
```

## Background and Context

### Prerequisite ADRs

- **ADR-0005** — append-only supersession discipline (this Blueprint supersedes ADR-0018 v1.0.0 via ADR-0038; both files preserved).
- **ADR-0007 v2.2.0** — GitNexus primary / codebase-memory-mcp fallback policy. **Per Gate-4 OI-1 closure**, the codebase-memory-mcp fallback is no longer registered in this feature's `.mcp.json`; the ADR-0007 policy remains in force as a project-level architectural fact, but this feature's inventory does not provision the fallback. Future features may revisit if fallback registration is needed.
- **ADR-0018 v1.0.0** — codebase-analysis schema (superseded in this feature by ADR-0038 v1.1.0).
- **ADR-0020** — KB structure / lowercase-hyphenated skill name convention. The two new skills (`KB-mcp-platform`, `KB-mcp-design`) conform.
- **ADR-0022** — subagent reasoning configuration. Per cc-design Principle 9, this feature does NOT modify any agent's `model:`/`effort:`/`skills:` fields; only `tools:` arrays are touched.
- **ADR-0030** — pedagogical-marker justification spec. Both new skills declare `pedagogical_sections` frontmatter.
- **ADR-0031** — auditing-shared skill module. Referenced indirectly by `auditing-mcp` augmentation; **ADR-0042 augments the cross-reference** by adding `auditing-mcp` as a graduated-family consumer of `auditing-shared`.
- **ADR-0033** — auditing-codespaces STUB / ADR-0029 execution extension. The augmented auditing-mcp owns lifecycle-completeness audit (OP-5) until auditing-codespaces stub is filled. Also: ADR-0040's design-codespaces Serena entry is forward-looking on this stub becoming real (see OI-6 / Known Unknown in ADR-0040 Decision Details).
- **ADR-0036** — single-location ADR placement. ADR-0007 relocation per ADR-0038 honors this.

**Authored in this feature:** ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041 (from Blueprint v1/v2), **ADR-0042** (Gate-4 v3 — auditing-mcp family graduation), **ADR-0043** (Gate-4 v3 — auditing-mcp Gate-6 hard gate). See ADR References below.

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
| MCP upstream: actionlint-mcp | `go install github.com/hongkongkiwi/actionlint-mcp@<sha>` | commit-SHA pin (no tagged releases C-0133); upstream identifier corrected at cycle-3 reconciliation (was `2manymws/actionlint-mcp` — repo 404; corrected to `hongkongkiwi/actionlint-mcp`; main.go at repo root, no `/cmd/...` subpath) |
| MCP upstream: Terraform MCP | `wget` release artifact from `releases.hashicorp.com`; SHA256 + GPG verify | binary-fetch path per ADR-0041 |
| MCP upstream: GitNexus | `npm install -g gitnexus@<TAG>` (persistent) / `npx -y gitnexus@<TAG> mcp` (ephemeral); `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` smoke-test | per ADR-0007 v2.2.0; install mechanism corrected at cycle-3 reconciliation (was `uvx` — GitNexus is npm-only TypeScript, not PyPI; AC-CS-9 wrapping intent preserved — env-var still suppresses npm's vendored tree-sitter grammar build). Prereq: Node.js LTS on PATH (provided by `node:1@20` Feature). |
| MCP upstream: Context7 | `https://mcp.context7.com/mcp` (remote HTTP) | `CONTEXT7_API_KEY` header per ADR-0039 |
| MCP upstream: Exa | `https://mcp.exa.ai/mcp` (remote HTTP) | `x-api-key` header per ADR-0039; URL-query form REJECTED |
| Codespaces secrets | `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` (TFE_TOKEN optional) | via `${localEnv:NAME}` indirection in `containerEnv` |

(Note: codebase-memory-mcp upstream row removed at v3 per Gate-4 OI-1 closure.)

### Agreement Checklist

#### Scope

- [x] `.mcp.json` (NEW at repo root) — register the 7 named servers (no fallback entry; per Gate-4 OI-1 closure)
- [x] 8 of 36 `.claude/agents/*.md` files — add `mcp__<server>__<tool>` entries
- [x] `KB-mcp-platform/` (NEW skill) — trifecta What-half
- [x] `KB-mcp-design/` (NEW skill) — trifecta How-half
- [x] `auditing-mcp/` augmentation — 10 new rule families (OP-1..OP-10) **plus family graduation per ADR-0042** (frontmatter `family:` field changes; body gains `## Sub-skill family` section)
- [x] `auditing-cc-configs/SKILL.md` — family list (lines 144–153) drops `auditing-mcp` row per ADR-0042
- [x] `auditing-shared/SKILL.md` — description updated to list `auditing-mcp` as a now-graduated consumer per ADR-0042
- [x] `.claude/runtime/mcp-events.jsonl` schema (NEW; gitignored; ADR-0037)
- [x] `.devcontainer/devcontainer.json` — Features block additions (Node 20 LTS pin; Go); containerEnv updates for three Codespaces secrets
- [x] `.devcontainer/postCreate.sh` (NEW) — idempotent install; sentinel-guarded with binary-presence check (covers 5 OSS-local servers; Context7/Exa are remote HTTP, no install)
- [x] `.devcontainer/postStart.sh` (NEW) — readiness probe writing `readiness_probe` records to `mcp-events.jsonl` (7 records per postStart cycle, per Gate-4 OI-1 closure)
- [x] `.devcontainer/install/terraform-mcp.sh` (NEW) — wget + SHA256 + GPG verify
- [x] `.devcontainer/lib/mcp-ping.sh` + `mcp-auth-probe.sh` (NEW) — probe helpers
- [x] `.devcontainer/versions.env` (NEW) — per-server pin table (5 OSS-local servers)
- [x] Orchestrator phase-validator update at Gate 6 — `auditing-mcp` non-zero exit is gate-blocking per ADR-0043

#### Non-Scope (Explicitly not changing)

- [x] No Dockerfile changes (ADR-0041 codifies)
- [x] No CI/CD layer changes (PRD Won't-Have)
- [x] No IaC layer changes (PRD Won't-Have)
- [x] No changes to pipeline stages, gates, or orchestrator topology beyond the Gate-6 phase-validator hard-gate wiring (per ADR-0043)
- [x] No `model:`/`effort:`/`skills:` field changes on any agent (cc-design Principle 9)
- [x] Preserve C-0445 zero-`mcp__` invariant for the 28 non-consumer agents
- [x] No new CLAUDE.md (cc-design — knowledge lives in the two new skills, model-invocable)
- [x] No new `.claude/rules/` (cc-design)
- [x] No new hooks (cc-design Principle 3)
- [x] No plugin packaging in this feature (Q-CC-7 deferred to follow-up)
- [x] No codebase-memory-mcp fallback registration in `.mcp.json` (per Gate-4 OI-1 closure; ADR-0007 policy remains in force at the project level but no fallback wiring lands in this feature)
- [x] No reconsideration of other auditing-* family-graduation decisions (per ADR-0042 Decision item 5 — deferred to future `auditing-family-structure-review-r1` pipeline run per `Issues/proposal-auditing-family-graduation-review.md`)

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

- [x] **`auditing-mcp` skill (augmented; graduated family-coordinator per ADR-0042)** — Enforces: 10 rule families (OP-1 env-block coverage; OP-2 consumer-mapping; OP-3 zero-`mcp__` preservation; OP-4 primary/fallback prose; OP-5 lifecycle completeness; OP-6 runtime log redaction; OP-7 trifecta consistency; OP-8 GitNexus-specific; OP-9 URL-credential rejection; OP-10 argv-leakage absence) — Config: `.claude/skills/auditing-mcp/` — Covers: `.mcp.json`, all 36 agent files, `mcp-events.jsonl`, devcontainer.json — Status: `adopted`. **Hard gate at Gate 6 per ADR-0043.**
- [x] **Per-server probe (FR-4)** — Enforces: every registered server responds to a real call — Config: each server's documented probe (JSON-RPC ping + Context7/Exa supplementary auth probe gated on env flag per D-8) — Covers: 7 `.mcp.json` entries — Status: `adopted`.
- [x] **Lifecycle health-check (FR-8)** — Enforces: surface health at postCreate / postStart / on-demand — Config: `postStart.sh` writes to `mcp-events.jsonl` — Covers: all 7 registered servers (per Gate-4 OI-1 closure) — Status: `adopted`.
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
- `auditing-mcp` currently sits inside the `auditing-cc-configs` family (line-30 frontmatter declaration); per Gate-4 OI-2 closure (ADR-0042), it graduates to its own family-coordinator.

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
- **Reliability**: per-server probe pass-rate 100% at acceptance; idempotent rebuild; no false-positive healthy reports; no silent runtime failures; ADR-0007 fallback policy preserved at the project level but not provisioned in this feature's `.mcp.json` per Gate-4 OI-1 closure.
- **Maintainability**: W/H/A trifecta provides long-tail maintainer interface; augmented auditing-mcp is the safety-net (hard gate per ADR-0043).
- **Operability**: every MCP failure reaches a named operator surface with named server, failure layer, remediation pointer; runtime log redacts credentials per ADR-0039.

## Acceptance Criteria (AC) - EARS Format

The Blueprint inherits PRD AC-FR-* / AC-NFR-* clauses and refines them with per-layer AC-CC-* (Claude Code) and AC-CS-* (Codespaces) contributions. Two additional ACs were authored in this composition: **AC-X-1** addresses the secret-absent failure (resolves I-DR-CS-003); **AC-X-2** codifies the inventory disposition (resolves I-DR-001 / Q-CC-6). **At v3, AC-X-2 and the dependent `readiness_probe` counts flip from 8 to 7 per Gate-4 OI-1 closure (codebase-memory-mcp fallback dropped from inventory).**

### Functional ACs

#### FR-1 — Seven named MCP servers installed and registered (always-on) — Layer: claude-code + codespaces

- [ ] **AC-FR-1-a (PRD)**: When the Codespace finishes its build and lifecycle setup, the system shall have every one of the seven named MCP servers listed by `claude mcp list` as *connected*.
- [ ] **AC-FR-1-b (PRD)**: When the operator runs the agreed per-server probe, the system shall return a successful response from every one of the seven servers.
- [ ] **AC-FR-1-c (PRD)**: If any of the seven servers is missing, not registered, or not responding at probe time, then the system shall surface a clear failure in the probe tool's output naming the specific server and the layer of failure.
- [ ] **AC-CC-1 (CC-refined)**: When the operator runs `claude mcp list` after `postCreate` completes on a fresh build, the system shall list exactly the **seven named servers** (`serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`, `context7`, `exa`) — seven `mcpServers` entries total — all in `connected` status. (See **AC-X-2** for the inventory-count convention; per Gate-4 OI-1 closure no fallback entry is registered.)

#### FR-2 + FR-3 — Tool wiring + repo-readability — Layer: claude-code

- [ ] **AC-FR-2-a (PRD)**: When the operator inspects each affected `.claude/agents/*.md`, the system shall show the appropriate MCP tool entries present in the `tools:` allowlist.
- [ ] **AC-FR-2-b (PRD)**: When the operator runs a stage whose sub-agent was wired to a new MCP capability, the system shall make the corresponding tool callable from inside that sub-agent.
- [ ] **AC-CC-2 (CC-refined)**: When the operator inspects each of the 8 affected agent files, the system shall show the prescribed `mcp__<server>__<tool>` entries (per the consumer-mapping table in §Design / Claude Code / Project Filesystem Design) and no others.
- [ ] **AC-CC-3 (CC-invariant)**: When the operator inspects the 28 non-consumer agent files, the system shall show zero `mcp__` entries. (Preserves C-0445.)

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

- [ ] **AC-FR-8-a (PRD)**: postCreate completes; consolidated health-check output for all seven servers.
- [ ] **AC-FR-8-b (PRD)**: postStart re-runs the check.
- [ ] **AC-FR-8-c (PRD)**: postAttach surfaces the most recent result (or triggers a fresh check beyond a staleness threshold — deferred to plan-author as part of UI-10 refinement).
- [ ] **AC-FR-8-d (PRD)**: Failure at any boundary surfaces server name, failing layer, remediation hint into `KB-mcp-platform`.
- [ ] **AC-FR-8-e (PRD)**: Operator-invokable on demand.
- [ ] **AC-CS-4 (CS-contributed)**: When `postStartCommand` runs, the system shall append exactly one `readiness_probe` JSONL record per registered server to `.claude/runtime/mcp-events.jsonl` (**seven records on a healthy run per AC-CC-1 + AC-X-2; per Gate-4 OI-1 closure**).
- [ ] **AC-CS-5 (CS-contributed)**: If one or more probes returns `fail`, the system shall write the JSONL records, emit a stderr banner naming the degraded count, AND exit 0 (warn-and-continue).
- [ ] **AC-CC-6 (CC-refined)**: After a postStart cycle, `.claude/runtime/mcp-events.jsonl` contains **seven `readiness_probe` records** (one per registered server, per Gate-4 OI-1 closure) with `result: pass` or `result: fail` + `failure_layer`.

#### FR-9 — Runtime MCP failures surface — Layer: claude-code

- [ ] **AC-FR-9-a (PRD)**: Mid-run server failure surfaces structured failure record at the next operator-visible surface.
- [ ] **AC-FR-9-b (PRD)**: Tool-level error response includes server name, tool name, error response.
- [ ] **AC-FR-9-c (PRD)**: Healthy→unhealthy transition visible in runtime log surface with timestamp + triggering event.
- [ ] **AC-FR-9-d (PRD)**: No silent fallback. (Note: per Gate-4 OI-1 closure, no GitNexus → codebase-memory-mcp fallback transition is provisioned in this feature; the ADR-0007 policy remains in force at the project level for any future feature that registers a fallback. ADR-0037's `primary_degraded` event-type remains in the schema and the OP-4 audit rule remains in force as a forward-looking provision; the event-type is currently not exercised in this feature's runtime.)
- [ ] **AC-CC-7 (CC-refined)**: If a primary→fallback transition occurs at runtime in any future feature that provisions a fallback, the system shall append a `primary_degraded` record to `.claude/runtime/mcp-events.jsonl` AND surface a stderr banner per ADR-0037; both shall be operator-readable. (Schema-level provision; no runtime fires in this feature per Gate-4 OI-1 closure.)

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
- [ ] **AC-CC-5 (CC-refined)**: When the augmented `auditing-mcp` skill (rule families OP-1 through OP-10) runs against the repo after Gate 6, the system shall report zero BLOCKER findings. **(Hard gate per ADR-0043: any BLOCKER halts the orchestrator at Gate 6; remediation + re-run is the required path.)**
- [ ] **AC-CC-8 (CC-trifecta-structure)**: Both new skills conform to trifecta structural conventions: `name:` lowercase-hyphenated; `description` ends with sister-cross-reference; design half has exactly two reference files (`patterns-and-anti-patterns.md` + `principles.md`) and no `assets/`.
- [ ] **AC-CC-9 (CC-cross-reference)**: `KB-mcp-platform/references/gitnexus-and-fallback.md` names GitNexus as primary and cites ADR-0007 v2.2.0; documents the codebase-memory-mcp fallback policy at the project level even though this feature does not provision it (per Gate-4 OI-1 closure). The `mcp-events.jsonl` `primary_degraded` schema in `KB-mcp-design/references/principles.md` is preserved as a forward-looking provision.
- [ ] **AC-CC-10 (CC-family-graduation; NEW at v3)**: After this feature ships, `auditing-mcp/SKILL.md` carries `family: auditing-mcp` in frontmatter and a `## Sub-skill family` section in the body; `auditing-cc-configs/SKILL.md` lines 144–155 area no longer lists `auditing-mcp` as a sub-skill; `auditing-shared/SKILL.md` description lists `auditing-mcp` as a graduated-family consumer. Per ADR-0042.

### Cross-Layer / Operational ACs

- [ ] **AC-NFR-1-a (PRD)**: Cold-cache build + lifecycle setup completes within ~10 min on 4 vCPU / 8 GB host.
- [ ] **AC-NFR-1-b (PRD)**: Warm-cache rebuild reuses cached layers; no re-download / re-compile of MCP server binaries.
- [ ] **AC-NFR-2-a (PRD-inherited; enumerated per reviewer I-DR-BP-005)**: When `git grep` runs over the repo at any commit, the system shall not surface any literal credential value (no secret values committed) — enforced by AC-CC-4 grep + augmented `auditing-mcp` OP-6 / OP-9 / OP-10 + ADR-0039 redact-at-source posture.
- [ ] **AC-NFR-2-c (PRD-inherited; enumerated per reviewer I-DR-BP-005)**: When the augmented `auditing-mcp` runs end-to-end at Gate 6, the system shall report zero BLOCKER findings. **Any BLOCKER finding halts the orchestrator at Gate 6 (hard gate per OI-3 / ADR-0043 closure).**
- [ ] **AC-NFR-2-d (PRD-inherited; enumerated per reviewer I-DR-BP-005)**: When postStart or any in-product fallback-detection code-site writes to `mcp-events.jsonl`, the system shall apply the redaction filter (env-block allowlist + HTTP-headers allowlist from `.mcp.json`) before write — per ADR-0039 redact-at-source SSOT; default-fail-closed if allowlist is empty.
- [ ] **AC-CS-1 (CS-features)**: After Feature install, Node 20 and Go are on PATH; `node --version` returns `v20.*` and `go version` returns non-error.
- [ ] **AC-CS-2 (CS-idempotence)**: Re-invoking `postCreate.sh` without intervening sentinel deletion shall observe each per-server install as already-satisfied (sentinel-present AND binary-present); the run completes in well under cold-cache time. (Per ADR-0041 sentinel naming = `<server>@<version>.installed` + binary-presence check.)
- [ ] **AC-CS-3 (CS-fail-fast)**: If any per-server install step fails inside `postCreate.sh`, the system shall surface the failing server name on the operator's terminal and shall exit non-zero, halting the lifecycle.
- [ ] **AC-CS-7 (CS-ports)**: `forwardPorts: []`; no port forwarded by default.
- [ ] **AC-CS-8 (CS-time)**: Cold-cache build within ~10 min; warm-cache within ~2 min (NFR-1).
- [ ] **AC-CS-9 (CS-GitNexus)**: `postCreate.sh` invokes GitNexus with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` (the env-var is exported BEFORE the install runs) and fails postCreate if the smoke-test (`--help`) fails (C-0388/C-0411). **Install mechanism: `npm install -g gitnexus@${GITNEXUS_TAG}` (persistent install) per cycle-3 reconciliation D-3.2 F2; smoke-test uses `npx -y gitnexus@${GITNEXUS_TAG} --help` for ephemeral verify.** **AC semantic intent is unchanged from v3.0.0**: cold-cache build does NOT require a C++ toolchain (`cc`/`g++`/`cargo`) — the env-var suppresses npm's vendored tree-sitter grammar build that would otherwise pull in the toolchain. The verify-at-execution check (T0.4) asserts: no C++ toolchain in install-process tree — install-command-agnostic.
- [ ] **AC-X-2 (revised at v3 per Gate-4 OI-1 closure; resolves I-DR-001 / Q-CC-6)**: The system shall treat the closed list of seven PRD-named servers (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, GitNexus, Context7, Exa) as the **canonical inventory**. The reconciliation: the PRD count of "seven named servers" matches `.mcp.json`'s entry count exactly (seven `mcpServers` entries; no fallback entry); per Gate-4 OI-1 closure the codebase-memory-mcp fallback is **not** registered in this feature's inventory. The augmented `auditing-mcp` rules OP-2 / OP-3 / OP-8 consequently no longer need to special-case codebase-memory-mcp by name; OP-4 retains the forward-looking primary/fallback prose audit rule (per ADR-0037 schema-level provision).

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | New | `.mcp.json` (repo root) | Project-scoped MCP registration; 7 mcpServers entries (per Gate-4 OI-1 closure; no fallback entry) |
| Claude Code | Existing/modified | `.claude/agents/*.md` (8 files) | Add `mcp__<server>__<tool>` to `tools:` arrays |
| Claude Code | New | `.claude/skills/KB-mcp-platform/` | Trifecta What-half |
| Claude Code | New | `.claude/skills/KB-mcp-design/` | Trifecta How-half |
| Claude Code | Existing/augmented | `.claude/skills/auditing-mcp/` | 10 new rule families OP-1..OP-10 + scripts + **family-graduation per ADR-0042 (frontmatter family: field + Sub-skill family body section)** |
| Claude Code | Existing/modified | `.claude/skills/auditing-cc-configs/SKILL.md` | **NEW at v3:** Family list (lines 144–155) drops `auditing-mcp` row per ADR-0042 |
| Claude Code | Existing/modified | `.claude/skills/auditing-shared/SKILL.md` | **NEW at v3:** Description gains `auditing-mcp` as a graduated-family consumer per ADR-0042 |
| Claude Code | New | `.claude/runtime/mcp-events.jsonl` | Cross-server event surface; gitignored; bootstrapped by postCreate |
| Claude Code | New | `.gitignore` (modified) | Adds `.claude/runtime/mcp-events.jsonl` |
| Codespaces | Existing/modified | `.devcontainer/devcontainer.json` | Features additions (Node 20 LTS; Go); containerEnv updates |
| Codespaces | New | `.devcontainer/postCreate.sh` | Idempotent install with version-pinned sentinels (5 OSS-local servers) |
| Codespaces | New | `.devcontainer/postStart.sh` | Readiness probe writer (7 records per cycle) |
| Codespaces | New | `.devcontainer/install/terraform-mcp.sh` | wget + SHA256 + GPG verify |
| Codespaces | New | `.devcontainer/lib/mcp-ping.sh` | Probe helper |
| Codespaces | New | `.devcontainer/lib/mcp-auth-probe.sh` | Auth-probe helper for Context7/Exa |
| Codespaces | New | `.devcontainer/versions.env` | Per-server pin table (5 OSS-local servers) |

### Integration Points

- **Integration Target:** Claude Code session consumes `.mcp.json`; sub-agents consume `tools:` allowlists; operators read `.claude/runtime/mcp-events.jsonl` via documented tail command; augmented `auditing-mcp` validates static config + runtime events; orchestrator Gate 6 invokes `auditing-mcp` as hard gate per ADR-0043.
- **Invocation Method:** lifecycle-driven (postCreate / postStart); operator-on-demand (audit script + tail command); session-startup (Claude Code reads `.mcp.json` on session creation); orchestrator-driven (Gate 6 phase-validator).

### Code Inspection Evidence

| File/Function | Relevance |
|---------------|-----------|
| `.devcontainer/devcontainer.json` | Existing Features block; this feature adds 2 entries, modifies 1 pin, preserves 3 |
| `.devcontainer/Dockerfile` | Existing baseline; **NOT modified** per ADR-0041 (E-0081 historical fragility) |
| `.claude/skills/KB-cc-platform/`, `KB-cc-design/`, `auditing-cc-configs/` | Trifecta exemplar 1; new skills mirror verbatim per D-0010. **NEW at v3:** the family enumeration block at lines 144–155 is updated by this feature per ADR-0042. |
| `.claude/skills/KB-codespaces-platform/`, `KB-codespaces-design/`, `auditing-codespaces/` | Trifecta exemplar 2 (auditing-codespaces is STUB per ADR-0033) |
| `.claude/skills/KB-github-actions-platform/`, `KB-github-actions-design/`, `auditing-github-actions/` | Trifecta exemplar 3 |
| `.claude/skills/auditing-mcp/SKILL.md` (line 30) | Current family-declaration: `auditing-cc-configs` family. **Per Gate-4 OI-2 closure / ADR-0042, this flips to `auditing-mcp` (own family-coordinator).** |
| `.claude/skills/auditing-shared/SKILL.md` | Description currently lists four consumers; **gains `auditing-mcp` as a graduated-family consumer per ADR-0042**. |
| `.claude/skills/KB-codebase-research/SKILL.md` | Names GitNexus primary / codebase-memory-mcp fallback per ADR-0007 v2.2.0 |
| `.claude/agents/discovery-codebase-researcher.md` (lines 3, 20, 29, 156) | Four prose references to primary/fallback — preserved verbatim; OP-4 audit rule (ADR-0037) makes this machine-checkable |
| `adrs/ADR-0007-code-graph-mcp-selection.md` vs `adrs-migrated/...` | Currently lives in `adrs-migrated/`; ADR-0038 relocates per ADR-0036 |
| `.claude/agents/*.md` (36 files) | C-0445 grep-verified zero `mcp__` entries; this feature adds entries to 8, preserves 28 |

### Fact Disposition Table

One row per codebase-analysis focusArea. The Disposition column states this Blueprint's commitment relative to existing behavior.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---------|------------|-------------|-----------|----------|
| C-0445 | Zero `mcp__` usage across all 36 sub-agents | preserve (for 28 of 36) | Least-privilege per cc-design Principle 5. Math: 6-agent base consumer-mapping (design-api, design-cicd, design-iac, discovery-external-researcher, discovery-codebase-researcher, review-architecture-auditor) + 5-agent ADR-0040 Serena allowlist (design-cicd, discovery-codebase-researcher, review-architecture-auditor, design-claude-code, design-codespaces) − 3 overlap = **8 unique touched agents**; 28 untouched. | grep-verified, codebase-analysis Batch 5 |
| C-0462 | `.mcp.json` absent at repo root | transform | Feature creates the file per ADR-0037 / ADR-0039 schema (env-block SSOT). **At v3, 7 entries — no fallback — per Gate-4 OI-1 closure.** | grep-verified |
| C-0455 / C-0456 / C-0457 | Three W/H/A trifectas exist (CC, Codespaces, GHA) | preserve (as exemplars) | KB-mcp-platform + KB-mcp-design mirror the convention verbatim per D-0010 / cc-design §Skill patterns. | direct inspection |
| C-0458 | MCP trifecta currently audit-only (auditing-mcp exists; KB-mcp-* absent) | transform | FR-11 completes the trifecta. | grep-verified |
| C-0441 / C-0495 | ADR-0018 v1.0.0 vs KB v1.1.0 drift | transform | ADR-0038 bumps ADR-0018 to v1.1.0 (this Blueprint authors). | direct inspection |
| C-0442 / C-0497 / C-0498 | ADR-0007 in `adrs-migrated/` not `adrs/` | transform | ADR-0038 relocates per ADR-0036. | direct inspection |
| C-0447 / C-0448 | GitNexus primary / codebase-memory-mcp fallback policy per ADR-0007 v2.2.0 | preserve (policy at project level; not provisioned in this feature) | Per Gate-4 OI-1 closure, codebase-memory-mcp fallback is dropped from this feature's `.mcp.json` inventory. ADR-0007 policy remains in force at the project level for any future feature that registers a fallback. | ADR-0007 v2.2.0 |
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
| C-0349 | F5.4 NO CONSENSUS for primary→fallback transition surfacing | transform | ADR-0037 establishes the project's novel convention; schema-level provision is preserved even though this feature does not exercise it per Gate-4 OI-1 closure. | verbatim |
| E-0081 | Dockerfile-Yarn-key historical fragility | preserve (as constraint) | ADR-0041 honors "no new Dockerfile work." | codebase-analysis |
| C-0463 | Existing Yarn-list workaround in Dockerfile | preserve | Not touched. | direct inspection |
| C-0040 / C-0042 / E-0098 | Serena v1.3.0 base_modes→added_modes breaking change | transform | ADR-0040 pins pre-v1.3.0. | research note T-001 |
| C-0073 | mcp-openapi-schema 0.0.1 14-month static | preserve (with verify-at-execution) | Plan-author confirms at install time; pin form is exact-tag. | research note T-002 |
| C-0133 / C-0153 | actionlint-mcp no tagged releases | preserve (with verify-at-execution) | Plan-author selects commit SHA at install time. | research note T-003 |
| C-0157 / C-0190 / C-0193 | Terraform MCP releases.hashicorp.com with SHA256 + GPG | transform | ADR-0041 codifies binary-fetch + verify path. | research note T-004 |
| C-0037 | Context7 v3.0.0 exposes a two-tool surface (`resolve-library-id`, `query-docs`); stable across v1.0.x → v2.x → v3.0.0 | preserve (with verify-at-execution §H-5) | **Corrected at cycle-3 reconciliation (D-3.2 F3).** The prior framing "v1.2.0 ReplaceContentTool replaces ReplaceRegexTool" was wrong on two counts: (1) Context7 v1.2.0 never existed (1.x capped at 1.0.30 per dispatch log npm probe); (2) `ReplaceContentTool` was a contamination from Serena's v1.2.0 CHANGELOG, not a Context7 tool. The verified v3.0.0 tool surface is the two long-standing tools. Allowlist entries `mcp__context7__resolve-library-id` and `mcp__context7__query-docs` are correct as-is. | research note T-005 v2.0.0 (cycle-3 refresh) + dispatch log npm probe |
| C-0205 | Context7 `--api-key` CLI flag form | transform | Rejected by ADR-0039 / rule OP-10. | research note T-005 |
| C-0444 | Universal-frontmatter calibration (medium-confidence) | preserve (as constraint) | Constraint #14; plan-author validates per-agent before editing. | codebase-analysis |
| C-0460 | `auditing-mcp` family-declaration at line 30 (`auditing-cc-configs`) | **transform — graduate per Path A** | **Composer resolution per Gate-4 user override (OI-2): auditing-mcp becomes its own family-coordinator per ADR-0042. The line-30 frontmatter `family:` field changes to `auditing-mcp`; `auditing-cc-configs/SKILL.md` family list is updated.** | direct inspection |
| C-0471 / C-0535 | ADR-0020 skill naming with lone `auditing-cc-configs` deviation | preserve | Both new skills follow standard naming; auditing-mcp's bare-topic name is correct. | direct inspection |
| C-0478 / C-0479 / C-0480 / C-0481 | Trifecta structural skeleton (design half = 2 refs, no assets; platform half = many refs + assets/templates/) | preserve | KB-mcp-design conforms (2 refs, no assets); KB-mcp-platform conforms (7 refs + assets/templates/). | codebase-analysis |
| C-0482 / C-0483 / C-0528 / C-0537 | Sister-cross-reference convention; body-prose family membership; ADR-0030 pedagogical_sections | preserve | Both new skills declare per the conventions. | codebase-analysis |
| C-0484 (file-counts) | 634 total / 468 markdown | preserve | Drives ADR-0040 narrowing. | single-sourced-medium |
| C-0499 | auditing-codespaces STUB per ADR-0033 | preserve | Augmented auditing-mcp owns lifecycle audit (OP-5) until stub is filled. design-codespaces's ADR-0040 Serena entry is forward-looking on this stub becoming real (see OI-6). | direct inspection |
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
    - ".mcp.json (NEW; 7 entries per Gate-4 OI-1 closure — no fallback)"
    - ".claude/agents/design-api.md, design-cicd.md, design-iac.md, discovery-external-researcher.md, discovery-codebase-researcher.md, review-architecture-auditor.md, design-claude-code.md, design-codespaces.md (mcp__ tools allowlist + Serena narrowing). Note: design-claude-code.md is the canonical filename; the agent's frontmatter `name:` field is `design-cc` per the Path-A reserved-word workaround (the validator rejects names containing 'claude')."
    - ".claude/skills/KB-mcp-platform/ (NEW)"
    - ".claude/skills/KB-mcp-design/ (NEW)"
    - ".claude/skills/auditing-mcp/ (10 augmentation rules; 6 new scripts; 2 extended; family graduation per ADR-0042 — frontmatter family: field + Sub-skill family body section)"
    - ".claude/skills/auditing-cc-configs/SKILL.md (NEW v3 touch — family list at lines 144–155 drops auditing-mcp row per ADR-0042)"
    - ".claude/skills/auditing-shared/SKILL.md (NEW v3 touch — description gains auditing-mcp as graduated-family consumer per ADR-0042)"
    - ".claude/runtime/mcp-events.jsonl (NEW; gitignored)"
    - ".gitignore (modified)"
    - "Orchestrator phase-validator at Gate 6 (NEW v3 — auditing-mcp non-zero exit is gate-blocking per ADR-0043)"
  codespaces:
    - ".devcontainer/devcontainer.json (Features additions + containerEnv updates)"
    - ".devcontainer/postCreate.sh (NEW; covers 5 OSS-local servers)"
    - ".devcontainer/postStart.sh (NEW; 7 probe records per cycle per Gate-4 OI-1 closure)"
    - ".devcontainer/install/terraform-mcp.sh (NEW)"
    - ".devcontainer/lib/mcp-ping.sh (NEW)"
    - ".devcontainer/lib/mcp-auth-probe.sh (NEW)"
    - ".devcontainer/versions.env (NEW; 5 OSS-local servers)"
Indirect Impact:
  - "Seven new ADRs ship: ADR-0037..ADR-0041 (from v1/v2) + ADR-0042 + ADR-0043 (Gate-4 v3 — auditing-mcp family graduation + hard-gate). ADR-0007 relocates from adrs-migrated/ to adrs/ per ADR-0036."
  - "ADR-0018 v1.0.0 superseded by ADR-0038 v1.1.0 (append-only per ADR-0005). Two downstream KB/agent consumers update to v1.1.0."
  - "All 36 sub-agents see new .mcp.json on session start; tool schemas deferred until invoked (cc-design Principle 1)."
  - "Cold-cache build time grows from current baseline by ~2–4 min (postCreate per-server installs)."
  - "Orchestrator pipeline gains a hard-gate dependency at Gate 6 on auditing-mcp (per ADR-0043); operator workflow on BLOCKER finding is remediate + re-run."
  - "auditing-cc-configs family becomes 5 sub-skills (was 6); auditing-mcp becomes its own family-coordinator with 0 sub-skills initially (per ADR-0042)."
No Ripple Effect:
  - "The 28 non-consumer agents' tools: arrays are NOT modified (C-0445 invariant preserved)."
  - "No model:/effort:/skills: changes on any agent (cc-design Principle 9 honored)."
  - "Pipeline stages, gates topology (Gate 6 presence) unchanged — only the Gate-6 phase-validator semantics gain hard-gate per ADR-0043."
  - "No Dockerfile changes (ADR-0041 codifies)."
  - "No port forwarding (codespaces-design Q-CS / AC-CS-7)."
  - "Other auditing-* siblings (auditing-skills, auditing-context-files, auditing-subagents, auditing-hooks, auditing-settings) remain in the auditing-cc-configs family; ADR-0042 sets a precedent but does not graduate them. The broader question is deferred to a future pipeline run per Issues/proposal-auditing-family-graduation-review.md."
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|----------|-----|--------------------|--------------------|
| ADR-0018 v1.0.0 schema | ADR-0038 v1.1.0 schema (additive `blast_radius` field) | No (additive; v1.0.0 outputs remain valid) | Forward-compatible — readers tolerant of missing `blast_radius` per "additive schema evolution" |
| ADR-0007 at `adrs-migrated/` | ADR-0007 at `adrs/` (canonical) | No (file move, content preserved) | Relocate per ADR-0036; optional redirect stub at `adrs-migrated/` |
| `.claude/agents/*.md` with zero `mcp__` entries (36 of 36) | 8 of 36 agents gain `mcp__<server>__<tool>` entries; 28 preserved | Yes (additive `tools:` array edits) | OP-2 / OP-3 audit rules validate the consumer-mapping ↔ live-state alignment |
| `auditing-mcp` description naming sister halves that didn't exist | `auditing-mcp` description names KB-mcp-platform + KB-mcp-design; **plus the graduated family-coordinator pattern per ADR-0042** | No (description update + frontmatter family: field flip) | Skill description update per the canonical sister-cross-reference convention (C-0482); family: frontmatter field flips from `auditing-cc-configs` to `auditing-mcp` |
| `auditing-mcp` member of `auditing-cc-configs` family (line-30 frontmatter; line-148 in auditing-cc-configs/SKILL.md list) | `auditing-mcp` family-coordinator in its own right (per ADR-0042); auditing-cc-configs family list drops the row | Yes (frontmatter field + body-section addition + family-list pruning + auditing-shared cross-ref expansion) | One-way migration; ADR-0042 codifies the precedent; auditing-cc-configs/SKILL.md inline-documents the graduation with cross-reference |
| `.claude/agents/discovery-codebase-researcher.md` (prose-only primary/fallback at lines 3/20/29/156) | Same prose preserved; backed by OP-4 audit rule per ADR-0037 (forward-looking provision; no fallback exercised in this feature per Gate-4 OI-1 closure) | No | OP-4 audit rule (`/primary.*fallback/` grep on agent body) makes the prose machine-checkable |
| Sentinel naming (codespaces-design draft used unversioned) | Sentinel naming = `<server>@<version>.installed` per ADR-0041 | Yes (postCreate.sh outline reconciled) | Single canonical form across Persistence Boundaries and postCreate.sh body |
| `.mcp.json` "7 servers" (PRD count) | `.mcp.json` 7 entries exactly — matches PRD inventory; no fallback entry per Gate-4 OI-1 closure | No (count alignment) | AC-X-2 (v3-revised) codifies; auditing-mcp no longer special-cases codebase-memory-mcp by name |
| Orchestrator Gate 6 (advisory or unspecified gating for auditing-mcp) | Orchestrator Gate 6 (hard gate per ADR-0043 — auditing-mcp BLOCKER halts orchestrator) | Yes (phase-validator wiring) | Plan-author updates the Gate-6 phase-validator per ADR-0043 Implementation Guidance |

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
                 │   │  - .mcp.json (7 mcpServers entries;      │   │
                 │   │    env: block = redaction SSOT;          │   │
                 │   │    no fallback entry per Gate-4 OI-1)    │   │
                 │   │  - 8 agents w/ mcp__<svr>__<tool> tools  │   │
                 │   │    (28 agents preserved zero-mcp__)      │   │
                 │   │  - KB-mcp-platform/ (NEW; "What" half)   │   │
                 │   │  - KB-mcp-design/  (NEW; "How"  half)    │   │
                 │   │  - auditing-mcp/ (augmented; OP-1..10;   │   │
                 │   │    graduated family per ADR-0042;        │   │
                 │   │    hard-gate at Gate 6 per ADR-0043)     │   │
                 │   └──────────────────────────────────────────┘   │
                 │                │                                 │
                 │                ▼ MCP protocol (stdio / HTTP)    │
                 │   ┌──────────────────────────────────────────┐   │
                 │   │  MCP servers (7):                        │   │
                 │   │  - serena (stdio, narrowed per ADR-0040) │   │
                 │   │  - mcp-openapi-schema (stdio)            │   │
                 │   │  - actionlint-mcp (stdio)                │   │
                 │   │  - terraform-mcp (stdio)                 │   │
                 │   │  - gitnexus (stdio; ADR-0007 primary)    │   │
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
     - For each OSS-local server (serena, mcp-openapi-schema, actionlint-mcp,
       terraform-mcp, gitnexus):
         - Read pin from versions.env
         - check_installed(): sentinel-present AND binary-present? → skip
         - install_<server>(): perform install; GPG-verify for terraform-mcp
         - touch sentinel: <server>@<version>.installed
     - First-run verify: .devcontainer/postStart.sh --first-run (non-fatal)
6. postStartCommand: `.devcontainer/postStart.sh`
     - For each registered server (7 entries from .mcp.json per Gate-4 OI-1):
         - lib/mcp-ping.sh <server> <transport>
         - Append readiness_probe record to mcp-events.jsonl
     - If MCP_AUTH_PROBE=1: supplementary auth probes for Context7, Exa
     - Emit stderr banner: "[postStart] MCP readiness: N/7 healthy"
     - exit 0 (warn-and-continue per Q-CS-3 / AC-CS-5)
7. Operator runs Claude Code session:
     - .mcp.json loaded; 7 servers registered
     - Sub-agent dispatched; if agent's tools: contains mcp__<svr>__<tool>,
       the tool is callable; otherwise permission-denied by allowlist.
8. Runtime failure (e.g., GitNexus stdio process exits):
     - In-product fallback-detection code-site (per ADR-0037 Implementation
       Guidance — plan-author places) appends:
         a) structured_failure record (failure_class=transport)
     - Stderr banner: "[mcp:gitnexus] transport failure; see .claude/runtime/mcp-events.jsonl"
     - Pipeline operator decides next action; no codebase-memory-mcp fallback
       in this feature per Gate-4 OI-1 closure (ADR-0007 policy preserved at
       project level for future features that may register a fallback)
9. Operator inspects mcp-events.jsonl via documented tail command:
     - Reads structured records; all credentials redacted per ADR-0039
     - Remediation pointer in structured_failure record → KB-mcp-platform
       troubleshooting section
10. Orchestrator Gate 6 (Deliverable Packaging):
     - Invokes auditing-mcp/scripts/audit_mcp.py --with-runtime
     - Non-zero exit (BLOCKER finding) halts orchestrator per ADR-0043
     - Operator workflow: remediate + re-run + resume
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|-------------------|----------|-------------------|-------------------|------------------|-------------------|
| Claude Code session MCP host | session startup | (no MCP servers) | reads `.mcp.json`; loads 7 servers (per Gate-4 OI-1 closure) | natural via Claude Code's `.mcp.json` discovery | `claude mcp list` shows 7 connected |
| Sub-agent tool dispatch | per-agent `tools:` allowlist | zero `mcp__` entries | 8 agents gain entries per consumer-mapping | direct file edit | OP-2 audit + per-agent runtime invocation |
| Codespaces secrets → MCP | `.devcontainer/devcontainer.json` containerEnv | (no MCP secrets wired) | `containerEnv` exports 3 vars via `${localEnv:NAME}`; `.mcp.json` reads `${VAR}` | natural via env-var substitution | AC-CS-6 + AC-FR-5-a |
| Lifecycle health-check | postStartCommand | (no health-check) | runs `postStart.sh` ping for 7 servers | devcontainer lifecycle | AC-CS-4 + AC-CC-6 |
| Mid-run failure surfacing | in-product fallback-detection code-site | (no surface; silent) | appends to `mcp-events.jsonl` + stderr banner | per ADR-0037 | AC-CC-7 + OP-6 audit |
| `.mcp.json` ↔ agent allowlist consistency | augmented `auditing-mcp` | (no audit) | OP-2 / OP-3 rules | script-invokable | `auditing-mcp` zero-BLOCKER (AC-CC-5) |
| ADR-0018 schema consumers | `KB-codebase-research/SKILL.md` + `discovery-codebase-researcher.md` | refer to v1.1.0 by phrase | refer to v1.1.0 per ADR-0038 | direct file edit | grep for `schema_version: 1.1.0` |
| auditing-mcp family membership | `auditing-mcp/SKILL.md` frontmatter + `auditing-cc-configs/SKILL.md` sub-skill family enumeration | `auditing-cc-configs` family (line-30 frontmatter; line-148 list entry) | `auditing-mcp` family-coordinator (own family per ADR-0042); auditing-cc-configs family list drops the row | one-way migration per ADR-0042 Implementation Guidance | direct grep for `family: auditing-mcp` + frontmatter test + audit-rule check |
| auditing-shared cross-reference | `auditing-shared/SKILL.md` description (consumer list) | 4 consumers listed | 5 consumers listed (gains `auditing-mcp` as graduated-family consumer) | description edit | direct grep |
| Orchestrator Gate 6 phase-validator | orchestrator's Gate-6 step | (no auditing-mcp invocation or advisory) | invokes auditing-mcp; non-zero exit halts orchestrator (hard gate per ADR-0043) | phase-validator script update by plan-author | manual gate firing + operator workflow validation |

### Main Components

#### Component 1: `.mcp.json` (NEW)

- **Responsibility**: Project-scoped MCP server registry. Single source of truth for (a) which servers are registered, (b) their transport + command, (c) the redaction allowlist (env-block + HTTP headers per ADR-0039). Per Gate-4 OI-1 closure, contains exactly 7 entries (no fallback entry for codebase-memory-mcp).
- **Interface**: Claude Code reads at session start; augmented `auditing-mcp` reads as static config.
- **Dependencies**: Codespaces' `containerEnv` populates the env vars `${VAR}` substitutions resolve against; `postCreate.sh` installs the binaries the `command`/`args` fields reference.

#### Component 2: Per-agent `tools:` allowlist edits (8 agents)

- **Responsibility**: Wire MCP tool callability per agent per consumer-mapping. Preserve zero-`mcp__` for 28 non-consumers.
- **Interface**: Each agent's `tools:` array; OP-2 / OP-3 audit rules validate.
- **Dependencies**: `.mcp.json` (server names must match); ADR-0040 (Serena 5-agent list).

#### Component 3: `KB-mcp-platform/` (NEW skill)

- **Responsibility**: "What" half of W/H/A trifecta. MCP platform facts: transports, install paths, credential surfaces, lifecycle integration, `mcp-events.jsonl` schema usage, GitNexus + (schema-level, not provisioned in this feature) fallback.
- **Interface**: model-invocable per description match; `allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch`.
- **Dependencies**: ADR-0007 (GitNexus/codebase-memory-mcp policy — preserved at project level), ADR-0037 (event schema), ADR-0039 (redaction), ADR-0041 (install paths).

#### Component 4: `KB-mcp-design/` (NEW skill)

- **Responsibility**: "How" half of W/H/A trifecta. MCP design discipline: principles (incl. `mcp-events.jsonl` schema canonical home) + patterns and anti-patterns.
- **Interface**: model-invocable; `allowed-tools: Read, Grep, Glob` (design-half-slim).
- **Dependencies**: synthesis §5 (operational discipline), ADR-0037, ADR-0039, ADR-0040, ADR-0041.

#### Component 5: `auditing-mcp/` (augmented in place; graduated to own family per ADR-0042)

- **Responsibility**: 10 rule families: OP-1 env-block coverage; OP-2 consumer-mapping; OP-3 zero-`mcp__` preservation; OP-4 primary/fallback prose; OP-5 lifecycle completeness; OP-6 runtime log redaction; OP-7 trifecta consistency; OP-8 GitNexus-specific; OP-9 URL-credential rejection; OP-10 argv-leakage absence. **Graduated to its own family-coordinator per ADR-0042; hard-gates orchestrator at Gate 6 per ADR-0043.**
- **Interface**: `scripts/audit_mcp.py [--with-runtime]` entry point; severity BLOCKER/MAJOR/MINOR/NIT. Frontmatter `family: auditing-mcp` (was `auditing-cc-configs`); body gains `## Sub-skill family` section.
- **Dependencies**: `.mcp.json` (static-config audit), `.claude/runtime/mcp-events.jsonl` (runtime audit when `--with-runtime`), the seven Trifecta exemplar skills, ADR-0007 (for OP-8), ADR-0033 (auditing-codespaces STUB context), ADR-0031 (auditing-shared consumer cross-reference; updated per ADR-0042), ADR-0042 (own graduation), ADR-0043 (hard-gate policy).

#### Component 6: `.claude/runtime/mcp-events.jsonl` (NEW; gitignored)

- **Responsibility**: Durable cross-server event surface. Three event types: `primary_degraded`, `readiness_probe`, `structured_failure`. Per ADR-0037. In this feature's runtime, `readiness_probe` and `structured_failure` are exercised; `primary_degraded` remains a schema-level provision and is not exercised because no fallback is provisioned per Gate-4 OI-1 closure.
- **Interface**: append-only JSONL; writers = postStart.sh + in-product fallback-detection code-site; readers = operator (tail), augmented `auditing-mcp --with-runtime`.
- **Dependencies**: ADR-0037 (schema canonical), ADR-0039 (redaction integrity); schema home in `KB-mcp-design/references/principles.md`.

#### Component 7: `.devcontainer/postCreate.sh` (NEW)

- **Responsibility**: Idempotent install for 5 OSS-local servers (Context7/Exa are remote HTTP — no install). Sentinel-guarded + binary-presence-checked re-run. Fail-fast on per-server failure.
- **Interface**: invoked by devcontainer `postCreateCommand`; exit codes propagate.
- **Dependencies**: `versions.env` (per-server pins), `install/terraform-mcp.sh`, Go Feature (for `go install`), Node 20 Feature (for `npx`/`uvx`).

#### Component 8: `.devcontainer/postStart.sh` (NEW)

- **Responsibility**: Fast readiness probe (JSON-RPC ping) for all 7 registered servers (per Gate-4 OI-1 closure). Writes `readiness_probe` JSONL records. Warn-and-continue on probe failure.
- **Interface**: invoked by devcontainer `postStartCommand`; exit 0 always except infrastructure failure (per ADR-0041 Implementation Guidance on I-DR-CS-008).
- **Dependencies**: `lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`, ADR-0037 event schema, ADR-0039 redaction allowlist.

#### Component 9 (NEW v3): Orchestrator Gate-6 phase-validator wiring

- **Responsibility**: Invokes `auditing-mcp/scripts/audit_mcp.py --with-runtime` at Gate 6 (Deliverable Packaging); non-zero exit halts orchestrator per ADR-0043. Operator-resumable: remediate + re-run + resume.
- **Interface**: Plan-author authors the concrete phase-validator script per ADR-0043 Implementation Guidance.
- **Dependencies**: ADR-0043 (hard-gate policy); ADR-0042 (graduated family-coordinator status of auditing-mcp; gating asymmetry resolved); existing orchestrator Gate-6 step.

### Contract Definitions

The canonical schema for `.claude/runtime/mcp-events.jsonl` lives in `KB-mcp-design/references/principles.md` per ADR-0037. The full table (common fields + event-specific fields per event type) is reproduced verbatim from cc-design §`mcp-events.jsonl` schema and refined below to address I-DR-004 (bootstrap semantics).

**Bootstrap semantics (resolves I-DR-004; revised at v3 per Gate-4 OI-1 closure):** On postCreate, the file is `touch`-ed if absent (zero records present). On postStart, exactly N `readiness_probe` records are appended where N = the number of registered servers in `.mcp.json` (currently 7 per AC-X-2 — per Gate-4 OI-1 closure dropping the fallback entry). An absent file or zero records after postStart is an OP-5 BLOCKER. (Companion edit: ADR-0037 Implementation Guidance line 143 was updated at v2 from "seven readiness_probe records" to "eight", then reverted at v3 back to "seven" per Gate-4 OI-1 closure; ADR-0037 carries a Document History row recording the revert.)

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
  - "primary_degraded event-type is schema-level provision; not exercised in this feature per Gate-4 OI-1 closure (no fallback registered)"
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
      - postStart_complete (readiness records in mcp-events.jsonl; 7 records per Gate-4 OI-1 closure)
      - session_ready (Claude Code session live; .mcp.json loaded; 7 servers connected)
      - mcp_failure (one or more servers degraded; structured_failure records in mcp-events.jsonl)
      - mcp_recovered (operator fixes; primary restored)

State Transitions:
  fresh → features_ready (Features run)
  features_ready → postCreate_in_progress → postCreate_complete (postCreate.sh runs; fail-fast if any server fails)
  postCreate_complete → postStart_complete (postStart.sh runs; warn-and-continue on probe fail)
  postStart_complete → session_ready (Claude Code session starts)
  session_ready → mcp_failure (server exits or returns error)
  mcp_failure → mcp_recovered (operator fixes; no automatic fallback in this feature per Gate-4 OI-1 closure)
  mcp_recovered → session_ready (no separate state; mcp-events.jsonl retains the history)

System Invariants:
  - "No credential value in any committed file or any line of mcp-events.jsonl (ADR-0039 + AC-NFR-2-a + AC-CC-4)"
  - "28 of 36 agents always have zero mcp__ entries (C-0445)"
  - "Every primary→fallback transition (if any is provisioned in a future feature) is operator-visible in mcp-events.jsonl + stderr (ADR-0037 schema-level provision; not exercised in this feature)"
  - "Every registered server in .mcp.json has a corresponding postStart probe (OP-5)"
  - "Every env-var reference in .mcp.json appears in an env: block or documented HTTP header allowlist (OP-1)"
  - "Any BLOCKER finding from augmented auditing-mcp halts the orchestrator at Gate 6 (hard gate per ADR-0043)"
  - "auditing-mcp frontmatter family: field is `auditing-mcp` (own family-coordinator per ADR-0042); auditing-cc-configs/SKILL.md sub-skill family list does NOT list auditing-mcp"
```

---

### Claude Code / Project Filesystem Design

This subsection integrates the cc-design.md per-layer subsection by reference; the full content lives in `working/feature/devcontainer-mcp-provisioning-r1/cc-design.md`. Key reconciliations made in this Blueprint:

- **Q-CC-1 (family-coordinator)**: **Path A per ADR-0042 (Gate-4 v3 user override of composer's pre-decision Path B).** `auditing-mcp` graduates to its own family-coordinator. Its frontmatter `family:` field changes from `auditing-cc-configs` to `auditing-mcp`. The body gains a `## Sub-skill family` section (initially empty — coordinator pattern reserved for future MCP-audit sub-skills). `auditing-cc-configs/SKILL.md` family list at lines 144–155 drops the `auditing-mcp` row and inline-documents the graduation with cross-reference. `auditing-shared/SKILL.md` description gains `auditing-mcp` as a graduated-family consumer per ADR-0031 + ADR-0042. Follow-up question (other auditing-* siblings) is captured in `Issues/proposal-auditing-family-graduation-review.md`. **Rationale**: failure-domain distance (MCP servers + supply-chain + credentials vs `.claude/`-config correctness) plus structural symmetry with `auditing-github-actions` (de-facto graduated) and future `auditing-codespaces` stub-fill.
- **Q-CC-2 (.claude/runtime/ git-status)**: Option (a) per ADR-0037 — `.claude/runtime/` directory is committed via `.gitkeep`; `.claude/runtime/mcp-events.jsonl` is gitignored.
- **Q-CC-3 (Serena agent list)**: Resolved by ADR-0040 — 5 named agents (review-architecture-auditor, design-cc, design-cicd, design-codespaces, discovery-codebase-researcher).
- **Q-CC-4 (auditing-mcp dimension organization)**: Option (a) — expand existing dimensions. One source of truth; one audit skill; the new rules (OP-1..OP-10) extend the existing rubric.
- **Q-CC-5 (primary/fallback expression)**: prose-only with OP-4 audit rule per ADR-0037. No new structured frontmatter field. (Provision preserved at the schema level even though this feature does not exercise it.)
- **Q-CC-6 (codebase-memory-mcp inventory status)**: **Revised at v3 per Gate-4 OI-1 closure** — the codebase-memory-mcp fallback is **dropped** from this feature's inventory. `.mcp.json` carries exactly 7 entries matching the PRD count. AC-X-2 codifies. The auditing-mcp rules OP-2 / OP-3 / OP-8 no longer special-case codebase-memory-mcp by name. ADR-0007's primary/fallback policy is preserved at the project level for any future feature that registers a fallback.
- **Q-CC-7 (plugin packaging future)**: deferred to follow-up feature (not authored here).
- **Q-CC-8 (ADR-authorship list)**: Resolved — ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041 (from v2), plus ADR-0042 + ADR-0043 (NEW at v3) all authored.
- **Q-CC-9 (auditing-mcp Gate 6 status)**: **Resolved at v3 per Gate-4 OI-3 closure / ADR-0043 — hard gate.** Any BLOCKER finding from augmented `auditing-mcp` halts the orchestrator at Gate 6; no operator-bypass at the gate; remediation + re-run is the required path. AC-CC-5, AC-FR-11-c, and AC-NFR-2-c carry the "zero BLOCKER findings" bar with strict enforcement semantics.

#### Per-layer Review Findings — Absorbed Recommended-Severity Items (resolves reviewer I-DR-BP-003)

Three recommended-severity findings from `cc-design-review-issues.json` were silent in Blueprint v1 and are now acknowledged explicitly:

- **I-DR-003 (placeholder-convention unification)**: design-cc used `<PIN_TAG>` vs `<TBD-per-ADR-0007-v2.2.0>` in different `.mcp.json` sketch lines. Disposition: **deferred to plan-author** per D-11 verify-at-execution discipline. Canonical placeholder form going forward is `<PIN_TBD>` across `.mcp.json` and `versions.env`; plan-author normalizes at task time.
- **I-DR-005 (KB-mcp-platform pedagogical_sections justification tightening per ADR-0030)**: design-cc justifications passed the rules but were more generic than the KB-github-actions-platform precedent. Disposition: **deferred to plan-author** as part of KB-mcp-platform authoring (Implementation Plan step 3). Justifications must name the specific OP-rule and anti-pattern in each `pedagogical_sections` entry, matching the KB-github-actions-platform precedent.
- **I-DR-006 (jsonc-vs-json fence convention)**: design-cc sketched `.mcp.json` with jsonc fences but the project convention is `.json` with comments in surrounding prose. Disposition: **resolved inline** — `KB-mcp-platform/assets/templates/.mcp.json.example` uses `.json` (matching project convention); design-time sketches that need inline comments may use jsonc fences in surrounding prose with a caption disclaimer ("illustrative; production file is `.json`, comments live in prose").

#### Family-Graduation Structural Changes (NEW at v3 per ADR-0042)

Per Gate-4 OI-2 closure, `auditing-mcp` graduates to its own family-coordinator. The structural changes are:

1. **`auditing-mcp/SKILL.md` frontmatter** — `family:` field changes from `auditing-cc-configs` to `auditing-mcp`.
2. **`auditing-mcp/SKILL.md` body** — add a `## Sub-skill family` section (initially empty; coordinator pattern reserved). Body language per ADR-0042 Implementation Guidance.
3. **`auditing-cc-configs/SKILL.md` lines 144–155 area** — remove the `auditing-mcp` row from the sub-skill enumeration; update the lead-in "six sibling skills" to "five sibling skills"; add a graduation-history paragraph below the list with cross-reference to ADR-0042 and the precedent rationale (security-distinct failure domain).
4. **`auditing-shared/SKILL.md` description** — list `auditing-mcp` as a now-graduated consumer alongside the four existing consumers (`auditing-cc-configs, auditing-skills, auditing-subagents, auditing-context-files`), per ADR-0031 cross-reference convention + ADR-0042.
5. **Orchestrator singular→plural family handling** — project files that reference "the auditing family" (singular) need audit and update for plural handling. Plan-author audits and updates per ADR-0042 Implementation Guidance + `Issues/proposal-auditing-family-graduation-review.md` §3 item 6.
6. **Cross-file pair-check coverage migration** — if `auditing-cc-configs/references/cross-file-checks.md` (or similar) contains MCP-relevant cross-file rules, plan-author audits and may migrate to `auditing-mcp/` coverage list.

Canonical step list mirrors `Issues/proposal-auditing-family-graduation-review.md` §3 items 1–6, scoped here to the `auditing-mcp` graduation specifically.

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.mcp.json` (NEW) | MCP server registry (7 entries per Gate-4 OI-1 closure) | new |
| `.claude/agents/*.md` (8 files) | Sub-agent tool allowlists | modified (tools: arrays only) |
| `.claude/skills/KB-mcp-platform/` | Trifecta What half | new |
| `.claude/skills/KB-mcp-design/` | Trifecta How half | new |
| `.claude/skills/auditing-mcp/` | Trifecta Audit half | modified (augmentation; sister-cross-reference update; 10 rule families; **family graduation per ADR-0042**) |
| `.claude/skills/auditing-cc-configs/SKILL.md` | Sub-skill family enumeration (lines 144–155) | modified (NEW at v3 per ADR-0042 — drop auditing-mcp row + graduation-history paragraph) |
| `.claude/skills/auditing-shared/SKILL.md` | ADR-0031 cross-audit-module shared-utility home | modified (NEW at v3 per ADR-0042 — description gains auditing-mcp consumer) |
| `.claude/runtime/mcp-events.jsonl` | Cross-server event surface | new; gitignored |
| `.gitignore` | Add `.claude/runtime/mcp-events.jsonl` | modified |
| Orchestrator Gate-6 phase-validator | Gate 6 step | modified (NEW at v3 per ADR-0043 — auditing-mcp invocation; non-zero exit halts) |

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
| `kb-mcp-platform` | `.claude/skills/KB-mcp-platform/SKILL.md` | model-invocable on MCP-related descriptions | Transports, install paths, credential surfaces, lifecycle integration, mcp-events.jsonl schema usage, GitNexus + (project-level-only) fallback policy |
| `kb-mcp-design` | `.claude/skills/KB-mcp-design/SKILL.md` | model-invocable on MCP-design questions | Principles (incl. event schema canonical home); patterns + anti-patterns |
| `auditing-mcp` (augmented; graduated family-coordinator per ADR-0042) | `.claude/skills/auditing-mcp/SKILL.md` | model-invocable + script-invokable + orchestrator Gate-6 hard-gate invocation per ADR-0043 | 10 rule families: OP-1..OP-10 |

#### Sub-Agents

This feature does NOT create new sub-agents. It modifies 8 of 36 existing agents' `tools:` allowlists only. Math: **6-agent base consumer-mapping** (design-api, design-cicd, design-iac, discovery-external-researcher, discovery-codebase-researcher, review-architecture-auditor) + **5-agent ADR-0040 Serena allowlist** (design-cicd, discovery-codebase-researcher, review-architecture-auditor, design-claude-code, design-codespaces) − **3 overlap** (design-cicd, discovery-codebase-researcher, review-architecture-auditor) = **8 unique touched agents** with **28 untouched** preserving C-0445.

| Sub-Agent | New `mcp__` entries | Source |
|---|---|---|
| `design-api` | `mcp__mcp-openapi-schema__*` | C-0450 |
| `design-cicd` | `mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows`, `mcp__serena__*` | C-0144 + ADR-0040 |
| `design-iac` | `mcp__terraform-mcp__*` | C-0452 |
| `discovery-external-researcher` | `mcp__context7__resolve-library-id`, `mcp__context7__query-docs`, `mcp__exa__web_search_exa`, `mcp__exa__company_research_exa`, `mcp__exa__crawling_exa` | C-0453, C-0454 |
| `discovery-codebase-researcher` | `mcp__gitnexus__*`, `mcp__serena__*` | ADR-0007 v2.2.0 (codebase-memory-mcp fallback policy preserved at project level but not provisioned per Gate-4 OI-1 closure); ADR-0040 |
| `review-architecture-auditor` | `mcp__gitnexus__*`, `mcp__serena__*` | ADR-0007 v2.2.0 (same fallback-policy note as above); ADR-0040 |
| `design-cc` | `mcp__serena__*` | ADR-0040 (touches auditing-mcp/scripts/) |
| `design-codespaces` | `mcp__serena__*` | ADR-0040 (touches auditing-codespaces/scripts/ if/when ADR-0033 stub becomes real; forward-looking — see OI-6) |

Total touched agents: **8** (each row above is one unique agent; the table has 8 rows). The **28** untouched agents (36 − 8) preserve C-0445.

Note: per Gate-4 OI-1 closure, the `mcp__codebase-memory-mcp__*` allowlist entries previously present in `discovery-codebase-researcher` and `review-architecture-auditor` are dropped from this feature's scope (no codebase-memory-mcp registration in `.mcp.json`). ADR-0007's primary/fallback policy is preserved at the project level — should a future feature register the fallback, the allowlist additions would land in that feature's scope.

#### MCP Servers

| Server | Configuration | Tools Exposed | Auth Method |
|---|---|---|---|
| serena | `.mcp.json` stdio entry; `uvx --from git+https://github.com/oraios/serena@${SERENA_TAG}` | `mcp__serena__*` (narrowed to 5 agents per ADR-0040) | none |
| mcp-openapi-schema | stdio; `npx -y mcp-openapi-schema@0.0.1` | `mcp__mcp-openapi-schema__*` | none |
| actionlint-mcp | stdio; `actionlint-mcp` (installed via Go) | 2 tools | none |
| terraform-mcp | stdio; `terraform-mcp` (binary on PATH, GPG-verified per ADR-0041) | `mcp__terraform-mcp__*` | `TFE_TOKEN` (optional; local-only is no-auth) |
| gitnexus | stdio; `npx -y gitnexus@${GITNEXUS_TAG} mcp` (persistent install in postCreate is `npm install -g gitnexus@${GITNEXUS_TAG}`); `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` | `mcp__gitnexus__*` | none |
| context7 | HTTP; `https://mcp.context7.com/mcp` | 2 named tools | `CONTEXT7_API_KEY` header |
| exa | HTTP; `https://mcp.exa.ai/mcp` | 3 named tools | `x-api-key` header |

(Note: codebase-memory-mcp row removed at v3 per Gate-4 OI-1 closure. Total = 7 servers.)

#### File Naming & Layout Conventions Introduced

- **`.claude/runtime/` directory**: reserved for ephemeral runtime state. New: `mcp-events.jsonl` (gitignored) + `install-sentinels/<server>@<version>.installed` (the binary-presence-checked sentinels per ADR-0041). Enforcement: convention only + augmented `auditing-mcp` OP-5 / OP-6.
- **Sentinel naming**: `<server>@<version>.installed` where `<version>` is the value in `.devcontainer/versions.env` (commit-SHA-prefix for actionlint-mcp). Enforcement: postCreate.sh logic + OP-5 audit.

#### Project Filesystem Error State Design

- **Missing `.mcp.json`**: Claude Code session starts with zero MCP servers. The augmented `auditing-mcp` OP-1 / OP-2 BLOCKER. postStart's "default-fail-closed" filter (per ADR-0039) emits `structured_failure` record with `failure_class=process_start` and refuses to write events.
- **Malformed `.mcp.json`**: same as above; Claude Code surfaces parse error in `claude mcp list`; OP-1 BLOCKER.
- **Augmented `auditing-mcp` BLOCKER finding**: **Hard gate per ADR-0043 — halts orchestrator at Gate 6.** Operator workflow: remediate + re-run audit + resume orchestrator. (Was TBD per OI-3 in Blueprint v2; closed at v3.)
- **`auditing-mcp` script execution failure**: surfaces in the operator's terminal; non-zero exit code; the failure is itself a BLOCKER per the augmented skill's existing contract → hard-gates orchestrator per ADR-0043.

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
- **I-DR-CS-004 (codebase-memory-mcp absent from postStart SERVERS array)**: **revised at v3 per Gate-4 OI-1 closure** — the SERVERS array contains 7 entries (no codebase-memory-mcp); the stderr banner reports "N/7 healthy". Original I-DR-CS-004 concern (mismatch between PRD count and registered count) resolves naturally by alignment at 7.
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
| `postCreateCommand` | `.devcontainer/postCreate.sh` (NEW) | Idempotent install for 5 OSS-local servers; sentinel + binary-presence check; fail-fast | Yes (sentinel-guarded) |
| `postStartCommand` | `.devcontainer/postStart.sh` (NEW) | Readiness probe for 7 registered servers (per Gate-4 OI-1 closure); writes `readiness_probe` records to `mcp-events.jsonl`; warn-and-continue | Yes (probe loop is read-only of state; write is append-only) |
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
| **Server crash mid-session** | GitNexus stdio process exits | In-product fallback-detection code-site detects | Append `structured_failure` record; stderr banner per ADR-0037; **no automatic fallback in this feature per Gate-4 OI-1 closure**; operator decides next action | Operator sees banner; manual remediation |
| **Augmented `auditing-mcp` BLOCKER** | OP-2: consumer-mapping drifted | `audit_mcp.py` exit code | Operator runs audit; sees BLOCKER finding; resolves before Gate 6 | **Hard gate per ADR-0043: orchestrator halts at Gate 6; remediate + re-run + resume** |
| **Credential leak detected in mcp-events.jsonl** | OP-6 grep finds credential shape | `audit_mcp.py --with-runtime` | BLOCKER; operator rotates credential + investigates redaction filter | Hard gate per ADR-0043; pipeline halt; remediation required |
| **`.mcp.json` malformed** | postStart.sh fails to parse env-block | `jq` parse failure | Default-fail-closed: empty allowlist; emit `structured_failure` with `failure_class=process_start`; warn-and-continue | Operator inspects `.mcp.json`; rebuild after fix |

### Logging and Monitoring

- **Log events**:
  - postCreate.sh: per-server install start/end + sentinel write.
  - postStart.sh: per-server probe latency + result + (on failure) failure_layer.
  - Server-crash events (ADR-0037 structured_failure records; primary_degraded events are schema-level provision not exercised in this feature).
  - `auditing-mcp` audit outcomes (BLOCKER / MAJOR / MINOR / NIT counts; BLOCKER is gate-blocking per ADR-0043).
- **Log levels**:
  - INFO: install success, probe pass.
  - WARN: probe fail (transient).
  - ERROR: install fail (fail-fast); credential leak detected (OP-6 BLOCKER); .mcp.json parse error; any BLOCKER finding at Gate 6 (per ADR-0043).
- **Sensitive data**: credential values redacted at the log-surface boundary per ADR-0039.
- **Metrics**: none (project is operator-run; no remote sink per PRD Won't-Have).
- **Traces**: none.
- **Alerts**: none (no on-call rotation per PRD NFR-8).
- **Dashboards**: none.

## Implementation Plan

### Implementation Approach

**Selected Approach**: Sequential per-layer with cross-layer reconciliation gates. Codespaces foundation (Features + containerEnv) before any postStart work; cc-layer authoring of `.mcp.json` schema and `mcp-events.jsonl` schema before codespaces postStart.sh implementation; auditing-mcp augmentation + family-graduation after both layers' artifacts exist; orchestrator Gate-6 hard-gate wiring after auditing-mcp is graduated and runnable.

**Selection Reason**: The two layers have tight cross-layer contracts (the `mcp-events.jsonl` schema is cc-owned + codespaces-consumed; the env-block-as-redaction-allowlist is cc-owned + codespaces-consumed at postStart). Sequencing prevents windowed inconsistencies. The graduation + hard-gate steps are added at v3 per Gate-4 OI-2 / OI-3 closures.

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **ADR + schema authoring (this Blueprint)**
   - Layer: design-composer (this stage)
   - Technical Reason: Seven ADRs (ADR-0037 through ADR-0043) and the mcp-events.jsonl schema must exist before plan-author writes per-task instructions
   - Dependent Elements: all subsequent

2. **`.devcontainer/versions.env` + devcontainer.json Features**
   - Layer: codespaces
   - Technical Reason: Plan-author needs the pin values to author postCreate.sh; the Node 20 + Go Features must exist before postCreate runs `go install` / `npx`
   - Prerequisites: ADRs authored

3. **`KB-mcp-platform/` + `KB-mcp-design/` skill authoring**
   - Layer: claude-code
   - Technical Reason: `KB-mcp-design/references/principles.md` is the canonical home for the `mcp-events.jsonl` schema (per ADR-0037). postStart.sh consumes this schema. The schema must be authored before the consumer.
   - Prerequisites: ADRs authored

4. **`.mcp.json` authoring (7 entries per Gate-4 OI-1 closure)**
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

7. **8 of 36 `.claude/agents/*.md` edits**
   - Layer: claude-code
   - Technical Reason: Adds `mcp__<server>__<tool>` entries that reference servers registered in `.mcp.json` (item 4). Per ADR-0040 includes the 5-agent Serena narrowing; 3 of those 5 (review-architecture-auditor, design-cicd, discovery-codebase-researcher) overlap with the base consumer-mapping; the other 2 (design-cc, design-codespaces) are net-new — total touched = 8 unique. **Per Gate-4 OI-1 closure, codebase-memory-mcp allowlist entries are dropped (not provisioned in this feature).**
   - Prerequisites: item 4

8. **`auditing-mcp/` augmentation (10 rule families + 6 new scripts) + family graduation per ADR-0042**
   - Layer: claude-code
   - Technical Reason: Validates the contracts established by items 3-7. Runnable at any time after they exist; the OP-5 lifecycle audit reads devcontainer.json (item 2); OP-6 reads mcp-events.jsonl (after item 6 runs at least once). **Family graduation steps (frontmatter `family:` flip + body `## Sub-skill family` section addition + auditing-cc-configs/SKILL.md family-list pruning + auditing-shared/SKILL.md description update) are part of this item per ADR-0042 Implementation Guidance.**
   - Prerequisites: items 2-7, ADR-0042

9. **Orchestrator Gate-6 phase-validator update (NEW at v3 per ADR-0043)**
   - Layer: claude-code (orchestrator topology)
   - Technical Reason: Wires the hard-gate semantics: `auditing-mcp/scripts/audit_mcp.py --with-runtime` non-zero exit halts the orchestrator at Gate 6. Per ADR-0043 Implementation Guidance, the validator is a script (Python or bash) invoked by the orchestrator's Gate-6 step.
   - Prerequisites: item 8 (auditing-mcp must be runnable + graduated)

10. **`.gitignore` update + `.claude/runtime/.gitkeep`**
    - Layer: claude-code
    - Technical Reason: Bootstraps the directory + ignores the runtime file. Resolution of Q-CC-2.
    - Prerequisites: none (independent housekeeping)

11. **ADR-0007 relocation (`adrs-migrated/` → `adrs/`)**
    - Layer: claude-code (ADR registry housekeeping)
    - Technical Reason: Per ADR-0038 / ADR-0036 single-canonical-ADR-location.
    - Prerequisites: ADR-0038 (this Blueprint)

12. **ADR-0018 v1.0.0 supersession marker + KB-codebase-research + discovery-codebase-researcher schema_version bump to 1.1.0**
    - Layer: claude-code
    - Technical Reason: ADR-0038 codifies; downstream consumers update to cite v1.1.0 + ADR-0038.
    - Prerequisites: ADR-0038

#### Cross-Layer Sequencing Notes

- **Schema before consumer**: KB-mcp-design `principles.md` (mcp-events.jsonl schema) before postStart.sh.
- **.mcp.json before agent edits**: agent allowlist entries must name registered servers.
- **devcontainer Features before postCreate**: postCreate.sh runs `go install` (needs Go feature) and `npx` (needs Node feature).
- **postCreate before postStart**: postStart probes binaries that postCreate installed.
- **All artifacts before auditing-mcp augmentation finalization**: the audit rules validate the live state; activate after the state exists.
- **auditing-mcp augmentation + graduation before orchestrator Gate-6 phase-validator update**: the hard-gate wiring depends on the audit-skill being runnable and the family-graduation being structurally complete (per ADR-0042 + ADR-0043).

### Migration Strategy

This feature is greenfield within its layers — there is no existing MCP wiring to migrate. The one supersession (ADR-0018 v1.0.0 → ADR-0038 v1.1.0) is additive-schema, handled by:
- Mark ADR-0018 status `Superseded by ADR-0038` (file remains in place per ADR-0005).
- Update KB-codebase-research/SKILL.md to cite ADR-0038 and `schema_version: 1.1.0`.
- Update discovery-codebase-researcher.md the same way.
- (Optional, low priority) Relocate ADR-0007 from `adrs-migrated/` to `adrs/` per ADR-0036.

The auditing-mcp family-graduation (per ADR-0042) is a one-way structural migration: frontmatter `family:` flips; auditing-cc-configs family list drops the row; auditing-shared description gains the consumer; orchestrator singular→plural family handling updated. No content loss; ADR-0042 documents the graduation history inline in `auditing-cc-configs/SKILL.md`.

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
| MCP upstream sources (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, GitNexus) | No | These are real upstreams; the install scripts pull from them. Acceptance is the actual install + probe pass. |
| Context7 / Exa SaaS endpoints | No | Real endpoints; tests at acceptance time use the real auth + real probe. The supplementary auth probes are gated on `MCP_AUTH_PROBE=1` to respect quotas. |
| Codespaces secrets surface | No (in Codespace) / Mock-via-local-env (in local devcontainer) | The Codespace environment provides the real secrets; local devcontainer testing requires the operator to set env vars manually. |
| `claude mcp list` output parsing | No (per ADR-0041 / D-0008) | Direct JSON-RPC probe via `lib/mcp-ping.sh` is the canonical primitive; we do NOT parse `claude mcp list` (brittle). |
| `mcp-events.jsonl` event records | Synthetic fixtures for unit tests of `auditing-mcp` OP-6 | The redaction-integrity check is tested against synthetic credential-shape strings; the live file is tested end-to-end. |

(Note: codebase-memory-mcp row removed at v3 per Gate-4 OI-1 closure.)

### Data Layer Testing Strategy

N/A — no data layer (no DB / no ORM).

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|-------|-----------|---------|----------|
| Claude Code | static-config audit | `auditing-mcp/scripts/audit_mcp.py` (Python) | `.claude/skills/auditing-mcp/scripts/` |
| Claude Code | runtime audit | `auditing-mcp/scripts/audit_mcp.py --with-runtime` | same |
| Claude Code | per-agent allowlist consistency | OP-2 / OP-3 scripts (NEW per cc-design) | same |
| Claude Code | family-graduation structural test (NEW v3) | grep + frontmatter assertion: `auditing-mcp/SKILL.md` carries `family: auditing-mcp`; `auditing-cc-configs/SKILL.md` does NOT list auditing-mcp in the sub-skill family enumeration | manual at Gate 6 or in audit-skill OP-7 trifecta-consistency rule |
| Codespaces | postCreate / postStart smoke (cold-cache) | wall-clock vs NFR-1; mcp-events.jsonl inspection | manual at Gate 6; operator workflow |
| Codespaces | rebuild idempotence (warm-cache) | rerun postCreate; sentinel + binary-presence check; expect short-circuit | manual at Gate 6 |
| Cross-layer | `claude mcp list` shows 7 connected | the canonical acceptance command | manual at Gate 6 |
| Cross-layer | per-server probe pass | the agreed probe per server (FR-4) | invoked via Claude Code session or audit-script in `--with-runtime` mode |
| Cross-layer (NEW v3) | orchestrator Gate-6 hard-gate semantics | invoke auditing-mcp with seeded BLOCKER finding; confirm orchestrator halts; remediate; re-run; confirm resume per ADR-0043 | manual at Gate 6 |

### Integration Verification Points

- **`claude mcp list` shows 7 of 7 connected** at postCreate completion (AC-FR-1-a + AC-CC-1).
- **Per-server probe returns success** for all 7 (AC-FR-1-b + AC-FR-4-a).
- **`mcp-events.jsonl` contains 7 `readiness_probe` records** after postStart (AC-CS-4 + AC-CC-6 per Gate-4 OI-1 closure).
- **`auditing-mcp` zero BLOCKER findings** at Gate 6 (AC-FR-11-c + AC-CC-5 + AC-NFR-2-c). **Hard gate per ADR-0043.**
- **`git grep` finds zero literal credentials** across the repo (AC-NFR-2-a + AC-CC-4).
- **OP-4 finds primary/fallback prose** in discovery-codebase-researcher + review-architecture-auditor (per ADR-0037 schema-level provision; preserved even though no fallback registered in this feature per Gate-4 OI-1 closure).
- **auditing-mcp graduation structural check (NEW v3)**: `auditing-mcp/SKILL.md` frontmatter `family: auditing-mcp`; `auditing-cc-configs/SKILL.md` family list does not include auditing-mcp; `auditing-shared/SKILL.md` description lists auditing-mcp as a consumer (per AC-CC-10 + ADR-0042).
- **Orchestrator Gate-6 hard-gate semantics (NEW v3)**: a seeded BLOCKER from auditing-mcp halts the orchestrator at Gate 6; remediation + re-run resumes; per ADR-0043.

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**:
  - All 7 mcpServers in `.mcp.json` connect at postCreate (per Gate-4 OI-1 closure).
  - Per-server probe returns success for each.
  - 8 agent files carry the prescribed `mcp__` entries; 28 preserve zero-`mcp__`.
  - `mcp-events.jsonl` contains 7 `readiness_probe` records (one per registered server) after every postStart cycle, with `result: pass` or `result: fail` + `failure_layer`.
  - `auditing-mcp` (10 rule families) reports zero BLOCKER findings against the post-feature devcontainer. Any BLOCKER halts orchestrator at Gate 6 per ADR-0043.
  - `auditing-mcp` family-graduation is structurally complete: frontmatter `family: auditing-mcp`; `## Sub-skill family` body section present; `auditing-cc-configs/SKILL.md` family list does not include auditing-mcp; `auditing-shared/SKILL.md` description lists auditing-mcp as a graduated-family consumer.
  - W/H/A trifecta is structurally complete and cross-referenced per the universal convention.
  - No credential value in any committed file or any line of `mcp-events.jsonl`.
- **Verification method**:
  - End-to-end smoke: open a fresh Codespace; observe postCreate completes; observe postStart writes 7 records; run `claude mcp list`; run `auditing-mcp/scripts/audit_mcp.py --with-runtime`; verify zero BLOCKER. Confirm `auditing-mcp/SKILL.md` frontmatter family field + body section structure.
  - Per-AC EARS-form acceptance test (authored by `test-acceptance-author` downstream).
- **Verification timing**:
  - At Gate 6 (Deliverable Packaging). **Hard gate per ADR-0043** — any BLOCKER halts; operator workflow is remediate + re-run + resume.
  - On every Codespace rebuild (continuous; lifecycle health-check produces fresh evidence).

### Early Verification Point

- **First verification target**: A single Codespace rebuild with `.mcp.json` + Features + postCreate.sh stub installing one server (Serena via uvx). If Serena installs and `claude mcp list` shows it connected, the install-path discipline (ADR-0041) is validated; the remaining four follow the same pattern.
- **Success criteria**: `claude mcp list` shows `serena: connected` after fresh build.
- **Failure response**: revisit ADR-0041 install-path posture; possibly reconsider Q-CS-2 (prebuild adoption) earlier.

### Output Comparison

N/A — entirely new behavior; no existing equivalent to compare against.

### Operational Verification

- **Pre-merge gates**: **Hard gate at Gate 6** per ADR-0043 — any BLOCKER finding from augmented `auditing-mcp` halts the orchestrator. No operator-bypass at the gate; remediation + re-run is the required path. (Was TBD per OI-3 in v2; closed at v3.)
- **Post-deploy verification**: every Codespace rebuild produces fresh `readiness_probe` records; operator inspects.
- **Migration verification**: KB-codebase-research/SKILL.md and discovery-codebase-researcher.md cite `schema_version: 1.1.0` and ADR-0038 — verified by grep at Gate 6. `auditing-mcp` frontmatter family field + body `## Sub-skill family` section — verified by grep / structural test at Gate 6 (per ADR-0042).
- **Rollback rehearsal**: N/A (no production deployment; rollback = revert merge).

## Future Extensibility

- **Extension points**:
  - `.mcp.json` is the SSOT; adding a new MCP server = adding to `.mcp.json` `env:` block (automatically covered by redaction + audit) + per-agent allowlist (if consumed) + KB-mcp-platform reference page.
  - `mcp-events.jsonl` schema accepts additive event types; the OP-6 audit rule remains valid (it grep-matches credential shapes, not event-type names).
  - The augmented `auditing-mcp` is plan-author-extensible; adding an OP-11 rule = adding a script in `scripts/` + a row in the rule-family table. **The graduated family-coordinator pattern (per ADR-0042) reserves the `## Sub-skill family` slot for future MCP-audit sub-skills.**
  - The graduation precedent (per ADR-0042) governs future `auditing-*` family decisions; see `Issues/proposal-auditing-family-graduation-review.md` for the broader future review.
- **Known future requirements**:
  - Plugin packaging of the trifecta (Q-CC-7) — design is plugin-compatible by following the universal trifecta conventions.
  - Prebuild adoption (Q-CS-2) — if cold-cache time becomes a felt constraint, a follow-up moves the workspace-agnostic install subset to `onCreateCommand`.
  - CI smoke-test workflow (`claude mcp list` + `auditing-mcp`) — PRD Won't-Have for this release; follow-up feature.
  - Serena post-v1.3.0 migration (`base_modes` → `added_modes`) — ADR-0040 pins pre-v1.3.0; follow-up ADR bumps.
  - Filling auditing-codespaces STUB (ADR-0033) — the augmented `auditing-mcp` OP-5 owns lifecycle audit until then; can hand back cleanly. design-codespaces's ADR-0040 Serena entry is forward-looking on this stub-fill (OI-6). **At stub-fill, the auditing-codespaces graduation default is its own family-coordinator (mirroring the ADR-0042 precedent).**
  - Reconsider codebase-memory-mcp fallback registration in a future feature — Gate-4 OI-1 closure dropped it from this feature, but ADR-0007's primary/fallback policy remains in force at the project level. A future feature may revisit; the ADR-0037 schema-level provision for `primary_degraded` is preserved.
  - `auditing-family-structure-review-r1` pipeline run (suggested slug) — captured in `Issues/proposal-auditing-family-graduation-review.md`; governs whether other `auditing-*` siblings warrant graduation under the ADR-0042 precedent.
- **Intentional limitations**:
  - No remote log sink, metrics dashboard, alerting (PRD Won't-Have; operator-run pipeline).
  - No structured frontmatter field for primary/fallback declaration (ADR-0037 prefers prose-with-audit-rule).
  - No new sub-agents introduced.
  - No CLAUDE.md added at this stage (cc-design).
  - No codebase-memory-mcp fallback in this feature's `.mcp.json` (per Gate-4 OI-1 closure; ADR-0007 policy preserved at project level).
  - Other `auditing-*` sibling graduation decisions deferred to future pipeline run (per ADR-0042).

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

### Alternative 5 (NEW at v3): Preserve auditing-mcp in auditing-cc-configs family (Path B)

- **Overview**: Composer's pre-decision recommendation — `auditing-mcp` remains a sub-skill of `auditing-cc-configs`; minimum convention change.
- **Advantages**: Minimum convention change; honors composer's repo-discipline brief.
- **Disadvantages**: Doesn't reflect the substantive failure-domain distance (MCP vs `.claude/`-config); creates gating asymmetry with the ADR-0043 hard-gate (one of six sub-skills hard-gates, five do not); the user's substantive reasoning identifies MCP risks as materially distinct (devcontainer/docker breakage).
- **Reason for Rejection**: **Rejected by user at Gate 4 in favor of Path A (graduation per ADR-0042).** User rationale: failure-domain distance + parallel hard-gate decision creates a coherent posture only under Path A. Follow-up question (other siblings) captured in `Issues/proposal-auditing-family-graduation-review.md`.

### Alternative 6 (NEW at v3): Advisory-mode auditing-mcp at Gate 6

- **Overview**: AC-CC-5's "zero BLOCKER findings" bar remains published but operator may proceed past with rationale documentation; no hard-halt.
- **Advantages**: Lower-friction operator workflow; allows judgment for edge cases.
- **Disadvantages**: Creates the worst-case condition for the AC-CC-5 bar (published but unenforced); failure modes `auditing-mcp` catches (credential leak, broken lifecycle, supply-chain anti-patterns) are categorically not the kind that should be operator-overridable; gating asymmetry with the ADR-0042 graduation is unresolved.
- **Reason for Rejection**: **Rejected by user at Gate 4 in favor of hard gate per ADR-0043.** User rationale (verbatim): "MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| Cold-cache build sits at upper bound of NFR-1 ~10 min target | codespaces | Medium (annoyance) | Medium | Estimate ~7-12 min per codespaces §Rebuild-Time Estimate; mitigation deferred to post-ship Q-CS-2 (prebuild adoption); kill criterion at 2× target (PRD Rollout Plan) |
| GitNexus skip-grammars smoke-test (C-0388/C-0411 partially_verified-medium) fails on pinned tag | codespaces | Medium | Medium | AC-CS-9 codifies fail-postCreate; operator sees failing server immediately and can repin |
| Stdio servers not auto-reconnected (C-0301) — seven servers fail open to operator recovery | claude-code | High (silent surface failure) | Low (event surface is now wired) | ADR-0037 `structured_failure` + stderr banner makes failures operator-visible; FR-9 contract is load-bearing |
| Credential leak in `mcp-events.jsonl` despite redaction | claude-code | **CRITICAL** (release blocker) | Low | ADR-0039 + OP-6 grep audit; `auditing-mcp --with-runtime` runs at Gate 6; default-fail-closed if allowlist empty; **hard gate per ADR-0043 ensures halt-on-detection** |
| ADR-0007 relocation surfaces deferred content questions | claude-code | Low | Low | Relocation is independent of content; v2.2.0 content unchanged |
| Per-agent context overhead with 7 always-on servers exceeds tolerable envelope across 36 agents (NFR-4) | claude-code | Medium | Medium-low (tool schemas deferred per cc-design Principle 1; one fewer server than v2 per Gate-4 OI-1 closure) | Plan-author measures in implementation; if intolerable, downscoping (conditional activation) opens as re-scope |
| The 5-agent Serena allowlist (ADR-0040) misses an agent that actually needs Serena | claude-code | Low (additive fix) | Low-medium | OP-2 audit + operator feedback in first weeks post-ship surfaces; additive ADR amendment is cheap |
| design-codespaces's Serena entry sits unused if ADR-0033 auditing-codespaces stub remains unfilled | claude-code | Low (cosmetic; additive entry is cheap) | Medium | Tracked as OI-6 / Known Unknown; kill-criterion: if no Serena tool invocation from design-codespaces for >90 days post-ship and stub still unfilled, an additive ADR may remove the entry |
| W/H/A trifecta drift over time (KB-mcp-platform and KB-mcp-design fall out of sync with `.mcp.json`) | claude-code | Medium (the maintenance interface becomes a lie) | Medium | OP-7 trifecta-consistency audit rule (every server in `.mcp.json` named in KB-mcp-platform; cross-references current); runs at every operator-invocation of `auditing-mcp` |
| Plan-author misses a sentinel/binary-persistence edge case (I-DR-CS-009 reopened by some unconsidered rebuild path) | codespaces | Medium | Low | ADR-0041 Implementation Guidance gives plan-author the binary-presence check pattern; OP-5 lifecycle audit catches sentinel-without-binary mismatches |
| **OI-3 / Q-CC-9 — augmented `auditing-mcp` Gate-6 status** | (cross-cutting) | Medium (pipeline behavior at Gate 6) | n/a (policy decision) | **Closed at Gate 4 v3 per ADR-0043 — hard gate; user rationale captured verbatim in the ADR**. Any BLOCKER halts orchestrator; remediation + re-run is the required path. AC-CC-5 / AC-FR-11-c / AC-NFR-2-c codify the "zero BLOCKER findings" bar with strict enforcement semantics. |
| **NEW at v3 — auditing-mcp graduation creates orchestrator singular→plural drift** | claude-code | Low-medium (project-files inconsistency) | Medium | Plan-author audits references to "the auditing family" (singular) per ADR-0042 Implementation Guidance + `Issues/proposal-auditing-family-graduation-review.md` §3 item 6; update to plural handling |
| **NEW at v3 — over-broad BLOCKER severity in auditing-mcp halts orchestrator on low-stakes issues** | claude-code | Medium (operator-friction) | Low-medium | Audit-skill's severity model is the only adjustment lever (per ADR-0043 Decision Details Known Unknowns (a)); routine review of rule-family BLOCKER assignments during maintenance windows; if proven over-eager, demote to MAJOR at the rule definition |
| Helper scripts (`lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`) introduce subtle JSON-RPC bugs | codespaces | Medium | Low-medium | ADR-0041 fixes contract; plan-author writes; review at Gate 5 |

## References

- **PRD**: `working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md` (v3.0.0)
- **Synthesis**: `working/feature/devcontainer-mcp-provisioning-r1/synthesis.md`
- **Codebase Analysis**: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json`
- **Predecessor Blueprint**: `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md` (superseded by this v3)
- **Per-layer Designs**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-design.md` (Claude Code / Project Filesystem)
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-design.md` (Dev Environment / Codespaces)
- **Per-layer Dependency Sidecars**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-dependencies.json`
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-dependencies.json`
- **Per-layer Review Findings (resolved/integrated in this Blueprint)**:
  - `working/feature/devcontainer-mcp-provisioning-r1/cc-design-review-issues.json` (6 findings; resolution mapping above; recommended I-DR-003/005/006 absorbed in §Claude Code / Project Filesystem Design)
  - `working/feature/devcontainer-mcp-provisioning-r1/codespaces-design-review-issues.json` (10 findings; resolution mapping above)
- **Blueprint v1 Review Findings (resolved in v2)**:
  - `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v1-review-issues.json` (6 findings: I-DR-BP-001..006; resolution mapping in Update History below)
- **Blueprint v2 Review Findings (resolved in this v3)**:
  - `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2-review-issues.json` (reviewer-APPROVED at v2; v3 is a focused Gate-4 decision-propagation revision, not a review-gated re-author)
- **Research Notes**: `working/feature/devcontainer-mcp-provisioning-r1/research-notes/T-001..T-008.md`
- **Agent Roster Impact Matrix (closure of Q-3; added pre-Gate-4)**: `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` — 36-row demand-driven sweep confirming the supply-driven consumer set. See OI-7 below.
- **Issues (companion artifacts; NEW at v3)**:
  - `Issues/proposal-auditing-family-graduation-review.md` — captures the broader auditing-family graduation question for downstream pipeline run (per ADR-0042 follow-up; cross-referenced from OI-2 closure).
- **ADRs authored in this Blueprint** (in `working/feature/devcontainer-mcp-provisioning-r1/adrs/`; promoted to `/workspaces/feature-pipeline/adrs/` at deliverable packaging time per ADR-0036):
  - ADR-0037 — MCP transition surfacing — `mcp-events.jsonl` + stderr banner (UI-15) — **edited in v3 (Implementation Guidance line 143 reverted from "eight" to "seven" readiness_probe records per Gate-4 OI-1 closure; Document History row added)**
  - ADR-0038 — `codebase-analysis.json` schema v1.1.0 (supersedes ADR-0018 v1.0.0)
  - ADR-0039 — Credential redaction posture — redact-at-source from `.mcp.json` env-block
  - ADR-0040 — Serena — narrowed always-on; Python-audit-surface allowlist (5 agents); pinned pre-v1.3.0
  - ADR-0041 — Install-mechanism strategy — hybrid Features + idempotent postCreate + verified binary fetch
  - **ADR-0042 (NEW v3) — auditing-mcp family graduation (codifies Gate-4 OI-2 Path A user override)**
  - **ADR-0043 (NEW v3) — auditing-mcp Gate-6 hard gate (codifies Gate-4 OI-3 user resolution)**
- **Existing ADRs referenced**: see Background and Context / Prerequisite ADRs above.
- **KBs used in composition**: KB-documentation-criteria (Blueprint + ADR templates; layer taxonomy; EARS), KB-general-coding-principles (code-block rubric for sample sketches), KB-review-disciplines (Gate 0/1 self-check), KB-cc-design + KB-cc-platform (per-layer composition), KB-codespaces-design + KB-codespaces-platform (per-layer composition).

### Open Items (deferred to user / Gate 4 disposition)

- **OI-1 (CLOSED at Gate 4 v3; user resolution: drop codebase-memory-mcp from inventory)**: Inventory count convention. **User decision (verbatim): "Lets move forward with 7 MCP the codebase-memory-mcp was an earlier assessment that is now stall."** Resolution baked into AC-X-2 (revised at v3): PRD's "seven named servers" = canonical inventory; `.mcp.json` carries exactly 7 entries (no fallback entry). The augmented `auditing-mcp` rules OP-2 / OP-3 / OP-8 no longer special-case codebase-memory-mcp by name. ADR-0037 Implementation Guidance edited in-place from "eight" to "seven" `readiness_probe` records (companion edit, see ADR-0037 Document History). All 13 v2 reviewer-flagged locations propagated to 7-server convention. **Closure artifact**: this Blueprint v3.
- **OI-2 (CLOSED at Gate 4 v3; user resolution: Path A — graduate)**: Family-coordinator path. **User decision (verbatim): "graduate and then write an issue on whether we need to look at github codespace and the others in an issue report under Issues/ for future consideration of a pipeline run."** `auditing-mcp` graduates to its own family-coordinator per ADR-0042 (NEW v3). Composer's pre-decision Path B (preserve family) was overridden. Follow-up question (other `auditing-*` siblings) captured in `Issues/proposal-auditing-family-graduation-review.md` for future `auditing-family-structure-review-r1` pipeline run. **Closure artifacts**: ADR-0042 + the Issues proposal.
- **OI-3 (CLOSED at Gate 4 v3; user resolution: hard gate)**: Augmented `auditing-mcp` Gate 6 status. **User decision (verbatim): "I agree hard gate. MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."** Hard gate codified per ADR-0043 (NEW v3) — any BLOCKER finding halts the orchestrator at Gate 6; no operator-bypass at the gate; remediation + re-run is the required path. AC-CC-5 / AC-FR-11-c / AC-NFR-2-c carry the bar with strict enforcement semantics; the orchestrator Gate-6 phase-validator wires the hard-gate behavior per ADR-0043 Implementation Guidance. **Closure artifact**: ADR-0043.
- **OI-4 (still open)**: Per-agent context-overhead measurement (UI-7 from PRD). Plan-author measures during implementation; if intolerable, opens a downscoping re-scope. Not blocking Gate 4.
- **OI-5 (still open)**: ADR-0007 content review post-relocation. Plan-author may file a separate review-and-update follow-up; not blocking this feature.
- **OI-6 (still open; v2 carryover)**: ADR-0040 design-codespaces forward-looking dependency on ADR-0033 stub-filling. design-codespaces is in the Serena 5-agent allowlist with rationale "may touch auditing-codespaces/scripts/ if/when the stub becomes real per ADR-0033." If the auditing-codespaces stub remains unfilled for >90 days post-ship AND design-codespaces fires zero Serena tool invocations in that window, an additive amendment ADR may remove the entry. Not blocking Gate 4; tracked as a known unknown so it surfaces in routine post-ship review.
- **OI-7 (CLOSED at Gate 4 by `agent-roster-impact-matrix.md`; v2 carryover)**: Q-3 from `codebase-analysis-report.md` line 200 ("are the 36 agent files all in-scope, or are some — esp. `synth-*` — deprecated and excluded from MCP wiring consideration?") and ADR-0040 line 74 hedge on `design-iac` / `design-api` Python-audit-surface evidence. **Closure artifact**: `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` — 36-row demand-driven sweep. **Findings**: 8 IN_CC_DESIGN (matches this Blueprint's consumer set), 0 NEWLY_PROPOSED, 28 EXPLICIT_NO with cited rationale per agent. `synth-*` agents confirmed **active, not deprecated** (excluded on "no MCP-relevant work surface" rationale). ADR-0040 hedge tested: no evidence found that `design-iac` / `design-api` touches `auditing-*/scripts/` Python today. No Blueprint-content changes triggered. **The matrix becomes the canonical demand-side closure record for this feature; future agent additions or surface changes must update it alongside any cc-design edits.**

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial Blueprint composition. Integrates cc-design.md + codespaces-design.md; authors ADR-0037 through ADR-0041; resolves 9 Q-CC-N + 8 Q-CS-N + 16 I-DR-N items; codifies the 8-entry inventory convention (AC-X-2) and the secret-absent failure mode (AC-X-1); adopts Path B for family-coordinator (Q-CC-1). | design-composer |
| 2026-05-23 | 3.0.1 | Patch-level reconciliation per architecture-audit cycle 2 (retroactive run; PKG-BLOCKER-002 resolution). Two important findings fixed in-place: **I-AA-001** — `design-cc.md` → `design-claude-code.md` at line 450 (filename drift; the agent's frontmatter `name:` is `design-cc` per Path-A reserved-word workaround, but the on-disk file is `design-claude-code.md`). **I-AA-002** — consumer-set math narrative corrected at Fact Disposition C-0445 (line 399) and Sub-Agents preamble (line 830): "7-agent base" replaced with auditor-verified "6-agent base + 5 Serena − 3 overlap = 8 unique" math (enumerated explicitly). Conclusion (8 unique touched agents) unchanged; only description path corrected. See `reconciliation-log-cycle-2.md`. | orchestrator (direct mechanical-edit patch per user disposition) |
| 2026-05-23 | 3.0.2 | Patch-level reconciliation per **execute-orchestrator Phase 0 verify-at-execution** findings, dispatched as reconciliation cycle 3 (D-3.2). Three findings patched in-place across the design surface: **F1 (BLOCKER)** — actionlint-mcp upstream identifier drift: `github.com/2manymws/actionlint-mcp` → `github.com/hongkongkiwi/actionlint-mcp`; subpath `/cmd/actionlint-mcp` dropped (upstream main.go is at repo root). Sites: External Resources Used table (actionlint-mcp row). **F2 (HIGH)** — GitNexus install-method category error: `uvx --from gitnexus@<TAG>` (Python, never published) → `npm install -g gitnexus@${GITNEXUS_TAG}` (persistent) + `npx -y gitnexus@${GITNEXUS_TAG} mcp` (ephemeral). Sites: External Resources Used (GitNexus row, with prereq Node-LTS note); AC-CS-9 (install-mechanism phrasing updated; AC-CS-9 SEMANTIC INTENT PRESERVED — no C++ toolchain at cold-cache; env-var `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` now suppresses npm's vendored tree-sitter grammar build instead of a Python C-extension build that never existed); Sub-Agents / MCP Servers table (gitnexus row). **AC-CS-9 wrapping-intent preservation note:** the verify-at-execution check (T0.4) asserts "no `cc`/`g++`/`cargo` in install-process tree" — install-command-agnostic; only the install command being probed changes form. **F3 (MAJOR; investigation-gated)** — Context7 v1.2.0 doesn't exist + `ReplaceContentTool` was Serena-CHANGELOG contamination: Fact Disposition row C-0037 rewritten from "v1.2.0 ReplaceContentTool replaces ReplaceRegexTool" to "v3.0.0 two-tool surface (`resolve-library-id`, `query-docs`); stable v1→v3". F3 investigation deliverables: (a) `research-notes/T-005-context7.md` refreshed to v2.0.0 with cycle-3 v3.0.0-verified facts; (b) `verify-at-execution.md` §H-5 stub authored framing the v3.0.0 verification work (live verification deferred to execute-orchestrator Phase 0 re-run). **Investigation-method caveat surfaced:** design-composer's tool set in this harness does not include WebFetch; cycle-3 F3 patches rely on the corroborated in-repo evidence base (T-005 v1.0.0 multi-source + dispatch log's documented npm probe at 2026-05-22T16:20Z). Three sub-findings flagged for cycle-4 audit: SF-F3-RESIDUAL-1 (live WebFetch deferred), SF-F3-RESIDUAL-2 (Redis-backed session state operator impact = OQ-T005-3 carryforward), SF-F3-AUTH-HEADER-1 (canonical Context7 auth-header form `CONTEXT7_API_KEY` vs `Authorization: Bearer` — out-of-scope for cycle-3; flagged for cycle-4). **Companion edits in this cycle**: ADR-0041 Document History bumped to v1.0.1 with npm/npx install-mechanism row added; cc-design.md gitnexus `.mcp.json` entry corrected; cc-dependencies.json actionlint identifier corrected + gitnexus install form noted + gitnexus-credential bracket placeholder unchanged (no GitNexus credential present); codespaces-design.md install_actionlint_mcp + install_gitnexus + smoke-test command corrected; codespaces-dependencies.json updated to note gitnexus is npm-installed + Node-LTS prereq surfaced (already provided by Node Feature, no new dep); tasks.json T0.2 / T0.4 / T0.5 / T3.4 descriptions corrected (T0.5 receives F3 reframing); verify-at-execution.md §H-5 stub authored. **Carried forward**: all v3.0.1 / v3.0.0 / v2.0.0 / v1.0.0 content not affected by F1/F2/F3 preserved verbatim. Section count remains 15. | design-composer (focused multi-artifact amendment per cycle-3 dispatch D-3.2) |
| 2026-05-23 | 2.0.0 | Focused fix for the 6 Blueprint v1 review findings (I-DR-BP-001..006). Changes: (1) **I-DR-BP-001** — propagated the ADR-0040 Serena-narrowing resolution (8 touched / 28 untouched) consistently across 13 reviewer-flagged locations: AC-CC-3, Design Summary blast_radius + main_constraints, Agreement Checklist Scope + Non-Scope, Fact Disposition row C-0445, Implementation Path Mapping (agent file count), Change Impact Map No Ripple Effect, Interface Change Matrix, Architecture Overview ASCII art, Component #2 description, State Invariants, Implementation Plan step 7, Verification Strategy Correctness Definition. Math verified against ADR-0040 (5 Serena consumers; 3 of 5 overlap with 7-agent base mapping; union = 8 unique). (2) **I-DR-BP-002** — edited ADR-0037 Implementation Guidance line 143 in-place from "seven readiness_probe records" to "eight readiness_probe records" with cross-reference to AC-X-2; Blueprint Contract Definitions section now notes the companion edit. (3) **I-DR-BP-003** — added explicit per-layer review-finding absorption block under §Claude Code / Project Filesystem Design that names I-DR-003 (placeholder-convention → `<PIN_TBD>`; deferred to plan-author), I-DR-005 (pedagogical justification tightening → deferred to plan-author at KB-mcp-platform authoring), and I-DR-006 (jsonc-vs-json fence → resolved inline: `.json` for the template, jsonc fences in design-time sketches with caption). (4) **I-DR-BP-004** — consolidated the Sub-Agents table: design-cicd is now a single row listing both `mcp__actionlint-mcp__*` tools and `mcp__serena__*`; the resolution-note parenthetical removed; table count matches the 8-agent total. (5) **I-DR-BP-005** — enumerated AC-NFR-2-a / AC-NFR-2-c / AC-NFR-2-d as PRD-inherited entries under Cross-Layer / Operational ACs. (6) **I-DR-BP-006** — documented ADR-0040 design-codespaces forward-looking dependency on ADR-0033 stub-filling as **OI-6** in Open Items + a Known-Unknown row in the Risks table + a Background and Context note under ADR-0033 prerequisite ADR entry. Carried forward: all other v1 content verbatim. Section count remains 15. | design-composer |
| 2026-05-23 | 3.0.0 | **Focused Gate-4 decision propagation revision (no review-gated re-author; v2 was reviewer-APPROVED at 88–93).** Propagates three discrete user decisions on Blueprint v2 Open Items: **(OI-1 closed)** Drop codebase-memory-mcp from the inventory (user: "Lets move forward with 7 MCP the codebase-memory-mcp was an earlier assessment that is now stall."). The design now carries 7 named MCP servers, 7 `.mcp.json` entries, 7 `readiness_probe` records, no fallback entry. **Locations changed**: Overview opening paragraph (8→7); Layer Scope (note); Design Summary blast_radius + complexity_rationale + main_constraints (added Gate-4 row); External Resources Used (codebase-memory-mcp row removed); Agreement Checklist Scope + Non-Scope (added "no fallback registration" line); Quality Assurance Mechanisms (per-server probe row; lifecycle health-check row); AC-CC-1 (8 entries → 7 entries; removed "+1 documented fallback" phrasing); AC-CS-4 + AC-CC-6 (8 records → 7 records); AC-FR-9-d + AC-CC-7 (no-fallback-in-this-feature qualifier; schema-level provision preserved); AC-X-2 (rewritten — PRD count matches `.mcp.json` count exactly at 7; rules OP-2/OP-3/OP-8 no longer special-case codebase-memory-mcp); Implementation Path Mapping (`.mcp.json` count 8→7; postStart records 8→7); Fact Disposition row C-0447 / C-0448 (preserved policy at project level; not provisioned in this feature); Change Impact Map (`.mcp.json` count); Interface Change Matrix (`.mcp.json` 7-entry alignment row); Architecture Overview ASCII (7 entries; codebase-memory-mcp row removed); Data Flow (postStart loop 8→7; banner "N/8" → "N/7"; runtime-failure step 8 no auto-fallback in this feature); Integration Points List (Claude Code session host: 8 → 7; lifecycle health-check 8 → 7); Component 1 (8 → 7 entries clarification); Component 6 (primary_degraded schema-level-provision note); Component 8 (8 → 7 registered servers); Contract Definitions Bootstrap Semantics (N=8 → N=7); State Transitions (8 → 7 records); Error Handling (server-crash row reworded — no automatic fallback in this feature); Sub-Agents (codebase-memory-mcp entries dropped from discovery-codebase-researcher and review-architecture-auditor; note added explaining project-level policy preservation); MCP Servers table (codebase-memory-mcp row removed; total 7); §I-DR-CS-004 disposition (revised — N/7 healthy banner); Lifecycle Scripts (postStart 8 → 7); Mock Boundary Decisions (codebase-memory-mcp row removed); Per-Layer Test Strategy (8 → 7); Integration Verification Points (8 → 7); Correctness Proof Method (7 entries throughout); Risks (per-agent overhead row 8 → 7); Open Items OI-1 closure block. **Companion ADR-0037 edit**: Implementation Guidance line 143 reverted from "eight" to "seven readiness_probe records" with Document History row noting v3 Gate-4 OI-1 closure as the trigger. **(OI-2 closed; Path A graduation)** `auditing-mcp` graduates to its own family-coordinator per the user's Gate-4 override (verbatim: "graduate and then write an issue on whether we need to look at github codespace and the others in an issue report under Issues/ for future consideration of a pipeline run"). **ADR-0042 NEW** codifies the precedent (security-distinct failure-domain; structural symmetry with already-de-facto-graduated `auditing-github-actions` and future `auditing-codespaces` stub-fill). **Locations changed**: Layer Scope (auditing-mcp graduation note); Background and Context (ADR-0031 row updated; ADRs authored list gains ADR-0042); Agreement Checklist Scope (added graduation row, auditing-cc-configs family list update row, auditing-shared consumer-list update row); Non-Scope (added "no reconsideration of other auditing-* siblings"); Quality Assurance Mechanisms (auditing-mcp row gains "graduated family-coordinator per ADR-0042" qualifier); §FR-11 ACs (NEW AC-CC-10 — family-graduation structural test); Implementation Path Mapping (NEW rows for auditing-cc-configs/SKILL.md edit + auditing-shared/SKILL.md edit); Code Inspection Evidence (auditing-cc-configs lines 144-155 note; auditing-shared note; auditing-mcp line-30 fact updated); Fact Disposition row C-0460 (flipped from "preserve Path B" to "transform — graduate per Path A"); Change Impact Map (3 new claude_code rows for the structural changes; Indirect Impact line on family-membership; No Ripple Effect line on other siblings); Interface Change Matrix (NEW row for auditing-mcp family migration + NEW row for auditing-shared cross-ref expansion); §Claude Code / Project Filesystem Design / Q-CC-1 disposition (rewritten — Path A); NEW subsection "Family-Graduation Structural Changes" with 6-item canonical step list; Conventions Touched (added auditing-cc-configs and auditing-shared rows); Skills table (auditing-mcp row updated — "graduated family-coordinator per ADR-0042"); Component 5 (added graduated-family-coordinator status + ADR-0042 dependency); §Implementation Plan step 8 (auditing-mcp augmentation gains family-graduation steps); §Migration Strategy (NEW paragraph on family-graduation migration); §Verification Strategy (Correctness Definition gains structural-completeness item; Per-Layer Test Strategy gains family-graduation structural-test row); §Future Extensibility (graduation precedent governs future auditing-* decisions; auditing-codespaces stub-fill default; future auditing-family-structure-review-r1 pipeline run); §Alternative Solutions (NEW Alternative 5 — Path B rejected); References (NEW Issues row; ADRs authored list gains ADR-0042); Risks table (NEW row — graduation creates orchestrator singular→plural drift); Open Items OI-2 closure block. **(OI-3 closed; hard gate)** Any BLOCKER finding from augmented `auditing-mcp` halts the orchestrator at Gate 6 per the user's Gate-4 decision (verbatim: "I agree hard gate. MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."). **ADR-0043 NEW** codifies the policy. **Locations changed**: Background and Context (ADRs authored list gains ADR-0043); Agreement Checklist Scope (NEW row — orchestrator phase-validator update at Gate 6); Non-Scope (added "no changes to pipeline stages, gates, or orchestrator topology beyond the Gate-6 phase-validator hard-gate wiring"); Quality Assurance Mechanisms (auditing-mcp row gains "Hard gate at Gate 6 per ADR-0043"); §FR-11 ACs / AC-CC-5 (added hard-gate qualifier); §Cross-Layer / Operational ACs / AC-NFR-2-c (rewritten — "Any BLOCKER finding halts the orchestrator at Gate 6 (hard gate per OI-3 / ADR-0043 closure)"); Implementation Path Mapping (NEW row for orchestrator phase-validator); Change Impact Map (claude_code new row + Indirect Impact line + No Ripple Effect line); Interface Change Matrix (NEW row for orchestrator Gate 6 phase-validator); §Claude Code / Project Filesystem Design / Q-CC-9 disposition (rewritten — hard gate per ADR-0043); §Project Filesystem Error State Design (auditing-mcp BLOCKER row — "Hard gate per ADR-0043; halts orchestrator at Gate 6"); §Conventions Touched (NEW row — orchestrator Gate-6 phase-validator); Skills table (auditing-mcp row updated — "orchestrator Gate-6 hard-gate invocation per ADR-0043"); NEW Component 9 (Orchestrator Gate-6 phase-validator wiring); State Transitions (System Invariants line); Error Handling (BLOCKER row + credential-leak row updated — hard gate per ADR-0043); §Implementation Plan (NEW step 9 — orchestrator Gate-6 phase-validator update); §Verification Strategy / Operational Verification (rewritten — hard gate); Per-Layer Test Strategy (NEW row — orchestrator Gate-6 hard-gate semantics); Integration Verification Points (NEW item — orchestrator Gate-6 hard-gate semantics); §Alternative Solutions (NEW Alternative 6 — advisory mode rejected); Risks table (OI-3 row updated from "TBD per OI-3" to "Closed at Gate 4 v3 per ADR-0043"; credential-leak risk row gains "hard gate per ADR-0043 ensures halt-on-detection"; NEW risk row — over-broad BLOCKER severity); References (ADRs authored list gains ADR-0043); Open Items OI-3 closure block. **Cumulative summary of v3 changes**: 7 ADRs in adrs_authored list (was 5); section count unchanged at 15; v2 content not affected by the three decisions is preserved verbatim. OI-4, OI-5, OI-6 remain open per v2; OI-7 remains closed per v2 with no v3 changes. | design-composer |
