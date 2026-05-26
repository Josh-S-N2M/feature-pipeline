---
id: BP-pipeline-quickwins-hardening-r1
version: 1.0.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
derived_from: working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
codebase_analysis: working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
adrs_referenced:
  - ADR-0005
  - ADR-0017
  - ADR-0029
  - ADR-0033
  - ADR-0036
  - ADR-0037
  - ADR-0039
  - ADR-0040
  - ADR-0041
  - ADR-0042
  - ADR-0043
  - ADR-0044
  - ADR-0056
adrs_authored:
  - ADR-0057
generated: 2026-05-26T00:00:00Z
generated_by: design-composer
---

# Pipeline Quick-Wins Hardening (Round 1) Design Document

## Contents

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

This feature closes five mechanically bounded MCP-incident exposures plus two small process items, with one cross-cutting actionable-diagnostic requirement that runs through them all. It is a carve-out hardening run: the seven Functional Requirements are MINOR-scope, locally blast-radius, two-way reversible, and individually exercisable. The deferral-register rows H-4 (GitNexus install smoke) and B-1 (CI `claude mcp list` smoke) are closed by this feature.

### Layer Scope

This Blueprint touches exactly three layers; the remaining six are out of scope and their layer subsections under Design, Security, Test Boundaries, and Verification are marked `N/A — out of scope`.

- [x] **Claude Code / Project Filesystem** — FR-1 (verdict-vs-findings parity validator), FR-2 (orchestrator dispatch self-check), FR-3 (`.mcp.json` ↔ ADR-0041 parity audit rule OP-11), FR-7 (deferral-register tightening), Claude-Code-side of FR-6
- [ ] **Frontend** — N/A — out of scope per PRD §Layer Scope
- [ ] **Backend** — N/A — out of scope per PRD §Layer Scope
- [ ] **API** — N/A — out of scope per PRD §Layer Scope
- [ ] **Query / Data Access** — N/A — out of scope per PRD §Layer Scope
- [ ] **Database** — N/A — out of scope per PRD §Layer Scope
- [x] **CI/CD (GitHub Actions)** — FR-5 (`mcp-connectivity-smoke.yml` workflow), CI/CD-side of FR-6
- [ ] **Infrastructure as Code** — N/A — out of scope per PRD §Layer Scope
- [x] **Dev Environment (Codespaces / Devcontainer)** — FR-4 (GitNexus install dry-run inside `.devcontainer/postCreate.sh`), Codespaces-side of FR-6

### Referenced Specifications

- **UI Spec**: N/A — no frontend in scope.
- **API Spec**: N/A — no API in scope.
- **Data Model Spec**: N/A — no database in scope.
- **Runbook / Operational Spec**: not required as a separate document; the operational surface is captured in the Implementation Plan and the FR-6 diagnostic contract.

## Design Summary (Meta)

```yaml
design_type: "tooling_change"
risk_level: "low"
complexity_level: "medium"
complexity_rationale: |
  Medium not because any single FR is complex, but because the cross-layer
  reconciliation has substantive items: FR-6 dual-stream diagnostic uniformity
  across three layers with three different output surfaces; AC-FR-5-a/b/c
  PRD-literal-name reconciliation (claude mcp list → claude --bare -p) without
  losing behavioral intent; checkpoint.execution_mode promoted to a first-class
  schema field (ADR-0057). The aggregate touches the orchestrator skill plus
  two auditing skills plus the devcontainer post-create script plus one new CI
  workflow, all coordinated through this Blueprint.
layers_touched:
  - "Claude Code / Project Filesystem"
  - "CI/CD (GitHub Actions)"
  - "Dev Environment (Codespaces / Devcontainer)"
blast_radius:
  runtime: |
    Every future feature run: the FR-1 validator runs at 9 reviewer-completion
    invocation sites; the FR-2 self-check runs once at orchestrator entry on every
    run; the FR-3 OP-11 audit runs at Gate 6 every time auditing-mcp is invoked.
    Every devcontainer rebuild: FR-4 runs on the cache-miss path. Every PR that
    touches a configured path: FR-5 runs.
  build_time: |
    Codespace cold-build cost gains the FR-4 assertion overhead (p95 ≤ 2s on top
    of the existing npm install). CI gains a new workflow whose p95 target is
    under 4 minutes (NFR-4 ceiling 5 minutes). No build-time impact on the
    feature-pipeline orchestrator itself.
main_constraints:
  - "MINOR scope class — every change is two-way reversible; per-mechanism isolation per NFR-11."
  - "No new MCP server, no new MCP allowlist entry (NFR-15 / ADR-0040)."
  - "No new credential surface (NFR-7); no credentials in diagnostics (NFR-8)."
  - "Existing reviewer outputs that the prior pipeline accepted must continue to pass (NFR-9)."
  - "No new event types on .claude/runtime/mcp-events.jsonl (NFR-13)."
  - "No ADR-0041 decision-text mutations — the [DEPRECATED] marker is an annotation, not a rewrite."
biggest_risks:
  - "FR-3 false positives on .mcp.json shapes ADR-0041 didn't anticipate (mitigated: kill criterion + narrow canonicalizer)."
  - "FR-4 silent pass when contract is broken via a mechanism the two signals don't detect (mitigated: opt-in calibration script)."
  - "FR-5 unauthenticated-CLI assumption (`claude --bare -p` emits system/init before auth) may not hold (mitigated: pre-merge validation gate per Q-CICD-8)."
  - "checkpoint.execution_mode field is a schema-surface change that future stages must respect when adding new dispatch postures (mitigated by ADR-0057's kill criterion and the closed-enum discipline)."
unknowns:
  - "The exact post-merge p95 of FR-5 (estimated under 4 minutes; pre-merge validation gate per D-0010 confirms before ship)."
  - "Whether the unauthenticated-CLI assumption holds; verified pre-merge per Q-CICD-8."
```

## Background and Context

### Prerequisite ADRs

- **ADR-0005** (append-only supersession): constrains how this Blueprint can evolve the schema introduced by ADR-0057 and the [DEPRECATED] annotation on ADR-0041's invocation table.
- **ADR-0017** (document-reviewer integration): the FR-1 validator wires into the five `shared-document-reviewer` invocation points this ADR documents.
- **ADR-0029** (no silent scope changes): the AC-FR-5-a/b/c reconciliation surfaces the `claude mcp list` → `claude --bare -p` substitution explicitly rather than silently.
- **ADR-0033** (ADR-0029 execution extension): the FR-1 scope sweep (`execute-task-quality-handler` inclusion) honors no-silent-scope-changes by enumerating the scope expansion in the design.
- **ADR-0036** (single-location ADR placement): the new ADR-0057 lives at the canonical `adrs/` root.
- **ADR-0037** (mcp-events.jsonl event schema): FR-4 honors the existing event types and adds no new ones.
- **ADR-0039** (credential redaction posture): FR-4 uses the existing `log_mcp_event` helper which implements redaction-at-source.
- **ADR-0040** (Serena narrowed always-on; precedent for the seven sub-agent allowlists): unchanged by this feature (NFR-15).
- **ADR-0041** (install-mechanism hybrid, v1.0.1): the canonical invocation prescription source FR-3 OP-11 compares `.mcp.json` against. This Blueprint annotates row 71 (`mcp-openapi-schema`) with `[DEPRECATED — removed 2026-05-24]`; this is an annotation, not a decision-text rewrite (see FR-3 design).
- **ADR-0042** (auditing-mcp family graduation): the OP-rule extension contract FR-3's new OP-11 follows.
- **ADR-0043** (auditing-mcp Gate-6 hard gate): the gate the new OP-11 rule inherits.
- **ADR-0044** (flatten execution dispatch hierarchy): the canonical source for `parent-driven-workaround` as a documented dispatch posture. ADR-0057 canonicalizes its on-disk surface.
- **ADR-0056** (no carve-outs in canonical placement): ADR-0057 lives at `adrs/` per this rule.

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|---|---|---|
| GitHub Actions runner | `ubuntu-latest` | Host for the FR-5 `mcp-connectivity-smoke.yml` workflow. |
| `devcontainers/ci` Action | `devcontainers/ci@<SHA>` (third-party; SHA pin REQUIRED at implementation) | Builds and runs the project's devcontainer image inside the FR-5 workflow. |
| `actions/checkout` Action | `actions/checkout@<SHA>` (first-party; major-version tag acceptable, SHA preferred) | Checks out the PR tree for FR-5. |
| Claude Code CLI | Pinned by the devcontainer's `claude-code` Feature | Provides `claude --bare -p` for the FR-5 invocation. Version pin discipline tracked as Q-CICD-1. |
| `gitnexus@1.6.5` npm package | Pinned via `GITNEXUS_TAG` in `.devcontainer/versions.env` | Subject of the FR-4 dry-run contract assertion. |
| Anthropic Agent SDK contracts | `system/init` event; `McpServerStatus` enum (`connected | failed | needs-auth | pending | disabled`) | The contract-bearing surface FR-5 consumes; documented at `https://code.claude.com/docs/en/agent-sdk/mcp` and `https://code.claude.com/docs/en/agent-sdk/typescript`. |

### Agreement Checklist

#### Scope
- [x] Verdict-vs-findings parity validator at the orchestrator's dispatch boundary (FR-1).
- [x] Orchestrator dispatch self-check at orchestrator entry (FR-2).
- [x] `auditing-mcp` OP-11 audit rule (FR-3) plus inline `[DEPRECATED]` annotation on ADR-0041 row 71.
- [x] GitNexus install dry-run inside `.devcontainer/postCreate.sh` (FR-4).
- [x] New CI workflow at `.github/workflows/mcp-connectivity-smoke.yml` (FR-5).
- [x] Cross-cutting actionable-diagnostic discipline across all five mechanisms (FR-6).
- [x] Deferral-register row tightening for B-1 and H-4 (FR-7).
- [x] One new ADR (ADR-0057) for the `checkpoint.execution_mode` schema-surface change.

#### Non-Scope (Explicitly not changing)
- [x] No new MCP server; no new MCP allowlist entry (NFR-15, ADR-0040).
- [x] No reviewer agent contract changes (the agents' `verdict` and `findings` shapes are read-only consumed by FR-1).
- [x] No `.mcp.json` content changes (read-only consumed by FR-3 and FR-5).
- [x] No ADR-0041 decision-text mutations (the marker is an annotation, not a rewrite).
- [x] No CLAUDE.md sentence additions beyond the single-character counter update `OP-1..OP-10` → `OP-1..OP-11`.
- [x] No patches to the still-broken MCP server files (PRD Product Policy Decisions row 4).
- [x] No expansion into the eight Won't-Have items deferred to the follow-on systemic-remediation feature.

#### Constraints
- [x] Parallel operation: Yes — all five mechanisms can coexist with the prior pipeline and with each other (NFR-11 per-mechanism isolation).
- [x] Backward compatibility: Required — applies to existing reviewer outputs (NFR-9), to `.mcp.json` entries already matching ADR-0041 (NFR-10), and to pre-feature `checkpoint.json` files lacking the new `execution_mode` field (per ADR-0057).
- [x] Performance measurement: Required for FR-5 pre-merge gate (D-0010); concrete thresholds set for NFR-1, NFR-2, NFR-3 per design.
- [x] Zero-downtime deployment: N/A — none of the mechanisms is a service.
- [x] Forward-compatible migration: Required for `checkpoint.json` — absence of `execution_mode` field on pre-feature checkpoints maps to `specialist-dispatch` (ADR-0057).

#### Applicable Standards
- [x] EARS acceptance-criteria format `[explicit]` — Source: KB-documentation-criteria `references/disciplines/ears-acceptance-criteria.md`.
- [x] OP-rule script naming `audit_op<N>_<short-descriptor>.py` `[explicit]` — Source: `.claude/skills/auditing-mcp/SKILL.md` (existing OP-1..OP-10 precedent).
- [x] OP-rule exit-code convention `0/1/2 = no-findings/blocker/internal-error` `[explicit]` — Source: existing audit_op*.py scripts under `auditing-mcp/scripts/`.
- [x] SHA-pinning of third-party GitHub Actions `[explicit]` — Source: KB-github-actions-platform non-negotiable #1.
- [x] Least-privilege `permissions:` blocks on workflows `[explicit]` — Source: KB-github-actions-platform non-negotiable #2.
- [x] `set -euo pipefail` shell posture `[implicit]` — Evidence: `.devcontainer/postCreate.sh:31`, `.devcontainer/postStart.sh`, `.devcontainer/lib/log-mcp-event.sh:15` — Confirmed: Yes.
- [x] Dual-stream diagnostic convention (plain-text echo + structured JSONL) `[implicit]` — Evidence: `.devcontainer/postCreate.sh` + `log_mcp_event` usage — Confirmed: Yes, adopted as the FR-6 surface convention for the Codespaces layer.

#### Quality Assurance Mechanisms

- [x] `actionlint` (binary or `mcp__actionlint-mcp__lint_workflow`) — Enforces: GitHub Actions YAML correctness, SHA-pinning, no-untrusted-input-interpolation — Config: KB-github-actions-platform — Covers: `.github/workflows/mcp-connectivity-smoke.yml` — Status: `adopted` (Plan task per cicd-design §Lint findings).
- [x] `auditing-mcp` Gate-6 hard gate per ADR-0043 — Enforces: OP-1..OP-11 rules on every pipeline run — Config: `.claude/skills/auditing-mcp/` — Covers: `.mcp.json` + ADR-0041 — Status: `adopted` (extended by FR-3).
- [x] `verdict_findings_parity.py` orchestrator-step gate (NEW) — Enforces: FR-1 verdict-vs-findings consistency — Config: `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` — Covers: 9 reviewer-completion invocation sites across 5 reviewer-shaped agents — Status: `adopted`.
- [x] Orchestrator dispatch self-check (NEW) — Enforces: FR-2 FULL-scope + parent-driven-workaround refusal — Config: `.claude/skills/recipe-feature-pipeline/SKILL.md` — Covers: every orchestrator entry — Status: `adopted`.
- [x] GitNexus contract assertion (NEW) — Enforces: FR-4 Signal 1 (stderr regex) + Signal 3 (artifact absence) on cache-miss installs — Config: inside `install_gitnexus()` in `.devcontainer/postCreate.sh` — Covers: every cache-miss devcontainer build — Status: `adopted`.
- [x] `mcp-connectivity-smoke.yml` (NEW) — Enforces: every server in `.mcp.json` reports `status: connected` from a freshly-provisioned devcontainer — Config: `.github/workflows/mcp-connectivity-smoke.yml` — Covers: PRs touching `.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**` — Status: `adopted`.

### Problem to Solve

The MCP incident shipped five of seven servers broken in production. The postmortem (captured in `Issues/cross-artifact-divergence-detection-gap/proposal.md`) traced the failure to a structural gap: each pipeline gate inspected its own artifact in isolation and never compared an ADR's prescription against the file that actually shipped. The full systemic remediation is deferred. This feature is the carve-out — five low-cost, locally scoped, mechanically bounded changes that together close roughly a third of the catalogued incident defects plus the single highest-risk deferral from the prior devcontainer-MCP feature's register.

Each change addresses one named failure mode:

- **FR-1**: a reviewer returning an "approved" verdict alongside a blocking finding silently propagated past the orchestrator.
- **FR-2**: an orchestrator dispatching FULL-scope work with a stage configured for single-agent fallback silently lost per-layer fan-out.
- **FR-3**: an MCP server's `.mcp.json` entry drifted from its ADR-0041 prescription without being flagged at any gate.
- **FR-4**: a Codespace install silently produced a half-working environment when an upstream env-var contract drifted.
- **FR-5**: a PR changing `.mcp.json` (or the devcontainer or an audit skill) merged with a server that no longer reached `connected` state.

### Current Challenges

The current pipeline has these specific structural gaps verified by Discovery:

- The `execute-task-quality-handler` agent's output contract today structurally allows `APPROVED` status alongside a `severity: blocker` finding (codebase-C-0018 verified).
- `scope_class` is read exactly once at line 350 of `recipe-feature-pipeline/SKILL.md`, inside Stage 13 (Deliverable Packaging) — too late for the FR-2 dispatch self-check to consume it (codebase-C-0028 verified).
- ADR-0041 still lists `mcp-openapi-schema` as one of seven invocation rows at line 71; `.mcp.json` removed it on 2026-05-24 leaving six servers (codebase-C-0038, codebase-C-0041, codebase-C-0105 verified). A naive symmetric-difference parity rule would emit a day-one BLOCKER false positive.
- The canonical Claude Code CLI docs are silent on `claude mcp list`'s exit-code and stdout-format contracts (t002-C-0001, t002-C-0002 verified) — a workflow that depends on the command's behavior depends on undocumented surface.
- GitNexus's `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var contract at the pinned v1.6.5 tag governs dart and proto only, not Swift, despite the upstream README's broader claim (t001-C-0022, t001-C-0038 verified).

### Requirements

#### Functional Requirements

- **FR-1** Verdict-vs-findings consistency check (Claude Code layer) — see PRD §FR-1.
- **FR-2** Orchestrator dispatch self-check refusing FULL-scope + single-agent-fallback (Claude Code layer) — see PRD §FR-2.
- **FR-3** `.mcp.json`-to-ADR-0041 parity audit rule OP-11 (Claude Code layer) — see PRD §FR-3.
- **FR-4** GitNexus install dry-run in devcontainer post-create (Codespaces layer) — see PRD §FR-4.
- **FR-5** CI workflow for MCP connectivity smoke (CI/CD layer) — see PRD §FR-5.
- **FR-6** Actionable diagnostics for every mechanism (cross-cutting) — see PRD §FR-6.
- **FR-7** Update deferral register to mark H-4 and B-1 adopted (Claude Code layer) — see PRD §FR-7.

#### Non-Functional Requirements

- **Performance**: FR-1 validator p95 ≤ 250 ms on ≤ 100 KB reviewer outputs (NFR-1 concrete threshold set by design-cc). FR-2 self-check p95 ≤ 100 ms (NFR-2). FR-4 assertion overhead p95 ≤ 2 s on the configured 4-CPU class (NFR-3 concrete threshold set by design-codespaces). FR-5 workflow p95 < 4 minutes (NFR-4); pre-merge validation gate confirms.
- **Reliability**: Determinism — same input produces same verdict twice in succession (NFR-5). Fail-closed on internal errors (NFR-6).
- **Security**: No new credential surface (NFR-7). No credentials in diagnostics (NFR-8).
- **Maintainability**: NFR-9 backward compatibility for existing reviewer outputs. NFR-10 backward compatibility for `.mcp.json` entries already matching ADR-0041.
- **Operability**: NFR-11 per-mechanism isolation (each mechanism exercisable end-to-end without the other four). NFR-13 compatibility with existing `mcp-events.jsonl` event schema (no new event types). NFR-14 Codespace boot cost bounded by NFR-3's threshold (no other devcontainer-layer additions). NFR-15 agent-driven workflow remains accessible (no MCP allowlist changes).

## Acceptance Criteria (AC) - EARS Format

Acceptance criteria are grouped by Functional Requirement; cross-layer/operational ACs follow.

### Functional ACs

#### FR-1 — Verdict-vs-findings parity validator — Layer: Claude Code

- [ ] **AC-CC-1-a** *(Event-driven)*: When the orchestrator detects that any of the 5 reviewer-shaped sub-agents in scope (across the 9 distinct invocation sites: 5 `shared-document-reviewer` ADR-0017 invocation points + Stage 8 architecture auditor + Stage 11 cross-artifact auditor + T7 phase-quality-reviewer + T2 execute-task-quality-handler) has written its verdict+findings output to disk, the system shall invoke `verdict_findings_parity.py` with the output path and the agent name before advancing to the next stage.
- [ ] **AC-CC-1-b** *(State-driven)*: If the validator's exit code is 1 and the agent's verdict is in the approving column for that agent and the findings array contains at least one finding with `severity` (case-insensitive) equal to `BLOCKER`, then the system shall halt orchestrator advance and surface the validator's JSON output to the user.
- [ ] **AC-CC-1-c** *(State-driven)*: Where the agent's verdict is not in the approving column for that agent, the system shall pass the reviewer output through unchanged regardless of finding severities.
- [ ] **AC-CC-1-d** *(State-driven)*: Where the agent's verdict is in the approving column and the findings array contains no finding with `severity` equal to `BLOCKER`, the system shall pass the reviewer output through unchanged.
- [ ] **AC-CC-1-e** *(Event-driven, NFR-6 fail-closed)*: When the validator returns exit 2, the system shall treat the run as failed-closed, emit the validator's stderr to the user, and require user resolution before any retry.
- [ ] **AC-CC-1-f** *(Ubiquitous, FR-6)*: The validator's JSON output shall always carry the four FR-6 fields (mechanism name, offending artifact path, rule violated, remedial-action hint).
- [ ] **AC-CC-1-g** *(Ubiquitous, NFR-5 determinism)*: When invoked twice on the same input file with the same agent name, the validator shall produce byte-identical stdout and the same exit code.
- [ ] **AC-CC-1-h** *(Ubiquitous, NFR-9 backward-compat)*: When the validator runs on any reviewer-shaped output that the prior pipeline accepted as conformant, the validator shall return exit 0.

#### FR-2 — Orchestrator dispatch self-check — Layer: Claude Code

- [ ] **AC-CC-2-a** *(Event-driven)*: When the orchestrator begins dispatch after Stage 1 (Intent Clarification) completes, the system shall read `scope_class` from `working/feature/<slug>/intent-clarification.md`'s frontmatter and enumerate every stage's `checkpoint.execution_mode` value (per ADR-0057's schema).
- [ ] **AC-CC-2-b** *(State-driven)*: If `scope_class == "FULL"` and any stage's `execution_mode == "parent-driven-workaround"`, then the system shall refuse to enter the dispatch loop, write a diagnostic to the orchestrator's surface stream, and exit non-zero.
- [ ] **AC-CC-2-c** *(State-driven)*: Where `scope_class` is `"MINOR"` or `"PATCH"`, the system shall permit any `execution_mode` value (including `parent-driven-workaround`) without raising a refusal.
- [ ] **AC-CC-2-d** *(Ubiquitous, FR-6)*: The refusal diagnostic shall always carry the four FR-6 fields.
- [ ] **AC-CC-2-e** *(Ubiquitous, NFR-5 determinism)*: When the orchestrator dispatch self-check runs twice in succession against the same `intent-clarification.md` and the same `checkpoint.json`, the system shall produce the same verdict and the same diagnostic both times.
- [ ] **AC-CC-2-f** *(Unwanted-behavior, NFR-6 fail-closed)*: If `intent-clarification.md` is missing or unparseable when the self-check needs to read it, the system shall treat the run as failed-closed and emit a diagnostic naming the missing-or-unparseable file, rather than skipping the self-check.
- [ ] **AC-CC-2-g** *(Ubiquitous, ADR-0057 backward-compat)*: When the self-check reads a `checkpoint.json` written before this feature shipped (i.e., a checkpoint whose stage records lack the `execution_mode` field), the system shall treat absence-of-field as equivalent to `execution_mode == "specialist-dispatch"`.

#### FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule OP-11 — Layer: Claude Code

- [ ] **AC-CC-3-a** *(Event-driven)*: When `audit_op11_adr_parity.py` is invoked against `.mcp.json`, the system shall iterate every server entry and, for each entry, locate the corresponding non-deprecated row in ADR-0041's invocation table.
- [ ] **AC-CC-3-b** *(State-driven)*: If the canonicalized live form does not equal the canonicalized prescribed form, then the system shall emit a BLOCKER finding naming the server, the prescribed form, the live form, and the diff dimension (`argv`, `env`, or `sentinel`).
- [ ] **AC-CC-3-c** *(State-driven)*: If ADR-0041 contains no non-deprecated row for a server present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-adr-0041`.
- [ ] **AC-CC-3-d** *(State-driven)*: If ADR-0041 contains a non-deprecated row whose server name is absent from `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-mcp.json`.
- [ ] **AC-CC-3-e** *(State-driven)*: Where ADR-0041 contains a row tagged `[DEPRECATED]` and the server is absent from `.mcp.json`, the system shall NOT emit a finding for that row.
- [ ] **AC-CC-3-f** *(Unwanted-behavior)*: If ADR-0041 contains a row tagged `[DEPRECATED]` and the server is present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: deprecated-row-still-present`.
- [ ] **AC-CC-3-g** *(Ubiquitous, NFR-10 backward-compat)*: When OP-11 runs on a `.mcp.json` entry whose canonicalized invocation form equals the canonicalized ADR-0041 prescription, the system shall produce no finding for that entry.
- [ ] **AC-CC-3-h** *(Ubiquitous, FR-6)*: Each finding shall always carry the four FR-6 fields.
- [ ] **AC-CC-3-i** *(Ubiquitous, NFR-5 determinism)*: When OP-11 runs twice on the same `.mcp.json` and the same ADR-0041, the system shall produce byte-identical stdout and the same exit code.
- [ ] **AC-CC-3-j** *(Ubiquitous, NFR-7 / NFR-8 no-credentials)*: The OP-11 rule shall not read any environment variable; the `${VAR}` placeholders shall be treated as opaque tokens both in canonicalization and in diagnostic output.
- [ ] **AC-CC-3-k** *(Unwanted-behavior, NFR-6 fail-closed)*: If ADR-0041 cannot be parsed or `.mcp.json` cannot be parsed, then the system shall return exit 2 with a diagnostic naming the parse failure.
- [ ] **AC-CC-3-l** *(Ubiquitous, NFR-13 event surface)*: When OP-11 runs, the system shall not write to `.claude/runtime/mcp-events.jsonl`.

#### FR-4 — GitNexus install dry-run — Layer: Codespaces

- [ ] **AC-CS-4-a** *(Event-driven, positive-assertion contract)*: When `.devcontainer/postCreate.sh` runs `install_gitnexus()` against a fresh (cache-miss) install at the pinned `GITNEXUS_TAG`, the system shall assert that the captured stderr matches the regex `\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)` at least once for each of `dart` and `proto`, AND that the paths `$(npm root -g)/gitnexus/node_modules/tree-sitter-dart/build/Release/tree_sitter_dart_binding.node` and `.../tree-sitter-proto/build/Release/tree_sitter_proto_binding.node` are both absent.
- [ ] **AC-CS-4-b** *(State-driven, failure halts the install)*: If either Signal 1 (stderr regex) or Signal 3 (artifact-path absence) fails its assertion, then the system shall (i) skip the sentinel `touch` so the next rebuild re-attempts the install, (ii) emit a `structured_failure` JSONL event via `log_mcp_event` whose `note:` field names FR-4, the pinned tag, the failing signal, and a one-line remedial hint, and (iii) return non-zero from `install_gitnexus()` so the existing `|| emit_degraded_banner` line trips.
- [ ] **AC-CS-4-c** *(State-driven, cached path unchanged)*: When the gitnexus sentinel is present AND `gitnexus` is on PATH at the pinned tag, the system shall fast-path through the existing sentinel check without running the dry-run assertions.
- [ ] **AC-CS-4-d** *(Unwanted-behavior, no Swift assertion)*: The system shall not assert any condition about `tree-sitter-swift`'s build outcome as a function of `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`.
- [ ] **AC-CS-4-e** *(Ubiquitous, no third sentinel)*: The system shall not introduce a third sentinel naming convention; the FR-4 dry-run shall be sentinel-less.
- [ ] **AC-CS-4-f** *(Event-driven, calibration opt-in)*: When the maintainer invokes the dedicated calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`, the system shall execute the negative-assertion path (set `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0`, install in a scratch directory, assert artifacts ARE built) and emit the result as a `structured_failure` or `install_complete` event; the per-rebuild flow in `postCreate.sh` shall not invoke this script.

#### FR-5 — MCP connectivity smoke workflow — Layer: CI/CD

This Blueprint reconciles the PRD's AC-FR-5-a/b/c (which literally name `claude mcp list`) with the design's contract-bearing substitute (`claude --bare -p "noop" --output-format stream-json | jq ...`) per Q-CICD-9 resolution below. The ACs below are rewritten to reference the substitute invocation; the behavioral intent is preserved verbatim. PRD Assumption A-3 is superseded — see "Q-CICD-9 disposition" in §Resolved cross-layer Q-items.

- [ ] **AC-CICD-5-a** *(Event-driven, reconciles PRD AC-FR-5-a)*: When a pull request modifies any file in the configured path-trigger set (`.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**`), the system shall run the `.github/workflows/mcp-connectivity-smoke.yml` workflow. The workflow shall build the project's devcontainer image and execute, inside that image, `claude --bare -p "noop" --output-format stream-json | jq` over the `system/init` event's `mcp_servers[]` array.
- [ ] **AC-CICD-5-b** *(State-driven, reconciles PRD AC-FR-5-b)*: If any server in the `mcp_servers[]` array reports `status != "connected"`, then the system shall fail the workflow job with a non-zero exit and surface the offending server names + their reported status in `$GITHUB_STEP_SUMMARY` per the FR-6 diagnostic format.
- [ ] **AC-CICD-5-c** *(State-driven, reconciles PRD AC-FR-5-c)*: When every server in the `mcp_servers[]` array reports `status == "connected"`, the system shall pass the workflow job and write a one-line confirmation to `$GITHUB_STEP_SUMMARY`.
- [ ] **AC-CICD-5-d** *(Event-driven, NFR-6 fail-closed)*: When `claude --bare -p` exits non-zero (the CLI itself failed), the system shall exit 2 from the workflow step and surface the failure to the user as an internal-error diagnostic distinguishable from the AC-CICD-5-b connectivity-fail case.
- [ ] **AC-CICD-5-e** *(Ubiquitous, FR-6)*: The `$GITHUB_STEP_SUMMARY` diagnostic on any failing run shall carry the four FR-6 fields.
- [ ] **AC-CICD-5-f** *(Ubiquitous, NFR-4 runtime budget)*: The workflow shall complete within 5 minutes (NFR-4 ceiling); the pre-merge validation gate per D-0010 confirms p95 ≤ 4 minutes before ship.
- [ ] **AC-CICD-5-g** *(Ubiquitous, NFR-7 / NFR-8 no credentials)*: The workflow shall not read any new secret; the workflow shall not emit any environment-variable value identified as a credential carrier in its diagnostics.

#### FR-6 — Actionable diagnostics — Layer: cross-cutting

- [ ] **AC-6-a** *(Ubiquitous, reconciles PRD AC-FR-6-a)*: When any of the five mechanisms (FR-1 to FR-5) emits a blocking diagnostic, the system shall include in the diagnostic at minimum: (1) the mechanism name, (2) the offending artifact path, (3) the rule or contract violated, and (4) a one-line remedial-action hint. The exact surface differs by layer (JSON-to-stdout for the orchestrator-side mechanisms FR-1/FR-2/FR-3; plain-text echo + structured JSONL for the Codespaces-side FR-4; Markdown to `$GITHUB_STEP_SUMMARY` for the CI/CD-side FR-5), but the four fields are always present.

#### FR-7 — Deferral-register tightening — Layer: Claude Code

The placement of FR-7's verification step is fixed by composer arbitration of Q-CC-5: the verification lives in the deliverable-archive commit (synthesis D-0009 recommendation adopted). The `-alt` placement variants in cc-design are NOT activated.

- [ ] **AC-CC-7-a** *(Event-driven)*: When the feature reaches the deliverable-archive step, the system shall verify that `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` row B-1 carries the exact parenthetical `*(ADOPTED 2026-05-25 by pipeline-quickwins-hardening-r1 — see Issues/cross-artifact-divergence-detection-gap/proposal.md)*` in the Item cell.
- [ ] **AC-CC-7-b** *(Event-driven)*: When the feature reaches the deliverable-archive step, the system shall verify that row H-4 carries the same parenthetical (same date / slug / link tokens).
- [ ] **AC-CC-7-c** *(State-driven)*: If either row's parenthetical is missing or differs from the canonical form, the system shall update the row to match.
- [ ] **AC-CC-7-d** *(State-driven)*: If either row's Why-excluded / Re-examination-trigger / Forgetting-risk cells do not carry the canonical post-adoption text ("Now adopted: ...", "Adopted by <slug>.", "Resolved by adoption."), the system shall update those cells.

### Cross-Layer / Operational ACs

- [ ] **AC-X-1** *(Event-driven, NFR-11 per-mechanism isolation)*: When any single mechanism (FR-1, FR-2, FR-3, FR-4, FR-5) is enabled in isolation against a workspace where the other four are disabled, the system shall produce the mechanism's expected behavior for its named failure mode without depending on the others being enabled.
- [ ] **AC-X-2** *(Ubiquitous, NFR-13 event surface)*: When FR-3, FR-4, or FR-5 runs against a workspace with the existing MCP event surface enabled, the system shall not write any event of a type not already defined in ADR-0037 to `.claude/runtime/mcp-events.jsonl`.
- [ ] **AC-X-3** *(Ubiquitous, NFR-15 allowlists)*: This feature shall not modify the seven sub-agents' MCP allowlists per ADR-0040.

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | Existing | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Parent orchestrator (629 lines); subject of FR-1 wire-in and FR-2 self-check additions |
| Claude Code | Existing | `.claude/skills/auditing-mcp/` | Audit skill family-coordinator per ADR-0042; extended by FR-3 with OP-11 |
| Claude Code | Existing | `.claude/skills/auditing-shared/scripts/` | Python validator family; gains `verdict_findings_parity.py` for FR-1 |
| Claude Code | Existing | `.claude/agents/{shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor, execute-phase-quality-reviewer, execute-task-quality-handler}.md` | The 5 reviewer-shaped agents whose output FR-1 validates; unchanged |
| Claude Code | Existing | `.mcp.json` | Six MCP server registrations; read-only consumed by FR-3 and FR-5 |
| Claude Code | Existing | `adrs/ADR-0041-install-mechanism-hybrid.md` | Canonical invocation prescription; gains `[DEPRECATED]` annotation on row 71 (FR-3) |
| Claude Code | Existing | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` | Verified and tightened by FR-7 |
| Claude Code | Existing | `CLAUDE.md` | Single-character counter update (`OP-1..OP-10` → `OP-1..OP-11`) at deliverable-archive time |
| Claude Code | New | `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` | FR-1 validator |
| Claude Code | New | `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` | FR-3 OP-11 audit rule |
| Claude Code | New | `.claude/skills/auditing-mcp/references/adr-parity.md` | FR-3 rationale + canonicalization rules + `[DEPRECATED]` convention |
| Claude Code | New | `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md` | ADR-0057 (authored by this Blueprint's design-composer pass) |
| Codespaces | Existing | `.devcontainer/postCreate.sh` | Subject of FR-4 assertion insertion (inside `install_gitnexus()`) |
| Codespaces | Existing | `.devcontainer/versions.env` | Source of `GITNEXUS_TAG=1.6.5` and `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` |
| Codespaces | Existing | `.devcontainer/lib/log-mcp-event.sh` | The `log_mcp_event` helper FR-4 uses to emit `structured_failure` / `install_complete` events |
| Codespaces | New | `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` | FR-4 opt-in calibration script (AC-CS-4-f) |
| CI/CD | New | `.github/workflows/mcp-connectivity-smoke.yml` | FR-5 workflow (greenfield — first workflow in this project) |

### Integration Points (Include even for new implementations)

- **Integration Target**: the orchestrator (`recipe-feature-pipeline`) is the single dispatch nexus per ADR-0044; FR-1, FR-2, and ADR-0057's new field all integrate here.
- **Invocation Method**: orchestrator-internal `python3` calls for FR-1; orchestrator-internal logic for FR-2; standard OP-rule invocation per ADR-0042 / Gate-6 per ADR-0043 for FR-3; standard devcontainer post-create flow for FR-4; standard `pull_request` paths-filtered trigger for FR-5.

### Code Inspection Evidence

| File/Function | Relevance |
|---|---|
| `.claude/skills/recipe-feature-pipeline/SKILL.md:350` | Current `scope_class` read site; FR-2 hoists to post-Stage-1 (codebase-C-0028) |
| `.claude/agents/execute-task-quality-handler.md:33-46` | Verdict + findings shape (`status: APPROVED|...`, `findings[]: {severity: blocker|...}`); structurally permits APPROVED + severity:blocker co-occurrence (codebase-C-0018) |
| `.claude/agents/review-architecture-auditor.md:135-137` | Canonical severity → verdict mapping; load-bearing for the FR-1 `conditional_pass`-is-approving rationale (codebase-C-0017) |
| `adrs/ADR-0041-install-mechanism-hybrid.md:68-71` | Invocation taxonomy table including the `mcp-openapi-schema` row that FR-3 annotates as `[DEPRECATED]` (codebase-C-0041, codebase-C-0105) |
| `.devcontainer/postCreate.sh:131-152` | `install_gitnexus()` function — the FR-4 assertion-insertion site (between `npm install -g` at line 142 and the sentinel `touch` at line 143) |
| `.devcontainer/postCreate.sh:5,9,158` | The "5 vs 4" head-comment inconsistency surfaced as Q-CS-3 (codebase-analysis known-issues row 3) — composer disposition below |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md:56,141` | Rows B-1 and H-4 already carry the adoption parenthetical inline; FR-7 verifies-and-tightens |
| `CLAUDE.md:9` | Existing project posture: `mcp-openapi-schema was removed 2026-05-24 ... that's a stale-doc issue, not an active server` — load-bearing for the FR-3 `[DEPRECATED]` marker rationale (codebase-C-0110) |

### Fact Disposition Table

The codebase analysis surfaced facts across `components`, `dependencies`, `blast_radius`, `conventions`, `known_issues`, `scope_completeness_finding`, `deprecation_finding`, and `open_questions_for_human`. Each is disposed below.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---------|------------|-------------|-----------|----------|
| C-COMP-01 | `shared-document-reviewer` verdict shape | preserve | FR-1 reads the existing verdict shape; no agent contract changes | codebase-analysis components row 1; per-agent verdict mapping table in cc-design |
| C-COMP-02 | `review-architecture-auditor` verdict shape + canonical severity-to-verdict mapping (lines 135-137) | preserve | FR-1 relies on the existing deterministic severity-to-verdict mapping to justify `conditional_pass`-as-approving | codebase-analysis components row 2; cc-design FR-1 |
| C-COMP-03 | `review-cross-artifact-auditor` dual-verdict payload (primary + convergence) | transform | FR-1 inspects the primary verdict only; the convergence verdict is documented as out-of-scope for parity checking | codebase-analysis components row 3; cc-design FR-1 reviewer scope |
| C-COMP-04 | `execute-phase-quality-reviewer` 5-dimensional verdict | preserve | FR-1 reads the existing `verdict` field per Contract 2 | codebase-analysis components row 4 |
| C-COMP-05 | `execute-task-quality-handler` APPROVED + severity:blocker co-occurrence permitted | transform | FR-1 closes this structural gap via the validator (the agent's contract is unchanged; the gate is added downstream) | codebase-analysis components row 6; scope_completeness_finding |
| C-COMP-06 | `finalize-deliverable-packager` chained findings | out-of-scope | Per D-0002: the upstream `shared-document-reviewer` invocation already passes FR-1; re-checking is redundant | codebase-analysis scope_completeness_finding; cc-design FR-1 reviewer-scope table |
| C-COMP-07 | `synth-critic` per-claim verdicts | out-of-scope | Per D-0002: shape is verdict-per-claim, not verdict-per-invocation; structurally different contract | codebase-analysis scope_completeness_finding |
| C-COMP-08 | `synth-framer`, `synth-synthesizer`, `finalize-reconciler` use-but-don't-emit verdicts | out-of-scope | Per D-0002: no verdict + findings emission contract | codebase-analysis scope_completeness_finding agents_with_verdict_keyword_but_clearer_exclusion |
| C-COMP-09 | `recipe-feature-pipeline` parent orchestrator (629 lines, 19 shared-doc-reviewer call sites) | transform | FR-1 wire-in at 9 reviewer-completion invocation sites; FR-2 dispatch self-check + scope_class hoist; ADR-0057 schema-field write | codebase-analysis components row 11 |
| C-COMP-10 | `execute-orchestrator` advisor (non-invocable per ADR-0044) | preserve | Not on the FR-2 self-check enumeration surface (the parent recipe is) | codebase-analysis components row 12 |
| C-COMP-11 | `auditing-mcp` family-coordinator + 10 OP scripts | transform | FR-3 adds OP-11 following the existing contract; SKILL.md routing-table entry; new `references/adr-parity.md` | codebase-analysis components row 13 |
| C-COMP-12 | `.mcp.json` six servers (no `mcp-openapi-schema`) | preserve | Read-only consumed by FR-3 and FR-5; no edits | codebase-analysis components row 14 |
| C-COMP-13 | `.devcontainer/postCreate.sh` `install_gitnexus()` at lines 131-152 | transform | FR-4 inserts the assertion block between line 142 and line 143 | codebase-analysis components row 15 |
| C-COMP-14 | `.devcontainer/versions.env` GITNEXUS_TAG=1.6.5 + other pins | preserve | FR-4 reads `GITNEXUS_TAG` only; no edits to versions.env | codebase-analysis components row 16 |
| C-COMP-15 | `.devcontainer/lib/log-mcp-event.sh` (ADR-0037 schema + ADR-0039 redaction) | preserve | FR-4 uses the existing helper as-is | codebase-analysis components row 17 |
| C-COMP-16 | `.github/workflows/` greenfield directory | transform | FR-5 creates `mcp-connectivity-smoke.yml` as the first workflow | codebase-analysis components row 18 |
| C-COMP-17 | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` rows B-1, H-4 inline adoption parentheticals | transform | FR-7 verifies-and-tightens; existing markers already in place per codebase-analysis | codebase-analysis components row 19 |
| C-COMP-18 | `Issues/cross-artifact-divergence-detection-gap/proposal.md` (adopted status) | preserve | Read-only seed proposal; no edits | codebase-analysis components row 20 |
| C-COMP-19 | `adrs/ADR-0041-install-mechanism-hybrid.md` (v1.0.1, seven invocation rows) | transform | FR-3 annotates row 71 inline with `[DEPRECATED — removed 2026-05-24]`; decision-text preserved verbatim | codebase-analysis components row 21; cc-design FR-3 |
| C-DEP-01 | Recipe → reviewer call counts (19/4/4/5/3/2) | preserve | FR-1 wire-in does not remove call sites; it adds a downstream validator invocation after each | codebase-analysis dependencies rows 1-7 |
| C-DEP-02 | `.mcp.json` → env-var dependencies (CONTEXT7_API_KEY, EXA_API_KEY, GITNEXUS_TAG, TFE_TOKEN) | preserve | Read-only consumed | codebase-analysis dependencies row 8 |
| C-DEP-03 | `postCreate.sh` → versions.env / log-mcp-event.sh / mcp-events.jsonl | preserve | FR-4 reuses; no new edges | codebase-analysis dependencies rows 9-11 |
| C-DEP-04 | `auditing-mcp/audit_mcp.py` → 10 OP scripts | transform | FR-3 adds the OP-11 edge | codebase-analysis dependencies row 12 |
| C-DEP-05 | ADR-0041 ↔ `.mcp.json` (7-row vs 6-server divergence) | transform | FR-3 makes the parity edge explicit and inspectable; the `[DEPRECATED]` annotation resolves the day-one false positive | codebase-analysis dependencies row 13; deprecation_finding |
| C-DEP-06 | 7 sub-agents with `mcp__*` allowlists per ADR-0040 | preserve | NFR-15 invariant; no allowlist changes | codebase-analysis dependencies row 14 |
| C-BR-01 | `shared-document-reviewer` blast radius (medium) | preserve | Validator is shape-additive, not shape-changing | codebase-analysis blast_radius row 1 |
| C-BR-02 | `review-architecture-auditor` blast radius (low) | preserve | Single-stage reviewer; FR-1 wire-in is local | codebase-analysis blast_radius row 2 |
| C-BR-03 | `review-cross-artifact-auditor` blast radius (medium, dual-verdict) | transform | Validator inspects primary verdict only (documented decision per cc-design FR-1) | codebase-analysis blast_radius row 3 |
| C-BR-04 | `execute-phase-quality-reviewer` blast radius (low) | preserve | Single-stage T7 transition | codebase-analysis blast_radius row 4 |
| C-BR-05 | `recipe-feature-pipeline` FR-2 self-check site (high blast) | transform | Single edit point (orchestrator entry); ADR-0057 canonicalizes the configuration surface | codebase-analysis blast_radius row 5 |
| C-BR-06 | `auditing-mcp` FR-3 host blast (low) | preserve | Additive new OP rule | codebase-analysis blast_radius row 6 |
| C-BR-07 | `.devcontainer/postCreate.sh` FR-4 host blast (medium) | transform | Assertion insertion + opt-in calibration script | codebase-analysis blast_radius row 7 |
| C-BR-08 | `.github/workflows/` FR-5 greenfield (low blast, medium precedent) | transform | First workflow; convention-setting documented in cicd-design | codebase-analysis blast_radius row 8 |
| C-BR-09 | `.mcp.json` FR-3+FR-5 probed artifact (medium; read-only) | preserve | Read-only consumed | codebase-analysis blast_radius row 9 |
| C-CONV-01 | CC conventions (file naming, frontmatter, verdict emission, severity taxonomy, logging, testing, report-only-vs-enforcing, ADR-authoring per FR-5) | preserve | All inherited unchanged | codebase-analysis conventions.cc |
| C-CONV-02 | auditing-mcp conventions (OP-N naming, script_naming, script_contract, finding_format, rationale_placement) | preserve | FR-3's OP-11 follows the established pattern | codebase-analysis conventions.auditing-mcp |
| C-CONV-03 | Codespaces conventions (shell_posture, sentinel_naming, idempotency, event_emission, diagnostic_format) | preserve | FR-4 honors all conventions; sentinel-less by design (per AC-CS-4-e) | codebase-analysis conventions.codespaces |
| C-CONV-04 | CI/CD conventions (GREENFIELD; KB-governed defaults) | transform | FR-5 establishes the project's first workflow convention; documented in cicd-design §Convention this layer establishes | codebase-analysis conventions.cicd |
| C-CONV-05 | deferral_register_row_update convention | preserve | FR-7 verifies-and-tightens against this convention | codebase-analysis conventions.documents.deferral_register_row_update |
| C-KI-01 | `execute-orchestrator` documented-as-advisor-but-carries-full-frontmatter | out-of-scope | Cosmetic; FR-2 enumerates by `execution_mode` field per ADR-0057, not by agent-frontmatter inspection | codebase-analysis known_issues row 1 |
| C-KI-02 | Sentinel naming inconsistency (ADR-0041 canonical vs live postCreate.sh form) | preserve (intentionally untouched) | Q-CS-2 disposition: surface as deferred-issue row in the register; this feature does NOT introduce a third sentinel format | codebase-analysis known_issues row 2; cc-design + codespaces-design |
| C-KI-03 | "5 vs 4 servers" cosmetic head-comment drift in `postCreate.sh` lines 5/9/158 | transform | Q-CS-3 disposition: fix the stray "5" in line 5 in the same FR-4 commit; one-line cosmetic edit | codebase-analysis known_issues row 3 |
| C-SCF-01 | scope_completeness_finding (FR-1 reviewer sweep) | transform | D-0002 inclusion list adopted: include `execute-task-quality-handler`; exclude `finalize-deliverable-packager`, `synth-critic`, `synth-framer`, `synth-synthesizer`, `finalize-reconciler` | codebase-analysis scope_completeness_finding |
| C-DF-01 | deprecation_finding (mcp-openapi-schema in ADR-0041 row 71 but absent from `.mcp.json`) | transform | D-0005 in-rule `[DEPRECATED]` marker convention; the annotation is recorded as an in-rule edit, not an ADR decision-text rewrite | codebase-analysis deprecation_finding; cc-design FR-3 |
| C-OQ-01 | Open question: FR-1 reviewer inclusion | resolved | Per D-0002 — see C-SCF-01 row | codebase-analysis open_questions_for_human row 1 |
| C-OQ-02 | Open question: FR-3 mcp-openapi-schema handling | resolved | Per D-0005 — see C-DF-01 row | codebase-analysis open_questions_for_human row 2 |
| C-OQ-03 | Open question: FR-2 self-check location + scope_class surface | resolved | Per D-0003 (refined per Q-CC-6): post-Stage-1 hoist; ADR-0057 introduces `checkpoint.execution_mode` as first-class field | codebase-analysis open_questions_for_human row 3 |
| C-OQ-04 | Open question: FR-4 sentinel handling | resolved | Per codespaces-design AC-CS-4-e: sentinel-less | codebase-analysis open_questions_for_human row 4 |
| C-OQ-05 | Open question: FR-7 existing partial markers | resolved | Per cc-design FR-7: confirmation-and-tightening, not authoring | codebase-analysis open_questions_for_human row 5 |

## Design

### Change Impact Map

```yaml
Change Target: Pipeline quick-wins hardening — verdict-parity validator, dispatch self-check, .mcp.json↔ADR-0041 parity audit, GitNexus install dry-run, MCP connectivity CI smoke, deferral-register tightening
Direct Impact:
  frontend: N/A — out of scope
  backend: N/A — out of scope
  api: N/A — out of scope
  query: N/A — out of scope
  database: N/A — out of scope
  cicd:
    - .github/workflows/mcp-connectivity-smoke.yml (NEW)
  iac: N/A — out of scope
  codespaces:
    - .devcontainer/postCreate.sh (MODIFIED — FR-4 assertion inside install_gitnexus())
    - .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh (NEW)
  claude_code:
    - .claude/skills/recipe-feature-pipeline/SKILL.md (MODIFIED — FR-1 wire-in at 9 invocation sites; FR-2 self-check at orchestrator entry; scope_class hoist from line 350; checkpoint.execution_mode schema documentation per ADR-0057)
    - .claude/skills/auditing-shared/scripts/verdict_findings_parity.py (NEW)
    - .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py (NEW)
    - .claude/skills/auditing-mcp/SKILL.md (MODIFIED — routing-table entry for OP-11; pedagogical_sections frontmatter update)
    - .claude/skills/auditing-mcp/references/adr-parity.md (NEW)
    - adrs/ADR-0041-install-mechanism-hybrid.md (ANNOTATED — [DEPRECATED — removed 2026-05-24] on row 71 only; decision-text preserved verbatim)
    - adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md (NEW — authored by this Blueprint)
    - Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md (VERIFIED-AND-TIGHTENED — FR-7)
    - CLAUDE.md (MODIFIED — single-character counter update OP-1..OP-10 → OP-1..OP-11)
Indirect Impact:
  - checkpoint.json schema gains documented execution_mode field per ADR-0057 (orchestrator-internal; resume-handling honors absence-as-specialist-dispatch)
  - .github/workflows/ becomes the convention-setting precedent for future workflows (cicd-design §Convention this layer establishes)
  - Cosmetic "5→4 servers" fix in postCreate.sh:5 (per Q-CS-3 disposition)
No Ripple Effect:
  - The 7 sub-agents' MCP allowlists (NFR-15)
  - The 5 reviewer-shaped agents' contracts (FR-1 reads; does not modify)
  - .mcp.json contents (read-only consumed by FR-3 and FR-5)
  - ADR-0041's decision text (only an inline marker added)
  - .claude/runtime/mcp-events.jsonl event types (NFR-13)
  - The 7 servers' install mechanisms (no patching per PRD Product Policy Decisions row 4)
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|---|---|---|---|
| Implicit dispatch posture in orchestrator | `checkpoint.execution_mode` documented field (enum: `specialist-dispatch`, `parent-driven-workaround`) per ADR-0057 | No conversion of existing checkpoints | Absence-equals-`specialist-dispatch` default on resume (ADR-0057 + AC-CC-2-g) |
| Reviewer verdict + findings output (5 agents) | Same shape, now gated by `verdict_findings_parity.py` downstream | No | Validator is shape-additive (NFR-9 + AC-CC-1-h) |
| `auditing-mcp` OP-1..OP-10 rule contract | OP-11 follows the same contract (one positional arg, JSON stdout, exit 0/1/2) | No | Inherits Gate-6 hard-gate per ADR-0043 |
| ADR-0041 invocation table (7 rows) | Same 7 rows; row 71 annotated `[DEPRECATED — removed 2026-05-24]` | No | Inline annotation; decision-text preserved verbatim (ADR-0005 append-only honored) |
| `install_gitnexus()` `npm install -g` redirects stderr to `/dev/null` | Same install captures stderr to a temp file for Signal 1 evaluation | No | Same exit-0-on-pass; warn-and-continue via `\|\| emit_degraded_banner` on signal failure |
| `.github/workflows/` empty | One new workflow file `mcp-connectivity-smoke.yml` | No | Greenfield — no compatibility surface |
| `claude mcp list` per PRD literal | `claude --bare -p "noop" --output-format stream-json \| jq` per design substitution | Reconciled at Blueprint time | AC-FR-5-a/b/c rewritten as AC-CICD-5-a/b/c; PRD Assumption A-3 superseded — see Q-CICD-9 disposition |

### Architecture Overview

The system under change is the feature-pipeline itself: a sequence of Claude Code sub-agents orchestrated by the `recipe-feature-pipeline` SKILL.md. The feature adds five non-overlapping gates and one schema field to that pipeline, plus one CI workflow that runs against the project's devcontainer image.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                  Feature-pipeline orchestrator (recipe-feature-pipeline)        │
│                                                                                 │
│  Stage 1 ────► [FR-2: dispatch self-check]  scope_class read; refuse if FULL+   │
│   Intent       checkpoint.execution_mode == parent-driven-workaround            │
│                (ADR-0057 introduces the field)                                  │
│                                                                                 │
│  Stages 2-12 ──► reviewer-shaped agents emit verdict+findings JSON              │
│                                                                                 │
│  At each of 9 reviewer-completion sites:                                        │
│   [FR-1: verdict_findings_parity.py]  refuses APPROVED + severity:BLOCKER        │
│                                                                                 │
│  Stage 6 audit gate (per ADR-0043):                                             │
│   [FR-3: audit_op11_adr_parity.py]  refuses .mcp.json ↔ ADR-0041 drift           │
│                                                                                 │
│  Stage 13 Deliverable Packaging:                                                │
│   scope_class consumed from checkpoint (hoisted from line 350)                  │
│   [FR-7: register row B-1/H-4 verification + tightening]                        │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                       Devcontainer (.devcontainer/postCreate.sh)                │
│                                                                                 │
│  install_gitnexus() — cache-miss path:                                          │
│    npm install -g gitnexus@${GITNEXUS_TAG}  (stderr captured to temp file)      │
│    [FR-4: Signal 1 stderr regex + Signal 3 artifact-absence]                    │
│    Pass: touch sentinel; emit install_complete                                  │
│    Fail: skip sentinel; emit structured_failure; return non-zero                │
│  Sentinel-present path: fast-path (no assertions)                               │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                    GitHub Actions (.github/workflows/)                          │
│                                                                                 │
│  on: pull_request paths=[.mcp.json, .devcontainer/**, adrs/ADR-0041-*.md,       │
│                            .claude/skills/auditing-mcp/**]                       │
│  jobs.smoke (runs-on: ubuntu-latest; timeout-minutes: 8):                       │
│    devcontainers/ci@<SHA>  (builds devcontainer image)                          │
│      → claude --bare -p "noop" --output-format stream-json                       │
│      → jq filter .type=="system".subtype=="init".mcp_servers[].status!="connected"│
│      Empty → PASS; Non-empty → FAIL with FR-6 diagnostic in $GITHUB_STEP_SUMMARY │
└────────────────────────────────────────────────────────────────────────────────┘
```

The three layer-specific surfaces are loosely coupled: the orchestrator's FR-1/FR-2/FR-3 don't depend on the devcontainer's FR-4 to ship; the CI's FR-5 runs against the devcontainer image FR-4 modifies, but only inherits it (FR-5 doesn't parse FR-4's output). All five mechanisms can ship in isolation per NFR-11.

### Data Flow

```
Reviewer-shaped agent (e.g., shared-document-reviewer at Gate 1 of PRD review):
  emit reviewer-output.json {verdict: <enum>, findings: [{severity: <enum>, ...}, ...]}
      │
      ▼
Orchestrator detects reviewer-output written to disk
      │
      ▼
[FR-1] Invoke `python3 verdict_findings_parity.py <path> <agent-name>`
      │
      ├─ exit 0 ──► proceed to next stage
      ├─ exit 1 ──► halt; surface JSON diagnostic to user (FR-6-shaped)
      └─ exit 2 ──► fail-closed; surface stderr; require user resolution


Orchestrator entry (every run, every feature):
  Run Stage 1 (Intent Clarification)
      │
      ▼
[FR-2] Read scope_class from intent-clarification.md frontmatter
       Enumerate every stage's checkpoint.execution_mode (per ADR-0057)
      │
      ├─ scope_class in {MINOR, PATCH} ────────────────────► proceed
      ├─ scope_class == FULL && all execution_mode == "specialist-dispatch" ──► proceed
      └─ scope_class == FULL && any execution_mode == "parent-driven-workaround"
                                                     ──► refuse; FR-6 diagnostic; exit non-zero


Audit gate (Gate 6 per ADR-0043, every pipeline run):
  Invoke auditing-mcp/scripts/audit_mcp.py coordinator
      │
      ├─ OP-1 .. OP-10 (existing) ──► each produces findings JSON
      └─ [FR-3] OP-11: invoke `python3 audit_op11_adr_parity.py .mcp.json`
                Canonicalize each .mcp.json entry; compare to non-deprecated ADR-0041 row
                Emit BLOCKER findings on argv/env/sentinel diff, missing-in-either-side, or
                deprecated-row-still-present
      │
      ▼
  Gate-6 collector — any BLOCKER → halt pipeline


Devcontainer cache-miss rebuild:
  install_gitnexus() ──► npm install -g gitnexus@${GITNEXUS_TAG} (stderr → temp file)
      │
      ▼
[FR-4] Signal 1: grep stderr for \[tree-sitter-(dart|proto)\] Skipping build (at least one per grammar)
       Signal 3: stat $(npm root -g)/gitnexus/node_modules/tree-sitter-{dart,proto}/build/Release/...
      │
      ├─ Signal 1 AND Signal 3 ─► touch sentinel; emit install_complete{status: ok, note: "contract assertion passed"}
      └─ Either fails ─► skip sentinel; emit structured_failure{note: FR-4 ...}; return non-zero


PR opened touching one of {.mcp.json, .devcontainer/**, adrs/ADR-0041-*.md, .claude/skills/auditing-mcp/**}:
  GitHub Actions ──► mcp-connectivity-smoke.yml
      │
      ▼
  actions/checkout@<SHA>
      │
      ▼
  devcontainers/ci@<SHA> { runCmd: ... }
      │
      ▼
[FR-5] claude --bare -p "noop" --output-format stream-json > $OUTPUT
       BAD=$(jq -c 'select(.type=="system" and .subtype=="init") | .mcp_servers[]? | select(.status != "connected") | {name, status}' < $OUTPUT)
      │
      ├─ $BAD empty ──► exit 0; PASS summary to $GITHUB_STEP_SUMMARY
      ├─ $BAD non-empty ──► exit 1; FR-6 FAIL summary naming each server + status
      └─ claude --bare -p exited non-zero ──► exit 2; INTERNAL-ERROR summary
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|---|---|---|---|---|---|
| Reviewer-output → orchestrator advance | `recipe-feature-pipeline/SKILL.md` at each reviewer-completion site | Unchecked passthrough | Validator-gated advance (FR-1) | Inline orchestrator step | Run validator on known-good and known-bad reviewer-output JSON fixtures |
| Orchestrator entry | `recipe-feature-pipeline/SKILL.md` | No dispatch self-check | Dispatch self-check after Stage 1 (FR-2) | Inline orchestrator step | Run pipeline twice: once with FULL + parent-driven-workaround (should refuse); once with FULL + specialist-dispatch (should proceed) |
| `auditing-mcp` Gate-6 dispatch | `.claude/skills/auditing-mcp/scripts/audit_mcp.py` | OP-1..OP-10 only | OP-1..OP-11 (FR-3 OP-11 added) | Coordinator includes new script | Run against current `.mcp.json`/ADR-0041 (expect no findings post-DEPRECATED-marker); against drift fixture (expect BLOCKER) |
| `install_gitnexus()` | `.devcontainer/postCreate.sh:131-152` | npm install -g (stderr to /dev/null); touch sentinel | npm install -g (stderr to temp); Signal 1 + Signal 3 assertions; touch sentinel iff both pass | Inline assertion block + temp-file redirection | Cache-miss rebuild: assertions evaluate; cache-hit rebuild: fast-path |
| PR check | `.github/workflows/` (greenfield) | No workflow | `mcp-connectivity-smoke.yml` | GitHub Actions `pull_request` trigger | Pre-merge validation gate (D-0010): three workflow_dispatch runs against draft branch confirming p95 < 4 min |
| ADR-0041 ↔ `.mcp.json` parity surface | `adrs/ADR-0041-install-mechanism-hybrid.md` row 71 + `.mcp.json` | Implicit; not gated | Annotated `[DEPRECATED — removed 2026-05-24]` on row 71; OP-11 reads the marker | Inline annotation + OP-11 rule | OP-11 fixture test under `auditing-mcp/tests/op11_smoke/` per OI-CC-2 |
| `checkpoint.json` schema | orchestrator-internal | Implicit dispatch posture | First-class `execution_mode` field per ADR-0057 | Orchestrator writes field at dispatch time; absence-as-default on resume | Resume a pre-feature checkpoint and confirm it does NOT trip FR-2 refusal (AC-CC-2-g) |

### Main Components

#### `verdict_findings_parity.py` (FR-1)

- **Responsibility**: Inspect a reviewer-emitted JSON for the contradiction "approving verdict + finding with severity in the blocking set."
- **Interface**: CLI script. Args: `<reviewer-output.json>` `<agent-name>`. Exit codes 0/1/2. Stdout: JSON `{mechanism, agent, verdict, blocking_findings, diagnostic, remediation}`.
- **Dependencies**: Python stdlib only. No MCP, no env vars beyond runtime PATH.

#### Orchestrator dispatch self-check (FR-2)

- **Responsibility**: Refuse the dispatch loop when `scope_class == FULL` and any stage's `execution_mode == parent-driven-workaround`.
- **Interface**: Orchestrator-internal logic at orchestrator entry (after Stage 1). Inputs: `intent-clarification.md` frontmatter, `checkpoint.json` per-stage `execution_mode` field. Outputs: pass-through OR refusal with FR-6-shaped diagnostic.
- **Dependencies**: ADR-0057 schema; the hoisted `scope_class` read site.

#### `audit_op11_adr_parity.py` (FR-3)

- **Responsibility**: Iterate every `.mcp.json` server entry and compare its canonicalized invocation form against the canonicalized non-deprecated ADR-0041 prescription.
- **Interface**: CLI script. Args: `<path-to-.mcp.json>` (ADR-0041 path resolved relative to repo root). Exit codes 0/1/2. Stdout: JSON `{rule, name, target, findings[], servers_checked, adr_servers_recognized, deprecated_rows_skipped}`.
- **Dependencies**: Python stdlib only. Inline ADR-table parser (per Q-CC-3 disposition).

#### `install_gitnexus()` assertion block (FR-4)

- **Responsibility**: After a cache-miss `npm install -g`, assert Signal 1 (stderr regex) + Signal 3 (artifact-path absence). On fail, emit `structured_failure` and skip sentinel.
- **Interface**: Inline shell block inside `install_gitnexus()` between line 142 and line 143. Inputs: captured stderr + post-install filesystem state. Outputs: `install_complete` (status ok) or `structured_failure` events to `mcp-events.jsonl`.
- **Dependencies**: `log_mcp_event` helper; `grep`; `test -f`.

#### `mcp-connectivity-smoke.yml` (FR-5)

- **Responsibility**: On PRs touching the configured paths, build the devcontainer image and assert every server in `.mcp.json` reports `status: connected` from `system/init`.
- **Interface**: GitHub Actions workflow. Trigger: `pull_request` paths-filtered + `workflow_dispatch`. Runner: `ubuntu-latest`. Timeout: 8 minutes. Permissions: `contents: read`.
- **Dependencies**: `actions/checkout@<SHA>` (first-party); `devcontainers/ci@<SHA>` (third-party, SHA-pinned per implementation); `claude` CLI inside the devcontainer image; `jq` inside the devcontainer image.

### Data Representation Decision

| Criterion | Assessment | Reason |
|---|---|---|
| Semantic Fit | Yes | `checkpoint.execution_mode` is a per-stage dispatch posture; semantically aligned with the existing per-stage checkpoint records |
| Responsibility Fit | Yes | The orchestrator owns dispatch; the orchestrator owns the checkpoint; co-locating the field with the rest of the per-stage checkpoint record is the natural home |
| Lifecycle Fit | Yes | The field is written at dispatch time, read at FR-2 entry; same lifecycle as the existing checkpoint per-stage record |
| Boundary/Interop Cost | Low | No external consumer; the field is intra-orchestrator with one named reader (FR-2 predicate) and one possible future reader (deliverable packager surfacing dispatch posture in archive summary) |

**Decision**: `new` field added to existing `checkpoint.json` structure — not a new structure; an additive field on the existing per-stage record. ADR-0057 documents the schema-surface change.

### Contract Definitions

The key contracts in this Blueprint:

- **`verdict_findings_parity.py` CLI contract** — see `cc-design.md §FR-1 Validator contract` and the Stdout schema documented in cc-dependencies.json `new_artifacts[0].invocation_contract`.
- **`audit_op11_adr_parity.py` CLI contract** — uniform with OP-1..OP-10 (one positional arg, JSON stdout, exit 0/1/2); see cc-design.md §FR-3 Rule contract.
- **`checkpoint.execution_mode` field contract** — per ADR-0057. Enum `{specialist-dispatch, parent-driven-workaround}`; absence treated as `specialist-dispatch`.
- **Anthropic Agent SDK `system/init` event contract** — `mcp_servers: [{name: string, status: "connected"|"failed"|"needs-auth"|"pending"|"disabled", ...}]`. Documented at `https://code.claude.com/docs/en/agent-sdk/mcp`.

### Data Contract

#### `verdict_findings_parity.py`

```yaml
Input:
  Type: <path-to-reviewer-output.json> <agent-name-from-fixed-roster>
  Preconditions: The reviewer-output.json file exists and is valid JSON; the agent-name is one of {shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor, execute-phase-quality-reviewer, execute-task-quality-handler}
  Validation: JSON parse; agent-name lookup in fixed per-agent table
Output:
  Type: JSON {mechanism, agent, verdict, blocking_findings[], diagnostic, remediation}
  Guarantees: The four FR-6 fields are always populated; verdict-comparison is case-sensitive per per-agent table; severity-comparison is case-insensitive against {BLOCKER}
  On Error: Exit 2 with stderr naming the parse failure or unknown-agent-name
Invariants:
  - Same input → same output (NFR-5 determinism)
  - No reviewer output the prior pipeline accepted is rejected (NFR-9)
```

#### `audit_op11_adr_parity.py`

```yaml
Input:
  Type: <path-to-.mcp.json>; ADR-0041 path resolved relative to repo root
  Preconditions: Both files exist and parse; the ADR-0041 invocation table is at the documented location
  Validation: JSON parse on .mcp.json; markdown table extraction on ADR-0041
Output:
  Type: JSON {rule: "OP-11", name: "adr-parity", target, findings[], servers_checked, adr_servers_recognized, deprecated_rows_skipped}
  Guarantees: Each finding carries the four FR-6 fields; severity is BLOCKER; diff_dimension is one of {argv, env, sentinel, missing-in-mcp.json, missing-in-adr-0041, deprecated-row-still-present}
  On Error: Exit 2 with stderr naming the parse failure
Invariants:
  - Same input → same output (NFR-5)
  - No .mcp.json entry already matching ADR-0041 produces a finding (NFR-10)
  - The rule does not read any environment variable (NFR-7 / NFR-8 / AC-CC-3-j)
  - The rule does not write to mcp-events.jsonl (NFR-13 / AC-CC-3-l)
```

#### `checkpoint.execution_mode` field (per ADR-0057)

```yaml
Field name: execution_mode (string, enum-valued)
Location: per-stage record inside checkpoint.json
Enum: {"specialist-dispatch", "parent-driven-workaround"}
Writer: recipe-feature-pipeline orchestrator at dispatch time (one write per stage)
Readers (current): FR-2 dispatch self-check predicate (one read per orchestrator entry, after Stage 1)
Readers (future-permitted): deliverable packager dispatch-posture surfacing; cross-artifact auditor run-state inspection
Backward-compat rule: absence-of-field equals "specialist-dispatch" (the project's pre-feature default)
Closed-enum discipline: any non-enum value at read time is a fail-closed error (NFR-6)
```

### Field Propagation Map

| Field | Boundary | Status | Detail |
|---|---|---|---|
| `verdict` (reviewer output) | Reviewer agent → orchestrator → FR-1 validator | preserved | Inspected case-sensitive per per-agent table |
| `findings[].severity` (reviewer output) | Reviewer agent → orchestrator → FR-1 validator | preserved | Inspected case-insensitive against `{BLOCKER}` |
| `scope_class` (intent-clarification frontmatter) | Stage 1 → orchestrator → FR-2 predicate (post-Stage-1, was line 350) | preserved (hoist location changes) | Read once after Stage 1; stored in checkpoint for downstream consumers (replaces Stage 13 re-read) |
| `checkpoint.execution_mode` (per ADR-0057) | Orchestrator dispatch → checkpoint write → FR-2 read | introduced | New field; one writer (orchestrator); one current reader (FR-2 predicate); absence-as-`specialist-dispatch` |
| `system/init.mcp_servers[].status` (Agent SDK event) | Claude Code CLI → stream-json → FR-5 jq filter | preserved | Read-only consumed; status enum is the contract per `https://code.claude.com/docs/en/agent-sdk/mcp` |
| `GITNEXUS_TAG` (versions.env) | versions.env → postCreate.sh → FR-4 dry-run | preserved | Read-only consumed for the pin-tag-drift diagnostic |

### State Transitions and Invariants

```yaml
checkpoint.execution_mode per-stage state machine:
  Initial state: absent (pre-feature checkpoints) OR specialist-dispatch (new runs)
  Possible states: {specialist-dispatch, parent-driven-workaround}

State Transitions:
  absent → (orchestrator write at dispatch) → specialist-dispatch
  absent → (orchestrator write at dispatch) → parent-driven-workaround
  No transitions between specialist-dispatch and parent-driven-workaround within a single run
  (the value is written once per stage at dispatch time and read once at FR-2)

System Invariants:
  - Any non-enum value at read time → fail-closed (AC-CC-2-f)
  - Absence at read time → treated as specialist-dispatch (AC-CC-2-g)
  - Only the orchestrator writes the field
  - The closed enum is the only set of valid values; future expansion requires ADR superseding ADR-0057
```

---

### Claude Code / Project Filesystem Design

The full per-layer Claude Code design is `working/feature/pipeline-quickwins-hardening-r1/cc-design.md` v0.2.0, integrated below by reference. The composer-integrated content from cc-design covers FR-1, FR-2, FR-3, FR-7, and the Claude-Code-side of FR-6.

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.claude/skills/recipe-feature-pipeline/` | Orchestrator skill | modified (FR-1 wire-in, FR-2 self-check, scope_class hoist, ADR-0057 schema documentation) |
| `.claude/skills/auditing-mcp/` | MCP audit skill | modified (OP-11 added; routing-table entry; new `references/adr-parity.md`) |
| `.claude/skills/auditing-shared/` | Shared validator family | modified (new `verdict_findings_parity.py`) |
| `adrs/` | ADR canonical root | modified (new ADR-0057; inline annotation on ADR-0041 row 71) |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/` | Deferral register | modified (FR-7 verify-and-tighten) |

#### CLAUDE.md Updates

| File | Change | Rationale |
|---|---|---|
| `CLAUDE.md` (repo root) | Counter-update: `MCP audit ruleset (OP-1..OP-10)` → `MCP audit ruleset (OP-1..OP-11)` in the Deeper-reference table | OP-11 lands; the existing pointer must reflect the new count. Single-character edit; no new sentence (per KB-cc-design Principle 5 single-source-of-truth) |

#### Slash Commands

None. No commands added or migrated; per cc-design §Command-to-skill migration.

#### Hooks

None. Per cc-design §Hook patterns: hooks are explicitly rejected for FR-1 and FR-2. FR-1's gating belongs at the orchestrator's dispatch boundary; a `PostToolUse` hook on Write would fire on every Write in the project. FR-2's self-check belongs in the orchestrator itself; a `SessionStart` hook would create a second `scope_class` read site that must stay in sync with the orchestrator-internal logic.

#### Skills

| Skill | Location | When Triggered | What It Provides |
|---|---|---|---|
| `recipe-feature-pipeline` (existing; modified) | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Operator-invoked pipeline run | Orchestration + (NEW) FR-1 validator wire-in + (NEW) FR-2 dispatch self-check |
| `auditing-mcp` (existing; modified) | `.claude/skills/auditing-mcp/SKILL.md` | Model-invocable; Gate-6 hard-gate per ADR-0043 | MCP audit (OP-1..OP-11 with OP-11 NEW) |
| `auditing-shared` (existing; modified) | `.claude/skills/auditing-shared/` | Cross-family utility script home per ADR-0031 | Now hosts `verdict_findings_parity.py` (NEW) |

#### Sub-Agents

None added or modified. Per cc-design §Subagent patterns and KB-cc-design Principle 9: no sub-agent model/effort/tools/skills/memory changes. The five reviewer-shaped agents are read-only consumed by FR-1.

#### MCP Servers

None added or removed. Per NFR-15 and ADR-0040: the seven sub-agents with `mcp__*` allowlists keep their existing allowlists. `.mcp.json` is read-only consumed by FR-3 (OP-11) and FR-5 (`claude --bare -p`).

#### File Naming & Layout Conventions Introduced

- OP-rule script naming `audit_op<N>_<short-descriptor>.py` — extension of existing convention; no new convention.
- Calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` — new convention (`.devcontainer/scripts/` for maintainer-initiated standalone scripts; not invoked by the lifecycle).
- CI workflow at `.github/workflows/mcp-connectivity-smoke.yml` — new (greenfield); convention documented in CI/CD §Convention this layer establishes.

#### Project Filesystem Error State Design

- Missing `verdict_findings_parity.py`: orchestrator exits with the standard `python3` not-found error (existing PATH allowlist convention).
- Missing `audit_op11_adr_parity.py`: Gate-6 audit coordinator skips with a warning per the existing `auditing-mcp` family-coordinator behavior.
- Malformed `intent-clarification.md` frontmatter at FR-2 read time: fail-closed per AC-CC-2-f.
- Malformed `.mcp.json` or unparseable ADR-0041 at OP-11 invocation: exit 2 with diagnostic per AC-CC-3-k.

### Frontend Design

N/A — out of scope.

---

### Backend Design

N/A — out of scope.

---

### API Design

N/A — out of scope.

---

### Query & Data Access Design

N/A — out of scope.

---

### Database Schema & Migration Design

N/A — out of scope.

---

### CI/CD Design (GitHub Actions)

The full per-layer CI/CD design is `working/feature/pipeline-quickwins-hardening-r1/cicd-design.md` v0.2.0, integrated below by reference. The composer-integrated content from cicd-design covers FR-5 and the CI/CD-side of FR-6.

#### Workflow Inventory

| Workflow File | Triggers | Purpose | Concurrency Group |
|---|---|---|---|
| `.github/workflows/mcp-connectivity-smoke.yml` | `pull_request` paths-filtered + `workflow_dispatch` | FR-5: assert every server in `.mcp.json` reports `status: connected` from the Agent SDK `system/init` event after a fresh devcontainer provision. Fail any PR that breaks the invariant. | None (not a deploy; parallel PR runs are safe). |

#### Job Graph

```
checkout ──► devcontainers/ci (build devcontainer image, run smoke)
                    │
                    └─► claude --bare -p "noop" --output-format stream-json > $OUTPUT
                                │
                                └─► jq filter on system/init.mcp_servers[] for status != "connected"
                                            │
                                            ├─► empty: PASS (exit 0; $GITHUB_STEP_SUMMARY = "all connected")
                                            └─► non-empty: FAIL (exit 1; FR-6 diagnostic in $GITHUB_STEP_SUMMARY)
```

#### Reusable Actions / Composite Actions

None introduced (per cicd-design §Reusable Actions / Composite Actions).

#### Secrets, Variables & Environments

None. The workflow reads no secrets, declares no environment, federates to no cloud. Cost: zero new credential surface (NFR-7).

#### Permissions

| Workflow / Job | `permissions:` block | Justification |
|---|---|---|
| `mcp-connectivity-smoke.yml` (workflow-level) | `contents: read` | Reads PR tree; does not write back, does not comment, does not deploy, does not federate. Per KB-github-actions-platform non-negotiable #2 (least privilege). |

#### Caching & Artifacts

None. Devcontainer image layer caching is owned by Docker/BuildKit on the runner, not by the workflow. If NFR-4 budget is exceeded, the canonical mitigation is a Codespaces-side prebuild — flagged as Q-CICD-2 (out-of-scope per this carve-out).

#### Environments & Promotion

| Environment | Protection Rules | Required Reviewers | Wait Timer | Deployment Branches |
|---|---|---|---|---|
| (none — not a deploy) | — | — | — | — |

#### Failure & Rollback

- **Failed-deploy behavior**: N/A — not a deploy.
- **Rollback workflow**: N/A — not a deploy. The PR check failure itself prevents merge.
- **Notification routing**: GitHub's built-in PR-check status. No Slack/email integration in scope (Q-CICD-6).

---

### Infrastructure as Code Design

N/A — out of scope.

---

### Dev Environment (Codespaces) Design

The full per-layer Codespaces design is `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` v0.2.0, integrated below by reference. The composer-integrated content from codespaces-design covers FR-4 and the Codespaces-side of FR-6.

#### Devcontainer Configuration

| File | Change | Purpose |
|---|---|---|
| `.devcontainer/devcontainer.json` | unchanged | Inherited from devcontainer-mcp-provisioning-r1; FR-4 reads no devcontainer.json field |
| `.devcontainer/Dockerfile` | unchanged | Inherited; FR-4 adds no apt package, no RUN step |
| `.devcontainer/postCreate.sh` | modified | FR-4 assertion block inserted inside `install_gitnexus()` between line 142 and line 143 |
| `.devcontainer/versions.env` | unchanged | FR-4 reads `GITNEXUS_TAG` only |
| `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` | new | FR-4 opt-in calibration script (AC-CS-4-f) |

#### Base Image & Features

- **Base image**: inherited (custom Dockerfile).
- **Features added by FR-4**: none.
- **Rationale for image choice**: inherited from prior feature.

#### Lifecycle Scripts

| Hook | Script | Purpose | Idempotent |
|---|---|---|---|
| `onCreateCommand` | inherited (tool-presence sanity check) | content-independent check | Yes |
| `postCreateCommand` | `postCreate.sh` (MODIFIED — FR-4 assertion inside `install_gitnexus()`) | MCP server installs + FR-4 dry-run on cache-miss path | Yes (sentinel-guarded; FR-4 fails skip the sentinel `touch`) |
| `postStartCommand` | inherited | per-session warming | Yes |
| `postAttachCommand` | inherited | terminal attach | Yes |

#### Forwarded Ports & Services

None — inherited empty `forwardPorts: []`.

#### Prebuilds

None — inherited (no prebuilds). Q-CS-4 disposition: composer has no visibility into a pending org-level prebuild policy; the no-prebuild posture is forward-compatible if one lands.

#### VS Code Configuration

Inherited; FR-4 adds no extensions, no workspace settings.

#### Parity with CI & Production

The devcontainer image is the FR-5 CI execution environment per synthesis D-0007. FR-4's modifications are inherited by FR-5 (the workflow uses the same image).

#### Secrets in Codespaces

Inherited; FR-4 introduces no new secret (NFR-7 / AC-CS-4-g — wait, this AC is FR-5; for FR-4 the equivalent is AC-CS-NFR-7-a from codespaces-design which is rolled up via NFR-7).

---

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---|---|---|---|---|
| Validation (FR-1 parity violation) | Reviewer emits `APPROVED` + severity:BLOCKER finding | `verdict_findings_parity.py` exit 1 | Halt orchestrator; surface FR-6 diagnostic; require user resolution before retry | Pipeline run blocks until the offending reviewer output is corrected |
| Validation (FR-2 refusal) | FULL-scope feature with stage configured `parent-driven-workaround` | Orchestrator dispatch self-check | Refuse dispatch loop; surface FR-6 diagnostic; exit non-zero | Pipeline run blocks before any stage runs |
| Validation (FR-3 BLOCKER finding) | `.mcp.json` server diverges from ADR-0041 non-deprecated row | `audit_op11_adr_parity.py` exit 1 | Halt-and-surface per Gate-6 ADR-0043 | Pipeline blocks at Gate 6 until parity is restored |
| Infrastructure (FR-4 contract drift) | GITNEXUS_SKIP_OPTIONAL_GRAMMARS contract no longer holds at pinned tag | Signal 1 (stderr regex) or Signal 3 (artifact absence) | Skip sentinel `touch`; emit `structured_failure`; return non-zero from `install_gitnexus()`; existing `\|\| emit_degraded_banner` trips | Devcontainer build emits a banner; the maintainer sees the diagnostic and re-pins or opens an upstream fix |
| Infrastructure (FR-5 server non-connected) | A server in `.mcp.json` reports `status != "connected"` from `system/init` | jq filter returns non-empty | Workflow exits 1; FR-6 diagnostic to `$GITHUB_STEP_SUMMARY`; PR check fails | PR cannot merge until connectivity is restored or the offending change is rolled back |
| Infrastructure (FR-5 CLI failure) | `claude --bare -p` itself exits non-zero | Capture exit code in the shell step | Workflow exits 2 (distinguishable from connectivity-fail per AC-CICD-5-d); INTERNAL-ERROR summary | PR check fails with a different diagnostic shape; maintainer investigates the CLI itself |
| Pipeline internal error (any FR) | Script crashes, file missing, parse failure | Exit 2 from any of the validators | Fail-closed per NFR-6; surface stderr; require user resolution | Pipeline run blocks; user-readable diagnostic |

### Logging and Monitoring

- **Log events** (the FR-6 actionable-diagnostic stream is the project's primary observability surface for these mechanisms):
  - FR-1 validator: JSON stdout per invocation (one line per reviewer-completion event)
  - FR-2 dispatch self-check: JSON stdout once per orchestrator entry
  - FR-3 OP-11: JSON stdout per invocation; nests under the `auditing-mcp` coordinator's findings stream
  - FR-4: `install_complete` event (status `ok` on pass) or `structured_failure` event (on fail) to `.claude/runtime/mcp-events.jsonl`; plain-text echo to stderr
  - FR-5: workflow-step stdout (visible in GitHub Actions run UI); `$GITHUB_STEP_SUMMARY` Markdown
- **Log levels**: not applicable in the structured-JSON-stdout pattern (the verdict + finding shape carries severity per-finding); plain-text echo from FR-4 is informational/error per the existing `postCreate.sh` convention.
- **Sensitive data**: per NFR-8, no environment variable value identified as a credential carrier appears in any diagnostic. Env-var **names** are emitted (e.g., `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, `GITNEXUS_TAG`); values are not.
- **Metrics**: per NFR-12, no new dashboards/metrics/alerts. The diagnostic stream is the observability surface.
- **Traces**: N/A — none of the mechanisms is request-scoped.
- **Alerts**: per FR-5, the PR check failing is the alert. No other notification routing.
- **Dashboards**: none.

## Implementation Plan

### Implementation Approach

**Selected Approach**: Single bundled PR delivering all seven FRs and the new ADR-0057, with per-mechanism isolation preserved by NFR-11.

**Selection Reason**: Per synthesis D-0008, cc-design Q-CC-4, and codespaces-design Q-CS-5: the seven FRs are tightly coupled at the implementation surface (FR-1 and FR-2 both touch `recipe-feature-pipeline/SKILL.md`; FR-3 and FR-5 both consume ADR-0041 and `.mcp.json`; FR-4 and FR-5 both touch the devcontainer surface). Splitting into sequenced PRs introduces artificial dependency edges that would have to merge in a fixed order anyway. For a MINOR-scope feature with a single-maintainer reviewer pool, one PR is the lower-overhead path. NFR-11's per-mechanism isolation is preserved either way (each mechanism is independently exercisable).

**Synthesis flagged D-0008 for user confirmation.** The composer adopts the recommendation with this rationale; if the user prefers sequenced PRs for review-ergonomic reasons not captured in the synthesis corpus, the sequenced shape is legitimate and would not require a Blueprint revision (the same edits, in five PRs instead of one). The Plan author should treat the single-bundled-PR shape as the default and surface back if the user redirects.

### Technical Dependencies and Implementation Order

This carve-out is largely parallelizable; the implementation order below is the natural sequence for a single-author bundled PR.

#### Required Implementation Order

1. **ADR-0057 (already authored by this Blueprint pass)**
   - Layer: Claude Code
   - Technical Reason: FR-2's design depends on the `checkpoint.execution_mode` field being a documented schema surface. ADR-0057 is the canonical home of that documentation.
   - Dependent Elements: FR-2 (reads the field), `recipe-feature-pipeline/SKILL.md` schema documentation, and any future reader of `checkpoint.json`.

2. **`verdict_findings_parity.py` (FR-1)**
   - Layer: Claude Code
   - Technical Reason: Pure new script under `auditing-shared`. No upstream dependencies in this feature.
   - Dependent Elements: `recipe-feature-pipeline/SKILL.md` wire-in (depends on this script existing).

3. **`audit_op11_adr_parity.py` + `references/adr-parity.md` + ADR-0041 annotation (FR-3)**
   - Layer: Claude Code
   - Technical Reason: Pure new OP-rule script. The ADR-0041 annotation is a same-commit edit (the OP-11 rule relies on the marker being present).
   - Dependent Elements: `auditing-mcp/SKILL.md` routing-table entry (depends on the new rule existing); `CLAUDE.md` counter update (depends on OP-11 landing).
   - Note: the OP-rule script reads ADR-0041 — the rule cannot pass against the current ADR-0041 without the inline annotation on row 71. Both edits must land together.

4. **`recipe-feature-pipeline/SKILL.md` modifications (FR-1 wire-in + FR-2 self-check + scope_class hoist + ADR-0057 schema documentation)**
   - Layer: Claude Code
   - Technical Reason: Depends on the new validator script (#2) and OP-rule (#3) existing, and on ADR-0057's schema canonicalization.
   - Dependent Elements: every future orchestrator run.

5. **FR-4 dry-run inside `install_gitnexus()` + calibration script**
   - Layer: Codespaces
   - Technical Reason: Independent of the Claude Code mechanisms. Modifies `.devcontainer/postCreate.sh` (assertion block + temp-file capture); creates `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`.
   - Dependent Elements: every future devcontainer cache-miss build.

6. **FR-5 workflow `.github/workflows/mcp-connectivity-smoke.yml`**
   - Layer: CI/CD
   - Technical Reason: Independent of the orchestrator mechanisms; depends on the devcontainer image working (so FR-4 should be in place for the same-PR shape to verify pre-merge).
   - Dependent Elements: every future PR touching the configured paths.
   - **Plan tasks** (per cicd-design): SHA-pin resolution for `actions/checkout` and `devcontainers/ci`; pre-merge validation of the unauthenticated-CLI assumption per Q-CICD-8; pre-merge three-run latency validation per D-0010; `actionlint` lint pass before commit per cicd-design §Plan task — actionlint deferral.

7. **FR-7 deferral-register verify-and-tighten**
   - Layer: Claude Code (deliverable-archive commit, per Q-CC-5 disposition: deliverable-archive placement adopted)
   - Technical Reason: Verification — the parentheticals are already in place; the work is checking text-exact match against the canonical form and tightening if needed.
   - Dependent Elements: this feature's deliverable archive.

8. **`CLAUDE.md` counter update (`OP-1..OP-10` → `OP-1..OP-11`) + Q-CS-3 cosmetic fix (`postCreate.sh:5` "5" → "4")**
   - Layer: Claude Code + Codespaces
   - Technical Reason: Housekeeping; bundled into the deliverable-archive commit.
   - Dependent Elements: future readers.

#### Cross-Layer Sequencing Notes

- **Schema before code**: ADR-0057 (the schema canonicalization) is referenced by `recipe-feature-pipeline/SKILL.md`'s FR-2 self-check edit. The ADR is authored at Design Composition time (this Blueprint pass); the SKILL.md edit lands at Implementation. The ADR is the schema document.
- **API before client**: N/A.
- **IaC before pipeline**: N/A.
- **Devcontainer before everything**: The FR-5 CI workflow depends on the devcontainer image working. The FR-4 modifications to that image should land in the same PR; pre-merge validation per D-0010 gates the merge.

### Migration Strategy

- **`checkpoint.json` schema migration (per ADR-0057)**: Absence-of-`execution_mode`-field on pre-feature checkpoints is treated as `specialist-dispatch` (AC-CC-2-g). No data migration is required; the orchestrator writes the field on new dispatches from the moment FR-2 lands.
- **`.mcp.json` migration**: None. The artifact is read-only consumed.
- **ADR-0041 migration**: None. The inline `[DEPRECATED]` annotation is forward-only; ADR-0005 append-only honored.
- **Reviewer-output migration**: None. NFR-9 — existing reviewer outputs that the prior pipeline accepted continue to pass the new validator (AC-CC-1-h).

### Feature Flags & Rollout

No feature flags. The mechanisms are deterministic gates; the kill criteria in PRD §Rollout Plan are the rollback levers (revert the specific commit; the mechanisms are per-mechanism reversible).

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: None of the mechanisms introduces a new authn/authz surface. FR-5's workflow runs unauthenticated by design (the `system/init` event is reachable in the unauthenticated state, verified pre-merge per Q-CICD-8).
- **Input Validation**: FR-1, FR-3 parse JSON or markdown; both fail-closed on parse failure per NFR-6. FR-4 evaluates regex on captured stderr (the regex is fixed at design time; no user-input regex injection surface). FR-5's `jq` filter is a literal string in the workflow YAML; no PR-author-controlled string is interpolated.
- **Sensitive Data Handling**: per NFR-8, no environment variable value identified as a credential carrier appears in any diagnostic. Env-var names are emitted; values are not.

### Frontend

N/A — out of scope.

### Backend / API

N/A — out of scope.

### Query / Database

N/A — out of scope.

### CI/CD

- **Secret exposure surface**: zero secrets read by the new workflow. `pull_request` (not `pull_request_target`) used — the workflow runs in the PR's context but with `contents: read` only and no secret access, so an attacker who landed a malicious `.mcp.json` cannot escalate (KB-github-actions-platform non-negotiable #3 honored).
- **Supply chain**: third-party action SHA-pinning is REQUIRED per the Plan task contract in cicd-design §SHA-pinning. `actions/checkout` (first-party, major-version tag acceptable per KB) and `devcontainers/ci` (third-party — SHA pin REQUIRED).
- **OIDC vs long-lived credentials**: N/A — no cloud integration.

### IaC

N/A — out of scope.

### Codespaces

- **Repo access from Codespace**: inherited unchanged.
- **Dotfiles / extension trust**: inherited unchanged. FR-4 introduces no new extension or first-run prompt.
- **FR-4 specific**: the dry-run reads `GITNEXUS_TAG` (non-secret) and `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (non-secret). The diagnostic names env-var keys, not values (NFR-8).

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---|---|---|
| `verdict_findings_parity.py` fixtures | No (use real reviewer-output JSON fixtures) | The validator's correctness depends on real reviewer-output shapes; mocking the input would shift the test surface |
| `audit_op11_adr_parity.py` fixtures | No (use real `.mcp.json` + ADR-0041 snapshots) | OP-11's contract is parity-against-real-artifacts; mocked artifacts would let drift slip past the test |
| `claude --bare -p "noop"` in CI | No (run the real CLI inside the devcontainer image) | The whole point of FR-5 is environment fidelity per synthesis D-0007 |
| `npm install -g gitnexus@1.6.5` in the FR-4 dry-run | No (run the real install at the pinned tag) | The whole point of FR-4 is asserting the real-install observable state |
| GitHub Actions runner | No (use real `ubuntu-latest`) | Pre-merge validation per D-0010 measures real runner wall-clock |

### Data Layer Testing Strategy

N/A — no database in scope.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|---|---|---|---|
| Claude Code (FR-1 validator) | Unit-style fixture invocation | `python3` + JSON fixtures | Suggested: `.claude/skills/auditing-shared/tests/verdict_parity_smoke/` (Plan author decides exact placement) |
| Claude Code (FR-2 self-check) | Pipeline-level smoke | Run pipeline against fixture intent-clarification.md with FULL scope + parent-driven-workaround stages | Suggested: Plan author defines fixture under `working/feature/<test-slug>/` |
| Claude Code (FR-3 OP-11) | Unit-style fixture invocation | `python3` + paired `.mcp.json` / ADR-0041 fixtures | Suggested: `.claude/skills/auditing-mcp/tests/op11_smoke/` per OI-CC-2 |
| Codespaces (FR-4) | Real devcontainer rebuild + drift-fixture rebuild | Manual rebuild of a fixture-broken contract | Demonstrated during the feature's verification per PRD Success Criteria |
| Codespaces (FR-4 calibration) | Manual maintainer-initiated run | `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` | Documented procedure in the script's head comment |
| CI/CD (FR-5) | Real workflow_dispatch + fixture PR | GitHub Actions | Pre-merge validation per D-0010 (three workflow_dispatch runs); demonstrated PR-fail per PRD Success Criteria |

### Integration Verification Points

- The orchestrator running end-to-end with all five mechanisms enabled against a known-good fixture pipeline run (smoke).
- The orchestrator running end-to-end with one mechanism disabled to confirm per-mechanism isolation per NFR-11 (AC-X-1).
- The CI smoke workflow running pre-merge against the draft branch three times per D-0010.

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**: each mechanism produces the expected verdict on its named failure mode and the expected pass on the negation. The aggregate is operationally verifiable as: "after this feature ships, a deliberately-broken artifact in the scope of any one mechanism causes that mechanism to fail; the prior pipeline's accepted artifacts continue to pass."
- **Verification method**: fixture-driven for the four orchestrator-internal mechanisms (FR-1, FR-2, FR-3, FR-7 verify); real-rebuild for FR-4; real-workflow for FR-5.
- **Verification timing**: per-mechanism unit verification at implementation time; pre-merge integration verification per D-0010 (FR-5 latency gate); post-merge per PRD Success Criteria (first five feature runs after ship, first three FULL-scope runs after ship, immediate audit-rule run on ship, fixture demonstrations).

### Early Verification Point

- **First verification target**: FR-3 OP-11 against the current `.mcp.json` and the annotated ADR-0041. After the `[DEPRECATED]` marker is added to row 71, OP-11 should produce zero findings against the current `.mcp.json`. This is the smallest, fastest, lowest-blast-radius check that proves the parity-rule + annotation work.
- **Success criteria**: `python3 audit_op11_adr_parity.py .mcp.json` returns exit 0 with `findings: []` against the current repo state post-annotation.
- **Failure response**: if findings appear, the canonicalizer's normalization rules are mis-stated for the current `.mcp.json` shape; revisit the canonicalization rules (per FR-3 risks-accepted) before proceeding to FR-1 and FR-2.

### Output Comparison (When Replacing or Modifying Existing Behavior)

N/A — every mechanism introduces new behavior; there is no existing output to compare against. The closest case is FR-2 hoisting the `scope_class` read site: design-cc verified by codebase-C-0028 that the read happens at exactly one site (line 350), so the hoist is mechanically safe (no parallel read sites to keep in sync).

### Operational Verification (When Pipeline / Infra / Migration in Scope)

- **Pre-merge gates**: the FR-5 workflow itself becomes a pre-merge gate for PRs touching the configured paths. The pre-merge validation per D-0010 (three workflow_dispatch runs) gates the merge of this feature itself.
- **Post-deploy verification**: per PRD Success Criteria:
  - Inspect every reviewer output in pipeline-run summary logs for the first five feature runs (target: zero approved-with-blockers reach the orchestrator).
  - Inspect state-transitions logs for the first three FULL-scope runs (target: zero FULL-scope dispatches with single-agent fallback enter the loop).
  - Run `auditing-mcp` with OP-11 enabled on the current repo (target: any present drift surfaces as a BLOCKER on first run).
  - Build the devcontainer against a fixture-broken contract (target: dry-run halts with clear message).
  - Open a fixture PR against the path-trigger set with a non-connected server (target: CI workflow fails the job).
- **Migration verification**: AC-CC-2-g check — resume a pre-feature `checkpoint.json` and confirm the dispatch self-check does not trip.
- **Rollback rehearsal**: per PRD §Rollout Plan kill criteria. Each mechanism is independently revertable (single commit in the bundled-PR shape).

## Future Extensibility

- **Extension point: FR-1 blocking-severity set expansion**. The validator's per-agent contract table is the single edit point for widening the blocking set from `{BLOCKER}` to `{BLOCKER, MAJOR}` in a future feature. NFR-9 backward-compatibility analysis would need to redo to confirm the wider set still passes existing reviewer outputs.
- **Extension point: OP-11 ADR-table parser**. Currently inline per Q-CC-3 disposition (inline for this carve-out). Future broader "design-realization audit dimension" feature can either reuse OP-11's parser or refactor to `auditing-shared/scripts/` for shared use across multiple OP rules.
- **Extension point: `checkpoint.execution_mode` enum expansion**. ADR-0057's closed enum is `{specialist-dispatch, parent-driven-workaround}`. Future features adding new dispatch postures extend the enum (ADR superseding ADR-0057 per ADR-0005).
- **Extension point: `[DEPRECATED]` marker convention project-wide**. Q-CC-2 disposition: scope-to-ADR-0041-only for this carve-out per synthesis calibration note on codebase-C-0111 (the N=1 generalization risk). A future feature that observes the same shape on a second ADR taxonomy table can lift the convention to project-wide.
- **Known future requirements**: the eight Won't-Have items in PRD §Won't Have are the deferred follow-on systemic-remediation feature. The five mechanisms in this run are sized as a quick-wins carve-out; the broader work (design-realization audit dimension, cross-file invariant catalog, live MCP reachability handshake, etc.) is a separate, later run.
- **Intentional limitations**: per the PRD carve-out, this feature does NOT close the broader systemic gap. It closes ~a third of incident defects plus the highest-risk deferral.

## Alternative Solutions

### Alternative 1: In-agent self-validation for FR-1

- **Overview**: Each of the 5 reviewer-shaped agents self-validates its own verdict-vs-findings consistency before emitting.
- **Advantages**: Per-agent ownership; no centralized validator to maintain.
- **Disadvantages**: Multiplies the implementation surface by 5 (one edit per agent); 9 invocation sites would still need to be wired separately; future reviewer-shaped agents added to the project would need the same edit.
- **Reason for Rejection**: Per synthesis D-0001 and cc-design FR-1 §Execution site: out-of-agent gives the same guarantee at ~one-fifth the maintenance cost.

### Alternative 2: New gate script for FR-2 (configurable separately from orchestrator)

- **Overview**: Externalize the FR-2 dispatch self-check into a standalone gate script invoked by the orchestrator at entry.
- **Advantages**: Reusable; potentially extensible to multiple fallback modes.
- **Disadvantages**: Premature factoring; the configuration surface has one value today. Adds new file surface, new permission entry, new invocation path. Two writers (the orchestrator and the operator who edits the gate's config) create coordination overhead.
- **Reason for Rejection**: Per synthesis D-0003 and ADR-0057 §Options Considered Option 2: MINOR-scope tiebreaker rules out premature factoring.

### Alternative 3: Amend ADR-0041 to drop the `mcp-openapi-schema` row

- **Overview**: Edit ADR-0041's invocation table to remove row 71 entirely, eliminating the FR-3 day-one false positive.
- **Advantages**: Removes the divergence at the source.
- **Disadvantages**: Excluded by the feature's carve-out (no ADR decision-text mutations). Also fights the project's append-only ADR posture per ADR-0005.
- **Reason for Rejection**: Out of scope by carve-out. The in-rule `[DEPRECATED]` annotation is an annotation pattern, not a decision-text rewrite — it stays inside the carve-out by interpretation.

### Alternative 4: `claude mcp list` for FR-5

- **Overview**: Run the PRD's literal command `claude mcp list` in the CI workflow, parse its stdout, check exit code.
- **Advantages**: Literal match to the PRD's wording in AC-FR-5-a/b/c.
- **Disadvantages**: Per t002-C-0001 and t002-C-0002 (verified): the canonical Claude Code CLI docs are silent on `claude mcp list`'s exit-code and stdout-format contracts. Depending on undocumented behavior is exactly the failure mode FR-5 exists to prevent.
- **Reason for Rejection**: Per synthesis D-0007. The substitute (`claude --bare -p "noop" --output-format stream-json | jq`) goes through the documented `system/init` event and `McpServerStatus` enum — the only stable contract available. The composer reconciles the PRD's literal name with the design's contract-bearing substitute by rewriting AC-FR-5-a/b/c at Blueprint time (this Blueprint's AC-CICD-5-a/b/c).

### Alternative 5: Five sequenced PRs (one per FR group) instead of one bundled PR

- **Overview**: Ship FR-1, FR-2, FR-3, FR-4, FR-5 in five separate PRs in sequence.
- **Advantages**: Finer rollback granularity; each PR independently reviewable.
- **Disadvantages**: The FRs are tightly coupled at the implementation surface; sequencing introduces artificial dependency edges; reviewer pays five context-switch costs.
- **Reason for Rejection**: Per synthesis D-0008, cc-design Q-CC-4, codespaces-design Q-CS-5. Composer adopts the single-bundled-PR shape with the synthesis-flagged user-confirmation caveat (recorded in Implementation Approach above).

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| FR-3 OP-11 false positives on `.mcp.json` shapes ADR-0041 didn't anticipate | Claude Code | Medium (noisy audit becomes ignored) | Medium | Canonicalizer is narrow (no env resolution, opaque `${VAR}`); PRD kill criterion allows disabling the rule and revising in a patch follow-up |
| FR-1 blocking-severity set chosen too inclusive and rejects reviewer outputs the prior pipeline accepted (NFR-9 breach) | Claude Code | Medium (cascading review rejections) | Low | Set is `{BLOCKER}` only; AC-CC-1-h is the explicit gate; design-cc traced each candidate severity token to existing reviewer behavior |
| FR-4 silently passes when env-var contract is broken upstream in a way the two signals don't detect | Codespaces | Medium (recreates failure mode the dry-run is meant to catch) | Low | Signal 1 AND Signal 3 conjunction catches "wrong-reason skip"; opt-in calibration script (AC-CS-4-f) is the periodic-recheck safety net |
| FR-5 unauthenticated-CLI assumption (system/init reachable without auth) doesn't hold | CI/CD | Medium (workflow can't initialize Claude Code to reach `system/init`) | Low-Medium | Pre-merge validation per Q-CICD-8; fallback is a read-only API key secret with documented NFR-7 deviation in a Blueprint addendum |
| FR-5 runtime exceeds NFR-4 5-minute ceiling | CI/CD | Medium (PR friction; maintainer pressure to disable) | Low-Medium | Pre-merge validation per D-0010 (three workflow_dispatch runs); kill criterion is immediate revert on any first-three-post-merge run exceeding 5 minutes |
| `checkpoint.execution_mode` enum proves too narrow for a future dispatch posture | Claude Code | Low (requires ADR superseding ADR-0057) | Low | Closed-enum discipline; future expansion is a documented mechanical edit per ADR-0057 §Kill criteria; ADR-0005 append-only supersession is the path |
| PR-shape choice (single bundled) creates merge-order ambiguity that ships one mechanism before another | Cross-cutting | Low (NFR-11 per-mechanism isolation makes any single-mechanism-first shipping safe) | Low | NFR-11 by design |
| Five mechanisms each pass their own checks but in aggregate don't prevent MCP-incident-pattern (systemic remediation is deferred) | Cross-cutting | Medium-High (carve-out's primary purpose is incompletely met) | Medium | Carve-out is explicit per PRD; Won't-Have list and deferred follow-on feature are the explicit acknowledgment |
| ADR-0041 table format changes in a future ADR amendment, breaking OP-11's parser | Claude Code | Low (fixture test catches the breakage at audit time) | Low | OI-CC-2 — Plan author adds a fixture smoke test under `.claude/skills/auditing-mcp/tests/op11_smoke/` |
| SHA-pin regression in `.github/workflows/mcp-connectivity-smoke.yml` (operator paste-mistakes a tag-pin) | CI/CD | Medium (supply-chain regression) | Low | Plan task contract in cicd-design §SHA-pinning of third-party actions explicitly forbids tag-pinning; `actionlint` Plan task as belt-and-braces |

## References

- PRD: `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` (v0.2.0 approved at Gate 2).
- Per-layer Designs (integrated by reference in this Blueprint):
  - `working/feature/pipeline-quickwins-hardening-r1/cc-design.md` v0.2.0
  - `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` v0.2.0
  - `working/feature/pipeline-quickwins-hardening-r1/cicd-design.md` v0.2.0
- Per-layer Dependencies sidecars:
  - `working/feature/pipeline-quickwins-hardening-r1/cc-dependencies.json` v0.2.0
  - `working/feature/pipeline-quickwins-hardening-r1/codespaces-dependencies.json`
  - `working/feature/pipeline-quickwins-hardening-r1/cicd-dependencies.json`
- Codebase analysis: `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json`; report `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis-report.md`.
- Research notes:
  - `working/feature/pipeline-quickwins-hardening-r1/research-notes/t-001-gitnexus-grammar-skip-contract.md` (GitNexus env-var contract at v1.6.5).
  - `working/feature/pipeline-quickwins-hardening-r1/research-notes/t-002-claude-mcp-list-contract.md` (Claude Code CLI contract silence on `claude mcp list`).
- Synthesis: `working/feature/pipeline-quickwins-hardening-r1/synthesis.md`.
- Seed proposal: `Issues/cross-artifact-divergence-detection-gap/proposal.md` (status: adopted).
- Deferral register: `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` (rows B-1 and H-4 closed by this feature per FR-7).
- ADRs referenced: see frontmatter `adrs_referenced`. ADRs authored: ADR-0057 at `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md`.
- KBs consulted: KB-documentation-criteria, KB-cc-design, KB-cc-platform, KB-codespaces-design, KB-codespaces-platform, KB-github-actions-design, KB-github-actions-platform, KB-review-disciplines, KB-general-coding-principles.

### Cross-references — Inherited ADRs Applied

Per the rationale brief and the per-layer dependencies sidecars, this Blueprint honors:

- **ADR-0005** (append-only supersession) — the inline `[DEPRECATED]` annotation on ADR-0041 row 71 is an annotation pattern, not a decision-text rewrite; the row's invocation form is preserved verbatim.
- **ADR-0017** (document-reviewer integration) — FR-1 wires into the 5 documented invocation points.
- **ADR-0029 / ADR-0033** (no silent scope changes) — the FR-1 reviewer-scope expansion (`execute-task-quality-handler` inclusion per D-0002) is documented explicitly; the AC-FR-5 reconciliation is surfaced explicitly per Q-CICD-9.
- **ADR-0036 / ADR-0056** (canonical ADR placement, no carve-outs) — ADR-0057 lives at `adrs/`.
- **ADR-0037** (mcp-events.jsonl event schema) — FR-4 honors existing event types only.
- **ADR-0039** (credential redaction posture) — FR-4 uses `log_mcp_event` which implements redaction-at-source.
- **ADR-0040** (Serena narrowed always-on; precedent for sub-agent allowlists) — unchanged by this feature.
- **ADR-0041** (install-mechanism hybrid) — read by FR-3 OP-11; annotated inline on row 71.
- **ADR-0042** (auditing-mcp family graduation) — FR-3's OP-11 follows the family contract.
- **ADR-0043** (auditing-mcp Gate-6 hard gate) — OP-11 inherits.
- **ADR-0044** (flatten execution dispatch hierarchy) — ADR-0057 canonicalizes the on-disk surface ADR-0044 already names.

### Cross-references — New ADRs Authored (this run)

- **ADR-0057** (`checkpoint.execution_mode` as first-class field) — `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md`. Authored by design-composer during this Blueprint pass. Rationale: the field is being introduced (not promoted from existing); a schema-surface change to a cross-cutting orchestrator artifact (`checkpoint.json`) clears the ADR-worthiness bar because (i) it has cross-component blast radius — every reader of `checkpoint.json` is affected; (ii) it has schema-surface stability implications — future stages adding new dispatch postures must extend the enum per ADR-0005; (iii) kill criteria worth preserving (closed-enum discipline); (iv) the synthesis framer's classification of decisions as LOCAL + REVERSIBLE was correct for the implementation-grade decisions but missed this schema-surface item which surfaces at composition time.

### Cross-references — Resolved Q-`<LAYER>`-N Items (composer dispositions)

**Claude Code layer:**

- **Q-CC-1 (Gate-7 elevation for FR-1 validator)**: disposition = (a) inline orchestrator-step rejection (cc-design recommendation adopted). Defer Gate-7 elevation to a future feature. Rationale: this is a structural-shape rejection, not a quality finding; elevating to a new gate would require ADR-text changes outside the carve-out per the no-ADR-amendment principle.
- **Q-CC-2 (`[DEPRECATED]` marker project-wide vs ADR-0041-only)**: disposition = (a) scope to ADR-0041 only (cc-design recommendation adopted). Rationale: synthesis calibration note on codebase-C-0111 explicitly downgrades the "established pattern" generalization to single-sourced (N=1). Lift in a future feature if a second ADR taxonomy table develops the same shape. **No ADR authored for this** — the calibration note is explicit that an ADR establishing project-wide convention would over-generalize from N=1.
- **Q-CC-3 (inline ADR-parser vs shared utility under `auditing-shared`)**: disposition = (a) inline for this carve-out (cc-design recommendation adopted). Rationale: the broader "design-realization audit dimension" is a Won't-Have; extracting prematurely is over-engineering. Lift to shared utility when the broader dimension lands in a future feature.
- **Q-CC-4 (D-0008 PR shape)**: disposition = (a) single bundled PR (cc-design + codespaces-design recommendations aligned). Composer adopts. Synthesis flagged D-0008 for user confirmation — see Implementation Approach above; if the user redirects to sequenced PRs, the Plan author treats this as a workflow change without a Blueprint revision.
- **Q-CC-5 (D-0009 deferral-register placement)**: disposition = (a) deliverable-archive commit (cc-design recommendation adopted). Synthesis D-0009 rationale (audit-trail completeness) governs. The `-alt` placement variant in cc-design AC-CC-7-a is NOT activated.
- **Q-CC-6 (D-0003 refinement — post-Stage-1 hoist)**: disposition = (a) accept post-Stage-1 refinement as operative (cc-design recommendation adopted). The data-dependency (`scope_class` is itself a Stage-1 output) makes a literal pre-Stage-1 hoist impossible on a fresh run; the refinement preserves D-0003's intent (single early read site that subsequent stages consume from a checkpoint field) while honoring the data dependency. Recorded here so the Plan author and any downstream reader understand the refinement.

**Codespaces layer:**

- **Q-CS-1 (immutable-tag assumption)**: disposition = (b) accepted with calibration script as periodic-recheck remedy (codespaces-design recommendation adopted). The cached-path-skip is safe by construction (sentinel name encodes the pin; pin change invalidates) plus opt-in calibration (AC-CS-4-f).
- **Q-CS-2 (two-sentinel-format inconsistency deferred surface)**: disposition = surface as deferred-issue row in `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`. The Plan author adds the deferred-issue row at deliverable-archive time. Explicit-defer per the codespaces-design recommendation.
- **Q-CS-3 (cosmetic 5-vs-4 server reference in `postCreate.sh:5`)**: disposition = fix the stray "5" in the FR-4 commit (codespaces-design recommendation adopted). One-line cosmetic edit; removes a future-reader hazard at near-zero cost.
- **Q-CS-4 (prebuild policy)**: disposition = no prebuild adopted (codespaces-design recommendation adopted). Composer has no visibility into a pending org-level prebuild policy. The no-prebuild posture is forward-compatible if such policy lands.
- **Q-CS-5 (D-0008 PR shape from Codespaces view)**: disposition = same as Q-CC-4 — single bundled PR.

**CI/CD layer:**

- **Q-CICD-1 (Claude Code CLI version pin)**: disposition = the devcontainer's `claude-code` Feature must pin to an exact version (Codespaces-layer obligation). The Plan author confirms the existing pin is exact-version (not `:latest`); if it is `:latest`, the Plan adds a task to pin it before the FR-5 workflow merges. The cicd-design owner-attribution is correct (design-codespaces decides the pin; design-composer reconciles).
- **Q-CICD-2 (Codespaces-side prebuild mitigation if NFR-4 breached)**: disposition = out-of-scope for this carve-out; the maintainer can request a follow-on feature if the post-merge p95 trends toward 4 minutes. Surface as a deferred-issue row at deliverable-archive time.
- **Q-CICD-3 (merge-time smoke variant)**: disposition = out-of-scope per the PRD's PR-gated FR-5 spec. Surface as future-extensibility note (not as a deferred issue — this is a feature-scope question).
- **Q-CICD-4 (nightly upstream-health smoke)**: disposition = out-of-scope per the carve-out. Surface as future-extensibility note.
- **Q-CICD-5 (PR-level concurrency cancel-in-progress)**: disposition = not set in the current design; add only if maintainer-ergonomics need is demonstrated. No action required.
- **Q-CICD-6 (Slack/email notification routing)**: disposition = out-of-scope; GitHub's built-in PR check status is the notification surface.
- **Q-CICD-7 (chain FR-3 audit and FR-5 smoke into one workflow)**: disposition = keep separate (cicd-design recommendation adopted). FR-3 is static-analysis at Gate-6; FR-5 is runtime connectivity. They are complementary, not duplicative.
- **Q-CICD-8 (unauthenticated-CLI assumption validation)**: disposition = upgraded to **Plan task** (cicd-design recommendation adopted). The Plan must include a pre-merge validation task: run `claude --bare -p "noop" --output-format stream-json` inside the devcontainer in the unauthenticated state CI will use; confirm `system/init` is emitted with populated `mcp_servers[]`. If validation fails, the fallback is a read-only `ANTHROPIC_API_KEY` repo secret scoped to the workflow with a documented NFR-7 deviation captured in a Blueprint addendum.
- **Q-CICD-9 (AC-FR-5-a/b/c PRD-literal reconciliation)**: disposition = (a) **AC text rewritten in this Blueprint** (cicd-design recommendation adopted). The PRD's literal `claude mcp list` is substituted with `claude --bare -p "noop" --output-format stream-json | jq` per synthesis D-0007 (grounded in t002-C-0001/t002-C-0002/t002-C-0008). The reconciled ACs live at AC-CICD-5-a/b/c above. PRD Assumption A-3 ("`claude mcp list` is available and its exit code reflects connectivity") is **superseded** by this reconciliation; the replacement assumption (Claude Code CLI on PATH in the devcontainer image) is already satisfied by the existing `claude-code` Feature.

### Cross-references — Unresolved Items Deferred to User

None.

The synthesizer flagged D-0008 (PR shape) for user confirmation. The composer's disposition (single bundled PR, per cc-design + codespaces-design aligned recommendations) is recorded in Implementation Approach. If the user prefers sequenced PRs, the Plan author treats it as a workflow change without a Blueprint revision (NFR-11 makes per-mechanism isolation hold either way). This is recorded explicitly as a non-blocking question for the maintainer to redirect on if they choose; it does not block the Plan-author stage.

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-26 | 1.0.0 | Initial Blueprint composed from cc-design v0.2.0, codespaces-design v0.2.0, cicd-design v0.2.0, synthesis v1.0.0, codebase-analysis. Authored ADR-0057 (`checkpoint.execution_mode` as first-class field). Reconciled AC-FR-5-a/b/c PRD-literal to AC-CICD-5-a/b/c per Q-CICD-9. Recorded disposition for all 6 Q-CC, 5 Q-CS, and 9 Q-CICD items. | design-composer |
