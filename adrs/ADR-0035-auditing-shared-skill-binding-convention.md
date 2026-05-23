---
id: ADR-0035
title: Auditing-shared Skill-binding convention for execution-phase agents
status: accepted
date: 2026-05-22
accepted: 2026-05-22
deciders: [user, claude (as design-composer)]
supersedes: []
superseded_by: []
related: [ADR-0029, ADR-0031, ADR-0032]
authored_in_feature: execution-pipeline-design-r1
pairs_synthesis_decisions: []
subsumes: []
change_summary: |
  Ratifies the convention that execution-phase agents materially depending on
  multiple auditing-shared scripts MAY bind auditing-shared in their skills:
  frontmatter field (loading SKILL.md as context) in addition to invoking its
  scripts via Bash. Opt-in for cross-cutting helper-home skills; not mandatory.
---

# ADR-0035: Auditing-shared Skill-binding convention for execution-phase agents

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Proposed — 2026-05-22

Pending Architecture Audit (Gate 4) acceptance. On gate-pass the status advances to `accepted` per ADR-0032's per-doc-type ADR vocabulary.

## Context

ADR-0031 (`auditing-shared-skill-module.md`) established `auditing-shared` as the canonical-helper-home for cross-cutting audit/validation/log scripts (e.g., `validate_frontmatter.py`, `audit_helpers.py`). ADR-0031's scope is **module organization** — where the scripts live — and is silent on **how downstream agents bind to it**.

Pre-existing practice (pre-this-feature): planning-side agents that touched auditing-shared scripts invoked them via Bash only. None bound `auditing-shared` as a Skill in their `skills:` frontmatter field. The `.claude/agents/finalize-reconciler.md` planning-side agent is the precedent: it has `skills: [KB-review-disciplines, KB-documentation-criteria]` and invokes auditing-shared scripts via Bash when needed, without binding the SKILL.md as context.

This feature's execution-side design (`cc-design.md` v1.0.0, reviewer_verdict=approved) introduced a divergent pattern. Four execution-phase agents materially depend on **multiple** auditing-shared scripts each, and binding the SKILL.md as context (in addition to Bash invocation) provides the agent with the conceptual model of the shared utilities — meaningfully helpful when the agent must orchestrate or interpret outputs from several scripts. The four agents:

| Agent | Auditing-shared scripts materially depended on |
|---|---|
| `execute-orchestrator` | `log_state_transition.py`, `validate_pipeline_frontmatter.py`, `check_pipeline_discipline.py`, `run_phase_checks.py`, `detect_stubs.py` (5 scripts) |
| `execute-task-quality-handler` | `detect_stubs.py`, plus acceptance-test runners and per-task validators delegated via auditing-shared (2+ scripts) |
| `execute-phase-quality-reviewer` | `run_phase_checks.py` (which fans out to multiple auditing-* families), `validate_pipeline_frontmatter.py`, `check_pipeline_discipline.py` (3+ scripts) |
| `execute-finalize-reconciler` | dispatch-matrix discipline + cycle-counter tracking depend on the shared dispatch artifacts authored under auditing-shared (effectively 2+ scripts, via dispatch protocol) |

Blueprint v4's convention note 1 (§Agent Frontmatter Specifications) explicitly surfaces the deviation per ADR-0029 + ADR-0033: "This feature establishes a new convention. The execute-orchestrator, execute-task-quality-handler, execute-phase-quality-reviewer, and execute-finalize-reconciler bind auditing-shared in their skills: field. Existing planning-side agents do not — they invoke auditing-shared scripts via Bash only and never load its SKILL.md as context." The surfacing is necessary per ADR-0029 but, as the round-6 architecture audit's finding I-AA-603 identified, **not sufficient** when the deviation is a project-wide convention change affecting how future agents bind to a cross-cutting helper-home skill. Per the established pattern (ADR-0011 for KB-structure conventions; ADR-0019 for naming conventions; ADR-0031 for canonical-helper-home placement), cross-feature shared-conventions changes warrant an ADR ratification.

ADR-0032's enumerated five Change categories (universal frontmatter fields; user-token chain; per-doc-type state vocabulary; doc_type taxonomy; execution-phase artifact frontmatter section) do not cover skill-binding conventions. The reconciliation cycle 3 explicit decision D-RC3-2 chose to author a **new** ADR rather than fold a sixth change into ADR-0032 — preserving ADR-0032's framing and honoring the one-decision-per-ADR pattern established by the ADR-0029 / ADR-0033 split (where ADR-0033 extends ADR-0029 rather than supersedes it).

## Decision

**Execution-phase agents that materially depend on multiple `auditing-shared` scripts MAY bind `auditing-shared` in their `skills:` frontmatter field** (loading SKILL.md as context) in addition to invoking scripts via Bash. Agents that invoke a single auditing-shared script via Bash MUST NOT bind unless the conceptual-model context is clearly load-bearing. The convention is **opt-in for cross-cutting helper-home skills; not mandatory.**

The four agents authored by this feature that exercise the convention are:

1. `execute-orchestrator`
2. `execute-task-quality-handler`
3. `execute-phase-quality-reviewer`
4. `execute-finalize-reconciler`

When an agent exercises this convention, its frontmatter or accompanying rationale MUST declare the helper-procedure use case explicitly (e.g., "auditing-shared bound because agent orchestrates N scripts and needs the shared conceptual model"). The Blueprint's §Agent Frontmatter Specifications subsection is the canonical home for this declaration.

## Decision Details

| Item | Content |
|---|---|
| Decision | Execution-phase agents materially depending on multiple `auditing-shared` scripts MAY (opt-in) bind `auditing-shared` in their `skills:` field; agents depending on a single script invoke it via Bash only. |
| Why now | Four execution-phase agents in this feature ship with the divergent binding pattern; without ratification, the convention exists in code without a discoverable canonical statement, contradicting ADR-0029 + ADR-0033 brief-honor requirements. |
| Why this | Preserves canonical-helper-home semantics (ADR-0031) while acknowledging that load-bearing conceptual context for multi-script orchestration warrants Skill binding. One-decision-per-ADR is the established pattern (ADR-0029 / ADR-0033 split rather than fold); folding into ADR-0032 would muddle its 5-change framing. |
| Known unknowns | Whether the binding's context-window cost (loading SKILL.md per agent invocation) is justified by the operational benefit; the four agents are the first to exercise it. First feature run using this design IS operational verification. |
| Kill criteria | If the first 3 feature runs surface evidence that the binding adds context-window cost without operational benefit (e.g., agent decisions don't reference the SKILL.md content), the convention is reversed — agents drop the binding and use Bash invocation only. |

## Rationale

The four affected agents have a structural property in common: each materially depends on **multiple** auditing-shared scripts (orchestrator: 5; quality-handler: 2+; phase-quality-reviewer: 3+; finalize-reconciler: 2+ via dispatch discipline). When an agent's reasoning must compose outputs across multiple scripts — interpreting which dispatch row applies, choosing between similar-shaped validator outputs, deciding when stub vs. real semantics matter — the conceptual model in SKILL.md is load-bearing. Bash-invocation alone surfaces only the script's stdout; the SKILL.md surfaces the relationships among scripts.

Planning-side agents that invoke a single script via Bash do not need the conceptual model; they invoke, parse, act. The single-script case has no orchestration concern. The convention therefore distinguishes the two cases explicitly: multi-script orchestration warrants Skill binding; single-script invocation does not.

The convention is **opt-in, not mandatory**, because future agents may have novel patterns this ADR cannot anticipate. The opt-in framing preserves design flexibility while documenting the worked-example precedent for multi-script orchestration.

This ADR honors:

- **ADR-0029 (no-silent-scope-changes principle)**: the convention is now surfaced in a discoverable ADR location, not only in a single feature's Blueprint convention-note.
- **ADR-0031 (canonical-helper-home)**: the script-organization invariant is preserved; this ADR adds a layer on top regarding binding semantics, without conflicting with ADR-0031's scope.
- **ADR-0033 (execution-phase Scope-Deviation extension)**: the convention divergence from planning-side practice IS a deviation; ratifying it here surfaces it in the canonical cross-feature location.

## Options Considered

### Option 1: Fold the convention into ADR-0032 as a sixth change category

**Pros:**
- Keeps cross-feature conventions consolidated in a single ADR
- One fewer ADR to track

**Cons:**
- ADR-0032 is already at 5 changes per its own framing (universal frontmatter fields; user-token chain; per-doc-type state vocabulary; doc_type taxonomy; execution-phase artifact frontmatter section)
- Skill-binding conventions are semantically distinct from frontmatter / vocabulary / taxonomy conventions
- Muddles ADR-0032's legibility as the "conventions canonicalization" ADR
- Departs from the established one-decision-per-ADR pattern (ADR-0029 / ADR-0033 split)

### Option 2: Defer to a follow-on conventions feature

**Pros:**
- No new ADR authored this feature run
- Allows broader survey of binding conventions across the project before committing

**Cons:**
- The convention is already in play in this feature (four agents ship with the binding)
- ADR-0029 + ADR-0033 require ratification when a deviation affects cross-feature norms; deferral perpetuates the silent-absorption pattern they forbid
- Downstream contagion: Plan-stage tasks will codify the convention in the validator's whitelist + four agent files without an ADR to cite; future features authoring new audit-touching agents will be uncertain whether the convention applies

### Option 3 (Selected): Author new ADR-0035

**Pros:**
- One decision per ADR; matches the established pattern (ADR-0029 / ADR-0033 split)
- Pairs structurally with ADR-0031 (ADR-0031 defines where scripts live; ADR-0035 defines how downstream agents bind)
- Surfaces the convention in the canonical cross-feature ADR location per ADR-0029 + ADR-0033 brief-honor requirements
- Discoverable from both this feature's Blueprint and from future features authoring audit-touching agents

**Cons:**
- One more ADR in the inventory (now 35 total)
- Requires a parallel reading with ADR-0031 to get the complete binding-and-organization picture

## Consequences

### Positive Consequences

- Cross-feature conceptual model available to agents that materially depend on multiple auditing-shared scripts; reduces ad-hoc reasoning per script invocation
- Pattern is repeatable: future agents with similar structural property (multi-script orchestration on a cross-cutting helper-home skill) have a precedent to cite
- ADR-0029 + ADR-0033 brief-honor restored at the cross-feature surface (not only at the Blueprint convention-note surface)
- ADR-0031 ↔ ADR-0035 pairing legibility: ADR-0031 defines where scripts live; ADR-0035 defines how agents bind

### Negative Consequences

- Context-window cost: agents binding auditing-shared load SKILL.md per invocation; the cost is per-agent-per-invocation
- Non-user-facing skill (auditing-shared is a helper-home, not a user-facing knowledge skill) in agent bindings is a deviation from past pattern; downstream readers must understand the helper-skill-vs-knowledge-skill distinction
- New dependency edge: an agent binding auditing-shared depends on the SKILL.md existing on disk (per FR-9-c symmetric application via FR-6 validator)

### Neutral Consequences

- The four affected agents' frontmatter already includes the binding per blueprint-v4 v4.0.0 spec; this ADR ratifies the convention rather than introducing it (the introduction was in cc-design.md v1.0.0)
- ADR-0031's scope is unchanged; ADR-0035 layers on top

## Architecture Impact

1. **Components that change:** None directly. The four affected agents already declare the binding per blueprint-v4 / cc-design.md spec. ADR-0035 ratifies the convention; it does not introduce agent changes.
2. **New dependencies introduced:** Helper-availability dependency edge for agents that bind. The SKILL.md must exist on disk before the bound agent becomes functional (analogous to FR-9-e's `ai-development-guide` install precondition).
3. **Architectural constraints added:** Future agents claiming the convention must declare the multi-script-orchestration rationale explicitly in their frontmatter or accompanying Blueprint rationale.
4. **Architectural constraints removed:** None.
5. **Layers affected:** Claude Code / Project Filesystem layer only (per ADR-0011 layer taxonomy).

## Implementation Guidance

The convention is opt-in. Implementation discipline:

- When authoring a new execution-phase agent, evaluate whether the agent materially depends on multiple auditing-shared scripts. If yes, consider the binding; the rationale belongs in the Blueprint's §Agent Frontmatter Specifications convention notes (or equivalent).
- When authoring a new agent that invokes a single auditing-shared script, prefer Bash invocation alone; do not bind unless the conceptual-model context is clearly load-bearing.
- KB-cc-design may grow a section on "helper-skill bindings vs knowledge-skill bindings" to canonicalize the distinction — deferred to a follow-on KB-enhancement feature, not blocking ratification of this ADR.
- The FR-6 frontmatter validator's `skills:`-existence check (per AC-FR-9-c symmetric application) treats `auditing-shared` like any other skill: if listed in an agent's `skills:` field, the SKILL.md must exist at `.claude/skills/auditing-shared/SKILL.md`.

Implementation procedures (e.g., "modify these four agent files to add the binding") are Plan-stage concerns, not ADR concerns. The four agent files already declare the binding per cc-design.md and blueprint-v5.md; this ADR documents the convention, not the per-file edit.

## Related Information

- **Related ADRs:**
  - ADR-0029 (no-silent-scope-changes principle) — the brief-honor requirement this ADR satisfies for the binding-convention deviation
  - ADR-0031 (auditing-shared skill module) — defines where the scripts live; ADR-0035 defines how downstream agents bind (structural pairing)
  - ADR-0032 (conventions canonicalization) — sibling convention ADR; this ADR was deliberately NOT folded into ADR-0032 per D-RC3-2 (one-decision-per-ADR discipline)
  - ADR-0033 (execution-phase Scope-Deviation extension) — symmetric pattern: this ADR is a cross-feature ratification of a deviation that ADR-0033 would otherwise require to surface only at the Blueprint level
- **Referenced specs / docs:**
  - `working/feature/execution-pipeline-design-r1/blueprint-v5.md` §Agent Frontmatter Specifications convention note 1 (the worked example)
  - `working/feature/execution-pipeline-design-r1/cc-design.md` v1.0.0 (the per-layer design declaring the binding for the four agents)
  - `working/feature/execution-pipeline-design-r1/reconciliation-log-cycle3.md` D-RC3-2 (the explicit choice between Option 1 / Option 2 / Option 3)
- **Issues / PRs:**
  - architecture-audit-issues-r6.json finding I-AA-603 (the audit finding this ADR resolves)
  - reconciliation-dispatch-cycle3.json (the dispatch payload authorizing this ADR's authoring)
- **Related KBs:**
  - KB-cc-design — design discipline for the Claude Code layer; future "helper-skill bindings vs knowledge-skill bindings" section candidate
  - KB-cc-platform — platform reference for `skills:` field syntax + semantics
