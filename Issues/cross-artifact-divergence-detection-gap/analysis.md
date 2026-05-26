---
id: ANALYSIS-cross-artifact-divergence-detection-gap
version: 1.0.0
doc_type: issue-analysis
status: open
since: 2026-05-24
feature_slug: pipeline-wide
generated: 2026-05-24
generated_by: claude (orchestrator) — dogfood authoring during issue-capture-mechanism-r1 Phase 1 post-review
# --- Per-state companion fields for status: open (per issue-doctypes-spec.md §4) ---
# since: 2026-05-24  (the date the open state was first set; required for status: open)
# --- Optional cross-link fields (per ADR-0046; partial adoption 2026-05-25 — analysis remains open) ---
# escalates_from: <none — this is the root analytical capture of the unified pattern>
escalated_to: PROPOSAL-cross-artifact-divergence-detection-gap
# Note: the sibling proposal carves out only the quick-wins subset (verdict-vs-findings consistency,
# single-agent fallback ban for full features, .mcp.json↔install-taxonomy parity rule, GitNexus
# install smoke test, CI mcp-list smoke test). The remaining hardening (design-realization audit,
# cross-file invariant catalog, reachability handshake, drift detection, per-agent design discipline)
# is deferred to a follow-on proposal for a separate feature run, so this analysis stays open.
# rolled_into_register: <none — no register absorbs this analysis>
---

# Cross-Artifact Divergence Detection Gap — gates check artifacts in isolation, not in relation

## Contents

- [x] TL;DR
- [x] Background / Evidence
- [x] Root Cause
- [x] Implications
- [x] Recommendations / Open Questions
- [x] Cross-links

## TL;DR

The feature pipeline's automated gates verify that each artifact is **internally consistent**
(parseable frontmatter, valid table, no forbidden phrases, etc.) but do not verify that
**related artifacts agree with each other**. Two recent failures are instances of the same
systemic gap: (1) the `issue-capture-mechanism-r1` Phase 1 spec contradicted its sibling
templates on the ID-derivation rule and still passed PV-1; (2) the `devcontainer-mcp-provisioning-r1`
feature shipped a configuration where 5 of 7 MCP servers were broken because ADR-prescribed
invocation strings never got compared against `.mcp.json` and the "hard-gate" audit was a
paper tiger. The PV-1 case was caught by human post-phase review before downstream damage;
the MCP case shipped and required forensic recovery. The pattern is the same. The hardening
recommendations from the MCP postmortem (especially H3 — design-realization audit dimension —
and H5 — verdict invariant validation) are the canonical fix; this analysis adds the
phase-validator-tier observation that PV-1 has the identical gap at smaller scope.

---

## Background / Evidence

### §1 — PV-1 spec-vs-templates §7 divergence (2026-05-24)

Full evidence: `evidence/pv1-spec-vs-templates-divergence.md`.

Phase 1 of `issue-capture-mechanism-r1` produced 4 files (3 templates + 1 canonical
structural spec). PV-1 ran 6 pass criteria and returned PASS across all 5 dimensions
(tests / audits / validator / discipline / scope_deviations). All per-task verdicts were
APPROVED. The phase-quality reviewer issued a clean PASS verdict.

Post-phase human review surfaced that the spec's §7 ID-derivation rule used the long-form
interpretation (`ISSUE-ANALYSIS-foo`) of ADR-0050 §Decision §7's ambiguous
`<UPPERCASE-DOCTYPE>` phrasing, while the 3 sibling templates and all 5 pre-existing
empirical precedents in `Issues/` use the short form (`ANALYSIS-foo`). The spec was the
outlier against 8 other data points the validators had read individually but never
cross-referenced.

| PV-1 check | What it verifies | Cross-artifact? |
|---|---|---|
| PV-1.C1 | All 4 files exist | No (per-file) |
| PV-1.C2 | YAML frontmatter parses | No (per-file) |
| PV-1.C3 | Spec §4 byte-matches the **Blueprint** authoritative table | Yes (spec vs Blueprint) — but NOT spec vs templates |
| PV-1.C4 | No triggering discipline in any file | No (per-file grep) |
| PV-1.C5 | SKILL.md additively updated | No (single-file diff) |
| PV-1.C6 | Optional Gate 0 reviewer | Per-file structural review |

Critically, **PV-1.C3 demonstrates the validators *can* do cross-artifact checks** (it
compares spec §4 against the Blueprint). The gap is not technological — it is that no one
authored an analogous check for spec §7 against the template `id:` placeholders.

The defect was fixed pre-Phase-2 via commit `7b56248`. If unfixed, Phase 2 T2.1 would have
populated the validator constants from the long-form spec and rejected every existing
`Issues/*` file post-migration with a `blocker` ID-mismatch finding — the entire feature's
backward-compatibility contract (NFR-8) would have failed at the validator's first real
run.

### §2 — MCP provisioning postmortem (2026-05-24)

Full evidence: `evidence/mcp-postmortem-2026-05-24/` (4 documents).

Forensic root-cause pass over `devcontainer-mcp-provisioning-r1`. The feature shipped a
configuration where **5 of 7 MCP servers were broken** at the configuration, install, or
transport layer. The pipeline's hard gate (PV-5.C-HARDGATE per ADR-0043) returned exit 0
against this broken state. The hard gate was authored explicitly to prevent this class of
failure; it failed silently in exactly the way the user's verbatim ADR-0043 rationale warned
about.

12 defects identified (4 BLOCKER, 8 MAJOR); zero caught by any automated audit or gate.
Five named cross-cutting patterns:

| Pattern | One-line description |
|---|---|
| P1 | Specified-but-never-run gate criteria |
| P2 | Static auditors mistaken for runtime auditors |
| **P3** | **ADR-to-implementation gap — auditors stop at "design artifacts are internally consistent"** |
| P4 | Verdict-without-finding paradoxes accepted |
| P5 | Emergency modes used on canonical paths |

P3 is the pattern this analysis subsumes the PV-1 gap into. Multiple MCP-postmortem
defects are direct instances:

- **DEF-03** (`.mcp.json` invokes `mcp-openapi-schema` with no schema-path arg) — ADR-0041
  prescribed the invocation form; `.mcp.json` dropped the `<spec-path>` token; no auditor
  compared the two. The postmortem calls this *"the clearest single-gate-missing case."*
- **DEF-05** (`serena` invocation missing `start-mcp-server` argv per ADR-0041) — identical
  trace pattern to DEF-03.
- **DEF-06** (sentinel naming/location diverged from ADR-0041 §Decision §2) — identical
  trace pattern.

The postmortem's verdict for these defects: *"ADR-0041 prescribed the correct invocation.
Implementation drifted. No auditor compared the two."*

### §3 — The two instances share a structural shape

| Aspect | PV-1 case | MCP case |
|---|---|---|
| Authoritative artifact | `issue-doctypes-spec.md` §7 (long form) | ADR-0041 install taxonomy |
| Drifted artifact | 3 templates' `id:` placeholders (short form) | `.mcp.json`, `postCreate.sh` |
| Gate that should have caught it | PV-1 cross-file consistency check | `review-architecture-auditor` design-realization axis (DEF-10) |
| Why it didn't | No PV-1 check compares spec to templates | Auditor doesn't verify ADR prescriptions against implementation |
| Caught by | Human post-phase review | Forensic post-shipment pass |
| Downstream impact | Zero (caught pre-Phase-2) | 5/7 servers broken in shipping config |

---

## Root Cause

The unified root cause is structural: **the pipeline's automated gates are organized around
per-artifact internal-consistency checks, not relational cross-artifact checks.** Two distinct
causal sites contribute.

### Causal site 1 — The validator architecture commits to per-file scope

`validate_pipeline_frontmatter.py` operates on one file at a time (the CLI reads
newline-separated paths from stdin and validates each in isolation). Phase validators (PV-N)
compose these per-file checks plus optional whole-file existence checks and diff-stat
checks. The architecture does not naturally express "for each row in A, verify the
corresponding row in B." That kind of check requires a custom invariant — and writing the
custom invariant requires noticing the two artifacts should agree, which is the very thing
the gate is supposed to provide.

This is not a deficiency of the validator's *capability*; PV-1.C3 demonstrates a
spec-vs-Blueprint cross-file check is technically possible. It is a deficiency of *which
cross-file invariants get authored*, and authorship has so far been driven by what a
particular ADR (e.g., ADR-0050 Decision §4 D-05 table) explicitly anchors as load-bearing.
ID-derivation didn't get anchored as load-bearing — even though it is.

### Causal site 2 — ADRs prescribe but pipeline doesn't enforce-prescriptions

The MCP postmortem's P3 names this directly: *"ADRs prescribe concrete commands... and
invariants. No auditor compares these prescriptions against the eventual implementation."*
ADR-0050 §Decision §7 prescribed an ID-derivation rule using ambiguous phrasing
(`<UPPERCASE-DOCTYPE>`); the spec author resolved the ambiguity one way and the template
authors resolved it the other way. The ADR ambiguity is one upstream contributor, but
even an unambiguous ADR (like ADR-0041's install-taxonomy table) doesn't prevent drift —
DEF-03 and DEF-05 prove this. The missing mechanism is a check that says: "for every
artifact the ADR prescribes, verify the eventual file matches."

These two sites compound. Even a perfectly authored ADR with an explicit prescription can
drift in the implementation, and the validator architecture doesn't naturally express
"check the prescription was honored." Hardening either site in isolation gives partial
coverage; both need attention.

---

## Implications

### What's at risk going forward

- **Phase 2 of `issue-capture-mechanism-r1`** populates validator constants from the spec.
  Any further spec ambiguity that the templates resolve differently will propagate to the
  validator and reject real files. The §7 catch was lucky timing; the next such defect may
  not get human review before downstream consumption.
- **Future ADRs** will continue to prescribe concrete implementation details (install paths,
  argv strings, schema field names, ID formats). Each such prescription is a candidate
  drift site. Without an enforcement mechanism, the MCP-postmortem failure mode is the
  default outcome at scale.
- **Cross-phase invariants (CPIs)** currently capture intra-feature consistency (e.g.,
  CPI-3: `issue-capture-author.md` has no `skills:` field). They don't capture
  spec-vs-template, ADR-vs-implementation, or template-vs-empirical-precedent invariants.
  The CPI machinery is the right home for these but the catalog is incomplete.

### What's already shipped broken

The MCP case is the live example: `devcontainer-mcp-provisioning-r1` shipped 5/7 broken
servers and was approved by every gate. The four broken files (`.mcp.json`,
`.devcontainer/lib/mcp-ping.sh`, `.devcontainer/Dockerfile`, `.devcontainer/postCreate.sh`)
are still in the codebase as of this analysis's authoring date. The MCP postmortem's
`03-hardening-recommendations.md` §"What NOT to do" explicitly warns against patching them
before hardening lands — because the next slip would clear the same paper gates.

The PV-1 case is the avoided counterfactual: had the gap not been caught by human review,
Phase 2 would have shipped a validator that rejected every `Issues/*` file, blocking the
feature's entire backward-compatibility contract.

### What this implies about the issue-capture mechanism itself

This Issue file is being authored as a **dogfood test** of the very templates Phase 1 just
shipped. The dogfood pass surfaces three meta-observations:

1. The templates' `Cross-links` body section is helpful for navigation but redundant with
   the frontmatter; either is sufficient. Not a defect, just a noticed verbosity.
2. The `status: open` + `since:` companion-field discipline is straightforward to apply
   when the file is authored by a human (or a human-equivalent orchestrator). The
   future Phase-4 agent will need clear rubric for choosing `status: draft` vs
   `status: open` at capture time — which the structural spec correctly defers to
   `KB-issue-capture` per ADR-0049.
3. The decision to place 4 ad-hoc-doctype MCP postmortem files under `evidence/` (where
   they are non-validated per spec §2.3) is the **right** architectural call. They retain
   their narrative integrity without being forced to retrofit the new 3-doctype taxonomy.

---

## Recommendations / Open Questions

The MCP postmortem's hardening recommendations (H1–H8 in
`evidence/mcp-postmortem-2026-05-24/03-hardening-recommendations.md`) remain the canonical
fix set. This analysis adds one phase-validator-tier addendum and reaffirms the
prioritization.

| Rec | Description | Source | Cost | Defects closed |
|---|---|---|---|---|
| **H5** | Verdict invariant validation (P4 fix) | MCP postmortem | Trivial | DEF-11 |
| **H4** | Forbid `single-agent-fallback` for FULL-scope features (P5 fix) | MCP postmortem | Low | DEF-12 |
| **H7** | `.mcp.json` ↔ ADR-0041 install-taxonomy parity OP rule (P3 narrow fix) | MCP postmortem | Low | DEF-03, DEF-05 |
| **H3** | Design-realization audit dimension for `review-architecture-auditor` (P3 broad fix) | MCP postmortem | Medium | DEF-03, DEF-05, DEF-06, DEF-10 |
| **H6** | Discovery-research §Protocol Conformance section | MCP postmortem | Low | DEF-02 |
| **H1** | `--with-mcp-reachability` audit flag + live handshake check | MCP postmortem | Medium | DEF-01, DEF-02, DEF-04, DEF-07, DEF-08 |
| **H8** | Live tool-surface drift detection | MCP postmortem | Low | DEF-07 |
| **H2** | Orchestrator-driven Codespace rebuild loop | MCP postmortem | High | DEF-09 |
| **H9 (new)** | **PV-tier cross-file consistency invariant catalog** — phase validators gain a documented invariant section listing every cross-file relationship the phase's deliverables share, with one assertion per relationship. PV-1 specifically would gain: `PV-1.C7 — spec §7 ID-prefix rule matches each template's id: placeholder convention; spec §4 per-state required-companion-field table matches each template's per-state frontmatter shape.` Phase Validator Author's rubric (`KB-documentation-criteria/...`) gains a "cross-file consistency" prompt: *"for every deliverable-file pair (D_i, D_j) in this phase, what claim does D_i make about D_j, and what assertion would verify that claim?"* | This analysis | Low (architecturally analogous to H3 but at PV-tier scope) | The class of defect this analysis captures |

### Open Questions for the future feature run

- **Q1**: Is H9 (PV-tier cross-file invariants) better authored as a new PV-N section in
  every phase validator file (denormalized), or as a centralized `cross-file-invariants.md`
  reference cited by each PV (normalized)? Argues for: normalized (DRY, single point of
  truth, easier to audit holistically). Argues for: denormalized (each PV is self-contained
  and runnable in isolation).
- **Q2**: Should H3 (design-realization audit dimension) require ADRs to ship an
  `adr_prescriptions.yaml` companion file (machine-checkable), or extract prescriptions
  via NLP-style parsing of ADR prose (lower-burden but lower-fidelity)?
- **Q3**: H4 (forbid single-agent-fallback for FULL) is a process gate. Does it need a
  technical enforcement (orchestrator self-check) or is a documentation-only assertion in
  `recipe-feature-pipeline/SKILL.md` sufficient? Per ADR-0044's flatten pattern the parent
  orchestrator is the dispatcher; the self-check has a natural home.
- **Q4**: Is the topic-slug `cross-artifact-divergence-detection-gap` durable, or will a
  future re-framing (e.g., when H3 + H9 both ship and the pattern is "solved") want a more
  specific name? For now `open` status; can rename via `superseded` transition if needed.

### Recommended sequence

Same as the MCP postmortem's composite roadmap (`03-hardening-recommendations.md`
§"Composite roadmap"), with H9 inserted in the medium-term tier alongside H3:

- **This week — Quick wins:** H5, H4, H7 (low-cost; 4 defects closed; no new infrastructure)
- **This month — Pipeline hardening:** H3, H6, H1, H8, **H9** (closes 11 of 12 MCP defects + the PV-tier class)
- **Long-term — Close the loop:** H2 (high-cost; closes DEF-09; required for live verification)

---

## Cross-links

**Evolution cross-links (per ADR-0046):**

- `escalates_from`: (none — this is the root analytical capture of the unified pattern; no
  prior sibling doctype evolved into this analysis)
- `escalated_to`: (none yet — when a future feature run is opened to actually implement
  the hardening, this file will be amended to add `escalated_to: PROPOSAL-<slug>`; the
  receiving proposal will carry `escalates_from: ANALYSIS-cross-artifact-divergence-detection-gap`)

**State vocabulary (per ADR-0050 + `issue-doctypes-spec.md` §3):**

Full 5-state vocabulary: `draft → open → adopted | complete | superseded | wontfix-with-rationale`.
This file's current state is `open` (real systemic finding; awaiting future remediation;
not actively being worked).

**Related files:**

- `evidence/pv1-spec-vs-templates-divergence.md` — §1 evidence thread
- `evidence/mcp-postmortem-2026-05-24/README.md` — §2 evidence thread, index
- `evidence/mcp-postmortem-2026-05-24/01-error-log.json` — §2 evidence thread, machine-actionable defect log
- `evidence/mcp-postmortem-2026-05-24/02-pipeline-trace.md` — §2 evidence thread, per-defect pipeline-stage trace
- `evidence/mcp-postmortem-2026-05-24/03-hardening-recommendations.md` — H1–H8 source
- `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md` — the structural spec under analysis (post-§7-fix version is the canonical reference)
- `working/feature/issue-capture-mechanism-r1/per-task-execution-result-task-009.json` — `post_phase_remediations[]` array contains the parent-applied §7 fix record
- Commit `7b56248` — the §7 fix landing
