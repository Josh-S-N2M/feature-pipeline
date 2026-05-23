---
id: RP-devcontainer-mcp-provisioning-r1
doc_type: research-plan
version: 1.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v1.md
generated: 2026-05-23T00:00:00Z
generated_by: discovery-plan-author
---

# Research Plan: Devcontainer MCP Server Provisioning

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The Research Plan Approval Gate scans top-down; lead with Information needs, then proposed research, then explicit exclusions.

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug**: `devcontainer-mcp-provisioning-r1`
- **PRD path**: `working/feature/devcontainer-mcp-provisioning-r1/prd-v1.md`
- **PRD version**: 1.0.0
- **PRD gate state**: approved at 2026-05-23 (PRD Approval Gate; `intent_user_token: gate1-approved-2026-05-23`)
- **Scope class**: FULL (13-stage pipeline pass)
- **Activated layers (from PRD Layer Scope)**: Claude Code / Project Filesystem; Dev Environment (Codespaces / Devcontainer)
- **Inherited ADRs in scope**:
  - **ADR-0021** (Discovery phase architecture — this Plan honors KB-and-ADR-first + the ≤6 external-topic cap + the 1 × codebase + N × external fan-out)
  - **ADR-0018** (codebase-analysis.json schema v1.1.0 — produced by `discovery-codebase-researcher`)
  - **ADR-0020** (KB structure — the KBs cited below are organized per this ADR)
  - **ADR-0009** (rationale brief 3-layer — the Plan is honored downstream as part of the rationale brief)
- **Applicable KBs** (for the activated layers + cross-cutting concerns):
  - `KB-cc-platform` (Claude Code primitives, `.mcp.json`, transports, scopes, `tools:` allowlist syntax)
  - `KB-cc-design` (which primitive to choose; context-cost discipline; sub-agent `tools:` restriction patterns)
  - `KB-codespaces-platform` (devcontainer.json schema, lifecycle hooks, Features, prebuild semantics)
  - `KB-codespaces-design` (image vs Dockerfile vs docker-compose; lifecycle-hook placement; secrets via Codespaces secrets)
  - `KB-codebase-research` (the codebase-analysis discipline applied by `discovery-codebase-researcher`)
  - `KB-documentation-criteria` (Research Plan template + Discovery Planning discipline)
  - `auditing-mcp` (the project skill that audits `.mcp.json` for toxic capability combinations — informs Acceptance, not a research target)
  - `KB-review-disciplines` (Gate 0/1 — the criteria this Plan will be reviewed against, indirectly)

## Information needs inventory

Each row maps a downstream-consumer information need to a disposition. Per ADR-0021, the disposition is the visible result of KB-and-ADR-first triage.

### Synthesis + per-layer Design needs (driven by PRD Undetermined Items)

- **IN-001** — *What `.mcp.json` registration shape (transport, command, env-var references) does Claude Code expect for project-scoped, always-on servers, and what is the syntax of the `tools:` allowlist field consumed by sub-agents?*
  - Downstream consumer(s): `design-cc` (Claude Code Designer; produces `.mcp.json` design + the agent allowlist edits); `design-composer` (integrates).
  - **Disposition**: `covered-by-KB:KB-cc-platform:references/integrations.md` + `covered-by-KB:KB-cc-platform:assets/templates/mcp-config.json.example`.

- **IN-002** — *Among Claude Code's seven extension primitives, which one(s) should the provisioning use (here: MCP servers; possibly hooks for runtime probes; subagent `tools:` for allowlist scoping)?*
  - Downstream consumer(s): `design-cc`.
  - **Disposition**: `covered-by-KB:KB-cc-design:references/patterns-and-anti-patterns.md` (decision matrix forces "MCP server" for "connect Claude to an external service" and "subagent `tools:` for per-agent allowlist scoping").

- **IN-003** — *What's the right Dev Container install mechanism for a binary/runtime that's not part of the base image — `features` vs Dockerfile RUN vs lifecycle hook — and what does each cost in rebuild time, prebuild cacheability, and credential surface?*
  - Downstream consumer(s): `design-codespaces` (Devcontainer Designer; resolves UI-2 install mechanism question for 5 of the 6 servers).
  - **Disposition**: `covered-by-KB:KB-codespaces-design:references/patterns-and-anti-patterns.md` (the "Features vs Dockerfile vs lifecycle" pattern + lifecycle-hook placement table) + `covered-by-KB:KB-codespaces-platform:references/devcontainer.md` (schema/lifecycle facts).

- **IN-004** — *How do Codespaces secrets surface as environment variables inside the container, and how are they referenced from `.mcp.json` without committing values?*
  - Downstream consumer(s): `design-codespaces`, `design-cc`.
  - **Disposition**: `covered-by-KB:KB-codespaces-platform:references/secrets-and-env.md` + `covered-by-KB:KB-cc-platform:assets/templates/mcp-config.json.example` (which demonstrates the `${VAR_NAME}` substitution pattern).

- **IN-005** — *What's the canonical version-pinning posture for tools installed in a devcontainer (pin exact / pin major / float), and how is it expressed in `features` blocks vs Dockerfile?*
  - Downstream consumer(s): `design-codespaces` (resolves the general half of UI-5).
  - **Disposition**: `designer-general-knowledge` — community-standard devcontainer hygiene (pin tool versions for determinism; express in Feature `version:` field or Dockerfile `ARG`/`apt-get install <pkg>=<version>` / `npm i <pkg>@<ver>`). KB-codespaces-design touches "right hook for right cost" but doesn't pin-policy explicitly. The designer must document the chosen pin policy with rationale in `codespaces-design.md`. **Per-server recommended version numbers** are NOT general knowledge — those are bundled into each server's external-research topic (T-001..T-006).

- **IN-006** — *What does the `auditing-mcp` skill check for, and what `.mcp.json` shapes does it flag as BLOCKER?*
  - Downstream consumer(s): `design-cc` (produces an `.mcp.json` that won't BLOCKER); `design-composer` (integrates UI-6 decision); `plan-author` (if `auditing-mcp` becomes a formal gate per UI-6, the Plan needs a phase validator).
  - **Disposition**: `codebase-topic` — the skill is local to the repo (`.claude/skills/auditing-mcp/`) and its rubric is fully discoverable by reading its `SKILL.md` and `references/*.md`. Not external research.

- **IN-007** — *What sub-agents exist today, what do each consume / produce, and which would naturally be the call sites for each of the six MCPs?*
  - Downstream consumer(s): `design-cc` (resolves UI-1 tool-to-agent mapping); `design-composer`.
  - **Disposition**: `codebase-topic` — the answer lives in `.claude/agents/*.md`. The Codebase Researcher inventories sub-agents and their current `tools:` allowlists; the per-layer Designer then maps. Cannot be answered without reading the repo.

- **IN-008** — *What is the actual current context-window cost of the existing baseline (no new MCP servers loaded), and what published per-server token characteristics does Claude Code surface (e.g., via `/context`)?*
  - Downstream consumer(s): `design-cc` (resolves UI-7 context-budget overhead).
  - **Disposition**: `codebase-topic` — measurement must happen against this repo's actual sub-agents. (External per-server token estimates are bundled into each server's external-research topic when published by upstream; absent that, the measurement is a codebase-discovery activity using `/context` against the built container at Design time.)

- **IN-009** — *Is this repo markdown-heavy enough that Serena's symbol-level traversal is wasted, and what existing codebase-traversal MCP role (GitNexus / codebase-memory-mcp per ADR-0007) does the project already specify?*
  - Downstream consumer(s): `design-cc` (resolves UI-8 Serena fit).
  - **Disposition**: `codebase-topic` — both parts (file-type composition, existing MCP role in agent definitions) live in the repo. The codebase researcher records file-type composition + ADR-0007 inheritance + which agents already declare GitNexus/codebase-memory-mcp.

- **IN-010** — *Whether `auditing-mcp` (no-BLOCKER) becomes a formal Gate 6 acceptance criterion vs. a strongly recommended check (UI-6).*
  - Downstream consumer(s): `plan-author` (chooses phase-validator strictness).
  - **Disposition**: **Open question for human resolution** — this is not a research question. The PRD encodes the "no BLOCKER" outcome under NFR-3 / AC-NFR-2-c; the gating question is a human / pipeline-operator decision. See Open Questions section.

### Per-MCP-server research needs (PRD UI-1, UI-2, UI-3, UI-4, UI-5; per-server slice)

For each of the six named servers, the Designer needs the same five facts: (i) install mechanism (binary/npm/Go/Docker/etc.), (ii) transport (stdio vs HTTP vs SSE), (iii) authentication shape (env var vs header vs query param), (iv) the set of tool names the server exposes (so the allowlist can name them), (v) a published version to pin to (with rationale). KB-cc-platform documents the *generic shape* of these fields in `.mcp.json`; it does NOT document any specific upstream server's choices. KB-codespaces-design documents the *general* install-mechanism trade-off; it does NOT document a specific package's install path. These are genuine KB gaps for each named server.

- **IN-011** — *Serena: install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-001`.
- **IN-012** — *mcp-openapi-schema (`hannesj/mcp-openapi-schema`): install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-002`.
- **IN-013** — *actionlint-mcp (`hongkongkiwi/actionlint-mcp`): install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-003`.
- **IN-014** — *HashiCorp Terraform MCP: install/transport/auth/tools/version-pin — with explicit attention to base-image constraints (no Go toolchain, no DinD).* (Resolves UI-2 Terraform path.) — **Disposition**: `external-research-topic:T-004`.
- **IN-015** — *Context7: install/transport (remote HTTP vs local stdio)/auth/tools/version-pin.* (Resolves UI-4.) — **Disposition**: `external-research-topic:T-005`.
- **IN-016** — *Exa: install/transport (remote HTTP vs local stdio)/auth (header vs query param)/tools/version-pin.* (Resolves UI-3.) — **Disposition**: `external-research-topic:T-006`.

## Codebase research scope

Single invocation of `discovery-codebase-researcher` (per ADR-0021). Output: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json` (schema v1.1.0 per ADR-0018) + sibling markdown report.

### Touch points

- `.devcontainer/Dockerfile` — base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`), current `apt-get` install layer, Yarn-list workaround. This is the surface the provisioning extends or replaces.
- `.devcontainer/devcontainer.json` — current `features` (Claude Code, Node LTS, GitHub CLI, common-utils), `onCreateCommand`, `containerEnv`, `hostRequirements`, `customizations`. The MCP install/registration lifecycle either lives here, is added as a new Feature, or is added in a lifecycle hook.
- `.mcp.json` — **confirmed absent** at the repo root as of plan-author's check (`Glob /workspaces/feature-pipeline/.mcp.json` returned no matches). This is the file the feature *creates*; the researcher confirms it does not exist and that no MCP registration is currently committed.
- `.claude/agents/*.md` — every sub-agent file. The researcher inventories which agents exist, what their current `tools:` allowlists are, and which are likely call sites for each of the six MCPs (per the PRD's Technical Considerations / Dependencies preliminary read). Of particular interest:
  - `discovery-codebase-researcher.md` (likely Serena consumer)
  - `discovery-external-researcher.md` (likely Context7 + Exa consumer)
  - `design-api.md` (likely mcp-openapi-schema consumer)
  - `design-cicd.md` (likely actionlint-mcp consumer)
  - `design-iac.md` (likely HashiCorp Terraform MCP consumer)
  - `design-codespaces.md`, `design-claude-code.md` (likely producers of this feature's design, not consumers)
- `.claude/skills/auditing-mcp/SKILL.md` + `references/*.md` — the rubric the resulting `.mcp.json` must satisfy at Gate 6 (AC-NFR-2-c). The researcher records the BLOCKER criteria so the design can pre-empt them.
- `adrs/ADR-0007*.md` (and any related ADR) — establishes GitNexus primary / codebase-memory-mcp fallback for codebase traversal. Confirms Serena's role is *additional* to (not a replacement for) the existing codebase-MCP role; informs UI-8.

### Blast-radius questions

Per ADR-0018, capture the following in `codebase-analysis.json`'s `blast_radius` section:

1. **`.mcp.json` (new file)**:
   - Who reads it? Every Claude Code session in this repo (loaded by `ghcr.io/anthropics/devcontainer-features/claude-code:1`).
   - 1-hop dependents: every `.claude/agents/*.md` whose `tools:` allowlist names an MCP tool registered there.
   - 3-hop dependents: every pipeline stage that fans out to those sub-agents (effectively the whole pipeline).
   - Test files: none today (CI smoke is FR-7-deferred — won't have); acceptance is `claude mcp list` + per-server probe (FR-1, FR-4).
2. **Each `.claude/agents/*.md` whose `tools:` allowlist is edited**:
   - 1-hop dependents: orchestrator stages that invoke that sub-agent.
   - Convention impact: agent-file frontmatter shape must conform to the project's existing pattern (the researcher records the canonical shape by reading several existing agent files).
3. **`.devcontainer/Dockerfile` and `devcontainer.json`**:
   - 1-hop dependent: the Codespaces build pipeline (GitHub-side, not in-repo).
   - Convention impact: the `vscode` `customizations` block, `containerEnv` block, `hostRequirements` block. The researcher records whether the project pins any Feature versions (it does — `node:1` is LTS, `claude-code:1` is unversioned-major, `python:1-3.11-bookworm` is pinned-minor); informs IN-005 / UI-5.

### Convention discovery

Per in-scope layer:

- **Claude Code / Project Filesystem**:
  - Agent file frontmatter convention: which fields are used (`name`, `description`, `model`, `effort`, `tools`, `skills`, `memory`)? What's the `tools:` field's syntax (a flat list of strings? namespaced like `mcp__<server>__<tool>`?)?
  - Skill structure: do existing skills follow `KB-*` naming + `SKILL.md` + `references/` layout (per ADR-0020)?
  - Existing MCP references: any `.claude/skills/*` that names a specific MCP tool (e.g., KB-codebase-research mentions GitNexus, codebase-memory-mcp, Context7; KB-cc-platform mentions Context7). These name *expected* MCP servers — confirm whether they're documented as "available to load" vs. "must be in `.mcp.json`."
- **Dev Environment (Codespaces)**:
  - Lifecycle pattern: project currently uses **Dockerfile-baked** for image-layer tools (ripgrep, jq, bat, tree, less) + **Features** for declarative installations (Claude Code, Node, GitHub CLI, common-utils) + **`onCreateCommand`** for verification (`claude --version && python3 --version && node --version && gh --version`). This is the convention any new install must extend or justify departing from.
  - Pin policy in use: per-Feature `version: "lts"` or `version: "latest"` or no `version:` field — the researcher records the inventory so the per-layer designer can apply IN-005 / UI-5 consistently with the project's existing posture.
  - Secrets surface: `containerEnv` is used for non-secret env (EDITOR, PAGER); no committed secret pattern exists. Confirm this is empty of credentials.

### Specific queries or grep targets

- `Grep "tools:" .claude/agents/*.md` — surface the canonical `tools:` allowlist shape used by existing agents (so the new tool entries match shape).
- `Grep "mcp__" .claude/` — find any existing reference to MCP tool naming conventions.
- `Grep -ri "Serena\|GitNexus\|codebase-memory\|Context7\|Exa\|actionlint\|terraform.?mcp\|openapi.?schema" .claude/ adrs/` — find every existing reference to any of the six servers (or the displaced ones) so the design respects prior assumptions.
- `find . -name "*.md" -not -path "./node_modules/*" | wc -l` and `find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | awk -F. '{print $NF}' | sort | uniq -c | sort -rn` — quick file-type composition for UI-8 / IN-009 (confirm "markdown-heavy").
- Cypher (GitNexus, if available): `MATCH (f:File) WHERE f.path STARTS WITH '.claude/agents/' RETURN f.path` — confirm full sub-agent inventory.

## External research topics

6 topics, exactly at the default budget cap (per ADR-0021 and `references/disciplines/discovery-planning.md`'s 6-topic ceiling). One topic per named MCP server. Each topic's research question is structurally identical (five facts about that server), so consolidation across servers is not viable — each server is its own upstream artifact with its own docs, transports, and auth shape. **Generic-with-N-invocations** per ADR-0021: each topic is dispatched to one `discovery-external-researcher` invocation; up to 6 run in parallel.

### T-001 — Serena MCP server

- **Research question**: For the Serena MCP server, what are the canonical (a) install mechanisms supported, (b) transport options, (c) tool names exposed, (d) authentication requirements (if any), and (e) a recommended pinned version with rationale — and to what extent is Serena's symbol-level value contingent on the target codebase being source-code-heavy vs. markdown-heavy?
- **KB gap justification**: KB-cc-platform documents the generic `.mcp.json` shape (stdio/HTTP/SSE; env-var substitution); it does NOT document Serena specifically — Serena is not one of the example servers in the template. KB-codebase-research mentions GitNexus / codebase-memory-mcp as the canonical codebase-traversal MCPs (per ADR-0007 v2.x); it does NOT cover Serena. KB-codespaces-design covers Features vs Dockerfile vs lifecycle generically; it does NOT cover Serena's specific install path. No ADR resolves Serena's role. This is not `designer-general-knowledge` — Serena is a specific upstream project and its install path / transport / tools are vendor-specific facts a competent designer would NOT just know.
- **Acceptance criteria**: names the upstream source URL (e.g., GitHub repo); identifies at least 2 of {pip install, uv tool install, pipx install, Docker image, prebuilt binary, build from source} that work on `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`; identifies the supported transports (likely stdio); enumerates the tool names exposed (at least the symbol-traversal and file-edit tools); states whether authentication is required (likely none — local LSP-style); quotes a specific recent version number to pin to (semver or tag); identifies the symbol-level-value-vs-markdown-heavy-repo trade-off explicitly (this is the UI-8 fit question).
- **Source constraints**: official upstream repo (likely on GitHub); the project's README / docs; release notes for the recommended pin; community discussion (HN / Reddit / blog posts from teams running Serena at scale) only where it confirms a published version or install path. No speculation about future versions.

### T-002 — mcp-openapi-schema (`hannesj/mcp-openapi-schema`)

- **Research question**: For the `hannesj/mcp-openapi-schema` MCP server, what are (a) install mechanism, (b) transport (likely stdio via Node), (c) tool names exposed for OpenAPI document loading/querying, (d) authentication (likely none for local schema-reading), and (e) a recommended pinned version with rationale?
- **KB gap justification**: KB-api-design covers OpenAPI as a contract format and informs `design-api`, but it does NOT cover this specific MCP server's install path or tool surface. KB-cc-platform documents stdio MCP shape generically but not this server. No ADR addresses it. Not `designer-general-knowledge` — this is a specific upstream package whose published shape requires lookup.
- **Acceptance criteria**: names the upstream GitHub repo + npm package (if applicable); identifies the install command (likely `npx -y <package>@<version>`); confirms transport is stdio; enumerates the tool names (e.g., "load-openapi-schema", "query-openapi-path"); confirms whether auth is required; quotes a specific recent version (semver) to pin to.
- **Source constraints**: official upstream GitHub repo; npm registry page (if published); release notes for the recommended pin. No speculation; if multiple `mcp-openapi-schema`-named packages exist, name the canonical one and explain how the choice was made.

### T-003 — actionlint-mcp (`hongkongkiwi/actionlint-mcp`)

- **Research question**: For the `hongkongkiwi/actionlint-mcp` MCP server, what are (a) install mechanism, (b) transport, (c) tool names exposed for GitHub Actions linting, (d) authentication (likely none; actionlint is a local linter), (e) the upstream `actionlint` binary it depends on (separate package; does it need to be installed first?), and (f) a recommended pinned version with rationale for *both* the MCP wrapper and the underlying actionlint binary?
- **KB gap justification**: KB-github-actions-design and KB-github-actions-platform cover GitHub Actions design and patterns; they do NOT cover the `actionlint-mcp` server's install path or how the underlying `actionlint` binary is acquired. KB-cc-platform documents stdio MCP shape but not this specific package. No ADR resolves it. Not `designer-general-knowledge` — vendor-specific and there's a dual-dependency wrinkle (MCP wrapper + actionlint binary) a competent designer would not just know without lookup.
- **Acceptance criteria**: names upstream repos for both `actionlint-mcp` wrapper and the `actionlint` binary; identifies install commands for both (the binary likely has a Go/curl-install path); confirms transport is stdio; enumerates tool names (likely a single "lint-workflow" tool or similar); confirms no auth; quotes specific recent versions for both with pin rationale; identifies whether the wrapper installs the binary or expects it on `$PATH`.
- **Source constraints**: official upstream GitHub repos for `actionlint-mcp` and `actionlint`; release notes; verified install instructions from each project's README.

### T-004 — HashiCorp Terraform MCP server (UI-2 + UI-5 partial resolution)

- **Research question**: For HashiCorp's Terraform MCP server (the canonical one referenced by the Intent Clarification + PRD), what are (a) install mechanisms supported AND specifically which ones are viable on `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` given no Go toolchain and no Docker-in-Docker are present, (b) transport (stdio vs HTTP), (c) tool names exposed, (d) authentication (likely `TFE_TOKEN` if it queries Terraform Cloud / Enterprise; possibly none if it only reasons offline), and (e) a recommended pinned version with rationale? This topic is load-bearing for UI-2 (Terraform MCP install path); the install-mechanism choice may force a base-image change or new Feature.
- **KB gap justification**: KB-iac-design covers Terraform design discipline; it does NOT cover the Terraform MCP server (a tool-side artifact, not an IaC pattern). KB-codespaces-design covers Features vs Dockerfile vs lifecycle generically; it does NOT cover HashiCorp's specific MCP distribution. KB-cc-platform documents the stdio/HTTP shape generically; not this server's specifics. No ADR addresses it. Not `designer-general-knowledge` — the base-image constraint makes the install path a specialized question requiring lookup of HashiCorp's official distribution channels and currently-available binaries.
- **Acceptance criteria**: names the official HashiCorp source URL (release page / registry); enumerates *all* documented install mechanisms (binary, Go install, Docker image, Homebrew, etc.); for each, states whether it works on the current base image with the current toolchain (Python 3.11, Node LTS, GitHub CLI, no Go, no DinD); recommends one with explicit base-image-fit rationale; identifies the transport; enumerates the tool names exposed; states whether `TFE_TOKEN` is required (and for which tools); quotes a specific recent version to pin to.
- **Source constraints**: HashiCorp's official documentation, GitHub repo, release page; the project's README. No third-party tutorials except to confirm a published install path; no speculation about future support.

### T-005 — Context7 (UI-4 resolution)

- **Research question**: For Context7 MCP, what are (a) the supported transports (remote HTTP endpoint vs locally-installed stdio server), (b) for the remote HTTP option, the endpoint URL and the authentication shape (Bearer header vs query param; the `CONTEXT7_API_KEY` env-var name confirmed), (c) for the stdio option, the install command (npm? Docker? binary?), (d) the tool names exposed (likely `query-docs` per KB-cc-platform's reference to it), and (e) a recommended pinned version with rationale for whichever transport is chosen?
- **KB gap justification**: KB-cc-platform's `references/integrations.md` and its source-of-truth lookup protocol **mention Context7 by name** as the verification source for Claude Code docs (it tells callers to use Context7 if available) — but KB-cc-platform does NOT document how to register Context7 in `.mcp.json`, what transport to choose, or what authentication shape Context7 expects. KB-cc-design is silent on the choice. No ADR addresses Context7's transport. Not `designer-general-knowledge` — Context7 is a specific SaaS + open-source pair and the transport choice has both reliability (remote endpoint availability) and cost (local install footprint) consequences a designer cannot just know.
- **Acceptance criteria**: confirms the official upstream + the hosted endpoint URL; documents both transport options with their trade-offs (remote: no install, requires network; local stdio: install footprint, offline-capable); names the auth header / query-param shape for remote; names the install command for local stdio; enumerates tool names (e.g., `query-docs`, `list-libraries`); recommends a default transport for this project's needs with rationale; quotes a specific recent version to pin to.
- **Source constraints**: Context7's official site + its open-source repo; verified release notes; no speculation. Where two transports exist, link to the official documentation for each.

### T-006 — Exa (UI-3 resolution)

- **Research question**: For Exa MCP, what are (a) the supported transports (remote HTTP vs local stdio), (b) for the remote HTTP option specifically the **transport-level authentication mechanism** (`Authorization: Bearer ${EXA_API_KEY}` header vs `?apiKey=${EXA_API_KEY}` URL query parameter — the PRD's UI-3 explicitly names this question), (c) for the stdio option (if any), the install command, (d) the tool names exposed (web-search-style tools), and (e) a recommended pinned version with rationale? Distinction per PRD: key availability is *closed* by Q5; this topic is purely about the transport/auth *shape*.
- **KB gap justification**: KB-cc-platform documents `.mcp.json` generic auth patterns (the template shows both Bearer-header and URL-arg shapes for different example servers). It does NOT document Exa's specific choice. No ADR addresses Exa. Not `designer-general-knowledge` — Exa's transport-level auth is a vendor-specific protocol decision; the wrong choice causes the per-server probe (FR-4) to fail at acceptance, which is a release-blocker risk explicitly flagged in the PRD's Risks table. Worth the dedicated topic.
- **Acceptance criteria**: confirms the official upstream (Exa Labs); documents the canonical hosted endpoint URL; states authoritatively whether `EXA_API_KEY` is passed as a header (which header name) or as a URL query parameter (which parameter name) — and quotes the source page; if both are supported, recommends one with rationale (security / readability / convention); names the tool names exposed (likely `search`, `find_similar`, `get_contents`); identifies whether a local-stdio variant exists and what its install command is; quotes a specific recent version to pin to.
- **Source constraints**: Exa's official documentation site; Exa's MCP server official repo (if open-sourced); Exa's API reference. No third-party tutorials except to confirm endpoint shape.

## Topics explicitly NOT researched

Per ADR-0021's anti-scope-creep discipline. Every information need with disposition `covered-by-KB`, `covered-by-ADR`, `codebase-topic`, or `designer-general-knowledge` lands here with its resolving artifact + a 1–2-sentence resolution summary.

### Resolved by existing KBs

- **IN-001** (project-scoped `.mcp.json` registration shape + `tools:` allowlist syntax) — Resolved by **KB-cc-platform** (`references/integrations.md` for MCP scope hierarchy + transport types; `assets/templates/mcp-config.json.example` for the canonical shape with stdio/HTTP/SSE examples; `references/extensions.md` for the `tools:`-field semantics on sub-agents). **Resolution summary**: the platform KB documents stdio/HTTP/SSE transport shapes, the `${VAR_NAME}` env-var substitution pattern, the project-scoped `.mcp.json` location, and the `mcp__<server>__<tool>` permission-naming convention used in sub-agent `tools:` allowlists. The Designer applies these patterns directly.

- **IN-002** (which Claude Code primitive to use) — Resolved by **KB-cc-design** (`references/patterns-and-anti-patterns.md`'s decision matrix: MCP server for "connect Claude to an external service"; subagent `tools:` restriction for per-agent allowlist scoping). **Resolution summary**: the design KB's decision matrix is dispositive — the provisioning is unambiguously "MCP server" (for the registration) plus subagent `tools:` restriction (for the wiring). No other primitives are on the critical path.

- **IN-003** (install mechanism: Features vs Dockerfile RUN vs lifecycle) — Resolved by **KB-codespaces-design** (`references/patterns-and-anti-patterns.md`'s "Right hook for right cost" pattern + "Features for common tools" / "Dockerfile for what Features don't cover" choices) + **KB-codespaces-platform** (`references/devcontainer.md` for the lifecycle-hook order table + prebuild boundaries). **Resolution summary**: the design KB establishes the generic trade-off; the platform KB pins down `onCreate` is prebuild-captured, `postCreate` is not, `updateContentCommand` runs on content change AND is prebuild-captured. The per-MCP-server install path within this trade-off is a separate per-server question (T-001..T-006); the choice of *which* mechanism for each server is the Designer's, informed by both KBs.

- **IN-004** (Codespaces secrets surfacing as env vars referenced by `.mcp.json`) — Resolved by **KB-codespaces-platform** (`references/secrets-and-env.md` covers Codespaces secrets vs Actions secrets, `${VAR}` references, what's auto-provisioned) + **KB-cc-platform** (`assets/templates/mcp-config.json.example`'s annotated `${VAR_NAME}` substitution at server startup). **Resolution summary**: Codespaces secrets surface as environment variables in the container; `.mcp.json` uses `${VAR_NAME}` substitution at MCP startup to reference them. The pattern is canonical and well-documented.

### Resolved by inherited ADRs

- (No ADR resolves an information need by itself in this feature; ADR-0021 governs *how* this Plan is structured but is not a resolution. ADR-0007 v2.0.0 establishes GitNexus/codebase-memory-mcp as the existing codebase-traversal MCP role, which is consulted under IN-009 / UI-8 as a codebase-topic, not a research topic.)

### Resolved as `designer-general-knowledge`

- **IN-005** (version-pinning posture for devcontainer tools) — **Resolution summary**: Standard devcontainer hygiene — pin tool versions for determinism; express via Feature `version:` field for declarative installs, `apt-get install <pkg>=<version>` or `ARG <PKG>_VERSION` for Dockerfile, `npm i <pkg>@<version>` for npm-based MCP servers. The per-layer Designer (`design-codespaces`) is committed to documenting the chosen pin policy with explicit rationale in `codespaces-design.md`. Per-server *recommended versions* are NOT general knowledge and are bundled into each external topic (T-001..T-006).

### Resolved as `codebase-topic` (routed to `discovery-codebase-researcher`)

- **IN-006** (`auditing-mcp` BLOCKER criteria) — Resolution: local skill `.claude/skills/auditing-mcp/SKILL.md` + `references/*.md`. The Codebase Researcher records the BLOCKER signal set so `design-cc` can pre-empt them.
- **IN-007** (sub-agent inventory + likely call sites for each MCP — UI-1 mapping) — Resolution: `.claude/agents/*.md`. The Codebase Researcher inventories existing agents, their current `tools:` allowlists, and their declared roles; `design-cc` produces the tool-to-agent mapping at Design.
- **IN-008** (current baseline context-window cost — UI-7) — Resolution: measurement against the built container at Design time using Claude Code's `/context` command (per KB-cc-platform's `Inspect a running session` table). The Codebase Researcher records the baseline; `design-cc` adds the per-server overhead estimate.
- **IN-009** (markdown-heavy-repo + existing codebase-MCP role — UI-8 input) — Resolution: file-type composition of this repo + ADR-0007 v2.0.0 + existing `discovery-codebase-researcher.md` declared role. The Codebase Researcher records both; `design-cc` decides UI-8 with the operator's confirmation (also flagged as a human-resolution item — see Open Questions).

## Estimated effort

- **Codebase research effort**: **medium**. The repo is bounded (≈30 sub-agents, one devcontainer surface, one skills directory, ~30 ADRs). The researcher must inventory all sub-agents' `tools:` allowlists and roles, read `auditing-mcp`'s rubric end-to-end, and confirm ADR-0007's codebase-MCP role. No deep graph traversal of application code is needed (this project has none).
- **External research topic count**: **6 of 6 budget** (cap met). One per named MCP server. Per the discipline (consolidate before exceeding 6): consolidation is not viable here — each server is a distinct upstream artifact with its own docs, transport, and auth. The cap is met, not exceeded.
- **Estimated wall-clock**: external research runs all 6 in parallel (per ADR-0021's ≤6-parallel cap; exactly 6 fits in a single batch). Per-topic acceptance criteria are tight (5 named facts each), bounding any single researcher's wander. Codebase research is single-instance and modest. Plausible total: external in parallel (≈1 wall-clock unit) + codebase (≈1 unit) ≈ 2 units total when run concurrently.

## Open questions for human resolution

Surface at the Research Plan Approval Gate. User answers update the Plan before research begins.

- **OQ-1 — Is the 6-topic external budget appropriate, or should it be reduced?** The Plan exactly fills the default cap with one topic per server. If the user wants fewer external invocations (e.g., on cost grounds), candidates for consolidation: T-005 (Context7) + T-006 (Exa) into a single "remote-HTTP MCPs auth + transport" topic, accepting a less precise per-server answer. **Default if no answer**: proceed with 6 separate topics — the per-server distinction is load-bearing for the per-server probe (FR-4) at acceptance.

- **OQ-2 — UI-6: Does `auditing-mcp` (no-BLOCKER) become a *formal* Gate 6 acceptance criterion, or stay a strongly-recommended check?** This is a human / pipeline-operator decision; it isn't research-resolvable. The PRD already encodes the "no BLOCKER" outcome under NFR-3 / AC-NFR-2-c regardless. The gating-formality question affects only what phase validator `plan-author` writes. **Default if no answer at this Gate**: defer to the Design Composition / Plan Authoring gate, where the orchestrator has the operator answer before phase-validator authoring.

- **OQ-3 — UI-8: Confirm Serena is still wanted at project scope on this markdown-heavy repo, before Design.** The PRD's Q4 closed "all six always-on," so Design cannot unilaterally drop Serena — but the Intent Clarification + PRD both invite the operator to reconfirm. T-001's acceptance criteria require the researcher to explicitly state the markdown-heavy fit caveat, so this question is *informed* by research but resolved by the operator. **Default if no answer at this Gate**: research proceeds; operator confirms at the Research Plan Approval Gate or, latest, at the Design Composition gate.

- **OQ-4 — Are there in-repo prior-art references to *any* of the six servers that the plan-author missed?** The codebase research will grep for each server name; if the operator knows of an existing reference (e.g., a draft `.mcp.json` in a branch, a stash, a private note), naming it here saves a research cycle. **Default if no answer**: rely on the grep result.
