---
id: PV-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
derived_from: working/feature/frontend-design-knowledge-r1/plan-v1.md
plan_version: 1.0.0
generated: 2026-05-21T00:50:00Z
generated_by: test-phase-validator-author
---

# Phase Validators: Frontend Design Knowledge Enhancement (Round 1)

## Contents

- [x] Validator discipline
- [x] Phase validators (8 entries: Phases 0-7)
- [x] Validator escalation policy

## Validator discipline

Per Plan v1.0.0, the feature has 8 phases (0-7). Each phase has a validator: a set of pass criteria that must hold before the next phase can begin. Validators check three categories:

- **Acceptance tests scheduled for this phase** — subset of the 19 acceptance tests assigned to this phase per Plan AC cross-reference.
- **Phase-specific operational checks** — phase-local invariants (e.g., baseline audit captured for Phase 0; no agent frontmatter changes until Phase 4).
- **Phase-specific NFR slices** — performance / size / scope checks where applicable.

Severity taxonomy:

- **BLOCKER** — phase cannot complete; reconciliation cycle triggered.
- **MAJOR** — phase complete with documented exception; downstream phase must adapt.
- **MINOR** — phase complete; deferred follow-up captured for next round.
- **INFO** — phase complete; observation recorded.

Each validator declares its automation hook (where automatable) and its manual-check requirement (where editorial / provenance judgment is needed).

## Phase validators

### Phase 0 — Setup

**Pass criteria:**
1. `.claude/skills/` and `.claude/agents/` directories exist and writable.
2. Baseline audit report exists at `/tmp/audit-baseline.md` with violation count recorded.
3. Anthropic upstream skill at `/mnt/skills/public/frontend-design/SKILL.md` is readable.
4. `KB-frontend-design/` content snapshot captured (git stash or equivalent).

**Severity rules:**
- (1) failure → BLOCKER (filesystem prerequisite).
- (2) failure → BLOCKER (baseline needed for Phase 6 delta).
- (3) failure → MAJOR (anti-slop reference cannot be authored without upstream access; alternative: cite Anthropic skill by name only, no inline content).
- (4) failure → MAJOR (AC-FR-7-a verification weakens without clean baseline).

**Automation hook:** bash `test -d` + `test -f` + `test -r`. Snapshot via `git stash list | head` verification.

### Phase 1 — KB-storybook-platform authored

**Pass criteria:**
1. `KB-storybook-platform/SKILL.md` exists with valid frontmatter (`name: kb-storybook-platform`; `description:`; `allowed-tools:`).
2. All 5 reference files exist with substantive content (≥ 200 lines each).
3. Total KB size in range 2000-3500 lines (AC-FR-2-b precursor).
4. Code-block density 3-5 per 100 lines (AC-FR-2-b).
5. Each file has `## Contents` H2 (AC-FR-3-c precursor).

**Severity rules:**
- (1) (2) (5) failures → BLOCKER (structural conformance).
- (3) failure → MAJOR (size target; depth proxy).
- (4) failure → MINOR (density target; soft cap).

**Automation hook:** bash arithmetic + grep + cc-audit partial.

**Acceptance tests verified at this phase:** AC-FR-3-b (precursor), AC-FR-3-c (precursor), AC-FR-3-a (Storybook naming).

### Phase 2 — 4 design-side KBs authored

**Pass criteria:**
1. All 4 KB directories exist: KB-ux-design, KB-visual-design, KB-design-system-design, KB-component-architecture-design (AC-FR-3-a).
2. Each KB has SKILL.md + ≥ 3 reference files (AC-FR-3-b).
3. Each file has `## Contents` H2 (AC-FR-3-c).
4. Each KB's SKILL.md has frontmatter conforming to KB-cc-design convention.
5. Design-side KB code-block density ≤ 1.5 per 100 lines (AC-FR-2-a soft cap).
6. Cross-references between the 4 KBs are present in `## Related KBs` sections.
7. Content-specific checks:
   - KB-ux-design/references/principles.md enumerates Nielsen's 10 heuristics.
   - KB-visual-design/references/anti-slop.md cites Anthropic frontend-design skill.
   - KB-design-system-design/references/tokens.md covers three-tier model.
   - KB-component-architecture-design/references/headless-libraries.md names ≥ 5 libraries.

**Severity rules:**
- (1) (2) (3) (4) failures → BLOCKER.
- (5) failure → MINOR (soft cap; rationale documented).
- (6) failure → MAJOR (cross-references are required per cc-design Modification 1 rationale).
- (7) sub-failures → MAJOR (content-coverage; substantive correctness).

**Automation hook:** bash + grep + cc-audit + content-pattern checks.

**Acceptance tests verified at this phase:** AC-FR-1-b, AC-FR-1-c, AC-FR-1-d, AC-FR-1-e, AC-FR-2-a, AC-FR-3-a, AC-FR-3-b, AC-FR-3-c.

### Phase 3 — Pedagogical markers applied

**Pass criteria:**
1. `KB-visual-design/references/anti-slop.md` contains marker patterns per `pedagogical-marker-spec.md`.
2. Other files with negative-references to AI-default aesthetics carry appropriate markers (medium density).
3. Partial cc-audit of new KB directories returns zero new violations from marker mis-application.

**Severity rules:**
- (1) failure → BLOCKER (the anti-slop file is the marker-heavy target).
- (2) failure → MAJOR.
- (3) failure → BLOCKER if cc-audit Step 4 verification fails on pedagogical content.

**Automation hook:** cc-audit partial; bash grep for marker patterns.

**Acceptance tests verified at this phase:** AC-FR-5-a, AC-FR-1-a (precursor — anti-slop file structurally validated).

### Phase 4 — Sub-agent frontmatter updated

**Pass criteria:**
1. `design-frontend.md` frontmatter `skills:` list contains 8 entries (the 4 existing + 4 new) (AC-FR-4-a).
2. `design-frontend.md` body contains a paragraph documenting model-invocation of `KB-storybook-platform`.
3. `design-composer.md` frontmatter `skills:` list contains the 4 new design-side KBs in addition to existing entries (AC-FR-4-b).
4. `design-composer.md` body contains the same model-invocation paragraph.
5. Neither agent's frontmatter has `KB-storybook-platform` in the `skills:` list (model-invocable only per D-005 rationale).
6. No reasoning-configuration changes (`model:`, `effort:`, `tools:`, `memory:` unchanged).

**Severity rules:**
- (1) (3) failures → BLOCKER.
- (2) (4) failures → MAJOR (documentation completeness).
- (5) failure → BLOCKER (violates D-005 lowest-cost-primitive rationale; ADR-0024 misapplied).
- (6) failure → BLOCKER (out-of-scope change).

**Automation hook:** bash grep + cc-audit frontmatter check + git diff scope check.

**Acceptance tests verified at this phase:** AC-FR-1-f, AC-FR-4-a, AC-FR-4-b.

### Phase 5 — KB-frontend-design SKILL.md docstring updated

**Pass criteria:**
1. `git diff .claude/skills/KB-frontend-design/SKILL.md` shows ONLY frontmatter `description:` changes.
2. `git diff .claude/skills/KB-frontend-design/references/` returns empty (AC-FR-7-a).
3. Updated description names the 4 new sibling design KBs.
4. The "no platform partner KB (frontend platforms vary widely)" sentence is preserved (still accurate).

**Severity rules:**
- (1) failure → BLOCKER (out-of-scope change to body; violates ADR-0005).
- (2) failure → BLOCKER (violates AC-FR-7-a / ADR-0005 — append-only supersession).
- (3) failure → MAJOR (documentation completeness).
- (4) failure → MAJOR (the rejection is still load-bearing).

**Automation hook:** git diff + bash grep.

**Acceptance tests verified at this phase:** AC-FR-7-a.

### Phase 6 — cc-audit and resolution

**Pass criteria:**
1. Full cc-audit completes successfully (no script failures).
2. Final violation count = baseline violation count (zero new violations from this feature; AC-FR-5-b).
3. Any cc-audit Step 4 verifications on pedagogical content resolve correctly (benign).

**Severity rules:**
- (1) failure → BLOCKER (audit infrastructure broken — independent of this feature).
- (2) failure → BLOCKER (Reconciliation cycle triggered per ADR-0021).
- (3) failure → MAJOR (pedagogical-marker mis-application; fix at Phase 3 in re-run).

**Automation hook:** `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --report /tmp/audit-final.md --json` + delta comparison.

**Acceptance tests verified at this phase:** AC-FR-5-a (final verification), AC-FR-5-b.

### Phase 7 — Rollout / Commit

**Pass criteria:**
1. All changes staged via `git add .claude/`.
2. Commit message references PRD + Blueprint + ADR-0024.
3. Project zip rebuilt at v4.4.0 (minor bump per ADR-0005).
4. `HANDOFF-v4.4.0.md` and `CONTINUE_PROMPT` updated.
5. AC-FR-5-c (provenance) verified: ADR-0024's `generated_by` is design-composer.
6. AC-FR-6-a (voice) verified by user at the Final Approval Gate (this is Gate 6's check, not Phase 7's; Phase 7 records the verification outcome).
7. AC-FR-8-a (pipeline-machinery defects) recorded: either a sibling ADR exists OR documented that no defects surfaced.

**Severity rules:**
- (1) (2) failures → BLOCKER (commit hygiene).
- (3) (4) failures → MAJOR (release artifact completeness).
- (5) failure → BLOCKER (provenance is design-by-pipeline).
- (6) failure → BLOCKER (Gate 6 user rejection; reconciliation triggered).
- (7) failure → MINOR (record-keeping).

**Automation hook:** git status + bash + manual provenance verification.

**Acceptance tests verified at this phase:** AC-FR-5-c, AC-FR-6-a, AC-FR-8-a.

## Validator escalation policy

If a phase validator surfaces a BLOCKER:
1. Stop execution; do not proceed to the next phase.
2. Route to Reconciliation cycle per ADR-0021. Cap: 4 cycles per ADR-0021.
3. If reconciliation fails to resolve within 4 cycles, route to user (out-of-band) for direction.

If a phase validator surfaces a MAJOR:
1. Document the exception in the phase's execution log.
2. Proceed with documented adaptation in the downstream phase.

If a phase validator surfaces MINOR or INFO:
1. Record for follow-up; proceed.
