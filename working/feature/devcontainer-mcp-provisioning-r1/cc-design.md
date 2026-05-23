---
id: CC-DESIGN-devcontainer-mcp-provisioning-r1
doc_type: per-layer-design-subsection
layer: claude-code
version: 1.0.1
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
synthesis_input: working/feature/devcontainer-mcp-provisioning-r1/synthesis.md
generated: 2026-05-23T00:00:00Z
generated_by: design-cc
change_summary: >-
  Initial Claude Code / Project Filesystem design subsection for the
  devcontainer-mcp-provisioning-r1 feature. Specifies the seven-server
  .mcp.json shape, per-agent narrow `mcp__` allowlist edits to 7 of 36
  agents (preserving the existing zero-`mcp__` state for the other 29),
  the KB-mcp-platform / KB-mcp-design authoring outlines following the
  trifecta convention verbatim, the auditing-mcp augmentation plan
  (operational-health rules + GitNexus-specific rules), and the
  `.claude/runtime/mcp-events.jsonl` JSONL schema that resolves the F5.4
  no-consensus UI-15 primary-to-fallback transition surface. All
  cross-cutting decisions (ADR candidates, family-coordinator
  resolution, redaction code-site placement) surfaced as Q-CC-N open
  items for design-composer per FR-5.
---

# Claude Code / Project Filesystem Design — devcontainer-mcp-provisioning-r1

This subsection covers all artifacts inside `.claude/` and the project-scoped `.mcp.json` at the repo root. The Dev Environment / Codespaces layer (devcontainer.json features, Dockerfile, lifecycle-hook scripts, Codespaces secret wiring) is owned by `design-codespaces` and referenced here only where the two layers interface (postStart writes to the cc-owned `mcp-events.jsonl`; devcontainer.json `containerEnv` maps Codespaces secrets that `.mcp.json` reads by env-var name).

## Contents

- [Layer responsibility scope](#layer-responsibility-scope)
- [Inventory of CC primitives being introduced or modified](#inventory-of-cc-primitives-being-introduced-or-modified)
- [CLAUDE.md changes](#claudemd-changes)
- [`.mcp.json` design](#mcpjson-design)
- [Rule patterns](#rule-patterns)
- [Skill patterns](#skill-patterns)
- [Subagent patterns — per-agent allowlist updates](#subagent-patterns--per-agent-allowlist-updates)
- [Hook patterns](#hook-patterns)
- [Permission policy](#permission-policy)
- [MCP server policy](#mcp-server-policy)
- [Plugin packaging](#plugin-packaging)
- [Command-to-skill migration](#command-to-skill-migration)
- [`mcp-events.jsonl` schema (UI-15 contract)](#mcp-eventsjsonl-schema-ui-15-contract)
- [`KB-mcp-platform` authoring outline](#kb-mcp-platform-authoring-outline)
- [`KB-mcp-design` authoring outline](#kb-mcp-design-authoring-outline)
- [`auditing-mcp` augmentation plan](#auditing-mcp-augmentation-plan)
- [Acceptance criteria contribution](#acceptance-criteria-contribution)
- [Dependencies on other layers](#dependencies-on-other-layers)
- [Architectural Questions for Composer (Q-CC-N)](#architectural-questions-for-composer-q-cc-n)
- [Open items](#open-items)

## Layer responsibility scope

The Claude Code layer owns the following artifacts for this feature (per synthesis §9.1):

1. **`.mcp.json`** at repo root — project-scoped registration of all seven MCP servers, with the `env:` block as the redaction allowlist SSOT (D-7). New file.
2. **Per-agent `tools:` allowlist edits** on 7 of 36 `.claude/agents/*.md` files — narrow `mcp__<server>__<tool>` additions per D-9. The other 29 agents are explicitly NOT touched (the existing zero-`mcp__` state is preserved as a least-privilege invariant; constraint #5 from synthesis §8).
3. **`KB-mcp-platform/`** skill — new platform-half (What) skill following `KB-cc-platform` template verbatim per D-10 and constraint #12.
4. **`KB-mcp-design/`** skill — new design-half (How) skill following `KB-cc-design` template verbatim per D-10 and constraint #12.
5. **`auditing-mcp/`** augmentation — adds operational-health rules (lifecycle health-check outcomes, runtime log integrity, error-handling presence, primary/fallback expression completeness) plus GitNexus-specific rules per FR-11-c / UI-14.
6. **`.claude/runtime/mcp-events.jsonl`** contract — the JSONL schema for primary→fallback transitions, readiness probes, and structured failure records (D-5). The cc layer defines the schema; design-codespaces' `postStartCommand` writes to it.

**Out of scope for this layer (referenced where the interface matters):**

- The devcontainer.json Features block, the postCreate/postStart lifecycle scripts, the Dockerfile, the Codespaces secret-to-`containerEnv` wiring (all owned by `design-codespaces`).
- ADR authorship (per FR-5; surfaced as Q-CC-N items below for `design-composer`).
- The pipeline orchestrator topology, gate definitions, or any change to the 13-stage pipeline (out of feature scope per PRD Policy Decisions).

## Inventory of CC primitives being introduced or modified

| # | Type | Filename / path | Purpose | Scope | Activation | Lowest-cost-primitive justification (KB-cc-design Principle 1) |
|---|---|---|---|---|---|---|
| 1 | Project-scoped MCP config | `.mcp.json` (root) | Register the seven MCP servers always-on, with `env:` block as redaction-allowlist SSOT | project | always-loaded every CC session in this repo | The project-scoped `.mcp.json` IS the canonical primitive for shared MCP registration. Per KB-cc-platform routing, this is the only way to commit MCP servers to source so every operator gets them at session start. User-scoped (`~/.claude/`) violates Q4 (all seven always-on) and the project's onboarding goal (US-1). MCP tool **schemas** are deferred until invoked, so the per-request context cost is zero until a tool is actually called — this is the lowest context-cost primitive for "always available, but invisible until used." |
| 2 | Subagent edit (per-agent `tools:` allowlist) | 7 files under `.claude/agents/` (see table below) | Add `mcp__<server>__<tool>` entries to exactly the 7 consumer agents; explicitly preserve zero-`mcp__` state for the other 29 | project | per-agent — only the edited agents can invoke MCP tools | Editing existing subagent `tools:` is the convention the project already uses to restrict tool access per agent. No new subagent is introduced. Narrow per-agent (D-9) is the least-privilege expression of the policy; broad wildcard (`mcp__*`) on all 36 agents would violate least-privilege and break the C-0445 grep-verified zero-`mcp__` invariant for 29 unrelated agents. |
| 3 | Skill (platform half) | `.claude/skills/KB-mcp-platform/SKILL.md` + `references/` + `assets/templates/` | "What" half of the W/H/A trifecta — MCP platform facts (transports, install paths, credential surfaces, redaction allowlist contract, lifecycle integration points, mcp-events.jsonl schema). Loaded by `design-cc`, `design-composer`, plan-author, reviewers when MCP work is in scope | project | model-invocable (description match) + user-loadable via `skills:` frontmatter; description text costs ~one line per request when discoverable | The W/H/A trifecta is the project's established maintenance interface (constraint #12: three precedents). A skill is the right primitive for "reusable reference knowledge that loads only when MCP-related work is in flight." A rule cannot carry `references/` + `assets/templates/`; CLAUDE.md would force every session to pay the cost. KB-cc-platform's full body costs the same shape on every session it loads into — same trade-off here. |
| 4 | Skill (design half) | `.claude/skills/KB-mcp-design/SKILL.md` + `references/patterns-and-anti-patterns.md` + `references/principles.md` | "How" half of the W/H/A trifecta — MCP design discipline. Mirrors KB-cc-design / KB-codespaces-design / KB-github-actions-design two-file convention verbatim | project | model-invocable (description match); slim by convention (no `assets/`, two reference files exactly) | Same justification as #3. The design half's slimness is a strong convention across all three existing trifectas (exactly two reference files, no assets). Departing would create a 4th template (D-10's single-option rationale). |
| 5 | Skill (audit half — augmentation, not new file) | `.claude/skills/auditing-mcp/` (existing skill, augmented) | Add operational-health rule families + GitNexus-specific rules. Sister-cross-reference description updated to name new KB-mcp-* halves | project | model-invocable + script-invocable (`scripts/audit_mcp.py`); same activation as today | The existing skill is the natural augmentation surface — it already audits `.mcp.json` configurations. Creating a sibling "auditing-mcp-runtime" skill (one of the open questions in codebase-analysis.json) would split the audit interface across two skills, violating KB-cc-design Principle 5 (one source of truth). The augmentation is in-place; whether the new rules expand the existing 10-dimension rubric or introduce an 11th dimension is a Design choice surfaced as Q-CC-4. |
| 6 | Runtime artifact / event file (CC contract; written by Codespaces postStart) | `.claude/runtime/mcp-events.jsonl` | Durable cross-server event surface — primary→fallback transitions (UI-15), readiness probes (FR-8), structured failure records (FR-9). NOT a per-line log mirror (D-6) | project (file lives in repo path but is `.gitignore`-able by Composer's call — see Q-CC-2) | Written at postStart and at runtime by whoever detects the event; read by operators via documented tail command | This is the lowest-cost durable contract for "machine-readable cross-server events" per D-5. The rejected alternatives (agent-level acknowledgement, frontmatter convention, stderr-only) all fail uniformity, machine-readability, or operator-visibility tests against the 36-agent surface. JSONL is the only option that keeps the file append-only, structured, and tail-friendly. |

**Not modified by this design:**

- CLAUDE.md (none today at repo root; this feature does not introduce one — see next subsection).
- `.claude/rules/` (none today; this feature does not introduce path-gated rules).
- `.claude/commands/` (no command-to-skill migration in this feature).
- `.claude/hooks/` (no hooks introduced; see Hook patterns subsection for rationale).
- Output styles, plugins, MCP server SDK code (not authored by this layer).

## CLAUDE.md changes

**No CLAUDE.md is introduced by this feature.** Per KB-cc-design Principle 5 (one source of truth) and the cost-conscious-selection principle, all MCP-related operator knowledge moves into the two new skills (`KB-mcp-platform` for facts, `KB-mcp-design` for discipline). A CLAUDE.md addition would:

- Cost every session in this repo the MCP-related lines on every request, even sessions that never invoke an MCP-related agent (e.g., a developer reading docs).
- Duplicate content that the skills carry — KB-cc-design Principle 5 anti-pattern.
- Bypass the trifecta convention (constraint #12) without any benefit.

The two new skills are model-invocable on description match, so an agent doing MCP work (e.g., `design-cc` on a future feature, `design-composer` reconciling MCP changes, an operator asking "how do I rotate the Exa key") will pull them in. Sessions not doing MCP work pay zero.

If a future feature finds that operators consistently need MCP knowledge in main-session context (rather than agent-loaded), the right move is to surface that as a re-scope ("add an MCP one-liner to CLAUDE.md pointing at the trifecta") rather than to front-load now.

## `.mcp.json` design

Project-scoped MCP config file at repo root. Per synthesis D-2, D-7, and the per-server matrix in synthesis §4. Authored by `design-cc`, validated by augmented `auditing-mcp` at Gate 6.

**Top-level shape (sketch — final fields verified against the live KB-cc-platform `assets/templates/mcp-config.json.example` at authoring time):**

```jsonc
{
  "mcpServers": {
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena@<PIN_PRE_V1.3.0>", "serena", "start-mcp-server"],
      "env": {}
    },
    "mcp-openapi-schema": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-openapi-schema@0.0.1", "<path-to-spec>"],
      "env": {}
    },
    "actionlint-mcp": {
      "type": "stdio",
      "command": "actionlint-mcp",
      "args": [],
      "env": {}
    },
    "terraform-mcp": {
      "type": "stdio",
      "command": "terraform-mcp",
      "args": [],
      "env": {
        "TFE_TOKEN": "${TFE_TOKEN}"
      }
    },
    "gitnexus": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "gitnexus@${GITNEXUS_TAG}", "mcp"],
      "env": {
        "GITNEXUS_SKIP_OPTIONAL_GRAMMARS": "1"
      }
    },
    // ↑ Install-mechanism corrected at cycle-3 reconciliation D-3.2 F2.
    //   Was: command "uvx", args ["--from", "git+...", "gitnexus", "serve"].
    //   GitNexus is npm-only TypeScript (PyPI 404); upstream README's
    //   canonical Claude-Code wiring is `npx -y gitnexus@<TAG> mcp`.
    //   Persistent install (in postCreate.sh) is `npm install -g gitnexus@<TAG>`.
    //   Pin: GITNEXUS_TAG=1.6.5 (latest stable npm dist-tags.latest 2026-05-16).
    //   env-block GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 PRESERVED per AC-CS-9 wrapping intent
    //   (suppresses npm's vendored tree-sitter grammar build → no C++ toolchain at cold-cache).
    //   Variable name change: <PIN_TAG> → ${GITNEXUS_TAG} for consistency with versions.env discipline.
    //   Prereq: Node.js LTS on PATH at MCP-server-spawn time (provided by node:1@20 Feature).
    "codebase-memory-mcp": {
      "type": "stdio",
      "command": "<TBD-per-ADR-0007-v2.2.0>",
      "args": [],
      "env": {}
    },
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp",
      "headers": {
        "x-api-key": "${EXA_API_KEY}"
      }
    }
  }
}
```

**Design rationale per server:**

- All five OSS-local servers use `type: stdio` per D-2 (vendor-canonical). Context7 and Exa use `type: http` against their vendor-canonical endpoints; this preserves Claude Code's 5-attempt exponential-backoff reconnect (C-0300) which stdio servers do not get (C-0301).
- All credentials are `${VAR}` env-var references — no inline secrets (NFR-2-a; D-7).
- The `env:` block in each server entry plus the HTTP `headers:` block enumerate every env-var-name and header-name that carries a credential. This is the **single source of truth** for the redaction-allowlist (D-7); the log-surface boundary in design-codespaces' postStart wrapper consumes this list verbatim. Adding a credential later means adding it here and **only here**.
- Exa's `exaApiKey` URL-query-param form is **rejected at config-validation time** by the augmented `auditing-mcp` (D-7, E-0095). The header form above is the only accepted Exa auth shape.
- Server names match the `mcp__<server-name>__<tool-name>` convention for downstream tool-allowlist entries on agents.
- Note on `codebase-memory-mcp`: included in `.mcp.json` because it is the ADR-0018 / ADR-0007 v2.2.0 documented fallback for `discovery-codebase-researcher` and `review-architecture-auditor`. The exact install command awaits the per-server install-path Discovery output for `codebase-memory-mcp`. **The PRD's "seven named servers" inventory does not include `codebase-memory-mcp`** — it is included in `.mcp.json` as the in-product fallback, not as one of the seven primary servers. This is a deliberate inventory question — surfaced as **Q-CC-6**.

## Rule patterns

**No new rules are introduced** in `.claude/rules/` by this feature. The project does not appear to use the `rules/` mechanism today (zero rules files observed in codebase-analysis), and the MCP design knowledge fits better in the two new skills:

- Unconditional rules load every session — they would cost the same as a CLAUDE.md addition and worse than the trifecta skills which only load when MCP work is in flight.
- Path-gated rules (`paths:` frontmatter, per KB-cc-design Principle 2) would be appropriate if MCP discipline only applied to certain file paths — but MCP work touches `.mcp.json`, `.claude/agents/*.md`, the trifecta skills themselves, and (indirectly) `.devcontainer/`. No single path-gate captures this surface cleanly. The two skills are the cleaner primitive.

If a future iteration finds operators need a "when editing .mcp.json, check X" path-gated reminder, that's an additive design choice with low cost — but not warranted in this feature.

## Skill patterns

The two new skills (`KB-mcp-platform`, `KB-mcp-design`) follow the trifecta convention extracted in synthesis §6 verbatim. Specific patterns:

- **Model-invocable, not user-invocable.** No `disable-model-invocation: true`. Both skills are loaded when an agent doing MCP work matches their description; that's the same activation as the three existing trifecta exemplars.
- **`allowed-tools` scoped per leg.** KB-mcp-platform: `Read, Grep, Glob, Edit, Write, WebFetch` (mirroring KB-cc-platform — Write is allowed because operators may follow the skill's guidance to author a `.mcp.json` template). KB-mcp-design: `Read, Grep, Glob` (mirroring KB-cc-design and KB-codespaces-design — design halves are read-only by convention). No MCP tool references inside `allowed-tools` (the skills describe MCP, they don't invoke it).
- **Sister-cross-reference in `description`.** KB-mcp-platform's description ends with "Pairs with KB-mcp-design." KB-mcp-design's description ends with "Pairs with KB-mcp-platform." This matches the universal convention across all three existing trifectas (C-0482).
- **`pedagogical_sections` frontmatter per ADR-0030.** Each skill declares the references files that legitimately carry anti-pattern catalogs or negative-example fixtures. Per codebase-analysis precedent: KB-cc-design has 1 entry, KB-codespaces-design has 1, KB-github-actions-platform has 8. KB-mcp-design will declare exactly one (`patterns-and-anti-patterns.md`); KB-mcp-platform will declare entries for any reference file that names anti-pattern examples (likely `auth-and-redaction.md` and `lifecycle-hooks.md`).
- **Skill `name:` frontmatter is lowercase-hyphenated.** `name: kb-mcp-platform` and `name: kb-mcp-design` (matching the existing convention of lowercase `name:` despite the directory's uppercase `KB-` prefix; C-0471).
- **Family-membership declaration is body-prose, not frontmatter.** Per C-0483/C-0537. The two new skills declare their family membership in the SKILL.md body, exactly mirroring how `auditing-mcp` currently declares `auditing-cc-configs` family membership at line 30. **The specific family these skills declare membership in depends on the D-10 family-coordinator resolution** — surfaced as Q-CC-1.

Detailed authoring outlines for each skill are below in their own subsections.

## Subagent patterns — per-agent allowlist updates

Per D-9 (narrow per-agent), 7 of 36 `.claude/agents/*.md` files get `mcp__<server>__<tool>` additions. The other 29 are explicitly untouched. The table below is the canonical mapping; the augmented `auditing-mcp` will validate it.

**Reasoning configuration discipline (KB-cc-design Principle 9):** This feature does **not** modify any agent's `model:`, `effort:`, or `skills:` fields. Only `tools:` is touched. The existing reasoning configuration on each consumer agent is preserved verbatim (e.g., `discovery-codebase-researcher` keeps `model: opus`, `effort: high`, `memory: project`, `skills: [KB-codebase-research]`). The `skills:` arrays on each agent are not modified to add MCP-knowledge skills here; the augmented `auditing-mcp` will simply check that the new `tools:` entries map to servers registered in `.mcp.json`. (Loading `KB-mcp-platform` / `KB-mcp-design` into every consumer agent's `skills:` is rejected: those skills are reference-grade for design/maintenance work, not runtime work. They load on model invocation when relevant.)

### Per-agent allowlist edits

| # | Agent file | New `mcp__` entries (added to existing `tools:` array) | Existing reasoning config (preserved verbatim) | Justification |
|---|---|---|---|---|
| 1 | `design-api.md` | `mcp__mcp-openapi-schema__*` (whole-server allowlist) | unchanged | The OpenAPI MCP exposes a small schema-traversal tool set, all relevant to API design. Whole-server allowlist is appropriate (C-0450). |
| 2 | `design-cicd.md` | `mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows` | unchanged | actionlint-mcp exposes exactly two tools (C-0144). Narrow per-tool is the canonical form; whole-server adds no value here. |
| 3 | `design-iac.md` | `mcp__terraform-mcp__*` (whole-server allowlist) | unchanged | Terraform MCP exposes a Terraform-reasoning tool set, all relevant to IaC design (C-0452). |
| 4 | `discovery-external-researcher.md` | `mcp__context7__resolve-library-id`, `mcp__context7__query-docs`, `mcp__exa__web_search_exa`, `mcp__exa__company_research_exa`, `mcp__exa__crawling_exa` | unchanged | Five explicit tool ids. Whole-server would expose Context7's experimental tools and Exa's full surface; narrow is the right discipline for an external-research agent (C-0453/C-0454). Context7 v3.0.0 two-tool surface (`resolve-library-id` + `query-docs`) is stable across v1→v3 per T-005 v3.0.0 cycle-3 D-3.2-completion (WebFetch-verified by orchestrator); the prior `ReplaceContentTool`/`ReplaceRegexTool` v1.2.0 rename narrative under C-0037 was debunked (v1.2.0 never existed; `ReplaceContentTool` was a Serena-CHANGELOG contamination). |
| 5 | `discovery-codebase-researcher.md` | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*` (whole-server allowlists for primary + fallback) | unchanged (model=opus, effort=high, memory=project, skills=[KB-codebase-research]) | GitNexus is primary, codebase-memory-mcp is fallback per ADR-0018 / ADR-0007 v2.2.0. The primary/fallback **expression** is the UI-15 question — see the dedicated subsection below. |
| 6 | `review-architecture-auditor.md` | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*` | unchanged | Same primary/fallback pair as #5, per ADR-0018 / ADR-0007 v2.2.0 / C-0447. Used during blast-radius analysis. |
| 7 | **TBD per D-13 narrowing** (the Python-touching agents — likely subset of: `review-architecture-auditor` already in row 6, and any audit-script-touching design agent). The exact list depends on Composer's review of which agents read or modify `.claude/skills/auditing-*/scripts/` Python files. | `mcp__serena__*` | unchanged | D-13 narrows Serena to the symbol-rich surface (52 Python audit scripts; 73.8% markdown corpus elsewhere). Whole-server allowlist on the narrow set, not on all 36 agents. **The exact agent list is surfaced as Q-CC-3.** |

The other 29 agents are NOT touched. This is the C-0445 grep-verified zero-`mcp__` invariant preserved for least-privilege.

### UI-15 primary/fallback expression on `discovery-codebase-researcher`

Codebase-analysis confirmed that the primary/fallback policy lives entirely as **prose** today, in four corpus layers:
1. ADR-0007 v2.2.0 (in `adrs-migrated/`): the canonical decision.
2. ADR-0018: four prose references pointing to ADR-0007.
3. `KB-codebase-research/SKILL.md`: dedicated body section ("Use codebase-memory-mcp as fallback") + description.
4. `discovery-codebase-researcher.md`: four prose statements (description + body lines 20, 29, 156). Nothing structured. No frontmatter field. The agent's `tools:` allowlist currently contains zero `mcp__` entries (the whole feature is the introduction of that pattern).

The substrate map enumerated four UI-15 options; D-5 recommended **`combined_jsonl_plus_stderr_banner`** which addresses the *transition surfacing*. The *primary/fallback declaration* itself (how the agent file expresses which server is primary and which is fallback) is a related but distinct sub-question. The design here picks:

- **Both servers appear in the `tools:` allowlist** — `mcp__gitnexus__*` and `mcp__codebase-memory-mcp__*` listed side-by-side. This is the minimum mechanism that makes both callable; without both being in the allowlist, the fallback cannot be exercised.
- **The primary/fallback semantics remain prose** — in the existing four corpus layers, untouched. **No new structured frontmatter field is introduced.** The codebase-analysis primary-fallback-wiring evidence shows that introducing a structured `mcp_primary:` / `mcp_fallback:` agent-file frontmatter field would be a NEW convention with no exemplars (zero precedent). Introducing a 36-agent-wide convention to address one agent's needs violates KB-cc-design Principle 4 ("Subagent isolation pays for itself" — generalized: don't invent a convention until two cases need it).
- **The transition itself is surfaced via `mcp-events.jsonl`** — the `primary_degraded` event records every primary→fallback transition. This is the machine-readable contract that addresses AC-FR-9-d. The stderr banner is the ephemeral operator-visible companion (D-5).
- **Auditability**: the augmented `auditing-mcp` adds a rule that **for any agent whose `tools:` allowlist contains both `mcp__gitnexus__*` and `mcp__codebase-memory-mcp__*`**, the agent body MUST contain prose naming the primary/fallback relationship (regex-matchable). This converts the prose convention into a machine-checkable invariant without inventing a structured field. **The rule itself is part of the auditing-mcp augmentation** — see UI-14 / Q-CC-4.

This choice is conservative: it adds zero new convention surface. The cost is that the primary/fallback semantics remain expressed in prose, requiring the audit-rule to enforce. The benefit is that no other agent file needs to learn a new frontmatter field, and the existing four-corpus-layer expression is the source of truth.

Surfaced as **Q-CC-5** for design-composer in case Composer prefers to introduce the structured frontmatter field instead.

## Hook patterns

**No hooks are introduced by this feature.** Per KB-cc-design Principle 3 ("hooks are deterministic guarantees, not non-deterministic guidance"):

- The MCP health-check (FR-8) is a **lifecycle-script** (postCreate / postStart), owned by `design-codespaces`. It is not a Claude Code hook in the `.claude/settings.json` `hooks:` sense — it fires on devcontainer lifecycle events, not on tool-use events.
- The redaction-at-source filter (D-7) is a **wrapper at the log-surface boundary**, owned by `design-codespaces`' postStart script. It is not a PreToolUse hook because the events being redacted come from MCP server stderr, not from Claude Code tool invocations.
- A PreToolUse hook to block argv-leaked-secret invocations (E-0094) was considered. **Rejected** because the project's `.mcp.json` will commit only to env-var-via-`env:` block invocations (D-7); the argv-leakage anti-pattern is structurally prevented at the config layer, not at the runtime layer. A hook to enforce "no `--api-key` flags in commands" would be redundant against the augmented `auditing-mcp`'s static-config check.
- A PostToolUse hook to append every tool call to `mcp-events.jsonl` was considered. **Rejected** because `mcp-events.jsonl` is reserved for **coarse events** (transitions, probes, structured failures), not per-line tool-call logs (D-6 explicit). Adding every tool call would defeat the design.

If a future feature wants enforced operator-side guarantees (e.g., "block any commit that introduces a literal API key into `.mcp.json`"), a PreToolUse Bash-grep hook would be the right primitive — but not warranted here.

## Permission policy

This feature does NOT introduce changes to `.claude/settings.json`'s `permissions` block. Reasoning:

- The 36 agents already have their own `tools:` allowlists which act as the per-agent permission surface. The seven-server feature works **only through those allowlists** — there is no global "allow MCP" or "deny MCP" at the settings level.
- The synthesis does not recommend a `permissions.deny` entry for MCP. The argv-leakage and URL-embedded-credential anti-patterns are blocked at the `.mcp.json` validation step (D-7), not at the permission-block step.
- A `permissions.deny: ["Bash(curl https://mcp.context7.com:*)"]` rule could be added to prevent operators from bypassing the MCP config and calling Context7 directly via curl — but the synthesis frames this as out of scope (the MCP servers ARE the canonical surface). If a future security review wants this, it's an additive change.

The augmented `auditing-mcp` is the safety-net for the permission concerns (toxic capability combinations, broad allowlists, missing env-var coverage). Per KB-cc-design Principle 6 ("permissions are a safety net"), the augmented audit is the safety-net for **configuration-level** issues; the runtime-event surface (`mcp-events.jsonl` + stderr banner) is the safety-net for **runtime-level** issues.

## MCP server policy

The seven-server inventory is fixed at PRD scope (closed list per Product Policy). The MCP scope is **project**: registrations in `.mcp.json` at repo root, loaded every Claude Code session in this repo. Per KB-cc-design Principle 5 (one source of truth):

- `.mcp.json` is the only place server commands, transports, env-var references, and HTTP headers are declared. Sub-agents' `tools:` allowlists name registered servers but do not duplicate their configuration.
- The `env:` block per server lists every env var the server consumes. This list is the **redaction allowlist** (D-7). Adding a new credential = adding to the `env:` block = automatically covered by redaction. Removing from `env:` without removing from the upstream secret store leaves an orphan credential — the augmented `auditing-mcp` checks for this.

**User-scoped MCP servers** are explicitly NOT introduced. Per Product Policy Q4: "All seven always-on" at project scope. User-scope would defeat reproducibility (operators on different machines would see different servers).

**Managed-scope MCP servers** are NOT applicable. This is not an enterprise-managed Claude Code deployment.

## Plugin packaging

**No plugin is introduced by this feature.** Per KB-cc-design Principle 7 ("plugins for cross-project distribution, not within-project organization"):

- The three artifacts (`.mcp.json`, the trifecta skills, the agent allowlist edits) live in **this one project**. They are not authored for cross-project share.
- A future plugin could bundle the trifecta skills (`KB-mcp-platform` + `KB-mcp-design` + `auditing-mcp`) for distribution to sister projects that adopt MCP. **Surfaced as Q-CC-7** for Composer — but this is explicitly future-work, not this feature.

If Composer judges the trifecta should be plugin-published preemptively, that's an additive design that does not change any of the artifacts above.

## Command-to-skill migration

**No commands are migrated** by this feature. The project has no `.claude/commands/*.md` files relevant to MCP today (codebase-analysis grep returned nothing — the project uses skills exclusively). Per KB-cc-design Principle 8, the new MCP knowledge goes into skills from the start, not commands.

## `mcp-events.jsonl` schema (UI-15 contract)

Per synthesis D-5 (`combined_jsonl_plus_stderr_banner` — the load-bearing one-way design call addressing F5.4 NO CONSENSUS). The CC layer **defines the schema**; design-codespaces' postStart script and any in-product fallback-detection code-site **write to it**.

**File location:** `.claude/runtime/mcp-events.jsonl`

**Format:** JSON Lines (one JSON record per line, append-only).

**Common fields (every record):**

| Field | Type | Required | Description |
|---|---|---|---|
| `ts` | string (ISO 8601 UTC, e.g. `2026-05-23T14:30:11.234Z`) | yes | Wall-clock timestamp of the event |
| `event` | string enum | yes | One of `primary_degraded`, `readiness_probe`, `structured_failure` |
| `server` | string | yes | The server name as registered in `.mcp.json` `mcpServers` key (e.g. `gitnexus`, `context7`) |
| `agent` | string | optional | The `.claude/agents/<name>.md` agent that triggered the event (when known). Omitted for lifecycle-phase events (e.g., a postStart readiness probe is not agent-scoped) |
| `extraction_method` | string | optional | For `primary_degraded` events: which detection path triggered (`transport_error`, `tool_error_response`, `manual_operator_invocation`). Reused from the existing `codebase-analysis.json` schema field name (per ADR-0018 / KB-codebase-research) for terminology consistency |

**Event-specific fields:**

**`primary_degraded`** — primary→fallback transition (the UI-15 contract):

| Field | Type | Required | Description |
|---|---|---|---|
| `primary_server` | string | yes | The intended primary that failed (e.g. `gitnexus`) |
| `fallback_server` | string | yes | The fallback being invoked (e.g. `codebase-memory-mcp`) |
| `reason` | string | yes | Human-readable failure reason; redacted per D-7 |

**`readiness_probe`** — output of the postStart probe (FR-8 lifecycle health check):

| Field | Type | Required | Description |
|---|---|---|---|
| `probe_method` | string enum | yes | `json_rpc_ping` (D-8 canonical) or `auth_probe` (the Context7/Exa supplementary probe, gated on env flag) |
| `latency_ms` | integer | yes | Probe round-trip latency in ms |
| `result` | string enum | yes | `pass`, `fail`, `timeout` |
| `failure_layer` | string | optional (only when `result=fail` or `timeout`) | One of `install`, `registration`, `transport`, `auth`, `probe`. Matches FR-9 / AC-FR-9-a naming |

**`structured_failure`** — FR-9 mid-run failure record:

| Field | Type | Required | Description |
|---|---|---|---|
| `failure_class` | string enum | yes | `transport`, `auth`, `tool_error`, `handshake`, `process_start` |
| `tool_name` | string | optional (only when `failure_class=tool_error`) | The MCP tool that returned the error (per AC-FR-9-b) |
| `message_redacted` | string | yes | The error message, with credential values replaced by `[REDACTED:<envvar-name>]` per D-7 |
| `remediation_pointer` | string | optional | URL or skill-relative path into `KB-mcp-platform` troubleshooting section (per AC-FR-8-d / AC-FR-9-a) |

**Example records (illustrative):**

```jsonl
{"ts":"2026-05-23T14:30:11.234Z","event":"readiness_probe","server":"gitnexus","probe_method":"json_rpc_ping","latency_ms":42,"result":"pass"}
{"ts":"2026-05-23T14:30:11.301Z","event":"readiness_probe","server":"exa","probe_method":"json_rpc_ping","latency_ms":189,"result":"pass"}
{"ts":"2026-05-23T15:12:44.812Z","event":"primary_degraded","server":"gitnexus","agent":"discovery-codebase-researcher","primary_server":"gitnexus","fallback_server":"codebase-memory-mcp","reason":"stdio process exited with code 1; not auto-reconnected","extraction_method":"transport_error"}
{"ts":"2026-05-23T15:12:44.812Z","event":"structured_failure","server":"gitnexus","agent":"discovery-codebase-researcher","failure_class":"transport","message_redacted":"connection refused","remediation_pointer":"KB-mcp-platform/references/lifecycle-hooks.md#stdio-not-auto-reconnected"}
```

**What the file is NOT:**

- NOT a per-line log mirror (D-6 explicit — stderr is the per-line log; jsonl is reserved for coarse events).
- NOT a metrics surface (NFR-1: log overhead must stay negligible; NFR-8: no remote sink, no alerting).
- NOT git-tracked. The file is operator-runtime state. Composer decides whether `.claude/runtime/` is gitignored or whether the directory carries a `.gitkeep` with the file gitignored — surfaced as **Q-CC-2**.

**Schema location:** This contract lives in **`KB-mcp-design/references/principles.md`** (per synthesis §9.1 specific work item 6). Composer's ADR for UI-15 (synthesis §7 risk 1) may also link to or pull from this contract.

## `KB-mcp-platform` authoring outline

Following KB-cc-platform template verbatim per D-10 / constraint #12.

### SKILL.md frontmatter

```yaml
---
name: kb-mcp-platform
description: |
  Platform knowledge for MCP (Model Context Protocol) servers as deployed in this
  project's devcontainer. Covers the seven named servers (Serena, mcp-openapi-schema,
  actionlint-mcp, HashiCorp Terraform MCP, GitNexus, Context7, Exa) plus the
  ADR-0018 codebase-memory-mcp fallback. Documents transports, install paths,
  credential surfaces, lifecycle integration, the .mcp.json env-block redaction
  allowlist contract, and the .claude/runtime/mcp-events.jsonl event schema.
  Pairs with KB-mcp-design.
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch
pedagogical_sections:
  - path: references/auth-and-redaction.md
    justification: "Names anti-patterns (argv-leaked secrets E-0094; URL-embedded credentials E-0095) that the auditor would otherwise flag as anti-pattern occurrences"
  - path: references/lifecycle-hooks.md
    justification: "Names false-positive 'healthy' patterns and stdio-no-reconnect failure modes used as negative examples"
---
```

### Body structure (router + sections)

Following KB-cc-platform's body shape:

- When this KB is loaded
- Mental model in 90 seconds (MCP transports stdio vs HTTP; how `.mcp.json` is consumed; redaction-at-source from `env:`)
- Decision matrix: pick the right transport / install path per server (the per-server matrix from synthesis §4)
- How to verify current details (per-server upstream check chain)
- Inspect a running session (the `claude mcp list` / `mcp-events.jsonl tail` workflow)
- When to load each reference file
- Templates (`assets/templates/.mcp.json.example`)
- Operating principles (precedence, redaction, stdio-not-reconnected, etc.)

### `references/` outline

Per synthesis §9.1 specific work item 3 (final filenames pinned at authoring time; substantively the seven topics below):

| File | Topic | Source claims |
|---|---|---|
| `transports.md` | stdio vs remote HTTP; vendor-canonical choice per server; Claude Code's reconnect behavior per transport | D-2, C-0301, C-0300, C-0302 |
| `install-mechanisms.md` | Per-server install paths (uvx / npx / go install / wget+verify / no-install) under base-image constraints (no Go, no DinD, no Node-without-feature) | D-1, D-3, T-001 through T-008 |
| `auth-and-redaction.md` | Credential flow (Codespaces secret → containerEnv → `${VAR}` → `.mcp.json env:` block); redaction-allowlist contract (D-7); argv-leakage anti-pattern (E-0094); URL-embedded-credential anti-pattern (E-0095); OWASP MCP01 | D-7, C-0333, C-0335, E-0094, E-0095, C-0330 |
| `lifecycle-hooks.md` | postCreate install, postStart probe, postAttach read; ping (D-8); the false-positive-healthy anti-pattern; the stdio-no-reconnect ground truth and what it means for FR-9 | D-4, D-8, C-0290, C-0291, C-0301 |
| `version-pinning.md` | Per-server pin form table (D-11); pin-then-review discipline; vendor-controlled vs operator-controlled pins; verify-at-execution caveats for time-sensitive pins | D-11, C-0040, C-0073, C-0133, C-0158, E-0073, E-0074 |
| `mcp-events-jsonl.md` | The full schema for `.claude/runtime/mcp-events.jsonl` (the table in this design subsection is the seed); event-shape rationale per D-5; example records; consumer expectations (postStart writer, operator-tail reader) | D-5, D-6 |
| `gitnexus-and-fallback.md` | GitNexus + codebase-memory-mcp specifics: primary/fallback per ADR-0007 v2.2.0 / ADR-0018; `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` rationale (C-0388/C-0411 smoke-test required); how the fallback is exercised; how the transition surfaces (the UI-15 contract) | ADR-0007 v2.2.0, ADR-0018, D-5, C-0388, C-0411 |

### `assets/templates/`

| Template | Purpose |
|---|---|
| `.mcp.json.example` | The canonical 7-server template (the sketch above, fully populated and commented). Operators copy this when adding an MCP server. **Note:** This is intentionally distinct from `KB-cc-platform/assets/templates/mcp-config.json.example`, which documents the *generic* `.mcp.json` shape (single example server). KB-mcp-platform's template is the *project-specific* seven-server shape with the redaction-allowlist invariant explicit. Cross-reference both. Resolves the codebase-analysis "Q-5" (the open question about duplication vs cross-reference) by deliberate split-of-concern, not duplication: KB-cc-platform owns the **schema**; KB-mcp-platform owns the **project template**. |
| `mcp-events-record.example.jsonl` | Three example records (one per event type), illustrating the schema |

## `KB-mcp-design` authoring outline

Following KB-cc-design template verbatim per D-10 / constraint #12. Slim by convention.

### SKILL.md frontmatter

```yaml
---
name: kb-mcp-design
description: |
  Design discipline for MCP (Model Context Protocol) integration in this project.
  Covers when to choose stdio vs remote HTTP, how to express primary/fallback
  relationships in agent allowlists, the redact-at-source-from-.mcp.json-env-block
  invariant, and the structural patterns that keep an MCP fleet operable across
  Codespace lifecycle boundaries. Pairs with KB-mcp-platform.
allowed-tools: Read, Grep, Glob
pedagogical_sections:
  - path: references/patterns-and-anti-patterns.md
    justification: "Names anti-patterns the auditor would otherwise flag (argv-leaked secrets, URL-embedded credentials, broad-wildcard tool allowlists, ToolHive-style proxy supervisors, single-postStart-conflation of install and readiness, agent-level acknowledgement convention)"
---
```

### Body structure

Following KB-cc-design's body shape exactly:

- When this KB is loaded
- The layer's responsibility (MCP-scoped — not the broader CC layer)
- Design decisions this layer owns (transport choice, install path, primary/fallback expression, redaction code-site, lifecycle-hook placement)
- Patterns and anti-patterns at a glance (the lift-from-synthesis summary)
- Interaction with other layers (Codespaces for install + secrets; CC for `.mcp.json` + agent allowlists; CI/CD out of scope this feature)
- Surfacing architectural questions (template — refers Composer for ADR work)
- When to load each reference file

### `references/` — exactly two files (D-10 verbatim)

| File | Content |
|---|---|
| `principles.md` | Core principles: (1) redact-at-source — `.mcp.json` `env:` block is the SSOT (D-7); (2) ping is the canonical health-check (D-8, C-0290); (3) stdio is not auto-reconnected — failures need operator-visible surfaces (C-0301, FR-9); (4) postCreate-install / postStart-probe separation (D-4); (5) `.claude/runtime/mcp-events.jsonl` is for coarse events, not per-line logs (D-6); (6) every primary/fallback transition is operator-visible (D-5, AC-FR-9-d); (7) least-privilege per agent — preserve zero-`mcp__` for non-consumers (D-9). Includes the **full mcp-events.jsonl schema** (the table above is the canonical home; the schema lives here per synthesis §9.1) |
| `patterns-and-anti-patterns.md` | Anti-patterns: argv-leaked secrets (E-0094); URL-embedded credentials in HTTP transport (E-0095); broad-wildcard tool allowlists (`mcp__*`); ToolHive-style supervisor proxy (D-6 rejected); single-postStart-conflation of install and readiness (D-4 rejected); agent-level free-text acknowledgement convention for transitions (D-5 rejected — uniformity risk); structured-frontmatter-field invention for primary/fallback before two cases exist. Patterns: per-server vendor-canonical transport (D-2); narrow per-agent allowlist (D-9); pin-then-review (D-11) |

### No `assets/`, no `scripts/`

Per the strong design-half convention (C-0479; KB-cc-design, KB-codespaces-design, KB-github-actions-design all carry no assets).

## `auditing-mcp` augmentation plan

Per FR-11-c, UI-14, and synthesis §9.1 specific work item 5. The augmentation is in-place: existing files extended, new files added under the existing `references/` and `scripts/` subdirectories.

### Sister-cross-reference update

The existing `auditing-mcp/SKILL.md` description names sister halves that didn't exist. Update the description to:

> "Audits Claude Code MCP (Model Context Protocol) server configurations and operational state. Pairs with KB-mcp-platform (What) and KB-mcp-design (How)."

### Family-membership statement

Currently at line 30 of `auditing-mcp/SKILL.md`: "This skill is part of the auditing-cc-configs family. Shared rubric, weights, thresholds, and triage live in the coordinator skill."

**The family-membership wording depends on the D-10 resolution.** Path A (graduate to own family with KB-mcp-* as sisters) means changing this line. Path B (stay in auditing-cc-configs family with KB-mcp-* as sibling knowledge skills) means leaving this line and adding a sentence: "Cross-references KB-mcp-platform and KB-mcp-design for the design / platform halves of the MCP knowledge surface; these are sibling knowledge skills in the auditing-cc-configs family rather than sister halves." **Surfaced as Q-CC-1** for Composer.

### New rule families to add

The existing skill has 10 dimensions and a BLOCKER/MAJOR/MINOR/NIT severity taxonomy. The augmentation adds rules across the operational-health surface plus GitNexus-specific rules. Whether these expand the existing dimensions or introduce an 11th dimension is **Q-CC-4** for Composer (the codebase-analysis "Q-4" surfaces this directly: the existing skill is framed as "config" audit; FR-11-c stretches it to "config + runtime").

**Rule families (regardless of how dimensions are organized):**

| # | Rule family | Purpose | New files / scripts | Severity per rule |
|---|---|---|---|---|
| OP-1 | **`.mcp.json` env-block coverage** | Every credential env var referenced in any `${VAR}` substitution in `.mcp.json` (including HTTP `headers:` values) MUST appear in the per-server `env:` block (when stdio) or be a documented header name (when http). This is the redaction-allowlist completeness check (D-7). | New: `scripts/check_env_block_coverage.py`. Updated: `references/anti-patterns.md` with the env-coverage anti-pattern. | BLOCKER |
| OP-2 | **Tool-allowlist consumer-mapping validation** | For each agent's `tools:` allowlist `mcp__<server>__*` entry, the server MUST exist in `.mcp.json`. For each agent listed in the canonical consumer-mapping table (the table in this design subsection), the agent's `tools:` MUST include the prescribed entries. Catches "the seven-of-36 mapping drifted." | New: `scripts/check_agent_consumer_mapping.py`. Updated: `references/anti-patterns.md`. | BLOCKER (missing consumer entry) or MAJOR (extraneous entry) |
| OP-3 | **Zero-`mcp__` preservation for non-consumer agents** | The 29 agents NOT in the consumer-mapping table MUST have zero `mcp__` entries. Catches "wildcard scope creep." | Same script as OP-2 (`check_agent_consumer_mapping.py`). | BLOCKER |
| OP-4 | **Primary/fallback prose presence (UI-15)** | For any agent whose `tools:` contains both `mcp__gitnexus__*` and `mcp__codebase-memory-mcp__*`, the agent body MUST contain prose matching `/primary.*fallback/` semantics naming both servers (this is the rule that makes the prose-only convention machine-checkable, per UI-15 design above). | New: `scripts/check_primary_fallback_prose.py`. Updated: `references/anti-patterns.md`. | MAJOR |
| OP-5 | **Lifecycle health-check completeness** | The devcontainer.json's `postStartCommand` (and the postStart script it points at) MUST cover all seven servers' readiness probes and MUST write results to `.claude/runtime/mcp-events.jsonl`. This is a cross-layer check (auditing-mcp reads devcontainer.json) and overlaps with auditing-codespaces' purview — but auditing-codespaces is a STUB per ADR-0033, so auditing-mcp owns this rule until that stub is filled. | New: `scripts/check_lifecycle_completeness.py`. Updated: `references/common-failures.md`. | MAJOR (missing server) or MINOR (other gaps) |
| OP-6 | **Runtime log redaction integrity** | The redaction filter applied at the log-surface boundary (wherever Composer places that code-site) MUST use the `.mcp.json` `env:` block + HTTP-header names as its allowlist. A non-matching credential in `mcp-events.jsonl` (e.g., a literal API key) is a BLOCKER. | New: `scripts/scan_mcp_events_for_secrets.py` (greps `mcp-events.jsonl` against credential shapes — reuses `auditing-mcp/scripts/scan_mcp_secrets.py` logic). | BLOCKER |
| OP-7 | **Trifecta consistency (W/H/A)** | Every server in `.mcp.json` MUST be named in `KB-mcp-platform`. Every server in `.mcp.json` SHOULD be addressed in `KB-mcp-design` patterns. The two skills MUST cross-reference each other. The audit skill MUST cross-reference both. | New: `scripts/check_trifecta_consistency.py`. Updated: `references/anti-patterns.md` with the drift anti-pattern (synthesis §7 risk: trifecta drift). | MAJOR (server unnamed in KB) or MINOR (cross-reference missing) |
| OP-8 | **GitNexus-specific rules** (per UI-14 augmentation extension to GitNexus) | (a) GitNexus is registered in `.mcp.json` with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` in its `env:` block; (b) GitNexus + codebase-memory-mcp pair appears in exactly the discovery-codebase-researcher.md and review-architecture-auditor.md `tools:` allowlists per ADR-0018; (c) `KB-mcp-platform/references/gitnexus-and-fallback.md` exists and names both servers; (d) ADR-0018 cross-reference is current. | New: `scripts/check_gitnexus_wiring.py`. Updated: `references/anti-patterns.md` with GitNexus-specific anti-patterns. | MAJOR (config gap) or BLOCKER (security/correctness) |
| OP-9 | **Exa URL-credential rejection (D-7 invariant)** | `.mcp.json`'s Exa entry MUST NOT use the `exaApiKey` URL-query-param form (E-0095). The `x-api-key` header form is the only accepted shape. | New rule in existing `scripts/validate_mcp_config.py`. Updated: `references/anti-patterns.md`. | BLOCKER |
| OP-10 | **Argv-leakage absence (D-7 invariant)** | `.mcp.json`'s `args:` arrays MUST NOT contain literal credential values or `--<flag>=<credential>` patterns. Credentials flow only via `env:` block. (Context7 `--api-key` CLI flag form per C-0205 is rejected.) | New rule in existing `scripts/scan_mcp_secrets.py`. Updated: `references/anti-patterns.md`. | BLOCKER |

### Scripts added vs reused

The existing `auditing-mcp/scripts/` contains 4 files: `audit_mcp.py` (entry point), `check_toxic_combinations.py`, `scan_mcp_secrets.py`, `validate_mcp_config.py`. The augmentation adds 6 new scripts and extends 2 existing scripts. The entry-point `audit_mcp.py` dispatches to all rule families and aggregates verdicts per the existing BLOCKER/MAJOR/MINOR/NIT taxonomy.

### `--with-runtime` flag

The existing skill already supports a `--with-runtime` flag (per codebase-analysis "audit dimensions" notes). The augmentation extends `--with-runtime` to include OP-5 (lifecycle completeness — reads the **most recent** `mcp-events.jsonl` line per server to confirm postStart ran), OP-6 (runtime-log redaction — scans `mcp-events.jsonl` for credential shapes), and OP-8(b) (the GitNexus + codebase-memory-mcp `mcp-events.jsonl` presence check). Without `--with-runtime`, these rules are skipped (the audit is static-only).

## Acceptance criteria contribution

EARS-form ACs the CC layer contributes (these reduce to and refine the PRD's AC-FR-* / AC-NFR-* clauses).

- **AC-CC-1**: When the operator runs `claude mcp list` after `postCreate` completes on a fresh build, the system shall list exactly the seven named servers (`serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`, `context7`, `exa`) plus `codebase-memory-mcp` (the ADR-0018 fallback) as connected. *Reduces:* AC-FR-1-a, AC-FR-2-b. (Note: the eighth registered server is the documented fallback, not an additional named server — see Q-CC-6.)
- **AC-CC-2**: When the operator inspects each of the 7 affected `.claude/agents/*.md` files, the system shall show the prescribed `mcp__<server>__<tool>` entries (per the consumer-mapping table in this design) and no others. *Reduces:* AC-FR-2-a.
- **AC-CC-3**: When the operator inspects the 29 non-consumer `.claude/agents/*.md` files, the system shall show zero `mcp__` entries (preserves the C-0445 invariant). *Reduces:* none directly — this is an invariant the audit upholds (OP-3).
- **AC-CC-4**: When `git grep` is run over the repo, the system shall not surface any literal credential value matching the credential-shape patterns in `.mcp.json`, `.claude/agents/*.md`, `.devcontainer/*`, or `.claude/runtime/mcp-events.jsonl`. *Reduces:* AC-NFR-2-a.
- **AC-CC-5**: When the augmented `auditing-mcp` skill (with the rule families OP-1 through OP-10) is run against the repo after Gate 6, the system shall report zero BLOCKER findings. *Reduces:* AC-NFR-2-c, AC-FR-11-c.
- **AC-CC-6**: When the operator opens `.claude/runtime/mcp-events.jsonl` after a postStart cycle, the system shall contain seven `readiness_probe` records (one per server) with `result: pass` (or `fail`+`failure_layer` if a server is unhealthy). *Reduces:* AC-FR-8-a.
- **AC-CC-7**: When a primary→fallback transition occurs at runtime (GitNexus → codebase-memory-mcp), the system shall append a `primary_degraded` record to `.claude/runtime/mcp-events.jsonl` AND surface a stderr banner; the operator shall be able to read both. *Reduces:* AC-FR-9-c, AC-FR-9-d.
- **AC-CC-8**: After this feature ships, the system shall contain a `.claude/skills/KB-mcp-platform/SKILL.md` and a `.claude/skills/KB-mcp-design/SKILL.md` conforming to the trifecta structural conventions (name field lowercase-hyphenated; `description` ends with sister-cross-reference; design half carries exactly two reference files named `patterns-and-anti-patterns.md` and `principles.md` with no `assets/`). *Reduces:* AC-FR-11-a, AC-FR-11-b, AC-FR-11-d.
- **AC-CC-9**: When the operator reads `KB-mcp-platform/references/gitnexus-and-fallback.md`, the system shall name both GitNexus and codebase-memory-mcp, cite ADR-0018 / ADR-0007 v2.2.0, and link to the `mcp-events.jsonl` `primary_degraded` schema in `KB-mcp-design/references/principles.md`. *Reduces:* AC-FR-11-d (sub-clause: both skills name GitNexus among the covered servers).

## Dependencies on other layers

**Provides to:**

- **Dev Environment / Codespaces (`design-codespaces`)**: the `.mcp.json` `env:` block enumeration (the redaction allowlist that the postStart wrapper consumes); the `mcp-events.jsonl` schema (the file the postStart probe writes to); the list of env-var names needed in `containerEnv`.
- **Composer (`design-composer`)**: the Q-CC-N open items for ADR authorship and family-coordinator resolution; the consumer-mapping table for cross-layer reconciliation; the `mcp-events.jsonl` schema for ADR-UI-15 reference.
- **CI/CD**: out of scope this feature per PRD; no provides_to today. If a future feature adds a CI smoke-test for `.mcp.json` drift (Won't-Have in this release), the augmented `auditing-mcp` is the natural script to invoke.

**Depends on:**

- **Dev Environment / Codespaces**: the devcontainer.json `containerEnv` block must export `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` (and any GitNexus credential per UI-16, currently believed to be none); the postCreate script must install the five OSS-local servers' binaries; the postStart script must run the JSON-RPC ping probe per D-8 and write `readiness_probe` records to `mcp-events.jsonl`.
- **Composer**: ADR-0018 bump to v1.1.0 (D-12; ADR-0018 schema-version drift); the UI-15 ADR (D-5; the jsonl event-shape is a natural new field for the v1.1.0 schema); the credential-redaction ADR (D-7); the Serena UI-8 narrowing ADR (D-13); the install-mechanism ADR (D-1, if Composer judges threshold).
- **External MCP servers**: the seven upstream MCP server projects. Pin discipline per D-11; verify-at-execution caveats per synthesis §7 (actionlint-mcp release status, Terraform MCP latest, mcp-openapi-schema staleness, GitNexus skip-grammars smoke-test).

**No dependency on:**

- Frontend, Backend, API, Query, Database, IaC layers — none of these are in scope for this feature.

## Architectural Questions for Composer (Q-CC-N)

- **Q-CC-1: Family-coordinator resolution for `auditing-mcp` and the new KB-mcp-* halves.** Per D-10, two paths exist:
  - **Path A**: Graduate `auditing-mcp` to its own family with `KB-mcp-platform` + `KB-mcp-design` as sister halves. Each of the three skills declares "This skill is part of the MCP family" in body prose. The currently-declared `auditing-cc-configs` family membership is broken at the `auditing-mcp/SKILL.md` line 30 statement.
  - **Path B**: Keep `auditing-mcp` in the `auditing-cc-configs` family (current state). `KB-mcp-platform` + `KB-mcp-design` are sibling knowledge skills cross-referenced from `auditing-mcp` but not sister halves in the family sense.
  - **Evidence:** Three existing trifectas show inconsistent treatment: Claude Code (auditing-cc-configs is the family coordinator for sub-families including auditing-mcp); Codespaces (auditing-codespaces is a stub, family treatment moot); GitHub Actions (auditing-github-actions consumes auditing-shared per ADR-0031).
  - **Recommended:** Path B if Composer wants minimum convention change; Path A if Composer wants the MCP trifecta to mirror Claude Code's / Codespaces' / GitHub Actions' shape. The synthesizer explicitly declined to choose (D-10 human decision point).
  - **Defer to Composer.**

- **Q-CC-2: `.claude/runtime/` git-status.** The `mcp-events.jsonl` file is runtime state. Options: (a) gitignore the file but commit `.claude/runtime/.gitkeep`; (b) gitignore the whole `.claude/runtime/` directory and have postCreate create it; (c) commit a fresh-empty `mcp-events.jsonl` with `.gitignore` covering only its content. Has knock-on effects for any future runtime file in `.claude/runtime/`. **Recommended:** (a) — operators see the directory exists, jsonl never enters git. Defer to Composer for the .gitignore patterns.

- **Q-CC-3: Exact agent list for D-13 Serena narrowing.** The synthesis names "Python-touching agents" as the Serena-narrowed surface, citing review-architecture-auditor + the design agents that touch tooling Python. Which design agents specifically? Candidates: `design-cc` (this layer's owner — may touch `.claude/skills/auditing-*/scripts/`), `design-backend` (may touch Python services in target codebases), the audit-script authors per `auditing-mcp/scripts/` (no agent owns this directly today). The codebase-analysis "Q-3" raises the parallel question of whether deprecated `synth-*` agents should get any wiring. **Recommended:** Compose with the user the exact 6-or-so-agent Serena recipient list before plan-author finalizes the per-agent edits.

- **Q-CC-4: `auditing-mcp` rule-family organization — dimension expansion vs new dimension.** The existing skill has 10 dimensions. The 10 new rule families OP-1 through OP-10 above fit naturally in existing dimensions (toxic combinations, credential handling, supply-chain, runtime-behavior). But OP-5 (lifecycle completeness) and OP-6 (runtime log redaction) stretch the audit from "config" to "config + runtime." Options: (a) expand existing dimensions; (b) introduce an 11th "operational health" dimension; (c) introduce a new sibling skill (`auditing-mcp-runtime`) — the codebase-analysis "Q-4" surfaced this directly. **Recommended:** (a) — keeps one source of truth (KB-cc-design Principle 5). Option (c) would split the maintainer interface (US-9). Defer to Composer.

- **Q-CC-5: Primary/fallback expression on `discovery-codebase-researcher` — prose-only vs structured frontmatter.** This design chose prose-only with an audit-rule making it machine-checkable. The alternative is to introduce structured frontmatter fields (e.g., `mcp_primary: gitnexus`, `mcp_fallback: codebase-memory-mcp`) which would be a NEW agent-file convention with zero precedent. **Recommended:** prose-only as designed; defer to Composer if Composer's review judges the audit-rule insufficient. The UI-15 ADR (Composer-authored) is the right place to record this convention choice.

- **Q-CC-6: `codebase-memory-mcp` inventory status.** The PRD names "seven servers" closed list. `codebase-memory-mcp` is the documented ADR-0018 fallback but is not in that count. This design includes it in `.mcp.json` (without it, the fallback cannot be exercised). Two interpretations: (a) the PRD's seven-server closed-list refers to **primary** servers; the fallback is implicit and not an eighth primary; (b) the PRD undercounts and should be updated to enumerate eight. **Recommended:** (a) — the PRD's Glossary at line 612 names `codebase-memory-mcp` as the fallback throughout, distinct from the seven; .mcp.json carries 8 mcpServers entries but the PRD's count is correct. Defer to Composer for confirmation; either way the design is unchanged.

- **Q-CC-7: Plugin packaging for future cross-project distribution.** Should the trifecta (`KB-mcp-platform` + `KB-mcp-design` + `auditing-mcp`) be plugin-published preemptively, so a sister project adopting MCP can install with one command? Per KB-cc-design Principle 7 ("plugins for cross-project distribution"), this is the canonical use case for plugins. **Recommended:** defer to a follow-up feature; not authored in this feature. The artifacts are designed to be plugin-compatible by following the trifecta conventions.

- **Q-CC-8: ADR authorship list (per FR-5 of recipe-feature-pipeline, Composer is the sole ADR author).** Per synthesis §7 risks: (1) UI-15 transition surfacing — ONE-WAY, novel design; recommended ADR. (2) ADR-0018 bump to v1.1.0 — drift remediation; recommended ADR. (3) Credential redaction posture — ONE-WAY, OWASP MCP01 top-rank; recommended ADR. (4) Serena UI-8 narrowing posture — D-13 two-way but coupled; recommended ADR. (5) Install-mechanism strategy — D-1 two-way; Composer judges threshold. The CC layer surfaces these for Composer's authorship; this design does not pre-author any of them. **Defer to Composer.**

- **Q-CC-9: Augmented-`auditing-mcp` Gate 6 status — formal gate vs strongly-recommended check.** Per PRD UI-6 and AC-NFR-2-c, the augmented skill must produce no BLOCKER findings. Whether this is a hard Gate 6 acceptance criterion is open. **Defer to Composer + pipeline operator.** This design's AC-CC-5 says "shall report zero BLOCKER findings" — but doesn't say whether failure halts the pipeline.

## Open items

These are CC-layer-level open items that don't rise to the Q-CC-N (composer-bound architectural question) level — they are best resolved during plan-authoring or implementation:

1. **Per-server probe `--with-runtime` enablement on Context7 + Exa.** The supplementary authenticated probe (D-8) is gated by an env flag to protect quota. Default the flag to ON for postCreate (initial install), OFF for postStart (every-attach probe) — but this is a tuning decision plan-author may revisit.
2. **`mcp-events.jsonl` rotation policy.** The PRD's NFR-1 commits log overhead to negligible but doesn't specify rotation. Plan-author decides: append-only with `.previous` rollover at N MB? Daily file with date suffix? Stick with single file (operator's concern only if disk fills)? Recommended: single file, with a slash-command-invokable `mcp-events.jsonl truncate` helper.
3. **Skill-loading discipline by reviewers / per-layer designers for MCP-related work.** Should `design-cc`, `shared-document-reviewer`, and `review-architecture-auditor` add `KB-mcp-platform` and/or `KB-mcp-design` to their `skills:` arrays so they pre-load for any MCP-related review? Recommended: NO — leave model-invocable, since most CC work doesn't touch MCP. If reviewers consistently miss MCP context, revisit.
4. **CLAUDE.md introduction for MCP one-liner.** Not in this feature. If future operator feedback shows the trifecta isn't discoverable enough, a one-line CLAUDE.md pointer is the cheapest remediation. Tracked as a future re-scope option.
5. **`README.md` or operator-facing changelog note for the seven-server provisioning + the new trifecta + the mcp-events.jsonl tail command.** Per PRD Rollout Plan. Owned by `design-composer` cross-layer reconciliation; the CC layer provides the trifecta-entry-point sentence.
