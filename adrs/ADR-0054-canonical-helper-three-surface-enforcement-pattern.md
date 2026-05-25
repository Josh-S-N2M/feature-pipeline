---
id: ADR-0054
version: 1.0.1
status: Accepted
generated: 2026-05-24
generated_by: design-composer
revised: 2026-05-25
revised_after: architecture-audit-r1
revised_by: design-composer
supersedes: []
adrs_inherited: [ADR-0031, ADR-0035, ADR-0042, ADR-0036]
applies_to:
  - adr-placement-mechanism-repair-r1
  - .claude/skills/auditing-shared/scripts/ (canonical-helper home)
  - .claude/skills/auditing-shared/scripts/validate_adr_placement.py (first non-audit-family consumer)
  - .claude/agents/finalize-deliverable-packager.md (consumer surface c)
  - .claude/skills/auditing-shared/scripts/run_phase_checks.py (consumer surface b)
  - .claude/skills/recipe-feature-pipeline/SKILL.md (consumer surface a)
  - future enforcement-class validators that follow the same triad pattern
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Extends ADR-0042's canonical-helper-home framing beyond the audit-family
  consumer set to a non-audit triad (orchestrator stage gate + execution-pipeline
  hook + finalize packager). Establishes the three-surface enforcement pattern
  for any pipeline-governance validator: same script, same default args, same
  exit-code semantics, same JSON output shape; three independent integration
  points each catching a distinct failure window. Codifies the per-invocation
  CLI-flag allowlist mechanism with two distinct usage modes (steady-state
  carve-outs at hard-coded dispatch sites; mid-migration ephemeral entries).
  Resolves the Research-Plan-adjacency-#2 concern surfaced by Synthesis D4.
  v1.0.1 resolves AA-007 (commitment-1 "same args" overstatement) and AA-015
  (commitment-2 steady-state vs mid-migration allowlist disambiguation),
  surfaced by architecture-audit-r1.
---

# ADR-0054: Three-surface enforcement pattern for canonical-helper validators (extension of ADR-0042 to non-audit consumers)

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

Accepted — 2026-05-24 (authored during Design Composition of `adr-placement-mechanism-repair-r1`).

## Context

ADR-0031 established `auditing-shared/scripts/` as the canonical home for cross-skill helper scripts. ADR-0035 codified the subprocess-dispatch + JSON-output + exit-0/2 convention. ADR-0042 graduated `auditing-mcp` to its own family and established the family-coordinator-as-consumer pattern; up to that point, the canonical-helper home was consumed exclusively by audit-family coordinator skills (`auditing-cc-configs`, `auditing-github-actions`, `auditing-codespaces`, etc.) and by the execution-pipeline `run_phase_checks.py` coordinator.

The `adr-placement-mechanism-repair-r1` feature requires a new validator — `validate_adr_placement.py` — that does NOT belong to any audit family. Its consumers are three non-audit-family surfaces:

- **Surface (a)**: the `recipe-feature-pipeline` orchestrator at Step 8 (Design Composition), catching author-time placement violations before reviewer invocation.
- **Surface (b)**: the execution-pipeline `run_phase_checks.py` parallel-dispatch coordinator, catching runtime violations during per-feature plan execution.
- **Surface (c)**: the `finalize-deliverable-packager` at Step 14, catching finalize-time violations as the last line of defense.

The PRD's NFR-6 explicitly requires non-redundancy and non-contradiction across the three surfaces. The Research Plan's adjacency #2 note flagged that extending ADR-0042's consumer set beyond the audit families is an architecturally meaningful precedent that should be explicitly captured so the Architecture Auditor does not treat it as an unannounced expansion.

Three structural questions emerged from the per-layer Design's Q-CC-3, Q-CC-5, Q-CC-6, Q-CC-7:

1. **Allowlist mechanism** — per-invocation CLI flag or persisted config file?
2. **Tool grant for packager** — add `Bash` to the packager's tools or invoke validator orchestrator-side?
3. **Dimension placement in run_phase_checks.py** — new dimension or fold into existing `validator` dimension?

Without an ADR, each future enforcement-class validator would re-litigate these structural choices, producing inconsistent integration patterns and inviting drift across surfaces.

## Decision

Enforcement-class validators (validators that enforce a pipeline-governance invariant rather than auditing a domain-specific configuration family) live in the canonical-helper home (`.claude/skills/auditing-shared/scripts/`), follow the existing CLI / exit-code / JSON conventions of ADR-0035, and integrate at three independent surfaces with the following structural commitments:

1. **Same script, same default args, same exit-code semantics, same JSON shape** at all three surfaces. Allowlist content is per-surface contextual (orchestrator + packager pass none; `run_phase_checks.py` passes `--allowlist output/synthesis-*/adrs/` per the synthesize-skill carve-out documented in the consuming Blueprint). The only inter-surface difference beyond the contextual allowlist content is the failure-surfacing mechanism (orchestrator surfaces via `AskUserQuestion`; `run_phase_checks.py` rolls into its 5-dimensional verdict; packager folds into `packager-report.json`).
2. **Per-invocation CLI-flag allowlist** (`--allowlist <comma-separated-paths>`). Empty default. No persistent config file. Two intended usage modes:
   - (a) **Steady-state allowlist entries** (e.g., the synthesize carve-out `output/synthesis-*/adrs/`) passed at every dispatch of the consuming script. These are hard-coded into the dispatch site itself; the dispatch site is the persistent declaration surface (NOT a config file).
   - (b) **Mid-migration allowlist entries** (e.g., during in-flight Phase 2 folders) passed once and removed when the migration phase ends.

   Both modes use the same CLI flag mechanism; persistent config-file state is forbidden. The steady-state usage carries no persistent config file because the dispatch site itself is the persistent declaration surface (a single code path with a hard-coded flag), which remains auditable at the call site rather than buried in a config file.
3. **Subprocess invocation requires `Bash` tool grant** at any consumer that runs the validator directly. The grant is narrowly scoped via `.claude/settings.json` allowlist entries to the specific script path; broader grants are rejected as lowering safety-net specificity per KB-cc-design Principle 6.
4. **`run_phase_checks.py` dimension** for enforcement validators is the existing `validator` dimension (sibling of `validate_pipeline_frontmatter.py`); a dedicated dimension is reserved for cases where rollup granularity is load-bearing distinct.
5. **Non-redundancy proof** is mandatory in the authoring Blueprint: each surface must catch a documented failure window the other two cannot.

## Decision Details

| Item | Content |
|---|---|
| Decision | Three-surface enforcement pattern for canonical-helper validators: same script + per-invocation CLI allowlist + narrow Bash grant + `validator` dimension by default + non-redundancy proof. |
| Why now | The `adr-placement-mechanism-repair-r1` feature is the first non-audit-family consumer of the canonical-helper home; without explicit framing, the Architecture Auditor and future contributors lose the precedent and re-litigate each structural choice. |
| Why this | Reuses every existing convention (ADR-0031 home, ADR-0035 dispatch shape, ADR-0042 consumer pattern) and adds only the structural commitments unique to enforcement-class validators (non-redundancy, CLI allowlist, narrow Bash grant). |
| Known unknowns | (1) Whether future enforcement validators will need a fourth surface (e.g., a pre-commit hook outside Claude Code). (2) Whether the per-invocation CLI flag scales when an enforcement validator has dozens of legitimate exceptions (current expectation: empty allowlist is the steady state). |
| Kill criteria | If two enforcement validators produce contradictory verdicts on the same artifact, or if the CLI-flag allowlist gets routinely set to non-empty values across runs, the pattern has failed and a config-file allowlist becomes warranted. |

## Rationale

The pattern is deliberately conservative — it reuses every existing canonical-helper convention rather than introducing a new mechanism. The three commitments unique to enforcement validators (allowlist mechanism, Bash grant, dimension placement, non-redundancy proof) are the smallest set that prevents the failure modes the per-layer Design surfaced:

- **CLI-flag allowlist over config file**: a persistent config invites silent drift. An ADR-placement allowlist entry left over from Phase 2 mid-migration that no one removed would defeat the entire enforcement purpose. The CLI flag is auditable at the call site and ephemeral by construction.
- **Narrow Bash grant over broad grant or orchestrator-side invocation**: the packager already owns the `packager-report.json` shape; pushing validator invocation upstream splits responsibility for one output across two agents. The smallest possible grant (narrow path scope in `.claude/settings.json`) preserves KB-cc-design Principle 6 (permissions-as-safety-net specificity).
- **Fold into `validator` dimension by default**: a new dimension per enforcement validator inflates the run_phase_checks rollup without architectural justification. The dimension granularity is a rollup-design decision, not a substantive one.
- **Non-redundancy proof in Blueprint**: catches the case where three surfaces inadvertently duplicate effort (extra latency without extra coverage) and the case where they contradict (orchestrator says PASS, packager says BLOCK on the same input).

## Options Considered

### Option 1: Single-surface enforcement (packager only)

**Pros:** Minimum integration effort; aligns with the pre-feature single-surface PKG-BLOCKER-001 model.

**Cons:** Defeats the explicit user directive at the Intent Confirmation Gate ("enforcement gates and validates the correct location"). Single surface failed empirically — the entire `adr-placement-mechanism-repair-r1` feature exists because a single declarative source-of-truth contradicted itself. Three independent surfaces provide defense in depth.

### Option 2: Three surfaces but with per-surface bespoke integrations (different scripts, different conventions per consumer)

**Pros:** Each consumer can optimize for its specific context.

**Cons:** Multiplies maintenance burden by 3x; near-certain to drift; contradicts NFR-6 (non-contradiction) by construction. Defeats the purpose of the canonical-helper home.

### Option 3 (Selected): Three surfaces, same script, structural commitments unique to enforcement validators

**Pros:** Reuses every existing convention; non-redundancy proof catches the failure mode; CLI-flag allowlist prevents drift; narrow Bash grant preserves the safety net; dimension folding keeps rollup stable.

**Cons:** Phase 2 of any feature introducing such a validator must include a non-redundancy proof in the Blueprint (one extra section). The Bash grant requires a `.claude/settings.json` edit (one extra file).

## Consequences

### Positive Consequences

- Future enforcement-class validators (e.g., a future "validate-no-feature-scoped-blueprints" or "validate-canonical-skill-naming") follow the same pattern without re-litigation.
- The Architecture Auditor has a citable precedent when reviewing a Blueprint that introduces such a validator; the non-redundancy proof is a checkable item, not a judgment call.
- The pattern's structural commitments (no persistent allowlist, narrow Bash grant) constrain the failure mode the originating feature exists to prevent — silent drift and dual sources of truth.

### Negative Consequences

- The Plan must author a non-redundancy proof in the Blueprint for every enforcement validator; this is one additional section, ~10–20 lines.
- The narrow Bash grant pattern requires editing `.claude/settings.json` for each new consumer; this is one additional file per validator.

### Neutral Consequences

- Existing audit-family validators (`validate_pipeline_frontmatter.py`, `pedagogical_marker_check.py`, etc.) are unaffected; the pattern applies to enforcement-class validators, not audit-class validators.
- The `validator` dimension in `run_phase_checks.py` grows to include enforcement validators; rollup arithmetic is unchanged.

## Architecture Impact

1. **Components that change**:
   - `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` (new; first enforcement-class validator).
   - `.claude/skills/auditing-shared/scripts/run_phase_checks.py` (modified to add validator to parallel-dispatch set; `validator` dimension extended).
   - `.claude/agents/finalize-deliverable-packager.md` (modified: tools list gains `Bash`; new §"### 3. ADR placement validator" replaces the FR-1-deleted prose).
   - `.claude/skills/recipe-feature-pipeline/SKILL.md` (modified: Step 8 adds the orchestrator-stage gate before reviewer invocation).
   - `.claude/settings.json` (modified: narrow allowlist entry for the packager's Bash grant).

2. **New dependencies introduced**: None. Python stdlib only per NFR-8; reuses existing subprocess-dispatch infrastructure.

3. **Architectural constraints added or removed**:
   - **Added**: Enforcement-class validators must follow the three-surface pattern with documented non-redundancy proof.
   - **Added**: Allowlist mechanism for enforcement validators is per-invocation CLI flag; persistent config is forbidden.
   - **Removed**: The implicit assumption that the canonical-helper home is audit-family-only is removed; the home is explicitly extended to enforcement-class consumers per this ADR.

4. **Layers affected**: Claude Code / Project Filesystem only.

## Implementation Guidance

- **CLI shape**: positional `[scan_path]` (default `.` per ADR-0027 cwd precondition), optional `--allowlist <comma-separated-paths>` flag (default empty). Conform to ADR-0035 (stdlib only; JSON to stdout; exit 0/2).
- **Non-redundancy proof template**: per-surface table in the Blueprint stating which class of violation each surface catches and which would slip past the other two. Sample shape: orchestrator catches author-time (before reviewer); run_phase_checks catches runtime (during plan execution); packager catches finalize-time (last line of defense).
- **Bash grant**: edit the consuming sub-agent's `tools:` frontmatter to add `Bash`; edit `.claude/settings.json` `allow` list with a narrow entry for the specific script path (e.g., `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)`).
- **Dimension fold**: add validator to `run_phase_checks.py`'s dispatch set; its findings count toward the existing `validator` dimension's verdict.
- **Non-canonical allowlist exceptions**: structural-not-contingent exceptions (e.g., `adrs/superseded/` is allowed as a subdirectory of canonical) are hard-coded into the validator algorithm, NOT expressed via allowlist. Contingent exceptions (mid-migration in-flight folders, the `output/synthesis-*/adrs/` synthesize-skill carve-out) go through the CLI flag.

Procedural details (which file is edited first; what commit boundary applies) belong to the Plan, not this ADR.

## Related Information

- Related ADRs: ADR-0031 (canonical-helper home), ADR-0035 (subprocess + JSON + exit-code convention), ADR-0042 (family-coordinator-as-consumer pattern; this ADR extends the consumer set to non-audit-family), ADR-0036 (single-location ADR placement — the invariant this enforcement validator enforces), ADR-0017 (reviewer invocation points — the orchestrator-stage gate is between Design Composition and reviewer), ADR-0044 (flatten execution dispatch — the execution-pipeline surface lives at `run_phase_checks.py`), ADR-0027 (cwd precondition — validator's default scan path).
- Referenced specs / docs: `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` (NFR-6 non-redundancy proof), Synthesis D4 + research-plan adjacency #2.
- Related KBs: `KB-cc-design` (Principle 1 lowest-cost primitive, Principle 6 permissions-as-safety-net), `KB-cc-platform` (subprocess + permission policy), `KB-documentation-criteria` (Blueprint template for non-redundancy proof location).

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | design-composer | Initial authoring during Design Composition of `adr-placement-mechanism-repair-r1`. |
| 1.0.1 | 2026-05-25 | design-composer | Frontmatter-stable amendment per ADR-0005, in response to architecture-audit-r1 findings AA-007 + AA-015. Commitment 1: replaced "same args" with "same default args; allowlist content is per-surface contextual" to align with the actual Blueprint allowlist enumeration (run_phase_checks.py passes --allowlist for the synthesize carve-out; the other two surfaces pass none). Commitment 2: distinguished steady-state allowlist usage (hard-coded at dispatch site; persistent declaration surface; e.g., synthesize carve-out) from mid-migration usage (ephemeral; one-shot; phase-bounded). Both modes use the same CLI flag mechanism; no persistent config file in either case. No supersession; Decision text unchanged in spirit. |
