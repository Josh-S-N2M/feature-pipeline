# Architecture reference

The agentic loop, the `.claude` directory layout, settings precedence, the context window, auto memory, and the surrounding plumbing. This is the reference for how Claude Code is put together — load it when reviewing setups, debugging precedence problems, or explaining how things fit.

## Contents

- The agentic loop
- The `.claude` directory
- Settings precedence
- CLAUDE.md loading order
- The context window
- Auto memory
- Environment variables
- Server-managed settings (enterprise)
- Diagnostic commands recap

## The agentic loop

Claude Code is a language model wrapped in an agentic harness. The harness provides tools, manages context, and coordinates execution. The loop has three phases that repeat:

1. **Gather context** — Claude reads files, runs searches, queries MCP tools, asks clarifying questions
2. **Take action** — Claude proposes edits, runs commands, writes files, calls tools
3. **Verify results** — Claude reads back what changed, runs tests, checks output, course-corrects

Claude chooses which phase to be in dynamically based on the task and what it learns from each step. The loop continues until the task is complete or the user interrupts. Users remain in the loop the entire time and can interrupt, redirect, or ask follow-up questions.

The loop terminates a turn when Claude responds with a final answer (no tool calls). It terminates the session when the user exits.

### Built-in tools

The model uses these tools without configuration:

| Tool | Purpose |
|---|---|
| `Read` | Read a file, with line range support |
| `Edit` | Replace a unique string in a file |
| `Write` | Create or overwrite a file |
| `Bash` | Execute shell commands (subject to permissions and sandboxing) |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents (uses ripgrep) |
| `Task` (a.k.a. `Agent`) | Spawn a subagent |
| `WebFetch` | Fetch a URL and read its content |
| `WebSearch` | Search the web |
| `TodoWrite` | Track multi-step task progress |

MCP tools surface as `mcp__<server>__<tool>` and are added to this set when servers are connected. SDK custom tools defined with `@tool` (Python) or the equivalent (TypeScript) appear under whatever MCP server name they are registered to.

For the current full list and tool signatures, fetch `https://code.claude.com/docs/en/tools-reference.md`.

## The `.claude` directory

Configuration lives in two parallel locations: project-scoped `.claude/` (committed, team-shared) and user-scoped `~/.claude/` (personal, applies to every project). The two locations have nearly the same structure.

### Project root

Files at the actual project root (not inside `.claude/`):

| File | Committed? | Purpose |
|---|---|---|
| `CLAUDE.md` | Yes | Project instructions loaded every session |
| `CLAUDE.local.md` | No (manual gitignore) | Personal per-project preferences, loaded alongside CLAUDE.md |
| `.mcp.json` | Yes | Project-scoped MCP servers |
| `.worktreeinclude` | Yes | Gitignored files to copy into new worktrees |

### `.claude/` (project)

| Path | Committed? | Purpose |
|---|---|---|
| `settings.json` | Yes | Permissions, hooks, env vars, model defaults — team config |
| `settings.local.json` | No (auto-gitignored) | Personal overrides for this project |
| `CLAUDE.md` | Yes | Alternative location for project CLAUDE.md (vs root) |
| `rules/*.md` | Yes | Topic-scoped or path-scoped instructions |
| `skills/<name>/SKILL.md` | Yes | Skills (with bundled supporting files) |
| `commands/*.md` | Yes | Single-file slash commands (legacy mechanism, still supported) |
| `agents/*.md` | Yes | Subagent definitions |
| `agent-memory/<agent>/MEMORY.md` | Yes | Persistent memory for subagents with `memory: project` |
| `agent-memory-local/<agent>/` | No (auto-gitignored) | For subagents with `memory: local` |
| `output-styles/*.md` | Yes | Project-shared custom output styles |
| `hooks/` | Yes | Hook scripts referenced from `settings.json` (convention, not required) |

### `~/.claude/` (global)

Same shape as project, with these additions:

| Path | Purpose |
|---|---|
| `~/.claude.json` | App state, OAuth, UI toggles, personal MCP servers, per-project trust decisions |
| `~/.claude/keybindings.json` | Custom keyboard shortcuts |
| `~/.claude/projects/<project>/memory/` | Auto memory — Claude's notes to itself, per project |
| `~/.claude/agent-memory/<agent>/` | Persistent memory for subagents with `memory: user` |

`~/.claude.json` is mostly managed through `/config` rather than edited directly.

### Enterprise-managed location

| File | Where | Purpose |
|---|---|---|
| `managed-settings.json` | OS-specific system path | Enterprise-enforced settings the user cannot override |

This is the highest-precedence settings source. Used by organizations that need to enforce policies (deny rules, model restrictions) regardless of user preferences. See `https://code.claude.com/docs/en/server-managed-settings.md`.

## Settings precedence

When the same setting is defined in multiple places, this is the order (highest → lowest):

1. **Managed settings** (`managed-settings.json`, system-level) — enterprise enforcement
2. **CLI flags** (e.g. `--permission-mode`, `--model`, `--settings`) — single session
3. **Project local** (`.claude/settings.local.json`) — personal per-project
4. **Project shared** (`.claude/settings.json`) — team per-project
5. **User global** (`~/.claude/settings.json`) — personal across all projects

Two important nuances:

- **Array settings combine across all scopes.** `permissions.allow`, `permissions.deny`, hooks, env vars — these merge. A `Bash(npm test *)` allow rule in user settings combines with project-level allows; you do not lose them.
- **Scalar settings use the most specific value.** `model`, `outputStyle`, `defaultMode` — these override. The value from the highest-precedence source wins; lower-precedence values are ignored.

CLAUDE.md and rules are different from settings — they are **content**, not configuration. All CLAUDE.md files at every level load additively into context. There is no "override" — Claude reconciles conflicts using judgment, with more specific (deeper or more recent) instructions typically taking precedence.

Some environment variables override their equivalent setting; this varies per variable. For exact behavior, fetch `https://code.claude.com/docs/en/env-vars.md`.

## CLAUDE.md loading order

CLAUDE.md is special — multiple files load simultaneously. The order they appear in context:

1. Managed-level CLAUDE.md (rare, enterprise)
2. User CLAUDE.md (`~/.claude/CLAUDE.md`)
3. Walking from project root **upward** to filesystem root (parent CLAUDE.md files in monorepos)
4. Project CLAUDE.md (root or `.claude/CLAUDE.md`)
5. `CLAUDE.local.md` (if present)
6. Subdirectory CLAUDE.md files **load when Claude accesses files in those subdirectories**

So in a monorepo, when Claude works in `packages/api/`, it sees the root CLAUDE.md plus `packages/api/CLAUDE.md` plus any rules with matching `paths:` globs. Working in `packages/web/` swaps the package-level file but keeps the root.

This is why you should not duplicate root content in package CLAUDE.md files — they are additive, not override. Put package-specific guidance only.

## The context window

Every session's context window contains:

| Section | When it loads | Cost profile |
|---|---|---|
| System prompt | Session start (cached for efficiency) | Fixed |
| CLAUDE.md (all levels) | Session start | Every request |
| Rules without `paths:` | Session start | Every request |
| Rules with matching `paths:` | When file enters context | Conditional |
| Skill descriptions (model-invocable) | Session start | Every request (small) |
| Skill content | When invoked or auto-loaded | Conditional |
| MCP tool names | Session start | Every request (small) |
| MCP tool schemas | When tool is searched/used | Deferred |
| Auto-memory `MEMORY.md` | Session start (first 200 lines / 25 KB) | Every request |
| Conversation messages | As they happen | Accumulates |

The bottom of the list is where context blows up. Long sessions accumulate messages, file reads, and tool outputs. When the window fills, Claude can `/compact` (summarize older messages) to reclaim space. Subagents are the structural answer — push expensive work into isolated context that returns only summaries.

Run `/context` inside Claude Code to see real token usage by category. This is the single most useful diagnostic for "why is the context so full?" questions.

For an interactive simulation, see `https://code.claude.com/docs/en/context-window.md`.

## Auto memory

```audit-example -- Documents the auto-memory mechanism's distinction from CLAUDE.md (user-authored) and CLAUDE.md imports; the auditor flags 'writing notes' co-occurring with 'CLAUDE.md' as a CLAUDE.md-modification anti-pattern, but this is descriptive prose explaining Claude Code's memory architecture, not an instruction.
Distinct from CLAUDE.md (which the user writes) and from CLAUDE.md imports. Auto memory is **Claude writing notes to itself across sessions**.
```

**Where it lives.** `~/.claude/projects/<project-path>/memory/` — a directory per project, keyed by repository path.

**Structure.**
- `MEMORY.md` is the index, loaded at session start. The first 200 lines (capped at 25 KB) are read into context.
- Topic files (`debugging.md`, `architecture.md`, `build-commands.md`, etc.) are created by Claude when MEMORY.md grows. Topic files are read on demand when a relevant task comes up, not at startup.

**Behavior.** Claude maintains these files automatically as it works — recording build commands that worked, debugging insights, architecture facts. The user does not author them but can edit or delete them; Claude will keep updating.

**Toggle.** On by default. Disable with `/memory` or `autoMemoryEnabled: false` in settings.

**Distinct from agent memory.** Subagent memory (`memory: project | user | local` in subagent frontmatter) is a separate per-agent feature; see `references/extensions.md` section 4. Auto memory belongs to the main session.

When reviewing a project's setup, do not edit auto-memory files as if they were user-authored configuration. They are Claude's working notes. If something in MEMORY.md is wrong, the right fix is usually to correct the underlying reality (the build command, the architecture) and let Claude update its notes, or to clear the file and let Claude rebuild.

For details: `https://code.claude.com/docs/en/memory.md` (auto-memory section).

## Environment variables

Many aspects of Claude Code can be configured via environment variables — model selection, region overrides, debug output, working directory behavior, telemetry. The full reference is at `https://code.claude.com/docs/en/env-vars.md`.

Variables you are most likely to encounter:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | API key for direct Anthropic access |
| `ANTHROPIC_MODEL` | Default model |
| `CLAUDE_CODE_USE_BEDROCK=1` | Route through Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | Route through Google Vertex AI |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key (alternative to AWS creds) |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Freeze the working directory for bash commands |
| `${CLAUDE_PROJECT_DIR}` | Project root path (available in hook commands) |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin root (available in plugin hook commands) |
| `${CLAUDE_SKILL_DIR}` | Skill directory (available in skill bash injections) |

Some of these override their equivalent settings; check the docs page for each.

## Server-managed settings (enterprise)

Public beta. Lets organizations centrally configure Claude Code without device management infrastructure. Settings are delivered from a server; the device fetches them on session start. Used for enforcing permission policies, model restrictions, telemetry endpoints, and proxy configuration.

For setup: `https://code.claude.com/docs/en/server-managed-settings.md`. For enterprise network configuration (proxies, custom CAs, mTLS): `https://code.claude.com/docs/en/network-config.md`.

## Diagnostic commands recap

When the architecture is the problem (something not loading, precedence biting), these slash commands inside Claude Code reveal the actual state:

| Command | Reveals |
|---|---|
| `/context` | Token usage by category — start here |
| `/memory` | Loaded CLAUDE.md, rules, auto-memory entries |
| `/agents` | Active subagents and their config |
| `/hooks` | Active hook configurations |
| `/mcp` | Connected MCP servers, status, per-server token cost |
| `/skills` | Available skills from project, user, plugin sources |
| `/permissions` | Current allow/deny/ask rules and active permission mode |
| `/doctor` | Installation and configuration diagnostics |
| `/config` | Open the in-app config editor (writes to `~/.claude.json`) |

The pattern is `/context` → identify the area → run the area-specific command → trace back to which file is responsible. The precedence tables above tell you what could be overriding what.
