---
id: ADR-0015
version: 2.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes: []
adrs_inherited:
  - ADR-0004 (test split — acceptance reads blueprint only)
  - ADR-0011 (canonical document skill)
  - ADR-0013 (Blueprint template adoption)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
superseded_by_consolidation: 2026-05-25
superseded_canonical_archived_to: adrs/superseded/ADR-0015-pre-consolidation-canonical.md
---

# ADR-0015: Adoption of EARS-format acceptance criteria

## Status

Accepted — 2026-05-12

## Context

Blueprint v3's acceptance criteria were authored in BDD-style scenarios (Given/When/Then). The uploaded Blueprint template specifies EARS format (Easy Approach to Requirements Syntax) with keywords `When` (event-triggered), `While` (state-dependent), `If-then` (conditional), and no-keyword (ubiquitous behavior).

EARS originated at Rolls-Royce (Mavin et al., RE'09 2009; claim C-R3-0001) and is adopted by Airbus, Bosch, Dyson, Honeywell, Intel, NASA, and Siemens (claim C-R3-0002). Critically, Amazon Kiro IDE adopted EARS as its native notation for spec-driven AI development in 2025 (claim C-R3-0003) — a near-identical use case to this pipeline (intent → requirements → design → tasks).

The user has explicitly confirmed strict EARS adoption (Q-v4-4 Option A).

## Decision

All acceptance criteria produced by the pipeline (in PRD functional requirements, blueprint Acceptance Criteria section, and acceptance tests) use EARS format strictly. The five EARS templates (Ubiquitous, Event-driven `When`, Unwanted/Error `If-then`, State-driven `While`, Optional Feature `Where`) are the permitted forms. Complex behaviors can combine templates (e.g., `While <state>, when <trigger>, the system shall <response>`).

## Decision Details

| Item | Content |
|---|---|
| Decision | All acceptance criteria across PRD, Blueprint, and acceptance test artifacts use EARS format with the five canonical templates. No BDD (Given/When/Then), no freeform "the system should..." prose. |
| Why now | Blueprint v4 introduces the canonical Blueprint template (ADR-0013) which specifies EARS format in the Acceptance Criteria section. Committing to EARS pipeline-wide ensures PRD acceptance criteria, Blueprint ACs, and test-acceptance-author outputs share one syntax. |
| Why this | EARS is industry-proven (15+ years, major adopters per claim C-R3-0002); Kiro's adoption (claim C-R3-0003) validates the format specifically for AI-driven workflows; structured keywords reduce ambiguity AI agents would otherwise resolve by assumption (claim C-R3-0006); maps cleanly to test types (When → event-driven test, If-then → branch coverage test, While → state condition test). |
| Known unknowns | EARS is best for event-driven systems (claim C-R3-0005); for ubiquitous behaviors and purely mathematical/functional requirements, EARS may feel forced. The "Ubiquitous" template (no keyword) handles this, but the question of when to use Ubiquitous vs an explicit keyword is a judgment call. |
| Kill criteria | If 30%+ of ACs across 3 consecutive feature runs use the Ubiquitous template (no keyword), the pipeline is producing ACs that don't benefit from EARS structure, and a hybrid format permitting BDD for non-event-driven behaviors should supersede this ADR. |

## Rationale

Three findings converge on strict EARS adoption:

(1) **Direct precedent in AI workflow.** Claim C-R3-0003: Amazon Kiro implements a workflow strikingly similar to ours (requirements.md with EARS → design.md → tasks.md). Their adoption was deliberate, citing that "EARS-formatted specifications reduce the ambiguity that causes AI agents to make undesirable assumptions" (claim C-R3-0006). Same use case, same conclusion.

(2) **Mature industry adoption.** Claim C-R3-0002: 15+ years of production use across safety-critical industries (aerospace, automotive). The format works at scale; not a research artifact.

(3) **Maps to test design.** The Blueprint template explicitly states the test-type mapping: When → event-driven test, While → state condition test, If-then → branch coverage test, Ubiquitous → basic functionality test. This gives test-acceptance-author a structured production path: each EARS AC becomes a specific test type.

The trade-off against BDD: BDD scenarios (Given/When/Then) are widely known and have richer expressive power for multi-step user flows. EARS focuses on system behavior — what the system shall do in response to triggers/states/conditions — which is a tighter scope. For our pipeline (architecting features, not exhaustively scripting user flows), EARS's tighter scope is the right level. BDD's strengths show in human-readable user stories — which is where they live, in PRD User Stories section, not Acceptance Criteria.

## Options Considered

**Option 1: BDD (Given/When/Then) format.** Current v3 approach; widely known.
- Pros: rich expressiveness for multi-step flows; familiar to developers; map directly to Cucumber/Specflow.
- Cons: more verbose; less structurally enforceable; AI agents fill `Given` with assumed context that isn't grounded (per claim C-R3-0014 AI tendency to fabricate).

**Option 2: Hybrid — BDD for user-facing flows, EARS for system behavior, prose for everything else.**
- Pros: format matches use case.
- Cons: classification overhead per AC; format inconsistency makes structural validation harder; shared-document-reviewer Gate 0 check for AC format becomes "is it any of three formats" rather than "is it EARS."

**Option 3 (Selected): Strict EARS across all AC artifacts.**
- Pros: industry-proven for safety-critical and AI-driven workflows; structural enforcement via shared-document-reviewer Gate 0; tight mapping to test design; reduces AI assumption-making per claim C-R3-0006; matches user-provided Blueprint template structure.
- Cons: ubiquitous (non-event) behaviors feel structurally forced; learning curve for contributors unfamiliar with EARS.

## Consequences

### Positive Consequences

- AC format is structurally enforceable via shared-document-reviewer Gate 0 (validates `When`/`While`/`If-then` keyword usage or explicit Ubiquitous form).
- test-acceptance-author has a defined production rule: each EARS AC maps to a specific test type per the Blueprint template's table.
- Cross-document consistency: PRD functional requirements ACs, blueprint Acceptance Criteria section, and acceptance test artifacts all use the same syntax.
- Reduces AI assumption-making: per claim C-R3-0006, EARS's structured triggers force the author to make preconditions/triggers explicit.
- Maps to the pipeline's failure-mode defense for wrong-assumption (MAST FM-2.2): when a critique finds the agent made an assumption the spec didn't license, the AC syntax shows whether the assumption is licensed by the AC's keyword structure.

### Negative Consequences

- Contributors unfamiliar with EARS face a learning curve. Mitigated by `KB-documentation-criteria` and `KB-documentation-criteria` containing EARS examples and the canonical template references.
- Some behaviors (mathematical/functional requirements without triggers) are naturally Ubiquitous and may not benefit from EARS structure — they just become AC-prefixed statements. Acceptable but watches for the kill criterion (30%+ Ubiquitous as a signal).
- ACs become longer than BDD equivalents in some cases due to explicit keyword usage. Acceptable trade-off for ambiguity reduction.

### Neutral Consequences

- User stories in PRD remain in their conventional `As a / I want / So that` format; EARS applies to acceptance criteria, not user stories. This matches the Blueprint template's separation.

## Architecture Impact

**Components that change:**
- `KB-documentation-criteria`: teaches EARS format for functional requirement acceptance criteria.
- `design-knowledge` (per ADR-0013, taught via the Blueprint template): teaches EARS for blueprint Acceptance Criteria section.
- `KB-documentation-criteria`: teaches mapping from EARS keyword to test type (`When` → event-driven test, etc.).
- intake-prd-author, synth-designer (and per ADR-0016 per-layer designers + composer), test-acceptance-author: all instructed to produce EARS-format ACs.
- shared-document-reviewer: `doc_type: PRD` and `doc_type: DesignDoc` Gate 1 quality checks validate EARS keyword usage in AC sections.

**New dependencies introduced:**
- None.

**Architectural constraints added:**
- All acceptance criteria across PRD, Blueprint, and acceptance test artifacts MUST use one of the five EARS templates.
- Combinations of templates (e.g., While+When) are permitted following EARS's complex requirement rules.
- The Acceptance Criteria section of the Blueprint template MUST group ACs by layer when the feature spans multiple layers (per the template).

**Architectural constraints removed:**
- Freeform "the system should..." AC prose no longer permitted.
- BDD (Given/When/Then) format no longer permitted in acceptance criteria. (BDD remains valid for user stories in PRD.)

## Implementation Guidance

- Use the EARS keyword that matches the behavior class: event-triggered behavior → `When`; state-dependent behavior → `While`; error/exception handling → `If <condition>, then`; always-on behavior → no keyword (Ubiquitous); feature-flagged behavior → `Where <feature>`.
- When a behavior involves both state and trigger, combine: `While <state>, when <event>, the system shall <response>`.
- Each AC should be testable in isolation. If an AC requires multi-step setup beyond what `While` or `Where` express, split it into multiple ACs or push the setup into separate state-establishment ACs.
- Group ACs by layer when blueprint spans multiple layers (Blueprint template convention).
- Reference: see `KB-documentation-criteria` → Templates → Blueprint → "Acceptance Criteria (AC) - EARS Format" section.

## Related Information

- User-provided template: BluePrint.txt (uploaded; specifies EARS in §"Acceptance Criteria (AC) - EARS Format").
- ADR-0013: Blueprint template adoption — locks in EARS structure for blueprint ACs.
- ADR-0017 (forthcoming): shared-document-reviewer Gate 1 quality checks include EARS keyword validation.
- Claims C-R3-0001 through C-R3-0006: EARS origin, adoption, AI workflow precedent.
- Reference: Mavin, A. et al. "Easy Approach to Requirements Syntax (EARS)." IEEE International Requirements Engineering Conference, 2009.

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0015-ears-acceptance-criteria-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
