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

Total findings: 83
- **BLOCKER**: 27
- **MAJOR**: 48
- **MINOR**: 8

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
- **[MINOR]** references/patterns-and-anti-patterns.md is 177 lines but has no recognized table-of-contents heading near the top.
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

- **[MAJOR]** Permission rule 'Bash(python3 -c "import json; d = json.load\(open\('/workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/plan-v2-review-issues.json'\)\); print\('JSON valid'\); print\('Verdict:', d['verdict']['verdict_label']\); print\('Gate 0:', d['gate0']['status']\); print\('Issues count:', len\(d['issues']\)\); print\('Prior context items received:', d['prior_context_check']['items_received']\); print\('Prior context resolved:', d['prior_context_check']['resolved']\); print\('Prior context declined_with_rationale:', d['prior_context_check']['declined_with_rationale']\); print\('Prior context unresolved:', d['prior_context_check']['unresolved']\)")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## Test inventory/,/^## Per-test details/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## Verification-layer summary/,/^## /' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## Acceptance Test Cross-Reference/,/^## Estimation Methodology/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## Acceptance Criteria/,/^## Existing Codebase Analysis/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## AC coverage matrix/,/^## Verification-layer summary/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(sed -n '999,1004p' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(echo "Total tests inventory rows: $\(awk '/^## Test inventory/,/^## Per-test details/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(sed -n '1,15p' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(awk '/^## Update History/,/^$/' /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(python3 -c ' *)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(sed -n '96,135p' /workspaces/feature-pipeline/.claude/skills/recipe-feature-pipeline/SKILL.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(echo "=== ADR-0034 count \(must be 0\) ===" && grep -c "ADR-0034" .claude/agents/execute-finalize-reconciler.md && echo "=== ADR-0033 count \(must be >= 3\) ===" && grep -c "ADR-0033" .claude/agents/execute-finalize-reconciler.md && echo "=== Agent in frontmatter check ===" && sed -n '/^---$/,/^---$/p' .claude/agents/execute-finalize-reconciler.md | head -20 | grep -q "Agent" && echo "FAIL: Agent still in frontmatter" || echo "PASS: Agent not in frontmatter" && echo "=== dispatch_directives present \(must exist\) ===" && grep -c "dispatch_directives" .claude/agents/execute-finalize-reconciler.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(python3 -c "import json; data=json.load\(open\('/workspaces/feature-pipeline/working/feature/execution-pipeline-design-r1/tasks.json'\)\); tasks=[t for t in data.get\('tasks', data\) if isinstance\(data, list\) or True]; print\(type\(data\)\)")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(python3 -c "import json; t=json.load\(open\('working/feature/synthetic-test-feature-T6/tasks.json'\)\); print\('tasks:', len\(t['tasks']\)\)")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.

### settings.local.json

- **[MAJOR]** Permission rule 'Bash(grep -rnE "[Ss]tage [0-9]+|[Pp]hase [0-9]+|[Ss]tep [0-9]+ of|[0-9]{1,2}-stage|[0-9]{1,2}-phase" /workspaces/feature-pipeline/.claude/agents/)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(grep -rnE "[Ss]tage [0-9]+|[Pp]hase [0-9]+|[0-9]{1,2}-stage|[0-9]{1,2}-phase" /workspaces/feature-pipeline/.claude/skills/)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(python3 -c "import json; d = json.load\(open\('/workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/intent-clarification-review-issues.json'\)\); print\('valid JSON; verdict:', d['verdict']['decision'], '; gate0:', d['gate0']['status'], '; issues:', len\(d['issues']\)\)")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(python3 -c "import json; d = json.load\(open\('/workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/prd-v2-review-issues.json'\)\); print\('JSON valid. Top-level keys:', list\(d.keys\(\)\)\); print\('Verdict:', d['verdict']['decision']\); print\('Prior context resolved:', d['prior_context_check']['resolved'], '/', d['prior_context_check']['items_received']\); print\('New issues count:', len\(d['issues']\)\)")' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(grep -n "skills:\\s*ABSENT\\|skills:.*OMITS\\|skills: ABSENT\\|no skills\\|NO.*skills\\|skills: \\|skills:$\\|runtime Read" /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/blueprint-v1.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(grep -A 5 "## Decision$" /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-three-doctypes-preserved.md /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0047-three-layer-enforcement.md /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0048-prior-context-handoff.md /workspaces/feature-pipeline/working/feature/issue-capture-mechanism-r1/adrs/ADR-0049-structural-vs-discipline-kb-split.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(grep -A 15 "## Decision$" /workspaces/feature-pipeline/adrs/ADR-0017-document-reviewer-integration.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.
- **[MAJOR]** Permission rule 'Bash(grep -A 15 "## Decision$" /workspaces/feature-pipeline/adrs-migrated/ADR-0009-rationale-brief-discipline.md)' has quote characters inside parens. The quotes are part of the literal pattern; the rule won't match real tool calls.
  - *Fix:* Remove the inner quotes.

## MCP servers

### .mcp.json

- **[MINOR]** Server 'gitnexus': package `gitnexus@${GITNEXUS_TAG}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MINOR]** Server 'mcp-openapi-schema': package `mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MINOR]** Server 'serena': package `git+https://github.com/oraios/serena@${SERENA_REF}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.

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