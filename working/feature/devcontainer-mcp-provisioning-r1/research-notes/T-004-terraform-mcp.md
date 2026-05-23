---
id: research-note-T-004
topic: HashiCorp Terraform MCP server — install/transport/tool surface/auth/version-pinning with base-image-constraint analysis
feature: devcontainer-mcp-provisioning-r1
version: 1.0.0
status: draft
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
---

# T-004 — HashiCorp Terraform MCP Server

## Topic and question

**Topic:** HashiCorp Terraform MCP server.

**Research question (verbatim from prompt):** Install / transport / tool surface / auth / version-pinning for HashiCorp Terraform MCP, with explicit base-image-constraint analysis (resolves PRD UI-2). The base image is `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` with NO Go toolchain and NO DinD.

Determine: (a) Does Terraform MCP have a pure-binary release that runs without Go installed? (b) If not, can it run via a published Docker image — and how would that work without DinD? (c) Would adding a devcontainer Feature for Docker or Go be acceptable? Trade-offs.

**KB-gap justification:** Vendor-specific install + base-image constraint (the most install-uncertain of the 8 topics).

## Executive summary

HashiCorp publishes pre-built static Go binaries for `terraform-mcp-server` on `releases.hashicorp.com` (including `terraform-mcp-server_0.5.2_linux_amd64.zip` with SHA256SUMS + GPG signature). **A pure-binary install is therefore feasible on the Python-only Bookworm base image with no Go toolchain and no DinD.** The recommended transport for a devcontainer single-user scenario is `stdio` (the upstream default). Authentication is required only for HCP Terraform / Terraform Enterprise tools (`TFE_TOKEN`, optional `TFE_ADDRESS`); the public-registry toolsets (`search_providers`, `search_modules`, `search_policies`, etc.) work anonymously. Version pinning should follow the same SHA256-verified download pattern already used for other MCP binaries in this feature, pinning to `v0.5.2` as the current stable release (released 2026-04-28). **Recommendation: pinned binary download (path "a"). Do not add a Docker-in-Docker feature or a Go toolchain Feature.**

## Findings

### F1. Pre-built linux/amd64 binary is published on releases.hashicorp.com

- **Claim.** HashiCorp publishes pre-built, signed Linux/amd64 zip binaries for each `terraform-mcp-server` release on `releases.hashicorp.com`, including SHA256SUMS and a GPG signature.
- **Source.** `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/` (HashiCorp Releases, dated per 2026-04-28 release).
- **Quote (≤15 words).** "terraform-mcp-server_0.5.2_linux_amd64.zip"
- **Confidence.** high (official primary).
- **Caveats.** Filename pattern observed for 0.5.2; assume same pattern for adjacent versions but verify if pinning to a different one.

### F2. Three documented install methods; binary path is officially listed

- **Claim.** The HashiCorp Developer deploy guide lists three install methods: Docker (the upstream "most users" recommendation), compiled binary download, and `go install` from source. The compiled binary path is configured as a stdio MCP server pointing at the local binary path.
- **Source.** `https://developer.hashicorp.com/terraform/mcp-server/deploy` (HashiCorp Developer, official deployment doc).
- **Paraphrased excerpt (no quote — second source already quoted above? No, F1 used releases page).** Quote: "Most users, consistent environments" — characterising the Docker recommendation. (≤15 words.)
- **Confidence.** high (official primary).
- **Caveats.** "Recommended" is for general users; the recommendation does not weight devcontainer/no-DinD constraints.

### F3. `go install` path requires the Go toolchain

- **Claim.** The GitHub README documents `go install github.com/hashicorp/terraform-mcp-server/cmd/terraform-mcp-server@latest` as an install option; this requires Go to be present.
- **Source.** `https://github.com/hashicorp/terraform-mcp-server` (README, main branch, official repository).
- **Quote (≤15 words).** "go install github.com/hashicorp/terraform-mcp-server/cmd/terraform-mcp-server@latest"
- **Confidence.** high (official primary).
- **Caveats.** Not relevant if F1 binary path is taken; included to confirm the alternative is real but requires adding a Go Feature.

### F4. Docker image exists but assumes a Docker daemon

- **Claim.** An official image `hashicorp/terraform-mcp-server` is published on Docker Hub, runnable in stdio mode via `docker run -i --rm hashicorp/terraform-mcp-server:0.5.2`. This requires a Docker daemon — incompatible with the "no DinD" base-image constraint.
- **Source.** `https://hub.docker.com/r/hashicorp/terraform-mcp-server` and confirmation via `https://developer.hashicorp.com/terraform/mcp-server/deploy`.
- **Quote (≤15 words).** "docker run -i --rm hashicorp/terraform-mcp-server"
- **Confidence.** high (official primary, Docker Hub registry).
- **Caveats.** Could be used with host-mounted Docker socket; that pattern is explicitly out of scope per the no-DinD constraint of this feature and introduces its own security/permission surface.

### F5. Default transport is stdio; HTTP is opt-in

- **Claim.** The server supports two transports: stdio (default) and streamable-HTTP. HTTP mode is enabled via `TRANSPORT_MODE=streamable-http` with `TRANSPORT_HOST`/`TRANSPORT_PORT`.
- **Source.** `https://developer.hashicorp.com/terraform/mcp-server/reference` (HashiCorp Developer, reference doc).
- **Quote (≤15 words).** "TRANSPORT_MODE"
- **Confidence.** high (official primary).
- **Caveats.** HTTP mode introduces a listening port and CORS/auth surface (`MCP_ALLOWED_ORIGINS`, `MCP_RATE_LIMIT_*`); unnecessary for single-user devcontainer.

### F6. Tool surface — broad, partitioned by toolset

- **Claim.** Tools are partitioned into toolsets selectable via `--toolsets`: `registry` (anonymous public registry), `registry-private` (private modules/providers, needs HCP/TFE auth), `terraform` (HCP Terraform / Enterprise workspace + run + variable + policy + stacks operations). Enumerated tools include `search_providers`, `get_provider_details`, `get_latest_provider_version`, `search_modules`, `get_module_details`, `get_latest_module_version`, `search_policies`, `get_policy_details` (registry); plus `list_terraform_orgs`, `list_workspaces`, `get_workspace_details`, `create_workspace`, `update_workspace`, `delete_workspace_safely`, `list_runs`, `get_run_details`, `create_run`, `action_run`, `get_plan_json_output`, `get_plan_details`, `get_plan_logs`, `get_apply_details`, `get_apply_logs`, `list_variable_sets`, `create_variable_set`, `attach_variable_set_to_workspaces`, `list_workspace_variables`, `list_stacks`, `get_stack_details`, `attach_policy_set_to_workspace`, etc.
- **Source.** `https://developer.hashicorp.com/terraform/mcp-server/reference` and `https://www.hashicorp.com/en/blog/terraform-mcp-server-updates-stacks-support-new-tools-and-tips` (HashiCorp blog announcing Stacks support).
- **Quote (≤15 words, blog source).** "Stacks support, new tools, and tips"
- **Confidence.** high (official primary docs + official blog).
- **Caveats.** Tool list evolves rapidly (Stacks added in 0.5.x); pin both binary and toolset list together. Some tools have destructive effects (`delete_workspace_safely`, `create_run` then `action_run`) — gate via `--toolsets registry` for read-only profile if HCP not needed.

### F7. Auth — `TFE_TOKEN` only for HCP/Enterprise paths

- **Claim.** Public Terraform Registry operations (provider docs, module discovery, Sentinel policies in the public registry) require no authentication. HCP Terraform or Terraform Enterprise operations require `TFE_TOKEN`; `TFE_ADDRESS` (default `https://app.terraform.io`) and `TFE_SKIP_TLS_VERIFY` are additional knobs.
- **Source.** `https://developer.hashicorp.com/terraform/mcp-server/deploy` and `https://developer.hashicorp.com/terraform/mcp-server/reference`.
- **Quote (≤15 words).** "Terraform Enterprise API token" (deploy doc, paraphrasing TFE_TOKEN). 15-word cap respected.
- **Confidence.** high (official primary).
- **Caveats.** If the feature wants the read-only / no-secret profile, ship with `--toolsets registry` and no `TFE_TOKEN`; this avoids any secret-handling requirement.

### F8. Version-pinning artifacts available

- **Claim.** Each release publishes signed checksums: `terraform-mcp-server_<VER>_SHA256SUMS`, `terraform-mcp-server_<VER>_SHA256SUMS.sig`, and a key-ID-suffixed signature file. Current stable is v0.5.2 (2026-04-28). Recent releases: 0.5.2 (Apr 28), 0.5.1 (Apr 7), 0.5.0 (Apr 1), 0.4.0 (Jan 22), 0.3.x line.
- **Source.** `https://github.com/hashicorp/terraform-mcp-server/releases` and `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/`.
- **Quote (≤15 words).** "terraform-mcp-server_0.5.2_SHA256SUMS"
- **Confidence.** high (official primary).
- **Caveats.** Pre-1.0; expect periodic breaking changes. Pin to exact patch and re-verify on bump.

## Synthesis (analysis — not from sources)

For a Python-only Bookworm devcontainer with no Go and no DinD, the constraint set forces a one-clear-answer:

| Path | Toolchain added | Works without DinD | Verifiable | Verdict |
|---|---|---|---|---|
| (a) Pre-built binary (F1, F2) | none | yes | SHA256 + GPG (F1, F8) | **Recommended** |
| (b) Docker image (F4) | Docker daemon | no (violates "no DinD") | image digest | rejected |
| (c) `go install` (F3) | Go toolchain (Feature) | yes | go-mod sums | not recommended; pulls a build-time toolchain into a runtime-only image |

Path (a) integrates cleanly with the existing per-binary "download + verify SHA256 + extract" pattern this feature uses for other MCP servers. Path (b) is HashiCorp's "general" recommendation but explicitly assumes a Docker daemon, which the PRD's UI-2 forbids. Path (c) would require adding `ghcr.io/devcontainers/features/go` solely to compile a single tool — net negative on image size, prebuild time, and supply-chain surface (transitive `go install` dependency resolution at install time, no checksum file).

For default config: `stdio` transport (F5), `--toolsets registry` for the anonymous read-only profile, leaving `TFE_TOKEN` unset. If the team later wants HCP Terraform tooling, the `TFE_TOKEN` flag can be added without re-provisioning the binary.

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Authoritative install command(s) with base-image impact | **satisfied** | Three documented options, base-image impact tabulated in Synthesis. |
| Transport recommendation | **satisfied** | stdio (default, F5), with rationale (single-user devcontainer; HTTP introduces port + CORS surface). |
| Tool surface enumeration | **satisfied** | F6 enumerates 30+ tools across registry/registry-private/terraform toolsets, cited to reference doc. |
| Auth mechanism | **satisfied** | F7: `TFE_TOKEN` only for HCP/Enterprise paths; public-registry tools anonymous. |
| Version-pinning recommendation | **satisfied** | F1 + F8: pin to `v0.5.2`, verify SHA256SUMS + GPG signature; same pattern as other binaries. |
| Recommendation: which install path best fits the base image | **satisfied** | Path (a) pre-built binary — see Synthesis table and Executive summary. |
| ≥3 independent reputable sources (HashiCorp official + others) | **satisfied** | 4 distinct HashiCorp official surfaces (releases.hashicorp.com, GitHub repo README, developer.hashicorp.com deploy, developer.hashicorp.com reference) + HashiCorp blog + Docker Hub. |

## Open questions

- The releases page lists 13 binary packages for 0.5.2; exact OS/arch matrix (linux_arm64, darwin_*, windows_*) was not enumerated in detail. If Codespaces ever runs on arm64, verify the `linux_arm64` artifact exists with the same filename pattern.
- Behaviour when `TFE_TOKEN` is set but the toolset filter excludes HCP tools: presumed safe (token simply unused) but not verified against source. Low-risk for the recommended config which omits the token.
- Whether 0.5.x is feature-stable enough to pin without expecting frequent bumps; release cadence in 2026 (0.5.0 Apr 1, 0.5.1 Apr 7, 0.5.2 Apr 28) suggests active iteration — expect periodic re-pin.

## Source list

1. HashiCorp — *Terraform MCP Server* (GitHub repository, README). `https://github.com/hashicorp/terraform-mcp-server` — official upstream source code and install documentation.
2. HashiCorp Developer — *Deploy the Terraform model context protocol (MCP) server*. `https://developer.hashicorp.com/terraform/mcp-server/deploy` — official deployment doc covering Docker, binary, and source paths.
3. HashiCorp Developer — *Terraform MCP server overview*. `https://developer.hashicorp.com/terraform/mcp-server` — capability overview.
4. HashiCorp Developer — *Terraform MCP server reference*. `https://developer.hashicorp.com/terraform/mcp-server/reference` — tool names, toolsets, env vars, flags.
5. HashiCorp Releases — *terraform-mcp-server 0.5.2 artifacts*. `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/` — confirmation that pre-built `linux_amd64.zip` + SHA256SUMS + GPG signature are published.
6. GitHub — *terraform-mcp-server releases*. `https://github.com/hashicorp/terraform-mcp-server/releases` — version history; current stable v0.5.2 (2026-04-28).
7. Docker Hub — *hashicorp/terraform-mcp-server*. `https://hub.docker.com/r/hashicorp/terraform-mcp-server` — confirms official image exists (path (b)).
8. HashiCorp blog — *Terraform MCP server updates: Stacks support, new tools, and tips*. `https://www.hashicorp.com/en/blog/terraform-mcp-server-updates-stacks-support-new-tools-and-tips` — confirms recent tool additions (Stacks, `attach_policy_set_to_workspaces`).
