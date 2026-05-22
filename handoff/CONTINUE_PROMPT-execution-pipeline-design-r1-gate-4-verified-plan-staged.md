<!-- Companion to handoff/HANDOFF-execution-pipeline-design-r1-gate-4-verified-plan-staged.md. Authored 2026-05-22T20:30:00Z. -->

# Continuation prompt — `execution-pipeline-design-r1` (Gate 4 verified; Plan staged; downstream stages pending)

## READ THIS FIRST — you are a fresh Claude Code session

You have **no in-context memory** of the prior session. The prior session was conducted in **claude.ai** (the web/desktop chat interface), NOT in Claude Code. That means the prior session **could not actually dispatch subagents** — it simulated subagent procedures and produced artifacts as if subagents had run. You ARE Claude Code; you CAN dispatch subagents. Reconciling these two realities is your first job.

Your first action is to verify state by reading specific files. Do not trust this prompt as your only source of truth — verify against the actual repo.

**Critical orientation**: you are working on a project that builds a **feature pipeline** — a multi-stage discipline-driven workflow for designing and shipping features. This project's "product" IS the feature pipeline itself; there are no separate product layers. The pipeline operates on itself recursively.

The current in-flight feature is **`execution-pipeline-design-r1`** — designing the **execution side** of the pipeline (the stages from `tasks.json` through deliverable archive). Single-layer feature (Claude Code only). 13 FRs / 60 ACs.

## TL;DR — where you are

The Architecture Audit stage went through 5 simulated audit rounds + 2 reconciliation cycles + 1 post-Gate-4 platform-validity correction pass. The Blueprint advanced through 4 versions (v1 → v2 → v3 → v4); v4 is the current draft. A `plan-v1.md` was also authored in simulation. **All of this was done in claude.ai without real subagent dispatch.** The substance is reasonable but authoritative validation has not occurred.

Pipeline state:

- **Design Composition**: blueprint-v4.md draft (latest); v1-v3 superseded
- **Architecture Audit**: converged through 5 simulated rounds (last verdict: pass)
- **Plan Authoring**: plan-v1.md draft (simulated)
- **Test Authoring**: NOT STARTED
- **Cross-Artifact Audit**: NOT STARTED
- **Task Decomposition**: NOT STARTED
- **Gate 6**: pending

Reconciliation budget: 2 of 4 cycles used; 2 remain.

The full snapshot is documented in `handoff/HANDOFF-execution-pipeline-design-r1-gate-4-verified-plan-staged.md`. Read it.

## STEP 1 — Verify pipeline state (do NOT skip)

Before doing any substantive work, verify the repo state matches what this prompt claims:

```bash
# Verify Blueprint versions exist and are in the expected statuses
ls working/feature/execution-pipeline-design-r1/blueprint-v*.md
grep -E '^status:' working/feature/execution-pipeline-design-r1/blueprint-v*.md
# Expected: v1, v2, v3 status: superseded; v4 status: draft

# Verify all 5 audit JSONs exist
ls working/feature/execution-pipeline-design-r1/architecture-audit-issues*.json
# Expected: architecture-audit-issues.json (r1), -r2.json, -r3.json, -r4.json, -r5.json

# Verify reconciliation cycles
ls working/feature/execution-pipeline-design-r1/reconciliation-*.{md,json}
# Expected: cycle1 and cycle2 logs + dispatch JSONs

# Verify plan-v1.md
ls working/feature/execution-pipeline-design-r1/plan-v1.md
head -15 working/feature/execution-pipeline-design-r1/plan-v1.md
# Expected: version 1.0.0, status: draft, agent_invocation_simulation: true

# Verify ADR-0034 is revised
grep -E '^(status|revised|revision_reason):' adrs/ADR-0034-prd-mis-credit-cleanup.md
# Expected: status: proposed; revised + revision_reason fields populated

# Verify the simulation caveat is present on each artifact
grep -l 'agent_invocation_simulation\|claude.ai simulation' working/feature/execution-pipeline-design-r1/*.{md,json}
# Expected: most blueprint v2+, all audit r2+, both reconciliation cycles, plan-v1
```

If anything is missing or mismatched, **stop and surface it to the user**. Don't paper over discrepancies.

## STEP 2 — Read the simulation caveats

Every artifact produced in the prior claude.ai session carries an explicit simulation disclosure. Read these before doing any work that builds on the simulated artifacts:

```bash
# Frontmatter notes on each simulated artifact
head -30 working/feature/execution-pipeline-design-r1/blueprint-v4.md   # agent_invocation field
head -30 working/feature/execution-pipeline-design-r1/plan-v1.md        # agent_invocation_simulation field
head -25 working/feature/execution-pipeline-design-r1/architecture-audit-issues-r5.json  # agent_invocation field
head -25 working/feature/execution-pipeline-design-r1/reconciliation-log-cycle2.md       # agent_invocation_note field
```

The handoff document also has a "Simulation caveat" section explicitly listing what was simulated and what wasn't:

```bash
sed -n '/Simulation caveat/,/^##/p' handoff/HANDOFF-execution-pipeline-design-r1-gate-4-verified-plan-staged.md
```

## STEP 3 — Identify the next action

You have two reasonable paths. Choose based on the user's preference (ask if unclear):

**Path A — Authoritative re-audit first (more rigorous):**

Run a real `review-architecture-auditor` invocation against blueprint-v4.md. The simulated audit r5 returned `pass`, but it was a simulation. An authoritative audit pass either confirms the simulation work (and you proceed to Plan Gate 5) or surfaces additional findings (and you route through reconciliation cycle 3 — 2 cycles remain in budget). This is the path the simulation work itself recommends in its scope-deviation notes.

**Path B — Trust the simulation and proceed (faster):**

Accept the simulated audit r5 pass verdict as sufficient for advancing to Plan Gate 5. Invoke `shared-document-reviewer` for Gate 0 structural review of plan-v1.md, then `review-cross-artifact-auditor` for Gate 1 cross-reference verification. This skips authoritative re-validation of the Blueprint but advances the pipeline faster.

**Recommendation: Path A.** The simulation work is substantive but the value of an independent authoritative audit is exactly that it's independent. The simulation cannot validate itself. Path A burns one subagent invocation but produces a defensible verdict.

After Path A or B clears, the remaining pipeline stages are:

1. **Plan Authoring Gate 5** — if Path B chosen, this is your first authoritative review
2. **Test Authoring** (stage 10) — invoke `test-acceptance-author` + `test-phase-validator-author` in parallel
3. **Cross-Artifact Audit** (stage 11) — invoke `review-cross-artifact-auditor`
4. **Task Decomposition** (stage 12) — invoke `finalize-task-decomposer`
5. **Deliverable Packaging** (stage 13)
6. **Gate 6 (Final Approval)** — present tasks.json + packager-report to user

The canonical procedure is in `.claude/skills/recipe-feature-pipeline/SKILL.md`.

## Critical disciplines this feature operates under (and applies to itself)

These are project-wide and remain active. The feature in flight is designing them; the project itself uses them recursively:

1. **ADR-0005 append-only supersession** — never edit the body of an artifact that's been gated past `draft`. Edits to predecessor versions are frontmatter-only (`status: superseded`, `superseded_by`, etc.). The exception: ADRs in `status: proposed` can be edited in-place because the `proposed → accepted` transition hasn't occurred yet (ADR-0034 was edited this way in cycle 1 reconciliation).
2. **ADR-0017 4-cycle reconciliation cap** — symmetric application per ADR-0034 (the planning-side and execution-side caps are the same number). 2 of 4 used in this snapshot; 2 remain. If you blow the cap, escalate to the user.
3. **ADR-0029 + ADR-0033 no-silent-scope-changes** — every scope deviation, simulation caveat, or unresolved question must be surfaced explicitly in artifact frontmatter or a dedicated section. Don't absorb silently.
4. **ADR-0032 per-doc-type state vocabularies** — gated artifacts use 5-state; analysis/logs use 3-state; ADRs use 4-state (no `draft`).
5. **AC-FR-9-e skill-install-before-binding sequencing** — `ai-development-guide` skill must exist at `.claude/skills/ai-development-guide/SKILL.md` BEFORE any agent file binding to it is authored.

## Cycle 3+ audit/reconciliation history (read once, don't repeat the journey)

If you take Path A and find issues, here's what the prior cycles already addressed (so you don't re-discover them):

- **Cycle 1** addressed: floor coverage inconsistency (Path B disposition); ADR-0034 unsupported ADR-0021 claim (rewritten); IN-009 counting error; Fact Disposition Table recount; Contract 4 scope-deviations dispatch procedure; stale "OR" framing; Contract 4 header label
- **Cycle 2 audit** returned pass — **retracted** by cycle 3 due to missed agent-frontmatter pattern check
- **Cycle 3** addressed: under-transcribed cc-design.md specs; Skills bound contradictions; missing tools: + memory: directives; Task vs TaskCreate naming (later revised in v4); Edit + auditing-shared validity
- **Cycle 5 (Gate 4 verification)** addressed: `memory: none` invalid (removed); Task→Agent canonical rename + TaskCreate/TaskUpdate is a separate tool family (corrected)

If your authoritative audit re-surfaces any of these, that's a signal worth surfacing — either the simulation got it wrong (in which case your audit is more rigorous and the fix should land) or there's still something off.

## What you should NOT do

- **Do not re-run simulated audit cycles in simulation.** You are Claude Code; dispatch the actual `review-architecture-auditor` subagent if you want a fresh audit. Re-simulating in your own context defeats the purpose.
- **Do not silently accept the simulation results without reading their scope-deviation surfacings.** The simulation notes explicitly mark itself as needing authoritative validation; honor that.
- **Do not edit blueprint v1, v2, or v3 bodies.** They are `superseded`; ADR-0005 forbids body edits to superseded artifacts. If you find an issue, the correction lands in v5 (or whatever the next active version becomes), not in a superseded predecessor.
- **Do not paper over disagreements between this prompt and actual repo state.** If state verification (STEP 1) surfaces a mismatch, stop and ask the user.
- **Do not bundle the devcontainer.json into pipeline scope.** It's at `.devcontainer/devcontainer.json` as an adjacent deliverable, NOT part of `execution-pipeline-design-r1`'s PRD. If the user wants devcontainer functionality in the pipeline itself, that's a PRD amendment cycle.

## Audit-procedure improvement notes (not blocking; for awareness)

Two gaps in the audit procedure spec were surfaced during this snapshot's work. Both are candidates for a future feature run targeting `KB-review-disciplines`:

1. **Canonical-agent-frontmatter-pattern check** — should be in Architecture Audit Phase 5 cross-section consistency checks. Its absence caused cycles 1+2 to miss the Blueprint's under-transcription of cc-design.md.
2. **Canonical-platform-docs verification step** — should be in Gate 4 procedure. Its absence let v3 ship with `memory: none` invalid syntax and a misreading of Task/Agent tool naming.

These are documented in the HANDOFF and in audit r5 + audit r3 (I-AA-310). Not in this feature's scope; surface to the user only if relevant to the current decision context.

## User preferences (carried forward)

- Three-option presentation at substantive decision points; user typically picks Option 1 (default-rhythm forward motion) but engages with 2/3 when distinct
- Prose-heavy with citations; tables for inventories
- Explicit confidence levels + open questions
- Direct response style; minimal preamble
- Substantive critique welcomed (don't pull punches)
- No silent failures; ADR-0029 + ADR-0033 discipline applied symmetrically

## What success looks like at the end of the next session

Either:

(a) **Authoritative re-audit of Blueprint v4 passes**; Plan Gate 5 review passes plan-v1.md; Test Authoring stage produces acceptance-tests.md + phase-validators.md; the pipeline is queued for Cross-Artifact Audit at Gate 11.

OR

(b) **Authoritative re-audit of Blueprint v4 surfaces findings** that warrant reconciliation cycle 3; design-composer produces blueprint-v5; cycle 6 audit verifies. (Budget: cycle 3 of 4 used; 1 remains.)

OR

(c) **You uncover a substantive defect in the simulation work** that warrants surfacing to the user before continuing. Stop and ask.

The goal is to reach Gate 6 (Final Approval) with a tasks.json that drives the Execution Phase. That's likely 2-3 Claude Code sessions away depending on findings.

## Recommended first message to send (you can edit; this is a suggestion not a script)

> "I've read the HANDOFF and verified the repo state. Blueprint v4 is the current draft, plan-v1.md is the current Plan, 2 of 4 reconciliation cycles used. Per the simulation caveat, I recommend Path A (authoritative `review-architecture-auditor` invocation on blueprint-v4) before advancing to Plan Gate 5. Confirm Path A, or specify B?"
