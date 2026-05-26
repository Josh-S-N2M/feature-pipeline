---
id: ADR-0058
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - ADR-0037
  - ADR-0005
applies_to:
  - pipeline-quickwins-hardening-r1
  - .claude/runtime/mcp-events.jsonl event surface (project-wide)
  - KB-mcp-design/references/principles.md (schema home; future amendment)
  - KB-mcp-platform/references/mcp-events-jsonl.md (usage documentation; future amendment)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Additive extension of ADR-0037's mcp-events.jsonl event-type vocabulary to admit a fourth event type, `calibration_result`, written by FR-4b's GitNexus grammar-skip behavioral calibration script. The three pre-existing event types (`install_complete`, `readiness_probe`, `structured_failure`) are preserved verbatim; consumers that filter on unknown types continue to ignore the new type per ADR-0037's forward-compatibility posture. Pre-finalization reconciliation (2026-05-26 cycle 1 of pipeline-quickwins-hardening-r1 Architecture Audit): event-type triad corrected from `primary_degraded / readiness_probe / structured_failure` to `install_complete / readiness_probe / structured_failure` (inherited prose error from ADR-0037 v1.0.0 / v1.0.1, since corrected in ADR-0037 v1.0.2); OP-6 → OP-7 label corrected for schema-validation rule references throughout (OP-6 audits credential redaction; OP-7 is the schema-validation rule).
---

# ADR-0058: `calibration_result` Event Type — Additive Extension to `mcp-events.jsonl` Vocabulary

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

Accepted — 2026-05-26

## Context

The `pipeline-quickwins-hardening-r1` feature's v0.3.0 reshape of FR-4 introduces a new opt-in / CI-scheduled behavioral calibration mechanism (FR-4b, owned by the Codespaces layer; FR-4c, owned by the CI/CD layer) that asks a question the existing `mcp-events.jsonl` event vocabulary does not name: "did the upstream GitNexus tag pinned in `versions.env` continue to honor the `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var contract?" The calibration emits one event per run to `.claude/runtime/mcp-events.jsonl` per ADR-0037 so that the outcome is observable on the same event surface other MCP-related signals already use — observability is the explicit antidote to the user-named "maintainer-only script that nobody invokes for six months" trap.

ADR-0037 (as corrected in v1.0.2 in lockstep with this ADR's authoring; see ADR-0037 §Document History 2026-05-26) establishes `.claude/runtime/mcp-events.jsonl` as the canonical event surface with three event types: `install_complete` (per-server install completion record written by postCreate.sh), `readiness_probe` (postCreate / postStart probe outcome), `structured_failure` (mid-run failure record — carries a `primary_degraded` boolean sub-field on primary→fallback transition records). Architecture Impact item 4 of ADR-0037 states: "the `mcp-events.jsonl` schema is the only schema permitted in this file; ad-hoc fields are rejected by the OP-7 audit rule" (the schema-validation rule implemented by `audit_op7_events_schema.py`; OP-6 audits credential redaction in the runtime log — a distinct concern). The event-type set is therefore closed at three values; adding a fourth requires an additive extension to the canonical schema.

The PRD anticipates this requirement directly. NFR-13 (verbatim): "FR-4b introduces a new calibration-outcome event type (`calibration_result` or similar — exact name and shape resolved at Design). Because this is a new event type, it is an additive extension to ADR-0037's event-surface schema; Design (Codespaces and/or design-composer) shall handle that extension either by amending ADR-0037 or by issuing a small new ADR that records the additive extension, so that the FR-4b event is a documented member of the event-surface schema rather than an undocumented appendage." This ADR is that small new ADR.

Both per-layer designers (codespaces-design v0.3.0 §Q-CS-1a; cicd-design v0.3.0 §Q-CICD-11) surfaced the same cross-layer question to the composer: does NFR-13's "no new event types" admit the addition (Interpretation A — recommended by both designers) or must the calibration reuse `install_complete` / `structured_failure` with a JSON-stringified payload in the `note:` field (Interpretation B)? The PRD's NFR-13 text resolves the question in favor of Interpretation A; the composer's task is to author the small new ADR the PRD names.

Two facts constrain the option space:

1. **ADR-0005 append-only supersession** — the event-type vocabulary can only evolve forward. Existing `mcp-events.jsonl` files written before this ADR lands continue to be valid; existing consumers that filter on the three pre-existing types continue to work; the new type is additive, not replacing.
2. **MINOR scope class for this feature** — the extension must be two-way reversible (a future ADR can remove or rename the type) and must not require coordinated changes across multiple components. The single writer (the FR-4b script) and the small number of readers (Q-CS-1b stale-calibration banner; future analytics; the optional auditing-mcp OP-rule that would validate `calibration_result`'s shape) keep the blast radius local.

## Decision

Extend the `mcp-events.jsonl` event-type vocabulary established by ADR-0037 with a fourth named event type, **`calibration_result`**, that records the outcome of a behavioral calibration run (currently FR-4b's GitNexus grammar-skip check; the type is reusable by future calibration mechanisms that ask the same shape of question). The three pre-existing event types (`install_complete`, `readiness_probe`, `structured_failure`) are preserved verbatim. The closed-enum discipline ADR-0037 establishes for the event-type set is preserved — the vocabulary remains closed; it is closed at four values now rather than three.

The canonical payload shape of a `calibration_result` event is fixed by this ADR's Implementation Guidance and lives in `KB-mcp-design/references/principles.md` (the schema home ADR-0037 designates) once that KB reference is updated by the Plan author.

## Decision Details

| Item | Content |
|---|---|
| Decision | Add `calibration_result` as a fourth event type to the `mcp-events.jsonl` vocabulary established by ADR-0037. Canonical payload: `{event, timestamp, server, mechanism, version, duration_ms, outcome ∈ {pass, fail, drift_detected}, signals: <map>, note}`. Existing three event types preserved verbatim. |
| Why now | FR-4b's calibration script writes its first event the moment it is invoked; without a named type, either NFR-13 forces the calibration into the wrong-shaped existing types (Interpretation B — stringified blob in a `note:` field), or the calibration ships without an observable event (defeating the user-named trap-avoidance). Naming the type concurrently with the FR-4b script's introduction is the only honest sequence. |
| Why this | A named type with a documented payload makes the calibration outcome filterable by downstream consumers via `jq 'select(.event == "calibration_result")'`, which is the canonical pattern for the existing three types. The alternative (Interpretation B — pack the signals map into `note:`) couples a semantic question into a free-text field, fails the OP-7 audit rule's shape discipline (the schema-validation rule that admits the event-type vocabulary; not OP-6, which audits credential redaction), and creates the documentation-vs-realization drift this carve-out exists to prevent. |
| Known unknowns | (a) Whether other behavioral calibrations in future features will reuse `calibration_result` with a different `signals` map shape, or will introduce their own event types. The `mechanism:` field (`"fr-4b-gitnexus-grammar-skip"` for this feature; other strings for future calibrations) namespaces the per-mechanism shape so reuse is possible without per-calibration ADRs. (b) Whether `auditing-mcp` should grow an OP-rule that validates `calibration_result` payloads against this ADR's canonical shape; Plan author may surface as a follow-on. |
| Kill criteria | If any future calibration mechanism's shape cannot cleanly map to the `{outcome, signals, note}` triad — e.g., a calibration that produces a continuous metric rather than a discrete pass/fail/drift_detected outcome — this ADR's payload shape is too narrow and should be superseded with a richer schema (per ADR-0005 append-only). If, six months after ship, no downstream consumer ever filters on `event == "calibration_result"` (the FR-4c CI workflow being the only reader), the extension's value is unproven and a future revision may collapse it back into `install_complete` / `structured_failure`. |

## Rationale

The decision honors four rationale-brief commitments:

1. **ADR-0037 (mcp-events.jsonl event-surface canonical schema)** — already establishes the file, the schema home (`KB-mcp-design/references/principles.md`), the OP-7 audit rule (`audit_op7_events_schema.py`) that rejects ad-hoc fields and validates the event-type vocabulary, and the closed-set discipline for event types. (OP-6, by contrast, audits credential redaction in the runtime log — a distinct concern.) This ADR is a faithful additive extension of OP-7's schema discipline, not a re-litigation. The vocabulary remains closed; it is closed at four values rather than three.
2. **ADR-0005 (append-only supersession)** — handled by additive-extension: existing `mcp-events.jsonl` files are not rewritten; existing consumers that filter on the three pre-existing types continue to work without modification; the new type slots in without disturbing the prior schema.
3. **MINOR scope class for this feature** — the change is two-way reversible (a future ADR can supersede or remove the type), local in blast radius (one writer — the FR-4b script; current readers — the FR-4c CI workflow, the optional Q-CS-1b staleness banner, the existing `discovery-codebase-researcher` per ADR-0007 v2.2.0 + ADR-0037 which already ignores unknown types per the forward-compatibility posture), and individually verifiable (the calibration script's contract test in Plan Authoring validates the event-write).
4. **NFR-13 (the PRD's explicit additive-extension directive)** — the PRD names this ADR (or an ADR-0037 amendment) by example and assigns ownership to Design Composition. Authoring the small new ADR is the path the PRD names; amending ADR-0037 would also be legitimate but would re-open a "Decision Details" table whose Known-unknowns and Kill-criteria items are otherwise stable. A separate ADR keeps the original decision's kill criteria pristine and isolates the extension's own kill criteria to its own surface.

The single-source-of-truth principle from KB-cc-design Principle 5 and KB-codespaces-design Principle 3 applies: one canonical event-type name, one canonical payload shape, one writer (the calibration mechanism), well-defined readers. Naming the type once now beats letting the FR-4b script ship with an undocumented event-type value and forcing downstream consumers to discover it from the file's contents.

The alternative interpretations evaluated and rejected:

- **Interpretation B (reuse existing types with stringified blob in `note:`)** — preserves NFR-13's "no new event types" under a strict reading but violates the spirit of the same NFR's verbatim text that admits the additive extension. Creates a free-text field that consumers must JSON-parse; OP-7 audit rule cannot validate the embedded shape (only the top-level event-type vocabulary); documentation drift becomes likely as downstream readers invent their own conventions for the stringified payload. The trap-avoidance discipline the user named ("emit results to the same mcp-events.jsonl event surface per ADR-0037") becomes harder to honor when the surface is a free-text field rather than a typed event.
- **Amend ADR-0037 in place** — would re-open the Decision Details table of an Accepted ADR whose three event types are stable and whose Kill-criteria items name behaviors specific to the original three. The amendment would create cross-cutting ambiguity about which "version" of ADR-0037 a future reader is consulting. The append-only discipline of ADR-0005 prefers a new ADR that cites and extends, not a re-write.
- **Defer the extension to a follow-on feature** — would force FR-4b to ship without an event emission (the calibration's primary observability channel) or to ship with an undocumented event type (the documentation-vs-realization drift this carve-out exists to prevent). Neither is acceptable; the extension must land with the feature that needs it.

## Options Considered

### Option 1: Interpretation B — reuse `install_complete` / `structured_failure` with stringified `signals` in `note:` (rejected)

Pack the calibration's signals map as a JSON-stringified blob into the existing `note:` free-text field of `install_complete` (for pass outcomes — the calibration does install gitnexus into a scratch dir) or `structured_failure` (for fail / drift_detected outcomes).

**Pros:** No new event type; strict reading of NFR-13's "no new event types"; existing consumers and the OP-7 audit rule require no change.

**Cons:** Couples a semantic, queryable signal (pass/fail/drift_detected + per-grammar Signal-N outcomes) into a free-text field; downstream consumers must JSON-parse the `note:` field to act on it; OP-7 audit rule cannot validate the embedded shape (it admits the event type but cannot reason about the stringified payload); semantically dishonest (the calibration is not an "install" in the install_gitnexus sense — even though it does an npm install into a scratch directory, the load-bearing observation is the contract-honoring outcome, not the install itself; conflating the two muddles the event-surface's vocabulary).

### Option 2: Amend ADR-0037 in place to add the fourth type (rejected)

Edit ADR-0037's Decision item 2 from "three event types" to "four event types"; update Architecture Impact item 4; bump ADR-0037 to v1.1.0.

**Pros:** Single source of truth for the event-type vocabulary; future readers consult one ADR rather than two.

**Cons:** Re-opens the Decision Details table of an Accepted ADR whose three Known-unknowns and Kill-criteria items reference behaviors specific to the original three event types; creates cross-cutting ambiguity about which "version" of ADR-0037 a future reader consults; the append-only discipline of ADR-0005 explicitly prefers a new ADR that cites the prior decision over a re-write. ADR-0037 v1.0.1's prior amendment was an Implementation Guidance edit (record-count revision) — not a decision-content change — and used in-place edit precisely because no decision content shifted. This extension does shift decision content (the vocabulary), making the append-only-via-new-ADR path the correct sequence.

### Option 3 (Selected): Issue a small new ADR (this ADR) for the additive extension

Author a focused, small ADR that cites ADR-0037 as inherited, adds the fourth event type, preserves the three pre-existing types verbatim, and documents the canonical `calibration_result` payload.

**Pros:** Single source of truth — for the additive extension. ADR-0037's original decision content is preserved; this ADR's kill criteria are scoped to the extension itself; future readers consulting `KB-mcp-design/references/principles.md` (the schema home ADR-0037 designates) see the unified four-type vocabulary while the ADR pair documents the evolutionary path. Honors ADR-0005's append-only discipline cleanly. Honors NFR-13's explicit "small new ADR" path.

**Cons:** Future readers must consult two ADRs (0037 + 0058) to understand the full event-type vocabulary; the schema-home reference (`KB-mcp-design/references/principles.md`) must be updated by Plan Authoring to reflect the four-type canonical shape so casual readers do not have to chase the ADR trail.

## Consequences

### Positive Consequences

- The FR-4b calibration's outcome is observable on the same `mcp-events.jsonl` surface as the existing three event types; downstream consumers filter via the standard `jq 'select(.event == "calibration_result")'` pattern.
- The FR-4c CI workflow's `$GITHUB_STEP_SUMMARY` block can cross-reference the event by type without parsing free-text; the Q-CS-1b staleness banner (admitted into Blueprint v2) can read `event == "calibration_result"` events cleanly to compute event age.
- The OP-7 audit rule discipline ADR-0037 establishes is preserved — the vocabulary is still closed; consumers can still reject ad-hoc fields. (OP-6 audits credential redaction in the runtime log — a distinct concern preserved unchanged.)
- Future behavioral calibrations (if any) inherit the canonical shape via the `mechanism:` namespace field; per-calibration ADRs are not required for additional members of the same class.
- The PRD's NFR-13 commitment is honored explicitly with the small new ADR the PRD names.

### Negative Consequences

- The event-type vocabulary grows from three to four; future readers consulting the schema must absorb one more type. Mitigated by the schema home being a single KB file (`KB-mcp-design/references/principles.md`) which the Plan author updates in lockstep with this ADR.
- The `calibration_result` payload introduces a `signals` map field that is per-mechanism — its internal shape varies by mechanism (FR-4b's signals are `{signal_1_stderr_match_dart, signal_1_stderr_match_proto, signal_3_artifact_absence_dart, signal_3_artifact_absence_proto, negative_assertion_artifacts_built}`; future calibrations will have different signal names). Consumers that filter at the `signals.*` level must understand which mechanism they are reading; consumers that filter only on `outcome:` are mechanism-agnostic. This is by design — the `mechanism:` field is the discriminator.
- Two ADRs (0037 + 0058) must be read together to understand the full event-type vocabulary. The schema-home KB file consolidates them for casual readers.

### Neutral Consequences

- Existing consumers that filter on the three pre-existing types continue to work without modification; they simply ignore `calibration_result` events as they would any other unknown type (per ADR-0037's forward-compatibility posture, which is unchanged by this ADR).
- The `gitignored` posture of `mcp-events.jsonl` (per ADR-0037 Implementation Guidance) is unchanged — `calibration_result` events live in the same ephemeral local file as the other three types.
- The `auditing-mcp` skill's OP-6 audit rule (credential redaction in the runtime log) is unaffected by this extension. The OP-7 audit rule (schema validation; the rule that admits or rejects event types) MUST be extended in lockstep with this ADR's introduction — see Implementation Guidance below — otherwise every FR-4b emission produces an OP-7 MAJOR finding on the `calibration_result` event-type vocabulary expansion. If a future Plan task adds a per-mechanism OP-rule that validates `calibration_result` payload shapes specifically (the `signals` map per-mechanism keys, the `outcome` enum, etc.), it would slot in alongside OP-1..OP-11 (with OP-11 being added by FR-3 in this same feature) as a future OP-12+.

## Architecture Impact

Components that change (the actual edits are made by Plan Authoring):

1. **`KB-mcp-design/references/principles.md`** — the schema home ADR-0037 designates. Plan Authoring updates this file to document the fourth event type (`calibration_result`) and its canonical payload shape. The update is additive — existing three-type documentation is preserved verbatim.
2. **`KB-mcp-platform/references/mcp-events-jsonl.md`** — the usage-side documentation ADR-0037 designates. Plan Authoring updates this file to add a `calibration_result` example record and to note the `mechanism:` discriminator field.
3. **`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`** (FR-4b — owned by Codespaces layer) — writes `calibration_result` events per this ADR's canonical payload shape.
4. **`.github/workflows/gitnexus-grammar-skip-calibration.yml`** (FR-4c — owned by CI/CD layer) — does NOT write `calibration_result` events directly; consumes the script's exit code only. The script is the authoritative emitter per the codespaces-design / cicd-design cross-layer contract.
5. **`.devcontainer/postCreate.sh`** — gains a small block that reads the most recent `calibration_result` event from `mcp-events.jsonl` and emits a degraded-banner if no event has been recorded in the last 2 weeks (Q-CS-1b admission per Blueprint v2). This consumer is the second reader of `calibration_result` events.

Layers affected (per the 9-layer taxonomy):

- **Claude Code / Project Filesystem** — primary. The schema home (`KB-mcp-design/references/principles.md`) and the usage docs (`KB-mcp-platform/references/mcp-events-jsonl.md`) both live here. ADR-0058 itself lives in `adrs/` per ADR-0036 / ADR-0056 canonical placement.
- **Dev Environment / Codespaces** — secondary. The FR-4b script (the writer) and the `postCreate.sh` consumer (the staleness-banner reader) both live here.
- **CI/CD (GitHub Actions)** — tangential. The FR-4c workflow invokes the writer but does not interact with the event-surface directly.

New dependencies introduced: none. The extension is local to the existing event-surface contract.

Architectural constraints added:

- Future behavioral calibrations that want to use `calibration_result` MUST populate the `mechanism:` field with a namespace string distinguishing their per-mechanism `signals` map shape (e.g., `"fr-4b-gitnexus-grammar-skip"` for this feature; future calibrations pick their own namespace).
- Future behavioral calibrations whose semantic outcome does NOT fit `{pass, fail, drift_detected}` MUST author a follow-on ADR superseding or extending this one (per the Kill criteria in Decision Details).
- The closed-enum discipline ADR-0037 establishes is preserved at four values; admitting a fifth event type requires a follow-on ADR that supersedes or further extends this one.

Architectural constraints removed: none.

## Implementation Guidance

Principled direction only (procedures live in Plan):

- The canonical `calibration_result` payload shape:

  ```json
  {
    "event": "calibration_result",
    "timestamp": "<iso8601>",
    "server": "<server-name>",
    "mechanism": "<per-calibration namespace string>",
    "version": "<server-version-or-tag>",
    "duration_ms": <integer>,
    "outcome": "pass | fail | drift_detected",
    "signals": { "<per-mechanism signal name>": "pass | fail | skipped", ... },
    "note": "<one-line summary; remedial hint on fail or drift_detected>"
  }
  ```

  The `event`, `timestamp`, `server`, `mechanism`, `version`, `duration_ms`, `outcome`, and `note` fields are required for every `calibration_result` record. The `signals` map is required but its keys are per-mechanism (the namespace string in `mechanism:` discriminates).

- The writer is the calibration mechanism itself (currently the FR-4b script `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`). Future calibrations are also writers; the writer set is open. No non-calibration code path may write `calibration_result` events.

- The readers are open. Current named readers: the FR-4c CI workflow's `$GITHUB_STEP_SUMMARY` block (which surfaces the event's `outcome:` and `mechanism:` to the maintainer in the workflow UI); the Q-CS-1b staleness banner in `postCreate.sh` (which reads the most recent `calibration_result` event's timestamp to determine event age); the existing `discovery-codebase-researcher` per ADR-0007 v2.2.0 + ADR-0037 (which currently ignores unknown event types per the forward-compatibility posture and continues to do so unless future updates make it `calibration_result`-aware).

- The `mechanism:` field is the namespace discriminator. For this feature, the value is exactly `"fr-4b-gitnexus-grammar-skip"`. Future calibrations choose their own namespace string; conflicts are prevented by the namespace being mechanism-specific by construction (no two calibrations share a mechanism identifier).

- Absence-of-event at read time (e.g., the Q-CS-1b banner finding no `calibration_result` events in the file) MUST be treated as "calibration has not yet been run" and surfaced to the operator accordingly. The staleness banner's threshold is 2 weeks (the canonical Blueprint v2 value, set per the user direction's "weekly cron + one week grace" logic) but the banner is also emitted when the file contains no `calibration_result` events at all — that case is "infinitely stale."

- The OP-7 audit rule discipline applies: any record in `mcp-events.jsonl` whose `event:` field is `"calibration_result"` MUST conform to the canonical payload shape; ad-hoc fields are rejected. Plan Authoring MUST extend `audit_op7_events_schema.py`'s `REQUIRED_FIELDS` dict and `VALID_EVENT_TYPES` set to admit `calibration_result` with the canonical required-fields list (`event`, `timestamp`, `server`, `mechanism`, `version`, `duration_ms`, `outcome`, `signals`, `note`) before the FR-4b script ships its first emission; without this extension every FR-4b emission triggers an OP-7 MAJOR finding. Plan Authoring may also add a per-mechanism OP-rule that validates per-mechanism `signals` map shapes; this is a follow-on enhancement, not a precondition for ADR-0058's acceptance. (OP-6 audits credential redaction in the runtime log — a distinct concern not affected by this ADR.)

- The Plan author's edits to `KB-mcp-design/references/principles.md` and `KB-mcp-platform/references/mcp-events-jsonl.md` are mechanical: add the fourth event type's documentation alongside the three existing entries; preserve all existing prose; cite this ADR.

## Related Information

- **Related ADRs:** ADR-0037 (canonical source for the `mcp-events.jsonl` event surface and the three pre-existing event types this ADR additively extends); ADR-0005 (append-only supersession; the discipline that motivates a new ADR over an in-place amendment of ADR-0037); ADR-0036 / ADR-0056 (canonical ADR placement; this ADR lives at `adrs/ADR-0058-*.md`); ADR-0007 v2.2.0 and ADR-0018 (downstream consumers of `mcp-events.jsonl` that ignore unknown types per the forward-compatibility posture); ADR-0057 (sibling schema-surface-evolution ADR from the same Blueprint v1 composition; precedent for the architectural-grade discipline applied to this extension).
- **Referenced specs / docs:** `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` §NFR-13 (the PRD's explicit additive-extension directive); `working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md` v0.3.0 §Q-CS-1a (the per-layer surface of the same question); `working/feature/pipeline-quickwins-hardening-r1/cicd-design.md` v0.3.0 §Q-CICD-11 (the cross-layer surface of the same question); `working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md` (this ADR is referenced in the Blueprint's FR-4b and Q-CS-1a / Q-CICD-11 dispositions).
- **Issues / PRs:** This ADR is authored as part of `pipeline-quickwins-hardening-r1` Design Composition v2 (Gate-4-prep reshape of FR-4 absorbed from the user's verbatim direction at 2026-05-26).
- **Related KBs:** KB-documentation-criteria (ADR-authoring discipline); KB-mcp-design (the schema home for the four-type vocabulary — to be updated by Plan Authoring); KB-mcp-platform (the usage documentation — to be updated by Plan Authoring); KB-codespaces-design (Principles 3 and 5 — single source of truth, persistence boundaries); KB-cc-design (Principle 5 — single source of truth).

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-26 | 1.0.0 | Initial ADR authoring during Blueprint v2 composition. Established `calibration_result` as the fourth event type in the `mcp-events.jsonl` vocabulary additively atop ADR-0037. Canonical payload shape fixed; writer set is open to calibration mechanisms; reader set is open. The PRD-named "small new ADR" path is taken (per NFR-13 verbatim) in preference to an in-place ADR-0037 amendment (per ADR-0005 append-only discipline). | design-composer |
| 2026-05-26 | 1.0.0 (revised in draft) | Pre-finalization reconciliation per pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 (findings I-AA-001 and I-AA-002). Event-type triad corrected: every reference to the three pre-existing event types now reads `install_complete / readiness_probe / structured_failure` (the actual on-disk vocabulary per `audit_op7_events_schema.py` `VALID_EVENT_TYPES` and per `.devcontainer/postCreate.sh` emissions); the prior `primary_degraded` references inherited the v1.0.0 / v1.0.1 ADR-0037 prose error, corrected in ADR-0037 v1.0.2 in the same reconciliation pass. `primary_degraded` is preserved only where it correctly names a boolean sub-field of `structured_failure` (Options Considered Option 1 — which discusses how Interpretation B would have packed signals into existing event types). OP-6 → OP-7 label corrected for every reference to the schema-validation rule (OP-6 audits credential redaction; OP-7 is the schema validator implemented by `audit_op7_events_schema.py`). Implementation Guidance §Plan Authoring section additionally surfaces the requirement that `audit_op7_events_schema.py` REQUIRED_FIELDS dict and VALID_EVENT_TYPES set MUST be extended to admit `calibration_result` in lockstep with the FR-4b script's first emission. The decision content of this ADR (the fourth event type, the canonical payload, the writer / reader posture, the kill criteria) is unchanged. | design-composer |
