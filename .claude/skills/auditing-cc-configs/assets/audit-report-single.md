# Audit Report — {target_name}

**Verdict:** {verdict}
**Score:** {score}/100
**Target:** `{target_path}`
**Target type:** {target_type}
**Date:** {date}
**Auditor:** auditing-cc-configs v{auditor_version}
**Mode:** {mode}

{security_block_banner}

## Summary

{summary_paragraph}

## Triage summary

- Deterministic findings: {total_findings}
- Confirmed by judge: {confirmed_count}
- Pedagogical (with marker): {pedagogical_marked_count}
- Pedagogical (missing marker): {pedagogical_unmarked_count}
- Ambiguous (human review needed): {ambiguous_count}
- Below triage threshold: {skipped_count}

{anomaly_banner}

## Per-dimension scores

| # | Dimension | Score | Status |
|---|---|---|---|
{per_dimension_table}

## Findings

### Critical / BLOCKER

{blocker_findings_section}

### MAJOR

{major_findings_section}

### MINOR

{minor_findings_section}

### NIT

{nit_findings_section}

## Pedagogical-marker findings (if any)

{marker_findings_section}

## Notes & disclosed false-positive classes

{notes_section}

## Recommended next actions

{next_actions_section}

## Verification commands

After applying fixes, run these inside Claude Code:

{applicable_verification_commands}

## Audit metadata

- Verification step applied: {verification_applied}
- Pedagogical sections declared: {pedagogical_sections_count}
- Anti-laundering check fired: {laundering_count} time(s)
