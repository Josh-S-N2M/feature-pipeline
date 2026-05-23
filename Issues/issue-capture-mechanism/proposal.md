---
id: PROPOSAL-issue-capture-mechanism
version: 0.1.0
doc_type: issue-proposal
status: draft
generated: 2026-05-23T00:00:00Z
generated_by: claude (planning-mode session — pre-mechanism bootstrap)
feature_slug: pipeline-wide
scope: pipeline-wide
mode: report-only
proposes_future_feature: issue-capture-mechanism-r1
companion_artifacts:
  - /home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md
  - Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md  (post-migration)
  - Issues/per-agent-design-evaluation-gap/analysis.md  (post-migration)
  - Issues/adr-placement-rootcause/analysis.md  (post-migration)
  - Issues/auditing-family-graduation-review/proposal.md  (post-migration)
  - .claude/skills/KB-documentation-criteria/
  - .claude/skills/KB-cc-design/
  - .claude/skills/KB-cc-platform/
  - .claude/skills/recipe-feature-pipeline/SKILL.md
  - .claude/agents/intake-intent-clarifier.md
  - .claude/skills/KB-review-disciplines/references/issue-lifecycle.md
  - .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py
  - .claude/settings.json
---

# Proposal — Formalize the Issue-Capture Mechanism (Outside-the-Pipeline)

## TL;DR

While running features through the Feature Pipeline, the user repeatedly noticed issues that were **out of scope for the active feature** but had to be remembered — pipeline-wide structural gaps, future-feature candidates, sweepable deferrals. Four such files already exist ad-hoc under `Issues/` (one register, two analyses, one proposal). The practice works, but it has no canonical templates, no agent that authors it, no enforcement that prevents pipeline sub-agents from accidentally writing into the same surface, and no documented handoff back into the Feature Pipeline when a captured proposal is ready to become a real feature.

This proposal seeds a feature run (`issue-capture-mechanism-r1`) that formalizes the practice. A planning-mode session already produced detailed design in [the companion plan file](/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md) — that work should serve as `prior_context` for the pipeline's Intent Clarifier rather than be re-derived from scratch.

## Precedent / triggering event

- **2026-05-23 conversation** — the user (Josh-S-N2M), working in `/workspaces/feature-pipeline`, observed: *"I am noticing as I work on features within the feature pipeline issues arise that need to be documented for future feature consideration. It is important to not pollute the feature run unless it is material to the feature scope. However, it is also super important to capture at that moment with the evidence to ensure it does not get forgotten."*
- The user requested a formal mechanism with three explicit constraints:
  1. Formalize the practice in `KB-documentation-criteria` (templates + frontmatter).
  2. Separate agent and KB skill outside the Feature Pipeline.
  3. Cannot be called by Claude main or pipeline sub-agents without user approval; approval must present clear WHY / WHAT / WHERE.
- A planning-mode session iteratively refined the design across four user-clarification rounds. Decisions were recorded in [the plan file](/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md). After realizing the scope (16+ files, multiple ADR-worthy decisions, cross-layer impact), the user redirected the work to go through the Feature Pipeline rather than execute the plan directly — which is the disciplined choice and matches the precedent set by `auditing-mcp` graduation in `devcontainer-mcp-provisioning-r1`.

## Why this matters / inputs the future feature should consider

This subsystem is **non-trivial** and **load-bearing for project discipline**:

- **Multi-primitive**: skills (KB + entry-point), agent, hook, settings, KB templates, validator script extension — touches `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, `.claude/settings.json`, and `Issues/`.
- **Multiple ADR-worthy decisions** (none yet ratified):
  1. Per-issue folder model vs. flat (decided: folder, per user)
  2. Three doctypes preserved (register / analysis / proposal) vs. unified
  3. Add-new-doctype-file evolution pattern vs. mutate-status
  4. Three-layer approval enforcement (disable-model-invocation + agent body + PreToolUse hook) vs. simpler
  5. Entry mechanism via Intent Clarification `prior_context` (existing optional parameter) vs. new pipeline stage
  6. Status vocabulary: 5-state for files (`draft → open → adopted | complete | superseded | wontfix-with-rationale`), distinct from intra-pipeline 4-state ledger
  7. Structural-vs-discipline split inside `KB-documentation-criteria` (templates here; triggering discipline elsewhere)
- **Cross-cutting compliance**:
  - Must not break frontmatter-validator (`validate_pipeline_frontmatter.py`) — instead, extend it.
  - Must not be auto-invocable by any of the ~28 pipeline sub-agents.
  - Must respect KB-cc-design Principles 1, 3, 5, 6, 8, 9.
  - Must preserve all 6 mandatory human gates (no bypass).
- **Sets a precedent** for how outside-pipeline mechanisms should be authored in this repo. Running it through the pipeline is the self-consistent answer the user explicitly insisted on.

### Inputs the Feature Pipeline should have ready

The Discovery and Design stages should consume:

1. The four existing `Issues/*.md` files (post-migration to per-issue folders) — these are the **empirical precedent** for what an "issue" looks like; the templates must codify their shape, not invent new shapes.
2. `KB-documentation-criteria/references/shared-conventions.md` — frontmatter inheritance source of truth.
3. `KB-documentation-criteria/references/templates/*.md` — existing pipeline templates that the new issue-doctype templates should structurally parallel.
4. `KB-review-disciplines/references/issue-lifecycle.md` — defines the intra-pipeline 4-state vocabulary that the new 5-state (for `Issues/*.md`) parallels but is **distinct from**.
5. `recipe-feature-pipeline/SKILL.md` — confirms exclusion rule "No stage advance without gate pass" and documents `intake-intent-clarifier`'s optional `prior_context` parameter that is the key to the handoff design.
6. `.claude/agents/cc-critique.md` and `.claude/agents/shared-document-reviewer.md` — the two existing non-pipeline agents; they serve as reference shape for the new `issue-capture-author`.
7. `.claude/skills/auditing-skills/references/frontmatter-spec.md` — authoritative on `disable-model-invocation: true`.
8. External research already conducted (Dual-Track Agile, Spotify RFC decision-tree, Pragmatic Engineer on RFCs/ADRs) — supports the "Discovery → Delivery handoff is disciplined, not a stage skip" design.

## Suggested slug for the future feature run

`issue-capture-mechanism-r1`

(The `proposes_future_feature` frontmatter field above carries this slug. The Feature Pipeline orchestrator should use it when invoked with `--raw-request Issues/issue-capture-mechanism/proposal.md`.)

## Scope hints for the future run

### In-scope (proposed)

- New KB skill `KB-issue-capture` with `disable-model-invocation: true` and four reference files (triage criteria, approval-prompt rubric, examples, non-pollution contract).
- New entry-point skill `capture-issue` exposing `/capture-issue` and `/capture-issue --update <path>` with `disable-model-invocation: true`.
- New outside-pipeline agent `issue-capture-author` (`tools: Read, Grep, Glob, Write, AskUserQuestion`, `model: sonnet`).
- New hook script under `.claude/hooks/` intercepting `Task` tool calls with `subagent_type == issue-capture-author`.
- Additive patch to `.claude/settings.json` (one permission entry + one PreToolUse hook block).
- Three new structural templates under `KB-documentation-criteria/references/templates/` plus a structural spec (`issue-doctypes-spec.md`) — strictly structural, no triggering discipline.
- Extension of `validate_pipeline_frontmatter.py` to recognise the three new `doc_type` enum values and the 5-state status vocabulary.
- Migration of the 4 existing flat `Issues/*.md` files into per-issue folders (`git mv`) and back-fill of `version: 0.1.0`.
- Small edits to `intake-intent-clarifier.md` (proposal-as-prior-context handling), `intent-clarification-template.md` (Source-section guidance), `recipe-feature-pipeline/SKILL.md` (invocation pattern).

### Out-of-scope (proposed)

- A new intra-pipeline issue mechanism (the existing `issues-ledger.json` is sufficient).
- A UI surface beyond the slash command.
- Automated cross-linking between `Issues/*.md` and intra-pipeline ledger entries (they MUST remain distinct).
- A scheduled sweep to back-fill or migrate Issues/ files that haven't yet adopted the folder model (handled as a one-time migration; ongoing files use the folder model from creation).
- Slack / webhook / external notification integration.

### Layers touched (preliminary)

Per KB-documentation-criteria's 9-layer taxonomy:

- **Claude Code / Project Filesystem** (primary) — skills, agent, hook, settings, KB templates.
- **Backend / Tooling** (secondary) — extension to `validate_pipeline_frontmatter.py` script.
- Frontend / API / Database / Query / IaC / CI-CD / Codespaces — out of scope.

## Adoption

To turn this proposal into the seeded feature pipeline run:

```
<recipe-feature-pipeline-skill>  issue-capture-mechanism-r1  --raw-request  Issues/issue-capture-mechanism/proposal.md
```

The Feature Pipeline's `intake-intent-clarifier` should:

1. Read this proposal file (detects `doc_type: issue-proposal`).
2. Treat the body as authoritative prior context (do NOT re-elicit the rationale, triggering event, doctype model, enforcement layers, naming, folder model, evolution pattern, or scope hints — they're decided).
3. Ask clarifying questions ONLY about what this proposal lacks:
   - **Functional Requirements** (FRs) in numbered form.
   - **Non-Functional Requirements** (NFRs) — performance, security, observability.
   - **Acceptance Criteria** in EARS format for each FR.
   - **Stakeholder posture** (formal table).
   - **Exhaustive Layer Scope** declaration across all 9 layers (this proposal hints at it but does not formally declare).
   - Detailed **Plan-internal phase boundaries**.
4. Also read the companion plan file at `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md` — it contains 400+ lines of decided design that the Blueprint and Plan stages should consume as input rather than re-derive.

## Cross-references

- **Plan file** (planning-mode session, 2026-05-23): [/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md](/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md) — detailed design across architecture, naming, file tree, frontmatter, approval prompt, hook script, lifecycle state machine, Issues-vs-ledger decision rubric, handoff design, verification plan, risks.
- **Existing ad-hoc Issues files** (precedents to codify, not modify):
  - `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` (pre-migration)
  - `Issues/analysis-per-agent-design-evaluation-gap.md` (pre-migration)
  - `Issues/analysis-adr-placement-rootcause.md` (pre-migration)
  - `Issues/proposal-auditing-family-graduation-review.md` (pre-migration)
- **Auto-memory** (relevant prior decisions):
  - `feedback_artifact_placement.md` — user wants plain-English confirmation before placing non-pipeline documents; this design honors that.
  - `project_agent_design_gap.md` — saved-for-later precedent for capturing structural gaps; this proposal formalizes the practice that's already happening.
- **KB pairings the per-layer designers will consult**:
  - `KB-cc-design` + `KB-cc-platform` (primary — most of the work is in `.claude/`).
  - `KB-documentation-criteria` (templates + frontmatter inheritance).
  - `KB-review-disciplines` (issue-lifecycle.md for parallel-but-distinct vocabulary).
- **External research conducted** (planning-mode):
  - [Productboard on Dual-Track Agile](https://www.productboard.com/glossary/dual-track-agile/)
  - [SVPG on Dual-Track Agile](https://www.svpg.com/dual-track-agile/)
  - [Pragmatic Engineer on RFCs/Design Docs/ADRs](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)
  - [Diamond's RFC process](https://blog.diamond.la/adopting-a-structured-rfc-process)
  - [LogRocket on Dual-Track Agile + Continuous Discovery](https://blog.logrocket.com/product-management/dual-track-agile-continuous-discovery/)

## Provenance

- **Authored**: 2026-05-23 by Claude (planning-mode session) at user request.
- **Bootstrap note**: This proposal is the dogfood test of the mechanism it proposes — it sits at `Issues/issue-capture-mechanism/proposal.md` using the per-issue folder model and frontmatter shape that the future feature run will canonicalize. The mechanism doesn't exist yet, so this file was hand-authored; once the mechanism ships, future proposals will be `/capture-issue`-authored.
- **Forgetting risk**: Negligible (the user has asked us to start the pipeline immediately). Captured here for audit-trail completeness — anyone reading `Issues/issue-capture-mechanism/proposal.md` after the fact will see the precedent that triggered the formalization.
