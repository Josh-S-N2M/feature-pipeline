# Seven Named MCP Servers — Inventory + Per-Server Detail

Canonical inventory per Gate-4 OI-1 closure (devcontainer-mcp-provisioning-r1). No `codebase-memory-mcp` entry per OI-1; the fallback policy remains at the project level for any future feature that registers it.

## Inventory table

| Server | Transport | Install | Auth | Tools |
|---|---|---|---|---|
| actionlint-mcp | stdio | `go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}` | none | `lint_workflow`, `check_all_workflows` |
| context7 | http | `https://mcp.context7.com/mcp` | `CONTEXT7_API_KEY` header | `resolve-library-id`, `query-docs` |
| exa | http | `https://mcp.exa.ai/mcp` | `x-api-key` header | `web_search_exa`, `company_research_exa`, `crawling_exa` (+ others) |
| gitnexus | stdio | `npx -y gitnexus@${GITNEXUS_TAG} mcp` (env `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`) | none | code-graph (resolve, search, callers, etc.) |
| mcp-openapi-schema | stdio | `npx -y mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}` | none | OpenAPI schema traversal |
| serena | stdio | `uvx --from git+https://github.com/oraios/serena@${SERENA_REF} serena` | none | symbol-level Python audit (read/find/refs) |
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

### gitnexus

- **Upstream**: `gitnexus` (npm package; the GitHub repo is `abhigyanpatwari/GitNexus`, but the npm package is the install target).
- **Pin**: `GITNEXUS_TAG=1.6.5` (latest stable on npm at execution slot 2026-05-23).
- **Install (cycle-3-corrected)**: `npm install -g gitnexus@${GITNEXUS_TAG}` (persistent) OR `npx -y gitnexus@${GITNEXUS_TAG} mcp` (one-shot). NOT `uvx` — that was a category error in pre-cycle-3 design; gitnexus is npm-only.
- **Env-var**: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` — skips optional tree-sitter grammars at install time on architectures without prebuilds. On x86_64-linux Codespaces (canonical target), tree-sitter packages ship `prebuilds/linux-x64/*.node` so no C++ compilation runs; AC-CS-9 wrapping intent ("no C++ toolchain at cold-cache") holds.
- **Tools**: code-graph (resolve symbol, search, find callers, file structure, etc. — whole-server allowlist).
- **Consumer**: `discovery-codebase-researcher` agent (primary) + `review-architecture-auditor` agent.

### mcp-openapi-schema

- **Upstream**: `mcp-openapi-schema` on npm.
- **Pin**: `MCP_OPENAPI_SCHEMA_VERSION=0.0.1` (single release on npm at 2025-03-13; `STALE_PACKAGE` annotation per Plan §H-3).
- **Install**: `npx -y mcp-openapi-schema@0.0.1`.
- **Tools**: OpenAPI schema traversal.
- **Consumer**: `design-api` agent (whole-server allowlist).

### serena

- **Upstream**: `oraios/serena` on GitHub (Python; installed via `uvx`).
- **Pin**: `SERENA_REF=v1.2.0` — latest tag strictly below v1.3.0 per ADR-0040 (pinned pre-v1.3.0 pending `base_modes`→`added_modes` migration review).
- **Install**: `uvx --from git+https://github.com/oraios/serena@${SERENA_REF} serena`.
- **Tools**: symbol-level Python audit operations (read/find/refs/etc. — whole-server allowlist on the **narrowed 5-agent set** per ADR-0040).
- **5-agent narrowed allowlist** (per ADR-0040): `review-architecture-auditor`, `design-claude-code` (frontmatter `name: design-cc`), `design-cicd`, `design-codespaces`, `discovery-codebase-researcher`. Other 31 agents do NOT carry `mcp__serena__*`.
- **Kill criterion**: design-time documentation only per Issues/register §O (no calendar machinery). Event trigger for re-eval: when `auditing-codespaces` stub-fill is undertaken (OI-6).

### terraform-mcp

- **Upstream**: `hashicorp/terraform-mcp-server` (HashiCorp official).
- **Pin**: `TERRAFORM_MCP_VERSION=0.5.2` (latest stable as of 2026-04-28). Release tarball SHA-256 + GPG signature verified at install time per `.devcontainer/install/terraform-mcp.sh`.
- **Install**: binary download + sha256sum -c + gpg --verify (HashiCorp signing key fingerprint `C874011F0AB405110D02105534365D9472D7468F`).
- **Auth**: optional `TFE_TOKEN` for Terraform Cloud features; local-only usage is no-auth.
- **Tools**: Terraform-reasoning tool set (whole-server allowlist).
- **Consumer**: `design-iac` agent.

## Cross-references

- **ADR-0007 v2.2.0** — code-graph MCP selection policy (GitNexus primary, codebase-memory-mcp fallback documented at project level).
- **ADR-0037** — `.claude/runtime/mcp-events.jsonl` event surface.
- **ADR-0039** — credential-redaction posture (env-block indirection; OP-9 URL-query REJECTED; OP-10 argv REJECTED).
- **ADR-0040** — Serena narrowed always-on (5-agent allowlist).
- **ADR-0041** — install-mechanism hybrid (per-server install taxonomy).
- **Plan T2.4** — `.mcp.json` authoring task (consumes this inventory).
