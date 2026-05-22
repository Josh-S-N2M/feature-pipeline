# Substrate Options Appendix

Run: `task-08-replication-20260501-021500`
Registry version: `2026-04-30.1`

For each architectural decision, the three-option enumeration drawn from `05-substrate-map.json`. The main report shows the recommended option; this appendix shows what was considered.

## D-0001: Substrate choice: Claude Code primitives vs. orchestration-framework alternative

**Recommended:** `native`

**Rationale:** Native is lossless enough for the design's stated goals (C-0001) and acknowledges its losses transparently (C-0002 explicitly out-of-scope; C-0003 acknowledged). Substrate change cost (16 weeks) is grossly disproportionate to the marginal gains for this single-pipeline use case. The corpus pre-justifies native — this enumeration confirms the choice rather than challenging it.

| Option | Description | Viable | Effort (weeks) | Loss summary |
|---|---|---|---|---|
| ✅ **native** | Build the pipeline using only Claude Code primitives: orchestrator skill, sub-agents via Task tool, ... | ✅ | 4 | pattern_fidelity, cycle_declaration, replay_determinism |
| ⚠️ **adapter** | Use Claude Code as the LLM provider but wrap with an external Python orchestrator that handles cycle... | ❌ | 12 | latency, cost_model, pattern_fidelity |
| · **substrate_change** | Adopt LangGraph (or Temporal, or AWS Step Functions) for orchestration, keeping Claude as the LLM. R... | ✅ | 16 | none |

### native
- **Description:** Build the pipeline using only Claude Code primitives: orchestrator skill, sub-agents via Task tool, file-system-as-state, hooks for QA, AskUserQuestion for the gate.
- **Viable:** True
- **Reason:** Direct realization. Per substrate registry, every needed primitive is present. Loss: framework-level supervisor abstractions are simulated rather than declared (cycle counters in orchestrator); deterministic replay is acknowledged out-of-scope per C-0003.
- **Cost:** effort_weeks=4, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=minor

### adapter
- **Description:** Use Claude Code as the LLM provider but wrap with an external Python orchestrator that handles cycle declaration, typed state, and deterministic replay outside the substrate.
- **Viable:** False
- **Reason:** Bypasses Claude Code's native primitives — loses MEMORY.md, .memories/, hooks, AskUserQuestion. Net cost greater than native AND substrate_change. Not viable as a middle ground.
- **Cost:** effort_weeks=12, runtime_overhead=significant, maintenance_burden=significant, irreversibility_cost=significant

### substrate_change
- **Description:** Adopt LangGraph (or Temporal, or AWS Step Functions) for orchestration, keeping Claude as the LLM. Recovers cycle declaration, typed state, and deterministic replay.
- **Viable:** True
- **Reason:** Recovers all explicitly out-of-scope properties. High switching cost. Worth it ONLY if multiple decisions push this direction; in this corpus, only D-0001 itself does.
- **Cost:** effort_weeks=16, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=significant

---

## D-0002: Memory architecture: two-tier (orchestrator + per-sub-agent) vs. single-tier MEMORY.md

**Recommended:** `native`

**Rationale:** Native carries the engineering-proposal flag (🔶), but the alternative (adapter) only differs in WHERE memory lives, not in conceptual approach. The two-tier convention from the source IS the substrate-idiomatic way to satisfy the requirement; rejecting it requires rejecting the synthesis-pipeline design, not refining it. Single-sourced caveat: Synthesizer should surface this in Limitations (C-0021's 🔶 marker).

| Option | Description | Viable | Effort (weeks) | Loss summary |
|---|---|---|---|---|
| ✅ **native** | Two-tier memory: orchestrator uses MEMORY.md (substrate-native); per-sub-agent memory layered on top... | ✅ | 1 | pattern_fidelity |
| · **adapter** | Single-tier MEMORY.md for the orchestrator; sub-agents receive their relevant memory slices through ... | ✅ | 0.5 | pattern_fidelity |
| · **substrate_change** | Switch to a framework with native multi-tier memory (e.g., LangGraph state with TypedDict per-node f... | ✅ | 16 | none |

### native
- **Description:** Two-tier memory: orchestrator uses MEMORY.md (substrate-native); per-sub-agent memory layered on top of file system at .memories/agents/<name>/ with READMEs encoding the read protocol and routing rule.
- **Viable:** True
- **Reason:** Engineering proposal (🔶 in source). Sub-agents do not have a native auto-loaded memory file (C-0021), so the proposal layers convention on top of the file system. Knowledge skills (C-0022) handle curated content; sub-agent memories handle accumulated runtime observations (C-0023). Loss: pattern fidelity is partial — the convention requires agent discipline rather than substrate enforcement.
- **Cost:** effort_weeks=1, runtime_overhead=none, maintenance_burden=minor, irreversibility_cost=minor

### adapter
- **Description:** Single-tier MEMORY.md for the orchestrator; sub-agents receive their relevant memory slices through the orchestrator's prompt at task start.
- **Viable:** True
- **Reason:** Lower implementation cost. Loss: orchestrator must curate and pass memory slices, growing its context budget by O(num_agents × per-agent-memory-size). Acceptable for small pipelines; degrades at scale.
- **Cost:** effort_weeks=0.5, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=none

### substrate_change
- **Description:** Switch to a framework with native multi-tier memory (e.g., LangGraph state with TypedDict per-node fields).
- **Viable:** True
- **Reason:** Substrate-level memory tiers exist in framework alternatives. Cost is the full substrate migration — disproportionate for this single concern.
- **Cost:** effort_weeks=16, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=significant

---

## D-0003: Verification regime: vertical-slice early verification gate vs. end-to-end-only acceptance

**Recommended:** `native`

**Rationale:** Native is the explicitly recommended path in BOTH source documents (cross-source bridge). The §7.4 vertical-slice gate is a real, falsifiable mechanism — this very run is its instance. Adapter is non-viable because per-phase isolation cannot reveal substrate-level integration failures.

| Option | Description | Viable | Effort (weeks) | Loss summary |
|---|---|---|---|---|
| ✅ **native** | Vertical-slice early verification gate: orchestrator + Extractor + claim-extraction-knowledge run en... | ✅ | 2 | replay_determinism |
| ⚠️ **adapter** | Phase-by-phase incremental verification: each phase agent ships with its own integration test agains... | ❌ | 8 | pattern_fidelity |
| · **substrate_change** | Use a framework with built-in verification hooks (LangGraph's state-validation, Temporal's determini... | ✅ | 16 | none |

### native
- **Description:** Vertical-slice early verification gate: orchestrator + Extractor + claim-extraction-knowledge run end-to-end on a 2-document corpus before any other phase is added. Six §7.4 success criteria are the falsifiable acceptance target.
- **Viable:** True
- **Reason:** Both source documents converge on this discipline. The output comparison method (C-0053) is the binding mechanism; reference artifacts captured per §7.4 criterion 6 are the smoke-run baseline. Loss: bit-exact replay is impossible (Claude Code is non-deterministic per C-0003); ±10% tolerance per §7.2 Layer C is the substitute.
- **Cost:** effort_weeks=2, runtime_overhead=none, maintenance_burden=minor, irreversibility_cost=minor

### adapter
- **Description:** Phase-by-phase incremental verification: each phase agent ships with its own integration test against synthetic upstream artifacts, no end-to-end gate.
- **Viable:** False
- **Reason:** Per-phase tests catch interface violations but cannot demonstrate substrate-level invariants (e.g., the recursion-safety + per-source-isolation interaction). Per the source, substrate-level mismatches are the failure mode the early-verification gate is designed to catch. Adapter would let those slip past until acceptance.
- **Cost:** effort_weeks=8, runtime_overhead=minor, maintenance_burden=significant, irreversibility_cost=minor

### substrate_change
- **Description:** Use a framework with built-in verification hooks (LangGraph's state-validation, Temporal's deterministic replay).
- **Viable:** True
- **Reason:** Substrate-built verification eliminates ±10% tolerance need. Cost is full substrate migration — and this single decision does not justify it.
- **Cost:** effort_weeks=16, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=significant

---

## D-0004: Recursion safety: hard rule (orchestrator + agent both check) vs. soft convention

**Recommended:** `native`

**Rationale:** Hard rule with defense-in-depth is the corpus's explicit recommendation (C-0019 'This is a hard rule'). Adapter is non-viable because the failure mode is silent corruption — irreversible by the time it's noticed.

| Option | Description | Viable | Effort (weeks) | Loss summary |
|---|---|---|---|---|
| ✅ **native** | Hard rule with defense-in-depth: orchestrator's input glob excludes output/synthesis-*/** AND each s... | ✅ | 0.5 | none |
| ⚠️ **adapter** | Soft rule via naming convention: prefix `synthesis-` is documented but not enforced; rely on agents ... | ❌ | 0 | pattern_fidelity |
| ⚠️ **substrate_change** | n/a — recursion safety is an architectural concern within Claude Code's file-system model and does n... | ❌ | 0 | none |

### native
- **Description:** Hard rule with defense-in-depth: orchestrator's input glob excludes output/synthesis-*/** AND each sub-agent's body includes a secondary `output/synthesis-*/` prefix check on source paths.
- **Viable:** True
- **Reason:** Cheap, simple, both checks are deterministic file-ops. Per substrate registry, Glob and string-prefix checks are native primitives.
- **Cost:** effort_weeks=0.5, runtime_overhead=none, maintenance_burden=none, irreversibility_cost=none

### adapter
- **Description:** Soft rule via naming convention: prefix `synthesis-` is documented but not enforced; rely on agents to follow convention.
- **Viable:** False
- **Reason:** If an agent or future code path forgets the convention, claim corpus pollutes itself silently — irrecoverable corruption per the source's 'every re-run would ingest its own prior output and degrade signal' (§4.5). High irreversibility makes this non-viable despite zero implementation cost.
- **Cost:** effort_weeks=0, runtime_overhead=none, maintenance_burden=minor, irreversibility_cost=significant

### substrate_change
- **Description:** n/a — recursion safety is an architectural concern within Claude Code's file-system model and does not require substrate change.
- **Viable:** False
- **Reason:** n/a — substrate change does not address this concern.
- **Cost:** effort_weeks=0, runtime_overhead=n/a, maintenance_burden=n/a, irreversibility_cost=n/a

---

## D-0005: User confirmation: required AskUserQuestion gate vs. assumed defaults vs. configuration file

**Recommended:** `native`

**Rationale:** Native is corpus-recommended (C-0008, C-0009). Adapter is viable but introduces UX ambiguity around cancellation that the corpus explicitly resolves (C-0009 — empty answers exit cleanly). Adapter would re-open a settled question.

| Option | Description | Viable | Effort (weeks) | Loss summary |
|---|---|---|---|---|
| ✅ **native** | Required AskUserQuestion gate at orchestrator step 3 with three concurrent questions on a single car... | ✅ | 0.5 | none |
| · **adapter** | Configuration file read at orchestrator start with prompt-on-missing for unspecified fields. | ✅ | 1 | pattern_fidelity |
| ⚠️ **substrate_change** | n/a — confirmation gate is application-level, not substrate-level. | ❌ | 0 | none |

### native
- **Description:** Required AskUserQuestion gate at orchestrator step 3 with three concurrent questions on a single card. Cancellation is dismissal-with-empty-answers; orchestrator exits cleanly without allocating run-id.
- **Viable:** True
- **Reason:** AskUserQuestion is a documented Claude Code primitive (per substrate registry §2). Native realization is direct. Loss: scripted invocation needs a bypass flag (out of scope for this design — the corpus does not address it).
- **Cost:** effort_weeks=0.5, runtime_overhead=minor, maintenance_burden=minor, irreversibility_cost=minor

### adapter
- **Description:** Configuration file read at orchestrator start with prompt-on-missing for unspecified fields.
- **Viable:** True
- **Reason:** Allows scripted invocation. Loss: user contract is split (some answers from file, some from prompt) — confusing UX. Cancellation semantics become unclear (does an empty config file mean cancel, or use defaults?).
- **Cost:** effort_weeks=1, runtime_overhead=none, maintenance_burden=minor, irreversibility_cost=minor

### substrate_change
- **Description:** n/a — confirmation gate is application-level, not substrate-level.
- **Viable:** False
- **Reason:** n/a — confirmation gates are an application-level concern within any substrate.
- **Cost:** effort_weeks=0, runtime_overhead=n/a, maintenance_burden=n/a, irreversibility_cost=n/a

---

