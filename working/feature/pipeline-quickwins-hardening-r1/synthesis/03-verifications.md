---
feature: pipeline-quickwins-hardening-r1
stage: synthesis
step: critique-audit-trail
generated: 2026-05-26T00:00:00Z
companion_to: 03-critique.json
---

# 03 — Verification audit trail

Pragmatic single-batch CoVe for a MINOR feature. ~20 highest-impact claims verified individually; remaining ~180 structural / file-path / line-number observations are passthrough-unverified per the orchestrator's scoping directive. See `03-critique.json` `passthrough_unverified.claim_ids_skipped` for the full list.

## Scope of this batch

Per orchestrator instructions, this batch focuses on:

1. **mcp-openapi-schema removal claims** — codebase-C-0038, C-0041, C-0103, C-0105, C-0110, C-0111, C-0112 (drives U-3)
2. **T-002 documentation-silence claims** — t002-C-0001, C-0002, C-0008 (drives FR-5 path shift; supersedes edge in graph)
3. **T-001 contract claims (incl. Swift divergence)** — t001-C-0001, C-0002, C-0003, C-0022, C-0033, C-0038 (drives FR-4 dry-run design)
4. **FR-2 scope_class hoisting** — codebase-C-0028, C-0029 (drives FR-2 design)
5. **FR-1 scope-sweep candidates** — codebase-C-0016, C-0017, C-0018, C-0019, C-0020 (drives U-1)

## Per-claim verification details

### codebase-C-0038 — `.mcp.json` has six servers today

**Verification questions:**
- Does `.mcp.json` at the repo root currently register exactly six servers?
- Are the six servers actionlint-mcp, context7, exa, gitnexus, serena, terraform-mcp (and only these)?

**Answers (from selective Grep / direct read of `/workspaces/feature-pipeline/.mcp.json`):**
- Yes — six entries under `mcpServers`.
- Yes — exactly those six keys; `mcp-openapi-schema` absent.

**Verdict:** verified | **Confidence:** high

Corroborated by CLAUDE.md line 9 (acknowledges 2026-05-24 removal) and postCreate.sh inline comment.

---

### codebase-C-0041 — ADR-0041 still has seven-row install-mechanism table including mcp-openapi-schema

**Verification questions:**
- Does ADR-0041 contain a per-server install-mechanism taxonomy table at Decision §1.b?
- Does the table still include a row for mcp-openapi-schema?

**Answers (from Grep `mcp-openapi-schema` on `/workspaces/feature-pipeline/adrs/ADR-0041-install-mechanism-hybrid.md`):**
- Yes — line 71: `| mcp-openapi-schema | npx -y (Node ephemeral via npm cache) | npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path> |`.
- Yes — that row is the seventh; the ADR table has not been amended.

**Verdict:** verified | **Confidence:** high

Direct on-disk evidence of the FR-3 day-one BLOCKER false-positive.

---

### codebase-C-0103 — postCreate.sh '5 OSS-local' references

**Verification questions:**
- Does postCreate.sh line 11 say '5 OSS-local servers'?
- Does postCreate.sh line 165 say '5 OSS-local servers'?

**Answers (from Read of postCreate.sh):**
- Partially — line 5 (header) says 'Installs the 5 OSS-local MCP servers'. Line 9 immediately follows with 'Servers installed here (4 — post-2026-05-24 postmortem; was 5)'.
- No — line 158 says 'installing 4 OSS-local MCP servers'; line 165 says 'OSS-local install pass complete' with no count.

**Verdict:** verified | **Confidence:** medium

Substance correct; cited line numbers (11, 165) are off by ~6 lines. Cosmetic-only severity assessment holds. Not load-bearing.

---

### codebase-C-0105 — U-3 day-one BLOCKER false-positive

**Verification questions:**
- Does ADR-0041 still list mcp-openapi-schema as one of seven rows?
- Does .mcp.json have six servers?
- Does AC-FR-3-c (parity rule) naturally flag this as day-one BLOCKER?

**Answers:**
- Yes — see codebase-C-0041.
- Yes — see codebase-C-0038.
- Yes — naive symmetric-difference audit between ADR-0041 table and .mcp.json flags mcp-openapi-schema as ADR-only. Per the severity taxonomy (codebase-C-0076/077), an ADR-config divergence is a BLOCKER by default.

**Verdict:** verified | **Confidence:** high

Centerpiece for U-3 framing.

---

### codebase-C-0110 — CLAUDE.md line 9 acknowledges removal + stale-doc framing

**Verification questions:**
- Does CLAUDE.md acknowledge mcp-openapi-schema was removed 2026-05-24?
- Does it frame KB-mcp-platform's reference as a stale-doc issue, not an active server?

**Answers (from the CLAUDE.md content present in the task context):**
- Yes — verbatim: 'mcp-openapi-schema was removed 2026-05-24 (see .devcontainer/postCreate.sh#L16). The KB-mcp-platform skill still references it as one of seven — that's a stale-doc issue, not an active server.'
- Yes — both halves match the claim.

**Verdict:** verified | **Confidence:** high

Establishes the project's stale-doc-tolerance posture; directly load-bearing for U-3 option (a).

---

### codebase-C-0111 — Stale-ADR-tolerance posture is established

**Verification questions:**
- Does the cited source show the project tolerating stale ADR/KB references coexisting with the live config?
- Is the posture recurring (established) rather than ad-hoc?

**Answers:**
- Yes — CLAUDE.md's explicit framing exemplifies the posture once.
- Cannot be inferred from a single instance. The claim generalizes from N=1.

**Verdict:** single_sourced | **Confidence:** medium

Over-confident-claim shape ('established'); downgraded. Framer should treat as 'project has shown willingness in one observed case', not 'pattern across many.'

---

### codebase-C-0112 — FR-3 should respect the stale-reference posture

**Verification questions:**
- Does this claim logically follow from C-0110 and C-0111?
- Is this a normative recommendation rather than a factual claim?

**Answers:**
- Yes — given the established (if N=1) posture, in-rule recognition is the consistent choice.
- Yes — normative; framer-facing guidance, not factual.

**Verdict:** verified | **Confidence:** high

Rests on C-0110/C-0111. Not load-bearing fact.

---

### codebase-C-0028 — scope_class read at line 350, Stage 12

**Verification questions:**
- Is scope_class read at line 350 of recipe-feature-pipeline SKILL.md?
- Is the read site inside 'Stage 12 (Deliverable Packaging)'?
- Is scope_class read anywhere else?

**Answers (from Grep `scope_class` on `.claude/skills/recipe-feature-pipeline/SKILL.md` + direct read):**
- Yes — line 350 reads `scope_class` from intent-clarification frontmatter.
- Partial mismatch — line 346 reads 'Step 14 — **Stage 13**: Deliverable Packaging (added in v4.5.0)'. The descriptor 'Deliverable Packaging' matches the claim; the stage NUMBER (13 vs. claim's 12) does not.
- No — `scope_class` appears at line 350 only. Single read site confirmed.

**Verdict:** verified | **Confidence:** medium

Line number + read-site uniqueness verified. Stage number is a minor inaccuracy. Framer: cite line number, not stage number, in the design frame.

---

### codebase-C-0029 — FR-2 self-check needs scope_class earlier; design-claude-code must hoist or add second read

**Verification questions:**
- Is FR-2's self-check semantically required at the start of dispatch?
- Does design-claude-code own this decision under U-2?

**Answers:**
- Yes — the PRD/intent framing for FR-2 places the self-check at orchestrator entry, well before Stage 13. The single existing read site at line 350 is too late.
- Yes — codebase-analysis-report assigns U-2 to design-claude-code.

**Verdict:** verified | **Confidence:** high

Load-bearing for FR-2 design.

---

### codebase-C-0016 — execute-task-quality-handler exists and is a STRONG FR-1 candidate

**Verification questions:**
- Does `.claude/agents/execute-task-quality-handler.md` exist?
- Does it issue per-task quality verdicts (verdict + findings)?

**Answers (from Read of the agent file):**
- Yes — file exists at the cited path.
- Yes — line 12: 'You issue per-task quality verdicts'; YAML description + Contract 1 confirm verdict+findings emission.

**Verdict:** verified | **Confidence:** high

---

### codebase-C-0017 — Agent emits {APPROVED, NEEDS_REVISION, STUB_DETECTED, BLOCKER} with findings array

**Verification questions:**
- Does the agent emit the four-status enum?
- Does findings have domain, severity, source_activity, file_path, locator, message?

**Answers:**
- Yes — line 33 of the agent: `"status": "APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER"`.
- Mostly — lines 34-44 confirm domain, severity, source_activity, file_path, message, dispatch_hint, depth_level. **'locator' is NOT a field**; actual extras are dispatch_hint + depth_level.

**Verdict:** verified | **Confidence:** high

Minor extraction inaccuracy ('locator' fabricated). Substance correct.

---

### codebase-C-0018 — APPROVED + severity:blocker contradiction can occur today

**Verification questions:**
- Can the agent emit APPROVED with a blocker-severity finding structurally?
- Does the agent's contract prevent this contradiction today?

**Answers:**
- Yes — status enum and findings array are independent fields in the JSON contract.
- No — the verdict-logic section orders the checks but no post-hoc parity validator is present.

**Verdict:** verified | **Confidence:** high

Substantiates execute-task-quality-handler inclusion in FR-1 sweep. Strong case for U-1.

---

### codebase-C-0019 — finalize-deliverable-packager exists, is a MODERATE FR-1 candidate

**Verification questions:**
- Does `.claude/agents/finalize-deliverable-packager.md` exist?
- Does it emit a verdict in the FR-1-relevant shape?

**Answers:**
- Yes.
- Yes — line 81: `"verdict": "PASS|BLOCK|REVIEW"`.

**Verdict:** verified | **Confidence:** high

---

### codebase-C-0020 — Packager verdict + chained reviewer_findings from doc_type:DeliverableArchive

**Verification questions:**
- Does the packager emit {PASS, BLOCK, REVIEW}?
- Are reviewer_findings chained from a doc_type:DeliverableArchive invocation of shared-document-reviewer?

**Answers:**
- Yes — line 81.
- Yes — line 87 shows `reviewer_findings: [...]`; line 122-125 context confirms BLOCKER/MAJOR/MINOR pass-through; shared-document-reviewer line 352 confirms doc_type:DeliverableArchive path.

**Verdict:** verified | **Confidence:** high

Substantiates the 'redundant FR-1 check' concern in U-1.

---

### t001-C-0001 — versions.env line 36 pins GITNEXUS_TAG=1.6.5

**Verification questions:**
- Does .devcontainer/versions.env line 36 pin GITNEXUS_TAG=1.6.5?
- Is the research note's citation correct?

**Answers:**
- Yes — confirmed by codebase-C-0048 (independent codebase audit reads the same line).
- Yes — research note and codebase audit agree.

**Verdict:** verified | **Confidence:** high (two-source consistent)

---

### t001-C-0002 — Env-var contract is implemented by two scripts

**Verification questions:**
- Does the research note cite scripts/build-tree-sitter-{dart,proto}.cjs as implementation?
- Does the note cite a verifiable upstream URL?

**Answers:**
- Yes — F-1 (dart) and F-2 (proto) of the note.
- Yes — raw URLs at https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/scripts/build-tree-sitter-{dart,proto}.cjs.

**Verdict:** verified | **Confidence:** high

Single-sourced upstream-citation; counter-verification would require fetching upstream raw files (out of scope this batch).

---

### t001-C-0003 — Strict `=== '1'` comparison

**Verification questions:**
- Does the note assert strict `=== '1'` semantics?
- Specific line numbers (dart 9, proto 28-34)?

**Answers:**
- Yes — F-1 quotes 'Strict `=== '1'` only' from dart comment line 7.
- Yes — F-1 (line 9 dart); F-2 (lines 28-34 proto).

**Verdict:** verified | **Confidence:** high

Drives the DM-4 calibration step (verify `=0`/`=true` still triggers rebuild).

---

### t001-C-0033 — Signal 1 (stderr-prefix) is positive observable

**Verification questions:**
- Does signal 1 appear in the research note's recommended observable signals?
- Is the literal-string fragility risk acknowledged?

**Answers:**
- Yes — Synthesis section.
- Yes — DM-1 (t001-C-0040) recommends regex pattern instead of full literal.

**Verdict:** verified | **Confidence:** high

---

### t001-C-0022 — README/code divergence on Swift

**Verification questions:**
- Does the GitNexus README claim env-var skips Swift?
- Does the actual code only skip Dart + Proto?

**Answers:**
- Yes — F-4 documents the README claim.
- Yes — F-1/F-2 cite only dart + proto in postinstall hook.

**Verdict:** verified | **Confidence:** high

This is an INTERNAL divergence within GitNexus (README vs code) — handled inside the research note, not a dissent between this critique's source-set.

---

### t001-C-0038 — Dry-run must NOT assert Swift via env-var

**Verification questions:**
- Does the note recommend the dry-run avoid Swift assertions via env-var?
- Is the basis the README/code divergence at v1.6.5?

**Answers:**
- Yes — Synthesis 'On Swift' bullet explicit recommendation.
- Yes — same bullet cites the divergence.

**Verdict:** verified | **Confidence:** high

Drives FR-4 design.

---

### t002-C-0001 — Canonical docs silent on `claude mcp list` exit code

**Verification questions:**
- Does the note assert silence on exit-code contract?
- Are the upstream URLs cited?
- Is silence demonstrated by contrast with documented sibling commands?

**Answers:**
- Yes — Executive summary + Finding 1.
- Yes — cli-reference and mcp pages cited.
- Yes — Findings 3-5 contrast with documented `claude auth status` / `daemon status` / `ultrareview` exit-code language.

**Verdict:** verified | **Confidence:** high

Drives FR-5 path shift; supersedes edge in graph (`claude mcp list` → `claude --bare -p` SDK-event).

---

### t002-C-0002 — Canonical docs silent on `claude mcp list` stdout format

**Verification questions:**
- Does the note assert silence on stdout format?
- Is this distinct from the exit-code silence?

**Answers:**
- Yes — Finding 2: no output example, no --json mention, no status-token vocabulary.
- Yes — Findings 1/3 (exit code) and Finding 2 (stdout) are independently established silences.

**Verdict:** verified | **Confidence:** high

---

### t002-C-0008 — Workflow depending on `claude mcp list` exit code depends on undocumented behavior

**Verification questions:**
- Does the note draw this conclusion?
- Is it grounded in silence + contrast finding?

**Answers:**
- Yes — Finding 1 paragraph 4 explicit.
- Yes — grounded in the silence demonstrated by contrast.

**Verdict:** verified | **Confidence:** high

Load-bearing for FR-5 path shift.

---

## Adversarial probes (where applied)

- **codebase-C-0105 (U-3 false-positive):** "Who benefits from this being true?" — No vendor; the audit naturally surfaces this regardless. Adversarial probe does not undermine.
- **codebase-C-0111 (stale-ref posture is established):** "What would falsify this?" — A second case where the project did NOT tolerate stale refs (e.g., forced ADR amendment for some removed entity) would falsify the 'established' framing. None found in this batch's sources; hence single_sourced + confidence:medium.
- **t002-C-0001 (silence is meaningful):** "What does silence on adjacent points imply?" — The researcher explicitly addresses this in Findings 3-5 by contrast with sibling commands. The silence-as-finding framing is defensible because the docs ARE comprehensive on adjacent commands.
- **t001-C-0022 (README/code divergence on Swift):** "Who benefits from this being true?" — The upstream maintainers would prefer the README be accurate; the divergence is documented in issue #1024 (closed not-planned). No incentive for upstream to overstate. Conclusion: divergence is real, not framed.

## Dissent findings

None. The graph's `conflicts_with` edges (e.g., E-0086 README → E-0076 env-var contract on Swift; E-0029 mcp-openapi-schema → E-0027 .mcp.json) are INTERNAL to a single source's analysis (research note documents the README/code divergence; codebase audit documents the ADR/.mcp.json divergence). These are NOT cross-source dissent — they're carefully recorded internal contradictions that the design must resolve. The framer surfaces them as design questions (U-3 for the .mcp.json divergence; FR-4 design for the Swift divergence), not as dissent between independent observers.

## Constraint violations

None. The feature has no hard_constraints in scope that any verified claim violates. (Manifest constraints not separately consulted as no `00-manifest.json` is present in the run path — the codebase-audit + research notes self-declare the relevant NFRs and are consistent with them.)

## Passthrough-unverified notes for the framer

The 180 passthrough claims are structural / file-path / line-number observations that the codebase-audit report and research notes record for traceability. They are:

- **Probably correct.** They cite specific file paths and line numbers, and the spot-checks done in this batch (C-0028 line 350 stage label, C-0017 'locator' field) suggest the extractor has a low but non-zero rate of small inaccuracies (~1 per 10 verified). Framer should not treat passthrough claims as load-bearing for any decision; design-X agents will read the live files directly when implementing.
- **Pragmatically out of scope.** They do not drive the open design decisions (U-1..U-8). Full CoVe over all 201 would have cost ~10x more orchestrator cycles for no decision-making payoff.

## Notable calibration downgrades summary

| Claim | Downgrade | Reason |
|---|---|---|
| codebase-C-0103 | confidence: medium | Cited line numbers 11, 165 are off by ~6 lines; substance correct |
| codebase-C-0017 | (still high) | 'locator' field is fabricated; actual fields are dispatch_hint + depth_level. Doesn't change verdict |
| codebase-C-0028 | confidence: medium | Stage number (12 vs. file's 13) mismatch; line number correct |
| codebase-C-0111 | verdict: single_sourced | Generalizes from N=1 observation |
