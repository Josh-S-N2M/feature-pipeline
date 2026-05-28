# Extensions reference

> **Canonical source.** Where this reference lists hook **event names**, the authoritative enumeration is [`.claude/canonical/hook-events.yaml`](../../../canonical/hook-events.yaml) (loaded by `canonical.py`; per ADR-0068). The names here mirror that file — if they disagree, the YAML wins. Per KB-cc-design Principle 11, do not duplicate the event enumeration without a reference back to the canonical source.

The seven extension primitives plus output styles. This is the load-bearing reference for designing, reviewing, and refactoring Claude Code setups.

Each section follows the same structure: what it is, where it lives, when it loads, frontmatter schema, common patterns, pitfalls, and pointers to the official docs page for current detail.

## Table of contents

1. [CLAUDE.md — persistent context](#1-claudemd--persistent-context)
2. [Rules — topic-scoped or path-scoped instructions](#2-rules--topic-scoped-or-path-scoped-instructions)
3. [Skills — reusable knowledge and invocable workflows](#3-skills--reusable-knowledge-and-invocable-workflows)
4. [Subagents — isolated context windows](#4-subagents--isolated-context-windows)
5. [Hooks — deterministic lifecycle scripts](#5-hooks--deterministic-lifecycle-scripts)
6. [MCP servers — external tools and data](#6-mcp-servers--external-tools-and-data)
7. [Plugins — packaging and distribution](#7-plugins--packaging-and-distribution)
8. [Output styles — system-prompt modifications](#8-output-styles--system-prompt-modifications)
9. [Choosing between similar primitives](#choosing-between-similar-primitives)
10. [Layering and precedence](#layering-and-precedence)

---

## 1. CLAUDE.md — persistent context

**What it is.** A markdown file Claude reads at the start of every session. Use it for project conventions, build commands, architecture decisions, and "always do X" rules.

**Where it lives.**
- `CLAUDE.md` at project root (committed, team-shared)
- `.claude/CLAUDE.md` (alternative project location if you prefer to keep root clean)
- `~/.claude/CLAUDE.md` (global, applies to every project)
- `CLAUDE.local.md` at project root (personal, gitignored — create manually and add to `.gitignore`)

**When it loads.** Session start. Full content of all CLAUDE.md files at every level loads into context simultaneously. Files in subdirectories load when Claude accesses files in those subdirectories. All levels are **additive** — they do not override each other; Claude reconciles conflicts using judgment, with more specific (deeper) instructions typically winning.

**Imports.** CLAUDE.md supports `@path` imports to pull in other markdown files. Useful for splitting large files without losing the always-on guarantee.

**Size guideline.** Keep under 200 lines. Longer files still load in full but the model adheres less reliably as it grows. When CLAUDE.md approaches 200 lines, split into rules (`.claude/rules/`) or move reference content to skills.

**What belongs here:**
- Build, test, lint commands the user runs frequently
- Tech stack and framework conventions
- File layout and naming conventions
- "Never do X" hard rules
- Code style preferences

**What does not belong here:**
- Reference material the model only needs sometimes (use skills)
- File-type-specific guidance like test conventions (use rules with `paths:`)
- Workflows the user triggers (use skills)
- Anything that needs to be enforced rather than suggested (use hooks or `permissions.deny`)

```audit-example -- Documents the /memory slash-command (a user-facing feature for opening the memory file in their preferred external editor). The auditor's MP-1 scanner uses a regex matching the keyword set on the left (the verbs that trigger) within thirty characters of the canonical filename it protects on the right; this paragraph is meta-documentation describing where that user-invoked feature surfaces, not an instruction Claude executes.
**In-session editing.** Run `/memory` inside Claude Code to open and edit CLAUDE.md. `/memory` also shows which CLAUDE.md and rules files are currently loaded.
```

See template: `assets/templates/CLAUDE.md.example`. Docs: `https://code.claude.com/docs/en/memory.md`.

---

## 2. Rules — topic-scoped or path-scoped instructions

**What it is.** Modular instruction files in `.claude/rules/` (or `~/.claude/rules/` for user-global). Same role as CLAUDE.md — guidance Claude reads — but split by topic and optionally gated to specific file paths.

**Where it lives.** `.claude/rules/*.md`, with subdirectories supported (e.g. `.claude/rules/frontend/react.md` is discovered automatically).

**When it loads.**
- Without `paths:` frontmatter — at session start, like CLAUDE.md
- With `paths:` frontmatter — only when Claude reads a file matching one of the globs

**Frontmatter:**
```yaml
---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
---
```

**Why use rules instead of CLAUDE.md.** Two reasons. First, organization — splitting code style, testing, security, and API conventions into separate files is easier to maintain than a single 400-line CLAUDE.md. Second, context savings — `paths:`-gated rules only consume tokens when relevant files are in play, which is a meaningful win for large repos.

**Pattern: convert a fat CLAUDE.md.** When CLAUDE.md grows past 200 lines, the typical refactor is to keep the top-level conventions (build commands, tech stack, hard rules) in CLAUDE.md and move the rest into `.claude/rules/` files. Path-specific guidance (test conventions, API design, frontend patterns) gets `paths:` globs; project-wide topical guidance (security review checklist, commit format) loads unconditionally.

See template: `assets/templates/rules-example.md`. Docs: `https://code.claude.com/docs/en/memory.md` (rules section).

---

## 3. Skills — reusable knowledge and invocable workflows

**What it is.** The most flexible extension. A skill is a folder containing `SKILL.md` plus any supporting files. Skills can be invoked by the user with `/<name>` or auto-loaded by Claude when relevant.

**Where it lives.**
- `.claude/skills/<name>/SKILL.md` (project, committed)
- `~/.claude/skills/<name>/SKILL.md` (user, global)
- Plugin skills are namespaced as `/<plugin>:<name>` to prevent conflicts

**When it loads.**
- Descriptions load at session start so Claude can decide when to invoke (low cost)
- Full content loads when invoked — by the user typing `/<name>`, by Claude matching the description, or when listed in a subagent's `skills:` field
- With `disable-model-invocation: true`, nothing loads until the user invokes manually (zero cost)

**Frontmatter:**
```yaml
---
description: What this skill does and when Claude should use it
disable-model-invocation: true       # Optional: only the user can invoke
user-invocable: false                # Optional: hide from / menu, Claude can still invoke
allowed-tools: Read, Grep, Bash      # Optional: restrict tools while skill runs
argument-hint: <branch-or-path>      # Optional: shown in / menu autocomplete
model: opus                          # Optional: override model for this skill
---
```

**Two flavors of skill:**
- **Reference skills** provide knowledge (API style guide, schema docs, runbook). Claude loads the content when relevant and uses it as context. The description is the sole determinant of when Claude auto-invokes.
- **Action skills** are workflows the user triggers (`/deploy`, `/review`, `/audit`). Use `disable-model-invocation: true` for actions with side effects to keep Claude from running them autonomously.

**Argument substitution.** `$ARGUMENTS` substitutes everything the user typed after the skill name. `$0`, `$1`, `$2` give positional access. Example: `/deploy staging --dry-run` makes `$ARGUMENTS = "staging --dry-run"`, `$0 = "staging"`, `$1 = "--dry-run"`.

**Bash injection.** A line like `` !`git status` `` runs the shell command and injects its output into the prompt before Claude sees it. Useful for grounding skills in current state. Inside scripts referenced by the skill, use `${CLAUDE_SKILL_DIR}` for the skill's directory path.

**Bundling supporting files.** Skills can bundle reference docs, templates, scripts, anything. The skill directory path is prepended to SKILL.md, so Claude can read bundled files by name (e.g. mentioning `checklist.md` in SKILL.md is enough — Claude knows where to find it).

**Description quality matters a lot.** Claude matches the user's task against skill descriptions to decide which to load. Vague or overlapping descriptions cause two failure modes: missing a skill that would help, and loading the wrong one. Descriptions should explicitly name when to use the skill, not just what it does. Be slightly pushy ("Use this skill whenever the user mentions X, Y, or Z, even if they don't ask for it explicitly") to combat undertriggering.

**Bundled skills.** Claude Code ships with built-in skills like `/simplify`, `/batch`, `/debug`. They work out of the box. Custom skills extend, not replace, these.

**Skills vs commands.** A file at `.claude/commands/deploy.md` creates `/deploy` the same way `.claude/skills/deploy/SKILL.md` does. Skills win when they share a name with a command. New work should be skills because they can bundle files; commands remain supported for compatibility.

**In subagents, skills load differently.** Subagents do not auto-load skills based on description. Instead, skills listed in the subagent's `skills:` frontmatter field are **fully preloaded** into the subagent's context at launch. This is the only way a subagent gets access to skills.

See template: `assets/templates/skill-SKILL.md.example`. Docs: `https://code.claude.com/docs/en/skills.md`.

---

## 4. Subagents — isolated context windows

**What it is.** A specialized agent with its own system prompt, tool access, and context window. Spawned by the main session (or another subagent) for a focused task. Returns a summary back; the work itself stays in the subagent's context.

**Where it lives.** `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (user-global).

**When it loads.** On demand — when the main agent decides to delegate, or when the user `@`-mentions the subagent. A fresh context window opens for the subagent.

**Frontmatter:**
```yaml
---
name: code-reviewer
description: Reviews code for correctness, security, and maintainability
tools: Read, Grep, Glob              # Optional: restrict the subagent's tool access
model: sonnet                        # Optional: override model for this subagent
effort: high                         # Optional: reasoning depth (low/medium/high/xhigh/max)
skills:                              # Optional: skills to fully preload
  - api-style-guide
  - testing-conventions
memory: project                      # Optional: enable persistent memory (see below)
isolation: worktree                  # Optional: run in a git worktree
---
```

The body of the file is the subagent's system prompt.

**What loads into a subagent's context:**
- Its own system prompt (from the body of the agent file)
- The shared system prompt from the parent (cached for efficiency)
- Full content of skills listed in the `skills:` field
- CLAUDE.md and git status, inherited from parent
- Whatever the lead agent passes in the spawn prompt

**What does not load:**
- The parent's conversation history
- Skills the parent invoked
- Auto memory from the parent

This isolation is the point. Use a subagent when the work would otherwise blow up the main context window — reading dozens of files, running long searches, exploring a large module. The main session only sees the summary the subagent returns.

**Tool restriction.** The `tools:` frontmatter limits what the subagent can do. A code-reviewer agent restricted to `Read, Grep, Glob` cannot edit anything by construction — useful when you want guarantees.

### Reasoning configuration: `model:`, `effort:`, and `skills:` are distinct knobs

A common authoring mistake is conflating these three fields. They are independent and control different things:

- **`model:`** picks which Claude model executes the subagent. `sonnet` is the default-bounded choice; `opus` provides deeper reasoning at higher cost and latency; `haiku` is fast and cheap for narrow transformations; `inherit` defers to the parent. The choice is per-subagent — the parent session's model does not constrain the subagent's.
- **`effort:`** controls how eagerly the chosen model spends thinking tokens. Documented values are `low` (minimal thinking, fastest), `medium` (moderate), `high` (deep reasoning), `xhigh` (extended; Opus 4.7 only, falls back to `high` on other models), `max` (maximum effort). Effort is independent of model: a `model: sonnet` subagent with `effort: high` does deeper sonnet-class reasoning; a `model: opus` subagent with `effort: low` economizes on opus's default thoroughness. Source: Claude Code Agent SDK `EffortLevel` literal.
- **`skills:`** preloads domain knowledge — the full content of each named SKILL.md is injected into the subagent's context at spawn. Skills carry rubrics, taxonomies, protocols, conventions. They are **not** a reasoning-depth control.

The trap: authors who want "deeper reasoning" sometimes write `skills: [deep-reasoning, …]` expecting the framework to dial up thinking budget. Claude Code does no such thing — `deep-reasoning` is treated as a literal skill identifier. If no `.claude/skills/deep-reasoning/SKILL.md` exists, the loader silently skips it. The subagent runs with default reasoning and the author's intent is silently lost. The auditing-subagents skill's SA-13 check catches this class of defect (BLOCKER).

Correct mapping of "I want this subagent to reason deeply" → set `model: opus`, OR `effort: high`, OR both, depending on the budget. Never the `skills:` array.

### Persistent memory for subagents

Subagents can have their own persistent memory, distinct from the main session's auto memory. Set `memory:` in frontmatter to one of three scopes:

| Scope | Where stored | Committed? | When to use |
|---|---|---|---|
| `memory: project` | `.claude/agent-memory/<agent-name>/MEMORY.md` | Yes (committed by default) | Knowledge the team shares about how this agent should operate in this project |
| `memory: local` | `.claude/agent-memory-local/<agent-name>/MEMORY.md` | No (auto-gitignored) | Personal notes for an agent in this project |
| `memory: user` | `~/.claude/agent-memory/<agent-name>/MEMORY.md` | No (global) | Knowledge the agent accumulates across all projects |

The first 200 lines (or 25 KB, whichever is smaller) of MEMORY.md load into the subagent's system prompt at start. The subagent reads and writes its own MEMORY.md autonomously — you do not author it. This is the same mechanism as the main session's auto memory, scoped per agent.

### Subagents vs agent teams

Two architecturally different ways to parallelize:

| | Subagent | Agent team |
|---|---|---|
| **Context** | Own window; result returns to caller | Own window; fully independent |
| **Communication** | Reports back to lead only | Teammates message each other directly |
| **Coordination** | Lead manages all work | Shared task list, self-coordinated |
| **Token cost** | Lower (only summary returns) | Higher (each teammate is a full session) |
| **Best for** | Focused tasks where only the result matters | Work needing discussion and competing hypotheses |

Use subagents until you hit the limit where they would need to communicate with each other or share findings — then agent teams are the natural next step. Agent teams are experimental and disabled by default.

See template: `assets/templates/subagent.md.example`. Docs: `https://code.claude.com/docs/en/sub-agents.md` and `https://code.claude.com/docs/en/agent-teams.md`.

---

## 5. Hooks — deterministic lifecycle scripts

**What it is.** Shell commands (or HTTP endpoints) that fire at specific points in the agentic loop. Hooks run **outside** the LLM — they are deterministic, programmable, and the strongest mechanism for enforcing behavior because Claude cannot ignore them.

**Where it lives.** Configured in `settings.json` under the `hooks` key. Project (`.claude/settings.json`), local (`.claude/settings.local.json`), or user-global (`~/.claude/settings.json`). Hooks merge across all sources — every registered hook fires for matching events regardless of source.

**Hook events:**

| Event | Fires when | Common uses |
|---|---|---|
| `PreToolUse` | Before any tool call | Validate/block dangerous commands, auto-approve safe ones |
| `PostToolUse` | After a successful tool call | Lint/format edited files, log usage, send notifications |
| `PostToolUseFailure` | After a failed tool call | Log failures, send alerts |
| `UserPromptSubmit` | When the user sends a prompt | Inject additional context, audit |
| `Notification` | When Claude needs user attention | Forward to Slack, desktop notifier |
| `SessionStart` | At session boot | Set up scratch dirs, log session metadata |
| `SessionEnd` | At session close | Persist state, clean up |
| `Stop` | When the agent loop ends a turn | Run tests, validate state |
| `SubagentStart` | When a subagent spawns | Inject context, log |
| `PermissionRequest` | When a permission prompt would appear | Auto-decide based on custom rules |
| `WorktreeCreate` | When a git worktree is created | Copy gitignored files (alternative to `.worktreeinclude`) |

**Configuration shape.** Hooks attach to events, optionally with a `matcher` to scope which tools trigger them:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/format.sh"
          }
        ]
      }
    ]
  }
}
```

The `matcher` is a regex matched against the tool name. Omit it to match all tools.

**Conditional matching with `if:`.** PreToolUse hooks can use an `if:` condition to match on tool input. Common pattern — block destructive bash commands:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "if": "Bash(rm *)",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
      }]
    }]
  }
}
```

**Hook input/output contract.** A hook receives JSON on stdin describing the event (tool name, tool input, project dir, etc.) and can write JSON to stdout to influence the loop. The most useful output for `PreToolUse`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Dangerous command blocked"
  }
}
```

`permissionDecision` can be `"allow"`, `"deny"`, or `"ask"`. Other useful fields per event:
- `additionalContext` — string to inject into the conversation
- `updatedInput` (PreToolUse) — modified tool arguments
- `updatedMCPToolOutput` (PostToolUse) — modified tool result

**Environment variables in hook commands.**
- `${CLAUDE_PROJECT_DIR}` — absolute path to project root
- `${CLAUDE_PLUGIN_ROOT}` — when the hook is shipped via a plugin

**HTTP hooks.** Instead of `"type": "command"`, use `"type": "http"` with a URL to call out to a service. Useful for centralized policy enforcement.

**Permissions vs hooks.** Both can block tool use. `permissions.deny` rules in `settings.json` are a simple allow-list/deny-list mechanism (see `references/configuration.md`). PreToolUse hooks are more flexible — they can inspect tool input and make dynamic decisions, log, or modify the input before it runs. Use permissions for static rules, hooks for anything dynamic.

See template: `assets/templates/hook-config.json.example`. Docs: `https://code.claude.com/docs/en/hooks.md` (reference) and `https://code.claude.com/docs/en/hooks-guide.md` (guide).

---

## 6. MCP servers — external tools and data

**What it is.** Model Context Protocol servers connect Claude to external systems: databases, browsers, Slack, GitHub, your own internal tools. MCP is an open standard — any compliant server works.

**Where it lives.** Three configuration locations, by scope:
- `.mcp.json` at project root (project scope, committed, team-shared)
- `~/.claude.json` under `mcpServers` key (user scope, applies across all projects)
- `~/.claude.json` under `projects.<path>.mcpServers` (local scope, per-project but not committed)

**Scope precedence:** local > project > user. When the same server name appears at multiple scopes, the most specific wins.

**When it loads.** Servers connect at session start. Tool **names** load at start. Tool **schemas** are deferred and load on demand via tool search — this keeps idle MCP tools from consuming context.

**Four transport types:**

```json
// stdio — most common, runs a local process
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}

// HTTP — for hosted servers
{
  "mcpServers": {
    "stripe": {
      "type": "http",
      "url": "https://mcp.stripe.com",
      "headers": { "Authorization": "Bearer ${API_TOKEN}" }
    }
  }
}

// SSE — Server-Sent Events transport
{
  "mcpServers": {
    "remote": {
      "type": "sse",
      "url": "https://api.example.com/mcp/sse",
      "headers": { "Authorization": "Bearer ${API_TOKEN}" }
    }
  }
}

// SDK — programmatic, used by Agent SDK with create_sdk_mcp_server()
```

`${VAR_NAME}` syntax expands environment variables at startup, so secrets stay out of the file.

**Adding via CLI.** `claude mcp add` interactively adds a server. `claude mcp add --scope user` writes to `~/.claude.json`. `claude mcp add --scope project` writes to `.mcp.json`.

**Tool naming.** Tools from MCP servers appear as `mcp__<server>__<tool>` in `allowedTools` lists. Example: GitHub server's `create_issue` tool is `mcp__github__create_issue`.

**Tool search.** With many MCP tools available, schemas would bloat context. Tool search (on by default) keeps schemas deferred and lets Claude search for the right tool when needed. Run `/mcp` to see token cost per server and disconnect ones you are not using.

**Reliability gotcha.** MCP connections can fail silently mid-session. If a server disconnects, its tools disappear without warning. If Claude tries to use a tool that no longer exists, it will fail. Run `/mcp` to check connection status when something stops working.

**Skills + MCP is a powerful pattern.** MCP gives Claude the *ability* to talk to your database. A skill teaches Claude *how* to use it well — your schema, query patterns, table conventions. The two together produce much better results than either alone.

See template: `assets/templates/mcp-config.json.example`. Docs: `https://code.claude.com/docs/en/mcp.md`. Full integration coverage in `references/integrations.md`.

---

## 7. Plugins — packaging and distribution

**What it is.** A plugin bundles skills, hooks, subagents, MCP servers, and commands into a single installable unit. Plugins are how teams distribute Claude Code extensions internally and how the community shares them publicly.

**Structure.** A plugin is a directory containing `.claude-plugin/plugin.json` (the manifest) plus any combination of subdirectories:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Manifest: name, description, version
├── skills/
│   └── <skill-name>/SKILL.md
├── agents/
│   └── <agent-name>.md
├── commands/
│   └── <command-name>.md
├── hooks/
│   └── hooks.json           # Or hook scripts referenced by hooks.json
└── .mcp.json                # MCP servers the plugin provides
```

**Manifest:**
```json
{
  "name": "quality-review-plugin",
  "description": "Adds a /quality-review skill for quick code reviews",
  "version": "1.0.0"
}
```

**Installation.**
```bash
claude plugin install <name>@<marketplace>
claude plugin install formatter@my-marketplace --scope project   # team-shared
claude plugin install formatter@my-marketplace --scope local     # gitignored
claude plugin install formatter@my-marketplace --scope user      # default, personal
```

`--scope project` writes the install to `.claude/settings.json`, sharing it with the team. `--scope local` keeps it personal but tied to the project. `--scope user` (default) makes it available across all projects.

**Namespacing.** Plugin skills are invoked as `/<plugin-name>:<skill-name>` to prevent name collisions. Plugin commands work the same way.

**Marketplaces.** A marketplace is a registry of plugins that users can browse and install from. You can build your own (a git repo with a manifest listing the plugins it offers) and host it anywhere.

**When to use a plugin.** Once a setup is reused across multiple repositories, or distributed to others, package it as a plugin. For one-off project setup, just use the raw primitives in `.claude/`.

**Component precedence.** Plugin-provided components have lower precedence than project and user definitions, so users can override plugin behavior in their own `.claude/`.

Docs: `https://code.claude.com/docs/en/plugins.md`, `https://code.claude.com/docs/en/plugins-reference.md`, `https://code.claude.com/docs/en/plugin-marketplaces.md`, `https://code.claude.com/docs/en/discover-plugins.md`.

---

## 8. Output styles — system-prompt modifications

**Not an extension, but lives in `.claude/` and is easy to confuse with skills.** Output styles modify Claude Code's system prompt directly. The default styles are tuned for software engineering; custom styles let you adapt Claude for non-coding work, or add modes like teaching or code review.

**Where it lives.** `.claude/output-styles/<name>.md` (project) or `~/.claude/output-styles/<name>.md` (user). Most are personal, so the user-global location is more common.

**Frontmatter:**
```yaml
---
name: Teaching mode
description: Explains reasoning and asks the user to implement small pieces
keep-coding-instructions: true   # Keep default coding instructions alongside additions
---
```

The body of the file is appended to the system prompt.

**Built-in styles:**
- **Default** — standard software engineering behavior
- **Explanatory** — adds reasoning and explanations
- **Learning** — leaves small changes for the user to implement

**Critical default:** Custom output styles **drop the built-in software-engineering instructions** unless you set `keep-coding-instructions: true` in frontmatter. This is the right default for non-coding adaptations (writing assistant, research helper) but the wrong default for review/teaching modes that should still know how to code.

**Selection.** Set in `settings.json`:
```json
{ "outputStyle": "teaching" }
```

Or interactively via `/config`. Changes take effect on the next session because the system prompt is fixed at startup for cache efficiency.

**Output style vs CLAUDE.md.** CLAUDE.md adds *content* to context. Output style replaces or augments the *system prompt itself*. CLAUDE.md is for project specifics; output style is for changing how Claude operates in general.

**Output style vs skill.** Output style is always-on once selected, applies to the whole session, and changes Claude's overall mode of operation. Skills are on-demand reference material or invocable workflows. If you want a "review mode" that affects everything Claude does for the session, that is an output style. If you want a `/review` workflow that runs and finishes, that is a skill.

See template: `assets/templates/output-style.md.example`. Docs: `https://code.claude.com/docs/en/output-styles.md`.

---

## Choosing between similar primitives

When the choice is not obvious, these comparisons cover the most common confusions.

### CLAUDE.md vs Rules vs Skills

All three store instructions; they differ in when they load.

| | CLAUDE.md | `.claude/rules/` | Skills |
|---|---|---|---|
| Loads | Every session, always | Every session (or path-gated) | On demand or when invoked |
| Scope | Whole project | Topic, optionally path-scoped | Task-specific |
| Best for | Core conventions, build commands | Modular topical guidance | Reference material, workflows |
| Context cost | High (every request) | Medium (every request unless gated) | Low (description only until used) |

Heuristic: **start in CLAUDE.md, refactor outward**. As CLAUDE.md grows past 200 lines, move file-type-specific guidance into path-gated rules and reference material into skills.

### Skill vs Subagent

| | Skill | Subagent |
|---|---|---|
| What it is | Reusable instructions/knowledge | Isolated worker with its own context |
| Key benefit | Share content across contexts | Context isolation; main session only sees summary |
| Best for | Reference docs, invocable workflows | Heavy reads, parallel work, specialized roles |

They combine well. A skill can spawn subagents (`/audit` skill kicks off security, performance, and style subagents in parallel). A subagent can preload skills (`skills:` field). A skill can declare `context: fork` to run in isolated context — useful when a skill reads a lot of files and you do not want the noise in the main conversation.

### MCP vs Skill

These solve different problems and pair well.

| | MCP | Skill |
|---|---|---|
| What it is | Protocol for connecting to external systems | Knowledge, workflows, reference material |
| Provides | Tools and data access | Context Claude uses with tools |
| Without it | Claude cannot reach the external system at all | Claude can use the tools but lacks domain knowledge |

Pattern: MCP server connects Claude to your database. A skill teaches Claude your data model, common query patterns, and which tables to use for which task.

### Hook vs Permission

Both can block actions. Use the simpler one when it is enough.

| | Permission rule | PreToolUse hook |
|---|---|---|
| What it is | Static allow/deny pattern in `settings.json` | Shell command that runs before each tool use |
| Decides based on | Tool name and pattern matching | Anything (full tool input, project state, external state) |
| Cost | Zero | Process spawn per tool call |
| Best for | "Block all `rm -rf`", "Allow `npm test *`" | "Allow `git push` only on `main`", "Inject project context" |

Use permissions first. Reach for hooks when you need to inspect tool input or make dynamic decisions.

### Subagent vs Agent team

| | Subagent | Agent team |
|---|---|---|
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Reports to main agent only | Teammates message each other directly |
| Coordination | Main agent orchestrates | Shared task list, self-coordinated |
| Token cost | Lower | Higher (each teammate is full session) |
| Best for | Focused isolated work | Complex work needing discussion |

Agent teams are experimental, disabled by default. Start with subagents; reach for agent teams when subagents need to talk to each other.

---

## Layering and precedence

When the same primitive is defined at multiple levels, the rules differ by primitive:

| Primitive | Behavior | Precedence (high → low) |
|---|---|---|
| **CLAUDE.md** | Additive — all levels load simultaneously | N/A (all contribute; conflicts resolved by Claude's judgment, more specific usually wins) |
| **Skills** | Override by name | managed > user > project |
| **Subagents** | Override by name | managed > CLI flag > project > user > plugin |
| **MCP servers** | Override by name | local > project > user |
| **Hooks** | Merge — all matching hooks fire | N/A (all sources contribute) |
| **Settings** | Merge for arrays, override for scalars | managed > CLI flag > local > project > user |

Plugin-provided components are namespaced (e.g. `/my-plugin:review`) so they coexist rather than override.

When troubleshooting "why isn't my X taking effect?", precedence is the first thing to check. Use `/skills`, `/agents`, `/mcp`, `/permissions`, and `/hooks` inside Claude Code to see what is actually active.

For settings precedence specifically and the full settings schema, see `references/configuration.md`.
