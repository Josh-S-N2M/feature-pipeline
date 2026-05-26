---
id: BP-pipeline-quickwins-hardening-r1
version: 2.3.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
derived_from: working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
codebase_analysis: working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
predecessor: working/feature/pipeline-quickwins-hardening-r1/blueprint-v1.md
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
  - ADR-0057
adrs_authored:
  - ADR-0058
generated: 2026-05-26T00:00:00Z
generated_by: design-composer
change_summary: >
  v2.3 is a purely additive amendment that absorbs Cross-Artifact Audit cycle 1
  finding I-CA-002 per reconciliation-log-r3.md. The cross-artifact auditor
  flagged a structural asymmetry in the v2.2 AC catalog: the v2.2 cycle lifted
  ACs the Blueprint v2.1 didn't already define (AC-CC / AC-CS / AC-CICD families
  + the freshly authored AC-NFR-14 and aliased AC-NFR-15), but AC-NFR-1-a
  through AC-NFR-13-b remained inherited-by-reference from PRD v0.3.0 §NFRs.
  The asymmetry is structural rather than a v2.2 oversight — the AC-NFR-N-a
  family was always cited-by-ID with PRD as canonical definition; that
  inheritance has always worked. The single edit in this pass is one inheritance
  note added to the §Acceptance Criteria preamble that names the inheritance
  pointer to PRD v0.3.0 §Non-Functional Requirements (lines 336-413) and the
  scope-of-lift discipline the v2.2 cycle applied. No AC text mutated (lifted
  or inherited); no decision content changed; no carve-out boundary movement;
  no scope-class shift; no ADRs authored or amended this cycle.
  ---
  v2.2 is an additive amendment that lifts 18 per-layer-design AC definitions
  into the Blueprint's canonical AC catalog per Plan review reconciliation
  finding I-DR-002 (Plan tasks T2.x/T3.x/T4.x/T7.x cited AC IDs the Blueprint
  declared "see Blueprint v1" rather than enumerating). Four ACs lifted from
  cc-design v0.2.0 §FR-1 cluster (AC-CC-1-d, -e, -f, -g); three from cc-design
  v0.2.0 §FR-2 cluster (AC-CC-2-d, -e, -f); nine from cc-design v0.2.0 §FR-3
  cluster (AC-CC-3-c through AC-CC-3-k); two from cc-design v0.2.0 §FR-7
  cluster (AC-CC-7-b, -c); four from cicd-design v0.3.0 §FR-5 cluster
  (AC-CICD-5-c, -d, -e, -f, recovered verbatim from blueprint-v1.md lines
  295-298 which originally introduced them). Plus one freshly authored
  NFR-coverage AC (AC-NFR-14, postCreate-execution-time bound) and one alias
  (AC-NFR-15 → AC-X-3, MCP-allowlist no-change) so Plan citations of AC-NFR-14
  and AC-NFR-15 resolve to canonical Blueprint definitions. Additive only —
  no existing AC IDs change, no decision content shifts, no ADRs authored
  this cycle, no carve-out boundary movement. The FR-1/FR-2/FR-3/FR-5/FR-7
  abbreviated-section pattern ("see Blueprint v1") is replaced with the full
  ACs inline so every cross-artifact citation lands on a definition local to
  the Blueprint.
  ---
  v2.1 reconciles architecture-audit-r1 cycle 1 (verdict approved_with_conditions,
  3 important + 2 recommended findings, all consolidated to design-composer per
  reconciliation-log-r1.md). Three categories of correction land in this pass.
  (1) Event-type triad correction (finding I-AA-001): every reference to the
  three pre-existing mcp-events.jsonl event types now reads
  `install_complete / readiness_probe / structured_failure` (the actual on-disk
  vocabulary per audit_op7_events_schema.py VALID_EVENT_TYPES and per
  .devcontainer/postCreate.sh emissions); the prior `primary_degraded` references
  inherited a v1.0.0 / v1.0.1 ADR-0037 prose error which is corrected in
  ADR-0037 v1.0.2 in lockstep with this Blueprint pass. The four-type
  vocabulary becomes `install_complete / readiness_probe / structured_failure
  / calibration_result`. (2) OP-rule label correction (finding I-AA-002):
  every reference to the schema-validation audit rule now reads "OP-7" (the
  rule implemented by audit_op7_events_schema.py); OP-6 references are
  preserved only where they correctly cite credential redaction (the
  distinct rule implemented by audit_op6_runtime_log_redaction.py). (3) FR-3
  pre-emption (finding I-AA-003): ADR-0041 row 70 (Serena) joins row 71
  (mcp-openapi-schema) in the FR-3 day-one `[DEPRECATED INVOCATION FORM]`
  annotation list; row 70 has the same shape of drift (documents
  uvx --from invocation form; runtime uses installed binary). Plus two
  recommended-severity items: ADR-0057 prose framing corrected from
  "introduce" to "promote-and-formalize" (the execution_mode field is
  pre-existing in SKILL.md:138 and 412; ADR-0057's contribution is its
  load-bearing canonicalization, not its introduction); and two new ordered
  Plan-tasks (OP-7 schema extension for calibration_result; immediate
  post-merge workflow run to retire Q-CS-1b "NEVER RUN" banner before any
  operator's first rebuild). Supporting in-place amendments: ADR-0037 to
  v1.0.2 (prose-only); ADR-0057 to v1.0.1 (prose-only); ADR-0058 revised in
  draft (Gate 4 status); ADR-0041 row 70 annotated (prose-only). All carry-
  forward dispositions, the FR-1 / FR-2 / FR-3 / FR-5 / FR-7 sections,
  ADR-0058 decision content, ADR-0057 decision content, and the carve-out
  boundary are preserved verbatim from v2.0.0.
revision_history:
  - version: 2.3.0
    date: 2026-05-26
    summary: |
      Cross-Artifact Audit cycle 1 reconciliation absorption per
      reconciliation-log-r3.md (single edit I-CA-002). Adds one inheritance
      note to the §Acceptance Criteria preamble naming PRD v0.3.0
      §Non-Functional Requirements as the canonical source for AC-NFR-1-a
      through AC-NFR-13-b (which remain inherited-by-reference, not lifted),
      and explaining that the v2.2 lift cycle was scoped to ACs the Blueprint
      v2.1 didn't already define (AC-CC / AC-CS / AC-CICD families plus the
      freshly authored AC-NFR-14 and aliased AC-NFR-15). The AC-NFR-N-a family
      was always cited-by-ID with PRD as canonical — the inheritance has
      always worked; the apparent asymmetry the auditor flagged is structural
      rather than a v2.2 oversight. Purely additive: ZERO existing AC text
      mutated (lifted or inherited); ZERO decision-content drift; ZERO ADRs
      authored or amended this cycle; carve-out boundary unchanged; scope
      class unchanged. After this Blueprint pass, the orchestrator advances
      Cross-Artifact Audit to cycle 2 for verification that the asymmetry
      reading is closed. Cycle counter: 1 of 4 for the Cross-Artifact Audit
      family.
  - version: 2.2.0
    date: 2026-05-26
    summary: |
      Additive lift of 18 per-layer-design ACs into Blueprint canonical AC
      catalog per Plan review reconciliation (I-DR-002). Plus AC-NFR-14
      authored and AC-NFR-15 aliased to AC-X-3. From cc-design v0.2.0:
      AC-CC-1-d/e/f/g (FR-1 cluster), AC-CC-2-d/e/f (FR-2 cluster),
      AC-CC-3-c through AC-CC-3-k (FR-3 cluster), AC-CC-7-b/c (FR-7 cluster).
      From cicd-design v0.3.0 / blueprint-v1.md: AC-CICD-5-c/d/e/f (FR-5
      cluster). New: AC-NFR-14 (postCreate.sh execution-time bound, used by
      Plan tasks T2.2 / T2.3 for Q-CS-1b banner overhead). Alias:
      AC-NFR-15 → AC-X-3 (MCP allowlist no-change; used by Plan task T4.2).
      Additive only — no existing AC IDs change, no decision content shifts,
      no ADRs authored this cycle, no carve-out movement. The previous
      "see Blueprint v1" abbreviated-section pattern is replaced with full
      AC text inline so every Plan / Test citation lands on a Blueprint-local
      definition. Carry-forward dispositions, FR-4 family ACs, ADR-0058
      decision content, ADR-0057 prose, FR-6 unification, the carve-out
      boundary, and the v2.1 audit-reconciliation corrections are preserved
      verbatim from v2.1.
  - version: 2.1.0
    date: 2026-05-26
    summary: |
      Architecture-audit-r1 reconciliation cycle 1 absorption. Five findings
      from architecture-audit-pipeline-quickwins-hardening-r1-r1 (verdict
      approved_with_conditions, 0 critical / 3 important / 2 recommended)
      addressed in a single coherent revision pass. Event-type triad corrected
      install_complete (was primary_degraded across multiple sections;
      inherited from ADR-0037 prose error, since corrected in ADR-0037 v1.0.2).
      OP-6 → OP-7 label corrected for schema-validation rule references. ADR-
      0041 row 70 (Serena) added to FR-3 day-one [DEPRECATED]-annotation list
      alongside row 71 (mcp-openapi-schema). ADR-0057 Context reworded
      "introduce" → "promote-and-formalize" to accurately describe the pre-
      existing execution_mode field. Two new ordered Plan-tasks (OP-7 schema
      extension; immediate post-merge banner-retirement workflow run). In-
      place ADR amendments: ADR-0037 v1.0.1 → v1.0.2 (prose-only, no decision
      change); ADR-0057 v1.0.0 → v1.0.1 (prose-only); ADR-0058 revised in
      draft; ADR-0041 row 70 annotated. Carve-out boundary reverified intact.
  - version: 2.0.0
    date: 2026-05-26
    summary: |
      Gate-4-prep reshape absorption. New per-layer inputs: codespaces-design
      v0.3.0, cicd-design v0.3.0. Authored ADR-0058 for the `calibration_result`
      event-type extension. Admitted Q-CS-1b staleness banner. Q-CICD-1..9
      dispositions unchanged. PR shape (single bundled) unchanged. Deferral-
      register placement (deliverable archive) unchanged. Carve-out boundary
      (eight Won't-Haves unchanged) reverified.
  - version: 1.0.0
    date: 2026-05-26
    summary: Initial Blueprint; authored ADR-0057; reconciled AC-FR-5.
---

# Pipeline Quick-Wins Hardening (Round 1) Design Document — v2.3

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

**v2 reshape note.** Per PRD v0.3.0 (Gate-4-prep user direction at 2026-05-26), FR-4 is internally subdivided into three sub-mechanisms answering questions on different cadences: FR-4a (per-rebuild static-shape check, sub-100 ms, Codespaces layer); FR-4b (opt-in behavioral calibration script, Codespaces layer); FR-4c (new CI workflow that drives FR-4b on weekly cron + on-change-to-versions.env, CI/CD layer). The five-mechanism count is preserved (FR-4 still counts as one mechanism for FR-6 and headline-mechanism purposes); the internal structure is more honest about cadence. The eight Won't-Have exclusions are unchanged; the MINOR scope class is unchanged; the carve-out boundary is reverified intact.

### Layer Scope

This Blueprint touches exactly three layers; the remaining six are out of scope and their layer subsections under Design, Security, Test Boundaries, and Verification are marked `N/A — out of scope`.

- [x] **Claude Code / Project Filesystem** — FR-1 (verdict-vs-findings parity validator), FR-2 (orchestrator dispatch self-check), FR-3 (`.mcp.json` ↔ ADR-0041 parity audit rule OP-11), FR-7 (deferral-register tightening), Claude-Code-side of FR-6
- [ ] **Frontend** — N/A — out of scope per PRD §Layer Scope
- [ ] **Backend** — N/A — out of scope per PRD §Layer Scope
- [ ] **API** — N/A — out of scope per PRD §Layer Scope
- [ ] **Query / Data Access** — N/A — out of scope per PRD §Layer Scope
- [ ] **Database** — N/A — out of scope per PRD §Layer Scope
- [x] **CI/CD (GitHub Actions)** — FR-5 (`mcp-connectivity-smoke.yml` workflow), **FR-4c (`gitnexus-grammar-skip-calibration.yml` workflow — NEW in v2)**, CI/CD-side of FR-6
- [ ] **Infrastructure as Code** — N/A — out of scope per PRD §Layer Scope
- [x] **Dev Environment (Codespaces / Devcontainer)** — **FR-4a (per-rebuild static-shape check in `.devcontainer/postCreate.sh` top-level, between current lines 197 and 198 — REPLACES v1's `install_gitnexus()`-internal placement)**, **FR-4b (opt-in behavioral calibration script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` — Codespaces-owned, CI-invoked via FR-4c)**, **Q-CS-1b staleness banner in `postCreate.sh` (NEW in v2)**, Codespaces-side of FR-6

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
  across three layers with FOUR distinct output surfaces (orchestrator JSON,
  postCreate.sh plain-text + structured JSONL, CI $GITHUB_STEP_SUMMARY for
  TWO workflows); AC-FR-5-a/b/c PRD-literal-name reconciliation (claude mcp
  list → claude --bare -p) without losing behavioral intent; checkpoint.execution_mode
  promoted to a first-class schema field (ADR-0057); FR-4 split into three
  sub-mechanisms on different cadences (FR-4a per-rebuild static, FR-4b opt-in
  behavioral, FR-4c CI-driven) with cross-layer Codespaces↔CI/CD handoff and
  a fourth event type extension to ADR-0037 (ADR-0058). The aggregate touches
  the orchestrator skill plus two auditing skills plus the devcontainer
  post-create script plus a new opt-in calibration script plus two new CI
  workflows, all coordinated through this Blueprint.
layers_touched:
  - "Claude Code / Project Filesystem"
  - "CI/CD (GitHub Actions)"
  - "Dev Environment (Codespaces / Devcontainer)"
blast_radius:
  runtime: |
    Every future feature run: the FR-1 validator runs at 9 reviewer-completion
    invocation sites; the FR-2 self-check runs once at orchestrator entry on every
    run; the FR-3 OP-11 audit runs at Gate 6 every time auditing-mcp is invoked.
    Every devcontainer rebuild: FR-4a (sub-100 ms static-shape check) runs on
    both cache-hit and cache-miss paths; the Q-CS-1b staleness banner reads the
    most recent calibration_result event (admitted in v2). Every PR touching
    configured paths: FR-5 runs; PR-bumps to .devcontainer/versions.env (or the
    calibration script) AND the weekly Monday 07:00 UTC cron trigger FR-4c.
  build_time: |
    Codespace cold-build cost gains the FR-4a static-check overhead (p95 ≤ 100 ms
    on the configured 4-CPU class — strictly tighter than v1's ≤ 2 s). CI gains
    TWO new workflows: FR-5 connectivity smoke (p95 target under 4 min, NFR-4
    ceiling 5 min) and FR-4c calibration (p95 target under 2 min, NFR-4 ceiling
    5 min per-workflow). No build-time impact on the feature-pipeline
    orchestrator itself.
main_constraints:
  - "MINOR scope class — every change is two-way reversible; per-mechanism isolation per NFR-11."
  - "No new MCP server, no new MCP allowlist entry (NFR-15 / ADR-0040)."
  - "No new credential surface (NFR-7); no credentials in diagnostics (NFR-8)."
  - "Existing reviewer outputs that the prior pipeline accepted must continue to pass (NFR-9)."
  - "Event-type vocabulary on .claude/runtime/mcp-events.jsonl extends additively from three to four (calibration_result), governed by ADR-0058 (NEW in v2) per NFR-13's explicit additive-extension directive."
  - "No ADR-0041 decision-text mutations — the [DEPRECATED] marker is an annotation, not a rewrite."
biggest_risks:
  - "FR-3 false positives on .mcp.json shapes ADR-0041 didn't anticipate (mitigated: kill criterion + narrow canonicalizer; plus v2.1 [DEPRECATED INVOCATION FORM] annotations on BOTH ADR-0041 row 71 (mcp-openapi-schema) AND row 70 (Serena) per Architecture Audit cycle 1 finding I-AA-003)."
  - "FR-4 silent pass when contract is broken via a mechanism the per-rebuild static + behavioral calibration combination doesn't detect (mitigated: FR-4c cron forces weekly invocation; Q-CS-1b staleness banner is the belt-and-suspenders surface; calibration's negative-assertion is enabled by default)."
  - "FR-5 unauthenticated-CLI assumption (`claude --bare -p` emits system/init before auth) may not hold (mitigated: pre-merge validation gate per Q-CICD-8)."
  - "checkpoint.execution_mode field is a schema-surface change that future stages must respect when adding new dispatch postures (mitigated by ADR-0057's kill criterion and the closed-enum discipline)."
  - "calibration_result event-type extension creates a documentation-vs-realization drift surface if the schema home (KB-mcp-design) is not updated in lockstep (mitigated: Plan task contract for the schema-home update accompanies the FR-4b script's introduction)."
unknowns:
  - "The exact post-merge p95 of FR-5 (estimated under 4 minutes; pre-merge validation gate per D-0010 confirms before ship)."
  - "The exact post-merge p95 of FR-4c (estimated under 2 minutes per cicd-design v0.3.0 commitment; image-build time dominates and is shared with FR-5)."
  - "Whether the unauthenticated-CLI assumption holds; verified pre-merge per Q-CICD-8."
```

## Background and Context

### Prerequisite ADRs

- **ADR-0005** (append-only supersession): constrains how this Blueprint can evolve the schemas promoted-and-formalized by ADR-0057 (`checkpoint.execution_mode` — v1.0.1 prose framing corrected per v2.1) and introduced by ADR-0058 (`calibration_result` event type — revised in draft per v2.1), the `[DEPRECATED INVOCATION FORM]` annotations on ADR-0041's invocation table (rows 71 and 70 per v2.1), the in-place prose amendments to ADR-0037 (v1.0.1 → v1.0.2; prose-only, no decision-content change per v2.1), and the additive extension of ADR-0037's event-type vocabulary.
- **ADR-0017** (document-reviewer integration): the FR-1 validator wires into the five `shared-document-reviewer` invocation points this ADR documents.
- **ADR-0029** (no silent scope changes): the AC-FR-5-a/b/c reconciliation surfaces the `claude mcp list` → `claude --bare -p` substitution explicitly rather than silently; the FR-4 internal split into three sub-mechanisms is documented explicitly per the same principle.
- **ADR-0033** (ADR-0029 execution extension): the FR-1 scope sweep (`execute-task-quality-handler` inclusion) honors no-silent-scope-changes by enumerating the scope expansion in the design.
- **ADR-0036** (single-location ADR placement): the new ADR-0057 and ADR-0058 both live at the canonical `adrs/` root.
- **ADR-0037** (mcp-events.jsonl event schema): FR-4a writes only existing event types (`structured_failure`); FR-4b writes the new `calibration_result` event type per the additive extension established by ADR-0058 (this Blueprint's second new ADR). The Q-CS-1b staleness banner reads `calibration_result` events from the same surface.
- **ADR-0039** (credential redaction posture): FR-4a and FR-4b both use the existing `log_mcp_event` helper which implements redaction-at-source.
- **ADR-0040** (Serena narrowed always-on; precedent for the seven sub-agent allowlists): unchanged by this feature (NFR-15).
- **ADR-0041** (install-mechanism hybrid, v1.0.1): the canonical invocation prescription source FR-3 OP-11 compares `.mcp.json` against. This Blueprint annotates **two rows** with `[DEPRECATED INVOCATION FORM]` markers (v2.1 expansion per Architecture Audit cycle 1 finding I-AA-003): **row 71 (`mcp-openapi-schema`)** with `[DEPRECATED — removed 2026-05-24]` (server fully removed from `.mcp.json` on that date), and **row 70 (Serena)** with `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is `serena start-mcp-server` from PATH after `uv tool install`; see postCreate.sh:82 + .mcp.json:28-31]` (the row documents `uvx --from "git+..."` but the runtime invocation is the installed binary from PATH; this is the same shape of drift as row 71 and would produce the same day-one BLOCKER false-positive under the FR-3 canonicalize+opaque-tokens algorithm). Both annotations are inline annotations, not decision-text rewrites (see FR-3 design); ADR-0005 hygiene is honored.
- **ADR-0042** (auditing-mcp family graduation): the OP-rule extension contract FR-3's new OP-11 follows.
- **ADR-0043** (auditing-mcp Gate-6 hard gate): the gate the new OP-11 rule inherits.
- **ADR-0044** (flatten execution dispatch hierarchy): the canonical source for `parent-driven-workaround` as a documented dispatch posture. ADR-0057 canonicalizes its on-disk surface.
- **ADR-0056** (no carve-outs in canonical placement): ADR-0057 and ADR-0058 both live at `adrs/` per this rule.
- **ADR-0057** (`checkpoint.execution_mode` as first-class documented field; authored Blueprint v1, preserved through v2; **prose-only amended to v1.0.1 in v2.1 per Architecture Audit cycle 1 finding I-AA-004**): unchanged by the FR-4 reshape. The v1.0.1 amendment reworded the §Context framing from "no existing `execution_mode` field on `checkpoint.json` today" to "promote-and-formalize" — the `execution_mode` field is documented in `recipe-feature-pipeline/SKILL.md:138` and 412 and is present (currently nulled) in this feature's working `checkpoint.json:106`. ADR-0057's load-bearing contribution is the field's promotion to first-class documented audit-surface status (the closed enum, the writer, the reader, the absence-default rule), not its introduction. The decision content is unchanged; only the framing of the field's pre-existing state was corrected.

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|---|---|---|
| GitHub Actions runner | `ubuntu-latest` | Host for BOTH the FR-5 `mcp-connectivity-smoke.yml` workflow and the new FR-4c `gitnexus-grammar-skip-calibration.yml` workflow. |
| `devcontainers/ci` Action | `devcontainers/ci@<SHA>` (third-party; SHA pin REQUIRED at implementation; same SHA reused across both workflows per cicd-design v0.3.0 §SHA-pinning) | Builds and runs the project's devcontainer image inside both CI workflows. |
| `actions/checkout` Action | `actions/checkout@<SHA>` (first-party; major-version tag acceptable, SHA preferred; same SHA reused across both workflows) | Checks out the PR / branch tree for both workflows. |
| Claude Code CLI | Pinned by the devcontainer's `claude-code` Feature | Provides `claude --bare -p` for the FR-5 invocation. Version pin discipline tracked as Q-CICD-1. |
| `gitnexus@1.6.5` npm package | Pinned via `GITNEXUS_TAG` in `.devcontainer/versions.env` | Subject of the FR-4a static-shape check and the FR-4b behavioral calibration. FR-4c's weekly cron and on-change-to-`versions.env` trigger force the calibration to run. |
| Anthropic Agent SDK contracts | `system/init` event; `McpServerStatus` enum (`connected | failed | needs-auth | pending | disabled`) | The contract-bearing surface FR-5 consumes; documented at `https://code.claude.com/docs/en/agent-sdk/mcp` and `https://code.claude.com/docs/en/agent-sdk/typescript`. |

### Agreement Checklist

#### Scope
- [x] Verdict-vs-findings parity validator at the orchestrator's dispatch boundary (FR-1).
- [x] Orchestrator dispatch self-check at orchestrator entry (FR-2).
- [x] `auditing-mcp` OP-11 audit rule (FR-3) plus inline `[DEPRECATED]` annotations on **ADR-0041 row 71 (mcp-openapi-schema) AND row 70 (Serena)** (v2.1 expansion: row 70 added per Architecture Audit cycle 1 finding I-AA-003 — same shape of drift as row 71).
- [x] **FR-4a — sub-100 ms static-shape check** inserted into `.devcontainer/postCreate.sh` top-level flow between current lines 197 and 198 (BEFORE `install_gitnexus`, AFTER `install_terraform_mcp`). **Replaces v1's placement inside `install_gitnexus()`.**
- [x] **FR-4b — opt-in behavioral calibration script** at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Performs the full scratch-dir install with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`, asserts Signal 1 (stderr regex) + Signal 3 (artifact absence) + optional negative-assertion confirmation, emits exactly one `calibration_result` event per ADR-0058. **NEW in v2** (replaces v1's `calibrate-gitnexus-grammar-skip.sh` placeholder with the full contract).
- [x] **FR-4c — new CI workflow** at `.github/workflows/gitnexus-grammar-skip-calibration.yml`. Triggers: Monday 07:00 UTC cron + `pull_request.paths: ['.devcontainer/versions.env', '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh']` + `workflow_dispatch`. Runs in devcontainers/ci-built image. `permissions: contents: read`. `concurrency: gitnexus-calibration` with `cancel-in-progress: false`. `timeout-minutes: 5`. **NEW in v2.**
- [x] **Q-CS-1b runtime staleness banner** in `postCreate.sh`. Reads the most recent `calibration_result` event from `mcp-events.jsonl`; emits a degraded banner if no event has been recorded in the last 2 weeks (or if no `calibration_result` event has ever been recorded). **NEW in v2** (admitted per composer arbitration; defeats the user-named "script that quietly stops running" trap as a belt-and-suspenders defense alongside FR-4c's cron).
- [x] New CI workflow at `.github/workflows/mcp-connectivity-smoke.yml` (FR-5).
- [x] Cross-cutting actionable-diagnostic discipline across all five mechanisms (FR-6 — FR-4 family counts as one mechanism per PRD §FR-6 verbatim).
- [x] Deferral-register row tightening for B-1 and H-4 (FR-7).
- [x] **Two new ADRs**: ADR-0057 (`checkpoint.execution_mode` first-class field — unchanged from v1) and **ADR-0058 (`calibration_result` event-type additive extension — NEW in v2)**.

#### Non-Scope (Explicitly not changing)
- [x] No new MCP server; no new MCP allowlist entry (NFR-15, ADR-0040).
- [x] No reviewer agent contract changes (the agents' `verdict` and `findings` shapes are read-only consumed by FR-1).
- [x] No `.mcp.json` content changes (read-only consumed by FR-3 and FR-5).
- [x] No ADR-0041 decision-text mutations (the marker is an annotation, not a rewrite).
- [x] No CLAUDE.md sentence additions beyond the single-character counter update `OP-1..OP-10` → `OP-1..OP-11`.
- [x] No patches to the still-broken MCP server files (PRD Product Policy Decisions row 4).
- [x] **No expansion of the event-type vocabulary beyond the single additive extension to four values established by ADR-0058 (NEW in v2).**
- [x] **No invocation of the FR-4b script from any path of `postCreate.sh` (per AC-CS-FR-4b-3 — invocation is exclusively manual-by-maintainer OR via the FR-4c CI workflow).**
- [x] **No FR-4c-side reimplementation of the calibration's Signal 1 / Signal 3 logic (the script is the authoritative writer; CI invokes by exit code).**
- [x] No expansion into the eight Won't-Have items deferred to the follow-on systemic-remediation feature. **Carve-out boundary reverified intact in v2.**

#### Constraints
- [x] Parallel operation: Yes — all five mechanisms can coexist with the prior pipeline and with each other (NFR-11 per-mechanism isolation). FR-4a, FR-4b, and FR-4c are also independently exercisable.
- [x] Backward compatibility: Required — applies to existing reviewer outputs (NFR-9), to `.mcp.json` entries already matching ADR-0041 (NFR-10), to pre-feature `checkpoint.json` files lacking the `execution_mode` field (per ADR-0057), and to existing `mcp-events.jsonl` consumers that ignore unknown event types (per ADR-0037's forward-compatibility posture, preserved by ADR-0058's additive-extension shape).
- [x] Performance measurement: Required for FR-5 pre-merge gate (D-0010); concrete thresholds set for NFR-1, NFR-2, NFR-3 (FR-4a sub-100 ms), NFR-4 (per-workflow under 5 min). FR-4c shares NFR-4's per-workflow budget.
- [x] Zero-downtime deployment: N/A — none of the mechanisms is a service.
- [x] Forward-compatible migration: Required for `checkpoint.json` — absence of `execution_mode` field on pre-feature checkpoints maps to `specialist-dispatch` (ADR-0057). Required for `mcp-events.jsonl` — existing consumers that ignore unknown event types continue to ignore `calibration_result` events; the Q-CS-1b staleness banner gracefully handles the case where no `calibration_result` events have been written yet (infinite staleness).

#### Applicable Standards
- [x] EARS acceptance-criteria format `[explicit]` — Source: KB-documentation-criteria `references/disciplines/ears-acceptance-criteria.md`.
- [x] OP-rule script naming `audit_op<N>_<short-descriptor>.py` `[explicit]` — Source: `.claude/skills/auditing-mcp/SKILL.md` (existing OP-1..OP-10 precedent).
- [x] OP-rule exit-code convention `0/1/2 = no-findings/blocker/internal-error` `[explicit]` — Source: existing audit_op*.py scripts under `auditing-mcp/scripts/`.
- [x] SHA-pinning of third-party GitHub Actions `[explicit]` — Source: KB-github-actions-platform non-negotiable #1. **Applied symmetrically to both FR-5 and FR-4c workflows in v2.**
- [x] Least-privilege `permissions:` blocks on workflows `[explicit]` — Source: KB-github-actions-platform non-negotiable #2. Both workflows declare `contents: read` only.
- [x] `set -euo pipefail` shell posture `[implicit]` — Evidence: `.devcontainer/postCreate.sh:31`, `.devcontainer/postStart.sh`, `.devcontainer/lib/log-mcp-event.sh:15` — Confirmed: Yes. FR-4a relies on this for fail-closed posture at the top-level (not inside a function with `|| emit_degraded_banner`).
- [x] Dual-stream diagnostic convention (plain-text echo + structured JSONL) `[implicit]` — Evidence: `.devcontainer/postCreate.sh` + `log_mcp_event` usage — Confirmed: Yes, adopted as the FR-6 surface convention for the Codespaces layer; FR-4a and FR-4b both honor it.

#### Quality Assurance Mechanisms

- [x] `actionlint` (binary or `mcp__actionlint-mcp__lint_workflow`) — Enforces: GitHub Actions YAML correctness, SHA-pinning, no-untrusted-input-interpolation — Config: KB-github-actions-platform — Covers: `.github/workflows/mcp-connectivity-smoke.yml` AND `.github/workflows/gitnexus-grammar-skip-calibration.yml` (both workflows, per cicd-design v0.3.0 §Plan task — actionlint deferral) — Status: `adopted` (Plan task pre-commit for each).
- [x] `auditing-mcp` Gate-6 hard gate per ADR-0043 — Enforces: OP-1..OP-11 rules on every pipeline run — Config: `.claude/skills/auditing-mcp/` — Covers: `.mcp.json` + ADR-0041 — Status: `adopted` (extended by FR-3).
- [x] `verdict_findings_parity.py` orchestrator-step gate (NEW) — Enforces: FR-1 verdict-vs-findings consistency — Config: `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` — Covers: 9 reviewer-completion invocation sites across 5 reviewer-shaped agents — Status: `adopted`.
- [x] Orchestrator dispatch self-check (NEW) — Enforces: FR-2 FULL-scope + parent-driven-workaround refusal — Config: `.claude/skills/recipe-feature-pipeline/SKILL.md` — Covers: every orchestrator entry — Status: `adopted`.
- [x] **FR-4a static-shape check (NEW; REVISED in v2)** — Enforces: A1 env-var set, A2 tag pinned, A3 versions.env source-of-truth, A4 npm root predictable on every devcontainer rebuild — Config: top-level block in `.devcontainer/postCreate.sh` between current lines 197 and 198 — Covers: every devcontainer build (cache-hit and cache-miss alike) — Status: `adopted`. **REPLACES v1's `install_gitnexus()`-internal placement.**
- [x] **FR-4b opt-in behavioral calibration script (NEW in v2)** — Enforces: Signal 1 stderr regex per-grammar match + Signal 3 artifact-path absence + optional negative-assertion artifacts-built confirmation when invoked — Config: `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` — Covers: manual maintainer invocation OR FR-4c CI invocation — Status: `adopted`. Emits exactly one `calibration_result` event per run per ADR-0058.
- [x] **FR-4c calibration CI workflow (NEW in v2)** — Enforces: weekly invocation of FR-4b on Monday 07:00 UTC cron + on-change-to-`versions.env` + manual `workflow_dispatch` — Config: `.github/workflows/gitnexus-grammar-skip-calibration.yml` — Covers: scheduled-cron and pin-bump-PR drift detection cadences — Status: `adopted`.
- [x] **Q-CS-1b staleness banner (NEW in v2)** — Enforces: `postCreate.sh` reads most recent `calibration_result` event; emits degraded banner if event older than 2 weeks (or absent) — Config: small block in `.devcontainer/postCreate.sh` adjacent to FR-4a's block — Covers: every devcontainer rebuild — Status: `adopted`. Belt-and-suspenders against the user-named "calibration script that quietly stops running" failure mode.
- [x] `mcp-connectivity-smoke.yml` (FR-5) — Enforces: every server in `.mcp.json` reports `status: connected` from a freshly-provisioned devcontainer — Config: `.github/workflows/mcp-connectivity-smoke.yml` — Covers: PRs touching `.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**` — Status: `adopted`.

### Problem to Solve

The MCP incident shipped five of seven servers broken in production. The postmortem (captured in `Issues/cross-artifact-divergence-detection-gap/proposal.md`) traced the failure to a structural gap: each pipeline gate inspected its own artifact in isolation and never compared an ADR's prescription against the file that actually shipped. The full systemic remediation is deferred. This feature is the carve-out — five low-cost, locally scoped, mechanically bounded changes that together close roughly a third of the catalogued incident defects plus the single highest-risk deferral from the prior devcontainer-MCP feature's register.

Each change addresses one named failure mode:

- **FR-1**: a reviewer returning an "approved" verdict alongside a blocking finding silently propagated past the orchestrator.
- **FR-2**: an orchestrator dispatching FULL-scope work with a stage configured for single-agent fallback silently lost per-layer fan-out.
- **FR-3**: an MCP server's `.mcp.json` entry drifted from its ADR-0041 prescription without being flagged at any gate.
- **FR-4** (now a family of three sub-mechanisms with different cadences per the v0.3.0 reshape): a Codespace install silently produced a half-working environment when an upstream env-var contract drifted (per-rebuild static-shape: FR-4a; behavioral via opt-in calibration: FR-4b; observable on CI cadence + pin-bump: FR-4c).
- **FR-5**: a PR changing `.mcp.json` (or the devcontainer or an audit skill) merged with a server that no longer reached `connected` state.

The FR-4 reshape rationale (per PRD v0.3.0 §Background): per-rebuild and behavioral are different questions on different cadences. The per-rebuild question is static-shape ("did someone delete the env-var, fat-finger the pin, or rename the artifact path?") — sub-100 ms, runs on every rebuild. The behavioral question is "has upstream honored the env-var contract at this tag?" — costs a full scratch install, runs only on the cadences where the question can change (weekly cron catches gradual drift; on-change-to-`versions.env` catches acute pin-bump drift; `workflow_dispatch` lets the maintainer ask the question on demand). Conflating them in v1 either doubled per-rebuild cost against ADR-0041's 7-12 min codespace budget or quietly stopped firing as a maintainer-only script.

### Current Challenges

The current pipeline has these specific structural gaps verified by Discovery:

- The `execute-task-quality-handler` agent's output contract today structurally allows `APPROVED` status alongside a `severity: blocker` finding (codebase-C-0018 verified).
- `scope_class` is read exactly once at line 350 of `recipe-feature-pipeline/SKILL.md`, inside Stage 13 (Deliverable Packaging) — too late for the FR-2 dispatch self-check to consume it (codebase-C-0028 verified).
- ADR-0041 still lists `mcp-openapi-schema` as one of seven invocation rows at line 71; `.mcp.json` removed it on 2026-05-24 leaving six servers (codebase-C-0038, codebase-C-0041, codebase-C-0105 verified). A naive symmetric-difference parity rule would emit a day-one BLOCKER false positive.
- **(v2.1 addition per Architecture Audit cycle 1 finding I-AA-003)** ADR-0041 row 70 (Serena) documents `uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server` as the invocation form, but `.mcp.json` lines 28-31 record `command: "serena", args: ["start-mcp-server"]` (the installed binary on PATH) per the actual install pattern in `.devcontainer/postCreate.sh:82` (`uv tool install -p 3.13 "serena-agent==${SERENA_VERSION}" --prerelease=allow`). Under the FR-3 canonicalize+opaque-tokens algorithm, row 70's Form column ↔ `.mcp.json` runtime form does not match — distinct command verbs, distinct arg shape. This is the same shape of drift as row 71 and would produce a day-one BLOCKER false positive without an annotation. v2.1 admits row 70 into the `[DEPRECATED INVOCATION FORM]` annotation list alongside row 71.
- The canonical Claude Code CLI docs are silent on `claude mcp list`'s exit-code and stdout-format contracts (t002-C-0001, t002-C-0002 verified) — a workflow that depends on the command's behavior depends on undocumented surface.
- GitNexus's `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var contract at the pinned v1.6.5 tag governs dart and proto only, not Swift, despite the upstream README's broader claim (t001-C-0022, t001-C-0038 verified). The behavioral cost of verifying this contract is non-trivial (~30 s scratch install) and cannot honestly be paid on every devcontainer rebuild.
- **(v2 addition; v2.1 prose correction)** ADR-0037's `mcp-events.jsonl` event-type vocabulary is closed at three values (`install_complete`, `readiness_probe`, `structured_failure`) per the OP-7 audit rule (the schema-validation rule implemented by `audit_op7_events_schema.py`; OP-6 audits credential redaction in the runtime log). The FR-4b calibration's outcome semantically does not fit those three; admitting a fourth value (`calibration_result`) requires an additive extension per ADR-0058. [v2.1 note: v2.0.0 of this Blueprint enumerated the three pre-existing event types as `primary_degraded / readiness_probe / structured_failure`, inheriting the ADR-0037 v1.0.0 / v1.0.1 prose error. ADR-0037 was corrected to v1.0.2 in lockstep with this Blueprint pass (per Architecture Audit cycle 1 finding I-AA-001); the actual on-disk vocabulary per `audit_op7_events_schema.py` `VALID_EVENT_TYPES` and per the 8+ live `log_mcp_event '{event:"install_complete",...}'` emissions in `.devcontainer/postCreate.sh` is `install_complete`. `primary_degraded` is a boolean sub-field of `structured_failure`, not a distinct event type. v2.1 also corrects the OP-rule label (was OP-6, now OP-7) per finding I-AA-002. The Blueprint's very mission — preventing documentation-vs-realization drift — applies retroactively to the ADRs it cites; that retroactive application is the practical demonstration of the mission.]

### Requirements

#### Functional Requirements

- **FR-1** Verdict-vs-findings consistency check (Claude Code layer) — see PRD §FR-1.
- **FR-2** Orchestrator dispatch self-check refusing FULL-scope + single-agent-fallback (Claude Code layer) — see PRD §FR-2.
- **FR-3** `.mcp.json`-to-ADR-0041 parity audit rule OP-11 (Claude Code layer) — see PRD §FR-3.
- **FR-4a** GitNexus per-rebuild static-shape check (Codespaces layer) — see PRD §FR-4 verbatim and PRD §AC-FR-4a-*.
- **FR-4b** GitNexus opt-in behavioral calibration script (Codespaces layer) — see PRD §FR-4 verbatim and PRD §AC-FR-4b-*.
- **FR-4c** GitHub Actions workflow that drives FR-4b on Monday 07:00 UTC cron + on-change-to-`versions.env` + `workflow_dispatch` (CI/CD layer) — see PRD §FR-4 verbatim and PRD §AC-FR-4c-*.
- **FR-5** CI workflow for MCP connectivity smoke (CI/CD layer) — see PRD §FR-5.
- **FR-6** Actionable diagnostics for every mechanism (cross-cutting) — see PRD §FR-6 verbatim. The FR-4 family (FR-4a, FR-4b, FR-4c) counts as a single mechanism for this requirement.
- **FR-7** Update deferral register to mark H-4 and B-1 adopted (Claude Code layer) — see PRD §FR-7.

#### Non-Functional Requirements

- **Performance**: FR-1 validator p95 ≤ 250 ms on ≤ 100 KB reviewer outputs (NFR-1 concrete threshold). FR-2 self-check p95 ≤ 100 ms (NFR-2). **FR-4a static-check p95 ≤ 100 ms with no network access (NFR-3 — tightened from v1's ≤ 2 s on cache-miss; FR-4a is now static-only)**. **FR-4b's wall-clock budget is folded into NFR-4's per-workflow ceiling under FR-4c**. **NFR-4 widened to per-workflow: both FR-5 and FR-4c shall complete in under 5 minutes (cicd-design v0.3.0 commits to FR-4c p95 under 2 minutes; FR-5 p95 under 4 minutes; pre-merge validation gate per D-0010 confirms FR-5)**.
- **Reliability**: Determinism — same input produces same verdict twice in succession (NFR-5). Fail-closed on internal errors (NFR-6). FR-4a halts `postCreate.sh` via `set -euo pipefail` on static-check failure (top-level placement; no `|| emit_degraded_banner` masking).
- **Security**: No new credential surface (NFR-7). No credentials in diagnostics (NFR-8).
- **Maintainability**: NFR-9 backward compatibility for existing reviewer outputs. NFR-10 backward compatibility for `.mcp.json` entries already matching ADR-0041.
- **Operability**: NFR-11 per-mechanism isolation (each mechanism exercisable end-to-end without the other four). **NFR-13 (REVISED v2): the existing three event types in `mcp-events.jsonl` are preserved verbatim; FR-4b's `calibration_result` event type is admitted as an additive extension per ADR-0058 (NEW in v2). No event types beyond the four (three pre-existing + `calibration_result`) are introduced.** **NFR-14 Codespace boot cost bounded by NFR-3's sub-100 ms threshold (FR-4a only runs in the post-create path; FR-4b is opt-in / CI-driven; the Q-CS-1b staleness banner adds negligible overhead via one `jq` read of `mcp-events.jsonl`).** NFR-15 agent-driven workflow remains accessible (no MCP allowlist changes).

## Acceptance Criteria (AC) - EARS Format

Acceptance criteria are grouped by Functional Requirement; cross-layer/operational ACs follow. **FR-1, FR-2, FR-3, FR-5, FR-7 ACs are preserved verbatim from Blueprint v1; FR-4 ACs are restructured to reflect the v0.3.0 three-sub-mechanism split.**

*(v2.3 inheritance note, added per Cross-Artifact Audit cycle 1 finding I-CA-002 / reconciliation-log-r3.md.)* The AC-NFR-N-a family — specifically AC-NFR-1-a through AC-NFR-13-b — is inherited by reference from PRD v0.3.0 §Non-Functional Requirements (lines 336-413; canonical EARS text lives there); a reader who needs the full EARS text for any AC in that range should consult the corresponding PRD subsection (e.g., AC-NFR-1-a's full text is at PRD §Performance / NFR-1; AC-NFR-13-b's full text is at PRD §Data / NFR-13). The v2.2 lift cycle was scoped narrowly to ACs the Blueprint v2.1 didn't already define (the AC-CC / AC-CS / AC-CICD families lifted from per-layer design docs, plus the freshly authored AC-NFR-14 and the AC-NFR-15 alias to AC-X-3); the AC-NFR-N-a family was always cited-by-ID with the PRD as canonical definition, and that inheritance has always worked. The asymmetry between inlined v2.2 ACs and inherited AC-NFR-N-a ACs is structural — not a v2.2 oversight — and is preserved here intentionally because a full lift of the AC-NFR-N-a family would duplicate text cleanly cited from the PRD without adding traceability value.

### Functional ACs

#### FR-1 — Verdict-vs-findings parity validator — Layer: Claude Code

*(v2.2: AC-CC-1-d/e/f/g lifted verbatim from cc-design v0.2.0 §FR-1 cluster per Plan review reconciliation I-DR-002. AC-CC-1-a/b/c/h preserved from Blueprint v1.)*

- **AC-CC-1-a** — When the orchestrator detects that any of the 5 reviewer-shaped sub-agents in scope (across the 9 distinct invocation sites) has written its verdict+findings output to disk, the system shall invoke `verdict_findings_parity.py` with the output path and the agent name before advancing to the next stage.
- **AC-CC-1-b** — If the validator's exit code is 1 and the agent's verdict is in the approving column and the findings array contains at least one finding with `severity` equal to `BLOCKER`, then the system shall halt orchestrator advance.
- **AC-CC-1-c** — see Blueprint v1.
- **AC-CC-1-d** *(EARS — State-driven)*: Where the agent's verdict is in the approving column and the findings array contains no finding with `severity` equal to `BLOCKER`, the system shall pass the reviewer output through unchanged.
- **AC-CC-1-e** *(EARS — Event-driven, NFR-6 fail-closed)*: When the validator returns exit 2, the system shall treat the run as failed-closed, emit the validator's stderr to the user, and require user resolution before any retry.
- **AC-CC-1-f** *(EARS — Ubiquitous, FR-6)*: The validator's JSON output shall always carry the four FR-6 fields (mechanism name, offending artifact path, rule violated, remedial-action hint).
- **AC-CC-1-g** *(EARS — Ubiquitous, NFR-5 determinism)*: When invoked twice on the same input file with the same agent name, the validator shall produce byte-identical stdout and the same exit code.
- **AC-CC-1-h** — When the validator runs on any reviewer-shaped output that the prior pipeline accepted as conformant (any output without a BLOCKER finding in the findings array, regardless of verdict; or any non-approving verdict regardless of findings), the validator shall return exit 0.

#### FR-2 — Orchestrator dispatch self-check — Layer: Claude Code

*(v2.2: AC-CC-2-d/e/f lifted verbatim from cc-design v0.2.0 §FR-2 cluster per Plan review reconciliation I-DR-002. AC-CC-2-a/b/c/g preserved from Blueprint v1.)*

- **AC-CC-2-a** — When the orchestrator begins dispatch after Stage 1 (Intent Clarification) completes, the system shall read `scope_class` and enumerate every stage's `checkpoint.execution_mode` value per ADR-0057.
- **AC-CC-2-b** — If `scope_class == "FULL"` and any stage's `execution_mode == "parent-driven-workaround"`, the system shall refuse to enter the dispatch loop.
- **AC-CC-2-c** — see Blueprint v1.
- **AC-CC-2-d** *(EARS — Ubiquitous, FR-6)*: The refusal diagnostic shall always carry the four FR-6 fields (mechanism name, offending artifact paths, rule violated, remedial-action hint).
- **AC-CC-2-e** *(EARS — Ubiquitous, NFR-5 determinism)*: When the orchestrator dispatch self-check runs twice in succession against the same `intent-clarification.md` and the same `checkpoint.json`, the system shall produce the same verdict (pass or refusal) and the same diagnostic both times.
- **AC-CC-2-f** *(EARS — Unwanted-behavior, NFR-6 fail-closed)*: If `intent-clarification.md` is missing or unparseable when the self-check needs to read it, the system shall treat the run as failed-closed and emit a diagnostic naming the missing-or-unparseable file, rather than skipping the self-check.
- **AC-CC-2-g** — see Blueprint v1.

#### FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule OP-11 — Layer: Claude Code

*(v2.2: AC-CC-3-c through AC-CC-3-k lifted verbatim from cc-design v0.2.0 §FR-3 cluster per Plan review reconciliation I-DR-002. AC-CC-3-a/b/l preserved from Blueprint v1. Alphabetic ordering reads a, b, c, d, e, f, g, h, i, j, k, l.)*

- **AC-CC-3-a** — When `audit_op11_adr_parity.py` is invoked, the system shall iterate every `.mcp.json` server entry and locate the corresponding non-deprecated row in ADR-0041.
- **AC-CC-3-b** — see Blueprint v1.
- **AC-CC-3-c** *(EARS — State-driven)*: If ADR-0041 contains no non-deprecated row for a server present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-adr-0041`.
- **AC-CC-3-d** *(EARS — State-driven)*: If ADR-0041 contains a non-deprecated row whose server name is absent from `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-mcp.json`.
- **AC-CC-3-e** *(EARS — State-driven)*: Where ADR-0041 contains a row tagged `[DEPRECATED]` and the server is absent from `.mcp.json`, the system shall NOT emit a finding for that row.
- **AC-CC-3-f** *(EARS — Unwanted-behavior)*: If ADR-0041 contains a row tagged `[DEPRECATED]` and the server is present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: deprecated-row-still-present`.
- **AC-CC-3-g** *(EARS — Ubiquitous, NFR-10 backward-compat)*: When OP-11 runs on a `.mcp.json` entry whose canonicalized invocation form equals the canonicalized ADR-0041 prescription, the system shall produce no finding for that entry.
- **AC-CC-3-h** *(EARS — Ubiquitous, FR-6)*: Each finding shall always carry the four FR-6 fields (mechanism name, offending server / file, rule violated, remedial-action hint).
- **AC-CC-3-i** *(EARS — Ubiquitous, NFR-5 determinism)*: When OP-11 runs twice on the same `.mcp.json` and the same ADR-0041, the system shall produce byte-identical stdout and the same exit code.
- **AC-CC-3-j** *(EARS — Ubiquitous, NFR-7 / NFR-8 no-credentials)*: The OP-11 rule shall not read any environment variable; the `${VAR}` placeholders shall be treated as opaque tokens both in canonicalization and in diagnostic output.
- **AC-CC-3-k** *(EARS — Unwanted-behavior, NFR-6 fail-closed)*: If ADR-0041 cannot be parsed (file missing or table not extractable), or `.mcp.json` cannot be parsed (file missing or invalid JSON), then the system shall return exit 2 with a diagnostic naming the parse failure.
- **AC-CC-3-l** — see Blueprint v1 (NFR-13 event-surface: OP-11 does not write to `.claude/runtime/mcp-events.jsonl`).

#### FR-4a — GitNexus per-rebuild static-shape check — Layer: Codespaces

*(NEW structure in Blueprint v2; replaces v1's FR-4 ACs. Mirrors codespaces-design v0.3.0 §AC-CS-FR-4a-* and PRD v0.3.0 §AC-FR-4a-*.)*

- **AC-CS-4a-1** *(Event-driven)*: When `.devcontainer/postCreate.sh` reaches the FR-4a block (between current lines 197 and 198), the system shall assert (A1) `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` equals the literal string `1`, AND (A2) `$GITNEXUS_TAG` matches `^v?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$`, AND (A3) `$GITNEXUS_TAG` matches the value in `.devcontainer/versions.env`, AND (A4) `npm root -g` returns a non-empty path whose parent is writable.
- **AC-CS-4a-2** *(Ubiquitous)*: When the codespace is created or rebuilt, the system shall execute the FR-4a static check on both cache-hit and cache-miss paths with no measurable cost difference between the two (the check never invokes `npm install -g`; there is no cache-vs-no-cache semantics).
- **AC-CS-4a-3** *(State-driven, fail-closed)*: If any of A1/A2/A3/A4 fails, the system shall (i) emit a `structured_failure` event via `log_mcp_event` whose `note:` field names FR-4a, the failing sub-assertion, the observed value, and a one-line remedial hint, (ii) emit a plain-text operator diagnostic to stderr, and (iii) cause `postCreate.sh` to exit non-zero via `set -euo pipefail` BEFORE `install_gitnexus` is invoked.
- **AC-CS-4a-4** *(Unwanted-behavior, no Swift assertion)*: The system shall not assert any condition about `tree-sitter-swift`'s build outcome as a function of `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (at `gitnexus@1.6.5` the env-var governs only Dart and Proto per T-001 F-4).
- **AC-CS-4a-5** *(Ubiquitous, sentinel-less)*: The FR-4a static check shall create no sentinel file and consult no sentinel of its own; its outcome is encoded only in the `structured_failure` event record (on fail) or in the silent green-light into `install_gitnexus` (on pass).
- **AC-CS-4a-6** *(Ubiquitous, NFR-3 budget)*: When the FR-4a static check (A1 + A2 + A3 + A4 + event emission) runs on the configured `hostRequirements.cpus: 4` machine class, the system shall complete the static check in under 100 milliseconds at p95 measured over 10 consecutive rebuilds, and shall not require any network access.
- **AC-CS-4a-7** *(Ubiquitous, FR-6 diagnostic)*: When FR-4a emits a failing diagnostic, the system shall name the four FR-6 elements (mechanism = "FR-4a"; offending artifact = one of `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` / `$GITNEXUS_TAG` / `versions.env` / `npm root -g`; rule violated = one of the four fixed signal tokens `signal-a1-env-var-unset-or-wrong` / `signal-a2-tag-pin-malformed` / `signal-a3-versions-env-mismatch` / `signal-a4-artifact-paths-unpredictable`; remedial-action hint).

#### FR-4b — GitNexus opt-in behavioral calibration script — Layer: Codespaces

*(NEW in Blueprint v2. Mirrors codespaces-design v0.3.0 §AC-CS-FR-4b-* and PRD v0.3.0 §AC-FR-4b-*.)*

- **AC-CS-4b-1** *(Event-driven, calibration contract)*: When the maintainer or CI invokes `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` with no arguments, the system shall (i) read `GITNEXUS_TAG` from `.devcontainer/versions.env`, (ii) create a scratch directory via `mktemp -d`, (iii) install `gitnexus@${GITNEXUS_TAG}` into the scratch directory with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` and stderr captured, (iv) assert Signal 1 (per-grammar stderr regex `\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)` matched at least once for each of `dart` and `proto`), (v) assert Signal 3 (artifact-path absence for both grammars at the scratch-prefix-derived paths), (vi) run the optional negative-assertion confirmation with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0` in a second scratch directory and assert the artifacts ARE built (enabled by default), (vii) emit exactly one `calibration_result` event to `.claude/runtime/mcp-events.jsonl` per ADR-0058's canonical payload shape, and (viii) clean up the scratch directories before exit.
- **AC-CS-4b-2** *(Ubiquitous, event-as-primary-channel)*: The calibration script shall emit one `calibration_result` event per run to `.claude/runtime/mcp-events.jsonl` regardless of pass/fail/drift_detected outcome; the script's exit code (0 on pass, non-zero on any signal failure) shall be the secondary observability channel.
- **AC-CS-4b-3** *(Unwanted-behavior, not invoked from postCreate.sh)*: The system shall NOT invoke `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` from any path of `.devcontainer/postCreate.sh`. (Invocation is exclusively manual-by-maintainer OR via the FR-4c CI workflow.)
- **AC-CS-4b-4** *(Unwanted-behavior, no Swift assertion)*: The calibration script shall not assert any condition about `tree-sitter-swift`'s build outcome as a function of `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`.
- **AC-CS-4b-5** *(Ubiquitous, ADR-0058 conformance)*: The `calibration_result` event written by the script shall conform to ADR-0058's canonical payload shape: `{event: "calibration_result", timestamp, server: "gitnexus", mechanism: "fr-4b-gitnexus-grammar-skip", version: <GITNEXUS_TAG>, duration_ms, outcome ∈ {pass, fail, drift_detected}, signals: <map of per-Signal pass/fail/skipped>, note}`.
- **AC-CS-4b-6** *(Ubiquitous, FR-6 diagnostic)*: When FR-4b emits a fail or drift_detected outcome, the event's `note:` field and the script's stderr shall name the four FR-6 elements (mechanism = "FR-4b"; offending artifact = the pinned `GITNEXUS_TAG`; rule violated = the failing Signal name; remedial-action hint).
- **AC-CS-4b-7** *(Ubiquitous, NFR-4 informational)*: When the calibration script is invoked, the system shall complete the full script (both scratch-dir installs + signal assertions + event emission + cleanup) in under 60 seconds wall-clock (informational; the load-bearing budget is NFR-4's per-workflow 5-minute ceiling enforced by FR-4c).

#### FR-4c — GitHub Actions workflow driving FR-4b — Layer: CI/CD

*(NEW in Blueprint v2. Mirrors cicd-design v0.3.0 §FR-4c and PRD v0.3.0 §AC-FR-4c-*.)*

- **AC-CICD-4c-1** *(Event-driven, weekly cron trigger)*: When the FR-4c GitHub Actions workflow at `.github/workflows/gitnexus-grammar-skip-calibration.yml` is triggered by its weekly cron (`0 7 * * 1` — Monday 07:00 UTC), the system shall invoke `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` inside the project's devcontainer image (built via `devcontainers/ci@<SHA>`) and surface the script's exit code as the workflow job's status.
- **AC-CICD-4c-2** *(Event-driven, on-change-to-`versions.env` trigger)*: When a pull request modifies `.devcontainer/versions.env` OR `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`, the system shall trigger the FR-4c workflow on that PR and surface the script's exit code as the workflow job's status, so a tag bump cannot merge without the behavioral calibration having been re-run on the new tag.
- **AC-CICD-4c-3** *(State-driven, fail surfaces in summary)*: When the FR-4c workflow runs and the calibration script exits non-zero, the system shall fail the workflow job and write a FR-6-shaped Markdown block to `$GITHUB_STEP_SUMMARY` naming: mechanism ("FR-4c calibration CI wiring"); calibration script path; the offending grammar (Dart or Proto) re-surfaced from the script's stdout; the failing Signal-N; remedial hint (multi-option: pin back, amend script, open follow-on).
- **AC-CICD-4c-4** *(Unwanted-behavior, trigger-restriction)*: Where the FR-4c workflow is triggered by any path-change set other than `.devcontainer/versions.env` or `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (and excluding the weekly cron and `workflow_dispatch`), the system shall not run the behavioral calibration; the behavioral cost is reserved for cron, pin-bump-on-the-two-specific-paths, and explicit manual triggers.
- **AC-CICD-4c-5** *(Event-driven, workflow_dispatch)*: When the FR-4c workflow is triggered by `workflow_dispatch`, the system shall invoke the calibration script identically to the cron path and surface the script's exit code as the job status.
- **AC-CICD-4c-6** *(Ubiquitous, NFR-4 budget per-workflow)*: The FR-4c workflow shall complete within 5 minutes (NFR-4 ceiling per-workflow); cicd-design v0.3.0 commits to p95 under 2 minutes on the standard `ubuntu-latest` runner.
- **AC-CICD-4c-7** *(Ubiquitous, concurrency)*: The FR-4c workflow shall declare `concurrency: { group: gitnexus-calibration, cancel-in-progress: false }` so that racing triggers (e.g., a `versions.env` PR opening at the same time as the cron tick) queue rather than emit duplicate `calibration_result` events.
- **AC-CICD-4c-8** *(Ubiquitous, NFR-7 / NFR-8 no credentials)*: The FR-4c workflow shall not read any new secret; the workflow shall not emit any environment-variable value identified as a credential carrier in its diagnostics. `permissions: contents: read` only.
- **AC-CICD-4c-9** *(Ubiquitous, exit-code-as-contract)*: The FR-4c workflow shall NOT re-implement the calibration's Signal 1 / Signal 3 logic; the script is the authoritative writer and the workflow consumes its exit code only.
- **AC-CICD-4c-10** *(Ubiquitous, no duplicate event emission)*: The FR-4c workflow shall NOT write any event to `.claude/runtime/mcp-events.jsonl`; the script is the authoritative event emitter (one `calibration_result` event per run per ADR-0058).
- **AC-CICD-4c-11** *(Ubiquitous, timeout)*: The FR-4c workflow shall declare `timeout-minutes: 5` so a runaway upstream-install hang fails loud rather than billing indefinitely.

#### FR-5 — MCP connectivity smoke workflow — Layer: CI/CD

*(Preserved verbatim from Blueprint v1. See blueprint-v1.md §FR-5 ACs AC-CICD-5-a through AC-CICD-5-g.)*

This Blueprint reconciles the PRD's AC-FR-5-a/b/c (which literally name `claude mcp list`) with the design's contract-bearing substitute (`claude --bare -p "noop" --output-format stream-json | jq ...`) per Q-CICD-9 resolution. The ACs in Blueprint v1 are rewritten to reference the substitute invocation; the behavioral intent is preserved verbatim. PRD Assumption A-3 is superseded.

- **AC-CICD-5-a** — When a PR modifies any file in the configured path-trigger set (`.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**`), the system shall run `.github/workflows/mcp-connectivity-smoke.yml`.
- **AC-CICD-5-b** *(State-driven, reconciles PRD AC-FR-5-b)*: If any server in the `mcp_servers[]` array reports `status != "connected"`, then the system shall fail the workflow job with a non-zero exit and surface the offending server names + their reported status in `$GITHUB_STEP_SUMMARY` per the FR-6 diagnostic format.
- **AC-CICD-5-c** *(State-driven, reconciles PRD AC-FR-5-c)*: When every server in the `mcp_servers[]` array reports `status == "connected"`, the system shall pass the workflow job and write a one-line confirmation to `$GITHUB_STEP_SUMMARY`.
- **AC-CICD-5-d** *(Event-driven, NFR-6 fail-closed)*: When `claude --bare -p` exits non-zero (the CLI itself failed), the system shall exit 2 from the workflow step and surface the failure to the user as an internal-error diagnostic distinguishable from the AC-CICD-5-b connectivity-fail case.
- **AC-CICD-5-e** *(Ubiquitous, FR-6)*: The `$GITHUB_STEP_SUMMARY` diagnostic on any failing run shall carry the four FR-6 fields.
- **AC-CICD-5-f** *(Ubiquitous, NFR-4 runtime budget)*: The workflow shall complete within 5 minutes (NFR-4 ceiling); the pre-merge validation gate per D-0010 confirms p95 ≤ 4 minutes before ship.
- **AC-CICD-5-g** — see Blueprint v1 (NFR-7 / NFR-8 no credentials).

*(v2.2: AC-CICD-5-b/c/d/e/f lifted verbatim from blueprint-v1.md lines 294-298 which originally introduced these reconciliations per cicd-design v0.3.0 §FR-5; per Plan review reconciliation I-DR-002.)*

#### FR-6 — Actionable diagnostics — Layer: cross-cutting

*(REVISED in Blueprint v2 to cover the four FR-4 family surfaces uniformly. Preserves Blueprint v1 intent.)*

- **AC-6-a** *(Ubiquitous)*: When any of the five mechanisms (FR-1, FR-2, FR-3, the FR-4 family — counting FR-4a + FR-4b + FR-4c as a single mechanism per PRD §FR-6 verbatim — and FR-5) emits a blocking diagnostic, the system shall include in the diagnostic at minimum: (1) the mechanism name **(or sub-mechanism label, e.g., `FR-4a`, `FR-4b`, `FR-4c`, when the family's sub-mechanisms emit independently)**, (2) the offending artifact path, (3) the rule or contract violated, and (4) a one-line remedial-action hint. The exact surface differs by layer: JSON-to-stdout for FR-1/FR-2/FR-3; plain-text echo + structured JSONL (`structured_failure` for FR-4a; `calibration_result` for FR-4b per ADR-0058) for the Codespaces-side; Markdown to `$GITHUB_STEP_SUMMARY` for FR-5 and FR-4c. The four fields are always present.

#### FR-7 — Deferral-register tightening — Layer: Claude Code

*(v2.2: AC-CC-7-b and AC-CC-7-c lifted verbatim from cc-design v0.2.0 §FR-7 cluster per Plan review reconciliation I-DR-002. AC-CC-7-a and AC-CC-7-d preserved from Blueprint v1.)*

- **AC-CC-7-a** — see Blueprint v1 (B-1 row carries the canonical "Adopted by `pipeline-quickwins-hardening-r1`" parenthetical with the date, slug, and link tokens; placement is the deliverable-archive verification step per D-0009).
- **AC-CC-7-b** *(EARS — Event-driven)*: When the feature reaches the verification step (deliverable-archive or separate housekeeping commit, per composer's D-0009 placement), the system shall verify that row H-4 carries the same parenthetical (with the same date / slug / link tokens).
- **AC-CC-7-c** *(EARS — State-driven)*: If either row's parenthetical is missing or differs from the canonical form, the system shall update the row to match. (Placement-agnostic: applies wherever composer places the verification step.)
- **AC-CC-7-d** — see Blueprint v1 (Why-excluded / Re-examination-trigger / Forgetting-risk cells carry the canonical post-adoption text).

### Cross-Layer / Operational ACs

- **AC-X-1** *(Event-driven, NFR-11 per-mechanism isolation)*: When any single mechanism (FR-1, FR-2, FR-3, the FR-4 family, FR-5) is enabled in isolation against a workspace where the other four are disabled, the system shall produce the mechanism's expected behavior for its named failure mode without depending on the others being enabled. **Within the FR-4 family, FR-4a, FR-4b, and FR-4c are also independently exercisable** — FR-4a runs on every rebuild regardless of whether FR-4b or FR-4c exist; FR-4b is invocable by maintainer regardless of whether FR-4c runs; FR-4c invokes FR-4b but is independent of FR-4a's per-rebuild path.
- **AC-X-2** *(Ubiquitous, NFR-13 event surface — REVISED in v2; PROSE-CORRECTED in v2.1)*: When FR-3, the FR-4 family, or FR-5 runs against a workspace with the existing MCP event surface enabled, the system shall not write any event of a type not already defined in ADR-0037 (`install_complete`, `readiness_probe`, `structured_failure`) **OR the additive extension established by ADR-0058 (`calibration_result`)**. The four-type closed-enum discipline is preserved.
- **AC-X-3** *(Ubiquitous, NFR-15 allowlists)*: This feature shall not modify the seven sub-agents' MCP allowlists per ADR-0040.
- **AC-X-4** *(NEW in v2; Ubiquitous, Q-CS-1b staleness banner)*: When `.devcontainer/postCreate.sh` runs on devcontainer rebuild, the system shall (i) read the most recent `calibration_result` event for `mechanism: "fr-4b-gitnexus-grammar-skip"` from `.claude/runtime/mcp-events.jsonl` via a small `jq` invocation, (ii) compare its timestamp to `now - 2 weeks`, (iii) if the most recent event is older than 2 weeks OR no `calibration_result` event has ever been recorded (infinite staleness), emit a single-line plain-text degraded banner to stderr naming the mechanism (`FR-4b calibration`), the staleness age (or "never run"), and a one-line remedial hint pointing the maintainer at the FR-4c workflow (`gh workflow run gitnexus-grammar-skip-calibration.yml`) or at the script's manual invocation path. The banner shall NOT cause `postCreate.sh` to fail-closed; it is informational. The banner shall NOT emit an `mcp-events.jsonl` event (banners are already a logged-at-rebuild observability surface per existing convention). Because the banner is informational and not blocking, it intentionally carries three of the four FR-6 diagnostic fields (mechanism + staleness-age-as-offending-state + remedial hint) and omits the "rule violated" field — no rule is violated, the calibration is merely stale.

### Non-Functional Coverage ACs

*(NEW in v2.2: AC-NFR-14 freshly authored and AC-NFR-15 aliased to AC-X-3 so Plan citations (T2.2 / T2.3 for AC-NFR-14; T4.2 for AC-NFR-15) resolve to canonical Blueprint definitions. Per Plan review reconciliation I-DR-002.)*

- **AC-NFR-14** *(NEW in v2.2; Ubiquitous, NFR-14 Codespace-boot-time bound)*: When `.devcontainer/postCreate.sh` runs on devcontainer rebuild with the FR-4a static-shape block and the Q-CS-1b staleness banner block both in place, the system shall not measurably extend the script's wall-clock execution time beyond NFR-14's per-script bound. Specifically, (i) FR-4a's static check completes in under 100 ms at p95 per AC-CS-4a-6, and (ii) the Q-CS-1b banner's single `jq` read of `.claude/runtime/mcp-events.jsonl` plus its `date` comparison plus its conditional `echo` add no more than 50 ms at p95 — total combined overhead under 150 ms at p95 measured over 10 consecutive rebuilds on the configured `hostRequirements.cpus: 4` machine class. The banner block shall not perform any network access, shall not spawn any container, and shall not invoke `npm`. (This AC names a measurable budget so Plan tasks T2.2 / T2.3 — which write the FR-4a block and the Q-CS-1b banner respectively — have a concrete bound to verify against, rather than relying on the narrative NFR-14 reference alone.)
- **AC-NFR-15** *(NEW in v2.2; alias for AC-X-3)*: This AC is an alias for AC-X-3 (the canonical MCP-allowlist no-change AC). Any Plan / Test citation of AC-NFR-15 shall be read as a citation of AC-X-3; the verification procedure for AC-NFR-15 is identical to AC-X-3 — confirm the seven sub-agents' MCP allowlists are byte-identical before and after the feature ships. (The alias exists so Plan task T4.2's NFR-15-named verification step resolves to a canonical Blueprint definition; downstream readers searching for either ID land at the same content.)

## Existing Codebase Analysis

### Implementation Path Mapping

*(Carried forward from Blueprint v1 with v2 deltas highlighted.)*

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | Existing | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Parent orchestrator (629 lines); subject of FR-1 wire-in and FR-2 self-check additions (UNCHANGED in v2) |
| Claude Code | Existing | `.claude/skills/auditing-mcp/` | Audit skill family-coordinator per ADR-0042; extended by FR-3 with OP-11 (UNCHANGED in v2) |
| Claude Code | Existing | `.claude/skills/auditing-shared/scripts/` | Python validator family; gains `verdict_findings_parity.py` for FR-1 (UNCHANGED in v2) |
| Claude Code | Existing | `.mcp.json` | Six MCP server registrations; read-only consumed by FR-3 and FR-5 (UNCHANGED in v2) |
| Claude Code | Existing | `adrs/ADR-0041-install-mechanism-hybrid.md` | Canonical invocation prescription; gains `[DEPRECATED]` annotations on **row 71 (mcp-openapi-schema)** AND **row 70 (Serena — v2.1 addition per Architecture Audit finding I-AA-003)** (FR-3) |
| Claude Code | Existing | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` | Verified and tightened by FR-7 (UNCHANGED in v2) |
| Claude Code | Existing | `CLAUDE.md` | Single-character counter update (`OP-1..OP-10` → `OP-1..OP-11`) at deliverable-archive time (UNCHANGED in v2) |
| Claude Code | New | `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` | FR-1 validator (UNCHANGED in v2) |
| Claude Code | New | `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` | FR-3 OP-11 audit rule (UNCHANGED in v2) |
| Claude Code | New | `.claude/skills/auditing-mcp/references/adr-parity.md` | FR-3 rationale + canonicalization rules + `[DEPRECATED]` convention (UNCHANGED in v2) |
| Claude Code | New | `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md` | ADR-0057 (authored Blueprint v1; UNCHANGED in v2) |
| Claude Code | **New (v2)** | `adrs/ADR-0058-calibration-result-event-type-additive-extension.md` | **ADR-0058 (authored Blueprint v2 — additive extension of ADR-0037's event-type vocabulary admitting `calibration_result`)** |
| Claude Code | **Modified (v2 Plan-task)** | `.claude/skills/KB-mcp-design/references/principles.md` | **Updated by Plan Authoring to document the four-type vocabulary per ADR-0058** |
| Claude Code | **Modified (v2 Plan-task)** | `.claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md` | **Updated by Plan Authoring to add `calibration_result` example record and `mechanism:` discriminator** |
| Codespaces | Existing | `.devcontainer/postCreate.sh` | **Subject of FR-4a static-shape check insertion AT TOP-LEVEL BETWEEN CURRENT LINES 197 AND 198 (CHANGED in v2 — v1 placed inside `install_gitnexus()` between line 142 and 143; v2 placement is honest to the static-only semantics and uses `set -euo pipefail` directly without `|| emit_degraded_banner` masking). ALSO subject of the NEW Q-CS-1b staleness banner block adjacent to FR-4a.** |
| Codespaces | Existing | `.devcontainer/versions.env` | Source of `GITNEXUS_TAG=1.6.5` and `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`; **also the FR-4c on-change path trigger** |
| Codespaces | Existing | `.devcontainer/lib/log-mcp-event.sh` | The `log_mcp_event` helper FR-4a uses to emit `structured_failure` events AND FR-4b uses to emit the new `calibration_result` event per ADR-0058 |
| Codespaces | **New (v2 — full contract)** | `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` | **FR-4b opt-in behavioral calibration script (v1 named the path as a placeholder; v2 fixes the full contract per AC-CS-4b-1..7). Performs scratch-dir install + Signal 1 + Signal 3 + negative-assertion; emits one `calibration_result` event per ADR-0058.** |
| CI/CD | New | `.github/workflows/mcp-connectivity-smoke.yml` | FR-5 workflow (UNCHANGED in v2) |
| CI/CD | **New (v2)** | `.github/workflows/gitnexus-grammar-skip-calibration.yml` | **FR-4c workflow — Monday 07:00 UTC cron + on-change-to-`versions.env`/`calibrate-gitnexus-grammar-skip.sh` + `workflow_dispatch`. `permissions: contents: read`. `concurrency: gitnexus-calibration; cancel-in-progress: false`. `timeout-minutes: 5`.** |

### Integration Points

*(Preserved from Blueprint v1; one new integration target added.)*

- **Integration Target**: the orchestrator (`recipe-feature-pipeline`) is the single dispatch nexus per ADR-0044; FR-1, FR-2, and ADR-0057's new field all integrate here.
- **NEW in v2 — Integration Target**: the `mcp-events.jsonl` event surface gains a fourth event-type writer (the FR-4b script) and a new reader (the Q-CS-1b staleness banner in `postCreate.sh`). The event-surface schema home (`KB-mcp-design/references/principles.md`) and the usage docs (`KB-mcp-platform/references/mcp-events-jsonl.md`) are updated by Plan Authoring to document the four-type vocabulary per ADR-0058.
- **Invocation Method**: orchestrator-internal `python3` calls for FR-1; orchestrator-internal logic for FR-2; standard OP-rule invocation per ADR-0042 / Gate-6 per ADR-0043 for FR-3; standard devcontainer post-create flow for FR-4a; manual-by-maintainer OR `workflow_dispatch`-or-cron-or-pull_request via the FR-4c workflow for FR-4b; standard `pull_request` paths-filtered + `schedule:` + `workflow_dispatch` trigger for FR-4c; standard `pull_request` paths-filtered trigger for FR-5.

### Code Inspection Evidence

*(Preserved from Blueprint v1 with one v2 addition.)*

| File/Function | Relevance |
|---|---|
| `.claude/skills/recipe-feature-pipeline/SKILL.md:350` | Current `scope_class` read site (UNCHANGED in v2) |
| `.claude/agents/execute-task-quality-handler.md:33-46` | Verdict + findings shape (UNCHANGED in v2) |
| `.claude/agents/review-architecture-auditor.md:135-137` | Canonical severity → verdict mapping (UNCHANGED in v2) |
| `adrs/ADR-0041-install-mechanism-hybrid.md:68-71` | Invocation taxonomy table; **row 71 (mcp-openapi-schema) AND row 70 (Serena)** annotated `[DEPRECATED]` (v2.1: row 70 added per Architecture Audit cycle 1 finding I-AA-003 — same shape of drift as row 71) |
| **`.devcontainer/postCreate.sh:197-198`** | **REVISED v2 anchor: FR-4a inserts as a discrete top-level block BETWEEN line 197 (`install_terraform_mcp || ...`) and line 198 (`install_gitnexus || ...`). The existing `gitnexus_post_install_warm` at line 201 does NOT collide. v1's line-142-143 anchor is RETIRED.** |
| `.devcontainer/postCreate.sh:5,9,158` | The "5 vs 4" head-comment inconsistency surfaced as Q-CS-3 (UNCHANGED in v2) |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md:56,141` | Rows B-1 and H-4 already carry the adoption parenthetical (UNCHANGED in v2) |
| `CLAUDE.md:9` | Existing project posture about `mcp-openapi-schema` (UNCHANGED in v2) |
| **`adrs/ADR-0037-mcp-events-jsonl-transition-surfacing.md` §Decision item 2 + §Architecture Impact item 4** | **NEW v2 reference (PROSE-CORRECTED in v2.1): ADR-0037's closed-enum discipline at three values (`install_complete`, `readiness_probe`, `structured_failure` per the on-disk vocabulary, as corrected in ADR-0037 v1.0.2) is the contract ADR-0058 additively extends to four. The OP-7 audit rule discipline (schema validation; `audit_op7_events_schema.py`) is preserved. OP-6 audits credential redaction in the runtime log — a distinct concern unchanged by either ADR.** |

### Fact Disposition Table

*(Preserved verbatim from Blueprint v1 — no codebase facts shifted by the FR-4 reshape; the reshape changes placement and adds new artifacts but does not perturb any existing fact's disposition. See blueprint-v1.md §Fact Disposition Table for the canonical roster of 35 facts C-COMP-01..C-OQ-05.)*

The Fact Disposition Table from Blueprint v1 covers every `focusArea` in `codebase-analysis.json` with disposition (preserve / transform / remove / out-of-scope) and rationale. v2 does not alter any disposition. The only fact-level addition surfaced by the reshape is:

- **C-NEW-01 (v2 addition)**: The FR-4a per-rebuild insertion site shifts from `.devcontainer/postCreate.sh:142-143` (inside `install_gitnexus()`) to `.devcontainer/postCreate.sh:197-198` (top-level, between `install_terraform_mcp` and `install_gitnexus`). Disposition: **transform** — anchor revised per codespaces-design v0.3.0 §Insertion site. The line numbers are anchors per the live `.devcontainer/postCreate.sh` at 2026-05-26; Plan Authoring treats them as anchors rather than absolutes.

## Design

### Change Impact Map

```yaml
Change Target: Pipeline quick-wins hardening — verdict-parity validator, dispatch self-check, .mcp.json↔ADR-0041 parity audit, GitNexus per-rebuild static-shape check + opt-in behavioral calibration + CI wiring, MCP connectivity CI smoke, deferral-register tightening
Direct Impact:
  frontend: N/A — out of scope
  backend: N/A — out of scope
  api: N/A — out of scope
  query: N/A — out of scope
  database: N/A — out of scope
  cicd:
    - .github/workflows/mcp-connectivity-smoke.yml (NEW — FR-5; unchanged from v1)
    - .github/workflows/gitnexus-grammar-skip-calibration.yml (NEW in v2 — FR-4c; weekly cron + on-change + workflow_dispatch)
  iac: N/A — out of scope
  codespaces:
    - .devcontainer/postCreate.sh (MODIFIED — REVISED v2: FR-4a top-level static-shape block between current lines 197 and 198; Q-CS-1b staleness banner block adjacent to FR-4a; cosmetic "5→4 servers" fix in line 5 per Q-CS-3 disposition)
    - .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh (NEW in v2 — FR-4b opt-in behavioral calibration script with full AC-CS-4b-1..7 contract)
  claude_code:
    - .claude/skills/recipe-feature-pipeline/SKILL.md (MODIFIED — FR-1 wire-in at 9 invocation sites; FR-2 self-check at orchestrator entry; scope_class hoist from line 350; checkpoint.execution_mode schema documentation per ADR-0057)
    - .claude/skills/auditing-shared/scripts/verdict_findings_parity.py (NEW)
    - .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py (NEW)
    - .claude/skills/auditing-mcp/SKILL.md (MODIFIED — routing-table entry for OP-11)
    - .claude/skills/auditing-mcp/references/adr-parity.md (NEW)
    - adrs/ADR-0041-install-mechanism-hybrid.md (ANNOTATED — [DEPRECATED INVOCATION FORM] on row 71 (mcp-openapi-schema) AND row 70 (Serena, v2.1 addition per Architecture Audit cycle 1 finding I-AA-003); decision-text preserved verbatim)
    - adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md (NEW — authored Blueprint v1; preserved in v2)
    - adrs/ADR-0058-calibration-result-event-type-additive-extension.md (NEW in v2 — authored this Blueprint pass)
    - .claude/skills/KB-mcp-design/references/principles.md (MODIFIED in v2 by Plan Authoring — documents four-type vocabulary per ADR-0058)
    - .claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md (MODIFIED in v2 by Plan Authoring — adds calibration_result example + mechanism: discriminator)
    - Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md (VERIFIED-AND-TIGHTENED — FR-7)
    - CLAUDE.md (MODIFIED — single-character counter update OP-1..OP-10 → OP-1..OP-11)
Indirect Impact:
  - checkpoint.json schema gains documented execution_mode field per ADR-0057 (UNCHANGED in v2)
  - .github/workflows/ becomes the convention-setting precedent for TWO workflows (FR-5 + FR-4c) — v2 establishes the two-workflow shape
  - mcp-events.jsonl event-type vocabulary grows from three to four with calibration_result per ADR-0058
  - Cosmetic "5→4 servers" fix in postCreate.sh:5 (per Q-CS-3 disposition; UNCHANGED from v1)
No Ripple Effect:
  - The 7 sub-agents' MCP allowlists (NFR-15)
  - The 5 reviewer-shaped agents' contracts (FR-1 reads; does not modify)
  - .mcp.json contents (read-only consumed by FR-3 and FR-5)
  - ADR-0041's decision text (only an inline marker added)
  - The three pre-existing mcp-events.jsonl event types (install_complete, readiness_probe, structured_failure — preserved verbatim by ADR-0058; v2.1 prose corrected from v2.0.0's `primary_degraded` per Architecture Audit cycle 1 finding I-AA-001, in lockstep with ADR-0037 v1.0.2)
  - The 7 servers' install mechanisms (no patching per PRD Product Policy Decisions row 4)
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|---|---|---|---|
| Implicit dispatch posture in orchestrator | `checkpoint.execution_mode` documented field per ADR-0057 (UNCHANGED in v2) | No conversion of existing checkpoints | Absence-equals-`specialist-dispatch` default |
| Reviewer verdict + findings output (5 agents) | Same shape, now gated by `verdict_findings_parity.py` downstream (UNCHANGED) | No | Shape-additive validator (NFR-9 / AC-CC-1-h) |
| `auditing-mcp` OP-1..OP-10 rule contract | OP-11 follows the same contract (UNCHANGED) | No | Inherits Gate-6 hard-gate per ADR-0043 |
| ADR-0041 invocation table (7 rows) | Same 7 rows; **rows 71 (mcp-openapi-schema) AND 70 (Serena)** annotated `[DEPRECATED INVOCATION FORM]` (v2.1: row 70 added per Architecture Audit cycle 1 finding I-AA-003) | No | Inline annotations; ADR-0005 honored |
| **v1: `install_gitnexus()` `npm install -g` redirects stderr to `/dev/null`** | **v2: `install_gitnexus()` is UNCHANGED. The FR-4a static-shape check sits at TOP-LEVEL between current lines 197 and 198, BEFORE `install_gitnexus` is invoked. The function itself is untouched.** | **No (v2 cleanly avoids modifying `install_gitnexus()` at all)** | **Top-level placement honors `set -euo pipefail` for fail-closed posture without function-internal `\|\| emit_degraded_banner` masking** |
| **v1: single placeholder `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`** | **v2: full FR-4b contract — no arguments + reads versions.env + mktemp scratch + Signal 1 + Signal 3 + negative-assertion + emits `calibration_result` event per ADR-0058 + cleanup** | **No (v2 ships the full script; v1's was a placeholder)** | **Script contract fixed by AC-CS-4b-1..7; emits ADR-0058-conformant event payload** |
| `.github/workflows/` (FR-5 only in v1) | **TWO workflows in v2: FR-5 connectivity smoke + FR-4c calibration CI wiring** | No | Greenfield; the two-workflow shape is the convention established in v2 |
| `claude mcp list` per PRD literal | `claude --bare -p "noop" --output-format stream-json \| jq` per design substitution (UNCHANGED) | Reconciled at Blueprint v1; preserved in v2 | AC-FR-5 reconciled to AC-CICD-5 |
| **ADR-0037 event-type vocabulary closed at three values (`install_complete`, `readiness_probe`, `structured_failure` — per ADR-0037 v1.0.2 prose correction)** | **ADR-0058 additively extends to four values with `calibration_result`; the three pre-existing types are preserved verbatim** | No (additive extension; existing consumers ignore unknown types per ADR-0037's forward-compatibility posture) | **ADR-0058 cites and extends ADR-0037; closed-enum discipline preserved at four values; OP-7 audit rule discipline (the schema-validation rule; `audit_op7_events_schema.py`) unchanged; OP-6 (credential redaction) remains a distinct concern.** |

### Architecture Overview

The system under change is the feature-pipeline itself plus the project's devcontainer and CI surfaces. The feature adds five non-overlapping gates and two schema field/event-type extensions to that pipeline, plus two CI workflows.

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
│   scope_class consumed from checkpoint                                          │
│   [FR-7: register row B-1/H-4 verification + tightening]                        │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                       Devcontainer (.devcontainer/postCreate.sh)                │
│                                                                                 │
│  ... install_terraform_mcp (line 197) ...                                       │
│                                                                                 │
│  [FR-4a: STATIC-SHAPE CHECK — TOP-LEVEL, BETWEEN LINES 197 AND 198]              │
│    A1 GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1?                                         │
│    A2 GITNEXUS_TAG matches semver/tag regex?                                     │
│    A3 GITNEXUS_TAG matches versions.env?                                         │
│    A4 npm root -g writable parent?                                               │
│    Pass: silent green-light into install_gitnexus                                │
│    Fail: structured_failure event + plain-text echo + set -euo pipefail halts    │
│                                                                                 │
│  install_gitnexus (line 198) ... (UNCHANGED from v1)                            │
│                                                                                 │
│  [Q-CS-1b: STALENESS BANNER (NEW in v2) — adjacent to FR-4a]                     │
│    Read most recent calibration_result event for fr-4b-gitnexus-grammar-skip    │
│    If event older than 2 weeks OR no event ever: emit degraded banner to stderr │
│    Informational; does NOT fail-close postCreate                                 │
│                                                                                 │
│  ... (rest of postCreate.sh unchanged) ...                                      │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│         Opt-in calibration (.devcontainer/scripts/calibrate-gitnexus-...sh)     │
│                                                                                 │
│  Invoked manually by maintainer OR by FR-4c CI workflow:                        │
│    1. Read GITNEXUS_TAG from versions.env                                       │
│    2. mktemp -d (scratch1); npm config set prefix scratch1/npm-global           │
│    3. GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install -g gitnexus@$TAG 2>stderr   │
│    4. Signal 1: grep stderr for [tree-sitter-(dart|proto)] Skipping...          │
│    5. Signal 3: stat scratch1/npm-global/.../tree_sitter_{dart,proto}_*.node    │
│    6. Optional negative-assertion: mktemp -d (scratch2); GRAMMARS=0 install;    │
│       assert artifacts ARE built                                                 │
│    7. log_mcp_event "calibration_result" {outcome, signals, ...} (per ADR-0058) │
│    8. Cleanup scratch1 + scratch2 via trap EXIT                                 │
│    9. Exit 0 on pass; non-zero on any signal failure                            │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│           GitHub Actions (.github/workflows/) — TWO workflows                   │
│                                                                                 │
│  FR-5: .github/workflows/mcp-connectivity-smoke.yml                             │
│    on: pull_request paths=[.mcp.json, .devcontainer/**, adrs/ADR-0041-*.md,     │
│                              .claude/skills/auditing-mcp/**] + workflow_dispatch │
│    runs-on: ubuntu-latest; timeout-minutes: 8; permissions: contents: read      │
│    actions/checkout + devcontainers/ci (both SHA-pinned)                        │
│    claude --bare -p "noop" --output-format stream-json | jq                     │
│    Empty bad-set: PASS; non-empty: FAIL with FR-6 diagnostic                    │
│                                                                                 │
│  FR-4c (NEW v2): .github/workflows/gitnexus-grammar-skip-calibration.yml        │
│    on: schedule: '0 7 * * 1' + pull_request paths=['.devcontainer/versions.env',│
│                  '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh'] +   │
│        workflow_dispatch                                                         │
│    runs-on: ubuntu-latest; timeout-minutes: 5; permissions: contents: read      │
│    concurrency: gitnexus-calibration; cancel-in-progress: false                  │
│    actions/checkout + devcontainers/ci (same SHAs as FR-5)                      │
│    Invokes .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh             │
│    Script exit code is the contract; CI surfaces FR-6 in $GITHUB_STEP_SUMMARY   │
│    Script writes calibration_result event per ADR-0058 (CI does NOT duplicate)  │
└────────────────────────────────────────────────────────────────────────────────┘
```

The four layer-specific surfaces are loosely coupled: the orchestrator's FR-1/FR-2/FR-3 don't depend on the devcontainer's FR-4 family to ship; the FR-5 CI workflow runs against the devcontainer image FR-4a modifies but only inherits it; the FR-4c CI workflow invokes the FR-4b script but is independent of FR-4a's per-rebuild path. All five mechanisms can ship in isolation per NFR-11; within the FR-4 family, FR-4a, FR-4b, and FR-4c are also independently exercisable per AC-X-1.

### Data Flow

*(Augmented from Blueprint v1 with v2 FR-4 family + Q-CS-1b banner.)*

```
[FR-1 / FR-2 / FR-3 / FR-5 / FR-7 data flows — preserved verbatim from Blueprint v1.]

Devcontainer rebuild (every kind — cache-hit, cache-miss, fresh codespace):
  postCreate.sh top-level flow:
    ...
    install_terraform_mcp || emit_degraded_banner ... (line 197)
        │
        ▼
[FR-4a static-shape check — top-level block between lines 197 and 198]
    A1 grep for $GITNEXUS_SKIP_OPTIONAL_GRAMMARS == "1"
    A2 regex-match $GITNEXUS_TAG against semver/tag form
    A3 compare $GITNEXUS_TAG to versions.env value
    A4 check npm root -g returns non-empty, parent writable
        │
        ├─ all pass ──► silent green-light (no event, no banner)
        └─ any fail ──► log_mcp_event "structured_failure" {note: FR-4a + signal + ...}
                        echo plain-text diagnostic to stderr
                        set -euo pipefail halts postCreate.sh (fail-closed; NFR-6)

[Q-CS-1b staleness banner — adjacent to FR-4a block; runs only on the FR-4a pass path (after FR-4a's green-light, before install_gitnexus). On the FR-4a fail path, set -euo pipefail halts postCreate.sh and the banner never runs — which is correct since the banner is informational and a fail-closed rebuild has more urgent signal already.]
    last_cal = jq 'select(.event=="calibration_result" and .mechanism=="fr-4b-gitnexus-grammar-skip") | .timestamp' < mcp-events.jsonl | tail -1
        │
        ├─ no event found ──► echo "[postCreate] FR-4b calibration: NEVER RUN. Suggest: gh workflow run gitnexus-grammar-skip-calibration.yml" >&2
        ├─ event < 2 weeks old ──► silent (no banner)
        └─ event ≥ 2 weeks old ──► echo "[postCreate] FR-4b calibration: STALE (last run <timestamp>, >2w ago). Suggest: gh workflow run gitnexus-grammar-skip-calibration.yml" >&2

    install_gitnexus || emit_degraded_banner ... (line 198)
    ...


Manual or CI invocation of .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh:
  read GITNEXUS_TAG from versions.env
  scratch1=$(mktemp -d); export NPM_CONFIG_PREFIX="${scratch1}/npm-global"
  trap 'rm -rf "${scratch1}" "${scratch2:-}"' EXIT
  GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install -g "gitnexus@${TAG}" 2> "${scratch1}/stderr.log"
      │
      ▼
  Signal 1: grep -E '\[tree-sitter-(dart|proto)\] Skipping build' "${scratch1}/stderr.log"
            (at least one match for each of dart and proto)
  Signal 3: stat "${scratch1}/npm-global/lib/node_modules/gitnexus/node_modules/tree-sitter-{dart,proto}/build/Release/*.node"
            (artifacts MUST be absent)
      │
      ▼
  scratch2=$(mktemp -d); export NPM_CONFIG_PREFIX="${scratch2}/npm-global"
  GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0 npm install -g "gitnexus@${TAG}"
  Negative-assertion: stat ${scratch2}/.../tree_sitter_{dart,proto}_*.node
                      (artifacts MUST be present)
      │
      ▼
  Compute outcome: {pass | fail | drift_detected}
  log_mcp_event "calibration_result" {server: "gitnexus", mechanism: "fr-4b-gitnexus-grammar-skip", version: "${TAG}", outcome, signals: {...}, note: "..."}
      │
      ├─ pass ──► exit 0
      └─ fail / drift_detected ──► exit non-zero (FR-4c CI surfaces in $GITHUB_STEP_SUMMARY)


FR-4c workflow triggered (cron Monday 07:00 UTC OR pull_request to versions.env/script OR workflow_dispatch):
  actions/checkout@<SHA>
      │
      ▼
  devcontainers/ci@<SHA> { runCmd: ".devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh" }
      │
      ├─ script exit 0 ──► $GITHUB_STEP_SUMMARY PASS block (FR-6 fields populated)
      └─ script exit non-zero ──► $GITHUB_STEP_SUMMARY FAIL block (FR-6 fields populated; surfaces script stdout for the offending grammar + Signal-N)
```

### Integration Points List

*(Augmented from Blueprint v1.)*

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|---|---|---|---|---|---|
| Reviewer-output → orchestrator advance | `recipe-feature-pipeline/SKILL.md` | Unchecked passthrough | Validator-gated advance (FR-1) (UNCHANGED) | Inline orchestrator step | Fixture invocation |
| Orchestrator entry | `recipe-feature-pipeline/SKILL.md` | No dispatch self-check | Dispatch self-check after Stage 1 (FR-2) (UNCHANGED) | Inline orchestrator step | Pipeline smoke |
| `auditing-mcp` Gate-6 dispatch | `auditing-mcp/scripts/audit_mcp.py` | OP-1..OP-10 only | OP-1..OP-11 (FR-3 OP-11 added) (UNCHANGED) | Coordinator includes new script | Fixture invocation |
| **`postCreate.sh` top-level flow between lines 197 and 198** | **`.devcontainer/postCreate.sh:197-198`** | **No check between install_terraform_mcp and install_gitnexus** | **FR-4a static-shape check + Q-CS-1b staleness banner** | **Inline top-level block; `set -euo pipefail` enforces fail-closed for FR-4a; banner is informational** | **Cache-hit/cache-miss devcontainer rebuilds; fixture-broken static-shape rebuilds; fixture-stale `mcp-events.jsonl` rebuild** |
| **Maintainer or CI invocation of `calibrate-gitnexus-grammar-skip.sh`** | **`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`** | **N/A — script did not exist (v1 named the path as placeholder)** | **Full FR-4b contract per AC-CS-4b-1..7; emits `calibration_result` event per ADR-0058** | **Standalone bash script; trap-based scratch cleanup** | **Real-tag calibration; drift-fixture calibration; broken-contract calibration** |
| PR check (FR-5) | `.github/workflows/mcp-connectivity-smoke.yml` (UNCHANGED) | No workflow | `mcp-connectivity-smoke.yml` | GitHub Actions `pull_request` trigger | Pre-merge validation per D-0010 |
| **Calibration CI cadence (FR-4c)** | **`.github/workflows/gitnexus-grammar-skip-calibration.yml`** | **N/A — no calibration CI** | **Weekly cron + on-change + workflow_dispatch; invokes the script; surfaces exit code via `$GITHUB_STEP_SUMMARY`** | **GitHub Actions `schedule:` + `pull_request paths:` + `workflow_dispatch:`** | **`workflow_dispatch` runs against draft branch; fixture pin-bump PR opens to confirm trigger fires** |
| ADR-0041 ↔ `.mcp.json` parity surface | `adrs/ADR-0041-*.md` rows 71 + 70 + `.mcp.json` (v2.1: row 70 (Serena) added per Architecture Audit cycle 1 finding I-AA-003) | Implicit | OP-11 + `[DEPRECATED INVOCATION FORM]` annotation on both rows | Inline annotations + OP-11 rule | Fixture test |
| `checkpoint.json` schema | orchestrator-internal (UNCHANGED) | Implicit | First-class `execution_mode` per ADR-0057 | Orchestrator writes; absence-as-default | Resume pre-feature checkpoint |
| **`mcp-events.jsonl` event-type vocabulary** | **`.claude/runtime/mcp-events.jsonl` + schema home + usage docs** | **Three types: install_complete, readiness_probe, structured_failure (per ADR-0037 v1.0.2 prose correction)** | **Four types: above three + calibration_result per ADR-0058** | **Additive extension; existing consumers ignore unknown types per ADR-0037 forward-compatibility** | **FR-4b script writes one event per invocation; Q-CS-1b banner reads most recent event; OP-7 audit rule discipline preserved (closed-enum schema validation, four values; `audit_op7_events_schema.py`). OP-6 (credential redaction) is a distinct rule unchanged by this extension.** |

### Main Components

*(Preserved from Blueprint v1 with v2 additions.)*

#### `verdict_findings_parity.py` (FR-1) — UNCHANGED in v2

See Blueprint v1 §Main Components.

#### Orchestrator dispatch self-check (FR-2) — UNCHANGED in v2

See Blueprint v1 §Main Components.

#### `audit_op11_adr_parity.py` (FR-3) — UNCHANGED in v2

See Blueprint v1 §Main Components.

#### FR-4a static-shape check (NEW component shape in v2)

- **Responsibility**: At the top-level of `postCreate.sh` between current lines 197 and 198, assert A1 + A2 + A3 + A4 (env-var, tag pin, versions.env source, npm root predictability) in under 100 ms with no network. On fail, emit `structured_failure` event + plain-text echo + halt via `set -euo pipefail`. On pass, silent green-light.
- **Interface**: Inline shell block at top-level of `postCreate.sh`. Inputs: environment variables (`$GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, `$GITNEXUS_TAG`) + `.devcontainer/versions.env` file + `npm root -g` output. Outputs: pass (silent) or `structured_failure` event to `mcp-events.jsonl` + stderr echo + non-zero exit.
- **Dependencies**: `log_mcp_event` helper; `grep`; `stat`; `test`; `npm root -g`.

#### Q-CS-1b staleness banner (NEW in v2)

- **Responsibility**: Adjacent to FR-4a's block in `postCreate.sh`. Reads the most recent `calibration_result` event for `mechanism: "fr-4b-gitnexus-grammar-skip"` from `mcp-events.jsonl`; emits a plain-text degraded banner to stderr if the event is older than 2 weeks OR if no such event has ever been recorded. Informational; does NOT cause fail-close.
- **Interface**: Inline shell block at top-level of `postCreate.sh`, adjacent to FR-4a's block. Inputs: `.claude/runtime/mcp-events.jsonl` (read-only via `jq`). Outputs: stderr banner (one line) or silence.
- **Dependencies**: `jq`; `date`; `[[ ]]` comparison.

#### `calibrate-gitnexus-grammar-skip.sh` (FR-4b — NEW component shape in v2)

- **Responsibility**: Standalone script. When invoked (no arguments), performs the full behavioral calibration of the GitNexus grammar-skip contract: read `GITNEXUS_TAG`, create scratch dir, install with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`, assert Signal 1 + Signal 3, run optional negative-assertion confirmation, emit exactly one `calibration_result` event per ADR-0058, cleanup. Exit 0 on pass; non-zero on any signal failure.
- **Interface**: Bash script. No arguments. Inputs: `.devcontainer/versions.env` (read). Outputs: one event to `.claude/runtime/mcp-events.jsonl`; exit code; stdout/stderr that names the failing grammar + Signal-N on fail.
- **Dependencies**: `npm`, `bash`, `mktemp`, `grep`, `stat`, `log_mcp_event` helper. Network: needs to reach the npm registry for the gitnexus tarball.

#### `mcp-connectivity-smoke.yml` (FR-5) — UNCHANGED in v2

See Blueprint v1 §Main Components.

#### `gitnexus-grammar-skip-calibration.yml` (FR-4c — NEW in v2)

- **Responsibility**: GitHub Actions workflow. Triggers on `schedule: '0 7 * * 1'` (Monday 07:00 UTC) + `pull_request.paths: ['.devcontainer/versions.env', '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh']` + `workflow_dispatch`. Builds the devcontainer image via `devcontainers/ci@<SHA>`; invokes the FR-4b script inside it; surfaces script exit code as job status + FR-6 diagnostic to `$GITHUB_STEP_SUMMARY`.
- **Interface**: GitHub Actions workflow file. Runner: `ubuntu-latest`. Timeout: 5 minutes. Permissions: `contents: read`. Concurrency: `{group: gitnexus-calibration, cancel-in-progress: false}`.
- **Dependencies**: `actions/checkout@<SHA>` (first-party); `devcontainers/ci@<SHA>` (third-party, SHA-pinned — same SHAs as FR-5); the FR-4b script inside the built image; `jq` inside the devcontainer image (for the per-event surfaces, though the workflow itself does not re-emit events — the script does).

### Data Representation Decision (ADR-0058)

| Criterion | Assessment | Reason |
|---|---|---|
| Semantic Fit | Yes | `calibration_result` is a per-run record of a behavioral calibration outcome; semantically aligned with the existing event types (each one names a discrete operational moment) |
| Responsibility Fit | Yes | The FR-4b script owns the calibration; the script is the natural writer; the event surface ADR-0037 establishes is the natural home |
| Lifecycle Fit | Yes | Written once per invocation (manual or CI); consumed by downstream readers on demand (CI summary, staleness banner, future analytics) |
| Boundary/Interop Cost | Low | The four-type vocabulary is bounded; the `mechanism:` field is the namespace discriminator for future calibrations; OP-7 audit rule discipline (schema validation; `audit_op7_events_schema.py`) is preserved. OP-6 (credential redaction) is a distinct rule unaffected. |

**Decision**: `new` additive value `calibration_result` on the existing event-type vocabulary established by ADR-0037 — not a new schema, an additive extension. ADR-0058 documents the change.

### Contract Definitions

The key contracts in this Blueprint:

- **`verdict_findings_parity.py` CLI contract** — UNCHANGED from Blueprint v1.
- **`audit_op11_adr_parity.py` CLI contract** — UNCHANGED from Blueprint v1.
- **`checkpoint.execution_mode` field contract** — per ADR-0057; UNCHANGED in v2.
- **Anthropic Agent SDK `system/init` event contract** — UNCHANGED from Blueprint v1.
- **`calibrate-gitnexus-grammar-skip.sh` script contract (NEW in v2)** — per AC-CS-4b-1..7; canonical script invocation `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (no arguments). Exit 0 on pass; non-zero on any signal failure. Emits exactly one `calibration_result` event per invocation per ADR-0058.
- **`calibration_result` event contract (NEW in v2 per ADR-0058)** — canonical payload `{event: "calibration_result", timestamp, server, mechanism, version, duration_ms, outcome ∈ {pass, fail, drift_detected}, signals: <per-mechanism map>, note}`. The `mechanism:` field is the namespace discriminator (for this feature: `"fr-4b-gitnexus-grammar-skip"`).
- **FR-4a static-shape diagnostic contract (NEW in v2)** — `structured_failure` event with `note:` field encoding the four FR-6 elements (mechanism = "FR-4a"; offending artifact; failing signal token from the fixed set `signal-a1-env-var-unset-or-wrong` / `signal-a2-tag-pin-malformed` / `signal-a3-versions-env-mismatch` / `signal-a4-artifact-paths-unpredictable`; remedial hint).

### Field Propagation Map

| Field | Boundary | Status | Detail |
|---|---|---|---|
| `verdict` (reviewer output) | Reviewer agent → orchestrator → FR-1 validator | preserved | UNCHANGED from v1 |
| `findings[].severity` (reviewer output) | Reviewer agent → orchestrator → FR-1 validator | preserved | UNCHANGED from v1 |
| `scope_class` (intent-clarification frontmatter) | Stage 1 → orchestrator → FR-2 predicate | preserved (hoist) | UNCHANGED from v1 |
| `checkpoint.execution_mode` (per ADR-0057) | Orchestrator dispatch → checkpoint write → FR-2 read | introduced v1; preserved v2 | UNCHANGED |
| `system/init.mcp_servers[].status` | Claude Code CLI → stream-json → FR-5 jq filter | preserved | UNCHANGED from v1 |
| `GITNEXUS_TAG` (versions.env) | versions.env → postCreate.sh → FR-4a + FR-4b | preserved | Read by FR-4a's A2/A3; read by FR-4b script |
| **`calibration_result` event (per ADR-0058)** | **FR-4b script → mcp-events.jsonl → FR-4c CI summary + Q-CS-1b staleness banner + future analytics** | **introduced (additive extension)** | **Writer: FR-4b script only. Readers: FR-4c CI workflow summary, Q-CS-1b banner, existing consumers (ignore-unknown). Closed-enum vocabulary preserved at four values.** |
| **`mechanism:` field within `calibration_result`** | **FR-4b script writes `"fr-4b-gitnexus-grammar-skip"`** | **introduced** | **Namespace discriminator for future calibration mechanisms reusing the type.** |

### State Transitions and Invariants

```yaml
checkpoint.execution_mode per-stage state machine: UNCHANGED from Blueprint v1.

calibration_result event sequence (NEW in v2):
  Pre-feature state: no calibration_result events in mcp-events.jsonl
  Each invocation of .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh:
    appends exactly one calibration_result event with outcome ∈ {pass, fail, drift_detected}
  Q-CS-1b staleness banner read:
    finds most recent calibration_result event for mechanism="fr-4b-gitnexus-grammar-skip"
    if absent: banner says "NEVER RUN"
    if present and timestamp >= now - 2 weeks: silent
    if present and timestamp < now - 2 weeks: banner says "STALE (last run <timestamp>)"

System Invariants (v2 additions):
  - Only the FR-4b script writes calibration_result events (single writer)
  - The four-type event vocabulary is closed: {install_complete, readiness_probe, structured_failure, calibration_result} (corrected in v2.1 from v2.0.0's primary_degraded enumeration per the on-disk vocabulary; the OP-7 schema-validation rule admits exactly these four values).
  - Existing consumers that ignore unknown types continue to work
  - The Q-CS-1b banner is informational; never causes fail-close
  - FR-4c CI workflow consumes exit code only; does not duplicate event emission
```

---

### Claude Code / Project Filesystem Design

*(UNCHANGED from Blueprint v1. The cc-design.md remains at v0.2.0; FR-1 / FR-2 / FR-3 / FR-7 are untouched by the FR-4 reshape.)*

The full per-layer Claude Code design is `working/feature/pipeline-quickwins-hardening-r1/cc-design.md` v0.2.0, integrated below by reference. See Blueprint v1 §Claude Code Design for the conventions-touched table, CLAUDE.md updates, slash commands (none), hooks (none), skills (existing modified), sub-agents (none), MCP servers (none).

**v2 addition for this layer's surface**: Plan Authoring updates `KB-mcp-design/references/principles.md` and `KB-mcp-platform/references/mcp-events-jsonl.md` to document the four-type vocabulary per ADR-0058. These are KB doc edits, not skill-logic changes.

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

The full per-layer CI/CD design is `working/feature/pipeline-quickwins-hardening-r1/cicd-design.md` **v0.3.0**, integrated below by reference. The composer-integrated content from cicd-design covers FR-5 (UNCHANGED), the NEW FR-4c calibration CI wiring, and the CI/CD-side of FR-6.

#### Workflow Inventory (v2 — TWO workflows)

| Workflow File | Triggers | Purpose | Concurrency Group |
|---|---|---|---|
| `.github/workflows/mcp-connectivity-smoke.yml` | `pull_request` paths-filtered + `workflow_dispatch` | FR-5: assert every server in `.mcp.json` reports `status: connected` from the Agent SDK `system/init` event after a fresh devcontainer provision. Fail any PR that breaks the invariant. | None (not a deploy; parallel PR runs are safe). |
| **`.github/workflows/gitnexus-grammar-skip-calibration.yml` (NEW in v2)** | **`schedule: '0 7 * * 1'` (Monday 07:00 UTC weekly cron) + `pull_request paths: ['.devcontainer/versions.env', '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh']` + `workflow_dispatch`** | **FR-4c: invoke the Codespaces-owned FR-4b calibration script on a regular cadence and on every pin bump, so the behavioral grammar-skip contract does not silently degrade between manual maintainer invocations. Fail when the script reports drift.** | **`gitnexus-calibration` (constant group, `cancel-in-progress: false`) — prevents duplicate `mcp-events.jsonl` emissions from racing triggers.** |

#### Job Graph

**FR-5** (UNCHANGED from v1):

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

**FR-4c (NEW in v2)**:

```
checkout ──► devcontainers/ci (build devcontainer image, run calibration)
                    │
                    └─► .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh
                                │
                                ├─► (side effect) script writes calibration_result event to mcp-events.jsonl per ADR-0058
                                │
                                └─► script exit code
                                            │
                                            ├─► 0: PASS ($GITHUB_STEP_SUMMARY names mechanism + script path + outcome + event emission)
                                            └─► non-zero: FAIL ($GITHUB_STEP_SUMMARY names mechanism + offending grammar + Signal-N + FR-6 remedial hint + trigger event_name)
```

#### Reusable Actions / Composite Actions

None introduced. The two workflows share `actions/checkout` and `devcontainers/ci` as-published; the same SHA is reused across both workflows per cicd-design v0.3.0 §SHA-pinning (one resolution effort, repeated `uses:` lines).

#### Secrets, Variables & Environments

None. Neither workflow reads secrets, declares an environment, federates to any cloud, or uses OIDC. Cost: zero new credential surface (NFR-7) — verified across BOTH workflows.

#### Permissions

| Workflow / Job | `permissions:` block | Justification |
|---|---|---|
| `mcp-connectivity-smoke.yml` (workflow-level) | `contents: read` | UNCHANGED from v1. |
| `gitnexus-grammar-skip-calibration.yml` (workflow-level) | `contents: read` | Identical posture to FR-5. Reads the PR/branch tree (versions.env, the calibration script, the devcontainer config) and runs the calibration inside the built image. No PR comments, no deploy, no OIDC. |

#### Caching & Artifacts

None. Devcontainer image layer caching is owned by Docker/BuildKit on the runner. If NFR-4 budget is exceeded on either workflow, the canonical mitigation is a Codespaces-side prebuild (Q-CICD-2) — applies symmetrically to both workflows.

#### Environments & Promotion

| Environment | Protection Rules | Required Reviewers | Wait Timer | Deployment Branches |
|---|---|---|---|---|
| (none — neither workflow is a deploy) | — | — | — | — |

#### Failure & Rollback

- **Failed-deploy behavior**: N/A — neither workflow is a deploy.
- **Rollback workflow**: N/A. The PR check failure (FR-5) or the workflow run UI (FR-4c cron) is the notification surface.
- **Notification routing**: GitHub's built-in PR-check status (FR-5) and the Actions tab failed-workflow surface (FR-4c). No Slack/email integration in scope (Q-CICD-6).

---

### Infrastructure as Code Design

N/A — out of scope.

---

### Dev Environment (Codespaces) Design

The full per-layer Codespaces design is `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` **v0.3.0**, integrated below by reference. The composer-integrated content from codespaces-design covers FR-4a + FR-4b (NEW STRUCTURE in v2), the FR-4c handoff to the CI/CD layer, the Q-CS-1b staleness banner admitted in v2, and the Codespaces-side of FR-6.

#### Devcontainer Configuration (v2)

| File | Change | Purpose |
|---|---|---|
| `.devcontainer/devcontainer.json` | unchanged | Inherited; FR-4 family reads no devcontainer.json field |
| `.devcontainer/Dockerfile` | unchanged | Inherited; FR-4 family adds no apt package, no RUN step |
| **`.devcontainer/postCreate.sh`** | **modified — REVISED v2** | **FR-4a top-level static-shape block between current lines 197 and 198; Q-CS-1b staleness banner adjacent to FR-4a; cosmetic "5→4 servers" fix in line 5 per Q-CS-3** |
| `.devcontainer/versions.env` | unchanged | Read by FR-4a (A2/A3) and FR-4b script |
| **`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`** | **new — REVISED v2 to ship full contract** | **FR-4b opt-in behavioral calibration script per AC-CS-4b-1..7** |

#### Base Image & Features

- **Base image**: inherited (custom Dockerfile). UNCHANGED from v1.
- **Features added by FR-4**: none. UNCHANGED from v1.
- **Rationale for image choice**: inherited from prior feature. UNCHANGED.

#### Lifecycle Scripts (v2 placement)

| Hook | Script | Purpose | Idempotent |
|---|---|---|---|
| `onCreateCommand` | inherited (tool-presence sanity check) | content-independent check | Yes |
| `postCreateCommand` | `postCreate.sh` (MODIFIED — FR-4a top-level block between lines 197/198; Q-CS-1b banner adjacent; cosmetic fix line 5) | MCP server installs + FR-4a static-shape check + Q-CS-1b staleness banner | Yes (FR-4a's fail-closed fail prevents the cache-miss install from running with broken inputs; banner is informational) |
| `postStartCommand` | inherited | per-session warming | Yes |
| `postAttachCommand` | inherited | terminal attach | Yes |

**Out-of-band of any lifecycle hook**: `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (FR-4b). Per AC-CS-4b-3, the script is NEVER invoked from `postCreate.sh` — only by maintainer manually or by the FR-4c CI workflow.

#### Forwarded Ports & Services

None — inherited empty `forwardPorts: []`. UNCHANGED.

#### Prebuilds

None — inherited (no prebuilds). Q-CS-4 disposition unchanged from v1: composer has no visibility into a pending org-level prebuild policy; the no-prebuild posture is forward-compatible if one lands. FR-4a (at `postCreateCommand`, uncaptured) and FR-4b (out-of-band of lifecycle) sit where prebuilds don't see them.

#### VS Code Configuration

Inherited; the FR-4 family adds no extensions, no workspace settings.

#### Parity with CI & Production

The devcontainer image is the FR-5 CI execution environment per synthesis D-0007. **In v2 it is ALSO the FR-4c CI execution environment** — both workflows build via `devcontainers/ci@<SHA>` and inherit the same image including FR-4a's modifications.

#### Secrets in Codespaces

Inherited; FR-4a and FR-4b introduce no new secret (NFR-7 / AC-CS-NFR-7-a per codespaces-design v0.3.0). FR-4b reads only `GITNEXUS_TAG` (non-secret) and `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (non-secret).

---

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---|---|---|---|---|
| Validation (FR-1 parity violation) | Reviewer emits `APPROVED` + severity:BLOCKER finding | `verdict_findings_parity.py` exit 1 | Halt orchestrator; surface FR-6 diagnostic | Pipeline run blocks (UNCHANGED from v1) |
| Validation (FR-2 refusal) | FULL-scope feature with stage configured `parent-driven-workaround` | Orchestrator dispatch self-check | Refuse dispatch loop | Pipeline run blocks before any stage runs (UNCHANGED) |
| Validation (FR-3 BLOCKER finding) | `.mcp.json` server diverges from ADR-0041 non-deprecated row | `audit_op11_adr_parity.py` exit 1 | Halt-and-surface per Gate-6 | Pipeline blocks at Gate 6 (UNCHANGED) |
| **Infrastructure (FR-4a static-shape failure)** | **Env-var unset, tag malformed, versions.env mismatch, or npm root unwritable** | **FR-4a A1/A2/A3/A4 assertion fail** | **`structured_failure` event + plain-text stderr echo + `set -euo pipefail` halts postCreate.sh BEFORE install_gitnexus runs** | **Devcontainer build fails-closed; maintainer fixes the static-shape issue (re-export, re-pin, fix versions.env, fix npm root) before re-rebuild** |
| **Infrastructure (FR-4b behavioral drift)** | **Pinned `GITNEXUS_TAG` no longer honors `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` upstream** | **FR-4b Signal 1 stderr regex fail OR Signal 3 artifact-presence fail OR negative-assertion fail** | **Script writes `calibration_result` event with `outcome: drift_detected` or `fail`; exits non-zero; FR-4c CI surfaces FR-6 diagnostic in `$GITHUB_STEP_SUMMARY`** | **PR bumping `versions.env` cannot merge until the new pin's behavioral contract is investigated; weekly cron alerts maintainer to gradual drift** |
| **Operational (FR-4b calibration stale or never run)** | **No `calibration_result` event in last 2 weeks** | **Q-CS-1b staleness banner reads mcp-events.jsonl on every postCreate.sh** | **Plain-text banner to stderr; informational, does NOT fail-close** | **Maintainer sees banner; suggested action is `gh workflow run gitnexus-grammar-skip-calibration.yml` or manual script invocation** |
| Infrastructure (FR-5 server non-connected) | Server reports `status != "connected"` | jq filter returns non-empty | Workflow exits 1; FR-6 diagnostic (UNCHANGED) | PR cannot merge |
| Infrastructure (FR-5 CLI failure) | `claude --bare -p` itself fails | Exit code in shell step | Workflow exits 2 (UNCHANGED) | PR check fails; INTERNAL-ERROR diagnostic |
| Pipeline internal error (any FR) | Script crash, file missing, parse failure | Exit 2 | Fail-closed per NFR-6 | User-readable diagnostic; halt |

### Logging and Monitoring

- **Log events** (the FR-6 actionable-diagnostic stream + the `mcp-events.jsonl` event surface are the project's primary observability surfaces for these mechanisms):
  - FR-1 validator: JSON stdout per invocation (UNCHANGED)
  - FR-2 dispatch self-check: JSON stdout once per orchestrator entry (UNCHANGED)
  - FR-3 OP-11: JSON stdout per invocation (UNCHANGED)
  - **FR-4a (REVISED v2)**: on pass — silent (no event written). On fail — `structured_failure` event to `mcp-events.jsonl` with `note:` field carrying the four FR-6 elements; plain-text echo to stderr.
  - **FR-4b (NEW v2)**: ALWAYS — one `calibration_result` event per invocation (per ADR-0058) regardless of pass/fail/drift_detected; the event's `outcome:` field carries the verdict; the `signals:` map carries per-Signal pass/fail; the `note:` field carries the FR-6 remedial hint on non-pass outcomes.
  - **FR-4c (NEW v2)**: workflow-step stdout (visible in GitHub Actions run UI); Markdown to `$GITHUB_STEP_SUMMARY` honoring FR-6 four-field discipline; the workflow does NOT write `mcp-events.jsonl` (the script is the authoritative writer per AC-CICD-4c-10).
  - **Q-CS-1b staleness banner (NEW v2)**: plain-text echo to stderr; never writes to `mcp-events.jsonl` (banners are an ephemeral observability surface per existing convention).
  - FR-5: workflow-step stdout + `$GITHUB_STEP_SUMMARY` Markdown (UNCHANGED).
- **Log levels**: structured-JSON-stdout pattern + structured-JSONL events; plain-text echoes from FR-4a banner and Q-CS-1b banner are informational/error per the existing `postCreate.sh` convention.
- **Sensitive data**: per NFR-8 — UNCHANGED from v1. Env-var **names** are emitted (`GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, `GITNEXUS_TAG`); values are not. AC-CS-NFR-8-a verifies both FR-4a and FR-4b honor this discipline.
- **Metrics / Traces / Alerts / Dashboards**: UNCHANGED from v1. The diagnostic streams + the event surface are the observability surface.

## Implementation Plan

### Implementation Approach

**Selected Approach**: Single bundled PR delivering all seven FRs (FR-1, FR-2, FR-3, FR-4a, FR-4b, FR-4c counted within the FR-4 family, FR-5, FR-6, FR-7), ADR-0057 (carried forward from v1), and **ADR-0058 (NEW in v2)**, with per-mechanism isolation preserved by NFR-11.

**Selection Reason**: Unchanged from Blueprint v1 (Q-CC-4 / Q-CS-5 disposition: single bundled PR). The v2 reshape adds one more script file (FR-4b) and one more workflow file (FR-4c) to the bundle but does not alter the cross-mechanism coupling story: FR-4a / FR-4b / FR-4c are tightly coupled at the implementation surface (the script is invoked by the workflow and the banner reads the events the script writes), so they belong in the same PR; the broader FR-1 / FR-2 / FR-3 / FR-5 / FR-7 bundle already encloses them per the v1 rationale.

### Technical Dependencies and Implementation Order

This carve-out is largely parallelizable; the order below is the natural sequence for a single-author bundled PR.

#### Required Implementation Order

1. **ADR-0057 (carried forward from Blueprint v1)** — UNCHANGED.

2. **ADR-0058 (authored in this Blueprint v2 pass)** — NEW.
   - Layer: Claude Code (ADR canonical placement).
   - Technical Reason: FR-4b's design depends on `calibration_result` being a documented additive extension to ADR-0037's event-type vocabulary. ADR-0058 is the canonical home of that documentation.
   - Dependent Elements: FR-4b script (writes the event); FR-4c CI workflow (consumes the script's exit code only; does not parse the event but cites the ADR in its `$GITHUB_STEP_SUMMARY`); Q-CS-1b staleness banner (reads the event); KB-mcp-design + KB-mcp-platform doc updates by Plan Authoring.

3. **`verdict_findings_parity.py` (FR-1)** — UNCHANGED from Blueprint v1 implementation order.

4. **`audit_op11_adr_parity.py` + `references/adr-parity.md` + ADR-0041 annotation (FR-3)** — UNCHANGED.

5. **`recipe-feature-pipeline/SKILL.md` modifications** (FR-1 wire-in + FR-2 self-check + scope_class hoist + ADR-0057 schema documentation) — UNCHANGED.

6. **FR-4a top-level block in `postCreate.sh` (REVISED v2) + Q-CS-1b staleness banner + FR-4b calibration script**
   - Layer: Codespaces.
   - Technical Reason: All three sit together in or alongside `postCreate.sh`. The FR-4a block goes between current lines 197 and 198 (top-level, not inside `install_gitnexus()`); the Q-CS-1b banner sits adjacent to FR-4a; the FR-4b script is a new file at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` with the full AC-CS-4b-1..7 contract. The Q-CS-3 cosmetic "5→4 servers" fix in `postCreate.sh:5` lands in the same commit per v1 disposition.
   - Dependent Elements: every future devcontainer cache-miss / cache-hit build (FR-4a + banner run on every rebuild); maintainer invocation OR FR-4c CI workflow (invokes the script).
   - **Plan task contract**: the calibration script must (a) exit non-zero on drift, (b) write its `mcp-events.jsonl` event before exiting, (c) name the offending grammar in its stdout in a way the FR-4c workflow's `$GITHUB_STEP_SUMMARY` can surface, per cicd-design v0.3.0 §Trap-avoidance observability.

7. **FR-4c workflow `.github/workflows/gitnexus-grammar-skip-calibration.yml` (NEW in v2)**
   - Layer: CI/CD.
   - Technical Reason: Depends on the FR-4b script existing (step 6). The workflow invokes the script and treats its exit code as the contract.
   - Dependent Elements: every Monday 07:00 UTC cron tick; every PR touching `.devcontainer/versions.env` or the calibration script.
   - **Plan tasks**: SHA-pin resolution for `actions/checkout` and `devcontainers/ci` (same SHAs as FR-5 per cicd-design v0.3.0 §SHA-pinning — one resolution effort); `actionlint` pre-commit pass per cicd-design v0.3.0 §Plan task — actionlint deferral (both workflows lint atomically); verify cron expression parses correctly on first run via `workflow_dispatch` against the draft branch.

8. **FR-5 workflow `.github/workflows/mcp-connectivity-smoke.yml`** — UNCHANGED from v1 implementation order.
   - **Plan task addendum (v2)**: when SHA-pinning `actions/checkout` and `devcontainers/ci`, use the same resolved SHAs in BOTH workflows per cicd-design v0.3.0 §SHA-pinning. When running `actionlint`, BOTH workflow files must pass before either is committed — a half-committed `.github/workflows/` directory is not a valid intermediate state.

9. **FR-7 deferral-register verify-and-tighten** — UNCHANGED from v1.

10. **`CLAUDE.md` counter update + Q-CS-3 cosmetic fix** — UNCHANGED from v1.

11. **(NEW v2) Plan-task KB doc updates for ADR-0058**:
    - Layer: Claude Code.
    - Technical Reason: ADR-0037's schema home is `KB-mcp-design/references/principles.md`; the usage docs are `KB-mcp-platform/references/mcp-events-jsonl.md`. Plan Authoring updates these to document the four-type vocabulary per ADR-0058.
    - Dependent Elements: future readers of the event-surface schema.
    - The edits are mechanical: add the fourth event type's documentation alongside the three existing entries; preserve all existing prose; cite ADR-0058.

12. **(NEW v2.1 per Architecture Audit cycle 1 finding I-AA-001 part (a)) Plan-task: OP-7 schema extension for `calibration_result`**:
    - Layer: Claude Code.
    - Technical Reason: Extend `.claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py`'s `REQUIRED_FIELDS` dict and `VALID_EVENT_TYPES` set to admit `calibration_result` with its canonical payload shape per ADR-0058 (required fields: `event`, `timestamp`, `server`, `mechanism`, `version`, `duration_ms`, `outcome`, `signals`, `note`). Without this extension every FR-4b emission triggers a MAJOR OP-7 finding because the script's default for unknown event types is MAJOR; OP-7 schema must learn the new vocabulary in lockstep with the first emission.
    - Dependent Elements: FR-4b script (every emission depends on the schema admitting `calibration_result`); the FR-4c CI workflow (depends on the script not generating spurious OP-7 findings on every invocation); the Q-CS-1b banner (depends on the file being well-formed for OP-7 audits).
    - Sequencing: this task MUST complete in the same PR as the FR-4b script and the new ADR-0058 record. The OP-7 schema extension and the first FR-4b emission must land in the same commit set; otherwise the first emission generates an OP-7 MAJOR finding before the next OP-7 audit cycle catches the schema gap. Single-PR D-0008 decision encloses this dependency.

13. **(NEW v2.1 per Architecture Audit cycle 1 finding I-AA-005) Plan-task: immediate post-merge banner-retirement workflow run**:
    - Layer: CI/CD (workflow invocation) + Codespaces (observable banner side-effect).
    - Technical Reason: Immediately post-merge, invoke `gh workflow run gitnexus-grammar-skip-calibration.yml --ref main` once to write the first `calibration_result` event to `.claude/runtime/mcp-events.jsonl`. This retires the Q-CS-1b "NEVER RUN" banner before any operator's first post-merge devcontainer rebuild. Without this task, every operator sees the banner on first rebuild, which is correct behavior but undermines the banner's signal-to-noise ratio (the banner is meant to flag long-stale calibration data, not first-deploy state).
    - Dependent Elements: every operator's first devcontainer rebuild post-merge (the banner is informational and reads the most recent `calibration_result` event timestamp).
    - Sequencing: this task is the LAST ordered task in the implementation sequence — it runs after PR merge to `main`, after the workflow file is on `main`'s ref, and before any operator's first rebuild. The operational handoff is "merge → run workflow → operators rebuild." The cron tick covers steady state from that point onward.

#### Cross-Layer Sequencing Notes

- **Schema before code**: ADR-0057 + ADR-0058 are referenced by orchestrator-internal logic and by the FR-4b script + Q-CS-1b banner + FR-4c CI summary. Both ADRs are authored at Design Composition time (this Blueprint pass for ADR-0058; Blueprint v1 for ADR-0057); the dependent code edits land at Implementation.
- **API before client**: N/A.
- **IaC before pipeline**: N/A.
- **Devcontainer before everything**: The FR-4c CI workflow depends on the FR-4b script existing inside the devcontainer image. The script + the FR-4a block + the Q-CS-1b banner all land in the same `.devcontainer/` commit per step 6; FR-4c depends on that commit's contents (step 7).
- **Two workflows land atomically per actionlint discipline**: per cicd-design v0.3.0 §Plan task — actionlint deferral, both `.github/workflows/` files must pass lint before either is committed.

### Migration Strategy

- **`checkpoint.json` schema migration (per ADR-0057)**: UNCHANGED from v1.
- **`.mcp.json` migration**: None. UNCHANGED.
- **ADR-0041 migration**: None. UNCHANGED.
- **Reviewer-output migration**: None. UNCHANGED.
- **NEW v2 (PROSE-CORRECTED in v2.1): `mcp-events.jsonl` event-type vocabulary migration (per ADR-0058)**: Additive — no migration of existing event records. Existing three event types (`install_complete`, `readiness_probe`, `structured_failure` per ADR-0037 v1.0.2) are preserved verbatim; new `calibration_result` records are appended by the FR-4b script after it ships. Existing consumers that ignore unknown types continue to work without modification. The Q-CS-1b banner gracefully handles the "no `calibration_result` event has been recorded yet" case (infinite staleness — emits "NEVER RUN" banner suggesting the maintainer trigger the calibration).

### Feature Flags & Rollout

No feature flags. UNCHANGED from v1. The mechanisms are deterministic gates; the PRD §Rollout Plan kill criteria (now including the v0.3.0 additions for FR-4a and FR-4c per PRD §Kill criteria rows) are the rollback levers.

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: UNCHANGED from v1. Neither FR-4a nor FR-4b nor FR-4c introduces a new authn/authz surface.
- **Input Validation**: UNCHANGED. FR-4a's static checks operate on environment variables, filesystem paths, and the project's own `versions.env` — no PR-author-controlled input. FR-4b reads its `GITNEXUS_TAG` from `versions.env` (project-owned). FR-4c's workflow YAML interpolates only the GitHub-controlled `${{ github.event_name }}` enum into a Markdown summary (safe per KB non-negotiable #3).
- **Sensitive Data Handling**: UNCHANGED. NFR-8 honored: env-var names emitted, values never. Verified across FR-4a / FR-4b / FR-4c.

### Frontend / Backend / API / Query / Database

N/A — out of scope.

### CI/CD

- **Secret exposure surface**: zero secrets read by BOTH workflows. `pull_request` (not `pull_request_target`) used in BOTH. `permissions: contents: read` only in BOTH.
- **Supply chain**: third-party action SHA-pinning REQUIRED in BOTH workflows per cicd-design v0.3.0 §SHA-pinning. Same SHAs reused across both per the cicd-design Plan task contract.
- **OIDC vs long-lived credentials**: N/A — no cloud integration in either workflow.

### IaC

N/A — out of scope.

### Codespaces

- **Repo access from Codespace**: inherited unchanged.
- **Dotfiles / extension trust**: inherited unchanged. FR-4 family introduces no new extension or first-run prompt.
- **FR-4a specific**: the static check reads `GITNEXUS_TAG` (non-secret), `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (non-secret), and `versions.env` (committed project file). Diagnostics name env-var keys, not values (NFR-8).
- **FR-4b specific**: the calibration script reads `GITNEXUS_TAG` (non-secret) and runs an `npm install` against the public `gitnexus` npm package (no auth needed). Scratch directories cleaned via `trap EXIT`. No new credential surface (NFR-7 / AC-CS-NFR-7-a per codespaces-design v0.3.0).
- **Q-CS-1b banner specific**: reads `.claude/runtime/mcp-events.jsonl` (committed location, gitignored content per ADR-0037 Implementation Guidance). Diagnostics name the staleness age but not any env-var value.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---|---|---|
| `verdict_findings_parity.py` fixtures | No (real reviewer-output JSON fixtures) | UNCHANGED from v1 |
| `audit_op11_adr_parity.py` fixtures | No (real `.mcp.json` + ADR-0041 snapshots) | UNCHANGED from v1 |
| `claude --bare -p "noop"` in CI | No (run the real CLI inside the devcontainer image) | UNCHANGED from v1 |
| `npm install -g gitnexus@1.6.5` in the FR-4b calibration | No (run the real install at the pinned tag in a scratch directory) | UNCHANGED — the whole point of FR-4b is asserting the real-install observable state. v2 confirms this in scratch rather than the global state. |
| **FR-4a static-shape check fixtures (v2)** | **No (use real `postCreate.sh` against fixture-broken environment states)** | **FR-4a's correctness depends on real shell-level behavior — env-var unset semantics, regex matching, `npm root -g` output. Mocking would shift the test surface.** |
| **Q-CS-1b staleness banner fixtures (v2)** | **No (use real `mcp-events.jsonl` fixtures with constructed timestamps)** | **The banner's correctness depends on the real `jq` filter against the real event-file format. Constructed fixtures with old timestamps are the test mode.** |
| **FR-4c workflow (v2)** | **No (use real `workflow_dispatch` runs against draft branch)** | **Pre-merge validation per cicd-design v0.3.0 §D-0010 — measure real wall-clock for cold-cache, warm-cache, and no-op-rebuild runs; confirm Monday 07:00 UTC cron parses on first scheduled tick.** |
| GitHub Actions runner | No (real `ubuntu-latest`) | UNCHANGED from v1 |

### Data Layer Testing Strategy

N/A — no database in scope.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|---|---|---|---|
| Claude Code (FR-1 / FR-2 / FR-3) | Unit-style fixtures + pipeline-level smoke | `python3` + JSON fixtures + pipeline run | UNCHANGED from v1 |
| **Codespaces (FR-4a)** | **Real devcontainer rebuild + fixture-broken-static-shape rebuild** | **Manual rebuild against environments with unset `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, malformed `GITNEXUS_TAG`, mismatched `versions.env`, and broken `npm root -g`** | **Demonstrated during the feature's verification per PRD Success Criteria** |
| **Codespaces (FR-4b)** | **Real calibration runs against current pin + fixture broken-contract pin** | **`bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` against `gitnexus@1.6.5` (pass case) + a constructed-fail-case fixture pin** | **Documented in the script's head comment; demonstrated per PRD Success Criteria** |
| **Codespaces (Q-CS-1b banner)** | **Fixture-timestamped `mcp-events.jsonl` + real rebuild** | **Pre-populate `.claude/runtime/mcp-events.jsonl` with a `calibration_result` event timestamped 3 weeks ago; rebuild; observe banner. Also test "no event ever" by removing the event-file content; rebuild; observe "NEVER RUN" banner.** | **Plan author defines fixture under `working/feature/<test-slug>/`** |
| **CI/CD (FR-4c)** | **Real `workflow_dispatch` + fixture-pin-bump PR + cron-tick observation** | **GitHub Actions — three `workflow_dispatch` runs against draft branch to measure runtime per cicd-design v0.3.0 §D-0010; one fixture PR opening with a `versions.env` change to confirm trigger fires; observe first Monday cron tick to confirm scheduled trigger works** | **Pre-merge validation gate (cicd-design v0.3.0 §D-0010); demonstrated PR-fail per PRD Success Criteria** |
| CI/CD (FR-5) | Real workflow_dispatch + fixture PR | GitHub Actions | UNCHANGED from v1 |

### Integration Verification Points

- The orchestrator running end-to-end with all five mechanisms enabled against a known-good fixture pipeline run (smoke). UNCHANGED.
- The orchestrator running end-to-end with one mechanism disabled to confirm per-mechanism isolation per NFR-11 (AC-X-1). UNCHANGED.
- The two CI workflows running pre-merge against the draft branch — three runs each for FR-5 (per v1 D-0010) and FR-4c (per cicd-design v0.3.0 §D-0010 NFR-4 commitment).
- **NEW v2**: a real devcontainer rebuild with `.claude/runtime/mcp-events.jsonl` carrying both a < 2-week-old and a > 2-week-old `calibration_result` event, to verify the Q-CS-1b banner logic.
- **NEW v2 (PROSE-CORRECTED in v2.1)**: the FR-4b calibration script run against a known-good pin (`gitnexus@1.6.5`) to verify the `calibration_result` event payload conforms to ADR-0058's canonical shape; the OP-7 audit rule (the schema-validation rule implemented by `audit_op7_events_schema.py`; or a fixture test) verifies the conformance. Note: this requires the Plan-author's OP-7 extension task to have landed (see §Implementation Plan task 11.a) — without it, every FR-4b emission triggers an OP-7 MAJOR finding for the unknown event-type vocabulary expansion.

## Verification Strategy

### Correctness Proof Method

- **Correctness definition** — UNCHANGED from v1: each mechanism produces the expected verdict on its named failure mode and the expected pass on the negation.
- **Verification method** — fixture-driven for FR-1 / FR-2 / FR-3 / FR-7 verify (UNCHANGED); real-rebuild for FR-4a (REVISED v2 — static-shape fixtures); real-invocation for FR-4b (NEW v2); real-workflow for FR-4c (NEW v2) and FR-5 (UNCHANGED).
- **Verification timing** — per-mechanism unit verification at implementation time; pre-merge integration verification per cicd-design v0.3.0 §D-0010 (both FR-5 latency gate AND FR-4c latency gate); post-merge per PRD Success Criteria.

### Early Verification Point

- **First verification target** — UNCHANGED from v1 in shape; v2.1 EXPANDS the pre-emption scope: FR-3 OP-11 against current `.mcp.json` and the annotated ADR-0041. After the `[DEPRECATED INVOCATION FORM]` annotations are added to **both row 71 (mcp-openapi-schema) AND row 70 (Serena)** per the v2.1 FR-3 pre-emption expansion (Architecture Audit cycle 1 finding I-AA-003), OP-11 should produce zero findings on first invocation. Without the row 70 annotation, OP-11's canonicalize+opaque-tokens algorithm against ADR-0041 row 70's Form column ↔ `.mcp.json` Serena entry would emit a day-one BLOCKER false positive (distinct command verbs and arg shapes). The row 70 annotation closes that gap.
- **Second verification target (NEW in v2)**: FR-4b calibration against the current `gitnexus@1.6.5` pin. After the script ships, a single `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` invocation should: (i) exit 0; (ii) emit one `calibration_result` event with `outcome: "pass"`; (iii) the event payload conforms to ADR-0058's canonical shape. This is the smallest, fastest, lowest-blast-radius check that proves the calibration's contract and the event-emission discipline are both correct.

### Output Comparison

N/A — every mechanism introduces new behavior. UNCHANGED from v1.

### Operational Verification

- **Pre-merge gates**: FR-5 workflow becomes a pre-merge gate for PRs touching the configured paths (UNCHANGED). **NEW in v2**: FR-4c workflow becomes a pre-merge gate for PRs touching `.devcontainer/versions.env` or `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Pre-merge validation per cicd-design v0.3.0 §D-0010 (three `workflow_dispatch` runs for each workflow) gates the merge of this feature itself.
- **Post-deploy verification**: per PRD Success Criteria (UNCHANGED list, with v0.3.0 reshape additions for FR-4a static-shape demonstrations and FR-4b/FR-4c calibration demonstrations).
- **Migration verification**: AC-CC-2-g check (resume pre-feature checkpoint) — UNCHANGED. **NEW v2**: confirm the Q-CS-1b banner gracefully handles an `mcp-events.jsonl` file with no `calibration_result` events by emitting the "NEVER RUN" variant.
- **Rollback rehearsal**: per PRD §Rollout Plan kill criteria. Each mechanism (and within the FR-4 family, each sub-mechanism) is independently revertable per NFR-11 / AC-X-1.

## Future Extensibility

- **Extension point: FR-1 blocking-severity set expansion** — UNCHANGED from v1.
- **Extension point: OP-11 ADR-table parser** — UNCHANGED from v1.
- **Extension point: `checkpoint.execution_mode` enum expansion** — UNCHANGED from v1 (ADR-0057).
- **Extension point: `[DEPRECATED]` marker convention project-wide** — UNCHANGED from v1.
- **NEW v2 — Extension point: `calibration_result` event type for future behavioral calibrations.** ADR-0058's `mechanism:` field is the namespace discriminator. Future calibrations (e.g., a hypothetical FR-4-style behavioral check for a different upstream contract) reuse `event: "calibration_result"` with a different `mechanism:` namespace string and a per-mechanism `signals` map shape. Per-mechanism `signals` shapes do not require per-mechanism ADRs — the `mechanism:` field is the discriminator and ADR-0058 explicitly admits open-ended `signals` map shapes per-mechanism.
- **NEW v2 — Extension point: Q-CS-1b banner threshold.** The 2-week threshold is fixed by Blueprint v2 composer arbitration. A future feature observing the value is too aggressive (e.g., frequent false-positive banners) can lower it; observing it is too lax (drift not surfaced) can raise it. The Plan author MAY surface the threshold as a `versions.env` variable if maintainability calls for it; the Blueprint does not require this.
- **NEW v2 — Extension point: chain FR-4c into FR-5's workflow set or extract a reusable workflow.** Per cicd-design v0.3.0 §Reusable Actions / Composite Actions, both workflows currently share the `actions/checkout` + `devcontainers/ci` pattern. A third workflow (Q-CICD-3 merge-time smoke, Q-CICD-4 nightly upstream-health) would be the moment to extract `.github/actions/devcontainer-runner/action.yml` or a reusable `.github/workflows/devcontainer-smoke.yml`. Not now.
- **Known future requirements**: the eight Won't-Have items in PRD §Won't Have are the deferred follow-on systemic-remediation feature. UNCHANGED — the v2 reshape stays within the carve-out.
- **Intentional limitations**: per the PRD carve-out, this feature does NOT close the broader systemic gap. UNCHANGED.

## Alternative Solutions

### Alternative 1: In-agent self-validation for FR-1 — UNCHANGED from v1 (rejected).

### Alternative 2: New gate script for FR-2 — UNCHANGED from v1 (rejected).

### Alternative 3: Amend ADR-0041 to drop the `mcp-openapi-schema` row — UNCHANGED from v1 (rejected).

### Alternative 4: `claude mcp list` for FR-5 — UNCHANGED from v1 (rejected).

### Alternative 5: Five sequenced PRs (one per FR group) instead of one bundled PR — UNCHANGED from v1 (rejected).

### NEW v2 — Alternative 6: Single per-rebuild dry-run (the v0.2.0 design that v0.3.0 supersedes)

- **Overview**: Keep the v0.2.0 design — a unified dry-run inside `install_gitnexus()` between lines 142 and 143 that performs Signal 1 stderr regex + Signal 3 artifact absence on every cache-miss `npm install -g`.
- **Advantages**: Single mechanism, single insertion site, no new workflow.
- **Disadvantages**: Per the PRD v0.3.0 §Background and the user-direction-at-Gate-4-prep verbatim direction: "Doubling the GitNexus step on cache-miss rebuilds for a check that only fires when upstream has actually drifted gets nothing back for most rebuilds." The per-rebuild and behavioral questions are different cadences; conflating them either pays behavioral cost on every rebuild (against ADR-0041's 7-12 min codespace budget) or quietly stops firing as a maintainer-only script. The v0.3.0 reshape into FR-4a + FR-4b + FR-4c structurally separates the cadences.
- **Reason for Rejection**: Per user direction at Gate-4 prep (2026-05-26, verbatim in PRD v0.3.0 Appendix). The v0.3.0 reshape is the canonical resolution.

### NEW v2 — Alternative 7: Reuse `install_complete` / `structured_failure` with stringified `signals` for FR-4b's emission (Interpretation B; v2.1 prose-corrected)

- **Overview**: Per Q-CS-1a Interpretation B — pack the calibration's signals map as a JSON-stringified blob into the existing `install_complete` (pass — since the calibration does install gitnexus into a scratch dir) / `structured_failure` (fail / drift_detected) event's `note:` free-text field. No new event type. [v2.1 prose correction: v2.0.0 of this Blueprint described Interpretation B as packing into `primary_degraded` / `structured_failure`. Since `primary_degraded` is a boolean sub-field of `structured_failure` rather than a distinct event type per ADR-0037 v1.0.2, the accurate description of Interpretation B is packing into `install_complete` (pass) or `structured_failure` (fail), per the actual on-disk vocabulary.]
- **Advantages**: Preserves NFR-13's "no new event types" under a strict reading.
- **Disadvantages**: Couples a semantic, queryable signal (pass/fail/drift_detected + per-grammar Signal-N outcomes) into a free-text field; downstream consumers must JSON-parse `note:` to act on it; OP-7 audit rule (the schema-validation rule) cannot validate the embedded shape (it admits the event type but cannot reason about the stringified payload); semantically dishonest (the calibration is not an "install" in the existing install_gitnexus sense — though both touch npm install, the load-bearing observation is the contract-honoring outcome, not the install itself).
- **Reason for Rejection**: Per composer arbitration of Q-CS-1a / Q-CICD-11 — the PRD's NFR-13 verbatim admits the additive extension and directs Design to "either amending ADR-0037 or issuing a small new ADR." Interpretation A (the new event type via ADR-0058) is the documented path; Interpretation B violates the spirit of NFR-13's additive-extension text.

### NEW v2 — Alternative 8: Defer the Q-CS-1b staleness banner to a follow-on feature

- **Overview**: Ship FR-4c (CI cron + on-change-to-`versions.env`) without the `postCreate.sh` runtime staleness banner; rely on the CI cron alone to defeat the "calibration script that quietly stops running" trap.
- **Advantages**: Smaller v2 surface; one less integration point to verify.
- **Disadvantages**: If CI itself is disabled (org policy, billing pause, broken `.github/workflows/` permissions, runner outage), the script's invocation cadence collapses to "manual maintainer only" — the very trap the user named. The banner is the belt-and-suspenders defense that surfaces the trap at the maintainer's next devcontainer rebuild, not on a CI surface the maintainer may not be watching.
- **Reason for Rejection**: Per composer arbitration of Q-CS-1b / Q-CICD-10 — both per-layer designers recommended YES (cost is ~10 lines of shell + one `jq` invocation per rebuild). The user direction at Gate-4 prep is explicit about defeating the trap "if it ends up as a maintainer-only shell script that nobody invokes for six months, option 3 degrades silently." The banner is the rebuild-time observability surface that the CI surface alone does not cover. The 2-week threshold balances "weekly cron + one week grace" — tight enough to surface drift quickly, loose enough to absorb one missed cron.

## Risks and Mitigation

*(Carries forward Blueprint v1 risks plus v2-specific additions per PRD v0.3.0 §Risks and Mitigation.)*

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| FR-3 OP-11 false positives | Claude Code | Medium | Medium | UNCHANGED from v1 in shape; v2.1 EXPANDS the pre-emption coverage per Architecture Audit cycle 1 finding I-AA-003: BOTH ADR-0041 row 71 (mcp-openapi-schema) AND row 70 (Serena) now carry `[DEPRECATED INVOCATION FORM]` annotations, closing the day-one false-positive surface for both shape-of-drift cases. Kill criterion + narrow canonicalizer remain the v1 mitigations; row-level annotation is the v2/v2.1 mitigation. |
| FR-1 blocking-severity set too inclusive (NFR-9 breach) | Claude Code | Medium | Low | UNCHANGED from v1 |
| **FR-4a passes (static shape clean) but upstream behavioral contract is broken, so per-rebuild is silent while drift exists** | **Codespaces** | **Low (deliberate split — per-rebuild and behavioral are different questions on different cadences)** | **Medium** | **Per PRD v0.3.0 §Risks: this is the deliberate split — FR-4c's weekly cron + on-change-to-`versions.env` triggers are the safety net. Q-CS-1b staleness banner is the belt-and-suspenders surface alerting the maintainer at rebuild time if calibration has gone stale.** |
| **FR-4b silent pass (env-var contract broken in a way Signal 1 + Signal 3 don't detect)** | **Codespaces** | **Medium (recreates the failure mode FR-4b is meant to catch)** | **Low** | **Per cicd-design v0.3.0 §Trap-avoidance: negative-assertion confirmation enabled-by-default catches the "skipping regardless of env-var" case. Signal-1-AND-Signal-3 conjunction catches the "wrong-reason skip" case. NFR-6 fail-closed-on-internal-error is the secondary safety net.** |
| **FR-4c trigger set misses a path that bumps the pin (e.g., a hypothetical future Dockerfile rewrite that changes the pin without touching `versions.env`)** | **CI/CD** | **Medium (workflow does not run when it should)** | **Low-Medium** | **Per PRD v0.3.0 §Risks: the `pull_request paths:` filter explicitly covers `.devcontainer/versions.env` AND `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. If a future feature relocates `versions.env` or splits the pin across multiple files, the filter must be updated in lockstep — flagged in cicd-dependencies.json as a tight cross-layer contract.** |
| **`calibration_result` event-type extension breaks downstream tooling that strictly validates event types** | **Cross-cutting (CC, Codespaces consumers)** | **Medium (could break consumers of the event surface)** | **Low** | **Per NFR-13's additive-extension discipline + ADR-0058's documented Interpretation A: existing consumers ignore unknown types per ADR-0037 forward-compatibility posture. The schema home (`KB-mcp-design/references/principles.md`) is updated by Plan Authoring to document the four-type vocabulary so future readers see it as a documented member of the schema rather than an undocumented appendage.** |
| FR-5 unauthenticated-CLI assumption doesn't hold | CI/CD | Medium | Low-Medium | UNCHANGED from v1 (Q-CICD-8 pre-merge validation gate) |
| FR-5 runtime exceeds NFR-4 5-minute ceiling | CI/CD | Medium | Low-Medium | UNCHANGED from v1 |
| **FR-4c runtime exceeds NFR-4 5-minute per-workflow ceiling** | **CI/CD** | **Medium (PR friction on pin-bump; maintainer pressure to disable)** | **Low** | **Per cicd-design v0.3.0 §NFR alignment: p95 estimated under 2 minutes (image-build dominates and is shared with FR-5). PRD v0.3.0 §Kill criteria allows narrower assertion or slower cadence if budget exceeded. Pre-merge validation per cicd-design v0.3.0 §D-0010 confirms before ship.** |
| `checkpoint.execution_mode` enum too narrow | Claude Code | Low | Low | UNCHANGED from v1 (ADR-0057 §Kill criteria) |
| PR-shape choice creates merge-order ambiguity | Cross-cutting | Low | Low | UNCHANGED from v1 (NFR-11 isolation) |
| Five mechanisms each pass but don't prevent MCP-incident-pattern (systemic gap deferred) | Cross-cutting | Medium-High | Medium | UNCHANGED from v1 (carve-out is explicit) |
| ADR-0041 table format changes in a future amendment, breaking OP-11's parser | Claude Code | Low | Low | UNCHANGED from v1 |
| SHA-pin regression in `.github/workflows/` | CI/CD | Medium | Low | UNCHANGED from v1 — extended to BOTH workflows per cicd-design v0.3.0 §SHA-pinning |

## References

- PRD: `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` (v0.3.0 Gate-4-prep reshape of FR-4).
- Per-layer Designs (integrated by reference in this Blueprint):
  - `working/feature/pipeline-quickwins-hardening-r1/cc-design.md` v0.2.0 (UNCHANGED — FR-1 / FR-2 / FR-3 / FR-7 untouched by the FR-4 reshape).
  - `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` **v0.3.1** (v2.1 prose-only repair per Architecture Audit cycle 1 finding I-AA-001 collateral — event-type triad corrected; v0.3.0 hybrid structure unchanged).
  - `working/feature/pipeline-quickwins-hardening-r1/cicd-design.md` **v0.3.0** (REVISED — FR-4c calibration workflow + symmetric SHA-pinning Plan-task contract across both workflows).
- Per-layer Dependencies sidecars:
  - `working/feature/pipeline-quickwins-hardening-r1/cc-dependencies.json` v0.2.0 (UNCHANGED).
  - `working/feature/pipeline-quickwins-hardening-r1/codespaces-dependencies.json` **v2.1.0** (v2.1 prose-only repair per Architecture Audit cycle 1 finding I-AA-001 collateral — event-type triad corrected; v2.0.0 structure unchanged).
  - `working/feature/pipeline-quickwins-hardening-r1/cicd-dependencies.json` v1.0.0 (source_design_version: 0.3.0).
- Codebase analysis: `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json` (UNCHANGED).
- Research notes:
  - `working/feature/pipeline-quickwins-hardening-r1/research-notes/t-001-gitnexus-grammar-skip-contract.md`.
  - `working/feature/pipeline-quickwins-hardening-r1/research-notes/t-002-claude-mcp-list-contract.md`.
- Synthesis: `working/feature/pipeline-quickwins-hardening-r1/synthesis.md` (v1 framing; v0.3.0 reshape is a Gate-4-prep refinement on top).
- Seed proposal: `Issues/cross-artifact-divergence-detection-gap/proposal.md`.
- Deferral register: `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`.
- ADRs referenced: see frontmatter `adrs_referenced`. ADRs authored: ADR-0057 (Blueprint v1) + **ADR-0058 (Blueprint v2; NEW)** at `adrs/ADR-0058-calibration-result-event-type-additive-extension.md`.
- KBs consulted: KB-documentation-criteria, KB-cc-design, KB-cc-platform, KB-codespaces-design, KB-codespaces-platform, KB-github-actions-design, KB-github-actions-platform, KB-review-disciplines, KB-general-coding-principles.
- Predecessor Blueprint: `working/feature/pipeline-quickwins-hardening-r1/blueprint-v1.md` (preserved for audit trail; v2 is the operative version for Gate 4).

### Cross-references — Inherited ADRs Applied

*(Carried forward from Blueprint v1 with v2 additions.)*

- **ADR-0005** (append-only supersession) — applied to: (a) the inline `[DEPRECATED INVOCATION FORM]` annotations on ADR-0041 **row 71 (mcp-openapi-schema) AND row 70 (Serena — v2.1 addition per Architecture Audit cycle 1 finding I-AA-003)** (annotation pattern; decision text preserved verbatim); (b) **the new ADR-0058 (additive extension of ADR-0037; cite-and-extend rather than in-place amend per the discipline; ADR-0058 revised in draft per v2.1 reconciliation)**; (c) **the in-place ADR-0037 v1.0.1 → v1.0.2 prose amendment (prose-only, no decision-content change — admitted by ADR-0005's append-only discipline because only the description of pre-existing state moves to match on-disk reality)**; (d) **the in-place ADR-0057 v1.0.0 → v1.0.1 prose amendment (prose-only, no decision-content change — Context framing reworded from "introduce" to "promote-and-formalize")**.
- **ADR-0017** (document-reviewer integration) — UNCHANGED from v1.
- **ADR-0029 / ADR-0033** (no silent scope changes) — UNCHANGED from v1; **v2 also surfaces the FR-4 internal split into three sub-mechanisms explicitly rather than silently per the same principle**.
- **ADR-0036 / ADR-0056** (canonical ADR placement, no carve-outs) — ADR-0057 AND **ADR-0058** both live at `adrs/`.
- **ADR-0037** (mcp-events.jsonl event schema; **amended in-place to v1.0.2 per v2.1 Architecture Audit cycle 1 findings I-AA-001 + I-AA-002**) — **EXTENDED additively by ADR-0058 (NEW in v2)** to admit the fourth event type `calibration_result`. The three pre-existing event types (`install_complete`, `readiness_probe`, `structured_failure` per the v1.0.2 prose correction) and the closed-enum discipline are preserved verbatim; the vocabulary remains closed at four values. v1.0.2 prose corrections (decision content unchanged): (a) event-type triad enumeration corrected from `primary_degraded` to `install_complete` (the on-disk top-level event type per `audit_op7_events_schema.py` `VALID_EVENT_TYPES`; `primary_degraded` is a boolean sub-field of `structured_failure`); (b) §Architecture Impact item 4's audit-rule citation corrected from OP-6 to OP-7 (OP-7 is the schema-validation rule; OP-6 audits credential redaction).
- **ADR-0039 / ADR-0040** — UNCHANGED from v1.
- **ADR-0041 / ADR-0042 / ADR-0043** — UNCHANGED from v1.
- **ADR-0044** (flatten execution dispatch hierarchy) — UNCHANGED from v1.
- **ADR-0057** (`checkpoint.execution_mode` first-class field; authored Blueprint v1) — UNCHANGED in v2 — the FR-4 reshape does not perturb this ADR's surface.

### Cross-references — New ADRs Authored (this run)

- **ADR-0057** (`checkpoint.execution_mode` as first-class field) — authored Blueprint v1; **carried forward verbatim in v2**.
- **ADR-0058** (`calibration_result` event type — additive extension to ADR-0037) — `adrs/ADR-0058-calibration-result-event-type-additive-extension.md`. **NEW in v2 (revised in v2.1).** Authored by design-composer during this Blueprint pass per the Q-CS-1a / Q-CICD-11 composer disposition. Rationale: PRD v0.3.0 §NFR-13 verbatim directs Design to "either amending ADR-0037 or issuing a small new ADR that records the additive extension." The "small new ADR" path is selected over in-place amendment of ADR-0037 because (i) ADR-0037 v1.0.1's Decision Details / Kill-criteria items are stable and re-opening them would create cross-cutting ambiguity; (ii) ADR-0005's append-only discipline prefers cite-and-extend over in-place amendment; (iii) the schema-surface change has the same architectural-grade shape as ADR-0057 (cross-component blast radius across event-surface consumers), clearing the ADR-worthiness bar. The four-type vocabulary remains closed; OP-7 audit rule discipline (schema validation; `audit_op7_events_schema.py`) is preserved; OP-6 (credential redaction) is a distinct rule unaffected; existing consumers that ignore unknown types continue to work without modification. [v2.1 prose corrections to ADR-0058 itself: event-type triad corrected (was inheriting ADR-0037 v1.0.0 / v1.0.1 prose error; corrected in lockstep with ADR-0037 v1.0.2); OP-6 → OP-7 label corrected for schema-validation rule references.]

### Cross-references — Resolved Q-`<LAYER>`-N Items (composer dispositions)

**Claude Code layer:** *(All six dispositions UNCHANGED from Blueprint v1.)*

- **Q-CC-1 through Q-CC-6** — see Blueprint v1 §Cross-references — Resolved Q-items. cc-design.md remains at v0.2.0; FR-1 / FR-2 / FR-3 / FR-7 are untouched by the v0.3.0 reshape.

**Codespaces layer:**

- **Q-CS-1 (REFRAMED in v0.3.0 codespaces-design; resolved in two parts in Blueprint v2)**:
  - **Q-CS-1a (event-type extension — does NFR-13 admit a new `calibration_result` event-type for FR-4b?)**: **disposition = (a) Interpretation A — admit the new event type via the small new ADR ADR-0058 (codespaces-design + cicd-design recommendations aligned).** Rationale: PRD v0.3.0 §NFR-13 verbatim admits the additive extension and directs Design to issue a small new ADR; Interpretation B (reuse existing types with stringified `signals` in `note:`) couples a semantic question into a free-text field, fails the OP-7 audit rule's shape discipline (the schema-validation rule; not OP-6, which audits credential redaction), and creates the documentation-vs-realization drift this carve-out exists to prevent. **ADR-0058 authored this run (revised in draft per v2.1 reconciliation)** to document the additive extension; the three pre-existing event types are preserved verbatim; the closed-enum discipline is preserved at four values.
  - **Q-CS-1b (runtime staleness banner in `postCreate.sh`)**: **disposition = (a) admit the banner with N=2 weeks threshold** (codespaces-design + cicd-design recommendations aligned). Rationale: per user direction at Gate-4 prep verbatim — "If it ends up as a maintainer-only shell script that nobody invokes for six months, option 3 degrades silently into option 1." The CI cron alone is insufficient because CI itself can be disabled (org policy, billing pause, broken `.github/workflows/` permissions). The banner is the belt-and-suspenders rebuild-time observability surface; cost is ~10 lines of shell + one `jq` invocation per rebuild — trivial against the benefit of defeating the user-named trap. N=2 weeks is the canonical threshold (weekly cron + one week grace). The implementation is mechanical and is documented in AC-X-4 above.
- **Q-CS-2 (two-sentinel-format inconsistency deferred surface)**: **disposition = surface as deferred-issue row in `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`** (UNCHANGED from v1).
- **Q-CS-3 (cosmetic 5-vs-4 server reference in `postCreate.sh:5`)**: **disposition = fix the stray "5" in the FR-4a commit** (UNCHANGED from v1).
- **Q-CS-4 (prebuild policy)**: **disposition = no prebuild adopted** (UNCHANGED from v1).
- **Q-CS-5 (D-0008 PR shape from Codespaces view)**: **disposition = same as Q-CC-4 — single bundled PR** (UNCHANGED from v1; codespaces-design v0.3.0 §Q-CS-5 confirms the v2 increment of one new standalone script + one new top-level block is still single-file-plus-one-new-file from the Codespaces view).

**CI/CD layer:**

- **Q-CICD-1 through Q-CICD-9** — UNCHANGED from Blueprint v1. See Blueprint v1 §Cross-references — Resolved Q-items.
- **Q-CICD-10 (stale-calibration banner in `postCreate.sh`)**: **disposition = same as Q-CS-1b — admit the banner with N=2 weeks threshold**. Rationale: the question is structurally the same as Q-CS-1b (cicd-design surfaced it because the FR-4c CI cron's value depends on the calibration's cadence being maintained even when CI itself is unavailable; the rebuild-time banner is the belt-and-suspenders surface). The implementation is Codespaces-layer (the banner lives in `postCreate.sh`) per cicd-design v0.3.0 §Q-CICD-10 owner attribution; the cicd-design's surfacing of the question is recorded here for traceability.
- **Q-CICD-11 (ADR-0037 event-surface schema extension for `calibration_result`)**: **disposition = same as Q-CS-1a — admit the new event type via ADR-0058** (cicd-design + codespaces-design recommendations aligned). The composer's reading of ADR-0037 (as corrected in v1.0.2): the event-type set IS closed at three values per ADR-0037 §Decision item 2 and §Architecture Impact item 4 — the three values are `install_complete`, `readiness_probe`, `structured_failure` per the on-disk vocabulary, and the rule that rejects ad-hoc fields is OP-7 (the schema-validation rule; `audit_op7_events_schema.py`). The additive extension is required, not optional. **ADR-0058 authored this run (revised in draft per v2.1 reconciliation)** as the small new ADR the PRD's NFR-13 names. The schema home (`KB-mcp-design/references/principles.md`) and usage docs (`KB-mcp-platform/references/mcp-events-jsonl.md`) are updated by Plan Authoring to document the four-type vocabulary.

### Cross-references — Unresolved Items Deferred to User

None.

The synthesizer flagged D-0008 (PR shape) for user confirmation in Blueprint v1; the composer's disposition (single bundled PR) is recorded in Implementation Approach. **v2 confirms the same disposition** — the FR-4 reshape adds one new script file (FR-4b) and one new workflow file (FR-4c) but does not alter the cross-mechanism coupling story. The Plan author treats single-bundled-PR as the default; if the user redirects to sequenced PRs, NFR-11 makes per-mechanism isolation hold either way and this is a workflow change without a Blueprint revision.

**Carve-out boundary check (v2 reverification)**: the FR-4 reshape stays strictly within the MINOR scope. The eight Won't-Have exclusions in PRD §Won't Have are unchanged. The five-mechanism count is preserved (FR-4a / FR-4b / FR-4c are sub-mechanisms within the FR-4 family per PRD §FR-6 verbatim). No new ADR beyond ADR-0058 (admitted by NFR-13 explicitly) is authored. No scope-creep through the reshape.

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-26 | 2.3.0 | Cross-Artifact Audit cycle 1 reconciliation absorption per reconciliation-log-r3.md (single edit I-CA-002). One inheritance note added to the §Acceptance Criteria preamble naming PRD v0.3.0 §Non-Functional Requirements (lines 336-413) as the canonical source for AC-NFR-1-a through AC-NFR-13-b (inherited-by-reference, not lifted) and explaining that the v2.2 lift cycle was scoped to ACs the Blueprint v2.1 didn't already define (AC-CC / AC-CS / AC-CICD families + freshly authored AC-NFR-14 + aliased AC-NFR-15). The AC-NFR-N-a family was always cited-by-ID with PRD as canonical definition; the inheritance has always worked. The asymmetry between inlined v2.2 ACs and inherited AC-NFR-N-a ACs is structural rather than a v2.2 oversight, and is preserved intentionally because a full lift of AC-NFR-N-a would duplicate text cleanly cited from the PRD without adding traceability value. Purely additive: ZERO existing AC text mutated (lifted or inherited); ZERO decision-content drift; ZERO ADRs authored or amended this cycle; carve-out boundary unchanged; scope class unchanged. After this Blueprint pass, the orchestrator advances Cross-Artifact Audit to cycle 2 for verification that the asymmetry reading is closed. Cycle counter: 1 of 4 for the Cross-Artifact Audit family. | design-composer |
| 2026-05-26 | 2.2.0 | Additive amendment lifting 18 per-layer-design ACs into Blueprint canonical AC catalog per Plan review reconciliation finding I-DR-002 (Plan tasks T2.x / T3.x / T4.x / T7.x cited AC IDs the Blueprint declared "see Blueprint v1" rather than enumerating; downstream review-cross-artifact-auditor surfaced the orphan-citation gap; reconciliation closes it by lifting). From cc-design v0.2.0 §FR-1 cluster: AC-CC-1-d (EARS State-driven; non-blocking-finding passthrough), AC-CC-1-e (EARS Event-driven NFR-6; exit-2 fail-closed), AC-CC-1-f (EARS Ubiquitous FR-6; four-field diagnostic), AC-CC-1-g (EARS Ubiquitous NFR-5; determinism). From cc-design v0.2.0 §FR-2 cluster: AC-CC-2-d (EARS Ubiquitous FR-6; refusal diagnostic four-field), AC-CC-2-e (EARS Ubiquitous NFR-5; self-check determinism), AC-CC-2-f (EARS Unwanted-behavior NFR-6; missing-intent-clarification fail-closed). From cc-design v0.2.0 §FR-3 cluster: AC-CC-3-c (EARS State-driven; missing-in-adr-0041), AC-CC-3-d (EARS State-driven; missing-in-mcp.json), AC-CC-3-e (EARS State-driven; deprecated-row absent silenced), AC-CC-3-f (EARS Unwanted-behavior; deprecated-row-still-present BLOCKER), AC-CC-3-g (EARS Ubiquitous NFR-10; canonicalized-match no finding), AC-CC-3-h (EARS Ubiquitous FR-6; finding four-field), AC-CC-3-i (EARS Ubiquitous NFR-5; OP-11 determinism), AC-CC-3-j (EARS Ubiquitous NFR-7/8; opaque-tokens no-env-read), AC-CC-3-k (EARS Unwanted-behavior NFR-6; parse-failure exit 2). From cc-design v0.2.0 §FR-7 cluster: AC-CC-7-b (EARS Event-driven; H-4 parenthetical verification), AC-CC-7-c (EARS State-driven; row-update-to-canonical). From cicd-design v0.3.0 §FR-5 cluster (recovered verbatim from blueprint-v1.md lines 295-298 where they were originally introduced): AC-CICD-5-b (State-driven, reconciles PRD AC-FR-5-b; status != connected fail), AC-CICD-5-c (State-driven, reconciles PRD AC-FR-5-c; all connected pass), AC-CICD-5-d (Event-driven NFR-6; CLI-non-zero exit 2 distinguishable), AC-CICD-5-e (Ubiquitous FR-6; failing-run four-field), AC-CICD-5-f (Ubiquitous NFR-4; 5-minute ceiling + pre-merge gate). New NFR-coverage ACs: AC-NFR-14 freshly authored (Ubiquitous NFR-14; postCreate.sh execution-time bound — combined FR-4a + Q-CS-1b banner overhead under 150 ms at p95 over 10 rebuilds on the configured 4-CPU machine class; no network, no container, no npm); AC-NFR-15 aliased to AC-X-3 (Ubiquitous NFR-15; MCP-allowlist no-change). Plan citations of AC-NFR-14 in T2.2 / T2.3 and AC-NFR-15 in T4.2 now resolve to canonical Blueprint definitions; the "see Blueprint v1" abbreviated-section pattern is replaced with full AC text inline so every cross-artifact citation lands on a Blueprint-local definition. ZERO existing-AC renumbering; ZERO existing-AC text mutation; ZERO decision-content drift; ZERO new ADRs (this cycle is purely AC catalog completeness). Carve-out boundary reverified intact. After this Blueprint pass, orchestrator re-runs plan-author / Plan reviewer; convergence target is Plan reviewer pass with no orphan AC findings. Cycle counter: 1 of 4 for the Plan family. | design-composer |
| 2026-05-26 | 2.1.0 | Architecture-audit-r1 reconciliation cycle 1 (single consolidated dispatch from finalize-reconciler). Absorbed all five findings from architecture-audit-pipeline-quickwins-hardening-r1-r1 (verdict approved_with_conditions; 0 critical / 3 important / 2 recommended). (1) Event-type triad correction (finding I-AA-001) across Blueprint v2 + ADR-0058 + ADR-0037 source: every reference to the three pre-existing mcp-events.jsonl event types now reads `install_complete / readiness_probe / structured_failure` (the actual on-disk vocabulary per `audit_op7_events_schema.py` `VALID_EVENT_TYPES` and per `.devcontainer/postCreate.sh` live emissions); the prior `primary_degraded` references inherited the v1.0.0 / v1.0.1 ADR-0037 prose error, now corrected in ADR-0037 v1.0.2 in lockstep. (2) OP-6 → OP-7 label correction (finding I-AA-002): every reference to the schema-validation rule now reads OP-7 (`audit_op7_events_schema.py`); OP-6 references are preserved only where they correctly cite credential redaction (the distinct rule implemented by `audit_op6_runtime_log_redaction.py`). (3) FR-3 pre-emption (finding I-AA-003): ADR-0041 row 70 (Serena) joins row 71 (mcp-openapi-schema) in the `[DEPRECATED INVOCATION FORM]` annotation list; row 70 documents `uvx --from` form while `.mcp.json` runs the installed binary — same shape of drift as row 71. (4) ADR-0057 framing correction (finding I-AA-004; recommended-severity): §Context reworded "introduce" → "promote-and-formalize" — the `execution_mode` field is documented in `recipe-feature-pipeline/SKILL.md:138` and 412 and is present (currently nulled) in the live `checkpoint.json:106`. ADR-0057's contribution is the field's promotion to first-class audit-surface status, not its introduction. (5) Two new ordered Plan-tasks (finding I-AA-001 part (a) + I-AA-005): task 12 — extend `audit_op7_events_schema.py` REQUIRED_FIELDS dict and VALID_EVENT_TYPES set to admit `calibration_result` in the same PR as the FR-4b script (otherwise every emission triggers an OP-7 MAJOR finding); task 13 — immediately post-merge, invoke `gh workflow run gitnexus-grammar-skip-calibration.yml` once to write the first `calibration_result` event and retire the Q-CS-1b "NEVER RUN" banner before any operator's first rebuild. Supporting in-place ADR amendments produced in lockstep with this Blueprint pass: ADR-0037 v1.0.1 → v1.0.2 (prose-only, no decision-change); ADR-0057 v1.0.0 → v1.0.1 (prose-only); ADR-0058 revised in draft (still pre-Gate-4); ADR-0041 row 70 annotated (prose-only). Per-layer collateral: codespaces-design v0.3.0 → v0.3.1 + codespaces-dependencies v2.0.0 → v2.1.0 (event-type triad correction); cicd-design unchanged (no drifted label). All decision content (FR-1..FR-7 design, ADR-0057 schema, ADR-0058 extension shape, Q-disposition outcomes, carve-out boundary) preserved verbatim from v2.0.0. After this Blueprint pass, shared-document-reviewer re-runs Gate 0/1 at IP-4; then review-architecture-auditor re-runs cycle 2 for verification that all five findings are resolved. | design-composer |
| 2026-05-26 | 2.0.0 | Absorbed PRD v0.3.0 Gate-4-prep reshape of FR-4 (split into FR-4a per-rebuild static-shape + FR-4b opt-in behavioral calibration + FR-4c CI cron-and-on-change workflow). Authored ADR-0058 (`calibration_result` event-type additive extension to ADR-0037 per Q-CS-1a / Q-CICD-11 disposition Interpretation A). Admitted Q-CS-1b / Q-CICD-10 runtime staleness banner with N=2 weeks threshold. Revised FR-4 ACs (AC-CS-4a-1..7 + AC-CS-4b-1..7 + AC-CICD-4c-1..11 replace v1's AC-CS-4-a..f). Updated Change Impact Map, Interface Change Matrix, Main Components, Field Propagation Map, State Transitions, Architecture Overview ASCII, Data Flow, Error Handling table, Test Boundaries, Verification Strategy to reflect the three-sub-mechanism structure. Two-workflow `.github/workflows/` convention established. NFR-3 tightened to sub-100 ms for FR-4a; NFR-4 widened to per-workflow (covers FR-5 and FR-4c independently); NFR-13 extended to admit the four-type vocabulary. cc-design v0.2.0 unchanged (FR-1 / FR-2 / FR-3 / FR-7 untouched by FR-4 reshape). ADR-0057 carried forward verbatim. All Q-CC-1..6 dispositions, Q-CICD-1..9 dispositions, D-0008 single-bundled-PR shape, and D-0009 deliverable-archive placement preserved. Carve-out boundary reverified intact. | design-composer |
| 2026-05-26 | 1.0.0 | Initial Blueprint composed from cc-design v0.2.0, codespaces-design v0.2.0, cicd-design v0.2.0. Authored ADR-0057. Reconciled AC-FR-5. Recorded all Q-item dispositions. | design-composer |
