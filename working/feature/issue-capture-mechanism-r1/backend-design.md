---
id: DESIGN-BE-issue-capture-mechanism-r1
doc_type: backend-design
version: 1.0.0
status: draft
feature_slug: issue-capture-mechanism-r1
layer: backend
derived_from:
  - working/feature/issue-capture-mechanism-r1/prd-v2.md
  - working/feature/issue-capture-mechanism-r1/research-plan.md
  - working/feature/issue-capture-mechanism-r1/codebase-analysis.json
  - working/feature/issue-capture-mechanism-r1/synthesis.md
generated: 2026-05-23T20:30:00Z
generated_by: design-backend
companion_artifacts:
  - working/feature/issue-capture-mechanism-r1/backend-dependencies.json
---

# Backend Design — Issue-Capture Mechanism (Validator Extension)

## 1. Layer Responsibility Scope

This Backend layer design is narrowly scoped to a single Python tooling artifact:

- **File touched (single):** `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py`
- **Change shape:** Additive extension — one new doc-type category (`issue`) parallel to the existing GATED / ANALYSIS / ADR categories. No mutation of existing categories. No new external dependencies. No change to the script's CLI surface, finding shape, exit-code semantics, or dispatch entry point.

Everything else in the feature (the agent, two skills, hook, slash command, templates, settings, migrations, intent-clarifier edits, recipe edits) belongs to the Claude Code layer and is owned by `design-cc`. This document does NOT design those surfaces and explicitly defers naming-level decisions (the doc_type enum string values, status vocabulary strings, frontmatter field names) to `design-cc` per the synthesis routing for D-05.

**KB-backend-design principles applicability.** This is a CLI script extension, not a service. Of the eight Backend Design principles, those that apply are:

- **Principle 2 (hexagonal / ports-and-adapters):** the existing validator's `make_finding` function and per-category `validate_*_artifact` functions are the de-facto ports; this design extends one port (`validate_pipeline_artifact`) by adding a new branch. No domain mutation. (See §3.)
- **Principle 3 (idempotency by default):** trivially satisfied — validation is a pure function of `(frontmatter, path)`; no mutation; running it N times yields the same findings.
- **Principle 4 (errors as first-class):** the validator uses a finite typed-severity vocabulary (blocker / major / minor / info — see VE-002, CP-002); the new `issue` branch reuses it verbatim. (See §6.)
- **Principle 5 (transactions scoped):** N/A — no data store, no transactions.
- **Principle 6 (observability):** trivially satisfied — findings are the output; no separate observability surface needed.
- **Principle 7 (concurrency model):** explicitly synchronous, single-process, single-thread — matching CP-002 (the auditing-shared CLI idiom).
- **Principle 8 (external calls):** N/A — no external calls.

Principles 1 (bounded contexts across services) and the saga / outbox / circuit-breaker patterns do not apply at the tooling-script scale.

## 2. Service Granularity and Module Layout

**Service granularity:** N/A — this is a stdlib-only Python CLI, not a service.

**Module layout (within `validate_pipeline_frontmatter.py`):** preserved as-is. The 422-line file has a flat structure of module-level constants, helper functions (`make_finding`, `parse_frontmatter`, `field_present`), per-category validators (`validate_gated_artifact`, `validate_analysis_artifact`, `validate_adr_artifact`), and an outer dispatcher (`validate_pipeline_artifact` at line 365-371; VE-004). The extension adds:

1. Two new module-level constants (`ISSUE_DOC_TYPES`, `ISSUE_STATES`) parallel to the existing `GATED_DOC_TYPES` / `ANALYSIS_DOC_TYPES` / `GATED_STATES` / `ANALYSIS_STATES` / `ADR_STATES` (VE-003).
2. One new module-level constant (`ISSUE_PER_STATE_REQUIRED_FIELDS`) — a dict mapping each of the 5 lifecycle states to its required-companion-field list. Module-level so unit tests can import it directly (per D-10's testability note).
3. One new function (`validate_issue_artifact(fm, path)`) parallel to the existing `validate_*_artifact` functions.
4. One new branch inside `validate_pipeline_artifact` that delegates to `validate_issue_artifact` when `doc_type ∈ ISSUE_DOC_TYPES`. Branch order: GATED → ANALYSIS → ADR → ISSUE → unknown. (See §3 for the dispatch decision rationale.)

The outer dispatch at lines 365-371 (VE-004) is unchanged. The skill / agent / pipeline-artifact path-based dispatch continues to route `Issues/*.md` files into `validate_pipeline_artifact`, where the new fourth branch picks them up by `doc_type` value.

## 3. Approach Decision (D-10): Fourth `issue` Category Branch Inside `validate_pipeline_artifact`

Three options were considered (per synthesis §Decision Framing D-10 and codebase-analysis F-012 / VE-004):

| Option | Mechanism | Decision |
|---|---|---|
| **A. Fourth `issue` category branch inside `validate_pipeline_artifact` (CHOSEN)** | Add `ISSUE_DOC_TYPES`, dispatch by `doc_type ∈ ISSUE_DOC_TYPES` inside the existing pipeline-artifact validator, alongside the GATED / ANALYSIS / ADR branches. | **Chosen.** |
| B. New path-based dispatch at outer level (`"Issues/" in str_path`) | Modify outer dispatch at lines 365-371 to route Issues paths to a separate `validate_issue_artifact` before the pipeline-artifact branch. | Rejected. |
| C. Separate validator file (`validate_issue_frontmatter.py`) | Doubles the caller surface — every caller of `validate_pipeline_frontmatter.py` (shared-document-reviewer, run_phase_checks, smoke_test_auditing_shared, execute-task-quality-handler) would need an additional call site. | Rejected. |

**Why A is the design.** Cohesion with the existing per-category dispatch (GATED / ANALYSIS / ADR — VE-003) is the strongest cohesion signal in the file. The existing structure already separates concerns by doc-type category at the same nesting level; adding a fourth peer is the minimum-surprise extension. Path-based dispatch (B) was rejected because the discriminator is **what kind of artifact** (a property of `doc_type`), not **where it lives** (path) — Issues files could in principle live elsewhere, and the path-prefix would become a brittle proxy for an intrinsic property. Separate file (C) was rejected because PRD §Dependencies and the codebase analysis both name `validate_pipeline_frontmatter.py` (singular) as the extension target, and the script's existing callers (5 named in codebase-analysis edges) would otherwise multiply.

**Backward compatibility (NFR-8).** Option A is the only option that trivially preserves existing dispatch — the new branch only fires when `doc_type ∈ ISSUE_DOC_TYPES`. Files whose `doc_type` is in any existing category continue through their existing branch with byte-identical behavior. This is the structural guarantee the NFR-8 regression-test corpus (§7) verifies empirically.

## 4. New Doc-Type Enum and Status Vocabulary (Consumed from `design-cc`)

**Three new `doc_type` enum values** added to `ISSUE_DOC_TYPES`:

- `issue-register`
- `issue-analysis`
- `issue-proposal`

These string values are owned by `design-cc` (see Q-BE-1 — confirm naming before lock). They appear in the PRD §FR-7, the proposal frontmatter precedent at `Issues/issue-capture-mechanism/proposal.md` (which already uses `doc_type: issue-proposal`), and the synthesis decision-frame routing. design-backend uses them verbatim from `design-cc`'s output.

**Five-state status vocabulary** added to `ISSUE_STATES`:

- `draft → open → adopted | complete | superseded | wontfix-with-rationale`

Specifically: `{"draft", "open", "adopted", "complete", "superseded", "wontfix-with-rationale"}`.

This vocabulary parallels but is **distinct** from the intra-pipeline 4-state ledger vocabulary captured verbatim in VE-001 from `KB-review-disciplines/references/issue-lifecycle.md`. Three state-name strings (`open`, `superseded`, `wontfix-with-rationale`) overlap by literal string match; the design must keep them separate because they apply to disjoint entities (intra-pipeline `issues-ledger.json` records vs. outside-pipeline `Issues/<topic>/<doctype>.md` files) with disjoint ID prefixes (`I-<DR|AA|CA>-NNN` vs. `<DOCTYPE>-<topic-slug>`). The validator achieves the separation structurally: `ISSUE_STATES` is consulted **only** in the new `validate_issue_artifact` function, which **only** runs when `doc_type ∈ ISSUE_DOC_TYPES`. Existing pipeline doc_types (`prd`, `blueprint`, etc.) continue to be validated against `GATED_STATES` / `ANALYSIS_STATES` / `ADR_STATES`, never against `ISSUE_STATES`.

## 5. Per-State Required-Companion-Field Rules (D-05)

The per-state companion-field rules are codified as a module-level dict `ISSUE_PER_STATE_REQUIRED_FIELDS` so they are unit-testable in isolation. Recommended rules (consumed from synthesis D-05; final field names owned by `design-cc`):

| State | Required companion fields (in addition to universal id / version / doc_type / status / feature_slug / generated / generated_by) | Severity if missing |
|---|---|---|
| `draft` | None beyond universal | n/a |
| `open` | `since: <ISO-8601-date>` | blocker |
| `adopted` | `adopted_by_feature_slug: <slug>` + `adopted_at: <ISO-8601-date>` | blocker |
| `complete` | `resolved_by: <ref>` + `resolved_at: <ISO-8601-date>` + `resolution_summary: <paragraph>` | blocker |
| `superseded` | `superseded_by_issue_id: <id>` + `superseded_at: <ISO-8601-date>` | blocker (mirrors ADR-0005 / VE-001 pattern at validator lines 314-323) |
| `wontfix-with-rationale` | `wontfix_rationale: <paragraph>` + `decided_at: <ISO-8601-date>` | blocker |

**Field names are placeholders.** The exact field-name strings (`since`, `adopted_by_feature_slug`, `resolved_by`, etc.) are owned by `design-cc` (Q-BE-2). The synthesis recommendation for `superseded` (`superseded_by_issue_id`) intentionally mirrors the existing ADR-0005 `superseded_by` enforcement at validator lines 314-323 so the new branch reuses an established pattern rather than inventing one.

**Optional cross-link fields** (validated for syntactic shape when present, never required):

- `escalates_from: <id>` — points to a sibling doctype in the same topic folder when FR-5 evolution has occurred.
- `escalated_to: <id>` — bidirectional back-link added to the older doctype.
- `rolled_into_register: <id>` — points to a register that consolidates the issue.

When present, these fields are validated for ID syntax only (regex match against the same shape used for `superseded_by_issue_id`). Absent → no finding. Type-mismatched → minor finding.

**Dispatch shape inside `validate_issue_artifact` (pseudocode — illustrative, not production):**

> **SUPERSEDED-NOTE (per blueprint-v2.md / I-DR-BP-004):** The pseudocode below — and the `field_present(fm, field)` references at §2, §5, and §Decision Summary of this layer-design — were superseded by the **Corrected Pseudocode Reference** subsection of `blueprint-v2.md` §Backend Design (per I-DR-BE-001 resolution). The actual codebase idiom is `field in fm` (cf. `validate_pipeline_frontmatter.py` lines 314-323, the ADR-0005 `superseded_by` enforcement); `field_present(...)` is fabricated and does not exist in the validator. **Readers consuming this section should treat the Blueprint's Corrected Pseudocode Reference as canonical.** The references below are retained for diff-history transparency and will be updated in a future per-layer revision if/when this design is re-authored. No new ADR is required — the correction is a sample-rubric compliance fix per KB-general-coding-principles Dimension 4 (no fabricated APIs).

```python
# illustrative — production wording owned by design-cc + implementer
def validate_issue_artifact(fm: dict, path: Path) -> list[dict]:
    findings = []
    doc_type = fm.get("doc_type")
    status = fm.get("status")

    # Status vocabulary check
    if status not in ISSUE_STATES:
        findings.append(make_finding(
            severity="blocker",
            file_path=path,
            message=f"status '{status}' not in issue vocabulary {sorted(ISSUE_STATES)}",
        ))
        return findings  # short-circuit; per-state rules require a known state

    # Per-state required companion fields
    for field in ISSUE_PER_STATE_REQUIRED_FIELDS.get(status, ()):
        if not field_present(fm, field):
            findings.append(make_finding(
                severity="blocker",
                file_path=path,
                message=f"status:{status} requires companion field '{field}'",
            ))

    # Advisory: proposes_future_feature on issue-proposal (D-06)
    if doc_type == "issue-proposal" and not field_present(fm, "proposes_future_feature"):
        findings.append(make_finding(
            severity="info",
            file_path=path,
            message="issue-proposal recommends a 'proposes_future_feature' slug",
        ))

    # Syntactic check on optional cross-link fields
    for field in ("escalates_from", "escalated_to", "rolled_into_register"):
        value = fm.get(field)
        if value is not None and not is_valid_id_syntax(value):
            findings.append(make_finding(
                severity="minor",
                file_path=path,
                message=f"field '{field}' value '{value}' does not match expected ID syntax",
            ))

    return findings
```

The example is illustrative per KB-general-coding-principles' design-time-sample rubric (stack matches project — Python; types explicit where the existing file uses them; error contract visible via severity strings; no fabricated APIs — `make_finding` and `field_present` exist in the existing file per VE-002 and lines 145-155).

## 6. `proposes_future_feature` Enforcement Posture (D-06)

**Recommendation: advisory.** When `doc_type == "issue-proposal"` and `proposes_future_feature` is absent, emit a finding at `severity: "info"` (matches the existing `info`-severity precedent in the validator). When present, accept any string value with no format enforcement.

**Rationale.** Two existing precedents (F-006) demonstrate field-shape divergence: `Issues/proposal-auditing-family-graduation-review.md` carries a suggested-slug; `Issues/issue-capture-mechanism/proposal.md` carries a fixed-slug. Strict enforcement would invalidate one of the two precedents without adding present-day value. The advisory posture preserves the forward-pointer signal, matches the validator's observer-only-default discipline (CP-002), and is trivially upgradable to `blocker` later if real-world use shows the field becomes load-bearing. Aligns with synthesis D-06 routing decision.

**Trade-off.** If a future feature (e.g., automation that scans `Issues/*.md` for `proposes_future_feature` slugs) assumes the field is reliably present, this advisory posture leaves a coverage gap. The risk is mitigated by D-05's independent requirement that `adopted_by_feature_slug` is mandatory on `status: adopted` — the load-bearing back-link is on the terminal state, not on the proposal's forward-pointer.

## 7. Backward Compatibility (NFR-8) and Regression-Test Corpus

NFR-8 is the hardest constraint on this design: zero false positives and zero false negatives on existing pipeline doc_types after the extension.

**Structural guarantee (necessary but not sufficient).** Option A (§3) only adds a new `elif` branch; no existing branch is modified. The new branch fires when `doc_type ∈ ISSUE_DOC_TYPES`; existing doc_types are not in that set. The outer dispatch at lines 365-371 (VE-004) is unchanged. Skill-file and agent-file validation paths are untouched (codebase-analysis §validator_extension_surface lists 6 unaffected checks).

**Empirical regression test (necessary AND sufficient).** Per synthesis D-10 ("design-backend MUST capture the pre/post regression corpus baseline BEFORE implementing the extension"), the implementation procedure is:

1. **Capture baseline (BEFORE extension).** Run `validate_pipeline_frontmatter.py` against the **regression corpus** (defined below) using the current HEAD. Persist the findings JSON.
2. **Implement extension.** Apply the changes per §2-§6.
3. **Re-run validator against the same corpus (AFTER extension).** Persist the findings JSON.
4. **Diff.** `diff baseline.json post-extension.json` must be empty. Any new finding line on a pre-existing doc_type is a regression.

**Regression-corpus composition.** Three layers:

| Layer | Files | Rationale |
|---|---|---|
| L1: existing pipeline-doc-type fixtures | All files currently exercised by `smoke_test_auditing_shared.py` (the only existing test surface that exercises the validator — codebase-analysis node `script.smoke_test_auditing_shared`). | Establishes the test-suite baseline. |
| L2: real pipeline artifacts | A representative sample of files from `working/feature/*/`: at minimum one of each `doc_type` in the current explicit enum (21 values) + one matching each of the 6 suffix patterns (`-design`, `-report`, `-log`, `-issues`, `-result`, `-summary`). 27 files minimum. | Validates against the live pipeline corpus, not synthetic-only. |
| L3: synthetic fixtures for the new branch | One fixture per (`doc_type`, `status`) combination of (3 issue doc_types × 6 states = 18) + one fixture per state with each per-state required companion field MISSING (6 missing-field cases) + one fixture per state with an INVALID `status` outside the 5-state vocabulary (1 case per doc_type = 3 cases). 27 synthetic fixtures minimum. | Verifies the new branch behaves correctly (positive and negative). |
| L4: post-migration regression | The 4 migrated files post-FR-8 back-fill (`Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` etc., per PRD AC-FR-8-a) with the back-filled `doc_type` + `status: open` + `since:` field. | Verifies AC-FR-7-a (clean validation on the 4 migrated files) and AC-FR-8-c. |

**Test harness extension.** Per CP-006 and the codebase-analysis edge `script.smoke_test_auditing_shared → script.validate_pipeline_frontmatter`, the regression-corpus runner should extend `smoke_test_auditing_shared.py` rather than introduce a new harness file (preserves the convention pattern). Specifically:

- Add fixtures directory `.claude/skills/auditing-shared/scripts/test_fixtures/issue_doc_types/` containing the L3 + L4 fixtures.
- Add a regression-runner function `regression_test_issue_extension()` invoked from the existing `main()` of `smoke_test_auditing_shared.py` (Plan-author owns the exact harness wiring).

Plan-author should also decide whether to add a sibling `test_validate_pipeline_frontmatter.py` if the smoke-test file grows beyond a maintainable size; this design is agnostic between the two layouts.

## 8. Error Model and Finding Shape

The validator's error model is established (VE-002, CP-002). The new branch reuses it verbatim:

| Element | Decision |
|---|---|
| Finding shape | `{domain, severity, source_activity, file_path, message, dispatch_hint, depth_level}` — verbatim from `make_finding` (VE-002) |
| Severity vocabulary | `{blocker, major, minor, info}` — existing 4-level taxonomy |
| `domain` field value | `"validator"` (existing default) |
| `source_activity` value | `"frontmatter-validator"` (existing default) |
| `dispatch_hint` for issue-* findings | `"the agent that authored the artifact"` (existing default; for Issues files this is `issue-capture-author`) |
| New severities introduced | None |
| New finding fields introduced | None |

**Severity assignment policy for the new branch:**

- `blocker` — status outside the 5-state vocabulary; required companion field missing for the declared state. Both are structural correctness violations (no graceful interpretation possible).
- `minor` — optional cross-link field present with malformed ID syntax (the file is still meaningful; the cross-link is corrupted).
- `info` — `proposes_future_feature` missing on `issue-proposal` (advisory; see §6).
- `major` is **not** used by this branch (no intermediate-severity case applies).

## 9. Concurrency Model

Single-process, single-thread, synchronous, CLI-invoked. Inherits from the existing validator (CP-002). No new concurrency surface. The validator is called once per file in the corpus during a Gate-0 pass; no parallelism, no locking, no shared mutable state.

## 10. External Calls

None. The validator reads files from the local filesystem via `pathlib`. No HTTP, no DB, no queue, no third-party API. Principle 8 does not apply.

## 11. Authentication and Authorization

None. The validator is a stdlib-only script invoked by the user or by a sub-agent via `Bash`. Permissions enforcement is at the Claude Code layer (existing `.claude/settings.json` `permissions.allow` entry at line 7 — CP-005 — pins invocation to this specific script path; the new extension changes nothing about that surface).

## 12. Observability Commitments

The validator's output IS its observability surface — findings JSON to stdout, stderr-prefixed errors per CP-002. No new observability surface is needed. The new branch emits findings using the existing `make_finding` shape (§8); these findings naturally flow into the existing consumers (shared-document-reviewer at line 460, execute-task-quality-handler at line 62, run_phase_checks at line 40, smoke_test_auditing_shared at line 29 — all per the codebase-analysis edges).

**EARS-format observability ACs (contributed by Backend layer):**

- The system shall emit one `make_finding`-shaped JSON record per validation issue on `doc_type ∈ {issue-register, issue-analysis, issue-proposal}`.
- When the validator processes an `Issues/*.md` file with the new `doc_type` values, the system shall use `source_activity: "frontmatter-validator"` (unchanged from existing behavior).
- The system shall not emit any additional log line, file write, or side effect beyond the JSON stdout finding stream (preserves CP-002 observer-only discipline).

## 13. Patterns Chosen

From the KB-backend-design pattern catalog:

| Pattern | Applicability | Rationale |
|---|---|---|
| **Additive-only extension** | Chosen | Reuses existing `make_finding`, `parse_frontmatter`, `field_present`, dispatch shape (lines 365-371). No deprecation. |
| **Module-level constants for testability** | Chosen | `ISSUE_DOC_TYPES`, `ISSUE_STATES`, `ISSUE_PER_STATE_REQUIRED_FIELDS` are module-level dicts/sets unit-testable in isolation, mirroring `GATED_DOC_TYPES` / `ANALYSIS_DOC_TYPES` style (VE-003). |
| **Errors-as-first-class (Principle 4)** | Chosen | Severity vocabulary + finding shape preserved verbatim from existing validator (VE-002). |
| **Idempotent validator (Principle 3)** | Trivially | Pure function over `(frontmatter, path)`. |
| **Hexagonal port reuse (Principle 2)** | Chosen | `make_finding` is the de-facto output port; the new branch is a new adapter producing through that port. |

Anti-patterns explicitly avoided:

- **Cross-cutting modification.** Existing per-category validators are not touched.
- **Reaching across categories.** `ISSUE_STATES` is consulted only inside `validate_issue_artifact`; existing branches never see it.
- **Silent overload of finding shape.** No new finding fields introduced (Principle 4 — error model is part of the contract).
- **External I/O at validation time.** No HTTP, no DB, no environmental dependency beyond Python stdlib.

## 14. Acceptance Criteria Contribution (EARS-format)

These ACs are contributed by the Backend layer to the Blueprint's overall acceptance posture. They restate FR-7 ACs from the PRD in implementation-grounded form and add backend-specific structural assertions.

**Functional (validator-behavior):**

- AC-BE-1 — When `validate_pipeline_frontmatter.py` is invoked with a file whose frontmatter declares `doc_type ∈ {"issue-register", "issue-analysis", "issue-proposal"}`, `status ∈ ISSUE_STATES`, and all required companion fields per `ISSUE_PER_STATE_REQUIRED_FIELDS[status]` are present, the system shall return zero findings for that file.
- AC-BE-2 — When the file declares `doc_type ∈ ISSUE_DOC_TYPES` but `status ∉ ISSUE_STATES`, the system shall emit exactly one `blocker`-severity finding naming the unrecognized status and the expected vocabulary.
- AC-BE-3 — When the file declares `doc_type ∈ ISSUE_DOC_TYPES` and `status ∈ ISSUE_STATES` but one or more required companion fields are absent, the system shall emit one `blocker`-severity finding per missing field, each naming the missing field.
- AC-BE-4 — When the file declares `doc_type == "issue-proposal"` and `proposes_future_feature` is absent, the system shall emit exactly one `info`-severity finding indicating the field is recommended.
- AC-BE-5 — When the file declares `doc_type ∈ ISSUE_DOC_TYPES` and any of `escalates_from`, `escalated_to`, or `rolled_into_register` is present with a value that does not match expected ID syntax, the system shall emit one `minor`-severity finding per malformed field.

**Backward compatibility (NFR-8):**

- AC-BE-6 — When the post-extension validator is run against the regression corpus (L1+L2+L4 per §7), the system shall produce findings byte-identical to the pre-extension baseline.
- AC-BE-7 — When the post-extension validator is run against any file whose `doc_type` is in the pre-existing explicit enum (the 21 values listed in `validator_extension_surface.current_doc_type_enum_explicit`) or matches any pre-existing suffix pattern, the system shall route the file through the pre-existing per-category validator unchanged.

**Dispatch invariants:**

- AC-BE-8 — While the outer dispatch (`validate_file`) is in scope, the system shall NOT change the path-based dispatch order at lines 365-371 (skill → agent → pipeline-artifact). The new branch lives inside `validate_pipeline_artifact`, not at the outer dispatch.
- AC-BE-9 — While `validate_issue_artifact` is in scope, the system shall reuse `make_finding` (VE-002) for every finding it produces; no parallel finding-construction helper is introduced.

## 15. Dependencies on Other Layers

This Backend design depends on the following from `design-cc`:

| Dependency | Owner | Why it blocks Backend |
|---|---|---|
| Final `doc_type` enum strings: `issue-register`, `issue-analysis`, `issue-proposal` | design-cc | These are the literal strings that populate `ISSUE_DOC_TYPES`. Renaming after Backend implementation would force a coordinated change. |
| Final 5-state status vocabulary strings: `draft`, `open`, `adopted`, `complete`, `superseded`, `wontfix-with-rationale` | design-cc | These populate `ISSUE_STATES`. Same coordinated-change concern. |
| Final per-state required-companion-field names (e.g., `since`, `adopted_by_feature_slug`, `resolved_by`, `resolution_summary`, `superseded_by_issue_id`, `wontfix_rationale`, `decided_at`) | design-cc (synthesis D-05 shared) | These populate `ISSUE_PER_STATE_REQUIRED_FIELDS`. |
| Optional cross-link field names: `escalates_from`, `escalated_to`, `rolled_into_register` | design-cc | These drive the syntactic-correctness check. |
| ID syntax regex (for the cross-link syntactic check) | design-cc | The validator needs a single canonical pattern. |
| Confirmation that `proposes_future_feature` field name remains literal (no rename) | design-cc | Drives the D-06 advisory check on `issue-proposal`. |
| Template structure for the 3 doc_types (FR-6) | design-cc | The validator does NOT inspect body shape — it only validates frontmatter. The dependency is informational: the templates' frontmatter sections must declare the fields this validator enforces. |

No dependency on Database, Query, API, IaC, or CI/CD layers — those are all `N/A — out of scope` per PRD Layer Scope.

## 16. Architectural Questions for Composer

- **Q-BE-1 — Final lock on the three new `doc_type` enum strings.** Evidence: `Issues/issue-capture-mechanism/proposal.md` already uses `doc_type: issue-proposal`; the 4 pre-migration files use older names (`deferral-register`, `analysis`, `proposal`) per F-005; PRD FR-7 names the new canonical enum. Options: (a) `issue-register` / `issue-analysis` / `issue-proposal` (synthesis recommendation, PRD-named); (b) drop the `issue-` prefix and keep `register` / `analysis` / `proposal` (matches 3 of 4 existing precedents but loses the namespace separation from any future non-issue `analysis` doc_type). Recommended: (a). Defer to composer.

- **Q-BE-2 — Final field-name slate for per-state required companions.** Evidence: synthesis D-05 routes this to design-cc + design-backend shared. The field names in §5 (`since`, `adopted_by_feature_slug`, `adopted_at`, `resolved_by`, `resolved_at`, `resolution_summary`, `superseded_by_issue_id`, `superseded_at`, `wontfix_rationale`, `decided_at`) are recommendations grounded in symmetry (each terminal state has one back-link field) and parallel with the existing `superseded_by` enforcement (VE-001/VE-003). Options: (a) adopt the recommendation verbatim; (b) align more closely with ADR-0032 conventions if `design-cc` finds prior-art divergence; (c) collapse the date suffixes (e.g., `adopted_at` → reuse a common `transitioned_at`). Recommended: (a). Defer to composer.

- **Q-BE-3 — Should `superseded_by_issue_id` for issue-* files share namespace with ADR-0005's `superseded_by` field?** Evidence: the existing validator enforcement at lines 314-323 (VE-003 implications) uses `superseded_by` on ADR doc_types. Reusing the same field name on issue-* files would cross category boundaries; using a distinct field name (`superseded_by_issue_id`) keeps the category separation explicit. Options: (a) distinct field name (synthesis recommendation; recommended); (b) shared field name; (c) shared field name with a `_kind` discriminator. Recommended: (a). Defer to composer.

- **Q-BE-4 — Should the validator extension be a single PR or split into "constants only" + "validation logic" PRs?** Evidence: NFR-8's regression-test workflow (§7) requires baseline capture BEFORE the new branch fires. Splitting would let the constants land first (no behavior change), then the regression baseline gets captured against the un-extended-behavior file, then the validation-logic PR adds the branch. Options: (a) single PR with baseline captured pre-merge by the plan; (b) split PRs as described. Recommended: (a) — the synthesis D-10 baseline-capture procedure (§7 step 1) is sufficient. Defer to composer + plan-author.

- **Q-BE-5 — Should the regression corpus L2 (real pipeline artifacts) be checked into the repo as fixtures, or referenced by path into `working/feature/*/`?** Evidence: `working/feature/*/` directories contain pipeline-run artifacts that may be cleaned periodically; check-in gives stability but duplicates content. Options: (a) check fixtures into `.claude/skills/auditing-shared/scripts/test_fixtures/regression_baseline/`; (b) reference by path with a snapshot manifest; (c) capture findings JSON only (not the source files) and assert against findings shape. Recommended: (c) — the load-bearing artifact is the FINDINGS, not the source files; capturing the findings JSON as the baseline is the smallest stable artifact. Defer to composer + plan-author.

## 17. Open Items

None beyond Q-BE-1..5 above. The design is complete pending naming-lock decisions owned by `design-cc`.

## 18. References

- **PRD:** `working/feature/issue-capture-mechanism-r1/prd-v2.md` — FR-7 (validator extension), NFR-8 (backward compatibility), AC-FR-7-a/b/c/d, AC-NFR-8-a/b.
- **Synthesis:** `working/feature/issue-capture-mechanism-r1/synthesis.md` — D-05 (per-state companion fields), D-06 (`proposes_future_feature` posture), D-10 (validator extension architecture). Per-layer-design routing §"Per-layer Design Routing" assigns D-05 (shared with design-cc), D-06, D-10 to design-backend.
- **Codebase analysis:** `working/feature/issue-capture-mechanism-r1/codebase-analysis.json`
  - F-005 (doc_type naming drift in pre-migration files)
  - F-006 (`proposes_future_feature` precedents)
  - F-008 (hand-rolled YAML parser is sufficient)
  - F-011 (sibling-script CLI idiom)
  - F-012 (extend `validate_pipeline_artifact` with a fourth branch)
  - CP-002 (auditing-shared script CLI conventions)
  - CP-007 (`feature_slug` universal-required per ADR-0032 Change 4)
  - VE-001 (intra-pipeline 4-state ledger — parallel-but-distinct anchor)
  - VE-002 (`make_finding` shape — reused verbatim)
  - VE-003 (current category constants — pattern this design mirrors)
  - VE-004 (current dispatch — preserved unchanged)
  - `validator_extension_surface` (current enum, suffix patterns, per-category state vocabularies, current per-state required-companion-field rule)
  - `blast_radius[0]` (validator extension blast radius — 3-hop transitive)
- **KB-backend-design:** Principles 2, 3, 4, 6, 7 (applicability per §1).
- **KB-general-coding-principles:** Design-time sample rubric applied to the pseudocode in §5.
- **KB-documentation-criteria:** Blueprint Backend-Design template (§1-§16 structure).
- **KB-review-disciplines:** `references/issue-lifecycle.md` (VE-001 source; the intra-pipeline 4-state vocabulary that the new 5-state vocabulary must remain distinct from).
