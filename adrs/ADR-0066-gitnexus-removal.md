---
id: ADR-0066
version: 1.0.0
status: Accepted
generated: 2026-05-27
generated_by: human-directed-surgical-edit
supersedes: []
adrs_inherited:
  - {id: ADR-0007, version: 2.2.0}
applies_to:
  - feature-pipeline (project-wide)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Removes the gitnexus MCP server from the project's active server inventory. Empirical use revealed reliability and usability problems that made the server "broken and unusable" in practice; ADR-0007's documented fallback to Read+Grep+Glob + serena symbol tools now applies as the canonical posture for the two dependent sub-agents. The ADR-0007 selection decision is now moot for active use.
---

# ADR-0066: Remove the gitnexus MCP Server

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Consequences
- [x] Cross-References

## Status

Accepted — 2026-05-27

## Update History

| Version | Date | Change | Driver |
|---|---|---|---|
| 1.0.0 | 2026-05-27 | Initial ADR authored alongside the surgical removal of all live gitnexus references from production configuration. | User report: gitnexus is "broken and unusable" in practice. |

## Context

`gitnexus` was selected as the project's primary code-graph MCP server in ADR-0007 v2.x. The selection was a theoretical-fit decision based on the server's published capability surface (code graph, blast-radius queries, symbol-level call traversal). The fallback documented in ADR-0007 was Read+Grep+Glob plus serena's symbol-level MCP tools, scoped to the same two sub-agents (`discovery-codebase-researcher`, `review-architecture-auditor`).

Empirical use over the lifetime of the project revealed reliability and usability problems that the selection-time analysis did not surface:

- The PreToolUse augment hook conflicted with the long-lived MCP server's KuzuDB lock (issue #1492 upstream), requiring a project-wide `GITNEXUS_DISABLE_PRETOOL_AUGMENT_WHEN_MCP=1` workaround.
- The optional tree-sitter grammar set required calibration machinery (FR-4b, ADR-0058) to confirm `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` honored its contract.
- The post-install warm step (`npx gitnexus setup` + `npx gitnexus analyze`) added 30–120 s of postCreate cost and was brittle on rebuilds.
- Index staleness behaviour required a PostToolUse hook to keep the index fresh; the hook itself added per-call latency and a separate set of failure modes.
- In actual use, agents reported "no indexed repositories," empty result sets on known-good queries, and intermittent transport disconnects.

The user reported the cumulative effect as: gitnexus is "broken and unusable" in practice.

## Decision

Remove the `gitnexus` MCP server from the project's architecture.

The five MCP servers that remain in the active inventory: `actionlint-mcp`, `context7`, `exa`, `serena`, `terraform-mcp`.

## Decision Details

The removal touches the following surfaces:

| Surface | Action |
|---|---|
| `.mcp.json` | Removed the `gitnexus` server entry. |
| `.claude/settings.json` | Removed the `mcp__gitnexus__*` permission allow rule; removed the two `~/.claude/hooks/gitnexus/gitnexus-hook.cjs` PreToolUse / PostToolUse hooks. |
| `.devcontainer/devcontainer.json` | Removed the `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, `GITNEXUS_DISABLE_PRETOOL_AUGMENT_WHEN_MCP`, `_GITNEXUS_1492_TRACKER`, and `GITNEXUS_TAG` containerEnv entries. |
| `.devcontainer/postCreate.sh` | Removed the `install_gitnexus`, `gitnexus_post_install_warm`, `_fr4a_check` (FR-4a pre-flight), and `_fr4b_calibration_banner` (FR-4b staleness) functions and their call sites. The OSS-local install count moved from 4 to 3. |
| `.devcontainer/postStart.sh` | Updated the expected-server count from 6 to 5. |
| `.devcontainer/versions.env` | Removed `GITNEXUS_TAG`. |
| `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` | Deleted. |
| `.github/workflows/gitnexus-grammar-skip-calibration.yml` | Deleted. |
| `.claude/skills/gitnexus/` | Entire directory deleted (six sub-skills: gitnexus-cli, gitnexus-debugging, gitnexus-exploring, gitnexus-guide, gitnexus-impact-analysis, gitnexus-refactoring). |
| `.claude/skills/KB-mcp-platform/references/gitnexus-and-fallback.md` | Deleted. |
| `.claude/skills/auditing-mcp/scripts/audit_op8_gitnexus.py` | Deleted. OP-8 audit rule retired. |
| `.claude/skills/auditing-mcp/scripts/audit_mcp.py` | Removed the OP-8 dispatch entry. |
| `.claude/agents/discovery-codebase-researcher.md` | Removed `mcp__gitnexus__*` from frontmatter `tools:`; updated body procedure to use Read/Grep/Glob + serena symbol tools. |
| `.claude/agents/review-architecture-auditor.md` | Same treatment as the discovery agent. |
| `AGENTS.md` (and the symlinked `CLAUDE.md`) | Removed the entire "# GitNexus — Code Intelligence" section, the gitnexus rows from the matrix and sub-agent delegation tables, and updated the server count to five. |
| KB-mcp-platform / KB-mcp-design / KB-codebase-research / KB-review-disciplines / KB-documentation-criteria / recipe-feature-pipeline | Removed gitnexus-specific instructions and examples; preserved primary/fallback schema fields and historical deprecation notes; replaced traversal patterns with the Read/Grep/Glob + serena equivalents. |

The historical artifacts under `working/feature/`, `Issues/`, and `adrs/` (other than this ADR) are intentionally untouched — they are the historical record of decisions made under the prior server inventory and remain accurate as such.

## Rationale

The fallback in ADR-0007 was authored to handle exactly the empirical situation we hit: a primary code-graph server failing to deliver its theoretical capability in practice. The fallback is well-trodden (Read/Grep/Glob is the default for the rest of the codebase; serena's `find_symbol` / `find_referencing_symbols` / `get_symbols_overview` cover the symbol-level surface that gitnexus was supposed to provide). Removing gitnexus rather than continuing to patch around it reduces:

- Configuration surface (15+ files touched by gitnexus-specific provisioning).
- postCreate cost (eliminated the 30–120 s warm-up + the FR-4a pre-flight + the FR-4b staleness banner).
- Per-call hook latency (removed two `gitnexus-hook.cjs` invocations on every `Read|Grep|Glob|Bash` and every `Bash` post-call).
- Failure-mode complexity (one fewer transport, one fewer index lifecycle, one fewer calibration mechanism).

The simpler posture also reduces the number of MCP-related primary/fallback edges in the codebase, leaving only well-trodden tool fallbacks (Read/Grep/Glob).

## Consequences

**Positive:**

- The two dependent sub-agents (`discovery-codebase-researcher`, `review-architecture-auditor`) fall back to Read/Grep/Glob + serena symbol tools — the documented fallback in ADR-0007. Their work continues with the documented degraded-method provenance recorded in `codebase-analysis.json`'s `extraction_method` field (values now `serena | grep-only | mixed`).
- Removed six sub-skills under `.claude/skills/gitnexus/`, one audit rule (OP-8), one calibration script, one calibration workflow, and one KB-mcp-platform reference file (`gitnexus-and-fallback.md`).
- postCreate is now ~30–120 s faster on cold cache (no warm-up step) and significantly simpler (no FR-4a pre-flight or FR-4b staleness banner).
- The settings.json hook surface no longer fires `gitnexus-hook.cjs` on every Read/Grep/Glob/Bash invocation.

**Negative / tradeoffs:**

- Blast-radius queries that gitnexus's `analyze_impact` previously returned in a single call now require multi-step traversal via `mcp__serena__find_referencing_symbols` iterated to N hops, plus Grep for string-name references the LSP doesn't see. The auditor's `blast_radius_method` field reflects this with values `serena | manual`.
- Behavioral "how does X work?" queries lose the process-grouped result ranking gitnexus provided. The new posture is Glob → Grep → serena symbol lookup, which is structurally similar but more verbose for the agent.
- Some legacy CLAUDE.md guidance ("MUST run `gitnexus_impact` before editing") is gone. The replacement guidance is to use serena's symbol tools, which is the same discipline at a different tool surface.

**Neutral:**

- The `primary_degraded` field on `structured_failure` records is preserved in the ADR-0037 schema for any future primary/fallback registration. No active primary/fallback pair exists as of 2026-05-27.
- The `calibration_result` event type from ADR-0058 is preserved for future calibration mechanisms. The historical `fr-4b-gitnexus-grammar-skip` mechanism is retired with this ADR.

## Cross-References

- **Supersedes:** ADR-0007 v2.2.0's selection of gitnexus as the primary code-graph MCP server. The fallback policy documented in ADR-0007 remains in force; the selection is moot.
- **Related:** ADR-0041 (install-mechanism-hybrid) — the gitnexus install row in ADR-0041's per-server invocation-form table becomes deprecated per the OP-11 audit-rule convention (annotate with `[DEPRECATED INVOCATION FORM` marker).
- **Related:** ADR-0058 (calibration_result event) — the FR-4b gitnexus-grammar-skip mechanism is retired; the event schema is preserved for future mechanisms.
- **Related:** ADR-0062 (MCP tool-surface drift detection) — gitnexus is removed from any active drift-detection target list. These cross-references may need their own updates in follow-on ADRs but that is out of scope for this ADR.
