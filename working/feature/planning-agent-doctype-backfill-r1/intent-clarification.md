---
id: IC-planning-agent-doctype-backfill-r1
version: 1.0.0
status: draft
feature_slug: planning-agent-doctype-backfill-r1
scope_class: MINOR
user_token: <pending — orchestrator to generate at Intent Confirmation Gate>
generated: 2026-05-22T23:55:00Z
generated_by: claude (acting as intake-intent-clarifier; spawned from execution-pipeline-design-r1 Gate-6 disposition)
doc_type: intent-clarification
spawned_from:
  feature: execution-pipeline-design-r1
  artifact: working/feature/execution-pipeline-design-r1/plan-v2.md
  task: T6.1 (Posture-A defer disposition)
  gate: Gate 6 Final Approval (2026-05-22)
authoring_context: |
  This intent doc was authored at Gate-6 of `execution-pipeline-design-r1` to
  formalize the deferred T6.1 work (Posture A: defer the ~20+ planning-side
  agent doc_type backfill to a follow-on feature run). The user selected
  "create a new intent document following our document skills" at the Gate-6
  T6.1 disposition. This spawning is documented per ADR-0029 +
  ADR-0033 no-silent-scope-changes discipline: rather than silently absorb the
  deferred work or leave it implicit in execution-pipeline-design-r1's Open
  Items, the deferred work becomes a discoverable follow-on feature with its
  own intent doc at this canonical location.
---

# Intent Clarification: Planning-side agent `doc_type` frontmatter backfill (r1)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft.

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [ ] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

This feature retroactively backfills the `doc_type` frontmatter field across the ~20+ planning-side subagents that author pipeline artifacts. The field was made universal-required by ADR-0032 (Change 4) during the `execution-pipeline-design-r1` feature run. New artifacts (those authored post-ADR-0032) declare `doc_type` correctly. Existing planning-side agents (those authoring agents already in place pre-ADR-0032) do not emit `doc_type` in their authoring prompts; their next-authored artifacts would fail the FR-6 frontmatter validator at Gate 0.

This feature closes the gap by editing each planning-side agent's authoring prompt to emit `doc_type` correctly for the artifact type it produces.

## Source

This intent was spawned at Gate-6 Final Approval of `execution-pipeline-design-r1` (2026-05-22). The orchestrator surfaced T6.1 (the doc_type backfill task) as a USER-DECISION blocker per `tasks-summary.md` DC-1: "T6.1 Posture A (defer) vs Posture B (execute) for ~20+ planning-side agent doc_type backfill — without those edits, the next post-ratification feature run will trigger validator failures at Gate 0 for every artifact those agents author."

The user selected Posture A (defer) and chose to formalize the deferred work via a new feature intent document rather than carry it forward as an Open Item in `execution-pipeline-design-r1`. The user's response to the AskUserQuestion at the Gate-6 disposition step: "create a new intent document following our document skills."

## Initial Interpretation

The execution-pipeline-design-r1 run introduced ADR-0032 Change 4: a universal-required `doc_type` field across all pipeline artifacts. Planning-side subagents authored before ADR-0032 do not emit this field. The remediation is a mechanical edit to each affected agent's authoring prompt: add a `doc_type: <type>` line to the frontmatter section the agent constructs when authoring its assigned artifact type.

The work is NOT architectural (no new decisions; ADR-0032 already made the decision). It is execution: enumerate the agents, edit each authoring prompt, verify the FR-6 frontmatter validator passes against newly-authored artifacts from each.

## Clarifying Questions and Answers

Posture-A defer disposition was decided at parent feature's Gate-6; the open intent-clarification questions are about scope and execution mechanics, not the decision itself. Default answers below were taken from the parent feature's context; the user should confirm or amend at Intent Confirmation Gate.

| # | Ambiguity | Question Asked | Default Answer (User to Confirm) | Resolved? |
|---|---|---|---|---|
| 1 | Whether the scope is fixed to ~20+ planning-side agents or also includes any execution-side agents | Implicit from parent context | Scope is planning-side only. Execution-side agents are not yet created (they are designed in execution-pipeline-design-r1's Plan v2 Phase 3 and will be authored with `doc_type` from inception per the Plan). | [ ] (confirm at gate) |
| 2 | Whether each agent's authoring prompt needs full review or just frontmatter edit | Implicit from parent context | Frontmatter edit only — minimal change to each agent's authoring prompt to emit `doc_type`. Full review out of scope. | [ ] (confirm at gate) |
| 3 | Whether the scope class for this feature is MINOR or PATCH | Per ADR-0023 + deliverable-archive-spec | MINOR — new sub-agent edits affect multiple agents but are backward-compatible extensions to existing surfaces; no architectural decision required. Per the spec, MINOR may skip Discovery / Research / Synthesis (no new requirements; ADR-0032 already documents them). | [ ] (confirm at gate) |
| 4 | How to verify completeness | Implicit from parent context | Run the FR-6 frontmatter validator (`auditing-shared/scripts/validate_pipeline_frontmatter.py` per execution-pipeline-design-r1 Plan v2 T1.1) against a sample artifact from each backfilled agent; assert no `doc_type_missing` finding. | [ ] (confirm at gate) |
| 5 | Whether to enumerate the affected agents in this intent doc or defer to PRD/discovery | Best practice | Enumerate at PRD time using `grep -L 'doc_type:' .claude/agents/*.md` filtered to planning-side. The ~20+ figure from execution-pipeline-design-r1's Blueprint Change Impact Map is approximate. | [ ] (confirm at gate) |
| 6 | Whether to author this run before or after the execute-* agents (Phase 3 of execution-pipeline-design-r1's Plan v2) are built | Implicit | Independent — this backfill operates on planning-side agents that already exist. Can run in parallel with execution-pipeline-design-r1 implementation. | [ ] (confirm at gate) |

## Clarified Intent

Backfill the `doc_type` frontmatter field across all planning-side subagents in `.claude/agents/` whose authoring prompts produce pipeline artifacts (PRD, Blueprint, Plan, etc.). The backfill is mechanical: for each affected agent, edit its authoring prompt to emit `doc_type: <type>` per ADR-0032 Change 4. Verify via the FR-6 frontmatter validator from `execution-pipeline-design-r1` (when that validator becomes operational; if it has not yet been implemented at the time this feature runs, surface that as an external dependency and address by manual frontmatter inspection).

The work is scoped MINOR per ADR-0023: backward-compatible extension to existing surfaces, no architectural decisions, Discovery / Research / Synthesis can be skipped (the architectural decision was made in ADR-0032 during the parent feature run).

## Scope Posture

### What's in scope

- Enumeration of planning-side subagents whose authoring prompts emit pipeline-artifact frontmatter (likely ~20+ agents per execution-pipeline-design-r1's Blueprint Change Impact Map).
- Edit each enumerated agent's authoring prompt to emit `doc_type: <type>` for the artifact type it produces. Mapping table from agent → doc_type included in the PRD.
- Verification via FR-6 frontmatter validator OR (if that validator is not yet operational) manual frontmatter inspection of a sample artifact from each backfilled agent.
- Single PR / single commit-set per affected agent (or batched into a small set of PRs by agent family). ADR-0005 supersession does not apply because agent files are not pipeline artifacts; they are configuration files and edited in-place.

### What's NOT in scope (explicitly excluded)

- Any architectural decision. ADR-0032 Change 4 already decided `doc_type` is universal-required; this feature implements it for planning-side agents only.
- Changes to the `doc_type` taxonomy. The enum (per ADR-0032) is fixed by that ADR.
- Net-new agents. This feature only edits existing planning-side agents.
- Execution-side agents (`execute-orchestrator`, `execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`). Those are authored by `execution-pipeline-design-r1`'s Plan v2 Phase 3 with `doc_type` already in place per their authoring spec.
- Backfill of `doc_type` in historical artifacts (already-authored PRD / Blueprint / Plan files in prior feature archives). Per ADR-0036's backward-compat pattern, historical artifacts are not retroactively cleaned.
- Synthesis-pipeline agents (`synth-*`) if they emit synthesis-specific artifacts that aren't subject to the feature-pipeline frontmatter discipline. The PRD enumeration step disambiguates.

### What's undecided (deferred to PRD or later)

- The exact list of planning-side subagents affected. The PRD author enumerates via `grep -L 'doc_type:' .claude/agents/*.md`.
- The exact `doc_type` value for each agent's authored artifact type. Most are obvious (intake-prd-author → `prd`; plan-author → `plan`; design-composer → `blueprint`) but some are ambiguous (e.g., what `doc_type` does `shared-document-reviewer` emit for review reports? what does `finalize-reconciler` emit for its reconciliation logs?). The PRD resolves these from ADR-0032's `doc_type` taxonomy.
- Whether to batch the edits into a single PR or per-agent PRs.

## Stakeholder Posture (Preliminary)

- **User (project owner):** wants planning-side agents to comply with the universal-required `doc_type` field so the next feature run does not trip the frontmatter validator at Gate 0.
- **`execution-pipeline-design-r1` Plan v2 T6.1 (deferred):** this feature's existence is the Posture-A disposition for that deferred task; closure of this feature closes the deferral.
- **Future feature pipeline runs:** they benefit from validator-passing planning-side agents; without this backfill, the FR-6 validator surfaces `doc_type_missing` BLOCKER on every new pipeline artifact.
- **Frontmatter validator (FR-6 from parent feature):** this is the audience that consumes the backfilled `doc_type` field. The validator's correctness depends on the field being present.

## Success Posture (Preliminary)

The feature is "working" when (a) every planning-side subagent's authoring prompt emits `doc_type: <appropriate-value>` for the artifact type it produces; (b) the FR-6 frontmatter validator (or manual inspection) confirms each backfilled agent's next-authored artifact passes the `doc_type_present` check; (c) the next live feature pipeline run does not surface any `doc_type_missing` finding from a planning-side agent. The closure is mechanical and verifiable.

## Confirmation

Pending Intent Confirmation Gate. User to confirm by saying "approve" (or equivalent) — orchestrator will then generate `user_token` and stamp the frontmatter, and the document advances to PRD Authoring.

## Open Items (Pending PRD Authoring)

- **Enumerate affected agents.** PRD author runs `grep -L 'doc_type:' .claude/agents/*.md` (or analogous) and filters to planning-side agents whose authoring prompts emit pipeline-artifact frontmatter. The output is the per-agent backfill list.
- **Map agent → doc_type value.** PRD author authors a table mapping each enumerated agent to the `doc_type` value its artifact requires per ADR-0032 Change 4.
- **Decide PR batching strategy.** PRD author surfaces single-PR-vs-batched-PR options for the user to pick at the PRD Approval Gate.
- **Validator dependency.** PRD author confirms whether FR-6 from `execution-pipeline-design-r1` is operational at the time this feature runs. If not, the PRD specifies the fallback verification method (manual frontmatter inspection of a sample artifact from each agent).
- **Cross-feature coordination.** This feature can run independently of `execution-pipeline-design-r1`'s implementation, but its closure removes the "validator-failure cascade" risk surfaced as T6.1's downstream-consequence note. The orchestrator should sequence this feature's run to land before the first post-`execution-pipeline-design-r1` feature pipeline invocation.
