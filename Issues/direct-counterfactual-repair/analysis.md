---
id: ANALYSIS-direct-counterfactual-repair
version: 0.1.0
doc_type: issue-analysis
status: draft
feature_slug: pipeline-quickwins-hardening-r1
generated: 2026-05-27
generated_by: issue-capture-author (via /capture-issue slash command), file write completed directly by main session because SendMessage was unavailable to continue the paused sub-agent
---

# Direct Counterfactual Repair — Pipeline vs Direct Claude Code

## Contents
- [TL;DR](#tldr)
- [Background / Evidence](#background--evidence)
- [Root Cause](#root-cause)
- [Implications](#implications)
- [Recommendations / Open Questions](#recommendations--open-questions)
- [Cross-links](#cross-links)

## TL;DR

The user's unbiased-assessment review (2026-05-27) concluded that the 13-stage feature pipeline has not been tested against its stated yardstick (*ships unrelated features autonomously*) and that the simplest counterfactual — Claude Code working directly — would likely deliver cleanup-grade improvement work faster than the pipeline can. This Issue records the deliberate test: a single batch of pipeline-improvement work is being executed by the main session **without** invoking `recipe-feature-pipeline` or any pipeline sub-agent (other than `issue-capture-author`, which sits outside the pipeline per its own contract). Scope: remove the gitnexus MCP from the architecture; fix 108 reference-rot findings (79 broken file links + 29 cascade-from-FAIL-skill findings); fix 8 missing-TOC findings; fix 2 SA-2 subagent-description-quality findings. The output of this Issue plus the post-repair audit re-run together form the evidence base.

## Background / Evidence

### 1. The counterfactual hypothesis

From the unbiased-assessment review, *Counterfactual* section:

> If you had given Claude Code the same FR-1..FR-7 of `pipeline-quickwins-hardening-r1` *without* the pipeline — just "implement these seven hardening fixes, write tests, open PR":
> - Time: ~1 working day (the pipeline run took roughly 5 calendar days).
> - Artifacts: the code + commit messages. No PRD, no Blueprint, no Plan, no Phase Validators.
> - Quality of code: likely the same.

The hypothesis being tested: *for cleanup-grade work whose changes are not architectural, the pipeline overhead is not justified.*

### 2. Repair scope (the test's observable inputs)

From `project-audit-report.json` (score 0.0/100, 153 findings):

| Category | Count | Severity profile |
|---|---:|---|
| Broken file links (doc → nonexistent file) | 79 | all BLOCKER |
| Cascade from FAIL skill (parent has broken refs) | 24 | all MAJOR |
| Cascade from WARN skill | 4 | all MAJOR |
| Stale MCP allowlist (removed `mcp-openapi-schema` server) | 1 | MAJOR |
| Cosmetic missing-TOC | 8 | all MINOR |
| SA-2 description quality | 2 | all MAJOR |
| **Total in scope** | **118** | |

Out-of-scope (not part of this counterfactual test):
- 2 BLOCKER SA-4 prompt-injection findings in `issue-capture-author.md`
- 1 BLOCKER credential-in-URL anti-pattern in a skill body
- 22 permission rule findings (ST-9 bare-tool names + unrecognized syntax)
- 4 OP-7 event-log schema noncompliance findings
- 1 MC-3 publisher provenance advisory

Plus the architectural removal:
- Remove gitnexus MCP server from `.mcp.json`, `.devcontainer/postCreate.sh`, sub-agent allowlists, `AGENTS.md`, the gitnexus skill family, and any KB references. The user reports gitnexus as "broken and unusable" in practice.

### 3. Pipeline context

Under the normal pipeline, this batch of cleanup would enter at the Intent Clarification stage, traverse PRD → Discovery Planning → Discovery Research → Synthesis → per-layer Design (likely the Claude Code design layer) → Design Composition → Architecture Audit → Plan Authoring → Acceptance Test Authoring → Phase Validator Authoring → Cross-Artifact Audit → Reconciliation (up to 4 cycles) → Task Decomposition → Deliverable Packaging. Each stage produces artifacts, and 6 human approval gates would punctuate the flow.

In this test, none of those stages run. The main session reads the audit JSON, writes a fix script (or surgical edits), executes, re-audits.

## Root Cause

The pipeline was designed under the implicit assumption that all pipeline-improvement work warrants the same architectural rigor as a green-field user feature. That assumption is *load-bearing* for the pipeline's value proposition. If it is false for any non-trivial class of work, the pipeline's scope must be narrowed and its no-go cases documented.

The audit-finding cleanup is the cleanest possible counter-instance: 79 of 82 BLOCKERs are dead links to files that don't exist. There is no design decision to make. There is no architectural blast radius to assess. There is no acceptance test that can fail. Doing this work through the pipeline produces 570KB+ of authoring artifacts that have no informational payload.

## Implications

Three possible outcomes of the test, and what each implies for pipeline scope:

1. **Direct repair completes in materially less wall-clock time with comparable or better audit-score delta.** Implies: the pipeline should *not* be the default entry point for audit-finding remediation work. A separate, lightweight cleanup discipline is warranted. The pipeline's stated success criterion (*ships unrelated features autonomously*) must still be tested separately.

2. **Direct repair completes but introduces regressions the pipeline would have caught.** Implies: the pipeline's auditing stages provide net value even on cleanup; the cleanup discipline should still go through Architecture Audit and Cross-Artifact Audit, but other stages can be skipped.

3. **Direct repair stalls or fails.** Implies: the apparent simplicity of "delete the broken links" hid real architectural complexity that only the pipeline surfaces. Strong evidence in favour of pipeline-everywhere.

## Recommendations / Open Questions

- Define a `scope_class` taxonomy at the pipeline entry point: `FEATURE` (full pipeline), `MINOR` (skip Discovery, abbreviated Design), `PATCH` (direct execution with audit re-run only), `CLEANUP` (no pipeline). ADR-0023 already introduces a partial version of this; this Issue's outcome should be a forcing function to make it operational.
- Decide what counts as a CLEANUP-class change. Working definition for this test: *changes whose only effect is to satisfy an existing audit rule, with no new requirements, no new code paths, and no observable behavioural change*.
- The unbiased-assessment review also recommended attempting one non-meta user-facing feature next. This Issue does NOT substitute for that test; the two tests are orthogonal.

## Cross-links

- Unbiased-assessment review: conversation artefact, this session (2026-05-27), see `project-audit-report.md` and conversation transcript for the verdict.
- Audit baseline: [project-audit-report.md](/project-audit-report.md), [project-audit-report.json](/project-audit-report.json).
- Pipeline run that surfaced the audit: [working/feature/pipeline-quickwins-hardening-r1/](/working/feature/pipeline-quickwins-hardening-r1/).
- ADR-0023 scope-class concept: [adrs/ADR-0023-discipline-refinements-from-integration-test.md](/adrs/ADR-0023-discipline-refinements-from-integration-test.md).
- ADR-0007 (code-graph MCP selection — the ADR being implicitly superseded by removing gitnexus): [adrs/ADR-0007-code-graph-mcp-selection.md](/adrs/ADR-0007-code-graph-mcp-selection.md).
