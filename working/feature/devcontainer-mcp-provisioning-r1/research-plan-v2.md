---
id: RP-devcontainer-mcp-provisioning-r1
doc_type: research-plan
version: 2.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v2.md
supersedes: working/feature/devcontainer-mcp-provisioning-r1/research-plan.md
predecessor: working/feature/devcontainer-mcp-provisioning-r1/research-plan.md
generated: 2026-05-23T00:00:00Z
generated_by: discovery-plan-author
change_summary: >-
  Gate-3-triggered scope-expansion re-author. v2 absorbs PRD-v2's FR-8 (lifecycle
  health checks at postCreate/postStart/postAttach with named-failure-layer
  reporting), FR-9 (runtime failure surfacing with structured failure records),
  FR-10 (per-server runtime log with credential redaction), and FR-11 (W/H/A
  trifecta completion — add KB-mcp-platform, add KB-mcp-design, augment
  auditing-mcp). Codebase research scope gains a new "Pattern archaeology —
  What/How/Audit trifecta" subsection inventorying the three existing trifectas
  (KB-cc-platform / KB-cc-design / auditing-cc-configs; KB-codespaces-platform /
  KB-codespaces-design / auditing-codespaces; KB-github-actions-platform /
  KB-github-actions-design / auditing-github-actions) so Design can mirror
  the structural conventions. One external topic added — T-007 MCP Operational
  Discipline — covering MCP server health endpoints, transport-event surface,
  structured logging in Codespaces, credential redaction patterns, and
  operator-facing failure feedback. v1's T-001..T-006 (one per named MCP
  server) carried forward unchanged. Budget cap goes from 6 → 7 (explicitly
  authorized at Gate 3 by the user's scope expansion). Open questions OQ-1..
  OQ-4 carried forward where still applicable; OQ-5 added on lifecycle-hook
  ordering vs the existing `onCreateCommand`.
---

# Research Plan v2: Devcontainer MCP Server Provisioning

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
- **PRD path**: `working/feature/devcontainer-mcp-provisioning-r1/prd-v2.md`
- **PRD version**: 2.0.0
- **PRD gate state**: PRD v2 generated 2026-05-23 in response to Gate-3 user scope expansion; carries Intent Clarification `user_token: gate1-approved-2026-05-23`. v2's expansion is itself the input that drives this research-plan v2.
- **Scope class**: FULL (13-stage pipeline pass)
- **Activated layers (from PRD v2 Layer Scope — unchanged from v1)**: Claude Code / Project Filesystem; Dev Environment (Codespaces / Devcontainer)
- **Inherited ADRs in scope**:
  - **ADR-0021** (Discovery phase architecture — this Plan honors KB-and-ADR-first; the external-topic count of 7 exceeds the default 6-cap and is explicitly authorized at Gate 3 per scope-expansion feedback — see Budget section)
  - **ADR-0018** (codebase-analysis.json schema v1.1.0 — produced by `discovery-codebase-researcher`)
  - **ADR-0020** (KB structure — the new `KB-mcp-platform` and `KB-mcp-design` will be authored to conform; the existing trifectas are inventoried under Pattern archaeology so Design can mirror the convention)
  - **ADR-0009** (rationale brief 3-layer — the Plan is honored downstream as part of the rationale brief)
  - **ADR-0007 v2.0.0** (GitNexus primary / codebase-memory-mcp fallback — informs UI-8 Serena-fit question; the new KB-mcp-platform will reference this ADR)
- **Applicable KBs** (for the activated layers + cross-cutting concerns):
  - `KB-cc-platform` (Claude Code primitives, `.mcp.json`, transports, scopes, `tools:` allowlist syntax) — **also a trifecta exemplar**
  - `KB-cc-design` (which primitive to choose; context-cost discipline; sub-agent `tools:` restriction patterns) — **also a trifecta exemplar**
  - `KB-codespaces-platform` (devcontainer.json schema, lifecycle hooks `postCreate` / `postStart` / `postAttach`, Features, prebuild semantics, secrets surface) — **also a trifecta exemplar**
  - `KB-codespaces-design` (image vs Dockerfile vs docker-compose; lifecycle-hook placement; secrets via Codespaces secrets) — **also a trifecta exemplar**
  - `KB-github-actions-platform` + `KB-github-actions-design` (trifecta exemplars only — the activated layers do not include CI/CD)
  - `KB-codebase-research` (the codebase-analysis discipline applied by `discovery-codebase-researcher`)
  - `KB-documentation-criteria` (Research Plan template + Discovery Planning discipline; the `skill-format` convention the new KB-mcp skills must conform to)
  - `auditing-mcp` (existing audit skill the project carries; v2 augments it per FR-11; its current rubric is a codebase research target)
  - `auditing-cc-configs`, `auditing-codespaces`, `auditing-github-actions` (trifecta exemplars; codebase-research inventories these for convention discovery)
  - `KB-review-disciplines` (Gate 0/1 — the criteria this Plan will be reviewed against, indirectly)

## Information needs inventory

Each row maps a downstream-consumer information need to a disposition. Per ADR-0021, the disposition is the visible result of KB-and-ADR-first triage.

### v1 needs carried forward (Synthesis + per-layer Design needs, driven by PRD v1 Undetermined Items)

- **IN-001** — *What `.mcp.json` registration shape (transport, command, env-var references) does Claude Code expect for project-scoped, always-on servers, and what is the syntax of the `tools:` allowlist field consumed by sub-agents?*
  - Downstream consumer(s): `design-cc` (Claude Code Designer); `design-composer`.
  - **Disposition**: `covered-by-KB:KB-cc-platform:references/integrations.md` + `covered-by-KB:KB-cc-platform:assets/templates/mcp-config.json.example`.

- **IN-002** — *Among Claude Code's seven extension primitives, which one(s) should the provisioning use?*
  - Downstream consumer(s): `design-cc`.
  - **Disposition**: `covered-by-KB:KB-cc-design:references/patterns-and-anti-patterns.md`.

- **IN-003** — *What's the right Dev Container install mechanism (features vs Dockerfile RUN vs lifecycle hook) — rebuild cost, prebuild cacheability, credential surface?*
  - Downstream consumer(s): `design-codespaces`.
  - **Disposition**: `covered-by-KB:KB-codespaces-design:references/patterns-and-anti-patterns.md` + `covered-by-KB:KB-codespaces-platform:references/devcontainer.md`.

- **IN-004** — *How do Codespaces secrets surface as environment variables inside the container, and how are they referenced from `.mcp.json` without committing values?*
  - Downstream consumer(s): `design-codespaces`, `design-cc`.
  - **Disposition**: `covered-by-KB:KB-codespaces-platform:references/secrets-and-env.md` + `covered-by-KB:KB-cc-platform:assets/templates/mcp-config.json.example`.

- **IN-005** — *What's the canonical version-pinning posture for tools installed in a devcontainer?*
  - Downstream consumer(s): `design-codespaces` (UI-5).
  - **Disposition**: `designer-general-knowledge` (per-server recommended versions are bundled into T-001..T-006).

- **IN-006** — *What does the `auditing-mcp` skill check for, and what `.mcp.json` shapes does it flag as BLOCKER?*
  - Downstream consumer(s): `design-cc`; `design-composer` (UI-6); `plan-author` (phase validator). **v2 additional consumer**: the design subagents authoring the FR-11-c augmentation.
  - **Disposition**: `codebase-topic` — the skill is local; researcher reads SKILL.md + `references/*.md` + any audit scripts. Records the BLOCKER signal set AND the augmentation surface (where new checks for lifecycle/log/trifecta-drift will be added per FR-11-c / UI-14).

- **IN-007** — *What sub-agents exist today, what do each consume / produce, and which would naturally be the call sites for each of the six MCPs?*
  - Downstream consumer(s): `design-cc` (UI-1); `design-composer`.
  - **Disposition**: `codebase-topic` — `.claude/agents/*.md`.

- **IN-008** — *Current context-window baseline cost, and per-server token characteristics surfaced by `/context`.*
  - Downstream consumer(s): `design-cc` (UI-7).
  - **Disposition**: `codebase-topic` — measurement against the built container.

- **IN-009** — *Is the repo markdown-heavy enough that Serena's symbol-level traversal is wasted, and what existing codebase-traversal MCP role does the project already specify?*
  - Downstream consumer(s): `design-cc` (UI-8).
  - **Disposition**: `codebase-topic` — file-type composition + ADR-0007 v2.0.0 inheritance + agent declarations.

- **IN-010** — *Whether `auditing-mcp` (no-BLOCKER) becomes a formal Gate 6 acceptance criterion vs. a strongly recommended check (UI-6).*
  - Downstream consumer(s): `plan-author`.
  - **Disposition**: **Open question for human resolution** (OQ-2, carried forward).

### Per-MCP-server research needs (PRD UI-1, UI-2, UI-3, UI-4, UI-5; per-server slice — carried forward from v1)

For each of the six named servers, the Designer needs the same five facts: (i) install mechanism, (ii) transport, (iii) authentication shape, (iv) tool names exposed, (v) a published version to pin to. KB-cc-platform documents the *generic shape* of these fields in `.mcp.json`; it does NOT document any specific upstream server's choices. KB-codespaces-design documents the *general* install-mechanism trade-off; it does NOT document a specific package's install path. These are genuine KB gaps for each named server.

- **IN-011** — *Serena: install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-001`.
- **IN-012** — *mcp-openapi-schema (`hannesj/mcp-openapi-schema`): install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-002`.
- **IN-013** — *actionlint-mcp (`hongkongkiwi/actionlint-mcp`): install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-003`.
- **IN-014** — *HashiCorp Terraform MCP: install/transport/auth/tools/version-pin — base-image constraints (no Go toolchain, no DinD).* — **Disposition**: `external-research-topic:T-004`.
- **IN-015** — *Context7: install/transport/auth/tools/version-pin.* — **Disposition**: `external-research-topic:T-005`.
- **IN-016** — *Exa: install/transport/auth (header vs query param)/tools/version-pin.* — **Disposition**: `external-research-topic:T-006`.

### New v2 needs (driven by PRD v2 FR-8 / FR-9 / FR-10 / FR-11 and UI-9..UI-14)

- **IN-017 (new in v2)** — *What devcontainer lifecycle hook ordering and re-entrancy semantics apply across `postCreate` / `postStart` / `postAttach` — including how each phase interacts with prebuild, whether `postAttach` runs in every attached shell or only once per attach session, and how the existing `onCreateCommand` composes with new hooks?*
  - Downstream consumer(s): `design-codespaces` (UI-9 — lifecycle-hook strategy for the health check); `design-cc` (UI-10 — staleness threshold + on-demand command shape).
  - **Disposition**: `covered-by-KB:KB-codespaces-platform:references/devcontainer.md` (KB-codespaces-platform documents the lifecycle-hook order, prebuild boundary, and re-entrancy of each phase). The interaction with the project's existing `onCreateCommand` is a **codebase-topic** (already covered by the v1 touch-points list which the researcher reads in any case).

- **IN-018 (new in v2)** — *What conventions and patterns does the project use today for "What/How/Audit" KB-skill trifectas — specifically: SKILL.md frontmatter shape (the `name`, `description`, `allowed-tools`, `pedagogical_sections` fields); `references/` subdirectory layout and naming (e.g., `principles.md`, `patterns-and-anti-patterns.md`, `integrations.md`); whether platform skills carry an `assets/templates/` directory while design skills do not; how the platform and design halves cross-reference each other; how the audit skill names its rubric files (`anti-patterns.md`, `toxic-combinations.md`, `common-failures.md`) and how its audit scripts are structured?*
  - Downstream consumer(s): `design-cc` (UI-13 — internal organization of `KB-mcp-platform` and `KB-mcp-design`; UI-14 — specific augmentations to `auditing-mcp`); `design-composer` (integrates).
  - **Disposition**: `codebase-topic` — the three existing trifectas live in `.claude/skills/`. The researcher inventories them and extracts the structural conventions so Design can mirror them. *Not* external research (the answer is "what does our codebase do"); *not* `designer-general-knowledge` (these conventions are project-specific). See the new "Pattern archaeology — What/How/Audit trifecta" subsection under Codebase research scope.

- **IN-019 (new in v2)** — *What MCP-specific operational disciplines exist outside this project's KBs and ADRs — specifically: MCP server health endpoints / readiness signaling conventions; Claude Code's MCP transport-event surface and disconnect/reconnect behavior; structured logging patterns for stdio MCP servers vs HTTP MCP servers in a Codespaces/devcontainer environment; credential redaction patterns for MCP logs; operator-facing failure-feedback patterns (how other projects surface a "this MCP just failed mid-run" event); runtime-monitoring approaches for MCP fleets that are NOT a remote telemetry pipeline?*
  - Downstream consumer(s): `design-codespaces` (UI-12 — runtime log surface specifics: path, format, rotation, redaction mechanism); `design-cc` (UI-11 — mid-run failure surface choice; UI-13 — what `KB-mcp-platform` documents about MCP operational facts; UI-14 — what new checks the augmented `auditing-mcp` carries); `design-composer` (integrates across UI-9..UI-14).
  - **Disposition**: `external-research-topic:T-007`. See KB gap justification under T-007 below.

- **IN-020 (new in v2)** — *What specific failure layers does Claude Code's MCP integration name when a server fails (install / registration / transport / auth / probe / tool-error), and what does its session-log / stderr surface look like for each? This drives the structured failure record's "named failure layer" field (AC-FR-9-a) and the remediation-pointer target (AC-FR-8-d).*
  - Downstream consumer(s): `design-cc` (UI-11 mid-run failure surface; UI-13 KB-mcp-platform troubleshooting section).
  - **Disposition**: this need is partially `covered-by-KB:KB-cc-platform:references/integrations.md` (the MCP integration section names the connect-status surface visible via `claude mcp list`) and partially **bundled into T-007** (the runtime / mid-run failure-surface shape is the operational gap T-007 closes). The KB covers the *static* MCP shape; T-007 covers the *runtime* shape. No additional external topic needed.

- **IN-021 (new in v2)** — *What does the project's existing runtime/log surface look like — does any existing skill or sub-agent produce per-component logs, and is there an established log-rotation or log-tailing convention this feature should reuse rather than reinvent?*
  - Downstream consumer(s): `design-codespaces` (UI-12).
  - **Disposition**: `codebase-topic` — researcher greps for existing log surfaces in `.claude/`, `.devcontainer/`, scripts, and existing sub-agents. If nothing exists, the absence is itself the finding and Design knows it is greenfield.

## Codebase research scope

Single invocation of `discovery-codebase-researcher` (per ADR-0021). Output: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json` (schema v1.1.0 per ADR-0018) + sibling markdown report.

### Touch points (v1 carried forward, v2 additions inline)

- `.devcontainer/Dockerfile` — base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`), current `apt-get` install layer, Yarn-list workaround. This is the surface the provisioning extends or replaces.
- `.devcontainer/devcontainer.json` — current `features` (Claude Code, Node LTS, GitHub CLI, common-utils), `onCreateCommand`, `containerEnv`, `hostRequirements`, `customizations`. **v2: also the integration point for the new `postCreate` / `postStart` / `postAttach` health-check hooks (FR-8); the researcher records the existing lifecycle-hook fields used today and the unused ones available for extension.**
- `.mcp.json` — **confirmed absent** at the repo root as of plan-author's check. This is the file the feature *creates*; the researcher confirms it does not exist and that no MCP registration is currently committed.
- `.claude/agents/*.md` — every sub-agent file. The researcher inventories which agents exist, their current `tools:` allowlists, and which are likely call sites for each of the six MCPs. Of particular interest (v1 list carried forward):
  - `discovery-codebase-researcher.md` (likely Serena consumer)
  - `discovery-external-researcher.md` (likely Context7 + Exa consumer)
  - `design-api.md` (likely mcp-openapi-schema consumer)
  - `design-cicd.md` (likely actionlint-mcp consumer)
  - `design-iac.md` (likely HashiCorp Terraform MCP consumer)
  - `design-codespaces.md`, `design-claude-code.md` (producers of this feature's design, not consumers)
- `.claude/skills/auditing-mcp/SKILL.md` + `references/*.md` + any audit scripts — the rubric the resulting `.mcp.json` must satisfy at Gate 6 (AC-NFR-2-c). **v2: also the surface the FR-11-c augmentation amends; researcher records both the current rubric and the file/script extension points where new checks will be added (UI-14).**
- `adrs/ADR-0007*.md` and adjacent ADRs — establishes GitNexus primary / codebase-memory-mcp fallback; informs UI-8 and the cross-reference targets in `KB-mcp-platform`.
- **v2 additions:**
  - `.claude/skills/KB-cc-platform/`, `.claude/skills/KB-cc-design/`, `.claude/skills/auditing-cc-configs/` — Claude Code trifecta exemplar (the most-developed pair; the canonical reference for `KB-mcp-platform` / `KB-mcp-design` shape).
  - `.claude/skills/KB-codespaces-platform/`, `.claude/skills/KB-codespaces-design/`, `.claude/skills/auditing-codespaces/` — Codespaces trifecta exemplar; closest in subject matter to the lifecycle / log work this feature does.
  - `.claude/skills/KB-github-actions-platform/`, `.claude/skills/KB-github-actions-design/`, `.claude/skills/auditing-github-actions/` — GitHub Actions trifecta exemplar; useful as a third data point to distinguish trifecta *conventions* from skill-specific quirks.
  - Any existing log surface or log-tail helper in `.claude/` or `.devcontainer/scripts/` — researcher greps for it (IN-021).

### Blast-radius questions

Per ADR-0018, capture the following in `codebase-analysis.json`'s `blast_radius` section:

1. **`.mcp.json` (new file)** — v1 unchanged.
   - Who reads it? Every Claude Code session in this repo.
   - 1-hop dependents: every `.claude/agents/*.md` whose `tools:` allowlist names an MCP tool registered there.
   - 3-hop dependents: every pipeline stage that fans out to those sub-agents.
   - Test files: none today (CI smoke deferred to Won't-Have per I-DR-005).
2. **Each `.claude/agents/*.md` whose `tools:` allowlist is edited** — v1 unchanged.
   - 1-hop dependents: orchestrator stages that invoke that sub-agent.
   - Convention impact: agent-file frontmatter shape must conform.
3. **`.devcontainer/Dockerfile` and `devcontainer.json`** — v1 unchanged.
   - 1-hop dependent: the Codespaces build pipeline.
   - Convention impact: the `vscode` `customizations` block, `containerEnv` block, `hostRequirements` block; existing Feature pin policy.
4. **(new in v2) New lifecycle hooks `postCreate` / `postStart` / `postAttach` invocations on `devcontainer.json`**:
   - 1-hop dependents: every Codespace build/start/attach event for this repo.
   - Convention impact: must compose with the existing `onCreateCommand` (currently a verification command — the researcher records whether health-check should extend it or run alongside).
   - 3-hop dependents: every sub-agent run in a Codespace (because the health check is the first signal those sub-agents see about MCP availability).
5. **(new in v2) The augmented `auditing-mcp` skill**:
   - 1-hop dependents: anyone (human or pipeline-stage) running the audit.
   - Convention impact: must continue to conform to the `auditing-cc-configs` family shape (shared rubric, weights, thresholds, triage as called out in `auditing-mcp/SKILL.md`).
6. **(new in v2) New `KB-mcp-platform` and `KB-mcp-design` skills**:
   - 1-hop dependents: any sub-agent or human reading the trifecta to reason about MCP — minimally `design-codespaces` and `design-cc` going forward.
   - Convention impact: must conform to the existing trifecta convention extracted under "Pattern archaeology" below.

### Convention discovery (v1 carried forward, v2 additions in their own subsection)

Per in-scope layer:

- **Claude Code / Project Filesystem** (v1):
  - Agent file frontmatter convention: which fields are used (`name`, `description`, `model`, `effort`, `tools`, `skills`, `memory`)? What's the `tools:` field's syntax?
  - Skill structure: do existing skills follow `KB-*` naming + `SKILL.md` + `references/` layout (per ADR-0020)?
  - Existing MCP references in `.claude/skills/*` (KB-codebase-research mentions GitNexus, codebase-memory-mcp, Context7; KB-cc-platform mentions Context7) — confirm whether they're documented as "available to load" vs. "must be in `.mcp.json`."
- **Dev Environment (Codespaces)** (v1):
  - Lifecycle pattern: project currently uses Dockerfile-baked for image-layer tools + Features for declarative installations + `onCreateCommand` for verification. The convention any new install must extend or justify departing from.
  - Pin policy in use across Features. Researcher records the inventory so the per-layer designer can apply IN-005 / UI-5 consistently.
  - Secrets surface: `containerEnv` is used for non-secret env. Confirm this is empty of credentials.

### Pattern archaeology — What/How/Audit trifecta (new in v2, per FR-11 / UI-13 / UI-14)

The researcher walks the three existing trifectas and extracts the **structural conventions** Design must mirror when authoring `KB-mcp-platform` + `KB-mcp-design` and when augmenting `auditing-mcp`. This is *pattern extraction*, not redesign — the goal is for `design-cc` and the design subagents to receive a concrete "the project's W/H/A convention is X" claim grounded in the three existing instances, so the new MCP trifecta is convention-coherent at first authoring.

**Trifectas to inventory** (each has all three legs in the repo):

1. **Claude Code trifecta**: `KB-cc-platform/` (What) + `KB-cc-design/` (How) + `auditing-cc-configs/` (Audit).
2. **Codespaces trifecta**: `KB-codespaces-platform/` (What) + `KB-codespaces-design/` (How) + `auditing-codespaces/` (Audit).
3. **GitHub Actions trifecta**: `KB-github-actions-platform/` (What) + `KB-github-actions-design/` (How) + `auditing-github-actions/` (Audit).

**Structural conventions to extract per trifecta** (the researcher produces a small table across the three):

- **SKILL.md frontmatter shape**: which fields appear in each (`name`, `description`, `allowed-tools`, `pedagogical_sections` with `path` + `justification`); whether the description format is consistent (e.g., always starts with a noun phrase naming the platform); whether platform vs design vs audit skills declare different `allowed-tools`.
- **`references/` subdirectory layout**: which canonical files appear (e.g., `principles.md`, `patterns-and-anti-patterns.md`, `integrations.md`, `configuration.md`); whether all three skills in a trifecta share a file convention or each leg has its own; whether file names are stable across trifectas (the most useful pattern) or vary per platform (in which case the researcher records the per-trifecta names).
- **`assets/templates/` directory presence**: does the platform half carry `assets/templates/<thing>.example` files? Does the design half? Does the audit half? (The KB-cc-platform frontmatter references an `mcp-config.json.example` — researcher confirms the file exists under `assets/templates/`.)
- **Model-invocable vs human-invocable**: is the skill invoked autonomously by sub-agents (via `skills:` declarations) or by humans via slash commands or `Skill` tool calls? Researcher records the invocation pattern for each leg.
- **Audit subdir conventions**: how does each `auditing-*/` organize its `references/` (e.g., `anti-patterns.md`, `toxic-combinations.md`, `common-failures.md`)? Are audit scripts present (`scripts/` dir or inline `Bash(python3 *)` calls)? Does the audit skill declare itself part of an audit *family* (the `auditing-cc-configs` family pattern visible in `auditing-mcp/SKILL.md`)?
- **Cross-reference style between platform and design halves**: how does `KB-cc-platform` reference `KB-cc-design` (and vice-versa)? Frontmatter `description` cross-reference (as `kb-cc-platform`'s description does: "Pairs with KB-cc-design"), inline `[[]]` linking in references files, or both? Researcher records the canonical style.
- **What/How/Audit naming consistency**: is the convention always `KB-<platform>-platform` / `KB-<platform>-design` / `auditing-<platform>`? Does `auditing-cc-configs` (note the trailing `-configs`) deviate, and if so, why? (Researcher records the variation and Design decides whether `auditing-mcp` is the canonical audit-skill name — it already exists — or whether v2's augmentation invites a rename. The PRD assumes no rename.)
- **Pedagogical-sections discipline (per ADR-0030)**: how is `pedagogical_sections` populated in each platform/design/audit skill — researcher records exemplary `justification` strings so the new KB-mcp skills mirror the discipline.

**Output for Design**: a "trifecta convention summary" table or markdown block embedded in `codebase-analysis.json`'s convention-discovery section, listing the conventions above, with concrete file-path examples drawn from the three existing trifectas. `design-cc` consumes this directly when authoring UI-13 (internal organization) and UI-14 (specific audit augmentations).

### Specific queries or grep targets

- `Grep "tools:" .claude/agents/*.md` — surface the canonical `tools:` allowlist shape.
- `Grep "mcp__" .claude/` — find any existing reference to MCP tool naming conventions.
- `Grep -ri "Serena\|GitNexus\|codebase-memory\|Context7\|Exa\|actionlint\|terraform.?mcp\|openapi.?schema" .claude/ adrs/` — find every existing reference to any of the six servers (or the displaced ones).
- `find . -name "*.md" -not -path "./node_modules/*" | wc -l` and `find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | awk -F. '{print $NF}' | sort | uniq -c | sort -rn` — file-type composition for UI-8 / IN-009.
- **v2 additions:**
  - `ls -la .claude/skills/KB-cc-platform/ .claude/skills/KB-cc-design/ .claude/skills/auditing-cc-configs/` (and same for codespaces / github-actions trifectas) — surface directory shapes for Pattern archaeology.
  - `Grep -l "pedagogical_sections" .claude/skills/` — confirm the convention is universal in trifecta skills.
  - `Grep "postCreate\|postStart\|postAttach\|onCreate" .devcontainer/devcontainer.json` — confirm which lifecycle phases the current devcontainer.json uses and which are available for FR-8 extension.
  - `Grep -ri "log\|tail\|rotat" .claude/ .devcontainer/` (excluding markdown body text; focus on script/config) — IN-021 existing-log-surface inventory.

## External research topics

7 topics total. T-001..T-006 carried forward from v1 unchanged; T-007 new in v2.

The default external-topic budget is 6 per ADR-0021. Exceeding the cap is explicitly authorized at this Gate by the PRD-v2 scope expansion (the user identified MCP operational discipline — health, runtime failures, logging, and trifecta completion — as a gap that v1 did not cover, and asked for the Research Plan to be re-authored to cover it). The 7th topic is **not** a per-server slice (those are already at 6); it is one new operational topic that consolidates several otherwise-fragmented sub-questions (FR-8 health-endpoint conventions; FR-9 runtime failure surfaces; FR-10 log capture and redaction; UI-11..UI-14 design choices). See "Budget" under Estimated effort.

**Generic-with-N-invocations** per ADR-0021: each topic is dispatched to one `discovery-external-researcher` invocation; up to 6 run in parallel (T-007 may run in the same parallel batch as 5 of the T-001..T-006, with the 7th in a second batch — or all 7 if the orchestrator's parallelism cap is raised; either is acceptable since per-topic acceptance criteria are tight).

### T-001 — Serena MCP server (carried forward from v1, unchanged)

- **Research question**: For the Serena MCP server, what are the canonical (a) install mechanisms supported, (b) transport options, (c) tool names exposed, (d) authentication requirements (if any), and (e) a recommended pinned version with rationale — and to what extent is Serena's symbol-level value contingent on the target codebase being source-code-heavy vs. markdown-heavy?
- **KB gap justification**: KB-cc-platform documents the generic `.mcp.json` shape; it does NOT document Serena specifically. KB-codebase-research mentions GitNexus / codebase-memory-mcp as the canonical codebase-traversal MCPs (per ADR-0007 v2.x); it does NOT cover Serena. KB-codespaces-design covers Features vs Dockerfile vs lifecycle generically; it does NOT cover Serena's specific install path. No ADR resolves Serena's role. Not `designer-general-knowledge` — Serena is a specific upstream project; vendor-specific facts.
- **Acceptance criteria**: names the upstream source URL; identifies at least 2 of {pip install, uv tool install, pipx install, Docker image, prebuilt binary, build from source} that work on `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`; identifies the supported transports; enumerates the tool names exposed; states whether authentication is required; quotes a specific recent version number to pin to; identifies the symbol-level-value-vs-markdown-heavy-repo trade-off explicitly.
- **Source constraints**: official upstream repo; the project's README / docs; release notes for the recommended pin; community discussion only where it confirms a published version or install path. No speculation about future versions.

### T-002 — mcp-openapi-schema (`hannesj/mcp-openapi-schema`) (carried forward from v1, unchanged)

- **Research question**: For the `hannesj/mcp-openapi-schema` MCP server, what are (a) install mechanism, (b) transport, (c) tool names exposed for OpenAPI document loading/querying, (d) authentication, and (e) a recommended pinned version with rationale?
- **KB gap justification**: KB-api-design covers OpenAPI as a contract format; it does NOT cover this specific MCP server's install path or tool surface. KB-cc-platform documents stdio MCP shape generically but not this server. No ADR addresses it. Not `designer-general-knowledge`.
- **Acceptance criteria**: names the upstream GitHub repo + npm package (if applicable); identifies the install command; confirms transport is stdio; enumerates the tool names; confirms whether auth is required; quotes a specific recent version (semver) to pin to.
- **Source constraints**: official upstream GitHub repo; npm registry page; release notes. No speculation; if multiple `mcp-openapi-schema`-named packages exist, name the canonical one and explain how the choice was made.

### T-003 — actionlint-mcp (`hongkongkiwi/actionlint-mcp`) (carried forward from v1, unchanged)

- **Research question**: For the `hongkongkiwi/actionlint-mcp` MCP server, what are (a) install mechanism, (b) transport, (c) tool names exposed for GitHub Actions linting, (d) authentication, (e) the upstream `actionlint` binary it depends on (separate package; does it need to be installed first?), and (f) a recommended pinned version with rationale for *both* the MCP wrapper and the underlying actionlint binary?
- **KB gap justification**: KB-github-actions-design and KB-github-actions-platform cover GitHub Actions; they do NOT cover the `actionlint-mcp` server's install path or how the underlying `actionlint` binary is acquired. KB-cc-platform documents stdio MCP shape but not this specific package. No ADR resolves it. Not `designer-general-knowledge` — vendor-specific and there's a dual-dependency wrinkle.
- **Acceptance criteria**: names upstream repos for both `actionlint-mcp` wrapper and the `actionlint` binary; identifies install commands for both; confirms transport is stdio; enumerates tool names; confirms no auth; quotes specific recent versions for both with pin rationale; identifies whether the wrapper installs the binary or expects it on `$PATH`.
- **Source constraints**: official upstream GitHub repos; release notes; verified install instructions from each project's README.

### T-004 — HashiCorp Terraform MCP server (carried forward from v1, unchanged — UI-2 + UI-5 partial resolution)

- **Research question**: For HashiCorp's Terraform MCP server, what are (a) install mechanisms supported AND specifically which ones are viable on `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` given no Go toolchain and no Docker-in-Docker are present, (b) transport (stdio vs HTTP), (c) tool names exposed, (d) authentication (`TFE_TOKEN`?), and (e) a recommended pinned version with rationale?
- **KB gap justification**: KB-iac-design covers Terraform design discipline; it does NOT cover the Terraform MCP server. KB-codespaces-design covers Features vs Dockerfile vs lifecycle generically; it does NOT cover HashiCorp's specific MCP distribution. KB-cc-platform documents the stdio/HTTP shape generically; not this server's specifics. No ADR addresses it. Not `designer-general-knowledge` — base-image constraint requires specialized lookup.
- **Acceptance criteria**: names the official HashiCorp source URL; enumerates *all* documented install mechanisms; for each, states whether it works on the current base image with the current toolchain; recommends one with explicit base-image-fit rationale; identifies the transport; enumerates the tool names exposed; states whether `TFE_TOKEN` is required; quotes a specific recent version to pin to.
- **Source constraints**: HashiCorp's official documentation, GitHub repo, release page; the project's README. No third-party tutorials except to confirm a published install path; no speculation.

### T-005 — Context7 (carried forward from v1, unchanged — UI-4 resolution)

- **Research question**: For Context7 MCP, what are (a) the supported transports (remote HTTP vs locally-installed stdio), (b) for the remote HTTP option, the endpoint URL and authentication shape, (c) for the stdio option, the install command, (d) the tool names exposed, and (e) a recommended pinned version with rationale?
- **KB gap justification**: KB-cc-platform's `references/integrations.md` mentions Context7 by name as a verification source but does NOT document how to register Context7 in `.mcp.json`, what transport to choose, or what authentication shape Context7 expects. KB-cc-design is silent on the choice. No ADR addresses Context7's transport. Not `designer-general-knowledge` — Context7 is a specific SaaS + open-source pair.
- **Acceptance criteria**: confirms the official upstream + the hosted endpoint URL; documents both transport options with their trade-offs; names the auth header / query-param shape for remote; names the install command for local stdio; enumerates tool names; recommends a default transport for this project's needs with rationale; quotes a specific recent version.
- **Source constraints**: Context7's official site + its open-source repo; verified release notes; no speculation.

### T-006 — Exa (carried forward from v1, unchanged — UI-3 resolution)

- **Research question**: For Exa MCP, what are (a) the supported transports, (b) for the remote HTTP option specifically the transport-level authentication mechanism (Bearer header vs URL query parameter), (c) for the stdio option (if any), the install command, (d) the tool names exposed, and (e) a recommended pinned version with rationale?
- **KB gap justification**: KB-cc-platform documents `.mcp.json` generic auth patterns; it does NOT document Exa's specific choice. No ADR addresses Exa. Not `designer-general-knowledge` — vendor-specific protocol decision; the wrong choice causes the per-server probe (FR-4) to fail at acceptance.
- **Acceptance criteria**: confirms the official upstream (Exa Labs); documents the canonical hosted endpoint URL; states authoritatively whether `EXA_API_KEY` is passed as a header (which header name) or as a URL query parameter — and quotes the source page; if both are supported, recommends one with rationale; names the tool names exposed; identifies whether a local-stdio variant exists; quotes a specific recent version.
- **Source constraints**: Exa's official documentation site; Exa's MCP server official repo; Exa's API reference. No third-party tutorials except to confirm endpoint shape.

### T-007 — MCP Operational Discipline (new in v2 — FR-8 / FR-9 / FR-10 / FR-11 cross-cutting)

- **Research question**: What are the externally-established operational disciplines for production-leaning MCP deployments — specifically: (a) **MCP server health endpoints and readiness signaling conventions** (how does an MCP host or operator detect that a stdio server has gone unhealthy, given stdio has no HTTP "health" endpoint? how does an HTTP MCP server expose readiness?); (b) **Claude Code's MCP transport-event surface** (what events does the Claude Code MCP client emit on connect, disconnect, handshake failure, tool-call error? where are they observable — session log, stderr, `claude mcp list` status field?); (c) **structured logging patterns for stdio vs HTTP MCP servers in a Codespaces / devcontainer environment** (file path conventions, format conventions — JSONL vs text, per-server-file vs interleaved, rotation policies in a single-operator no-on-call context); (d) **credential redaction patterns for MCP logs** (regex on credential shapes, env-var-name-driven redaction, structural redaction in the MCP client — which approach is used in practice by other MCP fleets and which is the least likely to leak); (e) **operator-facing failure-feedback patterns** (how do other projects surface a "this MCP just failed mid-run" event to the operator — CLI banner, stderr structured record, ephemeral chat-side notification, dedicated event file? what fields do the structured failure records carry?); (f) **runtime-monitoring approaches for MCP fleets that are NOT a remote telemetry pipeline** (local-only equivalents — what does a small team that runs MCP servers in devcontainers do for runtime observability without standing up Prometheus/Grafana)?
- **KB gap justification**: This is the single largest KB gap surfaced by the PRD-v2 scope expansion.
  - **KB-cc-platform**: documents the **static** `.mcp.json` shape (server config, transports, scopes, the `tools:` allowlist syntax) and the `claude mcp list` connect-status surface. It does NOT document runtime MCP behavior (mid-session disconnects, transport-event observability beyond the static list), structured-logging conventions for MCP servers, credential redaction patterns, or operator-facing failure feedback at runtime. The KB's MCP coverage is "register and connect," not "monitor and respond to failures."
  - **KB-codespaces-platform**: documents lifecycle hooks (`postCreate` / `postStart` / `postAttach`) generically — *what each phase does* — but does NOT cover MCP-specific health checks, log surfaces, or failure feedback. Lifecycle integration with MCP is novel cross-cutting territory.
  - **KB-cc-design**: provides the "which primitive when" decision matrix; silent on MCP runtime operational discipline.
  - **KB-codespaces-design**: provides Features-vs-Dockerfile-vs-lifecycle generic discipline; silent on MCP runtime.
  - **ADRs**: ADR-0007 establishes the codebase-traversal MCP role (GitNexus/codebase-memory-mcp) but is about *which MCPs do which job*, not about runtime health. No ADR covers MCP operational discipline.
  - **Why not `designer-general-knowledge`**: MCP is recent enough (Anthropic's protocol, public release within ~12 months of feature date) that "operational discipline for MCP fleets" is not yet conventional knowledge a designer would just carry. Production patterns are emerging in vendor docs and early-adopter writeups, not in established RFCs or stable industry idioms. A competent designer would consult sources rather than apply convention.
  - **Why not split across multiple topics**: each of (a)..(f) is too thin to warrant its own topic acceptance criteria, and the sources overlap heavily (Anthropic's MCP docs cover several; vendor-server projects' docs cover several). One consolidated topic with multi-part acceptance criteria is the discipline-aligned approach when topics share sources.
- **Acceptance criteria**: at least **3 independent reputable sources** cited (e.g., Anthropic's official MCP protocol documentation, one or more vendor MCP server implementations' operational docs, one or more devcontainer/Codespaces best-practice writeups from teams operating MCP at scale). For each of the 6 sub-questions (a)..(f): names at least one source-backed pattern (or, if no established pattern exists in the literature, says so explicitly — "no consensus pattern; emerging practice is X with caveat Y"); identifies at least 2 trade-offs (e.g., "regex redaction is simpler but misses keyed credentials; structural redaction is more reliable but requires MCP-client cooperation"); quotes specific version numbers, limits, or file-path conventions where the source provides them.
- **Source constraints**: prefer (in order): (i) Anthropic's official MCP protocol and Claude Code MCP documentation; (ii) the official repos / docs of widely-adopted MCP server implementations (including but not limited to the six named in this feature — researchers may cite operational practices from other named servers if the practice is transferable); (iii) devcontainer / Codespaces best-practice writeups from teams running MCP in containerized dev environments; (iv) credible engineering blogs / RFCs / community discussions from MCP early adopters at scale. Avoid speculative / unsourced blog posts and any source that does not name a specific version or pattern. If a sub-question has no good source, state so explicitly — "no consensus" is a valid finding here and informs Design's choice of where to innovate vs follow precedent.

## Topics explicitly NOT researched

Per ADR-0021's anti-scope-creep discipline. Every information need with disposition `covered-by-KB`, `covered-by-ADR`, `codebase-topic`, or `designer-general-knowledge` lands here with its resolving artifact + a 1–2-sentence resolution summary.

### Resolved by existing KBs

- **IN-001** (`.mcp.json` registration shape + `tools:` allowlist syntax) — Resolved by **KB-cc-platform** (`references/integrations.md` + `assets/templates/mcp-config.json.example` + `references/extensions.md`). **Resolution summary**: the platform KB documents stdio/HTTP/SSE transport shapes, `${VAR_NAME}` env-var substitution, project-scoped `.mcp.json` location, and the `mcp__<server>__<tool>` permission-naming convention.

- **IN-002** (which Claude Code primitive to use) — Resolved by **KB-cc-design** (`references/patterns-and-anti-patterns.md`). **Resolution summary**: decision matrix is dispositive — MCP server (registration) plus subagent `tools:` restriction (wiring).

- **IN-003** (install mechanism: Features vs Dockerfile RUN vs lifecycle) — Resolved by **KB-codespaces-design** (`references/patterns-and-anti-patterns.md`) + **KB-codespaces-platform** (`references/devcontainer.md`). **Resolution summary**: design KB establishes the generic trade-off; platform KB pins down lifecycle-hook order + prebuild boundaries. Per-server install paths are external topics T-001..T-006.

- **IN-004** (Codespaces secrets surfacing as env vars referenced by `.mcp.json`) — Resolved by **KB-codespaces-platform** (`references/secrets-and-env.md`) + **KB-cc-platform** (`assets/templates/mcp-config.json.example`). **Resolution summary**: Codespaces secrets surface as env vars; `.mcp.json` uses `${VAR_NAME}` substitution. Canonical and well-documented.

- **IN-017 (new in v2)** (devcontainer lifecycle hook ordering / re-entrancy across `postCreate` / `postStart` / `postAttach`) — Resolved by **KB-codespaces-platform** (`references/devcontainer.md`). **Resolution summary**: the platform KB documents which phase runs when (postCreate after build; postStart on every container start including resume; postAttach on every operator attach), the prebuild boundary, and the re-entrancy semantics. The interaction with the project's existing `onCreateCommand` is recorded by the codebase researcher (already a v1 touch point) and feeds the same answer.

### Resolved by inherited ADRs

- (No ADR resolves an information need by itself in this feature. ADR-0007 v2.0.0 establishes the existing codebase-traversal MCP role and is consulted under IN-009 / UI-8 as a codebase-topic. ADR-0021 governs *how* this Plan is structured. ADR-0030 governs pedagogical-marker justification — relevant to the new `KB-mcp-platform` / `KB-mcp-design` skills' frontmatter and surfaced under Pattern archaeology so Design mirrors the discipline.)

### Resolved as `designer-general-knowledge`

- **IN-005** (version-pinning posture for devcontainer tools) — **Resolution summary**: Standard devcontainer hygiene — pin tool versions; express via Feature `version:` field, `apt-get install <pkg>=<version>` or `ARG <PKG>_VERSION` in Dockerfile, `npm i <pkg>@<version>` for npm-based servers. `design-codespaces` documents the chosen pin policy with explicit rationale. Per-server *recommended versions* are NOT general knowledge and are bundled into T-001..T-006.

### Resolved as `codebase-topic` (routed to `discovery-codebase-researcher`)

- **IN-006** (`auditing-mcp` BLOCKER criteria + augmentation surface) — Resolution: `.claude/skills/auditing-mcp/SKILL.md` + `references/*.md` + any audit scripts. Researcher records BLOCKER signal set AND the file/script extension points for FR-11-c augmentation (UI-14).
- **IN-007** (sub-agent inventory + likely call sites for each MCP — UI-1 mapping) — Resolution: `.claude/agents/*.md`.
- **IN-008** (current baseline context-window cost — UI-7) — Resolution: measurement against the built container via `/context`.
- **IN-009** (markdown-heavy-repo + existing codebase-MCP role — UI-8 input) — Resolution: file-type composition + ADR-0007 v2.0.0 + existing `discovery-codebase-researcher.md` declared role.
- **IN-018 (new in v2)** (W/H/A trifecta structural conventions — UI-13 / UI-14 inputs) — Resolution: **codebase-research's new "Pattern archaeology — What/How/Audit trifecta" subsection** inventories the three existing trifectas (Claude Code, Codespaces, GitHub Actions) and extracts the SKILL.md frontmatter shape, `references/` layout, `assets/templates/` presence pattern, model-invocable-vs-human-invocable surface, audit subdir conventions, audit-script patterns, and cross-reference style. The trifecta-pattern question (UI-13 internal organization; UI-14 audit augmentation shape) is therefore explicitly **NOT** an external research topic — it is resolved entirely by reading what the codebase already does. T-007 covers the *operational* MCP gap, not the trifecta-structure gap; these are deliberately scoped to be non-overlapping.
- **IN-021 (new in v2)** (existing project runtime/log surface) — Resolution: grep `.claude/` and `.devcontainer/` for log conventions. If nothing exists, the absence is the finding and Design knows it is greenfield.

### Partially resolved (KB + bundled into external topic)

- **IN-020 (new in v2)** (Claude Code's MCP failure-layer naming + session-log/stderr surface) — Resolution: **partially covered by KB-cc-platform** (`references/integrations.md` describes the connect-status field visible via `claude mcp list`) and **the runtime/mid-run portion is bundled into T-007**. No standalone external topic — the runtime piece consolidates into the operational topic.

### Resolved by ADR-0021 + Gate-3 budget authorization (meta)

- The trifecta-pattern question (UI-13 — internal organization of `KB-mcp-platform` and `KB-mcp-design`; UI-14 — specific augmentations to `auditing-mcp`) is resolved by **codebase research** (Pattern archaeology), not by external research. ADR-0007 and KB-cc-platform together cover MCP *basics* (which MCP server fills which role; how `.mcp.json` is shaped); T-007 covers the genuinely external *operational* gap (runtime health / failure feedback / logging / redaction conventions that are not yet in any project KB or ADR). The deliberate split is: structure (trifecta) = codebase; operations (runtime) = T-007.

## Estimated effort

### Budget

- **Codebase research effort**: **medium → large** (v1 was medium). The repo is bounded (≈30 sub-agents, one devcontainer surface, one skills directory, ~30 ADRs), but v2 adds Pattern archaeology across three trifectas — that is roughly three additional skill-directory walks beyond the v1 work. Still within a single `discovery-codebase-researcher` invocation; no fan-out needed.
- **External research topic count**: **7 of an authorized 7** (was 6 of 6 default in v1). The default ADR-0021 cap is 6. The 7th topic (T-007 MCP Operational Discipline) is **explicitly authorized at Gate 3 by the user's PRD-v2 scope expansion** — the expansion identified operational discipline (FR-8/9/10 runtime + FR-11 trifecta) as a v1 gap and asked the Research Plan to cover it. Consolidation rationale: T-007 is itself a consolidation of six sub-questions (health endpoints, transport events, structured logging, credential redaction, failure feedback, local runtime monitoring) that share source overlap (Anthropic MCP docs, vendor MCP server docs, devcontainer best-practice writeups) — they cannot be further consolidated into one of T-001..T-006 without making a per-server topic responsible for the whole project's operational discipline, which is the wrong granularity. The per-server topics stay tight at five-facts-per-server; T-007 stays tight at six-operational-disciplines.
- **Estimated wall-clock**: external research runs all 7 in parallel up to the orchestrator's parallelism cap (default ≤6 per ADR-0021). T-007 can either ride in a batch with 5 of T-001..T-006, with the 7th in a second batch; or the orchestrator can raise the parallel cap to 7 for this Gate. Per-topic acceptance criteria are tight. Codebase research is single-instance, modest-to-medium (the Pattern archaeology subsection adds maybe 30 minutes of focused reading on top of v1). Plausible total wall-clock: external in parallel (≈1 unit) + codebase (≈1 unit, slightly longer than v1) ≈ 2 units concurrent.

## Open questions for human resolution

Surface at the Research Plan Approval Gate. User answers update the Plan before research begins.

- **OQ-1 (v1 carried forward) — Is the now-7-topic external budget appropriate, or should it be reduced?** The Plan exceeds the default ADR-0021 cap of 6 to admit T-007 (operational discipline), which is the v2-scope-expansion centerpiece. Candidates for further reduction if needed: combining T-005 (Context7) + T-006 (Exa) into a single "remote-HTTP MCPs auth + transport" topic, accepting a less precise per-server answer — that brings the total to 6 with T-007 included. **Default if no answer**: proceed with 7 topics (the operator's Gate-3 feedback explicitly added the operational concerns; reducing T-007 is regressive).

- **OQ-2 (v1 carried forward) — UI-6: Does `auditing-mcp` (no-BLOCKER) become a *formal* Gate 6 acceptance criterion?** Human / pipeline-operator decision; not research-resolvable. **v2 wrinkle**: FR-11-c augments `auditing-mcp` with new operational checks (lifecycle-health-script audit, runtime-log-redaction audit, trifecta-consistency audit). If the answer is "formal," all three new audit families also become Gate 6 release-blockers — a non-trivial implication. **Default if no answer**: defer to Design Composition / Plan Authoring gate.

- **OQ-3 (v1 carried forward) — UI-8: Confirm Serena is still wanted at project scope on this markdown-heavy repo, before Design.** Per PRD Q4 ("all six always-on"), Design cannot unilaterally drop Serena, but the Intent Clarification + PRD invite reconfirmation. **Default if no answer**: research proceeds; operator confirms at Design Composition gate.

- **OQ-4 (v1 carried forward) — Are there in-repo prior-art references to *any* of the six servers that the plan-author missed?** Codebase research will grep for each server name; an operator-known reference saves a cycle. **Default if no answer**: rely on the grep result.

- **OQ-5 (new in v2) — Does the FR-8 lifecycle health check extend the existing `onCreateCommand` (currently the verification command `claude --version && python3 --version && node --version && gh --version`), replace it, or run alongside it as a separate hook?** The PRD names `postCreate` / `postStart` / `postAttach` as the integration points (FR-8) and confirms the existing `onCreateCommand` shall not be broken (A-5), but does not state which composition pattern to use. This affects Design (UI-9 — lifecycle-hook strategy) and may affect Plan sequencing (whether the existing verification line is split, refactored, or untouched). The codebase researcher will record the current hook contents so Design has the data; the operator's preference (extend vs separate vs replace) would let Design pick a default. **Default if no answer**: research proceeds; `design-codespaces` proposes a default at Design Composition for operator review.
