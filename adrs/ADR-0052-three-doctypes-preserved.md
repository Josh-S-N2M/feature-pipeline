---
id: ADR-0045
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: []
applies_to:
  - issue-capture-mechanism-r1
  - Issues/ outside-pipeline issue surface (project-wide)
  - the three new doctype templates under KB-documentation-criteria
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Outside-pipeline issues preserve three structurally distinct doctypes —
  register, analysis, proposal — rather than unifying them into a single
  generic "issue" shape. Each doctype gets its own structural template;
  unification is rejected because the empirical body shapes diverge (CP-004).
---

# ADR-0045: Three doctypes preserved as distinct (register / analysis / proposal)

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

When designing the outside-pipeline issue-capture mechanism, a natural simplification question arose: do we need three separate doctypes (`register`, `analysis`, `proposal`) or could a single generic `issue` doctype suffice, with the body shape determined by free-form authoring?

The empirical evidence from the four pre-migration files (codebase-analysis CP-004) answers this question. The three doctypes have observably distinct body shapes:

- **Register** (`Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`): TL;DR + tabular sweep with columns `ID | Item | Source | Why deferred | Re-examination trigger | Forgetting risk`. The body is structured for at-a-glance scanning of many items.
- **Analysis** (`Issues/analysis-per-agent-design-evaluation-gap.md`, `Issues/analysis-adr-placement-rootcause.md`): TL;DR + numbered evidence sections (1. Evidence with subsections 1.1, 1.2, ...) + implications + open questions. The body is structured for deep-dive into one phenomenon.
- **Proposal** (`Issues/proposal-auditing-family-graduation-review.md`, `Issues/issue-capture-mechanism/proposal.md`): TL;DR + prose proposal + adoption-guidance. The body is structured for future-feature seeding (with the `proposes_future_feature:` frontmatter field on two precedents — F-006).

These are not stylistic variations of one shape. They serve different cognitive jobs: scan-many-items, deep-dive-one-phenomenon, seed-future-work. Forcing them into a unified template would either drop structural signal (the table column headers, the numbered evidence sections, the adoption-guidance subhead) or create a permissive template that codifies none of them — which is structurally equivalent to having no template at all.

The PRD §Product Policy Decisions row "Doctype preservation" already records this as a policy decision. This ADR makes the architectural commitment explicit.

## Decision

1. **Three distinct doctypes preserved.** `issue-register`, `issue-analysis`, and `issue-proposal` are three first-class doctypes, each with its own canonical filename (per ADR-0044), its own structural template under `KB-documentation-criteria/references/templates/`, and its own validator-enforced frontmatter shape.
2. **No unified `issue` doctype.** The design explicitly rejects unification. A future captured issue MUST be classified into one of the three.
3. **Triage rubric in `KB-issue-capture/references/triage-criteria.md`.** When the doctype is ambiguous, the rubric (authored at Plan stage) specifies how the issue-capture-author classifies. The four-option `AskUserQuestion` (per ADR-0047) gives the user a `Change-doctype` option for explicit re-classification.
4. **`evidence/` and `updates/` subdirectories are NOT doctypes.** Files under those subdirectories carry no doctype constraint (per ADR-0044). They are not validated as doctype files and may carry any shape. They exist to support, not to replace, a doctype file in the same topic folder.

## Decision Details

| Item | Content |
|---|---|
| Decision | Preserve three distinct doctypes (register, analysis, proposal); reject unification. |
| Why now | The three new structural templates (FR-6) and the validator extension (FR-7) both encode the three-doctype shape; without an ADR, the decision is implicit in the templates and easily lost in future refactors. |
| Why this | The three body shapes (CP-004) serve different cognitive jobs and have observable structural differences; unification would either lose signal or codify nothing. The proposal seed and four pre-migration files all map cleanly to one of the three. |
| Known unknowns | (a) Whether a fourth doctype emerges with real-world use; if so, an amendment ADR extends the set. (b) Whether the boundary between `register` and `analysis` becomes blurry in some captures; the four-option `AskUserQuestion` includes `Change-doctype` as the user-driven boundary-resolution mechanism. |
| Kill criteria | If after twelve months of real-world capture, three or more captures fall genuinely between two doctypes (irrespective of user `Change-doctype` resolution), revisit. If a fourth doctype proves necessary, amendment (not supersession) extends the set. |

## Rationale

Three load-bearing reasons three doctypes win over one:

1. **The three jobs are different.** Scanning a register of deferred items is a different cognitive task than reading a root-cause analysis. Reading a proposal-for-future-feature is a different task again. Templates that reflect those tasks help the reader; templates that abstract over them help no one.
2. **The empirical precedent is unambiguous.** Four files, three doctypes, three observably different shapes. The body-shape divergence is not stylistic accident — it tracks the underlying cognitive job. Codifying the three shapes preserves what the four files already demonstrate.
3. **Validator dispatch is cleaner per-doctype.** The FR-7 extension (per ADR-0050 / D-10) adds per-doctype rules (e.g., `proposes_future_feature` advisory check on issue-proposal only). A unified doctype would require runtime sniffing of body shape to apply doctype-specific rules — wrong direction.

The decision honors KB-cc-design Principle 5 (one source of truth): each doctype has one template; the template encodes the shape; the validator enforces the frontmatter; the agent body classifies and writes.

## Options Considered

### Option 1: Single unified `issue` doctype

One template, one validator branch, one frontmatter shape.

**Pros:** Simpler enum (one value); one template to maintain; the agent body doesn't classify (no triage rubric needed).

**Cons:** Loses the three distinct body shapes documented in CP-004; readers can't predict the body from the doctype; doctype-specific frontmatter rules (`proposes_future_feature` for proposals; tabular structure for registers) become awkward conditional logic in the validator; the empirical precedent of four files at three shapes is suppressed.

### Option 2 (Selected): Three distinct doctypes preserved

`issue-register`, `issue-analysis`, `issue-proposal` — each with its own template and validator branch.

**Pros:** Matches empirical precedent; doctype-specific frontmatter rules are clean per-doctype branches; readers know the body shape from the filename; validator dispatch is simple.

**Cons:** Three templates to maintain; agent body must classify (triage rubric needed); user gets four options at the AskUserQuestion (Approve / Approve-with-edits / Change-doctype / Cancel) rather than three.

### Option 3: Two doctypes — `report` (subsumes register + analysis) and `proposal`

Unify register and analysis (both are "report what is true now") and keep proposal distinct (because it has `proposes_future_feature:`).

**Pros:** Slightly fewer doctypes; still preserves the proposal signal.

**Cons:** Conflates the tabular-scan shape with the deep-dive shape (the most divergent pair of the three); readers lose the at-a-glance scan affordance for registers; the `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` precedent would not map cleanly into the unified shape.

## Consequences

### Positive Consequences

- Three structural templates codify the three observed shapes; new captures get template-guided authoring.
- Doctype-specific frontmatter rules (e.g., `proposes_future_feature` advisory) are validator-enforceable at the right granularity.
- Future readers see the doctype from the filename; cognitive load is lower than abstract `issue.md` would impose.
- Future evolution between doctypes (per ADR-0046) becomes the load-bearing mechanism for "this issue matured"; without three distinct doctypes, evolution has nothing to evolve into.

### Negative Consequences

- Triage discipline becomes a load-bearing concern. The `KB-issue-capture/references/triage-criteria.md` rubric (authored at Plan stage) must be unambiguous enough for the agent to classify reliably. Mitigation: the `Change-doctype` option in the AskUserQuestion gives the user explicit override.
- Three templates to maintain (vs. one). Mitigation: each template is short (~30-60 lines per Blueprint §Templates) and codifies a body skeleton; maintenance load is low.
- The fixed set of three is closed (per ADR-0044). A fourth doctype requires an amendment ADR. Mitigation: deliberate — the three doctypes are grounded in empirical precedent; surfacing a fourth is itself architectural news.

### Neutral Consequences

- The 4-option AskUserQuestion (Approve / Approve-with-edits / Change-doctype / Cancel) per AC-FR-1-b matches the maximum option count of Claude Code's AskUserQuestion primitive. Verified by KB-cc-platform documentation.

## Architecture Impact

1. **Layers affected.** Claude Code (the three templates, the agent body that classifies, the KB-issue-capture triage rubric). Backend (the validator extension that dispatches per-doctype rules).
2. **Components that change.**
   - 3 new templates under `KB-documentation-criteria/references/templates/`.
   - 1 new spec `issue-doctypes-spec.md` under the same KB.
   - `KB-issue-capture/references/triage-criteria.md` (the doctype classification rubric).
   - issue-capture-author agent body (Phase 1 classification step).
   - `validate_pipeline_frontmatter.py` (the per-doctype branches in `validate_issue_artifact`).
3. **New dependencies introduced.** None at runtime.
4. **Architectural constraints added.** Any future outside-pipeline doctype must either (a) extend the set via an amendment ADR, or (b) live as a non-doctype artifact under `evidence/` or `updates/`. The closed set is deliberate.

## Implementation Guidance

**For template authors (CC layer).** Each template (issue-register, issue-analysis, issue-proposal) codifies the body skeleton per CP-004 plus frontmatter per ADR-0050 (5-state lifecycle) and ADR-0032 (universal-required feature_slug). Templates are structural-only per ADR-0049 — no triggering discipline.

**For the agent body (CC layer).** Classification proceeds per the triage-criteria rubric (Plan-stage authored). On ambiguity, the conservative default is the lower-scope-cost doctype (register < analysis < proposal). The four-option AskUserQuestion lets the user override.

**For the validator extension (Backend layer).** `validate_issue_artifact` branches on `doc_type` and applies per-doctype rules (e.g., advisory `proposes_future_feature` on issue-proposal only; tabular body shape is NOT validated structurally — bodies are out of scope for the validator).

## Related Information

- Related ADRs:
  - ADR-0044 (per-issue folder model — the filesystem layout for the three doctypes)
  - ADR-0046 (add-new-sibling-file evolution — operates across doctype boundaries)
  - ADR-0049 (structural-vs-discipline KB split — templates here, discipline in KB-issue-capture)
  - ADR-0050 (5-state lifecycle vocabulary — applies uniformly across doctypes)
- Referenced specs / docs: PRD §FR-6 (three new templates); PRD §Product Policy Decisions row "Doctype preservation"; codebase-analysis CP-004 (three doctype body shapes); F-005 (doc_type naming drift requires FR-8 migration); F-006 (proposes_future_feature precedents on proposal doctype).
- Issues / PRs: `Issues/issue-capture-mechanism/proposal.md` (the proposal-doctype seed).
- Related KBs: KB-cc-design (Principle 5); KB-documentation-criteria (template-only structural codification); KB-issue-capture (triage discipline, not in KB-documentation-criteria).
