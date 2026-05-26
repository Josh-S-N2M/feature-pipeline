---
id: DD-CC-pipeline-quickwins-hardening-r1
version: 0.2.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
doc_type: per-layer-design
layer: claude-code
derived_from:
  - working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
  - working/feature/pipeline-quickwins-hardening-r1/synthesis.md
  - working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
  - working/feature/pipeline-quickwins-hardening-r1/codebase-analysis-report.md
  - working/feature/pipeline-quickwins-hardening-r1/research-plan.md
generated: 2026-05-26T00:00:00Z
generated_by: design-cc
revision_history:
  - version: 0.1.0
    date: 2026-05-26
    note: initial draft
  - version: 0.2.0
    date: 2026-05-26
    note: Gate-1 conditional-approval revision; resolves I-DR-001 (agent-count consistency to 5-agents/9-sites), I-DR-002 (verdict case-sensitivity rule added), I-DR-003 (per-agent exclusion rationale table), I-DR-004 (D-0003 refinement flagged + Q-CC-6 added), I-DR-005 (execution_mode reframed as new schema field), I-DR-006 (no-ADR-amendment line softened), I-DR-007 (FR-7 ACs placement-agnostic), I-DR-008 (FR-3 findings table reworded for symmetry)
---

# Claude Code / Project Filesystem — per-layer Design

## Layer responsibility scope

This layer owns the `.claude/` configuration that closes four of the five mechanically bounded MCP-incident exposures and one of the two housekeeping items in the carve-out:

- The verdict-vs-findings consistency check for reviewer-shaped sub-agents (FR-1).
- The orchestrator's dispatch self-check that refuses FULL-scope plus single-agent-fallback (FR-2).
- A new `auditing-mcp` audit rule that compares `.mcp.json` against ADR-0041's invocation taxonomy (FR-3), including the in-rule deprecation-marker convention that closes the day-one false-positive against the historically-removed `mcp-openapi-schema` row.
- The deferral-register tightening for rows H-4 and B-1 (FR-7).
- The Claude-Code side of the cross-cutting actionable-diagnostic contract (FR-6 applied to the FR-1, FR-2, FR-3 mechanisms).

The Codespaces side of FR-6 (the FR-4 dry-run's diagnostic shape) lives in `design-codespaces`. The CI/CD side of FR-6 (the FR-5 workflow's failure summary) lives in `design-cicd`. This layer documents only the parts of FR-6 it owns.

Out of scope for this layer (handled by sibling designers): FR-4 GitNexus install dry-run → `design-codespaces` (devcontainer post-create flow); FR-5 CI workflow for `claude mcp list` connectivity → `design-cicd`.

## What this layer is NOT doing

Three structural decisions deliberately stay inside the carve-out and are documented here as non-actions so the composer can reconcile against them:

- **No new MCP server.** Per NFR-15 / ADR-0040, no sub-agent allowlist changes and no new `mcp__*` entries.
- **No decision-text amendment to ADR-0041's rationale, options, or invocation-form prescriptions.** Per the carve-out, the deprecation of the `mcp-openapi-schema` row is handled by an in-rule marker convention. The marker is an **annotation pattern** (a new status token appended to one row) — a non-decision-text edit to the ADR's invocation table — not a rewrite of the ADR's decision, rationale, options, or any invocation-form prescription. The row's invocation form is preserved verbatim; only a status marker is added. See the FR-3 section below and the inventory row at line 53 for the literal annotation edit.
- **No new MCP audit rule beyond the parity rule.** The broader "design-realization audit dimension" is a Won't-Have. FR-3 introduces exactly one new OP rule (OP-11).

## Inventory of CC primitives introduced or modified

| Primitive | Type | Path | Purpose | Scope | Activation | Lowest-cost justification |
|---|---|---|---|---|---|---|
| `verdict_findings_parity` Python validator | Script under existing skill | `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` (NEW) | FR-1: structurally inspect a reviewer-emitted JSON for the contradiction "approving verdict + finding with severity in the blocking set" | project | invoked out-of-agent by `recipe-feature-pipeline` immediately after each reviewer-shaped sub-agent completes, before the verdict is consumed downstream | A Python script under the existing `auditing-shared` skill is the lowest-cost primitive: zero context cost (it is a shell-invoked validator, not a model artifact), single implementation surface (one script, not seven per-agent rules), and inherits `auditing-shared`'s existing `python3` runner convention. A Claude Code hook (`PostToolUse`) was considered and rejected: hooks fire on tool-call boundaries, not on sub-agent completion, and the reviewer outputs are written by the sub-agent's own `Write` calls — so the hook would fire on every Write in the project, which is worse than running one explicit script at one explicit invocation point. |
| `recipe-feature-pipeline` SKILL.md — verdict-parity hook step | Edit to existing orchestrator skill | `.claude/skills/recipe-feature-pipeline/SKILL.md` | FR-1: invoke the validator at each of the 9 distinct reviewer-completion invocation sites — 5 `shared-document-reviewer` invocation points (per ADR-0017), the Stage 8 auditor output, the Stage 11 auditor output, the T7 phase-quality-reviewer output, and the T2 execute-task-quality-handler output — covering the 5 reviewer-shaped agents in scope per D-0002 | project | always | The orchestrator is the single dispatch nexus per ADR-0044; instrumenting it once is cheaper than instrumenting each reviewer. |
| `recipe-feature-pipeline` SKILL.md — dispatch self-check step | Edit to existing orchestrator skill | `.claude/skills/recipe-feature-pipeline/SKILL.md` | FR-2: at orchestrator entry, before Stage 1 dispatch, refuse to enter the loop if `scope_class == FULL` and any stage's per-stage agent configuration matches the named fallback surface | project | always (at orchestrator entry only) | The check belongs in the orchestrator itself because the orchestrator owns dispatch (ADR-0044). A separate hook would create a second failure path (hook misconfigured, hook silently skipped) and a second `scope_class` read site. Orchestrator-internal logic is the lowest-cost shape that gives a single source of truth. |
| `recipe-feature-pipeline` SKILL.md — hoist `scope_class` read | Edit to existing orchestrator skill | `.claude/skills/recipe-feature-pipeline/SKILL.md` line 350 (read site relocated, not duplicated) | FR-2: make `scope_class` available at orchestrator entry, where the dispatch self-check runs, rather than only at Stage 13 Deliverable Packaging | project | always | Single-read-site hoist; no new file surface. Per synthesis D-0003 verified at codebase-C-0028. |
| `audit_op11_adr_parity.py` Python script | New OP rule script under existing skill | `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` (NEW) | FR-3: for each server in `.mcp.json`, locate its row in ADR-0041's invocation table and compare the canonicalized invocation form; emit a BLOCKER finding on mismatch, on a `.mcp.json` server not in ADR-0041, or on an ADR-0041 row (not marked `[DEPRECATED]`) not in `.mcp.json` | project | invoked by `auditing-mcp/scripts/audit_mcp.py` coordinator; runs at Gate 6 per ADR-0043 | The `auditing-mcp` skill already hosts ten OP rules with a uniform contract (one positional argument, JSON stdout, exit 0/1/2). Adding rule OP-11 is the lowest-cost extension: zero new infrastructure, inherits Gate-6 hard-gate semantics from ADR-0043, and matches the project's audit-rule-naming convention. |
| `auditing-mcp` SKILL.md routing table update | Edit to existing skill | `.claude/skills/auditing-mcp/SKILL.md` | FR-3: register dimension 11 ("ADR-0041 invocation parity") in the SKILL.md routing table; cite the new OP rule and its rationale-reference file | project | model-invocable (existing) | The routing table is the project's documented surface for OP rules; updating it is the minimum-surface change to make the new rule discoverable. |
| `auditing-mcp/references/adr-parity.md` rationale reference | New reference under existing skill | `.claude/skills/auditing-mcp/references/adr-parity.md` (NEW) | FR-3: document the comparison algorithm (canonicalize whitespace; treat `${VAR}` placeholders as opaque tokens; string-equal after canonicalization); document the in-rule `[DEPRECATED]` marker convention; cite ADR-0041 v1.0.1 and CLAUDE.md line 9 | project | loaded on demand by audit reviewers; not in main context | A `references/` doc is the canonical home for OP-rule rationale (see existing `mcp-spec.md`, `anti-patterns.md`, etc.). Lowest-cost placement; zero main-context cost. |
| ADR-0041 invocation table — add `[DEPRECATED]` marker on the `mcp-openapi-schema` row | Annotation edit to existing ADR | `adrs/ADR-0041-install-mechanism-hybrid.md` line 71 | FR-3 / D-0005: prevent the day-one false-positive against the historically-removed `mcp-openapi-schema` row by tagging it with the marker the OP-11 rule recognizes | project | inline in the ADR table | This is an **annotation**, not a decision-text rewrite. The marker is a new token on an existing row; the row's text body (its invocation form) is preserved verbatim. ADR-0005's append-only posture is honored: the row is not removed, the decision is not retracted. See "ADR-0041 annotation: is this a decision-text edit?" in the FR-3 section for the carve-out-compatibility analysis. |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — confirm + tighten existing adoption markers on rows B-1 and H-4 | Edit to existing artifact | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` lines 56 and 141 | FR-7: confirm the existing inline adoption parentheticals match the canonical row-update convention exactly (date, slug, link); update the Why-excluded / Re-examination-trigger / Forgetting-risk cells if they have not already been updated | project | static document | Per codebase-analysis: the parentheticals are already in place; FR-7 verifies and tightens, doesn't author from scratch. Zero new artifacts. |

No new sub-agents, no new top-level skills, no new hooks, no new MCP servers, no new plugins, no new output styles, no CLAUDE.md edits. The changes layer entirely onto existing primitives.

## CLAUDE.md changes

**None.** Per KB-cc-design Principle 5 (one source of truth), the FR-3 rationale (in-rule deprecation marker) lives in `auditing-mcp/references/adr-parity.md`, not in CLAUDE.md. CLAUDE.md already references KB-mcp-platform / KB-mcp-design / `auditing-mcp` via its existing MCP block; the new OP-11 rule is discoverable through the existing `auditing-mcp` SKILL.md routing table, which CLAUDE.md already points to ("MCP audit ruleset (OP-1..OP-10)" in the Deeper-reference table). When OP-11 lands, the CLAUDE.md entry should read "OP-1..OP-11" — but that single-character edit is the only CLAUDE.md change, and it is a counter update (no new sentence). Per Principle 5 it does not duplicate the OP-11 rationale; it just bumps the count. The composer should apply this single-character update at deliverable-archive time as a fact-of-record edit, not as a load-bearing instruction change.

## Rule patterns

No new rules in this design. The existing project does not use a `.claude/rules/` tree for the orchestrator or audit primitives; behavior is carried in SKILL.md files and Python audit scripts. Introducing a rule for this carve-out would be a category error (per KB-cc-design Principle 2, rules are for path-gated convention enforcement, not for orchestrator dispatch logic).

## Skill patterns

The `auditing-mcp` skill is the only skill modified. Its existing frontmatter (model-invocable; `allowed-tools: Read Grep Glob Bash(python3 *)`) already accommodates the new OP-11 rule. No frontmatter change. No `disable-model-invocation` flag needed — the audit skill is intentionally model-invocable so that the architecture auditor and other reviewer agents can pull it on demand.

The new rationale reference `auditing-mcp/references/adr-parity.md` follows the existing `references/` pattern. Per `pedagogical_sections:` discipline (the skill's existing `pedagogical-marker-justification-spec`-aligned frontmatter list), the new reference SHOULD be added to that list with a justification line. The Plan-author will own the literal frontmatter edit; this design specifies the intent: the new reference is justified by "documents the new OP-11 rule's comparison algorithm and the in-rule `[DEPRECATED]` marker convention; required reading for any reviewer triaging an OP-11 finding."

`auditing-shared` (the Python-script home for `verdict_findings_parity.py`) is also modified additively. It already hosts cross-family utilities per ADR-0031. The new validator is a single file, no frontmatter change required.

## Subagent patterns

No new sub-agents and no modifications to existing sub-agent frontmatter (model, effort, tools, skills, memory). Per KB-cc-design Principle 9, this is intentional: the FR-1 validator is a deterministic structural check, not a reasoning task, so model/effort selection does not apply. The orchestrator self-check (FR-2) is orchestrator-internal logic; the orchestrator skill has no `model:` / `effort:` frontmatter because the orchestrator is a SKILL.md, not an agent file.

For completeness against Principle 9: every reviewer-shaped sub-agent FR-1 covers (`shared-document-reviewer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, `execute-phase-quality-reviewer`, `execute-task-quality-handler`) already has `model: opus` and `effort: high` (or `xhigh` for the two terminal auditors per the worked example in KB-cc-design Principle 9). FR-1 does not modify those choices. The `skills:` arrays on each agent are domain-knowledge preloads (KB-review-disciplines, KB-documentation-criteria) — none are being changed.

## Hook patterns

**No new hooks.** This is a deliberate choice, justified per KB-cc-design Principle 1 (lowest-cost primitive) and Principle 3 (enforce vs instruct):

- For FR-1, a `PostToolUse` hook firing on `Write` would activate for every Write in the project. Filtering to reviewer-output Writes would require encoding the 5 reviewer-shaped agents' output paths (across 9 invocation sites) into the hook config — fragile and high-maintenance. The orchestrator's existing dispatch boundary is the right structural seam.
- For FR-2, a `SessionStart` hook is conceivable but redundant: the orchestrator already runs first per the `recipe-feature-pipeline` entry contract. Adding a hook would create a second read site for `scope_class` (which we are explicitly hoisting in the orchestrator) and a second failure path.

Both behaviors are deterministic and safety-critical (per the PRD's strictness-over-ergonomics tiebreaker), so per Principle 3 they need to be **enforced**, not merely instructed. They are enforced — by the orchestrator's own logic, which is mandatory on every run. The orchestrator's gate-history mechanism already provides the "halt and surface to user" behavior the refusal needs.

## Permission policy

No changes to `.claude/settings.json` permissions in this design. The new Python validator and the new OP rule both run via `Bash(python3 *)`, which is already in the allowlist for the agents that consume them (the orchestrator's `python3` runner via `recipe-feature-pipeline`, and the architecture auditor / reviewer agents' existing `Bash(python3 *)` entries).

Per KB-cc-design Principle 6 (permissions as safety net, not the design): the FR-1 / FR-2 / FR-3 enforcement mechanisms do not rely on permissions to function. They are deterministic checks the orchestrator runs explicitly. Permissions remain the safety net for everything else (e.g., the existing `permissions.deny` patterns for production paths and unsafe Bash invocations are unchanged).

## MCP server policy

No changes. NFR-15 is satisfied by construction:

- No new MCP server is added.
- No existing MCP server is reconfigured.
- The seven sub-agents with `mcp__*` allowlist entries (per ADR-0040 — `review-architecture-auditor`, `discovery-external-researcher`, `discovery-codebase-researcher`, `design-iac`, `design-codespaces`, `design-claude-code`, `design-cicd`) keep their existing allowlists unchanged.

The `.mcp.json` artifact is read-only consumed by FR-3 (the OP-11 audit script reads it as data) and FR-5 (the CI workflow reads it via `claude --bare -p`). Neither side perturbs the file.

## Plugin packaging

**None.** Per KB-cc-design Principle 7 (plugins for distribution, not organization): this feature ships project-specific machinery for the feature-pipeline. No other project would consume it. Bundling into a plugin would add manifest / versioning / distribution overhead with zero benefit. The artifacts commit directly into `.claude/`.

## Command-to-skill migration

**None.** The project has no `.claude/commands/*.md` artifacts in the orchestrator / audit surfaces. The existing model-invocable skills (`recipe-feature-pipeline`, `auditing-mcp`) already follow the post-migration shape per KB-cc-design Principle 8.

---

## FR-1 — Verdict-vs-findings parity validator (D-0001, D-0002)

### Decision

**Execution site:** out-of-agent — a single Python validator invoked by the orchestrator immediately after each reviewer-shaped sub-agent completes. Path: `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py`. This closes U-1's "in-agent vs out-of-agent" sub-question.

**Why out-of-agent.** Per synthesis D-0001: in-agent self-validation multiplies the implementation surface by 5 (the in-scope reviewer-shaped agent inventory per D-0002) — and instrumentation must be repeated across all 9 invocation sites. A future reviewer-shaped agent added to the project would need the same edit. A single downstream validator gives the same guarantee at one-fifth the maintenance cost (~one-ninth if counting invocation sites). The verified failure mode (codebase-C-0018: `execute-task-quality-handler`'s contract today structurally allows APPROVED + severity:BLOCKER co-occurrence) is what justifies building the validator at all.

**Blocking-severity set:** `{BLOCKER}` only. Lower-case `blocker` (the auditor-family alias used in `execute-task-quality-handler`'s findings) is included by case-insensitive normalization. Severity tokens `MAJOR`, `MINOR`, `NIT`, `INFO` are **not** in the blocking set for this validator.

**Why narrower than `{BLOCKER, MAJOR}`.** Per synthesis D-0001 and the constraint analysis: including MAJOR would retroactively turn every historical APPROVED-with-MAJOR-finding reviewer output into an inconsistency, which is a scope expansion (NFR-9 backward-compatibility breach). The PRD's strictness-over-ergonomics tiebreaker is honored at the limit by deferring the broader catch surface to a future feature, not by silently adopting it here.

### Reviewer scope (D-0002)

The validator runs against output from **5 reviewer-shaped agents in scope per D-0002**, instrumented at **9 distinct invocation sites** (the 5 `shared-document-reviewer` invocation points + 2 auditor stages + 1 T7 + 1 T2):

1. `shared-document-reviewer` — at all 5 ADR-0017 invocation points.
2. `review-architecture-auditor` — Stage 8 output (`architecture-audit-issues.json`).
3. `review-cross-artifact-auditor` — Stage 11 output (`cross-artifact-audit-issues.json`). Validator inspects only the **primary** verdict field, not the secondary `convergence` verdict. The convergence verdict is a downstream-of-other-verdicts summary, not an artifact verdict that can contradict findings (per codebase-analysis blast-radius note on the two-verdict payload).
4. `execute-phase-quality-reviewer` — T7-transition output (`phase-quality-report.json`).
5. `execute-task-quality-handler` — **strong sweep-candidate per the codebase-analysis `scope_completeness_finding`.** Per synthesis D-0002: this agent's contract today structurally allows the exact contradiction FR-1 names (APPROVED status + severity:blocker finding); excluding it would leave the execution-side per-task path open to the failure mode US-1 names.

**Excluded reviewer-shaped agents (per codebase-analysis `scope_completeness_finding`):**

| Agent | Per-agent exclusion rationale |
|---|---|
| `finalize-deliverable-packager` | Findings field is chained pass-through from a `shared-document-reviewer` invocation that already passes FR-1; re-checking at the packager is redundant. |
| `synth-critic` | Emits per-claim verdicts, not an artifact-level verdict-vs-findings contract. The verdict-findings parity check does not apply structurally. |
| `synth-framer` | No verdict-findings contract in its output shape (framing output is a structural composition, not a review). |
| `synth-synthesizer` | Emits decisions and per-question consolidation, not a reviewer-shaped verdict + findings payload. |
| `finalize-reconciler` | Downstream summary of upstream verdicts; does not itself emit a verdict-vs-findings pair that can contradict. |

Per the codebase-analysis `scope_completeness_finding`, these five exclusions complete the sweep across all agents producing review-like outputs in the orchestrator's stage graph.

### Validator contract

```python
# verdict_findings_parity.py
# Usage: python3 verdict_findings_parity.py <reviewer-output.json> <agent-name>
#
# Exit codes:
#   0 — no parity violation (verdict and findings are consistent OR verdict is non-approving)
#   1 — parity violation (approving verdict + finding(s) with severity in blocking set)
#   2 — internal error (bad input, JSON parse failure, unknown agent-name)
#
# Output (stdout, always JSON):
#   {
#     "mechanism": "verdict-findings-parity",
#     "agent": "<agent-name>",
#     "verdict": "<observed verdict string>",
#     "blocking_findings": [ ... ],          // empty unless exit 1
#     "diagnostic": "<one-line human-readable>",
#     "remediation": "<one-line hint>"
#   }
```

**Per-agent verdict mapping** (the validator's lookup table; one row per reviewer-shaped agent). Approving values are the values that, if paired with a finding in the blocking set, constitute a parity violation:

| Agent | Verdict field | Approving values | Non-approving values |
|---|---|---|---|
| `shared-document-reviewer` | `verdict` (per doc_type) | `pass`, `conditional_pass` | `fail` |
| `review-architecture-auditor` | `verdict` | `pass`, `conditional_pass` | `fail` |
| `review-cross-artifact-auditor` | `verdict` (primary) | `pass`, `conditional_pass` | `fail`, `hard_capped` |
| `execute-phase-quality-reviewer` | `verdict` | `PASS` | `NEEDS_RECONCILIATION`, `BLOCKER` |
| `execute-task-quality-handler` | `status` | `APPROVED` | `NEEDS_REVISION`, `STUB_DETECTED`, `BLOCKER` |

The validator returns exit 1 if the verdict is in the approving column and any finding in the findings array has `severity` (case-insensitive) equal to `BLOCKER`.

**Comparison-discipline rule (closes the determinism contract AC-CC-1-g depends on):** Verdict lookup is **case-sensitive per-agent** — the per-agent verdict mapping table above is the authoritative source of approving values for each agent. The validator MUST match the observed verdict literal against the table's column entries byte-for-byte; e.g., `APPROVED` is approving for `execute-task-quality-handler` but a verdict `approved` from the same agent is NOT recognized as approving (and would either be treated as a non-approving / unknown verdict per AC-CC-1-c, or surface via exit 2 if the agent's verdict-field schema demands a known enum value — see `verdict_findings_parity.py` implementation hint below). Severity comparison is **case-insensitive against the blocking set** `{BLOCKER}`: tokens `BLOCKER`, `Blocker`, and `blocker` all match. This asymmetry is intentional — verdicts are enum values fixed by each agent's contract (mixing cases would mask a contract bug), while severity tokens cross agent boundaries (the auditor family emits `blocker` lowercase per `execute-task-quality-handler`'s alias; the document-reviewer family emits `BLOCKER` uppercase) and must unify under one comparison.

**Why `conditional_pass` is treated as approving.** Per the canonical severity-to-verdict mapping documented in `review-architecture-auditor.md` lines 135-137 (verified at codebase-C-0017): any BLOCKER ⇒ fail; any MAJOR (no BLOCKER) ⇒ conditional_pass; only MINOR/INFO ⇒ pass. A reviewer emitting `conditional_pass` is implicitly asserting "no BLOCKERs." If the findings list contains a BLOCKER alongside `conditional_pass`, that is exactly the parity violation FR-1 targets. The validator therefore treats `conditional_pass` as approving for parity purposes.

### Backward compatibility (NFR-9)

The validator is **shape-additive**. A reviewer output the prior pipeline accepted (e.g., `verdict: conditional_pass` with only MAJOR findings, no BLOCKERs) passes the validator. NFR-9 is satisfied by the validator's narrow blocking set: `{BLOCKER}` only.

### Orchestrator integration

Per ADR-0044, the orchestrator (`recipe-feature-pipeline/SKILL.md`) is the single dispatch nexus. The validator is invoked from the orchestrator at each reviewer-completion site. Concretely, after each `shared-document-reviewer` Task call, after the Stage 8 / Stage 11 auditor outputs land on disk, and after the T7 / T2 execution-side reviewer outputs land. The orchestrator step pattern (illustrative; final shape decided at Plan time):

```text
After reviewer-output written to disk at <path>:
  1. Run `python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py <path> <agent-name>`.
  2. If exit 0: proceed normally.
  3. If exit 1: halt the orchestrator. Surface the validator's JSON output to the user with the actionable-diagnostic format below.
  4. If exit 2: treat as a fail-closed internal error per NFR-6. Surface the validator's stderr and exit code; require user resolution before retry.
```

The orchestrator does not retry-loop on a parity violation. A parity violation is a contract bug in the reviewer's output; a re-invocation of the same reviewer on the same artifact is likely to produce the same violation. The orchestrator's existing reconciliation-cycle limit (4 cycles per ADR-0017) is not used here — this is a structural-shape rejection, not a quality finding.

### Diagnostic format (FR-6)

The validator's JSON output satisfies FR-6 by construction:

- **Mechanism name:** `verdict-findings-parity` (in the JSON `mechanism` field).
- **Offending artifact path:** the reviewer-output JSON path passed as positional arg 1, echoed in the validator's `diagnostic` field.
- **Rule or contract violated:** the per-agent verdict/severity contract, named in the `diagnostic` field as e.g. `"approving verdict 'APPROVED' on execute-task-quality-handler output paired with severity:BLOCKER finding(s); the agent's contract requires status:BLOCKER when any finding is severity:BLOCKER"`.
- **Remedial-action hint:** the `remediation` field, e.g. `"re-invoke <agent-name> against <artifact-path> and require it to emit a non-approving verdict; if the BLOCKER finding is itself spurious, the reviewer should have downgraded the severity rather than the verdict"`.

### Acceptance criteria (FR-1 + FR-6)

- **AC-CC-1-a (EARS — Event-driven):** When the orchestrator detects that any of the 5 reviewer-shaped sub-agents in scope (across the 9 distinct invocation sites: 5 `shared-document-reviewer` invocation points + Stage 8 architecture auditor + Stage 11 cross-artifact auditor + T7 phase-quality-reviewer + T2 execute-task-quality-handler) has written its verdict+findings output to disk, the system shall invoke `verdict_findings_parity.py` with the output path and the agent name before advancing to the next stage.
- **AC-CC-1-b (EARS — State-driven):** If the validator's exit code is 1 and the agent's verdict is in the approving column for that agent, and the findings array contains at least one finding with `severity` (case-insensitive) equal to `BLOCKER`, then the system shall halt orchestrator advance and surface the validator's JSON output to the user.
- **AC-CC-1-c (EARS — State-driven):** Where the agent's verdict is not in the approving column for that agent, the system shall pass the reviewer output through unchanged regardless of finding severities.
- **AC-CC-1-d (EARS — State-driven):** Where the agent's verdict is in the approving column and the findings array contains no finding with `severity` equal to `BLOCKER`, the system shall pass the reviewer output through unchanged.
- **AC-CC-1-e (EARS — Event-driven, NFR-6 fail-closed):** When the validator returns exit 2, the system shall treat the run as failed-closed, emit the validator's stderr to the user, and require user resolution before any retry.
- **AC-CC-1-f (EARS — Ubiquitous, FR-6):** The validator's JSON output shall always carry the four FR-6 fields (mechanism name, offending artifact path, rule violated, remedial-action hint).
- **AC-CC-1-g (EARS — Ubiquitous, NFR-5 determinism):** When invoked twice on the same input file with the same agent name, the validator shall produce byte-identical stdout and the same exit code.
- **AC-CC-1-h (EARS — Ubiquitous, NFR-9 backward-compat):** When the validator runs on any reviewer-shaped output that the prior pipeline accepted as conformant (any output without a BLOCKER finding in the findings array, regardless of verdict; or any non-approving verdict regardless of findings), the validator shall return exit 0.

### Concrete latency threshold (NFR-1 / D-0010)

The validator is a JSON-parse-and-scan over a typically-small payload (reviewer outputs are tens of kilobytes; the largest observed is `shared-document-reviewer`'s body which is the agent file itself, not the output).

**Threshold:** p95 ≤ 250 ms on a reviewer-output JSON ≤ 100 KB, measured on the maintainer's reference Codespace (the GitHub Actions ubuntu-latest runner-equivalent the project's other audit scripts run on). Single-run p99 ≤ 500 ms.

**Methodology:** the threshold is set against the existing project's audit-script latency floor. Reference: the OP-1 script (`audit_op1_env_block_coverage.py`) parses the same `.mcp.json`, applies a regex sweep over fewer fields, and on the reference Codespace runs in well under 100 ms. The new validator is structurally similar (JSON parse + list comprehension + small enum lookup), and the threshold is set conservatively at 2.5× the OP-1 floor. The p95 / p99 split allows for occasional GC / cold-start variance on the Actions runner.

**Why not a smaller number.** A sub-100 ms threshold would over-constrain: the validator must JSON-parse the input (cost varies with payload size), look up the agent's per-agent contract (table lookup; constant), scan the findings array for the BLOCKER severity (O(n) over findings; typically n < 50), and emit JSON to stdout. A 250 ms p95 ceiling leaves headroom for ~10 KB payloads under non-ideal runner conditions without inviting flake on the larger end.

**Why not a qualitative threshold.** D-0010 says synthesis must not invent numbers; the named designers own measurement. design-cc is the named designer for NFR-1. The 250 ms p95 reflects the OP-1 floor calibration above; it is set against an observed audit-script baseline, not invented.

### Q-CC-1 (architectural question for composer)

**Q-CC-1:** Should the FR-1 validator be elevated to a Gate-7 hard gate (per the ADR-0043 Gate-6 precedent for `auditing-mcp`), or remain an inline orchestrator-step rejection that surfaces directly to the user? Evidence: the existing reviewer pipeline's gate-history mechanism already provides "halt and surface" behavior, and elevating to a new gate would require ADR-text changes (out-of-scope for this carve-out per the no-ADR-amendment principle). Options: (a) inline orchestrator-step rejection (this design's recommendation); (b) new Gate 7 — defer to a future feature. Recommended: (a). Defer the gate-elevation choice to design-composer.

---

## FR-2 — Orchestrator dispatch self-check (D-0003)

### Decision

**Self-check location:** orchestrator-internal logic in `recipe-feature-pipeline/SKILL.md`, at the start of dispatch, before Stage 1 Intent Clarification. This closes U-2's "where the self-check lives" sub-question.

**Why orchestrator-internal.** Per synthesis D-0003: a hook adds a second failure path (hook misconfigured, hook silently skipped) and a second `scope_class` read site that the orchestrator would need to keep in sync. A new gate script adds new file surface for a configuration surface that has one value today. Orchestrator-internal logic is the lowest-cost shape that gives a single source of truth.

**`scope_class` read site:** hoisted from line 350 (inside Step 14 / Stage 13 Deliverable Packaging) to orchestrator entry. The existing late read at line 350 is **replaced**, not duplicated. The self-check at orchestrator entry produces a `scope_class` value that subsequent stages consume; the Stage 13 site reads the same value (now hoisted into a checkpoint field) rather than re-reading the intent-clarification frontmatter.

The hoist requires the orchestrator to handle the case where `scope_class` is not yet known (Intent Clarification has not run; this is a fresh run with no `intent-clarification.md` on disk). In that case the orchestrator runs Stage 1 first, then runs the self-check after Stage 1 completes and `intent-clarification.md` exists. This is the natural sequencing — `scope_class` is a Stage-1 output, so the self-check cannot precede Stage 1. The synthesis D-0003 recommendation ("hoist the read to orchestrator entry") is interpreted as "hoist the read to the earliest point at which `scope_class` is available," which is immediately after Stage 1.

> **Divergence note (D-0003 refinement):** This design materially refines synthesis D-0003's prescription. D-0003 says "hoist to orchestrator entry"; this design hoists to "the earliest point at which `scope_class` is available — immediately after Stage 1 completes." The refinement is forced by a data-dependency the synthesis did not name: `scope_class` is itself a Stage-1 output (it does not exist on disk before Intent Clarification runs), so a literal pre-Stage-1 hoist is impossible on a fresh run. The refinement preserves D-0003's intent (a single early read site that subsequent stages consume from a checkpoint field, replacing the Stage-13 late re-read) while honoring the data dependency. The Plan author and the composer should be aware this is a refinement, not a verbatim adoption. See also Q-CC-6 below.

**Citation precision (per synthesis):** codebase-C-0028 verifies line 350 as the single read site. The SKILL.md header at line 346 labels the containing step "Stage 13 (Deliverable Packaging)." The synthesis (§4) flags a cosmetic stage-label drift in the original claim text ("Stage 12"); this design cites line 350 / Stage 13, which is the on-disk truth as of commit 8988be2.

### Named fallback-configuration surface

Per synthesis D-0003: "single-agent fallback" is not currently a named, inspectable config surface. The codebase-analysis describes the dispatch-mode posture as **implicit** in the orchestrator's stage-graph (the historical `parent-driven-workaround` fallback preserved per ADR-0044 is a behavioral posture, not a serialized field in the on-disk `checkpoint.json` schema). The decision:

- **Introduce `checkpoint.execution_mode` as a first-class, documented field** on the `checkpoint.json` schema, with a canonical enum `{ specialist-dispatch, parent-driven-workaround }`. This is a **schema-surface change** (a new field), not a renaming of an existing field.
- Document `parent-driven-workaround` as the named "single-agent fallback" surface that FR-2's self-check inspects.
- The orchestrator self-check writes the field at dispatch time (one row per stage); the FR-2 predicate reads it.

**Honest framing on lowest-cost-primitive justification:** because this introduces a new schema field (not merely names an existing one), the FR-2 self-check carries a small but real schema-evolution cost on top of the orchestrator-internal logic. The lowest-cost-primitive choice (orchestrator-internal logic over a hook or new gate) is unchanged, but the design honestly notes the schema-surface change: a new field gets canonicalized in one place (the orchestrator's checkpoint emitter), one place (the FR-2 self-check predicate), and one place (its documentation in `recipe-feature-pipeline/SKILL.md`). This is a smaller surface than a new hook + new config file + new permission entry, so the lowest-cost-primitive judgment still favors orchestrator-internal logic, but the cost is not zero.

**Schema-evolution note:** existing `checkpoint.json` files written before this feature lands will lack the `execution_mode` field. The orchestrator's self-check MUST treat absence-of-field as equivalent to `specialist-dispatch` (the default behavior the project already exhibits) on resumes from pre-feature checkpoints, so resuming a paused run does not trip a false refusal. New runs always write the field at dispatch time.

**Self-check predicate:**

```text
Let scope_class = read from intent-clarification.md frontmatter (after Stage 1).
Let stages_fallback = list of stage names where checkpoint.execution_mode for that stage equals "parent-driven-workaround".

If scope_class == "FULL" and stages_fallback is non-empty:
  refuse to enter the dispatch loop;
  surface a diagnostic naming each stage in stages_fallback and the configuration value that triggered the refusal;
  exit non-zero with the FR-6 actionable-diagnostic format.

If scope_class in {"MINOR", "PATCH"} or stages_fallback is empty:
  proceed with dispatch normally.
```

For MINOR and PATCH scopes the self-check is a no-op pass-through (AC-FR-2-c). The orchestrator runs the check once per run, after Stage 1, before Stage 2.

### Diagnostic format (FR-6)

The refusal diagnostic includes:

- **Mechanism name:** `dispatch-self-check`.
- **Offending artifact path:** the checkpoint.json path and the specific stage entries that triggered.
- **Rule or contract violated:** `"FULL-scope dispatch with single-agent-fallback configuration is forbidden; stages [<list>] are configured with execution_mode='parent-driven-workaround'"`.
- **Remedial-action hint:** `"either reconfigure the named stages to execution_mode='specialist-dispatch' (per ADR-0044's flatten posture), or downgrade scope_class to MINOR or PATCH if the feature does not require per-layer fan-out"`.

### Risk: hoisting changes when `scope_class` is read

Per synthesis D-0003 (risks accepted): hoisting the `scope_class` read changes **when** the read happens. Any downstream code that implicitly assumed late reading (Stage 13) would now see an earlier read. A grep across the orchestrator skill (codebase-C-0028) confirms `scope_class` is read at exactly one site, so the hoist is safe. The hoist is a single edit: the Stage 13 line (~350) is changed to consume `scope_class` from the checkpoint field rather than re-read the intent-clarification frontmatter.

### Risk: canonicalizing `parent-driven-workaround`

Per synthesis D-0003 (risks accepted): naming `parent-driven-workaround` as a first-class config canonicalizes a historical workaround. If the workaround was intended to remain temporary, this design entrenches it. The design's position: ADR-0044's flatten decision is recent and durable; `parent-driven-workaround` is the documented fallback that ADR codifies. Naming it does not entrench it beyond what ADR-0044 already does — and the FR-2 self-check explicitly **refuses** this configuration for FULL scope, which is the strongest form of "this is the exception, not the rule."

If a future feature wants to retire `parent-driven-workaround` entirely, the rename is mechanical (the field name is in one place, the enum is in one place, the self-check predicate is in one place). The naming choice here does not block that future change.

### Acceptance criteria (FR-2 + FR-6)

- **AC-CC-2-a (EARS — Event-driven):** When the orchestrator begins dispatch after Stage 1 (Intent Clarification) completes, the system shall read `scope_class` from `working/feature/<slug>/intent-clarification.md`'s frontmatter and enumerate every stage's `checkpoint.execution_mode` value.
- **AC-CC-2-b (EARS — State-driven):** If `scope_class == "FULL"` and any stage's `execution_mode == "parent-driven-workaround"`, then the system shall refuse to enter the dispatch loop, write a diagnostic to the orchestrator's surface stream, and exit non-zero.
- **AC-CC-2-c (EARS — State-driven):** Where `scope_class` is `"MINOR"` or `"PATCH"`, the system shall permit any `execution_mode` value (including `parent-driven-workaround`) without raising a refusal.
- **AC-CC-2-d (EARS — Ubiquitous, FR-6):** The refusal diagnostic shall always carry the four FR-6 fields (mechanism name, offending artifact paths, rule violated, remedial-action hint).
- **AC-CC-2-e (EARS — Ubiquitous, NFR-5 determinism):** When the orchestrator dispatch self-check runs twice in succession against the same `intent-clarification.md` and the same `checkpoint.json`, the system shall produce the same verdict (pass or refusal) and the same diagnostic both times.
- **AC-CC-2-f (EARS — Unwanted-behavior, NFR-6 fail-closed):** If `intent-clarification.md` is missing or unparseable when the self-check needs to read it, the system shall treat the run as failed-closed and emit a diagnostic naming the missing-or-unparseable file, rather than skipping the self-check.

### Concrete latency threshold (NFR-2 / D-0010)

The dispatch self-check is a YAML-frontmatter read (≤ a few KB) plus a JSON-field enumeration (`checkpoint.json` is ≤ a few KB). No I/O beyond these two reads.

**Threshold:** p95 ≤ 100 ms on the reference Codespace; p99 ≤ 200 ms. The check runs once per orchestrator entry — about 30 sub-agent dispatches per FULL feature run, but the self-check itself runs once, not per dispatch.

**Methodology:** the threshold is set against the existing orchestrator's per-stage checkpoint write latency, which is observed at single-digit milliseconds on the reference Codespace (verified by spot-check on prior feature runs' state-transitions logs). A 100 ms p95 is ~20× that floor, conservatively budgeted for variance.

### Q-CC-6 (architectural question for composer)

**Q-CC-6:** Synthesis D-0003 prescribes "hoist `scope_class` read to orchestrator entry." This design refines that to "hoist to the earliest point at which `scope_class` is available — immediately after Stage 1 completes" (the data-dependency forces this; `scope_class` is itself a Stage-1 output, so a literal pre-Stage-1 hoist is impossible on a fresh run). Should the composer accept this refinement as the operative design (recommended), re-arbitrate by amending D-0003's wording to match the data-dependency, or surface a different placement (e.g., a sentinel `scope_class` value pre-Stage-1 that the self-check tolerates)? Recommended: (a) accept the post-Stage-1 refinement. Defer to design-composer.

---

## FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule (D-0004, D-0005)

### Decision

**Comparison algorithm (D-0004):** canonicalize whitespace on both sides; leave `${VAR}` placeholders as opaque tokens that must match literally; compare with string equality after canonicalization. This closes U-3.

**Why this algorithm.** Per synthesis D-0004: simplest, reproducible across environments (Codespaces, local, Actions runner all produce the same verdict for identical files), doesn't depend on env state (so test fixtures are stable), and catches the parity drift FR-3 actually targets (rows present/absent, command verbs/flags). Resolve-then-compare was rejected because expanding `${VAR}` against the running environment would couple the audit's correctness to where it runs (a known false-positive shape per NFR-10). Exact-string match without normalization was rejected because incidental whitespace and trailing newlines would generate false positives that overwhelm signal.

**Canonicalization rules** (the OP-11 rule applies these in order to both the live `.mcp.json` form and the ADR-0041 prescribed form before equality check):

1. Strip leading and trailing whitespace from each token.
2. Collapse any run of whitespace inside a token to a single space.
3. Normalize quote style: convert smart quotes (`"`, `'`, `'`, `'`) to ASCII straight quotes if present in either source. (ADR-0041's table is markdown; rare but possible.)
4. Preserve `${VAR}` placeholders as opaque tokens. Two forms match if and only if their `${VAR}` literals are byte-identical (same variable name).
5. Compare the resulting canonicalized strings with `==`.

**No env-var resolution.** The OP-11 rule does **not** read environment variables. This honors NFR-7 / NFR-8 (no credential surface, no credentials in diagnostics) by construction: the audit literally cannot leak a value it never reads.

### Deprecated-row handling (D-0005)

**Decision:** add an in-rule deprecation-marker convention to ADR-0041's invocation table. Rows tagged `[DEPRECATED]` (the chosen marker token) are treated by the OP-11 rule as expected-absent from `.mcp.json`. The marker is a new column or status token on the row; the row's text (its invocation form prescription) is preserved verbatim.

**Why in-rule, not script-side allowlist.** Per synthesis D-0005: inferior locality-of-truth. A deprecation marker in the audit script would live next to the implementation, not next to the row it annotates. A future reader of ADR-0041 sees the row and has no signal that the audit treats it specially. The in-rule marker is self-documenting at the source.

**Why in-rule, not ADR amendment.** Per synthesis: amending ADR-0041 to drop the row is excluded by the carve-out (no ADR-text edits). The marker convention is an annotation pattern — a new token on an existing row — not a decision-text rewrite. This is the synthesis's explicit interpretation and it aligns with the project's append-only ADR posture (ADR-0005).

**ADR-0041 annotation: is this a decision-text edit?** The carve-out forbids "ADR-text mutations." Adding `[DEPRECATED]` to row 71 of the invocation table is:

- An annotation pattern (a new token on a row), not a decision rewrite.
- Aligned with the existing append-only ADR posture (the row's invocation form is preserved; only a status marker is added).
- Consistent with CLAUDE.md line 9's existing framing: "stale-doc issue, not an active server." The marker formalizes a posture the project already holds.

The marker token is `[DEPRECATED]` with optional sub-token `removed:YYYY-MM-DD` for traceability. The exact form of the column (a new `Status` column appended to the existing markdown table, or an inline `[DEPRECATED]` prepended to the Server column's value) is a Plan-time detail; the design's commitment is the marker convention itself, not the rendering choice. Recommended rendering: append an inline `[DEPRECATED — removed 2026-05-24]` token at the end of the Server cell for row 71. This is the smallest visible change and preserves the row's primary key (the server name) for any prior reader cross-reference.

**Calibration note (per synthesis):** the supporting evidence for the project's "established pattern" of tolerating stale design-time docs (codebase-C-0111) is single-sourced from N=1 (mcp-openapi-schema itself). The immediate D-0005 decision still holds because the immediate case IS that observation, but this design does not over-generalize the posture into "any future stale doc gets a marker." Each future stale row is a separate design call.

### Rule contract

```python
# audit_op11_adr_parity.py
# Usage: python3 audit_op11_adr_parity.py <path-to-.mcp.json>
#   (the ADR-0041 path is resolved relative to repo root: adrs/ADR-0041-install-mechanism-hybrid.md)
#
# Exit codes (uniform with OP-1..OP-10):
#   0 — no findings
#   1 — at least one BLOCKER finding
#   2 — internal error
#
# Output (stdout, JSON):
#   {
#     "rule": "OP-11",
#     "name": "adr-parity",
#     "target": "<absolute path to .mcp.json>",
#     "findings": [
#       {
#         "rule": "OP-11",
#         "severity": "BLOCKER",
#         "server": "<name>",
#         "field": "<argv|env|sentinel|missing-in-mcp.json|missing-in-adr-0041>",
#         "prescribed_form": "<canonicalized ADR-0041 string, or null if missing>",
#         "live_form": "<canonicalized .mcp.json string, or null if missing>",
#         "diff_dimension": "<argv|env-var-indirection|sentinel-path|presence>",
#         "message": "<one-line human-readable>",
#         "remediation": "<one-line hint>"
#       }
#     ],
#     "servers_checked": [<list of server names from .mcp.json>],
#     "adr_servers_recognized": [<list of server names from ADR-0041 table>],
#     "deprecated_rows_skipped": [<list of server names tagged [DEPRECATED]>]
#   }
```

**Findings emitted** (the rule produces at most one finding per server name, on the union of `.mcp.json` keys and ADR-0041 non-deprecated rows):

| Case | Severity | Finding `field` | Notes |
|---|---|---|---|
| Server in `.mcp.json`, present in ADR-0041 (not deprecated), forms match | (none) | — | passes silently |
| Server in `.mcp.json`, present in ADR-0041 (not deprecated), forms differ | BLOCKER | `argv` or `env` or `sentinel` (whichever dimension differs first) | emit `prescribed_form` and `live_form` and `diff_dimension` |
| Server in `.mcp.json`, absent from ADR-0041 | BLOCKER | `missing-in-adr-0041` | satisfies AC-FR-3-c |
| Server in ADR-0041 (not deprecated), absent from `.mcp.json` | BLOCKER | `missing-in-mcp.json` | satisfies AC-FR-3-c |
| Server in ADR-0041 tagged `[DEPRECATED]`, absent from `.mcp.json` | (none) | — | the marker convention's reason for existing |
| Server in ADR-0041 tagged `[DEPRECATED]`, present in `.mcp.json` | BLOCKER | `deprecated-row-still-present` | a server reappeared after being marked deprecated; surface as drift |

### Diagnostic format (FR-6)

Each finding carries the four FR-6 fields:

- **Mechanism name:** `OP-11` / `adr-parity` (in the JSON `rule` and `name` fields).
- **Offending artifact path:** the `target` field at the top-level (always `.mcp.json` path); the affected `server` and `field` per finding.
- **Rule or contract violated:** the `diff_dimension` and `message` fields, e.g. `"server 'gitnexus': .mcp.json args [-y gitnexus@${GITNEXUS_TAG} mcp] differs from ADR-0041 prescription [-y \"gitnexus@${GITNEXUS_TAG}\" mcp] on argv quote-style"`.
- **Remedial-action hint:** the `remediation` field, e.g. `"align .mcp.json to the ADR-0041 prescribed form, or open a follow-up to amend ADR-0041 if the live form is the intended new prescription"`.

### Risks accepted

Per synthesis D-0004:

- ADR-0041 is currently at v1.0.1. If its table format changes (column order, separator, marker convention), the canonicalizer needs maintenance. The OP-11 rule's `references/adr-parity.md` documents the expected table shape; a follow-up ADR amendment that changes the table is a known refactor-watch item.
- The canonicalizer is intentionally narrow. It does not normalize argv ordering, does not resolve env vars, does not understand semantic equivalence of differently-named env vars (e.g., `${GITNEXUS_TAG}` vs `${GITNEXUS_VERSION}` resolving to the same value). The narrow scope is the chosen trade-off; a wider canonicalizer would be either brittle (env-resolution) or overreach (semantic-equivalence is the broader audit dimension the carve-out defers).

Per FR-3 risk row in the PRD: if false positives are observed on real `.mcp.json` shapes ADR-0041 didn't anticipate, the rule can be widened in a patch follow-up. The kill criterion in the PRD Rollout Plan covers this.

### Acceptance criteria (FR-3 + FR-6 + NFR-10)

- **AC-CC-3-a (EARS — Event-driven):** When `audit_op11_adr_parity.py` is invoked against `.mcp.json`, the system shall iterate every server entry and, for each entry, locate the corresponding non-deprecated row in ADR-0041's invocation table.
- **AC-CC-3-b (EARS — State-driven):** If the canonicalized live form does not equal the canonicalized prescribed form, then the system shall emit a BLOCKER finding naming the server, the `prescribed_form`, the `live_form`, and the `diff_dimension`.
- **AC-CC-3-c (EARS — State-driven):** If ADR-0041 contains no non-deprecated row for a server present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-adr-0041`.
- **AC-CC-3-d (EARS — State-driven):** If ADR-0041 contains a non-deprecated row whose server name is absent from `.mcp.json`, then the system shall emit a BLOCKER finding with `field: missing-in-mcp.json`.
- **AC-CC-3-e (EARS — State-driven):** Where ADR-0041 contains a row tagged `[DEPRECATED]` and the server is absent from `.mcp.json`, the system shall NOT emit a finding for that row.
- **AC-CC-3-f (EARS — Unwanted-behavior):** If ADR-0041 contains a row tagged `[DEPRECATED]` and the server is present in `.mcp.json`, then the system shall emit a BLOCKER finding with `field: deprecated-row-still-present`.
- **AC-CC-3-g (EARS — Ubiquitous, NFR-10 backward-compat):** When OP-11 runs on a `.mcp.json` entry whose canonicalized invocation form equals the canonicalized ADR-0041 prescription, the system shall produce no finding for that entry.
- **AC-CC-3-h (EARS — Ubiquitous, FR-6):** Each finding shall always carry the four FR-6 fields (mechanism name, offending server / file, rule violated, remedial-action hint).
- **AC-CC-3-i (EARS — Ubiquitous, NFR-5 determinism):** When OP-11 runs twice on the same `.mcp.json` and the same ADR-0041, the system shall produce byte-identical stdout and the same exit code.
- **AC-CC-3-j (EARS — Ubiquitous, NFR-7 / NFR-8 no-credentials):** The OP-11 rule shall not read any environment variable; the `${VAR}` placeholders shall be treated as opaque tokens both in canonicalization and in diagnostic output.
- **AC-CC-3-k (EARS — Unwanted-behavior, NFR-6 fail-closed):** If ADR-0041 cannot be parsed (file missing or table not extractable), or `.mcp.json` cannot be parsed (file missing or invalid JSON), then the system shall return exit 2 with a diagnostic naming the parse failure.
- **AC-CC-3-l (EARS — Ubiquitous, NFR-13 event surface):** When OP-11 runs, the system shall not write to `.claude/runtime/mcp-events.jsonl` (the audit-script family does not emit MCP events; this is consistent with OP-1..OP-10).

### Concrete latency threshold (NFR-2 specifically for the parity rule)

Per the PRD's "MCP audit rule overhead (sub-second per server entry) is in scope but not separately gated — it inherits the existing MCP audit skill's performance posture." NFR-2 as the PRD writes it covers the dispatch self-check; the OP-11 rule's latency is set against the existing OP-1..OP-10 floor.

**Threshold:** p95 ≤ 300 ms total for OP-11 against the current 6-server `.mcp.json` and the 6-row (non-deprecated) ADR-0041 table on the reference Codespace. Per-server cost is sub-100 ms in steady state.

**Methodology:** the threshold is set against the OP-1 / OP-9 / OP-10 baseline (each runs in well under 100 ms total on the same fixture). OP-11 reads two files (rather than OP-1's one) and runs a string canonicalization + equality check (rather than a regex sweep), so the 3× cost ceiling is the conservative budget.

### Q-CC-2 (architectural question for composer)

**Q-CC-2:** Should the `[DEPRECATED]` marker convention in ADR-0041 be lifted into a project-wide convention for ADR taxonomy tables generally, or remain scoped to ADR-0041's invocation table? Evidence: the carve-out forbids generalizing the posture beyond N=1 (per the synthesis calibration note on codebase-C-0111). Options: (a) scope the marker to ADR-0041 only, with the convention documented in `auditing-mcp/references/adr-parity.md` (this design's recommendation); (b) lift to a project-wide ADR-row-status convention — defer to a future feature. Recommended: (a). Defer to design-composer.

### Q-CC-3 (architectural question for composer)

**Q-CC-3:** The OP-11 rule is the first OP rule that consumes a markdown ADR (rather than `.mcp.json` alone). Should the project add a shared ADR-table-parser utility under `auditing-shared/scripts/` for future OP rules that compare ADRs against live artifacts, or should OP-11 inline its own parser? Evidence: the Won't-Have list includes "design-realization audit dimension" which is the broader form; that dimension would consume many ADRs. Options: (a) inline parser in OP-11 (smaller surface, lower cost today); (b) shared parser under `auditing-shared/` (better extension story for the deferred broader dimension). Recommended: (a) for this carve-out; the shared utility lands when the broader dimension lands. Defer to design-composer.

---

## FR-7 — Deferral-register tightening

### Decision

The codebase-analysis confirms that rows B-1 and H-4 already carry the canonical adoption parenthetical inline (lines 56 and 141 of `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`):

> *(ADOPTED 2026-05-25 by pipeline-quickwins-hardening-r1 — see Issues/cross-artifact-divergence-detection-gap/proposal.md)*

FR-7's substantive work is **confirmation, not authoring**. This design specifies the exact verification checklist for the Plan author and the deliverable-archive packager:

1. **Date check.** The parenthetical's date is `2026-05-25` (the adoption date). Today's date for this design pass is `2026-05-26`. The date in the marker is the **adoption** date (when the feature was committed to via the seed-proposal status promotion), not the ship date — so it stays as `2026-05-25` regardless of when the feature actually ships.
2. **Slug check.** The slug is `pipeline-quickwins-hardening-r1` — matches this feature's slug exactly. No tightening needed.
3. **Link check.** The link is `Issues/cross-artifact-divergence-detection-gap/proposal.md` — matches the seed-proposal path. No tightening needed.
4. **Cell-coverage check.** Per the row-update convention documented in codebase-analysis-report `conventions.documents.deferral_register_row_update`:
   - Why-excluded cell → "Now adopted: <summary>"
   - Re-examination-trigger cell → "Adopted by <slug>."
   - Forgetting-risk cell → "Resolved by adoption."
   The Plan author verifies these three cells are updated on both rows B-1 and H-4. If any cell is not yet updated, the Plan author updates it.

The TL;DR and counts at the top of the register are **not** incrementally updated row-by-row (the register is a snapshot doc, not a live ledger — per the documented convention).

### Placement of the FR-7 edit (D-0009)

Per synthesis D-0009: include in the deliverable archive commit. **Defer the final commit-shape decision to design-composer** as a cross-layer item.

The design's recommendation: the FR-7 edit lands as part of the deliverable archive commit, alongside the FR-1 / FR-2 / FR-3 / FR-4 / FR-5 mechanism commits. The register marker tightening IS part of the feature's quality-gates deliverable — separating it loses the audit trail; a future reader looking at the archive sees the feature's full scope in one commit.

The synthesis flags D-0009 as a "no verified-claim driver" pure-process judgment. This design accepts that and forwards to composer with the recommendation but without claiming verified-evidence backing.

### Acceptance criteria (FR-7)

> **Placement note (D-0009 deferral):** The exact placement of the FR-7 verification step — at the deliverable-archive step (this design's recommendation, per synthesis D-0009) vs at a separate housekeeping commit — is forwarded to design-composer (see Q-CC-5). The ACs below are written to operate at **whichever placement composer selects**: the EARS trigger phrase "when the feature reaches the [verification step]" is intentionally placement-agnostic. If composer selects deliverable-archive placement, "the verification step" is the deliverable-archive step. If composer selects a separate housekeeping commit, "the verification step" is that commit's verification gate. The substantive ACs (b, c, d) are identical in both placements.

- **AC-CC-7-a (EARS — Event-driven, deliverable-archive placement — recommended):** When the feature reaches the deliverable-archive step, the system shall verify that `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` row B-1 carries the exact parenthetical `*(ADOPTED 2026-05-25 by pipeline-quickwins-hardening-r1 — see Issues/cross-artifact-divergence-detection-gap/proposal.md)*` in the Item cell.
- **AC-CC-7-a-alt (EARS — Event-driven, separate-housekeeping-commit placement — composer fallback):** When the feature reaches the housekeeping-commit verification gate, the system shall verify row B-1 carries the same parenthetical specified in AC-CC-7-a. (Composer activates this AC instead of AC-CC-7-a if it selects the separate-housekeeping-commit placement.)
- **AC-CC-7-b (EARS — Event-driven):** When the feature reaches the verification step (deliverable-archive or separate housekeeping commit, per composer's D-0009 placement), the system shall verify that row H-4 carries the same parenthetical (with the same date / slug / link tokens).
- **AC-CC-7-c (EARS — State-driven):** If either row's parenthetical is missing or differs from the canonical form, the system shall update the row to match. (Placement-agnostic: applies wherever composer places the verification step.)
- **AC-CC-7-d (EARS — State-driven):** If either row's Why-excluded / Re-examination-trigger / Forgetting-risk cells do not carry the canonical post-adoption text ("Now adopted: ...", "Adopted by <slug>.", "Resolved by adoption."), the system shall update those cells. (Placement-agnostic.)

---

## FR-6 — Actionable diagnostics (Claude-Code-owned portion)

FR-6 is cross-cutting; each per-layer designer owns the diagnostic shape for their layer's mechanisms. The Claude-Code-owned portion covers FR-1, FR-2, FR-3:

| Mechanism | Mechanism name string | Offending artifact source | Rule string source | Remediation hint source |
|---|---|---|---|---|
| FR-1 verdict-parity validator | `verdict-findings-parity` | reviewer-output JSON path passed as positional arg | per-agent verdict/severity contract table | per-agent canonical re-invocation hint |
| FR-2 dispatch self-check | `dispatch-self-check` | `checkpoint.json` path + stage names | FR-2 named-fallback predicate | the two canonical remediations (reconfigure to specialist-dispatch; or downgrade scope_class) |
| FR-3 OP-11 audit | `OP-11` / `adr-parity` | `.mcp.json` path + per-finding server name | per-finding `diff_dimension` and `message` | per-case canonical remediation hint (align to ADR; or open ADR-amendment follow-up) |

The composer should audit (per the synthesis §6 closing paragraph) that the cross-cutting diagnostic language is consistent enough across all five mechanisms that FR-6 is a single audit check at integration time. The Claude-Code-side commitment: all three of the above emit JSON output (not free prose) and all three carry the four FR-6 fields in named keys.

---

## Dependencies on other layers

- **Codespaces (`design-codespaces`):** none in the cross-layer-needs sense — FR-4 lives entirely in `.devcontainer/`. However, FR-4's diagnostic format (via `log-mcp-event.sh`) is the project's existing precedent for "JSONL via log_mcp_event helper plus single-line plain-text echo for operator legibility." The Claude-Code-owned mechanisms (FR-1, FR-2, FR-3) emit JSON directly to stdout; they do not write to `.claude/runtime/mcp-events.jsonl`. NFR-13 is satisfied by construction: the audit-script family does not emit MCP events, only diagnostic JSON consumed by the orchestrator and the gate machinery.

- **CI/CD (`design-cicd`):** the FR-5 CI workflow (`design-cicd`'s sole mechanism) reads `.mcp.json` to perform the `claude mcp list` (or the recommended `claude --bare -p ... | jq` SDK-event path per synthesis D-0007) connectivity smoke. The CC layer's contribution to that flow is the existence of the OP-11 rule, which the CI workflow MAY ALSO run as part of its job (cheap, deterministic, in the same step) — but that is `design-cicd`'s call, not this design's. The CC layer commits to: OP-11 is invocable from any context that can run `python3` against `.mcp.json` (no extra setup beyond what the existing OP-1..OP-10 scripts require). The CI workflow can wire it in if `design-cicd` wants the parity check at PR time as well as at Gate 6.

- **MCP servers:** unchanged. NFR-15 satisfied by construction.

- **Other layers (Frontend / Backend / API / Query / Database / IaC):** N/A — out of scope per the PRD's Layer Scope.

---

## Architectural Questions for Composer (consolidated)

- **Q-CC-1:** Should the FR-1 validator be elevated to a Gate-7 hard gate (per the ADR-0043 Gate-6 precedent for `auditing-mcp`), or remain an inline orchestrator-step rejection that surfaces directly to the user? Recommended: inline rejection (this design). Defer the gate-elevation choice to a future feature.

- **Q-CC-2:** Should the `[DEPRECATED]` marker convention in ADR-0041 be lifted into a project-wide convention for ADR taxonomy tables generally, or remain scoped to ADR-0041's invocation table? Recommended: scope to ADR-0041 only for this carve-out. Lift in a future feature if other ADR tables develop the same shape.

- **Q-CC-3:** Should the project add a shared ADR-table-parser utility under `auditing-shared/scripts/` for future OP rules that compare ADRs against live artifacts, or should OP-11 inline its own parser? Recommended: inline for this carve-out. Lift to shared when the broader design-realization audit dimension lands.

- **Q-CC-4 (cross-layer with design-composer):** D-0008 PR shape (single bundled vs sequenced) is a workflow decision the synthesis flagged for user confirmation. The CC layer's mechanisms (FR-1, FR-2, FR-3, FR-7) all touch `recipe-feature-pipeline/SKILL.md` or its adjacent skills, so they are tightly coupled at the implementation surface — single-bundled-PR is the lower-overhead shape from the CC layer's perspective. Defer to design-composer with this layer's preference as a single-PR recommendation.

- **Q-CC-5 (cross-layer with design-composer):** D-0009 deferral-register placement (deliverable-archive commit vs separate housekeeping commit). The CC layer's FR-7 edit is a verification-and-tightening of an existing adoption marker (not a fresh authoring), so the marginal commit-shape decision is small. Recommended: deliverable-archive commit (per synthesis D-0009). Defer to design-composer.

- **Q-CC-6 (refinement of synthesis D-0003):** This design refines D-0003's "hoist `scope_class` read to orchestrator entry" prescription to "hoist to the earliest point at which `scope_class` is available — immediately after Stage 1 completes," because `scope_class` is itself a Stage-1 output (a literal pre-Stage-1 hoist is impossible on a fresh run). Recommended: composer accepts the post-Stage-1 refinement and treats it as the operative D-0003 reading. Alternative: composer amends D-0003's wording to match. Defer to design-composer.

---

## Open items

- **OI-CC-1:** The `recipe-feature-pipeline` SKILL.md edits for FR-1 invocation site insertion (9 distinct invocation sites across the 5 reviewer-shaped agents in scope per D-0002: 5 `shared-document-reviewer` invocation points per ADR-0017, plus the Stage 8 architecture-auditor site, plus the Stage 11 cross-artifact-auditor site, plus the T7 phase-quality-reviewer site, plus the T2 execute-task-quality-handler site) are mechanical but voluminous (~10 small edits across the 629-line SKILL.md). The Plan author owns the exact diff. This design specifies the **intent** (one invocation per reviewer-completion site, run the validator, halt on exit 1) rather than the exact line-edits.

- **OI-CC-2:** The OP-11 script (`audit_op11_adr_parity.py`) has a known dependency on ADR-0041's table format remaining stable. The synthesis (§4 last bullet, D-0004 risks accepted) flags this as a known refactor-watch item. The Plan author should include a small fixture-driven smoke test for OP-11 against a snapshot of ADR-0041 v1.0.1's table, so that a future ADR table-format change is caught at audit time rather than at production-incident time. The design recommends: a tiny test fixture under `.claude/skills/auditing-mcp/tests/op11_smoke/` (one ADR-0041 snapshot + one `.mcp.json` snapshot + expected JSON output). This open item is forwarded to the Plan author.

- **OI-CC-3:** The `parent-driven-workaround` execution_mode enum value is being canonicalized by this design (per D-0003) but its origin is ADR-0044's flatten decision. The composer should confirm that no other ADR contradicts this naming (a quick CoVe-style check during architecture audit).

- **OI-CC-4:** The Stage-12-vs-Stage-13 cosmetic drift in the existing SKILL.md (line 346 header says "Stage 13 (Deliverable Packaging)", while the synthesis claim text said "Stage 12") is acknowledged but not fixed by this design. The synthesis explicitly excludes cosmetic ADR / SKILL.md cleanup from the carve-out. The composer should track this as a future housekeeping item.

- **OI-CC-5:** The `recipe-feature-pipeline` SKILL.md's "shared-document-reviewer Invocation Points" table (lines 79-89) lists 5 ADR-0017 invocation points. After FR-1 lands, the table should be augmented with a sixth column (or footnote) noting that the verdict-parity validator runs after each invocation. The Plan author owns the exact placement.
