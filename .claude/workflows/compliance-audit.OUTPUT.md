# Compliance-audit — codebase vs architecture (RUN OUTPUT, for review)

> 2026-05-30 (wf_03e83b0f-413; 101 agents, ~4.6M tokens). Each finding verified with file:line. Report-only — PROPOSES refactor tasks; the human folds them into the plan.

I have everything I need. The findings are pre-verified with file:line and refactors. Producing the report.

---

# Architecture-Compliance Non-Compliance Summary

## BLOCKER

**Domain registry omits the auditor bill-of-materials** (rule D-DOM-1-2)
- `.claude/canonical/engineering-domain-layers.yaml:52-116` — every layer declares a `design_agent` but no `auditor` field at all.
- Refactor: add an `auditor` field to each layer; name the auditor or declare `auditor: none` with a one-line rationale, so a completeness check does not false-flag intentional gaps.

## MAJOR — grouped by theme

**1. Validator runtime not reproducible from the committed build (rule TB8)**
- `.claude/skills/auditing-shared/scripts/canonical.py:47,77` — unguarded `import yaml`; PyYAML is third-party.
- `.devcontainer/Dockerfile:9-19` — installs apt tools + uv but no Python packages; a clean rebuild crashes the two hard-importing validators (`canonical.py`, `validate_adr_prescriptions.py`).
- Refactor: add a committed, pinned `requirements.txt` (`PyYAML==6.0.3`) and a `COPY` + `pip install --no-cache-dir -r requirements.txt` step in the Dockerfile. One source of truth for both. (Verifier note: `frontmatter.py` already has a fallback and is not affected.)

**2. Fitness-function layer asserted but never built (rule TB1/TB8 family)**
- `.claude/canonical/technology-boundaries.yaml` — eight non-null `fitness_function` names that resolve to nothing in the repo: TB1 (l.80), TB2 (l.92), TB3 (l.104), TB5 (l.128), TB8 (l.164), TB9 (l.176), TB10 (l.188), TB11 (l.200). The file's own line-16 invariant ("every non-null fitness_function names a check that exists") is violated.
- Refactor: implement each `ff_tb*` check in a single technology-boundaries CI workflow, OR set the unbuilt ones to `fitness_function: null` with an inline rationale, exactly as TB4/TB6/TB7 already do.

**3. Orchestration state passed via agent memory instead of file path (rule TB6)**
- `.claude/agents/execute-finalize-reconciler.md:24` and `:78` — sources/increments the per-phase cycle counter via `memory: project` shared with the orchestrator; this is the sticky-session pattern TB6 eliminates, and it misuses the persistent-learnings memory primitive (counter leakage across feature runs).
- Refactor: add a `checkpoint_path` input; Read the counter from `checkpoint.execution_pipeline_cycle_counters.per_phase[<phase_n>]`. The reconciler reports its cycle outcome in `quality-reconciliation-log.json`; the orchestrator persists the counter. Remove the `memory: project`-as-run-state framing at both lines.

**4. Independence parity gate is inert (wrong path) (rule R4)**
- `.claude/skills/recipe-feature-pipeline/SKILL.md:497` — passes `phase-quality-result.json`, but the reviewer emits `phase-quality-report.json`. The validator returns exit 2 (file-not-found) every run, which the orchestrator treats as a transient error. The self-approval gate never actually fires for phase-quality verdicts.
- Refactor: pass the emitted filename (`phase-quality-report.json`, or the per-phase `phase-quality-report-<phase_id>.json` variant).

**5. Reviewer gate is ordinal, with no abstain path (rule D-RG-1-R20)**
- `.claude/agents/review-cross-artifact-auditor.md:148,154-157` — verdict is `fail | conditional_pass | pass | hard_capped`, derived from severity counts; no per-criterion binary verdict, no rubric read, no abstain/escalate value.
- Refactor: emit per-criterion binary pass/fail read from `reviewer-rubric.yaml` with any-fail→fail / any-abstain→escalate. Must preserve the deterministic loop-back and cycle-cap semantics that `conditional_pass` currently drives.

**6. Supersession links broken / unfiled (rule D-KN-3-R18)**
- `adrs/ADR-0066-gitnexus-removal.md:7` — `supersedes: []` but `ADR-0058` claims `superseded_by: ADR-0066`; asymmetric edge. ADR-0066's body frames 0058 as "Related." Fix one side (add the back-link, or downgrade 0058 to `related:`).
- `adrs/ADR-0018-codebase-analysis-schema.md:3` — fully superseded but still in active `adrs/`; relocate to existing `adrs/superseded/` and normalize the status token.

**7. Commit-authorship rule duplicated across memory levels (rule D-KN-4)**
- `AGENTS.md:70-93` duplicates `feedback_no_overwrite_others_work.md` near-verbatim; additive precedence means no override engine resolves the clash.
- Refactor: keep the rule at one level — trim one to a pointer.

**8. Tool health probe is reachability-only, out-of-session (rule D-TOOL-1-R22)**
- `.devcontainer/postStart.sh:48-74` — uses `mcp-ping.sh` (tools/list reachability) at container lifecycle; a project-less serena records "ok" (false PASS).
- Refactor: keep the postStart sweep; add an in-session SessionStart probe that runs `activate_project` then verifies a project-scoped call.

## MINOR

- **ADR status casing not normalized** (rule D-KN-3-R18) — `adrs/ADR-0018-...md:3`: 45 `Accepted` / 14 lowercase `accepted` / one `Superseded` / one free-text `Superseded by ADR-0038`. Pick one canonical enum; move the target into `superseded_by` only.

---

# Proposed Refactor Tasks

| # | Title | Files | Rule satisfied | Size |
|---|---|---|---|---|
| T1 | Add `auditor` field (named or `none`+rationale) to every domain layer | `.claude/canonical/engineering-domain-layers.yaml` | D-DOM-1-2 | M |
| T2 | Commit pinned `requirements.txt` + install PyYAML in Dockerfile build | `.devcontainer/Dockerfile`, new `requirements.txt`; verify `canonical.py`, `validate_adr_prescriptions.py` | TB8 | S |
| T3 | Resolve fitness-function layer: implement `ff_tb*` checks in one CI workflow, or null-out unbuilt ones with rationale | `.claude/canonical/technology-boundaries.yaml`, new `.github/workflows/` (if implementing) | TB1/TB8 family | L |
| T4 | Make finalize-reconciler stateless: read/report cycle counter via checkpoint file, drop `memory:project` run-state | `.claude/agents/execute-finalize-reconciler.md` (l.24, 78) | TB6 | M |
| T5 | Fix phase-quality parity path so the independence gate actually runs | `.claude/skills/recipe-feature-pipeline/SKILL.md:497` | R4 | S |
| T6 | Convert cross-artifact verdict to per-criterion binary + abstain, preserving loop-back semantics | `.claude/agents/review-cross-artifact-auditor.md`, `reviewer-rubric.yaml` | D-RG-1-R20 | L |
| T7 | Repair supersession links: ADR-0066↔ADR-0058 symmetry; relocate ADR-0018 to `adrs/superseded/` | `adrs/ADR-0066-...md`, `adrs/ADR-0058-...md`, `adrs/ADR-0018-...md` | D-KN-3-R18 | M |
| T8 | De-duplicate commit-authorship rule to a single memory level | `AGENTS.md`, `feedback_no_overwrite_others_work.md` | D-KN-4 | S |
| T9 | Add in-session SessionStart serena health probe (init + project-scoped verify) | `.devcontainer/postStart.sh`, `.claude/settings.json`, SessionStart hook | D-TOOL-1-R22 | M |
| T10 | Normalize ADR status enum casing across the ADR set | all `adrs/*.md` with status frontmatter | D-KN-3-R18 | S |

Sequencing note: T2 unblocks any future CI in T3 (validators need a reproducible runtime first). T6 is the highest-risk change because the ordinal `conditional_pass` value drives the 4-cycle reconciliation loop — the binary rewrite must keep that machinery intact.

---

**Completeness note.** This pass audited the canonical YAML files, the named sub-agents, the orchestrator SKILL, the devcontainer build/lifecycle scripts, and the ADR frontmatter cited in the findings. It did not reach: (a) the *behavioral correctness* of the validator scripts beyond import-reproducibility — whether `verdict_findings_parity.py`, `run_phase_checks.py`, and the canonical accessors produce correct verdicts was not exercised; (b) the *other* reviewer gates (`shared-document-reviewer`, `review-architecture-auditor`) for the same ordinal/abstain defect found in the cross-artifact auditor — only the cited file was checked, so R20 conformance across all three gates needs a human sweep; (c) the full ADR set for supersession-link symmetry beyond ADR-0018/0058/0066 — a repo-wide cross-link-integrity check is the proper tool and does not yet exist; (d) whether the eight unbuilt fitness functions are individually *mechanizable* (some TBs may genuinely warrant `null`+judgment rather than a CI check) — that is a design call a human should make per-boundary. A human should also confirm the architecture spec's target-vs-shipped status, since several findings are non-compliance with an agreed-but-unimplemented design rather than a shipped contract.