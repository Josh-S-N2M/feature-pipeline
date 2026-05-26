---
id: research-note-T-002
topic: Claude Code `claude mcp list` CLI contract
feature_slug: pipeline-quickwins-hardening-r1
version: 1.0.0
status: draft
generated: 2026-05-25T00:00:00Z
generated_by: discovery-external-researcher
---

# Research Note T-002 — Claude Code `claude mcp list` CLI contract

## Topic and question

**Topic name:** Claude Code `claude mcp list` CLI contract.

**Research question (verbatim from prompt):** What is the documented exit-code and output-format contract of `claude mcp list` — specifically, does it return non-zero when any registered MCP server is non-connected, and is per-server connection status (connected vs not-connected) emitted in stdout/stderr in a stable, parseable form that a GitHub Actions workflow can grep / jq?

## Executive summary

The canonical Claude Code documentation is **silent on the exit-code contract and the stdout format of `claude mcp list`**. The `mcp` page documents the sub-command's existence and three sibling commands (`get`, `remove`, `list`), but does not specify exit codes, output format, JSON flag, or status string vocabulary. The companion CLI-reference page documents per-command exit-code behavior for adjacent commands (`claude auth status`, `claude daemon status`, `claude ultrareview`) — the absence of comparable language for `claude mcp list` is conspicuous and should be treated as an undefined / unstable contract rather than an inferred one.

The docs do, however, define a stable, structured, and parseable channel for the same information via the Agent SDK / `claude -p` machinery: a `system/init` event emitted to stdout under `--output-format stream-json` (or as a field in `--output-format json`) carrying an `mcp_servers[]` array whose `status` field uses the **canonical enum `"connected" | "failed" | "needs-auth" | "pending" | "disabled"`**. For a GitHub Actions workflow that must deterministically detect non-connected servers, this Agent-SDK-event path — not `claude mcp list` — is the contract-bearing surface the docs actually back.

For T-002's deciding question ("can a workflow `grep`/`jq` `claude mcp list` to fail the job when a server is non-connected?") the answer from the canonical sources is: **not via `claude mcp list` as documented today.** The supported deterministic path is `claude -p --bare --output-format stream-json` with a minimal prompt, piped to `jq` against `system/init.mcp_servers[].status`.

## Findings

### Finding 1 — `claude mcp list` exists; the CLI-reference page defers to the `mcp` page for details

The top-level CLI-reference table lists `claude mcp` as a sub-command family with the description "Configure Model Context Protocol (MCP) servers" and an example pointing to the standalone `mcp` page. No exit-code or output-format language appears for `claude mcp` in the CLI-reference command table.

- **Source:** https://code.claude.com/docs/en/cli-reference — "CLI commands" table, row `claude mcp`.
- **Quote (≤15 words):** "Configure Model Context Protocol (MCP) servers"
- **Confidence:** high (primary canonical source).
- **Caveats:** Page is undated; the CLI reference is treated as the living spec. Header note states `claude --help` is not exhaustive, so absence from the docs does not by itself prove absence in the binary — but the docs are what a workflow author can rely on for a stable contract.

### Finding 2 — The `mcp` page shows the `claude mcp list` invocation but does not specify exit code, output format, or status tokens

The dedicated MCP page (`/docs/en/mcp`) is the canonical place to look. Under "Managing your servers" it shows:

```bash
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get github

# Remove a server
claude mcp remove github

# (within Claude Code) Check server status
/mcp
```

A reader of this page learns the command exists and learns that **per-server status checking is documented as belonging to the in-session `/mcp` slash command**, not to `claude mcp list`. The page contains no example of `claude mcp list` output, no mention of `--json` on `claude mcp list`, no exit-code statement, and no status-token enumeration for it.

- **Source:** https://code.claude.com/docs/en/mcp — "Installing MCP servers" → "Managing your servers".
- **Paraphrase (no quote used for this finding; reserving the one quote allowed per source for Finding 5).**
- **Confidence:** high.
- **Caveats:** This is an absence-of-evidence finding, not evidence-of-absence. The binary may print structured output the docs simply don't pin down — but for workflow-contract purposes, undocumented behavior is unstable behavior.

### Finding 3 — The CLI reference documents exit codes for adjacent commands; `claude mcp list` is conspicuously absent from that pattern

The CLI-reference command table explicitly pins exit-code behavior for several adjacent diagnostic / status commands. Examples (paraphrased from the canonical table at https://code.claude.com/docs/en/cli-reference):

- `claude auth status` — documented as exiting 0 if logged in, 1 if not.
- `claude daemon status` — documented as exiting 1 if the supervisor isn't running.
- `claude ultrareview` — documented as exiting 0 on success or 1 on failure; supports `--json`.

For each of these the docs explicitly state the exit-code contract in the command description. The `claude mcp` row in the same table contains none of this language. **The pattern across the page is that when the docs intend an exit-code contract, they document it inline; the silence on `claude mcp list` is therefore meaningful** — a workflow that depends on `claude mcp list` returning non-zero on a non-connected server is depending on undocumented behavior.

- **Source:** https://code.claude.com/docs/en/cli-reference — "CLI commands" table; compare rows `claude auth status`, `claude daemon status`, `claude ultrareview` against `claude mcp`.
- **Quote (≤15 words, from the `claude auth status` row, illustrating the documented pattern):** "Exits with code 0 if logged in, 1 if not"
- **Confidence:** high (primary canonical source; cross-row textual comparison).
- **Caveats:** This is a structural inference from the docs page, not a direct statement about `claude mcp list`. It establishes that the docs *would* state the contract if one existed and was intended to be public.

### Finding 4 — The canonical MCP connection-status enumeration is defined for the Agent SDK, not for `claude mcp list`

The Agent SDK pages (`/docs/en/agent-sdk/typescript`, `/docs/en/agent-sdk/python`, `/docs/en/agent-sdk/mcp`) define the authoritative `McpServerStatus` type. Status is one of five values: `connected`, `failed`, `needs-auth`, `pending`, `disabled`. This is the documented platform-wide status vocabulary — and it lives in the SDK-event surface, not in `claude mcp list`'s stdout.

- **Source:** https://code.claude.com/docs/en/agent-sdk/typescript — "McpServerStatus" type definition; mirrored at https://code.claude.com/docs/en/agent-sdk/python.
- **Quote (≤15 words):** `"connected" | "failed" | "needs-auth" | "pending" | "disabled"`
- **Confidence:** high (primary canonical source; identical enumeration in two SDK pages).
- **Caveats:** This enumeration is documented for the `system/init` event's `mcp_servers[].status` field, NOT for any `claude mcp list` stdout token. Re-using these tokens to grep `claude mcp list` output is not safe — that output format is undocumented and may or may not use these strings.

### Finding 5 — `claude -p --output-format stream-json` emits a `system/init` event with `mcp_servers[]` carrying status — this IS the documented, parseable surface

The `mcp` page and the Agent SDK MCP page both document a structured channel that is canonical, stable, and explicitly intended for programmatic checking of MCP connection status:

- At the start of each query, the Agent SDK emits a `system` message with `subtype === "init"` whose payload includes `mcp_servers`, an array of `{ name, status, ... }` records.
- From a CLI / GitHub Actions perspective, this event is reachable via `claude -p --output-format stream-json` (newline-delimited JSON) or via `--output-format json` (single payload, metadata-included). The `headless` page documents both output formats and recommends `--bare` for CI to keep startup deterministic.
- The MCP page's "Error handling" sub-section explicitly shows the supported pattern: filter `mcp_servers` for any record whose `status !== "connected"`.

- **Source:** https://code.claude.com/docs/en/agent-sdk/mcp — "Error handling" section; cross-referenced with https://code.claude.com/docs/en/headless — "Get structured output" section.
- **Quote (≤15 words, from agent-sdk/mcp "Error handling" code sample):** `message.mcp_servers.filter((s) => s.status !== "connected")`
- **Confidence:** high (primary canonical source; identical pattern shown in TypeScript and Python).
- **Caveats:** This is documented from the SDK / `query()` perspective. The CLI bridge is `claude -p`; per the `headless` page, all CLI options apply to `claude -p`, and `--output-format json|stream-json` are the documented structured-output flags. A workflow that uses this path runs an actual agent query (even a trivial prompt like `claude --bare -p "noop" --output-format stream-json | head` is enough to capture the `system/init` event before the model is invoked in any meaningful way) — there is no documented "init-only and emit MCP status as JSON" non-agent invocation other than this. `--init-only` exists on the CLI but its output contract is not documented as structured JSON.

### Finding 6 — Per-server connection lifecycle in the `/mcp` panel uses tokens "pending" and "failed"; the same vocabulary appears in the docs

The MCP page describes runtime lifecycle behavior in language that aligns with the Agent SDK enum:

- During reconnect attempts, "The server appears as pending in `/mcp` while reconnection is in progress."
- "After five failed attempts the server is marked as failed and you can retry manually from `/mcp`."

This confirms that `pending` and `failed` are user-visible status labels in the in-session UI, consistent with the SDK enum from Finding 4. It does NOT confirm that `claude mcp list` prints these same tokens to stdout.

- **Source:** https://code.claude.com/docs/en/mcp — "Automatic reconnection" sub-section.
- **Quote (≤15 words):** "The server appears as pending in `/mcp` while reconnection is in progress"
- **Confidence:** medium (primary source, but applies to in-session `/mcp` panel UI, not to `claude mcp list` CLI output).
- **Caveats:** Inferring that `claude mcp list` uses the same tokens would be unsafe — the docs explicitly call this out for the `/mcp` panel only.

### Finding 7 — Version-skew signals: the Claude Code CLI evolves quickly; specific MCP features pin to specific versions

The CLI-reference and MCP pages cite specific Claude Code versions for individual MCP-related features:

- Initial-connection retry behavior (3 attempts on transient errors) — "as of v2.1.121."
- `--enable-auto-mode` flag — removed in v2.1.111.
- `--resume` picker showing background sessions with `bg` marker — "as of v2.1.144."
- `authServerMetadataUrl` config key — "requires Claude Code v2.1.64 or later."

This pattern means **the surface of "what `claude mcp` does, exactly" is version-sensitive.** A workflow that pins a specific behavior must pin the Claude Code version. The `claude install [version]` command accepts an exact version string (e.g. `2.1.118`), `stable`, or `latest` — so version pinning in CI is supported and is the recommended hardening.

- **Source:** https://code.claude.com/docs/en/cli-reference (`claude install` row); https://code.claude.com/docs/en/mcp ("Automatic reconnection", "Override OAuth metadata discovery").
- **Quote (≤15 words, from cli-reference `claude install` row):** "Accepts a version like `2.1.118`, or `stable` or `latest`"
- **Confidence:** high.
- **Caveats:** No version is documented for when (or if) `claude mcp list` itself stabilized into a particular output format — because the docs do not document its output format at all.

## Synthesis

Three observations emerge across the findings; the third is the load-bearing one for the design phase:

1. **The docs treat `claude mcp list` as a configuration-management command, not a health-check command.** Sibling commands in the same family (`add`, `add-json`, `get`, `remove`, `add-from-claude-desktop`) are all about *what is configured*, not *what is currently connected*. The `mcp` page explicitly points to the in-session `/mcp` slash command for "Check server status" — i.e., the docs route status questions to the runtime panel, not to `claude mcp list`.

2. **The platform's canonical status enumeration lives in the Agent SDK event surface, not in any documented CLI stdout format.** `"connected" | "failed" | "needs-auth" | "pending" | "disabled"` is a stable, primary-source-backed vocabulary — but only the SDK / `claude -p` event stream exposes it deterministically. Grepping `claude mcp list` stdout for these tokens is grepping for tokens the docs never promised it would emit.

3. **A workflow that needs to fail-fast on a non-connected MCP server should NOT depend on `claude mcp list`'s exit code or stdout format.** The contract-bearing path the docs actually support is `claude --bare -p "<noop-prompt>" --output-format stream-json | jq -c 'select(.type=="system" and .subtype=="init") | .mcp_servers[] | select(.status != "connected")'`. If that jq filter returns any rows, fail the job. This uses only documented surfaces: the `--bare` flag, the `-p` flag, `--output-format stream-json`, the `system/init` event, the `mcp_servers[]` field, and the documented status enum. The `claude install <version>` command lets the workflow pin a Claude Code version to lock the behavior.

Trade-off worth flagging to the designer: the SDK-event path costs one `claude -p` invocation per CI run (including model authentication / API tokens), which is heavier than a hypothetical `claude mcp list --json` would be. If the workflow already runs `claude -p` for other purposes (e.g., to execute a task), the MCP health check can piggy-back on the same invocation by reading the first emitted `system/init` event. If the workflow is *only* doing health-check, the cost is paid for that one purpose. There is no documented zero-cost MCP-status-check CLI invocation today.

## Acceptance-criteria check

| # | Criterion | Disposition | Reasoning |
|---|---|---|---|
| 1 | Cite the canonical docs page (URL + section) describing `claude mcp list` exit-code behavior; if silent, say so and cite the next-best authority. | **Partially satisfied.** | The canonical pages (`/docs/en/cli-reference`, `/docs/en/mcp`) are **silent** on `claude mcp list`'s exit-code behavior — this is explicitly cited and contrasted with adjacent commands that DO document exit codes (Findings 2 and 3). Next-best authority would be `claude mcp list --help` from a current binary; the source constraints permit this fallback, but it requires running the binary, which this research instance did not do (no binary execution was performed; per source constraints, only canonical docs + `--help` are admissible, and the latter was out of scope for this research pass). Recommend the designer either consult `claude mcp list --help` locally or treat the contract as undocumented and use the path in Finding 5 instead. |
| 2 | Name the output format and give a parseable-form example. | **Partially satisfied for `claude mcp list`; fully satisfied for the recommended alternative.** | For `claude mcp list` itself: the docs **do not document an output format** (no `--json` flag mentioned, no table-format example, no stdout sample). For the documented-parseable alternative (`claude -p --output-format stream-json`): the format is newline-delimited JSON; an example event is `{"type":"system","subtype":"init","mcp_servers":[{"name":"<n>","status":"connected"|"failed"|"needs-auth"|"pending"|"disabled", ...}], ...}`. |
| 3 | Identify the exact status string used to indicate a non-connected server. | **Satisfied for the alternative path; not satisfied for `claude mcp list`.** | The Agent SDK / `system/init` event uses the enum `"connected" \| "failed" \| "needs-auth" \| "pending" \| "disabled"` (Finding 4). A workflow should treat any value other than `"connected"` as non-connected — this matches the docs' own example pattern (Finding 5). The exact token a workflow can deterministically jq-match for a connected server is `"connected"` (literal, case-sensitive). For `claude mcp list` stdout: **no token is documented**. |
| 4 | Note version-skew risk; recommend pinning if needed. | **Satisfied.** | Finding 7. The CLI evolves with named version pins (e.g., v2.1.121 changed initial-connection retry behavior). Recommend pinning the Claude Code version in the workflow via `claude install <exact-version>` (e.g., `claude install 2.1.144` or a later known-good version). The Agent SDK `McpServerStatus` enum and the `system/init` event have been the documented status surface across the current docs corpus, but the docs do not pin the introduction version of either explicitly; assume the SDK status surface is the stable contract for Claude Code v2.1.x. |

**Overall disposition:** the topic is **resolved with a clear redirection**: the question as literally posed ("does `claude mcp list` return non-zero / does it emit a parseable status?") cannot be answered affirmatively from canonical sources, AND that fact is itself the load-bearing finding for the design. The designer should NOT build the workflow around `claude mcp list`; the designer SHOULD build it around the `system/init` event from `claude --bare -p ... --output-format stream-json`. No escalation to the user is required to proceed — the redirection is well-supported by canonical sources.

## Open questions

1. **Does `claude mcp list --help` print any structured-output flag (e.g. `--json`) that is intentionally omitted from the public docs?** The CLI-reference header explicitly warns: "`claude --help` does not list every flag, so a flag's absence from `--help` does not mean it is unavailable." The inverse — that `--help` may list flags the docs omit — is plausible. A 10-second `claude mcp list --help` locally would resolve this; this research pass did not run the binary.
2. **Is there a documented "init-only" invocation that emits MCP status as structured JSON without running an agent turn?** `--init-only` exists on the CLI (per the CLI reference: "Run Setup and SessionStart hooks, then exit without starting a conversation") but its output contract is not documented as structured JSON. If the designer wants a true zero-model-token health check, this is worth a quick test against the binary.
3. **Are MCP server statuses emitted in the JSON `--output-format json` summary payload (single-payload mode) in addition to the `stream-json` event stream?** The docs describe `--output-format json` as including "session metadata" but do not enumerate every field. The `stream-json` path is documented unambiguously; the `json` path is not.

## Source list

All sources are canonical Anthropic Claude Code documentation (`https://code.claude.com/docs/en/...`):

1. **Claude Code CLI reference.** https://code.claude.com/docs/en/cli-reference — top-level command table; documents `claude mcp` row (defers to MCP page), documents exit-code contracts for `claude auth status`, `claude daemon status`, `claude ultrareview`; documents `claude install <version>`; documents `--output-format`, `-p`, `--bare`. Undated; treated as living spec.
2. **Claude Code MCP page.** https://code.claude.com/docs/en/mcp — "Managing your servers" sub-section (lists `claude mcp list` with no output-format spec); "Automatic reconnection" sub-section (introduces `pending` / `failed` lifecycle tokens for the `/mcp` panel); various sub-sections name specific version pins for MCP behavior changes.
3. **Claude Code headless / Agent SDK CLI.** https://code.claude.com/docs/en/headless — documents `claude -p`, `--bare`, `--output-format text|json|stream-json`, `--include-partial-messages`, `--include-hook-events`.
4. **Agent SDK MCP page.** https://code.claude.com/docs/en/agent-sdk/mcp — "Error handling" and "Troubleshooting" sub-sections; canonical pattern for filtering `mcp_servers` by status; documents `failed` token semantics.
5. **Agent SDK TypeScript reference — `McpServerStatus` type.** https://code.claude.com/docs/en/agent-sdk/typescript — primary definition of the status enum `"connected" | "failed" | "needs-auth" | "pending" | "disabled"`.
6. **Agent SDK Python reference — `McpServerStatus` TypedDict.** https://code.claude.com/docs/en/agent-sdk/python — mirror definition of the same status enum.

All retrievals were via Context7 library `/websites/code_claude` and direct `code.claude.com/docs/en/*.md` fetches, per the source constraints. No third-party sources were consulted.
