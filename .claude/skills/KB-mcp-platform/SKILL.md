---
name: kb-mcp-platform
description: >-
  Platform knowledge for the Model Context Protocol (MCP) layer as
  provisioned in this feature-pipeline project — the five named servers
  registered at project scope in `.mcp.json`, their installation /
  invocation / health-check mechanics, the canonical event surface
  (`.claude/runtime/mcp-events.jsonl` per ADR-0037), credential indirection
  via env-block (per ADR-0039), the postCreate/postStart lifecycle wiring
  in this project's devcontainer, and the operator runbook + troubleshooting
  for routine MCP failure modes. Pairs with KB-mcp-design which adds the
  design discipline (when to add an MCP server, when to narrow vs whole-server
  allowlists, the OP-rule catalog). This KB is the PLATFORM half: facts,
  installation forms, lifecycle hooks, and lookup chains for the five
  registered servers (actionlint-mcp, context7, exa, serena, terraform-mcp).
  Historical: a seventh server (mcp-openapi-schema) was removed 2026-05-24
  per postmortem; gitnexus was removed 2026-05-27 per ADR-0066 — see body
  for the deprecation notes.
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch, Bash(python3 *)
pedagogical_sections:
  - path: references/credential-handling.md
    justification: "Documents the env-block credential indirection pattern + the OP-9 / OP-10 anti-patterns (URL-query embedded API keys; argv-passed API keys). The anti-pattern examples include placeholder credentials in URL-shaped strings the auditor flags as credential-leak training material, not live credentials."
  - path: references/operator-runbook.md
    justification: "Operator runbook for MCP failures. Contains example error outputs and example shell commands the auditor may flag (curl pipes, mcp-events.jsonl read patterns, redaction-test patterns); pedagogical reference content for postCreate / postStart troubleshooting, not executable installers."
  - path: references/troubleshooting.md
    justification: "Troubleshooting catalog for the six named servers. Contains anti-pattern examples (URL-query credential, argv-leaked API key) the auditor flags as DE-2 scanner anti-patterns; documents what to refuse, not what to execute. Also contains base64-shaped retry-token examples in API-error scenarios — pedagogical, not live tokens."
family: kb-mcp
---

# KB-mcp-platform — MCP Layer Platform Knowledge

Platform knowledge for the five named MCP servers this project provisions at project scope (`.mcp.json` at repo root). This KB is the PLATFORM half (facts, install forms, lifecycle wiring, event surface, troubleshooting). The DESIGN half (when-to-add, allowlist narrowing, OP rules) lives in **KB-mcp-design**.

> **Historical:** This KB previously documented seven servers, then six. `mcp-openapi-schema` was removed 2026-05-24 per postmortem (no spec source available; upstream npm package abandoned; `design-api` had no working spec server anyway). `gitnexus` was removed 2026-05-27 per ADR-0066 (empirical unreliability; the two dependent sub-agents fall back to Read/Grep/Glob + serena per ADR-0007's documented fallback). The removal notes are in [`.devcontainer/postCreate.sh`](../../../.devcontainer/postCreate.sh); the full postmortem evidence for `mcp-openapi-schema` is under `Issues/cross-artifact-divergence-detection-gap/evidence/mcp-postmortem-2026-05-24/`. Restore-path: if either removed server is ever re-justified, re-add to `.mcp.json` via the template in `assets/templates/mcp.json.tmpl` and re-grow this KB.

## Contents

- When this KB is loaded
- The five named servers
- `.mcp.json` structure + env-block credential indirection
- Lifecycle hooks (postCreate / postStart)
- Event surface (`.claude/runtime/mcp-events.jsonl` per ADR-0037)
- Code-graph extraction discipline (post-gitnexus-removal, ADR-0066)
- Credential handling (per ADR-0039)
- Operator runbook
- Troubleshooting

## When this KB is loaded

Load this KB when a feature, task, or troubleshooting session touches:

- `.mcp.json` at repo root (the five mcpServers entries)
- The postCreate / postStart lifecycle scripts in `.devcontainer/`
- The MCP event surface at `.claude/runtime/mcp-events.jsonl`
- Any of the five named servers' install paths, credential handling, or runtime probes
- The `auditing-mcp` skill family (this KB is the platform-facts side of its trifecta)

Pairs with **KB-mcp-design** for the design discipline (when to add a server, allowlist narrowing per agent, anti-pattern catalog).

## The five named servers

The active inventory is **five named MCP servers** (originally seven, then six; `mcp-openapi-schema` was removed 2026-05-24 per postmortem; `gitnexus` was removed 2026-05-27 per ADR-0066 — see deprecation note at the top of this file):

| Server | Transport | Install form | Auth | Pin source |
| --- | --- | --- | --- | --- |
| `actionlint-mcp` | stdio | `go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}` | none | `.devcontainer/versions.env` ACTIONLINT_MCP_SHA |
| `context7` | http (hosted) | `https://mcp.context7.com/mcp` | `CONTEXT7_API_KEY` header (canonical per Upstash README) | Codespaces secret `CONTEXT7_API_KEY` |
| `exa` | http (hosted) | `https://mcp.exa.ai/mcp` | `x-api-key` header (per T-006 F1 priority-1 header form) | Codespaces secret `EXA_API_KEY` |
| `serena` | stdio | `uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow` | none | `.devcontainer/versions.env` SERENA_VERSION (pinned strictly below v1.3.0 per ADR-0040) |
| `terraform-mcp` | stdio | binary at PATH (downloaded + GPG-verified by `.devcontainer/install/terraform-mcp.sh`) | optional `TFE_TOKEN` for cloud-tier features | `.devcontainer/versions.env` TERRAFORM_MCP_VERSION |

## `.mcp.json` structure

Canonical template at `assets/templates/mcp.json.tmpl`. Authored at repo root by Plan T2.4. Per ADR-0039 (credential redaction): env-block indirection only; **no URL-query credentials (OP-9)**, **no argv-passed credentials (OP-10)**. Per ADR-0041 (hybrid install): env-var names sourced from `.devcontainer/versions.env` or `containerEnv` (devcontainer.json).

## Lifecycle hooks

- **`onCreateCommand`** (devcontainer.json) — version probes (claude --version, python3 --version, node --version, go version, gh --version). Lightweight; runs once per container creation.
- **`postCreateCommand`** → `.devcontainer/postCreate.sh` — installs the 3 OSS-local servers (Serena via `uv tool install`; actionlint-mcp via `go install`; terraform-mcp via the dedicated install script); emits one `install_complete` JSONL record per OSS-local server. The 2 HTTP servers (context7, exa) have no install step.
- **`postStartCommand`** → `.devcontainer/postStart.sh` — emits 5 `readiness_probe` JSONL records (one per server). Tests each server's reachability via `claude mcp ping` (if available per T0.6 verify) OR direct JSON-RPC `tools/list` fallback per ADR-0041.

See `references/lifecycle-hooks.md` for the runbook detail.

## Event surface (`mcp-events.jsonl`)

Per ADR-0037, all MCP lifecycle events emit structured JSONL records to `.claude/runtime/mcp-events.jsonl`. The file is per-Codespace and never committed (per `.gitignore`). Schema: see `references/mcp-events-jsonl.md`.

Three event types (per ADR-0037):

1. `install_complete` — one per OSS-local server install (3 records per postCreate)
2. `readiness_probe` — one per registered server (5 records per postStart)
3. `structured_failure` — emitted on any MCP error condition (auth-fail, timeout, redacted-credential-leak, etc.)

## Code-graph extraction discipline (post-gitnexus removal)

Per ADR-0066 (2026-05-27), gitnexus was removed from the active server set. ADR-0007's documented fallback applies: the two dependent sub-agents (`discovery-codebase-researcher`, `review-architecture-auditor`) fall back to Read+Grep+Glob plus serena's symbol-level tools (`find_symbol`, `find_referencing_symbols`, `get_symbols_overview`) for the code-graph traversal patterns previously served by gitnexus. The `primary_degraded → falling back to <fallback>` event-surface schema field is preserved in `references/mcp-events-jsonl.md` for future code-graph servers that may be registered.

## Credential handling

Per ADR-0039 (redact-at-source posture):

- All credentials enter via env-block indirection (env-var name → Codespaces secret).
- No URL-query credentials (OP-9 BLOCKER if violated).
- No argv-passed credentials (OP-10 BLOCKER if violated).
- Header-based auth: `CONTEXT7_API_KEY` (canonical per Upstash README — NOT `Authorization: Bearer`) for context7; `x-api-key` for exa.

See `references/credential-handling.md` for the full discipline + OP-rule cross-references.

## Sub-skill family

This KB is part of the **MCP trifecta**:

- `KB-mcp-platform` (this skill) — platform facts
- `KB-mcp-design` — design discipline
- `auditing-mcp` — audit ruleset (OP-1..OP-10), graduated to its own family per ADR-0042

The trifecta mirrors the established convention used by `KB-github-actions-{platform,design}` + `auditing-github-actions` and `KB-codespaces-{platform,design}` + `auditing-codespaces`.

## References quick-lookup

| When you need | Read |
| --- | --- |
| The five-server inventory + per-server install/auth | `references/seven-named-servers.md` (filename retained for stability — content updated to reflect five active servers) |
| postCreate / postStart lifecycle runbook | `references/lifecycle-hooks.md` |
| Credential discipline + OP-9/OP-10 anti-patterns | `references/credential-handling.md` |
| `mcp-events.jsonl` schema + event types | `references/mcp-events-jsonl.md` |
| Operator runbook (routine actions, recovery) | `references/operator-runbook.md` |
| Troubleshooting catalog (failure → diagnosis → fix) | `references/troubleshooting.md` |
| `.mcp.json` template the canonical five entries use | `assets/templates/mcp.json.tmpl` |
