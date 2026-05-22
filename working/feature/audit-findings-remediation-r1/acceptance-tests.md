---
id: ACCEPTANCE-TESTS-audit-findings-remediation-r1
version: 1.0.0
status: superseded
feature_slug: audit-findings-remediation-r1
derived_from:
  - working/feature/audit-findings-remediation-r1/prd-v1.md (v1.2.0)
  - working/feature/audit-findings-remediation-r1/blueprint-v1.md (v1.0.0)
  - working/feature/audit-findings-remediation-r1/plan-v1.md (v1.0.0)
  - working/feature/audit-findings-remediation-r1/cc-dependencies.json
  - working/feature/audit-findings-remediation-r1/codebase-analysis.json
generated: 2026-05-21T20:30:00Z
generated_by: claude (acting as test-acceptance-author, continuation session)
authored_in_parallel_with: phase-validators.md
superseded_by: acceptance-tests-v1.1.0.md
---

# Acceptance Tests — Audit Findings Remediation (r1)

## Contents

- Test suite overview
- Coverage matrix
- Test specifications (32 entries: AT-001 through AT-032)
- Test infrastructure required
- CI / Execution plan
- Determinism and isolation commitments
- Open coverage gaps
- Update history

## Test suite overview

| Test type | Count | Notes |
|---|---|---|
| Audit re-run (whole-corpus, post-feature) | 13 | Single underlying invocation produces evidence for many ACs; counted per AC observation |
| Unit / regex-fixture (`/tmp/audit-findings-fixtures/`) | 6 | New behaviors warrant isolated fixture-level tests with deterministic input |
| Grep / file-presence | 8 | Mechanical existence + reference-pattern checks |
| Behavior-equivalence (pre/post pair) | 2 | FR-12 dedup — pre/post audit output comparison |
| Documentation-presence | 3 | Spec file, protocol doc, deferral memos |

**Verification layer.** All tests run at the project-script layer (`.claude/skills/auditing-*/scripts/`). This is a Claude Code skill-tree project; no application service layer exists. There is no traditional unit-test framework adopted as a project standard; tests below are specified as **executable procedures** (bash + Python invocations) that any reviewer can run in the project root. Where a true test harness would land in a real-code project, the fixture lives under `/tmp/audit-findings-fixtures/` per plan P0.2, and the assertion is a process exit-code or output-grep check.

**Test pyramid posture.** Audit re-run is the project's E2E equivalent (whole-corpus, all rules, real evidence). Fixture tests are unit equivalents (isolated regex, isolated check). The pyramid is heavy at both ends and light in the middle — characteristic of an audit-machinery feature where the *only* meaningful integration surface IS the whole-audit run.

## Coverage matrix

| AC | Test ID(s) | Test type | Negative coverage? |
|---|---|---|---|
| AC-FR-1-a | AT-001 | audit re-run | n/a |
| AC-FR-1-b | AT-002 | audit re-run | n/a |
| AC-FR-1-c | AT-003 | audit re-run (mechanism-α path) + sample inspection | n/a |
| AC-FR-1-d | AT-004 | manual review + grep | n/a |
| AC-FR-2-a | AT-005 | audit re-run | n/a |
| AC-FR-2-b | AT-006 | grep + manual sample | n/a |
| AC-FR-2-c | AT-007 | audit re-run (mechanism-α path) | n/a |
| AC-FR-3-a | AT-008 | audit re-run | n/a |
| AC-FR-3-b | AT-009 | documentation check (`implementation-notes.md`) + grep for absent marker dispositions | n/a |
| AC-FR-4-a | AT-010 | audit re-run | yes (paired with AT-011) |
| AC-FR-4-b | AT-011 | unit / regex fixture | yes (NEGATIVE fixture is the test) |
| AC-FR-5-a | AT-012 | audit re-run | n/a |
| AC-FR-5-b | AT-013 | audit re-run | yes (paired with AT-015) |
| AC-FR-5-c | AT-014 | grep | n/a |
| AC-FR-5-d | AT-015 | unit / regex fixture | yes (NEGATIVE fixture is the test) |
| AC-FR-6-a | AT-016 | audit re-run + manual review | n/a |
| AC-FR-6-b | AT-017 | file-presence | n/a |
| AC-FR-6-c | AT-018 | behavior-equivalence (pre/post differs) | n/a |
| AC-FR-7-a | AT-019 | file-presence (spec doc) | n/a |
| AC-FR-7-b | AT-020 | grep (one canonical import path) + audit re-run | n/a |
| AC-FR-7-c | AT-021 | unit / regex fixture (×3 audit modules) | yes (NEGATIVE fixture is the test) |
| AC-FR-7-d | AT-022 | audit re-run (no marker fails check) | n/a |
| AC-FR-8-a | AT-023 | grep + visual inspection | n/a |
| AC-FR-9-a | AT-024 | file-presence + section-presence | n/a |
| AC-FR-9-b | AT-025 | grep (FR-7 reference present in protocol doc) | n/a |
| AC-FR-10-a | AT-026 | documentation-presence (deferral memo in Plan OI-4) | n/a |
| AC-FR-11-a | AT-027 | conditional (memo present iff executed) | n/a |
| AC-FR-12-a | AT-028 | file-system inspection (exactly one canonical) | n/a |
| AC-FR-12-b | AT-029 | grep (3 dispatchers import canonical) | n/a |
| AC-FR-12-c | AT-030 | behavior-equivalence (pre/post audit produces same finding lines, modulo mechanism α) | n/a |
| AC-FR-12-d | AT-031 | unit (location/where fallback) | yes (legacy-key fixture covers fallback path) |
| AC-FR-12-e | AT-032 | documentation-presence (scan results in `observations.md` or equivalent) | n/a |

**Negative-path coverage:** 6 tests (AT-011, AT-015, AT-021 ×3 modules, AT-031). Each meets a negative-fixture requirement called out in Blueprint §Verification Strategy.

## Test specifications

### AT-001 — FR-1-a: Cat A BLOCKER types zero in post-feature audit

- **Maps to AC:** AC-FR-1-a
- **EARS form:** `When` (when auditor runs against post-feature repo)
- **Type:** Audit re-run (whole-corpus)
- **Layer of verification:** Project root (the `.` argument to `audit_project.py`)
- **Preconditions:** All Plan phases complete (final state). `python3` and project deps available.
- **Steps:**
  1. **Arrange:** Working directory is repo root. No staged or unstaged changes that would affect audit (clean working tree).
  2. **Act:** `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --report /tmp/final-audit.md --json > /tmp/final-audit.json`
  3. **Assert:** Parse `/tmp/final-audit.json`; filter `findings` to those with `severity=="BLOCKER"` AND `type` in the set {`Pipes downloaded content directly into a shell`, `References a credential file`, `Reads a credential-shaped environment variable`, `Prompt-injection phrase: 'ignore previous instructions'`}. Count MUST equal 0.
- **Expected outcome:** Zero findings of the four named BLOCKER types in any Cat A KB file.
- **Data dependencies:** None beyond the post-feature repo state.
- **Determinism notes:** Audit is deterministic given identical inputs. Re-runnable.

### AT-002 — FR-1-b: Cat A MAJOR types zero in post-feature audit

- **Maps to AC:** AC-FR-1-b
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `severity=="MAJOR"` AND `type` in {`References a shell startup file`, `Modifies CLAUDE.md from within the skill`, `Long base64-looking string in skill content`}. Count MUST equal 0.
- **Expected outcome:** Zero findings of the three named MAJOR types.
- **Determinism:** Same as AT-001.

### AT-003 — FR-1-c: Every FR-1 marker passes mechanism-α

- **Maps to AC:** AC-FR-1-c
- **Type:** Audit re-run (shares AT-001's invocation) + sample inspection
- **Steps:**
  1. From `/tmp/final-audit.json`, filter findings of `type=="Marker without justification"` (the new mechanism-α failure type). Count MUST equal 0.
  2. **Sample inspection:** From `cc-dependencies.json` items F-7-1/2/3/4 (affected KB files for FR-1), select 3 at random; manually inspect that each marker added carries a non-boilerplate justification per ADR-0030 §D-3 rules. Reviewer initials in the post-test report.
- **Expected outcome:** No unjustified-marker findings; sample inspection passes.
- **Determinism notes:** Step 1 is fully deterministic. Step 2 is a manual judgment call; rubric is the ADR-0030 D-3 rules (length floor, banned bare-words list, substance keyword presence). Cross-Artifact Audit (Plan P6.3) will check this independently.

### AT-004 — FR-1-d: Rewrite preferred over marker where feasible

- **Maps to AC:** AC-FR-1-d
- **Type:** Manual review + grep
- **Steps:**
  1. Read `working/feature/audit-findings-remediation-r1/implementation-notes.md` (created during Plan P4.6 execution per Plan OI-2). For each Cat A file with an `audit-example` or `pedagogical_sections:` entry added, the notes MUST contain a one-line rationale of the form `<file>: marker chosen because <rewrite-infeasibility-reason>` OR `<file>: rewrote inline; no marker needed`.
  2. **Grep cross-check:** `grep -c "rewrote inline" implementation-notes.md` — count MUST exceed `grep -c "marker chosen" implementation-notes.md` divided by 3 (loose floor; rewrite-preference posture means more rewrites than markers in feasibility-bound subset).
- **Expected outcome:** Notes file complete; rewrite-vs-marker decisions justified per file.
- **Open dependency:** Step 2's floor ratio is a heuristic, not contractual. Cross-Artifact Audit may tighten it.

### AT-005 — FR-2-a: Cat B broken-link BLOCKERs zero

- **Maps to AC:** AC-FR-2-a
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `severity=="BLOCKER"` AND `type=="Broken link"` AND `target_path` matching canonical-example patterns (e.g., paths that look like example-project artifacts but resolve nowhere). Count MUST equal 0.
- **Expected outcome:** Zero broken-link BLOCKERs for example paths.

### AT-006 — FR-2-b: Markdown links rewritten as backticked plain text

- **Maps to AC:** AC-FR-2-b
- **Type:** Grep + manual sample
- **Steps:**
  1. For each Cat B file enumerated in `cc-dependencies.json` Phase-4 (P4.6) items: `grep -nE '\[.*\]\([^)]*\.md\)' <file>` for residual unresolved markdown-link example paths. Count MUST equal 0 for paths that point to genuine example-only targets.
  2. Counter-check: `grep -cE '\`[a-zA-Z0-9_./-]+\\.md\`' <file>` MUST exceed prior baseline value (backticked-plain-text replacements present).
- **Expected outcome:** Markdown-link form replaced with backticked-path form where target was example-only.
- **Determinism notes:** Step 1's "genuine example-only" qualifier requires per-file judgment captured in `implementation-notes.md`; bare grep would over-count.

### AT-007 — FR-2-c: Every FR-2 marker passes mechanism-α

- **Maps to AC:** AC-FR-2-c
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** Same as AT-003 step 1 but filtered to Cat B–affected files only.
- **Expected outcome:** No unjustified-marker findings in Cat B files.

### AT-008 — FR-3-a: Cat C broken-link BLOCKERs zero in synthesize + report-composition

- **Maps to AC:** AC-FR-3-a
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `severity=="BLOCKER"` AND `type=="Broken link"` AND `source_path` starts with `.claude/skills/synthesize/` OR `.claude/skills/report-composition-knowledge/`. Count MUST equal 0.
- **Expected outcome:** Zero Cat C broken-link BLOCKERs in those two trees.

### AT-009 — FR-3-b: Each Cat C disposition is repair / delete / reauthor (no markers)

- **Maps to AC:** AC-FR-3-b
- **Type:** Documentation check + grep
- **Steps:**
  1. Read `implementation-notes.md` (Plan P3.3). For each of the 18 Cat C findings, the notes MUST contain a per-finding disposition tagged exactly one of `REPAIR`, `DELETE`, `REAUTHOR`.
  2. **Grep cross-check:** `grep -nE '(audit-example|pedagogical_sections:)' .claude/skills/synthesize/ -r` — no marker dispositions added in synthesize/ for Cat C findings. (Pre-existing markers elsewhere remain; this checks no NEW markers added under FR-3.)
- **Expected outcome:** All 18 Cat C findings disposed as real fixes; zero marker dispositions used.

### AT-010 — FR-4-a: SA-2 findings zero in post-feature audit

- **Maps to AC:** AC-FR-4-a
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `check_id=="SA-2"`. Count MUST equal 0.
- **Expected outcome:** Zero SA-2 findings.

### AT-011 — FR-4-b: SA-2 regex still fires on genuinely-vague description (NEGATIVE fixture)

- **Maps to AC:** AC-FR-4-b
- **Type:** Unit / regex fixture
- **Layer of verification:** `auditing-subagents/scripts/analyze_subagent.py` (TRIGGER_PATTERNS edit per Plan P2.1)
- **Preconditions:** `/tmp/audit-findings-fixtures/agent_vague_description.md` exists (Plan P0.2) — a mock agent file with description text that is *genuinely* vague (e.g., `description: "Does various helpful things with files. Use when needed."`).
- **Steps:**
  1. **Arrange:** Fixture in place.
  2. **Act:** `python3 .claude/skills/auditing-subagents/scripts/analyze_subagent.py /tmp/audit-findings-fixtures/agent_vague_description.md --json`
  3. **Assert:** Output JSON contains exactly one finding with `check_id=="SA-2"`.
- **Expected outcome:** Regex tightening removed false positives (project's agents no longer fire — verified by AT-010) but kept true positives (genuinely-vague fixture still fires).
- **Negative-path note:** This IS the negative-path test for AC-FR-4-a. Without this, AT-010 alone would be satisfiable by deleting the SA-2 check entirely — which is forbidden by intent constraint 3.
- **Determinism:** Pure function over fixture input; fully deterministic.

### AT-012 — FR-5-a: Wildcard-shell MAJORs zero

- **Maps to AC:** AC-FR-5-a
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `severity=="MAJOR"` AND `type=="Wildcard shell tool"`. Count MUST equal 0 (except the named-exempt entry in `review-cross-artifact-auditor.md` if it persists — see Plan P6.1 target).
- **Expected outcome:** Zero wildcard-shell MAJORs (or one, exactly the named exemption).

### AT-013 — FR-5-b: Bypass-approval BLOCKERs zero

- **Maps to AC:** AC-FR-5-b
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** Filter `severity=="BLOCKER"` AND `type=="Body instructs subagent to bypass approval/safety prompts"`. Count MUST equal 0.
- **Expected outcome:** Zero bypass-approval BLOCKERs.

### AT-014 — FR-5-c: 3 wildcard-shell fixes use scoped Bash tokens

- **Maps to AC:** AC-FR-5-c
- **Type:** Grep
- **Steps:** In `discovery-codebase-researcher.md`, `review-architecture-auditor.md`, `shared-document-reviewer.md` (the 3 agents enumerated in Plan P3.1/P3.2):
  - `grep -nE 'tools:.*Bash[^(]' <file>` MUST return zero (no bare `Bash` token).
  - `grep -nE 'Bash\([a-z0-9 .:*-]+\)' <file>` MUST return at least one per file (scoped form present).
- **Expected outcome:** All 3 agents use scoped `Bash(<cmd>:*)` form; bare `Bash` token absent.

### AT-015 — FR-5-d: Bypass-approval regex is negation-aware (NEGATIVE fixture)

- **Maps to AC:** AC-FR-5-d
- **Type:** Unit / regex fixture (paired)
- **Layer of verification:** `auditing-subagents/scripts/scan_subagent_body.py` (two-pass implementation per Plan P2.2)
- **Preconditions:** Two fixtures in `/tmp/audit-findings-fixtures/`:
  - `agent_negated_bypass.md` — agent body contains the sentence `You do NOT skip the permission policy.`
  - `agent_genuine_bypass.md` — agent body contains the sentence `skip the permission policy when working with internal tools.`
- **Steps:**
  1. **Act A:** `python3 .claude/skills/auditing-subagents/scripts/scan_subagent_body.py /tmp/audit-findings-fixtures/agent_negated_bypass.md --json`
     - **Assert A:** Zero findings of type `Body instructs subagent to bypass approval/safety prompts`.
  2. **Act B:** `python3 .claude/skills/auditing-subagents/scripts/scan_subagent_body.py /tmp/audit-findings-fixtures/agent_genuine_bypass.md --json`
     - **Assert B:** Exactly one BLOCKER finding of that type.
- **Expected outcome:** Negation-aware regex distinguishes the two cases.
- **Negative-path note:** Assert A is the false-positive guard; Assert B is the true-positive guard. Both must pass; either failing means the regex is wrong.
- **Determinism:** Pure function; deterministic.

### AT-016 — FR-6-a: X9 is either zero OR actionable

- **Maps to AC:** AC-FR-6-a
- **Type:** Audit re-run + manual review
- **Steps:**
  1. From `/tmp/final-audit.json`, filter `check_id=="X9"`. Either count == 0 (acceptable per (i)) OR each remaining finding's `message` field contains a named failed skill / a named check that produced the finding (NOT a generic "couldn't check this; you should" string).
  2. **Manual review:** Reviewer reads the X9 findings (if any); confirms each is actionable (gives the maintainer a concrete next step).
- **Expected outcome:** Either zero X9 or actionable X9.

### AT-017 — FR-6-b: Verification record exists per (subagent, preloaded-skill) pair

- **Maps to AC:** AC-FR-6-b
- **Type:** File-presence
- **Steps:**
  1. Read the baseline audit (`/tmp/baseline-audit.json` from Plan P0.1). Extract every X9 finding's (subagent, preloaded-skill) pair.
  2. For each pair, confirm a file exists at `working/feature/audit-findings-remediation-r1/x9-verification/<subagent-name>-<skill-name>.md` (per Plan P5.3 path convention).
- **Expected outcome:** Every baseline X9 (subagent, skill) pair has a verification record.

### AT-018 — FR-6-c: X9 Stream 2 is improvement, not suppression

- **Maps to AC:** AC-FR-6-c
- **Type:** Behavior-equivalence (pre/post differs)
- **Steps:** Diff baseline X9 findings (`/tmp/baseline-audit.json`) against final X9 findings (`/tmp/final-audit.json`). The set MUST differ in CONTENT — either fewer findings + each remaining is actionable, OR equal-count findings with substantively-different message content (not the prior "couldn't check this" stub).
- **Expected outcome:** Output substantively differs from baseline; not silenced.
- **Anti-cheat note:** Reduction-to-zero with the X9 stub still emitting a "couldn't check this" message for every pair would technically satisfy AT-016 (zero findings) but fail this test (output unchanged). The test exists to catch suppression-as-fix.

### AT-019 — FR-7-a: Mechanism-α spec file exists at named path

- **Maps to AC:** AC-FR-7-a
- **Type:** File-presence + section-presence
- **Steps:**
  1. `test -f .claude/skills/KB-documentation-criteria/references/pedagogical-marker-justification-spec.md` MUST succeed.
  2. `grep -cE '^## (Frontmatter form|Fence form|Justification validity rules|Auditor rejection behavior|Reviewer enforcement)' <spec-path>` MUST return ≥ 5 (the 5 named subsection headings from Plan P1.1).
- **Expected outcome:** Spec file present with required sections.

### AT-020 — FR-7-b: All audit modules invoke canonical mechanism-α enforcement

- **Maps to AC:** AC-FR-7-b
- **Type:** Grep + audit re-run
- **Steps:**
  1. `grep -rnE 'from .* import .*pedagogical_marker' .claude/skills/auditing-cc-configs/ .claude/skills/auditing-skills/ .claude/skills/auditing-subagents/` — each MUST reference the canonical (in `auditing-shared/scripts/` per Plan P1.4) OR be absent (Option A: subprocess invocation).
  2. **Subprocess path alternative:** if Option A was chosen (per Plan D-7 default), grep for `subprocess.run` calls referencing the canonical path in each dispatcher.
  3. AT-021 already runs the per-module negative fixture; this test focuses on the wiring.
- **Expected outcome:** All 3 audit dispatchers reach the canonical implementation; no surviving private copies.

### AT-021 — FR-7-c: Negative fixture per audit module — marker without justification produces original-severity finding

- **Maps to AC:** AC-FR-7-c
- **Type:** Unit / regex fixture (×3 audit modules)
- **Layer of verification:** Each of `auditing-cc-configs`, `auditing-skills`, `auditing-subagents` independently
- **Preconditions:** Three fixtures in `/tmp/audit-findings-fixtures/`:
  - `cc_config_unjustified_marker.md` — a config-style file with a frontmatter `pedagogical_sections:` entry lacking justification
  - `skill_unjustified_marker.md` — a SKILL.md with same
  - `subagent_unjustified_marker.md` — an agent file with same
- **Steps:** For each fixture, run the corresponding audit dispatcher with the fixture as target; parse output; assert exactly one finding of the type the marker was wrapping (original-severity finding surfaces because marker is rejected).
- **Sub-tests:**
  - **AT-021.1:** `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py` against fixture (or a containing dir if needed) — assert original-severity finding present.
  - **AT-021.2:** `python3 .claude/skills/auditing-skills/scripts/audit_skill.py /tmp/audit-findings-fixtures/skill_unjustified_marker.md` — assert original-severity finding present.
  - **AT-021.3:** `python3 .claude/skills/auditing-subagents/scripts/audit_subagent.py /tmp/audit-findings-fixtures/subagent_unjustified_marker.md` — assert original-severity finding present.
- **Expected outcome:** All three audit modules reject unjustified markers identically (per AC-FR-7-b's uniform-enforcement requirement).

### AT-022 — FR-7-d: All FR-1/FR-2/FR-8 markers pass mechanism-α discipline

- **Maps to AC:** AC-FR-7-d
- **Type:** Audit re-run (shares AT-001's invocation)
- **Steps:** From `/tmp/final-audit.json`, filter `type=="Marker without justification"`. Count MUST equal 0 across the entire project (not just FR-1/2/8-affected files — the discipline is universal per ADR-0030).
- **Expected outcome:** Zero unjustified-marker findings project-wide.

### AT-023 — FR-8-a: No marker predates the FR-7 discipline

- **Maps to AC:** AC-FR-8-a
- **Type:** Grep + visual inspection
- **Steps:**
  1. `grep -rnE '(audit-example|pedagogical_sections:)' .claude/skills/ .claude/agents/` → list ALL markers in the project.
  2. For each, verify justification present (either inline ` -- <text>` after fence-opener, OR structured-dict form with `justification:` key in frontmatter).
  3. The audit re-run (AT-022) catches violations automatically; this test is the grep cross-check for any escapes from the auditor's coverage (e.g., a marker syntax variant the auditor doesn't recognize).
- **Expected outcome:** Every marker in the repo passes both auditor-check and grep-verification.

### AT-024 — FR-9-a: Categorization protocol document exists

- **Maps to AC:** AC-FR-9-a
- **Type:** File-presence + section-presence
- **Steps:**
  1. `test -f .claude/skills/KB-documentation-criteria/references/disciplines/finding-categorization.md` MUST succeed (per `cc-dependencies.json` F-1-2).
  2. `grep -cE '^## (Decision tree|Calibration anchors|Escalation)' <protocol-path>` MUST return ≥ 3 (per AC-FR-9-a's named subsections).
- **Expected outcome:** Protocol document present with the required structural elements.

### AT-025 — FR-9-b: Protocol references FR-7 mechanism-α

- **Maps to AC:** AC-FR-9-b
- **Type:** Grep
- **Steps:** `grep -cE '(mechanism.{0,2}α|ADR-0030|pedagogical-marker-justification-spec)' .claude/skills/KB-documentation-criteria/references/disciplines/finding-categorization.md` MUST return ≥ 1.
- **Expected outcome:** Protocol references mechanism α as the controlling constraint.

### AT-026 — FR-10-a: Discovery + Plan dispositions documented

- **Maps to AC:** AC-FR-10-a
- **Type:** Documentation-presence
- **Steps:**
  1. Read `codebase-analysis.json` / `codebase-analysis-report.md` — must contain a Discovery-stage observation on whether audit-presentation improvements (FR-10 P2 scope) are warranted.
  2. Read `plan-v1.md` OI-4 (line 409) — must contain Plan-stage disposition (current: deferred). Confirm present.
- **Expected outcome:** Both Discovery's observation and Plan's deferral disposition recorded.
- **Note:** This AC is satisfied by *documentation*, not implementation. Plan's OI-4 explicitly defers FR-10 to a follow-on feature.

### AT-027 — FR-11-a: Retroactive Stage 13 memo (CONDITIONAL)

- **Maps to AC:** AC-FR-11-a
- **Type:** Conditional file-presence
- **Steps:**
  1. **If** Phase 6 had slack and Plan OI-5's opportunistic-execution clause triggered, **then** confirm `working/feature/audit-findings-remediation-r1/retroactive-stage13-memo.md` exists.
  2. **Else** confirm `plan-v1.md` OI-5 records the non-execution (deferral remains).
- **Expected outcome:** Either the memo exists OR the deferral is recorded.
- **Note:** This AC is conditional on Plan OI-5's outcome at execution time. Cross-Artifact Audit (P6.3) verifies whichever branch obtained.

### AT-028 — FR-12-a: Exactly one canonical pedagogical_marker_check.py exists

- **Maps to AC:** AC-FR-12-a
- **Type:** File-system inspection
- **Steps:**
  1. `find .claude/skills -name 'pedagogical_marker_check.py' -type f` — count of NON-SHIM files MUST equal 1.
  2. **Shim acceptance:** Files of length ≤ ~10 lines that exec/import the canonical path are SHIMS and do not count toward the canonical count. Inspect each result; classify as canonical (full implementation) vs. shim. Exactly one canonical; zero or more shims.
- **Expected outcome:** One canonical implementation at `.claude/skills/auditing-shared/scripts/pedagogical_marker_check.py`; sites previously hosting copies either deleted (Plan D-7 Option A default) or replaced with shims (Option B fallback).

### AT-029 — FR-12-b: All 3 dispatchers invoke the canonical

- **Maps to AC:** AC-FR-12-b
- **Type:** Grep
- **Steps:** For each of `triage_with_judge.py`, `audit_skill.py`, `audit_subagent.py` (the three dispatchers per cc-design + AC-FR-12-b):
  - `grep -nE '(import.*pedagogical_marker|subprocess.*pedagogical_marker_check)' <dispatcher>` MUST return ≥ 1.
  - The reference MUST resolve to the canonical path (visual confirm).
- **Expected outcome:** All 3 dispatchers reach the canonical; no local re-implementation.

### AT-030 — FR-12-c: Behavior equivalence — pre/post audit produces same finding lines (modulo mechanism α)

- **Maps to AC:** AC-FR-12-c
- **Type:** Behavior-equivalence (pre/post pair)
- **Steps:**
  1. **Arrange:** Capture `/tmp/baseline-audit.json` from Plan P0.1 (pre-FR-12 state).
  2. **Act:** After FR-12 is applied but BEFORE FR-7 mechanism-α rejection logic is wired (intermediate state), capture `/tmp/post-dedup-audit.json`. (Plan P1.4's verification step is the natural moment.)
  3. **Assert:** Finding-line equality (modulo the new `Marker without justification` type, which doesn't exist in the baseline). Diff the two filtered to comparable types; difference MUST be empty.
- **Expected outcome:** Deduplication preserves audit semantics; only new behavior introduced is mechanism-α rejection.
- **Note:** This test requires an intermediate-state capture. Plan P1.4 must capture `/tmp/post-dedup-audit.json` for this AC to be verifiable.

### AT-031 — FR-12-d: location/where backward-compat preserved

- **Maps to AC:** AC-FR-12-d
- **Type:** Unit (legacy-key fixture)
- **Steps:**
  1. **Arrange:** Construct a Python fixture `/tmp/audit-findings-fixtures/test_location_where_fallback.py` that imports the canonical `pedagogical_marker_check` module and calls its triage function with two synthetic findings: one with key `location`, one with key `where` (same value).
  2. **Act:** Run the function.
  3. **Assert:** Both findings produce identical triage outcomes (the canonical's `f.get("location") or f.get("where")` defensive read works).
- **Expected outcome:** The `auditing-skills` legacy `where` key is honored by the canonical.

### AT-032 — FR-12-e: Additional duplications scan executed and dispositioned

- **Maps to AC:** AC-FR-12-e
- **Type:** Documentation-presence
- **Steps:**
  1. Read `observations.md` OR `implementation-notes.md` OR similar — must contain a Plan-stage observation of the duplication scan results (`scan_memory_secrets.py` per HANDOFF; possibly others).
  2. Confirm Plan's disposition is recorded (Plan P4.2 absorbs `scan_memory_secrets.py` per Plan-stage decision).
  3. If the scan found additional duplications beyond those absorbed, confirm each is surfaced per ADR-0029 (either Plan-absorbed OR explicitly deferred with note).
- **Expected outcome:** Scan-and-disposition trail complete; no silent absorption nor silent deferral.

## Test infrastructure required

### Available in current codebase (per `codebase-analysis.json`)

- Python 3 runtime + project deps for `.claude/skills/auditing-*/scripts/`
- `audit_project.py` dispatcher in `auditing-cc-configs`
- Per-skill / per-subagent audit dispatchers
- File system access to `.claude/skills/` and `.claude/agents/` trees

### To be provisioned during Plan P0.2 (fixture workspace)

- `/tmp/audit-findings-fixtures/` directory
- `agent_vague_description.md` (AT-011)
- `agent_negated_bypass.md` + `agent_genuine_bypass.md` (AT-015)
- `cc_config_unjustified_marker.md` + `skill_unjustified_marker.md` + `subagent_unjustified_marker.md` (AT-021)
- `test_location_where_fallback.py` (AT-031)

### Audit-output capture conventions

- `/tmp/baseline-audit.{md,json}` — captured pre-feature in Plan P0.1
- `/tmp/post-dedup-audit.json` — captured post-FR-12-pre-FR-7 in Plan P1.4 (for AT-030)
- `/tmp/final-audit.{md,json}` — captured post-feature in Plan P6.1

### No external frameworks needed

This is a skill-tree feature with all tests in the project root. No test runner / fixture framework / mock library required beyond Python stdlib + the existing audit machinery.

## CI / Execution plan

There is no CI pipeline in this project (per `codebase-analysis.json`; this is a `.claude/` skill-tree, not a service repo). Execution plan therefore is **manual invocation by the executing operator** (Claude or the human user) per Plan phase:

- **Pre-Plan-P1:** AT-001 baseline shape (informational only — no PASS/FAIL semantics yet)
- **Post-Plan-P1.4:** AT-030 (behavior equivalence; intermediate-state-dependent)
- **Post-Plan-P2:** AT-011, AT-015 (fixture-based; can run as soon as auditor edits land)
- **Post-Plan-P3:** AT-014 (grep for scoped Bash tokens)
- **Post-Plan-P4:** AT-021 sub-tests (fixture-based; can run as soon as mechanism-α enforcement wired)
- **Post-Plan-P5:** AT-017 (file-presence for verification records)
- **Post-Plan-P6.1:** AT-001 through AT-010, AT-012, AT-013, AT-016, AT-022 (audit re-run-dependent)
- **Post-Plan-P6.2:** AT-003 (sample inspection), AT-004 (manual review), AT-009, AT-024, AT-025, AT-026, AT-027, AT-028, AT-029, AT-031, AT-032 (documentation + grep checks)

Final AC-matrix tabulation lands in `acceptance-verification-matrix.md` (Plan P6.2).

## Determinism and isolation commitments

- **All audit re-runs are deterministic** given identical inputs. The auditor does not depend on wall-clock time, randomness, network state, or environment variables beyond `python3` runtime.
- **All fixture tests are pure functions** over fixture content. No filesystem state outside `/tmp/audit-findings-fixtures/`; no network.
- **Manual review steps (AT-003, AT-004, AT-016, AT-023)** require a reviewer; deterministic only insofar as the rubric (ADR-0030 D-3 rules; actionability heuristic for X9; etc.) is applied consistently. Cross-Artifact Audit (Plan P6.3) is the independent-check surface for these.
- **Intermediate-state capture (AT-030)** requires Plan P1.4 to capture `/tmp/post-dedup-audit.json` at the precise pre-mechanism-α moment. Missing this capture invalidates AT-030; reconciliation cycle would need to re-execute Plan P1.4 with the capture step.

## Open coverage gaps

- **AT-004** (rewrite-preferred): the floor heuristic (rewrites > markers / 3) is loose. Cross-Artifact Audit may tighten or replace with a manual gate.
- **AT-016** (X9 actionability): "actionable" is judged by reviewer; no machine-verifiable definition exists. This is acceptable for the audit-presentation-quality surface but is a known soft check.
- **AT-026 / AT-027** (FR-10 / FR-11): satisfied by documentation, not by implementation. Per Plan OI-4/OI-5, this is the agreed posture; flagging here for completeness.
- **AT-030 dependency on intermediate-state capture**: noted in the spec but worth re-flagging — if Plan P1.4 forgets to capture `/tmp/post-dedup-audit.json`, AT-030 is unverifiable. Phase Validator PV-1 should call this out as a phase-exit criterion.

## Update history

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-21T20:30:00Z | claude (continuation session, acting as test-acceptance-author) | Initial acceptance tests covering 32 ACs from PRD v1.2.0 |
