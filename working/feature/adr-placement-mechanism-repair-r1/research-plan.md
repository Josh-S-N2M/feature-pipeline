---
id: RP-adr-placement-mechanism-repair-r1
doc_type: research-plan
version: 1.0.0
status: approved
gate_passed: research_plan_approval
approved_at: 2026-05-24T19:20:00Z
generated: 2026-05-24T18:45:00Z
generated_by: discovery-plan-author
feature_slug: adr-placement-mechanism-repair-r1
derived_from: working/feature/adr-placement-mechanism-repair-r1/prd-v1.md
prd_version: 1.0.2
prd_gate_state: approved
prd_approved_at: 2026-05-24T19:10:00Z
scope_class: FULL
layer_scope: ["claude-code"]
kb_inventory_cited:
  - KB-cc-platform
  - KB-cc-design
  - KB-documentation-criteria
  - KB-review-disciplines
  - KB-codebase-research
  - KB-task-decomposition
  - auditing-shared
  - auditing-cc-configs
  - auditing-skills
  - auditing-subagents
  - auditing-context-files
  - auditing-hooks
  - auditing-settings
  - auditing-mcp
  - auditing-github-actions
  - auditing-codespaces
  - recipe-feature-pipeline
  - synthesize
adr_inventory_cited:
  - ADR-0005
  - ADR-0011
  - ADR-0017
  - ADR-0018
  - ADR-0019
  - ADR-0020
  - ADR-0021
  - ADR-0027
  - ADR-0029
  - ADR-0031
  - ADR-0033
  - ADR-0035
  - ADR-0036
  - ADR-0038
  - ADR-0042
  - ADR-0044
  - ADR-0045
external_research_topic_count: 0
external_research_budget: 6
---

# Research Plan: Repair the ADR Placement Mechanism Per ADR-0036

This Research Plan is the contract between Discovery Planning and the Discovery Research stage. Per ADR-0021, every information need is mapped onto existing KBs and ADRs before any external research is authorized. For this feature, the result of that mapping is: **all information needs are either resolved by existing KBs/ADRs, are codebase-research topics, or are designer-general-knowledge.** Zero external research topics are authorized.

## Feature reference

- **Feature slug**: `adr-placement-mechanism-repair-r1`
- **PRD path**: `working/feature/adr-placement-mechanism-repair-r1/prd-v1.md`
- **PRD version**: 1.0.2
- **PRD gate state**: approved at 2026-05-24T19:10:00Z (PRD Approval Gate)
- **Scope class**: FULL
- **Layer scope**: CC-only (`.claude/`, `adrs/`, `working/feature/`, `Issues/`, `README.md`); breadth-within-layer flagged as the deviation signal in PRD §Layer Scope
- **Inherited ADRs in scope** (constraint or substrate for research):
  - ADR-0036 — Single-location ADR placement (the spec the feature aligns operators with; load-bearing)
  - ADR-0017 — Document-reviewer integration (governs `shared-document-reviewer`, one of the four target operator files)
  - ADR-0027 — Deliverable archive (governs `finalize-deliverable-packager`, another target file)
  - ADR-0019 — ADR-NNNN naming convention (preserved; informs FR-8d collision strategy)
  - ADR-0005 — Append-only supersession (relevant to FR-8b divergent-body archival)
  - ADR-0011 — Documentation-criteria canonical skill (constrains where KB-doctrine prose lives)
  - ADR-0018 / ADR-0038 — Codebase-analysis schema v1.1.0 (output contract for `discovery-codebase-researcher`)
  - ADR-0020 — KB structure (constrains where audit-discipline prose belongs)
  - ADR-0021 — Discovery phase architecture (this plan's parent ADR)
  - ADR-0029 / ADR-0033 — No-silent-scope-changes (the `adrs-migrated/` consolidation surfaces as a scope-deviation opportunity per OI-2 gate resolution)
  - ADR-0031 / ADR-0035 / ADR-0042 — `auditing-shared` skill-module + binding + family-graduation pattern (template for FR-10 validator placement)
  - ADR-0044 / ADR-0045 — Two of the three divergent-body cases; FR-8b directly reconciles these
- **Applicable KBs** (those whose principles or patterns touch this feature's CC-only layer scope):
  - KB-cc-platform, KB-cc-design — Claude Code primitives (skills, agents, hooks, scripts)
  - KB-documentation-criteria — ADR template, deliverable-archive-spec, shared-conventions
  - KB-review-disciplines — Gate 0/1 procedure for the operator-file BLOCKER prose edits
  - KB-codebase-research — Output contract for `discovery-codebase-researcher`
  - auditing-shared — Canonical home for the FR-10 validator (per OI-3 default)
  - auditing-* family (cc-configs, skills, subagents, context-files, hooks, settings, mcp, github-actions, codespaces) — Pattern reference for adding new validation machinery
  - recipe-feature-pipeline — The orchestrator; FR-3 modifies it; FR-10 wires the validator into it
  - synthesize, KB-task-decomposition — Downstream-consumer skills; included in FR-11 audit scope

---

## Information needs inventory

Each information need is named with `IN-NNN`, scoped to a downstream consumer, and triaged into one of the five dispositions per the Discovery Planning discipline. Justifications for `external-research-topic` (none in this Plan) and resolution summaries for `covered-by-*` (in the §"Topics explicitly NOT researched" section) follow.

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-001 | What is the byte-by-byte content equivalence between each of the 12 nominally-byte-identical feature-scoped ADRs and their canonical counterparts? (Re-verifies the orchestrator's pre-PRD finding; underpins FR-8a Assumption A2 baseline.) | `discovery-codebase-researcher`, then plan-author (Phase 2a per-task verification) | `codebase-topic` |
| IN-002 | What are the precise body diffs for the 3 divergent ADRs (ADR-0024 canonical-vs-`frontend-design-knowledge-r1`; ADR-0044 + ADR-0045 canonical-vs-`issue-capture-mechanism-r1`)? Each diff is required input for the FR-8b canonical-body proposal at Design Composition. | `discovery-codebase-researcher`, then `design-composer` (FR-8b reconciliation) | `codebase-topic` |
| IN-003 | What is the exact file inventory inside `adrs-migrated/` (47 files), classified into final-variant / `-pre-naming-convention` / `-pre-template-migration` per FR-8d? Is the "ADRs 0001–0010 only" hypothesis correct, or are higher-numbered files present? | `discovery-codebase-researcher`, then `design-composer` (FR-8d Blueprint disposition + collision strategy) | `codebase-topic` |
| IN-004 | Are there any canonical-vs-`adrs-migrated/` numbering collisions when consolidating per FR-8d? (Default hypothesis: no collisions because canonical lacks 0001–0010, but Discovery must enumerate.) | `discovery-codebase-researcher`, then `design-composer` (FR-8d AC-FR-8d-2 collision resolution) | `codebase-topic` |
| IN-005 | What does the orchestrator's `output_adrs_dir` parameter resolution look like today (`recipe-feature-pipeline/SKILL.md` line 273 + every surrounding usage site)? Is there an existing default, an implicit caller-supplied value, or no default at all? Discovery determines the form of the FR-3 edit. | `discovery-codebase-researcher`, then `design-composer` (Phase 1 operator-edit form per FR-3) | `codebase-topic` |
| IN-006 | What are the actual current line ranges (post-drift) for the retired BLOCKER prose in `finalize-deliverable-packager.md` (PRD cites 56–63) and the contradictory check in `shared-document-reviewer.md` (PRD cites 349) and the post-ADR-0036 statement (PRD cites 470–472)? PRD intentionally hedges with "or equivalent location"; Discovery pins down. | `discovery-codebase-researcher`, then `design-composer` (Phase 1 edit anchors) | `codebase-topic` |
| IN-007 | What are the actual line ranges for the `output_adrs_dir` parameter mentions in `design-composer.md` (PRD cites 48, 129, 187)? | `discovery-codebase-researcher`, then `design-composer` (Phase 1 FR-4 edit anchors) | `codebase-topic` |
| IN-008 | What is the complete inventory of in-repository cross-references to a relocated or deduplicated ADR — by file, line, reference-form (e.g., `adrs/ADR-NNNN`, `ADR-NNNN`, `[ADR-NNNN](path)`, `see ADR-NNNN`, `<../adrs/ADR-NNNN.md>`, `ADR NNNN` with a space, frontmatter `supersedes:` fields, `superseded_by:`, `related:`, `subsumes:`)? Includes pattern-set completeness check per OI-4. | `discovery-codebase-researcher`, then plan-author (Phase 3 sweep) | `codebase-topic` |
| IN-009 | What are the 3 enforcement-surface integration points for the FR-10 validator: (a) which orchestrator stage gate; (b) which execution-pipeline specialist or hook; (c) which packager check call-site? | `discovery-codebase-researcher`, then `design-composer` (FR-10 AC-FR-10-b/c/d Blueprint design) | `codebase-topic` |
| IN-010 | What existing validation-script invocation patterns are used by `auditing-shared/scripts/` (e.g., `pedagogical_marker_check.py`, `scan_memory_secrets.py`) — CLI interface, exit-code convention, subprocess dispatch shape? Underpins OI-3 default surface choice + NFR-8 dependency posture. | `discovery-codebase-researcher`, then `design-composer` (FR-10 validator design) | `codebase-topic` (with KB-cc-platform / auditing-shared SKILL.md as supplementary reading) |
| IN-011 | What is the complete list of skills that documents or enables ADR authoring/placement? PRD names 5 families (`KB-documentation-criteria`, `auditing-*`, `recipe-feature-pipeline`, synthesize-class, `KB-review-disciplines`); Discovery validates completeness per Assumption A5. | `discovery-codebase-researcher`, then `design-composer` (FR-11 audit-table population) | `codebase-topic` |
| IN-012 | For each skill in the FR-11 audit scope, what concrete prose or template fragments could permit feature-scoped ADR placement (e.g., template defaults pointing to `working/feature/<slug>/adrs/`, "place ADRs here" instructions)? Per-skill disposition (no-change-with-rationale vs update-with-fix) feeds AC-NFR-4-a. | `discovery-codebase-researcher`, then `design-composer` (FR-11 remediation Blueprint subsection) | `codebase-topic` |
| IN-013 | What is the canonical structure of an ADR file per ADR-0011 + ADR-0019 + the `adr-template.md` in KB-documentation-criteria? (Required for design-composer to propose FR-8b canonical bodies and provenance-footer format under OI-1.) | `design-composer` (FR-8b body composition) | `covered-by-KB:KB-documentation-criteria:references/templates/adr-template.md` |
| IN-014 | What is the supersession-discipline convention this feature must honor for archived divergent bodies (FR-8b) and for the shipped-Blueprint path-only sweep (FR-9)? | `design-composer`, plan-author | `covered-by-ADR:ADR-0005` |
| IN-015 | What is the canonical-helper-home pattern the FR-10 validator should follow (i.e., why does the validator belong in `auditing-shared/scripts/`)? | `design-composer` (OI-3 default rationale) | `covered-by-ADR:ADR-0031` (with ADR-0035 and ADR-0042 as reinforcement) |
| IN-016 | What is the deliverable-archive-spec post-amendment text (the single-location convention codified by ADR-0036)? | `design-composer` (Phase 1 FR-1/FR-2 prose-replacement target) | `covered-by-KB:KB-documentation-criteria:references/deliverable-archive-spec.md` (per ADR-0036 amendment) |
| IN-017 | What are the reviewer Gate 0/1 expectations for the documents this feature authors (Blueprint, ADR-of-this-feature, Plan, acceptance-tests, phase-validators)? | All downstream document authors | `covered-by-KB:KB-review-disciplines:references/gate-0-1-procedure.md` |
| IN-018 | What is the codebase-analysis.json schema (v1.1.0 per ADR-0018 + ADR-0038) that `discovery-codebase-researcher` must produce? | `discovery-codebase-researcher` | `covered-by-KB:KB-codebase-research:SKILL.md` (canonical schema) + `covered-by-ADR:ADR-0018` + `covered-by-ADR:ADR-0038` |
| IN-019 | What is the canonical 9-layer taxonomy for declaring Layer Scope? | `design-composer` (Blueprint Layer Scope subsection) | `covered-by-KB:KB-documentation-criteria:references/layer-taxonomy.md` |
| IN-020 | What is the EARS pattern set for authoring NFR/FR acceptance criteria in the Blueprint and the Plan? | `design-composer`, plan-author, test-acceptance-author | `covered-by-KB:KB-documentation-criteria:references/disciplines/ears-acceptance-criteria.md` |
| IN-021 | What is the Blueprint cross-cutting structure (Layer Scope, Fact Disposition Table, ADR pointers, NFR sections)? | `design-composer` | `covered-by-KB:KB-documentation-criteria:references/templates/blueprint-template.md` |
| IN-022 | What is the Plan template (phase-based decomposition with L1/L2/L3 verification per ADR-0020)? | plan-author | `covered-by-KB:KB-documentation-criteria:references/templates/plan-template.md` + `covered-by-KB:KB-task-decomposition:SKILL.md` |
| IN-023 | What is the no-silent-scope-changes discipline that constrains the `adrs-migrated/` consolidation discovery? (Confirms the OI-2 gate-resolved consolidation is the binding choice and Discovery does NOT re-open it.) | `discovery-codebase-researcher`, `design-composer` | `covered-by-ADR:ADR-0029` (with ADR-0033 execution-pipeline extension) |
| IN-024 | What is the orchestrator's working-directory precondition (cwd == repo-root) that any FR-3 / FR-10 path resolution must honor? | `design-composer` (FR-3 edit form), validator-author at Phase 4 | `covered-by-ADR:ADR-0027` |
| IN-025 | What is the standard Python-stdlib idiom for a glob-based file scanner producing a non-zero exit on findings? (Underpins FR-10 validator skeleton; NFR-8 posture.) | `design-composer` (FR-10 validator skeleton; the actual implementation is downstream of Plan) | `designer-general-knowledge` — Python stdlib `pathlib.Path.rglob` / `glob.glob` + `sys.exit(non_zero)` is industry-standard knowledge a competent designer applies; the Design subsection will document the rationale (per the discipline's "designer's prose carries authority" rule). |
| IN-026 | What is the conventional `git mv` invocation pattern for preserving history when relocating a file? (Underpins FR-8c relocation tasks; NFR-5 invariant.) | plan-author (Phase 2c task authoring), execute-task-code-producer | `designer-general-knowledge` — `git mv <src> <dst>` is standard Git knowledge; the Plan's Phase 2c tasks document the rationale per NFR-5-a. |
| IN-027 | What is the conventional Markdown link-rewriting pattern for path-only edits across files? (Underpins FR-9 sweep tasks; NFR-3 zero-false-negative invariant.) | plan-author (Phase 3 sweep task authoring) | `designer-general-knowledge` — Markdown link syntax `[label](path)` and standard `sed` / `Edit`-tool replacement patterns are industry-standard; Plan documents the rationale. |
| IN-028 | What is the `git log --follow` semantics for tracing a moved file's history? (Underpins NFR-5-b verification.) | plan-author (Phase 6 verification task authoring) | `designer-general-knowledge` — `git log --follow <path>` is standard Git knowledge. |

**Disposition summary:**

- `codebase-topic`: 12 (IN-001 through IN-012)
- `covered-by-KB`: 7 (IN-013, IN-016, IN-017, IN-018, IN-019, IN-020, IN-021, IN-022) — note IN-022 spans 2 KBs and is counted once
- `covered-by-ADR`: 6 (IN-014, IN-015, IN-018-part, IN-023, IN-024)
- `designer-general-knowledge`: 4 (IN-025, IN-026, IN-027, IN-028)
- `external-research-topic`: **0**

The CC-only layer scope and the in-house pattern coverage (auditing-shared, recipe-feature-pipeline, KB-documentation-criteria, KB-review-disciplines, the existing ADR substrate) saturate every information need. No external sourcing is required.

---

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The researcher reads this plan, produces `codebase-analysis.json` (per the v1.1.0 schema in KB-codebase-research) + `codebase-analysis-report.md`. The codebase-research effort for this feature is **the heart of Discovery** — the migration map, cross-reference inventory, validator integration-surface identification, and skill-audit scope inventory are all produced here.

### Touch points

Specific files, modules, and directories that this feature's FRs name. The researcher uses these as starting points for graph traversal and as direct read targets.

- `.claude/agents/finalize-deliverable-packager.md` — FR-1 edit anchor (retired BLOCKER prose at PRD-cited line 56–63; pin actual lines per IN-006) + FR-10 packager-side validator integration call-site (per IN-009-c).
- `.claude/agents/shared-document-reviewer.md` — FR-2 edit anchor (contradictory check at PRD-cited line 349; post-ADR-0036 statement at PRD-cited lines 470–472; pin actual lines per IN-006).
- `.claude/skills/recipe-feature-pipeline/SKILL.md` — FR-3 edit anchor (`output_adrs_dir` parameter at line 273 per PRD; orchestrator-side default-resolution form decided by Discovery per IN-005) + FR-10 orchestrator-stage-gate integration site (per IN-009-a).
- `.claude/agents/design-composer.md` — FR-4 edit anchor (parameter description at PRD-cited lines 48, 129, 187; pin actual lines per IN-007).
- `.claude/skills/auditing-shared/SKILL.md` + `.claude/skills/auditing-shared/scripts/` — FR-10 default validator home (per OI-3) + IN-010 pattern reference for `pedagogical_marker_check.py` and `scan_memory_secrets.py`.
- `adrs/` — canonical ADR registry; current 36 files; target of all FR-8 migrations.
- `adrs-migrated/` — 47-file legacy archive; FR-8d consolidation source; IN-003 + IN-004 inventory targets.
- `working/feature/frontend-design-knowledge-r1/adrs/` — source folder for divergent ADR-0024 (FR-8b); IN-002 diff input.
- `working/feature/issue-capture-mechanism-r1/adrs/` — source folder for divergent ADR-0044 + ADR-0045 (FR-8b) + the 5 truly feature-scoped ADR-0046 through ADR-0050 (FR-8c); IN-002 diff input + IN-001 byte-equality input.
- `working/feature/*/adrs/` — broader sweep for any remaining feature-scoped ADR sites the on-disk-reality verification may have missed.
- `.claude/skills/KB-documentation-criteria/SKILL.md` + `references/` — FR-11 audit target (canonical home of `adr-template.md`, `deliverable-archive-spec.md`, `shared-conventions.md`); IN-012 prose-fragment scan.
- `.claude/skills/auditing-*/SKILL.md` (full family) — FR-11 audit target; IN-011 + IN-012.
- `.claude/skills/synthesize/SKILL.md` + the synthesize-class skill family (`claim-extraction-knowledge`, `entity-graph-knowledge`, `decision-framing-knowledge`, `report-composition-knowledge`, `substrate-translation-knowledge`, `verification-knowledge`) — FR-11 audit target (synthesize-class per PRD scope).
- `.claude/skills/KB-review-disciplines/SKILL.md` + `references/` — FR-11 audit target.
- `.claude/agents/` (full directory) — secondary FR-11 audit target: agent files that may carry ADR-placement guidance even outside the named skill families.
- `working/feature/*/blueprint-v*.md`, `working/feature/*/plan-v*.md` — FR-9 sweep targets; IN-008 cross-reference inventory.
- `Issues/**/*.md` — FR-9 sweep target; IN-008 inventory.
- `README.md` — FR-9 sweep target; IN-008 inventory.

### Blast-radius questions

Per ADR-0018 + the v1.1.0 schema extension (ADR-0038), blast-radius is captured in `codebase-analysis.json`'s `blast_radius` section. The questions for this feature:

- **1-hop dependents of the four operator files** (FR-1/2/3/4 edit anchors): which other agent files, skills, or orchestrator paths reference them, and would a non-local change to the BLOCKER prose or `output_adrs_dir` parameter break a caller?
- **1-hop dependents of `auditing-shared/`**: which audit modules subprocess-dispatch into it today (per ADR-0042 graduated family list — 5 family coordinators); the new FR-10 validator extends this set.
- **3-hop reach from canonical `adrs/`**: every consumer that reads an ADR by path (Blueprints, Plans, agent prose, skill prose, Issues, README). Determines the FR-9 sweep blast surface.
- **3-hop reach from each `working/feature/<slug>/adrs/` source**: every artifact that references the soon-to-be-relocated ADRs by their feature-scoped path. Determines FR-9 inventory completeness per NFR-3.
- **Test coverage for the four operator files + the FR-10 validator**: any existing test fixtures, audit scripts, or pipeline smoke tests that exercise the BLOCKER prose, the `output_adrs_dir` parameter, or the packager's current ADR-cross-location check.
- **Reverse-dependency from `adrs-migrated/`**: any in-repo reference to a path under `adrs-migrated/`. Determines whether FR-8d consolidation introduces broken-link risk beyond the FR-9 sweep's known scope.

### Convention discovery

Per-layer convention discovery for the CC layer (the only in-scope layer):

- **`auditing-shared/scripts/` convention**: confirm CLI shape (positional args, exit-code convention, `--help` discoverability), Python-stdlib-only dependency posture per NFR-8, subprocess-dispatch shape used by family-coordinator skills, and test-fixture conventions if any exist. The new FR-10 validator MUST conform.
- **Orchestrator stage-gate hook convention**: identify how `recipe-feature-pipeline/SKILL.md` invokes existing validators or audit subprocesses; the FR-10 orchestrator-surface (IN-009-a) MUST integrate at an existing gate boundary, not introduce a novel one.
- **Execution-pipeline integration convention** (per ADR-0044 flatten-execution-dispatch): identify where the execution pipeline's specialists or hooks accept a validator call. The IN-009-b surface MUST conform to the post-ADR-0044 dispatch hierarchy.
- **`finalize-deliverable-packager` BLOCKER-emission convention**: how the packager raises a BLOCKER today (the existing dual-location check at line 56–63 is the reference pattern); the IN-009-c integration MUST emit BLOCKERs in the same format so downstream packager-report consumers do not break.
- **Redirect-note conventions**: scan for any precedent for stub-file or redirect-file conventions in the repo (none expected, but Discovery surfaces if any exist; informs OI-5 default).
- **`git mv` usage convention in prior Plans**: scan prior `plan-v*.md` for the conventional task-level shape used to relocate files (e.g., does any prior plan-task use `git mv`? what verification pattern do they specify?). Informs Phase 2c task authoring + NFR-5-a.
- **Markdown link-form conventions in shipped Blueprints**: catalog the dominant reference-forms in shipped `blueprint-v*.md` to ensure the IN-008 grep pattern-set is exhaustive per NFR-3.

### Specific queries or grep targets

The researcher may refine these; they represent the floor of pattern coverage required for IN-008 + IN-011 + IN-012.

**For IN-008 cross-reference inventory (FR-9 + NFR-3):**

- `rg --type md '\bADR-\d{4}\b'` — bare ID references (any prose mention).
- `rg --type md 'adrs/ADR-\d{4}'` — canonical-root path references.
- `rg --type md 'working/feature/[^/]+/adrs/ADR-\d{4}'` — feature-scoped path references.
- `rg --type md 'adrs-migrated/'` — legacy-archive path references.
- `rg --type md '\[ADR-\d{4}\]\([^)]+\)'` — Markdown link form.
- `rg --type md '<\.\./adrs/ADR-\d{4}[^>]*>'` and `<\.\./\.\./adrs/ADR-\d{4}[^>]*>` — angle-bracket relative-path form.
- `rg --type md 'ADR \d{4}'` — space-separated ID form (informal prose).
- `rg --type md 'see ADR-\d{4}'` and `rg --type md 'per ADR-\d{4}'` — prose citation forms.
- `rg --multiline 'supersedes:\s*(\[[^\]]*\]|\S+)'` — frontmatter `supersedes:` arrays.
- `rg --multiline 'superseded_by:\s*(\[[^\]]*\]|\S+)'` — frontmatter `superseded_by:` arrays.
- `rg --multiline 'related:\s*(\[[^\]]*\]|\S+)'` — frontmatter `related:` arrays.
- `rg --multiline 'subsumes:\s*' --type md` — frontmatter `subsumes:` arrays.
- `rg --type md 'pairs_synthesis_decisions:'` — frontmatter pairing arrays.

**For IN-011 + IN-012 skill-audit scope:**

- `rg -l --type md 'output_adrs_dir' .claude/skills/ .claude/agents/` — every site that references the parameter.
- `rg -l --type md 'working/feature/[^/]+/adrs' .claude/skills/ .claude/agents/` — every site that mentions feature-scoped placement.
- `rg -l --type md 'adrs/ADR-' .claude/skills/ .claude/agents/` — every site that mentions canonical placement (sanity-check for completeness).
- `rg -l --type md 'feature-scoped' .claude/skills/ .claude/agents/` — prose mentions of the retired pattern.
- `rg -l --type md 'dual-location' .claude/skills/ .claude/agents/` — prose mentions of the retired convention.

**For IN-003 + IN-004 archive inventory:**

- `ls -la adrs-migrated/` — direct enumeration.
- `find adrs-migrated/ -name '*.md' -printf '%f\n' | sort` — file-name extraction for collision check against `ls adrs/`.

**For IN-001 byte-equality verification (12 cases):**

- For each ADR-NNNN ∈ {0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043}: `diff -q adrs/ADR-NNNN-*.md working/feature/*/adrs/ADR-NNNN-*.md` (across all candidate source folders) → expected empty diff per the orchestrator's pre-PRD verification.

**For IN-002 divergent-body diff:**

- `diff -u adrs/ADR-0024*.md working/feature/frontend-design-knowledge-r1/adrs/ADR-0024*.md`
- `diff -u adrs/ADR-0044*.md working/feature/issue-capture-mechanism-r1/adrs/ADR-0044*.md`
- `diff -u adrs/ADR-0045*.md working/feature/issue-capture-mechanism-r1/adrs/ADR-0045*.md`

**For IN-009 enforcement-surface identification:**

- Read `recipe-feature-pipeline/SKILL.md` around each gate-transition step (Gate 4 Blueprint Approval, Gate 5 Plan Approval, Gate 6 Final Approval) to identify candidate orchestrator stage-gate integration points.
- Read the execution-pipeline orchestrator (whichever skill owns it post-ADR-0044 flatten) to identify the candidate hook or specialist for IN-009-b.
- Read `finalize-deliverable-packager.md` around the existing ADR cross-location check (lines 56–63 per PRD) to identify the call-site for the FR-10 replacement.

---

## External research topics

**No external research authorized.** All information needs in the inventory are resolved by existing KBs, ADRs, codebase research, or designer-general-knowledge. The CC-only layer scope and the in-house pattern saturation (auditing-shared as canonical home, recipe-feature-pipeline as orchestrator authority, KB-documentation-criteria as doctype authority, KB-review-disciplines as reviewer authority, and the 16-ADR substrate around ADR placement / supersession / scope-change discipline) cover every fact a downstream sub-agent will need.

**External-topic budget**: 0 of 6 used. Rationale: a positive design state per ADR-0021. The Plan would only authorize an external topic if a downstream consumer needed a fact that none of the in-scope KBs/ADRs document AND that no competent designer would just know — and no such fact exists for this repair-class feature.

---

## Topics explicitly NOT researched

Anti-scope-creep mechanism per the Discovery Planning discipline. Each entry confirms an information need resolved by the cited artifact; future revisits of the same question should start here.

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-013 | KB-documentation-criteria — `references/templates/adr-template.md` | The canonical ADR structure (frontmatter fields, REQUIRED body sections per Gate 0 structural check, `change_summary`, `supersedes` discipline) is the template `design-composer` already uses when authoring ADRs. The FR-8b canonical-body proposals and the OI-1 provenance-footer format both inherit from this template. |
| IN-014 | ADR-0005 (append-only supersession) | Supersession discipline: a superseded ADR is not deleted but marked `status: superseded` with `superseded_by:` pointer; in-place edits are restricted to `status: proposed`. This governs the FR-8b archival of divergent bodies (archived files cite supersession provenance) and constrains the FR-9 path-only sweep (shipped Blueprint prose is not semantically rewritten because the shipped artifact is itself a supersession-discipline-protected historical record). |
| IN-015 | ADR-0031 (auditing-shared canonical-helper-home) — reinforced by ADR-0035 (binding convention) and ADR-0042 (auditing-mcp family graduation) | Cross-cutting validation helpers belong in `auditing-shared/scripts/` as the single canonical implementation, dispatched via subprocess by family-coordinator skills. The FR-10 validator's OI-3 default (Python script under `auditing-shared/scripts/`) is this exact pattern, with the orchestrator + execution-pipeline hook + packager acting as the three family-coordinator-style consumers. ADR-0042 explicitly anticipates new family-coordinator consumers extending the canonical-helper-home set. |
| IN-016 | KB-documentation-criteria — `references/deliverable-archive-spec.md` (post-ADR-0036 amendment) | The amended spec codifies single-location placement (`adrs/ADR-NNNN-<title>.md` only); the dual-location convention is superseded historical context. Phase 1 FR-1 and FR-2 align the operator-file BLOCKER prose with this amended spec; no spec re-amendment is required. |
| IN-017 | KB-review-disciplines — `references/gate-0-1-procedure.md` | The Gate 0 (structural) + Gate 1 (quality) checks that `shared-document-reviewer` applies per ADR-0017; every document this feature authors (Blueprint, ADRs, Plan, acceptance-tests, phase-validators) passes through these checks. Document authors design their outputs to satisfy the procedure. |
| IN-018 | KB-codebase-research — `SKILL.md` (canonical schema) + ADR-0018 (original schema) + ADR-0038 (v1.1.0 blast-radius extension) | The `codebase-analysis.json` schema v1.1.0 is canonical; `discovery-codebase-researcher` produces it as the sole-format output of Discovery Research. This Research Plan's codebase-research scope (touch points, blast-radius questions, convention discovery, specific queries) is the input to that schema. |
| IN-019 | KB-documentation-criteria — `references/layer-taxonomy.md` | The 9-layer engineering taxonomy used by PRD + Blueprint. This feature's Layer Scope is CC-only (confirmed at PRD); Discovery does not re-derive the taxonomy. |
| IN-020 | KB-documentation-criteria — `references/disciplines/ears-acceptance-criteria.md` | The EARS pattern set (Ubiquitous "shall", Event-driven "When", State-driven "While", Optional "Where", Unwanted "If/then"). PRD's ACs already conform; downstream Blueprint/Plan/tests inherit. |
| IN-021 | KB-documentation-criteria — `references/templates/blueprint-template.md` (+ `references/disciplines/design-composition.md`) | The Blueprint cross-cutting structure (Layer Scope, Fact Disposition Table, ADR pointers, NFR sections). `design-composer` authors per this template. |
| IN-022 | KB-documentation-criteria — `references/templates/plan-template.md` + KB-task-decomposition — `SKILL.md` (+ `references/disciplines/plan-authoring.md`) | The Plan phase-based decomposition + L1/L2/L3 verification per ADR-0020. `plan-author` produces per this contract; the 7-phase decomposition the PRD outlines maps cleanly onto plan-template phase structure. |
| IN-023 | ADR-0029 (no-silent-scope-changes principle) — extended by ADR-0033 (execution-pipeline extension) | Any scope-deviation surface during execution requires explicit user surfacing. The PRD's Phase Scope Outline already encodes the OI-2 gate-resolved consolidation of `adrs-migrated/` as Phase 2d; Discovery does NOT re-open the OI-2 decision (the gate-binding choice is interpretation (a) — consolidate). If Discovery surfaces a new scope-deviation candidate (e.g., a 10th layer becoming implicated, a new ADR family discovered outside scope), the orchestrator's standard scope-amendment escalation applies. |
| IN-024 | ADR-0027 (cwd == repo-root precondition) | All `adrs/` and `working/feature/<slug>/adrs/` path resolutions resolve relative to repo root. FR-3 + FR-10 designs MUST honor this precondition; the validator's repository scan and the orchestrator's `output_adrs_dir` resolution both depend on it. |

---

## Estimated effort

- **Codebase research effort**: **Medium-Large.** Twelve `codebase-topic` needs spanning 4 distinct codebase regions (operator files at `.claude/agents/`, orchestrator at `.claude/skills/recipe-feature-pipeline/`, audit machinery at `.claude/skills/auditing-shared/`, and the repo-wide cross-reference inventory). The cross-reference inventory (IN-008) is the largest single workload — pattern-set design + execution across `.claude/`, `adrs/`, `adrs-migrated/`, `working/feature/`, `Issues/`, and `README.md`. The 47-file `adrs-migrated/` inventory (IN-003) and the per-skill prose-fragment scan (IN-012) add second-order workload. Single `discovery-codebase-researcher` invocation per ADR-0021; no fan-out.
- **External research topic count**: **0 of 6 budget.**
- **Estimated wall-clock**: bounded by `discovery-codebase-researcher` single-instance time (no external parallelism; no fan-in cost). Anticipated 1–2 hours for an experienced researcher given the breadth of the inventory work.

---

## Open questions for human resolution

These surface at the Research Plan Approval Gate. Each is a Plan-bounded question whose answer changes Discovery scope, not a downstream Design decision.

1. **Is the codebase-research scope above complete?** The PRD's Phase Scope Outline names Phase 0 Discovery as the source-of-truth producer for the migration map (Phase 2 input) and the cross-reference inventory (Phase 3 input). If the user knows of additional reference sites (e.g., a sibling-repo audit-log, an off-tree generator script, a CI workflow file) NOT covered by the touch-points list, surface now so Discovery includes them. *Default behavior if no answer: proceed with the touch-points list as authoritative; Phase 6 verification (re-running the IN-008 grep set) backstops completeness per NFR-3.*

2. **Is the IN-008 grep-pattern floor sufficient, or should additional patterns be added before Discovery executes?** The pattern set listed under §Specific queries enumerates the known reference forms; OI-4 (PRD) flags completeness as an explicit open item. If the user knows of additional reference forms used in shipped artifacts (e.g., HTML-anchor-style `#adr-NNNN`, RST-style `:doc:` references in any embedded RST), surface now. *Default if no answer: proceed with the listed pattern set; Phase 6 re-run validates empirically.*

3. **Should the FR-11 audit scope be expanded beyond the 5 named skill families?** PRD Assumption A5 names `KB-documentation-criteria`, `auditing-*` family, `recipe-feature-pipeline`, synthesize-class, `KB-review-disciplines`. The Research Plan's IN-011 task is to confirm this scope is complete by sweeping all `.claude/skills/**/*.md` for ADR-placement mentions. If the user wants to expand the audit scope a priori (e.g., to also include the per-layer KBs like `KB-cc-design`, `KB-backend-design`, etc., on the theory that any design-discipline skill could carry stale ADR-placement language), surface now. *Default if no answer: Discovery's IN-011 sweep determines empirically; any out-of-named-scope finding surfaces as an Assumption A5 amendment in the codebase-analysis report.*

4. **Should Discovery also produce a draft for the OI-1 (divergent-body archival format), OI-3 (validator implementation surface), and OI-5 (redirect-note format) decisions, or are those owned exclusively by Design Composition?** The PRD assigns ownership to Design Composition (Blueprint approval gate), but Discovery's IN-002 divergent-body diff + IN-010 auditing-shared pattern reference are both load-bearing inputs to those decisions. If the user prefers Discovery to surface draft proposals for Design Composition to refine, surface now. *Default if no answer: Discovery produces the load-bearing facts (diffs, pattern catalogs); Design Composition owns the proposals per PRD assignment.*

5. **Are there any topics the user would like added to the explicit-NOT-researched list?** The 12-entry table above captures every KB/ADR-resolved need in the inventory. If the user has a topic they want explicitly out-of-bounds (e.g., "do not investigate the synthesize-class skills' relationship to the ADR-0044 flatten-execution-dispatch decision"), surface now. *Default if no answer: the list stands as authoritative.*

---

## Approval posture

The Research Plan Approval Gate decides:

- **Codebase-research scope ratification.** The 12 codebase-topic needs + the touch-points list + the blast-radius questions + the grep-pattern floor are the authoritative input contract for `discovery-codebase-researcher`. Gate approval locks them; mid-Discovery scope expansion requires re-gate.
- **External-research zero ratification.** The 0-of-6 budget usage is a positive design state per ADR-0021. Gate approval confirms the KB/ADR coverage analysis is trustworthy and no external sourcing is required.
- **Open-question resolutions.** The 5 open questions above feed Discovery scope. Default-if-unanswered behaviors are documented; gate may override.
- **Estimated-effort acceptance.** Medium-Large codebase-research effort with no external parallelism is the expected shape; gate confirms the user accepts the single-instance wall-clock posture.

Post-approval, the orchestrator dispatches `discovery-codebase-researcher` (1 invocation) and zero `discovery-external-researcher` invocations. The Discovery Research stage produces `codebase-analysis.json` + `codebase-analysis-report.md`; no `research-notes/<topic>.md` files (zero external topics).

---

## Provenance

- **Authored by**: `discovery-plan-author` sub-agent, 2026-05-24, run ID `adr-placement-mechanism-repair-r1-20260524-183201`.
- **PRD basis**: `prd-v1.md` v1.0.2 (status `approved`, gate `prd_approval` passed 2026-05-24T19:10:00Z).
- **Intent Clarification reference**: `intent-clarification.md` v2.0.1 (status `approved`, gate `intent_confirmation` passed 2026-05-24T18:55:00Z; v1.1.0 → v2.0.0 binding scope expansion captured in §Scope Deviation Notice).
- **Authoritative discipline**: `KB-documentation-criteria/references/disciplines/discovery-planning.md` (KB-and-ADR-first triage; 6-topic external cap; explicit-NOT-researched discipline).
- **Authoritative template**: `KB-documentation-criteria/references/templates/research-plan-template.md` (Gate 0 structural contract).
- **Authoritative parent ADR**: ADR-0021 (Discovery phase architecture — KB-and-ADR-first principle; Discovery Research fan-out shape).
