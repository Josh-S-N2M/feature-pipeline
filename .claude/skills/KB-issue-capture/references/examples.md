# Worked Examples — 3 Doctypes Paired to Post-Migration Files

These three examples are paired to the four migrated `Issues/` files produced by
Phase 3 (T3.2–T3.5). They use POST-migration paths and POST-rename `doc_type` values
(per ADR-0049 §Decision §5 and Blueprint §Mechanism Designs D-04).

Each example documents:
- The topic hint that would produce this file
- Classification rationale (why this doctype, not another)
- Frontmatter shape (actual fields from the migrated file)
- Body shape (the structural sections)

For the full structural spec (required fields per state, body skeleton per doctype),
cite by path:
`.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`

---

## Example 1 — Register (Sweep of Multiple Deferred Items)

**Post-migration path**: `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`

### Topic hint that produced this file

> "all the deferred items and open questions from the devcontainer-mcp-provisioning-r1
> feature run before Gate 4 — open items, Won't-Haves, verify-at-execution items,
> kill criteria, risk table items, everything we punted on"

### Classification rationale

**Why register, not analysis**: The hint names multiple items across many categories
from one feature run. There is no single phenomenon to root-cause. The natural output
shape is a categorized table — one section per category, many rows. The triage-criteria
decision tree fires on "SWEEP of MULTIPLE deferred items grouped under one theme" and
resolves to ISSUE-REGISTER.

**Why register, not proposal**: The content is retrospective (what we deferred) rather
than forward-looking (what a future run should do). The register cross-references the
feature's blueprint and design artifacts; it does not propose a new feature run.

### Frontmatter shape

```yaml
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
  - ...
```

Key fields:
- `doc_type: issue-register` — the post-rename canonical value (was `deferral-register`
  pre-migration per F-005)
- `status: open` — back-filled from `draft` by the FR-8 migration
- `since: 2026-05-23` — added by the FR-8 migration per the `open` state's required
  companion field (ISSUE_PER_STATE_REQUIRED_FIELDS)
- `feature_slug: devcontainer-mcp-provisioning-r1` — feature-specific scope
- No `escalates_from` / `escalated_to` — no evolution cross-links; this is a
  standalone register

### Body shape

```
# Deferral Register — `<feature-slug>`

## TL;DR
[Counts: N distinct deferral items across M categories. Summary of what blocks and
what doesn't. Notable patterns.]

## A. <Category Name>
[Table with columns: ID | Item | Source | Why deferred | Re-examination trigger |
Forgetting risk]

## B. <Category Name>
[Same table structure]

...

## N. Cross-references
[Links to sibling Issues/ files and the feature's canonical artifacts]
```

The `devcontainer-mcp-provisioning-r1-deferrals/register.md` file has 15 sections
(A through O), 25 distinct items, and a pattern-observation section (§O) that captures
a project-wide posture on time-based deferral triggers.

---

## Example 2 — Analysis (Deep-Dive into One Phenomenon)

**Post-migration path**: `Issues/adr-placement-rootcause/analysis.md`

(The `Issues/per-agent-design-evaluation-gap/analysis.md` file is also a valid analysis
example; both share the same doctype and body structure. The adr-placement-rootcause
example is chosen here because it additionally demonstrates the evolution cross-link
pattern — `escalated_to: PROPOSAL-adr-placement-rootcause` — pointing to a sibling
proposal file in the same topic folder.)

### Topic hint that produced this file

> "why the ADR placement drift keeps happening — ADR-0036 was ratified but the four
> operational files that enforce ADR placement were never updated; root cause of the
> partial-amendment defect and what files are out of sync"

### Classification rationale

**Why analysis, not register**: The hint names ONE specific phenomenon (the
partial-amendment defect) with a single root cause (the ADR's Architecture Impact
section was incomplete). There is no sweep of multiple items; the output is analytical
narrative. The triage-criteria decision tree fires on "DEEP-DIVE into ONE specific
phenomenon with root-cause analysis" and resolves to ISSUE-ANALYSIS.

**Why analysis, not proposal**: The content is retrospective — it documents what
happened (the drift) and why (the partial amendment). The forward-looking component
(the follow-on feature) is captured in a SEPARATE sibling proposal file at
`Issues/adr-placement-rootcause/proposal.md`, linked via the `escalated_to` cross-link.
This is the sibling-evolution pattern per ADR-0046.

### Frontmatter shape

```yaml
id: ANALYSIS-adr-placement-rootcause
doc_type: issue-analysis
version: 1.0.0
status: open
since: 2026-05-23
feature_slug: devcontainer-mcp-provisioning-r1
generated: 2026-05-23
generated_by: claude (orchestrator) — manual analysis
# Optional evolution cross-link fields (per ADR-0046 / spec §5):
escalated_to: PROPOSAL-adr-placement-rootcause
# escalates_from: <none — this is the root analytical capture>
```

Key fields:
- `doc_type: issue-analysis` — the post-rename canonical value (was `analysis`
  pre-migration per F-005)
- `escalated_to: PROPOSAL-adr-placement-rootcause` — the forward cross-link to the
  sibling proposal. The `status:` of THIS analysis file was NOT changed when the
  proposal was added (per ADR-0046 §Decision §5 — no status mutation by evolution).
- `feature_slug: devcontainer-mcp-provisioning-r1` — which feature run triggered this
  capture; the phenomenon itself is pipeline-wide

### Body shape

```
# <Phenomenon Title>

## Contents
[Checkbox list of sections]

## TL;DR
[The finding in 2-3 sentences. The failure mode. The scope of the gap.]

## 1. Evidence — the chain that produced the gap
### 1.1 [Evidence point]
[Verbatim quotes from artifacts where relevant; file paths with line numbers]
...

## 2. The pattern is broader than the immediate case
[If the phenomenon repeats or generalizes, document the broader pattern here]

## 3. What's missing structurally
[What does the codebase lack that would prevent recurrence?]

## 4. Why this is recurring (the meta-problem)
[Root cause of the root cause, if applicable]

## 5. What this means for the current feature
[Current-state safety assessment — can the pipeline proceed?]

## 6. Recommended remediation paths
### 6.1 Track A — feature-scoped close-out
### 6.2 Track B — pipeline-scoped fixes (separate meta-feature)

## 7. Open questions for the meta-feature
[Questions for the future run to resolve]

## 8. Cross-references
[Links to evidence artifacts, related analyses, ADRs, and evolution cross-links]
```

The `adr-placement-rootcause/analysis.md` demonstrates a full analysis structure:
§1 Background/Evidence (4 sub-sections on causal sites), Root Cause, Implications (4
staleness mechanisms), Recommendations (two coherent end-states), and evolution
cross-links (`escalated_to:` pointing at the sibling `proposal.md`).

---

## Example 3 — Proposal (Future Feature Seed)

**Post-migration path**: `Issues/auditing-family-graduation-review/proposal.md`

### Topic hint that produced this file

> "should we graduate the other auditing-* skills to their own families the way we just
> graduated auditing-mcp — proposal for a future pipeline run to evaluate the whole
> auditing-* family structure"

### Classification rationale

**Why proposal, not analysis**: The hint is forward-looking. It proposes a future
pipeline run to answer a question ("which sub-skills warrant graduation?"), not an
analysis of why something went wrong. The triage-criteria decision tree fires on
"SEEDING a FUTURE FEATURE RUN with a proposed shape" and resolves to ISSUE-PROPOSAL.

**Why proposal, not register**: The content is prescriptive (what the future run should
do) rather than retrospective (what was deferred from the current run). A register
documents items deferred FROM a feature; a proposal documents input TO a future feature.

### Frontmatter shape

```yaml
id: PROPOSAL-auditing-family-graduation-review
doc_type: issue-proposal
status: open
since: 2026-05-23
version: 0.1.0
generated: 2026-05-23
generated_by: claude (orchestrator) — captured from Gate-4 decision
feature_slug: devcontainer-mcp-provisioning-r1
scope: pipeline-wide (not feature-scoped)
mode: report-only
companion_artifacts:
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md (OI-2)
  - .claude/skills/auditing-cc-configs/SKILL.md
  - .claude/skills/auditing-mcp/SKILL.md
  - .claude/skills/auditing-shared/SKILL.md
proposes_future_feature: auditing-family-structure-review-r1 (suggested slug)
```

Key fields:
- `doc_type: issue-proposal` — the post-rename canonical value (was `proposal`
  pre-migration per F-005)
- `proposes_future_feature: auditing-family-structure-review-r1` — the suggested slug
  for the future feature run this proposal seeds. This field is RECOMMENDED for
  `issue-proposal` files (info-severity finding if absent per D-06 advisory).
- `feature_slug: devcontainer-mcp-provisioning-r1` — which feature run triggered the
  capture (the Gate-4 graduation decision)
- No `escalates_from` — this proposal is a standalone seed, not evolved from a prior
  analysis in the same topic folder

### Body shape

```
# Proposal — <Question or Title>

## TL;DR
[The question being proposed for a future run. What this proposal does NOT answer —
it captures the question, not the answer.]

## 1. Precedent — what triggered this proposal
### 1.1 The decision that created the question
[What happened in the current feature run that surfaces this as a future question]
### 1.2 Why the precedent matters for the future
[What the precedent implies for adjacent cases]

## 2. Per-item candidate analysis (inputs for the future run)
[A rubric the future run should apply. A table or structured list with:
 per-candidate assessment against the rubric criteria]

## 3. What the proposed work actually entails
[Sizing the future run: what steps graduation / the proposed change would require]

## 4. Recommended scope for the future pipeline run
[Suggested feature slug. Suggested in-scope. Suggested out-of-scope.
Suggested gating considerations.]

## 5. Why this lives in Issues/ (not in the current feature's working directory)
[Rationale for placement under Issues/ rather than working/feature/<slug>/]

## 6. Cross-references
[Links to the triggering decision, existing skills/artifacts referenced,
and any related Issues/ analyses]
```

The `auditing-family-graduation-review/proposal.md` demonstrates a complete proposal:
§1 captures the Gate-4 precedent decision (OI-2 Path A override), §2 provides a
per-skill candidate table with three graduation criteria, §3 sizes the work per
graduated skill, §4 defines the recommended scope for `auditing-family-structure-review-r1`,
and §5 documents the placement rationale (pipeline-wide scope belongs in `Issues/`).

---

## Summary — When to Use Which Example

| Situation | Refer to |
|---|---|
| User captures a feature-run deferral sweep | Example 1 (register) |
| User captures a root-cause analysis of one pipeline gap | Example 2 (analysis) |
| User captures a proposal for a future feature run | Example 3 (proposal) |
| Analysis matures into a proposal (evolution) | Examples 2 + 3 together (the `escalated_to` / `escalates_from` cross-link pattern) |

For the triage decision ("which doctype does this hint map to?"), see:
`.claude/skills/KB-issue-capture/references/triage-criteria.md`

For the approval prompt wording before each Write, see:
`.claude/skills/KB-issue-capture/references/approval-prompt-rubric.md`
