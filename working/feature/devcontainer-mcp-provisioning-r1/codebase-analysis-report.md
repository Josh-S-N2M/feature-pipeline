---
id: CA-devcontainer-mcp-provisioning-r1
doc_type: codebase-analysis-report
version: 1.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
sibling_json: working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json
generated: 2026-05-23T00:00:00Z
generated_by: discovery-codebase-researcher
extraction_method: manual-grep-and-read (NEITHER GitNexus NOR codebase-memory-mcp configured — this feature provisions them)
commit: cf48e5e20602c9d3cb6f264c443aff4be027911e
---

# Codebase Analysis Report — devcontainer-mcp-provisioning-r1

## Executive summary

This is the discovery-codebase-research output for the seven-server MCP provisioning feature. The codebase is a markdown-heavy (73.8%) discipline-and-tooling repo with 36 sub-agent specs, 36 skills (organized as three What/How/Audit trifectas plus standalones), and a thin devcontainer surface. **Neither GitNexus nor codebase-memory-mcp is currently configured** — `.mcp.json` is confirmed absent, meaning the `discovery-codebase-researcher` agent's own bootstrap check ("at least one MCP must be available — surface as a blocking error if neither is") would fail by definition until this feature ships. The primary/fallback wiring is expressed entirely in **prose** across four layers (ADR-0007 in `adrs-migrated/`, ADR-0018 in `adrs/`, `KB-codebase-research/SKILL.md`, and `discovery-codebase-researcher.md`) with **zero structured frontmatter** anywhere — the load-bearing UI-15 finding. The three existing W/H/A trifectas show a strong, consistent shape that `KB-mcp-platform` + `KB-mcp-design` can mirror.

## Component inventory

### Touch-point files (current state)

| Path | Lines | State | Role this feature plays |
|---|---|---|---|
| `.devcontainer/Dockerfile` | 19 | Real | Will extend with install layers for GitNexus, Terraform MCP, Serena (per UI-16 / UI-2 / T-001) |
| `.devcontainer/devcontainer.json` | 70 | Real, uses ONLY `onCreateCommand` | Will add `postCreate` / `postStart` / `postAttach` lifecycle hooks (per FR-8); `postCreate`/`postStart`/`postAttach` are all unused today |
| `.mcp.json` | — | **ABSENT** | Created by this feature with seven server entries |
| `.claude/agents/discovery-codebase-researcher.md` | 157 | Real | `tools:` allowlist gains GitNexus (and codebase-memory-mcp) entries; primary/fallback expression convention is the UI-15 decision |
| `.claude/skills/KB-codebase-research/SKILL.md` | 247 | Real, single-file | Cross-referenced from `KB-mcp-platform` (not duplicated); names GitNexus + codebase-memory-mcp |
| `.claude/skills/auditing-mcp/` | SKILL + 4 refs + 4 scripts + 2 examples | Real | Augmented with per-server rules (incl. GitNexus) and operational-health rules per FR-11-c |
| `adrs/ADR-0018-codebase-analysis-schema.md` | 215, v1.0.0 | Real but version-drifted (KB+agent say v1.1.0; ADR says v1.0.0) | Read for primary/fallback policy cross-reference |
| `adrs-migrated/ADR-0007-code-graph-mcp-selection.md` | v2.2.0 | Real — canonical source-of-truth for primary/fallback decision | Read; not modified |

### Sub-agent inventory

**36 agent files** in `.claude/agents/`. All conform to a shared frontmatter convention (`name`, `description`, `tools`, `model`, `effort`, `skills`, `memory`). **No agent currently has any `mcp__<server>__<tool>` entry in its `tools:` allowlist** — verified by `grep -rn "mcp__" .claude/agents/` returning zero hits. The seven-server feature introduces the `mcp__` pattern to this repo for the first time.

Inferred likely-consumer mapping (input for UI-1):

| MCP server | Likely consumer agent(s) |
|---|---|
| **GitNexus** | `discovery-codebase-researcher` (PRIMARY per ADR-0007 v2.2.0); `review-architecture-auditor` (also names it as primary per agent body line 23) |
| **codebase-memory-mcp** | `discovery-codebase-researcher` (FALLBACK); `review-architecture-auditor` (FALLBACK) |
| Serena | `discovery-codebase-researcher` (symbol-level value contingent on UI-8 narrowing — repo is markdown-heavy) |
| mcp-openapi-schema | `design-api` |
| actionlint-mcp | `design-cicd` |
| HashiCorp Terraform MCP | `design-iac` |
| Context7 | `discovery-external-researcher` (also a documentation-lookup fallback for `KB-cc-platform/SKILL.md:109`) |
| Exa | `discovery-external-researcher` |

### Trifecta inventory

| Trifecta | Platform half | Design half | Audit half | Audit status |
|---|---|---|---|---|
| Claude Code | `KB-cc-platform/` (7 refs + 9 templates) | `KB-cc-design/` (2 refs) | `auditing-cc-configs/` (FAMILY COORDINATOR; 6 refs + 6+ scripts) | Complete; name has trailing `-configs` |
| Codespaces | `KB-codespaces-platform/` (10 refs + 5 templates incl. subdirs) | `KB-codespaces-design/` (2 refs) | `auditing-codespaces/` | **STUB** per ADR-0033 |
| GitHub Actions | `KB-github-actions-platform/` (19 refs + 21 templates) | `KB-github-actions-design/` (2 refs) | `auditing-github-actions/` (1 ref + 1 script; uses `auditing-shared` per ADR-0031) | Complete |
| **MCP (this feature)** | **KB-mcp-platform (NEW)** | **KB-mcp-design (NEW)** | **`auditing-mcp/`** (4 refs + 4 scripts + 2 examples; augmented per FR-11-c) | Audit half exists; platform+design are greenfield |

## Dependency map

```
                                              ┌──────────────────────────────┐
                                              │ adrs-migrated/ADR-0007 v2.2  │
                                              │ (CANONICAL: GitNexus primary │
                                              │  codebase-memory fallback)   │
                                              └────────────┬─────────────────┘
                                                           │ (prose ref ×4)
                                                           ▼
┌──────────────────────────┐   prose ref ×8    ┌──────────────────────────┐
│ KB-codebase-research/    │◄──────────────────│ adrs/ADR-0018 v1.0.0     │
│ SKILL.md                 │                   │ (declares schema v1.0;   │
│                          │                   │  agent+KB say v1.1 —     │
│ (declares schema v1.1.0  │                   │  drift!)                 │
│  inline at body)         │                   └──────────────────────────┘
└────────────┬─────────────┘
             │ skills: [KB-codebase-research]
             ▼
┌────────────────────────────────────┐
│ discovery-codebase-researcher.md   │  prose×4   ┌─────────────────────┐
│ tools: [Read, Glob, Grep,          │  ────────► │ GitNexus MCP        │
│         Bash(*), Write, Task*]     │            │ (NOT YET REGISTERED)│
│ skills: [KB-codebase-research]     │            └─────────────────────┘
│                                    │  prose×4   ┌─────────────────────┐
│ NO mcp__ ENTRIES TODAY             │  ────────► │ codebase-memory-mcp │
└──────────────┬─────────────────────┘            │ (NOT YET REGISTERED)│
               │                                  └─────────────────────┘
               ▼
┌──────────────────────────┐
│ .mcp.json (ABSENT)       │ ◄── EVERY Claude Code session reads this (when present)
└──────────────────────────┘
               │ (auto-load)
               ▼
┌──────────────────────────┐
│ .devcontainer/           │
│   devcontainer.json      │ only onCreateCommand used today;
│   Dockerfile (19 lines)  │ postCreate/postStart/postAttach all available
└──────────────────────────┘
```

Key relationships:

- The primary/fallback wiring is a **four-layer prose chain**: ADR-0007 (canonical) → ADR-0018 (cross-ref) → KB-codebase-research (consumer skill) → discovery-codebase-researcher (consumer agent). No structured field anywhere.
- The `auditing-mcp` skill explicitly declares membership in the `auditing-cc-configs` family (`SKILL.md:30`).
- `auditing-github-actions` consumes `auditing-shared` per ADR-0031 (canonical helper home).
- Both code-graph MCPs are **referenced** in seven existing corpus files but **registered** in zero (`.mcp.json` is absent).

## Blast-radius summary

| Touch point | 1-hop | 2-hop | 3+-hop | Risk profile |
|---|---|---|---|---|
| `.mcp.json` (new file, 7 servers) | 6 | 8 | 12 | UNIVERSALLY shallow but UNIVERSALLY broad — every session reads it. Typo = every session broken. |
| `discovery-codebase-researcher.md` tools allowlist | 2 | 3 | 8 | Convention-introduction event: first agent to carry `mcp__` entries. Whatever pattern lands becomes the de-facto convention. |
| `.devcontainer/Dockerfile + devcontainer.json` lifecycle hooks | 4 | 6 | 15 | Historically fragile surface (twice-fixed recently). Seven-server install adds substantial layer count + toolchain constraints (no Go, no DinD for GitNexus + Terraform MCP). |
| `auditing-mcp/` augmentation | 2 | 3 | 5 | Adds per-server (incl. GitNexus) rules + operational-health rules. Stretches scope from "config audit" to also "runtime audit" — see open question #4. |
| NEW: `KB-mcp-platform/` + `KB-mcp-design/` | 3 | 3 | 4 | Greenfield. Must conform to trifecta-platform-half / trifecta-design-half conventions. |
| GitNexus primary / codebase-memory fallback wiring on the agent file (UI-15 specific) | 2 | 2 | 3 | CONVENTION DECISION POINT. Existing convention is pure prose; new structured frontmatter would be unprecedented. |

## Conventions observed per layer

### Claude Code / Project Filesystem

- **Agent file frontmatter**: `name` + `description` required; `tools`, `model`, `effort`, `skills`, `memory` are common. **No agent currently carries any `mcp__` tool entry.**
- **`tools:` field syntax**: mixed — both bracketed array form (`tools: [Read, Glob, Grep, ...]`) and comma form (`tools: Read, Grep, Glob, ...`). Bash restrictions use `Bash(name:*)` or `Bash(name *)` — also mixed.
- **MCP tool naming convention** (from `KB-cc-platform/references/extensions.md:364`, `configuration.md:79`, `integrations.md:165`, `assets/templates/mcp-config.json.example:65`): `mcp__<server>__<tool>` for specific tools; `mcp__<server>` for whole-server permission grants. Documented but **not yet used** in any agent file.
- **Skill directory convention**: per ADR-0020 — `KB-<topic>-platform/`, `KB-<topic>-design/`, `auditing-<topic>/`. The `name:` field in frontmatter is lowercase-hyphenated. One naming deviation: `auditing-cc-configs` (trailing `-configs`).
- **Primary/fallback expression convention**: **DOES NOT EXIST AS A STRUCTURED CONVENTION TODAY.** Pure prose, four layers (ADR-0007 → ADR-0018 → KB-codebase-research → discovery-codebase-researcher). UI-15 is choosing whether to introduce structure.

### Dev Environment (Codespaces / Devcontainer)

- **Lifecycle hooks in use**: only `onCreateCommand` (a verification command: `claude --version && python3 --version && node --version && gh --version`). `postCreate`, `postStart`, `postAttach`, `updateContent` all **unused** and available.
- **Feature pin policy**: **mixed and inconsistent**. `common-utils:2` major-pinned; `github-cli:1` with `version: "latest"`; `node:1` with `version: "lts"`; `claude-code:1` major-pinned. No exact-version pin in use. UI-5 finding: there is no consistent pin policy to inherit.
- **Secrets surface**: `containerEnv` currently holds only `EDITOR` and `PAGER` (non-secret). Empty of credentials — confirms NFR-2-a baseline.
- **Image base**: `mcr.microsoft.com/devcontainers/python:1-${PYTHON_VERSION}-bookworm` (PYTHON_VERSION=3.11).
- **Recent fragility**: commit `5e7f4ac` fixed a base-image stale-Yarn-key build failure. The surface has demonstrated breakability.

### Skill trifecta structure (W/H/A pattern archaeology, per FR-11)

| Dimension | Platform half | Design half | Audit half |
|---|---|---|---|
| SKILL.md size | Large (multi-section) | Slim | Mid |
| `references/` files | Many (KB-cc=7, KB-codespaces=10, KB-gha=19) | **Exactly 2: `patterns-and-anti-patterns.md`, `principles.md`** (STRONG convention) | Variable (auditing-mcp=4, auditing-gha=1, auditing-codespaces=0) |
| `assets/templates/` | Yes (KB-cc=9 .example, KB-codespaces=5, KB-gha=21) | **None** (STRONG convention) | Sometimes (auditing-cc-configs has `triage-prompt.txt`) |
| `scripts/` | None at platform half today (per ADR-0031 relocation) | **None** | **Yes** (Python audit scripts) |
| `examples/` | None | None | Sometimes (auditing-mcp has good/bad-MCP-annotated.md) |
| `pedagogical_sections` count | Highest (KB-gha=8) | Lowest (KB-cc-design=1) | Mid |
| Cross-reference style | `description` ends with "Pairs with KB-<sister>-design" | `description` ends with "Pairs with KB-<sister>-platform" | Body line declaring family ("This skill is part of the auditing-cc-configs family") |
| Naming | `KB-<topic>-platform` | `KB-<topic>-design` | `auditing-<topic>` (one deviation: `auditing-cc-configs`) |

**Strong conventions to mirror for `KB-mcp-platform` + `KB-mcp-design`:**
1. Design halves carry **exactly two** references files named `patterns-and-anti-patterns.md` + `principles.md`. No `assets/`, no `scripts/`.
2. Platform halves carry many references files (topic-specific) + `assets/templates/` with example artifacts.
3. Frontmatter `description` ends with a sister cross-reference.
4. Frontmatter `name:` is lowercase-hyphenated (e.g., `kb-mcp-platform`, `kb-mcp-design`).
5. `pedagogical_sections` frontmatter list per ADR-0030, with substance-justified strings.

### File composition

- Total non-git, non-node_modules files: **634**.
- Markdown (`.md`): 468 (**73.8%**) — confirms repo is markdown-heavy.
- Python (`.py`): 52, concentrated in `.claude/skills/auditing-*/scripts/`.
- YAML (`.yml`): 21 — mostly `KB-github-actions-platform/assets/templates/` workflow templates.
- Shell (`.sh`): 8.
- `.example`: 8 — `KB-cc-platform/assets/templates/`.

Implication for UI-8: Serena's symbol-level value is **thin** on this repo (no application source code; symbol density is in 52 Python audit scripts only). GitNexus is similarly a TS-first tool reading a markdown-heavy corpus — but is nonetheless designated canonical per ADR-0007 v2.2.0.

### Log surface

- `.devcontainer/`: **no existing log surface** (grep for log/tail/rotat returned zero hits).
- `.claude/`: no operator-runtime log surface. Python audit scripts use stdout (subprocess JSON output). One file named `auditing-shared/scripts/log_state_transition.py` exists but is a pipeline-state-transition logger, not an MCP runtime log.

**Implication for FR-10 / UI-12**: greenfield. No log-rotation, log-tail, or log-path convention to reuse. UI-12's Design choice is unconstrained by existing pattern.

## Known issues / caution areas

1. **ADR-0018 schema version drift (medium severity).** ADR-0018 declares schema v1.0.0; `KB-codebase-research/SKILL.md`, `discovery-codebase-researcher.md`, and the research plan all reference v1.1.0 with a blast-radius extension. The v1.1.0 SHAPE lives in the KB only. Worth surfacing to `design-composer` and `review-architecture-auditor` (whose grounding is split).
2. **ADR-0007 lives in `adrs-migrated/`, not `adrs/` (low severity).** The research plan referenced `adrs/ADR-0007*.md`, which does not exist. Five variants of ADR-0007 are in `adrs-migrated/`, with current accepted v2.2.0. Lookup convention for inherited ADRs is implicit.
3. **`tools:` field syntax inconsistency (low severity).** Both bracketed array and comma forms appear; both `Bash(name:*)` and `Bash(name *)` patterns appear. Not blocking; design-cc's UI-15 choice should pick one form for any structured additions.
4. **`auditing-codespaces` is a STUB (low severity, pre-existing).** Per ADR-0033 stub-vs-real surfacing; emits `{"stub": true, "findings": []}`. This feature's devcontainer-layer changes therefore have no family-auditor backstop beyond what `auditing-cc-configs` cross-file-checks already do.
5. **Recent Dockerfile fragility (medium severity).** Commit `5e7f4ac` fixed a base-image stale-Yarn-key failure. Adding seven-server install layers (plus GitNexus and Terraform MCP, both with toolchain constraints) materially increases the failure surface. Incremental, rollback-friendly authoring is warranted.

## Pattern-archaeology summary table — W/H/A trifecta conventions

| Convention dimension | What `KB-mcp-platform` should do | What `KB-mcp-design` should do | What `auditing-mcp` (augmented) should do |
|---|---|---|---|
| Frontmatter `name` | `kb-mcp-platform` | `kb-mcp-design` | `auditing-mcp` (already correct) |
| `description` last clause | "Pairs with KB-mcp-design" | "Pairs with KB-mcp-platform" | "Part of the auditing-cc-configs family" (already correct) |
| `references/` files | Topic-specific (transports.md, lifecycle.md, credential-surfaces.md, logging.md, troubleshooting.md, etc.) | Exactly two: `patterns-and-anti-patterns.md` + `principles.md` | Add per-server (incl. GitNexus) and operational-health refs |
| `assets/templates/` | Yes — at minimum a seven-server `.mcp.json.example`; possibly health-check-script.sh.example, runtime-log-tail.sh.example | None | None (existing `examples/` carries good/bad-MCP-annotated.md fixtures) |
| `scripts/` | None (per ADR-0031 — audit scripts live in audit half) | None | Yes — extend existing four scripts; potentially add per-server validators + operational-health checkers |
| `pedagogical_sections` | Multi-entry list with substance-justified strings (per ADR-0030) | 1+ entry minimum (`patterns-and-anti-patterns.md`) | Already populated; extend for any new references files |
| `allowed-tools` | `Read, Grep, Glob, WebFetch` (mirroring KB-codespaces-platform) | `Read, Grep, Glob` (mirroring KB-cc-design / KB-codespaces-design / KB-github-actions-design) | Already correct: `Read Grep Glob Bash(python3 *)` |

## Open questions for human resolution

1. **ADR-0018 schema version drift** — is the v1.0.0/v1.1.0 mismatch intentional pending an ADR revision, or should this feature include the increment? Blocks design-composition-completion.
2. **ADR-0007 location** — is `adrs-migrated/` the canonical location for inherited ADRs that have been migrated, and should the research plan's path references be updated? Blocks design-composition-completion.
3. **Agent inventory scope for UI-1** — are the 36 agent files all in-scope, or are some (esp. the six `synth-*` files) deprecated and excluded from MCP wiring consideration? Blocks design-cc-completion.
4. **Audit scope expansion** — should the augmented `auditing-mcp` add operational-health rules (lifecycle, runtime log, secret redaction) as new dimensions in its existing 10-dimension routing table, or should those land in a sibling runtime-audit skill while `auditing-mcp` stays config-focused? UI-14 question. Blocks design-cc-completion.
5. **`KB-mcp-platform` template duplication** — `KB-cc-platform/assets/templates/mcp-config.json.example` already exists. Should `KB-mcp-platform` duplicate it (with seven-server shape) or cross-reference? UI-13 question. Blocks design-cc-completion.

## Specific recommendations for Design

1. **Pick one convention for the primary/fallback expression at UI-15.** The current state is pure prose across four layers, with zero structured frontmatter. The two endpoints are (a) leave it as prose (lowest convention drift; harder to audit mechanically) or (b) introduce a structured frontmatter field (e.g., `mcp_primary:` / `mcp_fallback:`) on agent files (unprecedented; cleanly auditable by extended `auditing-mcp` per UI-14).
2. **Mirror the trifecta-design-half convention exactly** for `KB-mcp-design`: slim SKILL.md, `references/` with exactly two files named `patterns-and-anti-patterns.md` and `principles.md`, no `assets/`, no `scripts/`.
3. **Add `mcp-config-seven-servers.json.example` to `KB-mcp-platform/assets/templates/`** rather than mutating `KB-cc-platform/assets/templates/mcp-config.json.example` — keep the generic shape in `KB-cc-platform` and the topic-specific seven-server shape in `KB-mcp-platform`. Cross-reference both ways.
4. **Treat the devcontainer surface as fragile.** Recent Dockerfile failure (commit `5e7f4ac`) demonstrates the base image's instability. Author install layers incrementally and rollback-friendly; constrain GitNexus and Terraform MCP install paths to mechanisms that work without Go toolchain and without Docker-in-Docker (per PRD-v3 Technical Considerations + UI-16 + T-004/T-008 inputs).
5. **Use the unused lifecycle hooks for FR-8 without overloading `onCreateCommand`.** `postCreate` / `postStart` / `postAttach` are all available. Composing health-checks with the existing verification `onCreateCommand` is straightforward; the latter can stay narrow (toolchain verification) while the former owns MCP-status reporting.
6. **The augmented `auditing-mcp` needs a per-server rules section.** Today's 10-dimension routing table is server-agnostic. Per FR-11-c AC, the augmented skill must include GitNexus rules specifically; per the convention extracted under Pattern archaeology, the rules belong in `references/per-server-rules.md` or analogous, with the existing `mcp-spec.md` / `toxic-combinations.md` / `anti-patterns.md` / `common-failures.md` reference set extended in place.
7. **Carry forward the family-membership declaration prose pattern.** When the augmented `auditing-mcp` adds new rules referencing operational health, the existing body-line-30 family declaration (`auditing-cc-configs` parent) stays. Optionally add a body line declaring "Operational-health rules consume `auditing-shared`" if any of those rules use shared helpers per ADR-0031.
8. **Plan for the absent log surface (UI-12).** No log-rotation, log-tail, or log-path convention exists. Greenfield choices should err on the side of operator-readable plain-text files in a documented location (e.g., `/tmp/mcp-logs/<server>.log`) with redaction at write-time per AC-FR-10-d.
9. **Surface the schema-version drift to `design-composer` and `review-architecture-auditor` proactively.** They will both read this analysis JSON and compare against ADR-0018 v1.0.0; the v1.1.0 shape carried in `KB-codebase-research/SKILL.md` is what this analysis actually conforms to. An ADR-0018 increment is a candidate consequence of this feature even though it's not strictly in scope.
10. **Use `KB-mcp-platform/SKILL.md` to cross-reference KB-codebase-research rather than restating its policy.** The primary/fallback policy is named in three corpus sites already; a fourth restatement compounds drift risk. Cross-reference and let `KB-codebase-research/SKILL.md` remain the consumer-side discipline KB.
