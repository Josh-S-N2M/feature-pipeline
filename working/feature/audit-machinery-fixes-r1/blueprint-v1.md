---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/audit-machinery-fixes-r1/prd-v1.md
adrs_referenced: [ADR-0005, ADR-0023, ADR-0025]
adrs_authored: [ADR-0026]
approved_at: 2026-05-21T02:10:00Z
gate_passed: 3
---

# Blueprint — audit-machinery-fixes-r1

## Approach

Three targeted Python script edits + one bonus (discovered during testing) + content reverts. No new files; no layout changes.

## Per-layer design

Single layer (audit machinery). No Frontend / Backend / API / DB / IaC / CC / GHA / Codespaces decomposition; all changes are within `.claude/skills/auditing-skills/scripts/` and `.claude/skills/auditing-cc-configs/scripts/`.

### Edits

| File | Lines | Change |
|---|---|---|
| `.claude/skills/auditing-skills/scripts/scan_security.py` | 57-66 | DE-2 regex hardening |
| `.claude/skills/auditing-skills/scripts/lint_references.py` | 105-128 | `normalize()` cross-KB branch |
| `.claude/skills/auditing-skills/scripts/lint_references.py` | 193-209 | depth-2 check within-skill scope |
| `.claude/skills/auditing-cc-configs/scripts/verdict_compute.py` | 133-145 | `deductions_by_severity` uses `final_severity` |

### Content reverts (v4.4.0 workarounds)

| File | Change |
|---|---|
| `.claude/skills/KB-design-system-design/references/governance.md` | `process['env']['NODE_ENV']` → `process.env.NODE_ENV` |
| `.claude/skills/KB-storybook-platform/references/composition.md` | Same |
| All 5 new KBs' Cross-references sections | `` `KB-X` (specifically references/Y.md) `` → `` `KB-X/references/Y.md` `` (16 sites; sed substitution) |

## ADRs

- **ADR-0026** (authored): Audit-machinery fixes — closes ADR-0025 defects 2, 3, 4. Documents the regex test methodology (14-case true-positive / false-positive matrix), the cross-KB resolution path, and the validation that baseline strictly decreased.

## Rationale (brief)

Detailed rationale per defect lives in ADR-0026. Summary: ADR-0025 captured the defects with concrete remediation guidance from the v4.4.0 execution; v4.4.1 implements that guidance. No new architectural decisions required.

## Version impact

PATCH bump (v4.4.0 → v4.4.1). No public surface change.
