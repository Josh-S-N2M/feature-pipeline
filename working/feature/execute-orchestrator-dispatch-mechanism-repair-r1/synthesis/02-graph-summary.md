# 02-graph-summary

Graph for `execute-orchestrator-dispatch-mechanism-repair-r1` Synthesis fan-in.
Sources: 3 per-source claims files (146 + 76 + 74 = 296 claims).
Run id: `execute-orchestrator-dispatch-mechanism-repair-r1-20260523-202235`.

This summary is for human review. Critic and Framer consume `02-graph.json` directly.

## Shape

- **Entities:** 105
- **Edges (relations):** 121
- **Communities (hand-curated):** 7
- **Dissent flags:** 5 (see below)
- **Orphan-entity drops:** 0 (every entity has at least one claim back-pointer)

## Claim-id namespacing

The three source files share the `C-NNNN` id space. To preserve uniqueness in this graph, claim ids are prefixed:

| Prefix | Source |
|---|---|
| `CR-` | `01-claims-codebase-analysis-report.json` (146 claims) |
| `T-`  | `01-claims-T-001-claude-code-subagent-tool-grant-semantics.json` (76 claims) |
| `AN-` | `01-claims-analysis-execute-orchestrator-dispatch-limitation.json` (74 claims) |

Strip the prefix to dereference the original `claim.id`.

## Top entities by claim count

| Rank | Entity | Type | Claim count | Notes |
|---|---|---|---|---|
| 1 | `Agent tool` (E-0008) | tool | 47 | The bridge entity across all 3 sources — the load-bearing tool whose runtime semantics differ from documentation expectation. |
| 2 | `execute-orchestrator` (E-0001) | service | 55 | Subject of the feature; the primary defect site. |
| 3 | `Claude Code` (E-0007) | service | 25 | The substrate that defines the dispatch constraint. |
| 4 | `execute-finalize-reconciler` (E-0002) | service | 19 | Inferred-defect dispatcher (same harness, same tool grant). |
| 5 | `dispatch_supported: false` (E-0009) | finding | 18 | Load-bearing T-001 decision claim. |
| 6 | `Anthropic Claude Code sub-agent documentation` (E-0046) | standard | 20 | Primary source for F-1 corroboration. |
| 7 | `single-agent fallback mode` (E-0043) | pattern | 19 | The active workaround posture; not the design target. |
| 8 | `§6 option (b) retire execute-orchestrator` (E-0014) | pattern | 17 | The largest-blast-radius option. |
| 9 | `execute-orchestrator runtime tool surface [Read, Write, Bash, Edit]` (E-0012) | finding | 14 | The empirical observation across all 3 sources. |
| 10 | `F-7 mid-session agent registry not hot-reloaded` (E-0011) | finding | 13 | Novel empirical finding from T-001 — orthogonal to dispatch_supported. |

## Top edges by claim count

| From | Relation | To | Claim count |
|---|---|---|---|
| `single-agent fallback mode` | `conflicts_with` | `specialist-isolation dispatch pattern` | 7 |
| `execute-orchestrator` | `requires` | `Agent tool` | 7 |
| `dispatch_supported: false` | `supersedes` | `harness-restriction hypothesis 4.1` | 5 |
| `dispatch_supported: false` | `instance_of` | `Claude Code` | 6 |
| `F-1 multi-source corroboration` | `implements` | `dispatch_supported: false` | 5 |
| `§6 option (b) retire execute-orchestrator` | `conflicts_with` | `PRD FR-4 8-file inventory` | 4 |
| `OI-CR-A` | `conflicts_with` | `ADR-0034` | 4 |
| `single-agent fallback mode` | `implements` | `devcontainer-mcp-provisioning-r1 originating run` | 4 |
| `Agent tool` | `instance_of` | `Claude Code` | 4 |
| `T-001 acceptance` | `requires` | `Anthropic sub-agent docs` | 3 |

## Identified clusters

Seven hand-curated topical clusters. The first three are the anchor decision-points; the next four are constraint clusters that bound design choice without driving it.

---

### Cluster 1 — Dispatch-supported / Kill-criterion-2 (the anchor decision)

**Load-bearing entity:** `dispatch_supported: false` (E-0009).

**Member entities:**
- `dispatch_supported: false` (E-0009)
- `kill-criterion-#2 triggered` (E-0010)
- `Agent tool` (E-0008)
- `execute-orchestrator` (E-0001)
- `execute-finalize-reconciler` (E-0002)
- `Claude Code` (E-0007)
- `execute-orchestrator runtime tool surface [Read, Write, Bash, Edit]` (E-0012)
- `F-1 multi-source corroboration` (E-0098)
- `F-2 grant-vs-runtime asymmetry` (E-0099)
- `F-3 inheritance semantics` (E-0100)
- `F-4 no documented enable-nesting flag` (E-0101)
- `F-5 example sub-agents do not declare Agent` (E-0102)
- `F-6 Task->Agent rename informational` (E-0103)
- `Task → Agent rename (v2.1.63)` (E-0074)
- `Plan built-in subagent` (E-0091)
- `coordinator example (main-thread only)` (E-0090)
- `tools: allowlist + disallowedTools denylist semantics` (E-0075)
- `harness-restriction hypothesis 4.1` (E-0065)
- `active-harness-behavior hypothesis 4.2` (E-0066)
- `Hypothesis H-a baseline tool-set inheritance` (E-0063)
- `Hypothesis H-b memory-field auto-enable` (E-0064)
- `Edit tool (undeclared runtime addition)` (E-0050)
- `Bash(python3:*) scope restriction` (E-0051)
- `memory: project field auto-enable` (E-0052)
- `Anthropic sub-agent docs` (E-0046)
- `Anthropic Agent SDK sub-agents docs` (E-0047)
- `T-001 acceptance criteria` (E-0097)
- `probe-dispatch-test-r1 / r2` (E-0048)
- `Skills mechanism (workaround alternative)` (E-0092)
- `Chain-from-main-conversation workaround` (E-0093)
- `fork mode CLAUDE_CODE_FORK_SUBAGENT=1` (E-0044)
- `agent teams CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (E-0045)
- `PRD FR-2 kill-criterion gating` (E-0034)

This is the densest cluster — three sources triangulate on `dispatch_supported: false`. The hypothesis chain (AN's 4.1 / 4.2) is resolved by T-001's documentation evidence (F-1 / F-2 / F-3 / F-4); the resolution is captured as `supersedes` edges from `dispatch_supported: false` to `harness-restriction hypothesis 4.1`.

---

### Cluster 2 — §6 design options & per-option blast-radius

**Load-bearing entity:** `§6 option (b) retire execute-orchestrator` (E-0014) — the largest-blast-radius option, also the one that conflicts with the 8-file inventory.

**Member entities:**
- `§6 option (a) flatten dispatch hierarchy` (E-0013)
- `§6 option (b) retire execute-orchestrator` (E-0014)
- `§6 option (c) Bash-script dispatch surface` (E-0015)
- `recipe-feature-pipeline` (E-0006)
- `PRD FR-4 8-file inventory` (E-0032)
- `AC-FR-4-a scope-expansion open-item gate` (E-0037)
- `OI-CR-B option (b) escapes 8-file inventory` (E-0068)
- `14-row state machine (T0..T13)` (E-0041)
- `KB-documentation-criteria template-assignment table` (E-0053)
- `pipeline-run-summary-template.md (T12)` (E-0054)
- `per-task-execution-result template` (E-0055)
- `phase-quality-report template` (E-0056)
- `quality-reconciliation-log template` (E-0057)
- `smoke_test_auditing_shared.py` (E-0058)
- `auditing-codespaces consumer note` (E-0059)
- `auditing-shared skill` (E-0060)
- `v1 invoking_agent invariant` (E-0095)
- `state-transitions.log schema` (E-0031)

This cluster captures the codebase-analysis-report's per-option blast-radius breakdown (CR-0095..CR-0109). The `requires` edges from option (b) to outside-inventory files are the load-bearing decision-shaping evidence.

---

### Cluster 3 — F-7 mid-session agent registry (orthogonal verification constraint)

**Load-bearing entity:** `F-7 mid-session agent registry not hot-reloaded` (E-0011).

**Member entities:**
- `F-7 mid-session agent registry not hot-reloaded` (E-0011)
- `PRD FR-6 verification step` (E-0036)
- `probe-dispatch-test-r1 / r2 (instrumentation)` (E-0048)
- `§6 option (b) retire execute-orchestrator` (E-0014) (bridge to cluster 2)

This cluster is intentionally small. It does NOT influence the §6 design choice; it imposes a session-boundary constraint on the FR-6 verification approach (must use a fresh session). Bridge into cluster 2 via the `conflicts_with` edge from F-7 to option (b) — if option (b) adds new sub-agents, those won't be invocable mid-session.

---

### Cluster 4 — ADR-attribution & cycle-cap invariants

**Load-bearing entity:** `ADR-0033 (ADR-0029 execution-phase extension)` (E-0016) — canonical home of symmetric D-12.

**Member entities:**
- `ADR-0033` (E-0016)
- `ADR-0034 (PRD mis-credit cleanup)` (E-0017)
- `ADR-0017 (4-cycle cap)` (E-0018)
- `ADR-0029 (no silent scope changes)` (E-0022)
- `ADR-0033 D-12 symmetric application` (E-0076)
- `PRD FR-3-c invariant set` (E-0035)
- `OI-CR-A documentary mis-attribution` (E-0067)
- `Q-CC-4 stub-vs-real distinction` (E-0082)

The `supersedes` edge from ADR-0033 → ADR-0034 captures the corrected attribution. The `conflicts_with` edge from `OI-CR-A` → ADR-0034 captures the mis-attribution as a documentary finding. This is one of the dissent surfaces (see below).

---

### Cluster 5 — Specialist-isolation pattern & single-agent fallback losses

**Load-bearing entity:** `specialist-isolation dispatch pattern` (E-0042).

**Member entities:**
- `specialist-isolation dispatch pattern` (E-0042)
- `single-agent fallback mode` (E-0043)
- `execute-task-code-producer` (E-0003)
- `execute-task-quality-handler` (E-0004)
- `execute-phase-quality-reviewer` (E-0005)
- `execute-finalize-reconciler` (E-0002)
- `Contract 4 / D-14 dispatch matrix` (E-0080)
- `Contract 5 state-transitioned dispatches` (E-0081)
- `D-2 verdict enums` (E-0077)
- `D-5 artifact-pair pattern` (E-0078)
- `D-13 5-dimensional verdict` (E-0079)
- `ai-development-guide 4-phase pattern` (E-0084)
- `KB-cc-design skill` (E-0083)
- `devcontainer-mcp-provisioning-r1 originating run` (E-0061)
- `Phase 0 verify-at-execution findings` (E-0062)

This cluster captures what is LOST by single-agent fallback and what dispatch is meant to preserve. The `conflicts_with` edge from `single-agent fallback mode` to `specialist-isolation dispatch pattern` (7 supporting claims) is the load-bearing motivation for repairing dispatch.

---

### Cluster 6 — Schema gaps & documentary drift

**Load-bearing entity:** `checkpoint.json schema` (E-0030).

**Member entities:**
- `checkpoint.json schema` (E-0030)
- `state-transitions.log schema` (E-0031)
- `OI-CR-C checkpoint execution-phase fields undocumented` (E-0069)
- `OI-CR-D template invariant + void/-prime undocumented` (E-0070)
- `void + -prime de facto log extensions` (E-0094)
- `v1 invoking_agent invariant` (E-0095)
- `NFR-5-a canonical-reference documentation gap closure` (E-0039)
- `NFR-6-a no-artifact-migration` (E-0040)

Pre-existing schema-drift surface. The codebase-analysis-report makes these load-bearing as "any §6 option that touches checkpoint must close the gap in lockstep" (NFR-5-a).

---

### Cluster 7 — Out-of-scope / meta-feature pointers

**Load-bearing entity:** `per-agent design evaluation gap` (E-0089).

**Member entities:**
- `agent-roster-design-discipline-r1 saved-for-later meta-feature` (E-0088)
- `per-agent design evaluation gap` (E-0089)
- `pipeline-gap family pattern` (E-0104)
- `OI-CR-F agent count 35 vs 36` (E-0072)
- `OI-CR-G execute-orchestrator self-declared parent skill` (E-0073)
- `OI-CR-E ADR-0035 not in Research Plan inherited-ADR list` (E-0071)
- `ADR-0035 (auditing-shared skill-binding)` (E-0023)
- `ADR-0019 (naming convention)` (E-0019)
- `ADR-0022 (sub-agent reasoning configuration)` (E-0020)
- `ADR-0027 (deliverable-archive gap)` (E-0021)
- `ADR-0036 (single-location ADR placement)` (E-0024)
- `ADR-0037 (mcp-events.jsonl transition surfacing)` (E-0025)
- `ADR-0040 (Serena narrowed always-on)` (E-0026)
- `ADR-0041 (install-mechanism hybrid)` (E-0027)
- `ADR-0042 (auditing-mcp family graduation)` (E-0028)
- `ADR-0043 (auditing-mcp Gate-6 hard gate)` (E-0029)
- `GitNexus MCP` (E-0085)
- `codebase-memory-mcp not registered` (E-0086)
- `manual-grep-and-read extraction method` (E-0087)
- `shared-document-reviewer agent` (E-0096)
- `task-tracking primitives` (E-0049)
- `codebase-analysis-report` (E-0105)

These are context entities — they bound the design space but are not anchor decisions.

---

## The three anchor decision points (for the per-layer cc Designer)

1. **`dispatch_supported: false`** (E-0009) — load-bearing T-001 claim. Supported by 18 direct claims plus the entire F-1 / F-2 / F-3 / F-4 finding chain. Three independent documentation sources with verbatim quotes ≤15 words. The hypothesis chain in `analysis-execute-orchestrator-dispatch-limitation.md` §4.1 (harness-restriction) is RESOLVED by T-001's documentation evidence — captured as a `supersedes` edge.

2. **`kill-criterion-#2 triggered → FULL repair pathway`** (E-0010) — direct consequence of (1). 2 supporting claims (T-0002, AN-0069).

3. **§6 option choice (a / b / c)** — T-001 confirms all three options respect the no-nested-dispatch constraint (T-0060), so the constraint does not pick between them. The codebase-analysis-report's blast-radius preview DOES differentiate them:
   - Option (a) — 1 outside-inventory file, AC-FR-4-a open count = 1
   - Option (b) — 5+ outside-inventory files, AC-FR-4-a open count = 5+ (needs operator check)
   - Option (c) — 1 outside-inventory file, AC-FR-4-a open count = 1
   The codebase-researcher flags this as evidence (not a pre-decision): option (b) carries materially larger blast-radius outside the inventory.

## Dissent flags (for synth-critic CoVe verification)

These are places where the 3 sources make claims that *partially disagree*, mostly resolution-of-prior-hypotheses by later evidence:

1. **DISSENT-1: Root-cause hypothesis resolution.** `analysis-execute-orchestrator-dispatch-limitation.md` §4.1 (AN-0041..AN-0046) hypothesizes `harness-restriction` as the most likely root cause; T-001 (T-0001, T-0003, T-0004, T-0005, T-0007, T-0050) confirms with documentation evidence that it IS deliberate harness design. The graph captures this as `dispatch_supported: false` `supersedes` `harness-restriction hypothesis 4.1`. The earlier source's "less likely" hypothesis 4.2 (active-harness-behavior — frontmatter rewrite) is partially supported by T-001's H-b (memory: auto-enable explains the Edit-tool addition); these are not in direct conflict but the framing differs. Surfaces in graph as the `E-0065` → `E-0009` supersession and the `E-0064` → `E-0050` implementation.

2. **DISSENT-2: ADR-0033 vs ADR-0034 attribution.** All 3 sources reference the symmetric-D-12 cap. The original AN source said "ADR-0034 symmetric D-12" but the orchestrator's correction note (CR-0010, AN-0029 provenance note) corrects this to ADR-0033 line 71. The PRD FR-3-c carries the uncorrected form (CR-0011, CR-0012, CR-0142). Captured as `ADR-0033` `supersedes` `ADR-0034`, plus a `conflicts_with` edge from `OI-CR-A` to ADR-0034. **Critic should verify all downstream artifacts cite ADR-0017 + ADR-0033, not ADR-0034.**

3. **DISSENT-3: 35 vs 36 agent count.** Research Plan claims 35 (CR-0064, CR-0137); actual sweep is 36 (CR-0063). Minor; recorded as OI-CR-F. Surfaces in graph as entity E-0072 with two contradictory-cardinality claims.

4. **DISSENT-4: Edit-tool mechanism.** AN-0049 / AN-0050 weighs the Edit-tool evidence as "active mutation between declaration and runtime" (active-harness-behavior). T-0023 / T-0024 (T-001) proposes two competing hypotheses (H-a baseline inheritance vs H-b memory-field auto-enable). The graph captures both H-a and H-b as `implements` edges into E-0050 (Edit tool) — these hypotheses are not yet refuted; H-b is flagged as "likeliest" in T-0068 but explicitly non-load-bearing (T-0069). **Critic note:** these competing hypotheses are out-of-scope for the kill-criterion decision but should be confirmed/refuted in FR-6 design.

5. **DISSENT-5: §6 design-option pre-disposition.** `analysis-execute-orchestrator-dispatch-limitation.md` §6 (AN-0061, AN-0062, AN-0063) frames the three options as candidates with no pre-decision. `analysis-execute-orchestrator-dispatch-limitation.md` §7 (AN-0072) explicitly defers the choice. `codebase-analysis-report.md` §5 surfaces option (b)'s larger blast-radius as evidence-not-pre-decision (CR-0108). T-001 (T-0061) explicitly says "the Designer's choice among PRD §6 options (a/b/c) is unconstrained by T-001's findings." **Surfaces of soft pressure:** the codebase blast-radius data and the AC-FR-4-a gate jointly load against (b) but do not preclude it.

## Orphans

None. Every entity has a non-empty `claims[]` back-pointer list. Drop step skipped.

## Edges not captured

A few weak or borderline-relational signals were intentionally left as entity-claim back-pointers rather than promoted to edges:

- "Severity" framings ("real audit-trail losses, not just cleanliness", AN-0037) — these are property assertions about a finding, not relations between named entities.
- "Recommendation" / "disposition" framings (e.g., CR-0108 "evidence not pre-decision") — these are stance qualifications, not relations.
- "Future-projection" claims (AN-0017 "next time any sub-agent declares Agent...") — these are about counterfactual entities and don't belong as edges in a finite-entity graph.

These remain visible to the Critic via the claim back-pointers on the relevant entities.

## Notes for downstream consumers

- **Framer:** the 3 anchor decisions above are the candidate decision frames. The 7-cluster topology should map cleanly to report sections (cluster 7 is suitable as an appendix / pointers section).
- **Critic:** focus CoVe verification on the 5 dissent flags above, especially DISSENT-2 (ADR attribution — directly affects downstream artifact correctness) and DISSENT-1 (the hypothesis resolution chain — the graph asserts T-001 supersedes AN's hypothesis but this should be verified).
- **Substrate:** every claim appears in at least one entity's back-pointer list; no Substrate-relevant claim is orphaned.
- **Synthesizer:** the graph supports a 3-anchor decision narrative with cluster-1 (load-bearing technical decision) + cluster-2 (design-option space) + cluster-3 (orthogonal verification constraint) as the spine; clusters 4–7 are supporting context.
