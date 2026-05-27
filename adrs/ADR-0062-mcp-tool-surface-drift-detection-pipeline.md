---
id: ADR-0062
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0042, version: 1.0.0}
applies_to:
  - pipeline-cross-artifact-discipline-r1
  - auditing-mcp-skill-family
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes the four-stage RFC-grounded MCP `tools/list` drift-detection pipeline and the canonical baseline-storage location under `auditing-mcp/baselines/`.
---

# ADR-0062: MCP Tool-Surface Drift Detection — Four-Stage Pipeline and Baseline Location

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

The `devcontainer-mcp-provisioning-r1` post-mortem identified two related gaps in the MCP audit surface: no live reachability check (FR-4 in `pipeline-cross-artifact-discipline-r1`) and no detection of upstream tool-surface drift (FR-5). The second gap is more subtle than the first — even when a server is reachable, its tool surface can change between two runs (added tools, removed tools, signature changes), and no audit mechanism today surfaces that drift to operators.

FR-5 must achieve NFR-4 (<5% false-positive rate across 50 consecutive audits against a stable MCP server set). The dominant FP sources in OpenAPI-style diff tools are well-documented: openapi-diff Issue #673 (cited in synthesis claim C-0195) is the canonical cautionary tale — naive object-diff treats cosmetic changes (whitespace, key ordering, description rewordings) as drift and spams the audit surface.

T-001 in this feature's research notes establishes a cross-source triple for a four-stage pipeline architecture:

1. **Stage 1 — Canonicalization.** RFC 8785 (JSON Canonicalization Scheme) normalizes whitespace, key-ordering, number representation, and Unicode (NFC). This is the dominant FP-suppression locus.
2. **Stage 2 — Baseline lookup.** Persisted canonical baseline per server (the oasdiff change-fingerprint pattern, baseline-as-bytes).
3. **Stage 3 — Structured diff.** RFC 6902 (JSON-Patch) computes the diff with identity-keyed array semantics (MCP spec guarantees tool names are unique, so `name` is a valid identity key).
4. **Stage 4 — Severity-catalog routing.** Locally-enumerated catalog modeled on oasdiff routes patch operations to severities per AC-FR-5-a/-b/-c/-d/-e.

The baseline storage location is a separate sub-decision. Three candidates were enumerated in cc-design Q-CC-4:

1. `.claude/skills/auditing-mcp/baselines/<server-name>.json` (skill-owned, committed).
2. `.claude/runtime/mcp-baselines/<server-name>.json` (runtime-scoped, may be gitignored).
3. Repo-root.

The committed-skill-owned location wins because baselines must be reproducible across operators and across CI runs — a gitignored runtime location loses that reproducibility, and a repo-root location lacks the locality-of-reference advantage.

## Decision

FR-5 ships a four-stage drift-detection pipeline:

1. **Canonicalize** (RFC 8785) the live `tools/list` response per server.
2. **Baseline lookup.** Read `.claude/skills/auditing-mcp/baselines/<server-name>.json`. On absence: write Stage 1 output as the new baseline, emit `INFO` diagnostic, skip Stages 3–4.
3. **JSON-Patch diff** (RFC 6902) with identity-keyed array semantics on the `name` field.
4. **Severity-catalog routing.** Apply the catalog in `auditing-mcp/references/drift-severity-catalog.md`: tool-remove-of-allowlisted → `BLOCKER`; tool-add → `MAJOR`; signature-change-on-allowlisted → `MAJOR`; description/title/icon → `INFO`; unparseable → `MAJOR`.

The canonical baseline-storage location is `.claude/skills/auditing-mcp/baselines/<server-name>.json` — committed to the repo, one file per MCP server entry in `.mcp.json`. Baselines update only on operator-acknowledged `--accept-drift` flag; never on silent observation.

NFR-4 (<5% FP rate) is validated at Phase Validator authoring time by running 50 audits against the current stable MCP server set and refining the catalog if measured FP > 5%. The pilot is event-triggered (per FR-11 framing) — it runs at PV-authoring time, not "post-ship" calendar-based.

## Decision Details

| Item | Content |
|---|---|
| Decision | Four-stage RFC-grounded pipeline; baselines committed at `.claude/skills/auditing-mcp/baselines/`. |
| Why now | FR-5 ships in `pipeline-cross-artifact-discipline-r1`; the drift-detection algorithm must be defined for the auditor to run. |
| Why this | Each stage grounded in an independent primary source (RFC 8785, oasdiff fingerprint pattern, RFC 6902, oasdiff catalog mapping); openapi-diff Issue #673 is the documented evidence that naive diff fails this exact use case; each stage is replaceable without re-architecting the others. |
| Known unknowns | NFR-4's <5% FP claim is mechanistic (the normalization + catalog moves remove the dominant FP sources) but the exact number is extrapolated — no surveyed source publishes a quantitative benchmark for the exact MCP `tools/list` use case. Pilot validation at PV-authoring time is the closing artifact. |
| Kill criteria | If measured FP rate exceeds 5% across three consecutive runs (per the PRD-v2 Rollout Plan kill-criteria), the severity catalog is revisited — and if catalog tuning cannot close the gap, the four-stage pipeline contract is reconsidered. |

## Rationale

Each stage carries independent primary-source grounding:

- **Stage 1 (RFC 8785).** JSON Canonicalization Scheme is an IETF standard with well-tested implementations. The normalization removes the dominant cosmetic-diff FP sources (whitespace, key-ordering, number representation, Unicode-form differences).
- **Stage 2 (baseline-as-bytes).** oasdiff's change-fingerprint pattern — store the canonical baseline; diff against it. Reproducible across operators and CI.
- **Stage 3 (RFC 6902).** JSON-Patch is the IETF standard for structured JSON diffs. Identity-keyed array semantics use the MCP spec's tool-name uniqueness guarantee to handle array reordering without false-positive churn.
- **Stage 4 (severity catalog).** Locally-enumerated; modeled on oasdiff. AC-FR-5-a/-b/-c/-d/-e drive the row contents.

The composition is novel (oasdiff catalog → MCP `tools/list` schema) but each underlying primitive is sound. The novelty is what the pilot validates, not the underlying mechanics.

The baseline-storage choice prioritizes **reproducibility** over **gitignore convenience**. A gitignored baseline means two operators audit the same server and may get different drift verdicts because their local baselines diverge. A committed baseline means the audit is reproducible: every operator, every CI run, sees the same baseline.

Operator-acknowledged baseline updates (`--accept-drift`) preserve the audit trail: every baseline change shows up in `git log` as a deliberate operator action. Silent observation updates would defeat the audit purpose by erasing the prior state.

## Options Considered

### Option 1: Naive object-diff with heuristic severity

**Pros:** Minimal new infrastructure; no canonicalization step.

**Cons:** openapi-diff Issue #673 is the documented evidence that naive diff fails the exact use case; cosmetic changes (description-polishing, CDN-URL rewrites) read as drift; heuristic severity is per-author per-audit with no auditable contract; fails NFR-4 on any realistic upstream.

### Option 2: Vendor tool reuse (oasdiff or openapi-diff directly)

**Pros:** Battle-tested tooling.

**Cons:** Neither tool natively understands the MCP `tools/list` schema — they target OpenAPI / Swagger; an adapter layer (translate MCP → OpenAPI → vendor diff → translate severity back) is more code than the bespoke four-stage pipeline AND inherits vendor-tool quirks. T-001 explicitly cites oasdiff as model, not target for adoption.

### Option 3 (Selected): Four-stage RFC-grounded pipeline + committed baselines

**Pros:** Each stage carries independent primary-source grounding; FP-suppression located where evidence supports it (normalization + catalog routing); identity-keyed array diff grounded in MCP spec; each stage replaceable without re-architecting the others; reproducible baselines.

**Cons:** <5% FP claim is single-sourced and mechanistic; composition step is novel; pilot validation required at PV-authoring time; committed baselines occupy ~6 small files in the repo (one per MCP server, ~few KB each).

### Option 4 (Sub-decision: baseline storage): gitignored runtime path

**Pros:** Baselines don't clutter git history; local-only state.

**Cons:** Audits are not reproducible across operators; CI runs lose the audit trail; the operator-acknowledged update semantics (`--accept-drift`) lose their git-visible audit value.

## Consequences

### Positive Consequences

- The MCP-shipment-class drift defect becomes structurally detectable. Tool surface changes that affect allowlisted tools surface as `BLOCKER` findings before the change propagates downstream.
- The pipeline's design honors NFR-4's <5% FP target by locating FP-suppression at the right stages (normalization + catalog routing), not at diff defaults.
- Each stage is independently replaceable — if a better canonicalization standard emerges, Stage 1 swaps without touching Stages 2–4.
- Committed baselines make audits reproducible across operators and CI runs.

### Negative Consequences

- New convention: 6 baseline files committed to the repo at first encounter (actionlint-mcp, context7, exa, gitnexus, serena, terraform-mcp).
- Baseline drift requires explicit operator action (`--accept-drift`); silent updates are forbidden.
- The <5% FP claim is mechanistic, not measured; the pilot at PV-authoring time is the validation.

### Neutral Consequences

- `auditing-mcp` skill family gains a new subdirectory (`baselines/`) and a new reference file (`drift-severity-catalog.md`).
- Two new scripts under `auditing-mcp/scripts/`: `check_mcp_reachability.py` (FR-4) and `check_tool_surface_drift.py` (FR-5).

## Architecture Impact

**Components that change:**

1. `.claude/skills/auditing-mcp/scripts/audit_mcp.py` — new dispatch for reachability + drift after the existing static-audit pass.
2. `.claude/skills/auditing-mcp/scripts/check_mcp_reachability.py` — new (FR-4).
3. `.claude/skills/auditing-mcp/scripts/check_tool_surface_drift.py` — new (FR-5; implements the four-stage pipeline).
4. `.claude/skills/auditing-mcp/baselines/` — new subdirectory; 6 baseline files at first encounter.
5. `.claude/skills/auditing-mcp/references/drift-severity-catalog.md` — new reference (Stage 4 catalog).

**New dependencies introduced:**

- Drift detection → committed baselines (read/write per `--accept-drift` semantics).
- Audit output → severity-vocabulary bridge table (ADR-0061).

**Architectural constraints added:**

- Baselines update only on operator-acknowledged `--accept-drift`; silent updates forbidden.
- Each MCP server entry in `.mcp.json` has at most one baseline file; the baseline filename is the server name.

**Layers affected:**

- Claude Code / Project Filesystem (only in-scope layer).

## Implementation Guidance

The pipeline's stages are **independently replaceable**. If the JSON Canonicalization Scheme evolves, Stage 1 swaps without touching the rest. If a better diff representation emerges, Stage 3 swaps. The composition discipline is: each stage has a single responsibility; the contract between stages is the canonical/diff/severity intermediate.

The severity catalog is the **operator dial** for FP suppression. If the pilot at PV-authoring time measures FP > 5%, the catalog rows for description/title/icon changes are tunable first (they are the most common FP sources). Signature changes and tool add/remove events are never normalized away — they are the load-bearing findings.

Baseline files are part of the audit trail. Their git history is a feature: every baseline change shows up as an operator action. The `--accept-drift` semantics make the operator decision explicit at the moment of update.

NFR-3 (drift detection wall-clock <500 ms/server) is honored by the staged architecture — each stage is bounded by the size of the per-server `tools/list` response, which is typically a few KB.

## Related Information

- Related ADRs: ADR-0042 (auditing-mcp family graduation — host for FR-4/5), ADR-0061 (severity vocabulary bridge — catalog severities map cross-surface), ADR-0039 (credential indirection — NFR-6 redaction rides on it).
- Referenced specs / docs: RFC 8785 (JSON Canonicalization Scheme), RFC 6902 (JSON-Patch); `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` §Drift-detection algorithm flow; `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` D-7.
- Issues / PRs: `Issues/cross-artifact-divergence-detection-gap/analysis.md`; openapi-diff Issue #673 (cautionary tale).
- Related KBs: `KB-mcp-platform`, `KB-mcp-design`, `auditing-mcp`.
