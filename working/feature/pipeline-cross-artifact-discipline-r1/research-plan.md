---
id: RP-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: draft
doc_type: research-plan
feature_slug: pipeline-cross-artifact-discipline-r1
derived_from: working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md
generated: 2026-05-26T13:25:00Z
generated_by: discovery-plan-author
---

# Research Plan: Cross-Artifact + Design-Time Discipline (R2)

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

---

## Feature reference

- **Feature slug**: `pipeline-cross-artifact-discipline-r1`
- **PRD path**: `working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md`
- **PRD version**: `2.0.0`
- **PRD gate state**: approved (PRD Approval Gate; v2 patch in response to I-DR-001..007)
- **Intent Clarification path**: `working/feature/pipeline-cross-artifact-discipline-r1/intent-clarification.md`
- **Inherited ADRs in scope**:
  - **ADR-0007** — GitNexus primary / codebase-memory-mcp fallback (blast-radius backbone for FR-1's audit pass).
  - **ADR-0009** — rationale brief / brief-honor (FR-1's brief-honor cross-check on ADR prescription).
  - **ADR-0011** — template consolidation (Blueprint, ADR template touched by FR-1's machinery — companion-file option in OI-A1).
  - **ADR-0016** — Design fan-out (FR-6 attaches a mandatory artifact at the `design-cc` lane).
  - **ADR-0017** — `shared-document-reviewer` at 5 invocation points (FR-6's matrix becomes a reviewable artifact; affects Blueprint Gate 0).
  - **ADR-0018, ADR-0038** — `codebase-analysis.json` schema v1.1.0 (FR-2 adds §Protocol Conformance to discovery output; schema extension).
  - **ADR-0020** — KB consolidation (FR-8 edits KB-cc-design Principle 9; FR-11 edits multiple discipline texts).
  - **ADR-0021** — KB-and-ADR-first; Discovery refactor (this artifact's authoring discipline).
  - **ADR-0027** — `cwd == repo-root` precondition (FR-4 / FR-5 live handshake must respect; orchestrator state).
  - **ADR-0033** — D-12 symmetric application (informs how the §O posture text propagates uniformly through KB-cc-design and PV-author rubric per FR-11).
  - **ADR-0036, ADR-0054, ADR-0056** — canonical ADR placement (FR-1's prescription-extraction needs a stable ADR locus; no carve-outs per ADR-0056 — H3 must apply uniformly).
  - **ADR-0037** — `mcp-events.jsonl` (FR-4 / FR-5 may emit transition events; FR-9 Blocks-X markers may write transition entries).
  - **ADR-0039** — credential indirection (NFR-6 — no leakage from reachability or drift findings).
  - **ADR-0040** — Serena narrowed allowlist (FR-5's allowlist-aware tool-surface drift uses this as the canonical referent).
  - **ADR-0041** — install-mechanism-hybrid (the canonical example of the design-realization gap FR-1 closes; the prescription FR-1 must mechanically verify).
  - **ADR-0042** — `auditing-mcp` graduated family (FR-4 / FR-5 land in this family; rename happens here).
  - **ADR-0044** — execution flatten / specialist-dispatch; `state-transitions.log` schema (FR-9 records Blocks-X marker transitions here).
  - **ADR-0045** — no Agent tool in sub-agents (FR-1's audit dimension lives inside `review-architecture-auditor`, no spawn-out).
  - **ADR-0049** — structural-vs-discipline KB split (FR-7 skill-coverage decisions are a discipline concern; structural template lives in KB-documentation-criteria).
- **Applicable KBs** (those whose principles or patterns touch the feature's layer scope):
  - `KB-cc-design` — design discipline for Claude Code surface; Principle 9 is the FR-8 target.
  - `KB-cc-platform` — what Claude Code primitives (agents, skills, hooks, MCP, settings) actually do; the substrate FR-4 / FR-5 / FR-6 act on.
  - `KB-mcp-platform` — MCP transport surface; ground truth for FR-4 (reachability handshake) and FR-5 (`tools/list` drift).
  - `KB-mcp-design` — MCP design discipline and OP-1..OP-10 catalog; affects FR-5 drift-detection design and NFR-6 credential redaction posture.
  - `KB-codebase-research` — `codebase-analysis.json` schema; the FR-2 §Protocol Conformance subsection extends this schema's output contract.
  - `KB-review-disciplines` — CoVe + blast-radius + brief-honor; FR-1's design-realization dimension extends this discipline.
  - `KB-task-decomposition` — phase decomposition; FR-3 PV-tier cross-file invariants attach to PV authoring inside this KB's surface.
  - `KB-documentation-criteria` — templates and shared conventions; FR-6 introduces a new mandatory artifact template; FR-7 introduces a Skill-Coverage Decisions section.
  - `recipe-feature-pipeline` — the 13-stage state machine; FR-6 and FR-9 attach new stage-transition gates.
  - `auditing-mcp` — FR-4 / FR-5 land here.
  - `auditing-subagents` — FR-10 (feature-touch-coverage rule) lands here.
  - `auditing-skills` — OI-A3 (reverse-check) target; carried as Blueprint Open Question.
  - `auditing-shared` — `audit-issues.json` schema; severity vocabulary used by FR-1 / FR-4 / FR-5 / FR-9 / FR-10 findings.

## Information needs inventory

Every downstream stage (Synthesis, per-layer Design, Plan, Tests, PV authoring) reads upstream artifacts to make decisions. The Research Plan inventories the information those stages will need. Per ADR-0021, each need carries a disposition.

The PRD-v2 is unusually well-mapped: it already names the in-scope agents, skills, ADRs, and surfaces, and has resolved many product-policy questions (OI-A1..OI-A6 are deferred to Synthesis/Design with explicit owners). Most Discovery work is therefore **codebase-topic** with a small, sharply-scoped external slice.

### IN-001 — Current contract of `review-architecture-auditor`

- **Description**: What input/output schema, audit dimensions, and contract does `review-architecture-auditor` currently expose, and where would an additive "design-realization audit dimension" attach (FR-1)?
- **Downstream consumer(s)**: `synthesize-*` (frames the FR-1 mechanism), `design-cc` (designs the auditor extension), `design-composer` (composes the audit-dimension contract).
- **Disposition**: `codebase-topic`
- **Justification**: Answer is "what does our codebase currently do?" — agent contract lives in `.claude/agents/review-architecture-auditor.md`; the discipline lives in `KB-review-disciplines/references/architecture-audit.md`. Routed to `discovery-codebase-researcher`.

### IN-002 — `audit-issues.json` schema and severity vocabulary

- **Description**: What does the auditor's findings JSON look like today (schema, severity values, required fields), and can it absorb FR-1's `design-realization` finding type, FR-4's per-server `reachable / unreachable / transport-error` result, and FR-5's BLOCKER/MAJOR drift severities with the `rule / target / divergence / next_action` fields NFR-8 prescribes?
- **Downstream consumer(s)**: `design-cc` (FR-1, FR-4, FR-5 extensions), `design-composer` (NFR-8 finding shape).
- **Disposition**: `codebase-topic`
- **Justification**: Schema is in `auditing-shared` (per ADR-0031, ADR-0035) and consumed by the architecture auditor; `discovery-codebase-researcher` enumerates the current fields and severity strings.

### IN-003 — `codebase-analysis.json` v1.1.0 schema and external-interface discovery surface

- **Description**: What does `discovery-codebase-researcher` produce today (per ADR-0018, ADR-0038), how does it currently discover external interfaces (MCP servers, external services, CLIs, third-party APIs), and where does the FR-2 §Protocol Conformance subsection attach?
- **Downstream consumer(s)**: `design-cc` (FR-2 extension), `design-composer` (composes the new subsection into the analysis output).
- **Disposition**: `codebase-topic`
- **Justification**: Schema and discovery surface live in `.claude/skills/KB-codebase-research/` and `.claude/agents/discovery-codebase-researcher.md`. Codebase fact.

### IN-004 — `recipe-feature-pipeline` 13-stage state machine, `shared-document-reviewer` 5 invocation points, and Blocks-X marker locations

- **Description**: What is the current state machine, where are the 5 `shared-document-reviewer` invocation points (per ADR-0017), where would FR-6's Design Composition block attach, and where would FR-9's Blocks-X enforcement gate attach? Where (if anywhere) do "Blocks <stage>" markers currently appear in discovery outputs?
- **Downstream consumer(s)**: `design-cc` (FR-6, FR-9 gate placements), `design-composer` (state-machine integration), `synthesize-*` (FR-9 grammar — feeds OI-A5).
- **Disposition**: `codebase-topic`
- **Justification**: State machine is in `recipe-feature-pipeline/SKILL.md`; gate locations are mechanical to enumerate. The Blocks-X marker grammar (OI-A5) requires a survey of recent `working/feature/*/codebase-analysis*` outputs — codebase fact, not external research. Routed to `discovery-codebase-researcher`.

### IN-005 — `design-cc` agent's current contract and artifact set

- **Description**: What does `design-cc` currently consume / produce, what skills does it load via `skills:` frontmatter, and where would the new mandatory `agent-roster-impact-matrix.md` artifact attach (FR-6)?
- **Downstream consumer(s)**: `design-cc` self (the matrix becomes its deliverable), `design-composer` (composition gate), `auditing-subagents` (FR-10 backstop).
- **Disposition**: `codebase-topic`
- **Justification**: Agent prompt body and frontmatter — direct file read by `discovery-codebase-researcher`.

### IN-006 — KB-cc-design Principle 9 current text and cross-reference targets

- **Description**: What is the verbatim current text of KB-cc-design Principle 9 (the FR-8 edit target), what cross-references does it carry, and what other principles / patterns will the active-vs-defensive rewording need to align with?
- **Downstream consumer(s)**: `design-cc` (FR-8 edit), `design-composer` (composition integrity).
- **Disposition**: `codebase-topic`
- **Justification**: Principle 9 lives in `.claude/skills/KB-cc-design/references/principles.md` (confirmed at line 182). Direct file read.

### IN-007 — `auditing-subagents` skill's current check inventory and rule-attachment points

- **Description**: What does `auditing-subagents` check today, what is the rule-attachment shape (Python script? Discipline text?), and where would the new "missing agent-roster matrix before deliverable packaging" rule (FR-10) attach?
- **Downstream consumer(s)**: `design-cc` (FR-10 rule design), `design-composer` (rule-set composition).
- **Disposition**: `codebase-topic`
- **Justification**: Skill body lives in `.claude/skills/auditing-subagents/`. Codebase fact.

### IN-008 — `auditing-mcp` current `--with-runtime` semantics, OP-1..OP-10 rules, and rename / reachability impact

- **Description**: What does `--with-runtime` currently do (per the SKILL.md it spawns servers, sends `tools/list`, scans descriptions, shuts down), where are OP-1..OP-10 enumerated, and what call sites use `--with-runtime` today (the FR-4-d "fail loudly on legacy flag" check needs the enumeration)? Where do OP-9 / OP-10 reference ADR-0039 credential indirection?
- **Downstream consumer(s)**: `design-cc` (FR-4 rename, FR-5 drift), `design-composer` (auditing-mcp contract update).
- **Disposition**: `codebase-topic`
- **Justification**: Skill body and its `scripts/audit_mcp.py` runner are in `.claude/skills/auditing-mcp/`; call sites are mechanically enumerable via grep across `.claude/`, `Issues/`, `working/feature/`, CI workflows.

### IN-009 — PV-author rubric current text and cross-file invariant attachment point

- **Description**: What does the PV-author rubric currently prompt the author for, and where does the new cross-file consistency invariant catalog prompt (FR-3) attach?
- **Downstream consumer(s)**: `design-cc` (FR-3 rubric edit), PV-author (downstream consumer).
- **Disposition**: `codebase-topic`
- **Justification**: PV-author rubric lives in `.claude/skills/KB-task-decomposition/` (per ADR-0020). Codebase fact.

### IN-010 — `devcontainer-mcp-provisioning-r1-deferrals/register.md` §O posture: the four rows and the §O.5 user direction

- **Description**: What is the exact text of the four §O.1 rows (E-3, A-3, D-5, I-1), the §O.3 going-forward framings, and the §O.5 user direction quoted verbatim? The PRD's AC-FR-11-c is testable by grep against verbatim content — Discovery must record the verbatim baseline.
- **Downstream consumer(s)**: `design-cc` (FR-11 discipline-text edits), `design-composer` (AC testability anchor).
- **Disposition**: `codebase-topic`
- **Justification**: Register lives at `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`. Direct file read.

### IN-011 — ADR placement validator (per ADR-0054, ADR-0056) and prescription-locus stability

- **Description**: How does the ADR-placement validator work today, where do ADRs live canonically (`adrs/`), and does the validator already provide a stable locus FR-1's prescription extractor can rely on? Relevant to OI-A1 (machine-checkable companion file vs NLP parse).
- **Downstream consumer(s)**: `design-cc` (OI-A1 design path), `design-composer` (FR-1 contract).
- **Disposition**: `codebase-topic`
- **Justification**: Validator and conventions live under `.claude/` and `adrs/`. Codebase fact. Also covered partly by `covered-by-ADR:ADR-0054, ADR-0056` for the placement rule itself.

### IN-012 — Three source Issue directories: evidence, analyses, framings

- **Description**: What is the exact framing of H1, H3, H6, H8, H9, B1..B5, and §O in their source Issue analyses and evidence subdirectories? Per the PRD's Appendix, these are the load-bearing inputs. Discovery must surface any additional constraints or sub-decisions the PRD condensed but Synthesis will need.
- **Downstream consumer(s)**: `synthesize-*` (frames the H/B/§O mechanisms), `design-cc`, `design-composer`.
- **Disposition**: `codebase-topic`
- **Justification**: Issue dirs are local files under `Issues/`. Codebase fact.

### IN-013 — `state-transitions.log` schema (per ADR-0044) and `dispatch_directives[]` Contract 6 indirection

- **Description**: What is the `state-transitions.log` schema today, where are entries written, and how does FR-9's Blocks-X marker transition (`resolved` / `deferred-with-OI` / `false-positive`) compose with the existing schema? Does the FR-9 transition need a new event type or does an existing one fit?
- **Downstream consumer(s)**: `design-cc` (FR-9 mechanism design), `design-composer` (orchestrator integration).
- **Disposition**: `codebase-topic`
- **Justification**: Schema is documented in KB-documentation-criteria templates and in the auditing-shared helper. Codebase fact.

### IN-014 — Mechanism dependencies among the 11 FRs (for the R2a/R2b contingency split)

- **Description**: Which FRs share machinery, share files, share gate locations, or depend on a common OI's resolution? `design-composer` applies the Contingency Split threshold mechanically (PRD's `Contingency Split` section) — it needs a dependency graph to apply the split cleanly if the threshold trips.
- **Downstream consumer(s)**: `design-composer` (Contingency Split application at the Design Composition Gate).
- **Disposition**: `codebase-topic`
- **Justification**: Dependency is derivable from current agent / skill / KB surfaces. Routed to `discovery-codebase-researcher` with an explicit reporting requirement (see Codebase scope below).

### IN-015 — Current `.claude/agents/*.md` inventory count (for FR-6 row-count AC)

- **Description**: What is the current count of `.claude/agents/*.md` files at the time of Discovery, and what are their names? FR-6's row count must equal this at authoring time; A-4 in the PRD assumes it's mechanically enumerable.
- **Downstream consumer(s)**: `design-cc` (FR-6 matrix authoring scaffold), `auditing-subagents` (FR-10 row-count check).
- **Disposition**: `codebase-topic`
- **Justification**: `ls .claude/agents/*.md` — trivial codebase fact.

### IN-016 — Six MCP server entries in `.mcp.json` and their tool surfaces (FR-4 / FR-5 baseline)

- **Description**: What are the six MCP server entries in `.mcp.json` (post 2026-05-24 `mcp-openapi-schema` removal), what is each server's transport, and what is each server's current tool surface (baseline for FR-5 drift detection)?
- **Downstream consumer(s)**: `design-cc` (FR-5 baseline shape), `design-composer` (FR-4 / FR-5 contract).
- **Disposition**: `codebase-topic`
- **Justification**: `.mcp.json` is in repo root. Codebase fact.

### IN-017 — MCP transport reachability probe: is there a stable `claude mcp ping`, `initialize`/`tools/list` call, or equivalent in the pinned Claude Code Feature version (PRD A-2)?

- **Description**: What reachability probe does the current Claude Code Feature version expose? Is `claude mcp ping` available? Is a direct JSON-RPC `initialize` / `tools/list` reachable from a Python runner? Does KB-mcp-platform document this protocol-level probe?
- **Downstream consumer(s)**: `design-cc` (FR-4 mechanism), `design-composer` (FR-4 contract; NFR-2 per-server timeout).
- **Disposition**: `covered-by-KB:KB-mcp-platform:references/mcp-events-jsonl.md AND codebase-topic` (split)
  - The protocol-level facts (initialize / list-tools / shutdown sequence; what counts as "reachable") are covered by KB-mcp-platform — the KB exists to document exactly this protocol surface, and `references/mcp-events-jsonl.md` covers transport-level event semantics.
  - Whether the pinned Claude Code Feature version exposes a `claude mcp ping` CLI command (or equivalent affordance) is a codebase / environment fact — `discovery-codebase-researcher` checks the pinned version's CLI surface.
- **Justification**: This is a positive disposition split — protocol semantics are KB; CLI affordance availability is codebase. NOT external research because KB-mcp-platform is the canonical project KB for the MCP transport surface (loaded by `discovery-external-researcher` for context7 / exa work).

### IN-018 — Drift-detection algorithm patterns and false-positive normalization (NFR-4 < 5% target)

- **Description**: What normalization rules suffice to keep drift-detection false positives < 5% across 50 audits against a stable server set? The PRD notes whitespace + description-only changes shall be normalized; signature changes shall not. What's the prior art for `tools/list` JSON-document drift comparison?
- **Downstream consumer(s)**: `design-cc` (FR-5 algorithm), `design-composer` (NFR-4 calibration).
- **Disposition**: `external-research-topic:T-001` (drift-detection prior art) + `covered-by-KB:KB-mcp-design` (the OP-1..OP-10 catalog covers the design-rule scaffolding; the empirical false-positive-rate engineering for the JSON-document diff is the gap).
- **Justification (external)**: KB-mcp-design names tool-surface stability as a design concern (OP-rule catalog) but does NOT cover the empirical engineering of low-false-positive JSON drift detection. KB-mcp-platform covers the protocol shape, not the diff algorithm. This is not `designer-general-knowledge` because the < 5% false-positive target across 50 audits is a measurable engineering constraint, not a conventional default — the designer needs sourced approaches (e.g., schema-diffing libraries, semver-aware tool comparison, normalization-rule catalogs from API-contract-drift tooling) rather than general intuition.

### IN-019 — Design-realization audit prior art (OI-A1's "machine-checkable companion file vs NLP parse" tension)

- **Description**: How do other dev systems verify that as-built matches as-designed? Specifically: ADR-style decision artifacts that ship machine-checkable companions (YAML, JSON-schema) vs. those that rely on natural-language parsing — what's the prior art that informs the OI-A1 resolution?
- **Downstream consumer(s)**: `design-composer` (OI-A1 resolution at the Design Composition Gate), `design-cc` (FR-1 mechanism).
- **Disposition**: `external-research-topic:T-002`
- **Justification (external)**: No project KB covers ADR-companion-file vs NLP-parse design patterns. KB-cc-design is about Claude Code agent / skill / MCP surface design, not ADR machinery. KB-documentation-criteria provides the ADR template but does not cover machine-checkability extensions. This is not `designer-general-knowledge` because the trade-off (authoring burden of companion files vs. fragility of NLP parsing) requires sourced examples from systems that have tried both — not a conventional default. The OI-A1 resolution is FR-1's testability hinge per AC-FR-1-c.

### IN-020 — Skill-coverage / capability-fitness rubric patterns (FR-7 W/H/A trifecta)

- **Description**: What's the prior art for capability-coverage analyses in agent platforms — LangGraph, AutoGen, AutoGPT, OpenAI Assistants? Is the W/H/A trifecta (Why / How / Anti-patterns) novel, or is there a community pattern the design should align with?
- **Downstream consumer(s)**: `synthesize-*` (FR-7 framing), `design-cc` (skill-coverage section template), `design-composer` (Skill-Coverage Decisions section structure).
- **Disposition**: `external-research-topic:T-003`
- **Justification (external)**: No project KB covers cross-platform agent-capability frames. KB-cc-design covers Claude-Code-specific skill design (Principle 2 — skill loading on-demand); it does not survey alternative frameworks' patterns for new-concept-to-capability mapping. This is not `designer-general-knowledge` because the W/H/A trifecta is a non-obvious specific shape — a designer would need sourced precedent (or its absence) to commit. Specifically, the research should answer: do other agent platforms ship a comparable decision-frame artifact at design time, and what do they require?

### IN-021 — Cross-file invariant catalog patterns in DevOps/IaC tooling (FR-3 / OI-A2)

- **Description**: How do other systems catalog cross-file invariants — Terraform's plan-time invariant validations, OpenAPI's schema-consistency invariants, dbt's schema tests, contract-testing tooling? Informs OI-A2's "denormalized per-PV vs centralized `cross-file-invariants.md`" tension.
- **Downstream consumer(s)**: `design-composer` (OI-A2 resolution), `design-cc` (PV-author rubric extension shape).
- **Disposition**: `external-research-topic:T-004`
- **Justification (external)**: KB-iac-design covers IaC-specific patterns but is out-of-scope (Layer Scope = Claude Code only). KB-task-decomposition covers PV authoring discipline but does not survey cross-file invariant catalog patterns outside the project. This is not `designer-general-knowledge` because the normalized vs denormalized trade-off is a real architectural decision with sourced precedent on both sides (Terraform leans normalized via providers; OpenAPI leans denormalized per file). The designer needs the precedent to choose intentionally.

### IN-022 — Event-triggered vs time-triggered deferral patterns (FR-11 / §O posture)

- **Description**: What's the engineering-discipline literature on "kill criteria" formats — event-triggered framings, honest-acceptance framings, concrete-machinery framings? The PRD lifts the §O posture into discipline texts; the three permitted framings need a literature-anchored vocabulary.
- **Downstream consumer(s)**: `design-cc` (FR-11 discipline-text edits across KB-cc-design, deferral conventions, PV-author rubric), `design-composer` (FR-11 composition).
- **Disposition**: `designer-general-knowledge`
- **Justification**: This is widely-documented engineering-discipline material (e.g., Lean Startup pivot/persevere criteria, SRE error budget triggers, Toyota Production System "kill the line" triggers). A competent designer can apply the three permitted framings (event-trigger / honest-acceptance / concrete-machinery) with explicit rationale documented in their design subsection. The PRD has already specified the three permitted framings; Discovery does not need to source-validate them.

### IN-023 — Live MCP reachability handshake mechanics across implementations

- **Description**: What's the protocol-level shape of the MCP `initialize` + `tools/list` handshake across stdio / HTTP / SSE transports, and how do operators in the wild implement reachability probes (timeouts, retries, transport-error classification)?
- **Downstream consumer(s)**: `design-cc` (FR-4 handshake design), `design-composer` (NFR-2 timeout calibration).
- **Disposition**: `covered-by-KB:KB-mcp-platform`
- **Justification**: KB-mcp-platform is the canonical project KB for MCP transport mechanics. The handshake sequence (initialize / list-tools / shutdown) and the per-server transport differences are exactly what this KB covers. Discovery checks the KB and the pinned version's CLI; no external research warranted because the KB is well-developed (loaded by `discovery-external-researcher` already and consulted by every MCP-touching designer).

### IN-024 — Tool-surface drift detection design considerations (signature comparison, schema diff, removal vs addition severity)

- **Description**: What design considerations should the FR-5 drift detector incorporate beyond the false-positive engineering (IN-018)? Specifically: schema-diff approaches (semver-aware, structural-equality, JSON-Patch), severity-mapping conventions (removal of allowlisted tool = BLOCKER, addition = MAJOR, signature change of allowlisted = MAJOR), and baseline-storage conventions.
- **Downstream consumer(s)**: `design-cc` (FR-5 algorithm shape), `design-composer` (FR-5 contract).
- **Disposition**: `covered-by-KB:KB-mcp-design AND external-research-topic:T-001` (shared with IN-018)
- **Justification**: KB-mcp-design's OP-1..OP-10 catalog covers the design-rule scaffolding (which severity for which event class). The empirical engineering (schema-diff algorithm choice; baseline-storage scheme) is shared with T-001's false-positive engineering — Discovery consolidates into one external topic rather than spawning a second.

---

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. Output: `codebase-analysis.json` per ADR-0018 / ADR-0038, augmented with the FR-2 §Protocol Conformance subsection IF the researcher elects to dogfood the new contract (recommended but not required for this run — the §Protocol Conformance contract is not yet shipped).

### Touch points

Drawn from the PRD's Layer Scope (Claude Code only) + Technical Considerations § Dependencies + the 11 named mechanisms. Each touch point names the file or directory and why it is in scope.

- `.claude/agents/review-architecture-auditor.md` — FR-1 audit-dimension attachment; IN-001.
- `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — FR-1 discipline extension; IN-001.
- `.claude/skills/auditing-shared/` — `audit-issues.json` schema, severity vocabulary; IN-002.
- `.claude/agents/discovery-codebase-researcher.md` — FR-2 §Protocol Conformance attachment; IN-003.
- `.claude/skills/KB-codebase-research/` — `codebase-analysis.json` v1.1.0 schema (per ADR-0018, ADR-0038); IN-003.
- `.claude/skills/recipe-feature-pipeline/SKILL.md` — 13-stage state machine, 5 reviewer invocation points, Blocks-X marker enforcement; IN-004.
- `.claude/agents/design-cc.md` — FR-6 mandatory artifact attachment; IN-005.
- `.claude/skills/KB-cc-design/references/principles.md` (line ~182 — Principle 9) — FR-8 active-vs-defensive edit; IN-006.
- `.claude/skills/KB-cc-design/references/patterns-and-anti-patterns.md` — cross-reference target for FR-8's edit; IN-006.
- `.claude/skills/auditing-subagents/` (full skill body) — FR-10 rule attachment; IN-007.
- `.claude/skills/auditing-mcp/SKILL.md` + `.claude/skills/auditing-mcp/scripts/audit_mcp.py` — FR-4 rename, FR-5 drift; IN-008.
- `.claude/skills/auditing-mcp/references/` (mcp-spec, toxic-combinations, anti-patterns, common-failures) — OP-1..OP-10 enumeration; IN-008.
- `.claude/skills/KB-task-decomposition/` (PV-author rubric files) — FR-3 cross-file invariant prompt; IN-009.
- `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` (§O.1, §O.3, §O.5) — FR-11 baseline; IN-010.
- `adrs/ADR-0054-canonical-helper-three-surface-enforcement-pattern.md`, `adrs/ADR-0056-no-carve-outs-in-canonical-placement.md`, `adrs/ADR-0036-single-location-adr-placement.md` — FR-1 prescription-locus stability; IN-011.
- `Issues/cross-artifact-divergence-detection-gap/analysis.md`, `proposal.md`, `evidence/` — H1/H3/H6/H8/H9 framings; IN-012.
- `Issues/per-agent-design-evaluation-gap/analysis.md` — B1/B2/B3/B4/B5 framings; IN-012.
- `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` — schema for FR-9 marker transitions; IN-013.
- `.claude/agents/*.md` (full inventory) — count for FR-6 / FR-10; IN-015.
- `.mcp.json` — six server entries for FR-4 / FR-5 baseline; IN-016.
- `.devcontainer/postCreate.sh`, `.devcontainer/postStart.sh` — install-mechanism context, the ADR-0041 prescription FR-1 must verify; IN-008, IN-011.
- `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` — the retroactive Track-A2 matrix; serves as the FR-6 reference exemplar; IN-005, IN-007.

### Blast-radius questions

Per ADR-0018, blast-radius analysis is captured in `codebase-analysis.json`'s `blast_radius` section. The questions:

- **For `review-architecture-auditor`**: Which agents / skills / scripts call into the auditor (1-hop)? Which docs reference its output contract (3-hop)? Does any current consumer of `audit-issues.json` make schema assumptions that would break if FR-1 adds a `design-realization` finding type?
- **For `auditing-mcp`'s `--with-runtime` flag**: Which call sites exist today (grep across `.claude/`, `.github/workflows/`, `Issues/`, `working/feature/`, `auditing-shared/`)? FR-4-d's "fail loudly on legacy flag" needs the full enumeration so no legacy site silently no-ops.
- **For `discovery-codebase-researcher` output schema**: Which downstream consumers read `codebase-analysis.json`? Will FR-2's §Protocol Conformance subsection (additive) break any existing reader?
- **For `design-cc`'s deliverable set**: Which agents / scripts read `design-cc`'s outputs? Will the new mandatory `agent-roster-impact-matrix.md` artifact break any existing consumer that expects a fixed deliverable list?
- **For KB-cc-design Principle 9**: Which other KB / skill / agent files cross-reference Principle 9 today (grep)? FR-8's active-vs-defensive rewording must align with each reference site.
- **For PV-author rubric**: Which phase validators currently consume the rubric, and how (e.g., loaded as a skill reference vs. inlined)? FR-3's cross-file invariant prompt must propagate consistently.
- **For `state-transitions.log` schema**: Which writers and readers exist? Will FR-9's Blocks-X marker transitions need a new event type or compose with existing?

Per ADR-0018, blast radius captures `hop_tier_distribution` (1-hop / 2-hop / 3-hop dependent counts).

### Convention discovery

Per-layer convention discovery for the Claude Code layer (the only in-scope layer):

- **Agent file conventions** — frontmatter fields used today (`model:`, `effort:`, `skills:`, `tools:`, `description:`, etc.); naming convention; deviation from defaults.
- **Skill file conventions** — `SKILL.md` shape, `references/` subdirectory pattern, `pedagogical_sections:` frontmatter (per ADR-0030), `family:` field (per ADR-0042).
- **KB cross-reference conventions** — how principles cross-reference each other (numbered? slug-linked?); how skills reference KBs from frontmatter `skills:` arrays; how discipline texts cite ADRs.
- **`audit-issues.json` finding shape conventions** — how findings name `rule`, `target`, `divergence`, `next_action` today (the NFR-8 fields the PRD prescribes). Are there existing findings that already use these field names? If so, FR-1 / FR-4 / FR-5 / FR-9 / FR-10 should align; if not, the convention is being established.
- **Severity-string conventions** — current vocabulary: BLOCKER / MAJOR / MINOR / NIT (per `auditing-mcp/SKILL.md`), or the alternative `critical / important / recommended` (per `KB-review-disciplines/references/severity-taxonomy.md`). FR-1 / FR-4 / FR-5 must declare which they emit; the convention question is for `design-composer`.
- **Blocks-X marker grammar (OI-A5)** — survey existing `Blocks <stage>` marker syntax across recent discovery outputs and state-transition logs. Report whether the grammar is stable, heterogeneous, or absent. This is the A-5 validation hook from the PRD's Assumptions table.

### Specific queries / grep targets

- `grep -rn "with-runtime" .claude/ .github/workflows/ auditing-* working/feature/ Issues/` — enumerate all call sites of the legacy flag (FR-4-d).
- `grep -rn "Blocks " working/feature/*/codebase-analysis*.md working/feature/*/research-plan*.md` — survey Blocks-X marker grammar (OI-A5).
- `grep -rn "Principle 9" .claude/skills/ .claude/agents/` — enumerate cross-references for FR-8 alignment.
- `grep -rn "agent-roster-impact-matrix" .claude/ working/feature/ Issues/` — confirm the retroactive Track-A2 matrix is the only existing reference; FR-6 establishes the convention.
- `grep -rn "with_runtime\|with-runtime\|with-mcp-reachability" .claude/skills/auditing-mcp/` — confirm the flag's current implementation in `audit_mcp.py`.
- `ls .claude/agents/*.md | wc -l` — A-4 validation; FR-6 row-count baseline.
- `jq '.mcpServers | keys' .mcp.json` — six-server enumeration (IN-016).
- `grep -rn "post-ship\|N days post-ship\|days post-ship" .claude/skills/ working/feature/*-deferrals/` — survey current "post-ship" trigger language to anchor FR-11's grep-checkable Success Criterion ("zero occurrences in artifacts authored after this feature ships").

### Mechanism-dependency reporting (special discipline for this run)

Per the orchestrator prompt, the codebase researcher MUST produce a **mechanism dependency table** as a dedicated subsection of `codebase-analysis.json` (or a sibling Markdown report cross-linked from it) so that `design-composer` can apply the Contingency Split threshold (PRD §Contingency Split) mechanically.

The table reports, for each FR (FR-1..FR-11), the per-FR set of:
- **Touched files** (1-hop edits).
- **Shared touch points with other FRs** (if FR-X and FR-Y both touch file F, they are linked).
- **Shared OI dependencies** (FR-X resolves only when OI-Y resolves; e.g., FR-1 ↔ OI-A1).
- **Shared gate locations** (FR-X attaches at the same state-machine gate as FR-Y; e.g., FR-6 and FR-7 both attach at Design Composition close).
- **R2a vs R2b membership claim per the PRD's Contingency Split § Candidate split membership**.

The output's purpose: `design-composer` reads it to detect FRs that cannot cleanly split (i.e., FR-1's PRD-suggested R2a placement with potential R2b relocation, called out explicitly in the PRD), and to surface a split recommendation at the Design Composition Gate if the threshold trips.

### Watch-items the codebase researcher should report on (PRD-derived)

Per the orchestrator prompt, the Plan flags these PRD-resolved-but-Discovery-evidence-needed items:

- **OI-A1 informant evidence** (machine-checkable companion file vs NLP parse): Discovery surfaces what ADR files currently look like, whether prescriptions are sectioned uniformly, and whether a companion-file convention already exists in the repo (e.g., any `*.yaml` sibling to an ADR file). Combined with T-002 (external).
- **OI-A2 informant evidence** (denormalized per-PV vs centralized): Discovery surfaces how cross-file consistency checks (if any) are currently authored across phase validators. Combined with T-004 (external).
- **OI-A4 evidence** (4-cycle reconciliation cap): Discovery reports the actual count and topology of OIs in recent feature runs to inform the threshold of 12 in the PRD's Contingency Split section. The PRD has already calibrated; Discovery confirms or surfaces a recalibration signal.
- **OI-A5 evidence** (Blocks-X grammar): per the grep target above; the A-5 validation hook.

---

## External research topics

Per ADR-0021, external research is conditional on documented KB gaps. The budget is 6 topics maximum; this Plan authorizes **4 topics**, with explicit KB-gap justifications. Two candidate topics evaluated and rejected (recorded in "Topics explicitly NOT researched").

### T-001 — Tool-surface drift detection: low-false-positive JSON-document diff and normalization rules

- **Topic ID**: `T-001`
- **Name**: MCP tool-surface drift detection algorithms and false-positive engineering
- **Research question**: What normalization rules, schema-diff algorithms, and baseline-storage conventions for `tools/list` JSON-document drift detection achieve < 5% false-positive rate across 50 audits against a stable upstream set, while still surfacing tool removals, additions, and signature changes?
- **KB gap justification**: KB-mcp-design's OP-1..OP-10 catalog covers the design-rule scaffolding (which severity for which event class) but does NOT cover the empirical engineering of low-false-positive JSON drift detection. KB-mcp-platform covers the protocol shape (the `tools/list` response schema) but not diff-algorithm choice. KB-codebase-research's blast-radius techniques cover relationship graphs, not document diffing. This is not `designer-general-knowledge` because the < 5% target across 50 audits (NFR-4) is a measurable engineering constraint requiring sourced approaches (e.g., from API-contract-drift tooling like Pact, OpenAPI-diff, Buf's schema-diff for Protobuf).
- **Acceptance criteria**:
  - Names ≥ 3 schema-diff / JSON-document drift detection approaches in production use (e.g., OpenAPI-diff, Pact contract testing, Protobuf wire-compat checks, JSON-Patch, JSON-Pointer-based diff).
  - For each approach, identifies the normalization rules it applies by default (whitespace, ordering, description text, optional fields).
  - Identifies ≥ 2 trade-offs (e.g., semver-awareness vs. structural-equality; description-text noise vs. signature change false negatives).
  - Quotes specific normalization-rule lists or false-positive-rate benchmarks where available.
  - Surfaces any approach that natively handles "removal of allowlisted item" vs "addition" with differentiated severity — directly applicable to AC-FR-5-a / AC-FR-5-d / AC-FR-5-e.
- **Source constraints**: Official documentation of the tools (OpenAPI Initiative, Pact Foundation, Buf), engineering blog posts from companies operating drift detection at scale (e.g., Stripe, Shopify on contract testing), peer-reviewed papers from contract-testing literature. No Medium articles; no AI-generated content farms.

### T-002 — Design-realization audit prior art: machine-checkable companion files vs. NLP prescription extraction

- **Topic ID**: `T-002`
- **Name**: ADR-style decision artifacts and design-realization verification patterns
- **Research question**: In dev systems that verify "as-built matches as-designed" (spec-as-code, architecture decision tracking, contract testing), which decision artifacts ship machine-checkable companion files vs. which rely on NLP-style parsing of decision prose, and what are the documented trade-offs (authoring burden, fragility, audit coverage)?
- **KB gap justification**: No project KB covers ADR-companion-file vs. NLP-parse design patterns. KB-cc-design covers Claude Code agent / skill / MCP surface design, not ADR machinery. KB-documentation-criteria provides the ADR template structure but does not survey machine-checkability extensions. KB-review-disciplines covers CoVe + blast-radius + brief-honor for the auditor lens, not the upstream artifact shape. This is not `designer-general-knowledge` because the trade-off requires sourced examples from systems that have tried both — a competent designer would not be expected to carry this without precedent. OI-A1 is FR-1's testability hinge (AC-FR-1-c); a sourced choice grounds the resolution.
- **Acceptance criteria**:
  - Identifies ≥ 3 production systems with comparable design-realization machinery (candidates: Architecture Decision Records with companions; Terraform Sentinel policies vs. Terraform plan diffs; OpenAPI spec-vs-implementation tooling; Pact contract testing; AsyncAPI; ArchUnit-style architecture tests in Java).
  - For each system, names whether the verification artifact is machine-checkable companion or NLP-parsed prose.
  - Identifies ≥ 2 trade-offs (authoring burden, fragility under prose drift, audit coverage breadth).
  - Surfaces any case study where one approach was adopted, found insufficient, and replaced — strongest signal for OI-A1.
- **Source constraints**: Primary sources only — project documentation, official architecture-decision-record guidance (e.g., Michael Nygard's ADR template, ThoughtWorks Tech Radar), engineering blog posts from companies operating ADR machinery at scale, peer-reviewed papers from architecture-decision research. Prefer recent (2023+) over older sources because tooling has moved.

### T-003 — Skill-coverage / capability-fitness rubric patterns in agent platforms

- **Topic ID**: `T-003`
- **Name**: Capability-coverage decision frames in agent platforms
- **Research question**: What's the prior art for capability-fitness analyses in agent ecosystems — LangGraph, AutoGen, AutoGPT, OpenAI Assistants, Anthropic's own agent literature — and is a Why / How / Anti-patterns trifecta a community pattern, an idiosyncratic shape, or novel for the project?
- **KB gap justification**: No project KB covers cross-platform agent-capability frames. KB-cc-design covers Claude-Code-specific skill design (Principle 2 — skill loading on-demand; Principle 1 — pick the lowest-cost primitive); it does not survey alternative frameworks' patterns for new-concept-to-capability mapping. KB-task-decomposition covers PV-tier decomposition, not capability decomposition. This is not `designer-general-knowledge` because the W/H/A trifecta is a specific shape — a designer cannot commit to it (or to an alternative) without sourced precedent.
- **Acceptance criteria**:
  - Identifies ≥ 3 agent platforms' patterns for "we have a new concept; do we need a new tool / skill / capability?" decision frames.
  - For each, names whether a structured decision artifact is required at design time.
  - Identifies ≥ 2 trade-offs (e.g., trifecta-style structured vs. free-form rationale; mandated-per-concept vs. mandated-only-when-proposing-new).
  - Surfaces any anti-patterns the literature documents (e.g., skill-proliferation; orphaned-capability decay) that FR-7's design should defend against.
- **Source constraints**: Official platform documentation (LangGraph, AutoGen, OpenAI Assistants, Anthropic agent guides), peer-reviewed papers from agent-architecture literature, engineering blog posts from companies operating multi-agent systems at scale. Avoid speculative posts about agent futures; prefer pattern-naming from systems already in production.

### T-004 — Cross-file invariant catalog patterns in DevOps/IaC tooling

- **Topic ID**: `T-004`
- **Name**: Cross-file invariant catalogs: denormalized per-file vs. centralized reference
- **Research question**: How do other systems catalog cross-file invariants — Terraform's plan-time invariant validations, OpenAPI's schema-consistency invariants, dbt's schema tests, contract-testing tooling — and what's the documented trade-off between authoring the invariants denormalized per-file (each file declares its relationships) vs. centralized in a single referenced catalog?
- **KB gap justification**: KB-iac-design covers IaC-specific invariant patterns (Terraform Sentinel, etc.) but is out-of-scope for this feature (Layer Scope = Claude Code only). KB-task-decomposition covers PV authoring discipline but does not survey cross-file invariant catalog patterns outside the project. KB-documentation-criteria covers template structure, not invariant authoring. This is not `designer-general-knowledge` because the normalized-vs-denormalized trade-off requires sourced precedent — both have committed practitioners, and the OI-A2 resolution should land on evidence rather than intuition.
- **Acceptance criteria**:
  - Identifies ≥ 3 systems that catalog cross-file invariants (candidates: Terraform `lifecycle` and Sentinel; dbt schema tests with refs; OpenAPI `$ref` resolution; SchemaStore JSON-Schema cross-file references; ArchUnit cross-package invariants).
  - For each system, names whether the invariant catalog is denormalized (per-file declarations) or centralized (referenced from each file).
  - Identifies ≥ 2 trade-offs (e.g., authoring burden vs. discoverability; per-PV locality vs. catalog reuse).
  - Surfaces any system that adopted one approach, found it insufficient, and migrated to the other — strongest signal for OI-A2.
- **Source constraints**: Official documentation of the tools, peer-reviewed papers from contract-testing and architecture-conformance literature, engineering blog posts from companies operating cross-file invariant tooling at scale. Avoid speculative or community-vote-driven sources.

---

## Topics explicitly NOT researched

Per ADR-0021's anti-scope-creep discipline, this section names every information need with disposition `covered-by-KB` or `covered-by-ADR` (and explicit `designer-general-knowledge` claims) so future revisits of "should we research X?" land here first.

### Covered by existing KBs

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-017 (protocol part) | `KB-mcp-platform:references/mcp-events-jsonl.md` and the SKILL.md root | KB-mcp-platform is the canonical project KB for MCP transport semantics: `initialize` / `tools/list` / `shutdown` sequence; per-transport differences (stdio / HTTP / SSE); event surface in `mcp-events.jsonl` (per ADR-0037). FR-4's handshake design draws from this KB. |
| IN-023 | `KB-mcp-platform` (whole KB) | Handshake sequence and per-server transport mechanics are exactly what KB-mcp-platform covers. The KB is loaded by `discovery-external-researcher` as context7 / exa lookups already; FR-4's design consults it directly. |

### Covered by existing ADRs

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| Scope class (PRD §Scope class) | `ADR-0021` + KB-documentation-criteria scope-class rubric | PRD already validated against rubric (FULL). No further research needed. |
| Codebase-analysis schema baseline | `ADR-0018` + `ADR-0038` | The v1.1.0 schema is fixed; FR-2 extends additively. Discovery confirms the extension point but does not re-derive the schema. |
| ADR placement / locus | `ADR-0036` + `ADR-0054` + `ADR-0056` | Canonical ADR placement at `/adrs`, no carve-outs; FR-1's prescription extractor can rely on a stable single location. |
| 5-invocation-point reviewer integration | `ADR-0017` | Five `shared-document-reviewer` invocations are fixed; FR-6's matrix-review attachment is mechanical (Blueprint Gate 0/1 absorbs the matrix as a reviewable artifact). |
| Design fan-out | `ADR-0016` | FR-6 attaches inside the `design-cc` lane of the existing fan-out; no topology change. |
| Credential redaction | `ADR-0039` | NFR-6 follows ADR-0039 redaction posture; no new design required. |
| `state-transitions.log` schema | `ADR-0044` | FR-9's Blocks-X marker transitions compose with the existing schema; Discovery confirms the event-type mapping but does not invent a new schema. |
| MCP event surface | `ADR-0037` | FR-4 / FR-5 may emit transition events via `mcp-events.jsonl`; the channel is fixed. |
| Auditing-mcp graduated family | `ADR-0042` | FR-4 / FR-5 land in this family; rename is mechanical. |
| No new sub-agents | `ADR-0045` + PRD Won't-Have | The PRD already commits; no design surface to research. |
| Append-only supersession discipline | `ADR-0005` | FR-8's Principle 9 rewrite uses the append-only supersession convention; no design research needed. |
| Brief-honor verification | `ADR-0009` | FR-1's design-realization dimension extends but does not replace brief-honor; the discipline is fixed. |

### Designer general knowledge

| Need ID | Disposition rationale |
|---|---|
| IN-022 (event vs time-triggered deferral framings) | Engineering-discipline literature is well-documented (SRE error budgets, Lean Startup pivot/persevere, Toyota Production System); the PRD already names the three permitted framings (event-trigger / honest-acceptance / concrete-machinery). The downstream `design-cc` author documents the chosen framing's rationale in the FR-11 discipline-text edits. The designer's prose carries the source authority. |

---

## Estimated effort

- **Codebase research effort**: **medium-large**. The touch-point list is broad (~20 distinct files / directories across 9 agents and 11 skills) but each touch is shallow — the PRD has already named most of them. The mechanism-dependency table is the most concentrated authoring work, but it's mechanically derivable. Estimated wall-clock: 4-6 hours for one `discovery-codebase-researcher` invocation.
- **External research topic count**: **4 of 6** budget. Two candidate topics consolidated or rejected (drift-detection and design-realization audit-prior-art are independent; capability-coverage and cross-file invariant are independent — no further consolidation possible without losing sharpness).
- **Estimated wall-clock (external, parallel)**: 4 topics in parallel; ~1.5-2 hours per topic; total wall-clock ~2 hours since they fan out.
- **Total Discovery Research wall-clock**: ~6 hours (codebase researcher single-instance time dominates; external runs in parallel).

---

## Open questions for human resolution

The Research Plan can resolve most ambiguities mechanically; these items surface at the Research Plan Approval Gate for explicit user input:

1. **Is 4 external topics the right cap for this run, or should the user override down or up?** This Plan authorizes 4 (below the 6 default). Rationale: the PRD is unusually well-mapped — the 11 mechanisms are scoped to known Claude-Code surfaces, the KB inventory is rich, and the 4 external topics target genuine gaps. Surfaces for confirmation.

2. **Should T-003 (capability-coverage frames) and T-004 (cross-file invariant catalogs) be merged?** They are independent — T-003 informs FR-7 (Synthesis / Design-time skill-coverage decisions), T-004 informs FR-3 / OI-A2 (PV-tier cross-file invariant authoring shape). The Plan keeps them separate; the user may direct consolidation if desired (which would loosen acceptance criteria on both).

3. **Should Discovery dogfood the FR-2 §Protocol Conformance subsection in its own output, as a forward-test of the new contract?** Recommended but not required — `discovery-codebase-researcher`'s current contract does not include this subsection, so dogfooding would be additive. The Plan notes this in the codebase-research scope but does not mandate.

4. **Should the mechanism-dependency table be authored as a sibling Markdown file or inlined in `codebase-analysis.json`?** The Plan defaults to sibling Markdown cross-linked from JSON (more readable for human review at the Design Composition Gate); user may direct inline-JSON if downstream tooling demands.

5. **Should Discovery survey "post-ship" trigger language across discipline texts as a baseline for FR-11's grep-checkable Success Criterion (zero post-ship occurrences after ship)?** The Plan includes this grep target; the user may direct that the baseline survey be skipped (deferred to the Plan stage or the test-acceptance-author).

---

*End of Research Plan. Awaiting Research Plan Approval Gate before Discovery Research dispatches.*
