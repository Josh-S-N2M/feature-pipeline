---
id: ADR-0007
version: 1.1.0
status: Superseded by ADR-0007 v2.1.0
generated: 2026-05-12
generated_by: synth-designer (retroactive template migration per ADR-0014)
supersedes:
  - {id: ADR-0007, version: 1.0.0}
superseded_by:
  - {id: ADR-0007, version: 2.1.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0005 (append-only supersession)
applies_to:
  - feature-pipeline (historical reference; superseded by v2.1.0)
template_format: per ADR.txt v1.0
---

# ADR-0007 (v1.1, template-migrated): Code-graph MCP selection — codebase-memory-mcp as primary, locus as fallback

## Status

Superseded — original Accepted 2026-05-12; superseded by ADR-0007 v2.0.0 on user feedback about license filter; template-migrated to v1.1.0 on 2026-05-12 per ADR-0014.

This version is preserved for historical reference. **Active version: ADR-0007 v2.x.x** (template-migrated to v2.1.0 in the same batch).

## Context

Blueprint v2 ADR-0001 commits the pipeline to using a code-graph MCP for blast-radius analysis in Critique-1 and codebase research in Stage 3. The original substrate-map (D-0008, D-0009) named locus as the recommended choice based on first-round research. Second-round research surfaced additional candidates with materially different tradeoffs that warrant revisiting the selection and locking it down in an ADR.

This v1 selected based on a filter (commercial-use license) that was subsequently clarified by user feedback to not be a hard constraint. The v2 reasoning therefore differs materially.

## Decision

**Primary: `codebase-memory-mcp` (DeusData)**

**Recommended fallback: `locus`** for cases where codebase-memory-mcp fails to index, or where the user's stack overlaps locus's bundled LSP set well (Go/Python/Rust/TS-JS/C-C++).

**Explicitly NOT recommended: GitNexus** — PolyForm Noncommercial license prohibits commercial use without paid enterprise tier. The pipeline must work in commercial settings; license-restricted dependencies are blast-radius hazards of their own.

(This v1 decision was reversed in v2 after user clarification that commercial-use is not a hard constraint.)

## Decision Details

| Item | Content |
|---|---|
| Decision | codebase-memory-mcp as primary; locus as fallback; GitNexus rejected on license grounds. |
| Why now | Code-graph MCP selection blocks critique-1-knowledge content authoring and stage-3 codebase research design. |
| Why this | Direct alignment between codebase-memory-mcp's hop-tier risk output and the pipeline's blast-radius semantics; 155-language coverage; MIT license; static binary minimizing setup friction. Locus's LSP-backed depth makes it a useful fallback. |
| Known unknowns | Whether codebase-memory-mcp's documented Cypher bugs (April 2026, issues #237-#254) are stable enough for production reliance; whether the 155-language tree-sitter quality is uniform. |
| Kill criteria | Replaced by v2 after user clarification that commercial-use license is not a filter. v2 swaps primary/fallback in light of the corrected constraint set. |

## Rationale

The v1 reasoning weighed three filters: (a) blast-radius semantic alignment, (b) language coverage, (c) license. With the license filter, GitNexus's strengths (ecosystem maturity, Claude Code integration depth) were not visible because PolyForm Noncommercial disqualified it for commercial users.

codebase-memory-mcp's hop-tier risk output (CRITICAL hop-1, HIGH hop-2, MEDIUM hop-3, LOW hop-4+) is a direct semantic match for the pipeline's multi-turn blast-radius framing — no translation layer required.

This reasoning is preserved in v1.1.0 (this file) for historical reference. The license filter was relaxed in v2, reordering primary/fallback.

## Options Considered

(Original options preserved verbatim from v1.0.0; see pre-migration file for full alternatives content.)

**Selected (in v1.0.0):** codebase-memory-mcp as primary, locus as fallback.

**Rejected (in v1.0.0):** GitNexus (license), code-review-graph (narrower coverage), CodeGraphContext (regex fallback hazard), syms (file-level only), MRCIS (smaller surface).

## Consequences

(Original consequences preserved verbatim from v1.0.0; see pre-migration file.)

### Positive Consequences

- Aligns blast-radius semantics 1:1 with risk tiers Critique-1 needs.
- 155-language coverage minimizes "user's stack outside our support" failure mode.
- MIT license enables commercial use.
- Static binary minimizes setup friction.

### Negative Consequences

- codebase-memory-mcp has documented Cypher bugs (April 2026, issues #237-#254).
- Vendor benchmarks unverified independently.
- 155-language claim assumes uniform tree-sitter grammar quality (not guaranteed).

### Neutral Consequences

- The code-graph MCP space is fast-moving. Revisited in 6 months (this happened immediately in v2 after the license-filter clarification).

## Architecture Impact

**Components that change (in v1.0.0; superseded in v2):**
- codebase-memory-mcp configured as primary in `.mcp.json`.
- locus configured as fallback.
- critique-1-knowledge skill consumes hop-tier risk output directly.

**Architectural constraints added:**
- GitNexus rejected as primary on license filter (subsequently reversed in v2).

**Architectural constraints removed:**
- N/A in v1.0.0 context.

## Implementation Guidance

See pre-migration file (`ADR-0007-code-graph-mcp-selection-v1-pre-template-migration.md`) for the original Configuration section and Tools-the-pipeline-uses subsection. Both are preserved verbatim there.

## Related Information

- Pre-migration version: `ADR-0007-code-graph-mcp-selection-v1-pre-template-migration.md` (v1.0.0 content).
- Superseding version: ADR-0007 v2.x.x — `ADR-0007-code-graph-mcp-selection.md`.
- ADR-0014: retroactive template migration that produced this v1.1.0.
- Claims: C-R2-0019 through C-R2-0022.
