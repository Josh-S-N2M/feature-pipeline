---
id: ADR-0028
title: Skill-design fixes shipped in v4.5.0 — closes ADR-0027
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0023, ADR-0027]
---

# ADR-0028: Skill-design fixes shipped in v4.5.0

## Context

ADR-0027 (authored in v4.4.2) documented three pipeline skill-design issues that compound to produce the gap observed in v4.4.0 and v4.4.1: planning artifacts didn't land in the deliverable archive. This ADR documents the v4.5.0 implementation that closes ADR-0027.

Two spot-issues surfaced during execution and are also documented here.

## What changed

### Change 1: Working-directory precondition (closes ADR-0027 Issue 1)

**File:** `.claude/skills/recipe-feature-pipeline/SKILL.md`

**Edits:**

- New section "Working-directory precondition" after "Execution Contract" — documents the `cwd == repo-root` requirement with rationale referring to ADR-0027.
- Stage 1 procedure extended with step 0: precondition check (verify `cwd / ".claude"` exists; halt with named error if absent).
- Orchestrator description updated: "Thirteen-stage" (was "Twelve-stage"); "Requires `cwd == repo-root` precondition" added.

### Change 2: Deliverable-archive packager agent (closes ADR-0027 Issue 2)

**New file:** `.claude/agents/finalize-deliverable-packager.md`

Scope: verifies `working/feature/<slug>/` contains the expected artifact set per scope class; invokes `shared-document-reviewer` with `doc_type: DeliverableArchive`; optionally drafts versioned handoff documents; emits `packager-report.json` with PASS / BLOCK / REVIEW verdict.

**Orchestrator edits:** Stage 14 (Step 14) added after Task Decomposition (Step 13). New stage invokes the packager before Gate 6.

The packager is intentionally lightweight: it REPORTS gaps rather than retroactively filling them. Backfilling artifacts requires re-running upstream stages — a deliberate human decision, not an automated repair.

### Change 3: Deliverable-archive validator (closes ADR-0027 Issue 3)

**File:** `.claude/agents/shared-document-reviewer.md`

**Edits:**

- `doc_type` taxonomy comment extended with `DeliverableArchive`.
- Input parameters section updated: `doc_type` enum extended; new `scope_class` parameter added (used only for DeliverableArchive reviews).
- New "DeliverableArchive Review (v4.5.0+)" section added before "Template References" documenting the invocation pattern, procedure (6 steps), and output format.

### Change 4: Expected-artifact spec (supporting infrastructure)

**New file:** `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md`

Documents the canonical expected-artifact set per scope class (FULL / MINOR / PATCH per ADR-0023). 9 sections including: scope classes overview, per-class artifact tables, versioning convention, ADR placement, handoff document convention, patterns/anti-patterns, cross-references.

## Spot-issues discovered during execution

### Spot-issue 1: Backward-compat for pre-v4.5.0 archives

**Problem.** During retroactive validation (T-6) of v4.4.2's `frontend-design-knowledge-r1` archive, the validator flagged `packager-report.json` as missing. The artifact is required for new runs (v4.5.0+) but doesn't exist in archives created before v4.5.0.

**Resolution.** Spec extended with a "Backward-compat note" stating: archives whose checkpoint shows completion pre-v4.5.0 are exempt from `packager-report.json` (treated as MINOR not BLOCKER). New runs post-v4.5.0 enforce the requirement at BLOCKER.

### Spot-issue 2: scope_class declaration absent in pre-v4.5.0 intent-clarifications

**Problem.** Older `intent-clarification.md` files don't have `scope_class:` in their frontmatter — the convention was introduced in v4.5.0. The validator requires this field to determine which expected-artifact set applies.

**Resolution.** Spec extended with an "Inference fallback" section: when `scope_class:` is absent, infer it from archive contents (research-plan + synthesis → FULL; layer-design without research-plan → MINOR; otherwise PATCH). Inferred scope reported as MINOR finding so future runs declare explicitly.

A separate cleanup observation: the v4.4.1 `intent-clarification.md` was authored in v4.4.2 (after ADR-0027 was already known). I should have included `scope_class:` from the start. Corrected during this execution; no append-only concern since v4.4.1's intent-clarification was less than 1 day old.

## Validation evidence

### AC-1, AC-2 (orchestrator precondition)

```
$ grep -nE 'Working-directory precondition|cwd MUST equal|ADR-0027|Precondition check' .claude/skills/recipe-feature-pipeline/SKILL.md
```

Returns 4+ lines covering the new section + Step 1 step 0 + rationale.

### AC-3, AC-4 (packager exists + documented)

`.claude/agents/finalize-deliverable-packager.md` exists; frontmatter parses; all 7 body sections present (Inputs, At task start, Procedure, Optional handoff drafting, Outputs, Failure modes, Related agents).

### AC-5 (orchestrator invokes packager)

Step 14 (Stage 13: Deliverable Packaging) added to orchestrator with explicit `finalize-deliverable-packager` invocation.

### AC-6, AC-7 (validator extension)

`shared-document-reviewer.md` `doc_type` taxonomy extended; new "DeliverableArchive Review" body section added with 6-step procedure.

### AC-8, AC-9 (spec exists with FULL/MINOR/PATCH sections)

`deliverable-archive-spec.md` exists with `## Contents` H2 and three `### FULL`/`### MINOR`/`### PATCH` subsections plus surrounding scope-class taxonomy section.

### AC-10 (retroactive FULL-scope archive validates)

Manual validation of `working/feature/frontend-design-knowledge-r1/` against FULL-scope expected set: 16/16 required artifacts present, ADR cross-location verified, 6/6 research notes present. Verdict: PASS (with one MINOR — packager-report.json absent under backward-compat exemption).

### AC-11 (retroactive PATCH-scope archive validates)

Manual validation of `working/feature/audit-machinery-fixes-r1/` against PATCH-scope expected set: 6/6 required artifacts present, ADR cross-location verified, scope_class now declared (after spot-issue 2 resolution). Verdict: PASS.

### AC-12 (this ADR)

This document.

## Consequences

**Carried-forward convention.** Going forward, every feature run's `intent-clarification.md` must declare `scope_class:` in frontmatter. This is the discipline floor for ADR-0028's validator to function precisely.

**Project version bump.** v4.4.2 → v4.5.0 (MINOR). Justified by:

- New public sub-agent (`finalize-deliverable-packager`).
- Extension of existing sub-agent surface (`shared-document-reviewer` with new `doc_type`).
- Extension of orchestrator's stage sequence (Stage 13 added).
- New reference file in `KB-documentation-criteria`.

No breaking changes; existing artifacts validate (with backward-compat exemption for `packager-report.json`).

**Sub-agent count.** Project moves from 27 sub-agents to 28 (added `finalize-deliverable-packager`).

**Validator integration in future runs.** Stage 13 (Deliverable Packaging) is mandatory for v4.5.0+ runs. Even small runs benefit from the validator's discipline check; the cost is one Stage-13 invocation per run.

## Notes

The two spot-issues (backward-compat + scope_class inference) are exactly the kind of finding that surfaces only during retroactive validation against real archives. Implementing the spec without testing against existing data would have shipped a spec that demanded artifacts older archives don't have. The discovery is the value of retroactive validation; it should be standard practice for every machinery feature.

One other observation worth recording: the packager's "optional handoff drafting" responsibility addresses the fourth concern raised in ADR-0027's notes section (no agent owns handoff documents). Folding this into the packager rather than creating a separate agent keeps the surface compact — the packager already runs at the right point in the sequence and has the right context.

## Addendum: auditor parser fix (discovered during v4.5.0 closeout)

When `finalize-deliverable-packager.md` was first authored with `tools:` declared as a YAML flow-sequence (`tools: [Read, Glob, Grep, Write, TaskCreate, TaskUpdate]`), the project's audit re-run flagged a MAJOR finding: "Body references tools ['Read'] not in declared `tools:` list."

Investigation showed the auditor's `parse_tools_from_frontmatter` in `auditing-subagents/scripts/analyze_subagent.py` handled only two of three YAML list shapes:

1. Inline comma-separated: `tools: A, B, C` — handled
2. Block sequence: `tools:` followed by `  - A` / `  - B` lines — handled
3. Flow-sequence (bracketed): `tools: [A, B, C]` — **not handled**; the literal brackets were retained, producing tool names like `[Read` and `TaskUpdate]` that didn't match body references.

**Fix.** Extended `parse_tools_from_frontmatter` to strip the brackets when present before splitting on commas. Three-line change at `analyze_subagent.py:65-68`.

**Impact.** The fix eliminated **28 MAJOR false-positive findings** across the project (from 70 to 42 MAJORs). Every agent file using the bracketed `tools:` syntax had been false-flagged for one or more body-referenced tools. The new `finalize-deliverable-packager.md` was the trigger but the fix cleared latent false positives that had been accumulating across the existing 27 agents whenever any of them used the bracketed form.

**Discipline carried forward.** New agent files may use either comma-separated OR bracketed YAML syntax; both now parse correctly. For project consistency, comma-separated remains the convention (matches the 23 existing agents that use it). `finalize-deliverable-packager.md` was normalized to comma-separated during the fix.

**Why this isn't a new ADR.** The auditor parser bug surfaced as a direct consequence of v4.5.0's new file and was fixed as part of the same execution. ADR-0028 documents v4.5.0's scope completely; the parser fix is part of that scope by the same logic that puts the orchestrator edit in ADR-0028 rather than a separate ADR.

**Remaining genuine finding.** `review-cross-artifact-auditor.md` body references `Bash` but doesn't declare it in `tools:` — a pre-existing, genuine MAJOR finding now visible after the false positives cleared. Defer to a future small fix or absorb into v4.6.0's scope.

