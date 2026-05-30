# Document-critique — architecture + plan (RUN OUTPUT, for review)

> Output of `document-critique` run 2026-05-30 (wf_62d0ab08-1c1; 46 agents, ~2.0M tokens). Report-only — findings adversarially verified. No blockers.

All key findings verified against source. The contradiction at line 27/87 (prose says "three ungated + two reviewed-only") versus the figure and table (four ungated + one reviewed-only) is confirmed, as is the 8gb-vs-16GB discrepancy. Producing the report.

---

## Prioritised fix list

No blockers. The verification pass surfaced no logic-breaking or capability-missing defect; the heaviest items are quantitative self-contradictions and a sequencing inversion.

### Major

| # | Problem (one line) | Fix (one line) | Touches |
|---|---|---|---|
| 1 | Run-event log is consumed by the orchestrator workstream but produced two workstreams later, so the consumer is scheduled before the producer. | Move a minimal run-event log into the early foundation workstream (WS-0/WS-1) and have WS-4a extend it, or state the forward dependency explicitly and revisit the WS-1→WS-4 graph edge. | `implementation-plan.md` WS-1f (lines 189-190), WS-4a (254-258), graph edge (line 101) |
| 2 | Ungated-seam count contradicts itself: prose says "three ungated + two reviewed-only" but the figure and leak table both show four ungated + one reviewed-only. | Change both prose counts (lines 27, 87) to "four ungated seams and one reviewed-only seam" to match the figure and table. | `governed-pipeline-architecture.md` §1 line 27, §2 line 87 |
| 3 | One durability decision (crash-recovery journal / run-event replay) is "Implemented" in two workstreams, breaking the plan's own "exactly one home" rule. | Keep WS-4 as the sole home; reword WS-1f's reference from "Implements" to "depends on (built in WS-4)". | `implementation-plan.md` line 39 vs WS-1f line 185/190 and WS-4a line 248/258 |
| 4 | The default-machine spec is stated flatly as "4-core/16 GB" with no citation, conflicting with `devcontainer.json` which declares 8gb. | Add the same caveat the appendix already uses ("8 GB floor is a loose minimum, not the provisioned size") and cite the Codespaces machine-type source, not hostRequirements. | `governed-pipeline-architecture.md` §30 line 792 |
| 5 | A plan deliverable says to "generalize the mcp-availability-probe," but no such artifact exists; the real probes are `mcp-ping.sh`/`mcp-auth-probe.sh` in `.devcontainer/lib/`, not the workflow portfolio. | Either name the real seed string and correct the location, or mark the deliverable net-new rather than a generalization. | `implementation-plan.md` WS-2 line 222; `governed-pipeline-architecture.md` line 615 |

### Minor

| # | Problem (one line) | Fix (one line) | Touches |
|---|---|---|---|
| 6 | WS-1 header omits D15 (Strangler-Fig) though the map and sub-workstream both place it in WS-1. | Add D15 to the WS-1 Implements header (between D14 and D16). | `implementation-plan.md` line 137 |
| 7 | The keystone deliverable (the pipeline manifest, WS-1c) lacks the per-sub-workstream "Implements" line every sibling carries. | Add an Implements line to WS-1c naming D2 (and any others it realizes). | `implementation-plan.md` WS-1c lines 160-166 |
| 8 | Two adopted decisions (registry-driven auditor dispatch; context-file DRY) are never named individually — only swept into range shorthand, so grep returns zero hits. | Name D-DOM-3 and D-KN-4 explicitly in the WS-2 and WS-3 Implements lines. | `implementation-plan.md` lines 211, 231 |
| 9 | A "see ... above" cross-reference points to a subsection that actually appears below it. | Change "above" to "below" (or to an explicit Part/section anchor). | `governed-pipeline-architecture.md` §18 line 495 |
| 10 | Two references treat "Operational recovery" as part of numbered §18, but it is an unnumbered subsection sitting after §18's body. | Either number the recovery subsection or reword references to "the Operational recovery subsection following §18". | `governed-pipeline-architecture.md` line 5, §13 line 404 |
| 11 | The decisions register defines D-DOM-4 out of order, separated from its three siblings by the whole D-* block. | Move the D-DOM-4 entry up to sit with D-DOM-1..3. | `governed-pipeline-architecture.md` Appendix C lines 973-990 |
| 12 | A few citations carry a year only, weaker provenance than dated peers in the same groups. | Optionally upgrade to publisher-stated month-level dates where available. | `governed-pipeline-architecture.md` Appendix D lines 1002, 1004 |

The seven PASS findings (no vendor leakage, all named tech within boundaries, decision-anchored vendors, ADR-0068 accuracy, the properly-hedged "three-quarters" metric) need no action and are noted only so the next pass does not re-litigate them.

---

## Completeness critic — what we did not cover

The seven lenses here were all **document-internal**: consistency between prose/figure/table, decision-to-workstream traceability, citation hygiene, boundary compatibility, and cross-doc coherence. They verify the architecture and plan agree *with each other and with themselves*. Several risk classes sit entirely outside that frame and need a human eye:

- **Technical soundness of the design itself.** No lens asked "is the run-event-log replay/idempotency model actually correct, or does it have a race or double-apply bug?" Internal consistency is silent on whether the agreed mechanism *works*. The durability and crash-recovery semantics deserve a hand review against a real concurrency/restart model.
- **Effort, sequencing realism, and critical path.** We caught one ordering inversion by traceability, but nobody assessed whether the workstream sizing is plausible, whether the dependency DAG has a feasible critical path, or whether "opt-in observability backend" survives contact with real Codespaces resource limits.
- **Security and credential-flow review.** The vendor-boundary lens confirmed names are *classed* correctly, not that the secret-handling design (Codespaces Secrets, env-block indirection, private port visibility) is *safe*. A dedicated security pass on the observability backend's data egress and the MCP credential surface is warranted.
- **The reciprocal direction of traceability.** Lenses checked that plan decisions trace *up* to the architecture. The inverse — does every architectural decision (D1–D18 and the D-* families) have a realizing deliverable, with no orphan decisions — was only spot-checked. A full architecture-to-plan coverage sweep would close that.
- **External fact-check of cited prior art.** We confirmed citations are *present and dated*, not that GreptimeDB, the rfc8785 library version, or the "engines converge on one pattern" claim are *accurate as of today*. A current-sources verification (the recent-consensus discipline) should confirm the technology-evaluation conclusions still hold before any ADR freeze-lift.

Net: this pass hardens the documents' internal integrity well; it does not certify the design is correct, secure, or schedulable. Route those four to a human or a substantive-design review before implementation.