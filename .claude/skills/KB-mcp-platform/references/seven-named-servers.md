# Named MCP Servers — Inventory + Per-Server Detail

Canonical inventory: **five active servers** (originally seven; `mcp-openapi-schema` was removed 2026-05-24 per postmortem; `gitnexus` was removed 2026-05-27 per ADR-0066 — see deprecation notes below). The code-graph fallback policy (Read+Grep+Glob + serena) applies in lieu of any registered code-graph server.

> **Filename note:** This file is named `seven-named-servers.md` for historical-link stability (the original inventory was seven; renaming would cascade through frozen phase-validator references in `working/feature/devcontainer-mcp-provisioning-r1/`). Content is now five servers.

## Inventory table

| Server | Transport | Install | Auth | Tools |
|---|---|---|---|---|
| actionlint-mcp | stdio | `go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}` | none | `lint_workflow`, `check_all_workflows` |
| context7 | http | `https://mcp.context7.com/mcp` | `CONTEXT7_API_KEY` header | `resolve-library-id`, `query-docs` |
| exa | http | `https://mcp.exa.ai/mcp` | `x-api-key` header | `web_search_exa`, `company_research_exa`, `crawling_exa` (+ others) |
| serena | stdio | `uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow` | none | symbol-level Python audit (read/find/refs) |
| terraform-mcp | stdio | binary on PATH (GPG-verified per ADR-0041) | optional `TFE_TOKEN` | Terraform-reasoning tools |

## Per-server detail

### actionlint-mcp

- **Upstream**: `github.com/hongkongkiwi/actionlint-mcp` (PRD-normative per cycle-3 reconciliation F1 — corrected from a propagation-drift `2manymws/actionlint-mcp` that returned HTTP 404).
- **Pin**: HEAD-of-main SHA per `.devcontainer/versions.env` `ACTIONLINT_MCP_SHA`. Cycle-3 default: `7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef` (2025-08-11).
- **Install**: `go install github.com/hongkongkiwi/actionlint-mcp@<SHA>` (NOT `/cmd/actionlint-mcp` subpath — main.go is at repo root).
- **Tools**: `lint_workflow`, `check_all_workflows` (two tools).
- **Allowlist convention**: narrow per-tool (`mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows`) — whole-server adds no value with only two tools.
- **Consumer**: `design-cicd` agent (per blueprint Sub-Agents row).

### context7

- **Upstream**: `@upstash/context7-mcp` (npm) + hosted endpoint `https://mcp.context7.com/mcp`.
- **Version**: v3.0.0 at execution slot 2026-05-23 (npm `dist-tags.latest`; verified via WebFetch + Bash curl in cycle-3 D-3.2-completion). Stable two-tool surface across v1→v3 per Upstash CHANGELOG.
- **Tools**: `resolve-library-id`, `query-docs` (NOT `get-library-docs` — cycle-3 D-3.2-completion correction per WebFetch verification).
- **Auth**: canonical `CONTEXT7_API_KEY: <value>` header (per Upstash README quote: *"pass your API key via the `CONTEXT7_API_KEY` header"*). **NOT** `Authorization: Bearer ${CONTEXT7_API_KEY}` — that was a non-canonical framing in design pre-cycle-3, retired per SF-F3-AUTH-HEADER-1 resolution.
- **Stateful in v3.0.0**: Upstash backs Context7 v3.0.0 with Redis for session management (CHANGELOG v3.0.0 major change). No design impact for this feature — we use the hosted endpoint where Redis is Upstash's concern.
- **Consumer**: `discovery-external-researcher` agent.

### exa

- **Upstream**: `exa-labs/exa-mcp-server` + hosted endpoint `https://mcp.exa.ai/mcp`.
- **Auth resolver priority** (per T-006 F1): (1) `exaApiKey` URL-query parameter, (2) `Authorization: Bearer …` header, (3) `EXA_API_KEY` env var (for stdio/npx mode). `x-api-key` header is documented for the hosted endpoint.
- **Our design choice**: `x-api-key` header (URL-query REJECTED per OP-9). Fallback path if `x-api-key` rejected: switch to `Authorization: Bearer ${EXA_API_KEY}` per T-006 priority-2.
- **Tools**: `web_search_exa`, `company_research_exa`, `crawling_exa` (+ others — design narrows to a 5-tool allowlist).
- **Consumer**: `discovery-external-researcher` agent.

### gitnexus (REMOVED 2026-05-27)

- **Status**: Removed per ADR-0066 — empirical unreliability in practice. The original selection in ADR-0007 was a theoretical-fit decision; in-practice failure modes (hooks conflict with long-lived MCP server, calibration churn for optional grammars, post-install warm cost, brittle index staleness behavior) made the server "broken and unusable" per user assessment.
- **Replacement**: The two dependent sub-agents (`discovery-codebase-researcher`, `review-architecture-auditor`) fall back to Read+Grep+Glob plus serena's symbol-level MCP tools (`find_symbol`, `find_referencing_symbols`, `get_symbols_overview`) per ADR-0007's documented fallback. The `extraction_method` field on `codebase-analysis.json` now takes values `serena | grep-only | mixed`.
- **Removal note**: ADR-0066-gitnexus-removal.md (Accepted 2026-05-27); supersedes the gitnexus selection in ADR-0007 v2.2.0.
- **Historical pin**: `GITNEXUS_TAG=1.6.5` (recorded here for postmortem-trail completeness; the env var is no longer in `.devcontainer/versions.env`).

### mcp-openapi-schema (REMOVED 2026-05-24)

- **Status**: Removed per postmortem 2026-05-24 — no spec source available; upstream npm package abandoned (single release `0.0.1` at 2025-03-13); `design-api` agent had no working spec server anyway.
- **Removal note**: `.devcontainer/postCreate.sh` line 16; full postmortem evidence under `Issues/cross-artifact-divergence-detection-gap/evidence/mcp-postmortem-2026-05-24/`.
- **Restore path**: if a working spec server is ever found, re-register in `.mcp.json` via `assets/templates/mcp.json.tmpl` (the template no longer includes the entry — re-add it) and re-populate this section with the new server's upstream + pin + install + tools + consumer.
- **Historical pin**: `MCP_OPENAPI_SCHEMA_VERSION=0.0.1` (recorded here for postmortem-trail completeness; the env var is no longer in `.devcontainer/versions.env`).

### serena

- **Upstream**: `oraios/serena` on GitHub (Python; PyPI package `serena-agent`, binary `serena`).
- **Pin**: `SERENA_VERSION=1.2.0` — latest tag strictly below v1.3.0 per ADR-0040 (pinned pre-v1.3.0 pending `base_modes`→`added_modes` migration review).
- **Install**: `uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow` (canonical upstream method per MCP-provisioning-postmortem 2026-05-24).
- **Tools**: symbol-level audit operations (read/find/refs/etc. — whole-server allowlist on the **narrowed 5-agent set** per ADR-0040).
- **5-agent narrowed allowlist** (per ADR-0040): `review-architecture-auditor`, `design-claude-code` (frontmatter `name: design-cc`), `design-cicd`, `design-codespaces`, `discovery-codebase-researcher`. Other 31 agents do NOT carry `mcp__serena__*`.
- **Post-gitnexus role (ADR-0066)**: serena is now the sole symbol-level MCP server. The two sub-agents previously also wired to gitnexus (`discovery-codebase-researcher`, `review-architecture-auditor`) retain their serena allowlist and use Read/Grep/Glob to cover what gitnexus's code-graph traversal previously served.
- **Kill criterion**: design-time documentation only per Issues/register §O (no calendar machinery). Event trigger for re-eval: when `auditing-codespaces` stub-fill is undertaken (OI-6).

### terraform-mcp

- **Upstream**: `hashicorp/terraform-mcp-server` (HashiCorp official).
- **Pin**: `TERRAFORM_MCP_VERSION=0.5.2` (latest stable as of 2026-04-28). Release tarball SHA-256 + GPG signature verified at install time per `.devcontainer/install/terraform-mcp.sh`.
- **Install**: binary download + sha256sum -c + gpg --verify (HashiCorp signing key fingerprint `C874011F0AB405110D02105534365D9472D7468F`).
- **Auth**: optional `TFE_TOKEN` for Terraform Cloud features; local-only usage is no-auth.
- **Tools**: Terraform-reasoning tool set (whole-server allowlist).
- **Consumer**: `design-iac` agent.

## Cross-references

- **ADR-0007 v2.2.0** — code-graph MCP selection policy (superseded for selection by ADR-0066; the documented fallback to Read/Grep/Glob + serena remains the canonical post-removal posture).
- **ADR-0066** — gitnexus removal (2026-05-27).
- **ADR-0037** — `.claude/runtime/mcp-events.jsonl` event surface.
- **ADR-0039** — credential-redaction posture (env-block indirection; OP-9 URL-query REJECTED; OP-10 argv REJECTED).
- **ADR-0040** — Serena narrowed always-on (5-agent allowlist).
- **ADR-0041** — install-mechanism hybrid (per-server install taxonomy).
- **Plan T2.4** — `.mcp.json` authoring task (consumes this inventory).
