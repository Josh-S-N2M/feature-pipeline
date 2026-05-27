---
id: WHAT-CHANGED-pipeline-design-time-discipline-r1
version: 1.0.0
status: published
audience: future feature authors and reviewers
generated: 2026-05-27T00:00:00Z
generated_by: design-cc (Phase 9 rollout)
feature_slug: pipeline-design-time-discipline-r1
parent_run: pipeline-cross-artifact-discipline-r1
sibling_run: pipeline-gate-validator-hardening-r1
---

# What Changed for Future Feature Authors: pipeline-design-time-discipline-r1 (R2a)

This document is the discoverability surface for the disciplines R2a established.
If your feature run touches the agent surface, introduces a new domain concept, uses Blocks-X markers,
authors ADRs with prescribed files, or produces skill-coverage decisions, read this first.

---

## TL;DR

**What R2a shipped at a glance:**
- 6 functional requirements (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10)
- 6 agents modified: `review-architecture-auditor`, `design-cc`, `design-composer`,
  `synth-synthesizer`, `discovery-codebase-researcher`, `execute-orchestrator`
- 5 skills modified: `KB-cc-design`, `KB-review-disciplines`, `KB-documentation-criteria`,
  `auditing-subagents`, `auditing-shared`
- 4 new scripts: `validate_adr_prescriptions.py`, `parse_blocks_x_markers.py`,
  `check_feature_touch_predicate.py`, `audit_feature_touch_coverage.py`
- 2 new templates: `agent-roster-impact-matrix-template.md`,
  `skill-coverage-decisions-section-template.md`
- 2 new ADRs: ADR-0064 (agent-roster impact matrix contract),
  ADR-0065 (skill-coverage decision discipline)
- 3 inherited ADRs carried forward: ADR-0059, ADR-0061, ADR-0063

**The 5 new disciplines future authors must observe:**

1. **Bridge consultation** — emit findings in the auditor vocabulary; consult
   `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` for vocabulary
   translation across auditor / reviewer / phase-validator surfaces; preserve both weight sets.

2. **Principle 9 active framing** — every agent on the touched surface is evaluated and recorded
   in `agent-roster-impact-matrix.md` per FR-6 and ADR-0064; "no change warranted" is a positive
   evidence string, not an omission.

3. **Blocks-X markers** — use the canonical grammar `<!-- BLOCKS: <stage-slug>-completion -->`
   per ADR-0063; the orchestrator runs the marker gate at T0/T7/T8/T11/T12 checkpoints via
   `parse_blocks_x_markers.py`.

4. **Design-realization audit** — ADRs with prescribed files or commands ship a companion
   `.prescriptions.yaml` sibling file, lint-checked by `validate_adr_prescriptions.py` on each
   architecture-auditor invocation.

5. **Skill-coverage decisions** — every new domain concept a feature introduces gets a row in
   `synthesis.md` §Skill-Coverage Decisions; the row must carry a W/H/A trifecta for new-skill
   proposals, and positive coverage evidence for existing-skill claims (ADR-0065).

**Headline dogfood result:** SA-14 cycle 0 returned FAIL on R2a's own matrix — the new
multi-table parser correctly caught a preamble-table mis-selection in the first-table scanner.
Cycle 1 patched the defect; SA-14 re-run returned PASS. R2a's discipline caught a real bug
in R2a's own machinery, confirming the central thesis.

---

## 1. Bridge Consultation

### What it is

`KB-review-disciplines/references/severity-taxonomy.md` is the canonical five-column bridge table
that maps severity vocabulary across all consumers: auditor (`review-architecture-auditor`),
reviewer (`shared-document-reviewer`), and phase-validator (`phase-quality-handler`).
Prior to R2a, each surface used its own vocabulary and reviewers had to translate mentally.
ADR-0061 (inherited from the parent run) pinned the host; R2a authored the content.

### Who emits / who consumes

- **Emitters:** `review-architecture-auditor` (FR-1 findings), `auditing-subagents` rules
  (SA-1 through SA-14), phase-quality validators.
- **Consumers:** `shared-document-reviewer` (when reviewing audit outputs), `execute-orchestrator`
  (when deciding whether to block on a finding), R2b's `pipeline-gate-validator-hardening-r1`
  (inherits the populated bridge).

### Which file the author touches

`.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`

Emit severity tokens from this table. Do not invent new severity labels without a table update
and a corresponding architecture-audit finding to justify it.

### Which audit catches violations

`review-architecture-auditor` Lens 4 (cross-artifact vocabulary consistency) emits a WARNING
when it detects a finding with a severity label absent from the bridge table.

### Canonical reference

ADR-0061 (`adrs/ADR-0061-severity-vocabulary-bridge-table.md`) — host decision.
The table itself lives at `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`.

### Worked example

An architecture-auditor finding reads: `"severity": "BLOCKER"`. The bridge table maps
`BLOCKER` → auditor column `BLOCKER` → reviewer column `CRITICAL` → PV column `FAIL`.
A phase-quality handler receiving the audit output resolves `BLOCKER` → `FAIL` via the table,
not by ad hoc parsing. If your feature adds a new finding severity (e.g. `ADVISORY`), add a row
to the bridge table first and update the ADR-0061 changelog.

---

## 2. Principle 9 Active Framing (Agent-Roster Impact Matrix)

### What it is

KB-cc-design Principle 9 previously read as passive: "consider whether other agents in the roster
should be updated." R2a re-framed it as active: every agent on the full roster is evaluated and
the outcome — changed, explicitly not-changed, or not-applicable — is recorded in a structured
artifact (`agent-roster-impact-matrix.md`) before Design Composition can close.

The trigger is four-condition: (1) the feature directly modifies an existing agent file; (2) the
feature adds a new agent; (3) the feature adds a skill that the design indicates existing agents
will load; or (4) the feature introduces a domain concept whose skill-coverage decision names an
existing agent as a downstream consumer. Any one of the four fires the mandate.

### Who emits / who consumes

- **Author:** `design-cc` during per-layer Design, or `design-composer` at Design Composition
  (whichever stage the trigger is confirmed).
- **Reviewer:** `shared-document-reviewer` invocation 3 (Blueprint review) checks matrix presence
  and row-count parity with the agent inventory.
- **Backstop auditor:** `auditing-subagents` SA-14 (`audit_feature_touch_coverage.py`) re-checks
  matrix presence and row count at pre-deliverable packaging.

### Which file the author touches

`working/feature/<slug>/agent-roster-impact-matrix.md`

Use the template at `.claude/skills/auditing-subagents/templates/agent-roster-impact-matrix-template.md`.
The matrix has five columns: Agent | Touch-Type | Rationale | Evidence | Disposition.
Row count must equal the full agent inventory count. Absent rows are a BLOCKER finding at SA-14.

### Which audit catches violations

SA-14 (`audit_feature_touch_coverage.py`) — emits `RULE_TABLE_NOT_FOUND` if the matrix file is
absent, `RULE_TABLE_AMBIGUOUS` if the parser finds multiple candidate tables and cannot resolve
the canonical one, and `FAIL` if row count does not match the agent inventory.

### Canonical reference

ADR-0064 (`adrs/ADR-0064-agent-roster-impact-matrix-contract.md`) — four trigger conditions,
column schema, positive-evidence-string discipline.
Template: `.claude/skills/auditing-subagents/templates/agent-roster-impact-matrix-template.md`
Script: `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py`
Advisory predicate (trigger 3/4): `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py`

### Worked example

Feature `example-agent-update-r1` adds a new MCP tool to 3 of 37 agents. Trigger condition 1
fires. `design-cc` authors `agent-roster-impact-matrix.md` with 37 rows. For the 3 changed agents,
the Evidence column reads the tool name and config delta. For the 34 unchanged agents, the
Evidence column reads "Evaluated: no MCP tool changes needed; existing skill set covers the
feature surface." At SA-14: `agent_count_expected=37`, `row_count_observed=37` → PASS.

---

## 3. Blocks-X Markers

### What it is

Blocks-X markers are HTML comments embedded in pipeline working documents that signal a stage
transition is blocked until a named condition resolves. The canonical grammar (ADR-0063,
inherited from the parent run) is:

```
<!-- BLOCKS: <stage-slug>-completion -->
```

Optional payload: `<!-- BLOCKS: blueprint-completion — pending ADR-0041 prescription file -->`.
Parser regex: `<!--\s*BLOCKS:\s*([a-z0-9-]+)-completion(?:\s+—\s+[^\n]*)?\s*-->`.

The orchestrator invokes `parse_blocks_x_markers.py` at T0/T7/T8/T11/T12 checkpoints and refuses
to advance a stage until all markers in that stage's scope transition to RESOLVED, DEFERRED,
or FALSE_POSITIVE.

### Who emits / who consumes

- **Author:** any pipeline agent that discovers a blocking condition during its stage (typically
  `discovery-codebase-researcher` at Discovery, or `design-composer` at Design Composition).
- **Resolver:** the agent or human that addresses the blocking condition updates the marker's
  state annotation.
- **Enforcer:** `execute-orchestrator`, reading `parse_blocks_x_markers.py` output at each gate.

### Which file the author touches

Any working document in `working/feature/<slug>/` may carry a marker. The marker is placed
inline at the point where the blocking condition was discovered. The parser scans all working
documents under the slug directory.

### Which audit catches violations

`parse_blocks_x_markers.py` — emits an unresolved-marker finding for each marker whose state
is not RESOLVED / DEFERRED / FALSE_POSITIVE. The orchestrator gates on this output.

### Canonical reference

ADR-0063 (`adrs/ADR-0063-blocks-x-marker-grammar.md`) — grammar, parser regex, state vocabulary.
Script: `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py`

### Worked example

During Discovery, `discovery-codebase-researcher` identifies that the feature's plan requires
a not-yet-existing helper script. It embeds:

```
<!-- BLOCKS: blueprint-completion — validate_adr_prescriptions.py does not exist yet; must be
authored before FR-1 audit can run -->
```

The Blueprint phase authors the script. The resolving agent updates the marker:

```
<!-- BLOCKS: blueprint-completion — RESOLVED: validate_adr_prescriptions.py authored at
.claude/skills/auditing-shared/scripts/ per T4.1 -->
```

The orchestrator's T7 checkpoint sees RESOLVED and advances.

---

## 4. Design-Realization Audit (ADR Prescriptions)

### What it is

When an ADR prescribes concrete files to be created, commands to be run, or configuration entries
to be set, those prescriptions must be machine-checkable. ADR-0059 (inherited from the parent run)
established the `.prescriptions.yaml` companion file as the canonical form. R2a wired the audit
dimension into `review-architecture-auditor` via `validate_adr_prescriptions.py`.

The companion file lives next to the ADR:
`adrs/ADR-NNNN-<slug>.prescriptions.yaml`

The architecture auditor scans for companion files on every ADR in scope. For each companion, it
compares the prescription list against the eventual implementation files and emits a BLOCKER
finding for any divergence.

### Who emits / who consumes

- **Author:** the agent that authors the ADR (typically `design-composer`) also authors the
  companion `.prescriptions.yaml` at the same time.
- **Auditor:** `review-architecture-auditor` (Lens 1 / FR-1) — reads companion files as ground
  truth; no-ops cleanly when no companion exists (opt-in by ADR scope).
- **Validator:** `validate_adr_prescriptions.py` — schema lints the companion file's YAML
  structure before the auditor consumes it.

### Which file the author touches

`adrs/ADR-NNNN-<slug>.prescriptions.yaml` (new file, sibling to the ADR).

### Which audit catches violations

`review-architecture-auditor` Lens 1 emits `BLOCKER` on prescription-vs-implementation
divergence. `validate_adr_prescriptions.py` emits schema-lint errors on malformed companions.

### Canonical reference

ADR-0059 (`adrs/ADR-0059-adr-prescriptions-companion-file.md`) — companion file schema.
Script: `.claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py`

### Worked example

ADR-0041 prescribes that `.mcp.json` must contain an `npx @anthropic/sdk` server entry.
The author creates `adrs/ADR-0041-<slug>.prescriptions.yaml`:

```yaml
schema_version: "1.0"
adr_id: ADR-0041
prescriptions:
  - artifact: .mcp.json
    check: json_key_present
    key: "mcpServers.anthropic-sdk"
    rationale: "ADR-0041 §Implementation requires this server entry"
```

At architecture-audit time, `review-architecture-auditor` reads the companion, checks `.mcp.json`
for the key, and — if absent — emits: `BLOCKER: ADR-0041 prescription 'anthropic-sdk server in
.mcp.json' not satisfied in eventual implementation`.

This is the exact defect class that shipped in `devcontainer-mcp-provisioning-r1` (5 of 7 MCP
servers broken post-ship). The companion file makes that class structurally unshippable.

---

## 5. Skill-Coverage Decisions

### What it is

When a feature introduces a new domain concept — a noun-phrase not previously named in the
project's KB or skill inventory — the synthesizer must record an explicit skill-coverage decision
for each concept before Design Composition can consume the synthesis. The decision is one of:

- **(a)** Name an existing skill that covers it, with positive evidence of coverage.
- **(b)** Propose a new skill with a W/H/A trifecta: Why this skill exists, How agents use it,
  Anti-patterns it prevents.
- **(c)** Record "no skill warranted" with explicit rationale for why the concept does not need
  a coverage artifact.

This fires at Synthesis. The section lives in `synthesis.md` §Skill-Coverage Decisions.
ADR-0065 codifies the contract; it is structural (present or absent) for new-skill proposals and
substantive (judge by content) for existing-skill and no-skill-warranted rows.

### Who emits / who consumes

- **Author:** `synth-synthesizer` at Synthesis stage (or `design-composer` if the concept
  surfaces first at Design Composition).
- **Reviewer:** `shared-document-reviewer` invocation 3 checks that each concept in scope has
  a row and that new-skill-proposal rows carry all three W/H/A cells.
- **Consumer:** `design-composer` reads the table when evaluating FR-6 trigger conditions 3/4
  (an advisory predicate scans it for trigger-shaped tokens).

### Which file the author touches

`working/feature/<slug>/synthesis.md` — add or extend the `## Skill-Coverage Decisions` section.

Use the template at `.claude/skills/KB-cc-design/templates/skill-coverage-decisions-section-template.md`.
Table columns: `Concept | Covering Skill | Confidence | W/H/A or Rationale | Dogfood Decision`.

### Which audit catches violations

`review-architecture-auditor` Lens 2 (FR-7) flags a synthesis.md that introduces domain concepts
without a corresponding Skill-Coverage Decisions row. The `shared-document-reviewer` rubric
(invocation 3) includes a structural check for W/H/A cell completeness on new-skill proposals.

### Canonical reference

ADR-0065 (`adrs/ADR-0065-skill-coverage-decision-discipline.md`) — W/H/A hybrid mandate, row
schema, placement decision (embedded in synthesis.md per Clause 1).

### Worked example

Feature `example-new-concept-r1` introduces the concept "multi-region failover topology."
`synth-synthesizer` adds to `synthesis.md`:

```markdown
## Skill-Coverage Decisions

| Concept | Covering Skill | Confidence | W/H/A or Rationale | Dogfood Decision |
|---|---|---|---|---|
| multi-region failover topology | KB-infra-resilience (proposed new) | low | **Why:** No existing skill names failover topology patterns. **How:** Loaded by IaC designer and backend designers when a feature adds region-spanning resources. **Anti-patterns:** Assuming active-active is always preferable; neglecting DNS TTL in failover calculus. | Propose new skill; author skeleton in this run |
```

The reviewer checks that Why/How/Anti-patterns are substantively filled. An empty cell or
"TBD" is a blocking finding under ADR-0065 Clause 2.

---

## 6. Inheritance Map for Future Runs

**This run = R2a** (design-time discipline half of the parent R2 split).

**Sibling run = R2b** (`pipeline-gate-validator-hardening-r1`) — gate/validator hardening half,
currently queued. Inherits the populated severity bridge from R2a. Covers FR-2, FR-3, FR-4,
FR-5, FR-11. See `working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md`
for the full lineage and inheritability table.

**What every future run that touches the agent surface inherits from R2a:**

The FR-6 advisory predicate (`check_feature_touch_predicate.py`) fires at Design Composition
when any of the four trigger conditions are present. The orchestrator enforces this by checking
for `agent-roster-impact-matrix.md` before closing the Design Composition stage.
SA-14 (`audit_feature_touch_coverage.py`) enforces it again at pre-deliverable packaging.
Future runs cannot skip this by omission — SA-14 returns FAIL without the file.

**What every future run that introduces new domain concepts inherits from R2a:**

The `synthesis.md` §Skill-Coverage Decisions section template is mandatory when a concept is new
to the project's KB/skill inventory. The `shared-document-reviewer` rubric checks for it at
invocation 3. `review-architecture-auditor` Lens 2 checks it at the architecture audit pass.
Skipping the section produces a BLOCKER finding that gates Blueprint approval.

**Inherited ADRs future runs carry forward:**

| ADR | What it governs | Binding on |
|---|---|---|
| ADR-0059 | `.prescriptions.yaml` companion-file schema | All future ADRs with concrete prescriptions |
| ADR-0061 | Severity-vocabulary bridge table host | All finding emitters |
| ADR-0063 | Blocks-X marker grammar | All pipeline agents at stage transitions |
| ADR-0064 | Agent-roster impact matrix contract | All features touching the agent surface |
| ADR-0065 | Skill-coverage decision discipline | All features introducing new domain concepts |

---

## 7. Open Items for Future Maintenance

These items were recorded in `audit-issues.json` (T9.1 output) as open but not blocking R2a's
PASS verdict. Future runs or maintenance cycles should address them.

| ID | Severity | Target | Description | Suggested action |
|---|---|---|---|---|
| I-PQ-P4-002 | MINOR | `.claude/agents/discovery-codebase-researcher.md` | Missing MCP init section per ADR-0040. The file does not include the required always-on MCP initialization section (narrowed always-on, 5-agent canonical list). | Add the ADR-0040-compliant MCP init section before the next agent update cycle. |
| I-PQ-P5-002 | MINOR | `working/feature/pipeline-design-time-discipline-r1/phase-validators.md` | PV-3.C2 lists `TRIGGER_OVERRIDE` under FR-9 Blocks-X scope; it belongs under ADR-0064 scope. Editorial cross-reference drift. | Correct PV-3.C2 attribution: move `TRIGGER_OVERRIDE` reference from FR-9 column to ADR-0064 column. Cosmetic; no behavioral impact. |
| I-PQ-P6-002 | NOTE | `working/feature/pipeline-design-time-discipline-r1/synthesis/synth-synthesizer.md` | Sub-section physical placement is cosmetically off — a sub-section appears outside its logical parent heading. | Reorder sub-section under its correct parent heading. Cosmetic only. |
| I-PQ-P7-001 | NOTE | `.claude/skills/auditing-subagents/examples/good-subagent-annotated.md` | Line 89 references SA-1-through-SA-12; catalog now extends through SA-14. Stale range undercounts the catalog. | Update line 89 to reference SA-1-through-SA-14 (or current catalog end). Cosmetic fixture update. |
| I-PQ-P8-001 | MINOR | `.claude/skills/auditing-subagents/SKILL.md` | SA-14 reference documentation lag. SKILL.md still describes first-table parser behavior (pre-T7.1 patch); 2 new rule constants (`RULE_TABLE_NOT_FOUND`, `RULE_TABLE_AMBIGUOUS`) are undocumented. | Update SA-14 entry: (a) describe multi-table scanner behavior; (b) document `RULE_TABLE_NOT_FOUND` and `RULE_TABLE_AMBIGUOUS` with semantics and exit codes. |

---

## 8. Cross-References

**Inherited ADRs from parent run:**
- `adrs/ADR-0059-adr-prescriptions-companion-file.md`
- `adrs/ADR-0061-severity-vocabulary-bridge-table.md`
- `adrs/ADR-0063-blocks-x-marker-grammar.md`

**New ADRs authored this run:**
- `adrs/ADR-0064-agent-roster-impact-matrix-contract.md`
- `adrs/ADR-0065-skill-coverage-decision-discipline.md`

**Phase-quality reports (full audit trail, P0 through P8):**
- `working/feature/pipeline-design-time-discipline-r1/phase-quality-report-P0.json` through
  `phase-quality-report-P8.json` and their `.md` companions.

**T9.1 audit output (SA-14 verdict PASS):**
- `working/feature/pipeline-design-time-discipline-r1/audit-issues.json`

**Parent run split decision:**
- `working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md`

**R2b queued run:**
- `working/feature/pipeline-gate-validator-hardening-r1/` (not yet started at R2a close)

**Agent-roster impact matrix (this run's own deliverable under ADR-0064):**
- `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md`

---

## 9. The Dogfood Validation Story

R2a's central thesis — "the pipeline must verify relationships across artifacts, not just
per-artifact correctness" — was applied to R2a itself. The run produced an `agent-roster-impact-matrix.md`
(per ADR-0064), six skill-coverage decisions in `synthesis.md` (per ADR-0065), and ran
SA-14 (`audit_feature_touch_coverage.py`) against its own matrix in Phase 8.

**Cycle 0 returned FAIL.** The parser defect: `audit_feature_touch_coverage.py` used a first-table
selection strategy that picked a 2-column preamble table at the top of the matrix file instead
of the canonical 5-column impact matrix. The parser returned `RULE_TABLE_NOT_FOUND` — a false
finding on a file that clearly contained the matrix.

The root cause was not in the matrix itself. It was in T7.1's parser implementation: the single
`_find_first_table()` call matched the first markdown table in the document regardless of column
schema. The canonical matrix was present and correct; the parser could not find it.

**Cycle 1 fixed the defect.** A cross-task patch rewrote the parser to use `_collect_all_tables()`
with canonical-header matching (`_is_canonical_matrix_table()`), scanning all tables in the
document and selecting by header schema (Agent | Touch-Type | Rationale | Evidence | Disposition).
Regression fixture F (a multi-table document with a preamble table preceding the matrix) was
added to the smoke suite. All 6/6 smoke tests passed.

**SA-14 re-run returned PASS**: 37 agents expected, 37 rows observed, 0 findings.

The significance: R2a's new discipline (`audit_feature_touch_coverage.py` + SA-14) caught a real
implementation defect in R2a's own new machinery — during the same run that authored the
machinery. The discipline did not merely validate an already-correct artifact; it surfaced a parser
bug that would have produced false-negative coverage verdicts on future runs had it shipped
undetected. This is the recurrence-risk-cancellation the central thesis promised: cross-artifact
verification caught what per-artifact correctness gates would have missed.
