---
id: PLAN-audit-findings-remediation-r1
version: 1.1.0
supersedes: plan-v1.md (v1.0.0)
status: superseded
feature_slug: audit-findings-remediation-r1
derived_from:
  - working/feature/audit-findings-remediation-r1/blueprint-v1.md (v1.0.0, approved)
  - working/feature/audit-findings-remediation-r1/cc-dependencies.json
  - working/feature/audit-findings-remediation-r1/architecture-audit-issues.json (PASS)
  - working/feature/audit-findings-remediation-r1/cross-artifact-audit-issues.json (round 1, conditional_pass)
  - working/feature/audit-findings-remediation-r1/reconciliation-log-cycle1.md
generated: 2026-05-21T20:42:00Z
generated_by: claude (acting as plan-author re-invoked by finalize-reconciler, continuation session)
supersession_addresses:
  - I-CA-001 (MAJOR — P6.6 stage-number discipline violation)
  - I-CA-002 (MAJOR — P1.4 intermediate-state audit capture missing)
  - I-CA-003 (MINOR — P1.3 SKILL.md temporal listing of scan_memory_secrets.py)
superseded_by: plan-v1.2.0.md
---

# Plan v1 — Audit Findings Remediation (r1)

## Contents

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — Foundation (mechanism-α spec + auditing-shared module)
- [x] Phase 2 — Auditor improvements (parallel)
- [x] Phase 3 — Real-fix dispositions (parallel with Phase 2)
- [x] Phase 4 — Marker upgrades + new markers
- [x] Phase 5 — Verification records (FR-6 Stream 1)
- [x] Phase 6 — Integration + final audit
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items
- [x] Update History

## Purpose

Sequence the 28 dependency-graph items from `cc-dependencies.json` into executable phases honoring the dependency constraints from cc-design + the discipline constraints from PRD + ADR-0029 + ADR-0030 + ADR-0031.

Per user constraint 4 (sequencing belongs to Plan stage), this is where ordering decisions land. Plan stage also resolves U-3 (release version) and the D-4 secondary-audit question.

## Source

- **Blueprint v1.0.0** (Gate 4 approved) — design source
- **`cc-dependencies.json`** — 28 items in 8 dependency groups; longest critical path = 4 steps
- **Architecture Audit** — PASS verdict; 3 informational observations carried forward (OBS-1/2/3)
- **PRD v1.2.0** — 12 FRs; 26+ ACs

## Phase 0 — Setup

### P0.1 — Baseline snapshot

Capture the current audit state for delta tracking:

```bash
python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . \
  --report /tmp/baseline-audit.md --json > /tmp/baseline-audit.json
```

Confirm baseline matches the PRD-stated values (77 BLOCKER / 42 MAJOR / 29 MINOR). If divergent, surface per ADR-0029 BEFORE phase 1 begins.

### P0.2 — Test-fixture workspace creation

Create `/tmp/audit-findings-fixtures/` for the negative-test fixtures the Acceptance Tests stage will need. Includes:

- A mock SKILL.md with `pedagogical_sections:` declarations both with and without justifications (FR-7-c test)
- A mock agent body with both negation-prefixed and bare instructions (FR-5-d test)
- A mock agent description with both clearly-triggering and clearly-vague language (FR-4-b test)

Fixtures themselves are authored in Phase 2 alongside the auditor changes.

### P0.3 — Release-version decision (U-3 resolution)

**Decision:** This feature ships as **v4.6.0** — MINOR bump from v4.5.0.

**Rationale:**
- New skill module (`auditing-shared`) is a feature addition, not breaking.
- Mechanism α is a new policy that affects authoring but is backward-compatible at audit-output level (markers without justification produce the same finding the auditor would have produced if the marker weren't there).
- FR-12 deduplication is internal refactoring; no observable behavior change for audit consumers.
- v5.0.0 would signal breaking change; nothing breaks.

## Phase 1 — Foundation

**Goal:** Land the cross-cutting spec and the canonical auditor module that everything else depends on.

**Dependency-graph items:** F-1-1, F-2-1, F-2-2, F-2-3

**Parallelizable internally:** No — F-1-1 → F-2-1 → F-2-3 is a serial chain by dependency.

### P1.1 — Author mechanism-α spec (F-1-1)

Create `.claude/skills/KB-documentation-criteria/references/pedagogical-marker-justification-spec.md`.

Content (per ADR-0030 + per Q-CC-6 + per OBS-3):

- Section 1: Why this spec exists (refers to ADR-0030)
- Section 2: Frontmatter form (structured dict)
- Section 3: Fence form (`--` separator)
- Section 4: Justification validity rules (length, banned bare words, substance requirement)
- Section 5: Auditor rejection behavior
- Section 6: Reviewer enforcement (PedagogicalMarkerJustification doc_type)
- Section 7: Extension procedure for substance-keyword list (per OBS-3 — must be explicit subsection)
- Section 8: Examples (valid + rejected — pedagogical content about the discipline itself; mechanism α applies)

Verification: shared-document-reviewer reviews against template; per L1 check.

### P1.2 — Update existing `pedagogical-marker-spec.md` with forward-pointer (F-1-3)

Add a top-of-file note in `.claude/skills/auditing-cc-configs/references/pedagogical-marker-spec.md` pointing to the new justification spec. One-paragraph addition.

### P1.3 — Create `auditing-shared` skill module (F-2-1, F-2-2)

Create `.claude/skills/auditing-shared/` directory + `SKILL.md`.

`SKILL.md` content (≤30 lines per OBS-2):

```markdown
---
name: auditing-shared
description: Utility module housing scripts shared across the auditing-* audit family (auditing-cc-configs, auditing-skills, auditing-subagents, auditing-context-files, etc.). NOT directly invocable — this module is a code-organization unit, not an audit target or capability. Future audit utilities used by 2+ audit dispatchers belong here.
user-invocable: false
---

# auditing-shared

This skill module houses utility scripts shared across the audit family. It exists per ADR-0031 to provide a canonical home for code that would otherwise be duplicated across sibling audit skills.

## Contents

- `scripts/pedagogical_marker_check.py` — canonical pedagogical-marker triage with mechanism-α enforcement (per ADR-0030)

*Note: `scripts/scan_memory_secrets.py` will be added to this listing when it is created in P4.2 (per supersession address of I-CA-003 from cross-artifact audit round 1).*

## Stability commitment

Scripts here are imported / invoked by other auditing skills' dispatchers. Breaking changes require coordinated updates to all callers and a corresponding ADR.

## What does NOT belong here

- Skill-specific logic (e.g., `analyze_subagent.py`'s SA-2 regex is subagent-specific)
- Test fixtures (live with the audit module they test)
- One-off helpers used by exactly one audit dispatcher
```

### P1.4 — Author canonical `pedagogical_marker_check.py` (F-2-3)

Create `.claude/skills/auditing-shared/scripts/pedagogical_marker_check.py`.

Content: union of the 3 existing copies + new mechanism-α enforcement.

Implementation steps:

1. Copy `auditing-cc-configs/scripts/pedagogical_marker_check.py` as the base (most-trafficked).
2. Add the `f.get("location") or f.get("where")` defensive backward-compat from the `auditing-skills` copy (per AC-FR-12-d).
3. Add a new function `justification_valid(j: str) -> bool` implementing D-3 rules (length floor, banned bare-words, substance keyword).
4. **Capture intermediate audit** (per supersession address of I-CA-002 from cross-artifact audit round 1): `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --json > /tmp/post-dedup-audit.json`. This captures the post-dedup / pre-mechanism-α / pre-schema-change state on the real corpus — the artifact AT-030 and PV-1.C5 require to verify AC-FR-12-c behavior equivalence. The justification_valid helper from step 3 is authored but NOT yet wired into the triage path; the input-schema parser is unchanged. At this moment the audit output should equal the baseline modulo no deltas.
5. Modify the existing marker-triage logic: when a marker is found, also check its justification is valid; if not, the marker is treated as absent (underlying finding surfaces at original severity).
6. Update the input-schema parsing to handle the new structured form (`pedagogical_sections: [{ path, justification }]`) instead of the old bare-list form.
7. Update the fence-form parser to expect ` -- justification` after `audit-example`.

Verification: Step 4's intermediate audit + the baseline audit (from P0.1) together verify AC-FR-12-c behavior equivalence on the real corpus (AT-030, PV-1.C5). Fixture-based negative tests after step 7 verify the new rejection behavior (AT-021 sub-tests).

**Gate within phase:** Before proceeding to Phase 2/3/4, verify P1.4's behavior-equivalence test passes (AC-FR-12-c).

## Phase 2 — Auditor improvements (parallel with Phase 3)

**Goal:** Fix the auditor regexes + replace the X9 stub. None depend on Phase 1 outputs (they're separate auditor modules).

**Dependency-graph items:** F-3-1, F-3-2, F-3-3

**Parallelizable internally:** Yes — all three edits are in different files with no inter-dependency.

### P2.1 — Tighten SA-2 TRIGGER_PATTERNS (F-3-1)

Edit `auditing-subagents/scripts/analyze_subagent.py`. Add 4 pattern alternatives per D-4 + Blueprint Design section. Verify with negative-test fixture (vague description still fires SA-2; project's actual descriptions no longer fire).

Per AC-FR-4-b decision (D-4-iii both): also queue secondary review of 29 flagged descriptions for genuine quality issues. If any fail the new regex too (which they shouldn't, but the secondary audit catches edge cases), they get a one-line tweak.

### P2.2 — Negation-aware bypass-approval regex (F-3-2)

Edit `auditing-subagents/scripts/scan_subagent_body.py`. Two-pass implementation per Blueprint Design (avoids Python lookbehind fixed-width constraint).

Verify with FR-5-d negative test: "do NOT skip" produces zero findings; "skip the permission policy" produces BLOCKER.

### P2.3 — Wire X9 recursive check (F-3-3)

Edit `auditing-cc-configs/scripts/cross_file_checks.py`. Replace `check_X9_subagent_skills_security_block` stub per D-6. Use existing subprocess dispatch pattern from `audit_project.py:51`. Cache per (subagent, skill) pair within single audit run.

Per AC-FR-6-a/c: post-fix X9 emission is either zero (all preloaded skills pass) OR carries actionable detail (named failed skill + check). Improvement, not suppression.

## Phase 3 — Real-fix dispositions (parallel with Phase 2)

**Goal:** Apply real fixes for Category C + Category E wildcard-shell. Independent of Phases 1 & 2.

**Dependency-graph items:** F-4-1, F-4-2, F-5-1, F-5-2; F-4-3 depends on P1.1 only.

### P3.1 — Scope Bash tool in 3 agents (F-4-1, F-4-2)

For `discovery-codebase-researcher.md` and `review-architecture-auditor.md`: inspect each agent's body to identify the specific Bash commands actually used; scope `Bash` to `Bash(<command>:*)` form. Likely scopes (Plan-time guess; per-layer Design confirms during execution): `Bash(git diff:*)`, `Bash(find:*)`, `Bash(grep:*)`, `Bash(python3:*)`.

### P3.2 — Scope Bash + add PedagogicalMarkerJustification doc_type to shared-document-reviewer (F-4-3)

Edit `shared-document-reviewer.md`:
- Scope `Bash` per P3.1 pattern.
- Add `PedagogicalMarkerJustification` to the doc_type taxonomy.
- Add documentation for the new doc_type (procedure: read target file; parse markers; validate each per mechanism α; emit findings).

Depends on P1.1 (mechanism-α spec) for the validation procedure to reference.

### P3.3 — Fix 18 Category C broken links (F-5-1, F-5-2)

Per AC-FR-3-b, per-finding disposition: repair / delete / reauthor. For `skills/synthesize/*`:

- `references/examples.md` → `output/auth-research.md`, `output/caching-survey.md` — likely DELETE references (output/ files don't exist; references are illustrative of past synthesis runs that don't apply here)
- `references/substrate-registry.md` → `commands/synthesize.md`, `output/constraint-aware-synthesis.md`, `skills/synthesize/SKILL.md` — `commands/synthesize.md` doesn't exist (no slash-command file); REPAIR to backticked plain text. `skills/synthesize/SKILL.md` self-link → REPAIR path. `output/constraint-aware-synthesis.md` → DELETE.
- `references/validators/json-schema-validator.md` → `skills/synthesize/SKILL.md` + `skills/synthesize/references/schemas/claim.schema.json` — REPAIR paths.
- `references/templates/blueprint-template.md` → `.devcontainer/devcontainer.json`, `.devcontainer/docker-compose.yml` — these are pedagogical example paths in a template; REWRITE to backticked plain text per AC-FR-2-b.
- `references/recipe-python.md` → `script.py` — REPAIR (it's a relative reference inside an example).
- `scripts/action_versions.md` → `.github/labeler.yml` — pedagogical-example path; REWRITE to backticked plain text.

For `report-composition-knowledge/*`:
- All 11 broken-link findings point to `output/*` files that the report-composition references as example outputs. DELETE or REWRITE to backticked plain text per case-by-case.

Per-disposition decisions land in `working/feature/.../implementation-notes.md` (created during execution) and are audited per FR-3-b.

## Phase 4 — Marker upgrades + new markers

**Goal:** FR-7-d (every marker passes discipline) + FR-8 (retroactive upgrade) + FR-1/FR-2 (Cat A/B new markers).

**Dependency-graph items:** F-6-1, F-6-2, F-6-3, F-7-1, F-7-2, F-7-3, F-7-4

**Parallelizable internally:** Mostly yes — file-level edits are independent.

**Depends on:** P1.4 (canonical pedagogical_marker_check.py exists with mechanism-α enforcement, so we can verify justifications as we add them).

### P4.1 — Replace shim/delete the 3 prior pedagogical_marker_check.py copies (F-2-4, F-2-5, F-2-6)

Three former-copy files become:
- **Option A (preferred per cc-design):** DELETE; update each caller (`triage_with_judge.py`, `audit_skill.py`, `audit_subagent.py`) to invoke the canonical via subprocess path resolution.
- **Option B (fallback):** Replace each with a 3-line shim that exec()s the canonical.

Decision deferred to execution-time inspection of the call sites; both are valid. Default to Option A.

### P4.2 — Same pattern for scan_memory_secrets.py duplicates (F-2-7, F-2-8, F-2-9)

Create canonical at `auditing-shared/scripts/scan_memory_secrets.py` (identical to either prior copy). Replace `auditing-context-files/scripts/scan_memory_secrets.py` + `auditing-subagents/scripts/scan_memory_secrets.py` per P4.1 pattern.

**Then amend `auditing-shared/SKILL.md` Contents listing** (per supersession address of I-CA-003 from cross-artifact audit round 1): add a new bullet `- scripts/scan_memory_secrets.py — canonical memory-secrets scan`. SKILL.md was authored at P1.3 with only `pedagogical_marker_check.py` listed; this amendment brings the documented Contents into alignment with the actual file system at P4.2 end-state.

### P4.3 — Retroactive marker upgrade in 9 KB SKILL.md files (F-6-1)

For each of the 9 files with existing `pedagogical_sections:` bare-list frontmatter:
- Convert bare list to structured-dict form
- Add a non-boilerplate justification per entry (writer reads the referenced file to author meaningful justification)

Verification: each file passes the new mechanism-α check (auditor re-run between batches confirms).

### P4.4 — Retroactive fence-marker upgrade (F-6-2)

For each of the 10+ KB reference files with existing `` ```audit-example `` fences:
- Add ` -- <justification>` to each fence opening line
- Per AC-FR-7-d, justifications must pass D-3 rules

### P4.5 — Convert v4.4.0 HTML-tag markers to canonical fence form (F-6-3)

In `KB-visual-design/references/anti-slop.md` + `type-color-space.md`:
- Replace `<pedagogical-example>...</pedagogical-example>` blocks with `` ```audit-example -- <justification> ``` `` fence form
- Per AC-FR-8-a (no grandfathering)

### P4.6 — Add new markers to 32 Cat A+B affected KB files (F-7-1, F-7-2, F-7-3, F-7-4)

Per PRD's categorization of the 32+ findings across `KB-cc-platform`, `KB-github-actions-platform`, `KB-codespaces-platform`, `KB-codespaces-design`, `KB-documentation-criteria`, `KB-cc-design`:

For each file with Cat A+B findings:
- Inspect findings; for each, decide:
  - Real rewrite preferred per AC-FR-1-d / AC-FR-2-b (e.g., broken-link to pedagogical example path → rewrite as backticked plain text)
  - Marker disposition otherwise — add `pedagogical_sections:` entry (frontmatter) OR `audit-example` fence wrap (block-level), with mechanism-α justification

Verification: each file passes mechanism-α check; final audit shows zero findings for Cat A+B types in these files.

## Phase 5 — Verification records (FR-6 Stream 1)

**Goal:** Per-(subagent, skill) verification records per AC-FR-6-b.

**Dependency-graph items:** F-8-1

**Depends on:** P2.3 (X9 wired) — once X9 emits actionable findings (named failed skill or zero), we know which pairs need explicit verification records.

### P5.1 — Enumerate (subagent, skill) pairs from current X9 findings

Read the baseline audit's 29 X9 findings; extract (subagent, preloaded-skill) pairs. Deduplicate to unique skills.

### P5.2 — For each unique preloaded skill, run auditing-skills

For each unique skill: `python3 .claude/skills/auditing-skills/scripts/audit_skill.py <skill-path>`. Capture verdict.

### P5.3 — Author one verification record per (subagent, skill) pair

At `working/feature/audit-findings-remediation-r1/x9-verification/<subagent-name>-<skill-name>.md`:
- skill name
- audit timestamp
- verdict
- any MAJOR/MINOR findings + manual disposition notes

If P5.2 surfaces a skill that FAILS its audit, surface per ADR-0029 — that's a real defect that should either be fixed (scope expansion to PRD amend) or noted as a follow-on Won't-Have for this feature.

## Phase 6 — Integration + final audit

**Goal:** Final audit re-run; verify all ACs satisfied; package deliverables.

**Depends on:** All prior phases complete.

### P6.1 — Final audit re-run

```bash
python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . \
  --report /tmp/final-audit.md --json > /tmp/final-audit.json
```

Targets:
- BLOCKER = 0
- MAJOR = 0 (modulo the named-exempt Bash MAJOR in `review-cross-artifact-auditor.md`)
- MINOR strictly < 29 (X9 reformulation reduces or replaces with higher-signal output)

### P6.2 — AC verification matrix

For each AC in PRD v1.2.0, verify pass condition. Document in `acceptance-verification-matrix.md` co-located with phase-validators output.

### P6.3 — Cross-Artifact Audit invocation

Stage 12 (Cross-Artifact Audit) reviews all artifacts for consistency. Per Synthesis surfacing items, MUST check:
- No "rewording-only" cosmetic fix for FR-5
- Post-FR-12 single canonical (no surviving independent implementations)
- Sample-check actual markers' justifications (not just count)

### P6.4 — Reconciliation cycle

If Cross-Artifact Audit finds issues, Stage 13 finalize-reconciler dispatches fixes; cycle until convergence (max 4 cycles per ADR-0021).

### P6.5 — Task decomposition

Stage 14 `finalize-task-decomposer` produces `tasks.json` for any granular work items that survive reconciliation.

### P6.6 — Deliverable packaging (added as a new stage in v4.5.0+)

`finalize-deliverable-packager` verifies the archive completeness; produces `packager-report.json`; optionally drafts `HANDOFF-v4.6.0.md` + `CONTINUE_PROMPT-v4.6.0.md` per OBS-2 + U-3 resolution.

## Cross-Phase Dependencies

```
Phase 0 (Setup)
    ↓
Phase 1 (Foundation) — serial: P1.1 → P1.3 → P1.4
    ↓
    ├─→ Phase 4 (Marker work) — depends on canonical pedagogical_marker_check
    ├─→ P3.2 (shared-document-reviewer extension) — depends on P1.1 (spec)
    └─→ Phase 5 (Verification records) — depends on P2.3 (X9 wired)

Phase 2 (Auditor improvements) ← independent of Phase 1; parallel
Phase 3 (Real-fix dispositions, except P3.2) ← independent of Phase 1; parallel

Phase 6 (Integration) — depends on ALL prior phases
```

Critical path: P0 → P1.1 → P1.4 → P4.6 (largest marker batch) → P6.

Parallel opportunities: Phase 2 + Phase 3 (excluding P3.2) can run alongside Phase 1.

## L1/L2/L3 Verification Discipline

Per the project's existing verification convention:

- **L1 (per-task verification):** each P phase concludes with a verification step (e.g., P1.4's behavior-equivalence test before phase ends).
- **L2 (per-phase verification):** Phase 1 has a gate (P1.4's verify step). Phase 4 ends with intermediate audit re-run to confirm marker upgrades + new markers don't introduce regressions.
- **L3 (cross-phase verification):** Phase 6 P6.1 (final audit) + P6.2 (AC verification matrix) + P6.3 (Cross-Artifact Audit).

## Acceptance Test Cross-Reference

Acceptance Tests (authored by `test-acceptance-author` in parallel with this Plan per ADR-0021) MUST cover every AC from PRD v1.2.0. This Plan's Phase 6 P6.2 is the verification surface; specific test invocations are in `acceptance-tests.md`.

Key tests with negative-fixture requirement:
- FR-4-b: negative test fixture (truly-vague description still fires SA-2)
- FR-5-d: negative test fixture (genuine "skip the permission policy" still fires BLOCKER)
- FR-7-c: negative test per audit module (marker without justification produces original-severity finding)

## Estimation Methodology

This is a single-author, single-session-or-multi-session feature. No team capacity multiplier. Estimated effort by phase:

| Phase | Effort estimate | Rationale |
|---|---|---|
| Phase 0 (Setup) | ~30 min | Baseline + fixture setup; mechanical |
| Phase 1 (Foundation) | ~3-4 hours | Spec authoring (P1.1) is the bulk; P1.4 canonical module is methodical |
| Phase 2 (Auditor improvements) | ~2-3 hours | Three independent edits; ~1 hour each |
| Phase 3 (Real-fix dispositions) | ~3-4 hours | 18 broken-link decisions + 3 agent Bash-scoping edits |
| Phase 4 (Markers) | ~6-10 hours | LARGEST PHASE — 32 new markers + 20 retroactive + 5 KB-visual-design conversions; thoughtful justifications take time |
| Phase 5 (Verification records) | ~1-2 hours | Per-skill audit runs are fast; record authoring is mechanical |
| Phase 6 (Integration) | ~2-3 hours | Final audit + AC matrix + Cross-Artifact Audit + reconciliation + packaging |
| **Total** | **~18-27 hours** | Single-author; multi-session likely |

Wall-clock vs effort: with reconciliation cycles potentially running, full feature completion likely spans 3-5 work sessions.

## Resourcing Posture

- **Author:** single (Claude in continuation session OR formalized execution pipeline once that ships).
- **Reviewer (gates):** single (the user).
- **No external dependencies** — all work is in `.claude/`; no third-party services, no MCP servers needed for execution (Discovery used web_search; execution doesn't).

## Open Items (Pending Cross-Artifact Audit)

- **OI-1:** Phase 3 P3.3's per-finding dispositions (repair/delete/reauthor) for the 18 Cat C findings will be decided during execution; Cross-Artifact Audit must verify each is consistent with AC-FR-3-b (no marker dispositions).
- **OI-2:** Phase 4 P4.6's per-file marker-vs-rewrite decisions (per AC-FR-1-d / AC-FR-2-b preferring rewrite) will be decided during execution; Cross-Artifact Audit must verify the rewrite preference was honored where feasible.
- **OI-3:** Phase 5 P5.2 may surface a preloaded skill that FAILS its audit. If so, per ADR-0029 the deviation surfaces; PRD amendment OR follow-on deferral OR rejection.
- **OI-4:** Plan-stage didn't make a decision on whether FR-10 P2 (audit-presentation improvements) is included. Default: NOT included unless Cross-Artifact Audit identifies meaningful value. Defer to follow-on feature.
- **OI-5:** Plan-stage didn't make a decision on whether FR-11 P3 (Stage 13 retroactive run against v4.4.x archives) is included. Default: NOT included unless time permits during Phase 6.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-21T19:10:00Z | plan-author | Initial Plan |
| 1.1.0 | 2026-05-21T20:42:00Z | plan-author (re-invoked by finalize-reconciler, continuation session) | Supersedes v1.0.0 per ADR-0005 append-only discipline. Addresses cross-artifact audit round 1 findings: I-CA-001 (MAJOR — P6.6 stage-number discipline violation; heading rewritten without stage numbers), I-CA-002 (MAJOR — P1.4 intermediate-state audit capture missing; inserted as new step 4, with steps 5-7 renumbered, and Verification line rewritten to reference real-corpus equivalence + fixture-based new-behavior), I-CA-003 (MINOR — P1.3 SKILL.md temporal listing of scan_memory_secrets.py; removed initial listing, added amendment instruction to P4.2). See `reconciliation-log-cycle1.md` and `cross-artifact-audit-issues.json` for full audit trail. |
