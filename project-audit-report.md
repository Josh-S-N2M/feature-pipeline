# Claude Code Configuration Audit — feature-pipeline

**Audited:** `/workspaces/feature-pipeline`
**Score:** 0.0/100
**Verdict:** FAIL

## Inventory

- skills: 43
- context files: 0
- subagents: 36
- subagent memory dirs: 23
- hook scripts: 0
- settings files: 2
- output styles: 0
- MCP configs: 1

## Summary

Total findings: 67
- **BLOCKER**: 27
- **MAJOR**: 30
- **MINOR**: 10

## Skills

### KB-documentation-criteria

- **[BLOCKER]** SKILL.md links to 'auditing-shared/scripts/log_state_transition.py' (line 70) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/shared-conventions.md links to 'working/feature/planning-agent-doctype-backfill-r1/intent-clarification.md' (line 307) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 71) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 90) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 100) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### KB-mcp-design

- **[BLOCKER]** references/principles.md links to '.devcontainer/lib/log-mcp-event.sh' (line 51) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/patterns-and-anti-patterns.md is 179 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.

### KB-mcp-platform

- **[BLOCKER]** SKILL.md links to '.devcontainer/install/terraform-mcp.sh' (line 68) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.devcontainer/postCreate.sh' (line 79) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.devcontainer/postStart.sh' (line 80) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[MINOR]** references/operator-runbook.md is 101 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.
- **[BLOCKER]** references/mcp-events-jsonl.md links to '.devcontainer/lib/log-mcp-event.sh' (line 110) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/mcp-events-jsonl.md is 111 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.
- **[BLOCKER]** references/lifecycle-hooks.md links to '.devcontainer/devcontainer.json' (line 13) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/lifecycle-hooks.md links to '.devcontainer/install/terraform-mcp.sh' (line 29) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/lifecycle-hooks.md links to '.devcontainer/lib/log-mcp-event.sh' (line 45) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/troubleshooting.md is 124 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.
- **[BLOCKER]** references/seven-named-servers.md links to '.devcontainer/install/terraform-mcp.sh' (line 74) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/credential-handling.md links to '.devcontainer/lib/log-mcp-event.sh' (line 89) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/credential-handling.md is 103 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.

### auditing-github-actions

- **[BLOCKER]** SKILL.md links to '.claude/skills/auditing-github-actions/scripts/audit_workflow.py' (line 78) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.

### auditing-mcp

- **[BLOCKER]** Instruction to append a credential to a URL or query parameter.
  - *Fix:* Credentials must never be sent in URLs.

### recipe-feature-pipeline

- **[BLOCKER]** SKILL.md links to '.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md' (line 150) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-orchestrator.md' (line 380) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-task-code-producer.md' (line 388) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-task-quality-handler.md' (line 389) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-phase-quality-reviewer.md' (line 390) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-finalize-reconciler.md' (line 391) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-orchestrator.md' (line 395) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/skills/auditing-shared/scripts/log_state_transition.py' (line 449) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/agents/execute-orchestrator.md' (line 461) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md' (line 472) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.

## Subagents and their memory

### execute-orchestrator.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

## Settings

### settings.json

- **[MAJOR]** Bare tool name 'Bash' in 'allow' is equivalent to 'Bash(*)'. (ST-9)
  - *Fix:* Add scoping: 'Bash(<pattern>)'.
- **[MAJOR]** Bare tool name 'Read' in 'allow' is equivalent to 'Read(*)'. (ST-9)
  - *Fix:* Add scoping: 'Read(<pattern>)'.
- **[MAJOR]** Bare tool name 'WebFetch' in 'allow' is equivalent to 'WebFetch(*)'. (ST-9)
  - *Fix:* Add scoping: 'WebFetch(<pattern>)'.

### settings.local.json

- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write

## MCP servers

### .mcp.json

- **[MINOR]** Server 'gitnexus': package `gitnexus@${GITNEXUS_TAG}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MINOR]** Server 'mcp-openapi-schema': package `mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MINOR]** Server 'serena': package `git+https://github.com/oraios/serena@${SERENA_REF}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MAJOR]** 
- **[MAJOR]** 

## Cross-file checks

- **[MAJOR] X9** — Subagent design-api.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-backend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'auditing-github-actions' whose audit verdict is FAIL (2 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-github-actions; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-claude-code.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-codespaces.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-composer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-database.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-frontend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-iac.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-query.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-external-researcher.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-orchestrator.md preloads skill 'recipe-feature-pipeline' whose audit verdict is FAIL (21 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/recipe-feature-pipeline; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-deliverable-packager.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-reconciler.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-task-decomposer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-intent-clarifier.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-prd-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-architecture-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-cross-artifact-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-acceptance-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-phase-validator-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (16 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.

## How to read this report

Severity meanings:

- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.
- **MAJOR** — works but degrades behavior or security.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.


Report-only: this audit does not modify any audited file.