# Failure-mode catalog + completeness review (RUN OUTPUT, for review)

> 2026-05-30 (wf_57a4b063-988; 21 agents, ~1.4M tokens). Coverage scan + FMEA over every rule/anti-pattern. Report-only — proposes new rules + the catalog for a human to fold in.

Now I'll assemble the foundation analysis from the provided coverage gaps and FMEA catalog.

---

# FOUNDATION ANALYSIS — Quick-Wins Hardening Pass

## 1. COVERAGE REPORT — missing concerns, severity-ranked

**Note on de-duplication:** the input lists prompt-injection twice (once as "security," once as "Safety") — they are one concern. Eight distinct gaps remain after merging.

### Major gaps (close these first)

| # | Concern | Why it bites | Proposed rule stub |
|---|---|---|---|
| 1 | **Untrusted-content / prompt-injection** — web/exa fetches, MCP tool outputs, authoritative-source re-checks (R23) feeding decisions | An injected instruction in fetched text could flip a gate verdict, mint a key, or trigger a write | Externally-fetched content is data, never instructions; it may inform a finding or flag staleness but may never alter a gate verdict, mint an idempotency key, or trigger a write without an independent deterministic check. |
| 2 | **Faulty/flaky validators** — a false-positive gate is an undetected outage | §29 names it; no rule (R1–R24) obligates fixtures | Every gate-library validator carries committed true-positive and true-negative fixtures and is itself a gated CI artifact; a validator without passing fixtures cannot be wired into the manifest. |
| 3 | **Toxic tool-capability combinations** — filesystem+web, db+network on one agent | The `auditing-mcp` OP-rules already exist but no pipeline rule enforces them | The tool registry's conformance check flags toxic capability combinations granted to a single agent and requires an explicit rationale, mirroring the OP-rule catalog. |
| 4 | **Destructive-operation guardrails** — `git reset --hard`, `rm -rf`, force-push, mass overwrite by an automated actor | R18 (supersede-not-overwrite) is the data-side analogue; nothing covers filesystem/VCS | Actors and the coordinator never run irreversible operations without explicit human-gate confirmation or a deny-by-default permission baseline. |
| 5 | **KB/skill registry governance** — declared assignment + load mode per agent | R22 does exactly this for *tools*; KB skills are ungoverned | Each KB skill is registry-declared with assigned agents and load mode; conformance asserts every agent's declared skill set exists and every installed KB skill is assigned to ≥1 agent. |
| 6 | **KB declared-vs-loaded-vs-used** — is loaded knowledge consulted; prune dead grants | Tool *usage* is observed (D-OBS-1); KB consultation is not | KB-skill load and consultation are observable per run so a never-consulted grant can be pruned and a missing-but-needed KB surfaced. |
| 7 | **All-pipelines-defined-the-same-way** + **uniform orchestration substrate** | Half-migrated pipelines drift; prose-defined pipelines escape the sentinel | Every pipeline (feature, execution, cc-critique, issue-capture, report-only, single-doc) is a manifest entry with a declared tier and runs on the one orchestration substrate; the sentinel flags orphan or prose-orchestrated pipelines. |

### Minor gaps (close after the majors)

| # | Concern | Proposed rule stub |
|---|---|---|
| 8 | **Secret/PII scan before commit** | A deterministic secret/PII scan gates any artifact before it is committed or packaged, since git history is permanent (TB2). |
| 9 | **MCP/tool supply-chain provenance** | A registry entry records provenance and a pinned version; add/update is gated on the pin so an unvetted/floating server cannot enter a run context. |
| 10 | **Concurrency / mutual exclusion** on shared durable state | Concurrent runs writing canonical, the registry, the knowledge index, or memory acquire a scoped lock or isolated working trees. |
| 11 | **Backward compatibility** for consumers outside the atomic commit | A breaking change to an externally-consumed surface (OTLP event schema, committed run-summary, cross-pipeline canonical) requires a compatibility window or migration step. |
| 12 | **Per-run cost/token ceiling** | A run declares a budget envelope per tier; the coordinator emits `budget.exceeded` and escalates to the human gate rather than spending unbounded. |
| 13 | **Sandboxing / deny-by-default permission baseline** | The execution surface declares which Bash/MCP/write operations each agent role may perform; the substrate audits no actor exceeds its role. |
| 14 | **Per-tool degradation contract** | Each tool registry entry declares its unavailability behavior (documented fallback or fail-loud) so an agent never silently produces degraded output mid-run. |

**The KB/skill load-use concern called out explicitly: STILL A GAP.** R22 governs *tools* (assignment, preload-vs-deferred, usage observation, dead-grant pruning), and §32 locates the discipline skill, but the equivalent discipline for *knowledge* is unwritten on both axes — registry assignment (#5) and load/consult observability (#6). The asymmetry is the finding: tools are governed, knowledge is not, and the architecture treats them as parallel everywhere else.

## 2. PROPOSED NEW RULES / ANTI-PATTERNS (id-less stubs for the human)

The seven rule stubs in §1's major table plus the seven minor stubs are the core proposals. Framed as the architecture's two forms:

**New rules (positive obligations):**
- *Untrusted content is data, not instructions* (gap 1).
- *Every validator carries true-positive/true-negative fixtures and is itself gated* (gap 2).
- *Destructive operations require human confirmation or deny-by-default* (gap 4).
- *KB skills are registry-declared, assigned, and load/consult-observable* (gaps 5+6 — one rule, two clauses, the R22 analogue for knowledge).
- *Every pipeline is a tiered manifest entry on the one substrate* (gap 7).
- *Secret/PII scan gates commit/package* (gap 8).
- *Per-tool provenance pin + degradation contract* (gaps 9+14).
- *Scoped locking on shared durable state* (gap 10).
- *Breaking-change compatibility window for external consumers* (gap 11).
- *Per-tier cost-budget envelope with escalation* (gap 12).

**New anti-patterns (named failures):**
- *Validator with no failing fixture* (the faked-coverage / Goodhart gate — co-occurs with A1, A10).
- *Toxic capability combination granted unaudited* (gap 3).
- *Orphan / prose-orchestrated pipeline* (the un-migrated pipeline — gap 7's negative form).
- *Destructive automated operation without confirmation* (gap 4's negative form).

## 3. CATALOG HEADLINES — highest-priority failure modes (grouped)

**A. Gate exists but never fires / can't be proven to fire**
- R2 → coordinator skips a declared gate on a reconciliation re-entry path → assert a `gate.result` precedes every downstream `stage.start` per edge.
- R3 → manifest edge has no gate, or malformed manifest loads silently → JSON-Schema-validate `pipelines.yaml` + keystone "every edge has a gate" sentinel; coordinator refuses a schema-invalid manifest.
- R8 → the sentinel itself never runs (CI trigger misses a path) → branch-protection audit + canary commit that introduces a deliberate orphan and asserts CI red.
- R13 / A8 → a gate decides but emits no event → harness wraps every gate so emission is inseparable from running; conformance cross-checks manifest gates against distinct gate ids in a reference run.

**B. Gate fires but lies or fails open**
- R2 → validator throws and the coordinator treats error as pass → `gate.result` carries explicit pass/fail/error; fixture injects a crash and asserts the run halts.
- R6 → a soft-fail / default-substitution branch defeats fail-loud → scan validators for `except: pass` and `.get(key, DEFAULT)` on required fields; fault-injection feeds malformed contracts.
- R13 → emitted verdict disagrees with the decision the coordinator acted on → serialize the *same* verdict object; assert any halt has a matching blocking `fail` event.

**C. Independence collapses**
- R4 / A3 → producer self-check mistaken for the independent boundary gate → assert author id ≠ validator id on the boundary `gate.result`.
- R20 / A20 → a provider outage or single abstain default-passes → unit-test the resolution truth table (any fail→fail, any abstain→escalate, no-quorum→fail-closed).

**D. Staleness ships silently**
- R11 / A11 → reverse-closure walk seeds from the manifest while digests live on the `derived_from` graph → bijection completeness check between the two graphs.
- R9 → content changes without a version bump → CI compares canonicalized content digest to the digest recorded for the declared version.

**E. Side effects duplicate or vanish on replay**
- R21 / A21 → key minted per-stage not per-side-effect, or cycle term dropped → static check (N writes ⇒ N keys); crash-injection in both windows asserts exactly-once; reconciliation regression asserts a cycle-2 write is not suppressed.

**F. Orphans survive removal**
- R14 / R15 / A15 → orphan check scans project scope only, returns clean while user-scope install lingers → enumerate project + user + MCP-config + devcontainer scopes; an unscanned required scope downgrades clean to inconclusive.

## 4. COMPLETENESS CRITIC — the unimagined-failure check, applied to ourselves

What neither the taxonomy nor the proposed rules covers:

1. **Human-gate authentication and non-repudiation.** Every escape valve routes to "the human gate," but nothing establishes *which* human, that they are authorized, or that the approval is tamper-evident. A21 protects machine side-effects with idempotency; the approval boundary that authorizes them has no equivalent integrity guarantee. An approval event could be forged, replayed, or attributed to the wrong identity and the whole gate stack would trust it.

2. **Clock / ordering trust.** R5, R11, R12, R18, R19 all depend on `written_at`, digests, and event timestamps to decide freshness, supersession, and replay order. Nothing addresses clock skew, a non-monotonic clock, or an actor that backdates an entry to win a recency-based current-view (R18). The bi-temporal model is only as honest as the timestamps fed into it.

3. **Observability backpressure / log integrity.** The run-event JSONL is the system of record for recovery (R21), ROI (R24), and nearly every detection above. No rule covers the log filling the disk, a slow append blocking the run, or the log itself being corrupted/truncated/tampered. The detection layer has no detection layer.

4. **Cascading-rollback semantics.** R9 lands fixes atomically and R18 supersedes-not-overwrites, but there is no rule for *reverting* a shipped change — how to roll back a promoted validator (R24) that proves harmful in production, or a contract bump whose compatibility window (gap 11) was misjudged. The flywheel can promote; nothing defines how it retracts.

5. **Cross-pipeline / shared-canonical blast radius.** Gap 11 names external consumers of the event schema; the deeper unmodeled case is two *pipelines* mutating the same canonical concurrently with semantically incompatible intent — gap 10's lock prevents corruption but not a logically-conflicting-but-individually-valid pair of edits.

Of these, **human-gate identity/non-repudiation (#1)** and **log integrity/backpressure (#2/#3)** are the most load-bearing: every other mechanism in the architecture ultimately trusts the human approval and the event log, and neither currently has an integrity rule guarding it.