# Claude Code Configuration Audit — feature-pipeline

**Audited:** `/workspaces/feature-pipeline`
**Score:** 17.0/100
**Verdict:** FAIL

## Inventory

- skills: 41
- context files: 0
- subagents: 36
- subagent memory dirs: 9
- hook scripts: 0
- settings files: 2
- output styles: 0
- MCP configs: 0

## Summary

Total findings: 50
- **BLOCKER**: 4
- **MAJOR**: 42
- **MINOR**: 4

## Skills

### KB-documentation-criteria

- **[MAJOR]** references/shared-conventions.md links to 'KB-documentation-criteria/references/templates/per-task-execution-result-template.md' (depth-2 nesting). Claude may partial-read it.
  - *Fix:* Add a direct link from SKILL.md to 'KB-documentation-criteria/references/templates/per-task-execution-result-template.md', or inline the content.
- **[MAJOR]** references/shared-conventions.md links to 'KB-documentation-criteria/references/templates/phase-quality-report-template.md' (depth-2 nesting). Claude may partial-read it.
  - *Fix:* Add a direct link from SKILL.md to 'KB-documentation-criteria/references/templates/phase-quality-report-template.md', or inline the content.
- **[MAJOR]** references/shared-conventions.md links to 'KB-documentation-criteria/references/templates/quality-reconciliation-log-template.md' (depth-2 nesting). Claude may partial-read it.
  - *Fix:* Add a direct link from SKILL.md to 'KB-documentation-criteria/references/templates/quality-reconciliation-log-template.md', or inline the content.
- **[MAJOR]** references/shared-conventions.md links to 'KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md' (depth-2 nesting). Claude may partial-read it.
  - *Fix:* Add a direct link from SKILL.md to 'KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md', or inline the content.
- **[MAJOR]** references/shared-conventions.md links to 'KB-documentation-criteria/references/templates/pipeline-run-summary-template.md' (depth-2 nesting). Claude may partial-read it.
  - *Fix:* Add a direct link from SKILL.md to 'KB-documentation-criteria/references/templates/pipeline-run-summary-template.md', or inline the content.
- **[BLOCKER]** references/shared-conventions.md links to 'working/feature/planning-agent-doctype-backfill-r1/intent-clarification.md' (line 307) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/disciplines/discovery-planning.md is 139 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.

### KB-github-actions-platform

- **[BLOCKER]** references/review-checklist.md links to 'scripts/audit_workflow.py' (line 3) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### auditing-github-actions

- **[BLOCKER]** SKILL.md links to '.claude/skills/auditing-github-actions/scripts/audit_workflow.py' (line 78) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/action_versions.md links to 'references/claude-code-cicd.md' (line 78) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

## Subagents and their memory

### execute-finalize-reconciler.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### execute-orchestrator.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### execute-phase-quality-reviewer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### execute-task-code-producer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### execute-task-quality-handler.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### review-cross-artifact-auditor.md

- **[MAJOR]** Body references tools ['Bash'] not in declared `tools:` list.
  - *Fix:* Add the tools to `tools:` (with scoping) or remove the body references.

## Settings

### settings.json

- **[MINOR]** Unrecognized field '_notes'. (ST-6) Will be silently ignored.
  - *Fix:* Check spelling, or remove the field. Schema: alwaysThinkingEnabled, autoMemoryDirectory, claudeMd, disableAllPlugins, disableBypassPermissionsMode, disableExternalConnectors, disableMcpServers, disableSpinnerTips, disableTelemetry, env, hooks, maxOutputTokens, mcpServers, model, outputStyles, permissionMode, permissions, promptCaching, spinnerTipsEnabled, subagents, verbose

### settings.local.json

- **[MAJOR]** Permission rule 'Bash(find / -maxdepth 4 -name "*.log" -path "*devcontainer*")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(cat /var/log/apk.log 2>/dev/null | tail -40; echo "---OS---"; cat /etc/os-release 2>/dev/null | head -5)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(find / -maxdepth 6 \\\( -name "creation.log" -o -name "*.log" -path "*codespaces*" -o -name "devcontainer*.log" \\\))' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(git commit -m ' *)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MAJOR]** Permission rule 'Bash(git commit -m 'chore: add MCP-provisioning intent doc; devcontainer + gitattributes *)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.

## Cross-file checks

- **[MAJOR] X10** — settings.local.json exists at project scope but is not covered by .gitignore. Will leak to commits.
  - *Fix:* Add a line for the path to .gitignore.
- **[MAJOR] X9** — Subagent design-api.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-backend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'KB-github-actions-platform' whose audit verdict is FAIL (32 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-github-actions-platform; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'auditing-github-actions' whose audit verdict is FAIL (4 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-github-actions; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-claude-code.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-codespaces.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-composer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-composer.md preloads skill 'KB-github-actions-platform' whose audit verdict is FAIL (32 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-github-actions-platform; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-database.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-frontend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-iac.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-query.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-external-researcher.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-deliverable-packager.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-reconciler.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-task-decomposer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-intent-clarifier.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-prd-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-architecture-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-cross-artifact-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-acceptance-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-phase-validator-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (20 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.

## How to read this report

Severity meanings:

- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.
- **MAJOR** — works but degrades behavior or security.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.


Report-only: this audit does not modify any audited file.