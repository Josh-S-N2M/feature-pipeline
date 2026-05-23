---
id: RN-T-001-serena
doc_type: research-note
version: 1.0.0
status: complete
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/research-plan-v3.md
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
topic_id: T-001
topic_name: Serena MCP server
---

# T-001 — Serena MCP server (research note)

## Topic and question

- **Topic**: Serena MCP server.
- **Research question (verbatim from prompt)**: How is Serena MCP server installed, registered, and used? What is its transport (stdio/HTTP/SSE), tool surface, authentication mechanism, version-pinning convention? Plus the markdown-heavy-fit caveat: how much value does Serena deliver on a repo that is mostly markdown rather than source code?
- **KB-gap justification**: KB-cc-platform documents the generic `.mcp.json` shape but not any specific server. No ADR resolves Serena. Vendor-specific facts; cannot be derived from designer general knowledge.

## Executive summary

Serena is an open-source MCP toolkit from `oraios/serena` that provides symbol-level code retrieval, editing, and refactoring tools to MCP clients (including Claude Code). On a Debian-bookworm Python 3.11 devcontainer the canonical install path is `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` (uv-managed; the uv tool itself is the only required prerequisite). For project-scoped `.mcp.json` always-on use, **stdio** is the correct transport — it is the documented default; HTTP mode exists but is intended for the "start the server yourself and give the client a URL" pattern, which is not what an always-on `.mcp.json` needs. **No authentication is required** for local stdio operation. The latest stable upstream release at the time of research is `v1.5.1` (2026-05-18); pinning by git tag (`git+https://github.com/oraios/serena@v1.5.1`) or by published `serena-agent` package version (`serena-agent==1.5.1`) is the recommended posture. Serena's value is overwhelmingly contingent on the target codebase being source-code-heavy: its tool surface is symbolic (find-symbol, find-referencing-symbols, replace-symbol-body, etc.) built on Language Server Protocol backends. Markdown is listed among "supported languages" only in the broadest sense; no symbol-level analysis is documented for markdown, and the documented capabilities all presume source-code semantics (declarations, references, type hierarchies). On a repo that is overwhelmingly markdown, Serena's symbol-level tools collapse to the basic-utility subset (`search_for_pattern`, `read_file`, `list_dir`, `find_file`) — capabilities that are not differentiated from what Claude Code natively offers.

## Findings

### F-1 — Canonical install command on Debian-bookworm Python 3.11

- **Claim.** The upstream-recommended install + launch path for a Linux environment with Python 3.10+ is `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`. This pulls Serena directly from GitHub via `uvx` (a `uv` subcommand) and starts the MCP server in one step. An alternative is `uv tool install -p 3.13 serena-agent@latest --prerelease=allow` followed by invoking `serena` from PATH. The base image `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` has Python 3.11; `uv` is not pre-installed and must be added (one line: `pip install uv` or the official `astral.sh/uv` installer).
- **Source.** Official upstream repository — oraios/serena. https://github.com/oraios/serena (README, accessed 2026-05-23).
- **Quote (≤15 words).** "Serena is managed by uv, and installing uv is the only required prerequisite."
- **Confidence.** High (official primary source).
- **Caveats.** Upstream README's `uv tool install` example pins Python 3.13; Python 3.11 is documented elsewhere as compatible (Itecs guide cites "Python 3.10 or later"). Serena's own docs warn experimental Python 3.12+ may have LSP compatibility issues for some language backends — not relevant to a Python 3.11 environment. **Do not** install via "an MCP or plugin marketplace" — upstream explicitly warns those carry outdated commands.

### F-2 — Transport: stdio is the default and the right choice for `.mcp.json` always-on

- **Claim.** Serena's default transport for MCP-client integration is **stdio** (the server is launched as a subprocess of the MCP client; communication is JSON-RPC over stdin/stdout). HTTP mode is available but is documented as a "start the Serena MCP server yourself in HTTP mode and provide the client with the URL" pattern — i.e., the operator runs Serena out-of-band and points the client at it. SSE is referenced in the changelog (HTTP/SSE mode bug fix in v1.2.0) but is not the documented default for client integrations.
- **Source (primary).** Itecs install guide. https://itecsonline.com/post/how-to-install-serena-mcp-linux (accessed 2026-05-23).
- **Quote (≤15 words).** "stdio transport, the standard protocol for MCP client-server communication."
- **Source (corroborating).** Serena official Connecting Your MCP Client docs. https://oraios.github.io/serena/02-usage/030_clients.html (accessed 2026-05-23) — shows the `claude mcp add serena -- serena start-mcp-server …` form (subprocess; stdio).
- **Confidence.** High (the upstream Claude-Code-integration example is unambiguously subprocess-launched; HTTP mode is an explicit opt-out for a separate use case).
- **Caveats.** None for the project-scoped `.mcp.json` always-on use case. If the design later wants to share one Serena instance across multiple containers or external clients, HTTP would become relevant — out of scope for this devcontainer.

### F-3 — `.mcp.json` registration shape (Claude Code-specific)

- **Claim.** For Claude Code project-scope, upstream recommends `claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"`. The `--context claude-code` flag adapts Serena's tool descriptions and system prompts to Claude Code's conventions. The `--project` flag binds the server to a specific project root. When using the `uvx` form (no global install), the equivalent is `claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)`. Both forms produce a stdio-transport entry in `.mcp.json` of the standard shape: `{"command": "serena", "args": ["start-mcp-server", "--context", "claude-code", "--project", "<root>"]}` (or `"command": "uvx"` with the appropriate args list).
- **Source.** Serena official Connecting Your MCP Client docs. https://oraios.github.io/serena/02-usage/030_clients.html (accessed 2026-05-23).
- **Quote (≤15 words).** *(no direct quote — paraphrased; one-quote-per-source budget reserved for F-2's corroboration if needed)*
- **Confidence.** High (official upstream docs).
- **Caveats.** Upstream notes recent Claude Code / Opus model updates have "drastically reduced adherence to instructions pertaining to Serena's tools" and recommends additional hooks — relevant to DesignDoc UI-1 / UI-7 / UI-8 sub-decisions about whether Serena's tool-surface adherence is reliable enough to justify always-on.

### F-4 — Tool surface (authoritative enumeration)

- **Claim.** Serena exposes roughly 20-25 MCP tools, grouped by function. The non-JetBrains-only set available via the MCP server is:
  - **Retrieval (symbol-level)**: `find_symbol`, `get_symbols_overview` (file outline), `find_referencing_symbols`, `find_declaration`, `find_implementations`, `diagnostics` / inspections.
  - **Symbolic editing**: `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `safe_delete`.
  - **Refactoring**: `rename` (symbol), `propagate_deletions`.
  - **Basic utilities (non-symbolic)**: `search_for_pattern` (regex), `replace_content` (regex/literal), `list_dir`, `find_file`, `read_file`, `execute_shell_command`.
  - **Memory / project**: a memory-management subsystem (project-scoped notes the agent can write and recall), plus onboarding/project-init tools (`onboarding`, project-config commands).
  - **JetBrains-only (NOT exposed through MCP)**: `move`, `inline`, `search in project dependencies`, `type hierarchy`, breakpoint/variable debugging.
- **Source.** Official upstream repository — oraios/serena. https://github.com/oraios/serena (README, accessed 2026-05-23).
- **Quote (≤15 words).** *(one-quote-per-source already spent on F-1; this finding is fully paraphrased)*
- **Confidence.** High for the categories and most tool names; medium for the precise tool-id strings (Serena's tool ids in the MCP wire protocol use snake_case as shown in the basic-utility list; the README presents some symbolic-tool names as natural-language phrases — "find symbol" — which mapping to snake_case `find_symbol` is the convention shared across mcp-server registries).
- **Caveats.** The exact MCP tool-id strings (which is what the Claude Code `tools:` allowlist consumes) are stable in the snake_case form but should be confirmed at integration time by running `claude mcp list` against an installed Serena instance — they are the authoritative source. The non-symbolic basic utilities (`search_for_pattern`, `read_file`, etc.) duplicate native Claude Code capabilities and contribute most of the context-window cost without unique value on a markdown-heavy repo.

### F-5 — Authentication: none required for local stdio

- **Claim.** Serena requires no API keys, OAuth tokens, or shared secrets for local stdio operation. The only "credential-shaped" inputs are optional environment variables some language-server backends require (e.g., `DOTNET_ROOT` for F#) — these are LSP backend prerequisites, not Serena authentication. There is no Codespaces-secret surface area required for this server.
- **Source (primary).** Official upstream Connecting Your MCP Client docs. https://oraios.github.io/serena/02-usage/030_clients.html (accessed 2026-05-23).
- **Source (corroborating).** mcpservers.org Serena listing. https://mcpservers.org/servers/oraios/serena (accessed 2026-05-23) — explicitly notes no API keys are required.
- **Quote (≤15 words).** *(both sources agree by omission — neither documents any required auth; no quote needed)*
- **Confidence.** High.
- **Caveats.** A separately paid JetBrains plugin exists with its own license; this is out of scope (we're integrating the MCP server, not the JetBrains plugin).

### F-6 — Version pinning: prefer semver release tag

- **Claim.** The upstream `oraios/serena` repository follows semver release tags. The latest stable tag at research time is **v1.5.1** (2026-05-18). Recent releases:
  - v1.5.1 — 2026-05-18 (onboarding-tool hotfix)
  - v1.5.0 — 2026-05-18 (GDScript LSP via TCP)
  - v1.3.0 — 2026-05-11 (Angular/HTML/SCSS/CSS/1C language servers; **breaking config change**: `base_modes` overrides in `project.yml` replaced with `added_modes`)
  - v1.2.0 — 2026-04-27 (Ada/SPARK, Svelte, Java-with-Lombok; HTTP/SSE bug fix; **tool replacement**: `ReplaceRegexTool` → `ReplaceContentTool`)
  - v1.1.2 — 2026-04-14
- **Source.** Releases page — oraios/serena. https://github.com/oraios/serena/releases (accessed 2026-05-23). Changelog — https://github.com/oraios/serena/blob/main/CHANGELOG.md (accessed 2026-05-23).
- **Quote (≤15 words).** *(release-list facts; no narrative quote)*
- **Confidence.** High.
- **Caveats.** The `uvx --from git+https://github.com/oraios/serena` form without a `@<tag>` suffix tracks `main` — **not** suitable for production. Pin via either (a) `uvx --from git+https://github.com/oraios/serena@v1.5.1 serena start-mcp-server` (tag-pinned) or (b) `uv tool install serena-agent==1.5.1` (PyPI-package pinned, if the project publishes — README's install example uses `serena-agent@latest` which suggests it is on PyPI). Both v1.2.0 and v1.3.0 contain documented breaking changes — upgrading across either requires a config or tool-id review. **Recommendation**: pin to `v1.5.1` or whichever is latest-stable at integration time, by **git tag** for transparency (the tag is in the `.mcp.json` arg list, visible in code review).

### F-7 — Markdown-heavy fit: low symbol-level value

- **Claim.** Serena's value proposition is symbol-level code understanding, built on Language Server Protocol backends per programming language. Its tools — `find_symbol`, `find_referencing_symbols`, `replace_symbol_body`, `type_hierarchy`, `find_implementations`, etc. — are operations over declarations, references, and types as defined by an LSP server for a source language. Markdown is listed among "supported languages" in the broadest sense (the LSP ecosystem includes generic markdown servers for outline/link extraction), but upstream documentation provides no symbol-level capability listing for markdown, and the marketed value is uniformly framed around code ("the IDE for your coding agent"). On a repo whose primary artifacts are markdown documents (specifications, KBs, PRDs, Plans, ADRs), Serena's symbol-level tools either return empty results or collapse to the basic-utility subset (`search_for_pattern`, `read_file`, `list_dir`, `find_file`) — capabilities that overlap heavily with Claude Code's native Read/Grep/Glob tools and provide no differentiation. Conclusion: on a markdown-dominant repository, the always-on token cost of Serena's tool descriptions is paid every session for capabilities the agent rarely uses and that duplicate native tools.
- **Source (primary).** Official upstream README. https://github.com/oraios/serena (accessed 2026-05-23) — every example, screenshot, and capability description is code-centric; the marketed framing is "the IDE for your agent."
- **Source (corroborating).** mcpservers.org listing. https://mcpservers.org/servers/oraios/serena (accessed 2026-05-23) — "Serena targets code repositories" framing.
- **Quote (≤15 words).** *(README quote-budget spent on F-1; this is paraphrased)*
- **Confidence.** Medium-high. The factual basis is strong (the tool surface IS symbol-and-LSP-bound; the documentation IS uniformly code-framed). The judgment ("low value on a markdown-heavy repo") is analyst synthesis but follows directly from the tool surface.
- **Caveats.** Serena's basic-utility tools (`search_for_pattern`, `read_file`) are still functional on markdown; the question is differentiation versus context-cost. If the repository contains a non-trivial code subdirectory (e.g., `.claude/skills/auditing-*/scripts/*.py`, audit Python scripts, validator scripts), Serena's symbol-level tools apply to that subdirectory — but a server-wide always-on registration pays full context cost for a small applicable subtree. The right design question (for Synthesis / UI-8 / per-layer design) is: does the Python script surface in this repo justify Serena's always-on cost, or would on-demand activation (Claude Code's `/mcp` enable/disable, or removing Serena entirely in favor of `KB-codebase-research`-driven GitNexus + native tools) be the better posture?

## Synthesis (analysis)

The findings converge on a tension the PRD already anticipates (UI-8). Serena is a well-engineered, actively maintained, no-auth-required, stdio-clean MCP server — there is no install/transport/auth/version blocker. The blocker is *fit*: the repository this devcontainer serves is dominated by markdown specification artifacts (PRDs, Plans, ADRs, KB documents, agent files), and Serena's differentiating capability set is symbol-level code operations. Three options are visible from the research:

1. **Always-on with broad `tools:` exposure** — pay full context cost (estimate: tool-description overhead for ~20 tools is meaningful; the actual byte cost should be measured at Design via `/context`). Most tools unused most of the time on this repo.
2. **Always-on with narrowed `tools:` allowlist** — register Serena but expose only the basic-utility subset (`search_for_pattern`, `read_file`, `list_dir`, `find_file`, `execute_shell_command`). This minimizes the token-cost surface but eliminates Serena's differentiation versus Claude Code's native Read/Grep/Glob — making the registration arguably redundant.
3. **Drop Serena from the always-on seven, keep it as on-demand** — `discovery-codebase-researcher` (the most likely Serena consumer per the Plan) is already served by GitNexus (primary) + codebase-memory-mcp (fallback) per ADR-0018 and `KB-codebase-research/SKILL.md`. If Serena's symbol-level value is small on this repo, the always-on slot may not earn its keep.

This is a Design decision (UI-8), not a Research recommendation; the research note's role is to surface the trade-off cleanly so `design-cc` / `design-codespaces` can adjudicate. The factual inputs needed for that adjudication are now present.

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Install command(s) workable from Debian-bookworm Python 3.11 devcontainer | **Satisfied** | F-1 gives two upstream-documented install paths (`uvx --from git+...` and `uv tool install serena-agent`) both compatible with Python 3.10+; base image is 3.11. |
| Transport recommended for project-scoped `.mcp.json` always-on | **Satisfied** | F-2 + F-3: stdio (default), via `serena start-mcp-server --context claude-code --project "$(pwd)"`. |
| Authoritative tool surface enumeration with brief descriptions | **Satisfied** | F-4 enumerates the MCP-exposed tools by category with descriptions; JetBrains-only tools explicitly excluded. Exact snake_case tool-id strings should be verified at integration time via `claude mcp list`. |
| Authentication mechanism | **Satisfied** | F-5: none required for local stdio operation. |
| Version-pinning recommendation | **Satisfied** | F-6: pin by semver git tag (`v1.5.1` current latest, 2026-05-18) or by `serena-agent==1.5.1` PyPI pin. Two breaking changes in 4 recent versions argue against floating `main` or `@latest`. |
| Markdown-heavy-fit observation | **Satisfied** | F-7: symbol-level value is overwhelmingly code-contingent; on a markdown-dominant repo Serena collapses to basic utilities overlapping with native Claude Code tools. Surfaced as input for UI-8 narrowing. |
| ≥3 independent reputable sources | **Satisfied** | Official upstream repo (oraios/serena) + official upstream docs site (oraios.github.io/serena) + GitHub releases/changelog + mcpservers.org community registry + Itecs install guide = 5 sources, with the first three being upstream-authoritative. |

All seven acceptance criteria satisfied; no escalation required.

## Open questions

- **OQ-T1-1.** The exact MCP wire-protocol tool-id strings (snake_case identifiers as they appear in `tools_list` over the MCP transport, which is what Claude Code's `tools:` allowlist consumes) are inferred from upstream documentation but not verified by direct invocation. Resolution belongs at the Design or Plan stage, not at Discovery: an integration smoke test (`uvx --from git+https://github.com/oraios/serena@v1.5.1 serena start-mcp-server` → connect with a minimal MCP client → list tools) would settle the authoritative identifier set. Not a blocker for Design.
- **OQ-T1-2.** Whether Serena's `--context claude-code` system-prompt-override (mentioned in F-3 caveat) needs to be applied to the devcontainer's Claude Code launch, and whether the upstream warning about "reduced instruction adherence" with recent Opus models is load-bearing for this project's adoption decision. This is a UI-8 sub-question for `design-cc` to adjudicate.
- **OQ-T1-3.** Estimated context-window cost (tokens) of Serena's tool descriptions when registered always-on. Cannot be answered by external research; must be measured at the Design stage against an installed instance (IN-008 / UI-7 in the Research Plan). Listed here for traceability.

## Source list

1. **oraios/serena (official upstream repository, README)** — https://github.com/oraios/serena — accessed 2026-05-23. Primary source for install commands, capability framing, language support, tool-category enumeration.
2. **Serena official documentation, "Connecting Your MCP Client"** — https://oraios.github.io/serena/02-usage/030_clients.html — accessed 2026-05-23. Primary source for Claude Code / Claude Desktop integration, transport (stdio default), `claude mcp add` form.
3. **oraios/serena Releases** — https://github.com/oraios/serena/releases — accessed 2026-05-23. Authoritative source for version tags and release dates.
4. **oraios/serena CHANGELOG.md** — https://github.com/oraios/serena/blob/main/CHANGELOG.md — accessed 2026-05-23. Authoritative source for breaking changes between recent versions (v1.2.0 `ReplaceContentTool` swap; v1.3.0 `base_modes` → `added_modes`).
5. **mcpservers.org listing for oraios/serena** — https://mcpservers.org/servers/oraios/serena — accessed 2026-05-23. Community MCP registry; corroborates no-auth-required claim and code-repository framing.
6. **Itecs Online — "How To Install Serena MCP For Ubuntu Linux"** — https://itecsonline.com/post/how-to-install-serena-mcp-linux — accessed 2026-05-23. Independent install guide; corroborates stdio default and `uvx --from git+...` Linux install form. (Cited as corroborating, not authoritative.)
