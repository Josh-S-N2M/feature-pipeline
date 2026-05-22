---
id: AcceptanceMatrix-audit-findings-remediation-r1
version: 1.0.0
status: complete
feature_slug: audit-findings-remediation-r1
artifact_type: AcceptanceCriteriaMatrix
generated: 2026-05-22T00:54:00Z
generated_by: claude (Plan task T032)
documents_phase: ship-gate verification
verdict: all AC MET
covers_ac_groups: [AC-FR-1, AC-FR-2, AC-FR-3, AC-FR-4, AC-FR-12, Cross-X9]
---

# Acceptance Criteria Matrix — v4.6.0 ship gate

**Plan reference:** T032 — confirm each AC from the PRD's EARS-format acceptance criteria has been satisfied by the implementation.

## AC-FR-1 — Marker form

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| AC-FR-1-a | Mechanism α frontmatter form is the canonical pedagogical marker | ✅ MET | KB-documentation-criteria/references/pedagogical-marker-justification-spec.md §3; canonical helper at auditing-shared/scripts/pedagogical_marker_check.py enforces structured-dict form with per-entry justification |
| AC-FR-1-b | Inline fence form requires ` -- justification` annotation | ✅ MET | `_parse_audit_example_fence_marker()` in pedagogical_marker_check.py requires the separator; all 88 existing fences pass validation |
| AC-FR-1-c | Both forms enforce same justification validity rules | ✅ MET | Both forms route through `justification_valid()` which enforces rules 1-3 |

## AC-FR-2 — Justification rules

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| AC-FR-2-a | Rule 1 (length floor: ≥5 words and ≥30 chars) | ✅ MET | `justification_valid()` line 1 enforces |
| AC-FR-2-b | Rule 2 (banned bare words: pedagogical, example, illustrative, illustration, illustrations, showing, demonstrate, demonstrates, demonstration, sample, placeholder, fake, test, demo, real, not, documentation) | ✅ MET | List in pedagogical_marker_check.py + tuned during execution per OBS-EXEC-003 |
| AC-FR-2-c | Rule 3 (substance keyword presence from controlled list) | ✅ MET | Substance-keyword list at pedagogical-marker-justification-spec-substance-keywords.txt (90 entries after pruning) |

## AC-FR-3 — Auditor behavior

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| AC-FR-3-a | Auditor emits MAJOR finding when frontmatter marker fails justification_valid() | ✅ MET | `get_pedagogical_section_marker_findings()` emits MARKER_INVALID_JUSTIFICATION |
| AC-FR-3-b | Auditor emits MAJOR finding when fence marker fails justification_valid() | ✅ MET | `get_audit_example_fence_marker_findings()` emits FENCE_INVALID_JUSTIFICATION |
| AC-FR-3-c | Rejected markers do NOT suppress underlying finding | ✅ MET | mechanism α appends rejection finding while preserving underlying finding at original severity |
| AC-FR-3-d | Triage matrix FULL_MARKER demotes to INFO when listed AND in_fence | ✅ MET | `process()` line 724-729 |
| AC-FR-3-e | Triage matrix MARKER_MISMATCH demotes one notch when listed but not in_fence | ✅ MET | `process()` line 749-763 |

## AC-FR-4 — Subagent improvements

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| AC-FR-4-a | SA-2 false-positive rate reduced via additional trigger patterns | ✅ MET | T010: 5 new trigger patterns added (at the X stage, during X, one invocation per, use at, after X passes); 22 SA-2 false positives cleared (29 → 7); plus T025 fix for hyphenated stage names |
| AC-FR-4-b | SUB-BYPASS-PROMPT supports negation-aware detection | ✅ MET | T011: NEGATION_PRE_PATTERN with 50-char lookback; cleared 3 false positives |

## AC-FR-12 — Canonical helper

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| AC-FR-12-a | Canonical pedagogical_marker_check.py at auditing-shared/scripts/ | ✅ MET | 540+ lines (canonical impl); 3 shims at auditing-cc-configs, auditing-skills, auditing-subagents |
| AC-FR-12-b | Shims preserve call-site compatibility | ✅ MET | All 3 shims dispatch via subprocess.run; verified end-to-end |
| AC-FR-12-c | auditing-shared SKILL.md lists canonical scripts | ✅ MET | Lists pedagogical_marker_check.py + scan_memory_secrets.py |
| AC-FR-12-d | finding_location() honors both `location` and `where` keys | ✅ MET | helper function in pedagogical_marker_check.py supports both (per Plan AC-FR-12-d backward-compat) |
| AC-FR-12-e | Canonical scan_memory_secrets.py at auditing-shared/scripts/ | ✅ MET | 150 lines + 2 shims at auditing-context-files, auditing-subagents |

## Cross-file (X9)

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| Cross-X9 | All preloaded skills pass their own audit | ✅ MET | 96/96 subagent×skill pairs PASS (see x9-verification-record.md) |
| Cross-X9-verdict | X9 verdict computed from POST-marker severities | ✅ MET | cross_file_checks.py uses `_eff_sev(f)` aggregate over security + references + deterministic_findings buckets |

## v4.6.0 ship criteria

| Criterion | Target | Actual | Status |
|---|---|---|---|
| BLOCKER | 0 | 0 | ✅ MET |
| MAJOR | ≤1 (named-exempt Bash) | 1 (review-cross-artifact-auditor.md Bash) | ✅ MET |
| MINOR | <29 | 1 (missing-TOC heading in 139-line discipline file) | ✅ MET |
| **Overall** | All criteria met | All criteria met | **🎯 SHIP-READY** |

## Reduction summary

| Pass | BLOCKER | MAJOR | MINOR | TOTAL |
|---|---|---|---|---|
| T001 baseline | 77 | 42 | 29 | 148 |
| Final | 0 | 1 | 1 | 2 |
| **Δ** | **-77** | **-41** | **-28** | **-146** |
| **% reduction** | **100%** | **98%** | **97%** | **99%** |
