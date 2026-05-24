# Triage Criteria — Doctype Classification Rubric

Given a captured-issue topic hint, classify it into one of three doctypes:
`issue-register` / `issue-analysis` / `issue-proposal`.

This is **discipline content** — the "this kind of topic goes to this doctype" rule.
It does NOT codify the structural shape of each doctype (required frontmatter fields,
body skeleton). That structural codification lives in:
- `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`
- `.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md`
- `.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md`
- `.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md`

---

## Decision Tree

```
Start: what is the primary character of the topic hint?
│
├─ Is this a SWEEP of MULTIPLE deferred or open items grouped under one theme?
│  Examples: "all the things we deferred in the X feature run",
│             "open questions we never resolved in Y", "items to verify before Z ships"
│  └─ YES → ISSUE-REGISTER
│            The categorized table format (sweep by category) fits.
│            Use when: the hint names a feature run + "deferrals" / "open items" /
│            "known-unknowns" / "kill criteria". Also: any pre-Gate-N sweep whose
│            output is primarily tabular.
│
├─ Is this a DEEP-DIVE into ONE specific phenomenon with root-cause analysis?
│  Examples: "why did the pipeline fail to catch cross-file divergence",
│             "what caused the ADR placement drift", "root cause of X pattern"
│  └─ YES → ISSUE-ANALYSIS
│            The evidence → root-cause → implications → recommendations flow fits.
│            Use when: the hint is about understanding WHY something happened or
│            WHY a gap exists. The output is analytical, not tabular.
│
├─ Is this SEEDING a future feature run with a proposed shape?
│  Examples: "should we graduate the auditing-* skill family",
│             "proposal to fix ADR placement mechanism",
│             "future feature idea for agent-roster design discipline"
│  └─ YES → ISSUE-PROPOSAL
│            The TL;DR → proposed feature → motivation → open questions flow fits.
│            Use when: the hint proposes a future pipeline run. The output is a
│            feature seed, not a description of the present state.
│            Note: proposals SHOULD carry a `proposes_future_feature:` slug field
│            (advisory per D-06 — info-severity finding if absent).
│
└─ AMBIGUOUS (hint matches two or more branches, or matches none clearly)
   └─ Use the Change-doctype escape hatch in the approval prompt (Archetype 1,
      option 2). Show the agent's first-guess classification with rationale; offer
      the user the option to re-route before any write occurs.
```

---

## Three Doctype Definitions (discipline summary)

### ISSUE-REGISTER (`issue-register`)

**Character**: Sweep. Multiple items. Tabular. One theme, many rows.

**Canonical signal words in hint**: "deferrals", "open items", "known-unknowns",
"kill criteria", "pre-Gate sweep", "everything we punted on", "verify-at-execution",
"Won't-Haves".

**Body shape (structural — cite template by path)**:
The body is a set of categorized tables (one section per category). Each row has an item
ID, description, source artifact, why deferred, re-examination trigger, and forgetting
risk. See the template:
`.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md`

**Key classification distinguisher**: Multiple items in one sweep. If the hint names a
single phenomenon for deep investigation, that is an analysis, not a register.

---

### ISSUE-ANALYSIS (`issue-analysis`)

**Character**: Deep-dive. One phenomenon. Analytical narrative with evidence and root cause.

**Canonical signal words in hint**: "root cause", "why did X happen", "gap analysis",
"how did Y occur", "why the pipeline doesn't catch Z", "investigating X", "post-mortem".

**Body shape (structural — cite template by path)**:
TL;DR → evidence sections (numbered) → root cause → implications → recommendations →
open questions → cross-references. The content is analytical prose, not tables.
See the template:
`.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md`

**Key classification distinguisher**: One phenomenon, one root cause. If the hint is a
list of disparate items, that is a register. If the hint proposes a future pipeline run,
that is a proposal.

---

### ISSUE-PROPOSAL (`issue-proposal`)

**Character**: Forward-looking. Proposes a future pipeline run or structural change.

**Canonical signal words in hint**: "should we", "proposal to", "future feature for",
"seeding the next run on", "recommend a feature run that", "we should consider opening
a pipeline run for".

**Body shape (structural — cite template by path)**:
TL;DR → precedent or motivation → proposed feature scope → per-item analysis → recommended
scope for the future run → cross-references. The content is prescriptive and forward-looking.
See the template:
`.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md`

**Key classification distinguisher**: The output is a SEED for a future feature run — it
proposes what the next run should do, not what happened or what the current state is. If
the hint is retrospective ("what happened"), that is an analysis.

---

## Worked Classification Examples

| Topic hint | First-pass classification | Rationale |
|---|---|---|
| "all the deferrals from the devcontainer-mcp-provisioning feature run" | `issue-register` | A sweep of multiple items from one feature run; tabular format fits. |
| "why the pipeline can't tell whether it evaluated all agents for a feature" | `issue-analysis` | One specific phenomenon (the evaluation gap); root-cause analysis fits. |
| "why ADR-0036 placement drift happened and what files are out of sync" | `issue-analysis` | One specific phenomenon (partial-amendment defect); evidence + root-cause + implications fits. |
| "should we graduate all the auditing-* sub-skills to their own families" | `issue-proposal` | Proposes a future pipeline run; the output seeds that run. |
| "open questions from the current feature run that block Gate 4" | `issue-register` | Multiple items; tabular sweep fits. The "blocks Gate 4" element raises urgency but doesn't change the doctype. |
| "the agent design discipline gap that the pipeline keeps missing" | Ambiguous (analysis or register) | If the hint is about one gap's root cause, classify as analysis. If it's a sweep of multiple missing steps, classify as register. Use Change-doctype to confirm. |

---

## The Change-Doctype Escape Hatch

If the agent's first-guess classification is wrong, the user can re-route via the
Approval Prompt (Archetype 1, option 2: Change-doctype). This loops back through the
triage rubric with the user's correction, and presents a fresh approval prompt with the
new doctype's drafted content.

The escape hatch is the correct recovery path — it is NOT a failure of the triage rubric.
Ambiguous hints legitimately exist, and the rubric is a first-pass guide, not an oracle.

The doctype change is always surfaced before any Write call. The user never needs to
correct a written file's doctype after the fact.

---

## Cross-References

- **examples.md** (sibling file): full worked examples for each doctype, paired to
  real post-migration files. See:
  `.claude/skills/KB-issue-capture/references/examples.md`
- **Structural templates** (not inlined here per ADR-0049):
  `.claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md`
  `.claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md`
  `.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md`
- **ADR-0045**: Three doctypes preserved — the rationale for keeping register / analysis /
  proposal as three distinct doctypes rather than collapsing them.
- **ADR-0049**: Structural-vs-discipline KB split — why this classification rubric lives
  in KB-issue-capture and not in the templates.
- **D-03 approval-prompt-rubric**: The Change-doctype option is Archetype 1 option 2.
  See: `.claude/skills/KB-issue-capture/references/approval-prompt-rubric.md`
