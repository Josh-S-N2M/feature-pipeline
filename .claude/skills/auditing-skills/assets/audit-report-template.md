# Skill Audit Report

**Skill:** `<skill-name>` at `<path>`
**Audited:** `<date>`
**Auditor version:** auditing-skills v1.1
**Verdict:** `<PASS | PASS-WITH-FIXES | FAIL | SECURITY-BLOCK>`
**Score:** `<N>/100`

<!-- If SECURITY-BLOCK, lead with this banner -->
<!-- 
> ## ⚠ SECURITY-BLOCK
>
> This skill contains one or more CRITICAL security findings (see Dimension 8).
> **Do not install or invoke** until reviewed by a human.
> Critical findings: <list IDs and locations>
-->

## Score breakdown

| # | Dimension | Score | Notes |
|---|---|---|---|
| 1 | Discoverability | `/10` | |
| 2 | Frontmatter validity | `/10` | |
| 3 | Token economy | `/10` | |
| 4 | Progressive disclosure | `/10` | |
| 5 | Instruction quality | `/10` | |
| 6 | Workflow soundness | `/10` | (or N/A) |
| 7 | Script hygiene | `/10` | (or N/A) |
| 8 | Security posture | `/10` | |
| 9 | Anti-pattern absence | `/10` | |
| 10 | Agent-fit | `/10` | |

## Findings

Findings are ordered by severity (BLOCKER → MAJOR → MINOR → NIT), then by dimension.

### BLOCKERs

<!-- Each finding:
- **[Dim N]** `<file>:<line>` — `<what's wrong>`
  Fix: `<concrete fix>`
-->

### MAJORs

### MINORs

### NITs

## Highlights — what the skill does well

<!-- Brief: 2-4 things this skill gets right. Acknowledging strengths makes the report
more useful and helps the author keep what's working. -->

## Recommended next actions

1. <!-- Highest-impact fix -->
2. <!-- Second highest -->
3. <!-- Third -->

## Notes

<!-- Anything that didn't fit in findings: scope decisions, N/A justifications,
co-occurring patterns across dimensions, suggestions for the author. -->

## Deterministic check output

<!-- Optional: paste the JSON output of audit_skill.py here for reproducibility. -->
