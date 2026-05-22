# Integrations reference

The surfaces Claude Code runs on (CLI, VS Code, Desktop, Web), the protocol that connects it to external systems (MCP), and the third-party integrations it ships with (Slack, Chrome, Remote Control). Same engine underneath all of them — configuration in `.claude/` and `~/.claude/` carries across surfaces.

For configuration detail and architecture, see other references. This file is for "what surface, when, and how do they connect to outside systems."

## Contents

- Surface comparison
- VS Code extension
- Desktop app
- Web (`claude.ai/code`)
- Remote Control
- Slack
- Chrome (beta)
- Computer use (preview)
- MCP — connecting to external systems
- CI/CD integrations
- Code review automation
- Enterprise integrations
- Quick "I want to" lookup

## Surface comparison

| Surface | Strengths | When to choose |
|---|---|---|
| **CLI** | Most comprehensive feature set, scripting and automation, full Agent SDK, headless mode | Default for terminal-native developers; required for Unix-pipe composition and CI integration |
| **VS Code extension** | Inline diffs, @-mentions, plan review, conversation history in the editor | When you mostly live in VS Code and want tight editor integration |
| **JetBrains plugin** | IntelliJ/PyCharm/WebStorm with diff viewing and selection-context sharing | JetBrains users; equivalent role to VS Code extension |
| **Desktop app** | Visual diff review, parallel sessions with git isolation, scheduled tasks, computer use, app previews | Reviewing many changes visually, running multiple sessions side by side, mobile-to-desktop handoffs |
| **Web** (`claude.ai/code`) | Cloud infrastructure, runs without local setup, long tasks while you do other things | Long-running tasks, working on repos you do not have locally, parallel work, mobile use |

All surfaces use the same engine and read the same `.claude/` and `~/.claude/` configuration. A skill defined once works everywhere; CLAUDE.md applies in every surface.

For the canonical comparison: `https://code.claude.com/docs/en/platforms.md`.

## VS Code extension

The Claude Code extension brings the CLI's capabilities into VS Code with editor-native UI. Key features:

- **Inline diffs** — Claude's proposed changes appear as diff overlays in the editor, accept or reject per-file or per-hunk
- **@-mentions** — `@filename` to bring a file into the conversation; `@selection` to bring the current selection
- **Plan review** — when Claude is in plan mode, the plan renders as structured UI with approve/reject controls
- **Conversation history** — past sessions accessible from the side panel
- **Command palette** — `Cmd/Ctrl+Shift+P` → "Claude Code" actions
- **Settings sync** — extension settings layer with `.claude/settings.json` and `~/.claude/settings.json`
- **Cursor compatibility** — works in Cursor and other VS Code forks

**Install paths:**
- VS Code Marketplace: search for "Claude Code"
- Direct: `vscode:extension/anthropic.claude-code`
- For Cursor: `cursor:extension/anthropic.claude-code`

After install, Command Palette → "Claude Code: Open in New Tab" launches a session in a new tab.

**The terminal still works.** Running `claude` in VS Code's integrated terminal launches the same CLI session, with the IDE integration features active. You can mix interactive editing (CLI) with diff review (extension UI) freely.

For details: `https://code.claude.com/docs/en/vs-code.md`.

## Desktop app

A standalone macOS/Windows app that runs Claude Code outside the terminal. Distinct capabilities:

- **Visual diff review** — every proposed change shown side-by-side, click to accept/reject
- **Parallel sessions with git isolation** — multiple sessions run in separate worktrees, no interference
- **Scheduled tasks** — recurring local tasks (morning PR review, weekly audits)
- **App previews** — render dev servers and web apps inline
- **PR monitoring** — watch PRs and react to events
- **Connectors** — graphical management of MCP servers
- **Dispatch** — send a task from your phone, open the resulting Desktop session
- **Computer use (preview)** — Claude can see your screen, click, type, open apps (macOS)

**`/desktop`** in the CLI hands off the current session to the Desktop app. Useful when you want to switch to visual diff review for a tricky change.

**Sessions are portable.** A session started in the Desktop app can be continued in the CLI with `claude --resume`, on the web at `claude.ai/code`, or on mobile via Remote Control.

For desktop specifics: `https://code.claude.com/docs/en/desktop.md` and `https://code.claude.com/docs/en/desktop-quickstart.md`.

## Web (`claude.ai/code`)

Browser-based Claude Code with no local setup. Runs on Anthropic-managed cloud infrastructure.

When the web makes sense:
- Long-running tasks that should keep going while your machine sleeps
- Repos you do not have cloned locally
- Mobile use (the iOS app embeds the same web experience)
- Parallel tasks across many repos

The web version connects to your repositories (GitHub) and runs in sandboxed cloud environments. Output streams back. Sessions can be moved to the CLI with `claude --teleport` on the receiving terminal.

Docs: `https://code.claude.com/docs/en/claude-code-on-the-web.md` and `https://code.claude.com/docs/en/web-quickstart.md`.

## Remote Control

Continue a local Claude Code session from your phone, tablet, or any browser. Works with `claude.ai/code` and the Claude mobile app.

Use case: you started a long task locally, you have to leave, you want to keep watching and giving direction from your phone without abandoning the local session. Remote Control connects the remote device to your local session, so messages sent from the phone reach the local CLI and responses stream back.

Docs: `https://code.claude.com/docs/en/remote-control.md`.

## Slack

Claude Code in Slack lets you delegate coding tasks from a Slack channel. Mention `@Claude` in a message with a task and Claude responds with a session — and can open pull requests, file issues, or post results back into the channel.

Common workflow: a teammate pastes a bug report into a channel, mentions `@Claude`, and walks away. A few minutes later, a PR appears with a fix.

Setup involves adding the Claude Code Slack app to your workspace and granting it the relevant scopes. Connection from Slack to your code is via your existing Anthropic Console / Claude.ai account.

Docs: `https://code.claude.com/docs/en/slack.md`.

## Chrome (beta)

Connect Claude Code to your Chrome browser. Use cases:

- Test web apps Claude built — Claude can navigate, click, type, screenshot
- Debug with console logs — Claude reads the console output and reasons about errors
- Automate form filling
- Extract data from web pages

The Chrome integration connects via a browser extension. Claude controls the browser through the extension's exposed API.

Docs: `https://code.claude.com/docs/en/chrome.md`.

## Computer use (preview)

Native computer use on macOS. Claude can open apps, click, type, and see your screen — useful for debugging visual UI, automating GUI-only tools, and testing native apps.

Different from Chrome (browser-only) — computer use works at the OS level. Higher capability, higher caution warranted.

Docs: `https://code.claude.com/docs/en/computer-use.md`.

## MCP — connecting to external systems

Model Context Protocol is Claude Code's primary mechanism for talking to external systems. For configuration shape and the per-primitive overview, see `references/extensions.md` section 6. This section covers the integration depth.

### Transports

Four transports, each suited to different deployment patterns:

| Transport | Connection | Typical use |
|---|---|---|
| **stdio** | Local process spawned and managed by Claude Code | Most common; servers shipped as npm packages or local scripts |
| **HTTP** | Remote HTTP endpoint | Hosted MCP servers (Stripe, internal services) |
| **SSE** | Server-Sent Events | Streaming-friendly hosted servers |
| **SDK** | In-process when using Agent SDK | Custom tools you write in Python/TypeScript via `create_sdk_mcp_server()` |

stdio is the default. Use HTTP/SSE for servers that should be hosted (centralized, auto-updating, multi-tenant). Use SDK transport when you are embedding Claude Code in your own application and want custom tools.

### Scope hierarchy

Three places MCP servers can be defined:

| Scope | File | Committed? | Used for |
|---|---|---|---|
| **project** | `.mcp.json` at project root | Yes | Servers the whole team uses |
| **user** | `~/.claude.json` under `mcpServers` | No | Personal servers across all your projects |
| **local** | `~/.claude.json` under `projects.<path>.mcpServers` | No | Personal servers for one project |

Precedence: local > project > user. Local overrides project (so you can swap a team's database server for your own dev instance). Project overrides user (so user-global servers do not conflict with team setups).

Add a server with `claude mcp add` (interactive, prompts for scope). Remove with `claude mcp remove`.

### Tool naming and permissions

MCP tools surface as `mcp__<server-name>__<tool-name>`. Permission rules can target individual tools or whole servers:

```json
{
  "permissions": {
    "allow": [
      "mcp__github__list_issues",
      "mcp__github__get_pull_request",
      "mcp__database"
    ],
    "deny": [
      "mcp__github__delete_repo",
      "mcp__database__drop_table"
    ]
  }
}
```

Allowing the whole server (`mcp__github`) is convenient but loose; for production setups, list individual tools.

### Tool search

With many MCP servers connected, raw tool schemas could fill the context window. Tool search (on by default) defers schemas — Claude searches for the right tool when needed and only loads its schema then. This lets you connect dozens of MCP servers without bloating context.

Run `/mcp` to see token cost per server. Disconnect servers you are not using:

```bash
claude mcp disable <server>
claude mcp remove <server>
```

### Authentication

`${VAR_NAME}` syntax in `.mcp.json` and `~/.claude.json` expands environment variables at startup. Keep secrets out of the file:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "stripe": {
      "type": "http",
      "url": "https://mcp.stripe.com",
      "headers": { "Authorization": "Bearer ${STRIPE_API_KEY}" }
    }
  }
}
```

For OAuth-based MCP servers, Claude Code handles the token exchange and stores credentials in `~/.claude.json`. The first connection prompts for authorization in a browser.

### Reliability

MCP connections can fail silently mid-session. If a server disconnects, its tools disappear without a notification. Two patterns to mitigate:

1. **Run `/mcp` periodically** when something stops working — it shows current connection status
2. **In the SDK**, call `get_mcp_status()` and `reconnect_mcp_server(name)` programmatically; SSE connections auto-reconnect on disconnect (added recently — check the changelog)

### MCP and skills together

The most powerful pattern: MCP gives Claude *access* to a system, and a skill teaches Claude *how to use it well*. Example pairing for a database:

- **MCP server** (`postgres`) — exposes `query`, `list_tables`, `describe_table` tools
- **Skill** (`db-conventions`) — your schema overview, common query patterns, table relationships, performance considerations, "always SELECT specific columns, never SELECT *", "the `users` table is denormalized for hot reads"

Together: Claude can query the database (MCP) and knows your conventions (skill). Either alone produces worse results.

### MCP servers worth knowing

Common MCP servers from the ecosystem (current as of writing — verify availability):

| Server | Capability |
|---|---|
| `@modelcontextprotocol/server-github` | GitHub: read issues/PRs, create PRs, browse repos |
| `@modelcontextprotocol/server-gitlab` | GitLab equivalent |
| `@modelcontextprotocol/server-filesystem` | Filesystem with sandboxed paths |
| `@modelcontextprotocol/server-postgres` | PostgreSQL queries |
| `@modelcontextprotocol/server-slack` | Slack messaging and history |
| `@modelcontextprotocol/server-puppeteer` | Browser automation |
| Anthropic-hosted: Stripe, Linear, Notion, etc. | Various SaaS connectors |

For the canonical, current list and connector partners: `https://claude.com/partners/mcp`.

For MCP details: `https://code.claude.com/docs/en/mcp.md`.

## CI/CD integrations

Two paths for running Claude Code in CI:

- **GitHub Actions** — `https://code.claude.com/docs/en/github-actions.md` (covered by your separate skill)
- **GitLab CI/CD** — `https://code.claude.com/docs/en/gitlab-ci-cd.md` (also typically covered by a CI-focused skill)

The general pattern for both: install Claude Code in the runner, set `ANTHROPIC_API_KEY` (or cloud-provider auth), and call `claude -p` with appropriate flags. Use `--bare` to skip auto-discovery so the runner has predictable state.

## Code review automation

`https://code.claude.com/docs/en/code-review.md` covers automated PR reviews using multi-agent analysis — a setup where Claude Code reviews every PR with subagents specializing in security, performance, and tests. Designed for GitHub. Worth pointing teams at when they ask about review automation beyond what GitHub Actions alone provides.

## Enterprise integrations

For organizations with platform requirements:

- **Bedrock** — `https://code.claude.com/docs/en/amazon-bedrock.md`
- **Vertex AI** — `https://code.claude.com/docs/en/google-vertex-ai.md`
- **Microsoft Foundry** — `https://code.claude.com/docs/en/microsoft-foundry.md`
- **LLM Gateway** — `https://code.claude.com/docs/en/llm-gateway.md`
- **GitHub Enterprise Server** — `https://code.claude.com/docs/en/github-enterprise-server.md`
- **Network configuration** (proxies, custom CAs, mTLS) — `https://code.claude.com/docs/en/network-config.md`
- **Server-managed settings** — `https://code.claude.com/docs/en/server-managed-settings.md`
- **Zero Data Retention** — `https://code.claude.com/docs/en/zero-data-retention.md`
- **Analytics** — `https://code.claude.com/docs/en/analytics.md`
- **Monitoring (OpenTelemetry)** — `https://code.claude.com/docs/en/monitoring-usage.md`

These are operator-level concerns. Most users do not need them; teams deploying Claude Code at scale do.

## Quick "I want to" lookup

| I want to… | Use |
|---|---|
| Edit code in VS Code with diffs | VS Code extension |
| Run a long task from my phone | Web (`claude.ai/code`) or iOS app |
| Continue a desktop session from anywhere | Remote Control |
| Trigger Claude from Slack mentions | Slack integration |
| Test a web app Claude is building | Chrome integration |
| Automate macOS GUIs | Computer use |
| Connect Claude to a database | MCP server (e.g. `postgres`), plus a skill for schema knowledge |
| Connect Claude to GitHub/GitLab | MCP server for read access; CI for write actions |
| Push CI events into a session | Channels (custom MCP server with channel capability) |
| Run Claude on a schedule in the cloud | Routines |
| Run Claude on a schedule on my machine | Desktop scheduled tasks |
| Review every PR automatically | GitHub Code Review (or your own CI workflow) |
