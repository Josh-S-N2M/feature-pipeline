---
id: IC-pipeline-quickwins-hardening-r1
version: 1.0.0
status: approved
feature_slug: pipeline-quickwins-hardening-r1
user_token: gate1-approved-as-is-20260525T2218Z
generated: 2026-05-25T00:00:00Z
generated_by: intake-intent-clarifier
doc_type: intent-clarification
scope_class: MINOR
seed_doc_type: issue-proposal
seed_path: Issues/cross-artifact-divergence-detection-gap/proposal.md
---

# Intent Clarification: Pipeline Quick-Wins Hardening (Round 1)

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

This document captures the user's intent for the first-round hardening work that follows the MCP shipment incident. The work is the carve-out subset of a larger sibling analysis — only the five low-cost, mechanically bounded fixes. The full systemic remediation is deliberately deferred to a follow-on run. This document gates progression to PRD Authoring.

## Source

This feature run was seeded by an outside-pipeline issue-proposal (per ADR-0048 proposal-seeded clarification flow). The proposal is treated as authoritative prior context and is cited verbatim here:

- **Seed proposal:** `Issues/cross-artifact-divergence-detection-gap/proposal.md` (status: `adopted`, adopted_at: 2026-05-25, adopted_by_feature_slug: `pipeline-quickwins-hardening-r1`).

The proposal's TL;DR, Proposed Feature, Motivation, In-Scope Mechanisms, and Out-of-Scope sections substitute for what this clarifier would otherwise elicit. The user's original framing, paraphrased from the proposal: *"Close the five quick-win exposures the MCP postmortem named, without trying to fix the whole systemic gap in this run."*

## Initial Interpretation

The user wants a small, bounded hardening pass on the feature-pipeline's review and install machinery, motivated by an incident in which five of seven MCP servers shipped broken because each gate inspected its own artifact in isolation and never compared an ADR's prescription against the file that actually shipped. The five mechanisms named in the proposal are mechanical and locally scoped — a reviewer output-shape check, an orchestrator self-check on dispatch, a new MCP audit rule, a devcontainer install smoke test, and a CI smoke workflow. The intent is to close the most acute holes now and explicitly leave the broader audit-dimension and design-discipline work for a separate, later feature.

## Clarifying Questions and Answers

This run uses the proposal-seeded path. The proposal's adopted status and the orchestrator's invocation prompt together specify scope class, layers touched, the five mechanisms verbatim, and the explicit out-of-scope list. The user has also pre-confirmed (via the orchestrator prompt) the carve-out boundary. No live questions were posed — auto-mode invocation per system instruction, and the seed proposal answers everything the template normally elicits.

| # | Ambiguity | Question Asked | User Answer | Resolved? |
|---|---|---|---|---|
| 1 | Whether the carve-out boundary in the seed proposal is exactly what the user wants for this run | Not asked live; pre-answered by adoption of the proposal and the orchestrator prompt's verbatim restatement of the five mechanisms and the deferred list | The five proposal mechanisms are in; the eight deferred items are explicitly out and belong to a follow-on run | [x] |
| 2 | Scope class for this run (drives deliverable archive packaging and orchestrator policy) | Pre-answered by the proposal frontmatter and body | MINOR | [x] |
| 3 | Which engineering layers are touched | Pre-answered by the proposal | Claude Code / Project Filesystem (audit skill, reviewer discipline, orchestrator self-check, install script) and CI/CD (one new workflow). All other 7 layers out of scope. | [x] |
| 4 | Primary stakeholder identification for this run | Inferred from the proposal motivation and pipeline conventions | Feature-pipeline maintainers (you), and downstream pipeline users / sub-agents whose runs the new checks will gate | [x] |
| 5 | Definition of "done" for this run | Inferred from the proposal's Acceptance Sketch | Each of the five mechanisms is implemented, exercisable, and demonstrates the named failure mode getting caught | [x] |

## Clarified Intent

Land five small, mechanically bounded hardening changes that together close roughly a third of the catalogued MCP-incident defects and the single highest-risk deferral, at low total cost. Specifically:

1. **Make verdict-vs-findings consistency a real check.** A reviewer that returns "approved" with any blocking finding in its output is rejected by an automated structural check before the verdict propagates upstream. Applies to the phase-quality reviewer and any other reviewer that emits a verdict+findings pair.
2. **Forbid the single-agent fallback path for full-scope features.** The feature-pipeline orchestrator's dispatch self-check refuses to enter the loop if any stage is configured for single-agent fallback when the feature's scope class is FULL. Minor and patch scopes still permit the fallback.
3. **Add a parity rule between `.mcp.json` and the install-taxonomy ADR (ADR-0041).** A new audit rule in the MCP audit skill that, for each server entry in `.mcp.json`, fetches the invocation form prescribed in ADR-0041 and verifies they match (argv strings, env-var indirection, sentinel paths). Mismatch is a blocking finding. This is the narrow mechanical version of the larger design-realization audit deferred to a future run.
4. **GitNexus install smoke test.** Wire a pre-install dry-run into the devcontainer post-create flow that asserts `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` still skips the C++ toolchain path against the pinned GitNexus tag. Failure halts install with a clear message about pin-tag drift. Closes deferral row H-4.
5. **CI smoke test asserting `claude mcp list` connectivity.** A new GitHub Actions workflow that runs `claude mcp list` against the configured `.mcp.json` and fails the job on any non-connected server. Triggered on PRs touching `.mcp.json`, the devcontainer, or any audit skill. Closes deferral row B-1.

The systemic remediation — design-realization audit dimension, cross-file invariant catalog, live reachability handshake, tool-surface drift detection, per-agent design discipline, post-ship trigger discipline, orchestrator-driven codespace rebuild — is explicitly out of scope for this run and will be the subject of a separate, follow-on proposal and feature run. The sibling analysis remains open for that reason.

## Scope Posture

### What's in scope

- Reviewer output-shape structural check that rejects approved-with-blockers verdicts before they propagate.
- Orchestrator dispatch self-check that refuses single-agent fallback for FULL-scope features.
- New audit rule in the MCP audit skill comparing each `.mcp.json` server entry against the invocation form prescribed in ADR-0041.
- A pre-install dry-run in the devcontainer post-create flow that verifies the `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` contract against the pinned GitNexus tag.
- A new GitHub Actions workflow that runs `claude mcp list` on PRs touching `.mcp.json`, the devcontainer, or any audit skill, and fails on any non-connected server.
- Marking deferral-register rows H-4 and B-1 as adopted by this feature.

### What's NOT in scope (explicitly excluded)

- Design-realization audit dimension for the architecture-audit reviewer (the broader form of mechanism 3).
- A discovery-research protocol-conformance subsection requirement.
- A phase-validator-tier cross-file consistency invariant catalog.
- A live MCP reachability handshake (`--with-mcp-reachability` audit flag).
- Live tool-surface drift detection.
- Per-agent design discipline: mandatory agent-roster impact matrix, strengthened "preserve invariant" principle, skill-coverage check at design time, real gating on "blocks downstream" markers, feature-touch-coverage audit rule.
- Post-ship trigger discipline rework (the deferral register's section O observation).
- An orchestrator-driven codespace rebuild loop.
- Further patches to the still-broken MCP server files. The postmortem is explicit: do not patch them until the audit hardening lands, because patches will clear the same paper gates the original bugs cleared.

### What's undecided (deferred to PRD or later)

- The exact JSON shape of the reviewer output-validation contract (which severity tokens count as "blocking" — `BLOCKER` only, or also `critical`? — and whether the check is in-agent or out-of-agent).
- Where exactly the orchestrator's dispatch self-check lives (a hook, the orchestrator agent's own logic, or a separate gate script) and how it determines which stages are "configured for single-agent fallback."
- The precise ADR-0041-to-`.mcp.json` comparison algorithm (exact-string match on argv? canonicalized form? how env-var indirection is normalized for comparison).
- The shape and exit-code contract of the GitNexus dry-run script and the specific diagnostic message on failure.
- The exact set of paths whose changes trigger the new CI workflow, and whether the workflow runs in a clean container or against the PR's devcontainer image.
- Whether the five mechanisms ship as one PR or as five separate PRs sequenced behind a single feature branch.

## Stakeholder Posture (Preliminary)

- **Feature-pipeline maintainers (the user):** want the named exposures closed so the next feature run cannot recreate the MCP incident's shipping-broken-past-gates pattern.
- **Downstream pipeline users (future feature runs and their sub-agents):** will be gated by the new checks; care that the checks are deterministic, fast, and produce diagnostics they can act on without rerunning the whole pipeline.
- **Codespace users (anyone rebuilding the devcontainer):** care that the new install smoke test fails fast and loud rather than silently producing a half-working environment.
- **Reviewers (the `shared-document-reviewer`, `review-architecture-auditor`, and `review-cross-artifact-auditor` agents):** their output contracts will gain a new structural validation; care that the contract is unambiguous so they don't get rejected for cosmetic mismatches.

## Success Posture (Preliminary)

The user will know this feature is done when: (a) a reviewer that emits `verdict: APPROVED` alongside any blocking finding is automatically rejected before the verdict reaches the orchestrator; (b) a FULL-scope feature run cannot enter dispatch with any stage in single-agent fallback mode; (c) running the MCP audit skill against the current repo surfaces any drift between an ADR-0041-prescribed invocation and the live `.mcp.json` entry as a blocking finding; (d) a fresh devcontainer build runs the GitNexus dry-run and fails with a clear pin-tag-drift message if the env-var contract no longer holds; and (e) a pull request that breaks any `.mcp.json` server's connectivity fails the new CI workflow before merge. Each of the five mechanisms must be exercisable end-to-end and must demonstrably catch its target failure mode.

## Confirmation

This document is generated under auto-mode invocation, seeded by an adopted issue-proposal. The user pre-confirmed the carve-out boundary by promoting the proposal to `status: adopted` and by listing the five mechanisms verbatim in the orchestrator's invocation prompt. The Intent Confirmation Gate that follows this stage will issue a `user_token` and record it in this document's frontmatter before the orchestrator proceeds to PRD Authoring.

## Open Items (Pending PRD Authoring)

- Resolve the reviewer output-validation contract details: which severity tokens are "blocking," and whether the check runs in-agent or as a post-agent gate.
- Specify where the orchestrator's dispatch self-check lives and how it identifies stages configured for single-agent fallback.
- Specify the comparison algorithm for the `.mcp.json` ↔ ADR-0041 parity rule (exact match vs. canonicalized form; normalization rules for env-var indirection).
- Specify the GitNexus dry-run script's exit-code contract and the on-failure diagnostic message.
- Specify the path-trigger set and execution environment for the new CI workflow.
- Decide PR shape: single bundled PR vs. five sequenced PRs on a shared feature branch.
- Confirm that the parallel update to `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` (marking rows H-4 and B-1 as adopted-by this feature) is part of this feature's deliverable archive rather than a separate housekeeping commit.
