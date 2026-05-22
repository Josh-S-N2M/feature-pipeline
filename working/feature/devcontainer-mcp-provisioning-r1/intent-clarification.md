---
id: IC-devcontainer-mcp-provisioning-r1
version: 1.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
scope_class: FULL
user_token: <pending — assigned at Intent Confirmation Gate>
generated: 2026-05-22T20:45:00Z
generated_by: intake-intent-clarifier
---

# Intent Clarification: Devcontainer MCP Server Provisioning

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

The first artifact in the feature-pipeline. It captures the user's intent before any
PRD or design work begins. It is NOT a requirements document, NOT a design document —
it is a structured record of what the user wants, with ambiguities surfaced and
resolved. It gates progression to PRD Authoring via the Intent Confirmation Gate.

## Source

> "Review each one of these MCPs and create an intent document on how to ensure they
> are installed and ready to be used within this devcontainer to be used within our
> feature pipeline" — six servers named: Serena, `hannesj/mcp-openapi-schema`,
> `hongkongkiwi/actionlint-mcp`, HashiCorp Terraform MCP, Context7, and Exa.

## Initial Interpretation

The request was first read as a one-off infrastructure task: produce a standalone
install/spec document with concrete `Dockerfile` edits and a `.mcp.json` next to the
devcontainer config. That interpretation baked in two assumptions the user corrected:
(1) that the artifact lived in `.devcontainer/`, and (2) that the intent document
should itself carry install design decisions. Both were wrong — this is a feature for
the pipeline, and the pipeline dictates where its artifacts live and what each stage
may decide.

## Clarifying Questions and Answers

| # | Ambiguity | Question Asked | User Answer | Resolved? |
|---|---|---|---|---|
| 1 | Where does the intent document belong? | Should this go in `.devcontainer/`? | No — review the feature pipeline; it dictates the location. Pipeline convention: `working/feature/<slug>/intent-clarification.md` (Stage 1 artifact). | [x] |
| 2 | How much pipeline rigor should this run carry? | MINOR shortened discipline / FULL 13 stages / intent-doc only? | FULL — all 13 stages. | [x] |
| 3 | Does "ready to be used" include changing the agent surface? | Wire MCP tools into sub-agents, or install + register only? | Wire the MCP tools into the relevant sub-agents. | [x] |
| 4 | Always-on vs. layer-conditional activation? | All six always-on, or tiered activation? | All six always-on. | [x] |
| 5 | How are server credentials handled? | Codespaces secrets with keys available, or keys TBD? | Codespaces secrets — keys are available. | [x] |

## Clarified Intent

Provision six MCP servers — Serena, `mcp-openapi-schema`, `actionlint-mcp`, HashiCorp
Terraform MCP, Context7, and Exa — into this project's devcontainer so they are
installed, registered, and usable by the feature-pipeline's sub-agents. The work runs
as a FULL 13-stage pipeline feature. "Ready to be used" explicitly includes wiring the
MCP tools into the relevant sub-agents' `tools:` allowlists, not just installing the
servers. All six servers are registered always-on (project-scoped `.mcp.json`, loaded
every session). Credentials are supplied via GitHub Codespaces secrets; the required
keys (notably `EXA_API_KEY`) are available, so every server must be verified working
at acceptance — not merely registered.

## Scope Posture

### What's in scope

- Devcontainer changes (`.devcontainer/Dockerfile` and/or `devcontainer.json`) so all
  six servers' runtimes and binaries are present in a freshly built container.
- A project-scoped `.mcp.json` registering all six servers always-on.
- Updating the relevant `.claude/agents/*.md` `tools:` allowlists so the consuming
  sub-agents (discovery and per-layer design agents) can invoke the new MCP tools.
- A secrets path via Codespaces secrets for `EXA_API_KEY`, `CONTEXT7_API_KEY`, and
  `TFE_TOKEN`, with no secret values committed to git.
- Verification that each registered server connects and responds.

### What's NOT in scope (explicitly excluded)

- Any MCP server beyond the six named.
- The Claude-hosted MCP servers already available on other Claude surfaces — those are
  a separate surface and are not removed, replaced, or depended upon here.
- Changes to pipeline stages, the six human gates, or the orchestrator topology.
- Authoring feature work that *consumes* these MCPs — this run provisions capability;
  it does not exercise it.
- The external codebases the pipeline is later run against.

### What's undecided (deferred to PRD or later)

- Transport per server (remote HTTP vs. local stdio) — notably for Context7 and Exa.
- Install mechanism — image-build (Dockerfile-baked) vs. lifecycle hooks; and the
  Terraform MCP install path (Go toolchain vs. Docker), given the container currently
  has neither a Go toolchain nor Docker-in-Docker.
- Whether Serena should additionally fill the `KB-codebase-research` codebase-traversal
  MCP slot (the "GitNexus / codebase-memory-mcp" role).
- The precise mapping of which MCP tools are added to which sub-agents' allowlists.
- Version-pinning policy for the servers and their runtimes.

## Stakeholder Posture (Preliminary)

- **Pipeline operator / maintainer:** wants the servers reliably present so runs never
  fail on a missing tool, and container startup stays fast and reproducible.
- **Consuming sub-agents** (discovery-codebase-researcher; design-iac / design-api /
  design-cicd; discovery-external-researcher): the actual tool users.
- **Devcontainer / Codespaces users:** want a deterministic, low-friction rebuild.
- **Security reviewer:** wants credentials kept out of git and no toxic MCP capability
  combinations introduced.

## Success Posture (Preliminary)

The feature is "done" when a freshly built devcontainer has all six servers installed,
`claude mcp list` shows each as connected, and each answers a trivial probe call. The
relevant sub-agents carry the new MCP tools in their `tools:` allowlists. No secret
values appear in any committed file, and Exa authenticates successfully with its
Codespaces-supplied key. The `auditing-mcp` skill run against the new `.mcp.json`
returns no BLOCKER findings.

## Confirmation

Before the orchestrator proceeds to PRD Authoring, the user confirms this document.
The confirmation token is recorded in frontmatter (`user_token`) and captured by the
orchestrator's AskUserQuestion at the Intent Confirmation Gate.

## Open Items (Pending PRD Authoring)

- Resolve the five "undecided" items above (transport, install mechanism, Serena's
  codebase-MCP role, tool-to-agent mapping, version pinning).
- Confirm the Exa hosted-server authentication mechanism (request header vs. URL query
  parameter) before `.mcp.json` is finalized.
- Assess the context-budget impact of six always-on servers across ~30 sub-agents;
  the PRD should state whether this is acceptable or warrants a mitigation.
- Note the Serena fit caveat: this repo is markdown-heavy, so Serena's symbol-level
  value is realized mainly when the pipeline runs against real feature codebases.
- Decide whether `auditing-mcp` (no-BLOCKER) becomes a formal acceptance criterion.
