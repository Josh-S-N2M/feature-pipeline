# Agent SDK reference

The Agent SDK is the programmatic interface to Claude Code. Use it when building applications, services, or scripts that embed Claude Code capabilities — agents that run on a schedule, internal developer tools, custom workflows that need fine-grained orchestration, evaluation harnesses, etc.

Two SDKs with feature parity: **TypeScript** (`@anthropic-ai/claude-agent-sdk`) and **Python** (`claude_agent_sdk`).

This reference covers the architecture, the common APIs, and the most useful patterns. The SDK surface is large — for exhaustive parameter lists and every type, fetch:
- `https://code.claude.com/docs/en/agent-sdk/overview.md`
- `https://code.claude.com/docs/en/agent-sdk/python.md`
- `https://code.claude.com/docs/en/agent-sdk/typescript.md`

## Contents

- Mental model
- Authentication
- `query()` — fire and forget
- `ClaudeSDKClient` — multi-turn sessions
- `ClaudeAgentOptions` — the configuration object
- Subagents in the SDK
- Hooks in the SDK
- Custom tools
- MCP servers in the SDK
- Streaming events for UI
- File checkpointing in the SDK
- Common SDK patterns
- SDK reference pages

## Mental model

The SDK exposes the same agentic loop and built-in tools as the CLI, plus the same configuration sources (CLAUDE.md, skills, hooks, MCP). The difference is **you control orchestration in code** instead of typing in a terminal.

Two main entry points:

- **`query()`** — fire-and-forget. Send a prompt, iterate over the streamed messages, done. No persistent client object. Equivalent to running `claude -p` from code. Use for one-shot tasks.
- **`ClaudeSDKClient`** (Python) / managing your own session (TypeScript) — persistent client, multiple back-and-forth turns, can interrupt mid-task, can react to streamed events. Use for interactive applications, REPLs, multi-turn workflows.

Both speak the same options object (`ClaudeAgentOptions`), receive the same message types, and use the same hook and tool primitives.

## Authentication

The SDK reads the same auth as the CLI:

```bash
export ANTHROPIC_API_KEY="..."                  # Direct Anthropic
export CLAUDE_CODE_USE_BEDROCK=1                # Amazon Bedrock
export CLAUDE_CODE_USE_VERTEX=1                 # Google Vertex AI
export AWS_BEARER_TOKEN_BEDROCK="..."           # Bedrock API key (alternative to AWS creds)
```

For Bedrock, Vertex, Foundry, or LLM gateway specifics: `https://code.claude.com/docs/en/agent-sdk/overview.md`.

## `query()` — fire and forget

The simplest usage. Send a prompt, iterate over the messages.

**Python:**
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def main():
    async for message in query(
        prompt="Refactor the auth module to use OAuth2",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Write", "Glob", "Grep", "Bash"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\nDone: {message.result}")

asyncio.run(main())
```

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Refactor the auth module to use OAuth2",
  options: {
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep", "Bash"],
    permissionMode: "acceptEdits",
  },
})) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "text") console.log(block.text);
    }
  }
  if (message.type === "result" && message.subtype === "success") {
    console.log(`Done: ${message.result}`);
  }
}
```

## `ClaudeSDKClient` — multi-turn sessions

Persistent client for back-and-forth interaction. Python has the dedicated class; TypeScript achieves the same pattern by managing the session ID and resuming.

**Python — interactive multi-turn:**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Bash"],
        permission_mode="acceptEdits",
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Read the auth module")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # Same session, with full context
        await client.query("Now find all callers")
        async for message in client.receive_response():
            ...
```

`ClaudeSDKClient` methods worth knowing:

| Method | Purpose |
|---|---|
| `connect(prompt=None)` | Open the connection (or use `async with`) |
| `query(prompt, session_id="default")` | Send a new prompt |
| `receive_messages()` / `receive_response()` | Iterate streamed messages |
| `interrupt()` | Stop the current task mid-execution |
| `set_permission_mode(mode)` | Switch permission mode |
| `set_model(model)` | Switch model |
| `rewind_files(message_id)` | Roll back files to a checkpoint (with `enable_file_checkpointing=True`) |
| `get_mcp_status()` | Check connected MCP servers |
| `reconnect_mcp_server(name)` | Reconnect a specific MCP server |
| `disconnect()` | Close the connection |

**TypeScript — sessions via `resume`:**
```typescript
let sessionId: string | undefined;

// First call
for await (const msg of query({
  prompt: "Read the auth module",
  options: { allowedTools: ["Read", "Glob"] },
})) {
  sessionId ??= msg.session_id;
}

// Resume with full context
for await (const msg of query({
  prompt: "Now find all callers",
  options: {
    resume: sessionId,
    allowedTools: ["Read", "Glob", "Grep"],
  },
})) {
  // ...
}
```

## `ClaudeAgentOptions` — the configuration object

Both SDKs accept the same options. The most useful fields:

| Field (TS / Python) | Purpose |
|---|---|
| `model` | Model ID or alias (`opus`, `sonnet`, `claude-opus-4-7`) |
| `permissionMode` / `permission_mode` | Permission mode: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `allowedTools` / `allowed_tools` | List of tool names (and `mcp__server__tool` names) auto-allowed |
| `disallowedTools` / `disallowed_tools` | Explicit deny list |
| `cwd` | Working directory |
| `additionalDirectories` / `additional_directories` | Extra accessible directories |
| `systemPrompt` / `system_prompt` | Override or extend the system prompt (see below) |
| `settingSources` / `setting_sources` | Which settings layers to load: `["user"]`, `["project"]`, `["user", "project"]` |
| `mcpServers` / `mcp_servers` | MCP server configurations (see below) |
| `agents` | Subagent definitions (inline) |
| `hooks` | Hook callbacks (see below) |
| `maxTurns` / `max_turns` | Cap turns to bound runaway loops |
| `resume` | Session ID to resume |
| `enableFileCheckpointing` / `enable_file_checkpointing` | Track file checkpoints for rewind |
| `includePartialMessages` / `include_partial_messages` | Stream partial deltas (for UI rendering) |
| `extraArgs` / `extra_args` | Pass-through CLI args |

**System prompt presets.** Critical detail: by default the SDK does **not** load Claude Code's default system prompt. To get Claude Code behavior (built-in coding instructions, project awareness), pass:

```python
ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
    setting_sources=["project"],   # Loads CLAUDE.md too
)
```

```typescript
{
  systemPrompt: { type: "preset", preset: "claude_code" },
  settingSources: ["project"],
}
```

Without `settingSources`, the SDK does **not** auto-discover CLAUDE.md, project skills, hooks, or permissions — that is by design (clean baseline for embedding into other apps). Pass `["project"]` for project-only, `["user", "project"]` for both.

For system prompt customization: `https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts.md`.

## Subagents in the SDK

Subagents can be defined either via files (the same `.claude/agents/*.md` discovered when `setting_sources` includes the appropriate scope) or **inline** via the `agents` option. Inline definitions are useful for self-contained scripts.

**Python:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async for message in query(
    prompt="Use the code-reviewer agent on src/auth/",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "Agent"],   # "Agent" enables subagent invocation
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code reviewer for security and quality",
                prompt="You are a senior code reviewer. Focus on security and maintainability.",
                tools=["Read", "Grep", "Glob"],
                model="sonnet",
            ),
        },
    ),
):
    if hasattr(message, "result"):
        print(message.result)
```

**TypeScript:**
```typescript
for await (const message of query({
  prompt: "Use the code-reviewer agent on src/auth/",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Agent"],
    agents: {
      "code-reviewer": {
        description: "Expert code reviewer for security and quality",
        prompt: "You are a senior code reviewer. Focus on security and maintainability.",
        tools: ["Read", "Grep", "Glob"],
        model: "sonnet",
      },
    },
  },
})) {
  if ("result" in message) console.log(message.result);
}
```

**`Agent` must be in `allowedTools`** for subagents to be invoked. Without it, Claude can see the subagent definition but cannot call it.

## Hooks in the SDK

Hooks attach to the same lifecycle events as file-based hooks (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, etc.) but as in-process callbacks instead of shell commands. Useful for security policy, auditing, custom permission logic.

**Python:**
```audit-example -- Documents the curl-pipe-shell installer pattern the auditor flags via DE-1 scanner; reference catalog of anti-pattern signatures, not real install instructions.
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, HookContext

async def block_dangerous_bash(input_data, tool_use_id, context):
    if input_data["tool_name"] == "Bash":
        cmd = input_data["tool_input"].get("command", "")
        if "rm -rf /" in cmd or "curl | sh" in cmd:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked",
                }
            }
    return {}

async def log_tool_use(input_data, tool_use_id, context):
    print(f"[tool] {input_data.get('tool_name')}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_bash], timeout=30),
            HookMatcher(hooks=[log_tool_use]),  # No matcher = all tools
        ],
        "PostToolUse": [HookMatcher(hooks=[log_tool_use])],
    }
)
```

**TypeScript:**
```audit-example -- Documents the curl-pipe-shell installer pattern the auditor flags via DE-1 scanner; reference catalog of anti-pattern signatures, not real install instructions.
const blockDangerousBash: HookCallback = async (input, toolUseID, { signal }) => {
  if (input.hook_event_name !== "PreToolUse") return {};
  const cmd = (input as PreToolUseHookInput).tool_input?.command ?? "";
  if (cmd.includes("rm -rf /") || cmd.includes("curl | sh")) {
    return {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Dangerous command blocked",
      },
    };
  }
  return {};
};
```

The hook output schema is the same as file-based hooks. See `references/extensions.md` section 5 for the event list and output fields.

## Custom tools

Build your own tools and expose them via an in-process MCP server. The model can call them like any other tool.

**Python — `@tool` decorator:**
```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args):
    try:
        result = eval(args["expression"], {"__builtins__": {}})
        return {"content": [{"type": "text", "text": f"Result: {result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "is_error": True}

server = create_sdk_mcp_server(name="utilities", version="1.0.0", tools=[calculate])

options = ClaudeAgentOptions(
    mcp_servers={"utils": server},
    allowed_tools=["mcp__utils__calculate"],
)
```

The tool name in `allowed_tools` follows the `mcp__<server-key>__<tool-name>` pattern.

**TypeScript** has the equivalent — see `https://code.claude.com/docs/en/agent-sdk/typescript.md` for the exact API.

## MCP servers in the SDK

The SDK supports the same MCP transports as the CLI: stdio, SSE, HTTP, plus an SDK-native transport for in-process servers.

```python
ClaudeAgentOptions(
    mcp_servers={
        # SDK in-process server (created with create_sdk_mcp_server)
        "utils": my_server_instance,

        # stdio (most common)
        "github": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        },

        # HTTP
        "stripe": {
            "type": "http",
            "url": "https://mcp.stripe.com",
            "headers": {"Authorization": f"Bearer {api_token}"},
        },

        # SSE
        "remote": {
            "type": "sse",
            "url": "https://api.example.com/mcp/sse",
            "headers": {"Authorization": f"Bearer {api_token}"},
        },
    },
    allowed_tools=["mcp__github", "mcp__stripe"],   # Allow whole servers
)
```

For MCP architecture and `.mcp.json` patterns, see `references/extensions.md` section 6 and `references/integrations.md`.

## Streaming events for UI

For applications that render incremental output (chat UIs, progress indicators), enable partial messages:

```python
options = ClaudeAgentOptions(
    include_partial_messages=True,
    allowed_tools=["Read", "Bash", "Grep"],
)

async for message in query(prompt="Find all TODOs", options=options):
    if hasattr(message, "event"):
        event = message.event
        if event.get("type") == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                print(delta.get("text", ""), end="", flush=True)
```

The event types follow the Anthropic API streaming protocol: `content_block_start`, `content_block_delta`, `content_block_stop`, plus higher-level message events.

For a full streaming UI pattern (status indicators, tool-call rendering): `https://code.claude.com/docs/en/agent-sdk/streaming-output.md`.

## File checkpointing in the SDK

Programmatic equivalent of the CLI's checkpoint/rewind feature:

```python
options = ClaudeAgentOptions(
    enable_file_checkpointing=True,
    permission_mode="acceptEdits",
    extra_args={"replay-user-messages": None},
)

async with ClaudeSDKClient(options) as client:
    await client.query("Refactor the auth module")
    checkpoints = []
    async for msg in client.receive_response():
        if hasattr(msg, "uuid") and msg.uuid:
            checkpoints.append(msg.uuid)

# Later: rewind
async with ClaudeSDKClient(ClaudeAgentOptions(
    enable_file_checkpointing=True,
    resume=session_id,
)) as client:
    await client.query("")
    async for msg in client.receive_response():
        await client.rewind_files(checkpoints[0])
        break
```

For complete checkpoint patterns: `https://code.claude.com/docs/en/agent-sdk/file-checkpointing.md`.

## Common SDK patterns

**Embedding in a CLI tool.** Use `query()` with `system_prompt` set to a custom prompt (no preset) for non-coding agents. Pass `setting_sources=[]` to skip auto-discovery and have a clean baseline.

**Building a Claude Code wrapper.** Use `query()` with `system_prompt={"type": "preset", "preset": "claude_code"}` and `setting_sources=["project"]`. You get the full Claude Code behavior including CLAUDE.md, skills, and hooks.

**Long-running services.** Use `ClaudeSDKClient` with explicit `connect()` and `disconnect()`. Add hooks for auditing every tool call. Set `max_turns` to bound runaway tasks.

**Headless CI replacement.** `query()` is essentially `claude -p` programmatically. Lower overhead than spawning a subprocess for each invocation, plus you can react to streamed messages.

## SDK reference pages

When you need exact parameter signatures, type definitions, or features not covered here:

- Overview and getting started — `https://code.claude.com/docs/en/agent-sdk/overview.md`
- Python API — `https://code.claude.com/docs/en/agent-sdk/python.md`
- TypeScript API — `https://code.claude.com/docs/en/agent-sdk/typescript.md`
- Subagents — `https://code.claude.com/docs/en/agent-sdk/subagents.md`
- Hooks — `https://code.claude.com/docs/en/agent-sdk/hooks.md`
- Slash commands (definition) — `https://code.claude.com/docs/en/agent-sdk/slash-commands.md`
- Sessions — `https://code.claude.com/docs/en/agent-sdk/sessions.md`
- Modifying system prompts — `https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts.md`
- Streaming output — `https://code.claude.com/docs/en/agent-sdk/streaming-output.md`
- MCP usage — `https://code.claude.com/docs/en/agent-sdk/mcp.md`
- File checkpointing — `https://code.claude.com/docs/en/agent-sdk/file-checkpointing.md`
- Loading Claude Code features (CLAUDE.md, skills, hooks via `setting_sources`) — `https://code.claude.com/docs/en/agent-sdk/claude-code-features.md`
- Agent loop architecture — `https://code.claude.com/docs/en/agent-sdk/agent-loop.md`
