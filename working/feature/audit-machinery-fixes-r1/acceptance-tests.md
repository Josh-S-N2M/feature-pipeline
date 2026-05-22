---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/audit-machinery-fixes-r1/prd-v1.md
approved_at: 2026-05-21T02:20:00Z
gate_passed: 5
---

# Acceptance tests — audit-machinery-fixes-r1

## AC-1 (DE-2 hardening — eliminate false positives)

**Setup.** A test corpus containing strings: `process.env.PORT`, `process.env.NODE_ENV`, `inputs.env == 'prod'`, `context.env.api_key`, `foo.envFile`, `config.environment`.

**Procedure.** Run hardened DE-2 regex against each.

**Pass condition.** Zero matches.

**Evidence.** `/tmp/test_de2.py` run output: 6/6 FALSE_POS cases produce `no match`. Verified during T-3.

## AC-2 (DE-2 preservation — keep true positives)

**Setup.** A test corpus containing strings: `.env`, `~/.aws/credentials`, `cat .env`, `"~/.aws/credentials"`, `['~/.aws/credentials']`, `Read(~/.aws/credentials)`, `rm ~/.netrc`, ` .env.local`.

**Procedure.** Run hardened DE-2 regex against each.

**Pass condition.** All 8 produce a match.

**Evidence.** `/tmp/test_de2.py` run output: 8/8 TRUE_POS cases produce `MATCH`. Verified during T-3.

## AC-3 (Cross-KB resolution)

**Setup.** v4.4.0's 16 cross-KB references reverted to backticked-full-path form across the 5 new KBs.

**Procedure.** Run `audit_project.py .` against the repo. Inspect the report for `links to '...KB-...references/...md'` BLOCKER findings.

**Pass condition.** Zero such findings.

**Evidence.** Final audit `/tmp/v441-final2.md` shows zero Reference Illusion findings for cross-KB references. Verified during T-12.

## AC-4 (Summary alignment)

**Setup.** Final audit run after all fixes.

**Procedure.** Compute BLOCKER count from both JSON summary's `deductions_by_severity.BLOCKER` and a grep of `^- \*\*\[BLOCKER\]\*\*` in the markdown report.

**Pass condition.** Both counts equal.

**Evidence.** Final audit: JSON summary BLOCKER 77 = line-count BLOCKER 77. Verified during T-12.

## AC-5 (Baseline reduction)

**Setup.** v4.4.0 baseline captured at start (`/tmp/v44-baseline.md`); v4.4.1 final captured after all fixes (`/tmp/v441-final2.md`).

**Procedure.** Compare BLOCKER counts.

**Pass condition.** Final BLOCKER count strictly less than baseline 95.

**Evidence.** Baseline BLOCKER (line count): 95. Final BLOCKER (line count): 77. Delta: −18. Verified during T-12.

## AC-6 (Workaround reversion)

**Setup.** v4.4.0 workarounds present in repo (verified pre-fix); reverts applied during T-8 and T-9.

**Procedure.** Grep for natural authoring patterns in the affected files.

**Pass condition.** 
- `process.env.NODE_ENV` (dot notation) present in 2 sites.
- `` `KB-X/references/Y.md` `` (backticked full path) present in 16 sites.
- New machinery produces zero false positives for these patterns.

**Evidence.** 
- `grep -c 'process.env.NODE_ENV' .claude/skills/KB-design-system-design/references/governance.md .claude/skills/KB-storybook-platform/references/composition.md` = 2.
- `grep -rcE '` `` `KB-[a-z-]+/references/[a-z-]+\.md` `` `'` across new KBs = 16.
- Final audit reports zero false-positive DE-2 or BACKTICK_PATH findings for these.

Verified during T-12.

## AC-7 (Discipline documentation)

**Setup.** ADR-0026 authored.

**Procedure.** Read the file; verify it contains: 4 fix descriptions, 14-case regex test reference, validation evidence per defect, scope-deferral note for defect 1.

**Pass condition.** All elements present and accurate.

**Evidence.** `adrs/ADR-0026-audit-machinery-fixes-v4-4-1.md` contains all elements. Verified during T-13.
