---
id: PL-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
derived_from: working/feature/frontend-design-knowledge-r1/blueprint-v1.md
blueprint_version: 1.0.0
architecture_audit: working/feature/frontend-design-knowledge-r1/architecture-audit-issues.json
audit_verdict: pass
generated: 2026-05-21T00:40:00Z
generated_by: plan-author
---

# Implementation Plan: Frontend Design Knowledge Enhancement (Round 1)

## Contents

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — Author `KB-storybook-platform`
- [x] Phase 2 — Author 4 design-side KBs (parallel logical streams)
- [x] Phase 3 — Apply pedagogical markers
- [x] Phase 4 — Update sub-agent frontmatter
- [x] Phase 5 — Update `KB-frontend-design` SKILL.md docstring
- [x] Phase 6 — Run `cc-audit` and resolve violations
- [x] Phase 7 — Rollout / Commit
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

Deliver the frontend-design knowledge corpus enhancement per Blueprint v1.0.0. The Plan sequences 5 new KB authorings, 2 sub-agent frontmatter edits, 1 KB docstring metadata update, and the final audit verification — in dependency order to minimize windows where sub-agents reference KBs that don't yet exist.

## Source

- **Blueprint:** `working/feature/frontend-design-knowledge-r1/blueprint-v1.md` v1.0.0
- **PRD:** `working/feature/frontend-design-knowledge-r1/prd-v1.md` v1.0.0
- **ADR-0024:** Structural choice — four sibling design KBs (Option B). Status: Proposed (becomes Accepted at Blueprint Approval Gate).
- **Inherited ADRs:** ADR-0005, ADR-0011, ADR-0013, ADR-0016, ADR-0017, ADR-0019, ADR-0020, ADR-0021, ADR-0022, ADR-0023.
- **Codebase Analysis:** `working/feature/frontend-design-knowledge-r1/codebase-analysis.json` (FA-001 through FA-006).
- **Architecture Audit:** pass (0 blockers, 0 majors, 0 minors, 2 informational observations).

## Phase 0 — Setup

**Goal:** Confirm execution environment and pre-existing audit baseline.

**Scope:**

- T-0-1: Verify `.claude/skills/` and `.claude/agents/` directories exist and are writable.
- T-0-2: Run baseline `cc-audit` via `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --report /tmp/audit-baseline.md --json`. Record current violation count for delta comparison at Phase 6.
- T-0-3: Confirm Anthropic upstream skill at `/mnt/skills/public/frontend-design/SKILL.md` is readable (cited by Phase 2).
- T-0-4: Snapshot the current `KB-frontend-design/` contents (`git stash` or equivalent) so Phase 5's docstring update can be diffed cleanly for AC-FR-7-a verification.

**Out of scope:** any content authoring; deferred to Phase 1.

**Deliverables:** baseline audit report at `/tmp/audit-baseline.md` (reference for Phase 6 delta check).

**Demonstrable increment:** none (setup phase, no user-visible change).

**Estimation:** small (~10 minutes single-instance).

## Phase 1 — Author `KB-storybook-platform`

**Goal:** Ship the largest single new KB first. Greenfield with no dependencies on other new KBs.

**Scope:**

- T-1-1: Create `.claude/skills/KB-storybook-platform/SKILL.md` with frontmatter (`name: kb-storybook-platform`, multiline `description` documenting model-invocation criteria, `allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch`).
- T-1-2: Author `## Contents` checklist + index prose in SKILL.md (~150-250 lines).
- T-1-3: Create `references/story-format.md` (CSF3 + CSF Factories + meta/args/argTypes/parameters/play/decorators; ~400-600 lines, 3-5 code blocks per 100 lines).
- T-1-4: Create `references/addons.md` (essentials, controls, a11y, viewport, interactions, docs, themes, coverage; ~400-500 lines).
- T-1-5: Create `references/docs.md` (MDX composition; Doc Blocks; decorator stacking; ~300-400 lines).
- T-1-6: Create `references/testing.md` (Chromatic VRT + `@storybook/test-runner` + Vitest integration + axe-core; ~400-500 lines).
- T-1-7: Create `references/composition.md` (multi-package via `refs`; design-system + product topology; ~200-300 lines).

**Out of scope:** sub-agent `skills:` list edits (deferred to Phase 4); pedagogical markers (deferred to Phase 3 — no AI-default-aesthetic content in Storybook KB).

**Deliverables:** `KB-storybook-platform/` complete (SKILL.md + 5 reference files; target 2000-3500 lines total per AC-FR-2-b).

**Dependencies:** Phase 0.

**Demonstrable increment:** `/skill KB-storybook-platform` resolves; user can inspect content.

**Estimation:** large (~2-3 hours single-instance). Largest single phase by content volume.

## Phase 2 — Author 4 design-side KBs (parallel logical streams)

**Goal:** Ship the four new design-side KBs. Logical parallelism — each KB is independent at the file level; cross-references between them are authored in T-2-9 once all four exist.

**Scope:**

Authored sequentially in execution, but per-KB content blocks are self-contained:

- **Stream A — `KB-ux-design`:**
  - T-2-1: Create `KB-ux-design/SKILL.md` (`## Contents`, `## When this KB is loaded`, index prose; ~100-150 lines).
  - T-2-2: Create `references/principles.md` (Nielsen's 10 with one-line summaries; cognitive load; error prevention/recovery; ~200-300 lines).
  - T-2-3: Create `references/journey-and-ia.md` (Norman's 7 stages; service blueprint; customer journey map; JTBD; card sort; tree test; content inventory; ~250-350 lines).
  - T-2-4: Create `references/accessibility-as-flow.md` (focus restoration; live-region choreography; error-recovery for AT; keyboard task completion; cognitive-load reduction; focus indicators; heading hierarchy; ~300-400 lines).

- **Stream B — `KB-visual-design`:**
  - T-2-5: Create `KB-visual-design/SKILL.md` (~100-150 lines).
  - T-2-6: Create `references/type-color-space.md` (type scales; color systems; spacing; iconography; ~300-400 lines).
  - T-2-7: Create `references/motion.md` (Material 3 + Apple HIG + Disney 12; cubic-bezier curves; `prefers-reduced-motion`; ~200-300 lines).
  - T-2-8: Create `references/responsive.md` (breakpoints; container queries; fluid type/space; density spectrum; ~200-300 lines).
  - T-2-9: Create `references/anti-slop.md` per D-002 (cites Anthropic upstream; names slop signatures; carries pedagogical markers added in Phase 3; ~250-400 lines).

- **Stream C — `KB-design-system-design`:**
  - T-2-10: Create `KB-design-system-design/SKILL.md` (~100-150 lines).
  - T-2-11: Create `references/tokens.md` (three-tier model with Carbon / Material 3 / Primer / Salesforce mappings; W3C DTCG; ~300-400 lines).
  - T-2-12: Create `references/theming.md` (CSS variables / Style Dictionary / build-time / CSS-in-JS legacy; ~200-300 lines).
  - T-2-13: Create `references/governance.md` (semver discipline; tokens-components-patterns three-layer; ~200-300 lines).

- **Stream D — `KB-component-architecture-design`:**
  - T-2-14: Create `KB-component-architecture-design/SKILL.md` (~100-150 lines).
  - T-2-15: Create `references/atomic-design.md` (Frost's 5 tiers; mental-model-not-file-structure; ~200-300 lines).
  - T-2-16: Create `references/headless-libraries.md` (Radix UI / React Aria / Headless UI / Ariakit / shadcn-ui; ~300-400 lines).
  - T-2-17: Create `references/patterns.md` (compound; slot — both senses; polymorphic `as`; controlled-vs-uncontrolled; ref forwarding incl. React 19; prop API; ~400-500 lines, 1-2 code blocks per 100 lines).

- **Cross-stream:**
  - T-2-18: Author cross-references in each new KB's `## Related KBs` section once all 4 exist (KB-component-architecture-design references KB-design-system-design's token tier model; KB-visual-design's `references/anti-slop.md` references KB-component-architecture-design's headless-library examples; etc.).

**Out of scope:** pedagogical markers (deferred to Phase 3); sub-agent `skills:` list edits (deferred to Phase 4).

**Deliverables:** 4 new design-side KBs (each ~600-1200 lines per blueprint sizing); cross-references established.

**Dependencies:** Phase 1 (Storybook KB shape is the template for KB authoring discipline; sequencing this after Storybook lets authoring discipline calibrate before applying to design-side content). Logical: Streams A-D can run in any order; T-2-18 requires all 4 streams done.

**Demonstrable increment:** all 5 new KBs available at `/skill KB-<name>`.

**Estimation:** large (~4-6 hours single-instance for all 4 streams; each stream ~1-1.5 hours).

## Phase 3 — Apply pedagogical markers

**Goal:** Per D-006 + AC-FR-5-a, apply pedagogical markers surgically to content that names AI-default aesthetics by name.

**Scope:**

- T-3-1: Apply markers per `pedagogical-marker-spec.md` to `KB-visual-design/references/anti-slop.md` (heavy density — names Inter, Roboto, system fonts, purple-gradient-on-white, Space Grotesk, default-rounded-shadcn).
- T-3-2: Apply markers to `KB-visual-design/SKILL.md` and `references/type-color-space.md` where negative-reference to AI-default aesthetics appears (medium density).
- T-3-3: Spot-check other new KBs for incidental pedagogical content (low density expected; T-001's research note pattern of citing AI-slop signatures by name only appears in anti-slop content).
- T-3-4: Run partial `cc-audit` scoped to the new KB directories to verify markers parse correctly.

**Out of scope:** full audit (deferred to Phase 6).

**Deliverables:** pedagogical markers applied per spec; partial audit clean.

**Dependencies:** Phase 2 (content must exist before marking).

**Demonstrable increment:** marker application verified at content-level.

**Estimation:** small (~30 minutes single-instance).

## Phase 4 — Update sub-agent frontmatter

**Goal:** Per FR-4, expand `design-frontend.md` and `design-composer.md` `skills:` lists to preload the 4 new design-side KBs. `KB-storybook-platform` is NOT added to either (model-invocable per Primitive 5; D-005's lowest-cost-primitive rationale).

**Scope:**

- T-4-1: Edit `.claude/agents/design-frontend.md` frontmatter. Expand `skills:` from `[KB-frontend-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines]` (4 entries) to `[KB-frontend-design, KB-ux-design, KB-visual-design, KB-design-system-design, KB-component-architecture-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines]` (8 entries).
- T-4-2: Edit `.claude/agents/design-frontend.md` body — add a paragraph documenting when to model-invoke `KB-storybook-platform` ("Invoke `KB-storybook-platform` when the feature's frontend includes Storybook stories, custom addons, or visual regression test integration.").
- T-4-3: Edit `.claude/agents/design-composer.md` frontmatter. Expand `skills:` list to include the 4 new design-side KBs. Existing entries preserved.
- T-4-4: Edit `.claude/agents/design-composer.md` body — add the same model-invocation paragraph as T-4-2.

**Out of scope:** any reasoning-configuration changes (`model:`, `effort:`); any tool list changes.

**Deliverables:** both agent files updated; `skills:` lists carry the new KB references.

**Dependencies:** Phase 2 (all 4 new design-side KBs must exist before being preloaded).

**Demonstrable increment:** next pipeline invocation of `design-frontend` or `design-composer` preloads the new KBs.

**Estimation:** small (~15 minutes single-instance; 4 atomic edits).

## Phase 5 — Update `KB-frontend-design` SKILL.md docstring

**Goal:** Per Modification 3 + AC-FR-7-a, update the existing `KB-frontend-design/SKILL.md` frontmatter description to name the new sibling KBs and clarify scope. Content unchanged (preserves ADR-0005).

**Scope:**

- T-5-1: Edit `.claude/skills/KB-frontend-design/SKILL.md` frontmatter only. Update `description:` to name the four new sibling design KBs and clarify that `KB-frontend-design` is the backend-of-the-frontend + a11y-baseline KB. The "no platform partner KB (frontend platforms vary widely)" sentence stays.
- T-5-2: Verify `.claude/skills/KB-frontend-design/references/principles.md` and `references/patterns-and-anti-patterns.md` are unchanged via `git diff` (AC-FR-7-a verification).

**Out of scope:** any content change to the 2 reference files; any structural change.

**Deliverables:** `KB-frontend-design/SKILL.md` docstring refreshed; reference files untouched (verified by diff).

**Dependencies:** Phase 2 (the new sibling KBs must exist for the docstring to reference them by name).

**Demonstrable increment:** `git diff` shows only frontmatter description change in SKILL.md; zero changes in `references/`.

**Estimation:** small (~10 minutes single-instance).

## Phase 6 — Run `cc-audit` and resolve violations

**Goal:** Per AC-FR-5-b + NFR-2-a, the full audit passes with zero new violations.

**Scope:**

- T-6-1: Run `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --report /tmp/audit-final.md --json`.
- T-6-2: Compare against the Phase 0 baseline. Zero new violations is the target. Any new violations are triaged:
  - Pedagogical-content-match false positives → confirm marker application is per spec; the Step 4 verification disposes correctly. Document in audit notes.
  - Frontmatter conformance violations → fix in the relevant SKILL.md.
  - Structural violations (missing `## Contents`, etc.) → fix in the relevant file.
- T-6-3: If any violation cannot be resolved by adjustment alone, route to Reconciliation cycle (per ADR-0021).
- T-6-4: Re-run audit after fixes. Repeat until zero new violations.

**Out of scope:** baseline violations from prior project state (those are unrelated to this feature; tracked separately).

**Deliverables:** `cc-audit` final report at `/tmp/audit-final.md`; zero new violations; audit JSON capturing pre/post counts.

**Dependencies:** Phases 1-5 (all content authored and edits applied).

**Demonstrable increment:** audit clean; the feature is ready for commit.

**Estimation:** medium (~30-60 minutes single-instance, including any iteration if violations surface).

## Phase 7 — Rollout / Commit

**Goal:** Land the changes. For a local-pipeline feature, "rollout" is commit + zip rebuild + handoff.

**Scope:**

- T-7-1: Stage all changes (`git add .claude/`).
- T-7-2: Commit with structured message referencing PRD + Blueprint + ADR-0024.
- T-7-3: Rebuild project zip — version bumps to **v4.4.0** per ADR-0005 (minor: knowledge addition + new ADR; 5 new KBs is a more-than-patch change).
- T-7-4: Update `HANDOFF-v4.4.0.md` documenting the Round 1 completion and Round 2 placeholder.
- T-7-5: Update `CONTINUE_PROMPT` for next session.

**Out of scope:** Round 2 planning (deferred to a future feature run).

**Deliverables:** committed change set; v4.4.0 zip; updated HANDOFF and CONTINUE_PROMPT.

**Dependencies:** Phase 6 (audit clean).

**Demonstrable increment:** v4.4.0 archive ready for next session.

**Estimation:** small (~20 minutes single-instance).

## Cross-Phase Dependencies

```
Phase 0 (Setup) → Phase 1 (KB-storybook-platform) → Phase 2 (4 design-side KBs) → Phase 3 (markers) → Phase 4 (agent frontmatter)
                                                                                                    → Phase 5 (KB-frontend-design docstring)
                                                                                                    → Phase 6 (audit)
                                                                                                    → Phase 7 (rollout)
```

- Phases 4 and 5 are independent of each other once Phase 2 completes; could run in parallel logical streams.
- Phase 6 requires all of Phases 1-5.
- Phase 3 strictly follows Phase 2 (markers cannot apply to non-existent content).

## L1/L2/L3 Verification Discipline

- **L1 (syntactic):** every new file passes its respective parser (Markdown for `.md`, JSON for `.json`, YAML frontmatter parses). Implicit in file authoring.
- **L2 (structural):** every new KB SKILL.md has frontmatter with `name`/`description`/`allowed-tools`; every SKILL.md and reference file has `## Contents` H2 checklist; design KBs have `## When this KB is loaded`. Verified by `auditing-cc-configs` at Phase 6.
- **L3 (semantic):** voice matches `KB-cc-platform`; content matches research-notes acceptance-criteria; cross-references resolve correctly. Verified by manual review at Final Approval Gate.

## Acceptance Test Cross-Reference

Each PRD AC maps to one or more Plan tasks:

| AC | Plan tasks |
|---|---|
| AC-FR-1-a (anti-slop preload via KB-visual-design) | T-2-5, T-2-9, T-3-1 |
| AC-FR-1-b (UX + a11y-flow via KB-ux-design) | T-2-1 through T-2-4 |
| AC-FR-1-c (UI/visual via KB-visual-design) | T-2-5 through T-2-8 |
| AC-FR-1-d (design-system via KB-design-system-design) | T-2-10 through T-2-13 |
| AC-FR-1-e (component-arch via KB-component-architecture-design) | T-2-14 through T-2-17 |
| AC-FR-1-f (Storybook model-invocable) | Phase 1 + T-4-2 |
| AC-FR-2-a (design-KB code density ≤1.5) | implicit in Phase 2 authoring |
| AC-FR-2-b (Storybook code density 3-5) | implicit in Phase 1 authoring |
| AC-FR-3-a (naming convention) | T-1-1, T-2-1/5/10/14 (frontmatter `name:` field) |
| AC-FR-3-b (KB structure) | Phase 1 + Phase 2 (SKILL.md + references/) |
| AC-FR-3-c (`## Contents` checklists) | implicit in all file authoring |
| AC-FR-4-a (design-frontend.md skills list) | T-4-1, T-4-2 |
| AC-FR-4-b (design-composer.md skills list) | T-4-3, T-4-4 |
| AC-FR-5-a (pedagogical markers) | T-3-1, T-3-2, T-3-3, T-3-4 |
| AC-FR-5-b (cc-audit zero new violations) | T-6-1, T-6-4 |
| AC-FR-5-c (only design-composer authors ADRs) | already satisfied at Design Composition stage (ADR-0024) |
| AC-FR-6-a (senior-engineer-handbook voice) | implicit in Phase 1 + Phase 2 authoring; verified at Final Approval Gate |
| AC-FR-7-a (KB-frontend-design content preserved) | T-5-2 |
| AC-FR-8-a (pipeline-machinery defect capture, conditional) | recorded during execution; sibling ADR if triggered |

Coverage: 19 ACs from Blueprint; 19 ACs mapped to Plan tasks. No orphan ACs.

## Estimation Methodology

Estimates are single-instance human-equivalent effort:
- **small** = ≤30 minutes
- **medium** = 30-120 minutes
- **large** = 2-6 hours

Estimates are coarse; the variance dominant factor is content authoring quality (matching `KB-cc-platform` voice across 5 new KBs requires editorial discipline).

## Resourcing Posture

- **Authoring sub-agent:** in execution, individual KB content can be authored by a content-authoring sub-agent (or directly by the user / Claude). For this walkthrough, authoring would happen via Claude file tools.
- **Audit:** automatic per `auditing-cc-configs/scripts/audit_project.py`.
- **Manual review:** at the Final Approval Gate (Gate 6).

## Open Items (Pending Cross-Artifact Audit)

None blocking. Two recorded by Architecture Audit (INFO-001, INFO-002) for the Cross-Artifact Audit to verify Plan addresses:

- **INFO-001** (documentation coupling): Plan honors ADR-0005 supersession for future revisions. ✓
- **INFO-002** (external dependency on Anthropic skill): Phase 2 T-2-9 (anti-slop reference file) should include a "Source Dependencies" section per the recommendation; Plan adds this expectation to T-2-9's scope statement.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-21 | plan-author | Initial Plan authored; 7 phases sequenced; 19 ACs cross-referenced; 0 open items |
