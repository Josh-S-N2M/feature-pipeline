---
id: RP-issue-capture-mechanism-r1
doc_type: research-plan
version: 1.0.0
status: draft
feature_slug: issue-capture-mechanism-r1
scope_class: FULL
derived_from: working/feature/issue-capture-mechanism-r1/prd-v2.md
generated: 2026-05-23T18:35:00Z
generated_by: discovery-plan-author
companion_artifacts:
  - Issues/issue-capture-mechanism/proposal.md
  - /home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md
  - working/feature/issue-capture-mechanism-r1/intent-clarification.md
---

# Research Plan: Issue-Capture Mechanism (Outside-the-Pipeline)

## Contents

- [x] Feature reference
- [x] KB inventory and applicability analysis
- [x] ADR inventory and applicability analysis
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Risks and open questions for Discovery / Design
- [x] Exit criteria
- [x] Estimated effort

---

## Feature reference

- **Feature slug**: `issue-capture-mechanism-r1`
- **PRD path**: `working/feature/issue-capture-mechanism-r1/prd-v2.md`
- **PRD version**: 1.1.0
- **PRD gate state**: Approved at PRD Approval Gate (Gate 2), 2026-05-23T17:05:00Z
- **Scope class**: FULL (per ADR-0023; multi-primitive subsystem)
- **Layer scope (from PRD §Overview/Layer Scope)**: Claude Code (primary) + Backend tooling (secondary, validator extension). Layers 2 / 4 / 5 / 6 / 7 / 8 / 9 are OUT.
- **Companion artifacts treated as authoritative prior context**:
  - `Issues/issue-capture-mechanism/proposal.md` — the formal seed proposal
  - `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md` — ~400-line decided-design plan from prior planning-mode session, including findings from external research already performed (Dual-Track Agile, Spotify decision tree, RFC-to-spec discipline)
  - `working/feature/issue-capture-mechanism-r1/intent-clarification.md` — Gate 1 approved 2026-05-23T16:51:00Z
- **Inherited ADRs that CONSTRAIN this run** (full applicability analysis below): ADR-0008, ADR-0011, ADR-0017, ADR-0019, ADR-0020, ADR-0021, ADR-0023, ADR-0032, ADR-0036.
- **Applicable KBs in scope** (full applicability analysis below): `KB-cc-design`, `KB-cc-platform`, `KB-documentation-criteria`, `KB-review-disciplines`, `KB-codebase-research`, `KB-task-decomposition`, `KB-general-coding-principles`, plus the `auditing-*` audit family (auditing-hooks, auditing-skills, auditing-subagents, auditing-settings, auditing-shared, auditing-cc-configs, auditing-context-files) as cross-cutting reviewers — invoked at pre-merge, but their reference material informs design-time decisions on hook/skill/agent/settings authoring.

---

## KB inventory and applicability analysis

Per the KB-and-ADR-first discipline, every KB available in the project is classified APPLICABLE (will be loaded by downstream consumers) or NOT APPLICABLE (out of this feature's layer scope or domain). The PRD's Layer Scope (CC + Backend-tooling only) drives most NOT-APPLICABLE classifications.

### APPLICABLE

| KB | Why applicable | Anticipated downstream consumer(s) |
|---|---|---|
| `KB-cc-design` | Primary KB for Layer 1. Governs skill structure (`disable-model-invocation`), agent body shape, slash-command authoring, hook design, settings-edit discipline. The PRD's three-layer enforcement (FR-3) and skill-localised-knowledge constraint (Won't-Have item) both anchor in this KB's principles. | `design-claude-code` (Stage 5 — primary); `synth` |
| `KB-cc-platform` | Authoritative on the Claude Code platform contract: `PreToolUse` hook semantics, `permissionDecision: "ask"`, `subagent_type` discriminator, `disable-model-invocation` flag, `AskUserQuestion` tool, `Task` tool spawn shape. Six of the seven `references/*.md` files mention these primitives. Validates Assumptions 2 and 6 of the PRD. | `design-claude-code`; `discovery-codebase-researcher` (for verifying current Claude Code version behavior) |
| `KB-documentation-criteria` | Owns the template canon. Three new templates and one new spec land under this KB. The new `KB-issue-capture` skill's discipline must NOT duplicate template structure (FR-6 / Won't-Have boundary). Frontmatter and supersession discipline inherited from `shared-conventions.md`. | `design-claude-code`; `design-composer` (ADR slate); `intake-prd-author` (already consumed for v2); `test-acceptance-author` |
| `KB-review-disciplines` | Two roles. (a) Authority on `issues-ledger.json` (intra-pipeline 4-state vocabulary per ADR-0008) — the new 5-state `Issues/` vocabulary is explicitly the *parallel-but-distinct* lifecycle (PRD §Product Policy Decisions). (b) `shared-document-reviewer` applies Gate 0/1 to the three new templates. The new templates must satisfy Gate 0 structural checks. | `design-claude-code`; `shared-document-reviewer` (against new templates); `design-composer` |
| `KB-codebase-research` | Defines `codebase-analysis.json` schema (per ADR-0018) and codebase-research conventions. Required reading for `discovery-codebase-researcher`. | `discovery-codebase-researcher` |
| `KB-task-decomposition` | Required for Plan authoring (Stage 7). The plan must decompose into phases that respect the FULL-class scope multi-primitive surface. | `plan-author` |
| `KB-general-coding-principles` | Cross-cutting design-time principles. Python validator extension (FR-7) must respect general coding principles; bash hook script (FR-3) likewise. | `design-claude-code`; `design-backend` (validator extension); cc-critique |

### NOT APPLICABLE (out-of-layer-scope or out-of-domain)

| KB | Why not applicable |
|---|---|
| `KB-frontend-design` | Frontend layer (Layer 2) is OUT of scope per PRD Layer Scope row 2. No UI surface beyond the slash command, which is itself a CC-layer artifact. |
| `KB-api-design` | API layer (Layer 4) is OUT. No HTTP/GraphQL/RPC contract change. |
| `KB-query-design` | Query/Data-Access layer (Layer 5) is OUT. No ORM, repository, or query layer. |
| `KB-database-design` | Database layer (Layer 6) is OUT. The `Issues/` directory and its frontmatter are explicitly NOT a database (PRD §Overview row 6). |
| `KB-github-actions-design`, `KB-github-actions-platform` | CI/CD layer (Layer 7) is OUT. No workflow / job / action change. PRD §Layer Scope row 7 leaves an "if Discovery surfaces a CI-invocation benefit" caveat, but no PRD requirement currently calls for it. |
| `KB-iac-design` | IaC layer (Layer 8) is OUT. No Terraform/Pulumi/CDK/CloudFormation. |
| `KB-codespaces-design`, `KB-codespaces-platform` | Dev-environment layer (Layer 9) is OUT. No devcontainer/prebuild/port/lifecycle changes. |
| `KB-storybook-platform` | Storybook is a frontend artifact; Layer 2 OUT. |
| `KB-component-architecture-design` | Frontend-component layer; Layer 2 OUT. |
| `KB-design-system-design` | Frontend design system; Layer 2 OUT. |
| `KB-ux-design` | Frontend UX layer; Layer 2 OUT. |
| `KB-visual-design` | Frontend visual layer; Layer 2 OUT. |

12 KBs NOT APPLICABLE, 7 KBs APPLICABLE. This 12-of-22-out ratio is consistent with the PRD's intentional layer narrowness (7 of 9 engineering layers OUT).

### Cross-cutting audit skills (load at pre-merge, but inform design)

The `auditing-*` family is loaded by `cc-critique` and pre-merge auditors, not by per-layer designers. Listed here because PRD U-5 explicitly anticipates pre-merge audit findings against the new agent/skills/hook/settings additions:

- `auditing-hooks` — applies to the new `.claude/hooks/intercept-issue-capture-agent.sh` (PRD FR-3). Has rich coverage of `PreToolUse`, `subagent_type` discrimination, fail-open patterns, and security pitfalls. **Strongly applicable** to Design.
- `auditing-skills` — applies to the new `KB-issue-capture` and `capture-issue` skills. Covers `disable-model-invocation` frontmatter (FR-3 Layer 1 anchor). **Strongly applicable** to Design.
- `auditing-subagents` — applies to the new `issue-capture-author` agent.
- `auditing-settings` — applies to the additive `.claude/settings.json` patch (FR-3, FR-15).
- `auditing-shared` — owns `validate_pipeline_frontmatter.py` (FR-7 extension target). The new doc_types + 5-state vocabulary land here.
- `auditing-cc-configs`, `auditing-context-files` — likely incidental coverage of repo-root config changes; secondary applicability.

---

## ADR inventory and applicability analysis

Every ADR present at the repo's authoritative `adrs/` path is classified. ADR-0008 lives at `adrs-migrated/ADR-0008-issue-ledger-scope.md` (a known placement-drift target per `Issues/adr-placement-rootcause/`-pending-migration analysis); for this run, ADR-0008 is treated as authoritative.

### CONSTRAIN this run

| ADR | Title (short) | Constraint imposed on this feature |
|---|---|---|
| ADR-0008 | `issues-ledger.json` scope | Defines the intra-pipeline 4-state issue ledger. This feature's 5-state `Issues/` vocabulary parallels but is explicitly distinct (PRD §Product Policy Decisions, FR-13). The two systems never share IDs. **Constraint**: any design that conflates the two is disallowed. **Verify**: locate the canonical schema (in `adrs-migrated/` per drift) and confirm the 4-state vocabulary text. |
| ADR-0011 | KB-documentation-criteria canonical skill | Templates land under `KB-documentation-criteria/references/templates/`. The three new issue-doctype templates (FR-6) MUST follow the same structure and discipline. |
| ADR-0017 | shared-document-reviewer integration (5 invocations) | The 5 fixed reviewer invocation points are unchanged. The new templates inherit Gate 0/1 review at the moment they are authored or when files using them are reviewed. **Constraint**: no new reviewer invocation points are created by this feature. |
| ADR-0019 | Naming convention | The new agent, skills, KB, hook script, templates, and spec files MUST follow the project naming convention. **Constraint**: agent `issue-capture-author`, skill `capture-issue`, KB `KB-issue-capture`, hook script under `.claude/hooks/` follow kebab-case and project-specific prefixes. |
| ADR-0020 | KB structure | KBs use `SKILL.md` + `references/*.md` structure. The new `KB-issue-capture` must conform. Triggering discipline lives in this KB; structural templates live in `KB-documentation-criteria` (PRD FR-6 split). |
| ADR-0021 | Discovery phase architecture (KB-and-ADR-first) | This Research Plan IS the artifact ADR-0021 mandates. Discovery research is conditional on documented KB-gap analysis. External topic budget = 6 default. |
| ADR-0023 | Scope class FULL / MINOR / PATCH | This feature is FULL-class (PRD §Product Policy Decisions row 1). Full pipeline applies including all 6 mandatory gates and all per-layer Design subsections (with N/A for OUT layers). |
| ADR-0032 | Conventions canonicalization (including `intent_user_token` chain) | Frontmatter discipline canonicalized here (e.g., `intent_user_token`, `companion_artifacts`, `generated`/`generated_by`). The new templates' frontmatter MUST inherit from `shared-conventions.md`. **Constraint**: validator extension (FR-7) must preserve all canonicalized fields. |
| ADR-0036 | Single-location ADR placement | This run's 7 anticipated ADRs (PRD U-10) MUST land at `adrs/` (not `adrs-migrated/` and not under `working/feature/<slug>/adrs/`). This run is NOT the right venue to author a finding about ADR-0036 drift; PRD U-10 is the slate plan. **Cross-reference**: `Issues/adr-placement-rootcause/analysis.md` already captures the drift; not in this run's scope. |

### Likely-NOT-applicable but worth surfacing

| ADR | Why likely not applicable |
|---|---|
| ADR-0012 | PRD-stage discipline; consumed already by `intake-prd-author` at Stage 2. Not a Discovery constraint. |
| ADR-0013 | Blueprint-template adoption; consumed at Stage 5 (design-composer). Not a Discovery constraint. |
| ADR-0014 | ADR-template adoption-and-migration; consumed at Stage 5 when the 7-ADR slate is authored. Not a Discovery constraint. |
| ADR-0015 | EARS acceptance-criteria; consumed by `intake-prd-author` (already) and `test-acceptance-author` (later). Not a Discovery constraint. |
| ADR-0016 | Per-layer fan-out / composer fan-in; consumed at Stage 5. Not a Discovery constraint. |
| ADR-0018 | `codebase-analysis.json` schema; consumed by `discovery-codebase-researcher`. Informs the Codebase Research Scope section below, but does not change feature design. |
| ADR-0022 | Sub-agent reasoning configuration; the new `issue-capture-author` follows the existing reasoning-config defaults. No deviation required. |
| ADR-0024 | Frontend-knowledge-corpus structure. **OUT of layer scope.** A known drift target per `Issues/adr-placement-rootcause/analysis.md`, but this feature does NOT touch the frontend KB structure. Flagged as in-context but out-of-scope. |
| ADR-0025 | Pipeline-machinery defects (integration-test 2); historical. |
| ADR-0026 | Audit-machinery fixes v4.4.1; parallel work line on the `auditing-*` skills. This feature's auditing-shared/scripts/ extension (FR-7) is additive and does not contradict ADR-0026. **Verify**: confirm the validator's current invocation contract has not shifted since ADR-0026. |
| ADR-0027 | Pipeline-skill design gap / deliverable-archive; not a constraint on issue-capture. |
| ADR-0028 | Skill-design fixes v4.5.0; historical. |
| ADR-0029 | No-silent-scope-changes principle; a meta-principle. The PRD's explicit `Won't-Have` list and Layer Scope OUT-rows already implement this. |
| ADR-0030 | Pedagogical marker justification; consumed at design-time if any pedagogical marker is added. Probably not relevant to the new templates (they are structural, not pedagogical). |
| ADR-0031 | `auditing-shared` skill module; this run extends `auditing-shared/scripts/` (FR-7). **Verify**: confirm ADR-0031's binding convention is honored (cross-references ADR-0035). |
| ADR-0033 | ADR-0029 execution extension; meta-principle. |
| ADR-0034 | PRD mis-credit cleanup; historical. |
| ADR-0035 | `auditing-shared` skill binding convention; FR-7 must honor this. **Verify-during-codebase-research**: confirm the validator script's location and binding to `auditing-shared` is unchanged. |

---

## Information needs inventory

Read top-down by the human at the Research Plan Approval Gate. Each row maps to a downstream stage's needed fact.

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-001 | The Claude Code `PreToolUse` hook contract: stdin JSON shape, expected stdout JSON shape (`permissionDecision`, `message`), exit-code semantics, and how `subagent_type` is exposed when hooking the `Task` tool. | `design-claude-code` (resolve PRD U-1); `synth` | `covered-by-KB:KB-cc-platform:references/extensions.md` + `covered-by-KB:auditing-hooks:references/hook-spec.md` |
| IN-002 | The `disable-model-invocation: true` frontmatter flag semantics: what blocks invocation, what permits invocation, edge cases (description-match, slash-command path). | `design-claude-code`; `design-composer` (ADR for three-layer enforcement) | `covered-by-KB:KB-cc-design:references/principles.md` + `covered-by-KB:KB-cc-platform:references/extensions.md` |
| IN-003 | The `AskUserQuestion` tool contract: prompt shape, options shape, single-question-per-spawn discipline, blocking semantics relative to subsequent `Write` calls. | `design-claude-code` (resolve PRD U-2 prompt-template text) | `covered-by-KB:KB-cc-platform:references/extensions.md` |
| IN-004 | The `Task` tool spawn shape: `subagent_type` field, parameter passing, how an agent body inherits `$ARGUMENTS`. | `design-claude-code`; `design-composer` | `covered-by-KB:KB-cc-platform:references/extensions.md` |
| IN-005 | Patterns and anti-patterns for additive `.claude/settings.json` edits: `permissions.allow` shape, `hooks.PreToolUse` block shape, how to add without disturbing existing entries. | `design-claude-code` (FR-3, FR-15) | `covered-by-KB:KB-cc-design:references/patterns-and-anti-patterns.md` + `covered-by-KB:auditing-settings:SKILL.md` |
| IN-006 | Hook script security and fail-open patterns: bash hardening, malformed-stdin tolerance, stderr discipline, what NOT to do (CVE class context). | `design-claude-code` (FR-3, NFR-2); cc-critique pre-merge | `covered-by-KB:auditing-hooks:references/security-checklist.md` + `covered-by-KB:auditing-hooks:references/anti-patterns.md` + `covered-by-KB:auditing-hooks:references/common-failures.md` |
| IN-007 | The current shape of `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py`: existing doc_type enum, status vocabulary, per-state companion-field rules, test surface, CLI entry point. | `design-backend` (FR-7); `discovery-codebase-researcher` | `codebase-topic` |
| IN-008 | The current shape of `.claude/agents/intake-intent-clarifier.md`: structure, where the small `Proposal-as-prior-context` sub-section would land (FR-11), `--raw-request` handling. | `design-claude-code` (FR-11) | `codebase-topic` |
| IN-009 | The current shape of `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md`: where the proposal-seed `Source` guidance lands (FR-12). | `design-claude-code` (FR-12) | `codebase-topic` |
| IN-010 | The current shape of `.claude/skills/recipe-feature-pipeline/SKILL.md`: where the one-bullet proposal-seed invocation-pattern documentation lands (FR-12). | `design-claude-code` (FR-12) | `codebase-topic` |
| IN-011 | The current shape of the four existing flat-format `Issues/*.md` files: their frontmatter, structure, doctype shape. The templates (FR-6) are *derived* from these as empirical precedent. | `design-claude-code` (FR-6, FR-8); design-time reverse-engineering of three worked examples (PRD U-3) | `codebase-topic` |
| IN-012 | The current shape of `.claude/skills/KB-review-disciplines/references/issue-lifecycle.md`: the intra-pipeline 4-state vocabulary against which the new 5-state must remain distinct (PRD §Product Policy Decisions). | `design-claude-code`; `design-backend` (FR-7 vocabulary); `design-composer` (ADR for 5-state) | `codebase-topic` |
| IN-013 | The current shape of `.claude/skills/KB-documentation-criteria/references/shared-conventions.md`: frontmatter inheritance source for the three new templates. | `design-claude-code` (FR-6) | `codebase-topic` |
| IN-014 | Existing non-pipeline agent patterns: `cc-critique.md`, `shared-document-reviewer.md` — body shape, tool restrictions, frontmatter, prior-context handling. The new `issue-capture-author` should structurally parallel these. | `design-claude-code` | `codebase-topic` |
| IN-015 | Existing skills using `disable-model-invocation: true`: which exist today, what their frontmatter looks like, what entry-point patterns they use. | `design-claude-code` (FR-3 Layer 1 anchor) | `codebase-topic` |
| IN-016 | Pipeline-isolation verification: how to grep for `KB-issue-capture` / `issue-capture-author` invocation across `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` (PRD FR-13 / AC-FR-13-a / AC-FR-13-b). Confirm current count is zero (must remain zero post-merge). | `design-claude-code`; `test-acceptance-author`; `review-cross-artifact-auditor` | `codebase-topic` |
| IN-017 | Blast radius of editing `validate_pipeline_frontmatter.py`: which callers depend on the script, which CI / makefile / test surfaces invoke it, what test fixtures exist. | `design-backend`; `plan-author` | `codebase-topic` |
| IN-018 | Blast radius of editing `intake-intent-clarifier.md`: pipeline runs that read its body, downstream agents that consume its outputs (`intent-clarification.md`). | `design-claude-code`; `plan-author` | `codebase-topic` |
| IN-019 | Blast radius of editing `recipe-feature-pipeline/SKILL.md`: orchestrator invocation sites, slash commands, anything that may parse its body. | `design-claude-code`; `plan-author` | `codebase-topic` |
| IN-020 | Sibling-script patterns in `auditing-shared/scripts/`: `check_pipeline_discipline.py`, `detect_stubs.py`, `log_state_transition.py` — how they handle CLI args, fail modes, output shapes. The validator extension should match their idiom. | `design-backend` | `codebase-topic` |
| IN-021 | Confirmation that the issue-doctype `proposes_future_feature:` slug field has no existing precedent in any KB or ADR (PRD U-6). | `design-backend` (FR-7, FR-11 / FR-12 handoff design) | `codebase-topic` |
| IN-022 | The current shape of `.claude/SETTINGS-NOTES.md` and `.claude/settings.json`: existing entries, append-target landing pattern (FR-15), permission entry shape (FR-3). | `design-claude-code` | `codebase-topic` |
| IN-023 | What scope class `FULL` formally entails for downstream stages — Plan phasing, mandatory gate count, acceptance-test coverage breadth. | `plan-author`; `test-acceptance-author` | `covered-by-ADR:ADR-0023` |
| IN-024 | How `shared-document-reviewer`'s Gate 0 will detect the three new templates and apply structural checks (FR-6 / AC-FR-6-a). | `design-claude-code`; `test-acceptance-author` | `covered-by-KB:KB-review-disciplines:references/gate-0-1-procedure.md` |
| IN-025 | EARS acceptance-criteria authoring discipline for the FR-1 through FR-15 acceptance criteria (already in PRD). | `test-acceptance-author` | `covered-by-KB:KB-documentation-criteria:references/disciplines/ears-acceptance-criteria.md` |
| IN-026 | Frontmatter `id:` / `version:` / `status:` / `generated:` / `generated_by:` shape for the three new templates and the new spec. | `design-claude-code` | `covered-by-KB:KB-documentation-criteria:references/shared-conventions.md` |
| IN-027 | The `intent_user_token` chain discipline (how the new templates' frontmatter inherits the intent token from the seeding flow). | `design-claude-code`; `design-backend` (validator may need to recognize this for issue-* doc_types) | `covered-by-ADR:ADR-0032` |
| IN-028 | The 9-layer engineering taxonomy used by the PRD/Blueprint's Layer Scope. | `design-composer`; per-layer designers | `covered-by-KB:KB-documentation-criteria:references/layer-taxonomy.md` |
| IN-029 | Plan-authoring discipline: phase-based decomposition, L1/L2/L3 verification, FULL-scope class implications. | `plan-author` | `covered-by-KB:KB-documentation-criteria:references/disciplines/plan-authoring.md` + `covered-by-KB:KB-task-decomposition:SKILL.md` |
| IN-030 | Design composition discipline: integration, arbitration, Fact Disposition Table, 7-ADR slate authoring rules (PRD U-10). | `design-composer` | `covered-by-KB:KB-documentation-criteria:references/disciplines/design-composition.md` |
| IN-031 | Whether community precedent exists for evolving markdown frontmatter `doc_type` enums backward-compatibly (FR-7 / NFR-8 zero-false-positive constraint). | `design-backend`; cc-critique | `designer-general-knowledge` — backward-compatible additive enum extension in a Python validator is well-trodden general software-engineering practice (add a new enum value, no removal, regression-test against pre-existing corpus). The downstream `design-backend` documents the rationale in its design section per the discipline. |
| IN-032 | Dual-Track Agile, Spotify decision-tree, RFC-to-spec discipline — frameworks justifying the proposal-as-prior-context handoff pattern. | `design-composer` (rationale citation in the handoff ADR) | `covered-by-companion-artifact:/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md` — external research already performed in prior planning-mode session; citations in the companion plan. DO NOT re-research. |

Disposition tally: 11 `covered-by-KB`, 3 `covered-by-ADR`, 1 `covered-by-companion-artifact` (planning-mode prior context), 16 `codebase-topic`, 1 `designer-general-knowledge`, 0 `external-research-topic` proposed by default. See External Research Topics section below for candidate proposals.

---

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The researcher runs once and produces `codebase-analysis.json` against the schema defined by ADR-0018 / KB-codebase-research.

The Codebase Research Scope is **broad** because the feature is multi-primitive and touches 16 distinct codebase facts. The depth on any single touch point is moderate (verification of current shape, not learning of new patterns).

### Touch points (with rationale)

The researcher uses these as starting points for graph traversal. Touch points are grouped by FR they support.

**Group A — Existing artifacts the feature edits or extends:**

- `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` — FR-7 extension target. Read the current doc_type enum, status vocabulary, per-state companion-field rules, CLI entry, test surface. Identify regression-test fixtures.
- `.claude/skills/auditing-shared/scripts/check_pipeline_discipline.py` — sibling; idiom reference (IN-020).
- `.claude/skills/auditing-shared/scripts/detect_stubs.py` — sibling; idiom reference.
- `.claude/skills/auditing-shared/scripts/log_state_transition.py` — sibling; idiom reference.
- `.claude/agents/intake-intent-clarifier.md` — FR-11 small-edit target. Identify the ≈15-line "Proposal-as-prior-context" insertion locus.
- `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md` — FR-12 small-edit target (≈5 lines).
- `.claude/skills/recipe-feature-pipeline/SKILL.md` — FR-12 small-edit target (one bullet).
- `.claude/skills/KB-documentation-criteria/SKILL.md` — FR-14 additive index update target.
- `.claude/SETTINGS-NOTES.md` — FR-15 append target.
- `.claude/settings.json` — FR-3 / FR-15 additive permission entry + `hooks.PreToolUse` block target.

**Group B — Existing artifacts that define structural / convention precedent:**

- `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` — register-doctype empirical precedent (IN-011).
- `Issues/analysis-per-agent-design-evaluation-gap.md` — analysis-doctype empirical precedent.
- `Issues/analysis-adr-placement-rootcause.md` — analysis-doctype empirical precedent.
- `Issues/proposal-auditing-family-graduation-review.md` — proposal-doctype empirical precedent.
- `Issues/issue-capture-mechanism/proposal.md` — already-canonical proposal precedent (this run's seed).
- `.claude/skills/KB-documentation-criteria/references/templates/*.md` — all existing templates; structural parallel reference for the three new ones.
- `.claude/skills/KB-documentation-criteria/references/shared-conventions.md` — frontmatter inheritance source (IN-013, IN-026).
- `.claude/skills/KB-review-disciplines/references/issue-lifecycle.md` — intra-pipeline 4-state vocabulary; confirm verbatim text (IN-012).
- `.claude/agents/cc-critique.md` — non-pipeline agent shape reference (IN-014).
- `.claude/agents/shared-document-reviewer.md` — non-pipeline agent shape reference; also defines the Gate 0/1 invocations.

**Group C — Platform / configuration references:**

- `.claude/skills/KB-cc-platform/references/extensions.md` — hook contract verification (IN-001).
- `.claude/skills/KB-cc-platform/references/architecture.md` — `Task` tool, agent spawn semantics.
- `.claude/skills/KB-cc-platform/references/configuration.md` — `settings.json` contract.
- `.claude/skills/KB-cc-design/references/principles.md` — Principles 1, 3, 5, 6, 8, 9 (FR-3 anchors; PRD §Constraints).
- `.claude/skills/KB-cc-design/references/patterns-and-anti-patterns.md` — additive-settings-edit patterns (IN-005).
- `.claude/skills/auditing-hooks/references/hook-spec.md`, `security-checklist.md`, `anti-patterns.md`, `common-failures.md`, `examples/good-hook-annotated.md`, `examples/bad-hook-annotated.md` — comprehensive hook design + security reference (IN-006).
- `.claude/skills/auditing-skills/references/frontmatter-spec.md` — `disable-model-invocation` authority (IN-002, IN-015).

**Group D — Pipeline-isolation verification surface (FR-13 / AC-FR-13-a / AC-FR-13-b):**

- All files matching `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` — confirm that `KB-issue-capture` and `issue-capture-author` references are currently absent. Establishes the zero-baseline for the structural invariant.

**Group E — Out-of-scope but contextually adjacent (verify only, no edits):**

- `adrs-migrated/ADR-0008-issue-ledger-scope.md` — ADR-0008 canonical text; confirm 4-state intra-pipeline vocabulary verbatim (IN-012 cross-reference, PRD §Product Policy Decisions row 2).
- `Issues/adr-placement-rootcause/`-equivalent or `Issues/analysis-adr-placement-rootcause.md` — context only; this run does NOT author findings here.

### Blast-radius questions

Per ADR-0018, the researcher records `blast_radius` with `hop_tier_distribution`. For this feature, the relevant questions are:

1. **For `validate_pipeline_frontmatter.py`** (the most blast-radius-sensitive touch point):
   - Which CI workflows, makefile targets, pre-commit hooks, or pipeline sub-agents invoke this script?
   - Which test fixtures exercise existing doc_types? (FR-7's backward-compatibility requirement depends on knowing the existing coverage surface.)
   - 1-hop: direct callers. 3-hop: callers-of-callers.
2. **For `intake-intent-clarifier.md`**:
   - Which pipeline sub-agents downstream consume `intent-clarification.md` (its output)? Answer informs whether FR-11's small edit can propagate any unintended signal.
   - 1-hop: every Stage-2-or-later pipeline sub-agent that reads `intent-clarification.md`.
3. **For `.claude/settings.json`** (FR-3, FR-15):
   - Is there any tooling (CI, devcontainer prebuild, audit script) that parses settings.json's structure? Additive edits should not perturb such parsers.
   - 1-hop: `auditing-settings` script callers.
4. **For `recipe-feature-pipeline/SKILL.md`** (FR-12):
   - Is the SKILL.md body parsed by any orchestrator code (e.g., for argument-shape introspection)? Or is it purely human-readable?
   - 1-hop: orchestrator invocation sites + slash-command surfaces.
5. **For the three new templates and the new `KB-issue-capture` skill**:
   - These are new artifacts; blast radius is zero at creation. But: does any auditor script enumerate all skill SKILL.md files (e.g., for description-routing checks)? If so, the new skill's `disable-model-invocation: true` posture must register cleanly.

### Convention discovery (per in-scope layer)

**Layer 1 (Claude Code):**

- File-naming: agent `<role>-<purpose>.md`, skill `<verb>-<noun>` or `KB-<topic>`, hook script `<verb>-<noun>.sh`, template `<doctype>-template.md`. Verify against existing artifacts.
- Frontmatter shape: confirm `shared-conventions.md` inheritance; note `intent_user_token` chain per ADR-0032.
- Agent body shape: front-loaded discipline statements, tool-restriction lists, prior-context handling. Mirror `cc-critique` / `shared-document-reviewer`.
- Skill body shape: SKILL.md + `references/*.md` per ADR-0020. The new `KB-issue-capture` must conform.
- Hook discipline: bash-or-python; explicit shebang; explicit fail-open posture; stderr logging idiom. Per `auditing-hooks/references/`.
- Slash-command shape: how `$ARGUMENTS` flows; how the slash-command spawns an agent via `Task`. (The `capture-issue` skill is the slash-command surface per the proposal.)
- `disable-model-invocation: true` frontmatter: confirm exact field name, position, and known auditor checks against it.

**Layer 3 (Backend, validator extension):**

- Python module conventions in `.claude/skills/auditing-shared/scripts/`: imports, CLI entry (argparse vs. typer vs. plain `sys.argv`), output format (JSON to stdout? findings list?), test fixture layout.
- Test framework: pytest? unittest? Where are existing fixtures kept?

### Specific queries (optional)

Cypher / grep targets the researcher should run:

1. `grep -r "KB-issue-capture" .claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` — confirm zero matches (FR-13 pre-condition / AC-FR-13-a baseline).
2. `grep -r "issue-capture-author" .claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` — confirm zero matches (AC-FR-13-b baseline).
3. `grep -r "disable-model-invocation: true" .claude/skills/*/SKILL.md` — enumerate existing precedent for the flag (IN-015).
4. `grep -r "doc_type:" .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` — locate the current enum (IN-007).
5. `grep -r "status:" .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` — locate the current status vocabulary (IN-007).
6. Cypher (GitNexus): `MATCH (caller)-[:CALLS|IMPORTS*1..3]->(target {path: ".claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py"}) RETURN caller, length(path)` — validator blast radius.
7. Cypher (GitNexus): `MATCH (consumer)-[:READS*1..3]->(out {path: "intent-clarification.md"}) RETURN consumer` — intent-clarification blast radius (approximate; actual schema dependent on GitNexus's relationship inventory).

### Anti-pattern detection

- Confirm zero references to `KB-issue-capture` and `issue-capture-author` in pipeline-agent files (queries 1, 2 above).
- Confirm no existing `Issues/<topic>/` folder structure exists yet (the per-folder model is novel; current state is four flat files + the one `Issues/issue-capture-mechanism/` folder this PRD's proposal seeded).
- Confirm no existing slash-command at `/capture-issue` (we are creating it).

---

## External research topics

Per ADR-0021, external research is **conditional on a documented KB gap**. The KB-and-ADR-first analysis above resolved 30 of 32 information needs without external research. The remaining 2 (`designer-general-knowledge` IN-031, `covered-by-companion-artifact` IN-032) explicitly do NOT need external research.

### Three candidate topics considered and rejected

Per the orchestrator's pre-task brief, three candidate external topics were considered. All three were rejected by KB-gap analysis. Documented here for the Research Plan Approval Gate's audit trail.

**Candidate 1 (REJECTED): PreToolUse hook security patterns / CVE-2025-59536-class context**

- **Research question (hypothetical)**: What are current public-guidance security patterns for safe `PreToolUse` shell-hook authoring beyond what `auditing-hooks` already encodes?
- **KB-gap analysis**: `auditing-hooks` already provides comprehensive coverage via `security-checklist.md`, `anti-patterns.md`, `common-failures.md`, `examples/good-hook-annotated.md`, and `examples/bad-hook-annotated.md`. The skill explicitly enumerates the threat model that includes the CVE class. The new hook is fail-open with stderr log (NFR-2); is defense-in-depth one of three layers, not the only layer; reads stdin JSON (not user-controlled paths); and emits stdout JSON. The risk surface is **narrow** relative to the rich coverage already in the KB.
- **Conclusion**: NO GAP. The `auditing-hooks` KB plus cc-critique pre-merge findings (PRD U-5) cover this completely. Authorizing external research would duplicate existing KB content.

**Candidate 2 (REJECTED): Slash-command vs skill-with-`disable-model-invocation` as user-invocable entry point**

- **Research question (hypothetical)**: Is there fresh `KB-cc-design` guidance beyond what we already have on choosing between a slash-command and a `disable-model-invocation` skill as the user-facing entry point?
- **KB-gap analysis**: The PRD already prescribes both — the `capture-issue` skill is the slash-command surface AND `KB-issue-capture` carries `disable-model-invocation: true`. The two are not in competition; they cooperate (slash-command is the user-facing route, `disable-model-invocation` blocks the model-auto-load route). `KB-cc-design/references/principles.md` and `KB-cc-platform/references/extensions.md` together cover both primitives. The PRD's three-layer enforcement (FR-3) is the user-confirmed primitive choice (PRD §FR-3 user-confirmed-primitives footnote); the design has already been settled at Intent-Clarification Gate 1.
- **Conclusion**: NO GAP. The KB pair covers both primitives. The PRD's user-confirmation closes the design choice.

**Candidate 3 (REJECTED): Markdown frontmatter validator extension patterns — backward-compatible enum evolution**

- **Research question (hypothetical)**: Is there community precedent for evolving doctype enums backward-compatibly in markdown frontmatter validators?
- **KB-gap analysis**: Backward-compatible enum extension (additive new values, no removal, regression-test against pre-existing corpus) is **well-trodden general software-engineering practice**. The PRD's NFR-8 (zero false positives, zero false negatives on existing doc_types) is the testable form; the implementation pattern (add enum value, add per-state companion-field rule, add unit tests, run regression against existing corpus) requires no community sourcing. This is `designer-general-knowledge` per the discipline's five-way triage — see IN-031.
- **Conclusion**: NO GAP. `designer-general-knowledge` disposition; `design-backend` will document the rationale in its per-layer Design section.

### Result

**No external research topics authorized.** All information needs are resolved via KBs, ADRs, codebase research, the companion planning-mode plan, or `designer-general-knowledge` rationale.

**Budget consumed**: 0 of 6.

This is a positive design state (the project's KBs are doing their job), not a gap. The bulk of design substance is either decided in the companion plan (~400 lines of prior decisions plus the planning-mode external research already done on Dual-Track Agile, Spotify decision-tree, and RFC-to-spec discipline) or anchored in well-covered KBs.

---

## Topics explicitly NOT researched

Anti-scope-creep mechanism. Each row corresponds to an information need with `covered-by-KB`, `covered-by-ADR`, `covered-by-companion-artifact`, or `designer-general-knowledge` disposition.

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-001 | KB-cc-platform `references/extensions.md` + auditing-hooks `references/hook-spec.md` | Claude Code's hook contract is fully documented: stdin JSON includes `tool_input.subagent_type`; stdout JSON's `permissionDecision` field accepts `allow` / `ask` / `deny`; non-zero exit fails-open per the auditing-hooks security checklist. |
| IN-002 | KB-cc-design `references/principles.md` + KB-cc-platform `references/extensions.md` | `disable-model-invocation: true` blocks main Claude's auto-description-match load while permitting explicit user-invocation (e.g., slash-command). The two KBs together cover the flag semantics. |
| IN-003 | KB-cc-platform `references/extensions.md` | `AskUserQuestion` tool contract is fully documented including prompt-shape, options array, and the single-question-per-call discipline. |
| IN-004 | KB-cc-platform `references/extensions.md` | `Task` tool's `subagent_type` field, parameter-passing, and `$ARGUMENTS` inheritance are documented. |
| IN-005 | KB-cc-design `references/patterns-and-anti-patterns.md` + auditing-settings `SKILL.md` | Additive `.claude/settings.json` edits and the `hooks.PreToolUse` block shape are covered. |
| IN-006 | auditing-hooks `references/security-checklist.md` + `anti-patterns.md` + `common-failures.md` | Hook script security and fail-open patterns are exhaustively covered including bash hardening and stderr discipline. |
| IN-023 | ADR-0023 (Scope class taxonomy) | FULL-class implies full pipeline including all 6 mandatory gates; multi-primitive subsystems classify as FULL per ADR-0023's decision table. |
| IN-024 | KB-review-disciplines `references/gate-0-1-procedure.md` | Gate 0/1 detection of new templates is by `doc_type:` frontmatter match; structural checks apply once `doc_type` is recognized. |
| IN-025 | KB-documentation-criteria `references/disciplines/ears-acceptance-criteria.md` | EARS authoring discipline is canonical here; consumed at PRD time (already complete for v2) and at acceptance-test time. |
| IN-026 | KB-documentation-criteria `references/shared-conventions.md` | Frontmatter shape (id / version / status / generated / generated_by) is canonicalized here. |
| IN-027 | ADR-0032 (Conventions canonicalization including intent_user_token chain) | Intent-token inheritance is canonicalized in ADR-0032. |
| IN-028 | KB-documentation-criteria `references/layer-taxonomy.md` | 9-layer engineering taxonomy is canonical here. |
| IN-029 | KB-documentation-criteria `references/disciplines/plan-authoring.md` + KB-task-decomposition `SKILL.md` | Plan-authoring discipline is canonical; FULL-scope decomposition is documented. |
| IN-030 | KB-documentation-criteria `references/disciplines/design-composition.md` | Design composition discipline including ADR-slate authoring (per FR-5 of the pipeline, only design-composer authors ADRs) is canonical here. |
| IN-031 | `designer-general-knowledge` (downstream `design-backend` will document rationale) | Backward-compatible additive enum extension in a Python validator is well-trodden practice. `design-backend` documents the rationale in its layer subsection. |
| IN-032 | `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md` (companion plan from prior planning-mode session) | Dual-Track Agile, Spotify decision-tree, RFC-to-spec discipline external research was already performed in planning-mode. Citations live in the companion plan. **Do not re-research.** |

---

## Risks and open questions for Discovery / Design

### Risks Discovery / Design must remain alert for

1. **Drift in the Claude Code platform contract.** KB-cc-platform documents a snapshot of the hook / `AskUserQuestion` / `Task` contracts. If the underlying Claude Code release has shifted since the KB was last updated, design assumptions may be subtly wrong. The codebase-researcher should spot-check KB-cc-platform's claims against `.claude/SETTINGS-NOTES.md` and any visible version notes.
2. **ADR-0008 placement drift.** ADR-0008 lives in `adrs-migrated/` per the known drift. If `design-composer`'s 7-ADR slate (PRD U-10) needs to cite ADR-0008's 4-state vocabulary, the canonical text should be loaded from the migrated path. **Do not attempt to migrate ADR-0008 as part of this run** — that is a separate (deferred) concern captured in `Issues/analysis-adr-placement-rootcause.md`.
3. **Validator-extension regression surface unknown until codebase research completes.** The full set of files validated by `validate_pipeline_frontmatter.py` is not yet inventoried. The "zero false positives, zero false negatives" NFR-8 requires that the regression baseline corpus be enumerable before the extension is implemented.
4. **Pipeline-isolation grep may surface ambient mentions in comments or documentation.** AC-FR-13-a / AC-FR-13-b expect zero matches in pipeline agent files. The codebase-researcher should distinguish "true reference to invoke the mechanism" from "discussion in a comment or example." If any current match exists, it's a baseline finding that must be resolved before merge.
5. **Hook fail-open semantics may differ between bash and other interpreters.** PRD U-1 leaves the hook implementation language open. The codebase-researcher should note any existing hook precedent in `.claude/hooks/` (if a `.claude/hooks/` directory already exists with any precedent).
6. **The `Issues/issue-capture-mechanism/` folder already exists** (containing `proposal.md`). It is the seed for this very run. Design must respect that the per-folder model is being introduced in the same release that uses it for the proposal. No special migration is needed; the folder is born canonical.

### Open questions for human resolution at the Research Plan Approval Gate

These surface to the user; their answers update this Plan before research begins.

1. **External research budget**: Is 0-of-6 acceptable? The decision rests on whether the user agrees that the planning-mode external research (Dual-Track Agile, Spotify decision-tree, RFC-to-spec) plus the KB coverage are sufficient. If the user wants any of the rejected candidates (PreToolUse hook security; primitive selection; backward-compatible enum evolution) to be researched anyway, name it and we'll add it.
2. **Should the codebase researcher attempt to migrate `ADR-0008` from `adrs-migrated/` to `adrs/` opportunistically?** The PRD says no (the drift is captured in `Issues/analysis-adr-placement-rootcause.md` and is its own future feature). Confirm.
3. **For pipeline-isolation verification (AC-FR-13-a / AC-FR-13-b)**: should the codebase researcher report any *prose* mentions of `KB-issue-capture` or `issue-capture-author` (e.g., in example sections of documentation) as findings, or only invocation-pattern matches? The PRD's acceptance criterion is `grep returns zero matches`, which suggests prose matches are also disallowed. Confirm.
4. **Scope of `intake-intent-clarifier` blast-radius analysis**: should the researcher enumerate all sub-agents that read `intent-clarification.md` (potentially expensive), or only those reachable within 3 hops via GitNexus? The 3-hop bound is recommended (ADR-0018 standard); confirm.
5. **Hook precedent question**: if `.claude/hooks/` does not yet exist as a directory, the new hook script is the first hook in the project. Does the user want a "first hook" callout in the design? (This is a Stage-5 design question; flagged here only because it affects how the codebase researcher should communicate the discovery.)

---

## Exit criteria

Discovery research is complete when:

1. `codebase-analysis.json` exists and conforms to the ADR-0018 schema, with blast-radius coverage for each touch point Group A and B above.
2. All `codebase-topic` information needs (IN-007, IN-008, IN-009, IN-010, IN-011, IN-012, IN-013, IN-014, IN-015, IN-016, IN-017, IN-018, IN-019, IN-020, IN-021, IN-022) have been answered with concrete findings.
3. The pipeline-isolation pre-condition (Group D queries) is verified: zero matches for `KB-issue-capture` and `issue-capture-author` in pipeline-agent files (or, if non-zero, the count and locations are reported as findings for Design / Plan to address).
4. The validator's existing doc_type enum, status vocabulary, and per-state companion-field rules are enumerated (IN-007) — input to FR-7 design.
5. The four existing flat `Issues/*.md` files' structures are inventoried (IN-011) — input to the three templates (FR-6).
6. The intra-pipeline 4-state vocabulary in `KB-review-disciplines/references/issue-lifecycle.md` is transcribed verbatim (IN-012) — input to the 5-state vocabulary design and the ADR that codifies their distinction.
7. The Risks list above is reviewed; any "real" risk surfaced by codebase research (e.g., a previously-undetected dependency on validate_pipeline_frontmatter.py) is added to the codebase-analysis output for Synthesis to absorb.

Synthesis can then proceed with sufficient grounding to map claims to PRD requirements and per-layer Design subsections.

---

## Estimated effort

- **Codebase research effort**: **Medium**. The touch-point inventory is broad (~30 files across `.claude/agents/`, `.claude/skills/`, `Issues/`, and root-level config) but depth on each is shallow (verification of current shape, not discovery of unknown patterns). One `discovery-codebase-researcher` invocation should suffice; estimate ~15-30 minutes wall-clock depending on GitNexus availability for blast-radius queries.
- **External research topic count**: **0 of 6**.
- **Estimated wall-clock total for Discovery research**: ~30-45 minutes (codebase-research-bound; no external-research parallelism needed).

---

## Provenance and cross-references

- **Discovery Planning discipline**: `.claude/skills/KB-documentation-criteria/references/disciplines/discovery-planning.md` (operational rules for this stage).
- **Research Plan template**: `.claude/skills/KB-documentation-criteria/references/templates/research-plan-template.md` (structural contract).
- **ADR-0021** (Discovery phase architecture; KB-and-ADR-first).
- **ADR-0018** (codebase-analysis.json schema; downstream consumer of Codebase Research Scope).
- **Prior-stage artifacts**:
  - PRD v1.1.0 — `working/feature/issue-capture-mechanism-r1/prd-v2.md`
  - Intent Clarification — `working/feature/issue-capture-mechanism-r1/intent-clarification.md`
  - Seed proposal — `Issues/issue-capture-mechanism/proposal.md`
  - Companion plan (decided design) — `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md`
