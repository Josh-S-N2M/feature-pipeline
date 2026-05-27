---
id: SA-14
rule_name: feature-touch-coverage
severity: BLOCKER|MAJOR
governing_adr: ADR-0064
executor: scripts/audit_feature_touch_coverage.py
introduced_by: pipeline-design-time-discipline-r1 (FR-10)
---

# SA-14: feature-touch-coverage — Reference

## Contents

- Purpose
- Triggering conditions
- Evaluation procedure
- Severity calibration
- Output finding shape (NFR-8 four-field)
- Remediation
- Cross-references


## Purpose

SA-14 is the **packaging-time hard gate** that ensures the `agent-roster-impact-matrix.md`
deliverable exists and is structurally compliant whenever a feature run touched the agent
surface. It is the FR-10 backstop mechanism: design-time advisory signals fire earlier
(check_feature_touch_predicate.py / T5.2), but SA-14 is the binding enforcement that blocks
deliverable packaging when those earlier signals fired and the required artifact is absent or
malformed.

The rule directly prevents the defect class identified in the `per-agent-design-evaluation-gap`
analysis: agents evaluated by absence — where no row in the matrix means no consideration
happened, and the gap is invisible to all per-artifact gates.

SA-14 is a **new rule entry**, not an extension of SA-1..SA-13. Existing rules audit
per-subagent-file properties (frontmatter, tools, body, memory). SA-14 audits a
per-feature-run cross-artifact deliverable. Coupling these two dimensions in one rule would
blur the ID-to-purpose mapping of the SA-NN catalog (synthesis D-R2a-5).

---

## Triggering conditions

SA-14 is **not-applicable** unless the advisory predicate fired. The predicate
(`check_feature_touch_predicate.py`) evaluates ADR-0064 Clause 1's four-condition trigger:

| Condition | Type | Description |
|---|---|---|
| 1 | Mechanical | Feature diff modifies, creates, or removes any file under `.claude/agents/*.md` |
| 2 | Mechanical | Feature diff modifies `.mcp.json` in a way that adds, removes, or changes the tool surface of an MCP server already allowlisted to one or more agents |
| 3 | Interpretive | Feature diff creates a new skill (`.claude/skills/<name>/SKILL.md`) that the feature's design indicates one or more existing agents will load |
| 4 | Interpretive | Feature design or PRD declares a new domain concept whose skill-coverage decision (per ADR-0065) names an existing agent as a downstream consumer |

For conditions 1 and 2, the predicate emits a definitive yes/no (file-diff and JSON-shape
parseable). For conditions 3 and 4, the predicate emits an advisory annotation by scanning the
`synthesis.md` Skill-Coverage Decisions section for trigger-shaped tokens; the `design-composer`
(human) ratifies.

SA-14 reads the predicate output (either live-invoked or pre-computed via `--predicate-output`)
and only proceeds to matrix validation if `predicate_fired: true`.

---

## Evaluation procedure

The executor script (`scripts/audit_feature_touch_coverage.py`) runs these steps in order:

**Step 1 — Obtain predicate output.**
Either invoke `check_feature_touch_predicate.py --feature-slug <slug> --repo-root <root>`
directly, or load a pre-computed JSON file via `--predicate-output <path>`. If the predicate
cannot be reached, SA-14 emits a BLOCKER finding and exits with code 2 (invocation error).

**Step 2 — Not-applicable fast path.**
If `predicate_fired` is `false`, emit `sa14_status: not_applicable`, verdict `PASS`, exit 0.
No matrix check is performed.

**Step 3 — Count expected agents.**
Glob `.claude/agents/*.md` from the repo root. The count is the required number of matrix rows.
If the agents directory is missing, a warning is logged to stderr; the row-count check still
runs against agent_count=0.

**Step 4a — Matrix presence check.**
If `working/feature/<slug>/agent-roster-impact-matrix.md` does not exist, emit a BLOCKER
finding and exit 1. No further validation is possible.

**Step 4b — Matrix structural validation (ADR-0064 Clause 2).**
Parse the first Markdown pipe table in the matrix file and check:

1. **Row count.** Data row count must equal the agent count from Step 3. Any divergence is a
   MAJOR finding.
2. **Column presence.** The table header must include all five explicit dimensions: `tools`,
   `skills`, `model`, `effort`, `prompt body`. Missing columns are a MAJOR finding; cell-
   discipline checks are skipped if columns are absent (structure is too ambiguous).
3. **Bare no-change discipline.** Every cell is tested against the pattern
   `^\s*no[- ]?change\s*$` (case-insensitive). Any cell matching this pattern — i.e., `no-change`
   without a `— <positive-evidence-string>` suffix — is structurally insufficient per
   ADR-0064 Clause 2. All offending cells are aggregated into one MAJOR finding.

**Output.** Results are written as JSON to stdout. Log messages go to stderr. Exit codes:
`0` = PASS, `1` = FAIL (findings present), `2` = invocation error.

---

## Severity calibration

SA-14 uses two severity levels per the ADR-0061 bridge table:

| Condition | Severity | Rationale |
|---|---|---|
| Matrix absent when predicate fired | **BLOCKER** | The entire agent-surface evaluation is missing; the deliverable cannot be packaged in a state where this defect is invisible. The `28-agents-evaluated-by-absence` failure mode is structurally possible with no matrix at all. |
| Matrix present but row-count wrong | **MAJOR** | Some agents are missing from the evaluation; the defect is partial but still a structural gap. The matrix exists and is recoverable by adding/removing rows. |
| Matrix present but columns missing | **MAJOR** | One or more of the five evaluation dimensions is absent; the matrix cannot be validated for cell discipline. Structurally non-compliant per ADR-0064 Clause 2. |
| Matrix present but bare no-change cells | **MAJOR** | Presence without evidence is structurally indistinguishable from "never evaluated" (ADR-0064 Rationale 3). The cells exist but do not constitute substance. |

MINOR and NOTE severities are not used by SA-14 — all SA-14 findings are structural
failures warranting at minimum MAJOR treatment. The BLOCKER/MAJOR distinction maps to
the ADR-0061 severity bridge: BLOCKER means "blocks packaging"; MAJOR means "must fix
before shipping but matrix is recoverable."

---

## Output finding shape (NFR-8 four-field)

All SA-14 findings follow the NFR-8 four-field shape:

```json
{
  "rule":        "<SA-14.rule_subtype>",
  "target":      "<path to matrix file or feature slug>",
  "divergence":  "<what was found vs what was required>",
  "next_action": "<concrete remediation step>",
  "severity":    "BLOCKER | MAJOR"
}
```

The three rule subtypes emitted by the executor:

| Subtype | Condition |
|---|---|
| `SA-14.matrix_missing` | Matrix file absent; or predicate output unreadable |
| `SA-14.row_count_mismatch` | Row count diverges from agent count; or columns missing; or table unparseable |
| `SA-14.cell_bare_no_change` | One or more cells contain bare `no-change` without an evidence string |

The outer result envelope contains: `sa14_status` (not_applicable / clean / findings / error),
`feature_slug`, `matrix_path`, `agent_count_expected`, `row_count_observed`, `findings[]`,
`verdict` (PASS / FAIL), `elapsed_ms`.

---

## Remediation

### Finding: SA-14.matrix_missing (BLOCKER)

The matrix file does not exist at `working/feature/<slug>/agent-roster-impact-matrix.md`.

**Fix:**
1. Author the matrix from the template at
   `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md`.
2. The table must have exactly N rows where N = count of `.claude/agents/*.md` files.
3. Each row covers one agent; each cell has the form `<value> — <positive-evidence-string>`.
4. Valid values: `no-change — <evidence>`, `tools-add: <list> — <evidence>`,
   `tools-remove: <list> — <evidence>`, `skills-add: <list> — <evidence>`,
   `skills-remove: <list> — <evidence>`, `model-change: <old>→<new> — <evidence>`,
   `effort-change: <old>→<new> — <evidence>`, `prompt-edit: <summary> — <evidence>`.
5. Re-run `scripts/audit_feature_touch_coverage.py --feature-slug <slug>` to confirm PASS.

### Finding: SA-14.row_count_mismatch (MAJOR)

The matrix has fewer or more rows than the current `.claude/agents/*.md` count.

**Fix:**
- If rows are missing: add one row per missing agent. Use `no-change — <evidence>` if the
  agent was genuinely unaffected; the evidence string proves consideration happened.
- If rows exceed the agent count: a file may have been removed from `.claude/agents/`; remove
  the corresponding matrix row, or verify whether the agent file was accidentally deleted.
- Re-run the executor to confirm the count matches.

### Finding: SA-14.row_count_mismatch — columns missing (MAJOR)

The matrix table header is missing one or more of the five required columns.

**Fix:**
Add the missing column(s) to the table header. Populate each agent's cell in that column.
The five required columns per ADR-0064 Clause 2 are: `tools`, `skills`, `model`, `effort`,
`prompt body`.

### Finding: SA-14.cell_bare_no_change (MAJOR)

One or more cells contain `no-change` (or `no change`) without a positive-evidence string.

**Fix:**
Replace each bare `no-change` cell with `no-change — <positive-evidence-string>`.
The evidence string is a short rationale derived from inspectable evidence — the agent's
prompt body, tools list, or the feature's diff. Examples:

- `no-change — agent has no tools overlap with .mcp.json changes in this feature`
- `no-change — agent's skills array does not include the new KB-cc-design; no prompt-body edit needed`
- `no-change — model/effort unchanged; agent is a read-only auditor not in this feature's blast radius`

A bare `no-change` is structurally indistinguishable from "never evaluated." The evidence
string IS the substance test (ADR-0064 Rationale 3).

---

## Cross-references

| Artifact | Relationship |
|---|---|
| **ADR-0064** (Agent-Roster Impact Matrix Contract) | Governing normative contract. Clauses 1–4 define the trigger, artifact shape, predicate+human seam, and override discipline that SA-14 enforces at packaging time. |
| **ADR-0061** (Severity Vocabulary Bridge) | SA-14's BLOCKER/MAJOR severity choices are mapped through this bridge table. |
| **T5.1** — `agent-roster-impact-matrix-template.md` | The template SA-14 points authors to when the matrix is absent. |
| **T5.2** — `scripts/check_feature_touch_predicate.py` | The advisory predicate SA-14 reads. SA-14 is silent when the predicate did not fire. |
| **T7.1** — `scripts/audit_feature_touch_coverage.py` | SA-14's executor script. Reads predicate output; validates matrix; emits NFR-8 findings. |
| **FR-10** (`pipeline-design-time-discipline-r1` PRD) | The PRD mechanism SA-14 realizes. |
| **recipe-feature-pipeline** orchestrator (Phase 9) | The pipeline phase that invokes SA-14 at deliverable packaging time. |
| **`auditing-subagents/SKILL.md`** | The skill's main catalog. SA-14 is listed in the SA-14 rule section. |
| **`references/anti-patterns.md`** | The SA-1..SA-14 anti-pattern catalog. SA-14 is the packaging-time gate entry. |
