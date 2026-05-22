---
id: ADR-0020
version: 1.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 production session)
supersedes: []
adrs_inherited:
  - ADR-0010 v2.0.0 (knowledge-skill frontmatter correction)
  - ADR-0011 (documentation-criteria canonical document skill — extended here to absorb additional skills)
  - ADR-0017 (document-reviewer integration — references the consolidated KB-review-disciplines)
  - ADR-0019 (naming convention — applies the KB- prefix)
applies_to:
  - feature-pipeline blueprint v4.3.0
  - all knowledge skills in `.claude/skills/`
template_format: per ADR.txt v1.0
---

# ADR-0020: KB structure — consolidation of related skills + platform/design split for 3 platform layers

## Status

Accepted — 2026-05-19

**KB-count ratification (2026-05-19):** The 17-KB final count (vs originally-proposed 15) was surfaced to the user post-Phase-8 with three options (accept, reject by folding stage-specific KBs into KB-documentation-criteria, defer to Phase 2 implementation). User selected ACCEPT. The 17-KB count is the ratified final inventory for v4.3.0. KB-codebase-research and KB-task-decomposition are retained as distinct stage-specific KBs.

## Context

v4.2's knowledge-skill inventory grew to 21 distinct skills across the pipeline. Three structural problems emerged:

(1) **Functional duplication in document authoring.** Four skills (`prd-authoring-knowledge`, `design-composition-knowledge`, `planning-knowledge`, `acceptance-testing-knowledge`) each held authoring discipline for a specific document type. Each of these documents was already templated in `documentation-criteria` per ADR-0011. The separation of "template" and "discipline" across different skills meant authors had to load 2-3 skills to author one document, with overlapping content (e.g., EARS-format guidance lives in `acceptance-testing-knowledge` but ALSO applies to the Blueprint's acceptance criteria section authored under `design-composition-knowledge`).

(2) **Functional duplication in review.** Three skills (`architecture-audit-knowledge`, `cross-artifact-audit-knowledge`, `document-review-knowledge`) each held a review discipline: CoVe + blast-radius for architecture review, CMC + diff-mode + convergence for cross-artifact review, and the document-reviewer's Gate 0/1 procedure. While the disciplines are distinct, they share core concerns (issue severity taxonomy, location specifiers, prior_context_check semantics) and are each loaded by exactly one sub-agent.

(3) **Asymmetry between Claude Code's platform/design split and other "platform" layers.** v4.2 had `claude-code-filesystem-knowledge` (what Claude Code IS — primitives, file layout) and `claude-code-fs-design-knowledge` (how to design for it) — a clean platform/design split. But the analogous split was missing for GitHub Actions and Codespaces, even though both are equally platform-bounded (each has a specific, finite, well-documented platform with concrete primitives, like Claude Code). v4.2 had `cicd-design-knowledge` and `codespaces-design-knowledge` — design half present, platform half absent. This asymmetry forced design-cicd and design-codespaces to either inline platform knowledge into design discipline (mixing concerns) or assume platform knowledge as ambient (relying on Claude's training-data familiarity, which drifts over time).

The user (Q-v4.3-kb) endorsed (a) consolidating the documentation-authoring skills into KB-documentation-criteria, (b) consolidating the review skills into a new KB-review-disciplines, and (c) extending the platform/design split to GitHub Actions and Codespaces.

## Decision

Restructure the KB inventory in three moves:

### Move 1 — Document-authoring consolidation

Delete four KBs and absorb their content into a single consolidated `KB-documentation-criteria`:
- `prd-authoring-knowledge` → absorbed (PRD authoring discipline now lives alongside the PRD template)
- `design-composition-knowledge` → absorbed (composer's integration patterns + evidence-based arbitration now live alongside the Blueprint template)
- `planning-knowledge` → absorbed (Plan authoring discipline now lives alongside the Plan template)
- `acceptance-testing-knowledge` → absorbed (EARS-AC discipline now lives alongside the Blueprint template, which has the AC section)

### Move 2 — Review-discipline consolidation

Delete three KBs and absorb their content into a single new `KB-review-disciplines`:
- `architecture-audit-knowledge` → absorbed
- `cross-artifact-audit-knowledge` → absorbed
- `document-review-knowledge` → absorbed

### Move 3 — Platform/design split extended to 3 platform layers

Add two new platform KBs to complete the platform/design split:
- `KB-github-actions-platform` — what GitHub Actions IS (workflow syntax, runners, matrix strategies, secrets, reusable workflows, action publishing)
- `KB-codespaces-platform` — what Codespaces IS (devcontainer.json schema, Features, prebuilds, port forwarding, dotfiles, lifecycle hooks)

Rename existing `cicd-design-knowledge` → `KB-github-actions-design` (per ADR-0019 naming convention + this ADR's platform-specificity decision — the pipeline is opinionated about GitHub Actions specifically as the CI/CD platform). Codespaces design KB keeps its scope (was already platform-specific) but renames per ADR-0019.

**The platform/design split applies only to these three "platform" layers:**

| Layer category | Has platform/design split? | Why |
|---|---|---|
| Claude Code | Yes | Specific platform with finite, documented primitives |
| GitHub Actions | Yes | Specific platform with finite, documented primitives |
| Codespaces | Yes | Specific platform with finite, documented primitives |
| Frontend | No | "Platform" varies per codebase (React, Vue, Svelte, Angular, vanilla, server-rendered) |
| Backend | No | "Platform" varies per codebase (Express, FastAPI, Spring, Rails) |
| API | No | Implementation-language-dependent; not a single platform |
| Query | No | Implementation-stack-dependent |
| Database | No | Implementation-engine-dependent |
| IaC | No | Tool-dependent (Terraform, CloudFormation, Pulumi, Bicep); KB stays generic until evidence of need for tool-specific splits |

For the 6 design-only layers, the codebase-researcher at Stage 3 discovers what platform/stack the user's codebase actually uses, and the design sub-agent applies design discipline to that discovered platform.

## Decision Details

| Item | Content |
|---|---|
| Decision | Three-move restructure: (1) consolidate 4 doc-authoring KBs into KB-documentation-criteria; (2) consolidate 3 review KBs into new KB-review-disciplines; (3) add 2 new platform KBs (KB-github-actions-platform, KB-codespaces-platform) to complete the platform/design split for 3 platform layers. Final count: 17 KBs (up from 13 in v4.2 if we count the absorbed skills together, or down from 21 if counted individually). |
| Why now | Three reasons: (a) the consolidations remove duplication that v4.2 had been carrying since v4.0; (b) the platform/design split's incompleteness was a v4.0-introduced regression vs v3 (v3 didn't have GitHub Actions or Codespaces as separate concerns; v4 added the layers but only added design KBs, missing the platform KBs); (c) v4.3 is pre-implementation, so the restructure is blueprint-text-only with no on-disk migration. |
| Why this consolidation pattern | The four absorbed doc-authoring skills all teach how to author a document whose template lives in documentation-criteria. Co-locating template and authoring discipline reduces cross-skill lookup. The three absorbed review skills all teach how to review documents/architecture; co-locating reduces concept fragmentation (e.g., issue severity taxonomy is now in one place, used by 3 sub-agents). |
| Why the platform/design split | Platform KBs answer "what primitives exist on this platform"; design KBs answer "given those primitives, how should we choose for a given feature?" Separating them lets the platform KB stay current with platform changes (GitHub releases new workflow syntax annually; Codespaces adds Features semi-regularly) without forcing the design KB to also churn. Design discipline is more stable than platform mechanics. |
| Known unknowns | Whether KB-documentation-criteria will grow too large after absorbing 4 skills' content; whether KB-review-disciplines will grow too large after absorbing 3 skills' content. Mitigation: skill loading is by reference, not full content; sub-agents load specific sections via Read tool, not the whole skill. |
| Kill criteria | If KB-documentation-criteria or KB-review-disciplines exceeds 8K tokens AND a sub-agent loads it just for a single section, split the skill via a follow-up ADR. |

## Rationale

**Consolidation reduces cross-skill lookups.** v4.2's PRD author needed to load `documentation-criteria` (template), `prd-authoring-knowledge` (discipline), and `KB-documentation-criteria`'s rationale-brief guidance — three skill loads for one document. After Move 1, one skill load covers all three.

**Platform/design split makes design discipline portable.** When GitHub releases a new workflow primitive (e.g., reusable workflow inputs gained `outputs` support in 2024), only `KB-github-actions-platform` changes. `KB-github-actions-design` (which says "use reusable workflows for X, inline workflows for Y") doesn't churn unless the design discipline itself changes.

**Asymmetry resolution.** v4.2 had only Claude Code's platform/design split. Either we drop the split (and inline Claude Code's platform knowledge into the design KB) or we extend the split to other platforms. The user chose the latter, which is the more architecturally coherent choice — recognizing that platform mechanics and design discipline are genuinely separable concerns regardless of which platform.

**Why not split for Frontend/Backend/etc.** A user might use React or Vue or Svelte for Frontend. Writing a `KB-frontend-platform` is impossible without picking a framework, and picking one for the KB constrains the pipeline to that framework. Instead, the codebase researcher discovers the framework at Stage 3, and the design KB applies framework-agnostic design discipline (component composition, state colocation, accessibility) to whatever framework the codebase uses.

**Why "github-actions-design" and not "cicd-design".** The pipeline is opinionated about GitHub Actions specifically (per ADR-0013's Layer Scope: "CI/CD (GitHub Actions)"). If a future version supports CircleCI or Jenkins, the cleaner extension path is to add `KB-circleci-platform` + `KB-circleci-design` rather than to make `KB-cicd-design` generic. Specific-platform-named KBs scale better than generic-category-named ones for design discipline.

## Consequences

### Positive

- 7 KB deletes + 2 KB adds = net -5 distinct skills to load, but consolidated KBs are richer.
- One-stop authoring KB for documents; one-stop review KB for review.
- Platform/design split is now symmetric across the 3 platform layers.
- Design discipline KBs are insulated from platform churn.

### Negative

- Migration cost for any tooling that pre-existed at the old KB names. Mitigated by the v4.3-is-pre-implementation timing.
- Two consolidated KBs are large. Mitigated by section-level loading.

### Neutral

- The KB count increased from the user's original 15-estimate to 17 because two stage-specific KBs (`KB-codebase-research`, `KB-task-decomposition`) were absent from the initial proposal and surface here as required-to-keep separate (codebase research is its own discipline; task DAG construction is its own discipline; neither fits the doc-authoring or review consolidations).

## Implementation Guidance

- The 7 KBs being absorbed are NOT physically renamed in v4.3.0 (they don't exist on disk yet — Phase 2 implementation hasn't started). v4.3.0 blueprint text references the consolidated KB names directly.
- KB-documentation-criteria's body will need to be authored in Phase 2 Implementation to actually contain (a) the 5 templates, (b) PRD-authoring discipline, (c) Plan-authoring discipline, (d) design-composition discipline, (e) EARS-AC discipline. v4.3.0 only specifies the structure; the content is Phase 2 work.
- KB-review-disciplines's body similarly needs Phase 2 authoring.
- KB-github-actions-platform and KB-codespaces-platform are brand-new KBs requiring fresh authoring in Phase 2 (no v4.2 predecessor).

## Related Decisions

- ADR-0011 (documentation-criteria canonical document skill) — extended here: documentation-criteria absorbs 4 additional skills.
- ADR-0017 (document-reviewer integration) — the renamed KB-review-disciplines is what shared-document-reviewer now loads.
- ADR-0019 (naming convention) — provides the KB- prefix; this ADR uses it.
- ADR-0021 (discovery phase architecture) — discovery-plan-author consults the KBs listed here to decide if external research is warranted.

## Open Questions

None at v4.3.0 acceptance time. The 17-KB structure is the consolidated end state.
