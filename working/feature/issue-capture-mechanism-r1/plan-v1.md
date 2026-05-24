---
id: PLAN-issue-capture-mechanism-r1
version: 1.0.0
status: draft
feature_slug: issue-capture-mechanism-r1
derived_from: working/feature/issue-capture-mechanism-r1/blueprint-v3.md
phases: 8
total_tasks: 47
generated: 2026-05-23T23:59:00Z
generated_by: plan-author
---

# Plan: Issue-Capture Mechanism (Outside-the-Pipeline)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Purpose
- [x] Source
- [x] Phase 0 — Baseline + structural-only setup
- [x] Phase 1 — Templates + structural spec (CC)
- [x] Phase 2 — Backend validator extension + path-prefix skip
- [x] Phase 3 — Migration of 4 Issues files + agent-roster-impact-matrix
- [x] Phase 4 — CC layer: KB skills + agent + entry-point skill
- [x] Phase 5 — CC layer: hook script + settings.json patch
- [x] Phase 6 — Cross-cutting handoff edits
- [x] Phase 7 — Rollout / verification + acceptance
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This Plan is the executable decomposition of `blueprint-v3.md` (audit-passed at Gate 4, cycle 2) for the outside-pipeline issue-capture mechanism. It sequences the multi-primitive subsystem — `KB-issue-capture` + `capture-issue` skills, `issue-capture-author` sub-agent, PreToolUse hook, `settings.json` patch, three templates + one spec, validator extension with outer-dispatch path-prefix skip, and 5 file migrations — into 8 sequential delivery phases plus a final rollout/verification phase.

Per ADR-0017, every Plan phase has measurable pass criteria for the upcoming `test-phase-validator-author` to consume. Per ADR-0023 scope class FULL, every phase has explicit blocking-severity thresholds in its exit criteria. Per NFR-8, the load-bearing verification mechanism is the **Phase 0 baseline + Phase 2 regression diff** — the pre-extension findings JSON snapshot is captured BEFORE any validator change, and the post-extension diff against that baseline MUST be empty.

The Plan does NOT re-author ADRs (per FR-5). The 7 ADRs (ADR-0044..ADR-0050) authored by `design-composer` are referenced as-is. Implementation specifics not pinned by the Blueprint are surfaced as Open Items.

## Source

- **Blueprint**: `working/feature/issue-capture-mechanism-r1/blueprint-v3.md` (v1.2.0; Architecture Audit cycle 2 verdict PASS)
- **PRD**: `working/feature/issue-capture-mechanism-r1/prd-v2.md` (v1.1.0; 15 FRs, 9 NFRs, 11 Undetermined Items)
- **ADRs (7 inherited from this run)**: `working/feature/issue-capture-mechanism-r1/adrs/ADR-{0044,0045,0046,0047,0048,0049,0050}*.md`
- **ADRs (8 prerequisite)**: ADR-0005, ADR-0008, ADR-0011, ADR-0017, ADR-0020, ADR-0023, ADR-0032, ADR-0036
- **Codebase analysis**: `working/feature/issue-capture-mechanism-r1/codebase-analysis.json` (16 findings F-001..F-016; 7 CPs; 4 VEs)
- **Phase taxonomy used**: Phase 0 (setup + baseline capture) → Phases 1..6 (feature delivery in dependency order from Blueprint Implementation Plan) → Phase 7 (rollout / verification + acceptance). All phases inherit the EARS-format Acceptance Criteria from the Blueprint.

---

## Phase 0 — Baseline + structural-only setup

### Goal

Capture pre-change validator findings as the NFR-8 regression baseline, capture pre-change pipeline-isolation invariant zero-baseline (AC-FR-13-a/b), capture pre-change `cc-critique` snapshot, and stage the test-fixture directory — all with **no behavior change** to the validator or any pipeline artifact.

### Tasks

#### T0.1: Capture validator findings baseline against L1 + L2 corpus

- **Layer:** Backend
- **Description:** Run `validate_pipeline_frontmatter.py` against the existing-pipeline regression corpus (L1: existing smoke-test corpus; L2: real pipeline artifacts — minimum 27 files covering the 21-value enum + 6 suffix patterns per Backend §7). Persist the findings JSON as `working/feature/issue-capture-mechanism-r1/validator-baseline-l1-l2.json`. This is the NFR-8 load-bearing artifact-of-record (Q-BE-5: findings JSON only; not source files).
- **Dependencies:** none
- **Estimate:** S (45–90 min)
- **Satisfies AC:** N/A — setup (baseline prerequisite for AC-BE-6 / AC-NFR-8-a verification in Phase 2)
- **L1 verification:** `validator-baseline-l1-l2.json` exists at the expected path and parses as JSON.
- **L2 verification:** Findings count and the per-file finding shape match a manual spot-check of three representative files (an existing `prd-*.md`, `blueprint-*.md`, and `analysis-*.md`).
- **L3 verification:** The baseline file is referenced by the Phase 2 regression-diff task (T2.6); Phase 2 cannot proceed without it.

#### T0.2: Capture pipeline-isolation invariant zero-baseline (AC-FR-13-a/b)

- **Layer:** Claude Code
- **Description:** Run the two verbatim grep commands from AC-FR-13-a and AC-FR-13-b against `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md`. Persist the (expected-empty) output to `working/feature/issue-capture-mechanism-r1/pipeline-isolation-baseline.txt` as the F-010 / F-015 zero-baseline of record. (Already captured at 2026-05-23T18:55Z against HEAD cf48e5e in codebase-analysis.json; this task re-runs at Plan-stage HEAD to confirm no drift introduced by interim work.)
- **Dependencies:** none
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** N/A — setup (zero-baseline anchor for AC-FR-13-a/b verification in Phase 7)
- **L1 verification:** `pipeline-isolation-baseline.txt` exists and is empty (or contains only the literal "0 matches" line).
- **L2 verification:** Both grep commands return exit code 1 (no matches) on the current HEAD.
- **L3 verification:** Phase 7's AC-FR-13-a/b verification (T7.4) compares post-implementation grep output to this baseline; expected equal (both empty).

#### T0.3: Capture pre-change cc-critique health snapshot

- **Layer:** Claude Code
- **Description:** Run `cc-critique` against the current `.claude/` tree (no new components yet). Persist the verdict + findings to `working/feature/issue-capture-mechanism-r1/cc-critique-baseline.json`. This snapshot is the pre-change comparison anchor for Phase 7's "cc-critique on new components produces PASS or PASS-WITH-MINOR-FIXES" success metric.
- **Dependencies:** none
- **Estimate:** S (15–30 min)
- **Satisfies AC:** N/A — setup
- **L1 verification:** `cc-critique-baseline.json` exists and parses.
- **L2 verification:** Baseline verdict captured (PASS / PASS-WITH-MINOR-FIXES / NEEDS-REVISION) with finding count.
- **L3 verification:** Phase 7 task T7.7 compares post-change cc-critique output to this baseline; new findings must be limited to MINOR-or-better on the new components.

#### T0.4: Stage test-fixture directory skeleton

- **Layer:** Backend
- **Description:** Create `.claude/skills/auditing-shared/scripts/test_fixtures/issue_doc_types/` directory (empty for now; populated in Phase 2). Add a `.gitkeep` to keep the directory tracked. No fixtures yet; just the path.
- **Dependencies:** none
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** N/A — setup (directory is populated in Phase 2 by T2.4)
- **L1 verification:** Directory `.claude/skills/auditing-shared/scripts/test_fixtures/issue_doc_types/` exists; `.gitkeep` present.
- **L2 verification:** `git status` shows the directory + `.gitkeep` staged.
- **L3 verification:** Phase 2 T2.4 successfully places fixtures under this path.

#### T0.5: Verify dev-environment dependencies (shellcheck, jq) for Phase 5

- **Layer:** Claude Code / Dev Environment
- **Description:** Confirm `shellcheck` and `jq` are present in the standard devcontainer (used by hook in Phase 5 and by hook script in production). Document versions in `working/feature/issue-capture-mechanism-r1/devenv-prereqs.txt`. No installation needed if already present; if missing, surface as Open Item to user (not a phase blocker — bash hook can be written without these tools, but D-07 layer A + D-02 require both).
- **Dependencies:** none
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** N/A — setup (Phase 5 D-07 layer A toolchain prerequisite)
- **L1 verification:** `which shellcheck` returns a path; `which jq` returns a path.
- **L2 verification:** Both tools execute --version successfully.
- **L3 verification:** Phase 5 T5.2 (shellcheck on hook script) succeeds; Phase 5 T5.4 (golden-file dry-run on hook script) succeeds (hook uses jq).

### Phase 0 Exit Criteria

- All Phase 0 task L3 verifications pass.
- `validator-baseline-l1-l2.json` exists and is the documented baseline-of-record for NFR-8 verification (load-bearing).
- `pipeline-isolation-baseline.txt` exists and is empty (AC-FR-13 zero-baseline preserved at Plan-stage HEAD).
- `cc-critique-baseline.json` captured.
- No file under `.claude/` has been edited; no Python under `.claude/skills/auditing-shared/scripts/` modified beyond the test-fixtures directory creation.
- **Blocking severity threshold (per ADR-0023 FULL):** any Phase 0 task failing L3 is a `blocker`; Phase 1 must not start.

Phase Validator (authored downstream by `test-phase-validator-author`): asserts the three baseline JSON / TXT files exist with the right shape; asserts no edits to validator code; asserts test-fixtures directory empty (only `.gitkeep`).

---

## Phase 1 — Templates + structural spec (CC)

### Goal

Author the three new doctype templates and one structural spec under `KB-documentation-criteria/references/`, and additively update `KB-documentation-criteria/SKILL.md`. These structural surfaces are read at runtime by `issue-capture-author` (Phase 4) and define the enum / state vocabulary consumed by the validator extension (Phase 2). Triggering discipline does NOT live here (per ADR-0049 — that lives in `KB-issue-capture` in Phase 4).

### Tasks

#### T1.1: Author `issue-register-template.md`

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md`. Structural-only (per ADR-0049): frontmatter shape (carrying `id`, `doc_type: issue-register`, `feature_slug`, `version`, `status`, `since`, per-state companion fields per ADR-0050), section headers, and body-shape guidance derived from the empirical precedent (`Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`). No triggering discipline. Per Q-BE-1: `doc_type` is the literal `issue-register`. No-frontmatter examples for the four terminal states.
- **Dependencies:** none
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-FR-6-a (template structure used by `shared-document-reviewer` Gate 0), AC-FR-6-b (no triggering discipline)
- **L1 verification:** File exists at the expected path; frontmatter parses; renders as well-formed markdown.
- **L2 verification:** Manual review confirms structural-only content (no "when to capture" guidance); template matches the four ADR-0050 frontmatter shapes per state.
- **L3 verification:** Phase 4 T4.4 (`issue-capture-author` body) successfully reads this template at runtime to draft a register file; Phase 7 acceptance test for AC-FR-6-a passes.

#### T1.2: Author `issue-analysis-template.md`

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md`. Same discipline as T1.1 but for analysis doctype. Empirical precedent: `Issues/analysis-per-agent-design-evaluation-gap.md` + `Issues/analysis-adr-placement-rootcause.md`. Body shape includes "Root cause", "Evidence", "Implications" sections. Per Q-BE-1: `doc_type` is the literal `issue-analysis`.
- **Dependencies:** none
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b
- **L1 verification:** File exists; frontmatter parses; renders as markdown.
- **L2 verification:** Manual review confirms structural-only content; two empirical precedents covered.
- **L3 verification:** Phase 4 T4.4 successfully reads this template; Phase 7 AC-FR-6-a passes.

#### T1.3: Author `issue-proposal-template.md`

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md`. Same discipline. Empirical precedent: `Issues/proposal-auditing-family-graduation-review.md` + `Issues/issue-capture-mechanism/proposal.md`. Frontmatter includes the `proposes_future_feature:` field per D-06 (advisory; any string accepted). Body shape includes "Proposed feature", "Motivation", "Open questions". Per Q-BE-1: `doc_type` is the literal `issue-proposal`.
- **Dependencies:** none
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b
- **L1 verification:** File exists; frontmatter parses; renders as markdown.
- **L2 verification:** Manual review confirms structural-only content; `proposes_future_feature:` field present as advisory; two empirical precedents covered.
- **L3 verification:** Phase 4 T4.4 successfully reads this template; Phase 7 AC-FR-6-a passes.

#### T1.4: Author `issue-doctypes-spec.md` (structural spec)

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md` — the canonical structural spec codifying (a) the three doc_types from ADR-0045; (b) the 5-state vocabulary from ADR-0050; (c) the per-state required-companion-field table verbatim from Blueprint §Backend Per-State Companion Field Authoritative Table (D-05); (d) the bidirectional cross-link fields per ADR-0046; (e) the `superseded_by_issue_id` field per Q-BE-3. This spec is the single source-of-truth that the validator extension (Phase 2) and the agent body (Phase 4) both consume; it does NOT contain triggering discipline.
- **Dependencies:** none
- **Estimate:** L (2–3 h)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b (no triggering discipline), AC-FR-14-a (referenced from SKILL.md index)
- **L1 verification:** File exists; frontmatter parses; renders as markdown; per-state companion-field table is structurally valid.
- **L2 verification:** Per-state companion-field table byte-matches the Blueprint's authoritative table (D-05) and the ADR-0050 §Decision Details.
- **L3 verification:** Phase 2 T2.1 (constants) populates `ISSUE_PER_STATE_REQUIRED_FIELDS` from this spec without divergence; Phase 4 T4.4 successfully reads this spec.

#### T1.5: Additively update `KB-documentation-criteria/SKILL.md` index

- **Layer:** Claude Code
- **Description:** Edit `.claude/skills/KB-documentation-criteria/SKILL.md` to add 3 rows under "Canonical templates" (for `issue-register-template.md`, `issue-analysis-template.md`, `issue-proposal-template.md`), 1 row referencing `issue-doctypes-spec.md` under "What's in this KB" (or equivalent index section), and 1 bullet under "Where this KB is NOT used" stating the triggering discipline for issue capture lives in `KB-issue-capture`. NO removals; NO restructure (FR-14 strict).
- **Dependencies:** T1.1, T1.2, T1.3, T1.4 (all 4 referenced paths must exist before the index row is added)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-14-a
- **L1 verification:** Diff against prior version shows only additive rows + 1 additive bullet; no removals; YAML frontmatter parses.
- **L2 verification:** Manual review confirms 4 new index entries match the 4 new files' paths; "Where this KB is NOT used" bullet present.
- **L3 verification:** Phase 7 AC-FR-14-a acceptance test passes (reader can find all 4 new templates/specs via the index).

### Phase 1 Exit Criteria

- All 4 new files exist at canonical paths under `KB-documentation-criteria/references/{templates,/}`.
- `KB-documentation-criteria/SKILL.md` lists all 4 new files in its index; the diff is purely additive.
- All 4 new files contain structural-only content (no triggering discipline) — confirmed by reviewer at Gate 0 of Phase 1's output.
- **Blocking severity threshold (per ADR-0023 FULL):** any `blocker` finding from `shared-document-reviewer` on a new template; any `important` finding on the spec → Phase 1 not done.

Phase Validator: asserts all 4 files exist; asserts SKILL.md diff is additive-only; runs Gate 0 against each new template and the spec.

---

## Phase 2 — Backend validator extension + path-prefix skip

### Goal

Extend `validate_pipeline_frontmatter.py` with (a) the four module-level constants, (b) the outer-dispatch path-prefix early-return for `Issues/<topic>/(evidence|updates)/**` (per I-AA-002 / ADR-0044 §Decision §4), (c) the extension of `doc_type_category` to return `"issue"`, (d) the `elif category == "issue"` branch dispatching to a new `validate_issue_artifact` function, and (e) the new function itself. Verify NFR-8 via empty regression diff against the Phase 0 baseline. Extend `smoke_test_auditing_shared.py` with L3 + L4 fixtures.

### Tasks

#### T2.1: Add module-level constants (early-verification target)

- **Layer:** Backend
- **Description:** Add to `validate_pipeline_frontmatter.py` (near other module-level constants at lines 38-68): `ISSUE_DOC_TYPES = {"issue-register", "issue-analysis", "issue-proposal"}`; `ISSUE_STATES = {"draft", "open", "adopted", "complete", "superseded", "wontfix-with-rationale"}`; `ISSUE_PER_STATE_REQUIRED_FIELDS = {...}` per Blueprint §Backend Per-State Companion Field Authoritative Table; `ISSUE_NON_VALIDATED_PATH_PREFIXES = ("Issues/*/evidence/", "Issues/*/updates/")` per I-AA-002. ALSO extend `doc_type_category` (lines 147-154) to return `"issue"` when `doc_type ∈ ISSUE_DOC_TYPES`. DO NOT add the `elif category == "issue"` branch yet (T2.2); DO NOT add `validate_issue_artifact` yet (T2.3); DO NOT add path-prefix early-return inside `validate_pipeline_artifact` yet (also T2.2). This isolates the constants-and-categorization-only change as the early-verification target per Blueprint §Verification Strategy.
- **Dependencies:** T1.4 (spec defines the per-state companion fields verbatim)
- **Estimate:** S (45–60 min)
- **Satisfies AC:** N/A — setup-equivalent for the early-verification target (the bind-and-isolate constants-only commit). Subsequent tasks T2.2/T2.3 satisfy AC-BE-1..AC-BE-9, AC-BE-10, AC-FR-7-a..d.
- **L1 verification:** Python file imports without error; constants are dict/set/tuple as expected; `doc_type_category("issue-register")` returns `"issue"`.
- **L2 verification:** `smoke_test_auditing_shared.py` existing tests all pass unchanged.
- **L3 verification:** Re-running the validator against the Phase 0 L1+L2 corpus yields findings byte-identical to `validator-baseline-l1-l2.json` (early-verification target per Blueprint §Verification Strategy). Empty diff. If any existing doc_type is reclassified, this task is defective and must be reassessed before T2.2 begins.

#### T2.2: Add outer-dispatch path-prefix early-return + `elif category == "issue"` branch

- **Layer:** Backend
- **Description:** Inside `validate_pipeline_artifact`, add (a) the 3-5 line path-prefix early-return guard BEFORE the existing `doc_type_category` dispatch at lines 365-371: if path matches any prefix in `ISSUE_NON_VALIDATED_PATH_PREFIXES`, return `[]` immediately (per I-AA-002 / ADR-0044 §4); (b) the new `elif category == "issue": return validate_issue_artifact(fm, path)` branch in the dispatch. The new function is a stub that returns `[]` for now (T2.3 fills it). Existing GATED/ANALYSIS/ADR branches unchanged (AC-BE-8). The unknown-category else branch unchanged.
- **Dependencies:** T2.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-BE-7 (existing categories route through pre-existing validators unchanged), AC-BE-8 (outer dispatch logic unchanged except for the new early-return; existing per-category dispatch preserved), AC-BE-10 partial (path-prefix skip behavior; full verification requires T2.5 fixture)
- **L1 verification:** Python imports; `validate_pipeline_artifact(fm, Path("Issues/foo/evidence/bar.md"))` returns `[]` regardless of fm contents.
- **L2 verification:** Unit-test: passing a synthetic fm with `doc_type: issue-register` + a path under `Issues/topic-x/` dispatches to the (stub) `validate_issue_artifact` and returns `[]`; passing the same fm with a path under `Issues/topic-x/evidence/` returns `[]` via the early-return; passing fm with `doc_type: blueprint` continues to dispatch to `validate_gated_artifact`.
- **L3 verification:** Re-run validator against Phase 0 L1+L2 corpus; diff against `validator-baseline-l1-l2.json` MUST be empty (NFR-8 + AC-NFR-8-a; the path-prefix early-return MUST NOT alter findings on any non-Issues path).

#### T2.3: Implement `validate_issue_artifact` function

- **Layer:** Backend
- **Description:** Implement `validate_issue_artifact(fm: dict, path: Path) -> list[dict]` per Blueprint §Corrected Pseudocode Reference. Uses `make_finding` (VE-002) verbatim — no parallel construction. Uses the actual codebase idiom `field in fm` (resolves I-DR-BE-001). Checks: (a) `status not in ISSUE_STATES` → blocker (short-circuit); (b) each missing field in `ISSUE_PER_STATE_REQUIRED_FIELDS[status]` → blocker; (c) `doc_type == "issue-proposal" and "proposes_future_feature" not in fm` → info (D-06 advisory); (d) `escalates_from / escalated_to / rolled_into_register` syntactic-shape via `is_valid_id_syntax` (introduce helper if not present) when present → minor when malformed.
- **Dependencies:** T2.2
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-BE-1 (clean validation), AC-BE-2 (invalid status → blocker), AC-BE-3 (missing companion field → blocker), AC-BE-4 (issue-proposal advisory info), AC-BE-5 (malformed cross-link → minor), AC-BE-9 (uses make_finding verbatim), AC-FR-7-a, AC-FR-7-c, AC-FR-7-d
- **L1 verification:** Python imports; function callable with synthetic fm; returns list of dicts.
- **L2 verification:** Unit-test (added in T2.4): for each of the 5 substantive states + `draft`, pass a valid fm + a fm missing each required field; observe expected findings count + severity.
- **L3 verification:** Smoke-test extension (T2.5) passes all 18 (doc_type × state) positive cases + 6 missing-field negative cases + 3 invalid-status negative cases. Plus AC-BE-10 fixture (T2.5) passes.

#### T2.4: Author L3 test fixtures (positive + negative)

- **Layer:** Backend
- **Description:** Populate `.claude/skills/auditing-shared/scripts/test_fixtures/issue_doc_types/` with: (a) 18 positive fixtures (3 doc_types × 6 states — each a minimal valid Issue/*.md frontmatter with required companion fields); (b) 6 missing-companion-field negative fixtures (one per state-with-required-field; missing one required field); (c) 3 invalid-status negative fixtures (one per doc_type with `status: invalid-state`); (d) 1 advisory fixture (issue-proposal missing `proposes_future_feature` → info finding). Each fixture is a minimal markdown file with frontmatter and a one-line body.
- **Dependencies:** T1.4 (spec defines the per-state required fields), T2.3 (function shape known)
- **Estimate:** L (2–3 h)
- **Satisfies AC:** N/A — setup-equivalent for testing the FR-7 ACs. Used by T2.5.
- **L1 verification:** All 28 fixture files exist; each parses as a frontmatter-bearing markdown file.
- **L2 verification:** Each fixture's frontmatter is syntactically well-formed; positive fixtures pass `parse_frontmatter` without error; negative fixtures cover the expected branches.
- **L3 verification:** T2.5 smoke-test extension passes all fixtures with expected findings.

#### T2.5: Extend `smoke_test_auditing_shared.py` with new test cases + AC-BE-10 L4 fixture

- **Layer:** Backend
- **Description:** Add to `smoke_test_auditing_shared.py`: (a) a per-fixture test that runs the validator over each fixture from T2.4 and asserts the expected findings (count + severity); (b) the AC-BE-10 L4 fixture — a copy of the to-be-migrated `agent-roster-impact-matrix.md` (or a structurally-equivalent stub) placed under `Issues/per-agent-design-evaluation-gap/evidence/` in the test-fixtures area, asserting `validate_pipeline_artifact` returns `[]` regardless of frontmatter; (c) a positive control — a non-Issues file with `doc_type: not-a-known-type` MUST continue to produce a `minor` finding (verifies the path-prefix skip doesn't over-silence per Blueprint §Verification Strategy).
- **Dependencies:** T2.3, T2.4
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-BE-1 through AC-BE-10, AC-FR-7-a/c/d
- **L1 verification:** Python imports; new test functions callable.
- **L2 verification:** All new test cases pass when run via `python3 smoke_test_auditing_shared.py`.
- **L3 verification:** All 28 fixture cases pass; AC-BE-10 fixture returns `[]`; positive control returns the expected `minor` finding; the test suite is part of the test-set that the Phase 7 acceptance phase exercises.

#### T2.6: Final NFR-8 regression diff (load-bearing)

- **Layer:** Backend
- **Description:** Re-run the validator against the same L1+L2 corpus used to produce `validator-baseline-l1-l2.json` in T0.1. Diff field-by-field, ordered by `file_path` then `severity`. Any new finding line is a regression. Persist the diff result to `working/feature/issue-capture-mechanism-r1/validator-postextension-l1-l2-diff.json`.
- **Dependencies:** T2.1, T2.2, T2.3 (full extension landed)
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-BE-6 (post-extension byte-identical to baseline on existing corpus), AC-NFR-8-a (zero new findings on pre-existing doc_types), AC-FR-7-b
- **L1 verification:** `validator-postextension-l1-l2-diff.json` exists.
- **L2 verification:** Diff file's content shows empty diff array.
- **L3 verification:** **Blocker if any new finding line is present.** Forces re-investigation of T2.1/T2.2/T2.3 before phase exits. Empty diff is the NFR-8 contract; this is the highest-blast-radius assertion of the whole feature.

### Phase 2 Exit Criteria

- All Phase 2 task L3 verifications pass.
- `validator-postextension-l1-l2-diff.json` shows empty diff (NFR-8 load-bearing).
- All 28 test fixtures (positive + negative) pass.
- AC-BE-10 L4 fixture (agent-roster-impact-matrix.md under `Issues/<topic>/evidence/`) returns `[]`.
- Positive control (non-Issues file with unknown doc_type) continues to produce a `minor` finding.
- Validator is now ready to consume the post-Phase-3 migrated files cleanly.
- **Blocking severity threshold (per ADR-0023 FULL):** ANY new line in the regression diff is a `blocker`. Any `blocker`-severity finding from `shared-document-reviewer` on the validator code is a `blocker`. Phase 3 must NOT start while T2.6 has any new findings.

Phase Validator: re-runs T2.6 regression diff; asserts empty. Re-runs T2.5 smoke test; asserts all fixtures pass. Asserts the constants list contains all 4 expected items.

---

## Phase 3 — Migration of 4 Issues files + agent-roster-impact-matrix

### Goal

Execute the one-time migration per FR-8 + FR-9 + ADR-0044's D-13. Five atomic commits (one per file), each consisting of `git mv` + frontmatter back-fill (back-fill skipped for the agent-roster-matrix per AC-BE-10 path-prefix skip). Verify `git log --follow` returns full history per AC-FR-8-b / AC-FR-9-b.

### Tasks

#### T3.1: Dry-run D-13 git-mv-with-similarity-index procedure on all 5 files

- **Layer:** Claude Code
- **Description:** For each of the 5 migration pairs (4 Issues files + 1 agent-roster-matrix), execute the D-13 dry-run in a scratch worktree (or via `git mv --dry-run`): `git mv <src> <dst>` → edit frontmatter (where applicable) → `git diff -M` to confirm similarity-index detection → `git log --follow <dst>` to confirm history preservation. Persist the dry-run outcome (PASS/FAIL per file) to `working/feature/issue-capture-mechanism-r1/migration-dryrun.json`. If any file fails similarity-index detection, switch to the two-commit-sequence fallback for that file (per D-13).
- **Dependencies:** Phase 2 complete (validator must accept the post-migration frontmatter shapes before migration commits land)
- **Estimate:** M (60–90 min)
- **Satisfies AC:** N/A — setup-equivalent for migration; load-bearing for AC-FR-8-b / AC-FR-9-b
- **L1 verification:** `migration-dryrun.json` exists and lists 5 file results.
- **L2 verification:** For each of the 5 files, dry-run output records (a) target path, (b) git-diff-M detected similarity ≥90%, (c) `git log --follow` would return the pre-migration history.
- **L3 verification:** All 5 dry-runs PASS (or fallback to two-commit recorded for any failure); blocks T3.2..T3.6 until each path is known-good.

#### T3.2: Migrate `register-devcontainer-mcp-provisioning-r1-deferrals.md` (atomic commit)

- **Layer:** Claude Code
- **Description:** Execute the migration per ADR-0044 D-13 (or two-commit fallback if T3.1 detected): `git mv Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` → back-fill frontmatter (`doc_type: issue-register` per Q-BE-1; `version: 0.1.0`; `status: open`; `since: 2026-05-23`) → `git commit` as one atomic commit. Commit message references FR-8 + ADR-0044.
- **Dependencies:** T3.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-8-a (target path correct), AC-FR-8-b (`git log --follow` returns history), AC-FR-8-c (validator zero findings post back-fill), AC-FR-8-d (no other files migrated)
- **L1 verification:** File exists at new path; old path does not exist; commit is single-atomic.
- **L2 verification:** `git log --follow Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` returns pre-migration commits including 5e7f4ac and 5bca8e0 if applicable.
- **L3 verification:** `validate_pipeline_frontmatter.py Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` returns zero findings (AC-FR-8-c).

#### T3.3: Migrate `analysis-per-agent-design-evaluation-gap.md` (atomic commit)

- **Layer:** Claude Code
- **Description:** Same discipline as T3.2: `git mv Issues/analysis-per-agent-design-evaluation-gap.md Issues/per-agent-design-evaluation-gap/analysis.md` → back-fill frontmatter (`doc_type: issue-analysis`; `version: 0.1.0`; `status: open`; `since: 2026-05-23`) → atomic commit.
- **Dependencies:** T3.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-8-a, AC-FR-8-b, AC-FR-8-c
- **L1 verification:** New path exists; old path absent; atomic commit.
- **L2 verification:** `git log --follow Issues/per-agent-design-evaluation-gap/analysis.md` returns full history.
- **L3 verification:** Validator returns zero findings on the migrated file.

#### T3.4: Migrate `analysis-adr-placement-rootcause.md` (atomic commit)

- **Layer:** Claude Code
- **Description:** Same discipline: `git mv Issues/analysis-adr-placement-rootcause.md Issues/adr-placement-rootcause/analysis.md` → back-fill frontmatter (`doc_type: issue-analysis`; `version: 0.1.0`; `status: open`; `since: 2026-05-23`) → atomic commit.
- **Dependencies:** T3.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-8-a, AC-FR-8-b, AC-FR-8-c
- **L1 verification:** New path exists; old path absent; atomic commit.
- **L2 verification:** `git log --follow Issues/adr-placement-rootcause/analysis.md` returns history.
- **L3 verification:** Validator returns zero findings on the migrated file.

#### T3.5: Migrate `proposal-auditing-family-graduation-review.md` (atomic commit)

- **Layer:** Claude Code
- **Description:** Same discipline: `git mv Issues/proposal-auditing-family-graduation-review.md Issues/auditing-family-graduation-review/proposal.md` → back-fill frontmatter (`doc_type: issue-proposal`; `version: 0.1.0`; `status: open`; `since: 2026-05-23`; preserve existing `proposes_future_feature:` field per F-006) → atomic commit.
- **Dependencies:** T3.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-8-a, AC-FR-8-b, AC-FR-8-c
- **L1 verification:** New path exists; old path absent; atomic commit.
- **L2 verification:** `git log --follow Issues/auditing-family-graduation-review/proposal.md` returns history.
- **L3 verification:** Validator returns zero findings on the migrated file.

#### T3.6: Migrate `agent-roster-impact-matrix.md` to evidence subdirectory (atomic commit)

- **Layer:** Claude Code
- **Description:** Per FR-9: `git mv working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` → no back-fill (validator skips this path per AC-BE-10 / I-AA-002 outer-dispatch path-prefix skip) → atomic commit. Commit message references FR-9 + ADR-0044 §Decision §4.
- **Dependencies:** T3.1, T3.3 (the per-agent-design-evaluation-gap topic folder must exist before evidence/ subdirectory can be populated — created by T3.3's `git mv`)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-9-a (target path correct; no copy at prior path), AC-FR-9-b (`git log --follow` returns history)
- **L1 verification:** New path exists; old path absent; atomic commit.
- **L2 verification:** `git log --follow Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` returns history including 5c6df71 if applicable.
- **L3 verification:** `validate_pipeline_frontmatter.py` returns `[]` on the migrated path (AC-BE-10 path-prefix skip verified end-to-end on a real migrated file, not a fixture).

#### T3.7: Confirm validator clean-run on all 4 migrated Issues files post-back-fill

- **Layer:** Backend
- **Description:** Run `validate_pipeline_frontmatter.py Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md Issues/per-agent-design-evaluation-gap/analysis.md Issues/adr-placement-rootcause/analysis.md Issues/auditing-family-graduation-review/proposal.md`. Expected: zero findings across all 4 files (AC-FR-8-c).
- **Dependencies:** T3.2, T3.3, T3.4, T3.5
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** AC-FR-8-c
- **L1 verification:** Validator command exits 0.
- **L2 verification:** Validator stdout shows no finding lines for the 4 files.
- **L3 verification:** Result archived to `working/feature/issue-capture-mechanism-r1/migration-validator-result.txt`; reviewed and confirmed empty.

### Phase 3 Exit Criteria

- All 5 file migrations have landed as atomic commits (or two-commit fallback documented).
- `git log --follow` returns full history for each of the 5 destination paths.
- Validator returns zero findings on the 4 migrated Issues files.
- Validator returns `[]` on the migrated agent-roster-matrix (path-prefix skip honored on a real file).
- No file under `Issues/` outside the migration scope has been altered (AC-FR-8-d).
- **Blocking severity threshold (per ADR-0023 FULL):** any file's `git log --follow` not returning pre-migration history → `blocker`; any unexpected validator finding on the 4 migrated files → `blocker`.

Phase Validator: enumerates 5 source paths (pre-migration); asserts each is absent; enumerates 5 destination paths; asserts each is present; runs `git log --follow` per destination; runs validator on the 4 migrated Issues files; runs validator on the migrated agent-roster-matrix and asserts `[]`.

---

## Phase 4 — CC layer: KB skills + agent + entry-point skill

### Goal

Author `KB-issue-capture/` (4 reference files + SKILL.md), `capture-issue/SKILL.md`, and `.claude/agents/issue-capture-author.md`. These are Layer 1 + Layer 2 of the three-layer enforcement (ADR-0047). The skills declare `disable-model-invocation: true` (project firsts per F-001 — first such declarations); the agent body OMITS `skills:` frontmatter (per F-003 BLOCKER mitigation) and reads its KB at runtime.

### Tasks

#### T4.1: Author `KB-issue-capture/SKILL.md` (router)

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-issue-capture/SKILL.md` — frontmatter declares `disable-model-invocation: true` (project first per F-001); `allowed-tools: Read, Glob, Grep`; body is the discipline router (~80–120 lines) per cc-design §Skill Patterns. References the 4 KB reference files (T4.2). Cites templates + spec from KB-documentation-criteria by path (NOT inlined per ADR-0049).
- **Dependencies:** none
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-FR-3-a (Layer 1 `disable-model-invocation: true` declaration)
- **L1 verification:** File exists; frontmatter parses; `disable-model-invocation: true` literally present.
- **L2 verification:** `auditing-skills` pre-merge check passes; manual review confirms structural-only routing (no inlined triggering rules — those go in the references).
- **L3 verification:** Phase 7 AC-FR-3-a acceptance test confirms main Claude cannot auto-load this skill by description-match.

#### T4.2: Author KB-issue-capture references (4 files)

- **Layer:** Claude Code
- **Description:** Create the 4 references under `.claude/skills/KB-issue-capture/references/`: (a) `non-pollution-contract.md` — the structural invariant + pipeline-isolation rationale (cross-references the §Background and Context > Project Precedents Established subsection in Blueprint v3); (b) `approval-prompt-rubric.md` — the 4 AskUserQuestion archetypes per D-03 (resolves U-2 prompt wording); (c) `triage-criteria.md` — doctype classification rubric (register vs analysis vs proposal); (d) `examples.md` — 3 worked examples paired to the post-migration files per D-04 (resolves U-3). Examples.md authored AFTER Phase 3 (cross-link from D-04 → D-13).
- **Dependencies:** T4.1 (SKILL.md references these), Phase 3 (examples.md cross-references post-migration paths)
- **Estimate:** L (3–4 h)
- **Satisfies AC:** N/A — setup-equivalent for triage discipline. Indirectly supports AC-FR-1-b (WHY/WHAT/WHERE rubric source).
- **L1 verification:** All 4 reference files exist; each parses as markdown.
- **L2 verification:** Manual review confirms (a) non-pollution-contract cites the 5 project precedents; (b) approval-prompt-rubric documents all 4 archetypes; (c) triage-criteria gives concrete classification examples; (d) examples.md paths point to the 4 migrated files from Phase 3.
- **L3 verification:** Phase 4 T4.4 successfully reads all 4 references at runtime; Phase 7 integration smoke test produces a clean WHY/WHAT/WHERE prompt.

#### T4.3: Author `capture-issue/SKILL.md` (entry-point)

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/capture-issue/SKILL.md` — frontmatter declares `disable-model-invocation: true` (project first per F-001); `allowed-tools: Task, AskUserQuestion`; `argument-hint: <hint> | --update <path>`; body is a thin slash-command surface (~30–50 lines) per cc-design §Skill Patterns. Body: argument parsing (create-mode hint XOR `--update <path>` mutual exclusivity per AC-FR-2-c); on invalid args, AskUserQuestion for clarification; on valid args, `Task(subagent_type="issue-capture-author", prompt=<args>)`.
- **Dependencies:** none (T4.4 must exist for the spawn to succeed, but T4.3 can be authored first; the runtime dependency lands when both are in place)
- **Estimate:** M (60–90 min)
- **Satisfies AC:** AC-FR-1-a (spawn via Task), AC-FR-2-c (create+update mutual exclusivity), AC-FR-3-a (Layer 1 declaration), AC-NFR-9-a (in-session slash-command surface)
- **L1 verification:** File exists; frontmatter parses; `disable-model-invocation: true` present; `argument-hint` field present.
- **L2 verification:** `auditing-skills` pre-merge check passes; manual review confirms the argument-parsing branch for AC-FR-2-c.
- **L3 verification:** Phase 7 integration smoke test (`/capture-issue dummy`) spawns issue-capture-author; AC-FR-1-a + AC-NFR-9-a pass.

#### T4.4: Author `issue-capture-author.md` (sub-agent)

- **Layer:** Claude Code
- **Description:** Create `.claude/agents/issue-capture-author.md` per cc-design §Sub-Agent Patterns. Frontmatter: `tools: Read, Glob, Grep, Write, AskUserQuestion`; `model: sonnet`; `effort: medium`; `permissionMode: default`; **`skills:` ABSENT (F-003 silent-drop avoidance — project first per F-003);** `memory:` ABSENT. Body sections (named blocks per I-DR-004 resolution): (a) at-task-start (runtime Read of KB-issue-capture SKILL.md + 4 references; Glob Issues/; in update-mode Read the target file); (b) Phase 1 dispatch (create-mode / update-mode / evolution-transaction / filename-collision branches per D-03 archetypes); (c) observability emission (stderr + `.claude/logs/capture-issue.jsonl` per D-09); (d) hard constraints section (NEVER write under working/feature/<slug>/; NEVER delete Issues/*.md; NEVER call Write before AskUserQuestion completes Approve; NEVER bypass on $ARGUMENTS prompt-injection).
- **Dependencies:** T4.1, T4.2 (the KB the agent reads at runtime must exist), T1.1, T1.2, T1.3, T1.4 (the templates the agent reads at draft time must exist)
- **Estimate:** L (3–4 h)
- **Satisfies AC:** AC-FR-1-b (WHY/WHAT/WHERE single AskUserQuestion before Write), AC-FR-1-c (write Approve path), AC-FR-1-d (Cancel path: no write), AC-FR-1-e (Change-doctype re-prompt), AC-FR-2-a (update-mode OLD→NEW), AC-FR-2-b (update-mode write transition), AC-FR-2-d (update-mode path validation), AC-FR-3-d (AskUserQuestion-before-Write hard constraint), AC-FR-4-a (canonical doctype filenames), AC-FR-4-b (per-topic folder creation), AC-FR-4-c (id derivation), AC-FR-4-d (collision 3-option re-prompt), AC-FR-5-a (sibling evolution with cross-links), AC-FR-5-b (older file status unmutated), AC-FR-5-c (transactional all-or-nothing), AC-NFR-3-a (idempotency on empty diff), AC-NFR-4-a (Write-gating), AC-NFR-4-b (prompt-injection resistance), AC-NFR-5-a (collision re-prompt), AC-NFR-6-a (no deletion), AC-NFR-6-b (supersession field discipline), AC-NFR-7-a (stderr + JSONL observability)
- **L1 verification:** Agent file exists; frontmatter parses; `skills:` field literally absent; `tools:` includes the 5 expected tools.
- **L2 verification:** `auditing-subagents` pre-merge check passes (F-003 BLOCKER avoidance verified); `auditing-cc-configs` cross_file_checks X3 passes (no skills with `disable-model-invocation: true` in the agent's preload — there is no preload at all).
- **L3 verification:** Phase 7 integration smoke test exercises create-mode happy path + cancel branch + AskUserQuestion-before-Write sequencing; ACs in scope pass.

#### T4.5: Add `.gitignore` entry for `.claude/logs/*.jsonl`

- **Layer:** Claude Code
- **Description:** Append `.claude/logs/*.jsonl` to `.gitignore` (per Q-CC-4 resolution; Blueprint Implementation Plan Phase 5 — this Plan places it under Phase 4 because it's a sub-task of the observability surface introduced by T4.4). Logs are session-local audit trail; gitignoring preserves signal-to-noise.
- **Dependencies:** none
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** N/A — setup (gitignore discipline for AC-NFR-7-a observability log destination)
- **L1 verification:** `.gitignore` contains the new line; line is appended (not replacing existing entries).
- **L2 verification:** `git status` does not list `.claude/logs/capture-issue.jsonl` after a synthetic write to that path.
- **L3 verification:** Phase 7 integration smoke test writes to `.claude/logs/capture-issue.jsonl` and `git status` shows no untracked-file entry for that path.

### Phase 4 Exit Criteria

- `KB-issue-capture/SKILL.md` + 4 reference files exist; both new skills declare `disable-model-invocation: true`.
- `capture-issue/SKILL.md` exists; argument parsing branches present for create-mode XOR update-mode (AC-FR-2-c).
- `issue-capture-author.md` exists; frontmatter has NO `skills:` field; hard-constraint section present in body.
- `.gitignore` includes `.claude/logs/*.jsonl`.
- `auditing-skills`, `auditing-subagents`, `auditing-cc-configs` pre-merge checks all pass (no `blocker` findings).
- **Blocking severity threshold (per ADR-0023 FULL):** ANY `auditing-subagents` blocker on F-003 silent-drop is `blocker`; any `disable-model-invocation: true` missing from either skill is `blocker`; any missing hard-constraint section in agent body is `blocker`.

Phase Validator: greps for `disable-model-invocation: true` in both new skill files; greps for absence of `skills:` field in issue-capture-author.md; runs auditing-skills, auditing-subagents, auditing-cc-configs and asserts zero blocker findings; asserts the 4 KB references exist.

---

## Phase 5 — CC layer: hook script + settings.json patch

### Goal

Author Layer 3 of the three-layer enforcement: the PreToolUse hook script + the additive `.claude/settings.json` patch. Verify via shellcheck (D-07 layer A), single-fixture golden-file dry-run (D-07 layer B, early-verification target per I-DR-BP-007), full 5-fixture golden-file suite, and the 1000-iteration p95 latency benchmark (D-11; ratifies or replaces AC-NFR-1-a's ~100ms target per U-11).

### Tasks

#### T5.1: Create `.claude/hooks/` directory + author `intercept-issue-capture-agent.sh`

- **Layer:** Claude Code
- **Description:** Create directory `.claude/hooks/` (project first per F-002 precedent). Author `intercept-issue-capture-agent.sh` per cc-design §Hook Patterns: bash + jq; `set -u` (no `-e`); reads stdin event JSON; extracts `.tool_input.subagent_type` via jq; if `issue-capture-author` → emit `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":<spawn-prompt-preview>}}`; else emit `permissionDecision: "allow"`; ALL paths exit 0 (fail-open per NFR-2); on error (missing jq, malformed stdin) write to stderr + emit `allow`. Header comment documents idempotency + concurrency posture per I-DR-010. Script length: ~40–60 lines.
- **Dependencies:** T0.5 (jq + shellcheck verified present)
- **Estimate:** M (90–120 min)
- **Satisfies AC:** AC-FR-3-b (ask emission on issue-capture-author), AC-FR-3-c (allow on other subagent_types), AC-NFR-1-a partial (fast-path; full verification in T5.5), AC-NFR-2-a (fail-open on error), AC-NFR-2-b (visible stderr line)
- **L1 verification:** File exists at expected path; is executable (`chmod +x`); first line is `#!/usr/bin/env bash`.
- **L2 verification:** `bash -n intercept-issue-capture-agent.sh` parses without error; manual review confirms `set -u` (no `-e`), all paths exit 0, jq path is `.tool_input.subagent_type`.
- **L3 verification:** Phase 5 T5.2 (shellcheck) + T5.3 (single-fixture) + T5.4 (5-fixture suite) + T5.5 (latency benchmark) all pass.

#### T5.2: Run shellcheck on hook script (early-verification target Step 1, per I-DR-BP-007)

- **Layer:** Claude Code
- **Description:** Run `shellcheck .claude/hooks/intercept-issue-capture-agent.sh`. Expected: zero warnings; portability-clean. If any warning surfaces, fix in-place before T5.3 begins. This is the CC-layer early-verification target step 1 per Blueprint §Verification Strategy.
- **Dependencies:** T5.1
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** N/A — setup-equivalent verification step (D-07 layer A)
- **L1 verification:** `shellcheck` exits 0.
- **L2 verification:** Output reports zero warnings.
- **L3 verification:** Recorded in `working/feature/issue-capture-mechanism-r1/hook-shellcheck.txt`; clean.

#### T5.3: Author single-fixture golden-file harness + run (early-verification target Step 2, per I-DR-BP-007)

- **Layer:** Claude Code
- **Description:** Author `.claude/hooks/test_intercept_issue_capture_agent.py` — a Python harness that pipes a canonical stdin JSON fixture into the hook script and asserts the stdout matches an expected JSON. The first fixture: `{"tool_input": {"subagent_type": "issue-capture-author"}, ...}` → expected `permissionDecision: "ask"`; exit 0. Run only this fixture initially (CC-layer early-verification target step 2 per Blueprint §Verification Strategy). If passes, proceed to T5.4. If fails, the defect is localized to the hook script's jq path or stdout shape.
- **Dependencies:** T5.2
- **Estimate:** S (45–60 min)
- **Satisfies AC:** AC-FR-3-b (verified at the canonical "ask" path)
- **L1 verification:** `test_intercept_issue_capture_agent.py` exists and is callable.
- **L2 verification:** Running the harness with the canonical fixture asserts stdout contains `permissionDecision: "ask"`.
- **L3 verification:** Exit 0; assertion passes.

#### T5.4: Extend harness to full 5-fixture golden-file suite (D-07 layer B)

- **Layer:** Claude Code
- **Description:** Extend `test_intercept_issue_capture_agent.py` with the remaining 4 canonical fixtures per Blueprint §Verification Strategy: (a) issue-capture-author spawn → ask (already in T5.3); (b) non-issue-capture-author spawn (e.g., `subagent_type: cc-critique`) → allow; (c) malformed JSON stdin → allow + stderr; (d) missing `tool_input` field → allow + stderr; (e) empty stdin → allow + stderr. All 5 fixtures pass.
- **Dependencies:** T5.3
- **Estimate:** M (60–90 min)
- **Satisfies AC:** AC-FR-3-b, AC-FR-3-c, AC-NFR-2-a, AC-NFR-2-b
- **L1 verification:** Harness file extended; 5 fixture cases enumerated.
- **L2 verification:** Each of 5 fixtures runs and asserts the expected outcome.
- **L3 verification:** All 5 pass; output recorded to `working/feature/issue-capture-mechanism-r1/hook-golden-results.json`.

#### T5.5: 1000-iteration p95 latency benchmark on hook script (D-11; resolves U-11)

- **Layer:** Claude Code / Dev Environment
- **Description:** Run the hook script 1000 times with the fast-path fixture (`subagent_type != "issue-capture-author"`) using `hyperfine --warmup 100 -n hook` or equivalent. Compute p50 / p95 / p99 in milliseconds. Persist results to `working/feature/issue-capture-mechanism-r1/hook-latency-results.json`. Apply D-11 algorithm: if p95 ≤ 100ms → ratify AC-NFR-1-a's ~100ms target (mark AC-NFR-1-c CLOSED); if 100ms < p95 ≤ 200ms → replace the target with the measured value + 20% safety margin in the test wording (test-acceptance-author absorbs the change); if p95 > 200ms → escalate to design iteration (likely re-author hook in faster language; e.g., python or compiled).
- **Dependencies:** T5.4 (hook script working end-to-end)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-NFR-1-a (latency target ratified or replaced), AC-NFR-1-c (deferral closed)
- **L1 verification:** `hook-latency-results.json` exists; contains p50, p95, p99 ms values.
- **L2 verification:** D-11 algorithm applied; outcome (ratify / replace / escalate) recorded with the threshold value the test-acceptance-author will assert against.
- **L3 verification:** AC-NFR-1-a's specific threshold is finalized and propagated to Phase 7 acceptance tests; AC-NFR-1-c is marked CLOSED.

#### T5.6: Patch `.claude/settings.json` additively with `hooks.PreToolUse` block

- **Layer:** Claude Code
- **Description:** Edit `.claude/settings.json`: add top-level `hooks` object containing a `PreToolUse` block matching `Task` and pointing to `${CLAUDE_PROJECT_DIR}/.claude/hooks/intercept-issue-capture-agent.sh`. The existing 13-line `permissions.allow` array (7 entries) is UNCHANGED — no new permission entry for the hook script (per cc-design §Permission Policy: hooks run via platform mechanism, not via Bash). No `permissions.deny` rules added (Q-CC-2 deferred).
- **Dependencies:** T5.1 (hook script must exist at the path referenced in settings.json)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-3-b (settings.json wires the hook into the platform), AC-FR-3-c (same)
- **L1 verification:** `settings.json` parses as valid JSON; `permissions.allow` array unchanged (verify diff shows only the additive `hooks` block).
- **L2 verification:** `auditing-settings` pre-merge check passes; no `blocker` findings.
- **L3 verification:** Phase 7 integration smoke test verifies hook actually fires on Task spawns post-merge.

#### T5.7: Append note to `.claude/SETTINGS-NOTES.md` (FR-15)

- **Layer:** Claude Code
- **Description:** Append a note to `.claude/SETTINGS-NOTES.md` documenting (a) the new hook policy (PreToolUse on Task, discriminator on subagent_type, fail-open per NFR-2); (b) the user authorization timestamp (sourced from Intent Clarification approval token `approved-2026-05-23T16:51:00Z`); (c) the 5 project firsts enumerated inline (per I-DR-BP-002 resolution): first `disable-model-invocation: true` skills; first `.claude/hooks/` directory; first `hooks` block in `settings.json`; first runtime KB-load sub-agent; first 5-state lifecycle vocabulary. Append-only — do NOT modify prior content.
- **Dependencies:** T5.6 (the settings.json patch is the artifact being documented)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-15-a (note describes hook policy + user authorization timestamp)
- **L1 verification:** File diff shows only appended content; previous content unchanged.
- **L2 verification:** Manual review confirms (a)–(c) above are all present in the appended note.
- **L3 verification:** Phase 7 AC-FR-15-a acceptance test passes (reader can find the appended note with the expected content).

### Phase 5 Exit Criteria

- `.claude/hooks/intercept-issue-capture-agent.sh` exists and is executable.
- shellcheck on the hook script exits 0 with zero warnings.
- All 5 golden-file fixtures pass.
- 1000-iteration p95 latency benchmark complete; AC-NFR-1-a threshold ratified or replaced; AC-NFR-1-c CLOSED.
- `.claude/settings.json` patched additively (new `hooks.PreToolUse[matcher=Task]` block; `permissions.allow` unchanged).
- `.claude/SETTINGS-NOTES.md` carries the appended note (FR-15).
- `auditing-hooks`, `auditing-settings` pre-merge checks pass.
- **Blocking severity threshold (per ADR-0023 FULL):** ANY shellcheck warning is `blocker`; any golden-file fixture failure is `blocker`; latency benchmark p95 > 200ms escalates to design iteration (re-author hook in faster language).

Phase Validator: re-runs shellcheck; re-runs the 5-fixture golden-file suite; asserts `.claude/settings.json`'s diff is purely additive; asserts `.claude/SETTINGS-NOTES.md` contains the FR-15 note; asserts the latency-results JSON shows p95 ≤ ratified threshold.

---

## Phase 6 — Cross-cutting handoff edits

### Goal

Apply the small handoff-supporting edits to existing CC artifacts: `intake-intent-clarifier.md` Phase 0 (FR-11), `intent-clarification-template.md` Source-section guidance (FR-12a), `recipe-feature-pipeline/SKILL.md` one-bullet (FR-12b). These are sequenced AFTER the load-bearing primitives are in place because they document the now-existing mechanism, not the other way around.

### Tasks

#### T6.1: Edit `intake-intent-clarifier.md` — add Phase 0 proposal-as-prior-context detection

- **Layer:** Claude Code
- **Description:** Edit `.claude/agents/intake-intent-clarifier.md` per ADR-0048 + D-14: add a "Phase 0 — Proposal-as-prior-context detection" sub-section (~15 lines) before the existing Phase 1. The sub-section instructs the agent to (a) check whether `--raw-request` is set; (b) if so, Read the file's frontmatter; (c) if frontmatter contains `doc_type: issue-proposal`, treat the body as authoritative prior context (per ADR-0048); (d) elicit only Stage-1 fields the proposal lacks (FR-11-b). The checklist itself lives in `intent-clarification-template.md` (T6.2) to prevent drift.
- **Dependencies:** Phase 5 (the agent edit documents a now-fully-deployed mechanism)
- **Estimate:** M (60–90 min)
- **Satisfies AC:** AC-FR-11-a (detection branch), AC-FR-11-b (elicit-only-missing)
- **L1 verification:** Diff shows only additive ~15-line Phase 0 block before Phase 1; no signature change.
- **L2 verification:** Manual review confirms the branch detects `doc_type: issue-proposal` and routes to authoritative-prior-context handling.
- **L3 verification:** Phase 7 AC-FR-11-a/b acceptance test passes (dry-run a synthetic `--raw-request <proposal-path>` invocation; clarifier respects the proposal body).

#### T6.2: Edit `intent-clarification-template.md` — add Source-section proposal-seed guidance

- **Layer:** Claude Code
- **Description:** Edit `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md` per FR-12a: append ~5 lines of guidance to the existing Source section explaining that when a proposal seeds the run, the Source section cites the proposal path verbatim (per ADR-0048). Include the proposal-checklist (what fields the clarifier expects).
- **Dependencies:** none
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-12-a (proposal-seed Source guidance inline in template)
- **L1 verification:** Diff shows only additive ~5 lines in the Source section; no removals.
- **L2 verification:** Manual review confirms the appended guidance.
- **L3 verification:** Phase 7 AC-FR-12-a acceptance test passes (reader of the template can find the proposal-seed guidance).

#### T6.3: Edit `recipe-feature-pipeline/SKILL.md` — add proposal-seed invocation bullet

- **Layer:** Claude Code
- **Description:** Edit `.claude/skills/recipe-feature-pipeline/SKILL.md` per FR-12b: append one bullet documenting the proposal-seed invocation pattern `recipe-feature-pipeline <slug> --raw-request Issues/<topic>/proposal.md`. NO new pipeline stage; NO new gate; NO bypass path (AC-FR-12-b strict).
- **Dependencies:** none
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** AC-FR-12-b (no new pipeline stage / gate / bypass added)
- **L1 verification:** Diff shows only one additive bullet (≤5 lines).
- **L2 verification:** Manual review confirms no new stage / gate / bypass introduced.
- **L3 verification:** Phase 7 AC-FR-12-b acceptance test passes (grep / diff confirms only additive content).

### Phase 6 Exit Criteria

- `intake-intent-clarifier.md` carries a new Phase 0 block (~15 lines) per FR-11.
- `intent-clarification-template.md` Source section appended (~5 lines) per FR-12a.
- `recipe-feature-pipeline/SKILL.md` appended (one bullet) per FR-12b.
- All 3 edits are purely additive — no removals, no structural changes.
- **Blocking severity threshold (per ADR-0023 FULL):** ANY non-additive change in T6.1/T6.2/T6.3 diffs is `blocker`. Any new pipeline stage or gate bypass in T6.3 is `blocker`.

Phase Validator: diffs each of the 3 edited files against the pre-Phase-6 state; asserts all changes are additive; asserts no new stage / gate / bypass language in `recipe-feature-pipeline/SKILL.md`.

---

## Phase 7 — Rollout / verification + acceptance

### Goal

Execute end-to-end verification: pipeline-isolation grep (AC-FR-13), validator regression diff (AC-NFR-8-a), integration smoke test (`/capture-issue dummy` happy path + cancel + negative), migration history (`git log --follow` on all 5), `cc-critique` health (vs. T0.3 baseline), and all the previously-unrun acceptance tests (test-acceptance-author owns `acceptance-tests.md` enumeration; this phase runs them).

### Tasks

#### T7.1: Integration smoke test — `/capture-issue` happy path (create-mode)

- **Layer:** Claude Code
- **Description:** Manually invoke `/capture-issue <test-hint>` in a Claude Code session. Verify: (a) hook fires and produces `ask` prompt with spawn-prompt preview; (b) on approve, agent classifies doctype + drafts file + presents WHY/WHAT/WHERE `AskUserQuestion`; (c) on approve, exactly one file written under `Issues/<topic-slug>/<doctype>.md`; (d) path reported to user; (e) stderr line + JSONL append observable. Capture session transcript to `working/feature/issue-capture-mechanism-r1/smoke-test-create-mode.txt`. (Clean up the test file post-test by `/capture-issue --update` to wontfix-with-rationale rather than delete — per NFR-6 AC-NFR-6-a no deletion.)
- **Dependencies:** Phases 1, 2, 3, 4, 5 all complete (full mechanism integrated)
- **Estimate:** M (60–90 min)
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c, AC-FR-3-b, AC-FR-3-d, AC-FR-4-a, AC-FR-4-b, AC-NFR-4-a, AC-NFR-7-a, AC-NFR-9-a (acceptance-tests.md will encode these formally; this is the integration smoke)
- **L1 verification:** Session transcript captured.
- **L2 verification:** Hook ask-prompt visible; agent AskUserQuestion visible; written file at expected `Issues/<topic>/<doctype>.md` path.
- **L3 verification:** All 10 ACs above pass per acceptance-tests.md enumeration.

#### T7.2: Negative integration smoke test — cancel branch + non-issue-capture spawn (fast-path)

- **Layer:** Claude Code
- **Description:** (a) Invoke `/capture-issue <test-hint>`; on the AskUserQuestion, select Cancel; verify NO file written (AC-FR-1-d). (b) Invoke a non-issue-capture-author agent (e.g., cc-critique) via Task; verify hook silently allows; verify no `ask` prompt surfaces (AC-FR-3-c).
- **Dependencies:** T7.1 (same session setup; or fresh session)
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-1-d (cancel: no file written), AC-FR-3-c (hook fast-path allow on non-issue-capture)
- **L1 verification:** Test transcript captured.
- **L2 verification:** Cancel branch produces no `Issues/*.md` file; non-issue-capture spawn produces no `ask` prompt.
- **L3 verification:** Both ACs above pass; integration smoke results recorded.

#### T7.3: Update-mode smoke test (AC-FR-2-a/b + AC-NFR-3-a idempotency)

- **Layer:** Claude Code
- **Description:** Invoke `/capture-issue --update <path>` against one of the 4 Phase-3 migrated files (use `Issues/auditing-family-graduation-review/proposal.md` to avoid disturbing the others). Verify: (a) OLD→NEW preview AskUserQuestion appears (AC-FR-2-a); (b) on approve, transition written in place; new `status:` reported (AC-FR-2-b); (c) re-invoke with the same target state — verify "no change" reported (AC-NFR-3-a idempotency). (Restore the file to its prior state at end of test for clean repo.)
- **Dependencies:** T7.1
- **Estimate:** S (30–45 min)
- **Satisfies AC:** AC-FR-2-a, AC-FR-2-b, AC-NFR-3-a
- **L1 verification:** Test transcript captured.
- **L2 verification:** OLD→NEW preview observed; transition applied; idempotent second invocation produces "no change".
- **L3 verification:** All 3 ACs above pass.

#### T7.4: Pipeline-isolation invariant grep (AC-FR-13-a/b)

- **Layer:** Claude Code
- **Description:** Re-run the verbatim grep commands from AC-FR-13-a and AC-FR-13-b against `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md`. Compare against the Phase 0 baseline `pipeline-isolation-baseline.txt`. Expected: still empty.
- **Dependencies:** Phases 4, 5, 6 complete (new components are the risk)
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** AC-FR-13-a, AC-FR-13-b
- **L1 verification:** Both greps return exit code 1 (no matches).
- **L2 verification:** Output is byte-identical to Phase 0 baseline (empty).
- **L3 verification:** Diff against baseline shows zero new lines; pipeline-isolation invariant preserved.

#### T7.5: Validator regression diff against existing pipeline corpus (NFR-8 + AC-NFR-8-a)

- **Layer:** Backend
- **Description:** Re-run T2.6's regression diff (re-run validator against the same L1+L2 corpus used to produce `validator-baseline-l1-l2.json` in T0.1; field-by-field diff). Expected: still empty post-Phase-3 migrations (migrated files are validated cleanly per AC-FR-8-c; the corpus does NOT contain the pre-migration paths because they no longer exist post-Phase-3). Persist re-confirmation to `working/feature/issue-capture-mechanism-r1/validator-final-l1-l2-diff.json`.
- **Dependencies:** Phase 3 complete (migrations changed paths under Issues/)
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** AC-BE-6, AC-NFR-8-a (verified end-to-end post-migration), AC-FR-7-b (regression baseline preserved)
- **L1 verification:** Diff JSON file exists.
- **L2 verification:** Diff is empty.
- **L3 verification:** Diff confirmed empty; no regression on existing pipeline doc_types.

#### T7.6: Migration history verification — `git log --follow` on all 5 destination paths

- **Layer:** Claude Code
- **Description:** Run `git log --follow` against each of the 5 Phase-3 destination paths. Each MUST return pre-migration history per AC-FR-8-b / AC-FR-9-b. Persist transcript to `working/feature/issue-capture-mechanism-r1/migration-history-confirmation.txt`.
- **Dependencies:** Phase 3 complete
- **Estimate:** XS (≤15 min)
- **Satisfies AC:** AC-FR-8-b (4 files), AC-FR-9-b (1 file)
- **L1 verification:** Transcript file captured.
- **L2 verification:** For each of 5 paths, `git log --follow` shows at least one pre-migration commit.
- **L3 verification:** All 5 paths confirmed with pre-migration history.

#### T7.7: Run `cc-critique` against new components (AC: Success Criteria #5)

- **Layer:** Claude Code
- **Description:** Run `cc-critique` against the new agent / skills / hook / settings.json patch. Compare against the Phase 0 baseline `cc-critique-baseline.json`. Expected: PASS or PASS-WITH-MINOR-FIXES (zero BLOCKER findings) per PRD §Success Criteria quantitative metric #5. Persist to `working/feature/issue-capture-mechanism-r1/cc-critique-final.json`.
- **Dependencies:** Phases 4, 5 complete
- **Estimate:** S (30–45 min)
- **Satisfies AC:** PRD §Success Criteria quantitative metric #5 (cc-critique PASS / PASS-WITH-MINOR-FIXES with zero BLOCKER); cross-references all CC-layer ACs
- **L1 verification:** cc-critique output captured to JSON.
- **L2 verification:** Verdict is PASS or PASS-WITH-MINOR-FIXES; finding-count breakdown documented.
- **L3 verification:** Zero BLOCKER findings on new components; any MINOR findings have remediation plan documented as Open Item if not resolved in-phase.

#### T7.8: Run full `auditing-{hooks, skills, subagents, settings, cc-configs}` pre-merge checks

- **Layer:** Claude Code
- **Description:** Run all 5 auditing-* checks against the staged feature work as the canonical pre-merge gate per Blueprint §Verification Strategy > Operational Verification. Persist combined output to `working/feature/issue-capture-mechanism-r1/auditing-final.json`. Expected: zero BLOCKER findings; ≤2 MINOR findings each (consistent with cc-critique baseline).
- **Dependencies:** Phases 4, 5, 6 complete
- **Estimate:** S (30–60 min)
- **Satisfies AC:** All CC-layer ACs (cross-cutting pre-merge gate); PRD §Success Criteria #5
- **L1 verification:** Combined audit output captured.
- **L2 verification:** Each of 5 audits records its verdict (PASS / PASS-WITH-MINOR-FIXES / NEEDS-REVISION).
- **L3 verification:** Zero BLOCKER across all 5 audits; finding-counts within expected envelope.

#### T7.9: Author and commit `.gitignore` final check + clean up test artifacts

- **Layer:** Claude Code
- **Description:** Verify (a) `.gitignore` contains `.claude/logs/*.jsonl` (per T4.5) and `.claude/logs/capture-issue.jsonl` is untracked; (b) integration-test artifacts (smoke-test transcripts, test fixture files outside `test_fixtures/` directory) cleaned up or moved to `working/feature/<slug>/` (which is itself ignored by deliverable packaging). Restore the test issue captured by T7.1 to its prior state or supersede (NOT delete; NFR-6 AC-NFR-6-a).
- **Dependencies:** T7.1, T7.2, T7.3 (integration tests done)
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-NFR-6-a (no Issues/ deletion confirmed end-to-end)
- **L1 verification:** `.gitignore` contains the line; `git status` shows clean working tree (apart from feature-branch additions).
- **L2 verification:** No untracked `.jsonl` files in `.claude/logs/`; no orphan test files.
- **L3 verification:** Repo state is clean for merge; no `Issues/*.md` file deleted as part of this run.

### Phase 7 Exit Criteria

- All integration smoke tests pass (create-mode happy path, cancel branch, non-issue-capture fast-path, update-mode + idempotency).
- Pipeline-isolation grep returns empty (AC-FR-13-a/b verified).
- Validator regression diff is empty (NFR-8 verified end-to-end).
- `git log --follow` returns pre-migration history for all 5 destination paths.
- `cc-critique` PASS / PASS-WITH-MINOR-FIXES with zero BLOCKER findings.
- `auditing-{hooks,skills,subagents,settings,cc-configs}` all PASS / PASS-WITH-MINOR-FIXES.
- Working tree clean for merge.
- **Blocking severity threshold (per ADR-0023 FULL):** ANY new line in T7.5 validator regression diff is `blocker`; ANY non-empty result from T7.4 pipeline-isolation grep is `blocker`; ANY `git log --follow` returning truncated history on a migrated path is `blocker`; ANY BLOCKER from cc-critique or any of the 5 audits is `blocker`.

Phase Validator: this is effectively the Plan-wide acceptance gate. Re-runs T7.4 (isolation grep), T7.5 (regression diff), T7.6 (history), T7.7 (cc-critique), T7.8 (auditing-*). All must pass with their threshold conditions met.

---

## Cross-Phase Dependencies

```
                                    Phase 0 (baselines + setup)
                                          │
              ┌───────────────────────────┼───────────────────────────────────┐
              │                           │                                   │
              ▼                           ▼                                   ▼
         T0.1 (validator           T0.2 (isolation                    T0.3..T0.5
         baseline)                 baseline)                          (cc-critique
              │                           │                           baseline; fixtures
              │                           │                           dir; devenv check)
              │                           │
              ▼                           ▼
        Phase 1 (templates + spec + KB-doc-criteria index)
        T1.1 ─┐
        T1.2 ─┤
        T1.3 ─┼─► T1.5 (index update — requires all 4 references to exist first)
        T1.4 ─┘
              │
              ▼
        Phase 2 (validator extension)
        T2.1 (constants + categorization — EARLY-VERIFICATION TARGET; diff must be empty)
              │
              ▼
        T2.2 (path-prefix early-return + elif issue branch)
              │
              ▼
        T2.3 (validate_issue_artifact body)
              │
              ▼
        T2.4 (28 test fixtures) ─► T2.5 (smoke-test extension) ─► T2.6 (regression diff — LOAD-BEARING)
              │
              ▼
        Phase 3 (migrations)
        T3.1 (dry-run all 5)
              │
              ├──► T3.2 ──┐
              ├──► T3.3 ──┤
              ├──► T3.4 ──┤  (T3.2..T3.5 parallelizable — independent files)
              ├──► T3.5 ──┤
              └──► (T3.6 depends on T3.3 because evidence/ subdir lives under T3.3's topic folder)
                     │
                     ▼
                   T3.7 (validator clean-run on 4 migrated Issues files)
              │
              ▼
        Phase 4 (KB skills + agent)                  Phase 5 (hook + settings)
        T4.1 ─► T4.2 ─► T4.4                          T5.1 ─► T5.2 (shellcheck — EARLY-VERIFICATION) ─►
        T4.3 (parallel to T4.1/4.2)                          T5.3 (single fixture — EARLY-VERIFICATION) ─►
        T4.5 (parallel; .gitignore)                          T5.4 (5-fixture suite) ─► T5.5 (latency benchmark)
                                                             T5.6 (settings.json patch) ─► T5.7 (SETTINGS-NOTES append)
              │                                       │
              └───────────────────┬───────────────────┘
                                  ▼
                          Phase 6 (handoff edits)
                          T6.1 ─┐
                          T6.2 ─┼─ (all 3 parallelizable; independent files)
                          T6.3 ─┘
                                  │
                                  ▼
                          Phase 7 (verification + acceptance)
                          T7.1 ─► T7.2 ─► T7.3 (integration smokes)
                          T7.4 (isolation grep) ─┐
                          T7.5 (validator diff) ─┤  (T7.4..T7.8 parallelizable)
                          T7.6 (git history) ────┤
                          T7.7 (cc-critique) ────┤
                          T7.8 (auditing-*) ─────┘
                                  │
                                  ▼
                                T7.9 (cleanup + merge-ready)
```

**Critical path:** T0.1 → T1.4 → T2.1 → T2.2 → T2.3 → T2.5 → T2.6 → T3.1 → T3.2 → T3.7 → T4.4 → T5.1 → T5.4 → T5.5 → T5.6 → T6.1 → T7.1 → T7.5. The validator extension chain (Phase 0 → Phase 2) is the highest-blast-radius critical path; the agent body (T4.4) is the second-tallest dependency consumer (it depends on T1.1..T1.4 and on T4.1/T4.2).

**Parallelization opportunities:**

- Within Phase 0: T0.1, T0.2, T0.3, T0.4, T0.5 are all independent — fully parallel.
- Within Phase 1: T1.1, T1.2, T1.3, T1.4 are independent (different files) — fully parallel.
- Within Phase 2: T2.4 (fixtures) can start as soon as T2.3 has its function signature known (L2 dependency on T2.3).
- Within Phase 3: T3.2, T3.3, T3.4, T3.5 are independent migrations — fully parallel after T3.1 (dry-run gate). T3.6 must wait for T3.3.
- Within Phase 4: T4.1+T4.2 parallel to T4.3 parallel to T4.5; T4.4 needs T4.1, T4.2, and Phase 1 outputs.
- Within Phase 5: T5.1 (script author) and T5.6 (settings.json) can be authored in parallel, but T5.6 depends on T5.1's path being final.
- Within Phase 6: T6.1, T6.2, T6.3 all independent — fully parallel.
- Within Phase 7: T7.4, T7.5, T7.6, T7.7, T7.8 all parallel (independent assertions over the integrated system).

---

## L1/L2/L3 Verification Discipline

Every task carries three verification criteria per `KB-documentation-criteria/references/disciplines/plan-authoring.md`:

- **L1 (cheapest):** Can be checked in seconds. Examples used in this Plan: file exists at expected path; YAML/JSON parses; Python imports; shellcheck exits 0; `git log --follow` returns ≥1 commit.
- **L2 (functional):** Can be checked in minutes. Examples: unit test green; single golden-file fixture passes; manual review of a section confirms structural-only content; argparse branches reachable.
- **L3 (integration):** Can be checked in tens of minutes. Examples: end-to-end `/capture-issue` smoke test passes; full 5-fixture golden-file suite passes; 28 validator fixtures all pass; regression diff is empty; cc-critique returns PASS or PASS-WITH-MINOR-FIXES.

A task is **complete** when all three pass for that task. The Phase Validator for the containing phase aggregates L3 verifications across the phase's tasks. The Phase 0 and Phase 2 L3 verifications are LOAD-BEARING per NFR-8.

---

## Acceptance Test Cross-Reference

Every Blueprint / PRD AC mapped to at least one task. Tasks tagged `N/A — setup` are Phase-0-only and contribute to the regression-baseline that downstream L3s depend on.

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-1-a (spawn via Task) | T4.3, T4.4, T7.1 |
| AC-FR-1-b (single AskUserQuestion WHY/WHAT/WHERE before Write) | T4.4, T7.1 |
| AC-FR-1-c (write Approve path) | T4.4, T7.1 |
| AC-FR-1-d (Cancel: no write) | T4.4, T7.2 |
| AC-FR-1-e (Change-doctype re-prompt) | T4.4 |
| AC-FR-2-a (update-mode OLD→NEW preview) | T4.4, T7.3 |
| AC-FR-2-b (update-mode write transition + new status reported) | T4.4, T7.3 |
| AC-FR-2-c (create+update mutual exclusivity) | T4.3 |
| AC-FR-2-d (update-mode path validation) | T4.4 |
| AC-FR-3-a (Layer 1 `disable-model-invocation: true`) | T4.1, T4.3 |
| AC-FR-3-b (Layer 3 hook ask emission on issue-capture-author) | T5.1, T5.4, T5.6, T7.1 |
| AC-FR-3-c (Layer 3 hook fast-path allow on others) | T5.1, T5.4, T7.2 |
| AC-FR-3-d (Layer 2 AskUserQuestion-before-Write) | T4.4, T7.1 |
| AC-FR-4-a (canonical doctype filenames) | T4.4, T7.1 |
| AC-FR-4-b (per-topic folder creation) | T4.4, T7.1 |
| AC-FR-4-c (id = <DOCTYPE>-<topic-slug>) | T4.4 |
| AC-FR-4-d (collision 3-option re-prompt) | T4.4 |
| AC-FR-5-a (sibling evolution with cross-links) | T4.4 |
| AC-FR-5-b (older file status unmutated) | T4.4 |
| AC-FR-5-c (transactional all-or-nothing) | T4.4 |
| AC-FR-6-a (template structure used at Gate 0) | T1.1, T1.2, T1.3 |
| AC-FR-6-b (no triggering discipline in templates) | T1.1, T1.2, T1.3, T1.4 |
| AC-FR-7-a (clean validation on valid issue file) | T2.3, T2.5 |
| AC-FR-7-b (regression baseline preserved) | T2.6, T7.5 |
| AC-FR-7-c (missing companion field → blocker) | T2.3, T2.5 |
| AC-FR-7-d (status outside vocabulary → finding) | T2.3, T2.5 |
| AC-FR-8-a (4 files at canonical target paths) | T3.2, T3.3, T3.4, T3.5 |
| AC-FR-8-b (git log --follow returns history for the 4 files) | T3.2, T3.3, T3.4, T3.5, T7.6 |
| AC-FR-8-c (validator clean on migrated files) | T3.7, T7.5 |
| AC-FR-8-d (no other files migrated) | T3.2..T3.6 (negative — Phase 3 PV enumerates) |
| AC-FR-9-a (agent-roster-matrix at evidence path; no copy at prior path) | T3.6 |
| AC-FR-9-b (git log --follow returns history) | T3.6, T7.6 |
| AC-FR-10-a (intent-clarification.md cites proposal path verbatim) | Dogfooded by this run; T6.1 verifies for future runs via AC-FR-11-a/b |
| AC-FR-11-a (intake-intent-clarifier detects issue-proposal doc_type) | T6.1 |
| AC-FR-11-b (elicit only missing fields) | T6.1 |
| AC-FR-12-a (proposal-seed Source guidance in template) | T6.2 |
| AC-FR-12-b (no new stage / gate / bypass) | T6.3 |
| AC-FR-13-a (grep KB-issue-capture: empty) | T0.2, T7.4 |
| AC-FR-13-b (grep subagent_type: issue-capture-author: empty) | T0.2, T7.4 |
| AC-FR-13-c (no automated cross-reference between Issues/ and ledger) | Structurally satisfied by design; no task adds such cross-reference |
| AC-FR-14-a (SKILL.md index updated additively) | T1.5 |
| AC-FR-15-a (SETTINGS-NOTES.md hook policy + user authorization) | T5.7 |
| AC-BE-1 (clean validation on valid file) | T2.3, T2.5 |
| AC-BE-2 (invalid status → exactly one blocker) | T2.3, T2.5 |
| AC-BE-3 (missing companion field → one blocker per missing) | T2.3, T2.5 |
| AC-BE-4 (issue-proposal missing proposes_future_feature → info) | T2.3, T2.5 |
| AC-BE-5 (malformed cross-link → minor per field) | T2.3, T2.5 |
| AC-BE-6 (post-extension byte-identical to baseline on existing corpus) | T2.6, T7.5 |
| AC-BE-7 (pre-existing categories unchanged) | T2.2, T2.6 |
| AC-BE-8 (outer dispatch logic unchanged except early-return) | T2.2 |
| AC-BE-9 (uses make_finding verbatim) | T2.3 |
| AC-BE-10 (path under Issues/<topic>/(evidence|updates)/ returns []) | T2.2, T2.5, T3.6, T7.5 |
| AC-NFR-1-a (hook fast-path ~100ms p95 ratified/replaced) | T5.5 |
| AC-NFR-1-b (no end-to-end pipeline regression) | T7.5, T7.8 |
| AC-NFR-1-c (deferral closed at design/plan stage) | T5.5 |
| AC-NFR-2-a (hook fail-open: emit allow on error + stderr) | T5.1, T5.4 |
| AC-NFR-2-b (stderr line visible) | T5.1, T5.4 |
| AC-NFR-3-a (update-mode idempotency on empty diff) | T4.4, T7.3 |
| AC-NFR-4-a (no Write before AskUserQuestion Approve) | T4.4, T7.1 |
| AC-NFR-4-b (prompt-injection resistance: agent body sequence governs) | T4.4 |
| AC-NFR-5-a (no silent overwrite; 3-option re-prompt) | T4.4 |
| AC-NFR-6-a (no Issues/*.md deletion) | T4.4 (hard constraint), T7.9 (test artifacts not deleted but superseded) |
| AC-NFR-6-b (supersession via superseded_by_issue_id field) | T4.4 |
| AC-NFR-7-a (stderr + JSONL observability) | T4.4, T4.5 (gitignore), T7.1 |
| AC-NFR-8-a (validator backward compatibility) | T2.6, T7.5 |
| AC-NFR-8-b (unit-test coverage for new doc_types + states) | T2.4, T2.5 |
| AC-NFR-9-a (`/capture-issue <hint>` from any session state) | T4.3, T7.1 |

**Orphan AC check:** All 50+ ACs above are mapped to at least one task. **Orphan task check:** Every task is mapped to at least one AC OR explicitly tagged `N/A — setup` (and lives in Phase 0; T0.1..T0.5, T2.1, T2.4, T3.1, T4.2, T4.5, T5.2, T5.3 are the setup-tagged tasks). No tasks outside Phase 0 are setup-tagged except for `auditing-*` precursor checks that are themselves setup for downstream phase exits (T2.1 enables T2.6; T5.2/T5.3 enable T5.4; T2.4 + T4.2 are fixtures/references that enable runtime behavior). The cross-artifact auditor should verify these classifications.

---

## Estimation Methodology

T-shirt sizes (XS / S / M / L) per `plan-authoring.md` §Estimation Discipline. Ranges in parentheses are aggregate per-task wall-clock estimates assuming a single implementer with full project context:

- **XS:** ≤15 min (file creation, simple verification commands, single-line edits)
- **S:** 15–60 min (small file authoring; small code change; argparse-equivalent edits)
- **M:** 60–120 min (template authoring; mid-size code modules; integration smokes)
- **L:** 2–4 h (KB-issue-capture references; sub-agent body; validator function with full fixture set)

The total Plan envelope (sum of high-end estimates):

| Phase | Total tasks | High-end aggregate |
|---|---|---|
| Phase 0 | 5 | ~3 h |
| Phase 1 | 5 | ~9 h |
| Phase 2 | 6 | ~7 h |
| Phase 3 | 7 | ~5 h |
| Phase 4 | 5 | ~10 h |
| Phase 5 | 7 | ~7 h |
| Phase 6 | 3 | ~3 h |
| Phase 7 | 9 | ~5 h |
| **Total** | **47** | **~49 h** |

Estimates are sizing-only (per plan-authoring.md anti-pattern: NOT for velocity tracking).

---

## Resourcing Posture

Single implementer (Josh-S-N2M, the sole user). Per Blueprint §Stakeholders, Josh is the primary user, sole invoker, primary author, and the implementer for r1. No team-distribution; no domain-handoff between contributors. Task descriptions assume full project context including familiarity with the Blueprint, the 7 ADRs, and the project's existing CC primitives.

---

## Open Items (Pending Cross-Artifact Audit)

The plan-author surfaces the following items that the Blueprint either deferred to plan-stage or that the Plan structurally cannot resolve from the Blueprint alone:

- **OI-PLAN-1 (resolves Blueprint U-1):** The hook stdin schema field name for `subagent_type` is documented in `KB-cc-platform/references/extensions.md` but should be verified live during T5.1 hook authoring against Claude Code's current platform behavior. If differently named, the hook's `jq` path changes; the rest of the architecture is unaffected (per I-DR-005 fallback note). **Owner:** T5.1 implementer. **Surface:** if mismatch detected, flag during Phase 5 and adjust.

- **OI-PLAN-2 (resolves Blueprint U-2):** The exact `AskUserQuestion` prompt wording for the 4 archetypes (WHY/WHAT/WHERE; OLD→NEW; collision 3-option; evolution 2-option) is authored as part of T4.2's `approval-prompt-rubric.md`. The structural shape is locked by the Blueprint; wording is polished at authorship time. **Owner:** T4.2 implementer.

- **OI-PLAN-3 (resolves Blueprint U-3):** The 3 worked examples for `KB-issue-capture/references/examples.md` are paired 1:1 with post-migration files per D-04. T4.2 authors examples.md; the cross-link from D-04 → D-13 means examples.md must be authored AFTER Phase 3 migrations land. **Owner:** T4.2 implementer; verifies Phase 3 complete before authoring.

- **OI-PLAN-4 (resolves Blueprint U-11):** The hook latency threshold per AC-NFR-1-a is ratified or replaced at T5.5. test-acceptance-author must read T5.5's outcome before encoding the AC-NFR-1-a test assertion. **Owner:** T5.5 implementer + test-acceptance-author downstream.

- **OI-PLAN-5 (Q-CC-4 ratification):** T4.5 places `.gitignore .claude/logs/*.jsonl` under Phase 4 rather than Phase 5 (the Blueprint Implementation Plan placed it in Phase 5). This is a phase-placement refinement; the work is unchanged. Cross-artifact auditor may verify the placement is consistent with the Phase 4 observability surface introduced by T4.4. **Owner:** plan-author (surfaced here); cross-artifact auditor verifies.

- **OI-PLAN-6 (test-acceptance-author handoff):** This Plan signals (via the AC Cross-Reference table) which tasks satisfy which ACs. `test-acceptance-author` reads the Blueprint's ACs directly (not the Plan) and authors `acceptance-tests.md`. Per `plan-authoring.md` §Cross-pass interactions, the Plan's L3 verifications SHOULD reference the acceptance tests where applicable — they currently reference the AC IDs symbolically. test-acceptance-author should produce `acceptance-tests.md` with one test per AC; the test names should be of the form `test_AC_FR_1_a`, `test_AC_BE_10`, etc., for easy cross-reference. **Owner:** test-acceptance-author downstream.

- **OI-PLAN-7 (test-phase-validator-author handoff):** This Plan's per-phase exit criteria are the contract for Phase Validators. test-phase-validator-author authors 8 Phase Validators (Phase 0, 1, 2, 3, 4, 5, 6, 7). Each Phase Validator MUST assert the exit criteria for its phase per ADR-0017. **Owner:** test-phase-validator-author downstream.

- **OI-PLAN-8 (no new ADR):** Per FR-5, plan-author authors NO new ADRs. If during implementation an architectural decision surfaces that the 7 existing ADRs don't cover, finalize-reconciler must be invoked to route back to design-composer for ADR authorship. plan-author CANNOT silently absorb such decisions.

- **OI-PLAN-9 (deliverable-packaging consideration per I-AA-001):** The 7 new ADRs remain at `working/feature/issue-capture-mechanism-r1/adrs/` per the user-accepted Option A. Deliverable-packager (Stage 13) follows current operational convention; this Plan does NOT include a task to relocate them to `/adrs/`. Future migration is the separate drift-remediation feature's responsibility.

---

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-23 | plan-author | Initial Plan v1. Decomposes Blueprint v3 (cycle-2 audit-passed) into 8 sequential phases (Phase 0 setup + baselines through Phase 7 verification + acceptance), 47 tasks total. AC Cross-Reference table maps all 50+ PRD/Blueprint ACs to ≥1 task with no orphans either direction. Per-phase exit criteria + blocking-severity thresholds per ADR-0023 FULL. Phase 0 validator baseline + Phase 2 regression diff is the load-bearing NFR-8 verification chain. No new ADRs per FR-5 (Open Item OI-PLAN-8). |
