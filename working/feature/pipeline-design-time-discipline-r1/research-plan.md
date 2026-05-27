---
id: RP-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: research-plan
feature_slug: pipeline-design-time-discipline-r1
derived_from: working/feature/pipeline-design-time-discipline-r1/prd-v1.md
predecessor: working/feature/pipeline-cross-artifact-discipline-r1/research-plan.md
parent_run: pipeline-cross-artifact-discipline-r1
inherited_research_notes: [T-002, T-003]
inherited_codebase_analysis: working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
generated: 2026-05-26T17:05:00Z
generated_by: discovery-plan-author
---

# Research Plan: Pipeline Design-Time Discipline (R2a)

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

- **Feature slug**: `pipeline-design-time-discipline-r1`
- **PRD path**: `working/feature/pipeline-design-time-discipline-r1/prd-v1.md`
- **PRD version**: `1.0.0`
- **PRD gate state**: approved at PRD Approval Gate (Auto Mode); see PRD frontmatter
- **Intent Clarification path**: `working/feature/pipeline-design-time-discipline-r1/intent-clarification.md`
- **Parent run (terminated at Gate 4 by split decision)**: `pipeline-cross-artifact-discipline-r1` — see `SPLIT-RECORD.md`
- **Sibling queued run (does NOT block this run)**: `pipeline-gate-validator-hardening-r1` (R2b)
- **Inherited ADRs in scope** (all Accepted in the parent run):
  - **ADR-0059** — Companion-file `.prescriptions.yaml` schema for ADR design-realization audits. Closes parent PRD OI-A1 and pins FR-1's prescription-extraction mechanism. **Load-bearing for FR-1.**
  - **ADR-0061** — Severity vocabulary bridge table host at `KB-review-disciplines/references/severity-taxonomy.md`. Cross-cuts R2a (FR-1, FR-9, FR-10) and R2b (FR-4, FR-5). R2a-first ordering means this run authors the bridge content; R2b inherits a populated table. **Load-bearing for FR-1, FR-9, FR-10.**
  - **ADR-0063** — Blocks-X marker grammar canonicalization. Closes parent PRD OI-A5 and pins the FR-9 grammar contract. **Load-bearing for FR-9.**
- **Inherited ADRs (background context, established by earlier runs)**:
  - **ADR-0009** rationale brief / brief-honor (FR-1 extends but does not replace).
  - **ADR-0011** template consolidation (FR-1's companion-file pattern compatibility).
  - **ADR-0016** Design fan-out (FR-6 attaches at the `design-cc` lane).
  - **ADR-0017** `shared-document-reviewer` 5 invocation points (FR-6 matrix is a reviewable artifact at point 4).
  - **ADR-0020** KB consolidation (FR-8 edits KB-cc-design Principle 9).
  - **ADR-0021** KB-and-ADR-first; Discovery refactor (this artifact's authoring discipline).
  - **ADR-0036, ADR-0054, ADR-0056** canonical ADR placement (FR-1 prescription locus).
  - **ADR-0044** specialist-dispatch / `state-transitions.log` schema (FR-9 records marker transitions).
  - **ADR-0045** no Agent tool in sub-agents (FR-1 audit dimension runs inline in `review-architecture-auditor`).
  - **ADR-0049** structural-vs-discipline KB split (FR-7 skill-coverage is a discipline concern).
- **Applicable KBs**:
  - `KB-cc-design` — design discipline for Claude Code surface; Principle 9 is the FR-8 target.
  - `KB-review-disciplines` — host KB for the severity-vocabulary bridge content (per ADR-0061). FR-1's design-realization dimension extends the architecture-audit discipline.
  - `KB-documentation-criteria` — templates and shared conventions; FR-6 introduces a new mandatory artifact, FR-7 introduces a Skill-Coverage Decisions section.
  - `KB-task-decomposition` — PV-author rubric; potential consumer for FR-7's section if Design Composition resolves OI-R2a-4 toward an embedded location.
  - `recipe-feature-pipeline` — the 13-stage state machine; FR-6 and FR-9 attach new stage-transition gates.
  - `auditing-subagents` — FR-10 rule attachment.
  - `auditing-skills` — OI-R2a-2 (reverse-check) target; carried as Blueprint Open Question.
  - `auditing-shared` — `audit-issues.json` schema and severity-string conventions; severity bridge consults these.

## Information needs inventory

The parent run produced 22 information needs (IN-001..IN-022 plus IN-023/IN-024). This Plan inherits the parent's dispositions verbatim for the FRs in R2a's scope (FR-1/6/7/8/9/10), and surfaces only the genuinely **new** items that bear on R2a — chiefly the three newly-inherited ADRs' content, the severity-bridge authoring source material, and any deltas since the parent's codebase-analysis was extracted (~3 hours earlier at 2026-05-26T13:30:00Z).

The parent's IN-018, IN-021, IN-022, IN-024 inform FR-3 / FR-4 / FR-5 / FR-11 and are **out of scope for this run** (R2b will inherit them).

### IN-R2a-001 — Content of inherited ADRs 0059, 0061, 0063

- **Description**: What do the three newly-inherited ADRs say verbatim — decision statement, decision details, accepted/rejected alternatives — so downstream Synthesis and Design Composition stages can frame their FRs against the canonical text rather than inferring from the parent PRD's summary?
- **Downstream consumer(s)**: `synthesize-*` (frames FR-1 / FR-9 / and the severity bridge against the ADR text); `design-cc` (designs FR-1 `.prescriptions.yaml` consumer, FR-9 grammar parser, FR-1/9/10 severity emission); `design-composer` (FR-1, FR-9, FR-10 contract composition + bridge-table authoring).
- **Disposition**: `codebase-topic`
- **Justification**: ADR files live at `adrs/ADR-0059-*.md`, `adrs/ADR-0061-*.md`, `adrs/ADR-0063-*.md` (confirmed Accepted status). Direct file read by `discovery-codebase-researcher`; the researcher captures decision statement + decision details + companion-file schema (for 0059) + bridge-table outline (for 0061) + canonical grammar regex/EBNF (for 0063) as new content not present in the parent's codebase-analysis.

### IN-R2a-002 — Source material for the severity-vocabulary bridge table (per ADR-0061)

- **Description**: What are the three severity vocabularies currently in use across the codebase that the bridge table must reconcile — (a) the auditor JSON schema vocabulary (BLOCKER / MAJOR / MINOR / NIT / INFO emitted by `review-architecture-auditor`, `review-cross-artifact-auditor`, and verdict-compute scoring in `auditing-cc-configs/scripts/verdict_compute.py`); (b) the reviewer-discipline vocabulary (`critical` / `important` / `recommended` in `KB-review-disciplines/references/severity-taxonomy.md`); (c) the PV-tier vocabulary (`blocking` / `warning` / `informational`)? And: what is the verdict-numeric mapping (BLOCKER -12, MAJOR -5, etc.) the bridge must preserve?
- **Downstream consumer(s)**: `design-composer` (authors the bridge content at `KB-review-disciplines/references/severity-taxonomy.md` per the SPLIT-RECORD R2a-first ordering); FR-1 / FR-9 / FR-10 design subsections (emit findings in vocabulary that round-trips via the bridge).
- **Disposition**: `codebase-topic`
- **Justification**: All three vocabularies live in files under `.claude/skills/` and `.claude/agents/`. The codebase researcher enumerates the exact strings and the verdict-numeric mapping so the bridge author has canonical data without re-surveying. Parent codebase-analysis already captured most of this in its IN-002 disposition; this need adds the explicit reporting requirement that the researcher consolidates into a single "severity vocabularies snapshot" subsection for the bridge author to ingest verbatim.

### IN-R2a-003 — Delta in `.claude/` and `adrs/` since the parent's codebase-analysis was generated

- **Description**: Have any files under `.claude/agents/`, `.claude/skills/`, or `adrs/` been modified, created, or removed between the parent's codebase-analysis generation (2026-05-26T13:30:00Z per the parent JSON) and this Discovery Research run? Most relevant: the three new ADRs (0059, 0061, 0063), any new ADRs (0064+) authored in the interim, any agent-prompt or KB edits that landed during the parent's Blueprint authoring. The parent reported 37 `.claude/agents/*.md` files; re-confirm.
- **Downstream consumer(s)**: All downstream R2a stages (Discovery inheritance integrity check).
- **Disposition**: `codebase-topic`
- **Justification**: Mechanical mtime / file-count comparison against the parent's recorded snapshot. The researcher emits a "deltas since parent" subsection listing any drift; if no drift, the parent's codebase-analysis can be inherited verbatim for the FR-1/6/7/8/9/10 touch points. This is a load-bearing inheritance-integrity check.

### IN-R2a-004 — Current Principle 9 cross-reference count (FR-8 alignment surface)

- **Description**: How many cross-references to KB-cc-design Principle 9 currently exist across `.claude/skills/` and `.claude/agents/`, and what is the verbatim citing text in each? The parent reported 2 cross-references at extraction time; FR-8's active-vs-defensive rewording must propagate to every citing site so designers don't encounter contradictory guidance (per AC-FR-8-b). Verify current state.
- **Downstream consumer(s)**: `design-cc` (FR-8 edit + propagation); `design-composer` (composition integrity).
- **Disposition**: `codebase-topic`
- **Justification**: Pure grep target: `grep -rn "Principle 9" .claude/skills/ .claude/agents/`. Parent reported 2; this need re-confirms in case Phase-4-era edits added or removed cross-references.

### IN-R2a-005 — "Post-ship" trigger-language survey scoped to R2a's discipline-text edits

- **Description**: The parent reported zero occurrences of "post-ship" or "N days post-ship" in `.claude/skills/` and `.claude/agents/`. R2a does not author FR-11 (which lives in R2b), but the FR-8 Principle 9 rewording and the FR-7 W/H/A trifecta text are discipline-text edits whose forward-compat with R2b's §O posture matters. Re-confirm zero occurrences across the surfaces R2a edits (KB-cc-design, recipe-feature-pipeline, KB-review-disciplines).
- **Downstream consumer(s)**: `design-cc` (FR-7, FR-8 discipline-text edits); `design-composer` (forward-compat with queued R2b).
- **Disposition**: `codebase-topic`
- **Justification**: Pure grep target. Cheap re-confirmation.

### IN-R2a-006 — Skill-coverage status of the 6 new domain concepts FR-7 self-applies to

- **Description**: The PRD's Eat-Own-Dogfood Deliverables section names 6 new domain concepts this run introduces — (a) design-realization audit; (b) agent-roster impact matrix; (c) skill-coverage decision check; (d) Principle 9 active reframing; (e) Blocks-X marker grammar; (f) agent-roster matrix-missing audit rule. The parent's report indicated each is likely covered by an existing skill (KB-review-disciplines, KB-cc-design, KB-documentation-criteria, auditing-subagents). Confirm current coverage so FR-7's dogfooded skill-coverage decisions can land on existing-skill rather than propose-new for each.
- **Downstream consumer(s)**: `design-cc` + `design-composer` (FR-7 dogfooding); `synthesize-*` (FR-7 framing).
- **Disposition**: `codebase-topic`
- **Justification**: Routed to the codebase researcher who has the skill / agent inventory already in hand. The researcher emits a 6-row table: concept → covering skill (if any) → load site → confidence. If a concept has no clear covering skill, that's a propose-new-skill signal the dogfooded decision must surface.

### IN-R2a-007 — Inherited information needs from the parent (resolved by inheritance, listed for traceability)

The following parent information needs cover FRs in R2a's scope and are **inherited verbatim** from the parent's codebase-analysis.json + research-notes/T-002 + research-notes/T-003. No re-research authorized.

| Parent need | FR served | Inheritance source | R2a disposition |
|---|---|---|---|
| Parent IN-001 (review-architecture-auditor contract) | FR-1 | parent codebase-analysis.json `components[review-architecture-auditor]` | Inherited verbatim |
| Parent IN-002 (audit-issues.json schema + severity vocabulary) | FR-1, FR-9, FR-10 | parent codebase-analysis.json `components[auditing-shared]` + agent-prompt schema lines | Inherited verbatim + augmented by IN-R2a-002 for bridge authoring |
| Parent IN-004 (recipe-feature-pipeline state machine + Blocks-X marker locations) | FR-6, FR-9 | parent codebase-analysis.json `components[recipe-feature-pipeline]` | Inherited verbatim; marker grammar now resolved by ADR-0063 (no further survey needed) |
| Parent IN-005 (design-cc contract + artifact set) | FR-6 | parent codebase-analysis.json `components[design-cc]` | Inherited verbatim |
| Parent IN-006 (KB-cc-design Principle 9 current text) | FR-8 | parent codebase-analysis.json `components[KB-cc-design]` | Inherited verbatim + IN-R2a-004 re-confirms cross-ref count |
| Parent IN-007 (auditing-subagents check inventory) | FR-10 | parent codebase-analysis.json `components[auditing-subagents]` | Inherited verbatim |
| Parent IN-013 (state-transitions.log schema) | FR-9 | parent codebase-analysis.json + ADR-0044 | Inherited verbatim |
| Parent IN-014 (mechanism dependency table) | All R2a FRs | parent codebase-analysis.json `mechanism_dependency_table` | Inherited verbatim — table covers all 11 parent FRs; R2a's design-composer reads the FR-1/6/7/8/9/10 subset |
| Parent IN-015 (.claude/agents/*.md inventory count) | FR-6, FR-10 | parent codebase-analysis.json — 37 agents reported | Re-confirmed via IN-R2a-003 delta check |
| Parent IN-019 (design-realization audit prior art) | FR-1 | parent research-notes/T-002 | **Inherited verbatim** (see External Research Topics §) |
| Parent IN-020 (skill-coverage rubric patterns) | FR-7 | parent research-notes/T-003 | **Inherited verbatim** (see External Research Topics §) |
| Parent OI-A1 (FR-1 extraction mechanism) | FR-1 | Resolved by inherited ADR-0059 | Closed |
| Parent OI-A5 (Blocks-X marker grammar) | FR-9 | Resolved by inherited ADR-0063 | Closed |

The parent's IN-003, IN-008, IN-009, IN-010, IN-011, IN-016, IN-017, IN-018, IN-021, IN-022, IN-023, IN-024 inform R2b-only FRs (FR-2/3/4/5/11) and are **out of scope** for R2a. They are not re-listed here.

---

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The contract for R2a is **inheritance-aware**: the parent's `codebase-analysis.json` (generated 2026-05-26T13:30:00Z) is full-fidelity for all 11 FRs; the R2a researcher's job is to confirm inheritance integrity, capture the three new ADRs' content, author the severity-vocabularies snapshot for the bridge author, and run a small set of R2a-specific blast-radius queries.

### Inheritance directive (load-bearing)

**The R2a `discovery-codebase-researcher` MUST inherit the parent's `codebase-analysis.json` for the FR-1/6/7/8/9/10 touch points verbatim, and produce a thinner R2a-specific `codebase-analysis.json` that:**

1. **Cites the parent JSON** as `inherited_from: working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json` in its frontmatter / top-level metadata.
2. **Carries forward** the parent's `components`, `dependencies`, `blast_radius`, and `mechanism_dependency_table` rows for the FR-1/6/7/8/9/10 subset. No re-derivation; cite the parent JSON's section IDs.
3. **Adds** (as new content) the items in IN-R2a-001..006 below.
4. **Reports any deltas** (per IN-R2a-003) so downstream consumers know whether to trust the inheritance.

This directive is per the SPLIT-RECORD's "Full inheritance" classification of the parent codebase-analysis and is load-bearing for the clock-time optimization motivating the R2a/R2b split.

### Touch points (R2a-specific; inheriting parent's broader inventory)

The parent's codebase-analysis enumerates ~21 components and ~21 dependency edges across all 11 FRs. R2a inherits the parent's full inventory and adds **only the new content** below as additional touch points:

- `adrs/ADR-0059-adr-prescriptions-companion-file.md` — IN-R2a-001 (decision + companion-file schema); FR-1 contract source.
- `adrs/ADR-0061-severity-vocabulary-bridge-table.md` — IN-R2a-001 (bridge-table outline + verdict-numeric mapping); FR-1 / FR-9 / FR-10 severity-emission source.
- `adrs/ADR-0063-blocks-x-marker-grammar.md` — IN-R2a-001 (canonical grammar regex/EBNF); FR-9 grammar contract source.
- `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` — host file for the bridge content this run authors per ADR-0061. The researcher reports current contents so the bridge author knows what's there vs. what's new.
- `.claude/skills/auditing-cc-configs/scripts/verdict_compute.py` — verdict-numeric mapping source (parent reported BLOCKER -12, MAJOR -5, MINOR -2, NIT -0.5, INFO 0). Required reading for the bridge author.
- `.claude/skills/auditing-shared/` (full skill body) — severity-string conventions used by audit-issues.json; cross-cuts with the bridge.

(The parent's full touch-point list — `.claude/agents/review-architecture-auditor.md`, `.claude/agents/design-cc.md` (filename `design-claude-code.md`), `.claude/agents/design-composer.md`, `.claude/skills/KB-cc-design/references/principles.md`, `.claude/skills/auditing-subagents/`, `.claude/skills/recipe-feature-pipeline/SKILL.md`, `.claude/skills/KB-documentation-criteria/`, etc. — is inherited verbatim and not re-listed.)

### R2a-specific blast-radius queries (smaller scope than parent's)

The parent ran broad blast-radius queries against all 11 FRs' touch points. R2a needs only the queries that bear on the design-time-discipline mechanisms; the rest is inherited.

1. **`review-architecture-auditor` consumers (1-hop and 3-hop)** — for FR-1's design-realization audit dimension attachment. Which agents / scripts / docs reference the auditor's output or contract? Does any consumer of `audit-issues.json` make schema assumptions that would break if FR-1 adds a `design_realization` finding type? (Parent likely answered most of this; R2a confirms for FR-1's specific finding-type addition.)
2. **`design-cc` deliverable consumers** — for FR-6's mandatory `agent-roster-impact-matrix.md` artifact. Which agents / scripts read `design-cc`'s output set? Does any consumer expect a fixed deliverable list that the matrix would break? (Parent ran this; R2a re-confirms only if IN-R2a-003 reports drift on `design-cc.md`.)
3. **`KB-cc-design` Principle 9 cross-references (FR-8 alignment)** — `grep -rn "Principle 9" .claude/skills/ .claude/agents/` (parent reported count of 2; R2a re-confirms verbatim citing text per IN-R2a-004 so FR-8's rewording can propagate to every site without contradiction).
4. **`auditing-subagents` rule call sites (FR-10 attachment)** — which scripts / agents invoke `auditing-subagents`? Where does the new "missing matrix at pre-deliverable-packaging" rule attach? (Parent answered most of this; R2a confirms the rule-set composition shape so design-cc can extend cleanly.)
5. **`KB-task-decomposition` PV-author rubric consumers (FR-7 attachment-location signal for OI-R2a-4)** — only if FR-7's skill-coverage section lands as an embedded section per OI-R2a-4. Which agents/skills load the PV-author rubric? If FR-7 attaches there vs. as a standalone artifact, the consumer set matters. (Parent did NOT pre-resolve this since OI-R2a-4 is a Design-stage call; R2a surfaces the consumer enumeration so design-cc has the data.)
6. **`KB-review-disciplines` consumers (bridge content propagation)** — which agents/skills load `KB-review-disciplines`, and which of those will consume the new bridge content at `references/severity-taxonomy.md`? Required so the bridge content lands at a location whose downstream consumers actually see it.

The mechanism-dependency table is **NOT re-derived**; the parent's table covers all 11 FRs and R2a's design-composer reads the FR-1/6/7/8/9/10 rows directly.

### Convention discovery (R2a-specific increment)

Most conventions are inherited from the parent's codebase-analysis. R2a adds one new survey:

- **Severity vocabularies snapshot (IN-R2a-002)** — the researcher emits a consolidated "severity vocabularies in the codebase today" subsection covering:
  - Auditor JSON schema vocabulary (BLOCKER / MAJOR / MINOR / NIT / INFO) — verbatim from `review-architecture-auditor.md` and `review-cross-artifact-auditor.md` agent prompts.
  - Reviewer-discipline vocabulary (`critical` / `important` / `recommended`) — verbatim from `KB-review-disciplines/references/severity-taxonomy.md` (current state, pre-bridge-content authoring).
  - PV-tier vocabulary (`blocking` / `warning` / `informational`) — verbatim from `KB-task-decomposition/` PV-author files.
  - Verdict-numeric mapping — verbatim from `auditing-cc-configs/scripts/verdict_compute.py`.
  - `audit-issues.json` finding-shape conventions (rule / target / divergence / next_action field presence, per NFR-8).

This snapshot is the load-bearing input for `design-composer`'s bridge-content authoring under ADR-0061.

### Specific queries / grep targets (R2a-scoped)

- `grep -rn "Principle 9" .claude/skills/ .claude/agents/` — IN-R2a-004 cross-reference re-confirmation.
- `grep -rn "post-ship\|N days post-ship\|days post-ship" .claude/skills/KB-cc-design/ .claude/skills/recipe-feature-pipeline/ .claude/skills/KB-review-disciplines/` — IN-R2a-005 forward-compat survey of R2a-edited surfaces.
- `ls .claude/agents/*.md | wc -l` — IN-R2a-003 delta check vs. parent's 37.
- `find .claude/ adrs/ -name "*.md" -newer working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json -type f` — IN-R2a-003 mtime delta enumeration.
- `find adrs/ -name "ADR-006*.md" -type f` — surface any ADR-0064+ authored between parent run and this run.
- `grep -rn "BLOCKER\|MAJOR\|MINOR\|NIT\|INFO" .claude/agents/review-architecture-auditor.md .claude/agents/review-cross-artifact-auditor.md .claude/skills/auditing-cc-configs/scripts/verdict_compute.py` — IN-R2a-002 auditor-vocabulary capture.
- `grep -rn "critical\|important\|recommended" .claude/skills/KB-review-disciplines/references/severity-taxonomy.md` — IN-R2a-002 reviewer-discipline vocabulary capture.

### Watch-items the codebase researcher should report (R2a-scoped)

Per the orchestrator prompt, the following PRD-derived watch-items need Discovery evidence even though the parent ADRs have closed the prior PRD's load-bearing OIs:

- **OI-R2a-1 informant evidence** (mechanical evaluator for FR-6 trigger conditions 3 and 4): the researcher reports whether the Blueprint's Skill-Coverage Decisions table (FR-7's output) is structurally suitable for a deterministic predicate that drives FR-6's trigger 3/4 evaluation. Combined with the parent's IN-014 mechanism dependency.
- **OI-R2a-3 informant evidence** (FR-9 marker-parser realization location): the researcher enumerates candidate hosts for the Blocks-X marker parser — (a) inside `review-architecture-auditor.md` prompt, (b) as a shared helper under `.claude/skills/auditing-shared/scripts/`, (c) inside the `auditing-subagents` rule itself. Reports the existing parser/regex infrastructure (if any) at each candidate site.
- **OI-R2a-4 informant evidence** (FR-7 artifact location): the researcher confirms whether the Blueprint and synthesis templates currently have a natural attachment point for a Skill-Coverage Decisions section, and whether a standalone `skill-coverage-decisions.md` artifact has any precedent in `working/feature/*/`.
- **OI-R2a-5 informant evidence** (FR-10 rule realization): the researcher reports whether `auditing-subagents` currently has any rule whose predicate is "feature working directory shape" (the closest analog to FR-10's trigger), so design-cc can extend vs. add cleanly.
- **OI-R2a-6 informant evidence** (severity-bridge sequencing): the researcher reports whether any current draft / WIP edit to `KB-review-disciplines/references/severity-taxonomy.md` exists in the repo that the bridge author would collide with.

These are reporting items, not blockers. The OIs themselves are owned by Design Composition (per the PRD).

---

## External research topics

**No external research topics are authorized for this run. `discovery-external-researcher` is NOT dispatched.**

The parent run (pipeline-cross-artifact-discipline-r1) authored 4 external research topics. For R2a:

- **T-002 (design-realization audit prior art)** — directly applicable to FR-1. The parent's research note at `working/feature/pipeline-cross-artifact-discipline-r1/research-notes/T-002-design-realization-audit-prior-art.md` is **inherited verbatim**; no re-research authorized. R2a's `design-composer` reads the inherited note directly as input to FR-1's contract design.
- **T-003 (skill-coverage rubric patterns)** — directly applicable to FR-7. The parent's research note at `working/feature/pipeline-cross-artifact-discipline-r1/research-notes/T-003-skill-coverage-rubric-patterns.md` is **inherited verbatim**; no re-research authorized. R2a's `synthesize-*` and `design-cc` read the inherited note directly as input to FR-7's framing.
- **T-001 (drift detection)** — informs FR-5 in the queued R2b run; **out of scope for R2a**. Not dispatched here.
- **T-004 (cross-file invariant catalogs)** — informs FR-3 in the queued R2b run; **out of scope for R2a**. Not dispatched here.

**Rationale for the zero-topic disposition**: the parent's external research is fresh (authored ~3 hours before this run) and directly applicable. Re-researching would (a) burn clock-time without changing the answer, (b) re-traverse Exa/context7 sources whose results are stable over a 3-hour window, and (c) violate the inheritance discipline that motivates the R2a/R2b split itself. The parent's research-notes/T-002 and T-003 are the canonical input artifacts for FR-1 and FR-7 in this run.

If a new external-research need surfaces during Synthesis or Design Composition (e.g., the dogfooded FR-7 skill-coverage decisions reveal a concept the parent's T-003 doesn't cover), the Blueprint Open Question slot is the correct surface — not a Discovery Research re-run.

---

## Topics explicitly NOT researched

Per ADR-0021's anti-scope-creep discipline. This section is unusually rich for R2a because the inheritance from the parent run closes most of what would otherwise be open research questions.

### Inherited research-notes (no re-research)

| Topic | Inherited from | R2a downstream consumer |
|---|---|---|
| T-002 — design-realization audit prior art | `working/feature/pipeline-cross-artifact-discipline-r1/research-notes/T-002-design-realization-audit-prior-art.md` | `design-composer` (FR-1 contract design); `design-cc` (FR-1 mechanism) |
| T-003 — skill-coverage / capability-fitness rubric patterns | `working/feature/pipeline-cross-artifact-discipline-r1/research-notes/T-003-skill-coverage-rubric-patterns.md` | `synthesize-*` (FR-7 framing); `design-cc` (FR-7 section template); `design-composer` (Skill-Coverage Decisions section structure) |

### Closed by inherited ADRs (parent PRD OIs resolved)

| Topic / Need | Resolving ADR | Resolution summary |
|---|---|---|
| FR-1 prescription-extraction mechanism (parent OI-A1) | ADR-0059 | Companion-file `.prescriptions.yaml` schema is canonical. `review-architecture-auditor` consumes the companion file mechanically; no NLP parse of ADR prose required. |
| FR-9 Blocks-X marker grammar (parent OI-A5) | ADR-0063 | Canonical grammar (regex / EBNF) is fixed. Discovery does not need to survey heterogeneous marker text across past discovery outputs. |
| Severity-vocabulary bridge host location | ADR-0061 | Host is `KB-review-disciplines/references/severity-taxonomy.md`. The decision of WHERE the bridge content lives is closed; this run authors the CONTENT there, with the source vocabularies captured via IN-R2a-002. |

### Covered by existing KBs (inherited from parent's "Topics explicitly NOT researched" section)

| Need | Resolving artifact | Resolution summary |
|---|---|---|
| MCP transport semantics (parent IN-017, IN-023) | `KB-mcp-platform` | Out of scope for R2a (no FR touches MCP transport); informs R2b only. |
| Tool-surface drift design (parent IN-024) | `KB-mcp-design` + R2b's T-001 | R2b-only; not relevant to R2a. |
| Event vs. time-triggered deferral framings (parent IN-022) | `designer-general-knowledge` per parent | R2b-only (FR-11); not relevant to R2a. |

### Covered by existing ADRs (inherited from parent; scoped to R2a-relevant ones)

| Need | Resolving ADR | Resolution summary |
|---|---|---|
| Codebase-analysis schema baseline (FR-2 substrate) | ADR-0018 + ADR-0038 | FR-2 is R2b; baseline is fixed and irrelevant to R2a's content authoring. |
| ADR placement / locus stability (FR-1 substrate) | ADR-0036, ADR-0054, ADR-0056 | Canonical placement at `/adrs`; FR-1's `.prescriptions.yaml` companion lives alongside the ADR file per ADR-0059. |
| 5-invocation-point reviewer integration (FR-6 attachment) | ADR-0017 | Five `shared-document-reviewer` invocations are fixed; FR-6's matrix-review attaches at invocation 4 (after Design Composition). |
| Design fan-out (FR-6 attachment) | ADR-0016 | FR-6 attaches inside the `design-cc` lane; no topology change. |
| No new sub-agents (PRD Won't-Have) | ADR-0045 | All 6 R2a mechanisms attach to existing agents; no spawn-out. |
| `state-transitions.log` schema (FR-9 transition events) | ADR-0044 | FR-9's Blocks-X marker transitions compose with the existing schema; no new event type required. |
| Append-only supersession discipline (FR-8 edit) | ADR-0005 | Principle 9 rewording uses the append-only convention; no design research needed. |
| Brief-honor verification (FR-1 lens) | ADR-0009 | FR-1's design-realization dimension extends but does not replace brief-honor; the discipline is fixed. |

### Designer general knowledge (R2a doesn't claim any new instances)

R2a introduces no new `designer-general-knowledge` claims beyond those the parent already made. FR-1, FR-6, FR-7, FR-8, FR-9, FR-10 are each grounded in either an inherited ADR (0059, 0061, 0063), an inherited research note (T-002, T-003), or an inherited codebase fact.

---

## Estimated effort

- **Codebase research effort**: **small**. Most of the parent's codebase-analysis is inherited verbatim. R2a's incremental work is the 3 new ADRs' content (mechanical file read), the severity-vocabularies snapshot (4 grep targets + 1 Python file read), the 5 small blast-radius re-confirmations (parent's data is recent enough that most will pass-through), and the IN-R2a-003 delta check. Estimated wall-clock: **1–2 hours for one `discovery-codebase-researcher` invocation** (down from the parent's 4–6 hour estimate).
- **External research topic count**: **0 of 6** budget. Two of the parent's four topics (T-002, T-003) are inherited verbatim; the other two (T-001, T-004) are out of scope for R2a (R2b-only).
- **Estimated wall-clock (external, parallel)**: **0** — no external researcher invocations.
- **Total Discovery Research wall-clock**: ~1–2 hours (single-instance codebase research; no external fan-out).

The clock-time saving versus the naive "re-run Discovery from scratch" path is ~4–5 hours, motivated by the SPLIT-RECORD's full-inheritance classification of the parent's codebase-analysis and the two R2a-applicable research notes.

---

## Open questions for human resolution

The Plan resolves most ambiguities by inheritance. These items surface at the Research Plan Approval Gate for explicit user input:

1. **Confirm the inheritance discipline.** This Plan inherits the parent's codebase-analysis verbatim for the FR-1/6/7/8/9/10 touch points and the parent's research-notes T-002 and T-003 verbatim. The user may direct re-research of either if the 3-hour staleness window or the parent run's terminated state changes the inheritance posture. Plan default: inherit; do not re-research.

2. **Confirm the zero-external-topic disposition.** This Plan authorizes 0 of 6 external topics, on the grounds that T-002 and T-003 cover the R2a-applicable external surface and T-001/T-004 are R2b-only. The user may override if they want fresh sources for FR-1 (T-002 re-research) or FR-7 (T-003 re-research). Plan default: 0 topics; rely on inherited notes.

3. **Confirm the severity-vocabularies snapshot scope (IN-R2a-002).** The snapshot consolidates 3 vocabularies + 1 verdict-numeric mapping + 1 finding-shape convention as load-bearing input for the bridge-content author under ADR-0061. The user may direct narrower scope (e.g., skip the PV-tier vocabulary if R2b ownership matters) or broader scope (e.g., include any reviewer custom-categories). Plan default: 3 vocabularies + verdict-numeric + finding-shape.

4. **Should the R2a `codebase-analysis.json` be a thin overlay citing the parent's, or a self-contained snapshot copying the relevant subset?** Both are defensible. Thin overlay is faster to author and unambiguous about provenance; self-contained snapshot is more robust if the parent run's directory is later relocated or pruned. Plan default: **thin overlay** with explicit `inherited_from` field, since the parent run's directory is preserved for archeological reading per the SPLIT-RECORD.

5. **Should Discovery dogfood the FR-2 §Protocol Conformance subsection?** The parent's research-plan flagged this as a recommended-but-not-required dogfooding item. FR-2 lives in R2b, so dogfooding it here is forward-test work for R2b. Plan default: **skip** (R2b is the natural place to dogfood its own contract; R2a focuses on the FR-6 + FR-7 dogfooding the PRD already commits to).

---

*End of Research Plan. Awaiting Research Plan Approval Gate before Discovery Research dispatches.*

*Discovery Research dispatch profile for this run: 1 × `discovery-codebase-researcher` (R2a-scoped, inheritance-aware); 0 × `discovery-external-researcher`. Estimated wall-clock: 1–2 hours.*
