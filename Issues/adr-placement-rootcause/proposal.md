---
id: PROPOSAL-adr-placement-rootcause
version: 0.2.0
doc_type: issue-proposal
status: adopted
feature_slug: devcontainer-mcp-provisioning-r1
generated: 2026-05-24
generated_by: claude (orchestrator) — promotion-prep from sibling analysis
proposes_future_feature: adr-placement-mechanism-repair-r1
# --- status: adopted companion fields (per spec §6 D-05 table) ---
since: 2026-05-24
adopted_by_feature_slug: adr-placement-mechanism-repair-r1
adopted_at: 2026-05-24
# --- Optional cross-link fields (per ADR-0046 / spec §5) ---
escalates_from: ANALYSIS-adr-placement-rootcause
# escalated_to: <none — this is the head of the evolution chain for this topic>
# rolled_into_register: <none>
---

# Proposal — Repair the ADR Placement Mechanism Per ADR-0036

## Contents

- [x] TL;DR
- [x] Proposed Feature
- [x] Motivation
- [x] Open Questions
- [x] Scope Considerations
- [x] Cross-links

## TL;DR

ADR-0036 (single-location ADR placement, accepted 2026-05-22) was a partial amendment: the spec was updated but the four operator files that enforce ADR placement (orchestrator, design-composer, packager, reviewer) still carry retired dual-location prose, and the orchestrator/composer defaults still compute to the feature-scoped path. Two empirical runs have demonstrated both the failure mode (`devcontainer-mcp-provisioning-r1` Gate-6 BLOCKER) and the counter-demonstration (`execute-orchestrator-dispatch-mechanism-repair-r1` ratified canonical-only at Gate-7 and shipped clean). The remaining gap is now small and surgical — 2 file-text deletions, 2 default-value changes, and a Blueprint misreading correction. This proposal seeds **`adr-placement-mechanism-repair-r1`** to close that gap.

## Proposed Feature

**Suggested slug:** `adr-placement-mechanism-repair-r1`
**Scope class:** MINOR (per [analysis.md](analysis.md) §10 re-scope; estimated 4–6 hours of work).
**Layers touched:** Claude Code / Project Filesystem only (`.claude/agents/`, `.claude/skills/recipe-feature-pipeline/`).

The future run produces a small, well-defined set of edits that bring the four operator files into alignment with the spec ADR-0036 already enforces:

- **Delete the retired dual-location BLOCKER prose** in `.claude/agents/finalize-deliverable-packager.md` lines 56–63 (Causal Site 3 of the analysis).
- **Delete the contradictory dual-location BLOCKER prose** in `.claude/agents/shared-document-reviewer.md` line 349, leaving only the post-ADR-0036 statement at lines 470–472 (Causal Site 4).
- **Change the orchestrator default** so that `output_adrs_dir` resolves to canonical-root `adrs/` rather than the feature-scoped path that the "everything under `working/feature/<slug>/`" convention currently produces (Causal Site 1 — `recipe-feature-pipeline/SKILL.md` lines 17–28 + 228).
- **Change the design-composer default** to match, with explicit ADR-0036 cross-reference in the parameter description (Causal Site 2 — `design-composer.md` lines 48, 129, 187).
- **Decide whether `output_adrs_dir` remains a parameter** (test-only override) or is eliminated entirely. Recommendation lean: keep as parameter, hard-code the default, document the override case.
- **Author a Blueprint that documents the disposition** for existing feature-scoped ADRs (the 12 listed in analysis §1.1) — leave in place per ADR-0036's grandfather clause, OR migrate to canonical with provenance footer. Hygiene-only, not blocking.
- **Optionally** reconcile the ADR-0024 drift between root and `frontend-design-knowledge-r1/adrs/` (the only confirmed drift case). Reconciliation requires semantic judgment about which body is canonical; the feature may flag this for a follow-up rather than absorb it.
- **Optionally** decide the `adrs-migrated/` disposition (ADRs 0001–0018 at non-canonical path). Same trade-off as the in-flight feature-scoped copies.

The deliverables are surgical text edits and a small Blueprint; no new ADRs are likely (the feature ratifies existing ADR-0036 rather than proposing new policy), but design-composer may author one if the parameter-vs-hard-code question demands it.

## Motivation

The empirical evidence is dual:

1. **`devcontainer-mcp-provisioning-r1` Gate-6 BLOCKER** (PKG-BLOCKER-001) — 7 ADRs (ADR-0037..ADR-0043) shipped only at the feature-scoped path; the packager's still-retired check fired; user disposition was "defer to a pipeline-fix follow-up feature." That deferral is this proposal.

2. **`execute-orchestrator-dispatch-mechanism-repair-r1` empirical counter** — the user ratified ADR-0036-canonical at Gate 7, the parent orchestrator explicitly passed `output_adrs_dir=/workspaces/feature-pipeline/adrs/`, ADR-0044 and ADR-0045 were written to canonical root, and the packager PASSED (25/25 artifacts; 0 BLOCKER). The packager agent's runtime spec-discretion saved this run, but the discretion is fragile — it depends on the packager reading the spec each run.

If the gap remains unaddressed:

- Every future feature run is one operator-attention-lapse away from re-triggering PKG-BLOCKER-001.
- The `output_adrs_dir` parameter has no in-pipeline default that conforms to ADR-0036; the next feature run that does not explicitly opt in at Gate-7 lands in the feature-scoped path again.
- The reviewer file remains self-contradicting (line 349 retired-rule vs. lines 470–472 amended-rule); whichever check fires first determines the verdict.
- The phantom-promotion phrase invented at `devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226` may propagate into future Blueprints as readers reach for it as precedent.

The full root-cause analysis lives at [analysis.md](analysis.md). The four staleness mechanisms (authoritative-state drift, supersession invisibility, numbering-collision risk, phantom-promotion blocks closure) are enumerated there with file:line evidence.

## Open Questions

- [ ] **Q1 (Parameter vs. hard-code)**: Should `output_adrs_dir` remain a parameter (test-only override preserved) or be eliminated entirely (canonical root hard-coded in `design-composer.md`)? Trade-off: flexibility for tests vs. drift prevention. Recommendation lean from the analysis: hard-code with a documented test-only override mechanism. The feature pipeline's Discovery + Design stages should make the final call.
- [ ] **Q2 (Migrate or grandfather)**: Do the 12 existing feature-scoped ADRs (per analysis §1.1) get migrated to canonical root as part of this feature, or treated as historical-only? The spec grandfathers pre-amendment archives, so leaving them is spec-compliant; migration is hygiene. Migrating requires deciding what to do with the working-directory references that the originating features still emit in their artifacts.
- [ ] **Q3 (ADR-0024 drift)**: Does this feature reconcile the confirmed drift between [adrs/ADR-0024-*.md](../../adrs/) and [working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md](../../working/feature/frontend-design-knowledge-r1/adrs/) by picking a canonical body, or flag-and-defer? Reconciliation requires semantic judgment about which body is project-canonical. Recommendation lean: flag and defer; reconciliation is a separate decision.
- [ ] **Q4 (`adrs-migrated/` disposition)**: Leave the legacy archive in place, or move ADRs 0001–0018 into `adrs/` to fully honor single-location? Same trade-off shape as Q2.
- [ ] **Q5 (Blueprint misreading clean-up)**: Should this feature reach into `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md` (a shipped artifact) and amend the misreading at line 1226, or treat shipped feature artifacts as immutable historical records? Recommendation lean: leave shipped Blueprints alone; the fix is at the agents/skill level so future Blueprints don't repeat the misreading.

## Scope Considerations

**In-scope (proposed):**
- Delete retired dual-location BLOCKER prose in `finalize-deliverable-packager.md:56–63`.
- Delete contradictory dual-location BLOCKER prose in `shared-document-reviewer.md:349`.
- Change `output_adrs_dir` resolution default in `recipe-feature-pipeline/SKILL.md:17–28` and `:228` to canonical-root.
- Change `output_adrs_dir` parameter description in `design-composer.md:48`, `:129`, `:187` to reference ADR-0036 and document the canonical default.
- Author a Blueprint documenting the in-flight feature-scoped ADR disposition (12 files; leave-grandfathered vs. migrate).

**Out-of-scope (proposed):**
- Authoring a "promotion" mechanism (explicitly ruled out — canonical-only is the end-state per ADR-0036).
- Mutating shipped feature Blueprints to remove the phantom-promotion misreading (treated as immutable historical records).
- Reconciling ADR-0024's drifted body (deferred; requires semantic judgment).
- Restructuring `adrs-migrated/` (deferred; same trade-off shape).
- Promotion-step automation, ADR cross-location validators, or any new schema.

**Deferred / conditionally in-scope:**
- If Q1 resolves to hard-code-with-override, the override surface (env var? CLI flag? test-fixture-only?) becomes part of this feature's scope.
- If Q2 resolves to migrate, the relocation of the 12 in-flight feature-scoped ADRs becomes a Phase task with explicit `git mv` operations and provenance footers.
- The 5-state lifecycle of this proposal will transition `draft → open` on user review and `open → adopted` when the feature pipeline starts the run (consuming this file as `--raw-request`).

## Cross-links

- **Escalates from**: [analysis.md](analysis.md) — the root-cause analysis this proposal promotes into the feature pipeline (ADR-0046 sibling-evolution).
- **Escalated to**: (none — this is the head of the evolution chain for this topic; the feature pipeline run will consume this file directly).
- **Companion artifacts**:
  - [adrs/ADR-0036-single-location-adr-placement.md](../../adrs/ADR-0036-single-location-adr-placement.md) — the load-bearing spec amendment
  - [working/feature/devcontainer-mcp-provisioning-r1/](../../working/feature/devcontainer-mcp-provisioning-r1/) — the originating feature run; PKG-BLOCKER-001 lives in `packager-report.json`
  - [working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/](../../working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/) — the empirical counter-demonstration; ADR-0044 and ADR-0045 shipped to canonical root
- **Related ADRs**:
  - ADR-0036 (single-location ADR placement) — the spec this proposal aligns the operators with
  - ADR-0045 (three doctypes preserved) — taxonomy this file conforms to
  - ADR-0046 (sibling evolution `escalates_from` / `escalated_to`) — the cross-link with the analysis
  - ADR-0050 (5-state lifecycle vocabulary; per-state companion fields) — the state vocabulary
- **Structural spec**: [.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md](../../.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md) — full per-state companion-field table and doctype vocabulary.

## Adoption

To turn this proposal into the seeded feature pipeline run once it is reviewed:

```
<recipe-feature-pipeline-skill>  adr-placement-mechanism-repair-r1  --raw-request  Issues/adr-placement-rootcause/proposal.md
```

The Feature Pipeline's `intake-intent-clarifier` should:

1. Read this proposal file (detects `doc_type: issue-proposal`).
2. Treat the body as authoritative prior context — do NOT re-elicit the rationale, the four causal sites, the empirical evidence from the two prior runs, or the in-scope/out-of-scope split (all decided in the sibling analysis).
3. Ask clarifying questions ONLY about:
   - The five Open Questions (Q1–Q5) above.
   - Formal Functional Requirements + EARS Acceptance Criteria.
   - Stakeholder posture table.
   - Layer-Scope declaration (predicted: CC-only).
   - Phase-internal boundaries (predicted: a single Phase 1 covers the surgical edits, with optional Phase 2 for hygiene migration if Q2 resolves "migrate").

## Provenance

- **Authored**: 2026-05-24 by Claude (orchestrator) at user request, as the promotion-prep companion to [analysis.md](analysis.md).
- **Authored against templates ratified in `issue-capture-mechanism-r1` Phase 1** (commit `82abdd8`): `issue-proposal-template.md` + `issue-doctypes-spec.md`. This file is the second dogfood instance of the new templates (after [Issues/cross-artifact-divergence-detection-gap/analysis.md](../cross-artifact-divergence-detection-gap/analysis.md)).
- **Lifecycle**: starts at `status: draft` per template; advances to `open` on user review; advances to `adopted` (with `adopted_by_feature_slug: adr-placement-mechanism-repair-r1`) when the feature pipeline starts the run.
