---
id: CBA-pipeline-quickwins-hardening-r1
version: 1.0.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
doc_type: codebase-analysis-report
derived_from: working/feature/pipeline-quickwins-hardening-r1/research-plan.md
generated: 2026-05-25T00:00:00Z
generated_by: discovery-codebase-researcher
companion_artifact: working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
---

# Codebase Analysis Report: Pipeline Quick-Wins Hardening (Round 1)

## Executive summary

Five mechanically bounded changes plus diagnostics-and-housekeeping. Every touch point named in the research plan exists, is structurally sound, and is amenable to the carve-out shape the PRD describes. Two material findings from the Gate-3 user-direction sweeps shape the per-layer designs ahead: the FR-1 reviewer set is larger than the four PRD-named agents (execute-task-quality-handler should be in scope, finalize-deliverable-packager is a moderate candidate), and the FR-3 parity rule will produce a false-positive on day one against the mcp-openapi-schema row in ADR-0041 unless the design adopts a deprecation-marker convention. Five remaining decisions reasonably belong to the per-layer designers (FR-1 scope, FR-2 self-check site, FR-3 deprecation handling, FR-4 sentinel posture, FR-7 marker tightening).

## Component inventory

### Reviewer-shaped agents (FR-1 inventory)

The four named in the PRD:

- **shared-document-reviewer** (`.claude/agents/shared-document-reviewer.md`). The pipeline's central reviewer, invoked at five doc_type points per ADR-0017. Emits a verdict object plus severity-tagged findings. Largest reviewer file in the project (26.7KB).
- **review-architecture-auditor** (`.claude/agents/review-architecture-auditor.md`). Stage 8 auditor. Verdict enum `{fail, conditional_pass, pass}`. The severity-to-verdict mapping (BLOCKER → fail, MAJOR → conditional_pass, MINOR/INFO → pass) is explicit in its body.
- **review-cross-artifact-auditor** (`.claude/agents/review-cross-artifact-auditor.md`). Stage 11 auditor. Verdict enum `{fail, conditional_pass, pass, hard_capped}` plus a SECONDARY `convergence` verdict in the same payload — design-claude-code's FR-1 check must decide whether to inspect one or both verdicts.
- **execute-phase-quality-reviewer** (`.claude/agents/execute-phase-quality-reviewer.md`). T7-transition reviewer (per-phase). Emits a 5-dimensional verdict per execution-pipeline-design-r1 Blueprint v5 Contract 2: `{PASS, NEEDS_RECONCILIATION, BLOCKER}` with findings array adjacent.

Additional reviewer-shaped agents surfaced by the scope-completeness sweep:

- **execute-task-quality-handler** (`.claude/agents/execute-task-quality-handler.md`). **STRONG candidate for FR-1 inclusion.** Emits `{APPROVED, NEEDS_REVISION, STUB_DETECTED, BLOCKER}` status enum with a clean findings array (domain, severity, source_activity, file_path, locator, message). The verdict-vs-findings consistency check applies directly: an APPROVED status alongside a finding with `severity: blocker` is the exact contradiction US-1 names. Excluding this agent leaves the execution-side per-task path open to the failure mode FR-1 is meant to catch.
- **finalize-deliverable-packager** (`.claude/agents/finalize-deliverable-packager.md`). **MODERATE candidate.** Emits its own `{PASS, BLOCK, REVIEW}` verdict but the findings field is chained (it includes `reviewer_findings` passed through from the shared-document-reviewer it invokes with `doc_type: DeliverableArchive`). The chained shape complicates the check: if shared-document-reviewer already passed the FR-1 check at its own invocation, re-checking at the packager may be redundant. design-claude-code decides.

Clearer exclusions from the sweep:

- **synth-critic** — uses verdicts but per-CLAIM, not per-INVOCATION. Recommend exclude.
- **synth-framer / synth-synthesizer** — consume verdicts; don't emit a verdict+findings contract pair.
- **finalize-reconciler** — emits a `convergence` verdict but its primary output is a dispatch JSON; the convergence verdict is a downstream summary, not an artifact verdict that can contradict findings.

### Orchestrator + dispatch (FR-2 inventory)

- **recipe-feature-pipeline parent skill** (`.claude/skills/recipe-feature-pipeline/SKILL.md`). 629 lines. Per ADR-0044 (flatten decision), this is the actual parent orchestrator. It directly dispatches reviewers at 5 invocation points and the 4 execution specialists at the T1/T2/T7/T9 transitions. The `scope_class` is currently read at line 350, inside Stage 12 (Deliverable Packaging) — FR-2's self-check needs it earlier (at the start of dispatch). design-claude-code under U-2 must hoist the read or add a second read site.
- **execute-orchestrator advisor** (`.claude/agents/execute-orchestrator.md`). Per ADR-0044, this is **non-invocable**. It is the canonical 12-substantive-state machine reference (T0..T13). FR-2's self-check does NOT live here.

The "single-agent fallback" concept the PRD names is not currently a named state in `checkpoint.json`. It's implicit in `checkpoint.execution_mode = "parent-driven-workaround"` (the historical fallback mode preserved per ADR-0044 for edge-case resumption) AND in any future per-stage agent-selection logic. design-claude-code under U-2 must define the configuration surface FR-2 inspects.

### MCP audit infrastructure (FR-3 inventory)

- **`.claude/skills/auditing-mcp/`** is a graduated family-coordinator per ADR-0042. Empty sub-skill family slot reserved. Hosts 14 Python scripts: `audit_mcp.py` (coordinator) + 10 OP-rule scripts (`audit_op1..audit_op10`) + 3 utility scripts (`check_toxic_combinations.py`, `scan_mcp_secrets.py`, `validate_mcp_config.py`). Each OP script follows a uniform contract: one positional argument, JSON findings to stdout, exit 0/1/2 per pass/fail/error.
- **`.mcp.json`** at the repo root. **Six servers** registered today: actionlint-mcp, context7, exa, gitnexus, serena, terraform-mcp. All entries pass OP-1, OP-9, OP-10 cleanly (env-block indirection only).
- **ADR-0041 v1.0.1** at `adrs/ADR-0041-install-mechanism-hybrid.md`. The per-server install-mechanism taxonomy table at Decision §1.b has **seven rows** — including mcp-openapi-schema, which is no longer in `.mcp.json` (see Deprecation finding below).
- **FR-3 lands as `audit_op11_*.py`** by convention. Severity tokens already canonical: BLOCKER, MAJOR, MINOR, NIT.

### Devcontainer (FR-4 inventory)

- **`.devcontainer/postCreate.sh`** (174 lines). `set -euo pipefail`. Installs **four** OSS-local MCP servers today (serena, actionlint-mcp, terraform-mcp, gitnexus — was 5, dropped to 4 when mcp-openapi-schema was removed). Idempotency via sentinel-file + binary-on-PATH check (the two-check pattern from ADR-0041 Decision item 3). FR-4's dry-run sits inside `install_gitnexus()` just before the `npm install -g` step (lines ~127-150).
- **`.devcontainer/versions.env`** holds the pin: `GITNEXUS_TAG=1.6.5`. Five pins active. Convention: one line per pin, full upstream rationale in adjacent comments.
- **`.devcontainer/lib/log-mcp-event.sh`** is the diagnostic-emission helper. Implements ADR-0037 event schema + ADR-0039 redaction-at-source, default-fail-closed. FR-4 should emit an `install_complete` (with `status:ok|failed`) — NOT a new event type (NFR-13 compatibility).
- **`.devcontainer/Dockerfile`** confirmed: no Dockerfile change required per ADR-0041's no-Dockerfile posture.

### CI/CD (FR-5 inventory)

- **`.github/workflows/`** does not exist. FR-5's workflow is the **first** in this project. There is no precedent for runner choice, SHA-pin, permissions, concurrency, path-filter, or claude-cli-install in this codebase. The KB defaults (security non-negotiables in KB-github-actions-platform/references/security.md) are the only inputs design-cicd has.

### Housekeeping artifacts (FR-7 inventory)

- **`Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`** is the target. Rows **B-1** (CI smoke) and **H-4** (GitNexus dry-run) **already carry the adoption parenthetical** inline (lines 56 and 141 respectively, marked `*(ADOPTED 2026-05-25 by pipeline-quickwins-hardening-r1 — see Issues/cross-artifact-divergence-detection-gap/proposal.md)*`). The Why-excluded / Re-examination-trigger / Forgetting-risk cells are also already updated. FR-7's substantive work appears to be already in place; design-claude-code / design-composer under U-7 confirms the marker text matches the convention exactly and decides packaging (in-archive vs separate housekeeping commit).
- **`Issues/cross-artifact-divergence-detection-gap/proposal.md`** — status is `adopted` (frontmatter line 5). Confirmed as the research plan asked.

## Dependency map

```
                     ┌─────────────────────────────────────────────────┐
                     │     recipe-feature-pipeline (parent SKILL.md)   │
                     │                  ADR-0044 dispatch nexus        │
                     └────────────────────────┬────────────────────────┘
                                              │
       ┌──────────────────────────────────────┼──────────────────────────────────────┐
       │                                      │                                      │
   ┌───▼────┐     ┌──────────────┐     ┌──────▼───────┐    ┌──────────┐     ┌────────▼────────┐
   │ shared │×19  │  review-     │×4   │  review-     │×4  │ exec-    │     │ exec-task-      │
   │  -doc- │     │ architecture │     │ cross-       │    │ phase-   │     │ quality-handler │
   │reviewer│     │  -auditor    │     │ artifact-aud │    │ quality- │     │   (FR-1?)       │
   └────┬───┘     └────────┬─────┘     └──────────────┘    │ reviewer │     └─────────────────┘
        │                  │                │              └──────────┘
        │                  ▼                ▼
        │           ┌──────────────┐ ┌────────────────┐
        │           │  arch-audit  │ │ cross-artifact │
        │           │  issues.json │ │  issues.json   │
        │           └───────┬──────┘ └──────┬─────────┘
        ▼                   │               │
   ┌──────────────┐         └─►finalize-reconciler◄─┘
   │ doc_type     │                  │
   │ verdicts at  │                  ▼
   │ 5 gates      │            dispatch.json
   └──────────────┘                  │
                                     ▼
                            re-author / re-dispatch

   ┌────────────────────┐  parity  ┌────────────────┐
   │  .mcp.json (live) │◄────────►│   ADR-0041     │
   │  6 servers        │   FR-3   │   7 rows       │  ← deprecation_finding
   └──────────┬─────────┘          └────────────────┘
              │
              │ probed by FR-5 (`claude mcp list`)
              ▼
   ┌────────────────────┐
   │ .github/workflows/ │  GREENFIELD
   │      (FR-5)        │
   └────────────────────┘

   ┌────────────────────┐
   │ postCreate.sh      │  FR-4 dry-run inserts here
   │  install_gitnexus()│  → reads versions.env GITNEXUS_TAG
   │                    │  → emits via log-mcp-event.sh (install_complete event)
   └────────────────────┘
```

## Blast radius summary per touch point

| Touch point | Risk | 1-hop dependents | Notes |
|---|---|---|---|
| shared-document-reviewer (FR-1) | MEDIUM | 2 (recipe-feature-pipeline at 5 points; packager at 1) | Bad shape change cascades, but FR-1 is shape-validating not shape-changing. |
| review-architecture-auditor (FR-1) | LOW | 2 (parent orchestrator; finalize-reconciler) | Single-stage; reconciler-driven downstream. |
| review-cross-artifact-auditor (FR-1) | MEDIUM | 2 (parent orchestrator; finalize-reconciler) | The TWO verdicts in the same payload (primary + convergence) need disambiguation. |
| execute-phase-quality-reviewer (FR-1) | LOW | 2 (parent orchestrator at T7; execute-finalize-reconciler) | Well-isolated via Contract 6 dispatch_directives. |
| recipe-feature-pipeline (FR-2) | HIGH | ~25 sub-agents | Single dispatch nexus. The self-check belongs here, but scope_class read site must be hoisted. Single-agent-fallback config surface must be defined. |
| auditing-mcp (FR-3) | LOW | 1 (Gate-6 hard gate per ADR-0043) | Additive new OP rule; no schema break. |
| postCreate.sh (FR-4) | MEDIUM | Every Codespace rebuild | False positive breaks bring-up for every contributor. PRD Kill-criterion covers. |
| .github/workflows/ (FR-5) | LOW for blast / MEDIUM for first-precedent | n/a (greenfield) | Workflow shape becomes the project's convention. |
| .mcp.json (FR-3 + FR-5 probed) | MEDIUM | Claude Code parser + 7 sub-agents with mcp__ allowlists | Read-only; risk is in misinterpretation (deprecation_finding). NFR-15: no allowlist change. |

The HIGH risk on `recipe-feature-pipeline` is structural (single point of dispatch) rather than indicative of poor design. The five mechanisms in aggregate touch this one file four times (FR-1 check site or hook attachment, FR-2 self-check, FR-3 audit dispatch reads, FR-7 metadata). design-claude-code should ensure the four touches compose cleanly rather than colliding.

## Conventions observed (must respect)

### Claude Code layer

- **Verdict emission:** always a single string field inside a structured JSON output object. Field name is consistently `verdict` or `status`. The enum values vary by agent and are listed component-by-component in the JSON artifact.
- **Findings:** always a JSON array adjacent to the verdict. The finding object shape (severity, file_path, message, rule/domain identifiers) varies by reviewer — design-claude-code's FR-1 validator must accommodate the variance or extract a common subset.
- **Severity taxonomy:** four canonical tokens — BLOCKER, MAJOR, MINOR, NIT/INFO. Mapping to verdicts is deterministic: any BLOCKER → fail/BLOCK/BLOCKER; any MAJOR (no BLOCKER) → conditional_pass / NEEDS_RECONCILIATION; only MINOR/INFO → pass. This mapping is the canonical "blocking-severity set" U-1 asks about; the canonical blocking-severity is `BLOCKER` (plus the auditor-family alias `blocker` lowercase used in `execute-task-quality-handler`'s findings).
- **ADR authoring:** ONLY design-composer authors ADRs per FR-5. All other agents may cite, not author.
- **Report-only vs enforcing:** auditing skills and reviewers are report-only. The "enforce vs instruct" choice for FR-1/FR-2 must add an enforcing layer ON TOP of these report-only contracts.
- **Frontmatter:** name, description, model, effort, tools, skills, memory. All required.
- **Logging:** TaskUpdate at start and end of sub-agent work (one line each). The parent skill writes checkpoint.json and state-transitions.log.

### auditing-mcp skill

- **Rule naming:** `OP-N` (integer). FR-3 is OP-11 by convention.
- **Script naming:** `audit_op<N>_<short-descriptor>.py`.
- **Script contract:** one positional argument (path-to-.mcp.json), JSON findings to stdout, exit 0/1/2 (no findings / BLOCKER finding / internal error).
- **Finding format:** `{rule, severity, server, field, message}`. FR-3 must include `{prescribed_form, live_form, diff_dimension}` to satisfy AC-FR-3-b.
- **Rationale placement:** each OP rule's rationale lives in `references/`. FR-3 should add a new section to `references/anti-patterns.md` or a dedicated reference file.

### Codespaces layer

- **Shell posture:** `set -euo pipefail` at the top of every script.
- **Sentinel naming:** two conventions coexist. ADR-0041 canonical: `<server>@<version>.installed` under `.claude/runtime/install-sentinels/`. Live in `postCreate.sh`: `.install-sentinel-<server>-<version>` directly under `.claude/runtime/`. FR-4 must NOT introduce a third convention.
- **Idempotency:** sentinel-presence AND binary-on-PATH (two-check pattern).
- **Event emission:** `log_mcp_event` helper writes one JSONL record per install/probe to `.claude/runtime/mcp-events.jsonl`. Event types per ADR-0037: `install_complete`, `readiness_probe`, `structured_failure`. **FR-4 must use one of these existing types — no new event type (NFR-13).**
- **Diagnostic format:** dual stream. Single-line `[postCreate] <message>` to stderr for operators, plus structured JSONL via `log_mcp_event` for machine readers. FR-6 actionable diagnostics for FR-4 should follow this pattern.

### CI/CD layer

- **GREENFIELD.** No existing convention. The KB security non-negotiables (SHA-pin third-party actions, least-privilege permissions, no untrusted input interpolation in `run:`, OIDC over long-lived keys, concurrency on deploy workflows) are design-cicd's baseline.

### Document layer

- **Deferral-register row update convention:** append `*(ADOPTED YYYY-MM-DD by <slug> — see <link>)*` inline in the Item-cell. Update Why-excluded → "Now adopted: <summary>". Update Re-examination-trigger → "Adopted by <slug>." Update Forgetting-risk → "Resolved by adoption." The TL;DR and counts are NOT incrementally updated row-by-row (snapshot doc, not a live ledger). **Rows B-1 and H-4 already conform to this convention** — FR-7 verifies and tightens, doesn't author.

## Known issues and recommended caution areas

1. **execute-orchestrator agent's advisor framing.** The file is documented as "advisor; non-invocable per ADR-0044" but still carries an invocable-shaped frontmatter block. If FR-2's self-check enumerates agents rather than invocable agents, it could stumble. Minor severity.
2. **Sentinel-naming inconsistency.** ADR-0041 canonical vs live postCreate.sh form (described above). Minor severity; FR-4 should adopt one of the two existing conventions or be sentinel-less.
3. **postCreate.sh server-count stale strings.** Lines 11 and 165 say "5 OSS-local servers" — should be 4 post-2026-05-24 removal. Minor severity; cosmetic; not a quick-wins-hardening concern.

## Open questions for human resolution

These bubble up to design-claude-code, design-codespaces, and design-cicd at per-layer Design time. They are also captured in the JSON artifact's `open_questions_for_human` field.

1. **FR-1 scope completeness.** Should `execute-task-quality-handler` be in FR-1 scope (strong sweep recommendation)? `finalize-deliverable-packager`? The PRD's named four are illustrative; the intent doc's binding framing is "any reviewer that emits a verdict+findings pair." design-claude-code's contract decision shapes the validator's reach.

2. **FR-3 deprecation handling.** ADR-0041 still lists mcp-openapi-schema as one of seven invocation rows; `.mcp.json` has six servers. AC-FR-3-c naturally reads as a day-one BLOCKER false-positive. Three options under U-3:
   - In-rule deprecation marker (preferred by CLAUDE.md framing; respects ADR-0005 append-only).
   - ADR amendment to drop the row (out-of-scope per carve-out).
   - Audit-script allowlist of known-deprecated row identifiers (least transparent).

3. **FR-2 self-check site and configuration surface.** The `scope_class` is currently read inside Stage 12 (line 350 of recipe-feature-pipeline SKILL.md); FR-2 needs it at the start of dispatch. The "single-agent fallback" is implicit in `execution_mode = "parent-driven-workaround"` and is not yet a named, inspectable config surface. design-claude-code under U-2 defines both.

4. **FR-4 sentinel posture.** With two existing sentinel conventions (ADR-0041 canonical vs live script), FR-4 likely runs without a sentinel (every rebuild) — but design-codespaces under U-4 confirms.

5. **FR-7 marker tightening.** Rows B-1 and H-4 already carry the adoption parenthetical. design-claude-code / design-composer under U-7 confirms exact-text match against the convention and decides packaging.

## Pipeline-relevant cross-references (for design-composer)

- **CLAUDE.md** explicitly acknowledges (line 9) that `mcp-openapi-schema` was removed 2026-05-24 and that `KB-mcp-platform` still references it as one of seven — "a stale-doc issue, not an active server." The project's posture on stale ADR/KB references is therefore established: removed-from-active-config can coexist with persistent stale references in design-time docs. FR-3's parity rule should respect this established posture (in-rule recognition, not forced ADR cleanup).
- **NFR-13 (MCP event surface compatibility):** the existing event types per ADR-0037 are `install_complete`, `readiness_probe`, `structured_failure`. FR-3/4/5 diagnostics must use one of these three or emit no event at all. The live evidence (postCreate.sh emits install_complete; postStart.sh emits readiness_probe + structured_failure) confirms the schema is stable.
- **NFR-15 (allowlist preservation):** seven sub-agents currently carry `mcp__*` allowlist entries per ADR-0040 (review-architecture-auditor, discovery-external-researcher, discovery-codebase-researcher, design-iac, design-codespaces, design-claude-code, design-cicd). This feature's mechanisms do not add new MCP servers or change which sub-agents need MCP access; NFR-15 is satisfied by construction.

---

End of report. JSON-shaped counterpart at `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json` (schema v1.1.0 per ADR-0018 + ADR-0038).
