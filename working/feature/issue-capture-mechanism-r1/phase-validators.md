---
id: PVALS-issue-capture-mechanism-r1
doc_type: phase-validators
version: 1.1.0
status: draft
feature_slug: issue-capture-mechanism-r1
derived_from: working/feature/issue-capture-mechanism-r1/plan-v2.md
prd_path: working/feature/issue-capture-mechanism-r1/prd-v2.md
blueprint_path: working/feature/issue-capture-mechanism-r1/blueprint-v3.md
generated: 2026-05-23T00:00:00Z
generated_by: test-phase-validator-author
phase_count: 8
validator_count: 8
parallel_sibling: test-acceptance-author (stage 10 parallel; AT-IDs not yet authored — references PRD ACs by AC-ID directly)
---

# Phase Validators: Issue-Capture Mechanism (Outside-the-Pipeline)

## Contents

- [Purpose](#purpose)
- [Validator overview and integration](#validator-overview-and-integration)
- [Severity policy](#severity-policy)
- [PV-0 — Baseline + structural-only setup](#pv-0--baseline--structural-only-setup)
- [PV-1 — Templates + structural spec (CC)](#pv-1--templates--structural-spec-cc)
- [PV-2 — Backend validator extension + path-prefix skip](#pv-2--backend-validator-extension--path-prefix-skip)
- [PV-3 — Migration of 4 Issues files + agent-roster-impact-matrix](#pv-3--migration-of-4-issues-files--agent-roster-impact-matrix)
- [PV-4 — CC layer: KB skills + agent + entry-point skill](#pv-4--cc-layer-kb-skills--agent--entry-point-skill)
- [PV-5 — CC layer: hook script + settings.json patch](#pv-5--cc-layer-hook-script--settingsjson-patch)
- [PV-6 — Cross-cutting handoff edits](#pv-6--cross-cutting-handoff-edits)
- [PV-7 — Rollout / verification + acceptance](#pv-7--rollout--verification--acceptance)
- [Cross-phase invariants](#cross-phase-invariants)
- [Validator dependency graph + parallelization](#validator-dependency-graph--parallelization)
- [Validator runbook (operator-facing)](#validator-runbook-operator-facing)
- [Cross-references](#cross-references)

---

## Purpose

This document operationalizes the per-phase **Exit Criteria** and **Phase Validator** anchors authored in `plan-v2.md` into a set of machine-checkable assertions with explicit severity rules. There is exactly one validator entry per Plan phase (PV-0..PV-7).

Each validator is a **gate between phases**: it must PASS before the next phase begins. The validators are distinct from acceptance tests:

| Surface | Owned by | Verifies |
|---|---|---|
| Phase Validators (this doc) | `test-phase-validator-author` | Whether a Plan phase has completed its Exit Criteria and is safe to leave |
| Acceptance Tests (`acceptance-tests.md`) | `test-acceptance-author` (parallel sibling) | Whether the feature satisfies the PRD/Blueprint Acceptance Criteria |

The two surfaces overlap at Phase 7 (the Plan-wide acceptance gate also runs acceptance tests as a sub-set of its checks), but the validators are scoped to **phase progress**, while the acceptance tests are scoped to **AC satisfaction**.

The load-bearing invariants this document enforces:

1. **NFR-8 backward compatibility** (PV-0 → PV-2 → PV-7): the validator regression diff against the Phase 0 baseline corpus MUST be empty.
2. **F-003 silent-drop avoidance** (PV-4): `.claude/agents/issue-capture-author.md` MUST NOT carry a `skills:` frontmatter field. This is the highest-priority validator assertion in the whole feature and is unambiguously BLOCKER.
3. **AC-FR-8-d migration scope** (PV-3): the Phase 3 commit-range diff MUST contain only the 5 expected file pairs and no other migrations.
4. **AC-FR-13 pipeline isolation** (cross-phase + PV-7): no pipeline agent under `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` may reference `KB-issue-capture` or `subagent_type: issue-capture-author`.

---

## Validator overview and integration

### When validators run

| Validator | When triggered | Triggering surface |
|---|---|---|
| PV-0 | Immediately after Phase 0 tasks T0.1..T0.5 complete | Manual + CI (pre-Phase-1 gate) |
| PV-1 | After Phase 1 tasks T1.1..T1.5 complete | `shared-document-reviewer` Gate 0 + grep checks |
| PV-2 | After Phase 2 tasks T2.1..T2.6 complete | CI (smoke test + regression diff) |
| PV-3 | After Phase 3 tasks T3.0..T3.8 complete | Git + validator-execution gate |
| PV-4 | After Phase 4 tasks T4.1..T4.5 complete | **Direct F-003 grep gate** + `auditing-{subagents,skills,cc-configs}` |
| PV-5 | After Phase 5 tasks T5.1..T5.7 complete | `shellcheck` + golden-file harness + `auditing-{hooks,settings}` |
| PV-6 | After Phase 6 tasks T6.1..T6.3 complete | `git diff` (additive-only assertion) |
| PV-7 | After Phase 7 tasks T7.1..T7.10 complete | Plan-wide acceptance gate (re-runs T7.4..T7.8) |

### Integration with CI / pre-merge gates / phase-quality-reviewer

- **Phase-quality-reviewer (execution-phase consumer):** the per-phase orchestrator runs the corresponding validator before declaring the phase "passed." Failed validators block phase advancement.
- **Pre-merge gates:** the auditing-* family (auditing-{hooks, skills, subagents, settings, cc-configs}) provides the platform-level pre-merge check. Validators here cite the corresponding auditing-* check where one exists.
- **CI-automatable surface:** every validator entry below names the concrete command (grep / shellcheck / pytest / git diff / json-diff / python harness) that the CI hook runs. The validator script(s) live as a downstream task in the task DAG (out of scope for this document; this document specifies the assertions, not their implementation).

---

## Severity policy

Every validator assertion carries one of three severity values. The rules are uniform across all 8 validators.

| Severity | Behavior on failure | Examples |
|---|---|---|
| **BLOCKER** | Phase MUST NOT be marked complete; the next phase MUST NOT start. No documented-rationale override permitted. | F-003 `skills:`-absence (PV-4); NFR-8 empty-diff (PV-2/PV-7); AC-FR-8-d scope (PV-3); pipeline-isolation grep (PV-7) |
| **MAJOR** | Phase SHOULD NOT be marked complete; advancement permitted only with an explicit documented rationale recorded as an Issues-ledger entry (`I-PV-NNN`) and user-visible warning. | Missing optional workflow step (T4.4b/c); single non-BLOCKER auditing-* finding |
| **MINOR** | Informational. Recorded in the validator output but does not block advancement. | Cosmetic spec drift; docstring missing on a setup-only artifact |

**Severity hygiene constraint** (per the `test-phase-validator-author` discipline): the load-bearing check of each phase MUST be BLOCKER. The load-bearing checks per phase are explicitly enumerated at the top of each validator entry.

**Failure response (default):** when a validator fails, the orchestrator surfaces the failing assertion(s) to the user and references the Plan's per-phase rollback path. Per-phase failure responses are documented at the foot of each validator entry below.

---

## PV-0 — Baseline + structural-only setup

- **Validator ID:** `PV-0`
- **Phase reference:** Plan Phase 0 — Baseline + structural-only setup (plan-v2.md §Phase 0)
- **Validator goal:** Prove that the three load-bearing baselines (validator findings, pipeline-isolation grep, cc-critique health) have been captured before any behavior change, and that no validator code has been edited yet.
- **Load-bearing assertions (BLOCKER):** PV-0.C1, PV-0.C2, PV-0.C5
- **Dependencies:** none (entry-point validator)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-0.C1 | NFR-8 validator baseline JSON exists and parses | `working/feature/issue-capture-mechanism-r1/validator-baseline-l1-l2.json` exists; `python3 -c "import json; json.load(open('<path>'))"` succeeds; top-level shape is a list (or `{findings: [...]}` per script convention) | T0.1 in plan-v2.md | `test -f <path> && python3 -c "import json; json.load(open('<path>'))"` | BLOCKER |
| PV-0.C2 | Pipeline-isolation zero-baseline captured + empty | `working/feature/issue-capture-mechanism-r1/pipeline-isolation-baseline.txt` exists; file size is 0 bytes OR the file contains only the literal "0 matches" line | T0.2 in plan-v2.md | `test -f <path> && (test ! -s <path> \|\| grep -q "^0 matches$" <path>)` | BLOCKER |
| PV-0.C3 | cc-critique pre-change baseline JSON exists | `working/feature/issue-capture-mechanism-r1/cc-critique-baseline.json` exists; parses; contains a `verdict` field | T0.3 in plan-v2.md | `test -f <path> && python3 -c "import json; assert 'verdict' in json.load(open('<path>'))"` | MAJOR (comparison anchor; PV-7 uses it but Phase 0 can still set baseline if cc-critique itself errors — see failure response) |
| PV-0.C4 | Test-fixture directory skeleton staged | `.claude/skills/auditing-shared/scripts/test_fixtures/issue_doc_types/` exists; contains `.gitkeep`; no other files (will be populated in Phase 2) | T0.4 in plan-v2.md | `test -d <dir> && test -f <dir>/.gitkeep && [ $(ls -1 <dir> \| wc -l) -eq 1 ]` | MAJOR |
| PV-0.C5 | No validator code edited in Phase 0 | `git diff --name-only <Phase-0-start>..HEAD -- .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` returns empty | Phase 0 Exit Criteria: "No file under `.claude/` has been edited; no Python under `.claude/skills/auditing-shared/scripts/` modified beyond the test-fixtures directory creation." | `git diff --name-only -- .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py \| wc -l` returns `0` | BLOCKER |
| PV-0.C6 | Devenv prerequisites (shellcheck, jq) confirmed | `working/feature/issue-capture-mechanism-r1/devenv-prereqs.txt` exists and lists shellcheck + jq versions | T0.5 in plan-v2.md | `test -f <path> && grep -q shellcheck <path> && grep -q jq <path>` | MAJOR |

### Acceptance tests scheduled for this phase

None. Phase 0 is setup-only; all baselines feed into PV-2 and PV-7.

### Operational checks (phase-specific)

- All three baseline artifacts are persisted to the run's working directory (so downstream phases and the packager can reach them).
- The validator source file has not been touched.
- The auditing-shared test-fixtures directory is staged and empty (only `.gitkeep`).

### Failure response

- **PV-0.C1 fail:** Re-run T0.1; if validator itself errors, treat as a defect outside the scope of this run and surface to user before continuing.
- **PV-0.C2 fail:** Investigate any recently-merged change that may have re-introduced a `KB-issue-capture` reference into a pipeline agent. Do not proceed until baseline is empty.
- **PV-0.C5 fail:** Hard rollback (`git checkout HEAD -- <validator-path>`). The Phase 0 invariant is "no behavior change." If T0.1..T0.5 inadvertently edited the validator, the baseline is invalidated and must be re-captured.

### Validator metadata

- **Run trigger:** Manual or CI, post-T0.5
- **Expected duration:** < 1 minute
- **Prerequisites:** Run cwd is the repo root; git in clean state.

---

## PV-1 — Templates + structural spec (CC)

- **Validator ID:** `PV-1`
- **Phase reference:** Plan Phase 1 — Templates + structural spec (plan-v2.md §Phase 1)
- **Validator goal:** Prove that 4 new files (3 templates + 1 spec) exist at canonical paths, that `KB-documentation-criteria/SKILL.md` has been additively updated with 4 new index entries, and that all 4 new files contain structural-only content (no triggering discipline).
- **Load-bearing assertions (BLOCKER):** PV-1.C1, PV-1.C2, PV-1.C5
- **Dependencies:** PV-0 PASS

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-1.C1 | All 4 new files exist at canonical paths | Files exist: `.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md`, `.../issue-analysis-template.md`, `.../issue-proposal-template.md`, `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md` | T1.1..T1.4 in plan-v2.md | `for f in <4 paths>; do test -f "$f" \|\| exit 1; done` | BLOCKER |
| PV-1.C2 | All 4 new files have parseable YAML frontmatter | Each file has `---`-delimited frontmatter at top; parses via `python3 -c "import yaml; yaml.safe_load(...)"` | shared-conventions | `python3 scripts/validate_frontmatter.py <4 paths>` (or inline parse loop) | BLOCKER |
| PV-1.C3 | `issue-doctypes-spec.md` per-state companion-field table byte-matches Blueprint authoritative table | Manual checksum + grep: the spec contains the 6-state × per-doctype required-field mapping verbatim from blueprint-v3.md §Backend Per-State Companion Field Authoritative Table | T1.4 L2 verification | Manual review checklist (one-time); plus grep that the spec lists all 6 states: `for s in draft open adopted complete superseded wontfix-with-rationale; do grep -q "$s" <spec-path> \|\| exit 1; done` | BLOCKER (this spec is the source-of-truth that PV-2.C1 reads from) |
| PV-1.C4 | None of the 4 new files contains triggering discipline | grep for forbidden phrases ("when to capture", "trigger", "invocation guidance") returns zero matches across the 4 files | AC-FR-6-b | `grep -l -i -E "when to capture\|invocation guidance" <4 paths>` returns empty | MAJOR (manual review confirms; grep is heuristic) |
| PV-1.C5 | `KB-documentation-criteria/SKILL.md` updated additively with 4 new index entries | Diff of `.claude/skills/KB-documentation-criteria/SKILL.md` shows: only additive rows; lists all 3 new template paths + the new spec path; no removals; "Where this KB is NOT used" bullet present mentioning `KB-issue-capture` | T1.5 in plan-v2.md | `git diff --stat HEAD~<phase-1-start>..HEAD -- .claude/skills/KB-documentation-criteria/SKILL.md` shows only insertions; `grep -c "issue-register-template\|issue-analysis-template\|issue-proposal-template\|issue-doctypes-spec" <SKILL.md>` returns ≥4 | BLOCKER |
| PV-1.C6 | Gate 0 PASS from `shared-document-reviewer` on each of the 4 new files | Each file passes Gate 0 structural review | KB-review-disciplines | Manual reviewer dispatch; output captured to `working/feature/issue-capture-mechanism-r1/phase-1-gate-0-results.json` | MAJOR |

### Acceptance tests scheduled for this phase

- AC-FR-6-a (template structure usable at Gate 0) — verified end-to-end at PV-7; foundation laid here.
- AC-FR-6-b (no triggering discipline in templates) — directly enforced by PV-1.C4.
- AC-FR-14-a (KB-documentation-criteria SKILL.md index updated) — directly enforced by PV-1.C5.

### Operational checks (phase-specific)

- All 4 files are committed (visible in `git status` as tracked / clean).
- SKILL.md diff is reviewable in a single PR-style hunk (no unrelated edits intermixed).

### Failure response

- **PV-1.C1/C2 fail:** Re-author the missing or malformed file per the corresponding T1.x task; re-run validator.
- **PV-1.C3 fail:** The spec MUST byte-match the Blueprint authoritative table; PV-2.C1 will diverge otherwise. Rollback PV-1.C5 and re-author the spec before re-running.
- **PV-1.C5 fail:** SKILL.md drift breaks the discoverability contract (AC-FR-14-a). Revert any non-additive edit and re-author the additive index rows.

### Validator metadata

- **Run trigger:** Post-T1.5
- **Expected duration:** ~5 minutes (mostly Gate 0 reviewer dispatch)
- **Prerequisites:** PV-0 PASS

---

## PV-2 — Backend validator extension + path-prefix skip

- **Validator ID:** `PV-2`
- **Phase reference:** Plan Phase 2 — Backend validator extension + path-prefix skip (plan-v2.md §Phase 2)
- **Validator goal:** Prove that the validator extension (constants, categorization, path-prefix skip, `validate_issue_artifact`) is in place AND that the **NFR-8 regression diff against the Phase 0 baseline is empty** — the highest-blast-radius assertion of the whole feature.
- **Load-bearing assertions (BLOCKER):** PV-2.C1, PV-2.C2, PV-2.C5, PV-2.C7
- **Dependencies:** PV-0 PASS, PV-1 PASS (the spec must exist before constants can be filled)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2.C1 | Module-level constants present in the validator | `grep -E "^ISSUE_DOC_TYPES\s*="` and `^ISSUE_STATES\s*=`, `^ISSUE_PER_STATE_REQUIRED_FIELDS\s*=`, `^ISSUE_NON_VALIDATED_PATH_PREFIXES\s*=` all return a single match each in `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` | T2.1 in plan-v2.md | `for c in ISSUE_DOC_TYPES ISSUE_STATES ISSUE_PER_STATE_REQUIRED_FIELDS ISSUE_NON_VALIDATED_PATH_PREFIXES; do [ $(grep -cE "^$c\s*=" <validator-path>) -eq 1 ] \|\| exit 1; done` | BLOCKER |
| PV-2.C2 | `doc_type_category` extended to return `"issue"` for the 3 new doc_types | Python smoke: `python3 -c "from validate_pipeline_frontmatter import doc_type_category; assert doc_type_category('issue-register') == 'issue'; assert doc_type_category('issue-analysis') == 'issue'; assert doc_type_category('issue-proposal') == 'issue'"` exits 0 | T2.1 in plan-v2.md | Inline Python snippet via `python3 -c` | BLOCKER |
| PV-2.C3 | Validator imports cleanly (no syntax / import errors) | `python3 -c "import py_compile; py_compile.compile('.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py', doraise=True)"` exits 0 | All Phase 2 tasks (regression safety) | `python3 -m py_compile <validator-path>` | BLOCKER |
| PV-2.C4 | New `validate_issue_artifact` function present + uses `make_finding` verbatim | `grep -nE "^def validate_issue_artifact\b" <validator-path>` returns 1 match; `grep -c "make_finding(" <validator-path>` count is ≥ N_pre + 1 where N_pre is the pre-Phase-2 count (uses helper, not parallel construction) | T2.3 in plan-v2.md; VE-002 anti-pattern | `python3 scripts/check_validate_issue_artifact_uses_make_finding.py` (validator implementation task) | MAJOR (functional but parallel-construction would be caught by reviewer; BLOCKER if grep returns 0) |
| PV-2.C5 | Outer-dispatch path-prefix early-return present | Static check: `validate_pipeline_artifact` body contains a guard that early-returns `[]` for paths matching `ISSUE_NON_VALIDATED_PATH_PREFIXES` BEFORE the existing `doc_type_category` dispatch | T2.2 in plan-v2.md; I-AA-002 | Inline grep + unit-test fixture (T2.5 positive-control assertion); plus AC-BE-10 fixture returning `[]` on `Issues/<topic>/evidence/agent-roster-impact-matrix.md` | BLOCKER |
| PV-2.C6 | 28 smoke-test fixtures all pass (`smoke_test_auditing_shared.py`) | Running `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` exits 0; output reports all 18 positive + 6 missing-companion + 3 invalid-status + 1 advisory fixtures pass | T2.5 in plan-v2.md | `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` | BLOCKER |
| PV-2.C7 | **NFR-8 regression diff against Phase 0 baseline is empty** | `working/feature/issue-capture-mechanism-r1/validator-postextension-l1-l2-diff.json` exists; parses; contains an empty diff array | T2.6 in plan-v2.md; NFR-8 load-bearing | `test -f <diff-path> && python3 -c "import json; d = json.load(open('<diff-path>')); assert d == [] or d == {'new_findings': []}"` | BLOCKER |
| PV-2.C8 | Positive control: non-Issues file with unknown doc_type continues to produce a `minor` finding | Smoke-test fixture explicitly verifies the path-prefix skip does NOT over-silence | T2.5 in plan-v2.md; blueprint-v3 §Verification Strategy positive-control mandate | Bundled into PV-2.C6 smoke test | BLOCKER |

### Acceptance tests scheduled for this phase

- AC-BE-1 through AC-BE-10 (clean validation; status-blocker; companion-field-blocker; advisory info; cross-link minor; regression baseline; existing categories preserved; outer-dispatch unchanged except early-return; make_finding reuse; path-prefix skip) — all directly verified by PV-2.C1..C8.
- AC-FR-7-a/b/c/d (validator behavior on issue files) — verified here; re-confirmed end-to-end at PV-7.C5.
- AC-NFR-8-a (regression baseline preserved) — directly enforced by PV-2.C7.

### Operational checks (phase-specific)

- The validator's existing GATED/ANALYSIS/ADR branches are syntactically unchanged (no behavior re-routing).
- The `make_finding` helper is the sole construction site for findings (verified by AC-BE-9 / VE-002 check).
- The smoke-test extension does not slow the pre-merge gate (fixtures complete in < 30s).

### Failure response

- **PV-2.C7 fail (ANY new finding line in regression diff):** This is the load-bearing assertion. Hard block. Investigate immediately. The most likely defects are:
  1. `doc_type_category` accidentally re-classifying an existing doc_type → revert T2.1 changes; re-author the categorization extension as pure-extension.
  2. The path-prefix early-return matching too broadly → tighten `ISSUE_NON_VALIDATED_PATH_PREFIXES` to literal prefixes only.
  3. The new `validate_issue_artifact` accessed unexpectedly → check the dispatch wiring in `validate_pipeline_artifact`.
  Per Plan Phase 2 Exit Criteria: "Phase 3 must NOT start while T2.6 has any new findings."
- **PV-2.C6 fail (fixture failure):** Inspect the specific fixture; defect is localized to either the function body (PV-2.C4 wiring) or the fixture content (PV-1.C3 spec).

### Validator metadata

- **Run trigger:** Post-T2.6
- **Expected duration:** ~2 minutes (smoke test + diff check)
- **Prerequisites:** PV-0 PASS, PV-1 PASS

---

## PV-3 — Migration of 4 Issues files + agent-roster-impact-matrix

- **Validator ID:** `PV-3`
- **Phase reference:** Plan Phase 3 — Migration of 4 Issues files + agent-roster-impact-matrix (plan-v2.md §Phase 3)
- **Validator goal:** Prove that the 5 file migrations have landed as atomic commits with preserved history (`git log --follow`), that the 4 migrated Issues files validate clean post-back-fill, that the migrated agent-roster-matrix returns `[]` via the path-prefix skip, AND that the Phase 3 commit-range diff contains ONLY the 5 expected file pairs (AC-FR-8-d direct enforcement per I-DR-PL-002).
- **Load-bearing assertions (BLOCKER):** PV-3.C2, PV-3.C3, PV-3.C5, PV-3.C7
- **Dependencies:** PV-0 PASS, PV-1 PASS, PV-2 PASS

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-3.C1 | Phase 3 commit-range anchors captured | Both `working/feature/issue-capture-mechanism-r1/phase-3-start-commit.txt` and `.../phase-3-end-commit.txt` exist; each contains a single 40-char SHA + newline; `git cat-file -e $(cat <file>)` succeeds for each | T3.0, T3.8 in plan-v2.md | `test -f <start-path> && test -f <end-path> && git cat-file -e $(cat <start-path>) && git cat-file -e $(cat <end-path>)` | BLOCKER |
| PV-3.C2 | 5 source paths absent | Each of these 5 paths does NOT exist: `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`, `Issues/analysis-per-agent-design-evaluation-gap.md`, `Issues/analysis-adr-placement-rootcause.md`, `Issues/proposal-auditing-family-graduation-review.md`, `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` | T3.2..T3.6 in plan-v2.md | `for p in <5 source paths>; do test ! -e "$p" \|\| exit 1; done` | BLOCKER |
| PV-3.C3 | 5 destination paths present | Each of these 5 paths exists: `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`, `Issues/per-agent-design-evaluation-gap/analysis.md`, `Issues/adr-placement-rootcause/analysis.md`, `Issues/auditing-family-graduation-review/proposal.md`, `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` | T3.2..T3.6 in plan-v2.md | `for p in <5 dest paths>; do test -f "$p" \|\| exit 1; done` | BLOCKER |
| PV-3.C4 | `git log --follow` returns pre-migration history for each destination | For each of 5 destination paths, `git log --follow <path>` returns ≥ 2 commits (the migration commit + at least one pre-migration commit) | AC-FR-8-b, AC-FR-9-b | `for p in <5 dest paths>; do [ $(git log --follow --oneline "$p" \| wc -l) -ge 2 ] \|\| exit 1; done` | BLOCKER |
| PV-3.C5 | Validator returns zero findings on 4 migrated Issues files | `python3 .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py <4 migrated Issues paths>` returns zero findings | T3.7 in plan-v2.md; AC-FR-8-c | `python3 <validator> <4 paths> \| python3 -c "import sys, json; d=json.load(sys.stdin); assert d==[] or d=={'findings':[]}"` | BLOCKER |
| PV-3.C6 | Validator returns `[]` on the migrated agent-roster-matrix (path-prefix skip on real file) | `python3 <validator> Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` returns `[]` regardless of frontmatter | T3.6 in plan-v2.md; AC-BE-10 verified end-to-end on a real file | Inline Python via `<validator>` | BLOCKER |
| PV-3.C7 | **AC-FR-8-d direct enforcement: Phase 3 commit-range diff contains only the 5 expected file pairs** | `working/feature/issue-capture-mechanism-r1/phase-3-scope-diff.txt` exists; enumerates EXACTLY the 5 expected file pairs (10 add/delete entries OR 5 rename entries via `--diff-filter=R`). Any other path → BLOCKER. | T3.8 in plan-v2.md; AC-FR-8-d; I-DR-PL-002 resolution | `python3 scripts/check_phase_3_scope.py` — script enumerates expected set and asserts `git diff --name-only $(cat phase-3-start-commit.txt)..$(cat phase-3-end-commit.txt)` equals the expected union (handles both rename and add/delete renderings) | BLOCKER |

### Acceptance tests scheduled for this phase

- AC-FR-8-a (migration target paths correct) — directly enforced by PV-3.C2 + PV-3.C3.
- AC-FR-8-b (`git log --follow` returns history on 4 Issues files) — directly enforced by PV-3.C4.
- AC-FR-8-c (validator zero findings on 4 migrated files) — directly enforced by PV-3.C5.
- AC-FR-8-d (no other files migrated) — **directly enforced by PV-3.C7** (per I-DR-PL-002, the Plan v1.1.0 absorbed this assertion into a machine-checkable form rather than relying on inference).
- AC-FR-9-a (agent-roster-matrix at evidence subdirectory; no copy at prior path) — directly enforced by PV-3.C2 + PV-3.C3.
- AC-FR-9-b (`git log --follow` returns history on agent-roster-matrix) — directly enforced by PV-3.C4.
- AC-BE-10 (path-prefix skip on a real migrated file) — directly enforced by PV-3.C6.

### Operational checks (phase-specific)

- Each migration is a single atomic commit (verified by inspecting commit messages between `phase-3-start-commit` and `phase-3-end-commit`).
- The 4 Issues files' back-filled frontmatter satisfies the per-doctype, per-state required-field rules from PV-2.C1's `ISSUE_PER_STATE_REQUIRED_FIELDS`.
- The agent-roster-matrix migration has NO frontmatter back-fill (validator skips this path; back-fill would be a waste and potentially malformed).

### Failure response

- **PV-3.C4 fail (history truncated):** `git mv` rename-detection failed for that file (similarity-index too low). Fall back to D-13's two-commit-sequence procedure per Plan T3.1; re-run history check.
- **PV-3.C5 fail (validator finds issues):** The frontmatter back-fill is incorrect (missing companion field, wrong status value, wrong doc_type). Inspect the validator output; correct the back-fill in-place; re-commit; re-run.
- **PV-3.C7 fail (extra paths in commit-range diff):** A non-migration edit was made in Phase 3. Hard rollback any non-migration commits in the range; restore the commit-range to contain only the 5 expected commits.

### Validator metadata

- **Run trigger:** Post-T3.8
- **Expected duration:** ~2 minutes
- **Prerequisites:** PV-0 PASS, PV-1 PASS, PV-2 PASS

---

## PV-4 — CC layer: KB skills + agent + entry-point skill

- **Validator ID:** `PV-4`
- **Phase reference:** Plan Phase 4 — CC layer: KB skills + agent + entry-point skill (plan-v2.md §Phase 4)
- **Validator goal:** Prove that the Layer 1 + Layer 2 of the three-layer enforcement is in place: two new skills carry `disable-model-invocation: true`, the new agent body is structurally complete (frontmatter + hard-constraint section + create-mode workflow + update-mode workflow), AND — most critically — that the agent body's frontmatter contains **NO `skills:` field** (F-003 silent-drop avoidance).
- **Load-bearing assertions (BLOCKER):** **PV-4.C1 (F-003)**, PV-4.C2, PV-4.C3, PV-4.C7
- **Dependencies:** PV-0 PASS, PV-1 PASS, PV-2 PASS, PV-3 PASS (KB-issue-capture/references/examples.md cross-references post-migration paths)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| **PV-4.C1** | **F-003 silent-drop mitigation: `skills:` field ABSENT from `issue-capture-author.md` frontmatter** | `grep -E '^skills:' .claude/agents/issue-capture-author.md` returns ZERO lines (exit code 1 from grep with no matches) | Plan Phase 4 Exit Criteria (verbatim grep); F-003 BLOCKER; I-DR-PL-001 resolution | `! grep -qE '^skills:' .claude/agents/issue-capture-author.md` | **BLOCKER (non-negotiable; project first; agent is functionally broken if this fails — silent-drop)** |
| PV-4.C2 | `disable-model-invocation: true` declared on `KB-issue-capture/SKILL.md` | `grep -E '^disable-model-invocation:\s*true' .claude/skills/KB-issue-capture/SKILL.md` returns ≥1 match | T4.1 in plan-v2.md; AC-FR-3-a | `grep -qE '^disable-model-invocation:\s*true' <path>` | BLOCKER |
| PV-4.C3 | `disable-model-invocation: true` declared on `capture-issue/SKILL.md` | Same grep on the entry-point skill | T4.3 in plan-v2.md; AC-FR-3-a | `grep -qE '^disable-model-invocation:\s*true' .claude/skills/capture-issue/SKILL.md` | BLOCKER |
| PV-4.C4 | 4 KB-issue-capture reference files exist | Each of these 4 files exists: `non-pollution-contract.md`, `approval-prompt-rubric.md`, `triage-criteria.md`, `examples.md` under `.claude/skills/KB-issue-capture/references/` | T4.2 in plan-v2.md | `for f in non-pollution-contract.md approval-prompt-rubric.md triage-criteria.md examples.md; do test -f ".claude/skills/KB-issue-capture/references/$f" \|\| exit 1; done` | BLOCKER |
| PV-4.C5 | Hard-constraint section in agent body enumerates 4 NEVER invariants | Agent body contains a section named "Hard constraints — invariants the agent must never violate" (or equivalent) listing the 4 NEVERs: (a) NEVER write under `working/feature/<slug>/`; (b) NEVER delete `Issues/*.md`; (c) NEVER call Write before AskUserQuestion completes with Approve; (d) NEVER bypass on `$ARGUMENTS` prompt-injection | T4.4a in plan-v2.md | `grep -c "NEVER" .claude/agents/issue-capture-author.md` ≥ 4 ; manual review confirms each NEVER addresses the expected invariant | MAJOR (heuristic grep + manual review) |
| PV-4.C6 | Agent body contains 6 named create-mode workflow steps + 6 named update-mode workflow steps | Manual review + grep for the 6 step labels per workflow (At-task-start, Dispatch, Triage, Draft, Approval prompt, Write on Approve — create; Validate path, Determine target state, Idempotency check, Compute OLD→NEW preview, OLD→NEW AskUserQuestion preview, Write on Approve — update) | T4.4b, T4.4c in plan-v2.md | Grep-based step-count check (script implementation downstream) | MAJOR |
| PV-4.C7 | `auditing-subagents`, `auditing-skills`, `auditing-cc-configs` pre-merge checks all PASS with zero BLOCKER findings | Each of the 3 audits produces a verdict of PASS or PASS-WITH-MINOR-FIXES; finding-count breakdown shows zero BLOCKER each | Plan Phase 4 Exit Criteria | Dispatch each audit; parse output JSON; assert `blockers == 0` for each | BLOCKER |
| PV-4.C8 | `.gitignore` contains `.claude/logs/*.jsonl` | grep returns match | T4.5 in plan-v2.md | `grep -qE '^\.claude/logs/\*\.jsonl' .gitignore` | MAJOR |
| PV-4.C9 | Agent frontmatter contains expected fields: `name`, `description`, `tools`, `model`, `permissionMode`; `memory:` ABSENT | YAML parse; check field presence/absence | T4.4a in plan-v2.md | `python3 scripts/check_agent_frontmatter.py .claude/agents/issue-capture-author.md` | MAJOR |

### Acceptance tests scheduled for this phase

- AC-FR-1-a (spawn via Task) — foundation laid by T4.3 + T4.4b; verified end-to-end at PV-7.C1.
- AC-FR-2-c (create+update mutual exclusivity) — verified by T4.3 dispatch logic; smoke at PV-7.
- AC-FR-3-a (Layer 1 `disable-model-invocation: true`) — **directly enforced by PV-4.C2 + PV-4.C3**.
- AC-FR-3-d (Layer 2 AskUserQuestion-before-Write hard constraint) — directly enforced by PV-4.C5.
- AC-NFR-4-a / AC-NFR-4-b / AC-NFR-6-a / AC-NFR-6-b (Write-gating + prompt-injection resistance + no-deletion + supersession via field) — declared as hard constraints in T4.4a; PV-4.C5 verifies declaration; runtime verification at PV-7.

### Operational checks (phase-specific)

- The agent reads its KB at runtime (via Read calls in its body) — NOT via `skills:` preload. This is the F-003 mitigation strategy: the agent's body explicitly Reads `KB-issue-capture/SKILL.md` + the 4 references at task start.
- `auditing-cc-configs` cross_file_checks X3 (no skills with `disable-model-invocation: true` in the agent's preload) inherently passes because there IS no preload — the agent has no `skills:` field.

### Failure response

- **PV-4.C1 fail (ANY `skills:` line in frontmatter):** Hard rollback. Remove the `skills:` field. This is non-negotiable; the agent is functionally broken (Claude Code silently drops the KB preload with no error message). Per Plan Phase 4 Exit Criteria: "F-003 silent-drop avoidance non-negotiable." Re-verify with `grep -E '^skills:'` after edit. Then re-run PV-4 from C1.
- **PV-4.C2/C3 fail:** Without `disable-model-invocation: true`, main Claude can auto-load the skill by description-match and bypass the Layer 1 enforcement. Re-author the skill frontmatter; re-run.
- **PV-4.C7 fail (auditing-* BLOCKER):** Inspect the specific finding; the most likely cause is a frontmatter shape divergence from auditing-* expectations. Resolve in-place; re-run audits.

### Validator metadata

- **Run trigger:** Post-T4.5
- **Expected duration:** ~3 minutes (audits dominate)
- **Prerequisites:** PV-0..PV-3 PASS

---

## PV-5 — CC layer: hook script + settings.json patch

- **Validator ID:** `PV-5`
- **Phase reference:** Plan Phase 5 — CC layer: hook script + settings.json patch (plan-v2.md §Phase 5)
- **Validator goal:** Prove that Layer 3 of the three-layer enforcement is in place: the PreToolUse hook script passes shellcheck, the 5-fixture golden-file harness passes, `.claude/settings.json` is patched additively (existing entries unchanged), and the latency benchmark (D-11) ratified or replaced AC-NFR-1-a's ~100ms target. *(v1.1, 2026-05-25: previously also required `.claude/SETTINGS-NOTES.md` to carry the FR-15 note; that requirement was retired with the rest of FR-15 — see PV-5.C6 RETIRED below and ADR-0047 v1.1.0.)*
- **Load-bearing assertions (BLOCKER):** PV-5.C1, PV-5.C2, PV-5.C3, PV-5.C5
- **Dependencies:** PV-0 PASS (T0.5 devenv check)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-5.C1 | `.claude/hooks/intercept-issue-capture-agent.sh` exists, is executable, shebang correct | File exists; mode includes +x; first line is `#!/usr/bin/env bash` | T5.1 in plan-v2.md | `test -x .claude/hooks/intercept-issue-capture-agent.sh && head -1 .claude/hooks/intercept-issue-capture-agent.sh \| grep -q '^#!/usr/bin/env bash'` | BLOCKER |
| PV-5.C2 | shellcheck PASS with zero warnings on the hook script | `shellcheck .claude/hooks/intercept-issue-capture-agent.sh` exits 0; output has zero warnings | T5.2 in plan-v2.md (early-verification target Step 1) | `shellcheck .claude/hooks/intercept-issue-capture-agent.sh` | BLOCKER |
| PV-5.C3 | All 5 golden-file fixtures PASS | `python3 .claude/hooks/test_intercept_issue_capture_agent.py` exits 0; output reports 5/5 fixtures pass: (a) issue-capture-author spawn → ask; (b) non-issue spawn → allow; (c) malformed JSON → allow + stderr; (d) missing tool_input → allow + stderr; (e) empty stdin → allow + stderr | T5.3 + T5.4 in plan-v2.md | `python3 .claude/hooks/test_intercept_issue_capture_agent.py` | BLOCKER |
| PV-5.C4 | 1000-iteration p95 latency benchmark recorded; D-11 outcome documented | `working/feature/issue-capture-mechanism-r1/hook-latency-results.json` exists; contains p50, p95, p99 in ms; D-11 algorithm outcome (ratify / replace / escalate) recorded; AC-NFR-1-c marked CLOSED with the finalized threshold value | T5.5 in plan-v2.md; D-11; resolves U-11 | `python3 scripts/check_hook_latency_results.py` (asserts schema + D-11 outcome) | BLOCKER (escalate-to-design is also a non-pass outcome for this validator) |
| PV-5.C5 | `.claude/settings.json` patched additively; `permissions.allow` unchanged | JSON parses; new `hooks.PreToolUse` block present; `permissions.allow` array byte-identical to pre-Phase-5 (only the `hooks` block is new) | T5.6 in plan-v2.md | `python3 scripts/check_settings_json_additive.py` (parses JSON; compares against snapshot) | BLOCKER |
| ~~PV-5.C6~~ | ~~`.claude/SETTINGS-NOTES.md` contains the FR-15 append~~ | **RETIRED v1.1, 2026-05-25** — FR-15 was removed from PRD v2 and the file deleted; the precedent enumeration this validator checked now lives inline in ADR-0047 §Decision §5. No replacement validator needed (ADR-0047 itself does not require runtime validation; doc-review covers it). See ADR-0047 v1.1.0 Document History. | ~~T5.7 in plan-v2.md; AC-FR-15-a~~ | N/A | N/A |
| PV-5.C7 | `auditing-hooks` + `auditing-settings` pre-merge checks PASS | Each produces verdict PASS or PASS-WITH-MINOR-FIXES; zero BLOCKER findings | Plan Phase 5 Exit Criteria | Dispatch each audit; parse output | BLOCKER |
| PV-5.C8 | p95 latency ≤ ratified threshold | After D-11 outcome, p95 from `hook-latency-results.json` ≤ threshold (100ms by default; replacement value if D-11 said "replace") | T5.5; AC-NFR-1-a | `python3 -c "import json; r=json.load(open('<path>')); assert r['p95_ms'] <= r['threshold_ms']"` | BLOCKER |

### Acceptance tests scheduled for this phase

- AC-FR-3-b (Layer 3 hook ask emission on issue-capture-author) — directly enforced by PV-5.C3 fixture (a).
- AC-FR-3-c (Layer 3 hook fast-path allow on others) — directly enforced by PV-5.C3 fixtures (b)–(e).
- AC-NFR-1-a (~100ms p95 wall-clock fast-path) — directly enforced by PV-5.C4 + PV-5.C8.
- AC-NFR-1-c (Design ratifies or replaces target; deferral closed) — directly enforced by PV-5.C4.
- AC-NFR-2-a (fail-open on error) — directly enforced by PV-5.C3 fixtures (c)–(e).
- AC-NFR-2-b (visible stderr line) — enforced by PV-5.C3 fixtures (c)–(e).
- ~~AC-FR-15-a (SETTINGS-NOTES.md append) — directly enforced by PV-5.C6.~~ *(RETIRED v1.1, 2026-05-25; AC-FR-15-a removed from PRD v2; PV-5.C6 retired; see ADR-0047 v1.1.0.)*

### Operational checks (phase-specific)

- The hook script has no `set -e` (only `set -u`) — fail-open requires every path to exit 0.
- jq path is `.tool_input.subagent_type` (verified at PV-5.C3 fixture pass).
- The hook header comment documents idempotency + concurrency posture (manual review per I-DR-010 resolution).

### Failure response

- **PV-5.C2 fail (shellcheck warning):** Fix in-place per Plan T5.2's "fix in-place before T5.3 begins"; re-run shellcheck.
- **PV-5.C3 fail (fixture):** Localize defect — most likely jq path or stdout shape. Per blueprint-v3 §Verification Strategy: "the defect is localized to the hook script before it enters any cross-cutting flow." Fix; re-run.
- **PV-5.C4 fail (p95 > 200ms):** Per D-11 algorithm and Plan Phase 5 Exit Criteria: escalate to design iteration; re-author hook in faster language (likely Python or compiled). This is NOT a code-fix scenario — it is a design-level decision and the validator HALTS Phase 5 until resolved.
- **PV-5.C5 fail (settings.json not additive):** Hard rollback. The `permissions.allow` invariant is load-bearing; any change other than the additive `hooks` block is forbidden.

### Validator metadata

- **Run trigger:** Post-T5.7
- **Expected duration:** ~3 minutes (latency benchmark dominates; ~1 minute for hyperfine + 1 minute for harness + audits)
- **Prerequisites:** PV-0 PASS (T0.5 devenv prerequisites)

---

## PV-6 — Cross-cutting handoff edits

- **Validator ID:** `PV-6`
- **Phase reference:** Plan Phase 6 — Cross-cutting handoff edits (plan-v2.md §Phase 6)
- **Validator goal:** Prove that the 3 cross-cutting handoff edits are purely additive — `intake-intent-clarifier.md` gains a Phase 0 block (~15 lines), `intent-clarification-template.md` Source section gains guidance (~5 lines), `recipe-feature-pipeline/SKILL.md` gains one bullet — and that NO new pipeline stage / gate / bypass language is introduced.
- **Load-bearing assertions (BLOCKER):** PV-6.C1, PV-6.C4
- **Dependencies:** PV-5 PASS (Phase 6 documents now-existing mechanism)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-6.C1 | All 3 edits are purely additive (no removals; no structural changes) | For each of the 3 files, `git diff HEAD~<phase-6-start>..HEAD -- <path>` shows only insertions (no `^-` lines beyond context); structural section headers unchanged | Plan Phase 6 Exit Criteria | `python3 scripts/check_phase_6_additive.py` (per-file unified-diff parser; rejects any `-`-prefix change line) | BLOCKER |
| PV-6.C2 | `intake-intent-clarifier.md` gains a "Phase 0 — Proposal-as-prior-context detection" block | Grep for the section header returns 1 match; the block is positioned BEFORE the existing Phase 1; the block contains the proposal-detection branch (mentions `doc_type: issue-proposal`) | T6.1 in plan-v2.md; AC-FR-11-a/b | `grep -E "Phase 0.*Proposal-as-prior-context" .claude/agents/intake-intent-clarifier.md` returns 1 match; `grep "doc_type: issue-proposal" <path>` returns ≥1 match | MAJOR |
| PV-6.C3 | `intent-clarification-template.md` Source section appended with proposal-seed guidance | Diff shows an additive ~5-line block in or near the Source section mentioning "proposal" verbatim | T6.2 in plan-v2.md; AC-FR-12-a | `git diff -- <path> \| grep "^+" \| grep -qi "proposal"` | MAJOR |
| PV-6.C4 | `recipe-feature-pipeline/SKILL.md` gains only one bullet; NO new pipeline stage / gate / bypass | Diff shows ≤5 additive lines forming a single bullet; bullet mentions `--raw-request Issues/<topic>/proposal.md`; grep for "new stage", "new gate", "bypass" in the diff returns ZERO matches | T6.3 in plan-v2.md; AC-FR-12-b | `python3 scripts/check_recipe_skill_diff.py` (asserts ≤5 lines, no stage/gate/bypass language) | BLOCKER |

### Acceptance tests scheduled for this phase

- AC-FR-11-a (`intake-intent-clarifier` detects proposal-as-prior-context) — declared by PV-6.C2; runtime verification at PV-7 (T7.1's broader smoke test path).
- AC-FR-11-b (elicit-only-missing) — same as above.
- AC-FR-12-a (template carries proposal-seed Source guidance) — directly enforced by PV-6.C3.
- AC-FR-12-b (no new pipeline stage / gate / bypass) — directly enforced by PV-6.C4.

### Operational checks (phase-specific)

- No signature changes to any of the 3 edited files (frontmatter `version` field may or may not bump, per project convention).
- The edits are committed in a separate commit (or commits) from any other work — making diff inspection clean.

### Failure response

- **PV-6.C1 fail:** Hard rollback. Per Plan Phase 6 Exit Criteria: "ANY non-additive change in T6.1/T6.2/T6.3 diffs is `blocker`." Identify the offending edit; restore the removed/changed content; re-author the additive intent.
- **PV-6.C4 fail:** Per Plan Phase 6 Exit Criteria: "Any new pipeline stage or gate bypass in T6.3 is `blocker`." The recipe is load-bearing for the pipeline; an unauthorized new stage breaks the orchestration contract. Revert; re-author as documentation-only bullet.

### Validator metadata

- **Run trigger:** Post-T6.3
- **Expected duration:** < 1 minute (pure diff checks)
- **Prerequisites:** PV-5 PASS

---

## PV-7 — Rollout / verification + acceptance

- **Validator ID:** `PV-7`
- **Phase reference:** Plan Phase 7 — Rollout / verification + acceptance (plan-v2.md §Phase 7)
- **Validator goal:** This is the Plan-wide acceptance gate. Re-runs all the cross-phase invariants end-to-end (pipeline-isolation grep, validator regression diff, migration history, cc-critique vs baseline, auditing-* family); verifies the integration smoke tests pass; asserts `packager-input-notes.md` is in place for finalize-deliverable-packager Stage 13 consumption (I-DR-PL-004 resolution).
- **Load-bearing assertions (BLOCKER):** PV-7.C1, PV-7.C2, PV-7.C3, PV-7.C5, PV-7.C6
- **Dependencies:** PV-0..PV-6 ALL PASS

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-7.C1 | Integration smoke tests PASS (create-mode happy path) | `working/feature/issue-capture-mechanism-r1/smoke-test-create-mode.txt` transcript shows: hook ask-prompt visible; agent AskUserQuestion visible; written file at `Issues/<topic>/<doctype>.md` path; path reported to user; stderr line + JSONL append observable | T7.1 in plan-v2.md | Manual smoke test + transcript review; downstream automatable via Claude Code session replay | BLOCKER |
| PV-7.C2 | Negative smoke tests PASS (cancel branch + non-issue fast-path) | (a) Cancel branch: no file written under `Issues/`; (b) non-issue spawn (e.g., cc-critique): hook silently allows, no `ask` prompt | T7.2 in plan-v2.md; AC-FR-1-d, AC-FR-3-c | Manual smoke + transcript review | BLOCKER |
| PV-7.C3 | Update-mode smoke test PASS (incl. idempotency) | OLD→NEW preview observed; transition applied; re-invocation produces "no change" | T7.3 in plan-v2.md; AC-FR-2-a, AC-FR-2-b, AC-NFR-3-a | Manual smoke + transcript review | BLOCKER |
| PV-7.C4 | Pipeline-isolation grep returns empty (AC-FR-13-a/b verified end-to-end) | Both verbatim greps from AC-FR-13-a/b against `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` return ZERO matches; output byte-identical to Phase 0 baseline | T7.4 in plan-v2.md; AC-FR-13-a, AC-FR-13-b | `! grep -rE "KB-issue-capture" .claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md`; `! grep -rE "subagent_type:\s*issue-capture-author" <same set>` | BLOCKER |
| PV-7.C5 | NFR-8 final regression diff against Phase 0 baseline is empty | `working/feature/issue-capture-mechanism-r1/validator-final-l1-l2-diff.json` exists; contains empty diff array | T7.5 in plan-v2.md; AC-NFR-8-a end-to-end | `python3 -c "import json; d=json.load(open('<path>')); assert d==[] or d=={'new_findings':[]}"` | BLOCKER |
| PV-7.C6 | `git log --follow` returns pre-migration history for all 5 destination paths | Same check as PV-3.C4 but re-confirmed at acceptance | T7.6 in plan-v2.md; AC-FR-8-b, AC-FR-9-b | Same automation as PV-3.C4 | BLOCKER |
| PV-7.C7 | `cc-critique` PASS or PASS-WITH-MINOR-FIXES with zero BLOCKER on new components | `working/feature/issue-capture-mechanism-r1/cc-critique-final.json` shows verdict PASS or PASS-WITH-MINOR-FIXES; new findings limited to MINOR-or-better; comparison against `cc-critique-baseline.json` does not show new BLOCKER findings | T7.7 in plan-v2.md; PRD §Success Criteria #5 | `python3 scripts/check_cc_critique_verdict.py` (asserts verdict ∈ {PASS, PASS-WITH-MINOR-FIXES} AND blockers == 0) | BLOCKER |
| PV-7.C8 | `auditing-{hooks, skills, subagents, settings, cc-configs}` family all PASS | Combined output in `working/feature/issue-capture-mechanism-r1/auditing-final.json`; each of the 5 audits shows verdict PASS or PASS-WITH-MINOR-FIXES; zero BLOCKER across all 5; ≤2 MINOR findings each | T7.8 in plan-v2.md; PRD §Success Criteria #5 | `python3 scripts/check_auditing_final.py` (per-audit verdict + blocker count check) | BLOCKER |
| PV-7.C9 | Working tree clean for merge | `git status --porcelain` shows only the intended feature-branch additions (no orphan `.jsonl` logs, no leftover test issues outside `Issues/`-supersession, no fixture files outside `test_fixtures/`) | T7.9 in plan-v2.md | `python3 scripts/check_clean_working_tree.py` (parses git status; whitelist of expected paths) | MAJOR |
| PV-7.C10 | `packager-input-notes.md` exists and contains 5 enumerated sections | `working/feature/issue-capture-mechanism-r1/packager-input-notes.md` exists; frontmatter parses; contains 5 sections: (1) Deviation summary; (2) Authoritative evidence (cites `Issues/adr-placement-rootcause/analysis.md`); (3) User acceptance (cites I-AA-001 Option A); (4) Packager direction (do NOT relocate ADRs to `/adrs/`); (5) Future remediation scope | T7.10 in plan-v2.md; I-DR-PL-004 resolution | `python3 scripts/check_packager_input_notes.py` (section-presence check + cross-reference verification) | MAJOR (per Plan Phase 7 Exit Criteria: "absence is `important` (warns; packager handoff is still possible via Open Items fallback but loses visibility per I-DR-PL-004 rationale)") |

### Acceptance tests scheduled for this phase

Phase 7 is the catch-all for ALL remaining ACs not already directly enforced earlier. From `plan-v2.md` Acceptance Test Cross-Reference, the ACs primarily verified at Phase 7 (in addition to those re-confirmed end-to-end here):

- AC-FR-1-a/b/c/d (create-mode end-to-end) — PV-7.C1 + PV-7.C2
- AC-FR-2-a/b (update-mode end-to-end) — PV-7.C3
- AC-FR-3-b/c/d (Layer 2 + Layer 3 end-to-end) — PV-7.C1 + PV-7.C2
- AC-FR-4-a/b (canonical filenames + per-topic folder) — PV-7.C1
- AC-FR-7-b (regression baseline preserved end-to-end) — PV-7.C5
- AC-FR-8-b/c, AC-FR-9-b (history + clean validation end-to-end) — PV-7.C5 + PV-7.C6
- AC-FR-13-a/b (pipeline isolation invariant) — PV-7.C4
- AC-FR-14-a (KB index discoverable end-to-end) — verified by PV-7.C7's cc-critique sweep
- ~~AC-FR-15-a (SETTINGS-NOTES.md append discoverable end-to-end) — verified by PV-7.C7~~ *(RETIRED v1.1, 2026-05-25; AC-FR-15-a removed from PRD v2; SETTINGS-NOTES.md deleted; see ADR-0047 v1.1.0.)*
- AC-NFR-1-a (latency target met) — verified by PV-5.C8; re-confirmed here via PV-7.C8 auditing-hooks
- AC-NFR-2-a/b (fail-open) — verified by PV-5.C3; re-confirmed here via PV-7.C2 fast-path
- AC-NFR-3-a (idempotency) — PV-7.C3
- AC-NFR-4-a/b (Write-gating + prompt-injection resistance) — PV-7.C1 (Write-gating observed via single AskUserQuestion preceding Write)
- AC-NFR-5-a (no silent overwrite) — verified by smoke if test fixture exercises collision; otherwise inferred from PV-4.C5 hard-constraint declaration
- AC-NFR-6-a (no Issues/ deletion) — PV-7.C9 (clean working tree confirms no deletion)
- AC-NFR-7-a (observability record) — PV-7.C1 (stderr + JSONL append observable)
- AC-NFR-8-a (validator backward compatibility end-to-end) — PV-7.C5
- AC-NFR-9-a (in-session invocation) — PV-7.C1

(Note: this enumeration is for cross-reference; the formal acceptance-tests.md authored by the parallel sibling `test-acceptance-author` will be the authoritative AT-NNN → AC-ID mapping.)

### Operational checks (phase-specific)

- All baseline artifacts from Phase 0 (`validator-baseline-l1-l2.json`, `pipeline-isolation-baseline.txt`, `cc-critique-baseline.json`) are preserved in `working/feature/issue-capture-mechanism-r1/` for the packager.
- `packager-input-notes.md` is present (T7.10) so finalize-deliverable-packager Stage 13 has direct binding for the I-AA-001 user-accepted deviation.
- The test issue captured by T7.1 is restored via `/capture-issue --update` to `wontfix-with-rationale`, NOT deleted (per AC-NFR-6-a).

### Failure response

- **PV-7.C4 fail (pipeline-isolation grep non-empty):** A new component leaked into a pipeline agent. Identify the offending pipeline agent file; revert the leak. Per Plan: "ANY non-empty result from T7.4 pipeline-isolation grep is `blocker`."
- **PV-7.C5 fail (regression diff non-empty):** The validator extension has a defect that surfaced only at end-to-end run. Hard block. Re-investigate per PV-2.C7 failure response.
- **PV-7.C7 fail (cc-critique BLOCKER):** Inspect the BLOCKER finding; this is a CC-design rubric violation on a new component. Fix in-place; re-run cc-critique. Per Plan: "ANY BLOCKER from cc-critique or any of the 5 audits is `blocker`."
- **PV-7.C10 fail (packager-input-notes.md missing):** Per Plan Phase 7 Exit Criteria: "absence is `important` (warns; packager handoff is still possible via Open Items fallback but loses visibility per I-DR-PL-004 rationale)." Treat as MAJOR; surface to user; advance only with explicit user decision to fall back to Open Items.

### Validator metadata

- **Run trigger:** Post-T7.10
- **Expected duration:** ~10 minutes (smoke tests + audits + cc-critique dominate)
- **Prerequisites:** PV-0..PV-6 ALL PASS

---

## PV-8 — Devcontainer hardening (shellcheck persistence)

- **Validator ID:** `PV-8`
- **Phase reference:** Plan Phase 8 — Devcontainer hardening (plan-v2.md v1.2.0 §Phase 8)
- **Validator goal:** Prove that `shellcheck` is now persisted via `.devcontainer/Dockerfile` (image-build-time install, prebuild-captured), that the Dockerfile change is structurally sound and apt-resolvable on the base image, and that the devenv-prereqs.txt + postCreate.sh documentation correctly handoff the rebuild requirement to future operators.
- **Load-bearing assertions (BLOCKER):** PV-8.C1
- **Dependencies:** PV-0 PASS (Phase 8 is order-independent with Phases 1–7; the Dockerfile edit does NOT depend on any feature delivery phase and the in-session hot-install at `~/.local/bin/shellcheck` already satisfies the Phase 5 T5.2 runtime prereq)

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-8.C1 | `shellcheck` continuation line present in Dockerfile apt-get install block | `grep -nE "^[[:space:]]+shellcheck[[:space:]]*\\\\$" .devcontainer/Dockerfile` returns exactly 1 match AND the matched line sits inside the existing `RUN apt-get update && apt-get install -y --no-install-recommends ...` block (verified by surrounding context: preceded by another tool name + `\\` continuation, followed by either another tool name or the `&& ln -sf` / `&& rm -rf` cleanup tail) | T8.1 in plan-v2.md | `[ $(grep -cE "^[[:space:]]+shellcheck[[:space:]]*\\\\$" .devcontainer/Dockerfile) -eq 1 ]` AND a one-shot manual review of the surrounding 5 lines | BLOCKER |
| PV-8.C2 | Apt-resolution evidence OR docker-build success captured | Either `working/feature/issue-capture-mechanism-r1/shellcheck-apt-resolution.txt` exists and contains a `Version:` line, OR T8.1 L2 docker-build succeeded (captured in task notes or build log) | T8.2 in plan-v2.md | `test -f working/feature/issue-capture-mechanism-r1/shellcheck-apt-resolution.txt && grep -q "^Version:" working/feature/issue-capture-mechanism-r1/shellcheck-apt-resolution.txt` (apt-cache path); OR check task-054 result.notes for `docker_build_status=succeeded` | MAJOR (if neither path verifies, escalate to user with manual-rebuild-confirmation rather than auto-block) |
| PV-8.C3 | `devenv-prereqs.txt` updated; postCreate.sh comment header references Phase 8 | (a) `working/feature/issue-capture-mechanism-r1/devenv-prereqs.txt` does NOT contain literal "shellcheck MISSING"; contains both `~/.local/bin/shellcheck` and `/usr/bin/shellcheck` references; contains a rebuild instruction. (b) `.devcontainer/postCreate.sh` head-of-file comment references "Phase 8" and "issue-capture-mechanism-r1". (c) `bash -n .devcontainer/postCreate.sh` exits 0. | T8.3 in plan-v2.md | `! grep -q "shellcheck MISSING" working/feature/issue-capture-mechanism-r1/devenv-prereqs.txt && grep -q "/usr/bin/shellcheck" working/feature/issue-capture-mechanism-r1/devenv-prereqs.txt && grep -q "Phase 8" .devcontainer/postCreate.sh && bash -n .devcontainer/postCreate.sh` | RECOMMENDED (documentation gap is recoverable post-merge; do not block on this alone) |
| PV-8.C4 | No edit to `.devcontainer/devcontainer.json` (Phase 8 scope = Dockerfile + postCreate.sh comment only) | `git diff --name-only <phase-8-start>..HEAD -- .devcontainer/devcontainer.json \| wc -l` returns `0` | Phase 8 Exit Criteria: "No edit to .devcontainer/devcontainer.json (Phase 8 is Dockerfile-only + script-comment-only)." | `[ $(git diff --name-only -- .devcontainer/devcontainer.json \| wc -l) -eq 0 ]` | MAJOR |
| PV-8.C5 | `validate_pipeline_frontmatter.py` not edited by Phase 8 (PV-0.C5 invariant preserved) | `git diff --name-only -- .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py \| wc -l` returns `0` (Phase 8 does NOT touch the validator) | CPI-2-adjacent invariant preserved | `[ $(git diff --name-only -- .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py \| wc -l) -eq 0 ]` | BLOCKER (cross-phase invariant; Phase 8 must not destabilize the validator) |

### Acceptance tests scheduled for this phase

None. Phase 8 is infrastructure hardening with no PRD/Blueprint AC binding; the binding is to the Open Item surfaced at T0.5 and to Phase 5 T5.2's runtime prerequisite (which is already satisfied in-session by the hot-install).

### Operational checks (phase-specific)

- `.devcontainer/Dockerfile` diff is one new line; passes `git diff --stat` size sanity (< 5 lines added).
- `.devcontainer/postCreate.sh` comment-only edit; `git diff` body shows zero changes inside any function definition.
- `devenv-prereqs.txt` records the dual-state (hot-installed v0.10.0 at `~/.local/bin/` + persisted apt-shipped at `/usr/bin/`) so post-rebuild operators understand which one is on PATH.

### Failure response

- **PV-8.C1 fail (Dockerfile line missing or malformed):** Re-author T8.1; verify continuation-line position (must be inside the existing `RUN apt-get install` block, not a separate `RUN` invocation which would defeat layer caching). Re-run validator.
- **PV-8.C2 fail (neither apt-cache nor docker-build verifies):** Escalate to user. Possible causes: Docker unavailable in the execution environment AND the spawned base-image container couldn't resolve `apt-get update` (network egress restriction). In that case, the user authorizes proceeding via a manual rebuild-and-verify on the actual Codespace. Do NOT auto-block on PV-8.C2 alone.
- **PV-8.C4 fail (devcontainer.json was edited):** Out of scope for Phase 8. Inspect the diff; if the edit is intentional and pulls in some other Codespaces decision, surface as a NEW deviation requiring user authorization. If accidental, `git checkout HEAD -- .devcontainer/devcontainer.json` and re-run.
- **PV-8.C5 fail (validator edited):** Hard rollback (`git checkout HEAD -- .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py`). Phase 8 must not destabilize the validator; if it did, the Phase 0 NFR-8 baseline is invalidated.

### Validator metadata

- **Run trigger:** Post-T8.3
- **Expected duration:** ~2 minutes (one Dockerfile grep + one apt-cache probe + two doc-presence greps)
- **Prerequisites:** PV-0 PASS. Note: PV-8 does NOT require PV-1..PV-7 to pass first; Phase 8 is order-independent. In practice, Phase 8 is executed alongside Phase 5 or batched with the rollout PR, but the validator imposes no upstream-phase ordering constraint beyond PV-0.

---

## Cross-phase invariants

These assertions MUST hold at every validator boundary, not just within a single phase. They are re-asserted by PV-N for `N ≥ 1` as part of the phase exit, and re-confirmed end-to-end at PV-7.

| Invariant ID | Description | Re-asserted by | Severity if violated mid-run |
|---|---|---|---|
| CPI-1 | Pipeline-isolation grep returns empty | PV-0.C2 (baseline), PV-7.C4 (final). Recommended at every PV boundary post-Phase-4. | BLOCKER |
| CPI-2 | `validate_pipeline_frontmatter.py` clean-runs on the current state of `Issues/` (post-Phase-3) | PV-3.C5/C6, PV-7.C5 | BLOCKER |
| CPI-3 | `.claude/agents/issue-capture-author.md` has NO `skills:` frontmatter field (F-003) | PV-4.C1, PV-7.C8 (via auditing-subagents) | BLOCKER |
| CPI-4 | NFR-8 regression diff against the Phase 0 validator baseline is empty | PV-2.C7, PV-7.C5 | BLOCKER |
| CPI-5 | No `Issues/*.md` file is ever deleted (AC-NFR-6-a) | PV-7.C9 (clean tree confirms) | BLOCKER |
| CPI-6 | `.claude/settings.json` `permissions.allow` array is unchanged from pre-Phase-5 state | PV-5.C5; re-confirmed by PV-7.C8 auditing-settings | BLOCKER |

### Cross-phase automation hook

A consolidated script `scripts/check_cross_phase_invariants.py` (downstream task in the task DAG; not part of this document) bundles CPI-1..CPI-6 into one CI-callable check, runnable at any time between phases.

---

## Validator dependency graph + parallelization

### Dependency graph

```
PV-0 ─► PV-1 ─► PV-2 ─► PV-3 ─► PV-4 ─► PV-5 ─► PV-6 ─► PV-7
                          │              │
                          └─► (parallel: PV-4 can start when PV-3 done; PV-5 can start as soon as PV-0 done — but Plan sequences PV-5 after PV-4 for ordering hygiene)
```

Per Plan v2 cross-phase dependencies:
- PV-0 must pass before PV-1 can start (baselines must be in place).
- PV-1 must pass before PV-2 (spec must exist before constants).
- PV-2 must pass before PV-3 (validator must accept post-migration frontmatter before commits land).
- PV-3 must pass before PV-4 (KB-issue-capture references cite post-migration paths).
- PV-4 must pass before PV-5 (Plan sequences Phase 5 after Phase 4; physically PV-5 depends only on PV-0).
- PV-5 must pass before PV-6 (Phase 6 documents the now-deployed mechanism).
- PV-6 must pass before PV-7 (Phase 7 is the acceptance gate).

### Critical-path validators

- **PV-2** (NFR-8 regression diff) — failure here is the highest-blast-radius scenario; the load-bearing validator backward-compatibility assertion. Re-runs as PV-7.C5.
- **PV-4** (F-003 skills:-absence) — failure here means the agent is functionally broken (silent-drop); the F-003 BLOCKER mitigation is the single highest-priority validator assertion across the whole feature.
- **PV-3** (AC-FR-8-d migration scope) — failure here means the migration touched unintended paths; resolves only by hard rollback.
- **PV-7** (Plan-wide acceptance gate) — failure of any C1..C8 BLOCKER assertion halts merge.
- **PV-8** (Devcontainer hardening) — order-independent (depends only on PV-0). Not on the feature-delivery critical path; sequencing is convenience-only.

### Parallelizable validator checks (within-phase)

- **PV-1.C1..C4** are independent file-existence + parse checks; can parallelize.
- **PV-2.C1..C5** are static checks; PV-2.C6..C8 are dynamic; the static set can run in parallel.
- **PV-3.C2..C6** are independent per-path checks; full parallelization possible.
- **PV-4.C2..C4 + C8** are independent static checks; can parallelize. **PV-4.C1 (F-003 grep) is single-shot; should run first (cheapest fail-fast).**
- **PV-5.C2..C3** are sequential by Plan design (shellcheck before fixture); PV-5.C4 (latency) parallelizable to neither (depends on hook working end-to-end).
- **PV-7.C4..C8** are independent end-to-end re-checks; full parallelization possible (the Plan calls this out explicitly).

### Shared validator infrastructure

| Resource | Used by | Source |
|---|---|---|
| `validator-baseline-l1-l2.json` | PV-2.C7, PV-7.C5 | T0.1 output |
| `pipeline-isolation-baseline.txt` | PV-7.C4 | T0.2 output |
| `cc-critique-baseline.json` | PV-7.C7 | T0.3 output |
| `phase-3-start-commit.txt` + `phase-3-end-commit.txt` | PV-3.C1, PV-3.C7 | T3.0, T3.8 output |
| `hook-latency-results.json` | PV-5.C4, PV-5.C8 | T5.5 output |
| `smoke_test_auditing_shared.py` (extended) | PV-2.C6 | T2.5 output |
| `test_intercept_issue_capture_agent.py` | PV-5.C3 | T5.3 + T5.4 output |
| Auditing-* dispatch | PV-4.C7, PV-5.C7, PV-7.C8 | Existing `.claude/skills/auditing-*` family |

---

## Validator runbook (operator-facing)

A human operator (or downstream phase-quality-reviewer agent) executes the validators as follows during a real run:

1. **End of Phase 0:** Run `PV-0`. Inspect output JSON; confirm `passed == true`. If any BLOCKER fails, halt; remediate per failure-response section above.
2. **End of Phase 1:** Run `PV-1`. Same procedure.
3. **End of Phase 2:** Run `PV-2`. **PV-2.C7 is the highest-stakes assertion of the feature; if the diff is non-empty, the orchestrator MUST halt and surface to user.** Per Plan: "Phase 3 must NOT start while T2.6 has any new findings."
4. **End of Phase 3:** Run `PV-3`. **PV-3.C7 is the AC-FR-8-d direct enforcement; any extra path in the commit-range diff is a hard block.**
5. **End of Phase 4:** Run `PV-4`. **PV-4.C1 (F-003 grep) is the project's highest-priority validator assertion; if it fails, the agent is silently broken — halt and remove the `skills:` field before any further work.**
6. **End of Phase 5:** Run `PV-5`. **PV-5.C4 latency outcome may force escalate-to-design (re-author hook in faster language); this is a non-pass that requires a design decision, not a code fix.**
7. **End of Phase 6:** Run `PV-6`. Diff-only; fast.
8. **End of Phase 7:** Run `PV-7`. This is the Plan-wide merge gate.
9. **End of Phase 8 (order-independent — may run any time after PV-0):** Run `PV-8`. Lightweight check; ~2 minutes. Failure of PV-8.C1 (BLOCKER) prevents the Phase 8 deliverable from shipping but does NOT halt Phases 1–7. Failure of PV-8.C5 (BLOCKER) means Phase 8 destabilized the validator — this is the only Phase 8 failure that affects the rest of the run.

**On any BLOCKER failure:** the orchestrator surfaces the failing assertion(s) to the user, cites the Plan's per-phase rollback path (the "Failure response" sections above), and does not advance to the next phase until the validator re-runs PASS.

**On any MAJOR failure:** the orchestrator surfaces to user; the user may explicitly defer with documented rationale (recorded as a new `I-PV-NNN` ledger entry). Advancement is permitted only with explicit user approval.

**On any MINOR failure:** recorded in the validator output; advancement proceeds.

---

## Cross-references

### Plan v2 cross-reference

Every PV-N maps to the corresponding Plan phase's Exit Criteria + the per-phase "Phase Validator" anchor sentence:

| Validator | Plan phase | Plan exit criteria anchor | Plan "Phase Validator" anchor |
|---|---|---|---|
| PV-0 | Phase 0 | "Blocking severity threshold: any Phase 0 task failing L3 is a `blocker`" | "asserts the three baseline JSON / TXT files exist with the right shape; asserts no edits to validator code; asserts test-fixtures directory empty (only `.gitkeep`)" |
| PV-1 | Phase 1 | "any `blocker` finding from `shared-document-reviewer` on a new template; any `important` finding on the spec → Phase 1 not done" | "asserts all 4 files exist; asserts SKILL.md diff is additive-only; runs Gate 0 against each new template and the spec" |
| PV-2 | Phase 2 | "ANY new line in the regression diff is a `blocker`" | "re-runs T2.6 regression diff; asserts empty. Re-runs T2.5 smoke test; asserts all fixtures pass. Asserts the constants list contains all 4 expected items." |
| PV-3 | Phase 3 | "any path in `phase-3-scope-diff.txt` outside the 5 expected file pairs → `blocker`" | "(I-DR-PL-002 concrete enforcement) Runs `git diff --name-only` ... asserts the output set is EXACTLY the 5 expected file pairs" |
| PV-4 | Phase 4 | "BLOCKER if `grep -E '^skills:' .claude/agents/issue-capture-author.md` returns any line — F-003 silent-drop avoidance non-negotiable" | "Direct F-003 grep enforcement: runs `grep -E '^skills:' .claude/agents/issue-capture-author.md` and asserts the output is empty" |
| PV-5 | Phase 5 | "ANY shellcheck warning is `blocker`; any golden-file fixture failure is `blocker`; latency benchmark p95 > 200ms escalates to design iteration" | "re-runs shellcheck; re-runs the 5-fixture golden-file suite; asserts `.claude/settings.json`'s diff is purely additive; ~~asserts `.claude/SETTINGS-NOTES.md` contains the FR-15 note;~~ *(SETTINGS-NOTES assertion RETIRED v1.1, 2026-05-25 — see PV-5.C6 above)* asserts the latency-results JSON shows p95 ≤ ratified threshold" |
| PV-6 | Phase 6 | "ANY non-additive change in T6.1/T6.2/T6.3 diffs is `blocker`. Any new pipeline stage or gate bypass in T6.3 is `blocker`" | "diffs each of the 3 edited files against the pre-Phase-6 state; asserts all changes are additive; asserts no new stage / gate / bypass language in `recipe-feature-pipeline/SKILL.md`" |
| PV-7 | Phase 7 | "ANY new line in T7.5 validator regression diff is `blocker`; ANY non-empty result from T7.4 pipeline-isolation grep is `blocker`; ANY BLOCKER from cc-critique or any of the 5 audits is `blocker`" | "this is effectively the Plan-wide acceptance gate. Re-runs T7.4 ... T7.8" |
| PV-8 | Phase 8 | "T8.1 L1 fail is `blocker` (Dockerfile change must be present and well-formed); T8.2 L3 fail is `important`; T8.3 verifications are `recommended`" | "asserts the Dockerfile line is present, the apt-resolution evidence file exists OR docker-build succeeded, and the devenv-prereqs.txt + postCreate.sh comment changes landed" |

### PRD v2 AC cross-reference

Each PRD Acceptance Criterion is enforced by one or more validator assertions:

| AC | Primary enforcement | Re-confirmation |
|---|---|---|
| AC-FR-1-a/b/c/d/e | PV-7.C1, C2 | — |
| AC-FR-2-a/b/c/d | PV-7.C3 | — |
| AC-FR-3-a | PV-4.C2, C3 | PV-7.C8 (auditing-skills) |
| AC-FR-3-b/c/d | PV-5.C3, PV-7.C1, C2 | — |
| AC-FR-4-a/b/c/d | PV-7.C1 | — |
| AC-FR-5-a/b/c | PV-7.C1 (if sibling-evolution exercised); PV-4.C5/C6 (declaration) | — |
| AC-FR-6-a/b | PV-1.C4 | — |
| AC-FR-7-a/b/c/d | PV-2.C6, C7 | PV-7.C5 |
| AC-FR-8-a/b/c/d | PV-3.C2..C7 | PV-7.C5, C6 |
| AC-FR-9-a/b | PV-3.C3, C4 | PV-7.C6 |
| AC-FR-10-a, AC-FR-11-a/b, AC-FR-12-a/b | PV-6.C2..C4 | — |
| AC-FR-13-a/b/c | PV-7.C4 (cross-phase invariant CPI-1) | — |
| AC-FR-14-a | PV-1.C5 | PV-7.C7 (cc-critique) |
| ~~AC-FR-15-a~~ | ~~PV-5.C6~~ | ~~PV-7.C7~~ — **RETIRED v1.1, 2026-05-25** (AC-FR-15-a removed from PRD v2; see ADR-0047 v1.1.0) |
| AC-BE-1..AC-BE-10 | PV-2.C1..C8 | PV-7.C5 |
| AC-NFR-1-a/b/c | PV-5.C4, C8 | PV-7.C8 |
| AC-NFR-2-a/b | PV-5.C3 | PV-7.C2 |
| AC-NFR-3-a | PV-7.C3 | — |
| AC-NFR-4-a/b | PV-4.C5 (declaration) | PV-7.C1 (Write-gating observed) |
| AC-NFR-5-a | PV-4.C5 (declaration); PV-7.C1 if collision exercised | — |
| AC-NFR-6-a/b | PV-4.C5 (declaration); PV-7.C9 (clean tree) | CPI-5 |
| AC-NFR-7-a | PV-7.C1 | — |
| AC-NFR-8-a/b | PV-2.C7 | PV-7.C5 (CPI-4) |
| AC-NFR-9-a | PV-7.C1 | — |

### Blueprint v3 Verification Strategy alignment

Per blueprint-v3 §Verification Strategy:

- **Early Verification Points:** Backend constants-only commit (PV-2.C1..C3, C7) + CC hook shellcheck + single-fixture (PV-5.C1..C3). Both are gated by validators above.
- **Operational Verification > Pre-merge gates:** auditing-* family + Gate 0/1 reviewer + validator regression diff + shellcheck. All four are enforced across PV-1..PV-7.
- **Migration verification:** `git log --follow` + validator clean-run + agent-roster-matrix path-prefix skip. Enforced by PV-3.C4, C5, C6 + PV-7.C6.

### Companion artifact: `acceptance-tests.md` (parallel sibling)

This validator document is authored in true parallel with `acceptance-tests.md` (owned by `test-acceptance-author`). When the sibling completes, the orchestrator's cross-artifact auditor (`review-cross-artifact-auditor`) will verify:

- Every AC referenced in this document maps to ≥1 acceptance test AT-NNN in `acceptance-tests.md`.
- No validator assertion contradicts an acceptance test's pass criterion.
- The PV-7 phase reference to "acceptance-tests.md enumeration" resolves correctly.

If the cross-artifact auditor surfaces a divergence, this document MAY be revised in a follow-up iteration to incorporate AT-NNN IDs (currently absent because the sibling is running concurrently).

---

## Update history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-05-23 | Initial authoring (Stage 10 parallel; sibling `test-acceptance-author` running concurrently). Authored per `KB-documentation-criteria` phase-validators discipline. Operationalizes Plan v1.1.0 Phase Validator anchors into 8 PV-N entries (PV-0..PV-7) with 50 individual pass criteria across the 8 validators. Load-bearing assertions explicitly marked BLOCKER per severity hygiene rules: NFR-8 regression diff (PV-2.C7, PV-7.C5), F-003 skills:-absence (PV-4.C1), AC-FR-8-d migration scope (PV-3.C7), pipeline-isolation grep (PV-7.C4). |
