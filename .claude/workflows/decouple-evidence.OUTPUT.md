# Decouple-evidence — architecture refactor playbook (RUN OUTPUT, for review)

> 2026-05-30 (wf_de4e5c84-7e0; 51 agents, ~2.4M tokens). Report-only refactor PLAN — the rewrite is a single-context pass after the no-loss attestation is clean.

I've confirmed the lossy source lines (notably the "to stay on the cheap default" cost-causality clause at line 813, and the §18 offline-eval change-type enumeration at line 509). I have everything needed. Assembling the four deliverables.

---

# 1. REFACTOR PLAYBOOK

Edits grouped by section. Each entry: **strip** → **replace with**. Intra-document refs (§N, Part N, Rn, Dn, TBn, Vn, figure ids) are KEPT throughout — they are document structure, not codebase citations. All `derived_from`/`pipelines.yaml`/`git`/product-name tokens generalize as noted.

## Part I — §1 Executive summary
- **Line 17** — strip the "see Appendix A" pointer and the "three-quarters" figure but **keep the epistemic hedge** (lossy-fix). Replace: *"Cheap, mechanical defects — a missing section, a broken cross-reference, a stale predecessor — slip past the unguarded seams and are caught only by the most expensive agents downstream, after they have already triggered rework. The large majority of defects fall in this mechanical class — a categorization estimate, not a measured rework-time share — exactly the class a deterministic check can catch, not substantive design flaws."* (Relocate the 125-of-165 figure + Appendix-A provenance to the evidence file.)

## Part I — §2 Problem A
- **Line 27** — strip "Four of seven … one more." Replace: *"Validation between stages is uneven: many stage-to-stage handoff seams are ungated, and some rely only on a human approval gate rather than a deterministic check."*
- **Line 28** — strip the four named documents. Replace: *"The lightest-weight artifacts tend to lack a machine-readable contract or a wired validator, leaving them unguarded."* (Relocate the named list to the plan so Appendix A's reference resolves.)
- **Line 29** — strip "reconciler / 4-cycle cap." Replace: *"Without an early gate, every defect propagates downstream to a reconciliation stage and re-invokes the expensive authoring agent, rather than being caught and triaged immediately at its source."*
- **Line 30** — keep nearly verbatim (already abstract): *"When authoring agents reference templates without pinning a version, contract drift goes undetected, and a field rename propagates silently."*
- **Line 31** — keep verbatim incl. `(Part IV)`.
- **Line 32** — generalize "install events" → "setup/install events"; keep `(Part V)`.
- **Heading "Evidence — prior runs" + line 36** — relocate the 14/11/8 prose to the plan, **but leave an abstract survivor** (lossy-fix): *"Empirically, most runs that reach the audit stages require at least one reconciliation cycle — late-caught defects forcing expensive rework are the norm, not the exception."*
- **Lines 38–49 (prior-runs table)** — relocate verbatim to the plan. No principles-doc survivor needed (carried by §1 + line 36 survivor).
- **Line 51 (top revision triggers)** — strip counts (72/53/40, 125 of 165, "across all audit JSONs"). Replace: *"Defects sort into three classes — cross-artifact consistency drift, completeness/missing-section gaps, and substantive design problems. The first two are mechanical and deterministically catchable, and they dominate; only the third is genuinely substantive and worth an expensive auditor's tokens."*
- **Figure V1 (53–75)** — relocate the concrete 13-stage diagram to the plan. **Mandatory** (lossy-fix): leave an abstract survivor in the principles doc — either a one-line claim *"Leaks concentrate where light artifacts cross stage boundaries — early research-to-synthesis handoffs and late test-authoring / task-decomposition handoffs"* or a stage-agnostic leak flowchart. Sweep for residual "Figure V1" references.

## Part I — §2 "What enforces today"
- **Line 81** — strip `shared-document-reviewer`, named doc types, count "five." Replace: *"The structural enforcement that does exist is partial — a document reviewer applies a structural-plus-semantic gate to only a subset of document types, leaving the others uncovered."*
- **Line 82** — strip `verdict_findings_parity.py`, "(five surfaces)." Replace: *"A deterministic consistency check can hard-halt the pipeline when a reviewer's verdict contradicts its own findings — though today such checks exist at only a few surfaces."*
- **Line 83** — strip the two script names + named stage. Replace: *"Some stages do have deterministic close-gates wired in, but only a scattered few — enforcement is not systematic across all stages."*
- **Line 85** — strip the settings.json/PreToolUse/serena inventory. Replace: *"When validation is entirely orchestrator-driven with no automatic write-time enforcement, every gate depends on the orchestrator remembering to invoke it — there is no defense-in-depth, and a forgotten invocation silently skips the check."* (Relocate the hook-matcher inventory to the plan as brownfield baseline.)
- **Leaks table (89–95)** — relocate to the plan **including the "Why it bites later" column** (lossy-fix — that column is rationale, not inventory). Abstract claim already carried by §1/§2.

## Part I — §2 "The contract layer today"
- **Line 99** — strip "documentation KB," count "nine." Replace: *"A central documentation source may own templates and authoring disciplines for the pipeline's document types, yet contract coverage across those types is typically asymmetric — some fully specified, others barely."*
- **Contract-layer table (101–111)** — relocate the per-doc-type matrix to the plan. **Mandatory** (lossy-fix): carry the weight-vs-risk diagnosis into the principles doc — strengthen the line-99 survivor with: *"…and coverage tracks a document's perceived weight, not its risk."*
- **Line 113** — strip the three script names + named invocation sites. Replace: *"Validators can exist yet be effectively orphaned — present but invoked only at narrow points and never at authoring time, so they are available but unenforced."* (Relocate the two invocation sites to the plan.)
- **Drift-surfaces list (115–124)** — strip named doc types/KB/`doc_type:`/`version:`/FR-AC specifics; keep all seven drift modes abstractly (use the disposition's restatement verbatim). Relocate item 5's "produces a structural finding" consequence to the plan.

## Part I — §3 Problem B
- **Lines 127–139** — strip the per-domain coverage matrix, named domains, `engineering-domain-layers.yaml`, "only two," bundle part names. Replace with the disposition restatement, **plus** (lossy-watch) an explicit orphan-direction clause: *"…and nothing flags an installed-but-undeclared part."* Ensure the install-scope-tracking registry gap lands in the plan (it powers cross-scope orphan detection).
- **Lines 141–143 (gitnexus anecdote)** — relocate the worked anecdote to the plan; leave the abstract survivor (disposition's standalone row): *"Without a single source of truth that reconciles every install site, removing a domain becomes a manual hunt across many surfaces and predictably leaves orphans — particularly parts installed at a scope the removal never reached, which resurface until manually deleted."*
- **Figure V2 (145)** — relocate with its table to the plan. **Mandatory** (lossy-fix): fold the matrix-reads-at-a-glance rationale into §3: *"A coverage matrix exposes bundle gaps at a glance, which is why a table beats a redundant heatmap."* Sweep for residual "Figure V2" references.

## Part II / §4 / §6
- **§4 line 161** — keep; generalize "the plan" → "an implementation"; keep `(Appendix F)`.
- **§6 substrate table rows 1–7 ("Realized as" column)** — apply the disposition restatements (generalize file/skill names; keep Role column intact, D-ORCH-1/§18/Part V refs).
- **§6 Figure V3 nodes (ci/cs/mcp/git)** — genericize labels (CI/CD platform; Devcontainer environment; MCP servers; version-controlled repository). Keep load-bearing properties ("ephemeral single-container," "durable system of record").
- **§6 Figure V4 tech tags (val/obs)** — drop "Python" / "JSONL + backend" language tags; keep "deterministic gates" / "append-only log + projection."
- **§6 Platform-foundations intro (232)** — apply restatement; add *"The specific bindings for any given instantiation belong in that instantiation's plan."*
- **§6 Platform-foundations table rows (AI-agent platform / Devcontainer / Remote VCS / IDE / CI-CD)** — relocate concrete bindings (Claude Code, Codespaces, GitHub, VSCode, GitHub Actions) to the plan's platform-binding table; **keep abstract rows in the refactored §6** stating each role + why it is architecturally significant. Keep TB refs with whichever doc carries the row. (Note: D14 below depends on §6 keeping the substrate's binding status.)

## Part II–V — body mechanisms (apply disposition restatements; all preserved)
- **§9 lines 337, 340, 343, 346** — drop moving-field benchmark figures (~28%, ~26pp, k=3→"small odd-sized panel"), named tiers, named KB/classifier; keep all qualitative judge claims + D-DR-1. Relocate figures to evidence file.
- **§10 lines 356, 360** — keep §356 row verbatim; strip "Claude Code Dynamic Workflows" realization clause from §360, keep D-ORCH-1 + one-level-nesting rule.
- **§11 line 368** — keep as-is.
- **§12 lines 386, 390, 391** — keep as-is / keep Bazel/Dagster/dbt as external prior-art illustrations.
- **§13 intro (398), move 3 (402), Figure V7 (374–375)** — generalize `derived_from`→"recorded-derivation edges," `pipelines.yaml`→"declared manifest," `in-git`→"durable substrate of record"; keep the completeness-check rationale and TB2. Relocate concrete identifiers to the plan.
- **§15 lines 437, 444** — generalize "git"→"version control / derivation graph"; keep TB2, Part IV, OpenLineage/OpenTelemetry standards.
- **§17 line 460** — strip "the same per-agent record the workflow runtime already writes"; keep two-level telemetry + stateless-actors + V4.
- **§18 Recovery lines 495, 496** — generalize receiver list (git push→version-control pushes, Slack→message-delivery, MCP POSTs→generic remote POSTs); keep AWS-Powertools, atomicity rationale, stage.complete/gate.result.
- **§18 Export/Durability lines 486, 487** — strip "the plan names the product"; keep D13/D17 refs, SDK-free OTLP, backend-optional, no-WORM. Relocate product-naming provenance to plan.
- **§18 Online/offline line 509** — **lossy-fix**: keep the change-type enumeration. Replace: *"Offline evaluation replays the historical-run regression corpus against every change — a new gate, a contract bump, a manifest edit, a rubric/prompt change — for a concrete before/after, so each iteration is proven better, not merely different."* (Treat WS-0 as intra-document; it resolves in-doc.)

## Part VI–VIII (apply disposition restatements; three lossy-fixes)
- **§22 line 586** — **lossy-fix**: append the dropped third mechanism. Replace ending with *"…reference-counted teardown, finalizer-gated termination, and owner-reference-style orphan prevention."*
- **§23 line 606** — **lossy-fix**: keep the "MCP is itself a domain" reuse anchor. Append to restatement: *"(the integration layer is itself already governed as a domain — its platform/design knowledge bases plus an auditor — so this reuses that shape rather than building a new system)."*
- **§29 line 800, §35 lines 923, 932** — apply restatements (intra-document figure/section refs kept; drop only the filename link).
- All other §19–§35 rows (R29/R33/A27, routing-classifier, tiering, tool-governance lines 552/578/608/613/615/617/621/623, §24–§26 knowledge governance, §30 lifecycle, §31–§32 tables, §33–§34 worked example + metrics) — apply disposition restatements verbatim; relocate counts/incidents as marked.
- **§30 line 813** — **lossy-fix**: keep the opt-in↔cost causal link. In the principles survivor add: *"start optional services opt-in — running them only when needed is what keeps the environment on its cheap default footprint."*

## Appendices
- **Appendix A (938–951) entire** — relocate to a new `architecture-evidence.md` (heading, Direct/Inferred legend, header, all 8 rows). **Repair the dangling `(evidence: Appendix A)` at line 642** in the same change. Each row's design claim already lives in its home Part.
- **Appendix C (D9–D-FM-1)** — apply restatements. **D14 (989) lossy-fix**: do NOT relabel the orchestration *substrate* as plan-level — only the manifest filename and routing-code mechanics are plan-level; the substrate is an architecturally-significant binding (cross-ref D-PF-1/D-ORCH-1/TB7). Strip literal names, keep binding status.
- **Appendix D (1017–1033)** — relocate all citation clusters/ledgers to `architecture-evidence.md`; keep abstract claims + internal cross-refs in the principles doc. Header verify-note + verification-pass record travel to the evidence file.
- **Appendix F (TB1–TB11)** — drop the "Evidenced in" column entirely; fold surviving §N intra-doc anchors into the boundary cell prose; relocate repo-file citations (`devcontainer.json`, `.gitignore`, ADR-0039, `canonical.py`, `auditing-shared`, machine-types docs) to the evidence file. **TB1 lossy-fix**: keep the abstracted machine rationale — *"default = smallest tier meeting the platform's minimum core count; the platform's memory floor is a loose minimum, not the provisioned size; cost scales proportionally with size"* — even after dropping literal numbers. Abstract "128 GB"→"largest available tier." Editor watch: TB8 boundary body names "Python 3.x" (out of scope for the evidence-column strip, flag separately).

---

# 2. EXTRACTED-EVIDENCE CONTENT (paste-ready)

Two targets. **Rule for "either":** repo-run provenance and the evidence-map → **`architecture-evidence.md`**; brownfield change-targets, business-case projections, and concrete bindings the plan acts on → **`implementation-plan.md`**.

## A. New file `architecture-evidence.md` (create in same change)

```markdown
# The Governed Pipeline — Architecture Evidence

> Repo-specific provenance backing the architecture's design claims. Each row maps a
> mechanism to the observed problem and corroborating evidence in this repo's artifacts.
> Direct = the symptom appears verbatim in audit JSONs / version counts / removal records.
> Inferred = the most likely cause of an observed effect, not a single labelled incident.
> Verify links and dates directly before any ADR cites them — search output is input to
> verify, not ground truth.

## Evidence map (was Appendix A)

| Mechanism | Problem it solves | Evidence | Strength |
|---|---|---|---|
| Producer self-check + boundary validators (III) | Cheap mechanical errors caught only by the late auditor | 165 findings counted (Direct); the 125 "mechanical" split is by category mapping (Inferred-by-categorization); one run ran 7 audit rounds (Direct) | Direct / Inferred |
| Contracts for ATs / Phase Validators / Research Plan / tasks.json (I, III) | Template-less artifacts first seen by the cross-artifact auditor | ATs + PVs have no template; that seam is UNGATED | Direct |
| Manifest + gates-declared (III) | Silent gate removal; unguarded seams | 3 UNGATED + 2 reviewed-only seams; filename drift | Direct |
| Freshness gate (IV) | Stale-predecessor drift as upstreams are revised | 72 consistency findings incl. stale contract-ID refs + version desync; Blueprint v1–v5, PRD v1–v3 churn | Direct (symptom) / Inferred (staleness drove churn) |
| Observability (V) | Cannot tell where cycle time goes; runs stall invisibly | Only install telemetry exists; 3 runs stalled pre-audit with no recorded reason; every metric here is extrapolated | Direct |
| Domain registry + conformance/orphan check (VI) | Unpredictable add; orphaned removal | The ragged bundle matrix; one removal touched 15+ surfaces and orphaned a user-scope install | Direct |
| Knowledge governance: index + supersession + freshness/conflict (VII) | ADR sprawl; stale/conflicting memory | 68 ADRs + ~1,470 cross-references (approx., by grep) + no index + 2 live-but-superseded records; memory has no freshness/conflict field or check; multi-level memory is additive ("no override, no de-duplication") | Direct (counts approx.) |
| Maintainability / tiering (VIII) | Over/under-gating; meta-run fragility | Two runs are self-improving meta-runs; one was abandoned/split mid-pipeline | Direct |

## §1 / §2 / §3 source-text provenance (was inline)
- The "roughly three-quarters" figure = 125 of 165 findings; categorization estimate, not measured rework-time share. (was §1 line 17, "see Appendix A")
- Top revision triggers across all audit JSONs: cross-artifact consistency drift 72; completeness/missing 53; clarity/substantive 40. Categories 1+2 = 125 of 165. (was §2 line 51)

## Reviewer-gate research figures (was §9)
- Temperature-0 judge flipped verdict on ~28% of re-runs of one pair.
- Atomic human-authored rubrics beat self-generated by ~26pp.
- (See LLM-as-judge citation cluster below.)

## Citation clusters (was Appendix D 1017–1033)
[Paste verbatim: the header verify-note; the verification-pass record (10-of-13 verified,
withdrawn arXiv 2605.08563, non-existent OpenLineage AgentRunFacet RFC, scoped OTel post);
the Freshness/lineage/invalidation cluster; Observability cluster; Extensibility/plugin-registry
cluster; Durable-knowledge cluster; LLM-as-judge reliability ledger; Durable-execution ledger;
Architecture-diagramming vocabulary incl. Mermaid v11.x.]

## Technology-boundary citations (was Appendix F "Evidenced in" column)
- TB1: devcontainer.json; Codespaces machine-types docs.
- TB2: .gitignore.
- TB5: canonical.py.
- TB7: ADR-0045 (sole-dispatch enforcement; platform constraint T-001).
- TB8: auditing-shared.
- TB10: ADR-0039 (MCP credential discipline).
```

## B. Into `implementation-plan.md` (under WS-0 / business-case / platform-binding sections)

- **Prior-runs table (was §2 38–49)** — paste verbatim as brownfield motivation.
- **§34 metrics table (906–915) + aggregate (917) + caveat (919's "install events only" fact)** — paste as the business case quantifying the rollout payoff. (Plan currently has only a single "~75%" reference at lines 112/157 — this is net-new.)
- **Leaks table (89–95) including the "Why it bites later" column** — paste as the concrete leak inventory.
- **Contract-coverage matrix (101–111)** — paste as the contract-coverage audit.
- **Named lightest-document list (line 28)**, **orphaned-validator invocation sites (line 113)**, **hook-matcher inventory (line 85)** — paste as brownfield baseline so Appendix A references resolve.
- **Figure V1 concrete 13-stage diagram** and **Figure V2 + coverage matrix** — paste into plan.
- **Platform bindings** — Claude Code, GitHub Codespaces, GitHub, VSCode, GitHub Actions, and "Dynamic Workflows is the named orchestration substrate," `pipelines.yaml` filename, `derived_from` field name — paste into the plan's platform-binding/realization table (most already present at plan lines 39/178/181/191–195).
- **§29 reuse-source build instruction (lossy item #4)** — **net-new required write**: *"WS-0/WS-1: extract the execution pipeline's existing schema'd result artifacts, stub detection, and dimensional verdicts into the shared `auditing-shared` gating harness — do not grow a second harness."*
- **§30 machine-sizing detail (813)** — paste **with rationale**: 4-core/16 GB default; the 8 GB `hostRequirements` is a loose minimum not the provisioned size; smallest tier meeting the 4-core floor is 16 GB; resizable at proportional $/hr.
- **gitnexus anecdote (141–143)** + **tool-orphan incident (617)** + **serena-not-initialized incident (608)** — paste as brownfield motivation (mostly already at plan lines 66/229/232).

---

# 3. NO-LOSS ATTESTATION

Every design claim survives — restated in place or relocated. The 12 lossy-flagged items are resolved as follows; **the refactor is NOT safe to apply until each fix below is in the rewrite:**

| # | Item | Fix (must be applied) | Status |
|---|---|---|---|
| 1 | §1 line 17 | Keep the "categorization estimate, not measured rework-time" hedge in the survivor; relocate 125/165 + Appendix-A provenance to evidence file. | Fixed in playbook |
| 2 | §2 line 28 | Relocate named-document list to plan so Appendix A resolves; abstract survivor kept. | Fixed |
| 3 | §2 "Evidence — prior runs" line 36 | Add abstract survivor ("reconciliation is the norm, not the exception") — not a bare relocate. | Fixed |
| 4 | §2 contract-layer matrix (101–111) | Carry the weight-vs-risk diagnosis into §3/line-99 survivor before relocating the matrix. | Fixed |
| 5 | §2 line 85 | Relocate hook-matcher inventory to plan (baseline for the claim). | Fixed |
| 6 | Figure V2 (145) | Make the matrix-at-a-glance fold MANDATORY in §3; sweep residual "Figure V2." | Fixed |
| 7 | §18 line 509 | Keep the four change-type enumeration verbatim. | Fixed |
| 8 | §22 line 586 | Append "owner-reference-style orphan prevention." | Fixed |
| 9 | §23 line 606 | Keep the "MCP is itself a domain" reuse anchor. | Fixed |
| 10 | §29 reuse-source (companion relocate) | **Net-new required write** of the extract-execution-side build instruction into the plan; verify it lands. | Fixed — verify on write |
| 11 | §30 line 813 | Keep the opt-in↔cheap-default cost causality. | Fixed |
| 12 | Appendix C D14 (989) | Do NOT demote the orchestration substrate to plan-level; only filename + routing-code mechanics are plan-level. Substrate stays architecturally-significant (D-PF-1/D-ORCH-1/TB7). | Fixed |

Additional non-blocking carries already handled in the playbook: Figure V1 abstract survivor mandatory; §3 orphan-direction clause; §33 quantitative backing cross-referenced to §34/evidence file; the §33 "misses 13/14" datum — judged disposable severity-evidence, but if kept it lands in the evidence file (state the call explicitly rather than silently dropping). With all 12 applied, **the lossy list is empty.**

---

# 4. RISK NOTE (report-only)

**The plan's traceability spine is the dominant hazard.** `implementation-plan.md` lines 15–30 are built on the premise that the same code appears twice — "as *problem evidence* in the architecture, and as *change target* here" — and the plan cites architecture evidence inline (e.g. the "72 instances" at line 157, "~75%" at 112/157). Moving Appendix A and the metrics to `architecture-evidence.md` breaks that spine: the plan will point at evidence that no longer lives where it says. **Re-point the spine (plan lines 15–30) and every inline evidence citation at `architecture-evidence.md` in the same change.** This is the single most likely silent regression.

**Execution-order dependency: the evidence file must be created before/with the strip.** `architecture-evidence.md` does not exist and the plan holds none of this evidence yet. Several "preserved" verdicts are *conditional on the relocation actually executing* — Appendix A, Appendix D ledgers, the §34 metrics/aggregate, the §29 reuse-source instruction, the platform-binding rows. If the strip lands without the corresponding writes, evidence is destroyed, not moved. Treat every `relocate_*` as a paired (delete-here, write-there) transaction; verify the destination received the content, including rationale, not just numbers.

**Dangling internal pointers.** Repair `(evidence: Appendix A)` at line 642 when Appendix A leaves. Sweep for residual "Figure V1" / "Figure V2" references after relocating those figures (Appendix E catalog rows V1/V2, and any prose). Appendix E rows V13/V14 point at §33 — if §33's real-run narrative relocates, those catalog rows must relocate with it or they dangle.

**Cross-cutting binding coherence.** The platform-foundations rationale ("a platform swap is an architecture-level change," D-PF-1) is the umbrella over the genericized V3/V4 diagram nodes, the §6 table rows, and Appendix C D14/D-ORCH-1/TB7. If §6's abstract platform section is dropped, those genericizations orphan their "why." Keep an abstract §6 platform-foundations section; ensure D14 does not contradict D-PF-1 by mislabeling the substrate as plan-level.

**TB2 is load-bearing for §13.** The in-git derivation-graph relocation (move 3 / line 402) is lossless *only because TB2 survives* carrying the "anything that must survive rebuild is committed" rationale. If any sibling edit strips TB2, the substrate rationale orphans — keep TB2 intact.

**Terminology drift between genericized figures and concrete plan.** Figure V7's edge label genericizes `derived_from`→"derived-from upstream vN" while the plan keeps the literal field. Keep §13 move-1 terminology and the figure label consistent so a reader does not read them as two different mechanisms — a copy-edit coherence check, not dropped information.

**CANON-1 orphan (Appendix F TB5).** CANON-1 is referenced but never defined in the architecture doc; its real definition is a CI fitness check in the plan. Either define it in the principles doc or relocate its grounding — do not leave a bare undefined acronym.