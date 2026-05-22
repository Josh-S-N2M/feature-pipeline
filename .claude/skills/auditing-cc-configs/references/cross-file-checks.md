# Cross-File Pair Checks

## Contents

- The 24 checks: X1 through X24
- Per-pair group: hooks ↔ scripts
- Settings ↔ permissions
- Subagent ↔ memory
- MCP ↔ toxic matrix

The 24 checks that fire after per-target audits complete. They detect interactions that no single-file audit can. Lives in `scripts/cross_file_checks.py`; runs as step 5 of the audit loop.

Each check examines a *pair* (or small set) of configuration artifacts and emits a finding if the interaction is problematic. Findings count toward the project-level verdict via the cross-file overlay rule (see `audit-rubric.md`).

## How cross-file checks work

The coordinator collects all audit targets and their findings into a single project state object. Each check is a function that takes the state and returns zero or more findings. Findings have the same shape as per-target findings: severity, location, what, fix.

Some checks need filesystem access beyond the audit targets (e.g., checking `.gitignore`, checking that hook scripts exist on disk). The coordinator provides this; sub-skills don't need to coordinate among themselves.

## The 24 checks

### Hook ↔ Settings

**X1 — settings.json references hook script that doesn't exist on disk**
- Severity: **BLOCKER**
- Pair: settings.json (any scope) ↔ filesystem
- Detection: walk all `hooks.<event>.[].hooks[].command` entries; resolve path; check existence
- Fix: create the script, or remove the hook entry

**X4 — Multiple hooks on same event with order dependency**
- Severity: **MINOR**
- Pair: hook (multiple) ↔ same event
- Detection: scan hook script bodies for comments like "must run before X" or "depends on Y"; parallel execution doesn't guarantee order
- Fix: merge into a single hook script that runs steps in order, or document that order doesn't matter

**X12 — Hook does pure string-matching that could be a permission rule**
- Severity: **MINOR**
- Pair: hook ↔ permissions.allow/deny
- Detection: hook script reads `tool_input.command` and grep-matches against a literal string; could be expressed as `Bash(<pattern>)` deny rule
- Fix: move to `permissions.deny` for zero-cost enforcement (cc-expert: "Use permissions first")
- cc-expert rationale: hooks have a process-spawn cost; permission rules are free

**X15 — Project settings.json references user-only hook script**
- Severity: **MAJOR**
- Pair: project settings.json ↔ hook path
- Detection: hook command path starts with `~/.claude/hooks/` or `$HOME/.claude/hooks/` but the setting is in project scope
- Fix: move the script to `.claude/hooks/` (committed), or move the setting to user scope, or document the per-developer assumption

### Settings ↔ Subagents / Skills

**X2 — Subagent bypassPermissions vs managed disableBypassPermissionsMode**
- Severity: **MAJOR** (informational — managed wins)
- Pair: subagent (any scope) ↔ managed-settings.json
- Detection: subagent frontmatter has `permissionMode: bypassPermissions` AND managed settings have `permissions.disableBypassPermissionsMode: "disable"`
- Fix: remove `permissionMode: bypassPermissions` from subagent (will silently fail anyway); or, if the subagent legitimately needs bypass, escalate to managed policy review

**X3 — Skill allowed-tools includes settings-denied tool**
- Severity: **MINOR**
- Pair: skill frontmatter ↔ settings.json permissions
- Detection: skill has `allowed-tools: Bash(...)` but settings denies a matching pattern
- Fix: remove the dead allowance from the skill, or revise the deny rule

**X9 — Subagent skills: list includes SECURITY-BLOCK skill**
- Severity: **BLOCKER**
- Pair: subagent frontmatter ↔ audited skills
- Detection: subagent `skills:` lists a skill that has SECURITY-BLOCK verdict in the same audit
- Fix: remove from `skills:` list until the underlying skill is remediated

**X17 — Subagent model alias unrecognized**
- Severity: **MAJOR**
- Pair: subagent frontmatter ↔ model registry
- Detection: `model:` value not in {`sonnet`, `opus`, `haiku`, `inherit`} and not a full model ID
- Fix: use a valid alias or remove the field (inherits default)

### Settings ↔ Output Styles

**X14 — settings.json outputStyle references nonexistent style**
- Severity: **BLOCKER**
- Pair: settings.json ↔ filesystem
- Detection: `outputStyle: <name>` set, but no `.claude/output-styles/<name>.md` or `~/.claude/output-styles/<name>.md`
- Fix: create the style file, or remove the outputStyle setting

### Settings ↔ Settings (scope interactions)

**X8 — Same key in user vs project settings (shadow/redundant)**
- Severity: **INFO** if different values, **MINOR** if redundant
- Pair: ~/.claude/settings.json ↔ .claude/settings.json
- Detection: same top-level key in both with same value (redundant) or different values (intentional shadowing — INFO only)
- Fix: remove redundant entry, or document why both are set

**X10 — settings.local.json present but not gitignored**
- Severity: **MAJOR**
- Pair: the project's settings.local.json file ↔ .gitignore
- Detection: file exists but path not matched by any .gitignore rule
- Fix: add the path to .gitignore

**X22 — autoMemoryDirectory in project or local settings (silently ignored)**
- Severity: **MAJOR**
- Pair: settings.json (project or local) ↔ setting scope rules
- Detection: `autoMemoryDirectory` key appears in a project or local settings.json (per docs, user-scope only)
- Fix: move to the user-scope settings.json file, or remove

### CLAUDE.md ↔ Rules / Imports

**X6 — CLAUDE.md vs rules duplication**
- Severity: **MINOR**
- Pair: CLAUDE.md ↔ .claude/rules/*.md
- Detection: same rule (substring match >40 chars, normalized whitespace) appears in both
- Fix: keep one canonical copy; remove from the other

**X7 — CLAUDE.md vs paths-rules overlap**
- Severity: **MINOR**
- Pair: CLAUDE.md ↔ .claude/rules/*.md with `paths:` frontmatter
- Detection: rule in CLAUDE.md applies to paths that a paths-rule also covers; CLAUDE.md loads always, paths-rule loads conditionally — same rule gets double-applied for matching files
- Fix: move the rule entirely into the paths-rule and remove from CLAUDE.md

**X16 — CLAUDE.md @-imports outside project**
- Severity: **MAJOR**
- Pair: CLAUDE.md ↔ @-import targets
- Detection: `@/absolute/path/...` or `@~/something` resolves outside the project root
- Fix: copy the imported file into the project, or document that this skill is single-machine-only

### Memory checks

**X13 — Subagent memory: declaration vs MEMORY.md / .gitignore**
- Severity: **MAJOR**
- Pair: subagent frontmatter ↔ filesystem ↔ .gitignore
- Detection:
  - `memory: project` declared but `.claude/agent-memory/<name>/MEMORY.md` doesn't exist (INFO — Claude creates lazily) **or**
  - `memory: local` declared but `.claude/agent-memory-local/` not in `.gitignore` (MAJOR)
- Fix: ensure .gitignore covers `.claude/agent-memory-local/`

**X19 — MEMORY.md and CLAUDE.md duplicate rule**
- Severity: **MINOR**
- Pair: MEMORY.md (auto or subagent) ↔ CLAUDE.md
- Detection: same rule substring (>40 chars, normalized) in both
- Fix: keep in CLAUDE.md (canonical, version-controlled); remove from MEMORY.md (or let Claude prune naturally)

**X20 — Subagent declares memory: but disallowedTools blocks Write/Edit**
- Severity: **MAJOR**
- Pair: subagent frontmatter (memory field) ↔ subagent frontmatter (disallowedTools field)
- Detection: `memory: <any>` set AND `disallowedTools:` contains Write or Edit
- Fix: remove Write/Edit from disallowedTools, or remove the memory field (one of the two must give)

**X21 — Orphan agent-memory directories**
- Severity: **MINOR**
- Pair: filesystem (agent-memory dirs) ↔ subagent definitions
- Detection: `.claude/agent-memory/<name>/` or `~/.claude/agent-memory/<name>/` exists but no subagent named `<name>` in the same scope has `memory: <scope>` declared
- Fix: remove the orphan directory, or define the subagent

**X23 — agent-memory-local not in .gitignore**
- Severity: **MAJOR**
- Pair: filesystem ↔ .gitignore
- Detection: `.claude/agent-memory-local/` exists or any subagent declares `memory: local`, but `.gitignore` doesn't cover the path
- Fix: add `.claude/agent-memory-local/` to `.gitignore`

**X24 — MEMORY.md committed with machine-local paths**
- Severity: **MAJOR**
- Pair: MEMORY.md ↔ git ↔ content
- Detection: MEMORY.md is tracked by git AND contains absolute paths like `/home/<user>/`, `/Users/<user>/`, `C:\\Users\\...`
- Fix: prune the machine-local paths from MEMORY.md, or move to a non-committed memory scope

### MCP ↔ MCP

**X5 — MCP toxic-combinations across configured servers**
- Severity: **CRITICAL** for pair types 3/6 (secret+network, shell+network); **MAJOR** for 1/2/4/5; **MINOR** for 7
- Pair: MCP servers in same scope (project, user, or merged effective set)
- Detection: capability-tag every server (FILE_READ, NETWORK_OUT, SHELL_EXEC, DATABASE, SECRETS, EMAIL, GIT); check every pair against the TOXIC matrix
- Reference: see the auditing-mcp sibling skill's toxic-combinations reference for the TOXIC matrix
- Fix: remove one of the pair, or isolate them to different sessions

**X11 — Hook references unconfigured MCP tool**
- Severity: **MINOR**
- Pair: hook script ↔ .mcp.json
- Detection: hook command pipes into or references `mcp__<server>__<tool>` syntax for a server not in .mcp.json
- Fix: configure the MCP server, or remove the reference

### Override-vs-additive conflicts

**X18 — Same-named primitive at multiple scopes**
- Severity: **MINOR** (dead-rule warning) or **INFO** (intentional shadowing)
- Pair: any override-type primitive at multiple scopes
- Detection:
  - Override primitives (skill, subagent, MCP server): same name at project and user — project wins, user is shadowed
  - Additive primitives (hook, CLAUDE.md): same content at multiple scopes — fires twice (hooks) or wastes tokens (CLAUDE.md)
- Reference: see `additive-vs-override.md`
- Fix: remove from the losing scope; or, if intentional, document why both exist

## Aggregation rule

Project-level score is the **lower** of:
- (a) Weighted average of per-target scores
- (b) Score implied by cross-file findings alone (starting at 100, each cross-file BLOCKER −12, MAJOR −5, MINOR −2, NIT −0.5)

This prevents a clean per-target audit from hiding dangerous cross-file interactions. A project with all clean targets but two cross-file BLOCKERs lands at 76 (NEEDS-WORK).

## Report structure

Cross-file findings appear in their own report section, separate from per-target findings:

```markdown
## Cross-file findings (24 checks run)

### X5 — MCP toxic combination
- Severity: CRITICAL
- Servers: `filesystem-mcp` (FILE_READ) + `http-mcp` (NETWORK_OUT)
- Pair type: TOXIC-001
- Fix: remove one of the two, or limit to non-sensitive workloads

### X10 — settings.local.json not gitignored
- Severity: MAJOR
- File: .claude/settings.local.json
- Fix: add `.claude/settings.local.json` to .gitignore
```

The full report template handles this section automatically when fed cross-file findings JSON.
