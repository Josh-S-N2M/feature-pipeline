# Claude Code Configuration Audit — work

**Audited:** `/home/claude/work`
**Score:** 0.0/100
**Verdict:** SECURITY-BLOCK
**SECURITY-BLOCK in effect** — at least one CRITICAL finding confirmed.

## Inventory

- skills: 37
- context files: 0
- subagents: 31
- subagent memory dirs: 0
- hook scripts: 0
- settings files: 0
- output styles: 0
- MCP configs: 0

## Summary

Total findings: 148
- **BLOCKER**: 77
- **MAJOR**: 42
- **MINOR**: 29

## Skills

### KB-cc-design

- **[BLOCKER]** references/patterns-and-anti-patterns.md links to '.claude/CLAUDE.md' (line 66) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/patterns-and-anti-patterns.md links to '.claude/agents/debug-history/MEMORY.md' (line 200) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### KB-cc-platform

- **[BLOCKER]** references/configuration.md links to '.claude/settings.json' (line 23) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/configuration.md links to '.claude/settings.local.json' (line 23) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/cli-and-headless.md links to '.claude/settings.json' (line 135) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/integrations.md links to '.claude/settings.json' (line 46) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/CLAUDE.md' (line 28) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/rules/frontend/react.md' (line 61) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/commands/deploy.md' (line 124) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/skills/deploy/SKILL.md' (line 124) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/skills/deep-reasoning/SKILL.md' (line 182) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/settings.json' (line 220) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/settings.local.json' (line 220) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude-plugin/plugin.json' (line 378) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/extensions.md links to '.claude/settings.json' (line 412) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/architecture.md links to '.claude/settings.local.json' (line 108) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/architecture.md links to '.claude/settings.json' (line 109) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/architecture.md links to '.claude/CLAUDE.md' (line 128) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/architecture.md links to 'packages/api/CLAUDE.md' (line 132) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[MAJOR]** Modifies CLAUDE.md from within the skill.
  - *Fix:* Skills should not silently rewrite project memory; surface the change to the user.
- **[MAJOR]** Modifies CLAUDE.md from within the skill.
  - *Fix:* Skills should not silently rewrite project memory; surface the change to the user.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.

### KB-codespaces-design

- **[BLOCKER]** references/patterns-and-anti-patterns.md links to '.devcontainer/setup.sh' (line 330) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.

### KB-codespaces-platform

- **[BLOCKER]** SKILL.md links to '.devcontainer/devcontainer.json' (line 81) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/workflows.md links to '.vscode/extensions.json' (line 215) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/workflows.md links to '.devcontainer/devcontainer.json' (line 247) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/devcontainer.md links to '.devcontainer/devcontainer.json' (line 19) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[MAJOR]** References a shell startup file (potential persistence vector).
  - *Fix:* Skills should not modify shell startup files unless that's the skill's stated purpose.
- **[MAJOR]** References a shell startup file (potential persistence vector).
  - *Fix:* Skills should not modify shell startup files unless that's the skill's stated purpose.
- **[MAJOR]** References a shell startup file (potential persistence vector).
  - *Fix:* Skills should not modify shell startup files unless that's the skill's stated purpose.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).
  - *Fix:* Skills should not read credential files unless the user has explicitly approved it for this skill's purpose.
- **[BLOCKER]** Reads a credential-shaped environment variable.
  - *Fix:* Verify the credential is necessary and only used locally; never include in URLs or external requests.

### KB-documentation-criteria

- **[BLOCKER]** references/layer-taxonomy.md links to '.claude/commands/deploy.md' (line 146) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/blueprint-template.md links to '.devcontainer/devcontainer.json' (line 712) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/templates/blueprint-template.md links to '.devcontainer/docker-compose.yml' (line 714) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### KB-github-actions-platform

- **[BLOCKER]** SKILL.md links to 'composite-action/action.yml' (line 141) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/recipe-python.md links to 'script.py' (line 377) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/migration.md links to '.circleci/config.yml' (line 34) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/reusable-workflows-and-actions.md links to 'dist/index.js' (line 240) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/reusable-workflows-and-actions.md links to 'dist/index.js' (line 332) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** scripts/action_versions.md links to '.github/labeler.yml' (line 46) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Reads a credential-shaped environment variable.
  - *Fix:* Verify the credential is necessary and only used locally; never include in URLs or external requests.
- **[BLOCKER]** Prompt-injection phrase: 'ignore previous instructions'.
  - *Fix:* Remove the phrase. Skills should not instruct Claude to override prior context.
- **[BLOCKER]** Reads a credential-shaped environment variable.
  - *Fix:* Verify the credential is necessary and only used locally; never include in URLs or external requests.
- **[MAJOR]** Long base64-looking string in skill content.
  - *Fix:* Decode and inspect. Legitimate skills rarely need embedded encoded payloads.
- **[MAJOR]** Long base64-looking string in skill content.
  - *Fix:* Decode and inspect. Legitimate skills rarely need embedded encoded payloads.
- **[BLOCKER]** Pipes downloaded content directly into a shell.
  - *Fix:* Never legitimate. Even for installers, instruct the user to download, inspect, then run.
- **[BLOCKER]** Prompt-injection phrase: 'ignore previous instructions'.
  - *Fix:* Remove the phrase. Skills should not instruct Claude to override prior context.

### report-composition-knowledge

- **[BLOCKER]** SKILL.md links to 'output/constraint-aware-synthesis.md' (line 28) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to 'output/ai-research-synthesis-report.md' (line 29) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** SKILL.md links to 'skills/synthesize/references/substrate-registry.md' (line 30) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/examples.md links to 'output/auth-research.md' (line 9) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'output/caching-survey.md' (line 9) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'output/auth-research.md' (line 13) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'output/auth-research.md' (line 17) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/examples.md links to 'output/caching-survey.md' (line 17) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/anti-patterns.md links to 'u1' (line 29) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/anti-patterns.md links to 'u2' (line 29) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/anti-patterns.md links to 'u3' (line 29) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.

### synthesize

- **[BLOCKER]** SKILL.md links to 'working/synthesis/run-index.md' (line 307) but the file does not exist (Reference Illusion).
  - *Fix:* Either create the file, inline the content into SKILL.md, or remove the broken link.
- **[BLOCKER]** references/substrate-registry.md links to 'output/constraint-aware-synthesis.md' (line 28) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/substrate-registry.md links to 'commands/synthesize.md' (line 41) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/substrate-registry.md links to 'skills/synthesize/SKILL.md' (line 48) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/substrate-registry.md links to 'commands/synthesize.md' (line 79) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/validators/json-schema-validator.md links to 'skills/synthesize/SKILL.md' (line 3) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[BLOCKER]** references/validators/json-schema-validator.md links to 'skills/synthesize/references/schemas/claim.schema.json' (line 15) but the file does not exist.
  - *Fix:* Either create the file or fix/remove the link.
- **[MAJOR]** Long base64-looking string in skill content.
  - *Fix:* Decode and inspect. Legitimate skills rarely need embedded encoded payloads.
- **[MAJOR]** Long base64-looking string in skill content.
  - *Fix:* Decode and inspect. Legitimate skills rarely need embedded encoded payloads.

## Subagents and their memory

### design-api.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-backend.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-cicd.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-claude-code.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.
- **[BLOCKER]** Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)
  - *Fix:* Remove the instruction. The subagent must request approval when permissionMode requires it.

### design-codespaces.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-composer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-database.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-frontend.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### design-iac.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.
- **[BLOCKER]** Body instructs subagent to remember credentials. (SAM-1 / memory poisoning)
  - *Fix:* Remove the instruction. Subagents must refuse to persist credentials.

### design-query.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### discovery-codebase-researcher.md

- **[MAJOR]** Wildcard shell tool: `Bash`. Subagent has full shell access. (SA-3)
  - *Fix:* Scope to specific commands, e.g. `Bash(git diff *)`, `Bash(npm test *)`.
- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### discovery-external-researcher.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### discovery-plan-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### finalize-reconciler.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.
- **[BLOCKER]** Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)
  - *Fix:* Remove the instruction. The subagent must request approval when permissionMode requires it.

### finalize-task-decomposer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### intake-intent-clarifier.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### intake-prd-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### plan-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### review-architecture-auditor.md

- **[MAJOR]** Wildcard shell tool: `Bash`. Subagent has full shell access. (SA-3)
  - *Fix:* Scope to specific commands, e.g. `Bash(git diff *)`, `Bash(npm test *)`.
- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### review-cross-artifact-auditor.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.
- **[MAJOR]** Body references tools ['Bash'] not in declared `tools:` list.
  - *Fix:* Add the tools to `tools:` (with scoping) or remove the body references.
- **[BLOCKER]** Body instructs subagent to bypass approval/safety prompts. (Prompt injection / SA-4 indicator)
  - *Fix:* Remove the instruction. The subagent must request approval when permissionMode requires it.

### shared-document-reviewer.md

- **[MAJOR]** Wildcard shell tool: `Bash`. Subagent has full shell access. (SA-3)
  - *Fix:* Scope to specific commands, e.g. `Bash(git diff *)`, `Bash(npm test *)`.
- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-critic.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-extractor.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-framer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-grapher.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-substrate.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### synth-synthesizer.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### test-acceptance-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

### test-phase-validator-author.md

- **[MAJOR]** Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)
  - *Fix:* Add explicit trigger: 'Use when ...' or 'Use for ...'.

## Cross-file checks

- **[MINOR] X9** — Subagent design-api.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-backend.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-cicd.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-claude-code.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-codespaces.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-composer.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-database.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-frontend.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-iac.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent design-query.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent discovery-codebase-researcher.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent discovery-external-researcher.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent discovery-plan-author.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent finalize-deliverable-packager.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent finalize-reconciler.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent finalize-task-decomposer.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent intake-intent-clarifier.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent intake-prd-author.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent plan-author.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent review-architecture-auditor.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent review-cross-artifact-auditor.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-critic.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-extractor.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-framer.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-grapher.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-substrate.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent synth-synthesizer.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent test-acceptance-author.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.
- **[MINOR] X9** — Subagent test-phase-validator-author.md preloads skills. Verify each listed skill's security audit passes (X9 full check requires running auditing-skills on each).
  - *Fix:* For each skill in the list, ensure it passes auditing-skills with no SECURITY-BLOCK verdict.

## How to read this report

Severity meanings:

- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.
- **MAJOR** — works but degrades behavior or security.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.


Report-only: this audit does not modify any audited file.