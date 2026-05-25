---
id: SYN-issue-capture-mechanism-r1
doc_type: synthesis
version: 1.0.0
status: draft
feature_slug: issue-capture-mechanism-r1
derived_from:
  - working/feature/issue-capture-mechanism-r1/04-decision-frames.json
  - working/feature/issue-capture-mechanism-r1/codebase-analysis.json
  - working/feature/issue-capture-mechanism-r1/codebase-analysis-report.md
  - working/feature/issue-capture-mechanism-r1/prd-v2.md
  - working/feature/issue-capture-mechanism-r1/intent-clarification.md
  - Issues/issue-capture-mechanism/proposal.md
  - /home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md
generated: 2026-05-23T20:00:00Z
generated_by: synth-synthesizer
companion_artifacts:
  - working/feature/issue-capture-mechanism-r1/prd-v2.md
  - working/feature/issue-capture-mechanism-r1/04-decision-frames.json
---

# Synthesis: Issue-Capture Mechanism (Outside-the-Pipeline)

## Executive Summary

This run designs an outside-pipeline mechanism for the sole user (Josh-S-N2M) to capture out-of-current-scope issues into `Issues/<topic-slug>/<doctype>.md` without polluting active feature-pipeline runs. The feature is a multi-primitive subsystem: a new agent (`issue-capture-author`), two new skills (`KB-issue-capture`, `capture-issue`), a new PreToolUse hook on `Task`, three new doctype templates, a backward-compatible validator extension, and a one-time migration of four flat `Issues/*.md` files plus the agent-roster-impact-matrix file (PRD §Overview; FR-1 through FR-15).

This run is itself the **dogfood test** of one of its own design decisions: `intake-intent-clarifier` was seeded by `Issues/issue-capture-mechanism/proposal.md` as `--raw-request`, the proposal body was treated as authoritative prior context, and only 7 ambiguities required user confirmation (intent-clarification.md §Initial Interpretation; F-013, F-014). The mechanism the pipeline is now designing is the same mechanism that bootstrapped this very run — a fact load-bearing for D-14 and validating in advance.

The headline Discovery finding is **F-003 (BLOCKER risk averted)**: skills declared `disable-model-invocation: true` are SILENTLY DROPPED from sub-agent `skills:` preload lists per the Claude Code platform contract (auditing-subagents/references/subagent-spec.md line 110, audited by auditing-cc-configs cross_file_checks.py X3). Both new skills carry that flag — so the `issue-capture-author` agent CANNOT list them in its `skills:` frontmatter. D-01 resolves this with a runtime Read/Glob pattern in the agent body (mirroring the cc-critique structural template; CP-001). Two further high-risk constraints attend the design: this run introduces the project's **first hook** in `.claude/hooks/` and the **first hooks block** in `settings.json` (F-002 — no in-project precedent to template from), and `validate_pipeline_frontmatter.py` is a 3-hop transitive dependency of every artifact in every pipeline run, so the FR-7 extension carries pipeline-wide blast radius (F-012, NFR-8).

The decision shape per-layer designers must consume is **14 decision frames** across 6 classes: 3 architecture, 2 mechanism, 2 naming, 5 validation, 1 lifecycle, 1 integration (decision-frames §framing_summary). Three are high-blast-radius (D-02, D-10, D-11 — each touching the hook or validator that fires on every pipeline operation); three are low-reversibility (D-01, D-10, D-13 — each making structural commitments that compound over time). Eight are high-reversibility and contained-blast — safe to try, easy to undo. A separate 7-item ADR slate (PRD U-10) routes to design-composer at Stage 7 for canonical decision-record authorship per FR-5 (the feature-pipeline rule that only design-composer authors ADRs).

## Single-source Synthesis Note

**This is a streamlined single-source synthesis.** Zero external research topics were authorized (the proposal + planning-mode plan supplied ~80% of the elicitation, per intent-clarification.md §Clarifying Questions; the remaining design questions are codebase-bound). Consequently this run did NOT execute the typical multi-source synthesize-skill pipeline (synth-extractor, synth-grapher, synth-critic, synth-substrate-mapper). The substantive Discovery deliverable is `codebase-analysis.json` / `codebase-analysis-report.md` produced by `discovery-codebase-researcher` (16 findings F-001..F-016; 7 convention patterns CP-001..CP-007; 4 verbatim extracts VE-001..VE-004; validator-extension-surface enumeration).

**Implications:**

1. **Confidence calibration is 0.5 baseline, 0.6 for high-quality codebase claims** (those backed by multiple file citations or verbatim extracts: F-001, F-002, F-003, F-008, F-012, VE-003, VE-004). All RICE confidence values across the 14 decision frames sit in [0.5, 0.6] per decision-frames §notes.
2. **Citation invariant (B-cite) is satisfied differently than in multi-source mode**: every assertion here cites F-NNN / CP-NNN / VE-NNN / FR-NN / NFR-NN / U-NN / D-NN — these are the artifact identifiers from this run's Discovery + PRD + framer outputs, not external sources.
3. **Constraint propagation (B-constr)** is the PRD's hard constraints (multi-primitive scope, FULL scope class, FR-5 prohibition on ADR authorship outside design-composer, FR-13 pipeline-isolation invariant, NFR-8 backward compatibility); each is explicitly addressed in §Constraints Honored.
4. **ADR-recording at Stage 7 canonicalizes the load-bearing decisions** (per PRD U-10 + FR-5). This synthesis surfaces ADR subjects but does NOT author ADR text. Stage 7's design-composer will use the 7-item slate from decision-frames §adr_slate_routing as input.
5. **Per-decision dissent is absent** in this synthesis — single-source synthesis cannot surface cross-source disagreement (there are no other sources to disagree). Where the codebase analysis or the PRD itself surfaced internal tension (notably the planning-mode plan's 3-state-vs-5-state inconsistency resolved at intent-clarification.md Q3), the resolution is recorded against the user-confirmed default rather than as ongoing disagreement.

## Findings Consolidated

The 16 codebase findings, 7 convention patterns, and 4 verbatim extracts cluster into five themes by relevance to design.

### Theme 1: First-of-kind constraints (drives D-01, D-02, D-11, D-12)

This run introduces three firsts in the project (F-001, F-002): the first SKILL.md files to declare `disable-model-invocation: true`; the first `.claude/hooks/` directory; the first `hooks` block in `settings.json`. There is no in-project worked example to template against. The most consequential cross-file constraint is **F-003**: skills with `disable-model-invocation: true` cannot be preloaded into a sub-agent's `skills:` field; the platform silently drops them and the deterministic check at `auditing-cc-configs/scripts/cross_file_checks.py` X3 (line 410) raises a BLOCKER. This finding alone restructures the architectural answer for D-01 — runtime Read/Glob in the agent body, not a `skills:` declaration.

### Theme 2: Validator architecture & extensibility (drives D-05, D-06, D-10)

`validate_pipeline_frontmatter.py` is 422 lines of pure-stdlib Python with a hand-rolled YAML parser (F-008, VE-002, VE-004). Three doc-type categories exist today — GATED (5 values), ANALYSIS (15 explicit + 6 suffix patterns), ADR (single) — at lines 38-68. Dispatch is path-based at lines 365-371. F-012 explicitly recommends the FR-7 extension as a fourth `issue` category branch inside `validate_pipeline_artifact`. VE-003 confirms the current ADR-0005 superseded-by enforcement at lines 314-323 — the pattern D-05's per-state companion-field rules mirror. CP-007 confirms `feature_slug` is universal-required per ADR-0032 Change 4.

### Theme 3: Sibling-script convention discipline (drives D-02, D-07, D-09)

CP-002 documents the auditing-shared script idiom: stdlib-only Python, argparse, JSON-stdout, observer-only-default exit codes, stderr discipline (`<script_name>: <reason>` prefix). CP-005 documents the `permissions.allow` entry shape (`Bash(python3 .claude/skills/.../scripts/*.py:*)`). CP-006 documents the smoke-test harness pattern (`smoke_test_auditing_shared.py`). VE-002 captures the canonical finding-dict shape. Together these convention patterns prescribe how the new hook script, validator extension, and observability log should be shaped to match existing project idiom rather than invent a new one.

### Theme 4: Empirical precedent for doctype shapes (drives D-04, FR-6)

CP-004 confirms three distinct body shapes across the four pre-migration `Issues/*.md` files: register (tabular sweep), analysis (TL;DR + numbered evidence), proposal (prose + adoption guidance). CP-003 confirms doc_type frontmatter drift in those four files (pre-migration values: deferral-register, analysis ×2, proposal — none matching the new canonical enum). F-005 enumerates the four files; F-009 confirms they are all at `status:draft` pending FR-8 back-fill to `status:open`. F-006 confirms two existing `proposes_future_feature:` precedents with divergent slug formats (one suggested-format, one fixed-format) — the basis for D-06's advisory-not-mandatory recommendation.

### Theme 5: Pipeline-isolation invariant baseline (drives FR-13, AC-FR-13-a/b)

F-010 and F-015 record three independent literal greps performed at 2026-05-23T18:55Z against HEAD commit cf48e5e: `grep -r "KB-issue-capture"`, `grep -r "issue-capture-author"`, `grep -r "capture-issue"` against `.claude/agents/` and against the entire `.claude/` tree (excluding `working/` and `Issues/`). All three returned zero matches. The pipeline-isolation invariant (FR-13) is currently satisfied at zero-baseline; design must preserve it. test-acceptance-author can encode the exact grep commands as direct acceptance assertions.

### Verbatim extracts of design-time relevance

- **VE-001** captures the verbatim intra-pipeline 4-state vocabulary from `KB-review-disciplines/references/issue-lifecycle.md` (with the ADR-0005 superseded-by enforcement). This is the canonical text the design-composer must cite when authoring the ADR distinguishing the new 5-state issues vocabulary from the existing 4-state ledger.
- **VE-002** captures the canonical finding-dict shape from `validate_pipeline_frontmatter.py` — the make_finding signature the FR-7 extension must reuse verbatim.
- **VE-003** captures the current GATED_DOC_TYPES, ANALYSIS_DOC_TYPES, and ADR enforcement structure — the patterns D-10's Option 1 mirrors.
- **VE-004** captures the current path-dispatch at lines 365-371 — the structure D-10 preserves unchanged.

## Decision Framing

This section presents the 14 decision frames in numeric order, each with the recommended option, rationale, PRD cross-references, and routing. **High blast-radius decisions (D-02, D-10, D-11)** are flagged with the "design-phase rigor required" marker; **low-reversibility decisions (D-01, D-10, D-13)** are flagged "get this right or pay later." D-10 carries both markers — it is the single most load-bearing decision in this run.

---

### **D-01: Skill-loading mechanism for `issue-capture-author`** *(low-reversibility — get right or pay later)*

Question: how does the `issue-capture-author` agent load `KB-issue-capture` content given that `disable-model-invocation: true` skills are silently dropped from sub-agent `skills:` preloads (F-003)?

**Recommended option:** Runtime Read/Glob in agent body — frontmatter omits `skills:` entirely (mirroring cc-critique precedent CP-001); the agent body's procedure section uses Read/Glob to load `.claude/skills/KB-issue-capture/SKILL.md` and its `references/*.md` at runtime.

**Rationale:** The only option that preserves all three enforcement layers (FR-3 / PRD §Product Policy row 5). Sidesteps the silent-drop BLOCKER (F-003) at the structural level — the constraint cannot be violated because no `skills:` entry exists. Matches the closest existing agent template (cc-critique, CP-001).

**PRD cross-references:** FR-3 AC-FR-3-a; NFR-4 (the agent-body sequence governs over in-context instructions).

**Risks:** Reading skill files at runtime burns context tokens at every spawn vs. skill-system caching (mitigated: KB is small, ~4 reference files). Single-source claim base — F-003 derives from the auditing-subagents spec; no executable test in-project demonstrates the silent-drop yet.

**Routed to:** design-claude-code.

---

### **D-02: PreToolUse hook stdin/stdout schema and exit semantics** *(high blast-radius — design-phase rigor required)*

Question: what is the hook's stdin event schema, stdout JSON response shape, exit-code semantics, and error/log destination?

**Recommended option:** Bash script + jq, JSON stdin event → JSON stdout permissionDecision. Hook at `.claude/hooks/intercept-issue-capture-agent.sh`. Reads stdin JSON via jq, branches on `tool_input.subagent_type`: equals `issue-capture-author` → emit `permissionDecision: "ask"` with spawn-prompt preview; else emit `permissionDecision: "allow"`. Errors (missing jq, malformed stdin) → stderr log + emit `allow` + exit 0 (fail-open per NFR-2). All paths exit 0.

**Rationale:** Lowest startup cost (best chance of meeting AC-NFR-1-a's ~100ms target); minimal dependencies (bash + jq are devcontainer-standard); single-file is easy to audit; matches sibling auditing-shared stderr discipline (CP-002). Python and Node variants were rejected on startup cost (~50-200ms cold start risks the fast-path target on a hook that fires every Task spawn).

**PRD cross-references:** FR-3 AC-FR-3-b, AC-FR-3-c; NFR-1; NFR-2 AC-NFR-2-a/b.

**Risks:** Hook fires on EVERY Task spawn (~30-100 per pipeline run; NFR-1); a regression breaks ~28 pipeline agents (PRD §Risks #1). PRD Assumption 2 (subagent_type lives in tool_input field) is unverified in-project — design must verify against live Claude Code platform docs. First hook in the project (F-002); cc-critique pre-merge findings will be load-bearing (PRD U-5).

**Routed to:** design-claude-code.

---

### **D-03: AskUserQuestion approval prompt structure**

Question: what is the exact text/structure of the WHY/WHAT/WHERE approval prompt — and the 4 fixed options (Approve / Approve-with-edits / Change-doctype / Cancel)?

**Recommended option:** Structured rubric in `KB-issue-capture/references/approval-prompt-rubric.md` codifying four prompt-archetypes: (a) create-mode WHY/WHAT/WHERE; (b) update-mode OLD→NEW diff; (c) filename-collision re-prompt (supersede/rename/cancel); (d) evolution-transaction (both-files preview + single Approve).

**Rationale:** Skill-localised (KB-cc-design Principle 1) — discipline lives in KB-issue-capture, not the agent body. Four archetypes cover FR-1, FR-2, FR-5, NFR-5 flows. Allows wording polish without agent-file edits. intent-clarification.md §What's in scope already names approval-prompt-rubric.md as one of the four KB-issue-capture reference files — this decision finalizes its internal structure.

**PRD cross-references:** FR-1 AC-FR-1-b; FR-2 AC-FR-2-a; FR-4 AC-FR-4-d; FR-5; NFR-4; NFR-5 AC-NFR-5-a; U-2.

**Risks:** Prompt wording is itself a UX surface; this recommendation is structural (where + shape), not final wording. Design-claude-code must verify that Claude Code's AskUserQuestion 4-option maximum matches PRD's 4 named options.

**Routed to:** design-claude-code.

---

### **D-04: Doctype-to-precedent pairing in examples.md**

Question: which of the four migrated `Issues/*.md` files demonstrates which doctype in `KB-issue-capture/references/examples.md` (post-rename: register / analysis / proposal → issue-register / issue-analysis / issue-proposal)?

**Recommended option:** 1:1 pairing — three examples (one per doctype): register → `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`; analysis → `Issues/per-agent-design-evaluation-gap/analysis.md` (richest evidence + drives FR-9 evidence/ subdirectory demonstration); proposal → `Issues/auditing-family-graduation-review/proposal.md`. Cite `Issues/adr-placement-rootcause/analysis.md` as second-of-set without re-rendering.

**Rationale:** Each doctype gets exactly one canonical exemplar; all four migrated files are referenced; the chosen analysis simultaneously demonstrates the FR-9 evidence/ subdirectory pattern. CP-004 confirms analyses share one shape — two exemplars would dilute structural signal.

**PRD cross-references:** FR-6 AC-FR-6-a; FR-8 AC-FR-8-a; FR-9 AC-FR-9-a; U-3.

**Risks:** examples.md must use POST-migration paths and POST-rename doc_type values — must be authored AFTER FR-8 migration (or paired write in the same change-set). Single-source: design-claude-code should read both analyses before pairing.

**Routed to:** design-claude-code.

---

### **D-05: Per-state required-companion-field rules**

Question: for each of the 5 terminal/lifecycle states (`draft`, `open`, `adopted`, `complete`, `superseded`, `wontfix-with-rationale`), which companion frontmatter fields are mandatory vs. optional?

**Recommended option:** Minimal-mandatory per state with one back-link field per terminal state:
- `draft`: id, version, doc_type, feature_slug, generated, generated_by (universal).
- `open`: draft set + `since`.
- `adopted`: open set + `adopted_by_feature_slug`.
- `complete`: open set + `completed_in_feature_slug`.
- `superseded`: open set + `superseded_by_issue_id` (parallels current ADR-0005 enforcement at validator lines 314-323; VE-001 / VE-003).
- `wontfix-with-rationale`: open set + `wontfix_rationale` (free-text).
- `proposes_future_feature`: advisory on issue-proposal (see D-06).
- `escalates_from` / `escalated_to`: optional; present only when FR-5 evolution has occurred.

**Rationale:** Mirrors existing ADR-0005 superseded_by enforcement — no new dispatch mechanism, just new field names. Each terminal state has exactly one back-link field — symmetric and learnable. Aligns with migration back-fill plan (intent-clarification.md Q6: `status:open` + `since`).

**PRD cross-references:** FR-7 AC-FR-7-c; CP-007; VE-001; U-4.

**Risks:** Single-source on field names: design-backend should verify `adopted_by_feature_slug` / `completed_in_feature_slug` against ADR-0032-related conventions before locking. Once mandated, these fields are structurally one-way (deserves an ADR slot, see ADR slate item 7).

**Routed to:** design-claude-code + design-backend.

---

### **D-06: `proposes_future_feature` enforcement posture**

Question: is `proposes_future_feature:` validator-enforced (presence required) or advisory on the `issue-proposal` doctype?

**Recommended option:** Advisory `info`-severity finding on absence; do not block. If present, accept any string value (no format enforcement).

**Rationale:** Honors both existing precedents (F-006: one uses suggested-slug format, one uses fixed-slug). Adds a forward-pointer signal without coercion. Aligns with sibling-script idiom (CP-002 — observer-only default, info-level findings). Easy to upgrade later if real-world use shows the field becomes load-bearing. The two existing precedents pass either way — strictness gains no immediate value.

**PRD cross-references:** FR-7; U-6.

**Risks:** If future FRs assume `proposes_future_feature:` is reliably present (e.g., auto-derived `adopted_by_feature_slug` per D-05), this advisory posture leaves a gap — mitigated by D-05 making `adopted_by_feature_slug` independently mandatory on adopted state.

**Routed to:** design-backend.

---

### **D-07: Hook test strategy**

Question: what is the test strategy for the new PreToolUse hook — shellcheck, bash harness, golden-file dry-run, integration test, or some combination?

**Recommended option:** Layered — (a) `shellcheck` as pre-merge lint (zero warnings); (b) golden-file test harness piping 4-5 canonical stdin JSON events through the hook and diffing stdout (cases: issue-capture-author spawn → ask; non-issue spawn → allow; malformed JSON → allow + stderr; missing field → allow + stderr; empty stdin → allow + stderr); (c) one integration smoke test invoking `/capture-issue dummy` end-to-end during acceptance phase. Unit harness at `.claude/hooks/test_intercept_issue_capture_agent.{sh,py}`, mirroring smoke_test_auditing_shared.py (CP-006).

**Rationale:** Three layers map cleanly to NFR-1 (lint catches syntax), NFR-2 (golden-file covers fail-open), AC-FR-3-b/c (integration covers real-spawn path). No new dependencies. Sub-100ms unit-test loop. bats-style was rejected as new dependency; integration-only rejected because fail-open branches cannot be exercised from outside Claude Code.

**PRD cross-references:** FR-3 AC-FR-3-b/c; NFR-1; NFR-2 AC-NFR-2-a/b; NFR-8 AC-NFR-8-b; U-7.

**Risks:** Golden-file format is tied to D-02's stdin/stdout schema; schema changes invalidate goldens. Integration smoke requires a working Claude Code session — gating behind "manual acceptance" rather than CI is acceptable per recipe-feature-pipeline hard exclusions.

**Routed to:** test-acceptance-author + plan-author.

---

### **D-08: Update-mode idempotency mechanism**

Question: how does `/capture-issue --update <path>` detect a no-op (idempotency)?

**Recommended option:** Frontmatter-state-diff. Update-mode flow: read file; parse current frontmatter; draft proposed new frontmatter (apply transition per D-05); diff current vs. proposed; if empty, report "no change" and exit without AskUserQuestion or Write; else present OLD→NEW preview. Body content not compared (FR-5 audit-trail discipline: body is not mutated by status transitions).

**Rationale:** Matches the actual mutation surface — status transitions and FR-5 evolution touch frontmatter only. No false-positives from body whitespace. Cheap. Naturally extends to FR-5 transactional case (independent diffs on both files; both-empty ⇒ no-op). File-hash equality was rejected (false-positives from non-canonical YAML re-serialization); status-field-only diff rejected (misses companion-field back-fills and the FR-5 escalated_to: addition with no status change).

**PRD cross-references:** FR-2; FR-5; NFR-3 AC-NFR-3-a; NFR-6; U-8.

**Risks:** If D-05's per-state companion-field rules change between runs, old files may diff against new rule set — design-claude-code should specify that the proposed-frontmatter is computed against the LIVE D-05 rules.

**Routed to:** design-claude-code.

---

### **D-09: Observability log destination**

Question: where does observability logging (write-path + user's selected option) go?

**Recommended option:** stderr + project-relative JSONL log at `.claude/logs/capture-issue.jsonl`. Every approved write emits: (a) one human-readable stderr line (`capture-issue: wrote <path> (user selected: <option>)`); (b) one JSONL line with structured fields `{ts, path, option, mode, topic_slug, doctype}`. Matches `log_state_transition.py`'s append-only JSONL pattern. JSONL append failure → stderr-only with stderr warning.

**Rationale:** Matches sibling-script precedent (CP-002); separates the log from any pipeline `working/` directory (matches FR-13 isolation invariant); stderr provides immediate session-tail visibility; JSONL enables post-hoc analysis. Creating `.claude/logs/` is additive and zero-blast-radius.

**PRD cross-references:** NFR-7 AC-NFR-7-a; FR-13; U-9.

**Risks:** New directory `.claude/logs/` may flag in auditing-settings / auditing-cc-configs — mitigated by additive documentation in `.claude/SETTINGS-NOTES.md` per FR-15. `.gitignore` semantics for the JSONL file need a plan-stage decision (recommend gitignore: logs are session-local).

**Routed to:** design-claude-code.

---

### **D-10: Validator extension architecture** *(high blast-radius AND low-reversibility — design-phase rigor required AND get right or pay later)*

Question: what is the shape of the `validate_pipeline_frontmatter.py` extension — fourth `issue` category branch, separate dispatch on path prefix, or a separate validator file?

**Recommended option:** Fourth `issue` category branch inside `validate_pipeline_artifact` (F-012 recommendation). Add `ISSUE_DOC_TYPES = {'issue-register', 'issue-analysis', 'issue-proposal'}`, `ISSUE_STATES = {'draft', 'open', 'adopted', 'complete', 'superseded', 'wontfix-with-rationale'}`, and `validate_issue_artifact(fm, path)` checking doc_type ∈ ISSUE_DOC_TYPES, status ∈ ISSUE_STATES, and per-state companion-field rules per D-05. Outer path dispatch at lines 365-371 unchanged. Reuses `make_finding` (VE-002) verbatim.

**Rationale:** Matches existing per-category dispatch pattern (GATED / ANALYSIS / ADR — VE-003) — cohesive with the codebase's mental model. Outer path dispatch (VE-004) preserved exactly — zero risk to skill/agent validation paths. Backward compatibility (AC-FR-7-b, NFR-8) trivially preserved. Path-based dispatch was rejected (location is not the right discriminator; doc_type is). Separate validator file was rejected (doubles caller surface; PRD §Dependencies names `validate_pipeline_frontmatter.py` SINGULAR as the extension target).

**PRD cross-references:** FR-7 AC-FR-7-a through AC-FR-7-d; NFR-8 AC-NFR-8-a/b.

**Risks:** **HIGHEST BLAST RADIUS in the run.** 3-hop transitive: every artifact in every pipeline run validates through shared-document-reviewer's Gate 0 → validate_pipeline_frontmatter.py → this extension. NFR-8 regression-test is load-bearing — **design-backend MUST capture the pre/post regression corpus baseline BEFORE implementing the extension** and treat ANY new finding on a pre-existing pipeline doc_type as a regression. Per-state companion-field rules (D-05) should live in a dedicated module-level constant for testability.

**Routed to:** design-backend.

---

### **D-11: Hook latency threshold finalization** *(high blast-radius — design-phase rigor required)*

Question: what is the concrete hook-latency threshold for AC-NFR-1-a (currently `~100ms` deferred per U-11)?

**Recommended option:** Confirm ~100ms; measure at design time on the standard devcontainer; ratify if achieved. Process: (a) run the bash + jq hook (per D-02) 1000 times against synthetic stdin events; (b) measure p50/p95/p99; (c) if p95 ≤ 100ms, ratify AC-NFR-1-a unchanged; (d) if p95 ∈ (100ms, 200ms], replace AC-NFR-1-a with the measured p95; (e) if p95 > 200ms, escalate to design-iteration (revisit D-02 — possibly different language or pre-warmed daemon).

**Rationale:** Empirical; tied to actual implementation. p95 is the standard performance-test metric. 200ms ceiling matches user-perceptible-latency rule of thumb. Provides a clear escalation path back to D-02 if implementation fails. Lower-threshold (50ms) rejected as speculative without baseline; removing-threshold rejected as undoing PRD I-DR-003 deliberate split.

**PRD cross-references:** NFR-1 AC-NFR-1-a/b/c; U-11.

**Risks:** If p95 > 200ms, design-iteration triggers — D-02's Option 2 (Python) and Option 3 (Node) were rejected partly on this risk; if bash also fails, design-claude-code must propose a new option. No in-project benchmark exists yet (F-002).

**Routed to:** design-claude-code.

---

### **D-12: First-of-kind audit-trail placement**

Question: where does the "first hook in the project" audit trail live (F-001/F-002 — first SKILL.md with `disable-model-invocation: true`, first `.claude/hooks/` directory, first `hooks` block in settings)?

**Recommended option:** Three-surface audit trail —
1. `.claude/SETTINGS-NOTES.md` append per FR-15 (settings-level change history).
2. ADR (one of the U-10 seven, "three-layer enforcement") authored by design-composer at Stage 7 (architectural rationale).
3. `KB-issue-capture/references/non-pollution-contract.md` cites the ADR and notes the `disable-model-invocation` flag is the project's first.

**Rationale:** Each surface plays its existing audit role — SETTINGS-NOTES.md is the settings-level change history; ADR is the decision record; KB reference is discipline content. FR-15 already mandates the SETTINGS-NOTES append (this just specifies content). U-10 already mandates the ADR slate (this just enriches one ADR with first-of-kind context). Cross-references are bidirectional. CHANGELOG.md at repo root was rejected (PRD §Won't Have forbids new root-level rules surfaces; KB-cc-design Principle 1 — audit content lives where the change lives).

**PRD cross-references:** FR-15 AC-FR-15-a; U-10.

**Risks:** Three surfaces means three places to keep in sync — mitigated because "first-of-kind" is a static fact after this run lands.

**Routed to:** design-claude-code + design-composer.

---

### **D-13: Migration commit shape (FR-8 + FR-9)** *(low-reversibility — get right or pay later)*

Question: should FR-8 migration of doc_type values happen atomically with `git mv` or as a separate frontmatter back-fill commit?

**Recommended option:** Single atomic commit per file (or as a small commit-group): `git mv` + frontmatter back-fill (doc_type rename + status:open + since: + version:0.1.0) in one commit. Cross-references in PRD/proposal updated in the same commit. FR-9's agent-roster-impact-matrix is included trivially (no doc_type change).

**Rationale:** `git log --follow` preserves history through move-with-edit at default similarity-index. Validator (post-FR-7) sees migrated files in final canonical state from commit 1 — no intermediate-state validation failures. No referrer-stale window. Matches PRD AC-FR-8-c semantics (validator-clean post-back-fill). The two-step alternative was rejected (introduces transient invalid states; cross-reference staleness; AC-FR-8-c framing does not anticipate).

**PRD cross-references:** FR-8 AC-FR-8-a/b/c/d; FR-9 AC-FR-9-a/b; CP-003; F-005; F-009.

**Risks:** Git's move-detection heuristic may classify a content-changing move as delete+add if similarity falls below threshold — design-claude-code (FR-8 owner) should verify with a dry-run `git mv && edit && git diff -M` that detection holds. If not, fall back to `git mv`-then-edit two-commit sequence ACKNOWLEDGED as explicit risk-mitigation.

**Routed to:** design-claude-code.

---

### **D-14: Proposal-as-prior-context surface in `intake-intent-clarifier`**

Question: when `intake-intent-clarifier` detects `doc_type: issue-proposal` in `--raw-request` (FR-11), how does it surface "no re-elicitation needed" vs. "partial re-elicitation needed" to the orchestrator and user at Stage 1?

**Recommended option:** Procedure-section edit (~15 lines per FR-11 scope): add a "Phase 0 — Detect proposal seed" branch to the agent procedure with a documented missing-fields checklist (FRs, NFRs, EARS ACs, 9-layer scope, stakeholder table, scope class per ADR-0023, success posture). The checklist lives in `intent-clarification-template.md` per FR-12's edit, not in the agent body (avoids drift). Phase 1 retains current behavior for non-proposal raw-requests.

**Rationale:** F-013 confirms the signature already supports this (no signature change required). F-014 confirms the template Source section is structurally ready. **This very run's intent-clarification.md is the validating example** — its Clarifying Questions table is the exact pattern (~80% elicitation work supplied by proposal; 7 ambiguities required user confirmation). Signature-level edit rejected (exceeds FR-11/FR-12 scope; unnecessary).

**PRD cross-references:** FR-10 AC-FR-10-a; FR-11 AC-FR-11-a/b; FR-12 AC-FR-12-a/b; F-013; F-014.

**Risks:** If a future proposal's body has gaps the checklist doesn't anticipate (e.g., a wholly new section), the intent-clarifier would silently miss them — mitigated by Stage 1's existing Gate 1 confirmation (user reviews intent-clarification before approval).

**Routed to:** design-claude-code.

---

## ADR Slate

Seven ADR-worthy subjects (PRD U-10) routed to **design-composer at Stage 7** for canonical authorship. This synthesis does NOT author ADR text per FR-5. The slate (from decision-frames §adr_slate_routing):

1. **Per-issue folder model** — `Issues/<topic-slug>/<doctype>.md` with fixed canonical doctype filenames. Ratifies PRD FR-4; PRD §Product Policy Decisions row "Doctype preservation".
2. **Three doctypes preserved as distinct** (register / analysis / proposal), not unified. Ratifies PRD §Product Policy row 3; CP-004.
3. **Add-new-file evolution pattern** — never mutate older doctype's state; bidirectional `escalates_from` / `escalated_to`. Ratifies PRD FR-5; PRD §Product Policy row 4.
4. **Three-layer enforcement** — `disable-model-invocation` + agent-body `AskUserQuestion` + PreToolUse hook. Ratifies PRD FR-3; D-01; D-02; D-03; F-001 + F-002 first-of-kind.
5. **Prior-context handoff via existing `--raw-request`** — no new stage, no gate skip. Ratifies PRD FR-10; FR-11; FR-12; D-14; F-013.
6. **Structural-vs-discipline KB split inside `KB-documentation-criteria`** — templates here; triggering discipline in `KB-issue-capture`. Ratifies PRD FR-6; FR-14; D-03's option-1 placement of approval-prompt-rubric.md inside KB-issue-capture.
7. **5-state vocabulary distinct from intra-pipeline 4-state ledger** — `draft → open → adopted | complete | superseded | wontfix-with-rationale`; never share IDs with `issues-ledger.json`. Ratifies PRD FR-7; PRD §Product Policy row 2; D-05; VE-001 parallels-but-distinct relationship to ADR-0008.

**Placement constraint:** All 7 ADRs land in `/workspaces/feature-pipeline/adrs/` per ADR-0036. They MAY cite ADR-0008 in its current `adrs/` location per F-004 (this run does NOT migrate ADR-0008; out of scope per PRD §Risks #2).

## Per-layer Design Routing

The 14 decisions partition across the two activated layers (Claude Code primary, Backend secondary per PRD Layer Scope):

**design-claude-code (12 decisions):** D-01, D-02, D-03, D-04, D-05 (shared with design-backend), D-07 (shared with plan-author / test-acceptance-author), D-08, D-09, D-11, D-12 (shared with design-composer), D-13, D-14.

**design-backend (3 decisions):** D-05 (shared with design-claude-code), D-06, D-10.

**design-composer (Stage 7, ADR authorship):** the 7-item ADR slate above + D-12's ADR surface.

**Mapping summary by decision class:**
- All 3 **architecture** decisions (D-01, D-10) and the 1 **lifecycle** decision (D-13) sit at the layer boundary — D-01 + D-13 to design-claude-code, D-10 to design-backend.
- All 2 **mechanism** decisions (D-02 hook, D-08 idempotency) → design-claude-code.
- All 2 **naming** decisions (D-04 examples-pairing, D-12 audit-trail) → design-claude-code (D-12 shared with design-composer).
- The 5 **validation** decisions split: D-03 + D-09 + D-11 → design-claude-code; D-06 + D-10 → design-backend; D-05 → shared.
- The 1 **integration** decision (D-14) → design-claude-code.
- D-07 (validation, hook test strategy) is the only decision NOT routed to a design-* agent — it is consumed by **plan-author** + **test-acceptance-author** at Stages 6/7.

## Open Items Propagated to Plan / Test Stages

The following items require specific Plan-stage or Test-stage attention beyond per-layer Design:

- **D-07 (hook test strategy) → plan-author + test-acceptance-author.** The three test layers (shellcheck lint + golden-file unit + integration smoke) must each map to a plan step and an acceptance test. Plan-author must decide unit-harness language (bash vs. Python) and golden-file storage path; test-acceptance-author must encode the 4-5 canonical stdin events as test fixtures.
- **F-010 / F-015 / FR-13 AC-FR-13-a/b → test-acceptance-author.** The three pipeline-isolation greps are deterministic and trivially executable — encode verbatim as direct acceptance assertions. The zero-baseline established at 2026-05-23T18:55Z (HEAD cf48e5e) is the regression anchor.
- **D-10 + NFR-8 → test-acceptance-author + test-phase-validator-author.** The validator-extension regression-corpus baseline MUST be captured BEFORE the FR-7 extension is implemented (codebase-analysis-report §Closing Notes). The acceptance assertion: re-run validator pre/post against the existing-pipeline corpus; diff findings; expect zero new lines.
- **D-11 → plan-author + test-acceptance-author.** The hook-latency measurement (1000-iteration p50/p95/p99 on the standard devcontainer) is itself a plan-stage execution step AND its result ratifies/replaces AC-NFR-1-a. Test-acceptance-author needs to know which threshold value to assert against — it's whatever design-claude-code records as the ratified threshold.
- **D-13 → plan-author.** The `git mv && edit && git diff -M` dry-run for FR-8 + FR-9 migration is a plan-stage verification step; record the result in the plan before executing the real migration.
- **AC-FR-3-b/c integration smoke (D-07 layer c) → test-acceptance-author.** The end-to-end `/capture-issue dummy` invocation is the only test that exercises the hook through real Claude Code — it cannot run in pre-merge CI gates (per recipe-feature-pipeline hard exclusions; no automated gate beyond the 6 human gates). Gating behind manual acceptance is acceptable.
- **NFR-7 AC-NFR-7-a (per I-DR-004 inline note) → test-acceptance-author.** Defer destination-specific assertion wording until D-09 is closed by design-claude-code. The load-bearing assertion ("a record exists") is testable independently of destination.
- **U-5 (pre-merge cc-critique / auditing-* findings) → phase-quality-reviewer.** Likely surface: missing exit-code documentation, allowed-tools scoping, description routing, additive-change phrasing. Pre-stage all four auditing-* skill checks (auditing-hooks, auditing-skills, auditing-subagents, auditing-settings) as L1/L2/L3 verification per intent-clarification.md §Other open items.

## Constraints Honored

The PRD's hard constraints (PRD §Technical Considerations / Constraints; FR-5; FR-13; NFR-8) and the run's structural invariants are addressed as follows:

- **FR-5 — only design-composer authors ADRs.** This synthesis surfaces the 7-item ADR slate (PRD U-10) and lists their subjects, but contains no ADR text. ADR authoring is routed to design-composer at Stage 7. The ADR slate's `ratifies_decisions` field is preserved verbatim from decision-frames §adr_slate_routing.
- **FR-13 — pipeline-isolation invariant.** No recommendation in this synthesis introduces a `KB-issue-capture` reference into any `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md` agent or causes any pipeline sub-agent to invoke `issue-capture-author`. The zero-baseline confirmed at F-010 / F-015 is the invariant; AC-FR-13-a and AC-FR-13-b encode the structural check.
- **NFR-8 — validator backward compatibility.** D-10's recommendation (fourth `issue` category branch, no change to outer path dispatch) trivially preserves existing GATED/ANALYSIS/ADR doc_type flows. The synthesis explicitly names the regression-corpus baseline-capture step (§Open Items D-10 entry) as a precondition for the FR-7 implementation.
- **PRD §Won't Have — no new CLAUDE.md or `.claude/rules/` at repo root.** D-12's audit-trail placement (Option 1) explicitly rejected the CHANGELOG.md-at-root alternative on this basis. No recommendation in this synthesis touches repo-root files beyond what PRD scope allows (the four migration cross-references at PRD § and proposal §).
- **PRD §Won't Have — no edit to recipe-feature-pipeline beyond FR-12's one-bullet documentation.** FR-12 AC-FR-12-b is upheld in the recommendations for D-14 (signature-level edit was rejected explicitly because it would exceed this scope).
- **PRD §Won't Have — no deletion of any `Issues/*.md` file, including terminal-state ones.** D-08 (idempotency) and D-13 (migration commit shape) both operate by transformation; no deletion path is recommended.
- **PRD §Won't Have — no automated cross-link between `Issues/*.md` and `issues-ledger.json`.** D-05's per-state companion fields (`adopted_by_feature_slug`, `completed_in_feature_slug`) point at feature-pipeline slugs; they do NOT point at ledger entries. The two systems remain disjoint as Recipe-and-PRD demand.
- **PRD §Constraints — must operate within Claude Code's tool inventory.** All recommendations use only Read, Grep, Glob, Write, AskUserQuestion, Task (per `tools:` declaration in CP-001 template and PRD §What's in scope agent frontmatter).
- **Scope class FULL per ADR-0023.** This is a multi-primitive subsystem touching .claude/agents/, .claude/skills/ (3 new skills), .claude/hooks/ (new dir), .claude/settings.json, KB-documentation-criteria/references/templates/ (3 new), validate_pipeline_frontmatter.py, plus 4 file migrations. The 7-ADR slate matches the scope-class expectation.

## Limitations of This Synthesis

- **Single-source.** Zero external research topics authorized; this synthesis derives entirely from the codebase analysis, the PRD, the intent clarification, the seed proposal, and the planning-mode plan. No external community precedent (e.g., other Claude Code projects' hook implementations, MADR template variations) was sampled. The dogfood framing partially mitigates this — the proposal + plan supplied ~80% of the elicitation, so the synthesis surface is small. But the absence of external precedent means design-stage validation against the live Claude Code platform docs (PRD Assumption 2) and against cc-critique pre-merge findings (PRD U-5) is load-bearing.
- **No synth-extractor / synth-grapher / synth-critic / synth-substrate-mapper ran.** Per single-source pipeline contract. Consequently this synthesis does NOT contain claim-cluster IDs, entity-graph clusters, or substrate-registry citations. The ADR provenance footers authored by design-composer at Stage 7 will cite this synthesis's decision-frame IDs (D-NN) rather than claim-cluster IDs.
- **Confidence calibration is 0.5 baseline / 0.6 for high-quality codebase claims.** This is per decision-frames §notes — single-source claims, even when backed by verbatim extracts, carry lower confidence than multi-source corroboration would. Three decisions sit at the 0.5 floor (D-02, D-05, D-07, D-11) on the basis that PRD Assumption 2 is unverified in-project, the field names are project-novel, and no measurement baseline exists. Design-stage verification against live platform docs is the recommended uplift path.
- **PRD Assumption 2 unverified in-project.** F-016 records: KB-cc-platform/extensions.md documents the general PreToolUse hook contract but does not explicitly demonstrate `tool_input.subagent_type` inspection inside a Task-tool hook. D-02's recommendation depends on this assumption; design-claude-code should verify against live Claude Code platform docs before implementation.
- **No in-project benchmark for hook latency.** F-002 — first hook in the project. D-11's threshold ratification requires a design-stage measurement step; no historical baseline exists.
- **The four pre-migration `Issues/*.md` files were not exhaustively read for shape-equivalence.** D-04's Option 1 designates `Issues/per-agent-design-evaluation-gap/analysis.md` as the canonical analysis exemplar on the basis of "richest evidence" (codebase-analysis-report Group B), but this judgment was not independently validated against `adr-placement-rootcause/analysis.md`. Design-claude-code should read both before locking the pairing in `examples.md`.
- **No dissent_evidence pairs surfaced.** Single-source synthesis has no cross-source disagreement surface. The one internal tension (planning-mode plan's 3-state-vs-5-state inconsistency) was resolved at Gate 1 (intent-clarification.md Q3 — 5-state confirmed); not recorded as ongoing disagreement.
- **No decision was assigned `recommended_option: null`.** All 14 frames carry a concrete recommendation. This is appropriate for a streamlined single-source synthesis where the proposal + plan supplied the design surface; if downstream design-stage review uncovers a recommendation the substrate cannot support, it would be raised as a design-stage iteration rather than re-opened here.

## Provenance and Cross-references

**Input artifact chain:**

| Artifact | Generated by | Role in synthesis |
|---|---|---|
| `Issues/issue-capture-mechanism/proposal.md` | Josh-S-N2M (manual) | Seed proposal (doc_type: issue-proposal) |
| `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md` | Josh + Claude (planning mode) | ~400-line design plan (companion artifact) |
| `working/feature/issue-capture-mechanism-r1/intent-clarification.md` | intake-intent-clarifier | 7 confirmed defaults; user_token approved-2026-05-23T16:51:00Z |
| `working/feature/issue-capture-mechanism-r1/prd-v2.md` | intake-prd-author | 15 FRs, 9 NFRs, 11 Undetermined Items; status: draft v1.1.0 |
| `working/feature/issue-capture-mechanism-r1/codebase-analysis.json` + `codebase-analysis-report.md` | discovery-codebase-researcher | 16 findings, 7 convention patterns, 4 verbatim extracts, validator-extension-surface |
| `working/feature/issue-capture-mechanism-r1/04-decision-frames.json` | synth-framer | 14 decision frames across 6 classes; 7-item ADR slate routing |
| `working/feature/issue-capture-mechanism-r1/synthesis.md` (this file) | synth-synthesizer | This document |

**Forward consumers (Stage 6+):**

- **design-claude-code (Stage 5/6):** consumes D-01, D-02, D-03, D-04, D-07 (shared), D-08, D-09, D-11, D-12 (shared), D-13, D-14; produces `claude-code-design.md`.
- **design-backend (Stage 5/6):** consumes D-05 (shared), D-06, D-10; produces `backend-design.md`.
- **design-composer (Stage 7):** consumes the 7-item ADR slate + D-12; produces 7 ADRs in `/workspaces/feature-pipeline/adrs/`.
- **plan-author (Stage 7/8):** consumes D-07 (shared), D-11, D-13; produces `plan.md`.
- **test-acceptance-author (Stage 7/8):** consumes D-07 (shared), D-10 (regression baseline), D-11, F-010 / F-015 (pipeline-isolation greps), AC-NFR-7-a deferral note; produces `acceptance-tests.md`.
- **phase-quality-reviewer / cc-critique (pre-merge):** consumes U-5 pre-staging note; runs auditing-hooks, auditing-skills, auditing-subagents, auditing-settings.

**Cross-references — out-of-scope items (informational only, do NOT raise as findings):**

- F-004: ADR-0008 lives at `adrs/ADR-0008-issue-ledger-scope.md`; explicitly out-of-scope for this run per PRD §Risks #2 and intent-clarification.md.
- Issues/analysis-adr-placement-rootcause.md: separate analysis precedent; cited only as "second analysis in the precedent set" per D-04 Option 1.
- `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md`: migrated per FR-9; not a decision surface.

**Run metadata:**

- Pipeline run ID: `issue-capture-mechanism-r1`
- Synthesis generated: 2026-05-23T20:00:00Z
- Generated by: `synth-synthesizer` (compose-report mode; streamlined single-source variant)
- Predecessor synthesis: none
- HEAD commit at synthesis time: cf48e5e (per F-010 / F-015 grep verification timestamp)
