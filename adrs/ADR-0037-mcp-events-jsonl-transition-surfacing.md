---
id: ADR-0037
version: 1.0.2
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0007, ADR-0018]
applies_to:
  - devcontainer-mcp-provisioning-r1
  - any future feature that registers an MCP server with a documented fallback
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Establishes `.claude/runtime/mcp-events.jsonl` JSONL schema (event types
  install_complete / readiness_probe / structured_failure) plus stderr-banner
  companion as the canonical UI-15 primary→fallback transition-surfacing
  contract. Resolves Q-CC-5 (prose-only-with-audit vs structured-frontmatter-field)
  in favor of prose-only for the per-agent declaration; the structured surface
  lives in the event file, not in the agent frontmatter. v1.0.2 prose-only
  amendment per pipeline-quickwins-hardening-r1 Architecture Audit cycle 1:
  the event-type triad in §Decision item 2 was incorrectly written as
  "primary_degraded / readiness_probe / structured_failure" — the actual
  on-disk vocabulary per audit_op7_events_schema.py and per .devcontainer/postCreate.sh
  emissions is "install_complete / readiness_probe / structured_failure"
  (primary_degraded exists only as a boolean sub-field of structured_failure,
  not as a distinct event type); and §Architecture Impact item 4 referenced
  the wrong OP rule for schema validation (OP-6 actually audits credential
  redaction; OP-7 is the schema-validation rule). Both corrections are
  prose-only; the decision content (event surface, three event types as a
  closed enum, prose-only declaration with audit-rule discipline) is unchanged.
---

# ADR-0037: MCP transition surfacing — `mcp-events.jsonl` + stderr banner (UI-15)

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

Accepted — 2026-05-23

## Context

The `devcontainer-mcp-provisioning-r1` PRD requires (AC-FR-9-c, AC-FR-9-d) that every primary→fallback MCP transition reach an operator-visible surface with the named server, the failure layer, and a remediation pointer; no silent fallbacks are permitted, including the canonical GitNexus → codebase-memory-mcp fallback documented in ADR-0007 v2.2.0 and referenced by ADR-0018.

Synthesis section 5 / D-0005 surfaced this as the **load-bearing one-way design call** in the feature: research note T-007 verified **verbatim "NO CONSENSUS PATTERN"** across five surveyed source categories (claim C-0349, verified-high). The closest analogue (microservice circuit-breaker telemetry) is explicitly disclaimed as "not MCP-specific" (C-0351). The current wiring is prose-only across ADR-0007 → ADR-0018 → KB-codebase-research/SKILL.md → discovery-codebase-researcher.md; there is no machine-readable event surface today (claim C-0448 — codebase-grep-verified).

Per-layer Design surfaced this as Q-CC-5 (prose-only-with-audit-rule vs structured-frontmatter-field). Both legs share a runtime event surface; they disagree only on how the per-agent primary/fallback semantics are *declared* (prose vs frontmatter).

The decision is one-way (reach=36 sub-agents, blast-radius=tenant, Wardley stage=genesis) because future MCP additions will inherit whatever event-shape this feature establishes. Per FR-5, the design-composer is the only ADR-authoring agent in the pipeline.

## Decision

1. Adopt **`.claude/runtime/mcp-events.jsonl`** as the durable cross-server event surface. The file is JSONL, append-only, project-local, and not committed to git (the directory is committed; the file is gitignored — see ADR-0037 Implementation Guidance).
2. The file carries **three event types**: `install_complete` (per-server install completion record written by postCreate.sh), `readiness_probe` (postCreate / postStart probe outcome), `structured_failure` (FR-9 mid-run failure record — carries a `primary_degraded` boolean sub-field when the failure record corresponds to a primary→fallback transition). [Prose-only correction in v1.0.2 per pipeline-quickwins-hardening-r1 Architecture Audit cycle 1: the v1.0.0 / v1.0.1 prose listed `primary_degraded` here as a distinct event type, but the actual on-disk vocabulary per `audit_op7_events_schema.py` `VALID_EVENT_TYPES` and per the live `.devcontainer/postCreate.sh` emissions is `install_complete`. `primary_degraded` is a boolean sub-field of `structured_failure`, not a top-level event type. The decision content — three event types as a closed enum — is unchanged.]
3. **Every `structured_failure` event whose `primary_degraded: true` sub-field is set** also produces a one-line stderr banner from whichever component detected the transition. The banner is ephemeral operator hint; the JSONL record is the durable contract.
4. The per-agent primary/fallback declaration **remains prose** — in the existing four corpus layers (ADR-0007 v2.2.0, ADR-0018, KB-codebase-research/SKILL.md, `.claude/agents/discovery-codebase-researcher.md`). No new structured agent-file frontmatter field is introduced. The convention is made machine-checkable by an `auditing-mcp` rule (OP-4 per cc-design): for any agent whose `tools:` allowlist contains both a primary and a documented-fallback MCP, the agent body MUST contain prose matching `/primary.*fallback/` semantics naming both servers.
5. Agents do NOT template-print transition acknowledgements in their own output. The JSONL is the FR-9 contract; the banner is the operator-visible hint.

## Decision Details

| Item | Content |
|---|---|
| Decision | Combined JSONL + stderr-banner transition surfacing; prose-only agent-declaration backed by an audit-rule. |
| Why now | F5.4 NO CONSENSUS finding means future MCP additions will copy whatever shape this feature establishes. Two stdio-no-reconnect ground-truths (C-0301) make the contract load-bearing rather than nice-to-have. |
| Why this | Combines machine-readability (JSONL) with ephemeral operator hint (stderr banner). Rejects the four corpus-surfaced alternatives that each fail one of {operator-visible-at-the-moment, machine-readable, uniform-across-agents}. Prose-only avoids inventing a 36-agent-wide convention to address one agent's needs. |
| Known unknowns | (a) Whether the stderr banner is visible inside subagent contexts (Claude Code captures stderr; the banner reaches the host, not the parent agent). (b) Rotation policy for the JSONL — single file; plan-author may add a `.previous` rollover if file size becomes a felt constraint. |
| Kill criteria | If, six months after ship, the operator workflow shows the JSONL is being ignored and the stderr banner is the only surface used, drop the JSONL or move to a leaner format. Conversely, if the OP-4 audit rule fires no matches for >90 days, revisit by promoting the convention into structured frontmatter (which this ADR explicitly defers, not rejects forever). |
| v1.0.2 prose-correction note | The original v1.0.0 prose of this ADR (and the v1.0.1 record-count amendment) misnamed the event-type triad as `{primary_degraded, readiness_probe, structured_failure}` and named the schema-validation audit rule as OP-6. Both errors are corrected in v1.0.2: the actual on-disk triad per the running script `audit_op7_events_schema.py` and per the live `.devcontainer/postCreate.sh` emissions is `{install_complete, readiness_probe, structured_failure}` (with `primary_degraded` as a boolean sub-field of `structured_failure`, not a top-level type), and the schema-validation rule is OP-7 (OP-6 audits credential redaction in the runtime log — a distinct concern). The discrepancy was discovered during the Architecture Audit cycle 1 of `pipeline-quickwins-hardening-r1`, a feature whose entire mission is preventing exactly this kind of documentation-vs-realization drift; the irony of the very ADR motivating that mission carrying the drift is recorded here for the next reader. The decision content of ADR-0037 is unchanged. |

## Rationale

The substrate map (synthesis §3 D-0005) enumerated four alternatives. The combined posture is the only one that simultaneously satisfies (a) operator-visibility-at-the-moment, (b) machine-readability for FR-9 and auditing, (c) uniformity across 36 sub-agents without inventing a new convention. The OWASP MCP01 redaction posture (codified separately in ADR-0039) consumes the same event surface; making the surface durable now avoids re-litigation. The prose-only-with-audit-rule choice for Q-CC-5 honors KB-cc-design Principle 4 (subagent isolation: don't invent a convention until two cases need it) and the C-0444 medium-confidence universal-frontmatter calibration that warns against assuming field uniformity across all 36 agent files.

## Options Considered

### Option 1: JSONL only

**Pros:** Machine-readable; uniform; auditable.

**Cons:** Operator-invisible until someone tails the file. Fails AC-FR-9-c (transition must be "visible in the runtime log surface" — interpretable as JSONL — but operationally invisible in the moment).

### Option 2: stderr banner only

**Pros:** Operator-visible at the moment of failure.

**Cons:** Loses machine-readability. FR-9 falls back to ad-hoc stderr parsing. The augmented `auditing-mcp` cannot validate consistency without a structured surface.

### Option 3: Agent-level free-text acknowledgement

**Pros:** Surfaces in the operator's Claude Code session output directly.

**Cons:** Uniformity risk across 36 agents (C-0357). Every agent owner would invent their own phrasing; the OP-4 audit rule would not exist (no anchor to grep against).

### Option 4: Structured frontmatter convention (mcp_primary: / mcp_fallback:)

**Pros:** Self-documenting at the agent file level.

**Cons:** New 36-agent-wide convention with zero precedent (C-0445 zero-mcp__ invariant currently holds). Inventing a convention to address two-agents' needs violates KB-cc-design Principle 4. Does not address the *transition* event itself — only the declaration.

### Option 5 (Selected): Combined JSONL + stderr-banner + prose-only declaration

**Pros:** All three properties (operator-visible, machine-readable, uniform) honored. Builds on the existing four-corpus-layer prose conventions instead of inventing a new field. The audit rule (OP-4) makes the prose machine-checkable without a frontmatter change.

**Cons:** The schema is novel — no upstream precedent to lean on. Designed conservatively (five common fields, three event types) to minimize blast-radius if a future revision changes the shape.

## Consequences

### Positive Consequences

- Every primary→fallback transition is operator-visible AND machine-readable.
- The augmented `auditing-mcp` skill (rule OP-4) can validate primary/fallback declaration without an agent-file schema change.
- Future MCP additions inherit a stable contract; no per-server schema invention.
- The JSONL surface composes with `auditing-mcp` rule OP-5 (lifecycle completeness), OP-6 (runtime log redaction integrity — credential scanning), and OP-7 (event-schema validation — verifies each record's event-type vocabulary and per-type required fields).

### Negative Consequences

- The JSONL is a novel project convention; readers unfamiliar with it must consult `KB-mcp-design/references/principles.md` (schema home) to interpret.
- The stderr banner can be missed if the operator is not actively watching the shell; the JSONL remains the durable record.
- Rotation policy is left to plan-author; if the file grows unboundedly, an operator may need to truncate manually (plan-author should add a documented helper).

### Neutral Consequences

- The schema introduces the `extraction_method` field repurposed from the codebase-analysis schema (ADR-0018) for terminological consistency. The field is optional per event-type.

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (owns the schema + the `auditing-mcp` rule) and Dev Environment / Codespaces (writes `readiness_probe` records from `postStart.sh`).
2. **Components that change.**
   - `KB-mcp-design/references/principles.md` (NEW) — canonical schema home.
   - `KB-mcp-platform/references/mcp-events-jsonl.md` (NEW) — usage-side documentation.
   - `auditing-mcp` augmentation rule OP-4 (NEW) — primary/fallback prose presence.
   - `.devcontainer/postStart.sh` (NEW) — writes `readiness_probe` records.
   - In-product fallback-detection code-site (in MCP client-side handler — exact location decided at plan-author time) — writes `structured_failure` records whose `primary_degraded: true` sub-field is set on the primary→fallback transition. The transition-record event type is `structured_failure`; the `primary_degraded` sub-field is the discriminator.
3. **New dependencies introduced.** None at the runtime level; the JSONL is a project-local file. `jq` is used in `postStart.sh` for record construction (devcontainer base image ships jq via Dockerfile per codebase-analysis).
4. **Architectural constraints added.**
   - The `.claude/runtime/` directory is reserved for ephemeral runtime state.
   - The `mcp-events.jsonl` schema is the only schema permitted in this file; ad-hoc fields are rejected by the OP-7 audit rule (`audit_op7_events_schema.py` — the schema-validation rule). OP-6 audits credential redaction within the runtime-log surface — a distinct concern. [v1.0.2 prose correction: the v1.0.0 / v1.0.1 prose of this item incorrectly referenced OP-6 for schema validation; the actual rule is OP-7. The decision content — closed-schema discipline on the event surface — is unchanged.]
   - The `extraction_method` enum is closed at `transport_error / tool_error_response / manual_operator_invocation`.

## Implementation Guidance

The schema, its event-types, common fields, and event-specific fields are codified in `KB-mcp-design/references/principles.md` (single source of truth). The `KB-mcp-platform/references/mcp-events-jsonl.md` file references the schema and documents consumer expectations (tail command, audit rule, redaction-allowlist interaction with ADR-0039).

The file is **bootstrapped** on postCreate (touch-if-absent). The bootstrap state is `empty file present`. The first postStart run appends seven `readiness_probe` records (one per registered server in `.mcp.json` — Blueprint v3 OI-1 closure dropped the codebase-memory-mcp fallback entry per the user's Gate-4 decision; the inventory is now 7 named MCP servers with no fallback, see Blueprint v3 §Acceptance Criteria / AC-X-2). An absent file or zero records after postStart is itself an `auditing-mcp` OP-5 BLOCKER (the hook did not run). This resolves I-DR-004 (bootstrap-semantics gap) from cc-design-review.

The file is **gitignored.** Project-local `.gitignore` includes `.claude/runtime/mcp-events.jsonl`. The directory `.claude/runtime/` is committed via `.gitkeep` so operators see the location. (Resolves Q-CC-2 in favor of recommended option (a) per cc-design.)

Records are **append-only.** Plan-author may add a `mcp-events.jsonl` truncate helper command but the writers never delete or rewrite records mid-flight.

The stderr banner format is one line, `[mcp:server-name] primary degraded → falling back to <fallback>; see .claude/runtime/mcp-events.jsonl`. Plan-author may refine; the load-bearing requirement is "one-line, names the server, points at the JSONL."

## Related Information

- Related ADRs: ADR-0007 (GitNexus / codebase-memory-mcp primary/fallback policy), ADR-0018 (codebase-analysis schema), ADR-0038 (ADR-0018 bump to v1.1.0), ADR-0039 (credential redaction posture — consumes the same event surface).
- Referenced specs / docs: synthesis.md §3 D-0005, §5 Operational Discipline Brief, §7 risk 1 / ADR candidate 1; cc-design.md §`mcp-events.jsonl` schema (UI-15 contract); codespaces-design.md postStart.sh outline.
- Issues / PRs: I-DR-001 (inventory count, resolved by cross-reference to ADR-0038 wording), I-DR-004 (bootstrap semantics, resolved here in Implementation Guidance), I-DR-CS-004 (codebase-memory-mcp probe coverage, resolved via this ADR's schema requiring all registered servers to emit `readiness_probe`).
- Related KBs: KB-mcp-design (schema home), KB-mcp-platform (usage documentation), KB-cc-design Principles 4 (subagent isolation) and 5 (one source of truth).

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial ADR authoring during Blueprint v1 composition. Established `.claude/runtime/mcp-events.jsonl` schema, three event types, prose-only-with-OP-4 agent declaration. Bootstrap semantics specified eight `readiness_probe` records (seven primary + one ADR-0007 fallback). | design-composer |
| 2026-05-23 | 1.0.1 | Implementation Guidance edit (in-place, no version bump of decision content): bootstrap-semantics record count reverted from "eight" to "seven" `readiness_probe` records. Trigger: Blueprint v3 Gate-4 OI-1 closure — the user dropped the codebase-memory-mcp fallback from `.mcp.json` inventory (now 7 named MCP servers, no fallback entry). Cross-reference: Blueprint v3 AC-X-2 (PRD-bound inventory of 7 servers) and Blueprint v3 §Open Items / OI-1 closure. The decision content of this ADR (event surface, event types, prose-only declaration, OP-4 audit rule) is unchanged. | design-composer |
| 2026-05-26 | 1.0.2 | Prose-only amendment, no decision-content change. Triggered by `pipeline-quickwins-hardening-r1` Architecture Audit cycle 1 (findings I-AA-001 and I-AA-002). Two corrections: (a) §Decision item 2's event-type triad was incorrectly written as `primary_degraded / readiness_probe / structured_failure`; the actual on-disk triad per `audit_op7_events_schema.py` `VALID_EVENT_TYPES` and per `.devcontainer/postCreate.sh` live emissions is `install_complete / readiness_probe / structured_failure` (with `primary_degraded` as a boolean sub-field of `structured_failure`, not a top-level event type) — corrected. (b) §Architecture Impact item 4 referenced "OP-6 audit rule" for schema validation; the actual schema-validation rule is OP-7 (`audit_op7_events_schema.py`). OP-6 audits credential redaction in the runtime log — a distinct concern — corrected. Both edits are prose-only per ADR-0005's append-only discipline (decision content unchanged, only the description of pre-existing state moves to match the on-disk implementation). The Decision Details "v1.0.2 prose-correction note" row records the rationale for the future reader and acknowledges the irony that the ADR motivating the documentation-vs-realization drift carve-out carried that very drift in its own prose. | design-composer |
