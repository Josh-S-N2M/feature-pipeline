---
id: IC-adr-placement-mechanism-repair-r1
version: 2.0.1
doc_type: intent-clarification
status: approved
feature_slug: adr-placement-mechanism-repair-r1
user_token: 2026-05-24-intent-confirmation-binding-override-consolidate-archive
gate_passed: intent_confirmation
approved_at: 2026-05-24T18:55:00Z
reviewer_verdict: pass
generated: 2026-05-24T18:32:01Z
generated_by: intake-intent-clarifier
scope_class: FULL
layer_scope: ["claude-code"]
prior_context_source: Issues/adr-placement-rootcause/proposal.md
prior_context_companion: Issues/adr-placement-rootcause/analysis.md
predecessor_version: 1.1.0
---

# Intent Clarification: Repair the ADR Placement Mechanism Per ADR-0036 (v2.0.0)

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Functional Requirements (Preliminary)
- [x] Acceptance Criteria (EARS, Preliminary)
- [x] Stakeholder Posture (Preliminary)
- [x] Layer Scope Declaration (Preliminary)
- [x] Phase-Internal Boundaries (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)
- [x] Scope Deviation Notice (v1.1.0 → v2.0.0)
- [x] Provenance

## Purpose

Capture the user's intent for `adr-placement-mechanism-repair-r1` before PRD authoring. This is the **v2.0.0** re-author following a binding user override at the Intent Confirmation Gate that materially expanded scope from the v1.1.0 "surgical edits + grandfather" framing to a "full migration + cross-reference sweep + enforcement gates + skill audit" framing. The binding override is recorded verbatim in the Provenance section. This document records (a) the proposal-derived intent as updated by the override, (b) the resolutions to the original five open questions Q1–Q5 (with Q2/Q4/Q5/FR-7 reversed or revised), (c) the on-disk reality discovery that materially restated the migration scope, and (d) the preliminary FR/AC/Stakeholder/Layer-Scope/Phase declarations the PRD author needs to begin work without re-eliciting decided material.

## Source

User-supplied raw request: the fully-prepared issue-proposal at `/workspaces/feature-pipeline/Issues/adr-placement-rootcause/proposal.md` (transitioned `draft → adopted` on 2026-05-24 with `adopted_by_feature_slug: adr-placement-mechanism-repair-r1`). The proposal in turn escalates from the sibling root-cause analysis at `Issues/adr-placement-rootcause/analysis.md`. The v2.0.0 binding-override source is the user's verbatim directive returned at the Intent Confirmation Gate following review of v1.1.0:

> "we need to migrate and ensure all references, paths and links all reference the new consolidated location. also the feature pipeline and execution pipeline need to be updated to ensure it adheres, enforcement gates and validates the correct location and references to ADRs. we also need to ensure all of our SKILLs are updated if required to prevent re-introducing the issue."

This directive is treated as authoritative and binding: Q2, Q4, Q5, and FR-7 are reversed or revised; Q1 and Q3 are re-evaluated under the new migration directive; FR-8 through FR-11 are added; scope class moves from MINOR to FULL.

## Initial Interpretation

The user wants a comprehensive repair of the ADR placement mechanism that (a) consolidates every ADR currently outside canonical `adrs/` into canonical `adrs/`, (b) updates every reference / path / link in the repository to point to the consolidated location, (c) wires enforcement gates into both the feature pipeline and the execution pipeline so the canonical-only convention is structurally enforceable rather than discretionary, and (d) audits and updates every skill that could otherwise re-introduce the feature-scoped placement behavior. The v1.1.0 framing of "four surgical edits + Blueprint disposition note" remains in scope as Phase 1 of a multi-phase initiative, but is no longer sufficient. The on-disk reality (verified by the orchestrator before this re-author) is materially different from the proposal's "12 ADRs to migrate" framing: 12 byte-identical duplicates (trivial dedupe), 3 divergent duplicates needing semantic resolution (ADR-0024, ADR-0044, ADR-0045), 5 truly feature-scoped ADRs needing relocation (ADR-0046–0050), and a 47-file legacy archive (`adrs-migrated/`) whose disposition is the single remaining genuinely-open question. Layer scope remains CC-only (the entire touch is within `.claude/`, `adrs/`, `working/feature/`, `Issues/`, and `README.md`), but the breadth of the touch within that single layer is substantially larger than the proposal predicted.

## Clarifying Questions and Answers

This re-author records the user's binding override at the Intent Confirmation Gate. Rows marked **RESOLVED (binding)** are no longer provisional — they reflect the verbatim user directive in the Source section above. Rows marked **OPEN** remain genuinely undecided and will be confirmed at the re-run Intent Confirmation Gate that follows this v2.0.0 document.

| # | Ambiguity | Question Asked | User Answer (binding per gate override) | Resolved? |
|---|---|---|---|---|
| 1 | Q1 — Parameter vs hard-code: should `output_adrs_dir` remain a parameter (test-only override) or be eliminated entirely (canonical root hard-coded)? | Keep `output_adrs_dir` as a parameter for test-only overrides, with canonical-root hard-coded as the default, or eliminate the parameter entirely? | **UNCHANGED from v1.1.0: Keep as parameter, hard-code canonical-root as default, document test-only override mechanism.** The v2.0.0 user directive does not touch this dimension; the v1.1.0 resolution stands. **RESOLVED (binding).** | [x] |
| 2 | Q2 — Migrate or grandfather: do the existing feature-scoped ADRs get migrated to canonical root, or treated as historical-only? | Migrate the in-flight feature-scoped ADRs to canonical `adrs/`, or grandfather them? | **REVERSED to MIGRATE.** Per verbatim user directive: "we need to migrate and ensure all references, paths and links all reference the new consolidated location." Per on-disk reality verification, the migration decomposes into 3 sub-cases: (a) dedupe 12 byte-identical duplicates after equality verification; (b) semantic-reconcile 3 divergent cases (ADR-0024, 0044, 0045); (c) `git mv` 5 truly feature-scoped ADRs (0046–0050) to canonical with redirect notes in originating feature folders. **RESOLVED (binding).** | [x] |
| 3 | Q3 — ADR-0024 (and newly-discovered ADR-0044, ADR-0045) drift reconciliation: pick a canonical body or flag-and-defer? | Reconcile the divergent ADR bodies in this feature, or defer? | **NO LONGER FLAG-AND-DEFER.** The migration directive (Q2) forces semantic resolution. Discovery + Design Composition propose a canonical body per divergent case; rejected bodies are archived to `adrs/superseded/<id>-feature-scoped-body.md` with a provenance footer (default interpretation; surfaces as Open Item #1 for the re-run gate to confirm or override the archival format). **RESOLVED (binding).** | [x] |
| 4 | Q4 — `adrs-migrated/` (47-file legacy archive) disposition: leave untouched, or consolidate? | Move the `adrs-migrated/` legacy archive contents into canonical `adrs/`, or leave the archive untouched? | **REVISED / SURFACES AS OPEN ITEM.** The "consolidated location" directive is ambiguous on whether the historical archive (pre-template-migration versioned variants) counts. Default lean for v2.0.0: interpretation (b) — `adrs-migrated/` is a different category (historical archive, not feature-scoped duplication), so it stays in place but is reviewed for cross-references to update. Interpretation (a) — strict reading, requires consolidation — remains a live alternative if the user overrides. Surfaces as Open Item #2 for the re-run gate. **RESOLVED (binding) with sub-question deferred to gate.** | [x] |
| 5 | Q5 — Shipped Blueprint cross-references: amend, or treat shipped Blueprints as immutable? | Reach into shipped Blueprint artifacts to update path references, or treat them as immutable historical records? | **REVISED.** Per "all references, paths and links" directive, shipped Blueprints are **updateable for path-only edits** (when an ADR moves, the path reference must follow). Semantic edits to shipped Blueprint prose remain out of scope. The phantom-promotion misreading at `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226` remains out of scope (it is a semantic misreading, not a path reference). **RESOLVED (binding).** | [x] |
| 6 | FR-7 — No new validator: confirm or supersede? | Should this feature introduce an ADR-location validator and wire it into pipeline gates, or rely on corrected defaults alone? | **SUPERSEDED.** Per "enforcement gates and validates the correct location" directive. FR-7 is replaced by FR-10 (validator + enforcement gates wired into feature pipeline, execution pipeline, and packager). **RESOLVED (binding).** | [x] |
| 7 | Layer Scope: CC-only or expand under the broadened scope? | The v1.1.0 prediction is CC-only. Under the v2.0.0 broadened scope (migration, cross-reference sweep, validator, skill audit), does layer scope change? | **CONFIRMED CC-only.** Every touched surface — `.claude/`, `adrs/`, `working/feature/`, `Issues/`, `README.md` — sits within the Claude Code / Project Filesystem layer. The touch is broader within the layer; the layer itself does not change. Flagged as a deviation in the Layer Scope Declaration. **RESOLVED (binding).** | [x] |
| 8 | Phase decomposition: 7-phase decomposition under v2.0.0 scope? | The v2.0.0 scope demands a multi-phase plan (discovery + setup, operator-file repairs, migration, cross-ref sweep, validator + gates, skill audit, verification). Confirm? | **CONFIRMED 7-phase decomposition** (Phase 0 Discovery + Setup; Phase 1 Operator file repairs; Phase 2 Migration with 3 sub-phases; Phase 3 Cross-reference sweep; Phase 4 Validator + enforcement gates; Phase 5 Skill audit + remediation; Phase 6 Verification; plus standard rollout). **RESOLVED (binding).** | [x] |
| 9 | Stakeholder posture: who is added under the broadened scope? | Under FR-8's divergent-body resolution, do the originating features' authors become informed stakeholders? | **YES, added.** The divergent-body decision for ADR-0024 affects `frontend-design-knowledge-r1`; ADR-0044 and ADR-0045 affect `issue-capture-mechanism-r1`. Authors of those originating features are now informed stakeholders. **RESOLVED (binding).** | [x] |

**Note on convention deviation:** the v2.0.0 binding answers were elicited via the orchestrator's `AskUserQuestion` at the v1.1.0 Intent Confirmation Gate, NOT via this sub-agent's `AskUserQuestion` (which is not in the sub-agent's allowlist). The user's gate-elicited directive is treated as binding for downstream PRD authoring, not as provisional. The five Open Items below remain genuinely open for the re-run Intent Confirmation Gate to confirm or override.

## Clarified Intent

Comprehensively repair the ADR placement mechanism so the canonical-only convention codified by ADR-0036 is enforced structurally across the entire repository rather than only declaratively in `deliverable-archive-spec.md`. The feature: (a) performs the four surgical operator-file edits originally scoped in v1.1.0 (Phase 1); (b) migrates every ADR currently outside canonical `adrs/` into canonical `adrs/` — dedupe 12 byte-identical duplicates, semantic-reconcile 3 divergent cases (ADR-0024, 0044, 0045), and `git mv` 5 truly feature-scoped ADRs (0046–0050) (Phase 2); (c) sweeps the repository for every reference / path / link to a relocated ADR and updates path-only edits to point to canonical `adrs/` (Phase 3); (d) authors an ADR-location validator and wires it into the feature pipeline (orchestrator stage gate), the execution pipeline (specialist or hook), and the `finalize-deliverable-packager` (replacing the deleted dual-location BLOCKER with a canonical-only check that calls the validator) (Phase 4); (e) audits every skill that documents or enables ADR authoring/placement and updates prose or templates that could permit feature-scoped placement to re-enter the pipeline (Phase 5); and (f) empirically verifies the new behavior by running a small mock feature through the orchestrator post-edit (Phase 6). The end-state is that canonical-only ADR placement is structurally enforced at three independent enforcement surfaces (orchestrator gate, packager check, execution-pipeline hook), no skill can re-introduce the feature-scoped behavior, and every cross-reference in the repository points to the consolidated canonical location.

## Scope Posture

### What's in scope

**Phase 1 — Operator file repairs (carry-over from v1.1.0):**
- Delete retired dual-location BLOCKER prose in `.claude/agents/finalize-deliverable-packager.md:56–63` (Causal Site 3 per analysis).
- Delete contradictory dual-location BLOCKER prose in `.claude/agents/shared-document-reviewer.md:349`, leaving only the post-ADR-0036 statement at lines 470–472 (Causal Site 4).
- Change the orchestrator-side `output_adrs_dir` value passed to `design-composer` so it resolves to canonical-root `adrs/` rather than a feature-scoped path. The parameter is declared at `.claude/skills/recipe-feature-pipeline/SKILL.md:273`; the precise edit form is decided during Discovery + Design Composition (Causal Site 1; supersedes the proposal's imprecise `:17–28, :228` line citation).
- Change `output_adrs_dir` parameter description in `.claude/agents/design-composer.md:48, :129, :187` to reference ADR-0036 and document the canonical default (Causal Site 2).
- Keep `output_adrs_dir` as a parameter for test-only overrides (per Q1 resolution); document the override surface explicitly in `design-composer.md`.

**Phase 2 — Migration (new under v2.0.0):**
- **2a — Dedupe 12 byte-identical duplicates.** ADR-0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043. Verify byte-equality, then delete the feature-scoped copy.
- **2b — Semantic-reconcile 3 divergent cases.** ADR-0024 (root vs `working/feature/frontend-design-knowledge-r1/adrs/`); ADR-0044 and ADR-0045 (root vs `working/feature/issue-capture-mechanism-r1/adrs/`). Discovery + Design Composition propose a canonical body per case; rejected body archived to `adrs/superseded/<id>-feature-scoped-body.md` with provenance footer (default; surfaces as Open Item #1).
- **2c — `git mv` 5 truly feature-scoped ADRs to canonical.** ADR-0046, 0047, 0048, 0049, 0050 (all from `working/feature/issue-capture-mechanism-r1/adrs/`). Relocate cleanly to canonical, leave redirect notes in originating feature folder (redirect-note format is Open Item #5).

**Phase 3 — Cross-reference sweep (new under v2.0.0):**
- Every reference to a relocated or deduplicated ADR (by path) in the repository shall be updated to point to canonical `adrs/`. Scope: shipped Blueprints (`working/feature/*/blueprint-v*.md`), Plans (`working/feature/*/plan-v*.md`), agent files (`.claude/agents/*.md`), skill files (`.claude/skills/**/*.md`), Issues files (`Issues/**/*.md`), and the README. Path-only edits only; no semantic rewrites. Per the Q5 revision, this includes shipped Blueprint path references.

**Phase 4 — Validator and enforcement gates (new under v2.0.0):**
- Author an ADR-location validator (likely Python under `.claude/skills/auditing-shared/scripts/`) that fails on any `ADR-*.md` file found outside canonical `adrs/`, with explicit allowlist for `adrs-migrated/` per Q4 default lean (subject to gate override).
- Wire the validator into (a) the feature pipeline orchestrator at a stage gate, (b) the execution pipeline (specialist or hook — exact surface decided by Discovery), and (c) `finalize-deliverable-packager` (replacing the deleted dual-location BLOCKER with a canonical-only check that calls the validator).

**Phase 5 — Skill audit + remediation (new under v2.0.0):**
- Audit every skill that documents or enables ADR authoring/placement: `KB-documentation-criteria`, `auditing-*` family, `recipe-feature-pipeline`, synthesize-class skills, `KB-review-disciplines`. Update prose or templates that could permit feature-scoped placement to re-enter the pipeline. The audit is documented in the Blueprint and tracked as Phase 5 tasks.

**Phase 6 — Verification (new under v2.0.0):**
- Empirically confirm a fresh feature run produces canonical-only ADRs; the validator blocks attempted feature-scoped writes; no broken cross-references remain after the sweep.

### What's NOT in scope (explicitly excluded)

- Semantic rewrites of shipped Blueprint prose (only path-only edits are in scope per Q5 revision).
- Amending the phantom-promotion misreading at `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226` (it is a semantic misreading, not a path reference).
- Consolidating `adrs-migrated/` per interpretation (a) — default lean is interpretation (b) (archive remains untouched but cross-references reviewed). Subject to gate override (Open Item #2).
- Any changes outside the Claude Code / Project Filesystem layer.
- Authoring new ADR templates or changing the ADR-NNNN numbering convention.
- Introducing a promotion-step automation (canonical-only is the only path; the validator enforces it, no copy/promote step exists).

### What's undecided (deferred to PRD or later)

- The exact override surface for the `output_adrs_dir` parameter (env var? CLI flag? test-fixture-only?) — Discovery + Design stages decide.
- The exact archival format for divergent-body losers under FR-8b (Open Item #1; default is `adrs/superseded/<id>-feature-scoped-body.md` with provenance footer; gate may override).
- The `adrs-migrated/` interpretation (Open Item #2; default is interpretation (b)).
- The validator's implementation surface (Open Item #3): exact path under `.claude/skills/auditing-shared/scripts/`, language (Python assumed but not binding), interface contract with the orchestrator and packager.
- The completeness of the cross-reference inventory from Phase 0 Discovery (Open Item #4): whether grep patterns capture every reference form (e.g., `adrs/ADR-NNNN`, `ADR-NNNN`, `[ADR-NNNN](path)`, `see ADR-NNNN`, etc.).
- The redirect-note format for relocated ADRs in originating feature folders (Open Item #5).

## Functional Requirements (Preliminary)

These are preliminary FRs derived from the proposal, the v1.1.0 analysis, and the v2.0.0 binding user directive. The PRD author will refine, split, or merge as warranted.

- **FR-1 — Delete retired dual-location BLOCKER prose in packager.** The `.claude/agents/finalize-deliverable-packager.md` file shall no longer contain the retired dual-location BLOCKER check at lines 56–63 (or its equivalent post-edit location). The packager's ADR-placement check shall be replaced by a call to the FR-10 validator.
- **FR-2 — Delete contradictory dual-location BLOCKER prose in reviewer.** The `.claude/agents/shared-document-reviewer.md` file shall no longer contain the contradictory dual-location check at line 349. The only ADR-placement statement shall be the post-ADR-0036 statement at lines 470–472 (or equivalent post-edit location).
- **FR-3 — Orchestrator `output_adrs_dir` value resolves to canonical root.** The `.claude/skills/recipe-feature-pipeline/SKILL.md` (the orchestrator) shall resolve `output_adrs_dir` to canonical-root `adrs/` (not a feature-scoped path) when invoking `design-composer`. The parameter declaration is at SKILL.md:273; the actual default-resolution edit form is determined by Discovery + Design Composition.
- **FR-4 — Design-composer `output_adrs_dir` parameter documents canonical default + ADR-0036 reference.** The `.claude/agents/design-composer.md` file at lines 48, 129, 187 shall describe the `output_adrs_dir` parameter with canonical-root as the default and cite ADR-0036 explicitly; the description shall document the test-only override mechanism.
- **FR-5 — `output_adrs_dir` remains a parameter with documented test-only override.** Per Q1 resolution, `output_adrs_dir` shall not be eliminated; it shall remain a parameter whose default is canonical-root, with the override surface documented in `design-composer.md`.
- **FR-6 — Blueprint documents migration disposition (revised under v2.0.0).** The Blueprint authored as part of this feature shall enumerate every ADR currently outside canonical `adrs/`, classify each (duplicate-identical / duplicate-divergent / feature-scoped-only / legacy-archive), and document the migration disposition per FR-8. **(Replaces v1.1.0 FR-6's grandfather-disposition framing.)**
- **FR-7 — SUPERSEDED.** The v1.1.0 FR-7 ("no new validator, no promotion machinery") is superseded by FR-10. The v2.0.0 user directive explicitly mandates enforcement gates and validation. Retained as a reserved FR slot for traceability; no behavior required.
- **FR-8 — Migration of duplicated, divergent, and feature-scoped ADRs.** Three sub-scopes:
  - **FR-8a — Dedupe.** The 12 byte-identical duplicates (ADR-0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043) shall be deduplicated by verifying byte-equality between the canonical and feature-scoped copies, then deleting the feature-scoped copy.
  - **FR-8b — Semantic reconciliation.** The 3 divergent cases (ADR-0024, ADR-0044, ADR-0045) shall be reconciled: Discovery + Design Composition propose a canonical body per case; the rejected body shall be archived to `adrs/superseded/<id>-feature-scoped-body.md` with a provenance footer (default; subject to Open Item #1 override).
  - **FR-8c — Relocation.** The 5 truly feature-scoped ADRs (ADR-0046, 0047, 0048, 0049, 0050) shall be relocated via `git mv` to canonical `adrs/`, with redirect notes left in the originating feature folder (format per Open Item #5).
- **FR-9 — Cross-reference sweep.** Every reference to a relocated or deduplicated ADR (by path) in the repository shall be updated to point to canonical `adrs/`. Scope: shipped Blueprints (`working/feature/*/blueprint-v*.md`), Plans (`working/feature/*/plan-v*.md`), agent files (`.claude/agents/*.md`), skill files (`.claude/skills/**/*.md`), Issues files (`Issues/**/*.md`), and the README. Path-only edits; no semantic rewrites.
- **FR-10 — ADR-location validator and enforcement gates.** The system shall provide a validator (likely Python under `.claude/skills/auditing-shared/scripts/`) that fails on any `ADR-*.md` file found outside canonical `adrs/`, with an explicit allowlist for `adrs-migrated/` (per Q4 default lean; subject to gate override). The validator shall be wired into three enforcement surfaces: (a) the feature pipeline orchestrator at a stage gate; (b) the execution pipeline (relevant specialist or hook); (c) `finalize-deliverable-packager` (replacing the deleted dual-location BLOCKER with a canonical-only check that calls the validator).
- **FR-11 — Skill audit and remediation.** Every skill that documents or enables ADR authoring/placement (`KB-documentation-criteria`, `auditing-*` family, `recipe-feature-pipeline`, synthesize-class skills, `KB-review-disciplines`) shall be reviewed; any prose or template that could permit feature-scoped ADR placement shall be updated. The audit shall be documented in the Blueprint and tracked as Phase 5 tasks.

## Acceptance Criteria (EARS, Preliminary)

Per `KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md`. Grouped by FR. Layer: Claude Code / Project Filesystem for all.

### FR-1 — Delete retired dual-location BLOCKER prose in packager

- [ ] AC-FR-1-a (CC): When `.claude/agents/finalize-deliverable-packager.md` is read after this feature ships, the system shall not contain the retired dual-location BLOCKER prose text (the text currently at lines 56–63).
- [ ] AC-FR-1-b (CC): When `finalize-deliverable-packager` runs on a feature whose ADRs were authored only to canonical root `adrs/`, the system shall NOT raise PKG-BLOCKER-001 or any equivalent dual-location BLOCKER. The replacement canonical-only check (per FR-10) shall pass.

### FR-2 — Delete contradictory dual-location BLOCKER prose in reviewer

- [ ] AC-FR-2-a (CC): When `.claude/agents/shared-document-reviewer.md` is read after this feature ships, the system shall not contain the contradictory dual-location BLOCKER check at line 349 (or its equivalent location).
- [ ] AC-FR-2-b (CC): When `shared-document-reviewer` reviews a Blueprint that references ADRs at canonical root only, the system shall not flag the canonical-only placement as a violation.

### FR-3 — Orchestrator `output_adrs_dir` default resolves to canonical root

- [ ] AC-FR-3-a (CC): When the orchestrator (`recipe-feature-pipeline/SKILL.md`) invokes `design-composer` without an explicit `output_adrs_dir` caller override, the system shall pass canonical-root `adrs/` (relative to repo root), not a feature-scoped path such as `working/feature/<slug>/adrs/`.
- [ ] AC-FR-3-b (CC): Where the orchestrator invokes `design-composer` without an explicit `output_adrs_dir` override, the system shall pass canonical-root as the value.

### FR-4 — Design-composer parameter description carries canonical default + ADR-0036 reference

- [ ] AC-FR-4-a (CC): When `.claude/agents/design-composer.md` is read after this feature ships, the `output_adrs_dir` parameter description shall cite ADR-0036 explicitly and state that canonical-root is the default.
- [ ] AC-FR-4-b (CC): The system shall document, in `design-composer.md`, the test-only override mechanism for `output_adrs_dir` (the override surface — env var / CLI flag / test-fixture — is decided by Discovery + Design).

### FR-5 — `output_adrs_dir` remains a parameter with documented test-only override

- [ ] AC-FR-5-a (CC): The system shall retain `output_adrs_dir` as a parameter on `design-composer` (it shall not be eliminated).
- [ ] AC-FR-5-b (CC): Where a caller passes `output_adrs_dir` explicitly (e.g., a test fixture), the system shall honor the passed value rather than the default.

### FR-6 — Blueprint documents migration disposition

- [ ] AC-FR-6-a (CC): The Blueprint authored in this feature shall contain a section enumerating every ADR currently outside canonical `adrs/`, classified into one of four categories (duplicate-identical / duplicate-divergent / feature-scoped-only / legacy-archive) per the Phase 0 Discovery output.
- [ ] AC-FR-6-b (CC): The Blueprint shall document the migration disposition per FR-8 for each classified ADR (dedupe / semantic-reconcile / `git mv` / leave-archived).

### FR-7 — SUPERSEDED

- [ ] AC-FR-7-a (CC): No acceptance criteria. FR-7 is superseded by FR-10; retained as a reserved slot for traceability with v1.1.0.

### FR-8 — Migration of duplicated, divergent, and feature-scoped ADRs

- [ ] AC-FR-8a-1 (CC): When this feature ships, the 12 byte-identical duplicate ADRs (0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043) shall exist at canonical `adrs/` only; the feature-scoped copies shall have been deleted.
- [ ] AC-FR-8a-2 (CC): Where a duplicate is deduplicated under FR-8a, the system shall log the byte-equality verification step in the Plan's per-task execution result (audit trail).
- [ ] AC-FR-8b-1 (CC): When this feature ships, ADR-0024, ADR-0044, and ADR-0045 shall exist at canonical `adrs/` only; the rejected body shall be archived (default location: `adrs/superseded/<id>-feature-scoped-body.md`).
- [ ] AC-FR-8b-2 (CC): When the archived rejected body is read, the system shall present a provenance footer identifying the originating feature folder and the canonical-body decision rationale.
- [ ] AC-FR-8c-1 (CC): When this feature ships, ADR-0046, 0047, 0048, 0049, 0050 shall exist at canonical `adrs/` only; the feature-scoped originals shall have been relocated via `git mv` (preserving Git history).
- [ ] AC-FR-8c-2 (CC): Where an ADR is relocated under FR-8c, the originating feature folder shall contain a redirect note (format per Open Item #5).

### FR-9 — Cross-reference sweep

- [ ] AC-FR-9-a (CC): When this feature ships, no in-repository reference shall point to a relocated or deduplicated ADR at its former (feature-scoped) path. A grep for the known former paths shall return zero matches (excluding the redirect notes themselves and the audit trail).
- [ ] AC-FR-9-b (CC): The cross-reference sweep shall be path-only; shipped Blueprint prose (semantic content) shall not be edited beyond the path replacement. A diff review of shipped Blueprints after the sweep shall show only path-token changes.
- [ ] AC-FR-9-c (CC): The Phase 0 Discovery output shall include a cross-reference inventory enumerating every reference site by file and line; the Phase 3 sweep shall update every entry in the inventory.

### FR-10 — ADR-location validator and enforcement gates

- [ ] AC-FR-10-a (CC): The system shall provide a validator script (likely Python under `.claude/skills/auditing-shared/scripts/`) that, when invoked, scans the repository for `ADR-*.md` files and returns non-zero exit status if any are found outside canonical `adrs/` (with explicit allowlist for `adrs-migrated/`).
- [ ] AC-FR-10-b (CC): When the feature pipeline orchestrator reaches its stage gate (exact stage decided during Design), the system shall invoke the validator and shall block stage progression on non-zero exit.
- [ ] AC-FR-10-c (CC): When the execution pipeline reaches its relevant specialist or hook (exact surface decided during Design), the system shall invoke the validator and shall block progression on non-zero exit.
- [ ] AC-FR-10-d (CC): When `finalize-deliverable-packager` runs, the system shall invoke the validator in place of the deleted dual-location BLOCKER and shall raise a BLOCKER on non-zero exit.
- [ ] AC-FR-10-e (CC): Where a test fixture writes an ADR to a feature-scoped path (deliberate negative-path test), the validator shall return non-zero and the corresponding gate shall block.

### FR-11 — Skill audit and remediation

- [ ] AC-FR-11-a (CC): When this feature ships, the audit log shall enumerate every skill reviewed (`KB-documentation-criteria`, `auditing-*` family, `recipe-feature-pipeline`, synthesize-class skills, `KB-review-disciplines`) and the disposition of each (no change required / updated).
- [ ] AC-FR-11-b (CC): Where a skill contains prose or a template that could permit feature-scoped ADR placement (e.g., a `output_adrs_dir` template default, a "place ADRs here" instruction in the feature folder), the system shall update the skill so canonical-only is the only path the skill describes.
- [ ] AC-FR-11-c (CC): The Blueprint shall record the skill audit findings and the remediation summary.

### Cross-Layer / Operational ACs

- [ ] AC-OP-1: When a fresh feature-pipeline run completes after this feature ships and does not pass an explicit `output_adrs_dir` override, the system shall write any authored ADRs only to canonical-root `adrs/` and the packager shall PASS (zero ADR-placement BLOCKERs).
- [ ] AC-OP-2: When the operator files touched in Phase 1 are read after this feature ships, the system shall present a single internally-consistent ADR-placement convention across all four (no file contradicts ADR-0036, no file contradicts another).
- [ ] AC-OP-3: When the validator is invoked on the post-feature repository state, the system shall return zero exit status (no ADR-placement violations remain after the migration completes).
- [ ] AC-OP-4: When a deliberate negative-path test writes an ADR to a feature-scoped path post-feature, all three enforcement surfaces (orchestrator gate, execution-pipeline hook, packager) shall block.

## Stakeholder Posture (Preliminary)

- **Owner — joshua.selfe@gmail.com:** cares that the ADR placement mechanism is structurally enforced (not merely declarative), that every cross-reference points to the consolidated canonical location, that no skill can re-introduce the feature-scoped behavior, and that the broadened v2.0.0 scope completes without regression in adjacent agent behavior.
- **Reviewer — `shared-document-reviewer`:** cares that this Intent Clarification (v2.0.0), the PRD, the Blueprint, and the Plan pass Gates 0/1; will run on every authored document per ADR-0017.
- **Reviewer — `review-architecture-auditor`:** cares that the Blueprint's migration disposition, the validator integration, and the skill-audit remediation are internally consistent with ADR-0036 and that the three enforcement surfaces are non-redundant and non-contradictory.
- **Reviewer — `review-cross-artifact-auditor`:** cares that the Plan and Tests stay consistent with the Blueprint across iterations, especially given the multi-phase scope.
- **Informed — `finalize-deliverable-packager`:** its PKG-BLOCKER-001 is replaced by a validator-backed canonical-only check; behavior changes from "BLOCKER on dual-location" to "BLOCKER on any non-canonical location."
- **Informed — Future feature-pipeline runs:** inherit canonical-only as the structurally-enforced default; no Gate-7 opt-in required, and the validator blocks attempted feature-scoped writes before they ship.
- **Informed — `devcontainer-mcp-provisioning-r1` Gate-6 deferral chain:** closes when this feature completes; the user's "defer to a pipeline-fix follow-up feature" disposition recorded against PKG-BLOCKER-001 is satisfied.
- **Informed — Author of `frontend-design-knowledge-r1`:** the divergent-body decision for ADR-0024 affects the originating feature; informed of the canonical-body selection rationale and the archival of the rejected body. **(Added under v2.0.0 Q9.)**
- **Informed — Author of `issue-capture-mechanism-r1`:** the divergent-body decisions for ADR-0044 and ADR-0045, plus the FR-8c relocation of ADR-0046–0050 from that feature folder, affect the originating feature; informed of the canonical-body selections, the relocations, and the redirect-note format. **(Added under v2.0.0 Q9.)**

## Layer Scope Declaration (Preliminary)

Per the 9-layer taxonomy in `KB-documentation-criteria/references/layer-taxonomy.md`. Confirmation of CC-only under broadened v2.0.0 scope.

- [x] **Claude Code / Project Filesystem** — `.claude/agents/finalize-deliverable-packager.md`, `.claude/agents/shared-document-reviewer.md`, `.claude/agents/design-composer.md`, `.claude/skills/recipe-feature-pipeline/SKILL.md`, `.claude/skills/auditing-shared/scripts/` (new validator), `.claude/skills/**/*.md` (skill audit + remediation), `adrs/` (migration target + archival under `adrs/superseded/`), `working/feature/**/adrs/` (migration source), `working/feature/**/blueprint-v*.md` (cross-reference sweep, path-only), `working/feature/**/plan-v*.md` (cross-reference sweep, path-only), `Issues/**/*.md` (cross-reference sweep), `README.md` (cross-reference sweep). (IN SCOPE.)
- [ ] **Frontend** — N/A — out of scope.
- [ ] **Backend** — N/A — out of scope.
- [ ] **API** — N/A — out of scope.
- [ ] **Query / Data Access** — N/A — out of scope.
- [ ] **Database** — N/A — out of scope.
- [ ] **CI/CD (GitHub Actions)** — N/A — out of scope.
- [ ] **Infrastructure as Code** — N/A — out of scope.
- [ ] **Dev Environment (Codespaces / Devcontainer)** — N/A — out of scope.

**Deviation flag for downstream reviewers:** scope substantially broadened from the v1.1.0 proposal prediction (MINOR / 4–6 hours / single Phase 1) to v2.0.0 (FULL / multi-day / 7 phases). The layer remains **CC-only**: every touched surface sits within the Claude Code / Project Filesystem layer. The breadth of the touch within that single layer is materially larger than predicted (validator script, skill audit, repo-wide cross-reference sweep, multi-surface enforcement integration), but no new layer is added. PRD author and Architecture Auditor should treat the breadth as the deviation, not the layer count.

## Phase-Internal Boundaries (Preliminary)

Per the v2.0.0 binding user directive and the on-disk reality discovery. 7 phases plus standard rollout.

- **Phase 0 — Discovery + Setup.**
  - Enumerate all ADRs at all locations (canonical `adrs/`, every `working/feature/*/adrs/`, `adrs-migrated/`).
  - Classify each (duplicate-identical / duplicate-divergent / feature-scoped-only / legacy-archive).
  - Produce migration map (the source-of-truth input for Phase 2).
  - Sweep all cross-references; produce reference inventory (the source-of-truth input for Phase 3).
- **Phase 1 — Operator file repairs** (carried forward from v1.1.0, FR-1 through FR-5).
  - Sub-task: delete retired dual-location BLOCKER prose in `finalize-deliverable-packager.md:56–63`.
  - Sub-task: delete contradictory dual-location BLOCKER prose in `shared-document-reviewer.md:349`.
  - Sub-task: change the orchestrator-side `output_adrs_dir` resolution in `recipe-feature-pipeline/SKILL.md`.
  - Sub-task: change `output_adrs_dir` parameter description in `design-composer.md:48, :129, :187`.
- **Phase 2 — Migration** (FR-8).
  - **Phase 2a — Dedupe identicals** (FR-8a, 12 ADRs). Verify byte-equality per ADR; delete feature-scoped copy on confirm.
  - **Phase 2b — Reconcile divergent** (FR-8b, 3 ADRs). Design Composition proposes canonical body per case; archive rejected body to `adrs/superseded/`.
  - **Phase 2c — Relocate feature-scoped** (FR-8c, 5 ADRs). `git mv` to canonical; leave redirect notes in originating feature folders.
  - Each sub-phase has its own verification step.
- **Phase 3 — Cross-reference sweep** (FR-9). Apply path-only updates per the Phase 0 reference inventory.
- **Phase 4 — Validator + enforcement gates** (FR-10). Author the validator; wire into the orchestrator stage gate, the execution-pipeline specialist or hook, and the packager.
- **Phase 5 — Skill audit + remediation** (FR-11). Review every skill that documents or enables ADR authoring/placement; update prose or templates that could permit feature-scoped placement.
- **Phase 6 — Verification.**
  - Empirical confirmation: a fresh feature-pipeline run produces canonical-only ADRs.
  - Negative-path test: the validator blocks an attempted feature-scoped ADR write.
  - Cross-reference sanity: a final grep over the repository for known former paths returns zero matches (excluding redirect notes and audit trail).
- **Rollout — standard.**

**Deviation flag for downstream reviewers:** phase decomposition substantially expanded from v1.1.0's single mandatory Phase 1 (with conditional Phase 2). The v2.0.0 user directive forces 7 phases. PRD author MUST honor this decomposition; Plan author MUST decompose proportionally.

## Success Posture (Preliminary)

Success looks like: a fresh feature-pipeline run completes after this feature ships, writes any authored ADRs only to canonical-root `adrs/` without the orchestrator needing to pass an explicit `output_adrs_dir` override, and `finalize-deliverable-packager` reports zero ADR-placement BLOCKERs. The validator returns zero exit on the post-feature repository state (no placement violations remain) and returns non-zero on a deliberate negative-path test (an attempted feature-scoped ADR write), with all three enforcement surfaces blocking. Reading the touched operator files in sequence after this feature ships shows a single internally-consistent ADR-placement convention. A grep over the repository for known former feature-scoped paths returns zero matches (excluding redirect notes and audit trail). Every reviewed skill is either confirmed no-change or updated; no skill describes feature-scoped placement as a permitted path. The user knows the feature is done when (a) the AC suite above passes; (b) the next pipeline run that creates an ADR demonstrates the canonical-only default empirically; (c) the validator's negative-path test confirms structural enforcement; (d) the `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001 deferral is closeable; and (e) the skill audit findings are documented in the Blueprint with each remediation tracked as a Phase 5 task.

## Confirmation

The Intent Confirmation Gate (re-run for v2.0.0) executed at 2026-05-24T18:55Z. **Gate verdict: APPROVED with one Open Item override.**

- **Scope ratification**: user approved the v2.0.0 scope as-is (FULL scope class, 7 phases, FR-1 through FR-11 with FR-7 superseded, CC-only layer).
- **Open Item #2 (`adrs-migrated/`) — OVERRIDDEN**: user selected interpretation (a) — `adrs-migrated/` shall be **consolidated** into canonical `adrs/`. Final variants move to canonical with `-superseded` suffix; `-pre-naming-convention` and `-pre-template-migration` variants are deleted (Git history preserves them). This adds a **Phase 2d sub-phase** to the Migration phase. PRD author honors this as binding; Discovery enumerates the collision-resolution strategy.
- **Open Items #1, #3, #4, #5 — ride on defaults**. PRD-review and downstream gates (Blueprint Approval, Plan Approval) may revisit each.

`user_token` populated; status advanced to `approved`; downstream PRD authoring is unblocked.

## Open Items (Pending PRD Authoring)

The following five items remain genuinely open for the re-run Intent Confirmation Gate to confirm or override. The PRD author should treat each as an open item in the rationale brief.

1. **Divergent-body archival format (FR-8b).** Default: rejected body archived to `adrs/superseded/<id>-feature-scoped-body.md` with a provenance footer identifying the originating feature folder and the canonical-body decision rationale. Alternatives: (a) inline-supersession (rejected body appended to the canonical body in a `## Superseded variant` section); (b) deletion with Git-history-only preservation (no archival file); (c) `working/feature/<originating-slug>/adrs/superseded/` archival (closer to originating feature). Gate to confirm or override.
2. **`adrs-migrated/` interpretation (Q4).** ~~Default lean: interpretation (b)…~~ **RESOLVED at Intent Confirmation Gate (2026-05-24T18:55Z): interpretation (a) selected.** `adrs-migrated/` shall be **consolidated** into canonical `adrs/`. Final variants move to canonical with `-superseded` suffix; `-pre-naming-convention` and `-pre-template-migration` variants are deleted (Git history preserves them). This adds a **Phase 2d sub-phase** to the Migration phase. Discovery enumerates the collision-resolution strategy (likely no collisions because canonical `adrs/` currently lacks ADRs 0001–0010, the archive's primary content).
3. **Validator implementation surface (FR-10).** Default: Python script under `.claude/skills/auditing-shared/scripts/` with a CLI interface invoked by orchestrator, execution-pipeline hook, and packager. Alternatives: shell script (lower dependency); embedded in `auditing-shared` as a Python module; integrated as a hook rather than a standalone script. Discovery + Design Composition decides; gate may pre-empt.
4. **Cross-reference inventory completeness (FR-9).** Default: Phase 0 Discovery uses a known set of grep patterns (`adrs/ADR-NNNN`, `ADR-NNNN`, `[ADR-NNNN](path)`, `see ADR-NNNN`, etc.) to build the reference inventory. Open: confirmation that the pattern set captures every reference form in the repo (e.g., does it catch `<../adrs/ADR-NNNN.md>`? `ADR NNNN` with a space? frontmatter `supersedes:` fields?). Discovery surfaces edge cases; gate to confirm or override completeness criteria.
5. **Redirect-note format for relocated ADRs (FR-8c).** Default: a one-line markdown file in the originating feature folder (`working/feature/<slug>/adrs/ADR-NNNN.md`) containing only `# Moved\n\nThis ADR was relocated to canonical [adrs/ADR-NNNN.md](../../../adrs/ADR-NNNN.md) on 2026-05-24 per feature `adr-placement-mechanism-repair-r1`.` Alternatives: (a) delete the originating file entirely (no redirect); (b) a `.tombstone` file in a non-`.md` extension to bypass the validator allowlist concern; (c) symlink (filesystem-level redirect). Gate to confirm or override.

## Scope Deviation Notice (v1.1.0 → v2.0.0)

This re-author records a material scope deviation from the v1.1.0 document. The deviation is binding: the user issued a verbatim directive at the Intent Confirmation Gate following review of v1.1.0, which the orchestrator captured and the re-author is honoring as authoritative.

### What changed

| Dimension | v1.1.0 | v2.0.0 |
|---|---|---|
| **Scope class** | MINOR (~4–6 hours, single Phase 1) | FULL (multi-day, 7 phases) |
| **Q2 (migrate vs grandfather)** | Grandfather (leave 12 in-flight ADRs in place) | **Migrate** (dedupe 12 identicals, reconcile 3 divergent, relocate 5 feature-scoped) |
| **Q4 (`adrs-migrated/` disposition)** | Leave untouched | Default lean leave untouched (interpretation b), but cross-references reviewed; gate may override (Open Item #2) |
| **Q5 (shipped Blueprint cross-references)** | Treat as immutable (no edits) | Path-only edits allowed (semantic edits still out of scope) |
| **FR-7 (no new validator)** | In effect | **Superseded** by FR-10 (validator + enforcement gates) |
| **Q3 (ADR-0024 drift)** | Flag and defer | No longer flag-and-defer — migration directive forces semantic resolution (extends to newly-discovered ADR-0044, ADR-0045) |
| **Phase decomposition** | Single Phase 1 + optional Phase 2 (not triggered) | 7 phases (Phase 0 Discovery; Phase 1 Operator-file repairs; Phase 2a/2b/2c Migration; Phase 3 Cross-reference sweep; Phase 4 Validator + gates; Phase 5 Skill audit; Phase 6 Verification) |
| **FRs** | FR-1 through FR-7 | FR-1 through FR-11 (FR-7 superseded as a slot; FR-6 revised; FR-8, FR-9, FR-10, FR-11 added) |
| **Stakeholders** | 7 entries | 9 entries (originating feature authors of `frontend-design-knowledge-r1` and `issue-capture-mechanism-r1` added as informed) |
| **Layer scope** | CC-only (unchanged) | CC-only (unchanged); deviation flag now reads "breadth substantially broader within the single layer" |

### Why (verbatim user directive)

> "we need to migrate and ensure all references, paths and links all reference the new consolidated location. also the feature pipeline and execution pipeline need to be updated to ensure it adheres, enforcement gates and validates the correct location and references to ADRs. we also need to ensure all of our SKILLs are updated if required to prevent re-introducing the issue."

### What downstream PRD / Discovery should treat as binding vs open

**Binding (no re-elicitation):**
- The 7-phase decomposition.
- The FR-1 through FR-11 list (with FR-7 as a superseded slot).
- The CC-only layer scope.
- The three-fold enforcement surface for FR-10 (orchestrator gate + execution-pipeline hook + packager check).
- The FR-8 three-way migration decomposition (dedupe / reconcile / relocate) per on-disk reality.
- The Q1 outcome (parameter kept, canonical default, documented override).

**Open (subject to re-gate review):**
- The five Open Items above (#1 archival format, #2 `adrs-migrated/` interpretation, #3 validator surface, #4 cross-ref inventory completeness, #5 redirect-note format).

**Discovery should determine (not gate-decide):**
- The exact `output_adrs_dir` edit form in `recipe-feature-pipeline/SKILL.md` (the parameter currently has no stated default at SKILL.md:273; Discovery decides whether to add a stated default, introduce a resolution helper, etc.).
- The exact validator integration surface in the execution pipeline (which specialist? which hook?).
- The canonical-body selection per divergent ADR (0024, 0044, 0045) — Design Composition proposes; the proposal is reviewable by Architecture Auditor.
- The skill-audit findings per skill (no change vs update; what update).

## Provenance

- **Authoritative prior context source:** `Issues/adr-placement-rootcause/proposal.md` (status `adopted`, `adopted_by_feature_slug: adr-placement-mechanism-repair-r1`, `adopted_at: 2026-05-24`).
- **Companion analysis:** `Issues/adr-placement-rootcause/analysis.md` (the root-cause analysis the proposal escalates from, per ADR-0046 sibling-evolution).
- **Load-bearing ADR:** ADR-0036 (single-location ADR placement, accepted 2026-05-22) — the spec amendment this feature aligns the operators with and structurally enforces.
- **Empirical evidence cited (no re-elicitation):** `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001 (failure mode) and `execute-orchestrator-dispatch-mechanism-repair-r1` Gate-7 ratification (counter-demonstration).
- **Authored by:** `intake-intent-clarifier` (this sub-agent), 2026-05-24, run ID `adr-placement-mechanism-repair-r1-20260524-183201`.

### v1.1.0 → v2.0.0 transition

- **Predecessor version:** 1.1.0 (this same file, prior content; archived in Git history at the commit preceding the v2.0.0 re-author).
- **Binding user directive (verbatim, returned at the v1.1.0 Intent Confirmation Gate):**

  > "we need to migrate and ensure all references, paths and links all reference the new consolidated location. also the feature pipeline and execution pipeline need to be updated to ensure it adheres, enforcement gates and validates the correct location and references to ADRs. we also need to ensure all of our SKILLs are updated if required to prevent re-introducing the issue."

- **On-disk reality discovery (verified by the orchestrator before this re-author):** the proposal's "12 ADRs to migrate" framing was materially inaccurate. Actual state: 12 byte-identical duplicates (trivial dedupe — ADR-0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043); 3 divergent duplicates needing semantic resolution (ADR-0024 between root and `working/feature/frontend-design-knowledge-r1/adrs/`; ADR-0044 and ADR-0045 between root and `working/feature/issue-capture-mechanism-r1/adrs/`); 5 truly feature-scoped ADRs needing relocation (ADR-0046–0050, all from `working/feature/issue-capture-mechanism-r1/adrs/`); 47-file legacy archive at `adrs-migrated/` (ADRs 0001–0010 with `-pre-naming-convention`, `-pre-template-migration`, and final variants — disposition is Open Item #2). Canonical `adrs/` currently contains ADR-0007, ADR-0011 through ADR-0045 (36 files total).
- **Convention-deviation note for the v2.0.0 re-author:** the Intent Confirmation Gate elicitation that produced the v2.0.0 binding override was performed via the **orchestrator's** `AskUserQuestion`, not via this sub-agent's (`AskUserQuestion` is not in this sub-agent's allowlist). The v2.0.0 answers in the Clarifying Questions table are **binding**, not provisional — the gate elicitation already happened, and the user's directive is treated as authoritative. The five Open Items remain genuinely open for the **re-run** Intent Confirmation Gate that follows this v2.0.0 document.
- **Scope class transition:** MINOR → FULL. Flagged in the Layer Scope Declaration and the Scope Deviation Notice. The PRD author MUST honor the scope-class change in PRD frontmatter and in any Discovery / Design / Plan downstream scoping decisions.
