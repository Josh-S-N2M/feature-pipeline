---
# Universal-required fields (all states including draft)
id: REGISTER-<kebab-topic-slug>
version: 1.0.0
doc_type: issue-register
status: <draft | open | adopted | complete | superseded | wontfix-with-rationale>
feature_slug: <feature-slug>
generated: <ISO-8601-date>
generated_by: <sub-agent-name>

# Per-state companion fields — include the block matching your status value:
#
# status: draft
#   (no additional fields required)
#
# status: open
#   since: <ISO-8601-date>
#
# status: adopted
#   since: <ISO-8601-date>
#   adopted_by_feature_slug: <feature-slug>
#   adopted_at: <ISO-8601-date>
#
# status: complete
#   since: <ISO-8601-date>
#   resolved_by: <description>
#   resolved_at: <ISO-8601-date>
#   resolution_summary: <one-line summary>
#
# status: superseded
#   since: <ISO-8601-date>
#   superseded_by_issue_id: REGISTER-<kebab-topic-slug>
#   superseded_at: <ISO-8601-date>
#
# status: wontfix-with-rationale
#   since: <ISO-8601-date>
#   wontfix_rationale: <rationale>
#   decided_at: <ISO-8601-date>

# Optional cross-link fields (include only when evolution has occurred — per ADR-0046):
# escalates_from: ANALYSIS-<kebab-topic-slug>
# escalated_to: ANALYSIS-<kebab-topic-slug>
# rolled_into_register: REGISTER-<kebab-topic-slug>
---

# Issue Register — `<topic-slug>`

## Contents

Section completion checklist — mark each box `[x]` when the corresponding section is complete.

- [ ] Status
- [ ] Purpose
- [ ] Entries
- [ ] Cross-links
- [ ] Resolution / supersession notes (if applicable)

## Status

<draft | open | adopted | complete | superseded | wontfix-with-rationale> — <ISO-8601-date>

## Purpose

<One paragraph. Describe the set of items this register tracks, the scope from which they were swept, and the mode (report-only or actionable). Example: "Pre-Gate-4 sweep of every item the feature artifacts mark as deferred, out-of-scope, or pending follow-up for `<feature-slug>`. Each entry records what was deferred, why, the source artifact, and the forgetting risk if the item is not re-examined.">

**Counts:** <N> distinct items across <M> categories. <Zero / N> are blocking <gate or milestone>.

---

## Entries

Entries are organized by category. Each table row carries: item ID, the item, its source artifact, why it was deferred or noticed, the re-examination condition, and the forgetting risk if it is not revisited.

### <Category A — descriptive label>

| ID | Item | Source | Why deferred / noticed | Re-examination condition | Forgetting risk |
|---|---|---|---|---|---|
| **A-1** | <item description> | `<artifact-path>` line <N> | <reason> | <event-based trigger — not a time-based trigger> | High / Medium / Low |
| **A-2** | <item description> | `<artifact-path>` | <reason> | <condition> | Low |

### <Category B — descriptive label>

| ID | Item | Source | Why deferred / noticed | Re-examination condition | Forgetting risk |
|---|---|---|---|---|---|
| **B-1** | <item description> | `<artifact-path>` | <reason> | <condition> | Medium |

---

## Cross-links

- `escalates_from`: <id of older sibling doctype file this register evolved from, per ADR-0046; omit if this is a root file>
- `escalated_to`: <id of newer sibling doctype file this register has evolved into, per ADR-0046; omit if no evolution has occurred>
- `rolled_into_register`: <id of a register in a different topic that absorbed related items, per ADR-0050; omit if not applicable>

For the full bidirectional evolution discipline, see `ADR-0046` at
`adrs/ADR-0046-add-new-sibling-file-evolution.md`.

For the per-state companion-field authoritative table and the state lifecycle vocabulary, see:
- **Canonical vocabulary:** `.claude/canonical/doc-types.yaml` (`issue_states`, `issue_doc_types`, `issue_per_state_required_fields`) — the machine source; the validator imports it.
- `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md` — the structural prose companion.
- `ADR-0050` at `adrs/ADR-0050-5-state-issues-vocabulary.md` — the originating decision.

---

## Resolution / supersession notes

<Complete this section only for terminal states: `adopted`, `complete`, `superseded`, or `wontfix-with-rationale`. For `draft` or `open` registers, replace this section body with "N/A — status is <draft|open>.">

<For `adopted`: name the feature run that adopted this register's items and cite `adopted_by_feature_slug`.>
<For `complete`: summarize how the underlying concern was resolved without an adoption pathway; reference `resolved_by` and `resolution_summary`.>
<For `superseded`: cite the newer register's ID from `superseded_by_issue_id` and explain the replacement.>
<For `wontfix-with-rationale`: state the rationale verbatim from `wontfix_rationale` and the decision date.>

---

*End of register.*
