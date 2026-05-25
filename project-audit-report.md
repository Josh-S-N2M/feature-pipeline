# Claude Code Configuration Audit — feature-pipeline

**Audited:** `/workspaces/feature-pipeline`
**Score:** 0.0/100
**Verdict:** SECURITY-BLOCK
**SECURITY-BLOCK in effect** — at least one CRITICAL finding confirmed.

## Inventory

- skills: 45
- context files: 0
- subagents: 37
- subagent memory dirs: 23
- hook scripts: 2
- settings files: 2
- output styles: 0
- MCP configs: 1

## Summary

Total findings: 161
- **BLOCKER**: 86
- **MAJOR**: 56
- **MINOR**: 19

## Skills

### KB-documentation-criteria

- **[BLOCKER]** SKILL.md links to 'auditing-shared/scripts/log_state_transition.py' (line 71) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/issue-doctypes-spec.md links to 'Issues/adr-placement-rootcause/analysis.md' (line 77) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/issue-doctypes-spec.md links to 'Issues/adr-placement-rootcause/analysis.md' (line 228) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/issue-doctypes-spec.md links to 'Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md' (line 230) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/issue-doctypes-spec.md links to 'Issues/auditing-family-graduation-review/proposal.md' (line 232) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/issue-doctypes-spec.md links to '.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py' (line 294) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/shared-conventions.md links to 'working/feature/planning-agent-doctype-backfill-r1/intent-clarification.md' (line 307) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 71) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 90) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/state-transitions-log-entry-template.md links to 'recipe-feature-pipeline/SKILL.md' (line 100) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-register-template.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md' (line 96) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-register-template.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0050-5-state-issues-vocabulary.md' (line 99) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-register-template.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 100) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-analysis-template.md links to 'Issues/analysis-per-agent-design-evaluation-gap.md' (line 63) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-analysis-template.md links to 'Issues/analysis-adr-placement-rootcause.md' (line 63) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-analysis-template.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 101) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/issue-proposal-template.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 97) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### KB-issue-capture

- **[BLOCKER]** `description` contains XML-style tags, which are not allowed.
  - *Fix:* Remove any `<...>` tags from the description.
- **[BLOCKER]** `name` ('KB-issue-capture') contains characters other than lowercase letters, digits, and hyphens.
  - *Fix:* Use only lowercase letters, digits, and hyphens.
- **[BLOCKER]** references/non-pollution-contract.md links to '.claude/agents/issue-capture-author.md' (line 36) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to '.claude/settings.json' (line 53) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'Issues/per-agent-design-evaluation-gap/analysis.md' (line 76) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'Issues/adr-placement-rootcause/analysis.md' (line 83) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md' (line 103) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md' (line 105) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0047-three-layer-enforcement.md' (line 108) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0049-structural-vs-discipline-kb-split.md' (line 110) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0050-5-state-issues-vocabulary.md' (line 113) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'Issues/per-agent-design-evaluation-gap/analysis.md' (line 117) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/non-pollution-contract.md links to 'Issues/adr-placement-rootcause/analysis.md' (line 118) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/non-pollution-contract.md is 118 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 9) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md' (line 10) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md' (line 11) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md' (line 12) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md' (line 71) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md' (line 89) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md' (line 109) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-issue-capture/references/examples.md' (line 149) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md' (line 151) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md' (line 152) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md' (line 153) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/triage-criteria.md links to '.claude/skills/KB-issue-capture/references/approval-prompt-rubric.md' (line 159) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/triage-criteria.md is 159 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.
- **[BLOCKER]** references/examples.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 15) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md' (line 21) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'devcontainer-mcp-provisioning-r1-deferrals/register.md' (line 92) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'Issues/adr-placement-rootcause/analysis.md' (line 100) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'Issues/per-agent-design-evaluation-gap/analysis.md' (line 102) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'Issues/adr-placement-rootcause/proposal.md' (line 125) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'adr-placement-rootcause/analysis.md' (line 192) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'Issues/auditing-family-graduation-review/proposal.md' (line 201) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'auditing-family-graduation-review/proposal.md' (line 286) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to '.claude/skills/KB-issue-capture/references/triage-criteria.md' (line 304) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to '.claude/skills/KB-issue-capture/references/approval-prompt-rubric.md' (line 307) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/approval-prompt-rubric.md links to '.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md' (line 160) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/approval-prompt-rubric.md is 160 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.

### KB-mcp-design

- **[BLOCKER]** `description` contains XML-style tags, which are not allowed.
  - *Fix:* Remove any `<...>` tags from the description.
- **[MINOR]** Unrecognized frontmatter field(s): ['family']. These are silently ignored.
  - *Fix:* Remove them, or check for typos (e.g. `descripton` instead of `description`).
- **[BLOCKER]** references/principles.md links to '.devcontainer/lib/log-mcp-event.sh' (line 51) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MINOR]** references/patterns-and-anti-patterns.md is 179 lines but has no recognized table-of-contents heading near the top.
  - *Fix:* Add a heading like `## Contents`, `## Table of contents`, `## In this file`, `## On this page`, or `## Sections` listing the file's sections. The property is navigable-index-near-the-top, not a specific heading string.

### KB-mcp-platform

- **[MINOR]** Unrecognized frontmatter field(s): ['family']. These are silently ignored.
  - *Fix:* Remove them, or check for typos (e.g. `descripton` instead of `description`).
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

- **[MINOR]** Unrecognized frontmatter field(s): ['family']. These are silently ignored.
  - *Fix:* Remove them, or check for typos (e.g. `descripton` instead of `description`).
- **[BLOCKER]** Instruction to append a credential to a URL or query parameter.
  - *Fix:* Credentials must never be sent in URLs.

### capture-issue

- **[BLOCKER]** Frontmatter failed to parse as YAML: mapping values are not allowed here
  in "<unicode string>", line 2, column 242:
     ... ent via Task. Mutually exclusive: create-mode positional hint XO ... 
                                         ^
  - *Fix:* Fix the YAML syntax. Common causes: unquoted colons in values, missing quotes around special chars.
- **[BLOCKER]** SKILL.md links to '.claude/agents/issue-capture-author.md' (line 42) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.claude/skills/KB-issue-capture/SKILL.md' (line 43) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to 'working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md' (line 44) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to '.../adrs/ADR-0047-three-layer-enforcement.md' (line 45) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.

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

### execute-task-code-producer.md

- **[MAJOR]** Wildcard shell tool: `Bash`. Subagent has full shell access. (SA-3)
  - *Fix:* Scope to specific commands, e.g. `Bash(git diff *)`, `Bash(npm test *)`.

### execute-task-quality-handler.md

- **[MAJOR]** Wildcard shell tool: `Bash`. Subagent has full shell access. (SA-3)
  - *Fix:* Scope to specific commands, e.g. `Bash(git diff *)`, `Bash(npm test *)`.

### issue-capture-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.
- **[MAJOR]** Body references tools ['Bash', 'Edit'] not in declared `tools:` list.
  - *Fix:* Add the tools to `tools:` (with scoping) or remove the body references.
- **[BLOCKER]** Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)
  - *Fix:* Remove the instruction. The subagent must request approval when permissionMode requires it.
- **[BLOCKER]** Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)
  - *Fix:* Remove the instruction. The subagent must request approval when permissionMode requires it.

## Hooks

### settings.json (hooks)

- **[BLOCKER]** Hook command references script that does not exist: /workspaces/feature-pipeline/.claude/${CLAUDE_PROJECT_DIR}/.claude/hooks/intercept-issue-capture-agent.sh. (HK-5 / cross-file X1)
  - *Fix:* Create the script or remove the hook entry.

## Settings

### settings.json

- **[MAJOR]** Bare tool name 'Bash' in 'allow' is equivalent to 'Bash(*)'. (ST-9)
  - *Fix:* Add scoping: 'Bash(<pattern>)'.
- **[MAJOR]** Bare tool name 'Read' in 'allow' is equivalent to 'Read(*)'. (ST-9)
  - *Fix:* Add scoping: 'Read(<pattern>)'.
- **[MAJOR]** Bare tool name 'Edit' in 'allow' is equivalent to 'Edit(*)'. (ST-9)
  - *Fix:* Add scoping: 'Edit(<pattern>)'.
- **[MAJOR]** Bare tool name 'Write' in 'allow' is equivalent to 'Write(*)'. (ST-9)
  - *Fix:* Add scoping: 'Write(<pattern>)'.
- **[MAJOR]** Bare tool name 'NotebookEdit' in 'allow' is equivalent to 'NotebookEdit(*)'. (ST-9)
  - *Fix:* Add scoping: 'NotebookEdit(<pattern>)'.
- **[MAJOR]** Bare tool name 'Glob' in 'allow' is equivalent to 'Glob(*)'. (ST-9)
  - *Fix:* Add scoping: 'Glob(<pattern>)'.
- **[MAJOR]** Bare tool name 'Grep' in 'allow' is equivalent to 'Grep(*)'. (ST-9)
  - *Fix:* Add scoping: 'Grep(<pattern>)'.
- **[MAJOR]** Bare tool name 'WebFetch' in 'allow' is equivalent to 'WebFetch(*)'. (ST-9)
  - *Fix:* Add scoping: 'WebFetch(<pattern>)'.
- **[MINOR]** Permission rule references unknown tool 'AskUserQuestion' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MAJOR]** Permission rule 'mcp__gitnexus__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__serena__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__actionlint-mcp__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__mcp-openapi-schema__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__context7__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__exa__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__*' (in 'allow') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__create_run' (in 'deny') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__apply_run' (in 'deny') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__discard_run' (in 'deny') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__cancel_run' (in 'deny') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.
- **[MAJOR]** Permission rule 'mcp__terraform-mcp__delete_workspace_safely' (in 'deny') has unrecognized syntax.
  - *Fix:* Use `Tool(pattern)` format. See permission-rules-spec.md.

### settings.local.json

- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write
- **[MINOR]** Permission rule references unknown tool 'Skill' (in 'allow').
  - *Fix:* Check spelling. Known: Bash, Edit, Glob, Grep, NotebookEdit, Read, Task, WebFetch, WebSearch, Write

## MCP servers

### .mcp.json

- **[MINOR]** Server 'gitnexus': package `gitnexus@${GITNEXUS_TAG}` is not in the known-publishers list. Review provenance. (MC-3)
  - *Fix:* Verify publisher. For third-party servers, read source before installing.
- **[MAJOR]** 
- **[MAJOR]** 
- **[MAJOR]** 

## Cross-file checks

- **[BLOCKER] X1** — Hook 'PreToolUse' command references script '${CLAUDE_PROJECT_DIR}/.claude/hooks/intercept-issue-capture-agent.sh' which does not exist.
  - *Fix:* Create the script or remove the hook entry.
- **[MAJOR] X9** — Subagent design-api.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-backend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'auditing-github-actions' whose audit verdict is FAIL (2 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-github-actions; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-cicd.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-claude-code.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-codespaces.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-composer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-database.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-frontend.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-iac.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent design-query.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-external-researcher.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent discovery-plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-finalize-reconciler.md preloads skill 'auditing-shared' whose audit verdict is WARN (1 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-shared; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-orchestrator.md preloads skill 'recipe-feature-pipeline' whose audit verdict is FAIL (21 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/recipe-feature-pipeline; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-orchestrator.md preloads skill 'auditing-shared' whose audit verdict is WARN (1 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-shared; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-phase-quality-reviewer.md preloads skill 'auditing-shared' whose audit verdict is WARN (1 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-shared; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent execute-task-quality-handler.md preloads skill 'auditing-shared' whose audit verdict is WARN (1 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/auditing-shared; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-deliverable-packager.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-reconciler.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent finalize-task-decomposer.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-intent-clarifier.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent intake-prd-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent plan-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-architecture-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent review-cross-artifact-auditor.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-acceptance-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.
- **[MAJOR] X9** — Subagent test-phase-validator-author.md preloads skill 'KB-documentation-criteria' whose audit verdict is FAIL (40 findings).
  - *Fix:* Review findings at /workspaces/feature-pipeline/.claude/skills/KB-documentation-criteria; either remediate or accept the risk in a security-exemption note.

## How to read this report

Severity meanings:

- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.
- **MAJOR** — works but degrades behavior or security.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.


Report-only: this audit does not modify any audited file.