---
id: ADR-0050
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0008, ADR-0032]
applies_to:
  - issue-capture-mechanism-r1
  - Issues/ outside-pipeline issue surface (project-wide)
  - the validator extension at .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py
  - any future outside-pipeline issue-capture lifecycle
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Outside-pipeline Issues/*.md files carry a 5-state lifecycle vocabulary
  (draft → open → adopted | complete | superseded | wontfix-with-rationale)
  enforced as a fourth category in the existing validator
  (alongside GATED 5-state / ANALYSIS-LOG 3-state / ADR 4-state-no-draft).
  This vocabulary is parallel-but-distinct from the intra-pipeline 4-state
  issues-ledger.json vocabulary (per ADR-0008). The two vocabularies share
  three literal state-name strings (open, superseded, wontfix-with-rationale)
  but operate on disjoint entities with disjoint ID prefixes and never share
  IDs. Per-state required companion fields are codified in
  ISSUE_PER_STATE_REQUIRED_FIELDS; proposes_future_feature is advisory.
---

# ADR-0050: 5-state Issues vocabulary distinct from intra-pipeline 4-state ledger

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

The project already maintains an intra-pipeline 4-state issue-tracking vocabulary captured verbatim in `KB-review-disciplines/references/issue-lifecycle.md` (per ADR-0008): `open → resolved | wontfix-with-rationale | superseded`. This vocabulary applies to `working/feature/<slug>/issues-ledger.json` records — issues raised by pipeline reviewers (DR / AA / CA prefixes; codebase-analysis VE-001).

The outside-pipeline issue-capture mechanism introduces a NEW lifecycle that overlaps with the intra-pipeline ledger by literal state-name string but is semantically distinct in entity, scope, and lifecycle:

- **Entity.** Intra-pipeline: a reviewer-raised issue inside one pipeline run. Outside-pipeline: a captured `Issues/<topic>/<doctype>.md` file that persists across pipeline runs and is the project's memory of noticed-but-out-of-scope concerns.
- **Scope.** Intra-pipeline: feature-scoped (lives in `working/feature/<slug>/`). Outside-pipeline: project-scoped (lives in `Issues/`).
- **Lifecycle.** Intra-pipeline: created → resolved-within-this-run (or wontfix-with-rationale, or superseded). Outside-pipeline: drafted → open-for-future-consideration → either adopted (a feature run picked it up), completed (the underlying concern resolved without a feature run), superseded (a newer file replaces it), or wontfix-with-rationale (deliberately not addressed).

Five state values are required for the outside-pipeline lifecycle:

- `draft` — newly-captured; the agent has written the file but the user may revise.
- `open` — actively-tracked; the issue is real and warrants future attention.
- `adopted` — a feature run is in flight or has shipped that addresses this issue.
- `complete` — the underlying concern is resolved without an adoption pathway.
- `superseded` — a different file replaces this one as the canonical record.
- `wontfix-with-rationale` — deliberate decision not to address.

The two vocabularies share three literal state-name strings — `open`, `superseded`, `wontfix-with-rationale`. The semantic differences are sufficient (different entity, different ID prefix structure) that the literal overlap is a feature, not a bug: a reader who knows the intra-pipeline vocabulary recognizes `superseded` immediately in the outside-pipeline vocabulary; the meaning is consistent across both ("this record has been replaced by another"). The two vocabularies never share IDs because the ID prefixes are disjoint: intra-pipeline uses `I-<DR|AA|CA>-NNN`; outside-pipeline uses `<DOCTYPE>-<topic-slug>` (e.g., `ANALYSIS-per-agent-design-evaluation-gap`).

The validator (per ADR-0050 / D-10) enforces this separation structurally: the 5-state vocabulary is consulted ONLY inside `validate_issue_artifact` (the new fourth category branch); the existing GATED/ANALYSIS/ADR validators never see the issue states. Existing pipeline doc_types (`prd`, `blueprint`, etc.) continue to validate against their existing 3-tier vocabularies per ADR-0032's three-tier policy (GATED 5-state / ANALYSIS-LOG 3-state / ADR 4-state-no-draft); the new vocabulary is a FOURTH category.

The PRD §FR-7 codifies the validator extension. PRD §Product Policy Decisions row "Issue-file lifecycle vocabulary" records the 5-state policy. PRD §NFR-8 codifies backward compatibility (zero false positives, zero false negatives on existing pipeline doc_types). This ADR makes the architectural commitment explicit, captures the parallel-but-distinct relationship to ADR-0008, codifies the per-state required-companion-field rules (D-05), and codifies the advisory posture for `proposes_future_feature:` (D-06).

## Decision

1. **5-state lifecycle vocabulary** for outside-pipeline `Issues/<topic>/<doctype>.md` files: `draft → open → adopted | complete | superseded | wontfix-with-rationale`.
2. **Parallel-but-distinct from ADR-0008's intra-pipeline 4-state ledger.** The two vocabularies share three literal state-name strings (`open`, `superseded`, `wontfix-with-rationale`) but operate on disjoint entities with disjoint ID prefixes. They MUST NEVER share IDs. No automated cross-reference is introduced between the two.
3. **Validator enforces as a fourth category.** `validate_pipeline_frontmatter.py` gains `ISSUE_DOC_TYPES = {issue-register, issue-analysis, issue-proposal}`, `ISSUE_STATES = {draft, open, adopted, complete, superseded, wontfix-with-rationale}`, and `ISSUE_PER_STATE_REQUIRED_FIELDS` (a module-level dict). The new branch is invoked only when `doc_type ∈ ISSUE_DOC_TYPES`; existing doc_types continue through their existing branches with byte-identical behavior (per NFR-8).
4. **Per-state required companion fields** (per Blueprint §Mechanism Designs D-05, shared input from design-cc to design-backend):
   - `draft`: universal-required only (id, version, doc_type, status, feature_slug, generated, generated_by).
   - `open`: draft set + `since` (ISO-8601 date).
   - `adopted`: open set + `adopted_by_feature_slug` + `adopted_at` (ISO-8601 date).
   - `complete`: open set + `resolved_by` + `resolved_at` + `resolution_summary`.
   - `superseded`: open set + `superseded_by_issue_id` + `superseded_at`. Mirrors ADR-0005 supersession discipline; uses a DISTINCT field name (`superseded_by_issue_id`) from ADR-0005's `superseded_by` to preserve category separation (per Q-BE-3 resolution).
   - `wontfix-with-rationale`: open set + `wontfix_rationale` + `decided_at`.
5. **Optional cross-link fields** (validated syntactically when present, never required):
   - `escalates_from: <id>` (per ADR-0046).
   - `escalated_to: <id>` (per ADR-0046).
   - `rolled_into_register: <id>` (advisory; topic-crossing relationship).
6. **`proposes_future_feature:` is advisory.** When `doc_type == issue-proposal` and `proposes_future_feature` is absent, the validator emits an `info`-severity finding. When present, accept any string value; no format enforcement. Two existing precedents diverge in field shape (one suggested-slug, one fixed-slug per F-006); strict enforcement would invalidate one without value. The advisory posture is upgradable to `blocker` in a later ADR if real-world use shows the field becomes load-bearing.
7. **ID derivation rule.** Frontmatter `id` is derived from path per ADR-0051: `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>`. The validator verifies this match.

## Decision Details

| Item | Content |
|---|---|
| Decision | 5-state vocabulary for Issues/ files (parallel-but-distinct from ADR-0008's 4-state ledger); validator fourth category branch; per-state required companion fields; `proposes_future_feature` advisory. |
| Why now | The validator extension (FR-7) is the only mechanism that enforces the vocabulary; without an ADR, the vocabulary is implicit in the validator constants and easily lost in future refactors. The four pre-migration files (FR-8 migration target) need a vocabulary to back-fill to; this ADR is that vocabulary. |
| Why this | Five states reflect the actual lifecycle of outside-pipeline issues (the four pre-migration files demonstrate at least four distinct states already; the fifth — `adopted` — emerges from the proposal-as-prior-context handoff per ADR-0048). The parallel-but-distinct relationship to ADR-0008 honors PRD §Product Policy Decisions row 2's explicit non-merge stance; the literal-string overlap is a learnability feature, not a coupling defect. Per-state companion-field rules mirror ADR-0005's existing supersession-discipline pattern; the advisory posture on `proposes_future_feature` honors the two divergent precedents (F-006). |
| Known unknowns | (a) Whether the field names (e.g., `adopted_by_feature_slug` vs. `adopted_in_feature_slug`) prove ergonomic in practice. The names are designed for symmetry (each terminal state has one back-link field) but real-world use may surface preferences. Amendment is cheap (validator constants change; templates change). (b) Whether `rolled_into_register` becomes load-bearing or stays advisory. Current posture: advisory; syntactic-only check. (c) Whether the `proposes_future_feature` advisory check ever needs to become enforced. Current posture: advisory; upgradable later. |
| Kill criteria | If the literal-string overlap between the two vocabularies causes real-world confusion (e.g., a contributor accidentally cross-references an `Issues/` file ID with an `issues-ledger.json` ID), revisit whether the overlap is worth the learnability gain. If the per-state field set proves over-constrained in real-world use (e.g., adopted captures that don't have a feature_slug yet), the field names and severity can be adjusted via amendment. |

## Rationale

Three load-bearing reasons the 5-state vocabulary wins over alternatives:

1. **The lifecycle is genuinely 5-state.** Outside-pipeline issues are not simply "open or resolved." A captured analysis may be adopted by a feature run (`adopted`), completed without a feature run (`complete`), or replaced by a newer analysis (`superseded`). The intra-pipeline 4-state vocabulary collapses `adopted` and `complete` into a single `resolved` state, which loses the signal "this issue led to a future feature run." Preserving the distinction is load-bearing for the proposal-to-feature handoff (per ADR-0048).

2. **The validator dispatch is structurally clean.** Adding a fourth category branch (`ISSUE_DOC_TYPES → validate_issue_artifact`) preserves the existing per-category dispatch pattern (GATED / ANALYSIS / ADR — VE-003) without disturbing it. The outer dispatch (line 365-371; VE-004) is unchanged. NFR-8 backward compatibility is trivially preserved by construction.

3. **The parallel-but-distinct discipline preserves both audit trails.** ADR-0008's intra-pipeline ledger captures within-run review discipline; this ADR's outside-pipeline vocabulary captures across-run memory. Neither subsumes the other; both are needed; the two are disjoint by entity, ID prefix, and lifecycle. The literal-string overlap (`open`, `superseded`, `wontfix-with-rationale`) is a learnability feature — readers who know one vocabulary recognize the shared semantics in the other without re-learning.

The decision honors KB-backend-design Principle 2 (hexagonal port reuse — `make_finding` is the existing port; the new branch is a new adapter producing through it) and Principle 4 (errors as first-class — the severity vocabulary is unchanged; new finding fields are not introduced). It also honors NFR-8 (structural + empirical backward compatibility per Blueprint §Verification Strategy regression-corpus procedure).

## Options Considered

### Option 1: Reuse ADR-0008's 4-state vocabulary verbatim

`open → resolved | wontfix-with-rationale | superseded`. No new vocabulary.

**Pros:** Single vocabulary; no parallel-but-distinct discipline to maintain; readers learn one set of states.

**Cons:** Conflates `adopted` (a feature run is in flight) and `complete` (the concern is resolved without a feature run); loses the signal for proposal-to-feature handoff; forces the validator to either (a) reuse the existing ANALYSIS/LOG 3-state validator (which lacks `wontfix-with-rationale`) or (b) abandon the per-doc-type 3-tier policy from ADR-0032. Rejected on semantic-conflation grounds.

### Option 2 (Selected): New 5-state vocabulary parallel-but-distinct from ADR-0008's 4-state

`draft → open → adopted | complete | superseded | wontfix-with-rationale`. Validator fourth category.

**Pros:** Captures the genuine lifecycle including `adopted`; preserves per-doc-type 3-tier dispatch (this is a NEW fourth category, not a modification of an existing one); literal-string overlap is learnability-positive; NFR-8 trivially preserved.

**Cons:** Two vocabularies to remember (mitigated by the literal overlap of three state names); per-state companion-field rules add validator complexity (mitigated by module-level constants per D-05).

### Option 3: Three-state vocabulary (draft → open → terminal)

Collapse `adopted`, `complete`, `superseded`, `wontfix-with-rationale` into a single `terminal` state with a free-form rationale.

**Pros:** Fewest states; least validator complexity.

**Cons:** Loses every meaningful distinction in the terminal half (adopted vs. complete vs. superseded vs. wontfix); rationale becomes the only differentiator and rationale is free-form (unenforceable); planning-mode plan's 3-state proposal was specifically rejected at intent-clarification Gate 1 by the user. Rejected.

### Option 4: Six-state vocabulary (split `adopted` into `adoption-pending` and `adopted`)

Adds a state for "a feature run has been authorized but has not started."

**Pros:** Finer granularity on the adoption pathway.

**Cons:** The signal is captured by `proposes_future_feature:` on `issue-proposal` (advisory) plus the orchestrator's actual start of the run; a separate state adds validator complexity for low signal. Rejected — the 5-state vocabulary's `adopted` covers both "authorized" and "in flight" sufficiently.

## Consequences

### Positive Consequences

- The lifecycle is faithful to the actual workflow; `adopted` vs. `complete` distinction is preserved.
- The proposal-as-prior-context handoff (per ADR-0048) has a natural state to transition to (`adopted` when the proposal seeds a feature run).
- Per-state companion fields make terminal states self-describing: a reader of an `adopted` file knows which feature run picked it up; a reader of a `superseded` file knows which file replaced it.
- The validator extension is structurally clean (fourth category branch; no modification of existing branches; NFR-8 trivially preserved).
- The parallel-but-distinct discipline preserves both audit trails (intra-pipeline ledger via ADR-0008; outside-pipeline issues via this ADR) without conflation.

### Negative Consequences

- Two vocabularies to learn (intra-pipeline 4-state and outside-pipeline 5-state). Mitigation: literal-string overlap (`open`, `superseded`, `wontfix-with-rationale`) carries semantics across; the distinct states (`draft`, `adopted`, `complete`) are well-named for self-explanation.
- Per-state companion-field rules add validator complexity. Mitigation: module-level constant `ISSUE_PER_STATE_REQUIRED_FIELDS` (per Blueprint §Backend Design §5) keeps the rules unit-testable in isolation; mirrors the existing ADR-0005 `superseded_by` enforcement pattern.
- The `proposes_future_feature` advisory posture leaves a gap if a future automation expects the field reliably. Mitigation: D-05's independent `adopted_by_feature_slug` requirement on `status:adopted` provides the load-bearing back-link; the advisory `proposes_future_feature` is a forward-pointer signal, not a back-link.

### Neutral Consequences

- The validator's existing 3-tier per-doc-type vocabulary policy (per ADR-0032) gains a fourth tier (issue 5-state); the policy framing in shared-conventions.md may want a brief update noting the fourth category. This is a minor documentation cleanup, not an architectural concern.
- The `since` field is now required on every `open`-state issue file (and back-filled by FR-8 migration). Real-world content includes the four migrated files at `status:open` with `since: <date>`.

## Architecture Impact

1. **Layers affected.** Backend (the validator extension is the canonical enforcer). Claude Code (the templates document the vocabulary; the issue-capture-author agent body's update-mode applies state transitions).
2. **Components that change.**
   - `validate_pipeline_frontmatter.py` — `ISSUE_DOC_TYPES`, `ISSUE_STATES`, `ISSUE_PER_STATE_REQUIRED_FIELDS` module-level constants; `validate_issue_artifact(fm, path)` function; fourth-category branch inside `validate_pipeline_artifact` (or via extending `doc_type_category` to return `"issue"` per Q-BE-5 resolution).
   - Three new templates (issue-register/analysis/proposal-template.md) — frontmatter section documents the vocabulary and per-state companion fields.
   - `issue-doctypes-spec.md` — codifies the vocabulary and the per-state required-field table as the authoritative structural spec.
   - `KB-issue-capture/references/triage-criteria.md` — documents how state transitions occur in the agent body.
   - smoke_test_auditing_shared.py — extended with regression-test fixtures per Blueprint §Backend Design §7.
3. **New dependencies introduced.** None at runtime. The validator extension is pure-stdlib.
4. **Architectural constraints added.** Any future change to the issues vocabulary MUST either (a) extend it via an amendment ADR (e.g., a sixth state), or (b) supersede this ADR with a replacement vocabulary. Any change to the per-state required companion fields is similarly amendment-bound. The validator's `ISSUE_STATES` set is the canonical source of truth.

## Implementation Guidance

**For the validator extension (Backend layer).** The new branch lives inside `validate_pipeline_artifact`, dispatched by `doc_type ∈ ISSUE_DOC_TYPES`. The function `validate_issue_artifact(fm, path)`:

1. Checks `status ∈ ISSUE_STATES`; emits a `blocker` finding on miss with the expected vocabulary.
2. For the declared status, iterates `ISSUE_PER_STATE_REQUIRED_FIELDS[status]` and checks each field's presence in `fm` (use the existing `in fm` idiom — NOT a fabricated `field_present` helper, per backend-design review I-DR-BE-001 resolution); emits a `blocker` finding per missing field.
3. On `doc_type == issue-proposal`, checks `proposes_future_feature` presence; emits an `info` finding if absent.
4. For each optional cross-link field present (`escalates_from`, `escalated_to`, `rolled_into_register`), validates syntactic shape (regex against `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>`); emits a `minor` finding on malformed value.

The finding shape uses `make_finding` (VE-002 at validator lines 157-167) verbatim. No new finding fields. No new severity levels.

**For the regression-corpus baseline (Plan-stage prerequisite).** Per ADR-0050 / D-10: capture pre-extension findings JSON BEFORE implementing the extension. Re-run post-extension. Diff MUST be empty on existing pipeline doc_types. Three regression-corpus layers: L1 (existing smoke-test fixtures); L2 (real pipeline artifacts from `working/feature/*/`; minimum 27 files covering the 21-value explicit enum + 6 suffix patterns; per Q-BE-5 resolution the artifact-of-record is the findings JSON, not the source files); L4 (post-migration files at `status: open` with companion fields).

**For the templates (CC layer).** Each template's frontmatter section documents the vocabulary and per-state companion fields. Per ADR-0049, this is structural-only — the templates do NOT include "when to use this state" prose; that lives in `KB-issue-capture/references/triage-criteria.md`.

**For agent body update-mode (CC layer).** The update-mode procedure (per Blueprint §Sub-Agent Patterns) applies the per-state companion-field rules at draft time: when the user invokes `/capture-issue --update <path>` and the proposed transition is `status: open → adopted`, the agent drafts the new frontmatter with `adopted_by_feature_slug:` and `adopted_at:` populated. The AskUserQuestion OLD→NEW preview shows the new companion fields explicitly.

**Field-name lock per Q-BE-1 / Q-BE-2 / Q-BE-3 resolution.** The field names in this ADR (`since`, `adopted_by_feature_slug`, `adopted_at`, `resolved_by`, `resolved_at`, `resolution_summary`, `superseded_by_issue_id`, `superseded_at`, `wontfix_rationale`, `decided_at`) are the canonical strings. The doc_type strings (`issue-register`, `issue-analysis`, `issue-proposal`) are the canonical strings. The status strings (`draft`, `open`, `adopted`, `complete`, `superseded`, `wontfix-with-rationale`) are the canonical strings. The validator constants populate from these.

No procedural detail beyond the above — the exact PR shape and test-fixture authoring is a Plan-author concern.

## Related Information

- Related ADRs:
  - ADR-0008 (intra-pipeline 4-state ledger; parallel-but-distinct anchor; THIS ADR does NOT migrate ADR-0008's placement — per PRD §Risks #2)
  - ADR-0005 (supersession discipline; this ADR's `superseded_by_issue_id` mirrors the pattern with a distinct field name to preserve category separation)
  - ADR-0032 (per-doc-type 3-tier vocabulary policy; this ADR adds a fourth tier)
  - ADR-0051 (per-issue folder model; `id` derivation rule)
  - ADR-0052 (three doctypes preserved; the validator's `ISSUE_DOC_TYPES` set)
  - ADR-0046 (add-new-sibling evolution; the optional cross-link fields)
  - ADR-0047 (three-layer enforcement; the validator runs at Gate 0 below the three layers)
  - ADR-0048 (prior-context handoff; the `adopted` state captures the post-handoff transition)
  - ADR-0049 (structural-vs-discipline KB split; the vocabulary documented in templates+spec is structural)
- Referenced specs / docs: PRD §FR-7 (validator extension); PRD §NFR-8 (backward compatibility); PRD §Product Policy Decisions row "Issue-file lifecycle vocabulary"; Blueprint §Backend Design §5 (per-state required companion fields); Blueprint §Backend Design §7 (regression-corpus); codebase-analysis VE-001 (intra-pipeline 4-state vocabulary, verbatim source); VE-002 (`make_finding` shape, reused verbatim); VE-003 (existing per-category constants, the pattern this ADR mirrors); VE-004 (outer dispatch, preserved unchanged); F-005 (doc_type naming drift, FR-8 migration target); F-006 (`proposes_future_feature` precedents, the advisory-posture grounding); F-012 (the recommended extension shape that this ADR ratifies).
- Issues / PRs: `Issues/issue-capture-mechanism/proposal.md` (the proposal seed already using `doc_type: issue-proposal` from the canonical enum).
- Related KBs: KB-backend-design (Principles 2, 3, 4, 6, 7); KB-review-disciplines (references/issue-lifecycle.md — VE-001 source); KB-documentation-criteria (references/shared-conventions.md — per-doc-type 3-tier policy this ADR extends).
