---
id: PHASE-VALIDATORS-audit-findings-remediation-r1
version: 1.1.0
supersedes: phase-validators.md (v1.0.0)
status: approved
feature_slug: audit-findings-remediation-r1
derived_from:
  - working/feature/audit-findings-remediation-r1/plan-v1.2.0.md (v1.2.0)
  - working/feature/audit-findings-remediation-r1/blueprint-v1.1.0.md (v1.1.0)
  - working/feature/audit-findings-remediation-r1/prd-v1.md (v1.2.0)
  - working/feature/audit-findings-remediation-r1/cc-dependencies.json
  - working/feature/audit-findings-remediation-r1/cross-artifact-audit-issues-r2.json
  - working/feature/audit-findings-remediation-r1/reconciliation-log-cycle2.md
cross_references:
  - working/feature/audit-findings-remediation-r1/acceptance-tests-v1.1.0.md (v1.1.0)
generated: 2026-05-21T21:16:00Z
generated_by: claude (acting as test-phase-validator-author re-invoked by finalize-reconciler cycle 2, continuation session)
authored_in_parallel_with: acceptance-tests-v1.1.0.md
supersession_addresses:
  - I-CA-004 (MAJOR — stage-number discipline violations, phase-validators portion: 3 instances at PV-6.C6, PV-6.C8, line 266)
---

# Phase Validators — Audit Findings Remediation (r1)

## Contents

- Posture
- PV-0 through PV-6 (per-phase validator entries)
- Cross-validator dependency graph
- Critical-path validators
- Parallelizable validator checks
- Shared validator infrastructure
- Validator runbook
- Update history

## Posture

This is a documentation + skill-tree feature (no service rollout, no flagged deploy, no monitoring period). The Phase-Validator framework's "Phase N+1 (Rollout)" stage from the agent spec is **not applicable** — feature delivery completes when the final audit converges and the deliverable archive is packaged.

Each PV-N maps 1:1 to the corresponding Phase N in the current Plan version. Validator scope is narrow because the phases are narrow: most pass-criteria are a small number of audit-output assertions plus the named acceptance tests scheduled for that phase. Severity defaults to `blocking` unless explicitly noted.

## PV-0 — Phase 0 (Setup)

**Phase reference:** Plan §Phase 0 (P0.1 baseline snapshot; P0.2 fixture workspace; P0.3 release version decision)

**Validator goal:** Confirm the baseline state is captured, the fixture workspace exists with all needed fixtures, and the release-version decision is recorded — without which downstream behavior-equivalence tests (AT-030) and fixture tests (AT-011, AT-015, AT-021, AT-031) are unverifiable.

**Pass criteria.**

- **PV-0.C1 — Baseline audit captured.** `test -s /tmp/baseline-audit.json` AND `test -s /tmp/baseline-audit.md`. Both files non-empty. *Severity: blocking. Automation hook: pre-Phase-1 manual or scripted check.*
- **PV-0.C2 — Baseline counts match PRD.** Parse `/tmp/baseline-audit.json`; assert `deductions_by_severity.BLOCKER == 77` AND `MAJOR == 42` AND `MINOR == 29`. If divergent, ADR-0029 surfacing fires BEFORE Phase 1 begins per Plan P0.1. *Severity: blocking. Source: PRD §Background; Plan P0.1 explicit precondition.*
- **PV-0.C3 — Fixture directory exists.** `test -d /tmp/audit-findings-fixtures/`. *Severity: blocking. Automation hook: shell `test`.*
- **PV-0.C4 — All required fixtures present.** Each of `agent_vague_description.md`, `agent_negated_bypass.md`, `agent_genuine_bypass.md`, `cc_config_unjustified_marker.md`, `skill_unjustified_marker.md`, `subagent_unjustified_marker.md`, `test_location_where_fallback.py` exists under the fixture dir. *Severity: blocking for the dependent ATs (AT-011, AT-015, AT-021, AT-031); warning for phase exit if some fixtures are scheduled for later authoring per Plan P2/P4.* (Plan P0.2 says fixtures are *authored in Phase 2 alongside the auditor changes* — so for PV-0 this criterion is **warning**; PV-2 promotes it to **blocking**.)
- **PV-0.C5 — Release version recorded.** Plan §P0.3 contains `**Decision:** This feature ships as **v4.6.0**`. Verified via grep. *Severity: blocking (U-3 resolution must exist before Plan can be considered complete).*

**Acceptance tests scheduled for this phase:** None directly (all ATs depend on later-phase work product). PV-0 is a precondition validator.

**Operational checks.** Working directory == repo root (per ADR-0027 precondition). No staged-but-uncommitted changes that would affect the baseline audit's reading of the repo.

**Failure response.** Any PV-0 blocking criterion failure halts Phase 1 launch. PV-0.C2 failure (baseline-count drift from PRD) triggers ADR-0029 surfacing to user: PRD was authored against a specific baseline; if drift is real, PRD may need amendment (re-run Gate 2) before remediation work begins.

**Validator metadata.** Run pre-Phase-1; expected duration < 1 minute (audit re-run for PV-0.C1/C2 takes longer, but that's the baseline run itself — already captured per Plan P0.1).

## PV-1 — Phase 1 (Foundation: mechanism-α spec + auditing-shared module)

**Phase reference:** Plan §Phase 1 (P1.1 mechanism-α spec; P1.2 forward-pointer; P1.3 auditing-shared module; P1.4 canonical pedagogical_marker_check.py)

**Validator goal:** Confirm the foundation artifacts (spec doc, shared skill module, canonical implementation) are in place AND that the dedup hasn't broken existing audit behavior (behavior-equivalence captured at the pre-FR-7 moment).

**Pass criteria.**

- **PV-1.C1 — Mechanism-α spec exists.** Satisfies AT-019. *Severity: blocking.*
- **PV-1.C2 — `auditing-shared` skill module exists.** `test -f .claude/skills/auditing-shared/SKILL.md`; SKILL.md ≤ 30 lines per OBS-2; `user-invocable: false` in frontmatter. *Severity: blocking.*
- **PV-1.C3 — Canonical `pedagogical_marker_check.py` exists in shared module.** `test -f .claude/skills/auditing-shared/scripts/pedagogical_marker_check.py`. *Severity: blocking.*
- **PV-1.C4 — Behavior-equivalence intermediate-state captured.** `/tmp/post-dedup-audit.json` exists, captured at the post-P1.4-pre-FR-7-wiring moment. *Severity: blocking — required for AT-030.*
- **PV-1.C5 — Behavior equivalence holds.** Diff `/tmp/baseline-audit.json` vs. `/tmp/post-dedup-audit.json`, filtered to types present in both. Difference MUST be empty (only acceptable delta: new `Marker without justification` type, which should not yet be wired at this checkpoint). Satisfies AT-030 partial. *Severity: blocking — non-equivalence means the dedup changed semantics, which violates AC-FR-12-c.*
- **PV-1.C6 — Forward-pointer in legacy spec.** `auditing-cc-configs/references/pedagogical-marker-spec.md` contains a top-of-file note pointing to the new justification spec. Verified via grep. *Severity: informational (helpful to future readers; doesn't gate downstream work).*

**Acceptance tests scheduled for this phase:** AT-019 (spec file presence); AT-030 partial (behavior-equivalence intermediate-state check).

**Operational checks.** P1's serial chain (P1.1 → P1.3 → P1.4) ran without backtracking; if backtracking occurred (e.g., P1.4 surfaced a flaw in P1.1's spec), supersede the spec first per ADR-0005, then re-run P1.4.

**Failure response.** PV-1.C5 (behavior equivalence) failing means the canonical implementation deviates from the prior copies' behavior in a way the dedup was supposed to preserve. Inspect the 18-28 line divergences per AC-FR-12-d; identify which one wasn't reconciled correctly; revise canonical; re-run.

**Validator metadata.** Run post-P1.4; expected duration ~2 minutes (audit re-run dominates).

## PV-2 — Phase 2 (Auditor improvements: SA-2 regex + negation-aware bypass-approval regex + X9 wire)

**Phase reference:** Plan §Phase 2 (P2.1 SA-2 regex tighten; P2.2 negation-aware bypass-approval regex; P2.3 X9 wire-recursive)

**Validator goal:** Confirm each auditor edit (a) does what it was supposed to and (b) doesn't fire on the negative-test cases. Auditor improvements are uniquely high-risk because they alter what *counts as* a finding; the negative-test fixtures are the guardrail against suppression-disguised-as-improvement (intent constraint 3).

**Pass criteria.**

- **PV-2.C1 — SA-2 regex tightened; negative fixture still fires.** AT-011 passes (genuinely-vague description still produces SA-2 finding). *Severity: blocking.*
- **PV-2.C2 — Project's actual agent descriptions no longer fire SA-2.** Run `audit_project.py .` against repo; count SA-2 findings. MUST be < baseline 29. (Final-state zero count is gated by AT-010 at PV-6, not here — PV-2 only confirms the regex tightening had effect.) *Severity: blocking.*
- **PV-2.C3 — Bypass-approval regex is negation-aware.** AT-015 passes both sub-cases (negated → zero; genuine → BLOCKER). *Severity: blocking.*
- **PV-2.C4 — X9 recursive check wired (not stub).** Inspect `auditing-cc-configs/scripts/cross_file_checks.py:check_X9_subagent_skills_security_block`. Function body MUST invoke the subprocess dispatch (per cc-design D-6 implementation note); MUST NOT be the prior placeholder. Grep for `subprocess` import or call. *Severity: blocking.*
- **PV-2.C5 — Per-pair caching present in X9.** Per Plan P2.3 implementation note: cache per (subagent, skill) pair within single audit run. Inspect for cache structure (dict, set, lru_cache, or equivalent). *Severity: warning — absence is a performance issue, not correctness.*
- **PV-2.C6 — All required fixtures now present (PV-0.C4 promoted).** Same check as PV-0.C4 but blocking at this stage since Phase 2 is where fixtures are authored per Plan P0.2's "authored in Phase 2 alongside the auditor changes". *Severity: blocking.*

**Acceptance tests scheduled for this phase:** AT-011, AT-015. AT-018 (X9 output substantively differs) is post-final-audit so is at PV-6, but PV-2 establishes the wiring that makes AT-018 verifiable.

**Operational checks.** Phase 2 is parallel-with-Phase-3 in Plan §Cross-Phase Dependencies; PV-2 and PV-3 may run independently and in either order.

**Failure response.** PV-2.C1 failure: regex tightening went too far (also rejected genuinely-vague descriptions). Loosen the pattern alternatives per D-4 per-layer Design; re-run AT-011. PV-2.C3 failure: lookbehind / two-pass implementation has a logic bug; revisit Plan P2.2. PV-2.C4 failure: P2.3 still stub; complete the wiring.

**Validator metadata.** Run post-Phase-2; expected duration ~5 minutes.

## PV-3 — Phase 3 (Real-fix dispositions: 3 agent Bash-scoping + 18 Cat C broken-link fixes)

**Phase reference:** Plan §Phase 3 (P3.1/P3.2 Bash scoping; P3.3 Cat C fixes)

**Validator goal:** Confirm the 3 named agents have scoped Bash (not bare `Bash`) and the 18 Cat C broken-link findings each have a documented disposition per AC-FR-3-b.

**Pass criteria.**

- **PV-3.C1 — All 3 agents use scoped Bash.** AT-014 passes (zero bare `Bash`; ≥ 1 scoped `Bash(<cmd>:*)` per file). *Severity: blocking.*
- **PV-3.C2 — `shared-document-reviewer` gains `PedagogicalMarkerJustification` doc_type.** Inspect `shared-document-reviewer.md`; grep for `PedagogicalMarkerJustification`. MUST appear ≥ 1 time (declaration + procedure documentation). *Severity: blocking — secondary enforcement of mechanism α per Blueprint Q-CC-2.*
- **PV-3.C3 — 18 Cat C dispositions documented.** `implementation-notes.md` contains 18 entries each tagged `REPAIR` / `DELETE` / `REAUTHOR`. Satisfies AT-009 partial. *Severity: blocking.*
- **PV-3.C4 — No marker dispositions used for Cat C.** AT-009 step 2 grep: zero NEW markers added in synthesize/ or report-composition-knowledge/ under FR-3 scope. *Severity: blocking — AC-FR-3-b explicitly forbids marker disposition for Cat C.*

**Acceptance tests scheduled for this phase:** AT-014 (Bash scoping); AT-009 partial (dispositions documented; the audit-re-run portion of AT-008 is PV-6).

**Operational checks.** P3.2 depends on PV-1.C1 (mechanism-α spec) since shared-document-reviewer's new doc_type references the spec.

**Failure response.** PV-3.C1 failure: an agent's `Bash` scoping is too narrow and breaks the agent's actual behavior. Inspect the agent's body for the actual commands invoked; widen the scope; re-run. PV-3.C4 failure: a Cat C finding was wrongly marker-disposed; revert the marker; re-execute the real-fix decision.

**Validator metadata.** Run post-Phase-3; expected duration ~3 minutes.

## PV-4 — Phase 4 (Marker upgrades + new markers)

**Phase reference:** Plan §Phase 4 (P4.1 delete/shim prior marker-check copies; P4.2 same for scan_memory_secrets.py; P4.3 9 frontmatter upgrades; P4.4 10 fence upgrades; P4.5 5 HTML-tag conversions; P4.6 32 new markers)

**Validator goal:** Confirm the dedup-driven file removals leave exactly one canonical implementation, the retroactive marker upgrades carry valid justifications, and the new markers added under FR-1/FR-2 all pass mechanism-α.

**Pass criteria.**

- **PV-4.C1 — Exactly one canonical `pedagogical_marker_check.py`.** AT-028 passes. *Severity: blocking.*
- **PV-4.C2 — All 3 dispatchers invoke canonical.** AT-029 passes. *Severity: blocking.*
- **PV-4.C3 — `scan_memory_secrets.py` similarly deduplicated.** Same pattern as PV-4.C1/C2 applied to `scan_memory_secrets.py` per Plan P4.2. *Severity: blocking (per AC-FR-12-e absorbed into Plan).*
- **PV-4.C4 — Retroactive upgrades complete.** All 9 frontmatter markers (P4.3) + all 10 fence markers (P4.4) + all 5 HTML-tag conversions (P4.5) are in canonical form. Inspect the affected file list from `cc-dependencies.json` items F-6-1/2/3. *Severity: blocking.*
- **PV-4.C5 — Intermediate audit re-run shows zero unjustified markers.** Per Plan §L1/L2/L3 Verification Discipline: Phase 4 ends with intermediate audit re-run. `python3 audit_project.py . --json > /tmp/post-phase4-audit.json`; filter `type=="Marker without justification"`; count MUST equal 0. (This is the per-phase verification gate per Plan L2.) *Severity: blocking.*
- **PV-4.C6 — Backward-compat for location/where preserved.** AT-031 passes. *Severity: blocking.*
- **PV-4.C7 — Sample-check justifications are non-boilerplate.** Pick 5 random markers from the 9 + 10 + 5 + 32 = 56 markers added/upgraded; manually verify each justification meets ADR-0030 §D-3 substance requirement. *Severity: warning — Cross-Artifact Audit (P6.3) will independently verify.*

**Acceptance tests scheduled for this phase:** AT-028, AT-029, AT-031. (AT-022 final all-markers-pass is at PV-6.)

**Operational checks.** This is the *largest* phase by effort estimate (6-10 hours per Plan §Estimation). Multiple sessions likely; resume points should be safe per file (each file is independent per Plan §Phase 4 internal parallelism note).

**Failure response.** PV-4.C5 failure: one or more markers added in this phase has an invalid justification. The audit output names the file + marker; revise the justification per ADR-0030 D-3 rules; re-run audit. PV-4.C7 sample failure: same pattern but at warning severity — Cross-Artifact Audit may upgrade to blocking.

**Validator metadata.** Run post-Phase-4; expected duration ~10 minutes (audit re-run + sample inspection).

## PV-5 — Phase 5 (Verification records)

**Phase reference:** Plan §Phase 5 (P5.1 enumerate pairs; P5.2 audit each; P5.3 author records)

**Validator goal:** Confirm every (subagent, preloaded-skill) pair from baseline X9 has a verification record at the named path.

**Pass criteria.**

- **PV-5.C1 — All pairs have verification records.** AT-017 passes. *Severity: blocking.*
- **PV-5.C2 — No skill in P5.2 audit failed without surfacing.** If any per-skill audit in P5.2 produced a FAIL verdict, per Plan §P5.3 note: "surface per ADR-0029 — that's a real defect that should either be fixed (scope expansion to PRD amend) or noted as a follow-on Won't-Have for this feature." Confirm `observations.md` or `implementation-notes.md` records the surfacing if any failure occurred. *Severity: blocking — silent failure here would violate ADR-0029.*

**Acceptance tests scheduled for this phase:** AT-017.

**Operational checks.** Phase 5 depends on PV-2.C4 (X9 wired) — without X9 emitting actionable findings, the pair enumeration in P5.1 has nothing to read.

**Failure response.** PV-5.C1 failure: missing verification record(s). Identify the missing pair(s) from the gap between AT-017's expected set and actual files; author the missing record(s).

**Validator metadata.** Run post-Phase-5; expected duration ~5 minutes.

## PV-6 — Phase 6 (Integration + final audit)

**Phase reference:** Plan §Phase 6 (P6.1 final audit re-run; P6.2 AC matrix; P6.3 Cross-Artifact Audit; P6.4 reconciliation; P6.5 task decomposition; P6.6 deliverable packaging)

**Validator goal:** Confirm the final audit converges on target counts AND every AC is verified AND Cross-Artifact Audit passes (potentially after one or more reconciliation cycles).

**Pass criteria.**

- **PV-6.C1 — Final audit captured.** `test -s /tmp/final-audit.json` AND `test -s /tmp/final-audit.md`. *Severity: blocking.*
- **PV-6.C2 — Final BLOCKER count == 0.** Per Plan §P6.1 target. *Severity: blocking.*
- **PV-6.C3 — Final MAJOR count == 0 modulo named exemption.** Per Plan §P6.1 target: zero MAJOR OR exactly one MAJOR being the named-exempt Bash MAJOR in `review-cross-artifact-auditor.md`. *Severity: blocking.*
- **PV-6.C4 — Final MINOR count < 29.** Strict inequality per Plan §P6.1 target (X9 reformulation reduces or replaces with higher-signal output). *Severity: blocking — equality means X9 just emitted the same shape as before, which fails AC-FR-6-c.*
- **PV-6.C5 — All acceptance tests pass.** AT-001 through AT-032 each have evidence recorded in `acceptance-verification-matrix.md` (per Plan §P6.2). Manual verification — but Cross-Artifact Audit at P6.3 is the independent check. *Severity: blocking.*
- **PV-6.C6 — Cross-Artifact Audit verdict is PASS or PASS-after-reconciliation.** Cross-Artifact Audit output exists; verdict either PASS directly OR PASS after ≤ 4 reconciliation cycles per ADR-0021 convergence cap. *Severity: blocking.*
- **PV-6.C7 — Cross-Artifact Audit's three Synthesis-flagged checks all pass.** Per Synthesis §3 + Blueprint §Verification Strategy: (1) After FR-12, only one canonical OR all import-shims (no surviving independent implementations); (2) sample-check actual markers' justifications for substance not boilerplate; (3) if per-layer Design chose "reword only" for AC-FR-5-b without regex fix, flag. *Severity: blocking — these are the explicit Synthesis surfacings per Plan §P6.3.*
- **PV-6.C8 — `tasks.json` produced if reconciliation surfaced granular work.** Plan §P6.5 — Task Decomposition produces `tasks.json` for any granular work items surviving reconciliation. If reconciliation closed everything, `tasks.json` may be empty/absent (acceptable). *Severity: informational.*
- **PV-6.C9 — Deliverable archive packaged and `packager-report.json` produced.** Plan §P6.6 — `finalize-deliverable-packager` verifies archive completeness; `packager-report.json` exists. *Severity: blocking — Gate 6 requires the packaged deliverable.*
- **PV-6.C10 — OBS-PLAN-001 (stage-number discipline violation) addressed OR explicitly deferred.** Per `observations.md`: either P6.3 picks up OBS-PLAN-001 → P6.4 reconciliation supersedes the prior Plan version, OR the observation is explicitly recorded as deferred-to-follow-on. *Severity: warning — explicit deferral is acceptable per user 2026-05-21 disposition; silent dropping is not.*

**Acceptance tests scheduled for this phase:** AT-001, AT-002, AT-003 (audit + sample), AT-004 (manual), AT-005, AT-006, AT-007, AT-008, AT-009 (final verify), AT-010, AT-012, AT-013, AT-016, AT-018, AT-020, AT-022, AT-023, AT-024, AT-025, AT-026, AT-027, AT-030 (final pair check), AT-032. (AT-011, AT-014, AT-015, AT-017, AT-019, AT-021, AT-028, AT-029, AT-031 already verified at earlier PVs.)

**Operational checks.** Final audit must run from clean repo state (no uncommitted changes from prior phases). Reconciliation cycle count must not exceed 4 (ADR-0021); if 4 cycles pass without convergence, escalate to user per ADR-0021.

**Failure response.** PV-6.C2/C3/C4 (count targets) failure: residual findings remain; reconciliation cycle dispatches per-finding fixes. PV-6.C6 (Cross-Artifact Audit not converging in 4 cycles): escalate to user with audit findings + reconciliation log; user decides whether to amend PRD/Blueprint or accept partial coverage. PV-6.C7 sub-check failures map directly to known anti-patterns this feature exists to prevent.

**Validator metadata.** Run iteratively during P6 cycle; expected duration ~30 minutes per cycle (audit + AC matrix + Cross-Artifact Audit + reconciliation pass).

## Cross-validator dependency graph

```
PV-0 (Setup)
   │
   ▼
PV-1 (Foundation) ──── PV-2 (Auditor improvements) ─┐
   │                              │                 │
   │                              ▼                 │
   │                          PV-5 (Verification    │
   │                              records)          │
   ▼                              │                 │
PV-4 (Marker work)                │                 ▼
   │                              │            PV-3 (Real-fix
   │                              │             dispositions)
   ▼                              │                 │
   └──────────────────────────────┴─────────────────┘
                  │
                  ▼
              PV-6 (Integration)
```

Hard dependencies:
- PV-1 blocks PV-4 (PV-4 needs canonical implementation from PV-1.C3)
- PV-2 blocks PV-5 (PV-5 needs X9 wired from PV-2.C4)
- PV-1 blocks PV-3 partial (P3.2 / PV-3.C2 needs the mechanism-α spec from PV-1.C1)
- All prior PVs block PV-6

Parallel-eligible pairs:
- PV-2 || PV-3 (different auditor modules vs. different agent edits)
- PV-2 || PV-4 (only the PV-1-dependent subset of PV-4 needs to wait)

## Critical-path validators

In descending order of feature-completion delay if failing:

1. **PV-6.C7** (Cross-Artifact Audit's Synthesis-flagged checks) — catches the specific anti-patterns this feature exists to prevent; failure routes through reconciliation cycles which can compound delay.
2. **PV-1.C5** (behavior equivalence) — if FR-12 broke audit semantics, every downstream count target is wrong.
3. **PV-2.C1 / C3** (regex behaviors) — auditor edits are foundational to most AT- verifications.
4. **PV-4.C5** (intermediate marker audit) — surfaces unjustified-marker problems before they pile up in P4.6's 32-file batch.

## Parallelizable validator checks

- Within PV-2: C1, C3, C4 cover different audit modules; can run in parallel.
- Within PV-4: C1/C2 (dedup verification) and C3 (scan_memory_secrets dedup) and C4 (retroactive upgrades) and C6 (location/where compat) are independent.
- Within PV-6: AT-001 through AT-010, AT-012, AT-013, AT-022 all share the single `/tmp/final-audit.json` capture — one read, multiple assertions, parallelizable.

## Shared validator infrastructure

- `/tmp/baseline-audit.{md,json}` — read by PV-0, PV-1, PV-6
- `/tmp/post-dedup-audit.json` — read by PV-1
- `/tmp/post-phase4-audit.json` — read by PV-4
- `/tmp/final-audit.{md,json}` — read by PV-6 (and indirectly by every AT- in PV-6's schedule)
- `/tmp/audit-findings-fixtures/` — read by PV-0, PV-2, PV-4
- `implementation-notes.md` — read by PV-3, PV-4 (sample-check provenance)
- `observations.md` — read by PV-5, PV-6 (ADR-0029 surfacings ledger)

## Validator runbook

For a human (or Claude in execution-session role) running the feature end-to-end:

1. **Before starting Phase 1:** run PV-0 (5 criteria); halt if any blocking fails. PV-0.C2 baseline-count check is the most common failure mode — investigate any drift before proceeding.
2. **After P1.4 lands:** run PV-1 (6 criteria); halt if C1-C5 blocking fails. C6 informational only.
3. **After Phase 2 lands (parallel-eligible with Phase 3):** run PV-2 (6 criteria); halt on blocking failure. Negative fixtures (C1, C3) are the highest-signal checks.
4. **After Phase 3 lands:** run PV-3 (4 criteria).
5. **After Phase 4 lands (largest phase):** run PV-4 (7 criteria). C5's intermediate audit is the per-phase L2 gate per Plan.
6. **After Phase 5 lands:** run PV-5 (2 criteria).
7. **During Phase 6:** PV-6 runs iteratively. Each reconciliation cycle re-runs PV-6.C1-C7. Cap at 4 cycles per ADR-0021; escalate beyond.
8. **At Gate 6:** user reviews `packager-report.json` + deliverable archive; PV-6.C9 satisfaction is the gate's mechanical precondition.

For Cross-Artifact Audit (Plan §P6.3), the auditor reviews ALL feature artifacts against each other for consistency. The PV framework supplies one input among many (the validator-pass record); the auditor does not re-execute validators, but DOES check that the validator framework's pass-criteria align with the Plan's exit criteria and the PRD's ACs.

## Update history

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-21T20:32:00Z | claude (continuation session, acting as test-phase-validator-author) | Initial phase validators covering Plan v1.0.0's P0-P6 |
| 1.1.0 | 2026-05-21T21:16:00Z | claude (continuation session, acting as test-phase-validator-author re-invoked by finalize-reconciler cycle 2) | Supersedes v1.0.0 per ADR-0005. Addresses cross-artifact audit round 2 finding I-CA-004 (MAJOR — stage-number discipline violation class, phase-validators portion: 3 instances rewritten — PV-6.C6 "Stage 12 output exists" → "Cross-Artifact Audit output exists"; PV-6.C8 "Plan §P6.5 — Stage 13 produces tasks.json" → "Plan §P6.5 — Task Decomposition produces tasks.json"; runbook line 266 "For Cross-Artifact Audit (Stage 12, Plan §P6.3)" → "For Cross-Artifact Audit (Plan §P6.3)"). Also addresses 2 stale `plan-v1.md` body references discovered during cycle-2 pre-round-3-audit sanity sweep — these were derivative defects from the supersession of plan-v1.md → plan-v1.2.0.md (Posture paragraph "in `plan-v1.md`" → "in the current Plan version"; PV-6.C10 "P6.4 reconciliation supersedes plan-v1.md" → "P6.4 reconciliation supersedes the prior Plan version"). Version-agnostic form chosen to prevent recurrence on any future Plan supersession. No other content changes; PV-0 through PV-6, dependency graph, critical-path, shared infrastructure, runbook all unchanged. See `reconciliation-log-cycle2.md` and `cross-artifact-audit-issues-r2.json` for full audit trail. |
