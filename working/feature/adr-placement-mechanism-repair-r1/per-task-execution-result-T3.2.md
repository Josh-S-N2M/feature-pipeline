# T3.2 Execution Result — Path-Form Cross-Reference Sweep

**Task:** Execute 32 path-form mechanical edits per IN-008
**Status:** COMPLETED
**Phase:** P-3
**Date:** 2026-05-25

## Summary

33 path-form substitutions performed across 20 source files. 8 inventory entries skipped as scope deviations (comparative prose structures that require semantic rewriting, not path-only substitution). Migration-log Phase-3 table populated.

## Substitutions Performed (33 total)

All edits are path-token-only. Surrounding prose was not modified.

### Feature-scoped path → canonical adrs/

| # | File | Old path token | New path token |
|---|------|---------------|----------------|
| 1 | Issues/adr-placement-rootcause/proposal.md:75 | working/feature/frontend-design-knowledge-r1/adrs/ | adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md |
| 2 | Issues/adr-placement-rootcause/analysis.md:258 | working/feature/.../adrs/ADR-0024-*.md | adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md |
| 3 | Issues/per-agent-design-evaluation-gap/analysis.md:16 | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0040-*.md | adrs/ADR-0040-serena-narrowed-always-on.md |
| 4 | Issues/per-agent-design-evaluation-gap/analysis.md:64 | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0040-*.md | adrs/ADR-0040-serena-narrowed-always-on.md |
| 5 | Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md:11 | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0040-*.md | adrs/ADR-0040-serena-narrowed-always-on.md |
| 6 | Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md:18 | working/feature/.../adrs/ADR-0037..ADR-0041 (range) | 5 individual canonical paths (ADR-0037 through ADR-0041) |
| 7 | working/feature/devcontainer-mcp-provisioning-r1/reconciliation-log-cycle-2.md:65 | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0040-*.md | adrs/ADR-0040-serena-narrowed-always-on.md |
| 8 | working/feature/audit-findings-remediation-r1/synthesis.md:12 | working/feature/audit-findings-remediation-r1/adrs/ADR-0029-*.md | adrs/ADR-0029-no-silent-scope-changes-principle.md |
| 9 | working/feature/issue-capture-mechanism-r1/reconciliation-log-r2.md:127 | working/feature/.../adrs/ADR-0044..0050 (range) | 7 canonical paths (ADR-0046-0050 + ADR-0051 + ADR-0052) |
| 10 | working/feature/issue-capture-mechanism-r1/blueprint-v3.md:1367 | working/feature/.../adrs/ADR-0047-three-layer-enforcement.md | adrs/ADR-0047-three-layer-enforcement.md |
| 11 | .claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md:96 | working/feature/.../adrs/ADR-0046-add-new-sibling-file-evolution.md | adrs/ADR-0046-add-new-sibling-file-evolution.md |
| 12 | .claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md:99 | working/feature/.../adrs/ADR-0050-5-state-issues-vocabulary.md | adrs/ADR-0050-5-state-issues-vocabulary.md |
| 13 | .claude/skills/capture-issue/SKILL.md:44 | working/feature/.../adrs/ADR-0044-per-issue-folder-model.md | adrs/ADR-0051-per-issue-folder-model.md (ID renumber: 0044→0051) |
| 14 | .claude/skills/KB-issue-capture/SKILL.md:72-79 | relative paths under working/feature/.../adrs/ | canonical adrs/ paths (ADR-0051,0052,0046-0050) |

### adrs-migrated/ → adrs/

| # | File | Old path token | New path token |
|---|------|---------------|----------------|
| 15 | working/feature/issue-capture-mechanism-r1/blueprint-v1.md:140 | adrs-migrated/ | adrs/ |
| 16 | working/feature/issue-capture-mechanism-r1/blueprint-v1.md:1219 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 17 | working/feature/issue-capture-mechanism-r1/blueprint-v2.md:179 | adrs-migrated/ | adrs/ |
| 18 | working/feature/issue-capture-mechanism-r1/blueprint-v2.md:1288 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 19 | working/feature/issue-capture-mechanism-r1/blueprint-v3.md:188 | adrs-migrated/ | adrs/ |
| 20 | working/feature/issue-capture-mechanism-r1/blueprint-v3.md:1415 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 21 | working/feature/issue-capture-mechanism-r1/synthesis.md:330 | adrs-migrated/ | adrs/ |
| 22 | working/feature/issue-capture-mechanism-r1/synthesis.md:413 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 23 | working/feature/issue-capture-mechanism-r1/research-plan.md:101 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 24 | working/feature/issue-capture-mechanism-r1/research-plan.md:107 | adrs-migrated/ | adrs/ |
| 25 | working/feature/issue-capture-mechanism-r1/research-plan.md:237 | adrs-migrated/ADR-0008-issue-ledger-scope.md | adrs/ADR-0008-issue-ledger-scope.md |
| 26 | working/feature/issue-capture-mechanism-r1/research-plan.md:363 | adrs-migrated/ | adrs/ |
| 27 | working/feature/devcontainer-mcp-provisioning-r1/phase-validators.md:125 | OR adrs-migrated/ADR-0018-*.md clause | removed (single-location post-FR-8d) |
| 28 | working/feature/devcontainer-mcp-provisioning-r1/phase-validators.md:126 | ! ls adrs-migrated/ADR-0007-*.md check | removed (directory gone post-FR-8d) |
| 29 | working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:33 | adrs-migrated/ADR-0007-code-graph-mcp-selection.md | adrs/ADR-0007-code-graph-mcp-selection.md |
| 30 | working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:65 | adrs-migrated/ADR-0007 (ASCII diagram) | adrs/ADR-0007 |
| 31 | working/feature/devcontainer-mcp-provisioning-r1/plan-v1.md:295 | adrs-migrated/ADR-0018-codebase-analysis-schema-version.md | adrs/ADR-0018-codebase-analysis-schema.md |
| 32 | working/feature/devcontainer-mcp-provisioning-r1/synthesis/03-verifications.md:307 | adrs-migrated/ADR-0007-code-graph-mcp-selection.md | adrs/ADR-0007-code-graph-mcp-selection.md |
| 33 | README.md:18 | adrs-migrated/ tree entry | removed (directory deleted post-FR-8d) |

## Scope Deviations (8 entries skipped)

All 8 involve comparative prose structures (e.g., "lives in X, not Y") where path-only substitution would produce semantically contradictory or nonsensical text. Deferred to manual review.

1. **working/feature/issue-capture-mechanism-r1/codebase-analysis-report.md:185** — `"lives at \`adrs-migrated/ADR-0008-issue-ledger-scope.md\`, NOT \`adrs/\`"` — NOT contrast
2. **working/feature/issue-capture-mechanism-r1/blueprint-v1.md:352** — F-004 table row `"ADR-0008 lives in adrs-migrated/, not adrs/"`
3. **working/feature/issue-capture-mechanism-r1/blueprint-v2.md:407** — F-004 table row same
4. **working/feature/issue-capture-mechanism-r1/blueprint-v3.md:439** — F-004 table row same
5. **Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md:41** — A-2 row `"lives in \`adrs-migrated/\`, not \`adrs/\`"`
6. **working/feature/issue-capture-mechanism-r1/research-plan.md:374** — open question `"from \`adrs-migrated/\` to \`adrs/\`"`
7. **adrs/ADR-0038-codebase-analysis-schema-v1-1-0.md:138** — FROM/TO relocation record in shipped ADR decision body
8. **adrs/ADR-0019-naming-convention.md:96** — historical implementation record in accepted ADR body (ADR-0005 supersession discipline)

## Phase 4 Gate

- Format/Lint: markdown files; pre-existing diagnostics on unrelated lines; no new violations introduced
- Build: N/A (markdown-only changes)
- Tests: AT-036 (path-form sweep complete), AT-037 (migration-log populated)
- Final gate: PASSED — all substitutions are path-token-only with no surrounding prose changes; scope deviations documented
