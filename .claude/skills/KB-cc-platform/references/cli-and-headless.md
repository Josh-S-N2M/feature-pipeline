# CLI and headless reference

The `claude` command, built-in slash commands, headless / non-interactive mode for scripting and CI, sessions and checkpoints, and the surrounding scheduling and event-pushing features (channels, routines, scheduled tasks, worktrees).

For the Agent SDK (programmatic Python/TypeScript use), see `references/agent-sdk.md`. For settings that affect CLI behavior, see `references/configuration.md`.

## Contents

- The `claude` command
- Common CLI flags
- Built-in slash commands
- Headless / non-interactive mode
- Sessions and resume
- Checkpoints
- Worktrees
- Channels
- Routines and scheduled tasks
- Composability — the Unix philosophy
- Quick reference summary

## The `claude` command

Three usage patterns:

```bash
claude                              # Interactive session in current directory
claude "do this thing"              # Interactive session, pre-filled with a prompt
claude -p "do this thing"           # Non-interactive (headless / print mode)
```

The interactive session is the default — Claude prompts back, the user replies, the loop continues. Headless mode runs once, prints the result, and exits.

## Common CLI flags

This is the field guide. For the complete flag list — they shift between releases — fetch `https://code.claude.com/docs/en/cli-reference.md`.

| Flag | Purpose |
|---|---|
| `-p "<prompt>"` | Print mode (headless). Run once, output result, exit. |
| `--model <name>` | Model for this session (`opus`, `sonnet`, `haiku`, `opusplan`, full IDs like `claude-opus-4-7`) |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools "<list>"` | Auto-approve specific tools without modifying settings (space- or comma-separated) |
| `--add-dir <path>` | Add another directory Claude can access |
| `--mcp-config <path>` | Load MCP servers from a specific file |
| `--settings <path>` | Use a specific settings file |
| `--agents '<json>'` | Define subagents inline (JSON object) for this session |
| `--continue` | Resume the most recent session in the current directory |
| `--resume [<name>]` | Resume by session name, or open a picker if no name given |
| `--from-pr <number>` | Resume a session linked to a specific pull request |
| `--worktree` | Run in a fresh git worktree (uses `.worktreeinclude` for gitignored files) |
| `--teleport` | Pull a web/desktop session into the terminal |
| `--output-format <format>` | Headless output: `text` (default), `json`, `stream-json` |
| `--max-turns <n>` | Cap turns in headless mode |
| `--bare` | Skip auto-discovery of local hooks and configs (predictable CI behavior) |
| `--debug` | Verbose debug output |
| `--append-system-prompt "<text>"` | Append text to the default system prompt |
| `--verbose` | Verbose logging |

`--bare` is the right flag for CI when you want a known environment without surprises from local `.claude/` files. `--allowedTools` paired with `--permission-mode acceptEdits` is the headless workhorse.

## Built-in slash commands

These run inside an interactive session by typing `/<name>`. Two categories: **diagnostics** (inspect what is loaded) and **actions** (modify session state, manage features).

### Diagnostics

| Command | Shows |
|---|---|
| `/context` | Token usage by category — system prompt, memory, skills, MCP tools, messages |
| `/memory` | Loaded CLAUDE.md, rules, auto-memory entries; opens MEMORY.md or CLAUDE.md for editing |
| `/agents` | Configured subagents |
| `/hooks` | Active hook configurations |
| `/mcp` | Connected MCP servers, status, per-server token cost |
| `/skills` | Available skills from project, user, plugin sources |
| `/permissions` | Current allow/deny/ask rules and active permission mode |
| `/doctor` | Installation and configuration diagnostics |
| `/status` | Session status overview |

### Actions

| Command | Action |
|---|---|
| `/compact` | Summarize older messages to reclaim context |
| `/clear` | Clear the conversation, keep settings |
| `/config` | Open the config editor (writes to `~/.claude.json`) |
| `/keybindings` | Open or create the keybindings file |
| `/login`, `/logout` | Authentication |
| `/desktop` | Hand off the current session to the Desktop app for visual diff review |
| `/schedule` | Create a routine (cloud-scheduled task) |
| `/loop` | Repeat a prompt within the session for polling |
| `/exit`, `/quit` | End the session |

Plus the bundled skills (`/simplify`, `/batch`, `/debug`, etc.) and any user/project skills and commands.

For the complete built-in list with current options: `https://code.claude.com/docs/en/commands.md`.

## Headless / non-interactive mode

`claude -p` runs once and exits. This is the integration mode for CI, pre-commit hooks, scripted workflows, and Unix pipelines.

```bash
# One-off
claude -p "Explain what this project does"

# Structured output
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing
claude -p "Analyze this log file" --output-format stream-json

# Pipe input
cat data.txt | claude -p "Summarize this data" --output-format text > summary.txt
tail -200 app.log | claude -p "Slack me if you see anomalies"

# Pipe in a file list
git diff main --name-only | claude -p "Review these files for security issues"
```

**Output formats:**

- **`text`** (default) — plain text response
- **`json`** — structured response with metadata (session ID, token counts, result fields). Parse with `jq`.
- **`stream-json`** — newline-delimited JSON events as they happen. Use when you want to render output incrementally.

**Combining flags:**

```bash
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit" \
  --permission-mode acceptEdits \
  --max-turns 20 \
  --output-format json
```

**`--bare` for predictable CI.** Skips auto-discovery of local hooks and configs so the environment is exactly what you specify. Without it, a project's `.claude/settings.json` and `.mcp.json` load automatically, which is usually what you want locally and almost never what you want in CI.

For headless patterns, error handling, and exit codes: `https://code.claude.com/docs/en/headless.md`.

## Sessions and resume

Every interactive session has a UUID. Sessions persist by default — you can resume them later from any directory (with the same project root). Sessions store the full conversation history, file checkpoints, and agent state.

```bash
claude --continue                   # Most recent session in this directory
claude --resume                     # Picker showing recent sessions
claude --resume auth-refactor       # Resume by name
claude --from-pr 123                # Resume the session linked to PR 123
```

**Naming sessions.** Use `/name <session-name>` inside a session to give it a memorable name for resume.

**Session storage.** Sessions live under `~/.claude/projects/<project-path>/`. The same per-project location holds auto memory.

For session lifecycle and management details: `https://code.claude.com/docs/en/checkpointing.md` (checkpoints are tied into sessions).

## Checkpoints

Claude Code records checkpoints throughout a session — snapshots of file state at specific user-message boundaries. You can rewind to any checkpoint, undoing all file changes since that point while keeping the conversation history.

This is most useful when an automated edit loop went off the rails and you want to reset the workspace without losing the conversation context that explains what was being attempted.

In the CLI, checkpoints are managed through the `/rewind` command and visible in `/status`. Programmatically (Agent SDK), `enableFileCheckpointing: true` plus `rewindFiles(messageId)` provides the same capability.

For details and SDK examples: `https://code.claude.com/docs/en/checkpointing.md`.

## Worktrees

Claude Code can run in a git worktree — a separate working directory backed by the same repository — to isolate parallel sessions or risky edits. Two ways to create one:

```bash
claude --worktree                   # Start a session in a new worktree
```

Or interactively, with the `EnterWorktree` tool, or by configuring a subagent with `isolation: worktree`.

**`.worktreeinclude`** lives at the project root and lists gitignored files to copy into each new worktree (using `.gitignore` syntax). Worktrees start as fresh checkouts, so untracked files (`.env`, secrets, local config) are missing by default. Patterns in this file get copied — but only files that are *both* gitignored *and* matched, so tracked files are never duplicated.

```audit-example -- Documents credential-file path patterns (cloud SDK creds, SSH keys, NETRC, dotenv) the auditor flags via DE-2 scanner; reference catalog explaining what to protect, not real credentials.
# Local environment
.env
.env.local

# Credentials
config/secrets.json
```

`.worktreeinclude` is git-only. If you use a custom VCS hook, configure a `WorktreeCreate` hook instead.

## Channels

Push external events into a running Claude Code session. A channel is an MCP server that emits notifications (CI results, chat messages, monitoring alerts, webhook deliveries) into the session so Claude can react while the user is away.

The contract: the MCP server declares the `channels` capability, sends notification events with a payload, and optionally exposes reply tools that Claude can call to respond on the same channel.

When to use: you want long-running Claude sessions that react to real events instead of polling, e.g. a session that watches CI and fixes failures, or one that responds to Slack mentions.

For the channel protocol: `https://code.claude.com/docs/en/channels.md` (guide) and `https://code.claude.com/docs/en/channels-reference.md` (the MCP contract details).

## Routines and scheduled tasks

Three ways to run Claude on a schedule:

| Mechanism | Where it runs | When to use |
|---|---|---|
| **Routines** | Anthropic-managed infrastructure | Scheduled or event-triggered work that should run when the user's machine is off (morning PR reviews, weekly audits) |
| **Desktop scheduled tasks** | The user's machine | Scheduled work that needs local file/tool access |
| **`/loop`** | The current CLI session | Polling within an active session (poll a build until it finishes) |

Create routines from the web, the Desktop app, or with `/schedule` in the CLI. Routines can also trigger on API calls or GitHub events.

Docs: `https://code.claude.com/docs/en/routines.md` (cloud), `https://code.claude.com/docs/en/desktop-scheduled-tasks.md` (local), `https://code.claude.com/docs/en/scheduled-tasks.md` (`/loop` and cron tools), `https://code.claude.com/docs/en/web-scheduled-tasks.md` (web scheduling UI).

## Composability — the Unix philosophy

Claude Code is designed to compose with the existing shell. Pipe into it, pipe out of it, chain it with other tools:

```bash
# Analyze recent logs
tail -200 app.log | claude -p "Slack me if you see any anomalies"

# Translation in CI
claude -p "translate new strings into French and raise a PR for review" \
  --permission-mode acceptEdits \
  --allowedTools "Bash Read Edit Write"

# Bulk operations across files
git diff main --name-only | claude -p "review these changed files for security issues"

# Chain with jq for structured output
claude -p "list the API endpoints" --output-format json | jq '.endpoints[]'
```

The `claude` binary is just a program. It honors stdin, exit codes, and pipes. Treat it like any other Unix tool.

## Quick reference summary

For a Claude Code script that needs to be reliable in CI:

1. Use `claude -p` for non-interactive
2. Add `--bare` to skip auto-discovery
3. Set `--allowedTools` explicitly — do not rely on settings
4. Set `--permission-mode acceptEdits` (or stricter)
5. Use `--output-format json` and parse with `jq`
6. Cap with `--max-turns` to bound runaway loops
7. Set `ANTHROPIC_API_KEY` (or cloud-provider auth) in the environment

For an interactive session that needs to be powerful:

1. `--permission-mode acceptEdits` for trusted edit loops, `--permission-mode plan` for discovery
2. `--add-dir` for cross-project work
3. `--worktree` for parallel/risky work
4. Use `Shift+Tab` to cycle modes mid-session
5. `/context` early and often to monitor token use
6. `/compact` when the window fills, or spawn subagents for heavy reads
