---
id: ResearchPlan-execution-pipeline-design-r1
version: 1.1.0
status: accepted
feature_slug: execution-pipeline-design-r1
derived_from: working/feature/execution-pipeline-design-r1/prd-v1.1.0.md
prd_user_token: PRD-REVISE-execution-pipeline-design-r1-20260522T030800Z
user_token: RP-CONFIRM-execution-pipeline-design-r1-20260522T031500Z
supersedes: <no prior research-plan-vN.md ratified — this is the initial Research Plan; the v1.0.0 → v1.1.0 bump reflects PRD revision from prd-v1.md to prd-v1.1.0.md, which cascaded edits into Open Questions and dispositions per ADR-0005 append-only at field granularity for in-progress drafts>
generated: 2026-05-22T03:00:00Z
revised: 2026-05-22T03:08:00Z
approved_at: 2026-05-22T03:15:00Z
gate_passed: 3
reviewer_verdict: approved (Gate 0 pass, Gate 1 pass — Consistency 94, Completeness 88, Rule compliance 95, Clarity 91)
generated_by: claude (acting as discovery-plan-author, continuation session)
revision_reason: PRD revision from v1.0.0 to v1.1.0 resolved Q-001, Q-002, Q-003. Open questions section updated to reflect resolutions; Q-004 retained.
external_research_topic_count: 0
external_research_budget: 6
---

# Research Plan: Execution Pipeline Design (r1)

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug**: `execution-pipeline-design-r1`
- **PRD path**: `working/feature/execution-pipeline-design-r1/prd-v1.md`
- **PRD version**: 1.0.0
- **PRD gate state**: approved at 2026-05-22T02:58:00Z (Gate 2 — user PRD Confirmation Gate)
- **Inherited ADRs in scope**:
  - ADR-0021 (Discovery-phase architecture) — defines planning-side reconciliation budget; informs FR-10's parallel execution-side budget
  - ADR-0029 (No-silent-scope-changes principle) — applies to execution-side deviations per PRD's Product Policy Decisions
  - ADR-0030 (Mechanism α — pedagogical-marker justification) — named-exempt mechanism applies to execution-side findings per Product Policy Decisions
  - ADR-0031 (auditing-shared canonical home) — pattern this feature extends to GHA and Codespaces per FR-8
- **Applicable KBs**:
  - `KB-documentation-criteria` — templates, shared-conventions, deliverable-archive-spec (extended by FR-7, FR-11)
  - `KB-review-disciplines` — Gate 0/1 procedure, severity taxonomy, prior-context-check (informs frontmatter validator's relationship to existing reviewer)
  - `auditing-shared` — canonical helpers pattern (FR-8-c sources from here)
  - `auditing-cc-configs`, `auditing-skills`, `auditing-subagents`, `auditing-context-files`, `auditing-hooks`, `auditing-mcp`, `auditing-settings` — existing auditing-X siblings (FR-8 extends the pattern)

## Information needs inventory

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-001 | Does the `ai-development-guide` skill exist in `.claude/skills/`? If yes, what is its file structure, frontmatter, and high-level content shape? | design-cc (FR-9 design); design-composer (Blueprint binding) | `codebase-topic` — `.claude/skills/ai-development-guide/` directory inspection |
| IN-002 | What audit scripts currently live in `.claude/skills/KB-github-actions-platform/scripts/`? What is each script's purpose, callable interface, and dependency footprint? | design-cc (FR-8-a extraction); design-cicd (per-layer reference); design-composer | `codebase-topic` — `.claude/skills/KB-github-actions-platform/scripts/` listing + script reads |
| IN-003 | What audit scripts (if any) currently live in `.claude/skills/KB-codespaces-platform/scripts/`? | design-cc (FR-8-b extraction); design-codespaces (per-layer reference); design-composer | `codebase-topic` — `.claude/skills/KB-codespaces-platform/scripts/` listing |
| IN-004 | What is the current structure of `shared-conventions.md`? Where would an "Execution-phase artifact frontmatter" section land per FR-7-b without restructuring existing planning-side content? | design-cc (template / convention extension) | `codebase-topic` — `.claude/skills/KB-documentation-criteria/references/shared-conventions.md` |
| IN-005 | What is the structure and extension surface of `shared-document-reviewer`? Can the new frontmatter validator (FR-6) be a sibling sub-agent invoked alongside it, a callable script the reviewer (and other agents) call, or an extension of the reviewer itself? | design-cc (frontmatter validator design) | `codebase-topic` — `.claude/agents/shared-document-reviewer.md` + `KB-review-disciplines/SKILL.md` + `KB-review-disciplines/references/gate-0-1-procedure.md` |
| IN-006 | What is the structural pattern of the existing `auditing-*` skill family (skills, shims, canonical helpers in auditing-shared)? What conventions does FR-8 need to mirror? | design-cc (FR-8 extraction); design-cicd; design-codespaces | `codebase-topic` — `.claude/skills/auditing-{cc-configs,skills,subagents,context-files,hooks,mcp,settings,shared}/` |
| IN-007 | What are the full agent definitions for the planning-side sub-agents that the execution-side reconciliation matrix (FR-4) dispatches to: intake-intent-clarifier, intake-prd-author, design-composer, plan-author, finalize-task-decomposer, finalize-reconciler? | design-cc (FR-4 dispatch matrix); design-composer | `codebase-topic` — `.claude/agents/{intake-*,design-composer,plan-author,finalize-*}.md` |
| IN-008 | What is the existing planning-side gate structure — Gates 0 through 6, their owning sub-agents, their gate-pass criteria, and the artifacts each gate ratifies? | design-cc (continuation of pattern for execution-side gates); design-composer | `codebase-topic` — `.claude/agents/*` frontmatter `gate:` references + KB-review-disciplines |
| IN-009 | What is the full content of ADR-0021, ADR-0029, ADR-0030, ADR-0031? The PRD references each extensively but a research-grounded design needs the source text. | design-cc; design-composer (Blueprint authoring) | `covered-by-ADR:ADR-0021,ADR-0029,ADR-0030,ADR-0031` — read directly during Discovery |
| IN-010 | What is the schema of `tasks.json` produced by `finalize-task-decomposer`? FR-2's per-task loop depends on tasks.json structure (Target Files, Investigation Targets, Dependencies, Operation Verification Methods). | design-cc (per-task loop interface); design-composer | `codebase-topic` — `.claude/agents/finalize-task-decomposer.md` + any existing tasks.json sample (e.g., audit-findings-remediation-r1's) |
| IN-011 | What is the structure of `deliverable-archive-spec.md`? How does the per-scope-class artifact expectation extend for execution-phase artifacts (FR-7)? | design-cc (deliverable spec extension); design-composer | `codebase-topic` — `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` |
| IN-012 | What are the full agent definitions of the per-layer designers (design-frontend, design-backend, design-api, design-query, design-database, design-cicd, design-codespaces, design-iac, design-claude-code)? Specifically: their `skills:` frontmatter (FR-9 will add `ai-development-guide` to whichever are code-producing in the execution context). | design-cc (FR-9 scope); design-composer | `codebase-topic` — `.claude/agents/design-*.md` frontmatter inspection |
| IN-013 | What testing-framework invocation patterns are well-established across layers (frontend, backend, API, query, database, CI/CD)? FR-3 calls "all layer tests" but the orchestrator needs to know how to invoke each. | design-cc (FR-3 invocation contract); design-composer | `designer-general-knowledge` — `npm test`, `pytest`, `go test`, etc. are universally-known runners; the orchestrator's invocation contract specifies "run the project's declared test command for each layer" without enumerating commands |
| IN-014 | What invocation patterns do the existing audit scripts use (cc-audit and the existing auditing-* family)? | design-cc (FR-3 audit-invocation contract); design-cicd; design-codespaces | `codebase-topic` — `auditing-cc-configs/scripts/` + `auditing-shared/scripts/` + any other auditing-* scripts |
| IN-015 | How are new templates added to `KB-documentation-criteria/references/templates/`? Are there conventions beyond "drop a `.md` file in the templates dir with `-template.md` suffix"? | design-cc (FR-7-a) | `codebase-topic` — `.claude/skills/KB-documentation-criteria/references/templates/` directory + SKILL.md Contents |
| IN-016 | What is the content shape of the user-uploaded `ai-development-guide` reference SKILL.md? (Used as Blueprint inspiration for FR-9 binding rationale.) | design-cc (FR-9 binding rationale); design-composer (Blueprint citation) | `codebase-topic` — `/mnt/user-data/uploads/SKILL__2_.md` (user-uploaded reference, not in project) |
| IN-017 | What is the content shape of the user-uploaded `task-executor` and `quality-fixer` reference templates? (Used as Blueprint inspiration for per-task loop sub-agents, not adopted verbatim per PRD.) | design-cc (per-task loop Blueprint design); design-composer | `codebase-topic` — `/mnt/user-data/uploads/task-executor__1_.md` + `/mnt/user-data/uploads/quality-fixer.md` (user-uploaded references) |

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`.

### Touch points

- `.claude/skills/KB-documentation-criteria/` — templates, shared-conventions, deliverable-archive-spec. Extension surface for FR-7 (new templates) and FR-11 (state vocabulary).
- `.claude/skills/KB-review-disciplines/` — Gate 0/1 procedure; pattern for the new frontmatter validator (FR-6).
- `.claude/skills/auditing-shared/` — canonical helpers pattern (FR-8-c destination).
- `.claude/skills/auditing-cc-configs/` + `.claude/skills/auditing-skills/` + `.claude/skills/auditing-subagents/` — three siblings already implementing the 3-way split; pattern source for FR-8.
- `.claude/skills/auditing-context-files/`, `.claude/skills/auditing-hooks/`, `.claude/skills/auditing-mcp/`, `.claude/skills/auditing-settings/` — other auditing-X siblings; informs the FR-8 pattern.
- `.claude/skills/KB-github-actions-platform/` — extraction source for `auditing-github-actions` (FR-8-a).
- `.claude/skills/KB-codespaces-platform/` — extraction source (or new-author source) for `auditing-codespaces` (FR-8-b).
- `.claude/skills/ai-development-guide/` — FR-9 binding target (presence to be verified per IN-001).
- `.claude/agents/intake-intent-clarifier.md`, `intake-prd-author.md`, `design-composer.md`, `plan-author.md`, `finalize-task-decomposer.md`, `finalize-reconciler.md` — re-entry dispatch targets for FR-4 quality-reconciliation loop.
- `.claude/agents/design-*.md` — per-layer designers; FR-9 candidate-set for `ai-development-guide` binding (PRD says "code-producing execution-phase sub-agents"; some of these may also qualify in the execution context).
- `.claude/agents/shared-document-reviewer.md` — sibling to the new frontmatter validator (FR-6).
- `.claude/agents/finalize-deliverable-packager.md` — terminal stage that consumes the execution pipeline's output.
- `adrs/ADR-0021-discovery-phase-architecture.md`, `ADR-0029-no-silent-scope-changes-principle.md`, `ADR-0030-mechanism-alpha-pedagogical-marker-justification.md`, `ADR-0031-auditing-shared-skill-module.md` — referenced extensively in the PRD; full text needed for Blueprint authoring.
- `working/feature/audit-findings-remediation-r1/` — prior feature whose execution surfaced the manual-cleanup pain that motivates FR-5, FR-6, FR-11. Read `tasks.json` for FR-2 / FR-10 schema inputs; read `implementation-notes.md` and `observations.md` for empirical patterns the design should accommodate.
- `/mnt/user-data/uploads/task-executor__1_.md` + `/mnt/user-data/uploads/quality-fixer.md` + `/mnt/user-data/uploads/SKILL__2_.md` (ai-development-guide) — user-uploaded references; design inspiration for FR-2 per-task loop and FR-9 binding rationale.

### Blast-radius questions

- Which sub-agents currently reference `KB-github-actions-platform` or `KB-codespaces-platform`? After FR-8 extraction, these may need their `skills:` frontmatter updated to additionally (or instead) reference the new `auditing-X` skill. Identify the dependency graph before extraction.
- Which sub-agents currently reference `shared-document-reviewer`? After FR-6 introduces the frontmatter validator, consider whether any of those callers should additionally invoke the new validator.
- Which sub-agents reference `shared-conventions.md`? After FR-7-b adds the execution-phase artifact frontmatter section, those readers transitively gain new vocabulary.
- For each planning-side sub-agent in IN-007: which artifacts does it produce, and what is the maximum cascade depth when an execution-side finding routes back to it (per FR-4-d)?

### Convention discovery

- Sub-agent file naming: `<role>-<purpose>.md` (e.g., `design-cc.md`, `intake-prd-author.md`). FR-1's new sub-agents must follow this.
- Sub-agent frontmatter shape: `name`, `description`, `model`, `effort`, `tools`, `skills`, `memory`. FR-9 modifies the `skills:` field on existing agents (selectively) and on the new execution-phase agents (uniformly for code-producers).
- Skill file naming: `KB-<area>` for knowledge, `auditing-<area>` for audit, `<role>` for roles (e.g., `synthesize`). FR-8 introduces `auditing-github-actions` and `auditing-codespaces` per this convention.
- ADR numbering: monotonic, project-wide, zero-padded 4-digit. FR-4-f, FR-10-a, and FR-11-e will produce new ADRs at the next available numbers.
- Template naming: `<doc-type>-template.md` in `KB-documentation-criteria/references/templates/`. FR-7-a adds execution-phase templates per this convention.
- ADR frontmatter shape: per project lean-style introduced at ADR-0023 (id, title, status, date, deciders, supersedes, superseded_by, related). New ADRs follow this.

### Specific queries or grep targets

- `grep -r "ai-development-guide" .claude/agents/ .claude/skills/` — to discover any existing references to the (uploaded-but-perhaps-not-installed) skill.
- `grep -rE "skills:\s*\[.*KB-github-actions-platform.*\]" .claude/agents/` — to find sub-agents that load the GHA platform KB (FR-8-f update candidates).
- `grep -rE "skills:\s*\[.*KB-codespaces-platform.*\]" .claude/agents/` — same for Codespaces.
- `grep -rln "shared-conventions" .claude/` — to scope the FR-7-b extension blast-radius.
- `find .claude/skills/auditing-* -name "*.py" -o -name "SKILL.md"` — full audit-skill inventory for FR-8 pattern matching.

## External research topics

**No external research authorized; all information needs covered by KBs, ADRs, or codebase reads.** This is a positive design state: the feature is entirely about extending the project's existing pipeline discipline and skill structure. Every information need is either:

- An existing project artifact whose content the design depends on (codebase-topic).
- An inherited ADR whose decision the design respects (covered-by-ADR).
- Well-known industry conventions a competent designer applies with documented rationale (designer-general-knowledge — IN-013 only).
- A user-uploaded reference document (codebase-topic on the uploads dir).

Per ADR-0021 §3, zero external topics is a design-state declaration that downstream stages (Synthesis, per-layer Design) can rely on: no external sources need to be cited, no novel external patterns are imported.

## Topics explicitly NOT researched

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-009 | ADR-0021, ADR-0029, ADR-0030, ADR-0031 | The four ADRs the PRD inherits; their decisions are authoritative and the design adopts them. No re-derivation. |
| IN-013 | designer-general-knowledge | Test invocation across layers (npm test / pytest / go test / etc.) is universally-known. The execution-pipeline design's contract is "the orchestrator invokes the project's declared test command for each layer," not "the orchestrator knows every test framework." |
| (broader) Generic CI-pipeline patterns | Industry common knowledge; the project's pipeline is bespoke | The execution pipeline this feature designs is the project's bespoke pipeline, not a general CI/CD pipeline. Patterns from generic CI tooling (Jenkins, CircleCI templates) are not applicable. |
| (broader) State-machine literature for document lifecycle | The 5-state vocabulary in `shared-conventions.md` is already pinned | FR-11 resolves drift between spec and practice; it doesn't invent new states. No literature search. |
| (broader) Generic "developer hooks" patterns (pre-commit, husky, etc.) | The state-transition hooks are orchestrator-internal | FR-5's hooks are not git hooks or shell hooks; they're orchestrator steps that update YAML frontmatter at gate boundaries. Generic hook literature is not directly applicable. |

## Estimated effort

- **Codebase research effort**: Medium. ~30 file reads + 4 directory traversals + 5 grep queries; bounded by IN-001 through IN-017 plus blast-radius queries.
- **External research topic count**: 0 of 6 budget.
- **Estimated wall-clock**: One pass of `discovery-codebase-researcher` over the touch-point set; expect single-instance time, no external-research-parallelism needed.

## Open questions for human resolution

These surface at the Research Plan Approval Gate. User answers update this Plan (and may cascade to PRD revision) before Discovery Research begins.

### Resolved (PRD cascade applied — see prd-v1.1.0.md amendment_log)

- **~~Q-001~~ [RESOLVED — prd-v1.1.0.md]**: The `ai-development-guide` skill is not installed in `.claude/skills/`. **Resolution**: Plan includes a task installing the skill from `/mnt/user-data/uploads/SKILL__2_.md` per new AC-FR-9-e; task executes before any execution-phase sub-agent definitions that bind to the skill, so FR-9's binding has a real target. Assumption A-1 corrected.

- **~~Q-002~~ [RESOLVED — prd-v1.1.0.md]**: `KB-codespaces-platform/scripts/` does not exist; FR-8-b's "or newly authored" path conflicted with Won't-Have. **Resolution**: FR-8-b clarified — `auditing-codespaces` ships as a **stub skill** (SKILL.md only, no audit scripts) preserving the 3-way-split structural pattern. Won't-Have carved out for the stub exception specifically; actual audit script authoring remains out of scope.

- **~~Q-003~~ [RESOLVED — prd-v1.1.0.md]**: What "GitHub Codespaces audit" means given Q-002. **Resolution**: AC-FR-3-b clarified — Codespaces audit is feature-scoped (audits whatever codespaces configuration the feature touches); a feature that touches no codespaces configuration produces a no-op pass; at this feature's ship time, `auditing-codespaces` is a stub so the audit is a no-op pass placeholder.

### Open (Blueprint-time decisions)

- **Q-004**: The PRD's FR-7-c names a five-artifact floor for execution-phase artifact templates: per-task execution log; phase-quality report; quality-reconciliation log; frontmatter-validation report; execution-reconciliation log. Reviewing the prior `audit-findings-remediation-r1` archive's ad-hoc artifacts, four additional candidate artifacts surfaced: `implementation-notes.md`, `observations.md`, `acceptance-matrix.md`, `cross-artifact-audit-final.md`. Should these be added to the FR-7-c floor at Blueprint time?
  
  Resolution path: deferred to Blueprint per AC-FR-7-d. No PRD change needed; Blueprint enumerates the full set when authoring the per-layer Claude Code Design.

---

## Related artifacts

- **PRD** (upstream input): `working/feature/execution-pipeline-design-r1/prd-v1.md`
- **Intent Clarification** (further upstream): `working/feature/execution-pipeline-design-r1/intent-clarification.md`
- **Discovery Planning discipline**: `.claude/skills/KB-documentation-criteria/references/disciplines/discovery-planning.md`
- **Codebase analysis schema** (downstream consumer of Codebase research scope): per ADR-0018 in KB-codebase-research / `.claude/agents/discovery-codebase-researcher.md`
- **Prior feature archive** (empirical reference): `working/feature/audit-findings-remediation-r1/`
- **User-uploaded references** (Blueprint inspiration, not adopted verbatim):
  - `/mnt/user-data/uploads/task-executor__1_.md`
  - `/mnt/user-data/uploads/quality-fixer.md`
  - `/mnt/user-data/uploads/SKILL__2_.md` (ai-development-guide)
