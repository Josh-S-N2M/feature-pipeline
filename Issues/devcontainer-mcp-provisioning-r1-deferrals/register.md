---
id: REGISTER-devcontainer-mcp-provisioning-r1-deferrals
doc_type: issue-register
version: 0.1.0
status: open
since: 2026-05-23
generated: 2026-05-23
generated_by: claude (orchestrator) — pre-Gate-4 deferral sweep
feature_slug: devcontainer-mcp-provisioning-r1
scope: feature-specific (registers what THIS feature deferred)
mode: report-only
companion_artifacts:
  - working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md
  - working/feature/devcontainer-mcp-provisioning-r1/cc-design.md
  - working/feature/devcontainer-mcp-provisioning-r1/codespaces-design.md
  - working/feature/devcontainer-mcp-provisioning-r1/research-plan-v3.md
  - adrs/ADR-0037-mcp-events-jsonl-transition-surfacing.md
  - adrs/ADR-0038-codebase-analysis-schema-v1-1-0.md
  - adrs/ADR-0039-credential-redaction-posture.md
  - adrs/ADR-0040-serena-narrowed-always-on.md
  - adrs/ADR-0041-install-mechanism-hybrid.md
  - Issues/analysis-per-agent-design-evaluation-gap.md
---

# Deferral Register — `devcontainer-mcp-provisioning-r1`

## TL;DR

Pre-Gate-4 sweep of every item the feature artifacts mark as **deferred / out-of-scope / Won't-Have / verify-at-execution / known-unknown / kill-criterion-pending / follow-up**. Each row carries: the deferral, the source artifact + line, why it was deferred, what triggers re-examination, and the risk if it's forgotten. Categories below.

**Counts:** 25 distinct deferral items across 11 categories. Zero are blocking Gate 4. Two have explicit kill criteria (ADR-0040 Serena 90-day, NFR-1 cold-cache 2x target). Five are verify-at-execution (resolved by plan-author at task time). Two are meta-feature candidates the user has explicitly chosen not to open yet.

**Pattern observation (added 2026-05-23 at Gate 4 v3 user review)**: see §O — multiple rows here use "post-ship" / "N days post-ship" / "first weeks post-ship" as trigger language, but this project has no shipping event, no calendar, and no review ritual that would fire those triggers. The annotations are honest about *what should happen* but silent about *what causes it to happen*. §O names the pattern and the posture going forward (event-triggers, honest acceptance, or concrete machinery). No feature-scope changes; recorded as a project-wide posture statement.

---

## A. Blueprint Open Items at Gate 4 (non-blocking)

These are recorded in `blueprint-v2.md` §Open Items (lines 1235-1244). OI-1/OI-2/OI-3 are dispositional questions for the user at Gate 4 (resolved this turn: defaults + hard-gate); OI-4/OI-5/OI-6 below carry forward as known-unknowns.

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **A-1 (OI-4)** | Per-agent context-overhead measurement (PRD UI-7 / NFR-4) | `blueprint-v2.md` line 1240 + `prd-v3.md` NFR-4 | Runtime measurement, not design-time. Tool schemas are deferred until invoked (cc-design Principle 1) so the design-time overhead is essentially zero. | Plan-author measures during implementation. If measured overhead breaches PRD NFR-4 threshold, downscoping (conditional activation per server) re-scopes. | Medium — if the overhead is actually intolerable in practice, users feel it on every session start. |
| **A-2 (OI-5)** | ADR-0007 content review post-relocation | `blueprint-v2.md` line 1242 | ADR-0007 v2.2.0 lives in `adrs-migrated/`, not `adrs/`. Relocation needed but content-correctness review is independent of the relocation mechanics. ADR-0038 bumps ADR-0018 schema but doesn't touch ADR-0007. | Plan-author may file separate review-and-update follow-up feature. Independent of this feature shipping. | Low — content is unchanged at v2.2.0; the deferral is operational hygiene, not correctness. |
| **A-3 (OI-6)** | ADR-0040 `design-codespaces` Serena entry vs ADR-0033 stub-filling | `blueprint-v2.md` line 1243 | `design-codespaces` is in the Serena 5-agent allowlist with rationale "may touch `auditing-codespaces/scripts/` if/when the stub becomes real per ADR-0033." The `auditing-codespaces` skill is currently a STUB. | **Explicit kill criterion: if `auditing-codespaces` stub remains unfilled for >90 days post-ship AND `design-codespaces` fires zero Serena tool invocations in that window, an additive amendment ADR removes the entry.** | Low — Serena's always-on cost is minimal (tool schemas deferred); kill criterion is utility-driven, not cost-driven. |

---

## B. PRD v3 Won't-Haves (explicit scope exclusions)

From `prd-v3.md` §Won't Have lines 351-360.

| ID | Item | Source | Why excluded | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **B-1** | **CI smoke-test that asserts `claude mcp list` shows all seven servers connected** | `prd-v3.md` line 353; was v1 FR-7 (P3) reclassified to Won't-Have per I-DR-005 | CI/CD layer is out of scope per Layer Scope. Acceptance is gated by `claude mcp list` + per-server probe + lifecycle health-check output at devcontainer post-build, not by a GitHub Actions job. | If the user later wants automated drift detection for `.mcp.json` or for the KB-mcp-trifecta audit run, it becomes its own feature. | Medium — without CI guard, MCP-config drift can land unnoticed in a PR until a Codespace rebuild surfaces it. |
| **B-2** | Any MCP server beyond the seven named | `prd-v3.md` line 354 (and intent-clarification.md) | Q-derived scope; deliberately closed at Intent Clarification. | A future feature that explicitly proposes an 8th server, with its own intent + PRD cycle. | Low — adding a new server is an additive change, naturally surfaces if needed. |
| **B-3** | Removal/replacement of Claude-hosted MCP servers (on other Claude surfaces) | `prd-v3.md` line 355 | Separate surface; Intent Clarification explicitly preserved them. | Future feature; would require an explicit migration ADR. | Low — orthogonal concern. |
| **B-4** | Changes to pipeline stages, six human gates, or orchestrator topology | `prd-v3.md` line 356 | Orthogonal to MCP provisioning. | Meta-feature (e.g., `agent-roster-design-discipline-r1` is one such candidate; see G-1 below). | Low — bounded by feature scope. |
| **B-5** | Feature work that *consumes* the MCPs (e.g., a pipeline run against a target codebase using the new servers) | `prd-v3.md` line 357 | This feature ships *capability*; *consumption* is a separate feature run. | Any downstream feature that invokes the seven (eight) MCPs against a real codebase. | Low — naturally exercised at first real-world use. |
| **B-6** | Modifications to external codebases the pipeline will later be run against | `prd-v3.md` line 358 | Out-of-repo scope. | Never (out of scope by construction). | None. |

---

## C. Layer Scope deferrals (7 out-of-scope layers)

From `prd-v3.md` Layer Scope (lines 88-96) and `blueprint-v2.md` Layer Scope (lines 79-86). All 7 marked `N/A — out of scope` with rationale.

| Layer | Source | Rationale | Re-examination trigger |
|---|---|---|---|
| Frontend | prd-v3 line 79; blueprint-v2 line 79 | No user-facing UI surface | New feature explicitly activating Frontend layer |
| Backend | prd-v3 line 80; blueprint-v2 line 80 | No service-side logic | New feature explicitly activating Backend layer |
| API | prd-v3 line 81; blueprint-v2 line 81 | No HTTP/GraphQL/RPC contract | New feature explicitly activating API layer |
| Query / Data Access | prd-v3 line 82; blueprint-v2 line 82 | No ORM, query layer | New feature explicitly activating Query layer |
| Database | prd-v3 line 83; blueprint-v2 line 83 | No schema, migrations | New feature explicitly activating Database layer |
| CI/CD (GitHub Actions) | prd-v3 line 84; blueprint-v2 line 84 | Acceptance gated by lifecycle scripts not CI; Won't-Have B-1 reinforces | Future CI smoke-test feature (closes B-1) |
| Infrastructure as Code | prd-v3 line 85; blueprint-v2 line 85 | Terraform MCP reasons about Terraform; does not provision | Feature that provisions cloud infra |

**Forgetting risk:** Low across the board — the layer-out-of-scope rationales are stable, and re-activation requires a fresh PRD pass.

---

## D. Design-stage deferred items (Q-CC-7, plan-author handoffs)

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **D-1 (Q-CC-7)** | Plugin packaging — should the W/H/A trifecta (KB-mcp-platform + KB-mcp-design + auditing-mcp) be plugin-published preemptively for cross-project distribution? | `cc-design.md` line 546 + `blueprint-v2.md` line 726 | Per KB-cc-design Principle 7, plugins are for cross-project distribution. This feature's artifacts are designed plugin-compatible by following trifecta conventions, but no plugin packaging work is done. | A sister project adopting MCP wants one-command install. | Low — artifacts are plugin-compatible-by-construction. |
| **D-2 (I-DR-003)** | Placeholder convention unification: cc-design used `<PIN_TAG>` vs `<TBD-per-ADR-0007-v2.2.0>` in different `.mcp.json` sketch lines | `blueprint-v2.md` line 734 | Discipline is settled — canonical placeholder form going forward is `<PIN_TBD>` across `.mcp.json` and `versions.env`. Plan-author normalizes at task time. | Plan-author's normalization step. | Low — cosmetic; doesn't affect runtime. |
| **D-3 (I-DR-005)** | KB-mcp-platform `pedagogical_sections` justification tightening per ADR-0030 | `blueprint-v2.md` line 735 | Design-cc justifications passed the rules but were more generic than the KB-github-actions-platform precedent. | Plan-author authors KB-mcp-platform (Implementation Plan step 3) with justifications naming the specific OP-rule and anti-pattern per `pedagogical_sections` entry. | Medium — if justifications stay generic, future maintainers may not understand why specific sections exist. |
| **D-4 (I-DR-CS-007)** | Go feature version pin (codespaces-design recommended) | `blueprint-v2.md` line 861 | Recommendation, not blocker. Codespaces-design pinned Node 20 LTS explicitly; Go feature version pin not as tight. | Plan-author selects an explicit Go major at install-script-authoring time. | Low — Go is needed only for actionlint-mcp build; supply-chain risk minor. |
| **D-5 (Q-CS-2)** | Prebuild adoption | `blueprint-v2.md` lines 902, 1151 | Not adopted in this release; postCreate is not captured by prebuilds anyway, so prebuild value is partial today. | If cold-cache rebuild time becomes felt at runtime (NFR-1 ~10 min target sits near upper bound — see I-1 below), a follow-up moves the workspace-agnostic install subset to `onCreateCommand`. | Medium — directly tied to user experience if rebuild times feel slow. |
| **D-6 (AC-FR-8-c partial)** | postAttach surfaces most-recent health-check result vs triggers fresh check beyond a staleness threshold | `blueprint-v2.md` line 294 | Deferred to plan-author as part of UI-10 refinement. | Plan-author defines the staleness threshold + on-demand command shape. | Low — operational detail. |

---

## E. ADR-0040 (Serena) known-unknowns and kill criteria

From `ADR-0040-serena-narrowed-always-on.md` lines 71-76.

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **E-1** | Whether `design-iac` and `design-api` also occasionally touch `auditing-*/scripts/` Python | ADR-0040 line 74 | **No current evidence** that they do. ADR-0040 explicitly tested this hedge during Q-3 closure (`agent-roster-impact-matrix.md`) — still no evidence. | If a future feature surfaces actual evidence of Python audit-script touches by these agents, an additive ADR amendment adds them to the 5-agent Serena allowlist. | Low — the Q-3 closure matrix establishes the current-state evidence baseline; any future ADR amendment will produce its own evidence. |
| **E-2** | Whether Serena's symbol-level operations on a markdown-heavy corpus produce *enough* value to warrant the augmented `auditing-mcp` audit cost | ADR-0040 line 74 | Felt-utility metric — only measurable post-ship. | Post-ship felt-utility review. | Low — see kill criterion below. |
| **E-3** | **Serena 90-day kill criterion** | ADR-0040 line 75 | If Serena fires no tool invocations across the 5 named agents for >90 days post-ship → downscope to `drop_from_always_on` (a future ADR supersedes ADR-0040). | 90 days post-ship, by counting Serena tool invocations across 5 named agents. | Medium — needs to be tracked operationally; the 90-day clock starts at deliverable packaging time. |
| **E-4** | Serena v1.3.0 migration (`base_modes` → `added_modes`) | `blueprint-v2.md` line 1153 + ADR-0040 line 64 | Pinned pre-v1.3.0 to honor the verified breaking change. | Separate follow-up feature reviews `base_modes` → `added_modes` and may then bump the pin. | Medium — Serena evolution may have other improvements; staying pinned has a cost. |

---

## F. Research-stage open questions deferred to Design / Plan Authoring

From `research-plan-v3.md` lines 434-444.

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **F-1 (OQ-2)** | Does augmented `auditing-mcp` (no-BLOCKER) become a *formal* Gate 6 acceptance criterion? | research-plan-v3 line 434 | Was deferred to Design Composition / Plan Authoring gate. **Resolved this Gate 4: HARD GATE.** | Resolved. (Tracked here for completeness; this row is closed.) | None (resolved). |
| **F-2 (OQ-6)** | Operator-visible surfacing of the actual GitNexus → codebase-memory-mcp fallback exercise as a formal Gate 6 acceptance criterion or strongly-recommended check | research-plan-v3 line 442 | The *policy* is settled (PRD-v3 AC-FR-9-d: no silent fallback). What remained open was whether *surfacing of an actual fallback exercise* (distinct from the agent-file expression in UI-15) is a Gate-6 blocker. **Resolved by OI-3 hard-gate decision this turn — auditing-mcp BLOCKER on absence halts Gate 6.** | Resolved. (Tracked here for completeness.) | None (resolved). |

Note: OQ-1 (budget right-sizing), OQ-3 (UI-8 Serena reconfirmation), OQ-4 (in-repo prior-art), OQ-5 (lifecycle hook composition) all resolved during the design stages and are no longer open.

---

## G. Track B meta-features deferred (saved-for-later)

User chose "Save recommendation in memory for later" at Gate 4 for Track B of `Issues/analysis-per-agent-design-evaluation-gap.md`. The recommendation is now in auto-memory at `~/.claude/projects/-workspaces-feature-pipeline/memory/project_agent_design_gap.md`.

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **G-1** | Meta-feature `agent-roster-design-discipline-r1` (B1 mandatory matrix artifact + B3 skill-coverage check + B4 enforce "Blocks X" markers) | `Issues/analysis-per-agent-design-evaluation-gap.md` §6.2 + memory `project_agent_design_gap.md` | User explicitly deferred to a separate future feature run; not in scope here. | Next time the user asks about pipeline improvements OR the next feature touches the agent surface — auto-memory will surface this. | Medium — without the systemic fix, the same defect-shape will recur on the next agent-surface-touching feature; the memory pointer is the only mitigation today. |

---

## H. Verify-at-execution items (plan-author resolves at task time)

These are not design questions — they are operational items the plan-author resolves at install/configuration time. From `cc-design.md` line 521 + `blueprint-v2.md` Fact Disposition rows.

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **H-1** | actionlint-mcp commit SHA at install time (C-0133: no tagged releases as of 2026-05-23) | blueprint-v2 line 127, 410 | No tagged releases exist; plan-author selects a commit SHA at install-script-authoring time. | Plan-author's install-script-authoring step. | Medium — picking a bad SHA leaves the feature on an arbitrary point-in-time; pin reproducibility is operationally critical. |
| **H-2** | Terraform MCP version pin re-confirmation (v0.5.2 selected as of design time) | blueprint-v2 line 411 | Release cadence is active (0.5.0 Apr 1, 0.5.1 Apr 7, 0.5.2 Apr 28). Plan-author re-confirms latest stable. | Plan-author's install-script-authoring step. | Low — versioning is conventional semver; bump is straightforward. |
| **H-3** | mcp-openapi-schema staleness (single release 2025-03-13; 14 months old at design time) | blueprint-v2 line 409 | Pin to 0.0.1; plan-author confirms at install time + flags as supply-chain review item. | Periodic supply-chain review; fork-to-org-mirror if long-term reliance. | Medium — abandoned-vs-stable ambiguity; if abandoned and a security issue surfaces, project is exposed. |
| **H-4** | GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env var smoke-test | cc-design line 521; ADR-0041 | Partially-verified (critic batch 1, medium confidence). Env var name is the load-bearing detail for avoiding C++ toolchain. | Plan must include CI pre-install dry-run smoke test verifying the env var still works on the pinned tag. | High — if env var no longer works on the pinned tag, install fails or requires C++ toolchain (base-image impact). |
| **H-5** | Context7 v1.2.0 ReplaceContentTool / ReplaceRegexTool rename (C-0037) — version-coupled allowlist | blueprint-v2 line 412; cc-design line 213 | Allowlist entries are version-coupled. If Context7 is pinned ≥v1.2.0, the entries must use the new name; plan-author re-validates. | Plan-author's install-script-authoring step. | Medium — wrong allowlist entry means the tool isn't callable from the agent; surfaces at first use. |
| **H-6** | `claude mcp ping` CLI existence in pinned Claude Code Feature version (OI-CS-5) | blueprint-v2 line 125; ADR-0041 | Verify-at-execution; ADR-0041 codifies fallback to direct JSON-RPC if the CLI doesn't exist in the pinned version. | Plan-author's install-script-authoring step. | Low — fallback path is documented. |
| **H-7** | Exa CLI `--header` flag support | research note T-006 OQ-T006-1 | Verify-at-execution; if `--header` doesn't work as documented, Claude Code MCP server config syntax handles the auth surface instead. | Plan-author's install-script-authoring step. | Low — multiple auth paths available. |

All seven are recorded in `blueprint-v2.md` Fact Disposition Table (lines 408-421) as `preserve (with verify-at-execution)` to make plan-author's responsibility explicit.

---

## I. Risk-table items with explicit kill criteria

From `blueprint-v2.md` Risks and Mitigation section (lines 1190-1206).

| ID | Item | Source | Why tracked | Kill criterion | Forgetting risk |
|---|---|---|---|---|---|
| **I-1** | Cold-cache build sits at upper bound of NFR-1 ~10 min target | blueprint-v2 line 1195 | Estimate ~7-12 min per codespaces §Rebuild-Time Estimate. | **Kill at 2× target (PRD Rollout Plan)** — i.e., if cold-cache routinely exceeds ~20 min, prebuild adoption (D-5) is no longer optional. | Medium — felt user experience; needs periodic review. |
| **I-2** | Per-agent context overhead with 8 always-on servers exceeds tolerable envelope across 36 agents (NFR-4) | blueprint-v2 line 1200 | Tool schemas are deferred per cc-design Principle 1, but per-session config-block-load cost is non-zero. | Plan-author measures in implementation; if intolerable, downscoping (conditional activation per server) opens as re-scope. | Medium — same as A-1; this row is the Risks-table mirror of OI-4. |
| **I-3** | ADR-0007 relocation surfaces deferred content questions | blueprint-v2 line 1199 | Relocation is independent of content; v2.2.0 content unchanged. | Standalone follow-up feature (mirrored by A-2). | Low. |

Note: this section overlaps with A (Blueprint Open Items) and H (verify-at-execution) by design — the Risks table is a cross-cut view; rows here may also appear elsewhere with different framing.

---

## J. cc-design / codespaces-design speculative deferrals

| ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk |
|---|---|---|---|---|---|
| **J-1** | `permissions.deny: ["Bash(curl https://mcp.context7.com:*)"]` rule to prevent operators from bypassing the MCP config and calling Context7 directly via curl | cc-design line 256 | Synthesis frames this as out of scope — the MCP servers ARE the canonical surface. | Future security review that wants belt-and-suspenders. | Low — additive change if ever wanted. |
| **J-2** | github-cli devcontainer feature repinning | codespaces-design line 66 | "Preserve current `version: \"latest\"`; not in scope to repin in this feature." | Future hygiene feature for devcontainer pin discipline. | Low. |

---

## K. Tracked but not blocking — kill criteria summary

Two kill criteria are armed and need operational tracking after deliverable packaging:

1. **ADR-0040 Serena 90-day kill** (E-3): zero invocations across 5 named agents → drop_from_always_on ADR.
2. **NFR-1 cold-cache 2× target kill** (I-1): cold-cache routinely exceeds ~20 min → mandate prebuild adoption.

A third weaker tripwire (E-2 Serena felt-utility on markdown-heavy corpus) has no formal kill criterion but is meant for periodic review.

---

## L. Forgetting-risk summary by category

| Category | High | Medium | Low | None | Total |
|---|---|---|---|---|---|
| A. Blueprint Open Items | 0 | 1 | 2 | 0 | 3 |
| B. PRD Won't-Haves | 0 | 1 | 4 | 1 | 6 |
| C. Layer Scope deferrals | 0 | 0 | 7 | 0 | 7 |
| D. Design-stage deferred | 0 | 2 | 4 | 0 | 6 |
| E. ADR-0040 known-unknowns | 0 | 2 | 1 | 0 | 3 |
| F. Research OQ resolved at Gate 4 | 0 | 0 | 0 | 2 | 2 |
| G. Track B meta-features | 0 | 1 | 0 | 0 | 1 |
| H. Verify-at-execution | 1 | 3 | 3 | 0 | 7 |
| I. Risk-table | 0 | 2 | 1 | 0 | 3 |
| J. Speculative deferrals | 0 | 0 | 2 | 0 | 2 |
| **Total** | **1** | **12** | **24** | **3** | **40** |

(Total > 25 because some rows appear in multiple cross-cut categories; the 25-distinct count is the unique-item count, not the row count above.)

**The single HIGH forgetting-risk item is H-4 (GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` smoke-test).** Plan-author must wire the CI pre-install smoke-test verifying this env var still works on the pinned tag; without it, an upstream change to GitNexus could silently break the install path.

---

## M. Recommended follow-up actions

1. **Plan-author** (Stage 9): inherits responsibility for H-1..H-7 verify-at-execution items + D-1..D-6 design-stage deferrals. The Plan should have a "Pre-install Verification Tasks" phase that runs H-1..H-7 before any task is marked complete.
2. **Phase-validator-author** (Stage 10): wires OI-3 hard-gate decision into the Gate-6 phase validators — any auditing-mcp BLOCKER halts.
3. **Post-ship operational** (after Gate 6): track the two armed kill criteria (E-3 90-day Serena utility; I-1 cold-cache 2× target). **CAVEAT: see §O below — "post-ship" triggers in this project have no firing mechanism today. The kill criteria are documented but unmonitored.**
4. **Memory pointer** (already in place): `~/.claude/projects/-workspaces-feature-pipeline/memory/project_agent_design_gap.md` will surface G-1 when relevant.
5. **Independent of this feature**: when next user reviews pipeline improvements, raise meta-feature `agent-roster-design-discipline-r1` (per G-1 + `Issues/analysis-per-agent-design-evaluation-gap.md`).

---

## O. Pattern observation — "post-ship" / time-based triggers are unreliable in this project

**Surfaced at Gate 4 v3 user review** (verbatim: *"i do not like annotating things like 90 day post ship. what does this even mean? how does that even help you ... me ... or anyone? it is just noise and will get lost"*). The user is correct, and the observation generalizes beyond OI-6.

### O.1 The pattern

Multiple rows in this register cite "post-ship," "N days post-ship," "first weeks post-ship," "post-ship felt-utility review," or similar time-anchored triggers. The rows are:

| Row | Trigger as-written | What "post-ship" means here today |
|---|---|---|
| **A-3 (OI-6)** | ">90 days post-ship AND zero Serena invocations from design-codespaces → remove entry" | Undefined. No shipping event; no day-0 anchor; no calendar; no audit hook counts invocations. |
| **D-5 (Q-CS-2)** | "if cold-cache rebuild routinely exceeds ~10 min in operator usage" | "If someone notices" — but no operator-feedback channel is defined. |
| **E-2** | "post-ship felt-utility review" of Serena value on markdown-heavy corpus | No felt-utility review ritual is defined. |
| **E-3** | "90 days post-ship, by counting Serena tool invocations across 5 named agents" | No counter exists; no day-0; no review ritual. |
| **I-1** | "if cold-cache routinely exceeds ~20 min, mandate prebuild adoption" | Same shape as D-5 — felt-by-operator with no defined feedback path. |

### O.2 Why this fails as a tracking mechanism

For a time-based or "felt-by-operator" trigger to fire, the project needs at least **one** of:
- A defined **ship date** (day-0 anchor) → this project produces design artifacts; "ship" is undefined.
- A **calendar / reminder system** that surfaces the item at the trigger date → none exists.
- An **audit hook or scheduled check** that fires automatically → none exists; the closest analogue (the augmented `auditing-mcp` audit) is operator-invoked at PR time, not time-scheduled.
- A **routine review ritual** (post-ship retrospective, quarterly review, etc.) → none defined.
- A **felt-operator-feedback channel** with a stated owner → none defined.

Without any of these, the trigger never fires. The annotation degrades to **deferred work with no owner and no firing condition** — exactly the failure mode the user flagged.

### O.3 Posture going forward

When a future feature is tempted to write a deferral with a time-based or "post-ship" trigger, use one of these instead:

1. **Event-trigger**: tie the re-examination to an observable event already in the system. Examples:
   - "If/when the `auditing-codespaces` stub is filled, the implementer re-evaluates ADR-0040's design-codespaces Serena entry as part of that work" — natural because filling the stub touches ADR-0033's siblings and ADR-0040 sits in that blast radius.
   - "If the augmented `auditing-mcp` audit flags ___ for two consecutive feature runs, open a follow-up" — the audit is the existing event; cumulative-fires is the trigger.
   - "If a feature consuming the MCPs reports rebuild-time complaints, open a prebuild-adoption feature" — the consuming feature is the trigger.
2. **Honest acceptance**: write down "we accept this cost; the entry is additive and cheap; no tracking" and stop tracking it. (Most of the §O.1 rows would close cleanly under this.)
3. **Concrete machinery**: if the item is load-bearing enough to deserve real tracking, propose the machinery as its own feature (e.g., a hook that fires on first `mcp-events.jsonl` write per session, an audit module that counts Serena invocations across runs). Don't write the trigger as an annotation in a deferral register — annotations don't fire.

### O.4 Why this is captured here (not as a separate Issue)

This register is the canonical place where the project tracks deferred items for this feature; the pattern observation is most useful **adjacent to the rows it critiques.** A separate `Issues/proposal-trigger-discipline.md` was considered and rejected — it would re-create the same forgetting-risk it's trying to fix. By living inside the register, §O is co-located with the rows that would otherwise propagate the pattern.

### O.5 Scope decision for THIS feature

Per user direction at Gate 4 v3 review: **no changes to the feature scope.** Blueprint v3 keeps the "90 days post-ship" phrasing in OI-6 and the Risks-table cold-cache row verbatim. The pattern observation is captured here as the project's posture going forward; future features adopt it, this feature ships as-designed.

### O.6 Rows in this register that would close cleanly under O.3 option 2 ("honest acceptance")

If a future cleanup pass wants to act on §O.3:
- **A-3 / OI-6** — the entry is additive; cost is one allowlist line. Accept.
- **E-2** — felt-utility on a markdown-heavy corpus is unfalsifiable at design time; if Serena is broadly useful or broadly unused, the natural signal is invocation patterns in `mcp-events.jsonl` (which the feature does instrument) — that becomes the event trigger, not a calendar.
- **E-3** — same as E-2; the kill criterion already names the metric (invocation count); the only missing piece is the firing event, which becomes "next feature run that touches ADR-0040's blast radius."

D-5 and I-1 are stickier — they describe a genuine user-experience risk where operator-felt-feedback is the only honest signal. For those, "honest acceptance" reads as "we don't yet have a feedback channel; if it bites, the bite is itself the trigger." That's fine — name it that way.

---

## N. Cross-references

- Sibling issue analysis: `Issues/analysis-adr-placement-rootcause.md`
- Sibling issue analysis: `Issues/analysis-per-agent-design-evaluation-gap.md`
- This feature's canonical artifacts (all in `working/feature/devcontainer-mcp-provisioning-r1/`): `prd-v3.md`, `blueprint-v2.md`, `cc-design.md`, `codespaces-design.md`, `agent-roster-impact-matrix.md`, `adrs/ADR-0037..ADR-0041`
- Auto-memory: `~/.claude/projects/-workspaces-feature-pipeline/memory/project_agent_design_gap.md`

---

*End of register. Report-only. Captured pre-Gate-4 per user direction so nothing we punted on gets lost in the shuffle.*
