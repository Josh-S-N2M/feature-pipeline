# Project Audit Report — {project_name}

**Verdict:** {verdict}
**Overall score:** {project_score}/100
**Date:** {date}
**Auditor:** auditing-cc-configs v{auditor_version}
**Mode:** {mode}

{security_block_banner}

## Triage summary

- Deterministic findings: {total_findings}
- Confirmed by judge: {confirmed_count} (severity unchanged)
- Pedagogical with marker: {pedagogical_marked_count} (demoted to INFO)
- Pedagogical missing marker: {pedagogical_unmarked_count} (demoted + marker-missing finding)
- Ambiguous (human review needed): {ambiguous_count}
- Below triage threshold: {skipped_count}

{anomaly_banner}

## Per-component scores

| Component | Path | Score | Verdict |
|---|---|---|---|
{per_component_table}

## Cross-file findings ({cross_file_count} of 24 checks fired)

{cross_file_section}

## Critical findings (require attention first)

{critical_section}

## Per-component details

{per_component_details}

## Memory audit details

### Auto memory ({auto_memory_status})

{auto_memory_section}

### Subagent persistent memory ({subagent_memory_status})

{subagent_memory_section}

## Notes & disclosed false-positive classes

{notes_section}

## Recommended next actions

{next_actions_section}

## Verification commands

After applying fixes, run these inside Claude Code to verify the changes took effect:

- `/permissions` — verify deny rules are loaded
- `/skills` — confirm skill set after edits
- `/agents` — confirm subagent definitions
- `/mcp` — confirm MCP servers and their tools
- `/hooks` — confirm hooks that will fire
- `/memory` — view CLAUDE.md / rules / auto memory loaded
- `/doctor` — surface any remaining configuration issues

## Audit metadata

- Targets audited: {targets_audited_count}
- Cross-file checks run: {cross_file_checks_run}
- Pedagogical sections declared: {pedagogical_sections_count}
- Triage anomaly flag: {anomaly_flag}
- Verification step applied: {verification_applied}
