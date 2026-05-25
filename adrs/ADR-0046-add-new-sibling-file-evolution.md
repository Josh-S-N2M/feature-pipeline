---
id: ADR-0046
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0005]
applies_to:
  - issue-capture-mechanism-r1
  - Issues/ outside-pipeline issue surface (project-wide)
  - any future cross-doctype evolution in Issues/
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  When an outside-pipeline issue evolves from one doctype to another
  (analysis matures into proposal; register triggers an analysis), the
  evolution is captured by adding a NEW sibling file in the same topic
  folder with bidirectional escalates_from/escalated_to cross-links. The
  older file's status is NEVER mutated by the evolution. Both writes occur
  in one approved transaction.
---

# ADR-0046: Add-new-sibling-file evolution pattern

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Proposed — 2026-05-23 (issue-capture-mechanism-r1; pending Gate 4 user ratification)

## Context

Outside-pipeline issues mature over time. An `analysis` may surface a recommendation that's ready to become a feature run, at which point a `proposal` is the natural next doctype. A `register` may catalog deferred items; one of those items may warrant its own deeper `analysis`. A `proposal` may be informed by a prior `analysis`. The relationship is many-to-many in principle and one-to-one in practice for any single evolution event.

Two competing approaches exist for capturing such evolution:

1. **Mutate-the-older-doctype.** Take the existing file, change its `doc_type` from `issue-analysis` to `issue-proposal` (and rename the file accordingly), update body content as needed. One file, one history.
2. **Add-new-sibling-file.** Leave the older file unchanged in shape; add a new file alongside it with a new doctype. Both files persist; a cross-link relates them.

The mutate-the-older approach is structurally simpler but has three failure modes:

- **Audit-trail erasure.** The original analysis content is lost (or buried in git history). A reader at time T+1 cannot see what the analysis said at time T without git archaeology.
- **State conflation.** The original analysis may have been at `status: open` (active concern). The mutated proposal may belong at `status: draft`. One file cannot simultaneously hold both.
- **Filename churn.** Per ADR-0051 (per-issue folder model with fixed canonical filenames), changing the doctype means renaming the file. This invalidates any in-flight reference and re-engages git's similarity-index heuristics.

The add-new-sibling approach preserves the audit trail by construction. The older file remains exactly as it was, with one additive amendment: a back-link field (`escalated_to: <newer-id>`) added to its frontmatter. The newer file declares the forward link (`escalates_from: <older-id>`). Both files persist; the relationship is browsable from either side.

The PRD §FR-5 codifies this pattern. PRD §Product Policy Decisions row "Issue evolution pattern" records it as policy. This ADR makes the architectural commitment explicit, defines the transactional semantics, and explains why mutation is rejected.

## Decision

1. **Add-new-sibling-file evolution.** When an issue evolves to a new doctype, the system writes a new file in the same topic folder (per ADR-0051) with `escalates_from: <id-of-older>` in its frontmatter. The older file's status field is NOT mutated. The older file is amended only to add `escalated_to: <id-of-newer>` to its frontmatter.
2. **Bidirectional cross-links.** Both files carry the relationship: the newer declares `escalates_from`; the older declares `escalated_to`. A reader of either file can navigate to the other.
3. **Single approved transaction.** Both writes (the new sibling file + the older file's frontmatter amendment) occur within one approved transaction. The `AskUserQuestion` (per ADR-0047) gates both writes simultaneously; on Approve both are written; on Cancel neither is written.
4. **Write order.** On Approve, the amended (older) file is written first, then the new sibling file. This ordering preserves the back-link before the forward link points at it (defense against partial-write inconsistency).
5. **No status mutation by evolution.** The older file's `status:` field is never changed by evolution. Status changes happen only via `/capture-issue --update <path>` (per ADR-0050's 5-state lifecycle), which is a separate user-initiated workflow.
6. **Multi-step evolution chains.** If a topic folder has `analysis.md` evolving to `proposal.md` and the proposal subsequently triggers a new `register.md`, both edges are recorded by repeating the pattern: `register.md` carries `escalates_from: PROPOSAL-foo`; `proposal.md` is amended to add `escalated_to: REGISTER-foo`. The proposal's prior `escalates_from: ANALYSIS-foo` is untouched. Cross-link fields are lists where multiple evolution events touch the same file.

## Decision Details

| Item | Content |
|---|---|
| Decision | Evolution adds a new sibling file with bidirectional cross-links; older file's status is never mutated by evolution. |
| Why now | The four pre-migration files already include cross-doctype evidence (an analysis that triggered a proposal-seed for THIS feature); without an ADR, the evolution pattern is implicit in the agent body's procedure section and easily lost. |
| Why this | Audit-trail preservation is the load-bearing concern (the four pre-migration files together demonstrate prior work that the project needs to remember); mutation erases that history; the add-sibling pattern is the only mutation-preserving pattern. |
| Known unknowns | (a) Whether `escalates_from` / `escalated_to` should ever support multi-valued forms (a single file evolving from two sources). Current design: lists are allowed but the common case is single-valued. (b) Whether evolution can ever cross topic boundaries. Current design: no — evolution is within-topic only; cross-topic relationships use the `rolled_into_register` field (advisory, per ADR-0050). |
| Kill criteria | If real-world use shows that audit-trail preservation is over-engineered (i.e., older files are rarely revisited after evolution and the cost of maintaining them exceeds the value), revisit. If transactional integrity proves brittle (one write fails, the other succeeds, the two get out of sync), revisit the write-order/transaction model. |

## Rationale

Three load-bearing reasons add-new-sibling wins over mutate-the-older:

1. **Audit trail is the feature.** The non-pollution-contract (Blueprint §Three-Layer Enforcement Architecture) exists because the user repeatedly notices issues that must be remembered. Mutation erases the very thing the mechanism exists to preserve. The older analysis's content, frontmatter, and `status:open` claim are all load-bearing facts about what was true at the time of the analysis; mutation discards them.

2. **Status semantics are doctype-specific.** An analysis at `status: open` (active investigation) has different meaning than a proposal at `status: open` (active proposal awaiting adoption). Mutating the doctype while preserving the status conflates the two semantics. Separating the files separates the semantic spaces.

3. **The transactional pattern is composable.** A single `AskUserQuestion` gating two writes (with all-or-nothing semantics per AC-FR-5-c) is structurally the same as gating one write — same approval surface for the user, same `AskUserQuestion` archetype (per ADR-0047 D-03 archetype 4). The transactional discipline scales to N-step chains without new mechanism.

The decision honors KB-backend-design Principle 4 (errors as first-class — the all-or-nothing write semantics is an explicit, named transactional invariant). It also honors KB-cc-design Principle 3 (enforce when safety-critical — audit-trail preservation is safety-critical for the mechanism's purpose).

## Options Considered

### Option 1: Mutate-the-older-doctype

Take the existing file, change its `doc_type`, rename it, update body content.

**Pros:** One file, one history; no cross-link mechanism needed; simpler agent body.

**Cons:** Audit trail erased (older content/state lost); status semantics conflated; filename churn invalidates referrers; git similarity-index re-engaged; the entire reason the user captures issues (to preserve memory of what was noticed) is undermined.

### Option 2 (Selected): Add-new-sibling-file with bidirectional cross-links

New file alongside the older; older file gets a back-link amendment only.

**Pros:** Audit trail preserved by construction; status semantics distinct per file; no filename churn; cross-link is browsable from either side; transactional discipline composable to N-step chains.

**Cons:** Two writes per evolution; cross-link discipline must be maintained (validator enforces syntactic correctness per ADR-0050); folder accumulates files over time (mitigated: the folder model handles this naturally, and `evidence/` / `updates/` subdirs absorb non-doctype additions).

### Option 3: Add-new-sibling-file without back-link amendment

New file declares `escalates_from`; older file is untouched.

**Pros:** Single write per evolution; older file is truly immutable post-creation.

**Cons:** Cross-link is one-directional; a reader of the older file cannot discover the newer file without scanning the folder; the "browsable from either side" affordance is lost. Rejected — the single back-link amendment is cheap, transactional, and explicitly required by AC-FR-5-a.

### Option 4: Mutate older file's status to `superseded`; cross-link via `superseded_by_issue_id`

Reuse the existing supersession discipline (per ADR-0005) for evolution.

**Pros:** Reuses an established pattern; one terminal state per file.

**Cons:** Evolution is NOT supersession — the older analysis is not invalidated by the newer proposal; both remain valid documents of their respective doctypes. Conflating evolution with supersession would erase the distinction. Rejected as semantic confusion.

## Consequences

### Positive Consequences

- Audit trail preserved by construction. The four pre-migration files (and any future captures) retain their original shape, status, and evidence.
- Evolution chains are composable. A topic folder can accumulate `register → analysis → proposal` (or any subset), each with its own audit trail.
- Cross-link bidirectionality enables browsing from either side. A reader landing on the older analysis can navigate forward; a reader landing on the newer proposal can navigate back.
- The transactional pattern (one AskUserQuestion gates both writes) is reusable for collision-resolution (the `supersede` option in NFR-5 uses the same transactional shape).

### Negative Consequences

- Two writes per evolution event. Mitigated: the AskUserQuestion gates both; the user experiences one approval; the failure modes are bounded (write order + all-or-nothing semantics).
- The validator extension (per ADR-0050) must syntactically validate `escalates_from` and `escalated_to` cross-link fields. Mitigated: the validation is regex-shape only (does the value look like a valid `<DOCTYPE>-<topic-slug>` id?) — referential integrity is not checked.
- Folders accumulate files. Mitigated: the per-topic folder model (per ADR-0051) is designed for this; a folder with `register.md + analysis.md + proposal.md + evidence/agent-roster-impact-matrix.md` is a normal, well-organized accumulation.

### Neutral Consequences

- `git log` history is doubled for evolution events (the older file's amendment plus the new file's creation are two distinct git operations within one logical commit).
- The cross-link fields appear in the validator's optional-field set (per ADR-0050 D-05) but do not appear in any required-companion-field set — they exist only when evolution has occurred.

## Architecture Impact

1. **Layers affected.** Claude Code (the issue-capture-author agent body's evolution-transaction branch; the templates that document the cross-link fields). Backend (the validator extension that syntactically validates the cross-link fields).
2. **Components that change.**
   - issue-capture-author agent body — Phase 1c (evolution-transaction branch) and the AskUserQuestion archetype 4 (evolution-transaction preview).
   - Three templates (issue-register/analysis/proposal-template.md) — document `escalates_from:` and `escalated_to:` as optional cross-link fields.
   - `validate_pipeline_frontmatter.py` — `validate_issue_artifact` adds syntactic validation of `escalates_from`, `escalated_to`, and `rolled_into_register` fields when present.
3. **New dependencies introduced.** None at runtime.
4. **Architectural constraints added.** Any future Issues-touching code MUST treat the older file as immutable apart from the cross-link back-link amendment. The `status:` field of the older file is off-limits to the evolution workflow.

## Implementation Guidance

**For the agent body (CC layer).** The evolution-transaction branch (Blueprint §Sub-Agent Patterns Phase 1c) is invoked when create-mode detects an existing topic folder. The agent:

1. Reads existing doctype files in the folder.
2. Identifies the older doctype the new file relates to.
3. Drafts the new sibling file with `escalates_from: <id-of-older>`.
4. Drafts the older file's amendment: ADD `escalated_to: <id-of-newer>` to frontmatter. Status untouched.
5. Presents the AskUserQuestion archetype 4 (evolution-transaction preview).
6. On Approve: writes the amended older file first, then the new sibling. Both writes complete or neither.
7. On Cancel: writes neither.

**For the validator (Backend layer).** `validate_issue_artifact` syntactically validates the optional cross-link fields when present:

- `escalates_from: <id>` — value matches `<DOCTYPE>-<topic-slug>` regex; minor finding if malformed.
- `escalated_to: <id>` — same syntactic check.
- `rolled_into_register: <id>` — same syntactic check.

Referential integrity (does the referenced file exist?) is NOT validated — the issue would surface in any reader's manual click-through and the cost of cross-file validation exceeds the value.

**Multi-step chains.** If a topic folder accumulates several evolutions, each evolution amends the immediate predecessor only. The agent body identifies "immediate predecessor" as the most-recently-modified existing doctype file in the folder; if multiple candidates exist, the user-confirmed-doctype-classification of the new file determines the predecessor (an `analysis.md` evolves from the existing `register.md`; a `proposal.md` evolves from the existing `analysis.md`).

No procedural detail beyond the above — exact AskUserQuestion wording lives in `KB-issue-capture/references/approval-prompt-rubric.md`.

## Related Information

- Related ADRs:
  - ADR-0051 (per-issue folder model — the layout that makes sibling-files natural)
  - ADR-0052 (three doctypes preserved — the doctype boundaries evolution crosses)
  - ADR-0047 (three-layer enforcement — the AskUserQuestion that gates both writes)
  - ADR-0050 (5-state lifecycle vocabulary — cross-link fields are optional-when-present)
  - ADR-0005 (supersession discipline — distinct from evolution; supersession DOES mutate older file's status)
- Referenced specs / docs: PRD §FR-5 (add-new-sibling-file evolution); PRD §Product Policy Decisions row "Issue evolution pattern"; PRD §NFR-6 (audit-trail preservation via supersession discipline — related, not conflated); Blueprint §Add-New-Sibling Evolution Pattern.
- Issues / PRs: `Issues/issue-capture-mechanism/proposal.md` (the proposal seeded by analyses; demonstrates the pattern at the input boundary of THIS feature).
- Related KBs: KB-backend-design (Principle 4 — errors as first-class for the all-or-nothing transactional semantics); KB-cc-design (Principle 3 — enforce when safety-critical).
