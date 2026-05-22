<!-- Companion to handoff/HANDOFF-execution-pipeline-design-r1-blueprint-complete.md. Authored 2026-05-22T07:00:00Z by claude (acting as design-composer). -->

# Continuation prompt — `execution-pipeline-design-r1` (Design Composition complete; Architecture Audit pending)

## READ THIS FIRST — you are a fresh Claude.ai session

You have **no in-context memory** of the prior session that produced the current pipeline state. **Do NOT assume anything from this prompt alone.** Your first action is to verify state by reading specific files. The user has explicitly noted that past handoffs have caused fresh sessions to get confused — this prompt is designed to prevent that by giving you (a) enough context to orient, AND (b) explicit verification steps to ground your understanding in actual repo state rather than this prompt.

**Critical orientation**: you are working on a project that builds a **feature pipeline** — a multi-stage discipline-driven workflow for designing and shipping features. This project's "product" IS the feature pipeline itself; there are no separate product layers (no frontend, no backend, no API, no database). The feature pipeline operates on itself recursively.

The current in-flight feature is **`execution-pipeline-design-r1`** — its goal is to design the **execution side** of the pipeline (the stages from `tasks.json` through deliverable archive). Single-layer feature (Claude Code only). 13 FRs / 60 ACs.

## TL;DR — where you are

- The **Design Composition stage is complete** for `execution-pipeline-design-r1`.
- A `blueprint-v1.md` was authored (2257 lines, 185 KB) plus 3 new ADRs (`ADR-0032`, `ADR-0033`, `ADR-0034`).
- A **self-review Gate 0 + Gate 1 reviewer pass** was completed; verdict: **approved** (Consistency 94 / Completeness 96 / Rule compliance 95 / Clarity 93 / Aggregate ~94.5).
- **The next stage is Architecture Audit** — an independent audit by `review-architecture-auditor` agent that produces `architecture-audit-issues.json`.
- After Architecture Audit, **Gate 4 (Blueprint Approval)** is the next user touch-point.

The self-review is NOT a substitute for Architecture Audit. Architecture Audit is the next stage.

## STEP 1 — Verify pipeline state (do NOT skip this)

Before doing any substantive work, verify the repo state matches what this prompt claims:

```bash
# Verify blueprint and ADRs exist with expected status
head -10 working/feature/execution-pipeline-design-r1/blueprint-v1.md
head -10 adrs/ADR-0032-conventions-canonicalization.md
head -10 adrs/ADR-0033-adr-0029-execution-extension.md
head -10 adrs/ADR-0034-prd-mis-credit-cleanup.md

# Expected: blueprint frontmatter has status:draft, reviewer_verdict:approved
# Expected: each ADR has status:proposed
```

If any of these files don't exist or have different status values, **stop and surface the discrepancy** per ADR-0029 (no silent absorption). Do NOT proceed assuming the prompt is correct.

## STEP 2 — Read the canonical state documents

Read these files in order:

1. **`handoff/HANDOFF-execution-pipeline-design-r1-blueprint-complete.md`** — the comprehensive handoff with full pipeline state, decisions, substrate refinements, and what's-next analysis. This is the most important file; read it carefully.

2. **`.claude/skills/recipe-feature-pipeline/SKILL.md`** — the canonical pipeline-procedure source. Confirm Architecture Audit is the next stage after Design Composition + the 5 disciplines this feature operates under.

3. **`working/feature/execution-pipeline-design-r1/blueprint-v1.md`** — the artifact under review for Architecture Audit. Pay particular attention to:
   - Q-CC-N Arbitration section (5 resolved architectural questions)
   - Contract Definitions (5 contracts including the D-13 5th-dimension extension noted in HANDOFF)
   - State Transitions and Invariants (12 states + 12 transitions + 10 invariants)
   - Future Extensibility + Risks and Mitigation sections (8 deferred items, 8 risks, 8 rejected alternatives)

4. **`adrs/ADR-0032-conventions-canonicalization.md`** — 5 coordinated changes to `shared-conventions.md`; pairs D-4 + D-18; subsumes IN-005.

5. **`adrs/ADR-0033-adr-0029-execution-extension.md`** — extends ADR-0029 Scope-Deviation surfacing to execution-phase artifacts.

6. **`adrs/ADR-0034-prd-mis-credit-cleanup.md`** — documents ADR-0017 is canonical home for 4-cycle reconciliation cap.

## STEP 3 — Identify the next action

The next pipeline stage is **Architecture Audit**. Specifically:

- **Invoke `review-architecture-auditor` agent** (definition at `.claude/agents/review-architecture-auditor.md`) on the Blueprint + 3 ADRs.
- The agent produces `working/feature/execution-pipeline-design-r1/architecture-audit-issues.json`.
- The auditor evaluates against architectural discipline; produces verdict PASS / FAIL / CYCLE.
- If issues surface, follow ADR-0017 4-cycle reconciliation cap; reconciliation cycle if needed.
- If audit passes (or after reconciliation converges), proceed to **Gate 4 — Blueprint Approval** (user touch-point).

## Critical disciplines this feature operates under (and applies to ITSELF)

This feature designs the discipline-enforcement machinery for the execution pipeline. The same disciplines apply to this feature's own authoring:

- **ADR-0005** — Append-only supersession. Never edit prior versions in place.
- **ADR-0017** — 4-cycle reconciliation hard cap. Canonical home for the cap (per ADR-0034 cleanup; PRD v1.1.0 prose informally mis-credits ADR-0021 — do not propagate the mis-credit).
- **ADR-0028** — Recipe-feature-pipeline discipline 5 (no pipeline-stage references by number; use stage names only). Self-applied; this session caught violations in claude's own earlier work and informed D-15 worked example.
- **ADR-0029** — Surface every scope deviation. "1 could be major." No silent absorption.
- **ADR-0030** — Mechanism α: inline justification per pedagogical marker; symmetric application (D-15 worked example mechanically enforces discipline 5).
- **ADR-0031** — `auditing-shared` is canonical home for cross-audit utilities.

**ADRs 0032/0033/0034 are `status: proposed`** — they advance to `status: accepted` at Architecture Audit pass per ADR-0032's per-doc-type ADR vocabulary (4-state: proposed → accepted OR superseded OR rejected). Honor them in newly-authored artifacts but don't ENFORCE them against existing artifacts until they're accepted.

## Items the Architecture Auditor should look at carefully

Surfaced by self-review (full list in HANDOFF):

1. **D-13 5th-dimension addition** — Blueprint Contract 2 extends D-13's verdict structure from 4 to 5 dimensions (`scope_deviations` added per ADR-0033). Is the refinement well-grounded?
2. **AC-FR-7-d floor expansion** — Blueprint introduces 2 artifacts beyond the FR-7-c floor. Editorial expansion within AC-FR-7-d's permission. Flagged in Open items.
3. **ADR-0034 novel pattern** — "ADR-as-corrective-reference for documentary mis-attribution without supersession" is novel. Is the bounding correct?
4. **State machine invariant #10** — cycle counter / log equivalence check. Operationally feasible?
5. **ADR-0033 mechanical enforcement gap** — v1 ships requirement in agent prompts; mechanical script deferred. Acceptable for v1 OR block?
6. **`doc_type` immutability** (invariant #7) — verify no edge cases.
7. **5th-dimension dispatch** — Contract 4 gains `scope_deviations` row. Dispatch target well-defined?

## User preferences

From prior-session memory (Josh):

- **Direct substantive critique over validation.** Adversarial framing of his own work is welcomed. Don't pull punches.
- **Prose-heavy responses with specific citations** preferred for analytical work; tables for inventories.
- **Explicit confidence levels + open questions** expected alongside structural conclusions; false certainty is a failure mode.
- **Handoff prompts enforce intellectual discipline across sessions** — specifically to prevent fresh sessions from treating prior tentative conclusions as settled. The self-review verdict is TENTATIVE; Architecture Audit is the substantive independent pass.
- **Strong preference for mechanical defenses over discipline-statements-alone.** D-15 substrate is the worked example.
- **Three-option presentation** preferred at decision points: typically picks option 1 (default rhythm), engages thoughtfully with options 2 + 3 when distinct. Recommendation should be explicit.
- **No silent failures** meta-discipline applied symmetrically including to claude's own working artifacts.

## What success looks like at the end of the next session

Either:

**Path A — Architecture Audit clean pass**:
- `architecture-audit-issues.json` exists with verdict PASS
- No issues requiring reconciliation
- Ready to present Gate 4 to user with: blueprint-v1.md draft + 3 ADRs proposed + audit verdict PASS
- User reviews, approves → ADRs transition to `accepted`; blueprint to `accepted` with `gate_passed=4` stamped

**Path B — Architecture Audit surfaces issues**:
- `architecture-audit-issues.json` exists with verdict CYCLE (or FAIL with rationale)
- Reconciliation cycle initiated per ADR-0017 4-cycle cap
- Either: revisions land within cycle budget → next audit pass → Gate 4
- OR: cycle exhaustion → escalate to user per AC-FR-10-c with documented findings

Both paths surface deviations per ADR-0029; no silent absorption.

## First message to send (template)

```
I'm resuming the execution-pipeline-design-r1 feature pipeline. I have no in-context 
memory of the prior session. I will:

1. Verify pipeline state by reading the file frontmatters
2. Read the HANDOFF document for full context
3. Read recipe-feature-pipeline/SKILL.md to confirm procedural next step
4. Read blueprint-v1.md + the 3 new ADRs to understand what's being audited
5. Invoke review-architecture-auditor on the Blueprint + ADRs

Starting verification now.
```

This gives a clean entry point that signals to the user (Josh) you've understood the framing and are about to ground in actual repo state.

## What NOT to do

- **Do not skip the verification step (STEP 1).** The user has noted handoff prompts have failed in the past from sessions assuming state rather than verifying.
- **Do not author code or files before reading recipe-feature-pipeline/SKILL.md.** That file specifies the procedural disciplines that govern all stages.
- **Do not treat the self-review verdict as a substitute for Architecture Audit.** The self-review is one pass; Architecture Audit is the independent pass.
- **Do not propagate the PRD v1.1.0 ADR-0017 vs ADR-0021 mis-credit.** Cite ADR-0017 as canonical home for the 4-cycle cap.
- **Do not silently absorb deviations.** Per ADR-0029 + ADR-0033, surface every deviation in a discoverable location.
- **Do not assume ADRs 0032/0033/0034 are accepted.** They are `status: proposed`. Architecture Audit must pass before they advance.
- **Do not propagate the cosmetic Gate 0 anchor-rendering quirks** as defects. The Blueprint sections exist; standard markdown renderers work correctly.
