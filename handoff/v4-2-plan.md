# v4.2.0 Production Plan — phased with discrete tasks and state tracking

**Run-id:** feature-pipeline-design-r3-v4-2-20260512
**Started:** 2026-05-12
**Plan owner:** synth-reconcile (this session)
**Predecessor:** blueprint-v4.1.0.md (preserved per ADR-0005)
**Defect being addressed:** Layer Scope category error in v4.0.0 and v4.1.0 — all 9 layers should be in scope (every layer is one the v4 pipeline can design FOR via its 9 per-layer designers); both prior versions incorrectly mark 8 layers as `N/A — out of scope`.

## Plan-level state

| Field | Value |
|---|---|
| Current phase | 1 (not started) |
| Current task | none |
| Issues to address from v4.1.0 review | None — v4.1.0 passed all 3 reviews; v4.2.0 addresses a defect not surfaced by review (user-identified Layer Scope category error) |
| Issues from v4.2.0 reviews | Tracked in `state.json` after Phase 6 |
| Estimated total content authoring | 8 per-layer Design sections × ~120-180 lines each = ~1000-1450 new lines; v4.1.0 is 1393 lines → v4.2.0 estimated ~2400-2850 lines |
| Path A fabrication guardrail | Each per-layer Design section includes a `Research grounding` subsection acknowledging non-research-backed content; deferred to Phase 2 of Implementation Plan for research-grounded skill bodies |

## Phase 1 — Layer Scope correction and section initialization

**Goal:** Fix the Layer Scope category error throughout v4.1.0's structure. Create the 8 per-layer Design section skeletons that Phase 2 will fill. This is the structural fix; substantive content follows in Phases 2-3.

**Why this phase first:** The Layer Scope checkboxes are referenced by 5 other sections (Design Summary YAML `layers_touched`, Change Impact Map per-layer breakdown, Project Filesystem table, Security Considerations, Implementation Path Mapping). Fixing scope first means subsequent phases author content against the corrected scope rather than perpetuating the error.

**Tasks:**

- **T1.1** — Copy v4.1.0 to v4.2.0 as working copy. Update frontmatter (`version: 4.2.0`, `supersedes` includes 4.1.0, new `v4_1_0_to_v4_2_0_changes_summary` field, new `decisions_carried_forward_from_v4_1_0` enumerating that all 18 ADRs + 12 FRs + EARS ACs + 5 doc-reviewer invocations + critic renames + retroactive ADR migration are all carried forward).
- **T1.2** — Fix Layer Scope checklist: all 9 layers marked `[x]` with brief inline rationale per layer (e.g., "Frontend — the v4 pipeline designs for features touching Frontend; per-layer designer `synth-designer-frontend` authors Frontend Design section").
- **T1.3** — Fix Design Summary YAML `layers_touched`: list all 9 layers (was just "Claude Code / Project Filesystem").
- **T1.4** — Fix Change Impact Map: replace each `N/A — out of scope` row with a substantive description of how that layer is touched by the v4 pipeline's per-layer designer + knowledge skill + integration with composer + tests.
- **T1.5** — Fix Implementation Path Mapping table: add rows for the 8 per-layer designer agent files and 8 per-layer knowledge skills that are currently only listed in aggregate (`synth-designer-<layer>.md (×9)` and `<layer>-design-knowledge/SKILL.md (×9)`). Each row gets a specific path naming the layer.
- **T1.6** — Create skeleton headers for the 8 per-layer Design sections (Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces). Each section gets a placeholder marker: `[Authoring deferred to Phase 2 of v4.2.0 plan]`. Removes the `N/A — out of scope.` body text.
- **T1.7** — Update Phase 1 of Implementation Plan inside v4.2.0: documentation-criteria extension list now explicitly includes content for all 9 per-layer designer knowledge skills (not just the previously-named handful).
- **T1.8** — Update `state.json` after Phase 1 completion. Save state for resume.

**Phase 1 deliverable:** v4.2.0 with corrected Layer Scope structure throughout, 8 per-layer Design section skeletons in place (substantive content not yet authored), state.json updated.

**Phase 1 estimated content:** ~100-150 lines added/modified to fix Layer Scope and create skeletons.

## Phase 2 — Per-layer Design section authoring (Part A: foundational layers)

**Goal:** Author substantive content for the 5 foundational layers (Frontend, Backend, API, Query, Database). These are the most common layers in user features; getting them right first means the most-used per-layer designers have the strongest design content.

**Why this batch:** Foundational layers share a common pattern (component/data-flow design with HTTP or query boundaries). Authoring them together captures cross-layer patterns (how Backend integrates with API, how Query integrates with Database) that would be hard to add later.

**Per-section structure (each of the 5 sections follows this):**
1. Research grounding subsection — explicit "this section is general-design-principle-derived; research-grounded layer-specific skill bodies are deferred to Implementation Plan Phase 2 of v4.2.0" acknowledgment
2. Responsibility scope — what the per-layer designer authors when invoked
3. Inputs the per-layer designer expects from upstream stages
4. Output structure — the per-layer Design section structure for blueprints this designer contributes to
5. Layer-specific concerns surfaced — what cross-layer dependencies typically arise from this layer
6. Layer-specific Acceptance Criteria patterns (EARS keywords mapped to layer behaviors)
7. Knowledge skill outline — what `<layer>-design-knowledge` teaches (header-level only; full skill bodies deferred to Implementation Plan Phase 2)
8. Test boundaries for this layer
9. Security considerations specific to this layer

**Tasks:**

- **T2.1** — Author Frontend Design section. (~140-180 lines)
- **T2.2** — Author Backend Design section. (~140-180 lines)
- **T2.3** — Author API Design section. (~140-180 lines)
- **T2.4** — Author Query / Data Access Design section. (~100-140 lines)
- **T2.5** — Author Database Schema & Migration Design section. (~120-160 lines)
- **T2.6** — Update `state.json` after each task completion. Save state for resume.

**Phase 2 deliverable:** v4.2.0 with 5 foundational per-layer Design sections substantively authored. Total estimated addition: 650-840 lines.

## Phase 3 — Per-layer Design section authoring (Part B: infrastructure & dev environment layers)

**Goal:** Author substantive content for the 3 infrastructure/dev-environment layers (CI/CD, IaC, Codespaces).

**Why this batch separately:** These layers are less common in user features and have a different design pattern (declarative configuration rather than runtime components). Batching them lets the Phase 2 patterns settle before Phase 3 starts.

**Tasks:**

- **T3.1** — Author CI/CD (GitHub Actions) Design section. (~100-140 lines)
- **T3.2** — Author Infrastructure as Code Design section. (~100-140 lines)
- **T3.3** — Author Dev Environment (Codespaces) Design section. (~80-120 lines)
- **T3.4** — Update `state.json` after each task completion.

**Phase 3 deliverable:** All 9 per-layer Design sections substantively authored. Total estimated addition: 280-400 lines.

## Phase 4 — Cross-section coherence pass

**Goal:** With all 9 per-layer Design sections authored, walk through the cross-cutting sections of v4.2.0 and update them so they reference the now-present per-layer content rather than referencing absent content.

**Why this phase:** Phases 2-3 author content INSIDE per-layer sections; Phase 4 updates the OTHER sections that reference those per-layer concepts. Critical for cross-artifact consistency.

**Tasks:**

- **T4.1** — Update Security Considerations subsection: each of the 8 layers currently marked `N/A — out of scope` gets a substantive security subsection. Use Phase 2-3 content as reference.
- **T4.2** — Update Test Boundaries table: 8 layers gain per-layer test type and tooling entries. Use Phase 2-3 content.
- **T4.3** — Update Error Handling table: ensure error categories cover all 9 layers (not just Claude Code FS). Add rows for layer-specific error cases.
- **T4.4** — Update Risks and Mitigation table: add layer-specific risks for the 8 layers (e.g., "Frontend per-layer designer fails to detect accessibility regressions" type entries).
- **T4.5** — Update Acceptance Criteria section: 8 layers currently have no per-layer ACs (only cross-layer/operational). Each layer gains a per-layer AC subsection grouping its FRs (mostly derived from FR-3 fan-out and FR-4 cross-layer dependencies as they apply to that layer).
- **T4.6** — Verify Change Impact Map (fixed in T1.4) is consistent with content authored in Phases 2-3. Reconcile any drift.
- **T4.7** — Verify Project Filesystem table (T1.5) is consistent with per-layer designer knowledge skill names that emerged during Phase 2-3 authoring. Reconcile naming.
- **T4.8** — Update Implementation Plan Phase 2 (inside v4.2.0): per-layer knowledge skill authoring tasks now have specific layer names and reference the per-layer Design sections.
- **T4.9** — Update `state.json` after each task.

**Phase 4 deliverable:** v4.2.0 internally consistent across all sections. Total estimated addition: 250-400 lines.

## Phase 5 — Final review preparation

**Goal:** Pre-flight checks before invoking the 3-stage review chain. Save tokens by catching obvious issues now.

**Tasks:**

- **T5.1** — Run grep checks for residual `N/A — out of scope` markers (should be zero in v4.2.0 except in legitimate places like `Plan` doc_type extension where the codebase analysis JSON is genuinely not provided).
- **T5.2** — Run EARS keyword distribution check across all per-layer AC subsections (verify EARS compliance maintained).
- **T5.3** — Run ADR reference check (all 18 ADR IDs still referenced; no broken links).
- **T5.4** — Run section header count check (still 16 top-level sections per template).
- **T5.5** — Verify v4.2.0 supersedes chain enumerates v3.0.0, v4.0.0, v4.1.0.
- **T5.6** — Update Update History table with v4.2.0 entry.
- **T5.7** — Update `state.json` indicating ready for Phase 6 review.

**Phase 5 deliverable:** v4.2.0 ready for review. Total estimated addition: ~30 lines (minor fixes from grep findings).

## Phase 6 — 3-stage review chain on v4.2.0

**Goal:** Run document-reviewer → synth-architecture-auditor → synth-cross-artifact-auditor on v4.2.0 (same discipline as v4.0.0 review).

**Tasks:**

- **T6.1** — Role-play document-reviewer Pass 1. Output JSON verdict.
- **T6.2** — Role-play synth-architecture-auditor Pass 2 with prior_context_check populated from Pass 1.
- **T6.3** — Role-play synth-cross-artifact-auditor Pass 3 with prior_context_check populated from Pass 2.
- **T6.4** — Aggregate issues across passes. Classify by severity.
- **T6.5** — Update `state.json` with review results.

**Phase 6 deliverable:** v4.2.0 review verdict triple (one per stage). If all three return `approved`, proceed to Phase 7. If any return `needs_revision`, Phase 7 includes reconcile to v4.2.1.

## Phase 7 — Reconcile (if needed) and final staging

**Goal:** Address any issues from Phase 6 reviews; stage final deliverable.

**Tasks (conditional on Phase 6 result):**

- **T7.1** (conditional) — If any Phase 6 review returned `needs_revision` or `rejected`, produce v4.2.1 fixing the issues (same mechanism as v4.0.0→v4.1.0 reconcile).
- **T7.2** (conditional) — Re-run review chain on v4.2.1 with prior_context_check populated.
- **T7.3** — Stage final v4.2.x to `/mnt/user-data/outputs/feature-pipeline-round-3/blueprint-v4.2.x.md`.
- **T7.4** — Update `state.json` to PHASE_7_COMPLETE.

**Phase 7 deliverable:** Final approved v4.2.x staged to outputs.

## Phase 8 — Handoff package

**Goal:** Package everything needed to continue this work in another session.

**Tasks:**

- **T8.1** — Create `state.json` final version with COMPLETE marker, all phase outcomes, all issue lifecycles, file inventory.
- **T8.2** — Author `HANDOFF.md` describing the session's work, what's done, what's pending (if anything), file inventory with descriptions.
- **T8.3** — Author `CONTINUE_PROMPT.md` — a copy-pastable prompt for a new session that re-establishes the project context.
- **T8.4** — Bundle the entire `/mnt/user-data/outputs/feature-pipeline-round-3/` directory plus state files into a zip.
- **T8.5** — Present the zip + continuation prompt to user.

**Phase 8 deliverable:** zip file + copyable prompt.

## State tracking schema

`state.json` shape:
```json
{
  "run_id": "feature-pipeline-design-r3-v4-2-20260512",
  "current_phase": <int>,
  "current_task": "<task-id or null>",
  "phases": {
    "1": {"status": "not_started | in_progress | complete", "tasks": {"T1.1": "complete", ...}, "deliverables": [...]},
    "2": {...},
    ...
  },
  "issues": {
    "from_v4_1_0_review": [],
    "from_v4_2_0_review": []
  },
  "files_produced": [
    {"path": "<path>", "phase": <int>, "task": "<task-id>", "purpose": "<text>"}
  ],
  "last_update": "<ISO-8601 timestamp>"
}
```

## Resume contract

If this session ends mid-execution, the new session can resume by:
1. Reading `state.json` to determine `current_phase` and `current_task`
2. Reading `HANDOFF.md` for full context
3. Reading `CONTINUE_PROMPT.md` and using it as the initial user message in a new conversation
4. Continuing execution from the named task

## Out-of-scope for this plan

- Not authoring the actual implementation Phase content (the knowledge skill bodies, sub-agent definitions, orchestrator skill modifications). Those are Phase 2 of v4.2.0's Implementation Plan section — separate work in a different session after v4.2.0 is approved.
- Not running v4 pipeline against an actual user feature (that's Phase 7 of v4.2.0's Implementation Plan).
- Not revisiting prior ADRs (ADRs 0011-0018 + retroactive 0001-0010 stay as authored).
