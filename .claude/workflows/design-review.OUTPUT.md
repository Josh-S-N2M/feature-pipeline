# Design-review — architecture + plan (RUN OUTPUT, for review)

> Full forensic design-soundness review, 2026-05-30 (wf_aaca06c5-e6d; 59 agents, ~3.9M tokens). Coverage: 24 rules + 24 anti-patterns + 10 Parts + 7 mechanism audits + schedulability. All listed defects survived adversarial verification. Report-only — candidates for human adjudication.

I have all the inputs needed: the coverage matrix, confirmed defects (all verified_real: true), and schedulability analysis. Let me synthesize the forensic review.

# Forensic Design Review — governed-pipeline-architecture.md vs implementation-plan.md

## 1. Coverage Summary

Every item in the architecture was checked. Nothing was skipped.

| Dimension | Total checked | OK | Findings |
| --- | --- | --- | --- |
| Rules (R1–R24) | 24 | 22 | 2 — R9 (major), R13 (minor) |
| Anti-patterns (A1–A24) | 24 | 24 | 0 |
| Parts (I–X) | 10 | 6 | 4 — Part I (major), Part III (major), Part IV (minor), Part VII (minor) |

Plus six **mechanism-level** correctness audits (run against the design end-to-end, not tied to a single Part/rule line). Five surfaced confirmed defects; one — reverse-transitive-closure propagation — surfaced two distinct defects.

Rules that came back as findings: **R9** (version-and-propagate atomically), **R13** (every gate emits a typed event).
Parts that came back as findings: **I** (problem statement), **III** (contract-gated pipeline), **IV** (freshness gate), **VII** (knowledge governance).
All 24 anti-patterns checked clean — though note the substance of A8, A11/A12, A21, A24 reappears below as mechanism defects, because the design *names* the anti-pattern but the plan does not *enforce* the guard against it.

## 2. Prioritised Confirmed-Defect List

All defects below survived adversarial verification (`verified_real: true`). All are candidates for human adjudication — this review surfaces risk, it does not certify.

### BLOCKER

There are no defects that remained blocker after verification. The one flag raised at blocker severity (reverse-transitive-closure propagation) was verified down to a major + the idempotency-cycle issue, because a per-artifact freshness backstop prevents the silent unbounded cascade for non-terminal artifacts. It is listed under Major.

### MAJOR

**[mechanism-correctness] Idempotency key collides across reconciliation cycles → corrected external write silently dropped.**
The recovery key is fixed at `{run}:{stage}` with "treat a duplicate as success," but reconciliation legitimately re-runs the same stage on cycle 2+ (the run-event surface already tracks a `cycle.*` index). For a side-effecting actor, cycle 2's *corrected* write presents the same key as cycle 1 and is suppressed as a duplicate — the stale state survives the exact pass built to fix it.
*Fix:* mint the key as `{run}:{stage}:{cycle}` so replay still dedups within a cycle but reconciliation lands.
*Location:* governed-pipeline-architecture.md:496, :717; implementation-plan.md:193.

**[mechanism-correctness] Idempotency key is inert against non-dedup tools, and per-stage granularity loses multi-effect writes.**
"Treat a duplicate as success" requires a receiver or local store to honor the key, but git push / file writes / Slack / generic MCP POSTs ignore caller keys, and no durable "key consumed" store exists separate from the boundary write — so a crash after a side effect but before the boundary re-fires it on replay (double-apply). A single stage with two distinct external writes shares one key, so a crash between them either skips both or re-fires the first (lost update). Also: the run-event JSONL append has no fsync/atomic-rename spec, so a torn final line either crashes replay or drops a completed `stage.complete`.
*Fix:* require a durable idempotency record written before the side effect (AWS-Powertools-table pattern), key per-side-effect not per-stage, and atomic-rename the journal append.
*Location:* governed-pipeline-architecture.md:496, :499, :614, :1008; implementation-plan.md:193, :331.

**[mechanism-correctness] Reviewer panel is treated as one atomic gate but is three non-reproducible actors — crash loses a completed finding; resolution policy is underspecified.**
The k=3 cross-provider panel records only the aggregated `gate.result`; a crash after judge A returns needs-revision but before the boundary forces a full re-run, and because judges are ~28% non-reproducible, A can flip to pass — silently losing a real finding. Separately, the resolution policy is written as the self-contradictory "majority/any-fail" with no tie-break, no partial-quorum rule, and no in-panel abstain composition, so a provider outage or one abstain can default-pass and defeat the anti-illusory-consensus rationale.
*Fix:* add per-panel-member boundary events to the run-event schema, and pin one resolution policy (recommend any-fail + any-abstain→escalate, quorum required).
*Location:* governed-pipeline-architecture.md:342-346, :495-499; implementation-plan.md:204-206, :257.

**[mechanism-correctness] Startup tool probe reports PASS for the exact "reachable but not initialized" failure it exists to catch.**
D-TOOL-1 claims the probe proves a tool is reachable AND initialized in the agent's run context (serena "no active project" is the named bug). The seed it generalizes (`mcp-ping.sh`) spawns a throwaway out-of-session subprocess and sends only `tools/list`, which returns success with no active project — empirically confirmed live. The probe validates reachability only; per-agent init context is never modeled.
*Fix:* run the probe at SessionStart in-session, execute the registered init step (`activate_project`), then verify a project-scoped call (`get_current_config`/`find_symbol`) succeeds.
*Location:* governed-pipeline-architecture.md:608-617, :718, :749, :988; implementation-plan.md:225; .devcontainer/lib/mcp-ping.sh:47-81.

**[mechanism-correctness] Improvement loop validates proposed changes against a corpus it writes itself — circular oracle defeats the A24 human gate.**
Telemetry → human-approve → validate-on-offline-corpus is the claimed Goodhart guard, but the same loop auto-populates the corpus from audit JSONs with no human gate on the corpus writes. A miscalibrated-but-confident recurring finding gets written as a golden failure case AND becomes the rationale for a new validator; the validator then "passes" against the poisoned corpus, and the human approves a wrong rule that ships as an enforced gate. The human gate adjudicates the change; the oracle that would falsify it was authored by the same loop.
*Fix:* gate or independently re-label corpus additions (apply "producer can't mark its own homework" to the meta-loop); run-lock + substrate-version-pin the periodic batch with same-window conflict resolution.
*Location:* governed-pipeline-architecture.md:505-512, :751; implementation-plan.md:290, :361.

**[mechanism-correctness] Reverse-transitive-closure propagation walks the manifest graph while staleness is stamped on the `derived_from` graph — the two are never reconciled.**
Invalidation closure walks `pipelines.yaml` lineage edges, but digests are detected/stamped via each artifact's `derived_from` frontmatter (which the architecture itself calls *the* lineage graph). No check asserts `derived_from ⊆ manifest-lineage`, and dynamic/router-decided edges are forbidden from the manifest by design — so the hard-gate can surface an *incomplete* stale set, and terminal artifacts whose handoff already passed can ship stale. (The per-artifact freshness check at each handoff backstops non-terminal artifacts, which is why this is major not blocker.)
*Fix:* add a completeness assertion that every `derived_from` edge maps to a manifest lineage edge — or seed the closure from the in-git `derived_from` graph the architecture already treats as canonical.
*Location:* governed-pipeline-architecture.md:402-404, :437; implementation-plan.md:167, :175-179.

**[rule-not-enforced] R9 "version and propagate atomically" has no concrete enforcer.**
The clause "a contract/template change bumps its version and lands with dependent fixes in one commit" is honored only by commit-hygiene prose. The drift sentinel's audited set (every contract→validator, every edge→gate, every domain→bundle, no hardcoded rules, no orphans) excludes version-propagation atomicity; no validator checks that a bump landed with re-synced dependents; and the agent-side template-version pinning the backstop would rely on is itself listed as an unresolved gap. This is exactly the A1 "rules in prose only" anti-pattern the architecture prohibits.
*Fix:* add a sentinel check asserting a template/contract version bump shipped with its dependents re-synced (compare consumers' pinned version to current).
*Location:* governed-pipeline-architecture.md:705 (R9), :763 (§29); implementation-plan.md:167, :220.

**[part-unsound-or-unrealized] Part I — the FR→AC→task→test cross-artifact traceability validator has no plan home.**
Part I names cross-artifact consistency drift (72 instances) as the single largest finding category and the headline ~75% mechanical-findings win leans on catching it, yet the plan builds only four *per-doc-type* validators plus a *structural* completeness check. No deliverable builds the cross-artifact content-chain validator, so this dimension stays "reviewer judgment" — the status quo Part I criticizes. (A secondary minor gap: doc_type frontmatter emission on planning-side authoring agents is also un-homed.)
*Fix:* add a cross-artifact FR→AC→task→test coverage validator to WS-1; add a doc_type-emission edit to the planning-side authoring agents.
*Location:* governed-pipeline-architecture.md:51, :120; implementation-plan.md:155, :167.
*Note:* the flag's third sub-claim (no Write/Edit defense-in-depth hook) did **not** survive verification — the producer-self-check + orchestrator-gate + CI triad is the architecture's chosen defense-in-depth and no harness hook is owed. Only the traceability and doc_type gaps stand.

**[part-unsound-or-unrealized] Part III — the "consumer pre-flight" gate is named as one of four keystone gate primitives but has no plan home.**
The cheapest-first stack names producer self-check, boundary validator, consumer pre-flight, and reviewer; pre-flight gets its own timing-table row ("before the consumer reads," distinct from the boundary validator "at the stage transition") and its own node in Figure V5/V6. The plan builds the other three; pre-flight is the only primitive with no change target and is not subsumed by the boundary gate.
*Fix:* either add an explicit pre-flight deliverable, or state explicitly that the per-edge gate model intentionally collapses the boundary and pre-flight firings into one.
*Location:* governed-pipeline-architecture.md §8, §9 timing table, Figure V5/V6; implementation-plan.md:158-159, :165-167.

### MINOR

**[rule-not-enforced] R13 — no check asserts gate→event emission.**
A8 ("a gate you can't measure can't be pruned") is realized by no deterministic check: the sentinel's five assertions exclude emission, and the completeness check verifies edges have gates, not that gates emit. A gate silently failing to call the emitter is caught by nothing. Minor because emit never blocks a run — harm is dead/unfalsifiable gates, not wrong output.
*Fix:* add an emission-coverage assertion to the sentinel — every manifest gate id appears as a `gate.result` source / has an emit call.
*Location:* governed-pipeline-architecture.md:704, :768; implementation-plan.md:167, :272.

**[part-unsound-or-unrealized] Part IV — freshness gate's "every handoff" placement is only wired into the reconciler.**
The architecture fires the freshness gate at every handoff AND reconciliation re-entry, but the plan explicitly wires `validate_freshness.py` only into the reconciler. The per-handoff half rides implicitly on the manifest `gate-per-edge` without being named. Mechanism is sound and an adjacent home is plausible — recoverable.
*Fix:* add a WS-1c/WS-1d deliverable wiring `validate_freshness.py` as a named per-edge gate kind in `pipelines.yaml`.
*Location:* governed-pipeline-architecture.md:401, :305; implementation-plan.md:179.

**[part-unsound-or-unrealized] Part VII — "one decision per ADR, stable IDs never renumbered" has no plan home.**
WS-3 ADR hygiene covers status-casing, relocating the two superseded ADRs, and two-way links, but no one-decision-per-ADR check and no stable-ID/no-renumber guard. Minor: it is an existing convention and the cross-link-integrity validator partly protects stable IDs transitively. (Thin spot, not a gap: the MCP query surface's "context-budget discipline" is carried only as an adjective without timeouts/truncation named.)
*Fix:* add a one-decision-per-ADR + no-renumber assertion to the cross-link-integrity validator.
*Location:* governed-pipeline-architecture.md:651, :652; implementation-plan.md:241, :239.

### CREDENTIAL-LEAK

None. No confirmed defect involves a real credential-leak path. (The closest adjacent item, the tool-governance probe, is a false-PASS reachability bug, not a credential exposure.) No zero-trust or compliance scope-creep is in scope here.

## 3. Schedulability Note

The DAG is schedulable: acyclic, all edges forward, no consumer scheduled before its producer. The one real ordering hazard — the run-event emitter (`emit_run_event.py`) shared by WS-0, WS-1f, and WS-4a — is correctly resolved producer-first in WS-0. Critical path is **WS-0 (M) → WS-1 → WS-4 → Close-out**. WS-3 sits safely off-path (feeds Close-out only) and can run in parallel.

Three sizing caveats for human attention, none of which break schedulability:

- **WS-1's "aggregate XL" understates the path.** Internally it is a hard sequence — contracts → validators (L) → manifest (L) → freshness (L) → orchestrator (XL) → reviewer hardening (M) — because the orchestrator consumes `pipelines.yaml`. The true length is that L+L+L+XL+M chain, dominated by the orchestrator sub-task.
- **WS-4a (sized L) carries the heaviest external risk on the path:** the young single-vendor GreptimeDB backend choice, single-container OTLP-HTTP ingest, durable-volume persistence across rebuild, and the SDK-free OTLP bridge — plus the low-maturity RFC-8785 library in WS-1d. Effort and risk run hotter than a flat L.
- **Close-out (XL) is a strict fan-in** waiting on all four upstreams and bundling the multi-pipeline migration, the single warn→enforce flip across all gate families, run-pinning, the discipline skill, and the improvement-loop capstone (which itself needs WS-4 observability + the WS-0 corpus). Nothing in it can start until WS-4 completes.

Several major mechanism defects above (idempotency keys, freshness graph reconciliation, reviewer-panel recovery) concentrate in **WS-1f** and **Close-out** — the two coarsest, latest, highest-risk nodes — so the fixes land on the part of the path with the least slack. Worth sequencing those fixes early rather than at the enforce-flip.