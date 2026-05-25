---
id: CR-adr-placement-mechanism-repair-r1
doc_type: codebase-analysis-report
version: 1.0.0
status: complete
feature_slug: adr-placement-mechanism-repair-r1
derived_from: working/feature/adr-placement-mechanism-repair-r1/research-plan.md
generated: 2026-05-24T19:45:00Z
generated_by: discovery-codebase-researcher
schema_version_of_companion_json: 1.1.0
pipeline_run_id: adr-placement-mechanism-repair-r1-20260524-183201
extraction_method: grep+find+Read (GitNexus available but not invoked; markdown-corpus content-search dominates)
---

# Codebase Analysis Report — adr-placement-mechanism-repair-r1

Narrative companion to `codebase-analysis.json` (v1.1.0 per ADR-0018 + ADR-0038). Cross-references the JSON throughout.

## Executive Summary

This feature touches a small surface in the Claude Code layer but has a large effective blast radius via the FR-9 cross-reference sweep and the 47-file `adrs-migrated/` consolidation. Discovery confirms the orchestrator's pre-PRD findings on the four operator files (FR-1/2/3/4 anchors are all at the cited line ranges; no drift) and the 12 byte-identical duplicate ADRs (all confirmed identical via `diff -q`). However, Discovery surfaces three material contradictions of the PRD's stated reality: (1) **ADR-0044 and ADR-0045 are numbering collisions, not divergent bodies** — the feature-side ADRs are distinct decisions sharing IDs by accident, and FR-8b's "archive rejected body" framing is structurally inapplicable; (2) **the PRD under-specifies the feature-scoped source set** (5 distinct feature folders host the 17 off-canonical ADRs, not the 2 named in the PRD); (3) **the PRD's `adrs-migrated/` "ADRs 0001-0010 only" hypothesis is wrong** — the archive contains 18 distinct IDs (0001-0018) with 8 name collisions against canonical, all content-divergent. These findings reshape the FR-8b/FR-8d Blueprint design decisions but do not threaten the feature's scope class or layer scope. Per IN-023, Discovery does not re-open the OI-2 gate decision (the `adrs-migrated/` consolidation is binding); Discovery merely enumerates the collisions and surfaces resolution recommendations for Design Composition.

## Component Inventory

| Component | Path | Role in this feature |
|---|---|---|
| `finalize-deliverable-packager` | `.claude/agents/finalize-deliverable-packager.md` (142 lines) | FR-1 edit target (lines 56-63 = retired dual-location BLOCKER); FR-10 packager-surface integration call-site |
| `shared-document-reviewer` | `.claude/agents/shared-document-reviewer.md` (473 lines) | FR-2 edit target (line 349 = contradictory dual-location BLOCKER); the canonical truth at lines 470-472 is preserved |
| `recipe-feature-pipeline` (orchestrator skill) | `.claude/skills/recipe-feature-pipeline/SKILL.md` (612 lines) | FR-3 edit target (line 273 = `output_adrs_dir` parameter passthrough, NO default today); FR-10 orchestrator stage-gate integration at Step 8 (Design Composition) |
| `design-composer` | `.claude/agents/design-composer.md` (206 lines) | FR-4 edit target (lines 48, 129, 187 = `output_adrs_dir` mentions; no ADR-0036 citation today) |
| `auditing-shared` | `.claude/skills/auditing-shared/scripts/` (7 production scripts + 1 smoke test) | FR-10 default validator home (per OI-3); pattern reference for FR-10 validator authoring |
| `execute-phase-quality-reviewer` | `.claude/agents/execute-phase-quality-reviewer.md` | FR-10 execution-pipeline-hook surface (via `run_phase_checks.py` parallel-dispatch coordinator) |

The four operator files are mutually referential: the orchestrator (`recipe-feature-pipeline`) invokes the other three; `finalize-deliverable-packager` invokes `shared-document-reviewer`; `design-composer` is invoked by `recipe-feature-pipeline` at Step 8. The internal contradiction in `shared-document-reviewer` (line 349 vs lines 470-472) is the strongest single-file evidence that FR-2 is well-defined: the file says both "BLOCKER on dual-location absence" AND "do NOT flag canonical-only as missing-mirror."

Full component records in `codebase-analysis.json` → `components[]`.

## Dependency Map

```
                                                  ┌─ shared-document-reviewer (5 invocation pts)
                                                  │     │
                                                  │     ├─→ auditing-shared/scripts/validate_pipeline_frontmatter.py (line 460)
                                                  │     │
                                                  ▼     │
recipe-feature-pipeline (orchestrator) ──┬──────► design-composer (writes ADRs to output_adrs_dir)
                                          │             │
                                          │             ▼
                                          │      output_adrs_dir filesystem (TODAY: implicit; per FR-3: canonical adrs/)
                                          │
                                          ├──► finalize-deliverable-packager (Step 14)
                                          │             │
                                          │             ├─→ shared-document-reviewer (DeliverableArchive dispatch)
                                          │             └─→ FR-10 validator (NEW per this feature)
                                          │
                                          └──► execute-phase-quality-reviewer (T7 dispatch, post-Gate-6)
                                                        │
                                                        └─→ auditing-shared/scripts/run_phase_checks.py
                                                                    │
                                                                    ├─→ validate_pipeline_frontmatter.py
                                                                    ├─→ check_pipeline_discipline.py
                                                                    ├─→ audit_workflow.py, audit_codespaces.py, audit_project.py
                                                                    └─→ FR-10 validator (NEW; extends this parallel set)
```

Full edge inventory in `codebase-analysis.json` → `dependencies[]`. 10 edges captured at `confidence: high`.

## Blast-Radius Summary per Touch Point

Detail in `codebase-analysis.json` → `blast_radius[]`. Highlights:

- **Operator-file edits (FR-1/2/3/4)** have LOW per-file blast radius for the prose-only edits; the mutually-referential 4-file family has the convention-consistency surface (AC-OP-2) as the true test of integration.
- **FR-10 validator** has HIGH blast radius via the 3 enforcement surfaces. Adding to `run_phase_checks.py`'s parallel set automatically wires it into `execute-phase-quality-reviewer` with zero new hook surface — that's the cheapest integration path.
- **FR-9 cross-reference sweep** has VERY HIGH blast radius via paths (4000+ bare ADR-NNNN mentions across the repo) but ACTIONABLE blast radius is bounded to the 14 path-form references identified in IN-008. Bare-ID mentions are out of scope (per FR-9b path-only).
- **FR-8d `adrs-migrated/` consolidation** has the highest risk subset because of the 8 numbering collisions (IN-004) requiring per-ID semantic decisions. `adrs/ADR-0038` (a SHIPPED canonical ADR) references `adrs-migrated/ADR-0007` paths in its body — surfaces the question whether path-only sweep extends to shipped canonical ADRs.

## Migration Map (FR-6 / FR-8 6-Category Taxonomy)

Per `codebase-analysis.json` → `migration_map`:

### Category FR-8a — Dedupe (12 byte-identical duplicates)

All 12 ADRs CONFIRMED byte-identical via `diff -q`. The duplicates span **4 source folders**, not 2:

| ADR | Source folder |
|---|---|
| ADR-0026 | `working/feature/audit-machinery-fixes-r1/adrs/` |
| ADR-0028 | `working/feature/pipeline-skill-design-fixes-r1/adrs/` |
| ADR-0029, 0030, 0031 | `working/feature/audit-findings-remediation-r1/adrs/` |
| ADR-0037 through 0043 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` |

Sub-action: delete feature-scoped copy per FR-8a. No rollback complication (Git history preserves; canonical version is unchanged).

### Category FR-8b — Reconciliation (3 cases; actually 2 sub-types)

The PRD's "3 divergent" framing is structurally wrong. Discovery finds:

| ADR | Sub-type | Recommendation |
|---|---|---|
| ADR-0024 | **Status-lift only** (canonical Accepted vs feature Proposed; body identical) | Keep canonical (Accepted), delete feature-scoped. No supersession archival needed. |
| ADR-0044 | **Numbering collision** (canonical `flatten-execution-dispatch-hierarchy` vs feature `per-issue-folder-model`; entirely different decisions) | RE-NUMBER feature-side to next-available canonical ID (proposed ADR-0051 if FR-8c runs first). FR-8b's "archive rejected body" framing is INAPPLICABLE. |
| ADR-0045 | **Numbering collision** (canonical `subagent-agent-tool-grant-prohibition` vs feature `three-doctypes-preserved`) | RE-NUMBER (proposed ADR-0052). |

This is open question #1 for the human at the Discovery Research gate (see end of report).

### Category FR-8c — Relocation (5 truly feature-scoped ADRs)

| ADR | Source | Target |
|---|---|---|
| ADR-0046 (add-new-sibling-file-evolution) | `working/feature/issue-capture-mechanism-r1/adrs/` | `adrs/` |
| ADR-0047 (three-layer-enforcement) | same | `adrs/` |
| ADR-0048 (prior-context-handoff) | same | `adrs/` |
| ADR-0049 (structural-vs-discipline-kb-split) | same | `adrs/` |
| ADR-0050 (5-state-issues-vocabulary) | same | `adrs/` |

Sub-action: `git mv` (preserves history per NFR-5) + redirect note per OI-5.

### Category FR-8d — `adrs-migrated/` consolidation (47 files; 18 distinct IDs)

The PRD hypothesis "ADRs 0001-0010 only" is WRONG. Archive contains IDs 0001-0018:

- **Final variants without canonical collision (9)**: ADR-0001 through ADR-0006, ADR-0008, ADR-0009, ADR-0010. `git mv` to canonical with no suffix needed.
- **Final variants WITH canonical collision (8)**: ADR-0011 through ADR-0018. Per-ID resolution:
  - ADR-0011 through ADR-0017: archive version is v2.0.0 (post-naming-convention update per ADR-0019); canonical is stale v1.0.0. **Replace canonical with archive**; Git history preserves both. (8 collisions — see open question #2.)
  - ADR-0018: INVERSE collision — canonical has the latest supersession-by-ADR-0038 marker; archive lacks it. **Keep canonical; delete archive.**
- **ADR-0007 (no final variant in archive)**: archive has 4 pre-* / -superseded variants; canonical version exists at `adrs/ADR-0007-code-graph-mcp-selection.md`. All 4 archive variants are DELETED per the pre-* / -superseded policy.
- **`-pre-naming-convention` variants (18)**: DELETE all.
- **`-pre-template-migration` variants (11)**: DELETE all.
- **`v1-superseded` variant (1, ADR-0007 only)**: DELETE.

Total file accounting: 17 final variants (ADR-0007 has none) + 18 pre-naming + 11 pre-template + 1 v1-superseded = 47. Verified.

Post-consolidation count change: canonical `adrs/` grows from 36 to roughly 52 (+5 from FR-8c relocations, +2 from re-numbered collisions, +9 from FR-8d collision-free, with 8 collision replacements overwriting in place). `adrs-migrated/` is empty (or removed).

## Cross-Reference Inventory (FR-9 sweep targets)

**Total path-form references requiring action**: ~50 across the inventory. Full per-line records in `codebase-analysis.json` → `cross_reference_inventory[]`. Highlights:

- **Feature-scoped path form** (`working/feature/<slug>/adrs/ADR-NNNN-*`): 14 hits across Issues files, shipped Blueprints, the orchestrator's own KB-documentation-criteria templates, and `capture-issue/SKILL.md`.
- **`adrs-migrated/` path form**: 18 hits across `phase-validators.md`, shipped Blueprints, plans, and the canonical `adrs/ADR-0038` itself (line 138).
- **Frontmatter array forms** (`supersedes:`, `superseded_by:`, `adrs_inherited:`, `adrs_authored:`, `related:`): all use bare ADR-NNNN form (no path) — NOT in FR-9 path-only sweep scope.
- **`README.md` line 18**: tree listing names `adrs-migrated/`; FR-8d removes the directory; tree listing must update.

The IN-008 grep-pattern floor in the Research Plan is sufficient (OI-4 resolved: no additional reference forms surfaced by Discovery). The Mermaid diagrams in shipped Blueprints do NOT contain ADR-path references (verified).

## Skill Audit Findings (FR-11 / OI-3)

Per `codebase-analysis.json` → `skill_audit_findings[]`. **8 skill-file-level findings** requiring action, **5 skill families confirmed CLEAN**.

| Skill / File | Line | Action |
|---|---|---|
| `recipe-feature-pipeline/SKILL.md` | 273 | update-with-fix (annotate default) |
| `KB-documentation-criteria/.../disciplines/design-composition.md` | 36, 295 | update-with-fix (replace feature-scoped path with canonical) |
| `KB-documentation-criteria/.../deliverable-archive-spec.md` | 150 | review-with-likely-update (backward-compat clause becomes stale) |
| `KB-documentation-criteria/.../shared-conventions.md` | 302 | NO CHANGE (already aligned with ADR-0036) |
| `KB-documentation-criteria/.../templates/issue-register-template.md` | 96, 99 | update-with-fix (path-only example refresh) |
| `KB-issue-capture/SKILL.md` | 72 | update-with-fix (path-only) |
| `capture-issue/SKILL.md` | 44 | update-with-fix (path + ID — ADR-0044 collision case) |
| `synthesize/SKILL.md` | 22, 240 | review-with-explicit-disposition (different output target; Design Composition decides validator allowlist policy) |

**Clean skill families** (no FR-11 finding): all 10 `auditing-*` skills, `KB-review-disciplines`, `KB-task-decomposition`, all per-layer KB-* design/platform skills, 6 synthesize-class knowledge skills (claim-extraction, entity-graph, decision-framing, report-composition, substrate-translation, verification).

PRD Assumption A5 ("5 skill families") is broadly correct. Discovery surfaces 8 file-level findings clustered into 4 families: `KB-documentation-criteria`, `KB-issue-capture` + `capture-issue` (issue-capture cluster), `recipe-feature-pipeline`, `synthesize`. The auditing-* family is clean; `KB-review-disciplines` is clean. Assumption A5 holds at the family level; the audit table must list files (not families) — 8 entries.

## Conventions Observed

Detail in `codebase-analysis.json` → `conventions.cc`. Notable findings:

- **`auditing-shared/scripts/` convention**: CLI positional args, JSON stdout, exit 0/2/non-zero (per `run_phase_checks.py:59`). Python stdlib only (NFR-8 satisfiable). FR-10 validator MUST conform — recommended naming `validate_adr_placement.py` (mirrors `validate_pipeline_frontmatter.py`).
- **`run_phase_checks.py` parallel-dispatch coordinator pattern**: the natural extension point for FR-10 execution-pipeline integration. Adding one entry to its dispatch set automatically wires the validator into `execute-phase-quality-reviewer`.
- **Subprocess invocation**: `subprocess.run(args, capture_output=True, text=True, timeout=120)`. 120s default timeout.
- **`git mv` usage convention**: established by `execution-pipeline-design-r1/plan-v2.md` (multiple `git mv` tasks) and `devcontainer-mcp-provisioning-r1/plan-v1.md:295`. Verification surface: `git log --follow <dst>` as L2 check. FR-8b/c task authoring should follow this pattern.
- **Redirect-note precedent**: NONE in the repo. The symlink option was REJECTED in `adrs/ADR-0036:107`. OI-5 default ("one-line markdown stub") is a fresh-design decision; no inheritance.
- **Markdown link-form catalog**: 6 path forms in active use (canonical-path, feature-scoped, legacy-archive, Markdown link, angle-bracket, frontmatter arrays). The IN-008 grep set captures all 6.
- **Operator-file frontmatter conventions**: agents have `tools:` arrays. `finalize-deliverable-packager` does NOT have `Bash` in its tools — open question for FR-10 packager-surface integration.

## Known Issues & Caution Areas

Per `codebase-analysis.json` → `known_issues[]`. Six issues surfaced:

1. **MAJOR**: PRD framing of ADR-0044/ADR-0045 as "divergent bodies" is structurally incorrect (numbering collisions). FR-8b is inapplicable to these cases.
2. **MINOR**: PRD names 2 feature folders for feature-scoped ADRs; Discovery surfaces 5 distinct folders. The Blueprint migration map must enumerate per-folder dispositions.
3. **MAJOR**: PRD "adrs-migrated/ contains ADRs 0001-0010" hypothesis is wrong; archive extends to ADR-0018 with 8 content-divergent collisions.
4. **MINOR**: OI-5 (redirect-note format) has no project precedent; Design Composition is fresh-designing.
5. **MINOR**: Canonical shipped ADR `adrs/ADR-0038:138` has prose-with-paths referencing `adrs-migrated/ADR-0007`. FR-9b "path-only edits to shipped Blueprints" — does it extend to shipped canonical ADRs?
6. **MINOR**: Numbering scheme for re-numbered collision ADRs (proposed ADR-0051/0052) must coexist with FR-8c relocations and any new ADRs this feature authors.

## Open Questions for Human (at Discovery Research gate)

Per `codebase-analysis.json` → `open_questions_for_human[]`. Five questions surface, all blocking downstream Design Composition:

1. **ADR-0044/0045 collision framing**: amend PRD or Blueprint-propose re-numbering scheme?
2. **`adrs-migrated/` collision resolution** for ADRs 0011-0018: Discovery recommends "archive v2.0.0 replaces canonical v1.0.0 for ADRs 0011-0017; canonical stays for ADR-0018 (supersession marker)". Blueprint approval required.
3. **synthesize's output ADR target**: allowlist (recommended) or re-target?
4. **FR-9b scope**: does path-only sweep extend to shipped canonical ADRs (e.g., `adrs/ADR-0038:138`)?
5. **Packager FR-10 surface**: add Bash to packager tools, or invoke validator via orchestrator hook, or via Python module import?

These are the load-bearing questions Design Composition needs answered (or interpreted) before authoring the Blueprint.

## Provenance

- **Authoring sub-agent**: `discovery-codebase-researcher`, single invocation per ADR-0021.
- **Inputs**: `research-plan.md` v1.0.0 (approved 2026-05-24T19:20:00Z), `prd-v1.md` v1.0.2 (approved 2026-05-24T19:10:00Z).
- **Extraction method**: `grep + find + Read`. GitNexus MCP available but not invoked — the markdown-corpus content-search analysis is faster and more precise via direct ripgrep/grep than via a Cypher graph query. Per KB-codebase-research SKILL.md, Read/Grep/Glob is the endorsed ground-truth verification path.
- **Schema version of companion JSON**: 1.1.0 per ADR-0018 + ADR-0038 (blast-radius extension).
- **Authoritative discipline**: `KB-codebase-research/SKILL.md`.
