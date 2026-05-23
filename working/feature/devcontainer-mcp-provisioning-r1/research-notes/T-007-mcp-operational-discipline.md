---
id: RN-T-007-mcp-operational-discipline
doc_type: research-note
version: 1.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
topic_id: T-007
topic_name: MCP Operational Discipline
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
---

# T-007 — MCP Operational Discipline (Research Note)

## Topic and question

**Topic:** MCP Operational Discipline (server-agnostic operational concerns; applies uniformly to all seven MCP servers including GitNexus per the v3 note in the Research Plan).

**Research question (six sub-questions):**

1. Health endpoints / readiness signaling for MCP servers — what conventions exist? Do MCP servers typically expose a ready/health hook beyond TCP-connect? Is there a standard MCP `ping` / probe capability beyond `claude mcp list` connect status?
2. Claude Code's MCP transport-event surface and disconnect behavior — how does Claude Code surface MCP transport events (connect, disconnect, error) to the operator and to running agents? What happens when an MCP server dies mid-session? Reconnect behavior? Failure-event channel?
3. Structured logging patterns for stdio vs HTTP MCP servers in Codespaces — how do practitioners capture stdio streams from stdio-transport MCP servers? Where do remote-HTTP MCPs' logs land? Per-server log routing patterns?
4. Credential redaction patterns for MCP logs — how do MCP servers and Claude Code handle credentials appearing in trace/log output? Industry patterns (redact-at-source, redact-in-collector, post-process)?
5. Operator-facing failure-feedback patterns — how is an MCP failure surfaced *to the user* (not just to logs)? Patterns from devcontainer / lifecycle health-check ecosystems. Including: when a primary MCP fails over to a documented fallback (e.g., GitNexus → codebase-memory-mcp per ADR-0018), how is the transition made operator-visible?
6. Runtime monitoring approaches for MCP fleets — local-only patterns (no remote telemetry sink) for keeping the seven-server MCP surface healthy across a Codespace session lifetime.

## Executive summary

The MCP protocol itself provides exactly one cross-transport health primitive — the JSON-RPC `ping` method (Anthropic MCP spec, 2025-03-26). Stdio servers do not and cannot expose HTTP `/health`; the spec-canonical liveness check is to send `{"jsonrpc":"2.0","method":"ping","id":"…"}` periodically and treat absent or slow responses as connection failure. Claude Code surfaces transport state through `claude mcp list`, the in-session `/mcp` command (pending / failed states), and `--debug` logs, and auto-reconnects HTTP/SSE servers with five-attempt exponential backoff but explicitly does **not** auto-reconnect stdio servers (per Claude Code MCP docs). Logging is governed by two converging conventions: stderr-for-stdio (anything on stdout corrupts the JSON-RPC stream) and `notifications/message` for the spec-level client-visible log channel (MCP spec, 2025-06-18, logging utility). Credential redaction has no MCP-specific standard; the strongest industry pattern is **redact at the instrumentation source by header/env-var name** (OWASP MCP Top-10 2025 / Velida) rather than regex post-processing. Operator-facing failure feedback is the weakest area: no consensus pattern exists for MCP fleets, and the devcontainer ecosystem itself has no native health-check primitive (Microsoft devcontainer issue #786), so projects assemble their own surfacing — log files, `/mcp` state, stderr banners, or a dedicated event file. Primary-to-fallback transitions specifically have **no consensus pattern** in the literature; this is the genuine novel design space for FR-9 / AC-FR-9-d. Local-only fleet monitoring without Prometheus/Grafana is dominated by a "phased" approach: local structured logs to per-server files first, then optional OpenTelemetry export later.

## Findings

### Sub-question 1 — Health endpoints / readiness signaling

#### F1.1 — MCP `ping` is the canonical cross-transport liveness primitive

- **Claim.** MCP defines a JSON-RPC `ping` method that either side may invoke; the receiver MUST return an empty result promptly, and timeout MAY be treated as connection failure. This is the only spec-canonical health primitive that works uniformly across stdio and HTTP transports.
- **Source.** Anthropic, *Model Context Protocol — Ping*, spec version 2025-03-26. https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping
- **Quote (≤15 words).** "The receiver MUST respond promptly with an empty response."
- **Confidence.** High (primary spec).
- **Caveats.** The spec calls ping "optional," and most SDKs auto-implement the *responder* side but the client must initiate. Ping checks the JSON-RPC layer but not downstream dependencies (DB, upstream API).

#### F1.2 — Stdio servers cannot use HTTP `/health`; ping is the substitute

- **Claim.** HTTP MCP servers typically expose `/health` and `/ready` endpoints for liveness vs readiness, but stdio servers (which the MCP-OpenAPI-schema, actionlint-mcp, Serena, GitNexus, etc. typically use) have no HTTP surface; the recommended substitute is periodic JSON-RPC `ping`, with a 30-second interval and a 2–5-second timeout, and "3 consecutive failed checks before triggering a restart."
- **Source.** Fast.io, *How to Implement MCP Server Health Checks (Pattern Guide)*, 2026. https://fast.io/resources/implementing-mcp-server-health-checks/
- **Quote (≤15 words).** "Timeout: between 2 to 5 seconds … any latency usually indicates a blocked event loop."
- **Confidence.** Medium (reputable vendor pattern guide, not a primary spec).
- **Caveats.** "3 failed checks before restart" is a Fast.io recommendation, not protocol-mandated; tune to local needs.

#### F1.3 — Ping verifies the JSON-RPC layer, not application readiness

- **Claim.** A successful ping confirms the message loop is unblocked and JSON-RPC serialization works; it does not confirm the server can actually answer tool calls (downstream DB, auth, file-system access). Production-leaning patterns add an "internal health-check tool" callable by the operator/client to assert downstream dependencies.
- **Source.** Fast.io health-check pattern guide (same URL as F1.2). Cross-referenced by MCPcat, *Build Health Check Endpoints for MCP Servers*. https://mcpcat.io/guides/building-health-check-endpoint-mcp-server/
- **Confidence.** Medium.
- **Caveats.** Not all MCP servers expose such a tool today; for this project's seven servers, none have been verified to do so.

### Sub-question 2 — Claude Code's MCP transport-event surface and disconnect behavior

#### F2.1 — HTTP/SSE auto-reconnect; stdio servers do not

- **Claim.** Claude Code automatically reconnects HTTP and SSE MCP servers that disconnect mid-session, with up to five attempts and exponential backoff starting at one second. **Stdio MCP servers are explicitly not auto-reconnected** — when a stdio process dies, the server is marked failed and only operator action (e.g., a restart command) recovers it. As of v2.1.121, initial-connect failures (5xx, connection refused, timeout) on HTTP/SSE retry up to three times.
- **Source.** Anthropic, *Connect Claude Code to tools via MCP — Automatic reconnection*. https://code.claude.com/docs/en/mcp
- **Quote (≤15 words).** "Stdio servers are local processes and are not reconnected automatically."
- **Confidence.** High (primary product docs).
- **Caveats.** Six of the seven servers in this feature are most naturally stdio (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, GitNexus, codebase-memory-mcp); only Context7 and Exa have remote-HTTP variants. The no-auto-reconnect rule therefore applies to most of the surface.

#### F2.2 — `/mcp` and `claude mcp list` are the operator-visible state surface

- **Claim.** The `/mcp` slash-command in-session shows per-server state (connected / pending / failed) and tool count; `claude mcp list` at the shell shows configured servers and their connection status. A reconnecting server shows `pending`; after five failed reconnects it shows `failed` and is retried only on operator action.
- **Source.** Anthropic, *Connect Claude Code to tools via MCP — Managing your servers / Automatic reconnection* (same URL as F2.1).
- **Confidence.** High.
- **Caveats.** Known bug in v2.1.62 returned empty output for `claude mcp list` (GitHub issue #29492); operator-visibility was briefly degraded. https://github.com/anthropics/claude-code/issues/29492

#### F2.3 — `claude --debug` is the diagnostic-level surface for transport events

- **Claim.** When MCP-server failures aren't obvious from `/mcp`, the recommended next step is `claude --debug`, which logs spawn lines and transport-close events. A characteristic log message is "Server transport closed unexpectedly, this is likely due to the process exiting early."
- **Source.** Anthropic Claude Code troubleshooting documentation and GitHub issue threads (e.g., issue #4097 "MCP server disconnects immediately"). https://github.com/anthropics/claude-code/issues/4097
- **Confidence.** Medium (issue-thread + docs corroboration).
- **Caveats.** The specific log strings are not part of a stable contract; they're observed behavior at the time of writing.

#### F2.4 — Per-server `MCP_TIMEOUT` and `timeout` field control startup/tool-call latency

- **Claim.** `MCP_TIMEOUT` (env var) controls MCP server startup timeout; a per-server `"timeout": <milliseconds>` field in `.mcp.json` sets a hard wall-clock cap on each tool call. The HTTP first-byte budget has a 60-second minimum regardless. Below-1000 values floor at one second.
- **Source.** Anthropic, *Connect Claude Code to tools via MCP — Tips* (same URL as F2.1).
- **Confidence.** High.
- **Caveats.** Useful for the FR-8 health check's per-server probe envelope; especially relevant for slow-starting stdio servers (Serena, GitNexus) where the default may need raising.

### Sub-question 3 — Structured logging patterns for stdio vs HTTP MCP servers

#### F3.1 — Stdio MUST log to stderr, never stdout

- **Claim.** Stdio MCP servers must direct all log output to stderr. Logging to stdout corrupts the JSON-RPC framing on the transport. The host application captures stderr automatically.
- **Source.** Anthropic, *Model Context Protocol — Debugging*. https://modelcontextprotocol.io/docs/tools/debugging
- **Quote (≤15 words).** "Local MCP servers should not log messages to stdout, as this will interfere with protocol operation."
- **Confidence.** High (primary docs).
- **Caveats.** Buffer-management caveat: orchestrators must consume stderr continuously or the stdio process can block when the buffer fills.

#### F3.2 — `notifications/message` is the spec-level client-visible log channel

- **Claim.** For transports beyond stdio (notably HTTP), the spec-canonical log channel is the `notifications/message` JSON-RPC notification. It carries `level` (RFC 5424: debug, info, notice, warning, error, critical, alert, emergency), optional `logger` name, and arbitrary JSON `data`. Clients adjust minimum level via `logging/setLevel`.
- **Source.** Anthropic, *Model Context Protocol — Logging (utility)*, spec 2025-06-18. https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging
- **Quote (≤15 words).** "Log messages MUST NOT contain credentials or secrets."
- **Confidence.** High (primary spec).
- **Caveats.** Implementations vary in `notifications/message` adoption; for stdio servers, stderr is still the primary channel.

#### F3.3 — Per-server file logging is the convention; rotation is operator-owned

- **Claim.** Claude Desktop writes per-server logs to `~/Library/Logs/Claude/mcp*.log` (macOS) and `%APPDATA%\Claude\logs\mcp*.log` (Windows); Claude Code does not publish equivalent canonical paths, but practitioners adopt the same per-server-file convention. There is no MCP-canonical rotation policy; operators apply standard log-rotation tooling.
- **Source.** Anthropic, *Model Context Protocol — Debugging — Viewing logs* (same URL as F3.1).
- **Confidence.** High for Claude Desktop; medium for Claude Code (the project's `~/.claude` log layout is not in the public docs at the level of granularity needed).
- **Caveats.** For Codespaces / devcontainer use, log files inside the container survive container restarts only if on a persisted volume; ephemeral container deletion loses logs unless exported.

#### F3.4 — Structured JSON-on-stderr is the recommended format

- **Claim.** Industry practice (multiple vendor MCP-logging guides converge here) is structured JSON on stderr with request ID, server name, method, and timestamp. Synchronous logging is discouraged; use async (non-blocking) loggers. Disable debug-level logging in production.
- **Source.** MCPevals, *MCP Logging Tutorial*, 2026. https://www.mcpevals.io/blog/mcp-logging-tutorial
- **Confidence.** Medium (engineering blog, not a spec, but consistent with the Anthropic Debugging guidance).
- **Caveats.** No single canonical schema for the JSON structure exists.

### Sub-question 4 — Credential redaction patterns for MCP logs

#### F4.1 — MCP spec mandates "no credentials in logs" but provides no technique

- **Claim.** The MCP logging spec states log messages MUST NOT contain credentials or secrets, and SHOULD rate-limit, validate, and monitor for sensitive content. The spec is normative on the **prohibition** but silent on the **technique** for enforcement.
- **Source.** Anthropic, *Model Context Protocol — Logging (utility)* (same URL as F3.2).
- **Confidence.** High.
- **Caveats.** The spec-level prohibition does not constrain implementations — each server author decides how to enforce.

#### F4.2 — Redact at instrumentation source by header/env-var name (strongest pattern)

- **Claim.** The most reliable redaction pattern documented in production MCP write-ups is to overwrite known-sensitive header names and env-var names with `[REDACTED]` at the instrumentation layer (e.g., the OpenTelemetry `EnrichWithHttpRequestMessage` callback) before the trace/log record is exported. Targeting by known name (e.g., `Authorization`, `X-Api-Key`, `Ocp-Apim-Subscription-Key`) is more reliable than regex pattern-matching on credential shapes.
- **Source.** Will Velida, *Preventing MCP01 — Token Mismanagement and Secret Exposure in MCP Servers*. https://www.willvelida.com/posts/preventing-mcp01-token-mismanagement-secret-exposure
- **Quote (≤15 words).** "By explicitly setting … to `[REDACTED]`, the actual subscription key value is overwritten before the trace is exported."
- **Confidence.** Medium (single-vendor implementation example; pattern is reasonable but not standards-anchored).
- **Caveats.** Header-name-targeted redaction misses credentials that appear in URL query strings or in tool-call argument bodies; a defense-in-depth approach combines name-based redaction with shape-based regex as a backstop.

#### F4.3 — OWASP MCP Top-10 ranks credential leakage as the #1 risk

- **Claim.** The OWASP MCP Top-10 (2025) ranks Token Mismanagement and Secret Exposure as MCP01 — the highest-priority MCP risk. The recommended controls cluster around (i) ephemeral context for credential-touching operations, (ii) protected diagnostic-trace storage with strict access control, and (iii) redaction before write to logs/telemetry.
- **Source.** OWASP, *MCP01:2025 — Token Mismanagement and Secret Exposure*. https://owasp.org/www-project-mcp-top-10/2025/MCP01-2025-Token-Mismanagement-and-Secret-Exposure
- **Quote (≤15 words).** "Redact or mask secrets before writing to logs or telemetry."
- **Confidence.** High (OWASP is an authoritative source for security taxonomies).
- **Caveats.** OWASP is prescriptive about the prohibition but, like the MCP spec, intentionally non-prescriptive on the implementation technique.

#### F4.4 — Env-var-name-driven redaction is feasible because `.mcp.json` names the env vars

- **Claim.** Claude Code's `.mcp.json` schema uses `${VAR_NAME}` substitution for credentials and an explicit `env` block for server-process environment variables. The names of all credential-bearing env vars are therefore knowable at registration time, which makes env-var-name-driven redaction (rather than value-shape regex) a particularly good fit for this project's setup.
- **Source.** Anthropic, *Connect Claude Code to tools via MCP — Environment variable expansion in `.mcp.json`* (same URL as F2.1).
- **Confidence.** High (this is a property of the existing `.mcp.json` schema).
- **Caveats.** This is a synthesis observation rather than an externally documented pattern; the design implication is that the augmented `auditing-mcp` could enforce a redaction-list-equals-env-vars-list invariant.

### Sub-question 5 — Operator-facing failure-feedback patterns (including primary/fallback transitions)

#### F5.1 — Claude Code surfaces MCP failure to the operator via three channels

- **Claim.** Claude Code's operator-visible MCP failure surface is the union of (i) the `/mcp` panel showing `failed` state with a manual-retry affordance, (ii) `claude mcp list` showing the same state at shell level, and (iii) `--debug`-mode stderr lines. There is no canonical structured "MCP failure record" emitted as a separate event file by default.
- **Source.** Anthropic Claude Code MCP docs (same URL as F2.1).
- **Confidence.** High.
- **Caveats.** The session log captures transport events but is not formatted as a structured record per failure — projects that want a structured per-failure record build it themselves.

#### F5.2 — Devcontainers have no native health-check primitive

- **Claim.** The dev-container specification (Microsoft) does not include a native health-check field analogous to Docker Compose's `healthcheck` or Kubernetes' readiness probes. Microsoft's own tracking issue (#786) acknowledges this as an open feature request. The community convention is to run health-assertion scripts in `postStartCommand` (every container start) and one-time validation in `postCreateCommand`.
- **Source.** Microsoft, *Implement dev container health check inline with OCI spec — issue #786*. https://github.com/microsoft/vscode-dev-containers/issues/786
- **Confidence.** High (project-tracked open issue).
- **Caveats.** This means MCP health-check surfacing inside a Codespace is greenfield — the project chooses its own pattern.

#### F5.3 — Operator-facing failure feedback patterns in containerized environments

- **Claim.** In containerized dev-environment ecosystems (e.g., Coder dev containers), failure feedback is surfaced through three converging channels: (i) startup-script log files at known paths (e.g., `/tmp/coder-startup-script.log`), (ii) a dashboard/status surface showing per-service running state, and (iii) recommended diagnostic commands (`docker ps`, build-output inspection). The pattern emphasizes the **known log file path** as the primary recourse and the dashboard as the at-a-glance surface.
- **Source.** Coder, *Troubleshooting dev containers*. https://coder.com/docs/user-guides/devcontainers/troubleshooting-dev-containers
- **Quote (≤15 words).** "Verify the dev container is running in the Coder dashboard."
- **Confidence.** Medium (one vendor's pattern; not a cross-ecosystem standard but consistent with the broader convention).
- **Caveats.** Codespaces does not have an equivalent "service dashboard" inside the container; the operator-visible surface is whatever the project assembles (stderr banner, MOTD on attach, dedicated log file, or a per-server check in `postStart`).

#### F5.4 — Primary-to-fallback transitions: NO CONSENSUS PATTERN

- **Claim.** Across the surveyed sources (Anthropic MCP docs, vendor MCP server docs, MCP-monitoring write-ups, devcontainer troubleshooting docs, OWASP MCP Top-10), **no consensus pattern exists** for how a primary-MCP-to-fallback-MCP transition is surfaced operator-visibly when the fallback fires in-product. The literature treats MCP servers as independent — a server is either available or failed — and does not address the "primary degraded; using fallback" semantic that ADR-0018 codifies for GitNexus → codebase-memory-mcp.
- **Source.** Negative finding spanning all sources surveyed for this note. The closest analogue is the generic "circuit-breaker open → using fallback path" pattern from microservice literature, but it is not MCP-specific.
- **Confidence.** High (the absence is well-supported; multiple sources surveyed yielded no positive pattern).
- **Caveats.** This is the **genuine novel design space** for FR-9 / AC-FR-9-d. Design has three reasonable options, none externally precedented: (a) **stderr banner on transition** ("[MCP] primary `gitnexus` unhealthy; agent `discovery-codebase-researcher` proceeding on fallback `codebase-memory-mcp`"); (b) **dedicated event file** in the project's runtime log surface (e.g., `.claude/runtime/mcp-events.jsonl` with `event: fallback_exercised, primary, fallback, agent, ts`); (c) **agent-level acknowledgement in the agent's own output** — the sub-agent that triggers the fallback names it explicitly in its result. Option (b) aligns most cleanly with the existing audit + structured-record discipline this project already practices for state transitions. Option (a) is lowest-friction but ephemeral. Option (c) places the obligation on each consuming agent, which has uniformity risk.

### Sub-question 6 — Runtime monitoring approaches for local MCP fleets

#### F6.1 — Phased-monitoring approach is the documented small-team pattern

- **Claim.** For small MCP deployments (≤10 concurrent users, ≤50 tools), the recommended monitoring path is: **start with local structured logs to per-server files**, add structured log forwarding only when the team grows, then add dashboards/alerting last. Prometheus/Grafana is overkill for single-operator local Codespace use; OpenTelemetry can be added later without redesigning the local surface.
- **Source.** SigNoz, *MCP Observability with OpenTelemetry*. https://signoz.io/blog/mcp-observability-with-otel/
- **Confidence.** Medium (vendor engineering write-up).
- **Caveats.** SigNoz's recommendation is shaped by their commercial interest; the underlying "start local, add telemetry later" advice is consistent across multiple sources.

#### F6.2 — Active ping-loop as a sidecar / supervisor process

- **Claim.** For runtime monitoring without a remote telemetry sink, the documented pattern is an active ping-loop (per F1.2) — a small supervisor process that issues `ping` to each registered MCP server on a 30-second interval, logs the result, and surfaces three consecutive failures as a state change. This is the local-only equivalent of a readiness probe.
- **Source.** Fast.io health-check pattern guide (same URL as F1.2).
- **Confidence.** Medium.
- **Caveats.** This adds a moving part (the supervisor) that itself needs to be supervised; for a seven-server Codespace, the supervisor can be a `postStart` script that runs once at attach time (one-shot health check) rather than a long-running daemon.

#### F6.3 — Decouple observability from the server via a proxy / supervisor

- **Claim.** ToolHive and similar proxy patterns decouple MCP observability from the server itself — the supervisor sits in front of the server's stdio transport and captures messages without requiring server-side code changes. This pattern is useful when the operator does not control the upstream server (e.g., GitNexus, Serena, Terraform MCP — none of which this project authors).
- **Source.** Stacklok / DEV Community, *Bridging the Observability Gap in MCP Servers with ToolHive*. https://dev.to/stacklok/bridging-the-observability-gap-in-mcp-servers-with-toolhive-3827
- **Confidence.** Medium (single-vendor pattern; conceptually clean but adds a process per server).
- **Caveats.** ToolHive itself is heavier than what this project needs. The conceptual takeaway — "instrument at the transport layer, not inside the server" — is what's transferable.

## Synthesis (explicit analysis)

Three patterns emerge cleanly from the source set, one is a deliberate gap, and one is the negative finding that the project's primary-to-fallback wiring will have to invent:

1. **Liveness probing is solved at the protocol level.** MCP `ping` is the canonical cross-transport health primitive, including for stdio. For a seven-server Codespace, a one-shot ping-each-server health check at `postStart` (per F1.2 / F6.2) is the lowest-overhead implementation that aligns with both the protocol and the devcontainer lifecycle. The FR-8 health-check script can be exactly this.

2. **Failure-state observability for the operator is "use what Claude Code surfaces, log what it doesn't."** Per F2.1–F2.3 and F5.1, the trio of `/mcp`, `claude mcp list`, and `--debug` covers the basics. The FR-9 structured-failure-record is the *project's* augmentation to that baseline — Claude Code does not emit a structured per-failure record by default, so the project building one is a genuine value-add, not a duplication.

3. **Redaction at the instrumentation source, keyed by env-var name, is the strongest pattern.** Per F4.2 and F4.4, the combination of "OWASP says do it" + "Claude Code's `.mcp.json` schema makes the credential names knowable in advance" + "Velida shows the OpenTelemetry pattern" converges on a recommendation: the project's runtime log redactor should consume the `env` block of `.mcp.json` as its allowlist of names-to-redact, rather than relying on regex shape-matching. This makes the augmented `auditing-mcp` rule trivially expressible (redaction-list ⊇ env-vars-list).

4. **Per-server structured JSON logs on stderr, written to `~/.claude/runtime/<server>.log` or equivalent.** Per F3.1 + F3.3 + F3.4, the convention converges; the only project-specific choice is the path and rotation policy. Rotation is operator-owned and not specified by any MCP source — `logrotate` or a date-stamped file convention both work.

5. **Primary-to-fallback transition surfacing is greenfield.** F5.4 is the load-bearing finding for AC-FR-9-d: nothing in the surveyed literature gives Design a pattern to copy. Design must choose. Option (b) — a dedicated structured event file (`mcp-events.jsonl`) emitted by an agent-side hook when the fallback fires — is the synthesis recommendation, because it (i) composes with the project's existing structured-record discipline, (ii) is auditable by the augmented `auditing-mcp` (rule: "if ADR-0018 fallback wires exist, a fallback-event-emission path must exist"), and (iii) is operator-discoverable without needing the operator to be present at the moment of transition.

## Acceptance-criteria check

The acceptance criteria for T-007 require (i) one section per sub-question with a source-backed pattern or explicit "no consensus" finding, (ii) ≥3 independent reputable sources across the whole note, and (iii) the sub-question-5 paragraph informed by ADR-0018.

| Criterion | Disposition | Reasoning |
|---|---|---|
| Sub-question 1 has a source-backed pattern | **Satisfied** | F1.1 (Anthropic spec) + F1.2 (Fast.io) + F1.3 (cross-ref) |
| Sub-question 2 has a source-backed pattern | **Satisfied** | F2.1–F2.4 all anchored to the official Claude Code MCP docs |
| Sub-question 3 has a source-backed pattern | **Satisfied** | F3.1 (Anthropic Debugging) + F3.2 (Anthropic Logging spec) + F3.3 + F3.4 |
| Sub-question 4 has a source-backed pattern | **Satisfied** | F4.1 (MCP spec) + F4.2 (Velida) + F4.3 (OWASP) + F4.4 (Claude Code schema implication) |
| Sub-question 5 has a source-backed pattern OR explicit "no consensus" | **Satisfied with explicit "no consensus"** for the primary/fallback transition (F5.4); other patterns documented in F5.1–F5.3 |
| Sub-question 6 has a source-backed pattern | **Satisfied** | F6.1–F6.3 |
| ≥3 independent reputable sources across the note | **Satisfied** | Sources span: Anthropic MCP spec (modelcontextprotocol.io); Anthropic Claude Code docs (code.claude.com); OWASP; Fast.io; MCPevals; SigNoz; Velida; Coder; Microsoft devcontainer GitHub; Stacklok/ToolHive — at least eight independent organizations |
| Sub-question 5's primary-to-fallback paragraph informed by ADR-0018 | **Satisfied** | F5.4's recommendation names ADR-0018's GitNexus / codebase-memory-mcp policy explicitly and the three Design options reference the agent (`discovery-codebase-researcher`) the ADR codifies as the fallback site |
| At least 2 trade-offs per sub-question | **Satisfied** in F1 (ping vs functional health check; protocol layer vs application readiness), F2 (HTTP/SSE auto-reconnect vs stdio operator-action; `/mcp` vs `--debug` vs structured record), F3 (stderr vs `notifications/message`; per-file vs interleaved), F4 (name-based vs regex; redact-at-source vs collector), F5 (banner vs file vs agent-level), F6 (phased vs upfront telemetry; in-process supervisor vs out-of-process proxy) |
| Specific version numbers / limits / paths quoted where the source provides them | **Satisfied** — quoted MCP spec versions (2025-03-26, 2025-06-18), Claude Code v2.1.121 retry behavior, v2.1.62 known bug, 5-attempt exponential backoff, 30-second/2–5-second ping interval, eight RFC 5424 log levels, three Coder log paths |

## Open questions

- **OQ-A.** What's the right log-path convention inside the Codespace — `.claude/runtime/<server>.log`, `/tmp/mcp-<server>.log`, or `$XDG_STATE_HOME/claude/mcp/<server>.log`? No external source dictates; this is a project choice that the `KB-mcp-platform` skill should codify once `design-codespaces` proposes a default. (Surfaces at UI-12.)
- **OQ-B.** Should the augmented `auditing-mcp` enforce "redaction-list ⊇ `.mcp.json` env-vars-list" as a BLOCKER rule (per Synthesis #3)? This is a Design choice informed by F4.4 but not externally precedented.
- **OQ-C.** For the primary-to-fallback transition (per F5.4), the project must invent — there is no external pattern to follow. This research note recommends Option (b) (structured event file) but Design owns the final choice. Forwards as a Design question to `design-cc` under UI-11 and to `design-composer` for cross-cutting consistency.
- **OQ-D.** Does Codespaces or Claude Code expose a canonical "container is attaching" event hook the project can latch the post-attach health summary to, beyond `postAttachCommand`? No source surveyed addressed this directly; may require codebase-research / experimentation.

## Source list

Primary specifications (Anthropic / official):
- Anthropic, *Model Context Protocol — Ping*, spec version 2025-03-26. https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping
- Anthropic, *Model Context Protocol — Logging (utility)*, spec version 2025-06-18. https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging
- Anthropic, *Model Context Protocol — Debugging*. https://modelcontextprotocol.io/docs/tools/debugging
- Anthropic, *Connect Claude Code to tools via MCP*. https://code.claude.com/docs/en/mcp

Industry / security:
- OWASP, *MCP01:2025 — Token Mismanagement and Secret Exposure*. https://owasp.org/www-project-mcp-top-10/2025/MCP01-2025-Token-Mismanagement-and-Secret-Exposure
- Will Velida, *Preventing MCP01 — Token Mismanagement and Secret Exposure in MCP Servers*. https://www.willvelida.com/posts/preventing-mcp01-token-mismanagement-secret-exposure

Vendor / pattern guides:
- Fast.io, *How to Implement MCP Server Health Checks (Pattern Guide)*, 2026. https://fast.io/resources/implementing-mcp-server-health-checks/
- MCPcat, *Build Health Check Endpoints for MCP Servers*. https://mcpcat.io/guides/building-health-check-endpoint-mcp-server/
- MCPevals, *MCP Logging Tutorial*, 2026. https://www.mcpevals.io/blog/mcp-logging-tutorial
- SigNoz, *MCP Observability with OpenTelemetry*. https://signoz.io/blog/mcp-observability-with-otel/
- Stacklok / DEV Community, *Bridging the Observability Gap in MCP Servers with ToolHive*. https://dev.to/stacklok/bridging-the-observability-gap-in-mcp-servers-with-toolhive-3827

Devcontainer / ecosystem:
- Microsoft, *Implement dev container health check inline with OCI spec — vscode-dev-containers issue #786*. https://github.com/microsoft/vscode-dev-containers/issues/786
- Coder, *Troubleshooting dev containers*. https://coder.com/docs/user-guides/devcontainers/troubleshooting-dev-containers

Claude Code issue corroboration (secondary, for transport-event behavior):
- *MCP server disconnects immediately — transport closes after initialization — issue #4097*. https://github.com/anthropics/claude-code/issues/4097
- *[BUG] claude mcp list command returns empty output in v2.1.62 — issue #29492*. https://github.com/anthropics/claude-code/issues/29492

Internal references (per acceptance criteria):
- ADR-0018: codebase-analysis schema + GitNexus / codebase-memory-mcp primary/fallback policy. `/workspaces/feature-pipeline/adrs/ADR-0018-codebase-analysis-schema.md`
