---
id: agent-roster-impact-matrix-template
version: 1.0.0
status: template
template_for: agent-roster-impact-matrix
derived_from: ADR-0064
generated_by: design-cc
---

# Agent-Roster Impact Matrix — Template

## Contents

- [Purpose and contract summary](#purpose-and-contract-summary)
- [When to author this matrix (four-condition trigger)](#when-to-author-this-matrix-four-condition-trigger)
- [The matrix table](#the-matrix-table)
- [Authoring discipline](#authoring-discipline)
- [Severity calibration](#severity-calibration)
- [Worked example](#worked-example)
- [Cross-references](#cross-references)
- [Update history](#update-history)

---

## Purpose and contract summary

The `agent-roster-impact-matrix.md` deliverable is the per-run artifact that proves **every agent on the full roster was considered** when the feature touches the agent surface. It is not a "what changed" document; it is a "what was evaluated" document. Its per-cell positive-evidence discipline is the substance test for whether KB-cc-design Principle 9's active framing actually happened — see §Authoring discipline below.

The contract governing this artifact is **ADR-0064** (Agent-Roster Impact Matrix Contract). Four normative clauses:

- **Clause 1** — Four-condition trigger (what fires the matrix requirement)
- **Clause 2** — Artifact shape (row count, five dimensions, per-cell discipline)
- **Clause 3** — Advisory mechanical predicate + human ratification
- **Clause 4** — Override-event discipline (logging disagreements with the predicate)

**Canonical path:** `working/feature/<feature-slug>/agent-roster-impact-matrix.md`

---

## When to author this matrix (four-condition trigger)

A feature is required to produce this matrix if **any** of the four conditions below holds during the run. Conditions 1 and 2 are mechanical (parseable from file diffs and `.mcp.json`). Conditions 3 and 4 are interpretive (the advisory predicate at `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` scans for trigger-shaped tokens; the human ratifies).

| # | Trigger condition | Evaluation mode |
|---|---|---|
| **1** | The feature's diff modifies, creates, or removes any file under `.claude/agents/*.md` | Mechanical — file-diff parseable |
| **2** | The feature's diff modifies `.mcp.json` in a way that adds, removes, or changes the tool surface of any MCP server already allowlisted to one or more agents | Mechanical — JSON-shape parseable |
| **3** | The feature's diff creates a new skill (`.claude/skills/<name>/SKILL.md`) that the feature's design indicates one or more existing agents will load | Interpretive — advisory predicate scans design artifacts; human ratifies |
| **4** | The feature's design or PRD declares a new domain concept whose skill-coverage decision (per ADR-0065) names an existing agent as a downstream consumer | Interpretive — advisory predicate scans `synthesis.md` Skill-Coverage Decisions section; human ratifies |

If no condition fires: no matrix is required. Record the predicate output in `state-transitions.log` as confirmation.

If any condition fires: the matrix is **mandatory**. Design Composition close is blocked until the matrix is present (per `recipe-feature-pipeline/SKILL.md` Stage 7 gate). Pre-deliverable packaging re-checks presence and row count via SA-14 (FR-10).

---

## The matrix table

**Row count:** exactly equal to `ls .claude/agents/*.md | wc -l` at matrix authoring time. At the 37-agent inventory (2026-05-27), the matrix is **37 rows × 5 columns = 185 cells**. No more, no fewer rows — the full-inventory discipline is what prevents "evaluated by absence."

**Five columns (one per dimension per ADR-0064 Clause 2):**

| Column | What it records |
|---|---|
| `tools` | Whether the agent's `tools:` array changes (MCP tools added or removed; Bash sub-patterns added or removed) |
| `skills` | Whether the agent's `skills:` array changes (new skill loaded; existing skill removed) |
| `model` | Whether the agent's `model:` frontmatter field changes |
| `effort` | Whether the agent's `effort:` frontmatter field changes |
| `prompt body` | Whether the agent's prompt body (instruction text) changes |

**Per-cell schema — `<value> — <positive-evidence-string>`:**

Every cell must contain the structural value followed by a dash and a positive-evidence string. The positive-evidence string is a short rationale derived from inspectable evidence (the agent's prompt body, tools list, feature's design artifacts, grep results, ADR citations).

Valid `<value>` tokens:

| Value token | Meaning |
|---|---|
| `no-change` | This dimension is unchanged for this agent |
| `tools-add: <list>` | One or more tool entries added |
| `tools-remove: <list>` | One or more tool entries removed |
| `skills-add: <list>` | One or more skill entries added |
| `skills-remove: <list>` | One or more skill entries removed |
| `model-change: <old>→<new>` | The `model:` frontmatter field changes |
| `effort-change: <old>→<new>` | The `effort:` frontmatter field changes |
| `prompt-edit: <one-line-summary>` | The prompt body is edited (describe the change briefly) |

**Bare `no-change` without a positive-evidence string is structurally insufficient** per ADR-0064 Clause 2. The evidence string IS the substance test.

Example well-formed cells:

- `tools` cell: `no-change — Designer confirmed FR-3 edits do not touch this agent's tool surface; grep confirmed Agent tool absent per ADR-0045`
- `skills` cell: `skills-add: KB-review-disciplines — FR-1 new audit dimension requires the severity-taxonomy bridge table; KB-review-disciplines is the host skill per ADR-0061`
- `model` cell: `no-change — Principle 9 active framing: opus + xhigh reasoning load required for cross-family critique; unchanged`
- `effort` cell: `effort-change: high→xhigh — new Lens 4 cross-document reconciliation over ADR prescriptions × implementation files; xhigh warranted`
- `prompt body` cell: `prompt-edit: add FR-6 matrix authoring procedure — Phase 2 extension adds mandatory output and four-condition trigger check`

**Table header to use in the actual deliverable:**

```markdown
| # | Agent file | tools | skills | model | effort | prompt body |
|---|---|---|---|---|---|---|
```

---

## Authoring discipline

Follow this sequence when authoring the matrix for a feature run.

### Step 1 — Trigger detection

Run the advisory predicate:

```bash
python3 .claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py \
  --feature-slug <slug> \
  --working-dir working/feature/<slug>/
```

The predicate emits a structured annotation for each of the four trigger conditions. For conditions 1 and 2 it provides a definitive yes/no; for conditions 3 and 4 it provides an advisory annotation. You (the designer) ratify whether each interpretive condition fires.

If you disagree with the predicate's classification of any condition, log the override per Step 1b before proceeding.

### Step 1b — Override-event logging (when disagreement occurs)

When your ratification disagrees with the predicate's advisory output, emit a `TRIGGER_OVERRIDE` event to `state-transitions.log` via:

```bash
python3 .claude/skills/auditing-shared/scripts/log_state_transition.py \
  --transition-name TRIGGER_OVERRIDE \
  --context '{"trigger_condition": <1|2|3|4>, "rationale": "<one-line>", "advisory_predicate_output": "<yes|no>"}'
```

Silent overrides (no log entry) are structurally indistinguishable from "no trigger fired." The log entry IS the override per ADR-0064 Clause 4.

### Step 2 — Row enumeration

```bash
ls .claude/agents/*.md | sort
```

This is your row set. One row per file. The row count you produce must equal `ls .claude/agents/*.md | wc -l` at authoring time.

### Step 3 — Per-cell authoring

For each agent × dimension cell:

1. Read the agent file: check current `tools:`, `skills:`, `model:`, `effort:`, and body text.
2. Determine whether this feature's changes touch this dimension for this agent.
3. Write `<value> — <positive-evidence-string>`.
4. The evidence string must derive from something inspectable: the agent's own text, a grep result, a cc-design.md reference, an ADR citation, a blueprint section. "No reason found" is not a valid evidence string.

**The evidence string is the active-framing artifact.** It records that you evaluated this dimension deliberately, not that you skipped it.

### Step 4 — Override-event posture for interpretive trigger disagreements

Per ADR-0064 Clause 3, the predicate does NOT mandate the matrix — it advises. You ratify. If the predicate says "condition 3 fires" and you judge it does not (because the new skill is not actually consumed by any existing agent per the design), log the override (Step 1b) and proceed without the matrix. The override log entry is the evidence of the deliberate no-matrix decision.

### Principle 9 cross-reference

KB-cc-design Principle 9 (active framing) requires that for every agent on the touched agent surface — changed and unchanged alike — the Designer records the consideration performed on that agent's three independent reasoning fields (`model:`, `effort:`, `skills:`), even when the recorded outcome is no change. The matrix's per-cell discipline is the artifact of that consideration. See `.claude/skills/KB-cc-design/references/principles.md` §Principle 9.

---

## Severity calibration

When the FR-10 audit (SA-14) or a reviewer finds matrix issues, the severity follows the bridge table in `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`:

| Condition | Severity | Audit surface |
|---|---|---|
| Matrix absent when a trigger condition fired | **BLOCKER** | SA-14 (FR-10) pre-deliverable packaging gate; shared-document-reviewer invocation 3 |
| Row count does not match `ls .claude/agents/*.md \| wc -l` | **BLOCKER** | SA-14 (FR-10); same gate |
| One or more cells contain bare `no-change` without a positive-evidence string | **MAJOR** | shared-document-reviewer invocation 3; design-composition close check |
| Matrix present, row count correct, all cells have evidence strings, but evidence strings are thin / assertion-free | **MINOR** | shared-document-reviewer invocation 3 (substance check) |

BLOCKER findings refuse-to-advance across all pipeline surfaces. MAJOR findings are blocking by default; downgrade to warning only with explicit per-finding rationale per the bridge table's non-monotonic edge description.

---

## Worked example

The following 3-row excerpt shows the matrix format using three agents from the current 37-agent inventory. These rows are illustrative of the format — they do not reflect any specific feature's actual changes.

**Scenario:** A hypothetical feature that modifies `design-claude-code.md` (adds a new procedure phase) and creates a new skill `KB-new-discipline/SKILL.md` that `review-architecture-auditor` will load. Conditions 1 and 3 both fire.

```markdown
| # | Agent file | tools | skills | model | effort | prompt body |
|---|---|---|---|---|---|---|
| 1 | design-claude-code.md | no-change — This feature does not modify the agent's `tools:` array; grep of feature diff confirms no `tools:` line touched; ADR-0045 Agent-tool absence not relevant (design-cc does not list Agent tool) | no-change — The new KB-new-discipline skill is authored for consumption by review-architecture-auditor (condition 3 trigger), not design-claude-code; grep of cc-design.md confirms design-cc's `skills:` array unchanged in this feature | no-change — Principle 9 active framing: model: opus unchanged; the new Phase 2 extension is procedural text addition, not a reasoning-load increase | no-change — effort: high unchanged; Phase 2 procedure extension is bounded authoring work within the existing effort envelope per NFR-7 | prompt-edit: add FR-X matrix authoring procedure — Phase 2 gains a new mandatory output block: `working/feature/<slug>/agent-roster-impact-matrix.md`, conditional on four-condition trigger check |
| 2 | review-architecture-auditor.md | no-change — This feature does not add or remove any MCP tool entries for this agent; serena whole-server allowlist unchanged; grep of diff confirms no `mcp__` token change in this agent file | skills-add: KB-new-discipline — FR-X implementation requires the new discipline KB at audit time; cc-design.md §FR-X confirms this agent loads KB-new-discipline for Lens N reasoning; design-composer ratified at Blueprint composition | no-change — Principle 9 active framing: model: opus unchanged; new Lens N adds cross-document comparison but remains within the existing xhigh reasoning envelope confirmed by cc-design.md §FR-1 justification | no-change — effort: xhigh unchanged; the new lens adds one additional cross-document check, not a reasoning-mode shift; xhigh remains warranted per cc-design.md §FR-X reasoning justification | no-change — This feature does not touch the prompt body of review-architecture-auditor.md; the new skill loading is a frontmatter change only; grep of diff confirms body text unchanged |
| 3 | discovery-codebase-researcher.md | no-change — This feature does not modify .mcp.json entries for this agent; serena allowlist unchanged; grep of diff confirms no `mcp__` token change | no-change — The new KB-new-discipline skill is scoped to review-architecture-auditor per cc-design.md §FR-X; discovery-codebase-researcher's `skills:` array is unchanged; grep of cc-design.md confirms no consumer assignment for this agent | no-change — Principle 9 active framing: model: opus unchanged; research-stage role unchanged; no reasoning-load shift | no-change — effort: high unchanged; new skill in KB-new-discipline does not alter the discovery stage's scope | no-change — This feature does not edit the body of discovery-codebase-researcher.md; grep of diff confirms no line changes in this file |
```

**Key observations from the example:**

1. Every `no-change` cell contains a positive-evidence string — a grep confirmation, a cc-design.md citation, or an ADR reference.
2. The one changed cell (`skills-add` for `review-architecture-auditor`) names the specific skill, the specific FR, and the specific design artifact that confirms the loading decision.
3. The `model` and `effort` cells for unchanged agents explicitly invoke "Principle 9 active framing" to signal deliberate evaluation, not absence-of-thought.
4. Bare `no-change` (no evidence) would fail at shared-document-reviewer invocation 3 as a MAJOR finding.

---

## Cross-references

| Reference | Relevance |
|---|---|
| `adrs/ADR-0064-agent-roster-impact-matrix-contract.md` | The normative contract this template implements (four-condition trigger, artifact shape, positive-evidence discipline, override-event logging) |
| `adrs/ADR-0045-*.md` | No Agent tool in sub-agents — relevant to the `tools` column: the absence of the Agent tool in most agents is an expected structural property, not an omission |
| `.claude/skills/KB-cc-design/references/principles.md` §Principle 9 | Active framing — the per-agent consideration discipline this matrix is the artifact of |
| `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` | Severity bridge table — governs what severity the FR-10 audit and reviewer emit for matrix-related findings |
| `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` | Advisory predicate that evaluates the four trigger conditions (T5.2 in `pipeline-design-time-discipline-r1`) |
| `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` | SA-14 audit script — packaging-time backstop that checks matrix presence and row-count parity |
| `.claude/skills/auditing-shared/scripts/log_state_transition.py` | Used to emit `TRIGGER_OVERRIDE` events when designer ratification disagrees with the predicate |

---

## Update history

| Entry | Date | Task / Phase | Notes |
|---|---|---|---|
| T5.1 / Phase 5 | 2026-05-27 | T5.1 / Phase 5 | Initial template authored per AC-FR-6-a, AC-FR-6-b, AC-FR-6-d, AC-NFR-9-a; derived from ADR-0064 + blueprint-v1.md + cc-design.md; worked example uses design-claude-code, review-architecture-auditor, discovery-codebase-researcher. |
