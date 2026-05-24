---
id: AT-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: acceptance-tests
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
version: 1.0.0
status: draft
scope_class: FULL
layer_scope: [cc]
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md
generated: 2026-05-24T01:15:00Z
generated_by: test-acceptance-author
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/phase-validators.md (peer artifact authored in parallel)
---

# Acceptance Tests: execute-orchestrator Dispatch Mechanism Repair (r1)

## Overview

### Feature recap

This Blueprint flattens the execution-phase dispatch hierarchy (ADR-0044): the `recipe-feature-pipeline` parent skill becomes the direct dispatcher of the four execution-side specialists at the main-conversation level (where dispatch IS supported per T-001 Finding F-1), and `execute-orchestrator.md` is re-scoped as a state-machine advisor. The repair is realized across 8 in-inventory + 1 outside-inventory files. ADR-0045 codifies the project-wide convention forbidding `Agent` in sub-agent `tools:` arrays. FR-1/FR-2 ACs are inherited from the in-pipeline Discovery investigation (T-001) outcome; FR-2 ACs are vacuously satisfied because kill-criterion-#2 fired (not kc-#1).

### Test posture

The verification surface is structural-and-filesystem: this feature changes documentation, frontmatter, and project filesystem state — there is no runtime service to instrument. Tests therefore rely on:

- **L1 (file-existence / grep / structural-parse):** the dominant test type. Cheap, deterministic, runnable post-task as a phase-validator stage.
- **L2 (structural-parse / behavioral):** YAML frontmatter parse, cross-file consistency, commit-message structural check, git history shape.
- **L3 (end-to-end / behavioral):** the synthetic minimal test feature dispatch loop under FR-6 — the load-bearing end-to-end verification, exercised by an operator after a session restart.

Two tests are operator-facing (require human interaction in a fresh Claude Code session); the remainder are scriptable. The bundled-commit invariant on T3.6 has its own structural-parse test that asserts the exact phrase `FR-5 sweep closure: affected set = 2` is present in the commit message and that exactly the right set of files is touched.

### Test pyramid disposition

The test pyramid for this feature is inverted relative to a typical service feature: there is no unit-test layer (no executable code in `.claude/` artifacts), no integration layer between services, and no UI. The pyramid here is:

```
                          ▲
                          │  L3 end-to-end:
                          │    T-FR-6-* (synthetic test feature dispatch)
                          │    T-AC-CC-1-coherence (cross-file ADR citation)
                          │
                          │  L2 structural-parse / behavioral:
                          │    T-FR-3-*, T-FR-4-*, T-FR-5-*, T-CC-*
                          │    Commit-message-shape tests
                          │
                          ▼  L1 file-existence / grep (the bulk):
                              T-AC-FR-{1,2}-* (kc gate verification)
                              T-T-* (per-task L1 grep tests)
```

All tests are deterministic and re-runnable; no time-of-day dependencies; no randomness in any assertion. The only operator-mediated steps are F-7 fresh-session gate (T6.2) and the verification of the Stage-13 packager waiver path (T0.2).

## Test inventory

One row per test. Columns: ID · Maps to AC · Test name · Type · Layer · Task mapped · Operator-facing?

| Test ID | Maps to AC | Test name | Type | L | Task | Op? |
|---|---|---|---|---|---|---|
| T-AC-FR-1-a-kb-gap-topic | AC-FR-1-a | Discovery Research emitted KB-gap research topic for harness sub-agent tool-grant semantics | file-existence + grep | L1 | satisfied-upstream (T-001) | No |
| T-AC-FR-1-b-finding-artifact | AC-FR-1-b | T-001 finding-with-evidence artifact exists and distinguishes 3 outcome classes | structural-parse | L2 | satisfied-upstream (T-001) | No |
| T-AC-FR-1-c-dispatch-supported-flag | AC-FR-1-c | T-001 note records `dispatch_supported: false` and is referenced by Synthesis | grep | L1 | satisfied-upstream (T-001) | No |
| T-AC-FR-2-a-no-kc1-posture | AC-FR-2-a | No `kill-criterion-1-triggered` posture marker in checkpoint.json | grep | L1 | vacuous-by-kc2 | No |
| T-AC-FR-2-b-progression-to-design | AC-FR-2-b | Pipeline progressed to per-layer cc Design (proving kc-#1 did NOT halt the run) | file-existence | L1 | vacuous-by-kc2 | No |
| T-AC-FR-2-c-no-followon-stub | AC-FR-2-c | No follow-on small-feature stub for one-flag fix exists (kc-#1 did not trigger) | file-existence (negation) + checkpoint.json grep | L1 | vacuous-by-kc2 | No |
| T-AC-FR-3-a-option-named | AC-FR-3-a | Blueprint and ADR-0044 name option (a) flatten-hierarchy with three-reason rationale | grep + structural-parse | L2 | T2.1, T3.1, T3.3 | No |
| T-AC-FR-3-b-specialist-substantive-preserved | AC-FR-3-b | The three leaf specialists' frontmatter (model/effort/skills/memory) unchanged from baseline | structural-parse + git-diff | L2 | T3.4, T3.5 | No |
| T-AC-FR-3-c-invariants-cited | AC-FR-3-c | ADR-0017 + ADR-0033 cited in Execution Phase Dispatch section; D-12 symmetric language present | grep | L1 | T2.1, T3.3 | No |
| T-AC-FR-4-a-inventory-cap | AC-FR-4-a | Git diff against rollback-baseline shows exactly 8 in-inventory + 1 outside-inventory files modified | git-diff + structural-parse | L2 | T0.2, T4.1, T4.2 | No |
| T-AC-FR-4-b-schema-lockstep | AC-FR-4-b | All 3 execution-phase fields documented in SKILL.md AND `void`/`-prime` extensions present in same commit set | grep + git-log | L2 | T1.1, T1.2, T1.3, T4.2 | No |
| T-AC-FR-4-c-leaf-specialists-substantive | AC-FR-4-c | Leaf specialists' Contract 1 / Contract 2 sections unchanged by diff inspection | git-diff | L2 | T3.4, T3.5 | No |
| T-AC-FR-5-a-agent-removed-both | AC-FR-5-a | `Agent` removed from `tools:` of execute-orchestrator + execute-finalize-reconciler | grep | L1 | T3.1, T3.3, T3.6 | No |
| T-AC-FR-5-a-adr-0034-zero | AC-FR-5-a | `grep -c ADR-0034` on execute-finalize-reconciler.md returns 0 | grep | L1 | T3.3 | No |
| T-AC-FR-5-a-adr-0033-ge-3 | AC-FR-5-a | `grep -c ADR-0033` on execute-finalize-reconciler.md returns ≥ 3 | grep | L1 | T3.3 | No |
| T-AC-FR-5-a-bundled-commit-message | AC-FR-5-a | Bundled commit message contains literal `FR-5 sweep closure: affected set = 2` | git-log grep | L2 | T3.6 | No |
| T-AC-FR-5-a-bundled-commit-fileset | AC-FR-5-a | Bundled commit touches exactly the 5 expected sub-agent files (no extras) | git-show structural | L2 | T3.6 | No |
| T-AC-FR-5-a-line-76-reframed | AC-FR-5-a | "Dispatch via Agent" prose at line 76-region replaced with "emit `dispatch_directives[]`" | grep (positive + negative) | L1 | T3.3 | No |
| T-AC-FR-5-b-inventory-artifact | AC-FR-5-b | `agent-tool-grant-inventory.md` exists with all 5 required elements | file-existence + grep | L1 | T5.1 | No |
| T-AC-FR-5-b-sweep-counts | AC-FR-5-b | Inventory artifact records "36 files swept" and "2 violations" (cited from codebase analysis) | grep | L1 | T5.1 | No |
| T-AC-FR-5-b-codebase-sweep-now-zero | AC-FR-5-b | Live grep across `.claude/agents/*.md` for `Agent` in `tools:` arrays returns 0 matches post-repair | grep | L2 | T3.6, T5.1 | No |
| T-AC-FR-6-a-log-per-boundary | AC-FR-6-a | Synthetic test's state-transitions.log emits ≥ 1 entry per specialist dispatch boundary | end-to-end + structural-parse | L3 | T6.3 | Yes |
| T-AC-FR-6-a-invoking-agent-preserved | AC-FR-6-a | All log entries record `invoking_agent: "execute-orchestrator"` (logical-owner v1) | JSONL grep | L3 | T6.3 | Yes |
| T-AC-FR-6-b-per-task-counter-at-T4 | AC-FR-6-b | checkpoint.json `per_task[<task-id>]` increments at T4 (NEEDS_REVISION); no increment at T0 | structural-parse + behavioral | L3 | T6.3 | Yes |
| T-AC-FR-6-b-per-phase-counter-at-T10 | AC-FR-6-b | checkpoint.json `per_phase[<phase-id>]` increments at T10 (phase reconciliation) | structural-parse + behavioral | L3 | T6.3 | Yes (conditional on NEEDS_RECONCILIATION) |
| T-AC-FR-6-b-T0-T13-no-increment | AC-FR-6-b | T0 and T13 log entries do NOT cause counter increments | behavioral | L3 | T6.3 | Yes |
| T-AC-FR-6-c-cycle-cap-halt | AC-FR-6-c | If counter reaches 4, run emits T13 TERMINATED + `escalation-cycle-cap.json` + user surface | behavioral | L3 | T6.3, T6.5 | Yes (conditional) |
| T-AC-FR-6-c-no-silent-fallback | AC-FR-6-c | On verification failure, `verification-failed` posture surfaces (negation of silent fallback) | behavioral | L3 | T6.5 | Yes (conditional) |
| T-AC-FR-6-d-no-new-subagents | AC-FR-6-d | Synthetic test feature design authors NO new sub-agent files (vacuously satisfies F-7) | grep (negation) | L2 | T6.1 | No |
| T-AC-FR-6-d-restart-task-documented | AC-FR-6-d | Plan T6.2 task definition includes operator-facing "Restart your Claude Code session" instruction | grep | L1 | T6.2 | No (structural check on Plan) |
| T-AC-FR-6-d-fresh-session-confirmed | AC-FR-6-d | Verification log records a fresh-session timestamp distinct from the Phase-3 edit session | file content check | L2 | T6.2, T6.4 | Yes |
| T-AC-FR-7-a-verification-log-naming | AC-FR-7-a | `verification-log.md` explicitly names FR-6 as gating and FR-7 (if performed) as confidence check | grep | L1 | T6.4 | No |
| T-AC-FR-8-a-adr-0045-exists | AC-FR-8-a | `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` exists with required linkages | file-existence + grep | L1 | T0.1 | No |
| T-AC-FR-8-a-manual-review-interim | AC-FR-8-a | Manual-review interim documentation present with the 4 required elements | grep | L1 | T5.2 | No |
| T-AC-NFR-1-a-end-to-end-complete | AC-NFR-1-a | Synthetic test reaches T12 `pipeline_complete` without parent-driven workaround fallback | behavioral | L3 | T6.3 | Yes |
| T-AC-NFR-1-b-explicit-failure-surface | AC-NFR-1-b | On dispatch failure, system surfaces failure (does NOT silently fall back) | behavioral | L3 | T6.5 | Yes (conditional) |
| T-AC-NFR-2-a-log-per-dispatch | AC-NFR-2-a | One state-transitions.log entry per specialist dispatch boundary (duplicate-of AC-FR-6-a; shared assertion) | JSONL structural | L3 | T6.3 | Yes |
| T-AC-NFR-2-b-dispatcher-identity-preserved | AC-NFR-2-b | Log entries record `invoking_agent` value distinguishable from parent-driven entries (none expected post-repair) | JSONL grep | L3 | T6.3 | Yes |
| T-AC-NFR-3-a-counters-increment | AC-NFR-3-a | checkpoint.json counters increment at task/phase boundaries (duplicate-of AC-FR-6-b assertion) | structural-parse | L3 | T6.3 | Yes |
| T-AC-NFR-3-b-cycle-cap-routes-via-reconciler | AC-NFR-3-b | If counter exceeds 4, halt routes through `execute-finalize-reconciler` (or its emit-directive equivalent under option (a)) | behavioral | L3 | T6.3 | Yes (conditional) |
| T-AC-NFR-4-a-finding-artifact | AC-NFR-4-a | T-001 research note exists with `dispatch_supported: false` flag and stable identifier | file-existence + grep | L1 | satisfied-upstream | No |
| T-AC-NFR-5-a-schema-reference-lockstep | AC-NFR-5-a | Schema-reference change in SKILL.md and any schema field change are in the same commit set | git-log structural | L2 | T1.1, T1.2, T1.3 | No |
| T-AC-NFR-6-a-in-flight-untouched | AC-NFR-6-a | `working/feature/devcontainer-mcp-provisioning-r1/` artifacts are NOT modified by this run | git-diff | L1 | T4.1 | No |
| T-AC-NFR-6-b-new-schema-marked | AC-NFR-6-b | `execution_mode` field documented with both v1 values (`single-agent-fallback` + `specialist-isolation`) | grep | L1 | T1.2, T4.2 | No |
| T-AC-NFR-7-a-synthetic-archived | AC-NFR-7-a | Synthetic test feature archived under `working/test-features/` after FR-6 PASS | file-existence | L1 | T6.4 | No |
| T-AC-CC-1-adr-0034-absent-skill-md | AC-CC-1 | `grep -c ADR-0034 .claude/skills/recipe-feature-pipeline/SKILL.md` returns 0 | grep | L1 | T2.1 | No |
| T-AC-CC-1-adr-0034-absent-finalize | AC-CC-1 | `grep -c ADR-0034 .claude/agents/execute-finalize-reconciler.md` returns 0 | grep | L1 | T3.3 | No |
| T-AC-CC-1-adr-0033-present-skill-md | AC-CC-1 | `grep -c ADR-0033 .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥ 1 | grep | L1 | T2.1 | No |
| T-AC-CC-1-adr-0033-present-finalize | AC-CC-1 | `grep -c ADR-0033 .claude/agents/execute-finalize-reconciler.md` returns ≥ 3 | grep | L1 | T3.3 | No |
| T-AC-CC-1-adr-0017-present | AC-CC-1 | `grep -c ADR-0017 .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥ 1 in dispatch section | grep | L1 | T2.1 | No |
| T-AC-CC-2-skill-md-lockstep | AC-CC-2 | D-001 dispatch section + D-004 schema closure land in the SAME logical commit set on SKILL.md | git-log structural | L2 | T1.1–T1.3, T2.1 | No |
| T-AC-CC-3-self-reference-rationale | AC-CC-3 | execute-orchestrator.md body contains explicit "self-reference is intentional" rationale paragraph | grep | L1 | T3.2 | No |
| T-AC-CC-3-self-reference-preserved | AC-CC-3 | execute-orchestrator.md `skills:` array still contains `recipe-feature-pipeline` | YAML parse | L2 | T3.1 | No |
| T-AC-CC-4-malformed-directives-handling | AC-CC-4 | SKILL.md documents malformed/empty `dispatch_directives[]` → user surface + cycle-cap-equivalent escalation | grep | L1 | T2.2 | No |

**Total tests:** 51.

## Per-test details

Each test below specifies preconditions, steps (concrete shell commands where possible), expected outcome (concrete assertions), and the layer.

---

### T-AC-FR-1-a-kb-gap-topic — Discovery Research emitted KB-gap research topic for harness sub-agent tool-grant semantics

- **Type:** file-existence + grep
- **L:** L1
- **AC:** AC-FR-1-a
- **Task:** satisfied-upstream (T-001 research authored at Stage 4)
- **Preconditions:** Research Plan artifact exists at `working/feature/<slug>/research-plan.md` or equivalent.
- **Steps:**
  1. `ls working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md`
  2. `grep -E 'disposition:[[:space:]]*external-research-topic' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-plan.md || grep -E 'disposition:[[:space:]]*external-research-topic' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-*.md`
  3. `grep -i 'kb_gap_justification.*sub-agent tool-grant\|harness sub-agent tool-grant' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-*.md`
- **Expected outcome:** Step 1 returns the file path (exit 0). Step 2 returns at least one line containing `external-research-topic`. Step 3 returns at least one line containing the KB-gap justification phrase.
- **Determinism notes:** Static filesystem read; fully deterministic.

---

### T-AC-FR-1-b-finding-artifact — T-001 finding-with-evidence artifact exists and distinguishes 3 outcome classes

- **Type:** structural-parse
- **L:** L2
- **AC:** AC-FR-1-b
- **Task:** satisfied-upstream (T-001)
- **Preconditions:** T-001 research note exists.
- **Steps:**
  1. `cat working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md`
  2. Assert the document distinguishes (a) harness-level restriction, (b) frontmatter-parsing bug, (c) one-flag-fix — each as a named outcome.
  3. Assert the document cites at least one Anthropic-controlled primary source URL and at least one probe sub-agent result.
- **Expected outcome:** Three outcome classes named in prose; ≥1 Anthropic URL cited; ≥1 probe result cited.
- **Determinism notes:** Static document parse.

---

### T-AC-FR-1-c-dispatch-supported-flag — T-001 note records `dispatch_supported: false` and is referenced by Synthesis

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-1-c
- **Task:** satisfied-upstream (T-001)
- **Preconditions:** T-001 note + synthesis.md exist.
- **Steps:**
  1. `grep -E 'dispatch_supported:[[:space:]]*false' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-*.md`
  2. `grep -l 'T-001\|dispatch_supported' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md`
- **Expected outcome:** Step 1 matches (load-bearing flag present); Step 2 confirms synthesis references the note.
- **Determinism notes:** Static grep.

---

### T-AC-FR-2-a-no-kc1-posture — No `kill-criterion-1-triggered` posture marker in checkpoint.json

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-2-a (vacuous-by-kc2)
- **Task:** vacuous-by-kc2
- **Preconditions:** Run's checkpoint.json exists.
- **Steps:**
  1. `grep -c 'kill-criterion-1-triggered\|kill_criterion_triggered.*1' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/checkpoint.json`
  2. `grep -E 'kill_criterion_triggered[[:space:]]*:[[:space:]]*2' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/checkpoint.json`
- **Expected outcome:** Step 1 returns 0 (no kc-#1 marker). Step 2 returns ≥1 (kc-#2 marker present, confirming FULL repair was chosen).
- **Negative-path coverage:** The AC's positive trigger condition is intentionally vacuous; the test verifies the absence of the trigger AND the presence of the alternative (kc-#2) for evidence.
- **Determinism notes:** Static file read.

---

### T-AC-FR-2-b-progression-to-design — Pipeline progressed to per-layer cc Design

- **Type:** file-existence
- **L:** L1
- **AC:** AC-FR-2-b (vacuous-by-kc2)
- **Task:** vacuous-by-kc2
- **Preconditions:** Run completed at least past Design stage.
- **Steps:**
  1. `ls working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md`
  2. `ls working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md`
  3. `ls working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md`
- **Expected outcome:** All three files exist (proving the run progressed beyond the kc-#1 halt point).
- **Determinism notes:** Static.

---

### T-AC-FR-2-c-no-followon-stub — No follow-on small-feature stub for one-flag fix exists

- **Type:** file-existence (negation) + checkpoint grep
- **L:** L1
- **AC:** AC-FR-2-c (vacuous-by-kc2)
- **Task:** vacuous-by-kc2
- **Preconditions:** working/feature/ directory readable.
- **Steps:**
  1. `find working/feature -maxdepth 2 -name 'analysis*one-flag*' -o -name '*one-flag-fix*'` (expect empty)
  2. `grep -E 'follow_on_feature_pointer' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/checkpoint.json` (expect not present)
- **Expected outcome:** No follow-on stub; checkpoint records `kill_criterion_triggered: 2` (cross-referenced from T-AC-FR-2-a).
- **Determinism notes:** Static.

---

### T-AC-FR-3-a-option-named — Blueprint and ADR-0044 name option (a) flatten-hierarchy with three-reason rationale

- **Type:** grep + structural-parse
- **L:** L2
- **AC:** AC-FR-3-a
- **Task:** T2.1, T3.1, T3.3
- **Preconditions:** Blueprint v1.1.0 + ADR-0044 exist.
- **Steps:**
  1. `grep -i 'option (a)\|flatten-hierarchy\|flatten dispatch hierarchy' adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md`
  2. `grep -A 20 'Rationale' adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md | grep -cE 'FR-4|inventory|invariant|specialist-isolation'`
  3. `grep -i 'option (a) flatten-hierarchy\|option (a) flatten dispatch' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md`
- **Expected outcome:** Step 1: ≥1 match. Step 2: ≥3 (three rationale reasons). Step 3: ≥1 match.
- **Determinism notes:** Static grep.

---

### T-AC-FR-3-b-specialist-substantive-preserved — Three leaf specialists' frontmatter unchanged from baseline

- **Type:** structural-parse + git-diff
- **L:** L2
- **AC:** AC-FR-3-b
- **Task:** T3.4, T3.5
- **Preconditions:** T3.6 bundled commit landed; baseline SHA recorded in rollback-baseline.txt.
- **Steps:**
  1. `BASE=$(cat working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt | head -1)`
  2. For each of `execute-task-code-producer.md`, `execute-task-quality-handler.md`, `execute-phase-quality-reviewer.md`:
     - `git diff ${BASE}..HEAD -- .claude/agents/<file>.md | grep -E '^[+-](model|effort|tools|skills|memory):'`
- **Expected outcome:** Step 2 returns no output for any of the three files (frontmatter lines unchanged in the diff).
- **Determinism notes:** Deterministic given the baseline SHA.

---

### T-AC-FR-3-c-invariants-cited — ADR-0017 + ADR-0033 cited; D-12 symmetric language present

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-3-c
- **Task:** T2.1, T3.3
- **Steps:**
  1. `grep -nE 'ADR-0017' .claude/skills/recipe-feature-pipeline/SKILL.md` (in dispatch section)
  2. `grep -nE 'ADR-0033' .claude/skills/recipe-feature-pipeline/SKILL.md`
  3. `grep -iE 'D-12|symmetric|per-task.*per-phase' .claude/skills/recipe-feature-pipeline/SKILL.md`
  4. `grep -nE 'D-2a|D-2c|D-2d|D-13|D-14' .claude/skills/recipe-feature-pipeline/SKILL.md` (dispatch-matrix definitions preserved)
- **Expected outcome:** Steps 1, 2, 3, 4 all return ≥1 match.
- **Determinism notes:** Static grep.

---

### T-AC-FR-4-a-inventory-cap — Git diff shows exactly 8 in-inventory + 1 outside-inventory files modified

- **Type:** git-diff + structural-parse
- **L:** L2
- **AC:** AC-FR-4-a
- **Task:** T0.2, T4.1, T4.2
- **Preconditions:** All feature commits landed; rollback-baseline.txt present.
- **Steps:**
  1. `BASE=$(cat working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt | head -1)`
  2. `git diff --name-only ${BASE}..HEAD | grep -vE '^working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/' | grep -vE '^adrs/ADR-004[45]' | sort -u > /tmp/touched.txt`
  3. `cat /tmp/touched.txt` — assert content equals the 9 expected paths:
     - `.claude/skills/recipe-feature-pipeline/SKILL.md`
     - `.claude/agents/execute-orchestrator.md`
     - `.claude/agents/execute-task-code-producer.md`
     - `.claude/agents/execute-task-quality-handler.md`
     - `.claude/agents/execute-phase-quality-reviewer.md`
     - `.claude/agents/execute-finalize-reconciler.md`
     - `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`
     - (the in-inventory checkpoint.json and state-transitions.log schemas are documented in SKILL.md — they're not separately-edited paths)
- **Expected outcome:** /tmp/touched.txt contains exactly the listed paths (the 7 substantive files; ADR-0044/0045 are new and added separately; the checkpoint.json + state-transitions.log "schemas" are reference-only inside SKILL.md). Any extra path triggers AC-FR-4-a operator-gate failure.
- **Determinism notes:** Deterministic given the baseline.

---

### T-AC-FR-4-b-schema-lockstep — All 3 execution-phase fields documented in SKILL.md AND `void`/`-prime` extensions present

- **Type:** grep + git-log
- **L:** L2
- **AC:** AC-FR-4-b
- **Task:** T1.1, T1.2, T1.3, T4.2
- **Steps:**
  1. `grep -nE 'execution_pipeline_state_transitions' .claude/skills/recipe-feature-pipeline/SKILL.md`
  2. `grep -nE 'execution_mode' .claude/skills/recipe-feature-pipeline/SKILL.md`
  3. `grep -nE 'execution_pipeline_cycle_counters' .claude/skills/recipe-feature-pipeline/SKILL.md`
  4. `grep -nE '\bvoid\b|void_reason' .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`
  5. `grep -nE '\-prime' .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`
- **Expected outcome:** Each step returns ≥1 match.
- **Determinism notes:** Static.

---

### T-AC-FR-4-c-leaf-specialists-substantive — Leaf specialists' Contract sections unchanged

- **Type:** git-diff
- **L:** L2
- **AC:** AC-FR-4-c
- **Task:** T3.4, T3.5
- **Steps:**
  1. `BASE=$(cat working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt | head -1)`
  2. For each leaf specialist: `git diff ${BASE}..HEAD -- .claude/agents/<file>.md` — visually confirm only prose-level changes (dispatcher references), no contract-shape changes.
  3. `git diff ${BASE}..HEAD -- .claude/agents/execute-task-code-producer.md | grep -E '^[+-].*Contract 1\|input.*shape\|output.*shape' | wc -l`
- **Expected outcome:** Step 3 returns 0 (no diffs touching Contract definitions or input/output shapes).
- **Determinism notes:** Deterministic.

---

### T-AC-FR-5-a-agent-removed-both — `Agent` removed from `tools:` of execute-orchestrator + execute-finalize-reconciler

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-5-a
- **Task:** T3.1, T3.3, T3.6
- **Steps:**
  1. `grep -E '^tools:.*\bAgent\b' .claude/agents/execute-orchestrator.md` (expect no match)
  2. `grep -E '^tools:.*\bAgent\b' .claude/agents/execute-finalize-reconciler.md` (expect no match)
  3. `grep -E '^tools:' .claude/agents/execute-orchestrator.md` (positive: tools line still present)
  4. `grep -E '^tools:' .claude/agents/execute-finalize-reconciler.md` (positive)
- **Expected outcome:** Steps 1, 2 return zero matches; Steps 3, 4 return one match each (tools array still declared, just without `Agent`).
- **Determinism notes:** Static.

---

### T-AC-FR-5-a-adr-0034-zero — `grep -c ADR-0034` on execute-finalize-reconciler.md returns 0

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-5-a (DISSENT-2 carry-through)
- **Task:** T3.3
- **Steps:**
  1. `grep -c 'ADR-0034' .claude/agents/execute-finalize-reconciler.md`
- **Expected outcome:** Returns the integer `0`. All three occurrences on lines 3, 19, 82 of the pre-repair file have been corrected.
- **Determinism notes:** Static.

---

### T-AC-FR-5-a-adr-0033-ge-3 — `grep -c ADR-0033` on execute-finalize-reconciler.md returns ≥ 3

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-5-a
- **Task:** T3.3
- **Steps:**
  1. `N=$(grep -c 'ADR-0033' .claude/agents/execute-finalize-reconciler.md); [ "$N" -ge 3 ]`
- **Expected outcome:** Exit status 0; integer ≥ 3 (covering the 3 lines previously holding ADR-0034 mis-cites).
- **Determinism notes:** Static.

---

### T-AC-FR-5-a-bundled-commit-message — Bundled commit message contains literal `FR-5 sweep closure: affected set = 2`

- **Type:** git-log grep
- **L:** L2
- **AC:** AC-FR-5-a (bundled-commit invariant)
- **Task:** T3.6
- **Preconditions:** T3.6 commit landed on the branch.
- **Steps:**
  1. Locate the bundled-commit SHA: `BUNDLE_SHA=$(git log --grep='FR-5 sweep closure: affected set = 2' --format=%H -1)`
  2. Assert: `[ -n "$BUNDLE_SHA" ]`
  3. `git log --format=%B -1 ${BUNDLE_SHA} | grep -F 'FR-5 sweep closure: affected set = 2'`
- **Expected outcome:** Step 1 finds a non-empty SHA; Step 3 returns exit 0 (literal string present in commit message body).
- **Determinism notes:** Static given commit history.

---

### T-AC-FR-5-a-bundled-commit-fileset — Bundled commit touches exactly the 5 expected sub-agent files

- **Type:** git-show structural
- **L:** L2
- **AC:** AC-FR-5-a
- **Task:** T3.6
- **Steps:**
  1. `BUNDLE_SHA=$(git log --grep='FR-5 sweep closure: affected set = 2' --format=%H -1)`
  2. `git show --name-only --format= ${BUNDLE_SHA} | sort -u > /tmp/bundle-files.txt`
  3. Assert content equals (sorted):
     - `.claude/agents/execute-finalize-reconciler.md`
     - `.claude/agents/execute-orchestrator.md`
     - `.claude/agents/execute-phase-quality-reviewer.md`
     - `.claude/agents/execute-task-code-producer.md`
     - `.claude/agents/execute-task-quality-handler.md`
- **Expected outcome:** /tmp/bundle-files.txt matches exactly the 5 paths (no extras).
- **Determinism notes:** Deterministic.

---

### T-AC-FR-5-a-line-76-reframed — "Dispatch via Agent" prose replaced with "emit `dispatch_directives[]`"

- **Type:** grep (positive + negative)
- **L:** L1
- **AC:** AC-FR-5-a
- **Task:** T3.3
- **Steps:**
  1. `grep -ciE 'Dispatch via Agent' .claude/agents/execute-finalize-reconciler.md` (expect 0)
  2. `grep -nE 'dispatch_directives\[\]' .claude/agents/execute-finalize-reconciler.md` (expect ≥1 match in the body)
- **Expected outcome:** Step 1: 0. Step 2: ≥1.
- **Determinism notes:** Static.

---

### T-AC-FR-5-b-inventory-artifact — Inventory artifact exists with all 5 required elements

- **Type:** file-existence + grep
- **L:** L1
- **AC:** AC-FR-5-b
- **Task:** T5.1
- **Steps:**
  1. `INV=working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md`
  2. `[ -f "$INV" ]`
  3. For each required element, grep:
     - `grep -i '36' "$INV"` (total swept)
     - `grep -i '2 violations\|two violations' "$INV"`
     - `grep -i 'execute-orchestrator' "$INV"` and `grep -i 'execute-finalize-reconciler' "$INV"`
     - `grep -i 'cleaned\|post-repair' "$INV"`
     - `grep -i 'ADR-0045' "$INV"`
- **Expected outcome:** File exists; each grep returns ≥1 match.
- **Determinism notes:** Static.

---

### T-AC-FR-5-b-sweep-counts — Inventory artifact records "36 files swept" and "2 violations"

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-5-b
- **Task:** T5.1
- **Steps:**
  1. `INV=working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md`
  2. `grep -iE '36 (files|sub-agents)' "$INV"`
  3. `grep -iE '2 violations|2 found' "$INV"`
- **Expected outcome:** Both greps return ≥1 match.
- **Determinism notes:** Static.

---

### T-AC-FR-5-b-codebase-sweep-now-zero — Live grep across `.claude/agents/*.md` for `Agent` in `tools:` returns 0

- **Type:** grep
- **L:** L2
- **AC:** AC-FR-5-b
- **Task:** T3.6, T5.1
- **Steps:**
  1. `grep -lE '^tools:.*\bAgent\b' .claude/agents/*.md | wc -l`
- **Expected outcome:** Returns `0`.
- **Negative-path coverage:** This test asserts the global filesystem invariant that ADR-0045 codifies.
- **Determinism notes:** Static.

---

### T-AC-FR-6-a-log-per-boundary — Synthetic test's state-transitions.log emits ≥ 1 entry per specialist boundary

- **Type:** end-to-end + structural-parse
- **L:** L3
- **AC:** AC-FR-6-a
- **Task:** T6.3
- **Operator-facing:** Yes
- **Preconditions:** Phases 0–5 complete; operator restarted Claude Code session (T6.2); synthetic test feature run via T6.3.
- **Steps:**
  1. After T6.3 completes, locate the synthetic run's log: `LOG=working/test-features/dispatch-mechanism-regression/state-transitions.log` (path per T6.1).
  2. `[ -s "$LOG" ]`
  3. Count entries per dispatched specialist:
     - `grep -c 'execute-task-code-producer' "$LOG"` ≥ 1
     - `grep -c 'execute-task-quality-handler' "$LOG"` ≥ 1
     - `grep -c 'execute-phase-quality-reviewer' "$LOG"` ≥ 1 (if synthetic includes phase boundary)
     - `grep -c 'execute-finalize-reconciler' "$LOG"` ≥ 1 (conditional on NEEDS_RECONCILIATION inclusion)
- **Expected outcome:** Each unconditional grep ≥ 1; the conditional reconciler grep ≥ 1 IF the synthetic test design includes NEEDS_RECONCILIATION.
- **Determinism notes:** Determinism depends on the synthetic test feature being well-designed; flake risk is low because the feature deterministically dispatches the same specialist set every run.

---

### T-AC-FR-6-a-invoking-agent-preserved — Log entries record `invoking_agent: "execute-orchestrator"`

- **Type:** JSONL grep
- **L:** L3
- **AC:** AC-FR-6-a
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:**
  1. `LOG=working/test-features/dispatch-mechanism-regression/state-transitions.log`
  2. `TOTAL=$(wc -l < "$LOG"); MATCH=$(grep -c '"invoking_agent":[[:space:]]*"execute-orchestrator"' "$LOG"); [ "$TOTAL" -eq "$MATCH" ]`
- **Expected outcome:** Every log line has `invoking_agent: "execute-orchestrator"` (logical-owner v1 invariant).
- **Determinism notes:** JSONL line counting is deterministic.

---

### T-AC-FR-6-b-per-task-counter-at-T4 — `per_task[<task-id>]` increments at T4; no increment at T0

- **Type:** structural-parse + behavioral
- **L:** L3
- **AC:** AC-FR-6-b
- **Task:** T6.3
- **Operator-facing:** Yes
- **Preconditions:** Synthetic test designed to trigger ≥1 NEEDS_REVISION cycle.
- **Steps:**
  1. Inspect `checkpoint.json.execution_pipeline_cycle_counters.per_task` after T6.3.
  2. Assert the per-task counter for the test's task is ≥ 1.
  3. Cross-reference with the state-transitions.log: count `"transition": "T4"` entries; counter value should equal the T4 count (within the test's task scope).
  4. Cross-check: count `"transition": "T0"` entries; assert counter did NOT increment by the T0 count.
- **Expected outcome:** Counter value matches T4 count, not T0 count.
- **Determinism notes:** Determinism depends on the synthetic feature's invocation pattern; recommended that T6.1 design provides a deterministic NEEDS_REVISION trigger.

---

### T-AC-FR-6-b-per-phase-counter-at-T10 — `per_phase[<phase-id>]` increments at T10

- **Type:** structural-parse + behavioral
- **L:** L3
- **AC:** AC-FR-6-b
- **Task:** T6.3
- **Operator-facing:** Yes (conditional on NEEDS_RECONCILIATION inclusion)
- **Preconditions:** Synthetic test designed to trigger ≥1 NEEDS_RECONCILIATION cycle (Plan Open Item #3 surfaced this — conditional).
- **Steps:**
  1. Inspect `checkpoint.json.execution_pipeline_cycle_counters.per_phase`.
  2. Count `"transition": "T10"` entries in state-transitions.log.
  3. Assert per_phase counter == T10 count.
- **Expected outcome:** Counter == T10 count.
- **Open coverage gap:** If T6.1 design does NOT include a NEEDS_RECONCILIATION trigger, this test cannot run; surface to operator at T6.1 design time.
- **Determinism notes:** Conditional; flagged in coverage matrix as conditional.

---

### T-AC-FR-6-b-T0-T13-no-increment — T0 and T13 log entries do NOT cause counter increments

- **Type:** behavioral
- **L:** L3
- **AC:** AC-FR-6-b (I-AA-609 invariant 10)
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:**
  1. Count T0 entries: `T0_N=$(grep -c '"transition":[[:space:]]*"T0"' "$LOG")`
  2. Count T13 entries: `T13_N=$(grep -c '"transition":[[:space:]]*"T13"' "$LOG")`
  3. Compare cycle counters to T4/T10 counts (per the two tests above); assert counters do not include T0/T13 contributions.
- **Expected outcome:** Counter delta = T4 count + T10 count, with no contribution from T0/T13.
- **Determinism notes:** Static given the log.

---

### T-AC-FR-6-c-cycle-cap-halt — Counter reaches 4 → T13 TERMINATED + `escalation-cycle-cap.json` + user surface

- **Type:** behavioral
- **L:** L3
- **AC:** AC-FR-6-c
- **Task:** T6.3, T6.5
- **Operator-facing:** Yes (conditional on synthetic test designed to exhaust cycle cap; recommended to be exercised in T6.5 negative-path branch)
- **Steps:**
  1. Force or simulate a 4-cycle exhaustion in the synthetic test (T6.5 conditional task).
  2. Assert `checkpoint.json.execution_pipeline_state_transitions[-1].transition == "T13"`.
  3. Assert `escalation-cycle-cap.json` exists in the synthetic test's working directory.
  4. Assert the run halts (no further dispatches in the log).
- **Expected outcome:** All three assertions pass.
- **Open coverage gap:** Triggering cycle-cap requires a deliberate test design; surface to T6.1.
- **Determinism notes:** Conditional and gated by T6.1 design.

---

### T-AC-FR-6-c-no-silent-fallback — On verification failure, `verification-failed` posture surfaces

- **Type:** behavioral
- **L:** L3
- **AC:** AC-FR-6-c, AC-NFR-1-b
- **Task:** T6.5
- **Operator-facing:** Yes (only if T6.3 fails — conditional)
- **Steps:**
  1. If T6.3 fails (per any of the AC-FR-6-a/b verifications), assert `working/feature/<slug>/verification-failed.md` exists.
  2. Assert checkpoint.json records the failure mode explicitly.
  3. Assert NO log entries indicate a parent-driven workaround fallback (no entries with `mode: single-agent-fallback` post-failure).
- **Expected outcome:** Failure surfaced explicitly; no silent fallback.
- **Negative-path coverage:** This is the primary negative-path test for AC-NFR-1-b.

---

### T-AC-FR-6-d-no-new-subagents — Synthetic test feature authors NO new sub-agent files

- **Type:** grep (negation)
- **L:** L2
- **AC:** AC-FR-6-d
- **Task:** T6.1
- **Steps:**
  1. `find working/test-features/dispatch-mechanism-regression -type f -name '*.md' | xargs grep -lE '^---$' | xargs grep -lE 'doc_type.*sub-agent\|^tools:'` (negation: expect empty)
  2. Or simpler: `find working/test-features/dispatch-mechanism-regression -path '*/.claude/agents/*.md' | wc -l` (expect 0)
- **Expected outcome:** No new sub-agent files in the synthetic test feature artifacts — F-7 constraint vacuously satisfied.
- **Determinism notes:** Static.

---

### T-AC-FR-6-d-restart-task-documented — Plan T6.2 includes operator-facing restart instruction

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-6-d
- **Task:** T6.2
- **Steps:**
  1. `grep -A 5 -nE '^#### T6\.2' working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md | grep -iE 'restart.*session|fresh-session|restart your Claude'`
- **Expected outcome:** ≥1 match (the operator-facing restart instruction is present in the Plan).
- **Determinism notes:** Static.

---

### T-AC-FR-6-d-fresh-session-confirmed — Verification log records a fresh-session timestamp

- **Type:** file content check
- **L:** L2
- **AC:** AC-FR-6-d
- **Task:** T6.2, T6.4
- **Operator-facing:** Yes (operator records the restart)
- **Steps:**
  1. `VLOG=working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-log.md`
  2. `grep -iE 'fresh.session|session.restart|restart.*at:' "$VLOG"`
  3. The recorded restart timestamp must be later than the T3.6 commit's timestamp: `RESTART=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z' "$VLOG" | head -1); COMMIT_TS=$(git log -1 --format=%cI <T3.6-sha>); [[ "$RESTART" > "$COMMIT_TS" ]]`
- **Expected outcome:** Fresh-session timestamp present and chronologically after the bundled commit timestamp.
- **Determinism notes:** Operator-mediated; flake risk low if restart is required by checklist.

---

### T-AC-FR-7-a-verification-log-naming — verification-log.md names FR-6 as gating, FR-7 as confidence-check

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-7-a
- **Task:** T6.4
- **Steps:**
  1. `VLOG=working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-log.md`
  2. `grep -iE 'FR-6.*gating|FR-6 is gating|gating.*FR-6' "$VLOG"`
  3. If FR-7 performed: `grep -iE 'FR-7.*confidence.check|confidence check.*FR-7' "$VLOG"`
- **Expected outcome:** Step 2 returns ≥1 match; Step 3 returns ≥1 match if FR-7 performed (else N/A).
- **Determinism notes:** Static.

---

### T-AC-FR-8-a-adr-0045-exists — ADR-0045 exists with required linkages

- **Type:** file-existence + grep
- **L:** L1
- **AC:** AC-FR-8-a
- **Task:** T0.1
- **Steps:**
  1. `[ -f adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md ]`
  2. `grep -iE 'T-001|dispatch_supported|investigation' adrs/ADR-0045-*.md` (links to investigation finding)
  3. `grep -iE 'ADR-0044|option \(a\)|flatten' adrs/ADR-0045-*.md` (links to chosen §6 option)
- **Expected outcome:** All three return success.
- **Determinism notes:** Static.

---

### T-AC-FR-8-a-manual-review-interim — Manual-review interim doc with 4 required elements

- **Type:** grep
- **L:** L1
- **AC:** AC-FR-8-a
- **Task:** T5.2
- **Steps:**
  1. Locate the interim doc — either in the inventory artifact or at `working/feature/<slug>/adr-0045-manual-review-interim.md`.
  2. For each of the 4 elements (where, who, trigger, follow-on pointer), grep:
     - `grep -iE 'design-cc|design-composer|per-agent design' <doc>` (where)
     - `grep -iE 'shared-document-reviewer|review-architecture-auditor' <doc>` (who)
     - `grep -iE 'tools:.*array|PR.*sub-agent|adding.*tools' <doc>` (trigger)
     - `grep -iE 'follow-on|audit-machinery|audit extension|SA-13' <doc>` (follow-on pointer)
- **Expected outcome:** All four greps return ≥1 match.
- **Determinism notes:** Static.

---

### T-AC-NFR-1-a-end-to-end-complete — Synthetic test reaches T12 `pipeline_complete` without workaround fallback

- **Type:** behavioral
- **L:** L3
- **AC:** AC-NFR-1-a
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:**
  1. `LOG=working/test-features/dispatch-mechanism-regression/state-transitions.log`
  2. `grep '"transition":[[:space:]]*"T12"' "$LOG"`
  3. Assert `pipeline-run-summary.json` exists in the synthetic feature's working dir.
  4. Assert no log entry indicates parent-driven workaround fallback.
- **Expected outcome:** T12 present in log; summary exists; no fallback markers.
- **Determinism notes:** Depends on the synthetic feature's design.

---

### T-AC-NFR-1-b-explicit-failure-surface — Failure surfaced explicitly (no silent fallback)

- **Type:** behavioral
- **L:** L3
- **AC:** AC-NFR-1-b
- **Task:** T6.5
- **Operator-facing:** Yes (conditional)
- **Steps:** (duplicate of T-AC-FR-6-c-no-silent-fallback)
- **Expected outcome:** As above.
- **Determinism notes:** Conditional negative-path test.

---

### T-AC-NFR-2-a-log-per-dispatch — One state-transitions.log entry per specialist dispatch boundary

- **Type:** JSONL structural
- **L:** L3
- **AC:** AC-NFR-2-a (overlapping with AC-FR-6-a)
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:** As T-AC-FR-6-a-log-per-boundary; the AC overlaps and the test is shared.
- **Note:** This row exists for AC-coverage traceability; the implementation is the same as the FR-6-a test.

---

### T-AC-NFR-2-b-dispatcher-identity-preserved — Dispatcher identity preserved (none expected post-repair)

- **Type:** JSONL grep
- **L:** L3
- **AC:** AC-NFR-2-b
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:**
  1. Grep the log for any entries whose `invoking_agent` is the literal `"recipe-feature-pipeline"` rather than `"execute-orchestrator"`.
  2. Expect: zero such entries (per v1 logical-owner clarification).
- **Expected outcome:** Step 1 returns zero matches.
- **Note:** Distinguishability is preserved structurally; under the v1 invariant, all entries carry the logical owner.

---

### T-AC-NFR-3-a-counters-increment — Counters increment at task/phase boundaries

- **Type:** structural-parse
- **L:** L3
- **AC:** AC-NFR-3-a (overlapping with AC-FR-6-b)
- **Task:** T6.3
- **Operator-facing:** Yes
- **Steps:** As T-AC-FR-6-b-per-task-counter-at-T4 and T-AC-FR-6-b-per-phase-counter-at-T10.

---

### T-AC-NFR-3-b-cycle-cap-routes-via-reconciler — Cycle-cap halt routes through reconciler / emit-directive equivalent

- **Type:** behavioral
- **L:** L3
- **AC:** AC-NFR-3-b
- **Task:** T6.3
- **Operator-facing:** Yes (conditional on cycle-cap exhaustion)
- **Steps:**
  1. If cycle-cap exhausted: assert the last reconciler dispatch (or, under option (a), the parent's reconciler-dispatch + dispatch_directives[] consumption) preceded the T13.
  2. Assert escalation routed via the documented path (not a silent shortcut).
- **Expected outcome:** Routing visible in log.

---

### T-AC-NFR-4-a-finding-artifact — T-001 research note exists with `dispatch_supported: false` and stable identifier

- **Type:** file-existence + grep
- **L:** L1
- **AC:** AC-NFR-4-a
- **Task:** satisfied-upstream
- **Steps:**
  1. `[ -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md ]`
  2. `grep -E 'dispatch_supported:[[:space:]]*false' <path>`
  3. `grep -E 'T-001' <path>` (stable identifier present)
- **Expected outcome:** All three checks pass.
- **Determinism notes:** Static.

---

### T-AC-NFR-5-a-schema-reference-lockstep — Schema-reference change + schema field change in same commit set

- **Type:** git-log structural
- **L:** L2
- **AC:** AC-NFR-5-a
- **Task:** T1.1, T1.2, T1.3
- **Steps:**
  1. Identify the commit(s) that introduced `execution_pipeline_state_transitions` to SKILL.md: `git log -p -S'execution_pipeline_state_transitions' .claude/skills/recipe-feature-pipeline/SKILL.md`
  2. Assert this commit (or its commit set on the same branch) is the same as the commit that documents the field's semantics.
  3. There must not be a commit modifying `checkpoint.json` schema in any in-flight feature without a corresponding SKILL.md schema-reference update.
- **Expected outcome:** Commit-set check passes.
- **Determinism notes:** Static given git history.

---

### T-AC-NFR-6-a-in-flight-untouched — devcontainer-mcp-provisioning-r1 artifacts unmodified

- **Type:** git-diff
- **L:** L1
- **AC:** AC-NFR-6-a
- **Task:** T4.1 (the v1 invariant clarification must preserve in-flight artifact validity)
- **Steps:**
  1. `BASE=$(cat working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt | head -1)`
  2. `git diff --name-only ${BASE}..HEAD -- working/feature/devcontainer-mcp-provisioning-r1/` (expect empty)
- **Expected outcome:** No files under devcontainer-mcp-provisioning-r1/ modified.
- **Determinism notes:** Static.

---

### T-AC-NFR-6-b-new-schema-marked — `execution_mode` documented with both v1 values

- **Type:** grep
- **L:** L1
- **AC:** AC-NFR-6-b
- **Task:** T1.2, T4.2
- **Steps:**
  1. `grep -E 'single-agent-fallback' .claude/skills/recipe-feature-pipeline/SKILL.md`
  2. `grep -E 'specialist-isolation' .claude/skills/recipe-feature-pipeline/SKILL.md`
- **Expected outcome:** Both greps return ≥1 match (both v1 values for `execution_mode` documented as distinguishable).
- **Determinism notes:** Static.

---

### T-AC-NFR-7-a-synthetic-archived — Synthetic test feature archived under `working/test-features/`

- **Type:** file-existence
- **L:** L1
- **AC:** AC-NFR-7-a
- **Task:** T6.4
- **Steps:**
  1. `ls working/test-features/dispatch-mechanism-regression/` (or the path per T6.1)
- **Expected outcome:** Directory exists with the synthetic test feature artifacts (PRD / Blueprint / Plan / tasks.json present).
- **Determinism notes:** Static.

---

### T-AC-CC-1-adr-0034-absent-skill-md — `grep -c ADR-0034` on SKILL.md returns 0

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-1
- **Task:** T2.1
- **Steps:**
  1. `grep -c 'ADR-0034' .claude/skills/recipe-feature-pipeline/SKILL.md`
- **Expected outcome:** Returns `0`.
- **Determinism notes:** Static.

---

### T-AC-CC-1-adr-0034-absent-finalize — `grep -c ADR-0034` on execute-finalize-reconciler.md returns 0

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-1 (overlapping with AC-FR-5-a; explicit duplicate for AC coverage)
- **Task:** T3.3
- **Steps:**
  1. `grep -c 'ADR-0034' .claude/agents/execute-finalize-reconciler.md`
- **Expected outcome:** Returns `0`.
- **Determinism notes:** Static.

---

### T-AC-CC-1-adr-0033-present-skill-md — `grep -c ADR-0033` on SKILL.md returns ≥ 1

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-1
- **Task:** T2.1
- **Steps:**
  1. `N=$(grep -c 'ADR-0033' .claude/skills/recipe-feature-pipeline/SKILL.md); [ "$N" -ge 1 ]`
- **Expected outcome:** Exit 0.
- **Determinism notes:** Static.

---

### T-AC-CC-1-adr-0033-present-finalize — `grep -c ADR-0033` on execute-finalize-reconciler.md returns ≥ 3

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-1
- **Task:** T3.3
- **Steps:** (duplicate of T-AC-FR-5-a-adr-0033-ge-3; tested under both ACs for coverage traceability)
- **Expected outcome:** Returns ≥ 3.

---

### T-AC-CC-1-adr-0017-present — ADR-0017 cited in dispatch section

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-1
- **Task:** T2.1
- **Steps:**
  1. `awk '/Execution Phase Dispatch/,/^## /' .claude/skills/recipe-feature-pipeline/SKILL.md | grep -c 'ADR-0017'` ≥ 1
- **Expected outcome:** Within the dispatch section, ADR-0017 cited at least once.
- **Determinism notes:** Static.

---

### T-AC-CC-2-skill-md-lockstep — D-001 + D-004 land in the same commit set on SKILL.md

- **Type:** git-log structural
- **L:** L2
- **AC:** AC-CC-2
- **Task:** T1.1–T1.3 (D-004 schema closure); T2.1 (D-001 dispatch section)
- **Steps:**
  1. Identify D-004-related commits (touching SKILL.md lines 96–128 schema region): `git log -p --follow .claude/skills/recipe-feature-pipeline/SKILL.md | head -200`
  2. Identify D-001-related commits (touching Execution Phase Dispatch section): same file; same branch.
  3. Assert all D-001 + D-004 commits are on the feature branch with no intervening unrelated work.
  4. Assert D-004 commit-time ≤ D-001 commit-time (edit ordering per I-DR-004 absorption).
- **Expected outcome:** Lockstep verified; ordering correct.
- **Determinism notes:** Static given history.

---

### T-AC-CC-3-self-reference-rationale — execute-orchestrator.md contains explicit self-reference rationale

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-3
- **Task:** T3.2
- **Steps:**
  1. `grep -iE 'self-reference is intentional|self.reference.*load.bearing|recipe-feature-pipeline.*entry.*intentional' .claude/agents/execute-orchestrator.md`
- **Expected outcome:** ≥1 match (rationale paragraph present).
- **Determinism notes:** Static.

---

### T-AC-CC-3-self-reference-preserved — `skills:` array still contains `recipe-feature-pipeline`

- **Type:** YAML parse
- **L:** L2
- **AC:** AC-CC-3
- **Task:** T3.1
- **Steps:**
  1. Extract frontmatter from `.claude/agents/execute-orchestrator.md` and parse the `skills:` array.
  2. Assert `recipe-feature-pipeline` is present.
- **Expected outcome:** Present.
- **Determinism notes:** Static.

---

### T-AC-CC-4-malformed-directives-handling — SKILL.md documents malformed/empty `dispatch_directives[]` handling

- **Type:** grep
- **L:** L1
- **AC:** AC-CC-4
- **Task:** T2.2
- **Steps:**
  1. `awk '/Execution Phase Dispatch/,/^## /' .claude/skills/recipe-feature-pipeline/SKILL.md | grep -iE 'malformed|empty.*dispatch_directives|surface to user|cycle-cap.equivalent'`
- **Expected outcome:** ≥1 match describing the malformed/empty handling rule (user surface; cycle-cap-equivalent escalation; no silent fallback).
- **Determinism notes:** Static.

---

## AC coverage matrix

Every AC → tests that verify it. Bold tests are load-bearing (an AC's primary verification); others are duplicate / cross-AC coverage rows.

| AC | Verifying tests |
|---|---|
| AC-FR-1-a | **T-AC-FR-1-a-kb-gap-topic** |
| AC-FR-1-b | **T-AC-FR-1-b-finding-artifact** |
| AC-FR-1-c | **T-AC-FR-1-c-dispatch-supported-flag** |
| AC-FR-2-a | **T-AC-FR-2-a-no-kc1-posture** (vacuous-by-kc2 verification) |
| AC-FR-2-b | **T-AC-FR-2-b-progression-to-design** (vacuous-by-kc2) |
| AC-FR-2-c | **T-AC-FR-2-c-no-followon-stub** (vacuous-by-kc2) |
| AC-FR-3-a | **T-AC-FR-3-a-option-named** |
| AC-FR-3-b | **T-AC-FR-3-b-specialist-substantive-preserved** |
| AC-FR-3-c | **T-AC-FR-3-c-invariants-cited** |
| AC-FR-4-a | **T-AC-FR-4-a-inventory-cap** |
| AC-FR-4-b | **T-AC-FR-4-b-schema-lockstep** |
| AC-FR-4-c | **T-AC-FR-4-c-leaf-specialists-substantive** |
| AC-FR-5-a | **T-AC-FR-5-a-agent-removed-both**, **T-AC-FR-5-a-adr-0034-zero**, **T-AC-FR-5-a-adr-0033-ge-3**, **T-AC-FR-5-a-bundled-commit-message**, **T-AC-FR-5-a-bundled-commit-fileset**, **T-AC-FR-5-a-line-76-reframed** |
| AC-FR-5-b | **T-AC-FR-5-b-inventory-artifact**, T-AC-FR-5-b-sweep-counts, T-AC-FR-5-b-codebase-sweep-now-zero |
| AC-FR-6-a | **T-AC-FR-6-a-log-per-boundary**, T-AC-FR-6-a-invoking-agent-preserved |
| AC-FR-6-b | **T-AC-FR-6-b-per-task-counter-at-T4**, T-AC-FR-6-b-per-phase-counter-at-T10, T-AC-FR-6-b-T0-T13-no-increment |
| AC-FR-6-c | **T-AC-FR-6-c-cycle-cap-halt**, T-AC-FR-6-c-no-silent-fallback |
| AC-FR-6-d | T-AC-FR-6-d-no-new-subagents, T-AC-FR-6-d-restart-task-documented, **T-AC-FR-6-d-fresh-session-confirmed** |
| AC-FR-7-a | **T-AC-FR-7-a-verification-log-naming** |
| AC-FR-8-a | **T-AC-FR-8-a-adr-0045-exists**, T-AC-FR-8-a-manual-review-interim |
| AC-NFR-1-a | **T-AC-NFR-1-a-end-to-end-complete** |
| AC-NFR-1-b | **T-AC-NFR-1-b-explicit-failure-surface** (shared with T-AC-FR-6-c-no-silent-fallback) |
| AC-NFR-2-a | **T-AC-NFR-2-a-log-per-dispatch** (shared with T-AC-FR-6-a-log-per-boundary) |
| AC-NFR-2-b | **T-AC-NFR-2-b-dispatcher-identity-preserved** |
| AC-NFR-3-a | **T-AC-NFR-3-a-counters-increment** (shared with T-AC-FR-6-b-*) |
| AC-NFR-3-b | **T-AC-NFR-3-b-cycle-cap-routes-via-reconciler** |
| AC-NFR-4-a | **T-AC-NFR-4-a-finding-artifact** |
| AC-NFR-5-a | **T-AC-NFR-5-a-schema-reference-lockstep** |
| AC-NFR-6-a | **T-AC-NFR-6-a-in-flight-untouched** |
| AC-NFR-6-b | **T-AC-NFR-6-b-new-schema-marked** |
| AC-NFR-7-a | **T-AC-NFR-7-a-synthetic-archived** |
| AC-CC-1 | **T-AC-CC-1-adr-0034-absent-skill-md**, **T-AC-CC-1-adr-0034-absent-finalize**, **T-AC-CC-1-adr-0033-present-skill-md**, **T-AC-CC-1-adr-0033-present-finalize**, T-AC-CC-1-adr-0017-present |
| AC-CC-2 | **T-AC-CC-2-skill-md-lockstep** |
| AC-CC-3 | **T-AC-CC-3-self-reference-rationale**, T-AC-CC-3-self-reference-preserved |
| AC-CC-4 | **T-AC-CC-4-malformed-directives-handling** |

**Coverage status:** every AC has ≥ 1 verifying test. No orphan tests.

## Verification-layer summary

| L | Phase coverage | Tests at this layer |
|---|---|---|
| L1 (file-existence / grep / structural-parse) | Phases 0–5 | 33 tests |
| L2 (structural-parse / git-history / behavioral) | Phases 0–5 | 11 tests |
| L3 (end-to-end behavioral via synthetic test feature) | Phase 6 | 7 tests (all gated on T6.3 / T6.5) |

Per-phase L3 concentration:

- **Phase 0:** L1-only (3 tests via T0.1, T0.2, T0.3 — though T0.* tasks satisfy no ACs directly).
- **Phase 1:** L1 + L2 (schema documentation greps + lockstep check).
- **Phase 2:** L1 + L2 (dispatch section greps + ADR citation tests).
- **Phase 3:** L1 + L2 (frontmatter greps + bundled-commit structural tests).
- **Phase 4:** L1 + L2 (template extension folding greps).
- **Phase 5:** L1 (inventory artifact tests).
- **Phase 6:** L3 (the load-bearing end-to-end synthetic test feature run + operator-mediated fresh-session confirmation).

## Operator-facing tests

Tests requiring operator interaction (a fresh Claude Code session, manual invocation, or human confirmation of an out-of-band action):

| Test ID | Why operator-facing | Operator action |
|---|---|---|
| T-AC-FR-6-a-log-per-boundary | Synthetic test feature run requires invoking `/feature-pipeline` against the test feature | Restart session (T6.2), invoke `/feature-pipeline` against synthetic feature path, wait for run completion |
| T-AC-FR-6-a-invoking-agent-preserved | Same — depends on the synthetic run's log | (see above) |
| T-AC-FR-6-b-per-task-counter-at-T4 | Depends on synthetic run's checkpoint.json | (see above) |
| T-AC-FR-6-b-per-phase-counter-at-T10 | Same, conditional on NEEDS_RECONCILIATION inclusion | (see above) |
| T-AC-FR-6-b-T0-T13-no-increment | Same | (see above) |
| T-AC-FR-6-c-cycle-cap-halt | Requires deliberate cycle-cap exhaustion (T6.5 conditional) | Trigger the cycle-cap path; operator confirms halt + escalation file |
| T-AC-FR-6-c-no-silent-fallback | Triggers only on T6.3 failure (T6.5 conditional) | Operator confirms `verification-failed.md` is surfaced |
| T-AC-FR-6-d-fresh-session-confirmed | Operator must restart session between Phase 3 and Phase 6 | Restart, record timestamp in verification log |
| T-AC-NFR-1-a-end-to-end-complete | Synthetic test run | (see above) |
| T-AC-NFR-1-b-explicit-failure-surface | Same as T-AC-FR-6-c-no-silent-fallback | (see above) |
| T-AC-NFR-2-a-log-per-dispatch | Synthetic test run | (see above) |
| T-AC-NFR-2-b-dispatcher-identity-preserved | Synthetic test run | (see above) |
| T-AC-NFR-3-a-counters-increment | Synthetic test run | (see above) |
| T-AC-NFR-3-b-cycle-cap-routes-via-reconciler | Synthetic test + cycle-cap exhaustion path | (see above) |

**Operator-facing test count: 14 (all gated on the FR-6 verification run; 5 are conditional on either cycle-cap exhaustion or T6.3 failure).**

Additionally, **Stage-13 packager BLOCKER + waiver path** (T0.2) is operator-facing but does NOT have a dedicated AC test in this document because no AC ties to it (it's a known follow-on issue documented for the operator at run time, not a feature acceptance criterion). It surfaces here for operator-awareness completeness:

| Operator interaction | Reference task | Operator action |
|---|---|---|
| Stage-13 packager BLOCKER + waiver | T0.2 | Operator applies the waiver citing the Blueprint's ADR-0036 placement disposition |

## Bundled-commit invariant — dedicated tests

Per the orchestrator's special-discipline instruction, the bundled-commit invariant (T3.6 + AC-FR-5-a) is tested as follows:

| Aspect | Test ID | Mechanism |
|---|---|---|
| Commit message contains literal string | **T-AC-FR-5-a-bundled-commit-message** | `git log --grep` finds the SHA; `git log --format=%B -1 <sha> \| grep -F 'FR-5 sweep closure: affected set = 2'` |
| Single commit (not split) | **T-AC-FR-5-a-bundled-commit-fileset** | `git show --name-only --format= <sha>` returns exactly the 5 expected files in one commit |
| `Agent` removed from both files in same commit | T-AC-FR-5-a-agent-removed-both + bundled-commit-fileset (combined) | Combined L1 grep + L2 git-show |
| 3-occurrence ADR sweep in same commit | T-AC-FR-5-a-adr-0034-zero + adr-0033-ge-3 + bundled-commit-fileset (combined) | Combined L1 greps + structural test |

The bundled-commit invariant is the load-bearing test for D-001 / D-004 / Phase 3 same-file ordering discipline as well: the `git log --format=%cI` ordering check (T-AC-CC-2-skill-md-lockstep) confirms D-004 commits precede D-001 commits on the SKILL.md timeline.

## Test infrastructure required

**What the codebase already provides** (per codebase-analysis.json):

- `git` (commit history queries, diffs).
- Standard POSIX shell utilities (`grep`, `awk`, `find`, `wc`, `ls`, `cat`, `sort`).
- `python3` for YAML parsing (`yaml.safe_load`); already used by `auditing-shared/scripts/validate_pipeline_frontmatter.py`.
- The recipe-feature-pipeline parent skill itself (for the L3 synthetic test feature run).

**What needs to be authored** (per Plan T6.1):

- The synthetic minimal test feature directory tree under `working/test-features/dispatch-mechanism-regression/` (1 phase, 1–2 tasks, no new sub-agents per AC-FR-6-d vacuous-satisfaction posture).
- The verification log artifact (`working/feature/<slug>/verification-log.md`) populated post-T6.3.

**No new test framework dependencies.** The L1/L2 tests are deterministic shell one-liners; L3 tests are observation of the synthetic feature run's filesystem state. Per the Plan's resourcing posture, all tests are single-operator-executable.

## CI execution plan

This feature has no CI integration; the project does not use GitHub Actions for the `cc` layer. Test execution discipline:

- **Per-task validation (Phase Validator stage):** L1 + L2 tests for each task run immediately after the task's L3 verification per the Plan's L1/L2/L3 discipline. These are the workhorse tests; runtime is seconds-to-minutes.
- **Per-phase validation:** L2 tests (e.g., bundled-commit shape, schema-reference lockstep) run at phase completion.
- **Phase 6 only:** L3 synthetic test feature run; runtime is hours (operator-mediated, single execution).
- **Regression re-run:** The archived synthetic test feature (per NFR-7) is re-runnable for future dispatch-mechanism changes; the test inventory in this document is the regression checklist.

There is no nightly / pre-release CI cadence; the project is single-operator.

## Determinism and isolation commitments

Per Principle X of KB-general-coding-principles (deterministic assertions; AAA structure; fast feedback):

1. **All L1/L2 tests are deterministic.** Static filesystem reads and grep/git operations; no time-of-day dependency; no randomness.
2. **L3 tests have one source of non-determinism: the operator's available session time.** The synthetic test feature's dispatch sequence is deterministic given a stable harness; flake risk is limited to harness-level variability outside this feature's scope.
3. **No test mocks the harness, the sub-agents, or the parent skill.** The verification is structural for L1/L2 and end-to-end-real for L3, per Blueprint Test Boundaries section.
4. **Tests are isolated.** Each L1/L2 test depends only on the filesystem state after the named task; no test depends on another test's output.
5. **No test writes shared state.** All tests are read-only on the codebase and the synthetic run's artifacts.
6. **AAA structure:** every test block has explicit Preconditions (Arrange), Steps (Act), Expected outcome (Assert).
7. **No "should work" language.** Every Expected outcome is a concrete observable assertion (exit codes, grep counts, byte-level file existence, JSONL field values).

## Open coverage gaps

These gaps are surfaced explicitly per the test-acceptance-author discipline:

1. **AC-FR-6-b per-phase counter at T10 — conditional on NEEDS_RECONCILIATION inclusion.** Plan Open Item #3 already surfaces this: the synthetic test's recommended shape (1 phase, 2 tasks, minimal code work) does NOT necessarily exercise NEEDS_RECONCILIATION. If T6.1 design omits a NEEDS_RECONCILIATION trigger, T-AC-FR-6-b-per-phase-counter-at-T10 cannot run; AC-FR-6-b is then only partially verified (per_task half only). **Recommendation:** T6.1 design should include a forced NEEDS_RECONCILIATION step. Failing that, document the partial coverage explicitly in the verification log.

2. **AC-FR-6-c cycle-cap halt path — conditional on deliberate cycle-cap exhaustion.** The cycle-cap path requires the synthetic test to fail ≥ 4 cycles deliberately. If T6.1 design does not include such a trigger, T-AC-FR-6-c-cycle-cap-halt cannot run; the negative-path is then unverified. **Recommendation:** T6.5 conditional task is the relief valve; if T6.5 fires (because T6.3 hit a real failure), the cycle-cap path may be incidentally exercised. Otherwise, an additional synthetic test scenario is required.

3. **AC-FR-2-a/b/c — vacuous by kill-criterion-#2 firing.** Per the orchestrator's special discipline, these ACs are vacuously-satisfied because kc-#2 fired (not kc-#1). The tests above verify the absence of the trigger (no kc-#1 posture marker; no follow-on stub) and the presence of the alternative (kc-#2 posture marker in checkpoint.json). **This is a structural verification of vacuous satisfaction, not a behavioral test of the kc-#1 path.** The kc-#1 path is genuinely untestable in this run; if the operator wants behavioral coverage of kc-#1, a separate test feature simulating that branch would be required (out of scope per FR-2 design).

4. **AC-FR-1-a/b/c — satisfied-upstream by T-001.** Tests verify the T-001 research note artifact and its load-bearing flag, but the substantive verification ("did the Discovery investigation produce a finding that distinguishes harness restriction from one-flag-fix?") is artifact-based, not behavioral. **The actual investigative reasoning is not testable post-hoc beyond inspecting the cited evidence.**

5. **No test directly exercises the dispatch-matrix routing (D-2a/c/d, D-12, D-13, D-14).** These are preserved as load-bearing invariants per AC-FR-3-c; the tests verify they are CITED in the dispatch section but not that they ROUTE correctly. The synthetic test feature would have to be designed to exercise each routing branch; T6.1's minimal design does not. **Recommendation:** Document this as accepted partial coverage; the substantive routing logic is unchanged by this feature (per FR-3-b) and remains tested by its original ADRs.

6. **Stage-13 packager BLOCKER (T0.2) has no AC.** The known issue is operator-facing only; the waiver path is documented but not tested by any AC in this document. This is intentional — the Stage-13 packager defect is a separate follow-on and not a feature acceptance criterion.

## References

- PRD: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md`
- Blueprint v1.1.0: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md`
- Plan v1.1.0: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md`
- ADR-0044: `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md`
- ADR-0045: `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md`
- T-001 research note: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md`
- Codebase analysis: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json`
- KB references applied: `KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md`, `KB-general-coding-principles/SKILL.md` (deterministic-assertion + AAA discipline)

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | test-acceptance-author | Initial Acceptance Tests document derived from PRD v1.0.0, Blueprint v1.1.0, Plan v1.1.0. 54 tests (27 L1 + 14 L2 + 13 L3) covering 35 ACs. Special-discipline tests for vacuously-satisfied ACs (kc-#2 path), satisfied-upstream ACs (T-001), bundled-commit invariant (T3.6 commit message + fileset), and 3-occurrence ADR-0034 → ADR-0033 sweep. 14 operator-facing tests gated on Phase 6 synthetic test run. (Status-report claim of "51 tests / 30 ACs" was a counting error in the author's summary — actual inventory and per-test detail blocks consistently show 54 tests / 35 ACs.) |
| 1.0.1 | 2026-05-24 | parent-orchestrator-surgical-patch | I-CA-002 absorption: corrected Update History count (51→54 tests; 30→35 ACs); per-L-level counts now match actual inventory. |
