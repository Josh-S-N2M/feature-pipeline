---
name: kb-cc-platform
description: >-
  Platform knowledge for Claude Code — Anthropic's agentic CLI, distinct from
  Claude.ai chat. Covers configuration, architecture, and extension mechanisms
  including CLAUDE.md, the .claude directory, skills, subagents, hooks, MCP
  servers, plugins, slash commands, rules, output styles, permission modes,
  settings.json, sandboxing, the Agent SDK (Python or TypeScript), headless
  mode, checkpoints, sessions, and the VS Code extension. Use whenever a
  feature touches Claude Code's surface — including references to .claude/,
  custom slash commands, or any of these primitives. Pairs with KB-cc-design
  which adds the design discipline (when to choose which primitive). This KB
  is the PLATFORM half: facts, syntax, configuration, and lookup chains.
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch
pedagogical_sections:
  - path: references/configuration.md
    justification: "Documentation of .claude/settings.json configuration reference; references the canonical platform config paths the auditor flags as broken links (the paths don't exist in this meta-repo)"
  - path: references/cli-and-headless.md
    justification: "Documentation of Claude Code CLI + headless mode invocation; references .claude/settings.json + canonical config paths the auditor flags"
  - path: references/integrations.md
    justification: "Documentation of Claude Code integrations; references .claude/settings.json paths for integration configuration (auditor flags non-existent paths)"
  - path: references/extensions.md
    justification: "Documentation of Claude Code extensibility points; references canonical .claude/* paths (CLAUDE.md, commands, skills, settings) the auditor flags as broken links"
  - path: references/architecture.md
    justification: "Documentation of Claude Code architecture; references canonical .claude/settings.local.json path the auditor flags as broken"
  - path: references/agent-sdk.md
    justification: "Agent SDK reference documenting npm install/curl-pipe-shell installer patterns as part of SDK installation instructions; documentation of canonical Anthropic SDK installation commands the auditor flags as pipe-to-shell anti-pattern signature (the install commands themselves are well-known canonical Anthropic distribution paths, not exfiltration)."
---

# KB-cc-platform — Claude Code Platform Knowledge

Platform knowledge for Claude Code. This is the **platform half** of the cc skill pair: it teaches what exists, how it is configured, and how to verify current details. The **design half** lives in `KB-cc-design` (sister KB) — that one teaches when to choose which primitive and how to evolve a configuration. Load both for Claude-Code-touching design work; load just this one for reviewing or auditing existing setups.

## Contents

- When this KB is loaded
- Mental model in 90 seconds
- Decision matrix: pick the right primitive
- How to verify current details
- Inspect a running session
- When to load each reference file
- Templates
- Operating principles

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Claude Code / Project Filesystem** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the `cc-design.md` subsection of the Blueprint
- Plan Authoring produces tasks that touch `.claude/`, `CLAUDE.md`, settings, skills, sub-agents, hooks, MCP configs, or plugins
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Claude Code configurations

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-cc` (per-layer Design, when Claude Code / Project Filesystem layer is in scope)
- `design-composer` (Design Composition, integrating CC design with cross-cutting concerns)
- `plan-author` (when tasks touch CC artifacts)
- `shared-document-reviewer` (Gate 1 CC-specific checks)
- `review-architecture-auditor` (CoVe checks on CC-related claims)

For the design discipline overlays (when to use a subagent vs a skill, when CLAUDE.md vs a rule, when to bundle into a plugin), load `KB-cc-design` in parallel.

You are working on Claude Code: Anthropic's agentic CLI that reads codebases, edits files, runs commands, and integrates with development tools. It runs in the terminal, IDE extensions (VS Code, JetBrains), the desktop app, and the web. The same engine powers all surfaces, so configuration in `.claude/` and `~/.claude/` applies everywhere.

The body below is the router — read it end to end first, then load the specific reference file for the task at hand.

## Mental model in 90 seconds

Claude Code is a **language model wrapped in an agentic loop** with built-in tools (Read, Edit, Write, Bash, Glob, Grep, Task, WebFetch, WebSearch, TodoWrite) and an extension layer the user controls. Every session begins by loading configuration from two locations: the current project's `.claude/` directory (committed, shared with the team) and the user's global `~/.claude/` directory (personal, applies everywhere). Settings layer with managed > CLI flag > local > project > user precedence; CLAUDE.md files from all levels load additively into context.

The seven extension primitives each plug into the loop at a different point:

- **CLAUDE.md** — persistent context loaded every session
- **Rules** (`.claude/rules/*.md`) — topic-scoped instructions, optionally gated by file paths
- **Skills** — reusable knowledge or invocable workflows (the most flexible primitive)
- **Subagents** — isolated context windows that return summaries to the main session
- **Hooks** — deterministic shell scripts on lifecycle events, run outside the loop
- **MCP servers** — connect Claude to external services and data
- **Plugins** — packaging layer that bundles the above for distribution

Plus **output styles**, which are not extensions but a separate mechanism that modifies Claude's system prompt directly. They sit alongside skills in `.claude/output-styles/` and are easy to confuse with skills, which is why they are covered in the same reference file.

The most common mistake is picking the wrong primitive. The decision matrix below is the load-bearing reference for that decision.

## Decision matrix: pick the right primitive

| If the goal is… | Use | Why |
|---|---|---|
| "Always do X" rules every session needs | **CLAUDE.md** | Loads every request, additive across levels |
| Conventions that only matter for certain files (e.g. tests, API routes) | **Rules with `paths:`** | Loads only when matching files enter context |
| A workflow the user triggers like `/deploy` or `/review` | **Skill** with `disable-model-invocation: true` | User-invoked, no context cost until used |
| Reusable knowledge Claude should pull in when relevant (API docs, style guides) | **Skill** (model-invocable, default) | Claude matches description and loads on demand |
| Work that reads many files but the main conversation only needs the summary | **Subagent** | Isolated context, returns summary only |
| Specialized worker with a dedicated system prompt and restricted tools | **Subagent** with `tools:` frontmatter | Per-agent tool restriction + own context window |
| Subagent that should remember things across runs | **Subagent** with `memory: project\|user\|local` | Persistent MEMORY.md per agent |
| Deterministic side effect (lint, format, notify) on every edit/commit | **Hook** | Runs outside the loop, zero context cost, no LLM |
| Block dangerous commands before they run | **Hook** on `PreToolUse` returning `permissionDecision: "deny"` | Or use a `permissions.deny` rule |
| Connect Claude to a database, browser, Slack, or external API | **MCP server** | Standard protocol; tool schemas deferred |
| Bundle skills + hooks + subagents + MCP for a team or marketplace | **Plugin** | Packaging layer with namespacing |
| Adapt Claude for non-coding work, or add a teaching/review mode | **Output style** | Modifies the system prompt itself |

When two primitives could work, prefer the one that **costs less context** and **localizes the change**. Skills with `disable-model-invocation: true` cost zero context until invoked. Hooks cost zero context, period. MCP tool schemas are deferred until used. CLAUDE.md is the heaviest because it loads in full every request — keep it under 200 lines and move reference material to skills.

## How to verify current details

Claude Code evolves quickly — flags, schemas, and features change between releases. **Do not rely on memory for current specifics.** When you need to verify a CLI flag, settings field, hook event name, SDK parameter, or any version-specific detail, follow this lookup chain:

1. **Context7 MCP, if available.** Call `Context7:query-docs` with library ID `/websites/code_claude` (the indexed Claude Code docs site, the highest-quality source). Backup library IDs if the primary fails: `/anthropics/claude-code` and `/llmstxt/code_claude_llms_txt`.
2. **Web fetch fallback.** If Context7 is not available or returns nothing useful, use `web_fetch` on `https://code.claude.com/docs/en/<page>.md`. The `.md` suffix returns clean markdown rather than rendered HTML and is the canonical form to fetch.
3. **Find the right page.** If you don't know which page covers a topic, fetch `https://code.claude.com/docs/llms.txt` first — it is the canonical index of all docs pages with one-line descriptions.

Common page names: `overview`, `quickstart`, `how-claude-code-works`, `features-overview`, `claude-directory`, `memory`, `permission-modes`, `permissions`, `settings`, `cli-reference`, `commands`, `skills`, `sub-agents`, `hooks`, `hooks-guide`, `mcp`, `plugins`, `plugins-reference`, `headless`, `sandboxing`, `output-styles`, `vs-code`, `agent-sdk/overview`, `agent-sdk/python`, `agent-sdk/typescript`, `best-practices`, `common-workflows`, `checkpointing`, `context-window`, `env-vars`, `tools-reference`.

Reading this skill itself never requires Context7 — only verifying things that may have shifted.

## Inspect a running session

When reviewing or troubleshooting an existing setup, the user can run these slash commands inside Claude Code to show what is actually loaded right now. Suggesting these is often more useful than guessing from files on disk, because precedence rules and runtime overrides can hide things.

| Command | What it shows |
|---|---|
| `/context` | Token usage by category (system prompt, memory, skills, MCP tools, messages). Run this first for the overview. |
| `/memory` | Which CLAUDE.md and rules files loaded, plus auto-memory entries |
| `/agents` | Configured subagents and their settings |
| `/hooks` | Active hook configurations |
| `/mcp` | Connected MCP servers, their status, and per-server token cost |
| `/skills` | Available skills from project, user, and plugin sources |
| `/permissions` | Current allow/deny/ask rules and the active permission mode |
| `/doctor` | Installation and configuration diagnostics |
| `/keybindings` | Open or create the keybindings file |

`/context` first, then the specific area. If something is missing that the user expected, the most likely cause is precedence — check `references/architecture.md`.

## When to load each reference file

The reference files below are scoped by task. Load only the ones relevant to the current question — they are designed to stand alone.

| Load this file | When the task involves |
|---|---|
| `references/architecture.md` | The agentic loop, `.claude` directory layout (project + global), `CLAUDE.local.md`, settings precedence, context window, auto memory (`MEMORY.md`), environment variables, server-managed settings |
| `references/extensions.md` | Choosing or building any of the seven primitives (CLAUDE.md, rules, skills, subagents, hooks, MCP, plugins) or output styles. Includes the deeper decision matrix and the agent-memory scopes (project/user/local). |
| `references/configuration.md` | `settings.json` schema, permissions (allow/deny/ask), permission modes, sandboxing, status line, keybindings, fullscreen, voice dictation |
| `references/cli-and-headless.md` | CLI flags, built-in slash commands, headless / non-interactive mode (`-p`), output formats (text/json/stream-json), sessions and resume, checkpoints, `.worktreeinclude`, channels, routines and scheduled tasks |
| `references/agent-sdk.md` | Programmatic use via `@anthropic-ai/claude-agent-sdk` (TypeScript) or `claude_agent_sdk` (Python). `query()`, `ClaudeSDKClient`, custom tools, hooks, MCP integration, system-prompt presets |
| `references/workflows.md` | Best practices: explore→plan→code, test-driven development, parallel sessions and worktrees, common workflows, model selection (`opusplan`, fast mode), agent teams |
| `references/integrations.md` | MCP details (stdio/SSE/HTTP/SDK transports, scope hierarchy, tool search), VS Code extension, web and desktop app, Slack, Chrome (beta), Remote Control |

When working on a setup that touches multiple areas (e.g. "review my hooks and permissions"), load multiple files. They are written to be read independently and overlap minimally.

## Templates

`assets/templates/` contains real, working starter files. When creating any of these, view the template first rather than reconstructing from prose — frontmatter fields and structure shift between Claude Code versions, and these examples are the current canonical shape.

| Template | Use for |
|---|---|
| `assets/templates/CLAUDE.md.example` | New project context file |
| `assets/templates/settings.json.example` | Permissions, hooks, model defaults |
| `assets/templates/rules-example.md` | Both unconditional and `paths:`-gated rules |
| `assets/templates/skill-SKILL.md.example` | New skill (model-invocable, with `$ARGUMENTS` and bash injection patterns) |
| `assets/templates/subagent.md.example` | New subagent (with `tools:` restriction and `memory:` scope examples) |
| `assets/templates/hook-config.json.example` | Hook entries for `settings.json` (PreToolUse, PostToolUse, etc.) |
| `assets/templates/mcp-config.json.example` | `.mcp.json` for project-shared MCP servers (stdio + HTTP/SSE) |
| `assets/templates/slash-command.md.example` | Single-file command in `.claude/commands/` (the older mechanism; new work should use skills) |
| `assets/templates/output-style.md.example` | Custom output style for non-coding modes or teaching/review modes |

## Operating principles

A few things to keep front of mind whenever advising on Claude Code:

**Precedence beats guessing.** When something does not behave as expected, check what overrode it. Settings: managed > CLI > local > project > user. Skills/subagents: managed > user > project (skills); managed > CLI > project > user > plugin (subagents). MCP: local > project > user. CLAUDE.md is additive across all levels, not overridden. Hooks merge across all sources.

**Context is finite and expensive.** Every CLAUDE.md line, every rule without `paths:`, every always-loaded skill description costs tokens on every request. When reviewing a setup, the question "what could move from CLAUDE.md to a skill or path-gated rule?" is almost always productive.

**Hooks and permissions are guarantees; instructions are guidance.** CLAUDE.md and rules tell Claude what to do — Claude usually follows but is not obligated to. Hooks and `permissions.deny` are enforced by Claude Code itself regardless of what the model decides. For anything safety-critical or compliance-related, use the enforced mechanism.

**Subagents do not inherit conversation context.** When a user is frustrated that a subagent "doesn't know" something the main session knew, that is by design. Subagents get a fresh context window plus only what the lead agent passes in, plus skills explicitly listed in the agent's `skills:` field. This isolation is the feature, not a bug — but it means the subagent's prompt and skill list have to be self-sufficient.

**Skills replaced commands but commands still work.** New invocable workflows should be skills (`skills/<name>/SKILL.md`) because they can bundle supporting files. Single-file `commands/*.md` still work and are still documented. If a skill and command share a name, the skill wins.

**Prefer the official docs for current detail.** This skill captures durable architecture and patterns. For exact flag spelling, current schema fields, or recently shipped features, follow the lookup chain in the section above.
