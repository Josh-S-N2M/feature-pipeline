---
id: CodebaseAnalysis-execution-pipeline-design-r1
version: 1.1.1
status: complete
feature_slug: execution-pipeline-design-r1
derived_from: working/feature/execution-pipeline-design-r1/research-plan.md
research_plan_user_token: RP-CONFIRM-execution-pipeline-design-r1-20260522T031500Z
generated: 2026-05-22T03:16:00Z
completed_at: 2026-05-22T03:38:00Z
revised: 2026-05-22T04:18:00Z
revision_reason: Post-checkpoint user-prompted review surfaced framing problems in the end-of-discovery Blueprint-decision distillation. Four classes of issues identified (lumped decisions, mis-framed dichotomies, mis-attributed decisions, missing decisions); six material gaps captured. Substantive IN findings stand unchanged; only the Blueprint-decision distillation is re-framed. The prior 11-item table is preserved in-place per ADR-0005 append-only, marked superseded-in-place, with a new "Revised Blueprint-decision distillation" section appended. Net: 11 mixed-grade items → 14 substantive + 3 mechanical applications.
generated_by: claude (acting as discovery-codebase-researcher, continuation session)
batches_completed: [A, B, C, D, E, F]
INs_covered: [IN-001, IN-002, IN-003, IN-004, IN-005, IN-006, IN-007, IN-008, IN-009, IN-010, IN-011, IN-012, IN-014, IN-015, IN-016, IN-017]
INs_not_applicable: [IN-013]
external_research_topics_consumed: 0
external_research_topics_budget: 6
blueprint_decisions_surfaced: 14
mechanical_applications: 3
scope_deviations_surfaced: 1
adr_corrections_surfaced: 1
companion_artifact: <none — single .md per project convention for this feature>
reviewer_verdict: approved (Gate 0 pass, Gate 1 pass — Consistency 95, Completeness 92, Rule compliance 94, Clarity 93)
reviewed_at: 2026-05-22T03:55:00Z
amendment_log:
  - v1.1.0 at 2026-05-22T03:48:00Z — Revised Blueprint-decision distillation per user post-checkpoint review. Prior 11-item table superseded-in-place; substantive IN findings unchanged. Re-framed list: 14 substantive Blueprint decisions + 3 mechanical applications. Six missing decisions surfaced: execution-side reviewer architecture (#9), agent inventory (#10), "code-producing" definition (#11), reconciliation budget value (#12), phase-quality scoring dimensions (#13), FR-4 dispatch taxonomy (#14). See appended "Revised Blueprint-decision distillation" section.
  - v1.1.1 at 2026-05-22T04:18:00Z — Discipline-5 violation correction (recipe-feature-pipeline/SKILL.md). User-surfaced at 2026-05-22T04:12:00Z. Two locations had stage-by-number references: (a) IN-007's agent-role table used "(Stage N)" parentheticals across 14 rows — removed; stage names alone convey pipeline ordering. (b) IN-009's ADR-0021 commitment summary used "Stage 2 input contract", "Stage 3 invokes", "Stage 3 fan-out" — replaced with stage names "Discovery Planning input contract", "Discovery Research invokes", "Discovery Research fan-out". Also corrected an in-table "4-cycle budget per ADR-0021" caption to "per ADR-0017" (canonical home; see IN-009 Batch E narrative for mis-credit surfacing). Patch-level per shared-conventions.md versioning rules (clarification of existing statements without changing meaning). Substantive IN findings unchanged. Self-surfacing entry added to companion synthesis.md "Surfaced for cross-artifact audit" section as symmetric self-application of ADR-0029.
---

# Codebase Analysis — Execution Pipeline Design (r1)

Per the Research Plan, this document captures the codebase findings for each Information Need (IN-001 through IN-017). Findings are added in batches; each batch ends with a checkpoint summary.

Format per IN: heading, finding, evidence (file paths + key excerpts where relevant), design implication.

## Batch A — Pre-scan verifications and uploaded reference reconnaissance

### IN-001 — Does `.claude/skills/ai-development-guide/` exist?

**Finding**: **DOES NOT EXIST.**

**Evidence**: `[ -d .claude/skills/ai-development-guide ]` returns false (verified 2026-05-22T03:16:00Z).

**Design implication**: 
- Confirms the pre-implementation pre-scan documented in `prd-v1.1.0.md` Assumption A-1.
- Validates the resolution chosen for Q-001: install the skill in this feature as a Plan task (per AC-FR-9-e).
- The Plan task shall source content from `/mnt/user-data/uploads/SKILL__2_.md` (see IN-016 for content shape).
- All execution-phase code-producing sub-agents defined by this feature's Blueprint shall list `ai-development-guide` in their `skills:` frontmatter (per AC-FR-9-a) — but the bindings must execute the install task FIRST per AC-FR-9-e to avoid pointing at a non-existent skill.

---

### IN-003 — What audit scripts (if any) live in `.claude/skills/KB-codespaces-platform/scripts/`?

**Finding**: **No `scripts/` subdirectory exists.** The skill itself exists with a substantial SKILL.md (16.4 KB), an `assets/` directory, and a `references/` directory — but no audit scripts.

**Evidence**:
```
.claude/skills/KB-codespaces-platform/
├── SKILL.md         (16,448 bytes — design wisdom, not audit logic)
├── assets/
└── references/
```
(verified 2026-05-22T03:16:00Z)

**Design implication**:
- Confirms PRD Assumption A-3 correction in v1.1.0.
- Validates the resolution chosen for Q-002: ship `auditing-codespaces` as a stub skill (SKILL.md only, no audit scripts) per AC-FR-8-b.
- The stub preserves the 3-way-split structural pattern (per ADR-0031) so future codespaces audit script authoring has a canonical home.
- The substantial existing KB-codespaces-platform/SKILL.md captures design wisdom about codespaces; the new `auditing-codespaces/SKILL.md` stub should reference KB-codespaces-platform for "what to audit" knowledge while making clear that audit script authoring is a separate future feature.

---

### IN-016 — Content shape of the uploaded `ai-development-guide` reference SKILL.md

**Finding**: A 302-line technical guide with 9 major sections covering anti-pattern detection, fail-fast principles, debugging techniques, and a 4-phase quality-check workflow.

**Frontmatter** (sparse — only the two universal SKILL.md fields):
```yaml
name: ai-development-guide
description: Technical decision criteria, anti-pattern detection, debugging techniques, and quality check workflow. Use when making technical decisions, detecting code smells, or performing quality assurance.
```

**Section outline**:
1. Technical Anti-patterns (Red Flag Patterns) — code quality + design anti-patterns
2. Fail-Fast Fallback Design Principles — when fallbacks are acceptable, error masking detection
3. Rule of Three — criteria for code duplication
4. Common Failure Patterns (5 patterns: Error Fix Chain, Circumventing Correctness Guarantees, Implementation Without Sufficient Testing, Ignoring Technical Uncertainty, Insufficient Existing Code Investigation)
5. Debugging Techniques — Error Analysis Procedure, 5 Whys, Minimal Reproduction Code, Debug Log Output
6. Quality Assurance Mechanism Awareness
7. Quality Check Workflow — 4 phases: Static Analysis → Build Verification → Testing → Final Quality Gate
8. Situations Requiring Technical Decisions — abstraction timing, perf vs readability, contract granularity, scope expansion
9. Implementation Completeness Assurance + Impact Analysis (3-stage process: Direct Impact → Indirect Impact → Data Flow)

**Design implication**:
- Section 7 ("Quality Check Workflow") with its 4-phase structure is directly relevant to PRD FR-3 (phase-level quality stage). The Blueprint should consider whether the 4-phase decomposition (static → build → test → final gate) maps onto FR-3's phase-quality structure, or whether FR-3 collapses these into a single sweep.
- Section 4 (Common Failure Patterns) provides the "anti-patterns to watch for" content that the Blueprint should cite when explaining FR-9's binding rationale (per AC-FR-9-d).
- The frontmatter shape (only `name:` + `description:`) is sparser than typical project SKILL.md files. The Plan's install task (AC-FR-9-e) may need to add project-conventional frontmatter fields — needs Blueprint decision based on what shared-conventions.md (IN-004) requires.
- The content style is hierarchical with deep nesting (### under ## under ##); fits the project's existing skill-content style.

---

### IN-017 — Content shape of uploaded `task-executor` and `quality-fixer` reference templates

**Finding**: Two heavyweight sub-agent definitions, each with phase-entry/exit BLOCKING gates, structured-JSON returns, and explicit escalation responses. Both are Blueprint inspiration only (per PRD pre-Discovery note), not adopted verbatim.

#### task-executor (444 lines)

**Frontmatter** (substantive):
```yaml
name: task-executor
description: Executes implementation completely self-contained following task files. ...
tools: Read, Edit, Write, MultiEdit, Bash, Grep, Glob, LS, TaskCreate, TaskUpdate
skills: coding-principles, testing-principles, ai-development-guide, implementation-approach, external-resource-context
```

**Workflow shape**:
1. Phase Entry Gate [BLOCKING]
2. File Scope Constraint
3. Mandatory Judgment Criteria (3-step Pre-implementation Check):
   - Step 1: Design Deviation Check (Any YES → Immediate Escalation)
   - Step 2: Quality Standard Violation Check (Any YES → Immediate Escalation)
   - Step 3: Similar Function Duplication Check
4. Responsibility Boundaries
5. 5-step Workflow: Task Selection → Background Understanding → Implementation Execution → Completion Processing → Return JSON Result
6. Step Completion Gates [BLOCKING] embedded throughout
7. Structured Response Specification with 6 escalation response types (Design Doc Deviation, Similar Function Discovery, Investigation Target Not Found, Dependency Version Uncertain, Out of Scope File, Binding Decision Violation)
8. TDD-compliant implementation flow
9. Operation Verification step
10. Exit Gate [BLOCKING]

#### quality-fixer (330 lines)

**Frontmatter**:
```yaml
name: quality-fixer
description: Specialized agent for fixing quality issues in software projects. ...
tools: Bash, Read, Edit, MultiEdit, TaskCreate, TaskUpdate
skills: coding-principles, testing-principles, ai-development-guide, external-resource-context
```

**Workflow shape**:
1. Input Parameters
2. Initial Required Tasks
3. 6-step Workflow:
   - Step 1: Incomplete Implementation Check [BLOCKING — before any quality checks]
   - Step 2: Detect Quality Check Commands
   - Step 3: Execute Quality Checks
   - Step 4: Fix Errors
   - Step 5: Repeat Until Approved
   - Step 6: Return JSON Result
4. Status Determination: `stub_detected` | `approved` | `blocked`
5. JSON Output Format (internal structured response)
6. Intermediate Progress Report mechanism
7. Required Fix Patterns section

**Design implications**:
- Both agents bind to `ai-development-guide` in their `skills:` frontmatter (matching FR-9's pattern). This is **direct precedent** for FR-9's binding mechanism.
- The 6 escalation types in `task-executor` are blueprint inspiration for FR-4's dispatch matrix — they suggest concrete finding categories that the Level 4+ classifier should distinguish (design deviation → dispatch to design-composer; similar function discovery → dispatch to design-composer; investigation target not found → dispatch to discovery-codebase-researcher; etc.).
- `quality-fixer`'s Step 1 BLOCKING incomplete-implementation check is precedent for the **stub detection** mechanism that the Blueprint should incorporate into FR-2's per-task quality loop.
- The structured-JSON return pattern (both agents) is precedent for FR-7's execution-phase artifact schemas (per-task-execution-log, phase-quality-report).
- `task-executor`'s Step Completion Gates [BLOCKING] pattern is precedent for FR-5's state-transition hooks: every gate boundary blocks until verified.
- **Critical Blueprint decision**: these references are denser and more prescriptive than the project's existing planning-side sub-agents. The Blueprint must decide which structural patterns to adopt (escalation types, BLOCKING gates, JSON returns, stub detection) and which to leave out. Per PRD pre-Discovery note: "Blueprint inspiration only, not adopted verbatim."

---

## Batch A checkpoint summary

- **All 4 INs in Batch A produced confirmed findings** (no surprises; pre-scans validated; uploaded reference structures captured).
- **Pre-scan confirmations stand**: PRD Assumption A-1 and A-3 corrections in v1.1.0 are correct.
- **Resolutions validated**: Q-001 (install task per FR-9-e) and Q-002 (stub skill per FR-8-b) are appropriate given the actual filesystem state.
- **New design considerations surfaced**:
  - The ai-development-guide reference's Section 7 (4-phase quality workflow) may inform FR-3's phase-quality structure decomposition (Blueprint decision).
  - The 6 escalation types in task-executor are concrete inputs to FR-4's dispatch-matrix design.
  - quality-fixer's stub_detected status is precedent for incorporating stub detection into FR-2's per-task loop.
  - Frontmatter shape difference between the uploaded ai-development-guide (sparse) and typical project skills (richer) needs reconciliation in the Plan's install task — depends on shared-conventions.md (IN-004).

**Next batch (B)**: existing audit script landscape (IN-002, IN-006, IN-014).

---

## Batch B — Existing audit script landscape

### IN-002 — Audit scripts in `.claude/skills/KB-github-actions-platform/scripts/`

**Finding**: Two files. One audit script (`audit_workflow.py`), one reference (`action_versions.md`).

**Inventory**:
| File | Size | Type | Purpose |
|---|---|---|---|
| `audit_workflow.py` | 28,163 bytes | Python script | Static analysis of GitHub Actions workflow files; flags unpinned actions, broad permissions, script injection, dangerous patterns |
| `action_versions.md` | 10,013 bytes | Markdown reference | Action-version-pinning catalog (not a script — misplaced under `scripts/`) |

**`audit_workflow.py` interface**:
```
Usage:
    python audit_workflow.py path/to/workflow.yml
    python audit_workflow.py .github/workflows/         # directory: audits all .yml files
    python audit_workflow.py --json path/to/file.yml    # machine-readable output

CLI args:
    targets                positional, 1+ workflow files or directories
    --json                 emit machine-readable JSON
    --fail-on              {BLOCKER, MAJOR, MINOR}, default MAJOR — exit-code threshold

Exit codes:
    0 — no findings (or only INFO)
    1 — at least one MAJOR or BLOCKER finding (or as configured by --fail-on)
    2 — usage error / could not parse
```

**Self-description**: "This is a static linter — it can produce false positives. Use the output as a starting point for review, not as a gospel pass/fail."

**Design implication for FR-8-a**:
- `audit_workflow.py` is the canonical existing GHA audit script and should move to `auditing-github-actions/scripts/audit_workflow.py` per the 3-way split pattern.
- `action_versions.md` is reference material, not a script — should move to `auditing-github-actions/references/action_versions.md` during extraction (correcting the current misplacement under `scripts/`).
- The CLI signature is consistent with the broader auditing-* family conventions (see IN-014) — no API change needed during the move.
- `KB-github-actions-platform/SKILL.md` (19.3 KB, design wisdom) should remain in place; only `scripts/` and the misplaced `action_versions.md` move out per ADR-0031.

---

### IN-006 — Structural pattern of the `auditing-*` skill family

**Finding**: 8 skills in the family — 1 coordinator (`auditing-cc-configs`), 6 audit-module skills, 1 canonical helper library (`auditing-shared`). All audit-module skills share the same 5-subdirectory structure; the canonical helper library is structurally different.

**Family inventory** (alphabetical):
| Skill | Role | Sub-dirs | Script count |
|---|---|---|---|
| `auditing-cc-configs` | Coordinator + 24 cross-file checks | SKILL.md, assets/, examples/, references/, scripts/, tests/ | 6 |
| `auditing-context-files` | CLAUDE.md, MEMORY.md, rules audit | SKILL.md, assets/, examples/, references/, scripts/ | 7 |
| `auditing-hooks` | hooks.json + hook scripts audit | SKILL.md, assets/, examples/, references/, scripts/ | 3 |
| `auditing-mcp` | MCP config audit + secrets | SKILL.md, assets/, examples/, references/, scripts/ | 4 |
| `auditing-settings` | settings.json + output styles | SKILL.md, assets/, examples/, references/, scripts/ | 5 |
| `auditing-shared` | **Canonical helper library** | SKILL.md, scripts/ only | 2 (`pedagogical_marker_check.py`, `scan_memory_secrets.py`) |
| `auditing-skills` | SKILL.md + slash command audit | SKILL.md, assets/, examples/, references/, scripts/ | 5 |
| `auditing-subagents` | sub-agent + subagent-memory audit | SKILL.md, assets/, examples/, references/, scripts/ | 6 |

**Key structural conventions** (from `auditing-cc-configs/SKILL.md` and `auditing-shared/SKILL.md` inspection):

1. **Audit-module skills** carry: `SKILL.md` (the skill description + invocation guide), `scripts/` (the runnable Python), `examples/` (negative-example fixtures the scanners flag), `references/` (deep-dive specs), `assets/` (resources like prompts).
2. **Canonical helper library** (`auditing-shared`) carries: `SKILL.md` + `scripts/` only. Declares `user-invocable: false` in frontmatter. Established by ADR-0031 in v4.6.0.
3. **Frontmatter convention** for audit-module skills:
   - `name:` (skill identifier)
   - `description:` (purpose + when-to-invoke prose)
   - `allowed-tools:` (capability declaration: `Read Grep Glob Bash(python3 *)`)
   - `pedagogical_sections:` (optional list of paths exempt from anti-laundering rules per ADR-0030 — each item has `path:` + `justification:`)
4. **Common helper sharing**: Scripts that would otherwise duplicate across audit-module skills live in `auditing-shared/scripts/` and are dispatched via subprocess (e.g., `pedagogical_marker_check.py` is called by `auditing-cc-configs`, `auditing-skills`, `auditing-subagents`). Mechanism α (ADR-0030) requires single canonical implementation.
5. **Script naming convention**:
   - `audit_<thing>.py` — main entry for the skill
   - `validate_<thing>.py` — structural validators
   - `analyze_<thing>.py` — analysis with output report
   - `scan_<thing>.py` — scanners (commonly for secrets)
   - `check_<thing>.py` — discrete checks

**Design implication for FR-8 (both -a and -b)**:
- For `auditing-github-actions` (FR-8-a): mirror the audit-module pattern — SKILL.md + scripts/ + references/ + examples/ + assets/. Frontmatter: `name`, `description`, `allowed-tools`, plus `pedagogical_sections:` if example workflows contain credential-string fixtures.
- For `auditing-codespaces` (FR-8-b, stub): SKILL.md only is acceptable per the PRD; matches the **stub** definition. Frontmatter still declares `name`, `description`, `allowed-tools` (consistent skill shape across the family even with no scripts present).
- Any cross-audit helpers shared with GHA or Codespaces audit (surfaced during real implementation later) should land in `auditing-shared/scripts/`, not be duplicated in the new skills.

---

### IN-014 — Invocation patterns of existing audit scripts

**Finding**: All scripts in the auditing-* family follow a consistent CLI convention: `python3 <script> <target(s)> [--json] [--fail-on <severity>]`. Exit codes use the same semantic across scripts: 0 = pass, 1 = finding above threshold, 2 = usage error.

**Common CLI pattern** (observed across `audit_project.py`, `audit_workflow.py`, `audit_skill.py`, `audit_subagent.py`, etc.):
```
positional:    target(s) — file path or directory
--json         emit machine-readable JSON sidecar
--fail-on      {BLOCKER, MAJOR, MINOR} — exit-code threshold (default MAJOR)
```

**Coordinator-specific options** (`audit_project.py`, the cc-audit walker):
```
--with-runtime    enable MCP live probing
--managed         apply stricter enterprise lint
--report PATH     where to write the Markdown report
```

**Dispatch pattern**: `auditing-cc-configs` is the coordinator. It walks a project's `.claude/` tree, classifies each target by type, and dispatches to the appropriate sub-skill via `subprocess`. The full dispatch table (15 rows) maps target paths to audit-module skills. **The dispatch is currently scoped to `.claude/` tree only — GitHub Actions workflows under `.github/workflows/` and codespaces config under `.devcontainer/` are NOT in the current dispatch table.**

**Design implication for FR-3 and FR-8**:
- The phase-quality stage (FR-3) invokes three audit families: cc-audit project-wide, GitHub Actions workflow audit, GitHub Codespaces audit. These are **parallel invocations**, not a single coordinator's dispatch — because the cc-audit walker doesn't currently extend to `.github/` or `.devcontainer/`.
- **Blueprint decision** (surfaced from this batch): Does FR-3's invocation model adopt three parallel audit invocations (current de-facto pattern) OR extend the `auditing-cc-configs` dispatch table to include GHA + Codespaces targets, giving a single unified entry point? The dispatch-table extension would change `auditing-cc-configs/SKILL.md` and `audit_project.py`'s walker.
- Either way, the CLI conventions for the new audit scripts (when authored) must match the family pattern (`--json`, `--fail-on`, target-or-directory positional args).
- **Stub skill caveat for codespaces**: per FR-8-b's resolution, no codespaces audit script exists at this feature's ship time, so the FR-3 codespaces-audit step is a no-op pass placeholder until a future feature authors actual scripts.

---

## Batch B checkpoint summary

- **All 3 INs in Batch B produced clear findings.** No surprises in script structure or CLI convention.
- **Extraction path validated**: `audit_workflow.py` + `action_versions.md` are the only files needing relocation from `KB-github-actions-platform/scripts/` to `auditing-github-actions/scripts/` (and `.../references/` for the .md file). Clean extraction; no API change.
- **3-way split pattern crystallized**: KB-X-platform = "what" (design wisdom), KB-X-design = "how" (per-feature design references, where authored), auditing-X = "audit" (the scanners). ADR-0031 establishes this; the new auditing-github-actions + auditing-codespaces (stub) follow.
- **Canonical helper discipline**: any future cross-audit helpers go to `auditing-shared/scripts/`, never duplicated.
- **New Blueprint-time decision surfaced** (3rd of the discovery):
  - **(4)** Does FR-3's GHA + Codespaces audit invocation extend `auditing-cc-configs` dispatch table (unified entry), or stay as 3 parallel audit invocations (current de-facto)? The dispatch-table extension is more elegant; the parallel-invocation is what already exists.

**Next batch (C)**: convention & extension points (IN-004 shared-conventions; IN-005 shared-document-reviewer + KB-review-disciplines; IN-011 deliverable-archive-spec).

---

## Batch C — Convention & extension points

### IN-004 — `shared-conventions.md` structure and extension points

**Finding**: 220-line canonical spec at `.claude/skills/KB-documentation-criteria/references/shared-conventions.md`. Defines frontmatter format (universal + per-doc-type), supersession discipline (ADR-0005), versioning rules, traceability chain, file-naming convention, path discipline, YAML pitfalls, and cross-references.

**Section inventory**:
1. Frontmatter format — 5 universal required fields (`id`, `version`, `status`, `generated`, `generated_by`); 5-state vocabulary (`draft|proposed|accepted|superseded|rejected`)
2. Per-document-type frontmatter fields — IC, PRD, Blueprint, ADR, Plan each declare additional required fields
3. Supersession discipline (ADR-0005) — preserved versions, `predecessor:`/`superseded_by:` cross-linkage
4. Versioning rules — semver; "substantive content change" → minor or major; "structural change" → major; "typo/clarification" → patch
5. Traceability chain — IC → PRD-FRs → Blueprint-ACs → Plan-tasks → Tests/Validators
6. File-naming convention — explicit working/feature/<slug>/ layout
7. Path discipline — project-relative paths in document content
8. YAML pitfalls — unquoted colons, flow-sequence brackets, multi-line indicators, tabs
9. Cross-references — file references in backticks, doc IDs bare, version specificity rules

**Critical observations for FR-6 (frontmatter validator)**:

The 5-state vocabulary is the canonical source. Per-document-type required fields are:
- **Intent Clarification**: `feature_slug`, `user_token`
- **PRD**: `feature_slug`, `derived_from`
- **Blueprint**: `feature_slug`, `derived_from`, `predecessor` (when version > 1.0.0), `codebase_analysis`, `adrs_referenced`, `adrs_authored`
- **ADR**: `id` (ADR-NNNN format), `supersedes`, `change_summary`
- **Plan**: `feature_slug`, `derived_from`, `phases`, `total_tasks`

**Three current archive-vs-spec divergences observed** (carrying into the execution pipeline this feature is designing):
- The PRD frontmatter spec does NOT include `intent_user_token` — but our current PRDs (audit-findings-remediation-r1 archive and this feature's `prd-v1.1.0.md`) carry it. **Convention drift in practice.**
- The spec does NOT define a `gate_passed` field, but actual archive frontmatter (e.g., `prd-v4.6.0.md` in the prior shipped archive) carries `gate_passed`. **Convention drift in practice.**
- The spec does NOT define `reviewer_verdict` or `approved_at` fields, but archive practice uses them. **Convention drift in practice.**

**Design implication for FR-6 (frontmatter validator) and FR-11 (canonical state vocabulary)**:
- The validator (FR-6) must read `shared-conventions.md` for the authoritative per-document-type field list — but if archive practice has authoritative extension fields (`intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at`), the validator either accepts them as additional or the spec must be extended to canonicalize them.
- **Blueprint-time decision (5th of the discovery)**: Does this feature's PRD-revision-cycle add the missing fields to `shared-conventions.md` (canonicalizing archive practice), or does FR-6 accept them as "extension fields" without requiring spec update? The principled answer is: canonicalize them in `shared-conventions.md` (an ADR for the convention update; Plan task to apply edit). This may surface as a new ADR alongside the Blueprint, paired with U-6 / FR-11-e's ADR-canonicalizing-state-vocabulary work.
- The 5-state vocabulary itself is fully spec'd; FR-11's "canonical state vocabulary" job is mostly clarifying when each state applies, not introducing new states.
- YAML pitfalls section is directly applicable to FR-6's parser: it must handle quoted colons, flow-sequence brackets, multi-line indicators, etc.

---

### IN-005 — `shared-document-reviewer` agent + `KB-review-disciplines/` structure

**Finding**: One coordinator agent at `.claude/agents/shared-document-reviewer.md` (431 lines, model: opus, effort: high). Backed by one skill `KB-review-disciplines/` (8.1 KB SKILL.md + 6 references totaling 53 KB). Implements the Gate-0 / Gate-1 procedure that this feature's reviewer passes have been following.

**shared-document-reviewer agent shape**:

Frontmatter:
```yaml
tools: Read, Grep, Glob, LS, Bash(git diff:*), Bash(find:*), Bash(grep:*), Bash(rg:*), Bash(python3:*), TaskCreate, TaskUpdate, WebSearch
skills: KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines
model: opus
effort: high
```

Workflow:
1. Step 0: Input Context Analysis (MANDATORY)
2. Step 1: Parameter Analysis
3. Step 2: Target Document Collection
4. Step 3: Perspective-based Review (Gate 0 then Gate 1)
5. Step 4: Prior Context Resolution Check
6. Step 5: Self-Validation (MANDATORY before output)
7. Step 6: Return JSON Result

Review modes:
- **Composite Perspective Review** (recommended)
- Per-perspective modes (consistency, completeness, rule-compliance, clarity individually)
- DeliverableArchive Review (v4.5.0+)
- PedagogicalMarkerJustification Review (v4.6.0+)

Verdict mapping (from `severity-taxonomy.md`):
```
APPROVED
  Gate 0: all pass
  Consistency > 90, Completeness > 85
  Rule compliance: no severity:high
  Issues: no `critical`

APPROVED_WITH_CONDITIONS
  Gate 0: all pass
  Consistency > 80, Completeness > 75
  Rule compliance: only severity:medium or below
  Issues: only easily-fixable

NEEDS_REVISION
  Gate 0: any fail OR
  Consistency < 80 OR Completeness < 75 OR
  Rule compliance: any severity:high OR
  Issues: any `critical`, or many `important`

REJECTED
  Many critical issues; fundamental rework needed
```

**KB-review-disciplines references** (6 files, 53 KB total):
| File | Size | Purpose |
|---|---|---|
| `gate-0-1-procedure.md` | 12 KB | The Gate 0 + Gate 1 procedure (used in this feature's reviewer passes) |
| `architecture-audit.md` | 11 KB | Architecture Audit pass procedure (DesignDoc reviewer) |
| `cross-artifact-audit.md` | 9.7 KB | Cross-Artifact Audit procedure (post-Plan) |
| `severity-taxonomy.md` | 7.2 KB | 3-severity vocabulary + verdict thresholds |
| `issue-lifecycle.md` | 7.7 KB | Issue state machine across passes |
| `prior-context-check.md` | 7.0 KB | Step 4's prior-context-resolution-check spec |

**Critical observation for FR-3 and FR-4**:

The current `shared-document-reviewer` is the **document-side reviewer** — it reviews documents (PRDs, Blueprints, Plans, ADRs) for consistency, completeness, rule compliance, clarity. **There is no equivalent execution-side reviewer.** The phase-quality stage (FR-3) needs an execution-side analog — call it `execution-phase-quality-reviewer` — that:
- Reads phase-quality-report artifacts (per FR-7)
- Synthesizes the unit/integration/E2E/audit findings into a phase verdict
- Hands off failures to FR-4's dispatch matrix

**Critical observation for FR-9 (skill binding)**:

`shared-document-reviewer.md` already lists `skills: KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines` in its frontmatter. **Precedent for the skill-binding mechanism** that FR-9 will apply: the validator (FR-6) reads the `skills:` field and verifies bindings. This proves the binding mechanism works — it's already used by document-side agents. FR-9 extends it to execution-side code-producing agents.

**Design implications**:
- The 4 scoring dimensions (Consistency, Completeness, Rule compliance, Clarity) are **document-quality** dimensions. The execution-side phase-quality reviewer needs **execution-quality** dimensions — Blueprint must define these (likely: test pass rate, audit finding count, build correctness, validator-pass count). This is **new design work** for FR-3, not extension of existing.
- The Gate 0 + Gate 1 + Prior Context Check pattern is potentially adaptable for execution-side reviewer: Gate 0 = "Required artifacts exist" (per FR-7), Gate 1 = "Quality thresholds met". Blueprint should consider whether to mirror this structure or use a different shape.
- `severity-taxonomy.md`'s 3-severity vocabulary (critical / important / recommended) is potentially extensible to execution-phase findings — Blueprint decision.

---

### IN-011 — `deliverable-archive-spec.md` extension points for execution-phase artifacts

**Finding**: 175-line spec defining the canonical archive structure for FULL/MINOR/PATCH scope features. **FULL scope currently lists 13 stages with required artifacts.** Adding execution-phase artifacts requires extending this list.

**FULL-scope required artifacts** (BLOCKER if missing):
| Artifact | Stage that produces it |
|---|---|
| `intent-clarification.md` | Intent Clarification |
| `prd-v<N>.md` (highest N) | PRD Authoring |
| `research-plan.md` | Discovery Planning |
| `research-notes/<topic>.md` (≥1) | Discovery Research |
| `codebase-analysis.json` + `codebase-analysis-report.md` | Discovery Research |
| `synthesis.md` (or `synthesis/`) | Synthesis |
| `<layer>-design.md` + `<layer>-dependencies.json` (≥1 layer) | per-layer Design |
| `blueprint-v<N>.md` | Design Composition |
| `architecture-audit-issues.json` | Architecture Audit |
| `plan-v<N>.md` | Plan Authoring |
| `acceptance-tests.md` | Acceptance Test Authoring |
| `phase-validators.md` | Phase Validator Authoring |
| `cross-artifact-audit-issues.json` | Cross-Artifact Audit |
| `tasks.json` | Task Decomposition |
| `checkpoint.json` | (continuously updated) |
| `packager-report.json` | Deliverable Packaging (added in v4.5.0) |

**Critical observation for FR-7 (execution-phase artifact templates)**:

**ZERO execution-phase artifacts are currently named in the spec.** The spec covers only the **planning-side** stages (IC through Cross-Artifact Audit) and the **packaging** stage. Everything between Task Decomposition and Deliverable Packaging — the actual execution — has no spec'd artifact contract.

**The 5-artifact floor from FR-7-c maps onto this gap exactly**:
| FR-7-c artifact | Stage that produces it |
|---|---|
| per-task execution log | per-task execution loop (FR-2) |
| phase-quality report | phase-level quality stage (FR-3) |
| quality-reconciliation log | reconciliation loop (FR-4) |
| frontmatter-validation report | frontmatter validator (FR-6) |
| execution-reconciliation log | execution-level reconciliation cap (FR-10) |

**Plus the 4 candidate artifacts from Q-004** (deferred to Blueprint):
- `implementation-notes.md`
- `observations.md`
- `acceptance-matrix.md`
- `cross-artifact-audit-final.md`

**Design implication for FR-7**:
- The Blueprint must author execution-phase artifact templates AND a Plan task to extend `deliverable-archive-spec.md` (per AC-FR-7-a-or-b) so these artifacts become canonically named, required in FULL scope, and validated.
- The extension to `deliverable-archive-spec.md` is a **specification change** that warrants an ADR (per ADR-0019's naming convention). Likely co-authored with the Blueprint.
- The conditional-artifacts table ("MAJOR if missing without justification") already has a pattern for "required only under condition X" — execution-phase artifacts naturally fit this (e.g., `quality-reconciliation log` is conditional on the reconciliation loop having fired). Blueprint should use the conditional pattern where appropriate.
- **The "PATH" pattern**: existing artifacts use both `.json` (machine-parseable) and `.md` (human-narrative). FR-7-b's "≥1 machine-parseable per artifact" requirement should respect this — the spec's existing pattern is "X.json for the data + X.md for the narrative" (e.g., `codebase-analysis.json` + `codebase-analysis-report.md`). Blueprint should consider whether execution-phase artifacts follow the same pair pattern or use a unified format.

**Backward-compat note observed**: v4.5.0 added `packager-report.json`; pre-v4.5.0 archives are grandfathered. **Same pattern will apply when this feature ships** — pre-feature execution runs won't have the new execution-phase artifacts; the validator should treat them as MINOR (not BLOCKER) for archives whose `checkpoint.json` predates this feature's ship date.

---

## Batch C checkpoint summary

- **All 3 INs in Batch C produced rich findings**. Two new Blueprint-time decisions surfaced (5th, 6th of the discovery).
- **Three convention-drift items observed in IN-004**: `intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at` — all in archive practice but not in spec. **Blueprint decision (5th): canonicalize via spec update + ADR, or accept as extension fields in FR-6 validator?**
- **The Gate 0 + Gate 1 + Prior Context pattern is potentially adaptable** for the execution-side phase-quality reviewer that FR-3 implies (currently no such reviewer exists). Document-side reviewer is precedent; execution-side reviewer is new.
- **Existing skill-binding precedent confirmed**: `shared-document-reviewer.md`'s `skills:` frontmatter field is the mechanism FR-9 will extend. FR-6 validator already has a precedent target.
- **The deliverable-archive-spec has ZERO execution-phase artifacts spec'd today** — the spec needs extension by this feature. The 5-artifact floor + 4 Q-004 candidates are the candidate set. Likely paired with an ADR.
- **Blueprint decision (6th)**: Does FR-7 follow the existing "X.json + X.md" pair pattern for execution-phase artifacts, or use a unified format?

**Next batch (D)**: agent landscape + gates (IN-007 planning-side agents; IN-008 gate structure; IN-010 prior archive ad-hoc artifacts; IN-012 deviation surfacing per ADR-0029).

---

## Batch D — Agent landscape + gates

### IN-007 — Planning-side agent inventory

**Finding**: 31 agents at `.claude/agents/`. Organized by pipeline stage: 2 intake, 1 discovery-planning, 2 discovery-research, 5 synth, 9 design, 1 design-composer, 3 review (architecture/cross-artifact/document), 3 finalize (reconciler, task-decomposer, packager), 2 test-authoring, 1 critique, 1 shared-document-reviewer. **No orchestrator file** — orchestration is encoded in the agent prompts themselves + the user-facing pipeline that selects which agent to invoke at each gate.

**Full inventory grouped by pipeline-stage role**:

| Stage role | Agents | Notes |
|---|---|---|
| Intake | `intake-intent-clarifier`, `intake-prd-author` | Gate 1, Gate 2 |
| Discovery Planning | `discovery-plan-author` | Gate 3 |
| Discovery Research | `discovery-codebase-researcher`, `discovery-external-researcher` | No user gate; fan-out |
| Synthesis | `synth-substrate`, `synth-framer`, `synth-grapher`, `synth-extractor`, `synth-synthesizer`, `synth-critic` | 6 synth agents = micro-pipeline within Synthesis |
| Per-layer Design | `design-api`, `design-backend`, `design-cicd`, `design-claude-code`, `design-codespaces`, `design-database`, `design-frontend`, `design-iac`, `design-query` | 9 layers; only activated layers fire per PRD Layer Scope |
| Design Composition | `design-composer` | Single composer |
| Architecture Audit | `review-architecture-auditor` | DesignDoc reviewer pattern |
| Plan Authoring | `plan-author` | Gate 7 |
| Acceptance Test Authoring | `test-acceptance-author` | |
| Phase Validator Authoring | `test-phase-validator-author` | |
| Cross-Artifact Audit | `review-cross-artifact-auditor` | Pattern from KB-review-disciplines |
| Reconciliation | `finalize-reconciler` | 4-cycle budget per ADR-0017 (canonical home; see IN-009 Batch E for ADR-0021 mis-credit surfacing) |
| Task Decomposition | `finalize-task-decomposer` | Produces tasks.json |
| Deliverable Packaging | `finalize-deliverable-packager` | Added in v4.5.0 per ADR-0027 |
| Critique (cross-stage utility) | `cc-critique`, `synth-critic` | |
| Document review (cross-stage utility) | `shared-document-reviewer` | Used at every gate |

**Common frontmatter shape** (observed across all 31 agents):
```yaml
name: <agent-name>
description: <when-to-use prose>
model: opus | sonnet
effort: high | medium | low
tools: [Read, Glob, Grep, Write, AskUserQuestion, TaskCreate, TaskUpdate, ...]
skills: [KB-skill-1, KB-skill-2, ...]
memory: project | none
```

The `skills:` field is the binding mechanism FR-9 will extend. The `tools:` field constrains capabilities. The `memory:` field controls cross-invocation state.

**Workflow shape** (observed across all agents): Each agent has a deterministic procedure: at-task-start reads (KBs/templates), inputs (from orchestrator prompt), phased procedure with explicit Step gates, output protocol, exit. The `intake-intent-clarifier.md` template (93 lines, 6 sections: At task start, Inputs, Procedure with 4 Phases, Output, Memory discipline, What you do NOT do) is representative.

**Design implication for FR-1 (pipeline structure) and FR-9 (skill binding)**:
- The execution-side pipeline structure (FR-1) follows precedent: per-task execution agents will be code-producing sub-agents with the same frontmatter shape (name, description, model, effort, tools, skills, memory).
- Per FR-9, every execution-phase code-producing sub-agent must list `ai-development-guide` in `skills:`. Precedent: `shared-document-reviewer.md` lists 3 KB skills; new execution-side agents will list `ai-development-guide` + others.
- **Open Blueprint decision**: are execution-phase sub-agents a new family (e.g., `execute-*`) at `.claude/agents/`, or a new namespace, or co-existing with current 31? The cleanest structural answer mirrors the planning-side family: define new `execute-task-runner`, `execute-quality-checker`, etc. as siblings under `.claude/agents/`.

---

### IN-008 — Gate structure and gate-firing mechanism

**Finding**: Gates are encoded as **user-confirmation points** in the agent prompts themselves. There is no central gate-dispatcher; each agent's procedure includes "exit with user confirmation token" semantics. The `finalize-reconciler` agent encodes the 4-cycle reconciliation cap explicitly.

**Gate-firing pattern** (from inspection of `intake-intent-clarifier.md` + `finalize-reconciler.md`):
- An agent runs its procedure end-to-end, writes the artifact, then exits via `TaskUpdate`.
- The orchestrator (user-side) then invokes `shared-document-reviewer` to perform Gate 0 + Gate 1 on the new artifact.
- If reviewer verdict is `approved` or `approved_with_conditions`, the user provides a confirmation token, which is stamped into the artifact's frontmatter (`user_token: ...`).
- The next pipeline stage's agent is invoked, taking the prior artifact as input.

**Reconciliation pattern** (from `finalize-reconciler.md`):
- 6-phase procedure: read issues → categorize → determine dispatch set → convergence check (cycle > 1) → 4-cycle hard cap handling → author log.
- **Convergence check** (Phase 4): for each prior issue, detect persistence. First persistence: continue normally. Second persistence: recommend structural change. Third persistence (cycle 4): surface to user.
- **4-cycle hard cap** (Phase 5): if `cycle_number == 4`, output explicitly recommends either "ship with documented exceptions" OR "escalate to user with detailed open-issue list".
- **Dispatch decisions** map issue categories to re-author targets: PRD revision → `intake-prd-author`; Blueprint revision (cross-cutting) → `design-composer`; per-layer Design revision → `design-<layer>`; Plan revision → `plan-author`; Acceptance Tests/Phase Validators → respective test authors.

**Design implication for FR-4 (reconciliation dispatch matrix) and FR-10 (reconciliation budget)**:
- FR-4's execution-side dispatch matrix follows the `finalize-reconciler` shape but with execution-side categories: implementation bug → `execute-task-runner` re-invocation; quality-check failure → `execute-quality-checker`; phase-quality regression → phase-quality-reviewer; etc. **Blueprint authors the execution-side analog of finalize-reconciler.**
- The 4-cycle hard cap (ADR-0021) is the planning-side budget. FR-10's "execution reconciliation budget" must declare its own cap — Blueprint decision (likely also 4 to mirror, but could be different).
- The convergence-check mechanism (persistence detection across cycles) is reusable wholesale.
- **Gate-firing mechanism is uniform** — no new gate framework needed for execution; same pattern (agent runs → reviewer audits → user confirms with token).

---

### IN-010 — Prior archive `audit-findings-remediation-r1` ad-hoc artifacts

**Finding**: The prior shipped feature archive contains **9 ad-hoc artifacts not currently named in `deliverable-archive-spec.md`**. Each has a frontmatter-declared `artifact_type:` field, and each carries content that maps onto an execution-phase concern that FR-7's templates need to cover.

**Ad-hoc artifacts inventory** (extracted from `working/feature/audit-findings-remediation-r1/`):

| Ad-hoc artifact | `artifact_type:` | Frontmatter declaration | Purpose |
|---|---|---|---|
| `acceptance-matrix.md` | (not labeled) | `version, status, generated, generated_by` | AC-to-evidence traceability matrix produced at execution-completion time |
| `cross-artifact-audit-final.md` | (not labeled) | similar | Final cross-artifact audit after all execution reconciliation cycles |
| `final-audit-report.md` | `FinalAuditReport` | `verdict: SHIP-READY`, `findings_summary`, `companion_artifact: final-audit.json` | The final phase-quality report (auditing-cc-configs full project audit) |
| `final-audit.json` | (machine-parseable sidecar) | n/a | JSON sidecar to `final-audit-report.md` |
| `implementation-notes.md` | `ImplementationNotes` | `documents_phase: Execution (Phase 0 — Phase 4)` | Per-finding execution dispositions; Cat A/B/C disposition vocab |
| `observations.md` | `ObservationsLog` | `purpose: append-only log of mid-execution deviations and auditor improvements beyond plan scope`, `entry_count: 6`, `entries: [OBS-EXEC-001..006]` | **Direct precedent for FR-7's execution-deviation surfacing per ADR-0029** |
| `packager-report-final.json` | (machine sidecar) | n/a | Companion to `packager-report.json` produced at the last cycle |
| `reconciliation-log-cycle1.md` | `ReconciliationLog` | `cycle: 1`, `budget_used_so_far: 1`, `adr_reference: ADR-0021` | Per-cycle reconciliation log; FR-4 / FR-10 precedent |
| `reconciliation-log-cycle2.md` | `ReconciliationLog` | `cycle: 2`, `budget_used_so_far: 2` | Same |
| `x9-verification/x9-status.json` + `x9-status.md` | (ad-hoc subdirectory) | n/a | Phase-9 final verification dossier |

**Critical observation about `observations.md`**:
- This is the **observed instance** of ADR-0029's deviation-surfacing discipline at execution time. The frontmatter declares 6 entries, each with structured fields: location, verbatim, discipline-violated, severity-classification, surfaced-by, root-cause-hypothesis, disposition, follow-on-feature-implications.
- This is exactly what FR-7's "execution-reconciliation log" — or possibly a separate ObservationsLog artifact — should standardize. The structure is well-formed enough to canonicalize.

**Critical observation about pair pattern**:
- `final-audit-report.md` (narrative) + `final-audit.json` (machine-parseable sidecar) follows the existing spec pattern (`codebase-analysis.json` + `codebase-analysis-report.md`).
- `packager-report-final.json` is JSON only — no .md companion. This is a **divergence from the pair pattern**; Blueprint should decide whether to canonicalize the pair convention or allow .json-only artifacts.

**Design implication for FR-7-c (5-artifact floor) + Q-004 (4 additional candidates)**:

The actual archive evidence suggests the floor should be larger than 5 and the Q-004 candidates aren't speculative:

| FR-7-c floor (PRD) | Archive evidence |
|---|---|
| per-task execution log | (implicitly captured in `implementation-notes.md` — Cat A/B/C dispositions per task) |
| phase-quality report | `final-audit-report.md` |
| quality-reconciliation log | `reconciliation-log-cycle1.md`, `reconciliation-log-cycle2.md` |
| frontmatter-validation report | (not in archive — gap; this feature's FR-6 introduces it) |
| execution-reconciliation log | `reconciliation-log-cycleN.md` is also this; OR Blueprint splits quality-reconciliation from execution-reconciliation |

| Q-004 candidate | Archive evidence |
|---|---|
| `implementation-notes.md` | ✓ present (15.5 KB) — substantive content |
| `observations.md` | ✓ present (27.4 KB) — substantive content; ADR-0029 precedent |
| `acceptance-matrix.md` | ✓ present (5.4 KB) — AC-to-evidence traceability |
| `cross-artifact-audit-final.md` | ✓ present (4.1 KB) — final cross-artifact audit |

**All four Q-004 candidates are present and content-rich in the prior archive.** The Q-004 question (deferred to Blueprint per AC-FR-7-d) is whether to canonicalize all four — the archive evidence is "yes, they earned their place".

**Plus three additional artifacts** the archive surfaced beyond Q-004:
- `final-audit-report.md` + `final-audit.json` pair — the actual phase-quality-report incarnation
- `x9-verification/` subdirectory — phase-9 final verification dossier (Blueprint-time: does this become a canonical `phase-9-verification.md` artifact, or is it specific to the prior feature's structure?)

---

### IN-012 — ADR-0029 deviation surfacing — specific application points

**Finding**: ADR-0029 ("No-silent-scope-changes principle — every scope deviation must surface") is accepted and codifies the surfacing discipline across all 13 planning-side stages plus implicitly the execution side. It names per-stage surfacing locations and requires audit-stage enforcement.

**Per-stage surfacing locations** (from ADR-0029 § "Operational rules" §2):

| Stage | Surfacing location |
|---|---|
| Intent Clarification | (N/A — intent itself defines scope) |
| PRD Authoring | "Undetermined Items" section + explicit annotation |
| Discovery Planning | "Open questions for human resolution" |
| Discovery Research (codebase) | `codebase-analysis-report.md` — "Scope-deviation findings" section |
| Discovery Research (external) | Per-topic research note — explicit annotation |
| Synthesis | `synthesis.md` — "Surfaced scope deviations" section |
| Per-layer Design | `<layer>-design.md` — "Q-`<LAYER>`-N" open questions; mark `scope-deviation: yes` |
| Design Composition | `blueprint-v<N>.md` — "Architectural Questions" carries forward layer deviations |
| Architecture Audit | `architecture-audit-issues.json` — gains `scope_deviation` boolean per issue |
| Plan Authoring | `plan-v<N>.md` — "Risks" section flags any plan-time scope discoveries |
| Acceptance Test / Phase Validator | Document any AC or validator that can't be authored as PRD-stated |
| Cross-Artifact Audit | `cross-artifact-audit-issues.json` — gains `scope_deviation` boolean; MUST check upstream artifacts for unsurfaced deviations |
| Reconciliation | `reconciliation-log-r<R>.md` — surface any unresolved deviation as cycle blocker |
| Task Decomposition | `tasks.json` — any task that exceeds PRD scope is a deviation |
| Deliverable Packaging | `packager-report.json` — final check |

**Resolution paths** (from ADR-0029 § "Operational rules" §4):
- (a) PRD amendment — update PRD, version bump, re-approval
- (b) Defer to follow-on feature — record in handoff
- (c) Reject the deviation — record with rationale
- **Silent absorption is NOT among the resolution paths.**

**Triviality is explicitly disallowed** as a surfacing-skip justification: "nothing should be silent because 1 could be major."

**Execution-stage extension gap**:
- ADR-0029 lists 13 planning-side surfacing locations + Reconciliation (covers post-execution audit cycles). It does NOT explicitly enumerate the **execution-phase** surfacing locations:
  - Per-task execution → where surface? (implicit: in implementation-notes.md per the prior archive)
  - Phase-level quality stage → where surface? (implicit: in observations.md per the prior archive)
  - Quality-reconciliation loop → where surface? (overlaps with planning-side Reconciliation's reconciliation-log-r<R>.md pattern)
- The prior archive's `observations.md` is the *de-facto* execution-side surfacing artifact (6 OBS-EXEC-NNN entries with full root-cause analysis). But it's not yet ADR-codified.

**Design implication for FR-7 + a likely new ADR**:
- The Blueprint should author a new ADR extending ADR-0029 with explicit execution-phase surfacing locations:
  - Per-task → entries in per-task execution log (or implementation-notes.md if Blueprint canonicalizes that)
  - Phase-quality → entries in observations.md OR phase-quality report
  - Quality reconciliation → entries in quality-reconciliation log
- OR the Blueprint argues that the existing 14 surfacing locations cover execution implicitly (via Reconciliation log) — but the prior archive's evidence shows this isn't sufficient; execution deviations want their own surface.
- The audit-stage enforcement (ADR-0029 §3) is a real check that should land in FR-3's phase-quality stage: scan upstream artifacts for unsurfaced deviations during the execution audit.

---

## Batch D checkpoint summary

- **All 4 INs in Batch D produced significant findings**. Two more Blueprint-time decisions surfaced.
- **31 planning-side agents inventoried** with uniform frontmatter shape (name, description, model, effort, tools, skills, memory). The skill-binding mechanism (FR-9) extends a proven pattern.
- **No orchestrator file exists** — orchestration is encoded in agent prompts + user-facing pipeline. **Blueprint decision (7th)**: should the execution-side pipeline introduce an orchestrator agent, or follow planning-side precedent (orchestration distributed across agent prompts)?
- **The reconciliation pattern** from `finalize-reconciler.md` (6-phase procedure, convergence detection, 4-cycle hard cap) is reusable wholesale for FR-4 + FR-10's execution-side analog.
- **Prior archive evidence** validates Q-004's 4 candidate artifacts: `implementation-notes.md`, `observations.md`, `acceptance-matrix.md`, `cross-artifact-audit-final.md` are all present in `audit-findings-remediation-r1/` with substantive content. The Q-004 question's principled answer is "canonicalize all 4 in FR-7's template floor", lifting the FR-7-c floor from 5 to 9 artifacts (plus the `.json` machine-parseable pair pattern for at least 3 of them).
- **Blueprint decision (8th)**: extend ADR-0029 with explicit execution-phase surfacing locations, OR argue existing 14 cover execution implicitly?
- **The `observations.md` content shape** (entry_count, entries list, per-entry structured fields: location, verbatim, discipline-violated, severity-classification, root-cause-hypothesis, disposition, follow-on-feature-implications) is canonical-template-ready.

**Next batch (E)**: ADRs (IN-009) — read ADR-0021, ADR-0029, ADR-0030, ADR-0031 in full to confirm inheritances.

---

## Batch E — ADRs (inheritances confirmed)

### IN-009 — ADR inheritances and their forward implications for execution pipeline

**Finding**: 4 ADRs read in full. Each contributes specific inheritances + forward implications the Blueprint must respect. A 5th surfaced during the read: **ADR-0017** is the canonical home of the 4-cycle reconciliation cap (not ADR-0021, as the PRD informally credited).

#### ADR-0021 — Discovery phase architecture

**Status**: Accepted 2026-05-19. Inherits from ADR-0006, ADR-0007 v2.0.0, ADR-0009, ADR-0018, ADR-0019, ADR-0020.

**Three commitments**:
1. **Discovery Planning input contract requires KB+ADR consultation**: `discovery-plan-author`'s rationale brief MUST include path to approved PRD + paths to all KBs in Layer Scope + paths to all existing ADRs. The agent MUST inventory existing KBs/ADRs, identify KB-gaps, identify ADR-conflicts.
2. **External research is conditional**: If KB-gap analysis shows all open questions already addressed, declare `external_research: skipped` with per-question rationale. Discovery Research invokes only `discovery-codebase-researcher`. (This feature's research-plan is exactly this case: 0/6 external topics; all 17 INs covered by codebase research.)
3. **Discovery Research fan-out semantics**: `discovery-codebase-researcher` always × 1; `discovery-external-researcher` × N (N=0 for this feature). Generic-with-N-invocations pattern (single agent template invoked N times).

**Forward implications for execution pipeline**:
- ADR-0021 is **discovery-phase-specific** — it does NOT directly constrain execution-phase design.
- BUT its KB+ADR-consultation pattern is reusable: the execution-side phase-quality reviewer (FR-3) and per-task execution agent (FR-2) should read the **Blueprint** and **Plan** at task start, not just the task file. Mirrors ADR-0021's "consult what's already known" principle.
- The fan-out pattern (generic-with-N-invocations) is precedent for FR-2's per-task execution loop if multiple tasks are dispatched in parallel. **Blueprint decision (9th)**: does FR-2's per-task loop run tasks serially or fan out per-task-DAG-level (per `tasks.json`)?

**IMPORTANT CORRECTION**: The PRD v1.1.0 credits ADR-0021 with the "4-cycle reconciliation cap" in Assumption A-related context. **This credit is misplaced.** ADR-0021 covers discovery phase architecture; it does NOT contain the 4-cycle cap. The 4-cycle cap is canonical in **ADR-0017** (document-reviewer-integration), which states: *"Iteration cap: 4 cycles (matching the pipeline's broader fixed-point iteration discipline from blueprint v3 §3.7)"*. The cap is "blueprint v3 §3.7" by reference; ADR-0017 surfaces it for the reviewer-integration use case.

**Surfaced as scope-deviation per ADR-0029**: This is a documentation-accuracy finding. Resolution paths (per ADR-0029 §4):
- (a) PRD amendment: correct the ADR reference. (FR-10's mention of "4-cycle cap per ADR-0021" should become "per ADR-0017".)
- (b) Defer to follow-on: noted in handoff, not amended this run.
- (c) Reject: leave the misattribution.

Recommended resolution: **(a) PRD amendment** as a TINY edit (single-field correction). Since the PRD is already at v1.1.0, this could either be folded into the eventual Blueprint authoring step or batched with other minor cleanups. The mis-credit doesn't affect the substantive design — it just affects citation accuracy. **Surfacing here, recommending PRD edit on next revision.**

#### ADR-0017 — Document-reviewer integration (canonical 4-cycle cap)

**Status**: Accepted (pre-v4.5.0). Forward-cited by ADR-0021 and others.

**Key inheritance for execution pipeline**:
- The 4-cycle iteration cap originated in blueprint v3 §3.7 as a general fixed-point iteration discipline. ADR-0017 surfaces it for shared-document-reviewer's iteration loop with reconciler.
- **FR-10's execution-reconciliation budget should cite ADR-0017** (or, more accurately, "blueprint v3 §3.7's fixed-point iteration cap, surfaced for execution-side reconciliation").
- The convergence-check pattern in `finalize-reconciler.md` (Phase 4: detect persistence; first persistence = continue, second = recommend structural change, third = escalate to user) is co-canonical with the 4-cycle cap. **Reusable wholesale for FR-4's execution-side dispatcher.**

#### ADR-0029 — No-silent-scope-changes principle

**Status**: Accepted 2026-05-21. Authored during `audit-findings-remediation-r1` Gate 3.

**Reread captured the Forward implications section** (not visible in Batch D's read):
- Several existing stage templates (`codebase-analysis-report.md`, `synthesis.md`, audit JSON schemas, `packager-report.json`) need a new "Scope-Deviation" structural element. **Out of scope for ADR-0029 itself; a follow-on machinery feature run implements the templates + audit checks.**
- The `audit-findings-remediation-r1` feature itself is bound by the principle going forward.
- **Risk of over-application**: Authors may mistake "any unexpected detail" for "scope deviation" and surface trivia. The rule-of-thumb in the ADR: *"a finding is a scope deviation when it would change what the PRD's acceptance criteria require, or when it would change the count of files / agents / specs the feature must touch by ≥1 (regardless of magnitude)."*

**Forward implication for THIS feature**: 
- The "follow-on machinery feature run" that ADR-0029 anticipated includes **execution pipeline machinery** (this feature). FR-7's execution-phase artifact templates ARE the partial fulfillment of ADR-0029's "templates need a new Scope-Deviation structural element."
- **Blueprint decision (already enumerated as #8)**: extend ADR-0029 with explicit execution-phase surfacing locations, OR argue the existing 14 cover execution implicitly?
- **Strengthening**: this feature is materially advancing ADR-0029's machinery agenda. The Blueprint should explicitly trace ADR-0029 → FR-7 → specific execution-phase template fields (`scope_deviations_surfaced:` per-artifact, ObservationsLog entries, etc.).

#### ADR-0030 — Mechanism α (pedagogical-marker justification)

**Status**: Accepted 2026-05-21. Authored alongside ADR-0031 in `audit-findings-remediation-r1` Design Composition.

**Key inheritance**: Every pedagogical marker (frontmatter `pedagogical_sections:` entry OR block-level `audit-example` fence) MUST carry an inline justification. Auditor REJECTS markers without justification.

**Forward implications for execution pipeline (FR-6 frontmatter validator)**:
- FR-6's frontmatter validator MUST check `pedagogical_sections:` entries for `justification:` fields. If any entry lacks justification, surface as severity:high (the marker is treated as absent, the underlying finding surfaces at original severity).
- The Blueprint should consider whether FR-6 reuses `auditing-shared/scripts/pedagogical_marker_check.py` directly (subprocess) or implements the check natively. **Reuse via subprocess is preferred** — single source of truth per ADR-0030 + ADR-0031.

**Forward implications for ADR-0029 (mechanism α IS a no-silent-failure mechanism at the marker level)**:
- ADR-0030 explicitly notes: *"Aligns with ADR-0029 (no-silent-scope-changes). Mechanism α IS a no-silent-failure mechanism applied at the marker level; ADR-0029 is the same principle applied at the stage level. Symmetric discipline."*
- This is a strong design-pattern statement: the project has a meta-discipline of "no silent failures" applied at multiple layers (markers, stages, scope changes). The execution pipeline must extend this pattern. **FR-3 phase-quality stage cannot silently pass; FR-4 reconciliation cannot silently absorb findings; FR-6 validator cannot silently pass invalid frontmatter.**

#### ADR-0031 — auditing-shared skill module

**Status**: Accepted 2026-05-21.

**Key inheritance**: Canonical home for utilities shared across the auditing-* skill family. Initial contents: `pedagogical_marker_check.py`, `scan_memory_secrets.py`. Established to eliminate 3-copy duplication.

**Canonical implementation rules** (from the ADR):
1. **Single source of truth** — each utility lives in exactly one file under `auditing-shared/scripts/`.
2. **Backward-compatibility preserved** — real semantic differences (e.g., `location`/`where` field-name compat) preserved in the canonical implementation.
3. **Subprocess invocation pattern unchanged** — dispatchers reference filesystem path, not Python import name.
4. **No new behavior in the merge** — output equivalence pre- and post-deduplication, modulo new ADR-0030 check.

**Forward implications for execution pipeline (FR-8 3-way split extension)**:
- ADR-0031 established the 3-way split pattern (KB-X-platform = "what", KB-X-design = "how", auditing-X = "audit"). FR-8 extends this pattern to GitHub Actions (FR-8-a) and Codespaces (FR-8-b stub).
- The Blueprint should cite ADR-0031 when describing FR-8's extraction rationale — extension of an established pattern, not a new architectural decision.
- **Any new audit utilities introduced by this feature** (e.g., if FR-6's frontmatter validator includes a `pedagogical_sections:`-checker for execution-side artifacts) should land in `auditing-shared/scripts/` per ADR-0031's single-source-of-truth rule. **Blueprint decision (10th)**: FR-6's frontmatter validator — does it become a new `auditing-shared/scripts/validate_frontmatter.py`? Or does it live elsewhere (e.g., `auditing-cc-configs/scripts/validate_frontmatter.py` — but that already exists for cc-configs sub-skill audit)?

**Conflict check**: `auditing-skills/scripts/validate_frontmatter.py` exists. FR-6's new frontmatter validator is **NOT** the same thing — FR-6 validates pipeline-document frontmatter (PRDs, Blueprints, Plans), while `auditing-skills`'s validate_frontmatter.py validates SKILL.md frontmatter. **Blueprint should make this distinction explicit to avoid naming collision.**

---

## Batch E checkpoint summary

- **All 4 ADRs (0021, 0029, 0030, 0031) read in full**. Inheritances confirmed.
- **One material correction surfaced**: 4-cycle cap is canonical in ADR-0017, not ADR-0021 as PRD informally credits. Recommended PRD edit on next revision (or fold into Blueprint citation accuracy).
- **One meta-discipline pattern crystallized**: "No silent failures" applies at marker level (ADR-0030), stage level (ADR-0029), and now must apply at execution level (this feature). FR-3, FR-4, FR-6 all need to enforce this symmetric discipline.
- **One new Blueprint decision** (10th): where does FR-6's frontmatter validator live — `auditing-shared/scripts/validate_pipeline_frontmatter.py` (new, distinct from `auditing-skills/scripts/validate_frontmatter.py`)?
- **One PRD-cascade-worthy observation** (the ADR-0017 vs ADR-0021 4-cycle-cap credit): recommended resolution is option (a) PRD amendment, batched with other minor cleanups. Surfacing here per ADR-0029.

**Next batch (F)**: template directory conventions (IN-015).


---

## Batch F — Template directory conventions

### IN-015 — Where execution-phase artifact templates should live

**Finding**: 6 templates currently exist at `.claude/skills/KB-documentation-criteria/references/templates/`. Each is a self-describing document — frontmatter declares the template's own `id` placeholder, the `## Contents` checklist serves as both authoring guide AND reviewer's Gate 0 structural-presence anchor.

**Current template inventory** at `KB-documentation-criteria/references/templates/`:

| Template | Size | Maps to stage |
|---|---|---|
| `adr-template.md` | 5.5 KB | ADR authoring (any stage) |
| `blueprint-template.md` | 39 KB | Design Composition |
| `intent-clarification-template.md` | 5.5 KB | Intent Clarification |
| `plan-template.md` | 7.4 KB | Plan Authoring |
| `prd-template.md` | 15 KB | PRD Authoring |
| `research-plan-template.md` | 8.3 KB | Discovery Planning |

**Common template structure** (observed across all 6):
1. **Frontmatter block** — declares the document's `id`, `version`, `status`, `feature_slug`, `derived_from`, `generated`, `generated_by` placeholders. Per-doc-type fields per `shared-conventions.md`.
2. **`# <Doc Type>: [Feature Name]`** — H1 title with placeholder
3. **`## Contents`** — section completion checklist as `- [ ] Section Name` items (the canonical Gate 0 anchor)
4. **Section-by-section authoring guide** — each H2 section in the template lists the required fields/sub-sections and authoring guidance

**Template loading convention**:
- Agents load templates by reading the file directly. Example from `intake-prd-author.md`: *"Read `prd-template.md` in KB-documentation-criteria. This is the canonical structure your output must follow."*
- 5 agents directly load templates (per grep): `design-composer.md`, `design-frontend.md`, `discovery-plan-author.md`, `finalize-deliverable-packager.md`, `review-architecture-auditor.md`. Other agents load via prose reference (e.g., "read prd-template.md in KB-documentation-criteria").
- Templates are referenced by **filename within `templates/`**, not absolute path, per the path-discipline convention in `shared-conventions.md`.

**Broader `KB-documentation-criteria/references/` structure**:

```
KB-documentation-criteria/references/
├── deliverable-archive-spec.md      (10.8 KB — archive contract per scope class)
├── disciplines/                     (5 authoring discipline guides)
│   ├── design-composition.md
│   ├── discovery-planning.md
│   ├── ears-acceptance-criteria.md
│   ├── plan-authoring.md
│   └── prd-authoring.md
├── layer-taxonomy.md                (10.9 KB — 9-layer taxonomy)
├── pedagogical-marker-justification-spec.md (19 KB)
├── pedagogical-marker-justification-spec-substance-keywords.txt (1.3 KB)
├── rationale-brief.md               (10.8 KB — ADR-0009 instruction)
├── shared-conventions.md            (10.1 KB — universal conventions)
└── templates/                       (6 templates as inventoried above)
```

**KB-documentation-criteria's stated scope** (from its SKILL.md frontmatter description): *"Canonical templates, authoring disciplines, and shared conventions for every document the feature-pipeline produces: Intent Clarification doc, PRD, Blueprint, ADRs, and Plan."*

**KB-* family inventory** (22 KBs total):
| Domain | KBs |
|---|---|
| Documentation | KB-documentation-criteria, KB-review-disciplines |
| Coding | KB-general-coding-principles, KB-codebase-research, KB-task-decomposition |
| Per-layer design | KB-api-design, KB-backend-design, KB-cc-design, KB-codespaces-design, KB-database-design, KB-frontend-design, KB-github-actions-design, KB-iac-design, KB-query-design, KB-design-system-design, KB-component-architecture-design, KB-ux-design, KB-visual-design |
| Per-layer platform | KB-cc-platform, KB-codespaces-platform, KB-github-actions-platform, KB-storybook-platform |

**Design implication for FR-7's execution-phase templates — where should they live?**

Three options identified in this batch:

**Option A** — Add to `KB-documentation-criteria/references/templates/` alongside existing 6:
- Pros: Mirrors the existing pattern; agents already know to look here for canonical templates; `shared-conventions.md` already covers cross-cutting conventions.
- Cons: KB-documentation-criteria's stated scope is "documents the feature-pipeline produces" — execution-phase artifacts may or may not fit this framing depending on how "documents the feature-pipeline produces" is interpreted.
- KB-documentation-criteria's SKILL.md says: *"Houses the 5 canonical templates"* — that count is already stale (6 exist; research-plan-template was added). Adding execution-phase templates makes the count grow but doesn't require a new home.

**Option B** — Subdirectory: `KB-documentation-criteria/references/templates/execution-phase/`:
- Pros: Clusters the new templates without polluting the top-level templates directory; signals the execution-phase domain explicitly.
- Cons: Creates a 2-level nesting that no other reference subdirectory uses. Templates are currently flat.

**Option C** — New top-level KB: `KB-execution-pipeline/` (or `KB-execution-criteria/`):
- Pros: Separates execution-domain from documentation-domain cleanly; symmetric with `KB-review-disciplines` (which is a domain KB on the review side, sibling to `KB-documentation-criteria`).
- Cons: Heaviest structural change; creates a new entry point for agents to load; requires updating cross-references.

**Recommendation** (surfacing for Blueprint decision):

**Option A** is the lowest-friction path AND aligns with current scope framing if we interpret "documents the feature-pipeline produces" broadly. The pipeline does produce execution-phase documents — they're documents, the pipeline runs them, they have frontmatter and templated structure. The fact that KB-documentation-criteria currently only houses planning-side templates is **historical**, not architectural.

**However, there's a counterargument from IN-005's finding**: the document-side and execution-side reviewers will be different agents. If the execution-side reviewer loads a different set of canonical references, that's an argument for option C (parallel KB structure).

**This is Blueprint decision (11th of the discovery)**: Option A, B, or C for execution-phase template location?

**Subordinate Blueprint decision (11.5)**: Either way, do execution-phase templates follow the same internal structure (frontmatter + `## Contents` checklist + section-by-section guide)? **Strong recommendation: yes.** The pattern is uniform across all 6 existing templates and the Gate 0 procedure depends on the `## Contents` checklist as the structural-presence anchor. Diverging would break the reviewer's Gate 0 reuse.

---

## Batch F checkpoint summary

- **IN-015 produced a clear inventory**: 6 existing templates, all at `KB-documentation-criteria/references/templates/`, all using the same internal structure (frontmatter + Contents checklist + section guide).
- **One new Blueprint decision** (11th, plus 11.5 subordinate): where do execution-phase templates live (Options A/B/C), and do they follow the same internal structure?
- **Strong recommendation for 11.5**: yes, same internal structure — preserves Gate 0 reusability.
- **No further surprises**. Discovery research is structurally complete.

---

## Discovery research final checkpoint — all 17 INs covered

**Coverage**: 17/17 INs covered. 0/6 external research topics consumed (within budget; ADR-0021's "external research is conditional" applied correctly).

**Accumulated Blueprint-time decisions** (11 primary + subordinate):

> **[SUPERSEDED-IN-PLACE 2026-05-22T03:48:00Z — see "Revised decision list" section appended below.]** The 11-decision distillation in the table immediately below was the working synthesis at end-of-discovery. A post-checkpoint review surfaced framing problems: lumped decisions hiding substructure (#2), false-binary framings (#1, #7), decisions mis-attributed to the wrong stage (#3 is Plan-time; #5 is spec-authority not validator), foregone conclusions presented as deliberations (#10, #11), and six material gaps the table didn't capture (execution-side reviewer architecture, agent inventory, "code-producing" definition, reconciliation budget value, phase-quality scoring dimensions, FR-4 dispatch taxonomy). The substantive IN findings above and below this table stand unchanged; only this Blueprint-decision distillation is re-framed in the appended section. Per ADR-0005 append-only: the original table is preserved here; the corrected list is appended below rather than overwriting.

| # | Decision | Surfaced in |
|---|---|---|
| 1 | Does FR-3's phase-quality structure decompose into the 4-phase pattern (Static → Build → Test → Final Gate) from `ai-development-guide`, or collapse into one sweep? | Batch A (IN-016) |
| 2 | Which `task-executor`/`quality-fixer` structural patterns (BLOCKING gates, escalation types, JSON returns, stub detection) to adopt verbatim vs adapt vs omit? | Batch A (IN-017) |
| 3 | The uploaded `ai-development-guide` reference's frontmatter is sparse (`name:`, `description:` only); the Plan's install task should add project-conventional fields — which fields, per `shared-conventions.md`? | Batch A (IN-016) + Batch C (IN-004) |
| 4 | Does FR-3's GHA + Codespaces audit invocation extend `auditing-cc-configs` dispatch table (unified entry), or stay as 3 parallel audit invocations? | Batch B (IN-014) |
| 5 | Convention-drift handling: canonicalize the 4 extension fields (`intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at`) in `shared-conventions.md` via spec update + ADR, OR accept as extension fields in FR-6 validator? | Batch C (IN-004) |
| 6 | FR-7 artifact format: follow existing "X.json + X.md" pair pattern, or unified format? | Batch C (IN-011) + Batch D (IN-010 reinforces) |
| 7 | Execution-side pipeline orchestration: introduce a single orchestrator agent, OR follow planning-side precedent (orchestration distributed across agent prompts)? | Batch D (IN-007) |
| 8 | Extend ADR-0029 with explicit execution-phase surfacing locations (per-task, phase-quality, quality-reconciliation), OR argue the existing 14 locations cover execution implicitly via Reconciliation? | Batch D (IN-012) + Batch E (IN-009 reinforces) |
| 9 | Does FR-2's per-task execution loop run tasks serially or fan out per-task-DAG-level (per `tasks.json`)? | Batch E (IN-009) |
| 10 | Where does FR-6's frontmatter validator live: `auditing-shared/scripts/validate_pipeline_frontmatter.py` (new, distinct from existing `auditing-skills/scripts/validate_frontmatter.py`)? | Batch E (IN-009) |
| 11 | Where do execution-phase templates live: Option A (add to existing `templates/`), B (subdirectory), or C (new KB `KB-execution-pipeline`)? | Batch F (IN-015) |
| 11.5 | Do execution-phase templates follow same internal structure (frontmatter + Contents checklist + section guide)? **Recommend: yes.** | Batch F (IN-015) |

**One PRD-cascade-worthy observation deferred to Blueprint** (per user direction, option 1):
- ADR-0017 vs ADR-0021 4-cycle-cap mis-credit in PRD v1.1.0. Resolution path: Blueprint cites ADR-0017 correctly; PRD's informal mention isn't normative. Audit trail satisfied by surfacing here. (Batch E IN-009)

**One editorial expansion candidate for FR-7-c floor** (deferred to Blueprint per AC-FR-7-d):
- The 4 Q-004 candidate artifacts (`implementation-notes.md`, `observations.md`, `acceptance-matrix.md`, `cross-artifact-audit-final.md`) are all present with substantive content in the prior `audit-findings-remediation-r1` archive. Plus 2 additional artifacts the archive surfaced: `final-audit-report.md` + `final-audit.json` pair, and `x9-verification/` subdirectory. Blueprint expands FR-7-c floor from 5 to ~9-11 artifacts. (Batch D IN-010)

**Three meta-discipline patterns confirmed**:
1. **"No silent failures"** applies at marker (ADR-0030), stage (ADR-0029), and now execution (this feature) levels.
2. **"Consult what's already known"** (ADR-0021's KB+ADR-consultation principle) applies to execution-phase reviewers: read Blueprint + Plan + per-task context before executing.
3. **"Canonical helper discipline"** (ADR-0031) constrains where new audit utilities land: `auditing-shared/scripts/`, single source of truth.

**Audit-trail note**: All 17 INs answered. Discovery costs: ~30 file reads + 4 directory traversals + 6 grep queries + 0 external tool calls. Medium-effort estimate from research-plan honored.

Final status: **codebase-analysis.md is COMPLETE.** Status field bumped to `complete` in the next step.

---

## Revised Blueprint-decision distillation (v1.1.0)

**Why this revision**: The end-of-discovery decision list in the prior section presented 11 Blueprint decisions. A post-checkpoint review (user-prompted, 2026-05-22T03:46:00Z) surfaced four classes of framing problems and six material gaps. Per the project's "no silent failures" meta-discipline (ADR-0029 + ADR-0030, applied here at the working-synthesis level), the framing errors are surfaced explicitly rather than silently corrected.

### Framing problems identified in the prior table

**Class 1 — Lumped decisions hiding substructure.** Prior #2 ("Which task-executor/quality-fixer patterns to adopt verbatim/adapt/omit?") bundled four independent choices at different architectural layers: BLOCKING gates (state-machine pattern), escalation-type taxonomy (finding taxonomy), structured-JSON returns (serialization contract), stub detection (workflow gate). Bundling obscures that the Blueprint will address each separately.

**Class 2 — Mis-framed dichotomies.** Prior #1 ("4-phase decomposition vs single sweep") is a false binary. The actual question is what *organizing dimension* the phase-quality stage uses: by `ai-development-guide`'s generic 4-phase pattern (Static→Build→Test→Final Gate), by audit-family domain, by layer (frontend tests separately from backend), or by hybrid. The 2-option framing loses three alternatives. Prior #7 ("orchestrator agent vs distributed across agent prompts") similarly omits a third option (DAG-walker walking `tasks.json` forward without a dedicated orchestrator agent).

**Class 3 — Mis-attributed and over-promoted decisions.** Prior #5 (convention drift) is framed as an FR-6 implementation choice; it is actually an upstream spec-authority decision (what `shared-conventions.md` declares) likely warranting a new ADR, independent of FR-6's implementation. Prior #3 (which frontmatter fields the install task adds) is too low-level for Blueprint — it's a Plan-task specification detail. Prior #10 (FR-6 validator file location) is functionally a foregone conclusion under ADR-0031. Prior #11 (template location A/B/C) inflates apparent uncertainty: Option A is default-by-precedent given KB-documentation-criteria's stated scope; B and C exist only as deviations requiring justification.

**Class 4 — Missing decisions.** Six material design surfaces the prior table omitted, surfaced in the discovery findings but not promoted to decision status:
- Execution-side reviewer architecture (no analog of `shared-document-reviewer` exists for execution-side)
- Execution-side agent inventory (the planning side has 31; the execution-side count and responsibilities are undefined)
- "Code-producing" definition for FR-9-b (boundary undefined; reconciler / frontmatter-validator inclusion unclear)
- Execution reconciliation budget value (FR-10 names a cap; the actual number is unset)
- Phase-quality scoring dimensions (planning-side uses Consistency/Completeness/Rule-compliance/Clarity; execution-side analog undefined)
- FR-4 dispatch-matrix taxonomy (`finalize-reconciler` has 6+ planning-side categories; execution-side taxonomy unenumerated)

### Revised decision list

14 substantive Blueprint decisions (with two having sub-decisions), plus 3 items that drop out as mechanical applications.

| # | Decision | Source |
|---|---|---|
| 1 | **Phase-quality organizing dimension** — ai-development-guide 4-phase / audit-family / layer / hybrid? | IN-016 (re-framed from prior #1 binary to 4-way) |
| 2a | BLOCKING-gates pattern (task-executor) — adopt for execution-phase agents? | IN-017 (un-lumped from prior #2) |
| 2b | Escalation-type taxonomy (task-executor's 6 categories) — verbatim / subset / project-specific new set? | IN-017 (un-lumped from prior #2) |
| 2c | Structured-JSON return schema — task-executor's / simplified / new? | IN-017 (un-lumped from prior #2) |
| 2d | Stub detection (quality-fixer Step 1 BLOCKING) — incorporate into FR-2? | IN-017 (un-lumped from prior #2) |
| 3 | **FR-3 invocation model** — extend `auditing-cc-configs` dispatch table (unified entry) or 3 parallel audit invocations (current de-facto)? | IN-014 (renumbered from prior #4) |
| 4 | **Convention drift — spec authority** — canonicalize 4 extension fields (`intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at`) in `shared-conventions.md` via spec update + ADR, OR leave archive-practice extension fields off-spec? | IN-004 (re-attributed from prior #5 validator framing to upstream spec-authority decision) |
| 5 | **FR-7 artifact format** — pair pattern (`X.json` + `X.md`) or unified single-format? | IN-011 + IN-010 (renumbered from prior #6) |
| 6 | **Execution-side orchestration shape** — explicit orchestrator agent / user-driven (planning-side precedent) / DAG-walker (per-task agent walks `tasks.json` forward without a dispatcher)? | IN-007 (re-framed from prior #7 binary to 3-way) |
| 7 | **ADR-0029 extension** — author explicit execution-phase surfacing locations as a new ADR (or amendment), OR argue existing 14 locations cover execution implicitly via Reconciliation? | IN-012 + IN-009 (renumbered from prior #8) |
| 8 | **FR-2 per-task loop topology** — serial / DAG-parallel (per `tasks.json`) / batched? | IN-009 (renumbered from prior #9) |
| 9 | **Execution-side reviewer architecture** — single `execute-phase-quality-reviewer` agent / extend `shared-document-reviewer` with execution-phase modes / multiple specialized reviewers (per audit-family domain)? | IN-005 (NEW — was buried in IN-005 commentary; promoted to first-class Blueprint decision because this shape is FR-3's architectural skeleton) |
| 10 | **Execution-side agent inventory** — minimum set of named agents + their responsibilities + frontmatter shape? Implied minimum: per-task runner, quality reviewer, reconciler analog, frontmatter-validator agent. Actual list determines FR-9 binding scope + FR-7 artifact ownership. | IN-007 (NEW) |
| 11 | **"Code-producing" definition for FR-9-b** — does the reconciler (writes log files) qualify? Does the frontmatter-validator (its outputs are reports; itself is code) qualify? Boundary needs definition before AC-FR-9-c can fire as a hard validator check. | FR-9-b + IN-007 (NEW) |
| 12 | **Execution reconciliation budget value (FR-10)** — mirror planning-side at 4 (per ADR-0017 / blueprint v3 §3.7), smaller (execution loops may be more expensive per cycle), or larger? | FR-10 (NEW) |
| 13 | **Phase-quality scoring dimensions** — execution-side rubric replacing planning-side Consistency/Completeness/Rule-compliance/Clarity. Candidates: test pass rate, audit finding count, build correctness, validator-pass count. Actual rubric undefined. | IN-005 (NEW — analog of planning-side `severity-taxonomy.md` for execution) |
| 14 | **FR-4 dispatch-matrix taxonomy** — finding categories that drive re-author dispatch. Planning-side has 6+ (PRD revision, Blueprint cross-cutting, per-layer Design, Plan, Acceptance Tests, Phase Validators). Execution side undefined. Without it, FR-4 has nothing to dispatch *to*. | IN-008 (NEW) |

### Items dropped to mechanical-application status

Three prior-table items are not Blueprint decisions; they are mechanical applications of established conventions or foregone conclusions. The Blueprint applies them; it doesn't deliberate them:

| Prior # | Item | Mechanical resolution |
|---|---|---|
| 3 | Frontmatter fields the install task adds for `ai-development-guide` | **Plan-task specification detail** per `shared-conventions.md`. The Blueprint authorizes "install ai-development-guide as a project skill"; the Plan task spec'd by `plan-author` enumerates the fields. |
| 10 | Where does FR-6's frontmatter validator file live | **Foregone under ADR-0031**: any new audit utility goes to `auditing-shared/scripts/`. Filename: `validate_pipeline_frontmatter.py` (distinguishes from existing `auditing-skills/scripts/validate_frontmatter.py` which validates SKILL.md frontmatter). |
| 11 | Where execution-phase templates live (Options A/B/C) | **Default-by-precedent**: Option A (add to `KB-documentation-criteria/references/templates/`). KB-documentation-criteria's stated scope already covers "every document the feature-pipeline produces." Options B and C would require justification *against* the default; no such justification surfaced. |
| 11.5 | Do execution-phase templates follow same internal structure | **Yes — strong precedent**. Frontmatter + `## Contents` checklist + section-by-section guide. Diverging would break Gate 0 reviewer's structural-presence anchor. |

### Why this re-framing matters for downstream stages

- **Synthesis** consumes a substrate of design surfaces. A list of 14 substantive decisions + 3 mechanical applications is a different substrate than a list of 11 mixed-grade items; the synthesis-of-the-discovery work is different.
- **Per-layer Design (Claude Code)** has clearer targets when each decision is well-framed. Decision #9 (execution-side reviewer architecture) is, in scale, the single largest under-determined design surface — comparable to how `shared-document-reviewer` is to the planning side. Burying it in IN-005 commentary risked Blueprint-time under-specification.
- **Blueprint Composition** can deliberate 14 substantive choices in proportion to their weight, rather than treating Option-A-vs-B-vs-C deliberations (mechanical applications) and execution-side-reviewer-architecture (foundational) as equal-weight decisions.

### Trail of corrections

Per ADR-0029 audit-trail discipline, the corrections themselves are documented:

| Correction class | Items corrected |
|---|---|
| Un-lumped | Prior #2 → 2a/2b/2c/2d (4 sub-decisions) |
| Re-framed (binary → multi-option) | Prior #1 (2 → 4 options); Prior #7 (2 → 3 options) |
| Re-attributed | Prior #5 (FR-6 implementation → spec authority) |
| Demoted to mechanical | Prior #3 (Plan-time), #10 (foregone), #11 (default-by-precedent) |
| Newly promoted to Blueprint decision | Execution-side reviewer architecture, agent inventory, "code-producing" definition, reconciliation budget value, phase-quality scoring, FR-4 dispatch taxonomy |

Net change: 11 mixed-grade items → 14 substantive + 3 mechanical. Substantive design surface increased (more decisions correctly identified); deliberation friction decreased (mechanical items don't consume Blueprint cycles).

