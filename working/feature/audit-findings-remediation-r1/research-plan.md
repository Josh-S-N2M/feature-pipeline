---
feature_slug: audit-findings-remediation-r1
version: 1.1.0
status: approved
derived_from: working/feature/audit-findings-remediation-r1/prd-v1.md
prd_version_referenced: 1.1.0
generated: 2026-05-21T17:20:00Z
generated_by: claude (acting as discovery-plan-author)
approved_at: 2026-05-21T17:40:00Z
amended_at: 2026-05-21T17:55:00Z
amendment_reason: PRD v1.1.0 added FR-12 (deduplication). Research plan extends with IN-013 to characterize the deduplication scope; existing IN-002 amended to note the 3-copy reality discovered during execution.
gate_passed: 3
---

# Research Plan — audit-findings-remediation-r1

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug**: `audit-findings-remediation-r1`
- **PRD path**: `working/feature/audit-findings-remediation-r1/prd-v1.md`
- **PRD version**: 1
- **PRD gate state**: approved at 2026-05-21T17:15:00Z (PRD Approval Gate / Gate 2)
- **Inherited ADRs in scope**:
  - `ADR-0021` (Discovery Phase Architecture — KB-and-ADR-first discipline; external-research budget)
  - `ADR-0023` (Discipline refinements; PATCH-scope shortcut — informs Plan's scope-class decision but doesn't constrain discovery)
  - `ADR-0025` (Original pipeline-machinery defects; defect 1 = the pedagogical-marker-backfill scope this feature addresses)
  - `ADR-0026` (v4.4.1 audit-machinery fixes — context for how the auditor is currently structured)
  - `ADR-0028` (v4.5.0 skill-design fixes + parser-fix addendum — auditor parsing conventions that constrain mechanism-α implementation)
- **Applicable KBs**:
  - `KB-documentation-criteria` (template + discipline owner; new marker-justification spec lives here)
  - `KB-cc-design` (subagent description quality — informs SA-2 disposition for Category D)
  - `KB-cc-platform` (where most Category A/B markerable findings live)
  - `KB-codespaces-platform`, `KB-codespaces-design`, `KB-github-actions-platform`, `KB-github-actions-design` (other affected platform KBs)
  - `KB-review-disciplines` (Gate 0 / shared-document-reviewer checks may need adjustment if marker spec extends)
  - `auditing-cc-configs` (skill housing the marker spec + triage machinery — not a KB but a knowledge surface)
  - `auditing-skills` + `auditing-subagents` (auditor module families touched by FR-6 + FR-7)

## Information needs inventory

Every downstream stage will read the artifacts produced by this Discovery to make implementation decisions. Each information need below is tagged with a disposition per `disciplines/discovery-planning.md`.

### Marker-discipline information needs

- **IN-001** — What is the current syntactic form of pedagogical markers in this project (frontmatter `pedagogical_sections:` form AND `audit-example` fence form)?
  - Consumer: per-layer design (design-claude-code, for FR-7 spec authoring)
  - Disposition: `covered-by-KB: auditing-cc-configs:references/pedagogical-marker-spec.md` — the spec file already documents both forms with worked examples.

- **IN-002** — How does the auditor currently process pedagogical markers — at what stage in the audit pipeline is severity demoted, and what code path decides whether to trust a marker?
  - Consumer: per-layer design (for FR-7-b auditor extension); plan-author (for sequencing)
  - Disposition: `codebase-topic` — needs to be read out of THREE `pedagogical_marker_check.py` copies (`auditing-cc-configs/scripts/`, `auditing-skills/scripts/`, `auditing-subagents/scripts/`; PRD v1.0.0 originally said 2; the 3rd was surfaced during Stage 4 execution per ADR-0029 and triggered the PRD amendment to v1.1.0). Each copy is called by its respective audit dispatcher: `triage_with_judge.py`, `audit_skill.py`, `audit_subagent.py`. Routed to `discovery-codebase-researcher`.

- **IN-013** — (Added in research-plan v1.1.0) What is the precise divergence between the three `pedagogical_marker_check.py` copies, and what is the canonical shape FR-12's deduplication should produce?
  - Consumer: per-layer design (FR-12 spec); plan-author (sequencing — deduplication is a prerequisite for FR-7-b uniform enforcement)
  - Disposition: `codebase-topic` — preliminary scan during Stage 4 found 18-28 line diffs between pairs (mostly comment formatting; one defensive `location`/`where` field-name backward-compat in the `auditing-skills` copy). Full characterization: per-line diff between all three pairs; identification of which divergences are intentional (FR-12-d says the `location`/`where` compat MUST be preserved) vs accidental drift. Routed to `discovery-codebase-researcher`.

- **IN-003** — Are there existing pedagogical markers in the project beyond `KB-visual-design/references/anti-slop.md`? If so, how many and where?
  - Consumer: per-layer design (to size FR-8 retroactive-upgrade scope); plan-author (sequencing)
  - Disposition: `codebase-topic` — grep for `pedagogical_sections:` frontmatter AND `audit-example` fences across `.claude/`. Routed to `discovery-codebase-researcher`.

- **IN-004** — What anti-laundering rules does the existing marker spec already encode, and how do those constrain mechanism-α's design?
  - Consumer: per-layer design (FR-7 spec authoring); cross-artifact-auditor (to detect tension between α and existing anti-laundering)
  - Disposition: `covered-by-KB: auditing-cc-configs:references/pedagogical-marker-spec.md` — the "Anti-laundering rules" section directly addresses this; mechanism-α must not violate or duplicate those rules.

### Auditor structure information needs

- **IN-005** — Where exactly does the X9 finding originate in the auditor source, and what data does it have access to at that point?
  - Consumer: per-layer design (for FR-6 Stream 2 reformulation)
  - Disposition: `codebase-topic` — search `auditing-*/scripts/` for X9 emission. Routed to `discovery-codebase-researcher`.

- **IN-006** — Does the auditor have a mechanism to invoke `auditing-skills` recursively against preloaded skills, or would that need to be built?
  - Consumer: per-layer design (FR-6 Stream 2 — does Stream 2 reformulation reuse a recursive-audit capability that exists, or does it need to invent one?)
  - Disposition: `codebase-topic` — read `auditing-cc-configs/scripts/audit_project.py` to see how it dispatches to skill audits. Routed to `discovery-codebase-researcher`.

- **IN-007** — What is the SA-2 detection regex (`TRIGGER_PATTERNS`) and which of the 29 SA-2-flagged descriptions have descriptions a reasonable human would consider clearly-triggering despite the regex missing them?
  - Consumer: plan-author (for U-2 — option (i) [29 rewrites] vs option (ii) [tighten regex])
  - Disposition: `codebase-topic` — read `auditing-subagents/scripts/analyze_subagent.py` for the regex; sample 5-10 of the 29 flagged descriptions; produce a brief assessment. Routed to `discovery-codebase-researcher`.

### Genuine-defect information needs

- **IN-008** — For the 18 Category C "genuinely stale" broken links in `skills/synthesize/*` and `report-composition-knowledge/*`: are these skills being actively maintained, mid-migration, or deprecated?
  - Consumer: per-layer design (decides between repair / delete / reauthor per AC-FR-3-b)
  - Disposition: `codebase-topic` — read recent edits to those directories (file mtimes; any open-PR-equivalent indicators); read each skill's SKILL.md to assess status. Routed to `discovery-codebase-researcher`.

- **IN-009** — For each Category E genuine agent defect (3 wildcard-shell-tool MAJORs + 3 "bypass approval" BLOCKERs): what is the specific problematic line, what is the agent legitimately trying to do, and what is the minimal fix?
  - Consumer: per-layer design (specific fix per agent)
  - Disposition: `codebase-topic` — read the 6 agent files; for each, identify the offending line and propose the minimal disposition. Routed to `discovery-codebase-researcher`.

### Categorization-protocol information needs

- **IN-010** — Are there documented categorization protocols (in any community / similar project / academic source) for distinguishing pedagogical-content findings from real defects in security/lint scanners?
  - Consumer: per-layer design (for FR-9 protocol authoring — prior art may shape the decision tree)
  - Disposition: `designer-general-knowledge` — this is a question a competent designer would approach by surveying static-analysis suppression conventions (`// noqa`, `# pylint: disable`, `eslint-disable-next-line`, `// nosec`) and adapting principles. The designer carries the rationale in their design subsection per `disciplines/discovery-planning.md`. No external research warranted; reaching for sources would be over-engineering.

### Cross-cutting information needs

- **IN-011** — What does the existing audit report look like end-to-end (length, structure, how findings are grouped) and does that presentation make finding-categorization harder than necessary (per FR-10)?
  - Consumer: per-layer design (decides whether FR-10 audit-presentation improvements are warranted)
  - Disposition: `codebase-topic` — examine the current audit output; assess presentation. Routed to `discovery-codebase-researcher`.

- **IN-012** — Does the existing `shared-document-reviewer` framework support new doc_types via a registration pattern, and would a new "PedagogicalMarkerJustification" doc_type fit (or would mechanism-α be better enforced in the marker_check script directly)?
  - Consumer: per-layer design (FR-7-b enforcement-location decision)
  - Disposition: `codebase-topic` — read `shared-document-reviewer.md` (the agent) AND any spec-registration code; assess fit. Routed to `discovery-codebase-researcher`.

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The researcher reads `prd-v1.md` + this research-plan + the touch points below; outputs `codebase-analysis.json` + `codebase-analysis-report.md`.

### Touch points

Files / modules likely in scope:

- `.claude/skills/auditing-cc-configs/scripts/pedagogical_marker_check.py` — primary marker enforcement (FR-7-b)
- `.claude/skills/auditing-skills/scripts/pedagogical_marker_check.py` — possibly a duplicate; relationship to be confirmed
- `.claude/skills/auditing-cc-configs/scripts/audit_project.py` — top-level audit orchestrator (FR-6 X9 emission likely lives here or in dispatched modules)
- `.claude/skills/auditing-cc-configs/scripts/triage_with_judge.py` — marker pre-triage layer; mechanism-α may extend triage logic
- `.claude/skills/auditing-cc-configs/references/pedagogical-marker-spec.md` — current spec; mechanism-α extends or supersedes
- `.claude/skills/auditing-cc-configs/references/triage-protocol.md` — current triage protocol
- `.claude/skills/auditing-subagents/scripts/analyze_subagent.py` — SA-2 regex (FR-4); X9 emission for subagents that preload skills (FR-6)
- `.claude/skills/auditing-skills/scripts/scan_security.py` — DE-2 + similar (already fixed in v4.4.1 / v4.5.0; context for FR-7)
- `.claude/skills/auditing-skills/scripts/lint_references.py` — broken-link emission (Category A/B/C dispositions need to know the exact rule)
- All 29 sub-agent files in `.claude/agents/*.md` flagged by SA-2 (FR-4)
- 6 specific agent files for Category E: `discovery-codebase-researcher.md`, `review-architecture-auditor.md`, `shared-document-reviewer.md` (wildcard MAJORs); `design-claude-code.md`, `finalize-reconciler.md`, `review-cross-artifact-auditor.md` (bypass-approval BLOCKERs)
- All affected KB SKILL.md files for Category A/B markup: `KB-cc-platform`, `KB-cc-design`, `KB-codespaces-platform`, `KB-codespaces-design`, `KB-github-actions-platform`, `KB-documentation-criteria`
- `skills/synthesize/` + `report-composition-knowledge/` directories for Category C — assess maintenance status
- `KB-visual-design/references/anti-slop.md` — existing v4.4.0 markers (FR-8 retroactive upgrade)

### Blast-radius questions

- Which sub-agents preload which skills (the X9 fan-out — IN-006)? Required for FR-6 Stream 1 verification record enumeration.
- Which files import / depend on `pedagogical_marker_check.py` (both instances)? Required for FR-7-b enforcement-change risk assessment.
- Which audit invocations (CI hooks, scripts, manual invocations) exercise the audit pipeline? Required for FR-10 to know how presentation changes propagate.
- Are there any consumers of the audit JSON output (beyond the markdown report) that mechanism-α would break? Required for FR-6 Stream 2.

### Convention discovery

- Existing project conventions for adding new spec files to `KB-documentation-criteria/references/` (file naming, frontmatter, cross-referencing patterns).
- Existing conventions for inline comments / annotations in markdown frontmatter (any precedent for inline justification syntax that mechanism α could match).
- Per-layer designer conventions for `<layer>-design.md` + `<layer>-dependencies.json` shape (this feature is single-layer Claude Code, so `claude-code-design.md` + `claude-code-dependencies.json`).

### Specific queries or grep targets

- `grep -rln 'pedagogical_sections' .claude/` — enumerate every frontmatter declaration (IN-003)
- `grep -rln '^\`\`\`audit-example' .claude/` — enumerate every fence-wrapped block (IN-003)
- `grep -rln 'X9' .claude/skills/auditing-*/` — enumerate every X9 emission site (IN-005)
- `grep -nE 'skills:' .claude/agents/*.md` — map subagent → preloaded-skills (FR-6 Stream 1 scope)
- File-mtime survey on `skills/synthesize/` + `report-composition-knowledge/` (IN-008)

## External research topics

Per ADR-0021, every external topic carries explicit KB-gap justification. Default budget: 6.

This feature is internal-tooling work entirely within the project's own conventions. Most information needs are codebase-research or covered by existing KBs/specs. **One** external topic is genuinely warranted:

- **T-001** — Static-analysis suppression-discipline patterns from comparable tools
  - **Research question**: How do mature static-analysis tools (ESLint, Pylint, Bandit, Semgrep, RuboCop) handle the "false-positive vs real-defect" dispositioning problem, especially the discipline mechanisms that prevent suppression annotations from becoming a casual reach-for?
  - **KB gap justification**: `KB-documentation-criteria` covers project-internal disciplines; `auditing-cc-configs/references/pedagogical-marker-spec.md` covers the project's own marker spec. NEITHER discusses how this dispositioning problem is solved in other static-analysis ecosystems. The mechanism-α decision (require inline justification per marker) was made by analogy to common practice during intent refinement — but the analogy wasn't grounded in specific patterns. Without that grounding, mechanism-α's spec may miss adjacent patterns (e.g., "justification must reference an issue ID"; "suppression annotations have expiration dates"; "blanket suppressions vs scoped suppressions"). This is NOT designer-general-knowledge — most designers haven't surveyed the comparative literature here, and the per-layer design needs the survey to make informed mechanism-α decisions.
  - **Acceptance criteria**:
    - Names ≥4 distinct static-analysis ecosystems and their suppression annotation conventions
    - For each, identifies the discipline mechanism (if any) that prevents casual suppression
    - Identifies ≥2 patterns the project could adopt and ≥1 the project should NOT adopt (with rationale)
    - Cites primary sources (tool docs or canonical project conventions), not blog summaries
  - **Source constraints**: Official tool documentation + canonical project conventions (e.g., the rules a major OSS project documents for its team). Reputable engineering blogs from companies operating large codebases at scale ARE acceptable; aggregator listicles are NOT.

That is the only external topic. All other information needs route to codebase-research or KB/ADR/general-knowledge dispositions.

## Topics explicitly NOT researched

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-001 | `auditing-cc-configs/references/pedagogical-marker-spec.md` | Frontmatter form (`pedagogical_sections:` list) AND fence form (` ```audit-example ` opening fence) both documented with worked examples in the existing spec. |
| IN-004 | Same | The spec's "Anti-laundering rules" section defines what marker patterns the auditor distrusts (e.g., declared-pedagogical files that ALSO contain genuine credentials; markers without surrounding context). Mechanism-α extends but does not contradict. |
| IN-010 | designer-general-knowledge | Per-layer designer applies their general knowledge of suppression-annotation conventions (ESLint disable comments, Pylint annotations, etc.) with documented rationale in the design subsection. External research T-001 above DOES go further than designer-general-knowledge — that one is justified because mechanism-α is consequential enough to warrant primary-source grounding, not just designer recollection. |

## Estimated effort

- **Codebase research effort**: **medium**. Multiple files to read across two auditor skill families; 29 sub-agents to grep-sample; 6 specific agent files for Category E; 2 candidate-deprecated skills to assess. Estimated: ~2-3 hours single-instance.
- **External research topic count**: 1 of 6 budget. (Under-budget is correct — most needs route elsewhere.)
- **Estimated wall-clock**: ~3-4 hours total (codebase + external in parallel where possible).

## Open questions for human resolution

**Resolved at Gate 3 approval (2026-05-21T17:40:00Z):**

- **OQ-001** (RESOLVED): External research stays at single topic (T-001). No additional topics warranted.
- **OQ-002** (RESOLVED — generalized to a cross-stage principle): The original question was about scope-shift handling for Category C. The user's answer ("a but for all findings. nothing should be silent because 1 could be major") elevates this to a cross-stage discipline that supersedes the per-question scoping rule.
  - **Principle (no-silent-scope-changes):** ANY discovery, design, or implementation finding that would expand, contract, or reinterpret the PRD's scope — for ANY category, not just C — MUST be surfaced explicitly for human resolution. No silent absorption. No silent deferral. "Just one extra finding" is not a valid reason to skip surfacing: a single deviation could be the canary for a larger pattern, and the discipline only holds if there are zero unilateral scope decisions.
  - **Application scope:** All downstream stages (Discovery Research, Synthesis, per-layer Design, Design Composition, Architecture Audit, Plan, Cross-Artifact Audit, Reconciliation, Task Decomposition, Deliverable Packaging).
  - **Surfacing mechanism:** A new "Scope-deviation surfacing" entry MUST be added to the relevant stage's output document (e.g., `codebase-analysis-report.md`'s Findings section; `<layer>-design.md`'s Open Questions; `blueprint-v<N>.md`'s Architectural Questions; `plan-v<N>.md`'s Risks; etc.). The Architectural Audit and Cross-Artifact Audit stages MUST check that any scope deviation observed in an upstream artifact was surfaced rather than absorbed.
  - **Trigger examples:** Discovery finds a 7th finding category. Design needs a new agent. Plan reveals an upstream PRD AC is unverifiable as written. Implementation finds a Category C ref pointing to a deprecated skill the team didn't realize was deprecated. All MUST surface, regardless of how small.
- **OQ-003** (RESOLVED): T-001's ecosystem selection is the external researcher's choice. The acceptance criteria (≥4 ecosystems, primary sources) bound quality; specific ecosystem prioritization is not directed.

---

## Authoring rules adherence (per disciplines/discovery-planning.md)

1. ✓ KB-and-ADR-first applied: 3 information needs disposed to existing KB/ADR; 1 to designer-general-knowledge; only 1 routed external.
2. ✓ External topic carries explicit justification (T-001 names which KBs/specs were checked and what gap remains).
3. ✓ External topic count (1) under budget (6).
4. ✓ T-001 acceptance criteria are concrete (named counts, source-type constraints).
5. ✓ Codebase research scope is non-empty (12 touch points, 4 blast-radius questions).
6. ✓ Section order: confirmed → proposed → exclusions (template order honored).

## Related artifacts

- PRD: `working/feature/audit-findings-remediation-r1/prd-v1.md` (Stage 2 output)
- Discovery-planning discipline: `.claude/skills/KB-documentation-criteria/references/disciplines/discovery-planning.md`
- ADR-0021 (Discovery Phase Architecture): `adrs/ADR-0021-discovery-phase-architecture.md`
- Pedagogical-marker spec (current state): `.claude/skills/auditing-cc-configs/references/pedagogical-marker-spec.md` — note: PRD references KB-documentation-criteria as the spec's home; the actual location is `auditing-cc-configs`. Per-layer design must reconcile (likely the new mechanism-α spec lives in `KB-documentation-criteria` for cross-cutting visibility while the implementation continues to live in the auditor scripts).
