---
id: AT-pipeline-quickwins-hardening-r1
version: 1.0.1
status: draft
feature_slug: pipeline-quickwins-hardening-r1
doc_type: acceptance-tests
derived_from: working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md
source_prd: working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
source_plan: working/feature/pipeline-quickwins-hardening-r1/plan-v1.md
codebase_analysis: working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
generated: 2026-05-26T00:00:00Z
generated_by: test-acceptance-author
supersedes: null
revision_history:
  - version: 1.0.0
    date: 2026-05-26
    summary: |
      Initial Acceptance Test specification. One specification per Blueprint v2.2
      AC across FR-1 (8 ACs / FR-1 cluster), FR-2 (7 ACs incl. migration smoke),
      FR-3 (12 ACs incl. deprecated-row handling), FR-4a (7 ACs), FR-4b (7 ACs),
      FR-4c (11 ACs), FR-5 (7 ACs), FR-6 (1 cross-cutting AC), FR-7 (4 ACs),
      cross-layer ACs AC-X-1..AC-X-4, and NFR ACs (NFR-1 through NFR-15 with
      explicit AC bindings). Coverage matrix below; every AC has at least one
      AT-NNN entry. Tests follow the project's convention of self-contained
      `smoke_test_*.py` scripts adjacent to validator scripts plus
      devcontainer-rebuild and GitHub-Actions `workflow_dispatch` integration
      tests. No new test framework introduced.
  - version: 1.0.1
    date: 2026-05-26
    summary: |
      Cross-Artifact Audit cycle 1 reconciliation (two surgical edits).
      (1) I-CA-001 — Added a PRD-to-Blueprint AC ID alias note at the top of the
      Coverage Matrix so readers arriving from the PRD with `AC-FR-N-x` IDs can
      find them under their Blueprint-expanded forms (`AC-CC-N-x` / `AC-CICD-N-x`
      / `AC-CS-N-x`). (2) I-CA-007 — Added AT-080 (Option (a) per the auditor's
      recommendation): a static-inspection unit test that parses both CI workflow
      YAMLs and asserts byte-identical SHA pins for `actions/checkout` and
      `devcontainers/ci`. Open Coverage Gaps item 7 updated to point at AT-080.
      No other AT-NNN content changed; no test-type distribution change beyond
      +1 unit-style static-inspection test; CI execution plan adjusted to add
      AT-080 to the static-inspection fast-PR class.
---

# Acceptance Tests: Pipeline Quick-Wins Hardening (Round 1)

## Contents

- [x] Coverage Matrix
- [x] Test Suite Overview
- [x] Test Specifications
- [x] Test Infrastructure Required
- [x] CI Execution Plan
- [x] Determinism and Isolation Commitments
- [x] Open Coverage Gaps
- [x] References

---

## Coverage Matrix

Every AC has at least one acceptance test. Where a single AC has multiple distinct conditions (e.g., the FR-4a A1/A2/A3/A4 assertion fan-out, FR-4c's three trigger types) each condition gets its own AT-NNN entry.

**AC ID alias note (PRD ↔ Blueprint).** Readers arriving from the PRD will find AC IDs of the form `AC-FR-N-x` (e.g., `AC-FR-1-a`, `AC-FR-5-a`). These PRD-original IDs are tested under their Blueprint-expanded forms in this matrix — the Blueprint composition stage re-namespaced ACs by layer for cross-mechanism distinguishability. Mapping: `AC-FR-1-x` → `AC-CC-1-x`, `AC-FR-2-x` → `AC-CC-2-x`, `AC-FR-3-x` → `AC-CC-3-x`, `AC-FR-4a-x` → `AC-CS-4a-x`, `AC-FR-4b-x` → `AC-CS-4b-x`, `AC-FR-4c-x` → `AC-CICD-4c-x`, `AC-FR-5-x` → `AC-CICD-5-x`, `AC-FR-7-x` → `AC-CC-7-x`. (FR-6 is cross-cutting and retains the `AC-6-a` form.) See Blueprint v2.2 §Acceptance Criteria for the canonical naming and per-layer rationale.

| AC | EARS Form | Test IDs | Layer |
|---|---|---|---|
| **FR-1 — Verdict-vs-findings parity validator** | | | |
| AC-CC-1-a | When (event-driven) | AT-001 | Claude Code |
| AC-CC-1-b | If-then (unwanted) | AT-002, AT-003 | Claude Code |
| AC-CC-1-c | See Blueprint v1 (paraphrased pass-through; reuse AT-004) | AT-004 | Claude Code |
| AC-CC-1-d | Where (state-driven) | AT-004 | Claude Code |
| AC-CC-1-e | When (NFR-6 fail-closed) | AT-005 | Claude Code |
| AC-CC-1-f | Ubiquitous (FR-6 fields) | AT-006 | Claude Code |
| AC-CC-1-g | Ubiquitous (NFR-5 determinism) | AT-007 | Claude Code |
| AC-CC-1-h | Ubiquitous (NFR-9 back-compat) | AT-008 | Claude Code |
| **FR-2 — Orchestrator dispatch self-check** | | | |
| AC-CC-2-a | When (event-driven) | AT-009 | Claude Code |
| AC-CC-2-b | If-then (refusal) | AT-010 | Claude Code |
| AC-CC-2-c | Where (MINOR/PATCH permit) | AT-011 | Claude Code |
| AC-CC-2-d | Ubiquitous (FR-6 fields) | AT-012 | Claude Code |
| AC-CC-2-e | Ubiquitous (NFR-5 determinism) | AT-013 | Claude Code |
| AC-CC-2-f | If-then (NFR-6 fail-closed missing input) | AT-014 | Claude Code |
| AC-CC-2-g | When (migration; pre-feature checkpoint resume per ADR-0057) | AT-015 | Claude Code |
| **FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule OP-11** | | | |
| AC-CC-3-a | When (iteration trigger) | AT-016 | Claude Code |
| AC-CC-3-b | If-then (invocation mismatch BLOCKER) | AT-017 | Claude Code |
| AC-CC-3-c | If-then (missing-in-adr-0041) | AT-018 | Claude Code |
| AC-CC-3-d | If-then (missing-in-mcp.json) | AT-019 | Claude Code |
| AC-CC-3-e | Where (deprecated + absent → no finding) | AT-020 | Claude Code |
| AC-CC-3-f | If-then (deprecated-row-still-present BLOCKER) | AT-021 | Claude Code |
| AC-CC-3-g | Ubiquitous (NFR-10 back-compat) | AT-022 | Claude Code |
| AC-CC-3-h | Ubiquitous (FR-6 fields) | AT-023 | Claude Code |
| AC-CC-3-i | Ubiquitous (NFR-5 determinism) | AT-024 | Claude Code |
| AC-CC-3-j | Ubiquitous (NFR-7 / NFR-8 opaque env tokens) | AT-025 | Claude Code |
| AC-CC-3-k | If-then (NFR-6 parse failure) | AT-026 | Claude Code |
| AC-CC-3-l | Ubiquitous (NFR-13 — no event writes) | AT-027 | Claude Code |
| **FR-4a — Static-shape check** | | | |
| AC-CS-4a-1 | When (A1+A2+A3+A4 assertion bundle) | AT-028, AT-029, AT-030, AT-031 | Codespaces |
| AC-CS-4a-2 | Ubiquitous (cache-hit/cache-miss parity) | AT-032 | Codespaces |
| AC-CS-4a-3 | If-then (fail-closed event + halt) | AT-033 | Codespaces |
| AC-CS-4a-4 | If-then (no Swift assertion) | AT-034 | Codespaces |
| AC-CS-4a-5 | Ubiquitous (sentinel-less) | AT-035 | Codespaces |
| AC-CS-4a-6 | Ubiquitous (NFR-3 budget, p95 < 100 ms) | AT-036 | Codespaces |
| AC-CS-4a-7 | Ubiquitous (FR-6 four fields) | AT-037 | Codespaces |
| **FR-4b — Calibration script** | | | |
| AC-CS-4b-1 | When (full calibration contract) | AT-038 | Codespaces |
| AC-CS-4b-2 | Ubiquitous (one event per run regardless of outcome) | AT-039 | Codespaces |
| AC-CS-4b-3 | If-then (NOT invoked from postCreate.sh) | AT-040 | Codespaces |
| AC-CS-4b-4 | If-then (no Swift assertion) | AT-041 | Codespaces |
| AC-CS-4b-5 | Ubiquitous (ADR-0058 payload shape) | AT-042 | Codespaces |
| AC-CS-4b-6 | Ubiquitous (FR-6 fields on fail/drift) | AT-043 | Codespaces |
| AC-CS-4b-7 | Ubiquitous (NFR-4 wall-clock ≤ 60 s informational) | AT-044 | Codespaces |
| **FR-4c — Calibration CI workflow** | | | |
| AC-CICD-4c-1 | When (weekly cron) | AT-045 | CI/CD |
| AC-CICD-4c-2 | When (versions.env / script-change PR) | AT-046 | CI/CD |
| AC-CICD-4c-3 | If-then (fail surfaces in `$GITHUB_STEP_SUMMARY`) | AT-047 | CI/CD |
| AC-CICD-4c-4 | If-then (trigger-restriction; other paths don't run) | AT-048 | CI/CD |
| AC-CICD-4c-5 | When (workflow_dispatch parity) | AT-049 | CI/CD |
| AC-CICD-4c-6 | Ubiquitous (NFR-4 5-min ceiling; p95 < 2 min) | AT-050 | CI/CD |
| AC-CICD-4c-7 | Ubiquitous (concurrency: gitnexus-calibration) | AT-051 | CI/CD |
| AC-CICD-4c-8 | Ubiquitous (no new secrets; `contents: read`) | AT-052 | CI/CD |
| AC-CICD-4c-9 | Ubiquitous (exit-code-as-contract) | AT-053 | CI/CD |
| AC-CICD-4c-10 | Ubiquitous (no duplicate event emission) | AT-054 | CI/CD |
| AC-CICD-4c-11 | Ubiquitous (`timeout-minutes: 5`) | AT-055 | CI/CD |
| **FR-5 — MCP connectivity smoke workflow** | | | |
| AC-CICD-5-a | When (path-trigger fires) | AT-056 | CI/CD |
| AC-CICD-5-b | If-then (non-connected → fail) | AT-057 | CI/CD |
| AC-CICD-5-c | When (all connected → pass) | AT-058 | CI/CD |
| AC-CICD-5-d | When (CLI itself fails → exit 2) | AT-059 | CI/CD |
| AC-CICD-5-e | Ubiquitous (FR-6 fields on fail) | AT-060 | CI/CD |
| AC-CICD-5-f | Ubiquitous (NFR-4 5-min ceiling; p95 ≤ 4 min) | AT-061 | CI/CD |
| AC-CICD-5-g | Ubiquitous (NFR-7/NFR-8 no credentials) | AT-062 | CI/CD |
| **FR-6 — Cross-cutting diagnostic discipline** | | | |
| AC-6-a | Ubiquitous (four-field diagnostic across all mechanisms) | AT-063 | Cross-cutting (aggregator) |
| **FR-7 — Deferral-register tightening** | | | |
| AC-CC-7-a | (B-1 canonical parenthetical) | AT-064 | Claude Code |
| AC-CC-7-b | When (H-4 same parenthetical) | AT-065 | Claude Code |
| AC-CC-7-c | If-then (mismatch → update) | AT-066 | Claude Code |
| AC-CC-7-d | (Why-excluded / Re-examination / Forgetting-risk text) | AT-067 | Claude Code |
| **Cross-Layer** | | | |
| AC-X-1 | When (per-mechanism isolation; NFR-11) | AT-068, AT-069 | Cross-layer |
| AC-X-2 | Ubiquitous (NFR-13 four-type closed-enum) | AT-070 | Cross-layer |
| AC-X-3 | Ubiquitous (NFR-15 MCP allowlists unchanged) | AT-071 | Claude Code |
| AC-X-4 | Ubiquitous (Q-CS-1b staleness banner) | AT-072, AT-073, AT-074 | Codespaces |
| **Non-Functional explicit ACs** | | | |
| AC-NFR-1-a | Ubiquitous (FR-1 small-number-of-seconds) | AT-075 | Claude Code |
| AC-NFR-2-a | Ubiquitous (FR-2 small-number-of-seconds) | AT-076 | Claude Code |
| AC-NFR-3-a | Ubiquitous (FR-4a sub-100 ms + no network) | AT-036 (shared with AC-CS-4a-6) | Codespaces |
| AC-NFR-4-a | Ubiquitous (FR-5 ≤ 5 min) | AT-061 (shared with AC-CICD-5-f) | CI/CD |
| AC-NFR-4-b | Ubiquitous (FR-4c ≤ 5 min) | AT-050 (shared with AC-CICD-4c-6) | CI/CD |
| AC-NFR-5-a | Ubiquitous (determinism across all five) | AT-007, AT-013, AT-024 (per mechanism aggregator) | Cross-layer |
| AC-NFR-6-a | If-then (fail-closed on internal error) | AT-005, AT-014, AT-026 (per mechanism aggregator) | Cross-layer |
| AC-NFR-7-a | Ubiquitous (no new credentials) | AT-052, AT-062 + AT-077 | Cross-layer |
| AC-NFR-8-a | Ubiquitous (no credential values in diagnostics) | AT-078 | Cross-layer |
| AC-NFR-9-a | Ubiquitous (back-compat reviewer outputs) | AT-008 (shared with AC-CC-1-h) | Claude Code |
| AC-NFR-10-a | Ubiquitous (back-compat `.mcp.json` already matching) | AT-022 (shared with AC-CC-3-g) | Claude Code |
| AC-NFR-11-a | When (isolation, same as AC-X-1) | AT-068, AT-069 | Cross-layer |
| AC-NFR-13-a | Ubiquitous (no event-type out of the four) | AT-070 (shared with AC-X-2) | Cross-layer |
| AC-NFR-13-b | When (exactly one calibration event per run) | AT-039 (shared with AC-CS-4b-2) | Codespaces |
| AC-NFR-14 | Ubiquitous (combined FR-4a + Q-CS-1b ≤ 150 ms p95) | AT-079 | Codespaces |
| AC-NFR-15 | Alias for AC-X-3 | AT-071 (shared with AC-X-3) | Claude Code |
| **Cross-Workflow SHA-Pin Symmetry (auditor-surfaced, Blueprint §SHA-pinning commitment)** | | | |
| (SHA-pin byte-identity across FR-4c and FR-5 workflows) | Ubiquitous (invariant across two YAML files) | AT-080 | CI/CD |

**Coverage check:** 51 distinct ACs (after collapsing alias AC-NFR-15 → AC-X-3); 80 test IDs (AT-001 through AT-080); every AC has ≥ 1 mapped test. Shared tests (e.g., AT-007 covers both AC-CC-1-g and AC-NFR-5-a's FR-1 facet) are explicitly noted; no AC is left uncovered. AT-080 covers the Blueprint's cross-workflow SHA-pin symmetry commitment (previously surfaced under Open Coverage Gaps item 7 in v1.0.0; promoted to an explicit AT in v1.0.1 per the cross-artifact auditor's I-CA-007 recommendation).

---

## Test Suite Overview

By **type**:

| Type | Count | Examples |
|---|---|---|
| Unit-style fixture test (Python script + JSON fixtures) | 34 | AT-001..AT-008, AT-009..AT-015, AT-016..AT-027, AT-064..AT-067, AT-071, AT-080 |
| Devcontainer-rebuild integration test (real shell, fixture environment) | 18 | AT-028..AT-037, AT-068..AT-070, AT-072..AT-074, AT-077..AT-079 |
| Calibration-script behavioral test (real `npm install` in scratch dir) | 7 | AT-038..AT-044 |
| GitHub Actions integration test (`workflow_dispatch` + fixture PR + cron observation) | 18 | AT-045..AT-062 |
| Cross-cutting aggregator test (assembles findings from multiple mechanisms) | 3 | AT-063, AT-075, AT-076, AT-078 |

By **layer of verification**:

| Layer | Test Count |
|---|---|
| Claude Code (orchestrator + auditing-shared + auditing-mcp + Issues/) | 36 |
| Codespaces (devcontainer rebuild + calibration script + staleness banner) | 25 |
| CI/CD (two workflow files + cross-workflow SHA-pin symmetry) | 19 |

By **fixture posture**:

- **Real artifacts, no mocks** — every test uses real `.mcp.json`, real reviewer-output JSON, real `postCreate.sh`, real `claude --bare -p` invocations, real `npm install -g`. The Blueprint's §Test Boundaries §Mock Boundary Decisions table commits to no mocking; this test plan enforces that.
- **Constructed fixtures** — pre-feature `checkpoint.json` (AT-015), broken-static-shape environment fixtures (AT-028..AT-031), broken-contract pin fixtures (AT-038, AT-043), stale `mcp-events.jsonl` fixtures (AT-072..AT-074).
- **Pre-merge `workflow_dispatch` validation** — three runs each for FR-4c and FR-5 per Blueprint §Verification Strategy / D-0010 (AT-050, AT-061).

---

## Test Specifications

Each test specifies: **Maps to AC**, **Type**, **Layer**, **Preconditions**, **Test steps (AAA)**, **Expected outcome**, **Negative-path companion** (when applicable), **Data dependencies**, **Determinism notes**.

---

### FR-1 — Verdict-vs-findings parity validator

#### AT-001 — Validator is invoked after every reviewer-output write
- **Maps to AC:** AC-CC-1-a
- **Type:** Integration (orchestrator-level pipeline trace)
- **Layer:** Claude Code
- **Preconditions:** Orchestrator wired to invoke `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` at each of the 9 reviewer-completion invocation sites enumerated in Blueprint v1 §Main Components (FR-1 wire-in). A trace facility (state-transitions log or wrapper assertion) records each invocation.
- **Test steps:**
  1. **Arrange:** Stage a feature pipeline run such that each of the 5 reviewer-shaped agents completes once across 9 invocation sites; configure the wrapper to log `(site, agent_name, output_path)` tuples for every invocation of `verdict_findings_parity.py`.
  2. **Act:** Run the orchestrator end-to-end against a known-good fixture pipeline.
  3. **Assert:** The wrapper log records exactly 9 invocations; each invocation precedes the orchestrator's "advance to next stage" log line for the same stage; each invocation's `output_path` argument is a real file on disk written by the reviewer immediately prior.
- **Expected outcome:** Validator invoked exactly once per reviewer-completion site before orchestrator advance; no advance-before-validate gaps.
- **Data dependencies:** Fixture pipeline run with 9 distinct reviewer completions; orchestrator wrapper log.
- **Determinism notes:** The 9-site count is set by Blueprint v1; if scope sweep adds sites in a future revision the test's expected count must be updated in lockstep.

#### AT-002 — Approving verdict + BLOCKER finding → exit 1
- **Maps to AC:** AC-CC-1-b
- **Type:** Unit-style fixture (Python + JSON)
- **Layer:** Claude Code
- **Preconditions:** `verdict_findings_parity.py` exists; fixture file `tests/fixtures/fr-1/reviewer-approve-with-blocker.json` contains a real-shape reviewer output with `verdict: "pass"` and a findings array containing one finding with `severity: "BLOCKER"`.
- **Test steps:**
  1. **Arrange:** Stage the fixture file at a known path; choose an agent name in the approving-verdict-enum-bearing set (e.g., `review-architecture-auditor`).
  2. **Act:** Invoke `python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py <fixture-path> <agent-name>`.
  3. **Assert:** Process exit code equals 1; stdout JSON contains `mechanism: "FR-1"`, names the agent, lists the BLOCKER finding's `file_path` and `message`, and includes a remedial-action hint.
- **Expected outcome:** Exit 1; structured JSON diagnostic naming reviewer, verdict, and offending finding(s).
- **Negative-path companion:** AT-004 (the pass-through case).
- **Data dependencies:** `tests/fixtures/fr-1/reviewer-approve-with-blocker.json`.
- **Determinism notes:** Fixture is byte-stable; no time-of-day or randomness in the validator path.

#### AT-003 — Multiple BLOCKER findings all named in diagnostic
- **Maps to AC:** AC-CC-1-b (companion: completeness of the offending-findings list)
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Fixture `tests/fixtures/fr-1/reviewer-approve-with-three-blockers.json` has `verdict: "pass"` and three findings each with `severity: "BLOCKER"`.
- **Test steps:**
  1. **Arrange:** Stage fixture.
  2. **Act:** Invoke `verdict_findings_parity.py` against the fixture.
  3. **Assert:** Exit 1; diagnostic enumerates all three offending findings (by `file_path` and `message`), not just the first.
- **Expected outcome:** All BLOCKER findings present in diagnostic.
- **Data dependencies:** `tests/fixtures/fr-1/reviewer-approve-with-three-blockers.json`.
- **Determinism notes:** Deterministic given fixture.

#### AT-004 — Approving verdict + no BLOCKER → exit 0, pass-through
- **Maps to AC:** AC-CC-1-c, AC-CC-1-d
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Fixture `tests/fixtures/fr-1/reviewer-approve-clean.json` has `verdict: "pass"` and findings array `[]` (or only MAJOR/MINOR/NIT).
- **Test steps:**
  1. **Arrange:** Stage a clean-approve fixture; stage a second fixture with `verdict: "pass"` + a single `severity: "MAJOR"` finding.
  2. **Act:** Invoke validator against each.
  3. **Assert:** Both invocations return exit 0; stdout JSON indicates pass-through; the fixture content is not modified.
- **Expected outcome:** Exit 0; no rejection; input file untouched.
- **Data dependencies:** Two fixtures (`reviewer-approve-clean.json`, `reviewer-approve-with-major.json`).
- **Determinism notes:** Deterministic.

#### AT-005 — Validator internal error → exit 2 fail-closed
- **Maps to AC:** AC-CC-1-e, AC-NFR-6-a (FR-1 facet)
- **Type:** Unit-style fixture (corrupt input)
- **Layer:** Claude Code
- **Preconditions:** Fixture `tests/fixtures/fr-1/reviewer-malformed.json` is intentionally invalid JSON (e.g., truncated mid-object).
- **Test steps:**
  1. **Arrange:** Stage the malformed fixture.
  2. **Act:** Invoke `verdict_findings_parity.py <fixture> <agent-name>`; capture stdout, stderr, exit code.
  3. **Assert:** Exit code equals 2; stderr names the parse failure; orchestrator wrapper (when present) treats the run as failed-closed and does not advance.
- **Expected outcome:** Exit 2; failed-closed; user-resolution required before retry.
- **Data dependencies:** `tests/fixtures/fr-1/reviewer-malformed.json`.
- **Determinism notes:** Deterministic; relies on Python `json.load` raising on the truncated input.

#### AT-006 — Validator JSON output carries the four FR-6 fields
- **Maps to AC:** AC-CC-1-f
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** A failure-case fixture (reuse AT-002's input).
- **Test steps:**
  1. **Arrange:** Stage `reviewer-approve-with-blocker.json`.
  2. **Act:** Invoke validator; parse stdout JSON.
  3. **Assert:** JSON object has all four FR-6 fields populated with non-empty strings: `mechanism` (== `"FR-1"`), `offending_artifact_path` (== fixture path), `rule_violated` (names the verdict-vs-findings contract), `remedial_action_hint` (one line, ≤ 200 chars).
- **Expected outcome:** Four fields all present and non-empty.
- **Data dependencies:** Same as AT-002.
- **Determinism notes:** Deterministic.

#### AT-007 — Validator is deterministic across repeated invocations
- **Maps to AC:** AC-CC-1-g, AC-NFR-5-a (FR-1 facet)
- **Type:** Unit-style fixture (repeated invocation)
- **Layer:** Claude Code
- **Preconditions:** A fail-case fixture and a pass-case fixture.
- **Test steps:**
  1. **Arrange:** Stage both fixtures.
  2. **Act:** Invoke validator twice in succession on each fixture; capture stdout bytes and exit codes.
  3. **Assert:** For each fixture, both invocations produce byte-identical stdout and identical exit codes. No timestamp, randomness, or environment-dependence in output.
- **Expected outcome:** Byte-identical outputs; identical exit codes.
- **Data dependencies:** AT-002 fixture + AT-004 fixture.
- **Determinism notes:** This test IS the determinism check; if it fails the validator has non-deterministic content (e.g., embedded `time.time()` or randomized ordering).

#### AT-008 — Validator accepts prior-pipeline-conformant outputs (NFR-9 back-compat)
- **Maps to AC:** AC-CC-1-h, AC-NFR-9-a
- **Type:** Unit-style fixture (corpus sweep)
- **Layer:** Claude Code
- **Preconditions:** Corpus `tests/fixtures/fr-1/prior-conformant/` containing ≥ 10 real reviewer outputs harvested from prior approved pipeline runs (any verdict, no BLOCKER in findings — these are outputs the prior pipeline accepted).
- **Test steps:**
  1. **Arrange:** Snapshot real reviewer outputs from prior pipeline runs into the corpus (one file per output, original frontmatter preserved).
  2. **Act:** Iterate every file; invoke validator with the original agent name.
  3. **Assert:** Every invocation returns exit 0; no rejection.
- **Expected outcome:** All prior-conformant outputs continue to pass.
- **Data dependencies:** Snapshot corpus of prior-pipeline outputs.
- **Determinism notes:** Deterministic; if the corpus grows the test scales naturally.

---

### FR-2 — Orchestrator dispatch self-check

#### AT-009 — Self-check enumerates every stage's `execution_mode` after Stage 1
- **Maps to AC:** AC-CC-2-a
- **Type:** Integration (orchestrator trace)
- **Layer:** Claude Code
- **Preconditions:** Orchestrator wired with the dispatch self-check at `recipe-feature-pipeline/SKILL.md`; `intent-clarification.md` carries `scope_class` frontmatter; `checkpoint.json` is initialized with per-stage `execution_mode` fields per ADR-0057.
- **Test steps:**
  1. **Arrange:** Run a fresh pipeline through Stage 1 (Intent Clarification) only; instrument the orchestrator to log the self-check's read operations.
  2. **Act:** Orchestrator transitions from Stage 1 to dispatch.
  3. **Assert:** The trace contains exactly one read of `scope_class` from `intent-clarification.md` frontmatter and exactly one enumeration of every stage's `checkpoint.execution_mode` value; the enumeration completes before any Stage 2+ agent is dispatched.
- **Expected outcome:** Self-check fires once after Stage 1; reads documented inputs only.
- **Data dependencies:** Fresh fixture intent-clarification.md + fresh checkpoint.json.
- **Determinism notes:** Deterministic given seeded inputs.

#### AT-010 — FULL scope + `parent-driven-workaround` → dispatch refused
- **Maps to AC:** AC-CC-2-b
- **Type:** Integration (orchestrator-level)
- **Layer:** Claude Code
- **Preconditions:** Fixture `tests/fixtures/fr-2/full-with-parent-driven-checkpoint.json` has `scope_class: "FULL"` in the intent-clarification frontmatter AND at least one stage with `checkpoint.execution_mode: "parent-driven-workaround"`.
- **Test steps:**
  1. **Arrange:** Stage the FULL-scope intent-clarification + the parent-driven checkpoint; clear any leftover dispatch state.
  2. **Act:** Run the orchestrator; observe dispatch step.
  3. **Assert:** Orchestrator refuses to enter dispatch loop; emits a structured JSON diagnostic to stdout naming the offending stage (its position and name) and the configuration (`execution_mode: "parent-driven-workaround"`). No Stage 2+ agent is dispatched.
- **Expected outcome:** Refusal; diagnostic; no per-stage agent invoked.
- **Negative-path companion:** AT-011 (MINOR/PATCH permitted case).
- **Data dependencies:** Fixture intent-clarification + checkpoint.
- **Determinism notes:** Deterministic.

#### AT-011 — MINOR / PATCH scope permits `parent-driven-workaround`
- **Maps to AC:** AC-CC-2-c
- **Type:** Integration (orchestrator-level)
- **Layer:** Claude Code
- **Preconditions:** Two fixture pairs: MINOR-scope intent-clarification + parent-driven checkpoint; PATCH-scope variant.
- **Test steps:**
  1. **Arrange:** Stage MINOR fixture pair.
  2. **Act:** Run orchestrator through dispatch self-check.
  3. **Assert:** Orchestrator does not refuse; dispatch proceeds; no FR-2 diagnostic emitted.
  4. Repeat (2)-(3) with the PATCH variant; same expected result.
- **Expected outcome:** Both variants permitted; no refusal.
- **Data dependencies:** Two scope-class variant fixtures.
- **Determinism notes:** Deterministic.

#### AT-012 — Refusal diagnostic carries the four FR-6 fields
- **Maps to AC:** AC-CC-2-d
- **Type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Same fixture as AT-010.
- **Test steps:**
  1. **Arrange:** Stage AT-010 fixture pair.
  2. **Act:** Run orchestrator; capture refusal stdout.
  3. **Assert:** JSON diagnostic has the four FR-6 fields: `mechanism` (== `"FR-2"`), `offending_artifact_paths` (array containing both `intent-clarification.md` and `checkpoint.json`), `rule_violated` (FULL-scope-with-fallback rule), `remedial_action_hint`.
- **Expected outcome:** All four fields present.
- **Data dependencies:** AT-010 fixture pair.
- **Determinism notes:** Deterministic.

#### AT-013 — Self-check is deterministic
- **Maps to AC:** AC-CC-2-e, AC-NFR-5-a (FR-2 facet)
- **Type:** Integration (repeated invocation)
- **Layer:** Claude Code
- **Preconditions:** A pass-case fixture pair (e.g., MINOR + parent-driven) and a refuse-case fixture pair (FULL + parent-driven).
- **Test steps:**
  1. **Arrange:** Stage both pairs.
  2. **Act:** Invoke the orchestrator dispatch self-check twice against each pair (using a wrapper that exposes the self-check's structured output deterministically).
  3. **Assert:** Per pair, both invocations produce identical verdict (pass/refusal) and byte-identical diagnostic when failing.
- **Expected outcome:** Identical outputs across repeated invocations.
- **Data dependencies:** AT-010 and AT-011 fixtures.
- **Determinism notes:** This test is the determinism check.

#### AT-014 — Missing or unparseable `intent-clarification.md` → fail-closed
- **Maps to AC:** AC-CC-2-f, AC-NFR-6-a (FR-2 facet)
- **Type:** Integration (negative-path)
- **Layer:** Claude Code
- **Preconditions:** A fixture set where `intent-clarification.md` is either missing or contains malformed YAML frontmatter.
- **Test steps:**
  1. **Arrange:** Stage the missing-file variant; separately stage the malformed-frontmatter variant.
  2. **Act:** Run the orchestrator through dispatch self-check.
  3. **Assert:** Both variants cause the orchestrator to halt with a fail-closed diagnostic naming the missing-or-unparseable file path and the parse error; the orchestrator does NOT proceed past the self-check.
- **Expected outcome:** Fail-closed; diagnostic; no advancement.
- **Data dependencies:** Two error fixtures.
- **Determinism notes:** Deterministic; relies on YAML parser raising on bad input.

#### AT-015 — Pre-feature checkpoint resume (migration smoke per ADR-0057)
- **Maps to AC:** AC-CC-2-g
- **Type:** Integration (migration scenario)
- **Layer:** Claude Code
- **Preconditions:** Fixture `tests/fixtures/fr-2/pre-feature-checkpoint.json` is a real checkpoint authored BEFORE this feature shipped (specifically before ADR-0057 introduced the `execution_mode` field) — therefore the field is absent on every stage entry. `intent-clarification.md` carries `scope_class: "FULL"`.
- **Test steps:**
  1. **Arrange:** Stage the pre-feature checkpoint and the FULL-scope intent-clarification.
  2. **Act:** Run the orchestrator's dispatch self-check.
  3. **Assert:** The self-check treats the absent `execution_mode` as the documented default `"specialist-dispatch"` per ADR-0057's absence-default rule. Because no stage carries `parent-driven-workaround`, dispatch proceeds without refusal.
- **Expected outcome:** Pre-feature checkpoint resumes successfully; absence-default honored.
- **Data dependencies:** Pre-feature checkpoint fixture (real artifact harvested from the working tree before T1.1 lands).
- **Determinism notes:** Deterministic; the absence-default rule is constant.

---

### FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule OP-11

#### AT-016 — OP-11 iterates every `.mcp.json` server entry
- **Maps to AC:** AC-CC-3-a
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` exists; fixture `.mcp.json` with N servers (N=6 to mirror current repo state).
- **Test steps:**
  1. **Arrange:** Stage fixture `.mcp.json` (6 servers) + fixture ADR-0041 with row 71 and row 70 carrying `[DEPRECATED INVOCATION FORM]` annotations.
  2. **Act:** Invoke `audit_op11_adr_parity.py <fixture-mcp> <fixture-adr>`.
  3. **Assert:** Script's structured stdout records `servers_checked: 6`; each server appears in the per-server processing log (visible via `--verbose` if supported, or via stderr trace).
- **Expected outcome:** All N=6 servers iterated; correspondence located in ADR-0041 for every non-deprecated row.
- **Data dependencies:** Fixture `.mcp.json` + annotated fixture ADR-0041.
- **Determinism notes:** Deterministic.

#### AT-017 — Invocation-form mismatch → BLOCKER finding with diff dimension
- **Maps to AC:** AC-CC-3-b
- **Type:** Unit-style fixture (drift simulation)
- **Layer:** Claude Code
- **Preconditions:** Fixture `.mcp.json` where one server's `args` differ from the ADR-0041 prescribed form (e.g., GitNexus invocation lists `--bare` when ADR-0041 omits it).
- **Test steps:**
  1. **Arrange:** Stage a fixture where exactly one server has drifted argv.
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit code 1; findings array contains exactly one finding with `rule: "OP-11"`, `severity: "BLOCKER"`, `server: <name>`, `field: argv` (or `env`/`sentinel` per drift kind), `prescribed_form`, `live_form`, and a remedial-action hint.
- **Expected outcome:** Single BLOCKER finding; named diff dimension.
- **Negative-path companion:** AT-022 (no drift → no finding).
- **Data dependencies:** Drift fixture.
- **Determinism notes:** Deterministic.

#### AT-018 — Server in `.mcp.json` absent from ADR-0041 → BLOCKER (`missing-in-adr-0041`)
- **Maps to AC:** AC-CC-3-c
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Fixture `.mcp.json` lists a server name with NO matching non-deprecated row in fixture ADR-0041.
- **Test steps:**
  1. **Arrange:** Stage the mismatch fixture pair.
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit 1; finding carries `field: missing-in-adr-0041`, names the server, and exits non-zero.
- **Expected outcome:** BLOCKER with the named `field`.
- **Data dependencies:** Mismatch fixture pair.
- **Determinism notes:** Deterministic.

#### AT-019 — Non-deprecated ADR-0041 row absent from `.mcp.json` → BLOCKER (`missing-in-mcp.json`)
- **Maps to AC:** AC-CC-3-d
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Fixture ADR-0041 contains a non-deprecated row for a server not present in fixture `.mcp.json`.
- **Test steps:**
  1. **Arrange:** Stage the mismatch fixture pair.
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit 1; finding carries `field: missing-in-mcp.json`, names the server.
- **Expected outcome:** BLOCKER with the named `field`.
- **Data dependencies:** Reverse-direction mismatch fixture.
- **Determinism notes:** Deterministic.

#### AT-020 — Deprecated ADR row + absent from `.mcp.json` → NO finding (suppressed)
- **Maps to AC:** AC-CC-3-e
- **Type:** Unit-style fixture (real-world current state)
- **Layer:** Claude Code
- **Preconditions:** Fixture ADR-0041 with row 71 (mcp-openapi-schema) carrying `[DEPRECATED INVOCATION FORM]` annotation; fixture `.mcp.json` does NOT list `mcp-openapi-schema` (real current state per 2026-05-24 removal).
- **Test steps:**
  1. **Arrange:** Stage the live current-state fixture pair.
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit 0; no finding emitted for the deprecated row; findings array empty (or contains only findings from other unrelated drift).
- **Expected outcome:** No false positive; deprecated row suppressed.
- **Data dependencies:** Real-state fixtures.
- **Determinism notes:** Deterministic; this test verifies the v2.1 row-70 + row-71 day-one false-positive pre-emption.

#### AT-021 — Deprecated ADR row + server STILL present in `.mcp.json` → BLOCKER (`deprecated-row-still-present`)
- **Maps to AC:** AC-CC-3-f
- **Type:** Unit-style fixture (regression simulation)
- **Layer:** Claude Code
- **Preconditions:** Fixture ADR-0041 has row 71 marked `[DEPRECATED]` AND fixture `.mcp.json` contains the deprecated server.
- **Test steps:**
  1. **Arrange:** Stage the regression fixture pair (simulating a future commit that re-added the deprecated server).
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit 1; finding carries `field: deprecated-row-still-present`, names the server, emits BLOCKER.
- **Expected outcome:** Regression caught.
- **Data dependencies:** Regression fixture.
- **Determinism notes:** Deterministic.

#### AT-022 — Matched `.mcp.json` entries produce no finding (NFR-10 back-compat)
- **Maps to AC:** AC-CC-3-g, AC-NFR-10-a
- **Type:** Unit-style fixture (live current state)
- **Layer:** Claude Code
- **Preconditions:** Fixture pair is the live `.mcp.json` + live ADR-0041 with row 70 and row 71 annotated `[DEPRECATED]`.
- **Test steps:**
  1. **Arrange:** Copy live `.mcp.json` and live annotated ADR-0041 into a fixture directory.
  2. **Act:** Invoke OP-11.
  3. **Assert:** Exit 0; findings array empty; `servers_checked` equals the live server count (6).
- **Expected outcome:** Clean current state; zero findings.
- **Data dependencies:** Live-snapshot fixture pair.
- **Determinism notes:** Deterministic; this is the day-one clean-pass check.

#### AT-023 — Each OP-11 finding carries the four FR-6 fields
- **Maps to AC:** AC-CC-3-h
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Any fail-case fixture (AT-017, AT-018, AT-019, or AT-021).
- **Test steps:**
  1. **Arrange:** Stage AT-017 fixture.
  2. **Act:** Invoke OP-11; parse JSON stdout.
  3. **Assert:** Each finding object has `mechanism` (== `"FR-3"` or `"OP-11"`), `offending_artifact_path` (== `.mcp.json` or ADR path), `rule_violated`, `remedial_action_hint`.
- **Expected outcome:** Four-field invariant holds per finding.
- **Data dependencies:** AT-017 fixture.
- **Determinism notes:** Deterministic.

#### AT-024 — OP-11 is deterministic
- **Maps to AC:** AC-CC-3-i, AC-NFR-5-a (FR-3 facet)
- **Type:** Unit-style fixture (repeated invocation)
- **Layer:** Claude Code
- **Preconditions:** Any fixture pair (pass-case + fail-case).
- **Test steps:**
  1. **Arrange:** Stage both pass and fail fixtures.
  2. **Act:** Invoke OP-11 twice on each.
  3. **Assert:** Byte-identical stdout per fixture across repeated invocations; identical exit codes.
- **Expected outcome:** Byte-identical outputs.
- **Data dependencies:** AT-022 (pass) + AT-017 (fail).
- **Determinism notes:** This IS the determinism check.

#### AT-025 — OP-11 treats `${VAR}` as opaque tokens (NFR-7 / NFR-8 no env reads)
- **Maps to AC:** AC-CC-3-j, AC-NFR-7-a (FR-3 facet), AC-NFR-8-a (FR-3 facet)
- **Type:** Unit-style fixture + environment audit
- **Layer:** Claude Code
- **Preconditions:** Fixture pair carries `${SOME_TOKEN}` placeholders in both `.mcp.json` and ADR-0041 prescribed forms.
- **Test steps:**
  1. **Arrange:** Set `SOME_TOKEN` to a sentinel value in the calling environment (e.g., `SOME_TOKEN=must-not-leak-into-output`); stage the fixture pair.
  2. **Act:** Invoke OP-11; capture stdout AND stderr.
  3. **Assert:** Neither stdout nor stderr contains the string `must-not-leak-into-output`; the `${SOME_TOKEN}` literal appears verbatim in any canonicalization output; OP-11's code path does not call `os.environ` or `os.getenv` on the placeholder (verifiable via static inspection or `strace`/`audit_op*.py` test mode).
- **Expected outcome:** No env-var values leak; canonicalization treats `${VAR}` as opaque.
- **Data dependencies:** Token-bearing fixture.
- **Determinism notes:** Deterministic.

#### AT-026 — Parse failure on `.mcp.json` or ADR-0041 → exit 2 fail-closed
- **Maps to AC:** AC-CC-3-k, AC-NFR-6-a (FR-3 facet)
- **Type:** Unit-style fixture (corrupt input)
- **Layer:** Claude Code
- **Preconditions:** Two error fixtures — corrupt `.mcp.json` (truncated JSON) and corrupt ADR-0041 (table-extractor-defying markdown).
- **Test steps:**
  1. **Arrange:** Stage each error fixture separately.
  2. **Act:** Invoke OP-11 against each.
  3. **Assert:** Exit code 2 in both cases; stderr names the parse failure (file path + parse error class).
- **Expected outcome:** Exit 2 on either parse failure; no silent pass.
- **Data dependencies:** Two corrupt fixtures.
- **Determinism notes:** Deterministic.

#### AT-027 — OP-11 does NOT write to `mcp-events.jsonl`
- **Maps to AC:** AC-CC-3-l, AC-NFR-13-a (FR-3 facet)
- **Type:** Unit-style fixture + file-system observation
- **Layer:** Claude Code
- **Preconditions:** Any OP-11 invocation; `.claude/runtime/mcp-events.jsonl` initialized empty.
- **Test steps:**
  1. **Arrange:** Snapshot `.claude/runtime/mcp-events.jsonl` byte-content (empty initial).
  2. **Act:** Invoke OP-11 against any fixture (pass or fail).
  3. **Assert:** `.claude/runtime/mcp-events.jsonl` byte-content is unchanged; no append occurred.
- **Expected outcome:** Event surface untouched by OP-11.
- **Data dependencies:** Initialized empty event log.
- **Determinism notes:** Deterministic.

---

### FR-4a — GitNexus per-rebuild static-shape check

#### AT-028 — A1 assertion: `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` unset or wrong → fail
- **Maps to AC:** AC-CS-4a-1 (A1 fan-out), AC-CS-4a-3
- **Type:** Devcontainer-rebuild integration (fixture-broken environment)
- **Layer:** Codespaces
- **Preconditions:** A fixture devcontainer environment where the `versions.env` line setting `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is removed or set to a value other than `1`.
- **Test steps:**
  1. **Arrange:** In a fresh codespace OR a devcontainer-rebuild simulation, override `.devcontainer/versions.env` to remove the A1 export (or set it to `0`).
  2. **Act:** Trigger a devcontainer rebuild (`postCreate.sh` runs).
  3. **Assert:** `postCreate.sh` halts at the FR-4a block (before `install_gitnexus` runs); a `structured_failure` event is appended to `.claude/runtime/mcp-events.jsonl` with `note:` carrying the four FR-6 elements and `rule_violated == "signal-a1-env-var-unset-or-wrong"`; stderr carries the same message in plain text; `install_gitnexus` is NOT invoked (no GitNexus install attempt).
- **Expected outcome:** Fail-closed before install; event recorded; install bypassed.
- **Data dependencies:** Override `versions.env`.
- **Determinism notes:** Deterministic.

#### AT-029 — A2 assertion: malformed `$GITNEXUS_TAG` → fail
- **Maps to AC:** AC-CS-4a-1 (A2 fan-out), AC-CS-4a-3
- **Type:** Devcontainer-rebuild integration
- **Layer:** Codespaces
- **Preconditions:** Fixture environment where `$GITNEXUS_TAG` is set to a value that fails the semver/tag regex `^v?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$` (e.g., `main`, `latest`, `1.6`).
- **Test steps:**
  1. **Arrange:** Override `GITNEXUS_TAG=main` in `versions.env`.
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** Halt at FR-4a block; `structured_failure` event carries `rule_violated == "signal-a2-tag-pin-malformed"`; install bypassed.
- **Expected outcome:** Fail-closed on malformed pin.
- **Data dependencies:** Override `versions.env`.
- **Determinism notes:** Deterministic.

#### AT-030 — A3 assertion: `$GITNEXUS_TAG` ≠ `versions.env` value → fail
- **Maps to AC:** AC-CS-4a-1 (A3 fan-out), AC-CS-4a-3
- **Type:** Devcontainer-rebuild integration
- **Layer:** Codespaces
- **Preconditions:** Fixture environment where `$GITNEXUS_TAG` is exported in the shell but its value differs from the value declared in `.devcontainer/versions.env`.
- **Test steps:**
  1. **Arrange:** In a fresh rebuild, export `GITNEXUS_TAG=1.6.4` before `postCreate.sh` runs, while `versions.env` declares `GITNEXUS_TAG=1.6.5`.
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** Halt at FR-4a block; `structured_failure` event carries `rule_violated == "signal-a3-versions-env-mismatch"`.
- **Expected outcome:** Source-of-truth divergence caught.
- **Data dependencies:** Mismatched env override.
- **Determinism notes:** Deterministic.

#### AT-031 — A4 assertion: `npm root -g` empty or unwritable parent → fail
- **Maps to AC:** AC-CS-4a-1 (A4 fan-out), AC-CS-4a-3
- **Type:** Devcontainer-rebuild integration
- **Layer:** Codespaces
- **Preconditions:** Fixture environment where `npm root -g` returns empty OR its parent directory is non-writable (e.g., chmod 0500 simulated).
- **Test steps:**
  1. **Arrange:** Simulate broken `npm` configuration (e.g., shadow `npm` with a stub that prints nothing on `root -g`).
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** Halt at FR-4a block; `structured_failure` event carries `rule_violated == "signal-a4-artifact-paths-unpredictable"`.
- **Expected outcome:** Path-predictability assertion caught.
- **Data dependencies:** Stub `npm` shim.
- **Determinism notes:** Deterministic.

#### AT-032 — FR-4a runs on both cache-hit and cache-miss devcontainer rebuilds
- **Maps to AC:** AC-CS-4a-2
- **Type:** Devcontainer-rebuild integration (two-rebuild sequence)
- **Layer:** Codespaces
- **Preconditions:** A clean devcontainer.
- **Test steps:**
  1. **Arrange:** Discard any existing devcontainer image cache.
  2. **Act:** Rebuild devcontainer (cache-miss); observe FR-4a block executes; then trigger a second rebuild without touching the image (cache-hit); observe FR-4a block executes again.
  3. **Assert:** Both rebuilds run the FR-4a check; the check's behavior is identical (no `npm install -g` invocation; the check never has cache-vs-no-cache divergence).
- **Expected outcome:** FR-4a fires twice; identical behavior.
- **Data dependencies:** None beyond a clean devcontainer.
- **Determinism notes:** Deterministic given fixed rebuild semantics.

#### AT-033 — FR-4a failure halts `postCreate.sh` via `set -euo pipefail`
- **Maps to AC:** AC-CS-4a-3, AC-NFR-6-a (FR-4a facet)
- **Type:** Devcontainer-rebuild integration
- **Layer:** Codespaces
- **Preconditions:** Any fixture from AT-028..AT-031.
- **Test steps:**
  1. **Arrange:** Stage AT-028 fixture.
  2. **Act:** Trigger rebuild; capture `postCreate.sh` exit code and any subsequent lifecycle hook output.
  3. **Assert:** `postCreate.sh` exits non-zero at the FR-4a block; subsequent in-script statements after FR-4a (including `install_gitnexus`) are not executed; the failure surface is NOT masked by `|| emit_degraded_banner` (the FR-4a block is at the top-level, not inside a function).
- **Expected outcome:** Hard halt; no install attempt; no `emit_degraded_banner` masking.
- **Data dependencies:** AT-028 fixture.
- **Determinism notes:** Deterministic.

#### AT-034 — FR-4a does NOT assert on `tree-sitter-swift`
- **Maps to AC:** AC-CS-4a-4
- **Type:** Static-inspection unit test
- **Layer:** Codespaces
- **Preconditions:** The completed `postCreate.sh` (with FR-4a block).
- **Test steps:**
  1. **Arrange:** Read the FR-4a block.
  2. **Act:** Grep the block for any reference to `swift` (case-insensitive) or `tree-sitter-swift`.
  3. **Assert:** No matches in the FR-4a block; only `dart` and `proto` (and only via the FR-4b script, not FR-4a) appear in the calibration context.
- **Expected outcome:** No Swift assertion.
- **Data dependencies:** None.
- **Determinism notes:** Deterministic; static grep.

#### AT-035 — FR-4a creates no sentinel file
- **Maps to AC:** AC-CS-4a-5
- **Type:** Devcontainer-rebuild + filesystem observation
- **Layer:** Codespaces
- **Preconditions:** A clean rebuild trigger.
- **Test steps:**
  1. **Arrange:** Snapshot `.claude/runtime/` directory contents before rebuild.
  2. **Act:** Trigger a clean rebuild (FR-4a passes).
  3. **Assert:** `.claude/runtime/` gains no new sentinel-shaped file authored by FR-4a (the only writes are pre-existing convention sentinels from `install_*` functions and any `mcp-events.jsonl` append from the FR-4a fail-path or other emissions — confirmed by tagging the FR-4a code with a sentinel-absence assertion).
- **Expected outcome:** FR-4a sentinel-less.
- **Data dependencies:** Filesystem snapshot.
- **Determinism notes:** Deterministic.

#### AT-036 — FR-4a p95 latency under 100 ms with no network access
- **Maps to AC:** AC-CS-4a-6, AC-NFR-3-a
- **Type:** Devcontainer-rebuild benchmark (10 consecutive rebuilds) + network observation
- **Layer:** Codespaces
- **Preconditions:** A `hostRequirements.cpus: 4` codespace; timing instrumentation around the FR-4a block; network observation (e.g., `tcpdump` on lo + eth0 or `iptables` counters).
- **Test steps:**
  1. **Arrange:** Configure timing via `EPOCHREALTIME` capture immediately before and after the FR-4a block; instrument a network observer to count packets sent during the block.
  2. **Act:** Trigger 10 consecutive devcontainer rebuilds.
  3. **Assert:** Across 10 rebuilds, p95 wall-clock for FR-4a < 100 ms; network observer reports zero packets sent during the FR-4a block window.
- **Expected outcome:** p95 < 100 ms; zero network access.
- **Data dependencies:** Timing + network observers.
- **Determinism notes:** Variance from `npm root -g` system-call latency may push individual rebuilds; p95 is the gating metric per the AC.

#### AT-037 — FR-4a failing diagnostic carries the four FR-6 fields
- **Maps to AC:** AC-CS-4a-7
- **Type:** Devcontainer-rebuild + event inspection
- **Layer:** Codespaces
- **Preconditions:** Any AT-028..AT-031 fixture.
- **Test steps:**
  1. **Arrange:** Stage AT-028 fixture (signal-a1 fail).
  2. **Act:** Trigger rebuild; capture stderr plain-text echo + `mcp-events.jsonl` `structured_failure` event.
  3. **Assert:** Both surfaces (plain text + structured event `note:` field) name: `mechanism == "FR-4a"`, offending artifact (`$GITNEXUS_SKIP_OPTIONAL_GRAMMARS`), rule (`signal-a1-env-var-unset-or-wrong`), remedial hint. Same for AT-029 (a2), AT-030 (a3), AT-031 (a4) — parameterized.
- **Expected outcome:** Four FR-6 fields present on every signal-N failure.
- **Data dependencies:** Each of AT-028..AT-031 fixtures.
- **Determinism notes:** Deterministic.

---

### FR-4b — GitNexus opt-in behavioral calibration script

#### AT-038 — Full calibration contract: read pin, scratch install, signals, event, cleanup
- **Maps to AC:** AC-CS-4b-1
- **Type:** Calibration-script behavioral test
- **Layer:** Codespaces
- **Preconditions:** Network access to npm registry; `gitnexus@1.6.5` available; `.devcontainer/versions.env` declares `GITNEXUS_TAG=1.6.5`; the calibration script exists.
- **Test steps:**
  1. **Arrange:** Snapshot `.claude/runtime/mcp-events.jsonl` byte-content; verify no scratch directories under `/tmp`.
  2. **Act:** Invoke `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`.
  3. **Assert:** Script reads `GITNEXUS_TAG` from `versions.env`; creates a scratch directory via `mktemp -d`; runs `npm install -g gitnexus@1.6.5` with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` and stderr captured; asserts Signal 1 (stderr matches `\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)` for each of dart and proto); asserts Signal 3 (artifact paths absent under scratch prefix for both grammars); runs negative-assertion confirmation in a second scratch dir with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0` (artifacts MUST be built); appends exactly one `calibration_result` event to `mcp-events.jsonl`; cleans up scratch directories before exit.
- **Expected outcome:** Exit 0; one event appended; scratch dirs removed.
- **Data dependencies:** Network egress.
- **Determinism notes:** Determinism depends on upstream npm registry; this test treats `gitnexus@1.6.5` as a fixed pin. If the npm tarball is unavailable, the test marks itself blocked rather than failing.

#### AT-039 — Exactly one `calibration_result` event per run regardless of outcome
- **Maps to AC:** AC-CS-4b-2, AC-NFR-13-b
- **Type:** Calibration-script behavioral test (matrix)
- **Layer:** Codespaces
- **Preconditions:** Calibration script exists; ability to fixture a broken-contract pin (e.g., a hypothetical tag where Signal 1 regex fails — implemented by intercepting stderr).
- **Test steps:**
  1. **Arrange:** Stage three scenarios — pass (real `gitnexus@1.6.5`); fail (intercepted stderr removing the Skipping-build line); drift_detected (intercepted to fail Signal 3 only). Snapshot `mcp-events.jsonl` line count before each invocation.
  2. **Act:** Run the script three times, once per scenario.
  3. **Assert:** Each invocation appends exactly one new `calibration_result` event to `mcp-events.jsonl`; `outcome:` field equals `pass`, `fail`, `drift_detected` respectively; exit code is 0, non-zero, non-zero respectively.
- **Expected outcome:** One event per run; outcome reflects scenario; exit code is the secondary channel.
- **Data dependencies:** Stderr-interception fixtures.
- **Determinism notes:** Deterministic given fixture interception.

#### AT-040 — Calibration script NOT invoked from `postCreate.sh`
- **Maps to AC:** AC-CS-4b-3
- **Type:** Static-inspection unit test
- **Layer:** Codespaces
- **Preconditions:** Completed `postCreate.sh`.
- **Test steps:**
  1. **Arrange:** Read `postCreate.sh`.
  2. **Act:** Grep for any reference to `calibrate-gitnexus-grammar-skip` or to the script's path under `.devcontainer/scripts/`.
  3. **Assert:** No invocation of the script appears in any code path of `postCreate.sh` (mentions in comments are acceptable; actual calls are not).
- **Expected outcome:** Zero invocations from `postCreate.sh`.
- **Data dependencies:** None.
- **Determinism notes:** Deterministic; static grep.

#### AT-041 — Calibration does NOT assert on Swift
- **Maps to AC:** AC-CS-4b-4
- **Type:** Static-inspection unit test
- **Layer:** Codespaces
- **Preconditions:** The calibration script.
- **Test steps:**
  1. **Arrange:** Read `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`.
  2. **Act:** Grep for `swift` (case-insensitive).
  3. **Assert:** No matches in any active assertion (matches in `# comment` clarifications are acceptable).
- **Expected outcome:** No Swift assertion.
- **Data dependencies:** None.
- **Determinism notes:** Deterministic.

#### AT-042 — `calibration_result` event conforms to ADR-0058 canonical payload shape
- **Maps to AC:** AC-CS-4b-5
- **Type:** Calibration-script behavioral test + schema-validation
- **Layer:** Codespaces
- **Preconditions:** OP-7 schema validator extended to admit `calibration_result` per Plan task 12; ADR-0058's documented payload shape.
- **Test steps:**
  1. **Arrange:** Run AT-038 once successfully.
  2. **Act:** Extract the appended `calibration_result` event; validate against ADR-0058's payload schema (event, timestamp, server, mechanism, version, duration_ms, outcome ∈ {pass, fail, drift_detected}, signals, note).
  3. **Assert:** All required fields present; `mechanism == "fr-4b-gitnexus-grammar-skip"`; `server == "gitnexus"`; `outcome` is one of the three permitted values; `signals` is a map; `timestamp` is ISO 8601; OP-7 validator returns no findings.
- **Expected outcome:** Event passes ADR-0058 + OP-7 validation.
- **Data dependencies:** Live event from AT-038; ADR-0058; OP-7 validator.
- **Determinism notes:** Deterministic.

#### AT-043 — Failing/drift_detected outcome surfaces the FR-6 four fields
- **Maps to AC:** AC-CS-4b-6
- **Type:** Calibration-script behavioral test (fault injection)
- **Layer:** Codespaces
- **Preconditions:** Stderr-interception fixture to induce Signal 1 failure.
- **Test steps:**
  1. **Arrange:** Configure interception to drop the Skipping-build lines.
  2. **Act:** Invoke script.
  3. **Assert:** Script's stderr names: mechanism (`FR-4b`), offending artifact (the pinned `GITNEXUS_TAG=1.6.5`), rule (failing Signal name, e.g., `Signal-1`), remedial hint. The `calibration_result` event's `note:` field carries the same four elements.
- **Expected outcome:** Both stderr and event note carry four FR-6 fields.
- **Data dependencies:** Stderr-interception fixture.
- **Determinism notes:** Deterministic given fixture.

#### AT-044 — Calibration completes within 60 seconds wall-clock (informational)
- **Maps to AC:** AC-CS-4b-7
- **Type:** Calibration-script behavioral test (timing)
- **Layer:** Codespaces
- **Preconditions:** Network access; clean scratch directories.
- **Test steps:**
  1. **Arrange:** Capture wall-clock start.
  2. **Act:** Run the script end-to-end.
  3. **Assert:** Wall-clock duration < 60 seconds on the maintainer's laptop OR on the `ubuntu-latest` runner. Note: this is informational; the load-bearing budget is FR-4c's NFR-4 5-minute per-workflow ceiling.
- **Expected outcome:** Sub-60 s on the maintainer's hardware.
- **Data dependencies:** Wall-clock instrumentation.
- **Determinism notes:** Variance is acceptable; the threshold is informational. If the test environment's network is slow this becomes a flake source — mitigated by running in CI on a stable runner.

---

### FR-4c — GitHub Actions workflow driving FR-4b

#### AT-045 — Weekly cron trigger fires and surfaces script exit code
- **Maps to AC:** AC-CICD-4c-1
- **Type:** GitHub Actions integration (cron observation)
- **Layer:** CI/CD
- **Preconditions:** Workflow `.github/workflows/gitnexus-grammar-skip-calibration.yml` deployed on the default branch with `schedule: '0 7 * * 1'`.
- **Test steps:**
  1. **Arrange:** Wait for the first Monday 07:00 UTC after merge; record the GitHub Actions run UI for the workflow.
  2. **Act:** Observe the cron-triggered run.
  3. **Assert:** A workflow run with `event_name: schedule` exists; the run invokes `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` inside the devcontainer image (built via `devcontainers/ci@<SHA>`); the workflow job's conclusion equals the script's exit code's pass/fail mapping (success ↔ exit 0).
- **Expected outcome:** Cron-triggered run exists; exit code surfaced.
- **Data dependencies:** First post-merge Monday 07:00 UTC cron tick observation; or `workflow_dispatch` simulation against draft branch for pre-merge confidence.
- **Determinism notes:** First cron observation is one-shot; the test treats AT-049's `workflow_dispatch` parity as proxy evidence during pre-merge.

#### AT-046 — `pull_request` on `versions.env` OR calibration-script path triggers workflow
- **Maps to AC:** AC-CICD-4c-2
- **Type:** GitHub Actions integration (fixture PR)
- **Layer:** CI/CD
- **Preconditions:** Workflow merged.
- **Test steps:**
  1. **Arrange:** Open two fixture PRs — one bumps `GITNEXUS_TAG` in `.devcontainer/versions.env`; the other edits a comment in `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`.
  2. **Act:** Observe Actions UI per PR.
  3. **Assert:** Each PR triggers the FR-4c workflow; the workflow runs the calibration script; the job's conclusion equals the script's exit code's mapping.
- **Expected outcome:** Both PRs trigger the workflow.
- **Data dependencies:** Two fixture PR drafts.
- **Determinism notes:** Deterministic given workflow paths-filter.

#### AT-047 — Non-zero script exit surfaces FR-6 diagnostic in `$GITHUB_STEP_SUMMARY`
- **Maps to AC:** AC-CICD-4c-3
- **Type:** GitHub Actions integration (fail simulation)
- **Layer:** CI/CD
- **Preconditions:** Ability to inject a failing calibration outcome (e.g., via a draft branch where the script is patched to exit 1 unconditionally).
- **Test steps:**
  1. **Arrange:** Push a draft branch where the calibration script exits 1; open a PR or run `workflow_dispatch`.
  2. **Act:** Workflow runs; capture the `$GITHUB_STEP_SUMMARY` Markdown block.
  3. **Assert:** Job's conclusion is `failure`; `$GITHUB_STEP_SUMMARY` carries a Markdown block naming: mechanism (`FR-4c calibration CI wiring`), calibration script path, offending grammar, failing Signal-N (extracted from script stdout), remedial hint.
- **Expected outcome:** Fail surfaces with the four FR-6 fields.
- **Data dependencies:** Draft branch with patched calibration script.
- **Determinism notes:** Deterministic.

#### AT-048 — Routine PR not touching the two paths does NOT trigger the workflow
- **Maps to AC:** AC-CICD-4c-4
- **Type:** GitHub Actions integration (negative-path)
- **Layer:** CI/CD
- **Preconditions:** Workflow merged.
- **Test steps:**
  1. **Arrange:** Open a fixture PR that modifies a file outside `.devcontainer/versions.env` and outside `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (e.g., a doc-only change to `README.md`).
  2. **Act:** Observe Actions UI.
  3. **Assert:** No FR-4c workflow run is triggered for this PR; only the FR-5 workflow (if its trigger fires) or no FR-* workflow at all runs.
- **Expected outcome:** No spurious calibration runs.
- **Data dependencies:** Off-path fixture PR.
- **Determinism notes:** Deterministic.

#### AT-049 — `workflow_dispatch` parity with cron path
- **Maps to AC:** AC-CICD-4c-5
- **Type:** GitHub Actions integration (manual trigger)
- **Layer:** CI/CD
- **Preconditions:** Workflow merged.
- **Test steps:**
  1. **Arrange:** Navigate to Actions UI; select the calibration workflow.
  2. **Act:** Run `workflow_dispatch` against the default branch.
  3. **Assert:** The run invokes the same calibration script as the cron path; the exit code is surfaced as job status; the run is indistinguishable from a cron-triggered run except for `event_name`.
- **Expected outcome:** Manual trigger behaves identically to cron.
- **Data dependencies:** Manual UI action.
- **Determinism notes:** Deterministic.

#### AT-050 — Workflow completes within 5 minutes (NFR-4-b) with p95 under 2 minutes
- **Maps to AC:** AC-CICD-4c-6, AC-NFR-4-b
- **Type:** GitHub Actions integration (three `workflow_dispatch` runs)
- **Layer:** CI/CD
- **Preconditions:** Pre-merge validation gate per Blueprint §Verification Strategy + cicd-design v0.3.0 §D-0010.
- **Test steps:**
  1. **Arrange:** Push the draft branch to `origin`.
  2. **Act:** Trigger three `workflow_dispatch` runs of the FR-4c workflow on the draft branch.
  3. **Assert:** All three runs complete in under 5 minutes (NFR-4 ceiling); p95 (the slower of run 2 and run 3, or the slowest of the three) is under 2 minutes per cicd-design v0.3.0 commitment.
- **Expected outcome:** Hard cap 5 min met; p95 ≤ 2 min target met.
- **Data dependencies:** Pre-merge draft branch + three runs.
- **Determinism notes:** Variance from `devcontainers/ci` image-build dominates; first run typically cold-cache (heavier); runs 2-3 warm-cache.

#### AT-051 — Concurrency group `gitnexus-calibration` with `cancel-in-progress: false`
- **Maps to AC:** AC-CICD-4c-7
- **Type:** GitHub Actions integration (concurrency observation)
- **Layer:** CI/CD
- **Preconditions:** Workflow merged.
- **Test steps:**
  1. **Arrange:** Stage two trigger events to fire near-simultaneously (e.g., the cron tick aligns with an open `versions.env` PR).
  2. **Act:** Observe Actions UI.
  3. **Assert:** Both triggers result in workflow runs; the second run queues (does not cancel the first); neither emits a duplicate `calibration_result` event (verified by inspecting `mcp-events.jsonl` after both runs complete).
- **Expected outcome:** Queueing, not cancellation; no duplicate events.
- **Data dependencies:** Staged near-simultaneous triggers.
- **Determinism notes:** Timing-sensitive; the `cancel-in-progress: false` setting governs the behavior; if the test cannot reliably stage near-simultaneous triggers it falls back to static-inspecting the workflow YAML for the concurrency declaration.

#### AT-052 — Workflow declares `permissions: contents: read` only; no new secrets read
- **Maps to AC:** AC-CICD-4c-8, AC-NFR-7-a (FR-4c facet)
- **Type:** Static-inspection unit test
- **Layer:** CI/CD
- **Preconditions:** Workflow file exists.
- **Test steps:**
  1. **Arrange:** Read `.github/workflows/gitnexus-grammar-skip-calibration.yml`.
  2. **Act:** Parse YAML; inspect `permissions:` block; inspect for any `secrets.*` interpolation in `run:` steps.
  3. **Assert:** `permissions: { contents: read }` declared at workflow level (or job level with no broader grants); no `secrets.*` references in any step; `actionlint` reports no security findings.
- **Expected outcome:** Least-privilege; no new credential surface.
- **Data dependencies:** None beyond the workflow YAML.
- **Determinism notes:** Deterministic.

#### AT-053 — Workflow consumes script exit code only (no Signal-N reimplementation)
- **Maps to AC:** AC-CICD-4c-9
- **Type:** Static-inspection unit test
- **Layer:** CI/CD
- **Preconditions:** Workflow file exists.
- **Test steps:**
  1. **Arrange:** Read the workflow file.
  2. **Act:** Grep for any Signal-1 / Signal-3 regex literals, any `[tree-sitter-` substring, or any artifact-path stat-style logic in `run:` blocks.
  3. **Assert:** No matches; the workflow's `run:` blocks invoke the script and check `$?` only.
- **Expected outcome:** Single-source-of-truth preserved.
- **Data dependencies:** None.
- **Determinism notes:** Deterministic.

#### AT-054 — Workflow does NOT write to `mcp-events.jsonl`
- **Maps to AC:** AC-CICD-4c-10
- **Type:** GitHub Actions integration + filesystem observation
- **Layer:** CI/CD
- **Preconditions:** Workflow merged.
- **Test steps:**
  1. **Arrange:** Snapshot the `mcp-events.jsonl` line count inside the devcontainer at the start of the workflow run (via an instrumentation step).
  2. **Act:** Run the workflow (any trigger).
  3. **Assert:** After the script completes, `mcp-events.jsonl` line count grew by exactly 1 (the script's event); the workflow's `run:` steps appended nothing additional.
- **Expected outcome:** Exactly one event written, by the script only.
- **Data dependencies:** Instrumentation step in the workflow (test-only).
- **Determinism notes:** Deterministic.

#### AT-055 — Workflow declares `timeout-minutes: 5`
- **Maps to AC:** AC-CICD-4c-11
- **Type:** Static-inspection unit test
- **Layer:** CI/CD
- **Preconditions:** Workflow file exists.
- **Test steps:**
  1. **Arrange:** Read workflow YAML.
  2. **Act:** Parse for `timeout-minutes:`.
  3. **Assert:** `timeout-minutes: 5` declared at the job level.
- **Expected outcome:** Hard timeout declared.
- **Data dependencies:** None.
- **Determinism notes:** Deterministic.

---

### FR-5 — MCP connectivity smoke workflow

#### AT-056 — Path-trigger fires on `.mcp.json`, devcontainer, audit skill, ADR-0041 PRs
- **Maps to AC:** AC-CICD-5-a
- **Type:** GitHub Actions integration (four fixture PRs)
- **Layer:** CI/CD
- **Preconditions:** `mcp-connectivity-smoke.yml` merged.
- **Test steps:**
  1. **Arrange:** Open four fixture PRs — one per path-trigger entry: `.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**`.
  2. **Act:** Observe Actions UI per PR.
  3. **Assert:** Each PR triggers the FR-5 workflow.
- **Expected outcome:** All four paths trigger.
- **Data dependencies:** Four fixture PRs.
- **Determinism notes:** Deterministic.

#### AT-057 — Non-connected server → workflow fails with FR-6 diagnostic
- **Maps to AC:** AC-CICD-5-b
- **Type:** GitHub Actions integration (fault injection)
- **Layer:** CI/CD
- **Preconditions:** Ability to push a draft branch where one MCP server is broken (e.g., bad argv that prevents connection).
- **Test steps:**
  1. **Arrange:** On a draft branch, intentionally break one server's `.mcp.json` entry.
  2. **Act:** Open the fixture PR (or trigger `workflow_dispatch`).
  3. **Assert:** Workflow job concludes `failure`; `$GITHUB_STEP_SUMMARY` carries a Markdown block naming the offending server(s) + their reported status + the four FR-6 fields.
- **Expected outcome:** Fail with diagnostic.
- **Data dependencies:** Draft branch with broken server.
- **Determinism notes:** Deterministic.

#### AT-058 — All connected → workflow passes with confirmation in summary
- **Maps to AC:** AC-CICD-5-c
- **Type:** GitHub Actions integration (clean PR)
- **Layer:** CI/CD
- **Preconditions:** Live `.mcp.json` with all 6 servers connected.
- **Test steps:**
  1. **Arrange:** Open a fixture PR touching `.mcp.json` cosmetically (e.g., whitespace).
  2. **Act:** Observe workflow run.
  3. **Assert:** Job concludes `success`; `$GITHUB_STEP_SUMMARY` carries a one-line confirmation `"all 6 servers connected"`.
- **Expected outcome:** Pass + confirmation.
- **Data dependencies:** Cosmetic-change fixture PR.
- **Determinism notes:** Deterministic given current MCP server health.

#### AT-059 — CLI itself fails → workflow exits 2 (internal-error distinguishable from fail)
- **Maps to AC:** AC-CICD-5-d, AC-NFR-6-a (FR-5 facet)
- **Type:** GitHub Actions integration (CLI fault injection)
- **Layer:** CI/CD
- **Preconditions:** Ability to stub `claude` CLI to exit non-zero on `--bare -p`.
- **Test steps:**
  1. **Arrange:** In a draft branch, shadow `claude` in the devcontainer image with a stub that exits 1.
  2. **Act:** Run the FR-5 workflow.
  3. **Assert:** Workflow step exits 2 (distinguishable from AT-057's exit 1); `$GITHUB_STEP_SUMMARY` names the internal-error category.
- **Expected outcome:** Exit 2; internal-error category distinct.
- **Data dependencies:** Stub `claude` in draft branch.
- **Determinism notes:** Deterministic.

#### AT-060 — Failing summary carries the four FR-6 fields
- **Maps to AC:** AC-CICD-5-e
- **Type:** GitHub Actions integration
- **Layer:** CI/CD
- **Preconditions:** AT-057 fault-injection branch.
- **Test steps:**
  1. **Arrange:** Stage AT-057 fixture.
  2. **Act:** Observe failing `$GITHUB_STEP_SUMMARY`.
  3. **Assert:** Four FR-6 fields present: mechanism (`FR-5`), offending artifact (server name + `.mcp.json` path), rule violated (`server-status-not-connected`), remedial-action hint.
- **Expected outcome:** Four fields present.
- **Data dependencies:** AT-057 fixture.
- **Determinism notes:** Deterministic.

#### AT-061 — FR-5 completes within 5 minutes with p95 ≤ 4 min
- **Maps to AC:** AC-CICD-5-f, AC-NFR-4-a
- **Type:** GitHub Actions integration (three `workflow_dispatch` runs)
- **Layer:** CI/CD
- **Preconditions:** Pre-merge validation gate per Blueprint §Verification Strategy + cicd-design v0.3.0 §D-0010.
- **Test steps:**
  1. **Arrange:** Push draft branch.
  2. **Act:** Trigger three `workflow_dispatch` runs.
  3. **Assert:** All three under 5 minutes (NFR-4 ceiling); p95 ≤ 4 minutes per pre-merge target.
- **Expected outcome:** Hard cap met; p95 target met.
- **Data dependencies:** Pre-merge draft branch + three runs.
- **Determinism notes:** Variance from image-build cache state; first run cold-cache.

#### AT-062 — FR-5 introduces no new credential surface; no credential values in summary
- **Maps to AC:** AC-CICD-5-g, AC-NFR-7-a (FR-5 facet), AC-NFR-8-a (FR-5 facet)
- **Type:** Static-inspection + runtime observation
- **Layer:** CI/CD
- **Preconditions:** Workflow file.
- **Test steps:**
  1. **Arrange:** Read workflow YAML; grep for `secrets.`, `env.`, any token-shaped string.
  2. **Act:** Parse `permissions:` block; run AT-057 fail-case; capture `$GITHUB_STEP_SUMMARY` byte-content.
  3. **Assert:** `permissions: contents: read` only; no `secrets.*` reference; summary contains no string matching credential-shape regexes (`AKIA`, `ghp_`, `sk_`, JWT 3-segment base64).
- **Expected outcome:** No credentials anywhere.
- **Data dependencies:** Workflow YAML + AT-057 fail-case.
- **Determinism notes:** Deterministic.

---

### Cross-workflow SHA-pin symmetry (FR-4c ↔ FR-5)

#### AT-080 — `actions/checkout` and `devcontainers/ci` SHA pins are byte-identical across both workflows
- **Maps to AC:** Blueprint v2.2 §SHA-pinning commitment (cross-workflow invariant for FR-4c and FR-5); promoted from Open Coverage Gap item 7 in v1.0.0 to an explicit AT per cross-artifact auditor recommendation I-CA-007.
- **Type:** Unit-style static-inspection (YAML parse + byte-string comparison)
- **Layer:** CI/CD (cross-workflow)
- **Preconditions:** Both workflow files exist: `.github/workflows/gitnexus-grammar-skip-calibration.yml` (FR-4c) and `.github/workflows/mcp-connectivity-smoke.yml` (FR-5). Each declares at least one `uses:` line referencing `actions/checkout@<SHA>` and at least one `uses:` line referencing `devcontainers/ci@<SHA>` (per Blueprint's per-workflow SHA-pin requirement). `PyYAML` (or equivalent YAML parser) available in the test environment.
- **Test steps:**
  1. **Arrange:** Stage both live workflow files. Define the canonical action references the symmetry check covers: `actions/checkout` and `devcontainers/ci`.
  2. **Act:** For each workflow file:
     - Parse the YAML.
     - Walk every job's `steps[]` array.
     - For each step carrying a `uses:` field whose `<owner>/<repo>` prefix matches one of the canonical references, extract the SHA segment after `@` (anything matching `^[0-9a-f]{40}$`; non-SHA refs like `@v4` or `@main` are a separate failure surfaced by `actionlint`'s pin check and are NOT this test's scope).
     - Build a per-workflow map `{"actions/checkout": "<sha-or-None>", "devcontainers/ci": "<sha-or-None>"}`.
  3. **Assert (byte-identity):** For each canonical action reference:
     - If both workflows declare a pin: the two SHA strings are byte-identical (40-character lowercase hex equality).
     - If exactly one workflow declares a pin: the test fails naming which workflow is missing the action.
     - If neither workflow declares the pin: the test marks the reference as not-applicable for this pair (informational; not a failure — Blueprint only requires symmetry where the action is actually used).
  4. **Assert (diagnostic shape on failure):** A divergence emits a structured diagnostic naming: the action reference (`actions/checkout` or `devcontainers/ci`), the two workflow paths, the two extracted SHA strings (or `MISSING` sentinel), and a remedial-action hint (`"Update both workflows to the same pinned SHA"`).
- **Expected outcome:** For every canonical action used in either workflow, the SHA pins match byte-for-byte across both workflow files; divergence fails with a precise structured diagnostic.
- **Negative-path companion:** Implicit — a synthetic fixture pair in `tests/fixtures/cross-workflow/sha-divergent/` (one workflow pinned to SHA `aaaa…`, the other to SHA `bbbb…`) MAY be staged to verify the test itself fails when divergence is present; this confirms the assertion is load-bearing, not vacuous.
- **Data dependencies:** The two live workflow files (read directly from `.github/workflows/`); optional divergence fixture for assertion-load-bearing confirmation.
- **Determinism notes:** Deterministic. YAML parsing and 40-char hex comparison have no time-of-day, randomness, or environment dependence. Test is unit-style and runs in well under 1 s — the structural check executes in test-time rather than only at workflow-execution time, complementing PV-3's actionlint + per-workflow SHA-format check which validates each workflow in isolation but does not enforce cross-workflow byte-identity.

---

### FR-6 — Cross-cutting diagnostic discipline

#### AT-063 — Four-field invariant holds across every mechanism's blocking diagnostic
- **Maps to AC:** AC-6-a
- **Type:** Cross-cutting aggregator (samples diagnostics from FR-1, FR-2, FR-3, FR-4a, FR-4b, FR-4c, FR-5)
- **Layer:** Cross-cutting (Claude Code + Codespaces + CI/CD)
- **Preconditions:** Each mechanism's fail-case test has been run and produced a diagnostic surface (validator JSON, orchestrator JSON, OP-11 JSON, `structured_failure` event, `calibration_result` event with non-pass outcome, FR-5 `$GITHUB_STEP_SUMMARY`, FR-4c `$GITHUB_STEP_SUMMARY`).
- **Test steps:**
  1. **Arrange:** Collect representative blocking diagnostics from each mechanism (reuse outputs from AT-002, AT-010, AT-017, AT-028, AT-043, AT-047, AT-057).
  2. **Act:** Parse each diagnostic per its native surface (JSON, JSONL event, Markdown).
  3. **Assert:** Every diagnostic carries the four FR-6 fields — mechanism name (or FR-4 sub-mechanism label), offending artifact path, rule/contract violated, one-line remedial-action hint. The sub-mechanism labels for the FR-4 family are present (`FR-4a` / `FR-4b` / `FR-4c`) when those sub-mechanisms emit.
- **Expected outcome:** Universal four-field discipline.
- **Data dependencies:** Outputs from the seven enumerated tests.
- **Determinism notes:** Deterministic given upstream tests are deterministic.

---

### FR-7 — Deferral-register tightening

#### AT-064 — Row B-1 carries the canonical adoption parenthetical
- **Maps to AC:** AC-CC-7-a
- **Type:** Unit-style fixture (Markdown content inspection)
- **Layer:** Claude Code
- **Preconditions:** Deliverable-archive step has run; `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` is the live file.
- **Test steps:**
  1. **Arrange:** Read the register file at the deliverable-archive verification step.
  2. **Act:** Parse the table row for B-1.
  3. **Assert:** The Item-cell contains the parenthetical `*(ADOPTED 2026-MM-DD by pipeline-quickwins-hardening-r1 — see <link>)*` with date/slug/link tokens populated.
- **Expected outcome:** Canonical parenthetical present.
- **Data dependencies:** Live register file post-archive.
- **Determinism notes:** Deterministic.

#### AT-065 — Row H-4 carries the same canonical parenthetical
- **Maps to AC:** AC-CC-7-b
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Same as AT-064.
- **Test steps:**
  1. **Arrange:** Read the register file.
  2. **Act:** Parse the table row for H-4.
  3. **Assert:** Same parenthetical shape as B-1; date / slug / link tokens identical.
- **Expected outcome:** H-4 mirrors B-1.
- **Data dependencies:** Live register file post-archive.
- **Determinism notes:** Deterministic.

#### AT-066 — Mismatched or missing parenthetical → updated to canonical form
- **Maps to AC:** AC-CC-7-c
- **Type:** Unit-style fixture (regression detection)
- **Layer:** Claude Code
- **Preconditions:** A pre-deliverable-archive fixture where B-1 or H-4 has either no parenthetical or a divergent one (e.g., differing slug spelling).
- **Test steps:**
  1. **Arrange:** Stage the fixture register with intentional mismatch.
  2. **Act:** Run the deliverable-archive verify-and-tighten step (or the FR-7 update routine).
  3. **Assert:** Post-update register matches the canonical form; the offending row was updated, the other row was preserved.
- **Expected outcome:** Idempotent fix.
- **Data dependencies:** Pre-archive fixture register.
- **Determinism notes:** Deterministic.

#### AT-067 — Why-excluded / Re-examination / Forgetting-risk cells carry canonical post-adoption text
- **Maps to AC:** AC-CC-7-d
- **Type:** Unit-style fixture
- **Layer:** Claude Code
- **Preconditions:** Post-archive register.
- **Test steps:**
  1. **Arrange:** Read the register.
  2. **Act:** For each of B-1 and H-4, inspect the Why-excluded, Re-examination-trigger, and Forgetting-risk cells.
  3. **Assert:** Why-excluded contains "Now adopted: <summary>"; Re-examination-trigger contains "Adopted by pipeline-quickwins-hardening-r1."; Forgetting-risk contains "Resolved by adoption."
- **Expected outcome:** Three cells per row carry the canonical text.
- **Data dependencies:** Live post-archive register.
- **Determinism notes:** Deterministic.

---

### Cross-Layer / Operational ACs

#### AT-068 — Per-mechanism isolation across the five mechanisms (NFR-11)
- **Maps to AC:** AC-X-1 (cross-mechanism part), AC-NFR-11-a
- **Type:** Integration (five isolation scenarios)
- **Layer:** Cross-layer
- **Preconditions:** Per-mechanism toggle (e.g., a feature-flag or a temporary revert of one mechanism's wire-in).
- **Test steps:**
  1. **Arrange:** Build five workspaces. In each, one of the five mechanisms is enabled and the other four are disabled.
  2. **Act:** Run the canonical demonstration for the enabled mechanism (e.g., for FR-1, replay AT-002; for FR-3, replay AT-017; etc.).
  3. **Assert:** The enabled mechanism produces its expected behavior on its named failure mode; the four disabled mechanisms remain inert and do not interfere.
- **Expected outcome:** Each of the five works alone.
- **Data dependencies:** Five workspace fixtures.
- **Determinism notes:** Deterministic.

#### AT-069 — Per-sub-mechanism isolation within FR-4 family
- **Maps to AC:** AC-X-1 (intra-family part)
- **Type:** Integration (three intra-family isolation scenarios)
- **Layer:** Cross-layer (Codespaces + CI/CD)
- **Preconditions:** Per-sub-mechanism toggle.
- **Test steps:**
  1. **Arrange:** Three workspaces — (a) FR-4a only (script absent, workflow absent); (b) FR-4b only (script present, workflow absent, postCreate.sh has no FR-4a block); (c) FR-4c only (workflow present invokes script, but no postCreate.sh block).
  2. **Act:** Run each variant's canonical demonstration: (a) trigger devcontainer rebuild with broken env-var; (b) manually invoke calibration script; (c) trigger workflow.
  3. **Assert:** Each sub-mechanism produces its expected behavior independent of the others.
- **Expected outcome:** FR-4a/4b/4c are independently exercisable.
- **Data dependencies:** Three workspace fixtures.
- **Determinism notes:** Deterministic.

#### AT-070 — Event-type closed-enum holds at four values
- **Maps to AC:** AC-X-2, AC-NFR-13-a
- **Type:** Cross-cutting (event-surface audit)
- **Layer:** Cross-layer
- **Preconditions:** OP-7 schema validator extended per Plan task 12 to admit the four event types `install_complete`, `readiness_probe`, `structured_failure`, `calibration_result`.
- **Test steps:**
  1. **Arrange:** Snapshot the live `.claude/runtime/mcp-events.jsonl` and a representative post-run version (after FR-3 / FR-4 family / FR-5 mechanisms have all been exercised).
  2. **Act:** Run OP-7 schema validator against both snapshots; additionally grep for any `event:` field value not in the four-value set.
  3. **Assert:** OP-7 returns zero findings; grep finds no out-of-vocabulary event types.
- **Expected outcome:** Closed-enum invariant holds.
- **Data dependencies:** Pre/post event log snapshots; OP-7 validator.
- **Determinism notes:** Deterministic.

#### AT-071 — Seven sub-agents' MCP allowlists are byte-identical pre/post feature
- **Maps to AC:** AC-X-3, AC-NFR-15
- **Type:** Static-inspection (byte-comparison)
- **Layer:** Claude Code
- **Preconditions:** Snapshot of the seven sub-agents' frontmatter `tools:` blocks at feature-start commit.
- **Test steps:**
  1. **Arrange:** At pre-feature commit, snapshot the `tools:` allowlist of the seven sub-agents named in ADR-0040 (`discovery-codebase-researcher`, `review-architecture-auditor`, `design-cicd`, `design-codespaces`, `design-claude-code`, `discovery-external-researcher`, `design-iac`).
  2. **Act:** After feature-final commit, snapshot the same seven `tools:` blocks.
  3. **Assert:** Byte-identical for all seven; any byte-level diff fails the test.
- **Expected outcome:** No MCP allowlist mutation.
- **Data dependencies:** Two snapshots.
- **Determinism notes:** Deterministic.

#### AT-072 — Q-CS-1b staleness banner: NEVER RUN variant when no `calibration_result` event exists
- **Maps to AC:** AC-X-4 (NEVER RUN branch)
- **Type:** Devcontainer-rebuild integration (fixture-empty event log)
- **Layer:** Codespaces
- **Preconditions:** `.claude/runtime/mcp-events.jsonl` contains no `calibration_result` events (either empty or only the three pre-existing types).
- **Test steps:**
  1. **Arrange:** Reset `mcp-events.jsonl` to contain no `calibration_result` rows.
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** Stderr contains a single-line banner naming `FR-4b calibration: NEVER RUN` and the remedial hint pointing to `gh workflow run gitnexus-grammar-skip-calibration.yml`; banner does NOT cause `postCreate.sh` to fail; rebuild completes successfully.
- **Expected outcome:** NEVER RUN banner on stderr; rebuild continues.
- **Data dependencies:** Pre-populated empty-of-calibration event log.
- **Determinism notes:** Deterministic.

#### AT-073 — Q-CS-1b banner: STALE variant when most recent event is > 2 weeks old
- **Maps to AC:** AC-X-4 (STALE branch)
- **Type:** Devcontainer-rebuild integration (fixture-stale event log)
- **Layer:** Codespaces
- **Preconditions:** Constructed `mcp-events.jsonl` carrying a `calibration_result` event with `timestamp` set to 3 weeks ago.
- **Test steps:**
  1. **Arrange:** Append a `calibration_result` event with `timestamp: "2026-05-05T12:00:00Z"` (3 weeks before 2026-05-26) and `mechanism: "fr-4b-gitnexus-grammar-skip"`.
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** Stderr contains banner naming `STALE (last run 2026-05-05T12:00:00Z, >2w ago)` and remedial hint; rebuild succeeds.
- **Expected outcome:** STALE banner on stderr; rebuild continues.
- **Data dependencies:** Constructed stale-event fixture.
- **Determinism notes:** Banner threshold (2 weeks) is fixed; the test pegs "now" to 2026-05-26 by either running in CI on the day or by injecting a fake-`date` shim for the fixture rebuild.

#### AT-074 — Q-CS-1b banner: silent when most recent event is ≤ 2 weeks old
- **Maps to AC:** AC-X-4 (silent branch)
- **Type:** Devcontainer-rebuild integration
- **Layer:** Codespaces
- **Preconditions:** Constructed event log with a `calibration_result` event timestamped 1 week ago.
- **Test steps:**
  1. **Arrange:** Append `calibration_result` with `timestamp: "2026-05-19T12:00:00Z"` (1 week before 2026-05-26).
  2. **Act:** Trigger devcontainer rebuild.
  3. **Assert:** No stale-banner stderr line appears (silent path); rebuild succeeds.
- **Expected outcome:** Silent; no banner.
- **Data dependencies:** Constructed fresh-event fixture.
- **Determinism notes:** Same `date` discipline as AT-073.

---

### Non-Functional explicit ACs not already covered

#### AT-075 — FR-1 validator wall-clock per invocation under small-number-of-seconds (and p95 ≤ 250 ms target)
- **Maps to AC:** AC-NFR-1-a
- **Type:** Unit-style benchmark
- **Layer:** Claude Code
- **Preconditions:** Validator + a corpus of ≤ 100 KB reviewer outputs.
- **Test steps:**
  1. **Arrange:** Prepare ten representative reviewer-output JSON files of varying size (10 KB – 100 KB).
  2. **Act:** Invoke validator on each, capture wall-clock; repeat 10 invocations per file.
  3. **Assert:** All invocations complete in well under one second; p95 ≤ 250 ms per Blueprint NFR-1 concrete threshold.
- **Expected outcome:** Sub-second performance; p95 target met.
- **Data dependencies:** Reviewer-output corpus.
- **Determinism notes:** Some variance; p95 is the gating metric.

#### AT-076 — FR-2 self-check wall-clock under small-number-of-seconds (and p95 ≤ 100 ms target)
- **Maps to AC:** AC-NFR-2-a
- **Type:** Integration benchmark
- **Layer:** Claude Code
- **Preconditions:** Orchestrator instrumented to time the dispatch self-check.
- **Test steps:**
  1. **Arrange:** Time the self-check phase via wrappers around the orchestrator entry.
  2. **Act:** Run ten orchestrator starts; capture self-check wall-clock per run.
  3. **Assert:** All runs complete the self-check in well under one second; p95 ≤ 100 ms per Blueprint NFR-2.
- **Expected outcome:** Sub-second performance; p95 target met.
- **Data dependencies:** Timing wrappers.
- **Determinism notes:** Some variance.

#### AT-077 — Aggregate no-new-credential audit across all FR mechanisms
- **Maps to AC:** AC-NFR-7-a (aggregate)
- **Type:** Cross-cutting aggregator
- **Layer:** Cross-layer
- **Preconditions:** All mechanism artifacts merged.
- **Test steps:**
  1. **Arrange:** Enumerate every artifact this feature adds or modifies (the validator scripts, OP-11, postCreate.sh changes, calibration script, two workflows, ADRs, KB doc updates).
  2. **Act:** Grep each artifact for any credential-shape literal (AKIA, ghp_, sk_, JWT 3-segment base64, private-key PEM headers); inspect each workflow's `secrets.*` references.
  3. **Assert:** Zero matches; no new secret name introduced; no new `permissions:` write-scope granted.
- **Expected outcome:** No new credential surface anywhere.
- **Data dependencies:** Full artifact set at feature-final commit.
- **Determinism notes:** Deterministic.

#### AT-078 — No credential values appear in any diagnostic (NFR-8)
- **Maps to AC:** AC-NFR-8-a
- **Type:** Cross-cutting aggregator
- **Layer:** Cross-layer
- **Preconditions:** Each mechanism's fail-case diagnostic captured.
- **Test steps:**
  1. **Arrange:** Set environment variables that look like credential carriers (e.g., `FAKE_TOKEN=must-not-appear-in-diag-aaaa`).
  2. **Act:** Run AT-002, AT-010, AT-017, AT-028, AT-043, AT-047, AT-057 — exhibiting every fail-path diagnostic surface.
  3. **Assert:** None of the captured diagnostics (JSON, JSONL event, Markdown summary, plain-text stderr) contains the sentinel value `must-not-appear-in-diag-aaaa`. Env-var names may appear; values must not.
- **Expected outcome:** Names-not-values discipline holds.
- **Data dependencies:** Sentinel env values + each mechanism's fail-case test.
- **Determinism notes:** Deterministic.

#### AT-079 — Combined FR-4a + Q-CS-1b banner overhead p95 ≤ 150 ms (NFR-14)
- **Maps to AC:** AC-NFR-14
- **Type:** Devcontainer-rebuild benchmark
- **Layer:** Codespaces
- **Preconditions:** Live `postCreate.sh` carrying both the FR-4a block and the Q-CS-1b banner block; instrumentation that records wall-clock for both blocks separately and the sum.
- **Test steps:**
  1. **Arrange:** Configure timing markers immediately before FR-4a, between FR-4a and the banner block, and immediately after the banner block.
  2. **Act:** Trigger 10 consecutive devcontainer rebuilds on the `hostRequirements.cpus: 4` machine class.
  3. **Assert:** Across the 10 rebuilds: FR-4a block p95 < 100 ms; banner block p95 < 50 ms; combined p95 < 150 ms; no network packets observed during either block.
- **Expected outcome:** Combined overhead ≤ 150 ms p95; zero network access.
- **Data dependencies:** Timing markers; network observer.
- **Determinism notes:** Variance from `jq` startup; p95 is the gating metric.

---

## Test Infrastructure Required

### Frameworks and tooling

The codebase analysis confirms the project's convention is **no traditional unit-test framework** — each validator script is independently invocable and ships a sibling `smoke_test_*.py` (precedent: `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`). This test plan follows that convention:

| Layer | Tooling | Location |
|---|---|---|
| Claude Code (unit-style fixtures) | `python3` invocations of `verdict_findings_parity.py`, `audit_op11_adr_parity.py`; fixture JSON files; sibling `smoke_test_*.py` per validator | `.claude/skills/auditing-shared/scripts/` + `.claude/skills/auditing-mcp/scripts/` + `tests/fixtures/fr-1/`, `tests/fixtures/fr-2/`, `tests/fixtures/fr-3/` (NEW dirs under the project root) |
| Claude Code (integration / orchestrator trace) | Orchestrator instrumented via wrapper assertions; state-transitions log; checkpoint fixtures | `working/feature/<feature-slug>/tests/` for fixture artifacts |
| Codespaces (devcontainer rebuild) | Real `postCreate.sh`; fixture overrides of `versions.env`; constructed `mcp-events.jsonl` snapshots; `EPOCHREALTIME` timing; network observation via `iptables` / `tcpdump` (test-only) | `.devcontainer/` + `.claude/runtime/` + test-only timing scripts under `tests/codespaces/` |
| Codespaces (calibration script) | Real `bash` invocation; real `npm install -g gitnexus@1.6.5`; scratch dirs via `mktemp -d`; stderr interception fixtures for fault injection | `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` + fault-injection fixtures under `tests/fr-4b/` |
| CI/CD | Real GitHub Actions `workflow_dispatch`; fixture PRs; `actionlint` static linting; `$GITHUB_STEP_SUMMARY` capture | `.github/workflows/mcp-connectivity-smoke.yml` + `.github/workflows/gitnexus-grammar-skip-calibration.yml` + draft PRs |

### Fixtures required (new under `tests/fixtures/` or `working/feature/<feature-slug>/tests/`)

| Fixture | Purpose | Used by |
|---|---|---|
| `fr-1/reviewer-approve-with-blocker.json` | Approve verdict + BLOCKER finding | AT-002, AT-006 |
| `fr-1/reviewer-approve-with-three-blockers.json` | Multiple BLOCKER findings | AT-003 |
| `fr-1/reviewer-approve-clean.json` | Clean pass-through | AT-004 |
| `fr-1/reviewer-approve-with-major.json` | Major finding only (NFR-9 pass) | AT-004, AT-008 |
| `fr-1/reviewer-malformed.json` | Truncated JSON | AT-005 |
| `fr-1/prior-conformant/` | Snapshot corpus of prior-pipeline outputs | AT-008 |
| `fr-2/full-with-parent-driven-checkpoint.json` | FULL + parent-driven workaround | AT-010, AT-012, AT-013 |
| `fr-2/minor-with-parent-driven.json` | MINOR-scope permitted case | AT-011 |
| `fr-2/patch-with-parent-driven.json` | PATCH-scope permitted case | AT-011 |
| `fr-2/missing-intent.md` / `fr-2/malformed-intent.md` | Fail-closed scenarios | AT-014 |
| `fr-2/pre-feature-checkpoint.json` | Real pre-feature checkpoint (no `execution_mode`) | AT-015 |
| `fr-3/mcp-json-current.json` + `fr-3/adr-0041-annotated.md` | Live current state | AT-022, AT-024 |
| `fr-3/mcp-json-drift-argv.json` | Argv drift | AT-017, AT-023 |
| `fr-3/mcp-json-missing-in-adr.json` | Server not in ADR | AT-018 |
| `fr-3/adr-with-missing-in-mcp.md` | Non-deprecated ADR row not in `.mcp.json` | AT-019 |
| `fr-3/mcp-json-with-deprecated-server-still-present.json` | Regression simulation | AT-021 |
| `fr-3/mcp-json-truncated.json` / `fr-3/adr-0041-corrupted.md` | Parse failure | AT-026 |
| `fr-3/token-bearing-pair/` | `${VAR}` placeholder pair | AT-025 |
| FR-4a environment override fixtures (4 scenarios) | A1/A2/A3/A4 failure scenarios | AT-028..AT-031, AT-033, AT-037 |
| FR-4b stderr-interception fixtures (3 scenarios) | Pass / fail / drift_detected | AT-039, AT-043 |
| Q-CS-1b event-log fixtures (3 scenarios) | NEVER RUN / STALE / silent | AT-072, AT-073, AT-074 |
| FR-5 fault-injection branches (1 broken server, 1 stub `claude`) | Connectivity-fail and CLI-fail | AT-057, AT-059 |
| FR-4c failing-calibration-script branch | Workflow fail-surface | AT-047 |

### Required test environment

- A `hostRequirements.cpus: 4` codespace class for the FR-4a / NFR-14 timing benchmarks (AT-036, AT-079).
- Network egress to the npm registry for FR-4b calibration tests (AT-038, AT-039, AT-042, AT-044).
- GitHub Actions `ubuntu-latest` runner for FR-4c and FR-5 timing benchmarks (AT-050, AT-061).
- A test-mode `date` shim for the Q-CS-1b staleness fixtures (AT-073, AT-074).

### Plan task dependencies (gates this test plan)

- **Plan task T2.x** must land FR-4a block + Q-CS-1b banner in `postCreate.sh` before AT-028..AT-037, AT-072..AT-074, AT-079 can run.
- **Plan task 11** (KB doc updates for ADR-0058) must land before AT-042 can validate against the documented schema.
- **Plan task 12** (OP-7 schema extension for `calibration_result`) must land before AT-070 can validate the closed-enum invariant; without it AT-070 produces an OP-7 MAJOR finding for every FR-4b emission.

---

## CI Execution Plan

| Test class | Trigger | Frequency | Test IDs |
|---|---|---|---|
| Unit-style fixture (Python + JSON) — fast | PR (any) | Every push | AT-001..AT-008 (FR-1), AT-009..AT-015 (FR-2), AT-016..AT-027 (FR-3), AT-040, AT-041, AT-053, AT-055, AT-064..AT-067 (FR-7), AT-071 (allowlist diff), AT-077 (no-new-credentials), AT-078 (no-credential-values) |
| Static-inspection (grep / YAML parse) — fast | PR (any) | Every push | AT-034, AT-040, AT-041, AT-052, AT-053, AT-055, AT-062 (partial), AT-080 |
| Devcontainer-rebuild integration — slow | PR touching `.devcontainer/**` OR `.claude/runtime/**` | On-trigger only | AT-028..AT-037, AT-068, AT-069 (FR-4a parts), AT-072..AT-074, AT-079 |
| Calibration-script behavioral — slow | PR touching `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` OR `.devcontainer/versions.env`; weekly cron | On-trigger only | AT-038..AT-044 (run by the FR-4c workflow itself; the workflow IS the test surface) |
| GitHub Actions integration (workflow_dispatch + cron + fixture PRs) | Pre-merge validation gate (D-0010) + post-merge production | Pre-merge (three runs per workflow) + ongoing | AT-045..AT-062 |
| Cross-cutting aggregator — slow | Pre-merge gate | Once before merge | AT-063, AT-070 |
| Benchmarks (NFR-1, NFR-2, NFR-3, NFR-4, NFR-14) | Pre-merge gate + nightly | Pre-merge (three runs) + nightly | AT-036, AT-050, AT-061, AT-075, AT-076, AT-079 |

**Pre-merge gate (per Blueprint §Verification Strategy / D-0010):**

1. All unit-style and static-inspection tests pass on every push (target: < 30 s aggregate).
2. Devcontainer-rebuild integration tests pass once on the merge candidate.
3. Three `workflow_dispatch` runs of FR-5 (`mcp-connectivity-smoke.yml`) — all under 5 min; p95 ≤ 4 min.
4. Three `workflow_dispatch` runs of FR-4c (`gitnexus-grammar-skip-calibration.yml`) — all under 5 min; p95 ≤ 2 min.
5. Cross-cutting aggregator (AT-063, AT-070) green.
6. AT-071 (MCP allowlist byte-diff) green.

**Post-merge cadence:**

- FR-5 workflow runs on every qualifying PR (path-filtered).
- FR-4c workflow runs on every Monday 07:00 UTC cron + on every `versions.env`/calibration-script PR + on `workflow_dispatch`.
- AT-064..AT-067 (FR-7) verified once at deliverable-archive commit.

**Won't run in CI (one-shot validation):**

- AT-045 cron-tick observation requires real first-Monday observation post-merge; pre-merge is covered by `workflow_dispatch` parity (AT-049).
- AT-015 migration smoke is a manual one-shot verification with a checkpoint snapshot from before this feature shipped.

---

## Determinism and Isolation Commitments

Per Blueprint NFR-5 and AC-NFR-5-a:

1. **Repeated invocation invariant.** AT-007 (FR-1), AT-013 (FR-2), AT-024 (FR-3) are the load-bearing determinism checks for each validator; they require byte-identical stdout across repeated invocations on the same input. If a validator embeds `time.time()`, randomized dict iteration order, or environment-dependent output, these tests catch it.
2. **Fixture immutability.** Every fixture under `tests/fixtures/` is byte-stable; tests that mutate state (e.g., AT-066 register fix) operate on a copied fixture, never on the source.
3. **No network in determinism path.** FR-4a (AT-036) explicitly asserts zero network access; OP-11 (AT-025) does not read `os.environ`; the FR-1 / FR-2 validators do not touch the network at all.
4. **CI test isolation.** FR-4c (AT-051) and FR-5 are concurrency-grouped or trigger-isolated; their tests rely on workflow-level concurrency declarations rather than ad-hoc coordination.
5. **Time-sensitive tests.** AT-073 and AT-074 (staleness branches) depend on "now" relative to fixture timestamps. The test plan pegs "now" by either (a) running on a controlled date (2026-05-26 in CI), or (b) injecting a `date` shim. Variance avoided.

Per Blueprint NFR-11 / AC-NFR-11-a:

6. **Per-mechanism isolation.** AT-068 and AT-069 explicitly exercise each mechanism in isolation; if any mechanism silently couples to another (e.g., FR-2 reads a field FR-1 writes), these tests catch it.

Per Blueprint NFR-6 / AC-NFR-6-a:

7. **Fail-closed on internal error.** AT-005 (FR-1), AT-014 (FR-2), AT-026 (FR-3), AT-033 (FR-4a), AT-059 (FR-5) each exhibit an internal-error path and assert exit code 2 (or equivalent) and a non-silent diagnostic. No mechanism is permitted to silently pass on its own error.

---

## Open Coverage Gaps

The following observations are surfaced for the cross-artifact auditor and the orchestrator's awareness; they are NOT gaps in AC-to-test mapping (every AC has ≥ 1 test) but rather coverage caveats worth naming.

1. **AT-045 (cron first-tick observation) is a post-merge one-shot.** Pre-merge confidence comes from AT-049 (`workflow_dispatch` parity); the actual first-Monday cron tick can only be observed once after merge. If the cron expression `0 7 * * 1` is parsed wrong (e.g., DST shift, runner timezone confusion), AT-049 will not catch it but AT-045 will. Suggested follow-up: surface AT-045 as a manual deliverable-archive verification step.
2. **AT-044 (FR-4b sub-60-second informational budget) may flake on slow-network maintainer hardware.** The load-bearing budget is NFR-4-b (AT-050) for the CI workflow. AT-044's informational threshold is best-effort; suggest treating CI runner timing (via AT-050) as the canonical measurement.
3. **AT-070 (closed-enum invariant) depends on Plan task 12 (OP-7 schema extension).** Until that task lands, AT-070 will flag every FR-4b emission as a MAJOR finding. Plan task 12 is sequenced as a Plan dependency before AT-070 can be executed cleanly.
4. **AT-042 (`calibration_result` ADR-0058 conformance) depends on Plan task 11 (KB doc updates).** Without the KB updates, the schema reference for the validation is the ADR alone — sufficient for the test but reduces the "documented vocabulary" property the test indirectly verifies.
5. **AT-051 (concurrency observation) is timing-sensitive.** Real near-simultaneous trigger staging may be difficult; the fallback is static-inspection of the workflow YAML's `concurrency:` declaration. Both paths are acceptable; runtime observation is preferred when feasible.
6. **AT-008 (NFR-9 corpus sweep) coverage scales with corpus size.** A corpus of 10 prior-pipeline outputs is a minimum; richer coverage requires harvesting more historical outputs. Suggest growing the corpus opportunistically over time.
7. **Cross-workflow SHA-pinning symmetry — RESOLVED in v1.0.1 by AT-080.** The Blueprint's commitment to byte-identical SHA pinning across the two workflows (FR-4c `gitnexus-grammar-skip-calibration.yml` and FR-5 `mcp-connectivity-smoke.yml`) for `actions/checkout` and `devcontainers/ci` is now an explicit acceptance test (AT-080) rather than an open coverage gap. AT-080 is a static-inspection unit test that parses both workflow YAMLs and asserts byte-identity; it complements PV-3 §Operational checks (actionlint + per-workflow SHA-format check), which validates each workflow in isolation but does not enforce cross-workflow byte-identity. Per the cross-artifact auditor's I-CA-007 recommendation, AT-080 was added in v1.0.1 because byte-identity is a structural assertion that actionlint does not enforce and that benefits from executable test-time enforcement.
8. **AT-074 (silent branch) is implicitly a negative-coverage assertion.** It verifies that the banner does NOT fire on fresh events; a flaky banner that occasionally fires on fresh events would slip through if it fired during a different rebuild. Suggested follow-up: repeat AT-074 across three rebuilds for stability evidence.

These are surfaced for cross-artifact-audit visibility; none requires Blueprint revision.

---

## References

- **PRD:** `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` (v0.3.0).
- **Blueprint:** `working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md` (v2.2.0).
- **Plan:** `working/feature/pipeline-quickwins-hardening-r1/plan-v1.md` (v1.0.1).
- **Codebase analysis:** `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json`.
- **ADRs referenced:** ADR-0037 (v1.0.2), ADR-0040, ADR-0041 (with rows 70 + 71 `[DEPRECATED]`-annotated), ADR-0042, ADR-0043, ADR-0044, ADR-0056, ADR-0057 (v1.0.1), ADR-0058.
- **EARS discipline:** `.claude/skills/KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md`.
- **Test framework convention precedent:** `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`.
- **OP-rule script contract:** see codebase-analysis.json `conventions.auditing-mcp.script_contract` (exit 0/1/2 = no-findings/blocker/internal-error).
- **Severity taxonomy:** `KB-review-disciplines/references/severity-taxonomy.md` (BLOCKER / MAJOR / MINOR / NIT or INFO).
- **Predecessor test specs:** none — this is the first acceptance-tests document for this feature.
