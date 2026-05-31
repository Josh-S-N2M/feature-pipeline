# Failure-modes + rule-completeness + KB-governance — research (for review)

> research-and-verify 2026-05-30 (wf_b4c9d9bc-c75; 65 agents, ~2.6M tokens). Verified-subset; could-not-verify at foot.

Consensus answer follows.

---

# Making architecture rules + anti-patterns complete and detectable

## Thread 1 — Failure-modes technique

**Consensus (plain English).** There is a mature, settled practice for turning a system into a structured failure catalog: **FMEA** (Failure Mode and Effects Analysis). For each element you enumerate every way it can go wrong, its effects, its causes, the controls already in place, and a remediation. Crucially, **detectability is a first-class, scored dimension** — FMEA rates each failure on Severity, Occurrence, and **Detection** (1 = certain to catch, 10 = certain to miss). The modern automotive handbook (AIAG-VDA, 2019) replaced the old "multiply into one number" (RPN) approach with **Action Priority** lookup tables and split remediation into two columns — *Preventive* action and *Detection* action — which is exactly the "what good looks like + how we'd catch it" pairing you want.

For software specifically, the practice lightens: NASA's handbook still mandates a named **detection method + compensating provision per failure mode**, but practitioner variants (SW-FMEA) **drop numeric scoring entirely** and instead use a fixed set of **guidewords** (non-execution, untimely, incorrect result, wrong state transition, stale data, corrupted config, interface mismatch) to enumerate malfunctions systematically. The complementary techniques are settled too: **fault-tree analysis** (top-down "how could this hazard happen?") pairs with FMEA (bottom-up); **misuse/abuse cases** enumerate hostile/negative scenarios with explicit *prevents*/*detects* relations and a "check completeness — was a critical case omitted?" step; and **assurance cases / GSN** structure the positive argument (Goals → Strategy → Solution-evidence) with an explicit **"undeveloped" node** that makes an *unaddressed* concern visible by construction.

**The key insight for your situation:** FMEA's effectiveness "rests on accurately enumerating possible failure modes — *no work is done on unimagined failures*." This is precisely your gap. Misuse-case / hostile-intent analysis is the recommended technique that *feeds* FMEA the scenarios it would otherwise miss.

**Effective vs. bureaucratic (settled, well-sourced).** Scope to one function not the whole product; write the scoring rubric *before* the workshop and anchor scores to real controls and defect history; force every entry through the full cause→local→next→end-effect chain; **link each row to artifacts** (failure mode→spec, detection control→a test case that "proves whether controls are real," action→a ticket with owner, residual risk→a review gate); and define explicit **re-review triggers** (interface/architecture changes, serious failures) — otherwise "living document" is just a phrase. For low-consequence systems, skip the heavyweight version and use lightweight design review.

## Thread 2 — Agent knowledge/skill governance

**Consensus (plain English).** The "declared vs. loaded vs. used" gap is **real, recognized, and currently under-governed** — this is the least settled of the three threads.

Anthropic's own model makes the three states structural: at startup only each skill's **name + description** load (declared); the full `SKILL.md` body loads only when the model judges it relevant (loaded); whether instructions are acted on is a separate question (used). In Claude Code, a subagent's `skills:` frontmatter **preloads full content deterministically**, but this controls only *what is preloaded, not what is accessible* — the subagent can still discover/invoke unlisted skills at runtime via the Skill tool. Skill descriptions live in a context budget (~1% of the window); on overflow, least-used descriptions are dropped first, **silently stripping the keywords the model needs to match a request**. After compaction, invoked skill bodies are re-injected but capped (5K/skill, 25K total, oldest dropped). `/context`, `/memory`, and `/doctor` report what actually loaded.

**"Declared ≠ loaded" is empirically observed, not theoretical:** a confirmed bug showed a `skills:` frontmatter entry that did *not* inject content (verified by searching for unique strings); agent-scoped skill loading is an open feature request; `disallowedTools: Skill` does not reliably prevent auto-invocation. This **justifies auditing actual load/use rather than trusting configuration**.

For auditing, the converging substrate is **OpenTelemetry GenAI semantic conventions** — `invoke_agent`/`execute_tool` spans show "what the agent decided to do, not just what tokens it emitted." But the spec is still *Development*-stage and explicitly **does not cover** which-skill-loaded or declared-vs-used governance signals — **you must author those as your own namespaced attributes.** Microsoft's agent-governance-toolkit RFC confirms the gap: existing governance checks tool *names* but has no skill dimension and doesn't tag audit events with `skill_name`/`skill_origin`; it proposes a `validate_skill()` hook before load. A working file-based pattern (`ai-loadout`) records load/use to append-only JSONL and flags **dead entries (never loaded), budget drift, and keyword-routing overlaps** — a concrete model for your `.claude` layer.

## Thread 3 — Rule-set completeness (conformance vs. completeness)

**Consensus (plain English, well-settled).** The distinction you hit is **canonical and documented**. SEI states it directly: a **conformance review** checks the description against a normative spec ("does it obey the shalls?"); a **separate coverage review** asks whether every stakeholder concern is *addressed by something* — and "questions revealing **missing** stakeholders or **missing** concerns are the most critical." SEI further names the exact class you fell into: **architectural concerns are decisions that should be made *whether or not they're expressed as requirements*** — including *internal requirements* (derived, not in any doc) and *issues* (surfaced only by analysis). A concern can be real and obligatory yet have **no written rule to conform to**. That is your missing KB-load concern precisely.

**The instruments for testing coverage** are settled: **ISO/IEC 42010** requires every stakeholder concern be explicitly addressed (enumerate stakeholders → concerns → confirm each is covered); **ISO/IEC 25010** gives a nine-characteristic quality checklist used to "validate the comprehensiveness of requirements"; **arc42** recommends 25010 as a checklist and provides a *Crosscutting Concepts* section where a concern like "which knowledge loads into which agent" would live — **a missing entry there is a coverage gap, not a conformance violation**; **AWS Well-Architected** is a living checklist *grown from root-cause analyses* of past failures (its Sustainability pillar, added late, is itself proof a checklist can have blind spots).

**The review techniques that actually catch a missing concern** (conformance cannot): **ATAM**'s two-pronged elicitation (top-down utility tree + bottom-up stakeholder brainstorm) surfaces unmade decisions; **Active Design Reviews** (Parnas & Weiss) flip the script — *designers* pose questions to reviewers, phrased so they can't be answered yes/no, forcing study that surfaces *absences*; assurance-case **undeveloped nodes** make gaps visible. The framing: **conformance asks "do we obey what's written"; completeness asks "is every concern in the taxonomy addressed by something written."**

---

## Settled vs. contested

| Thread | Settled | Contested / emerging |
|---|---|---|
| 1 Failure-modes | FMEA as the catalog method; detection as a scored axis; FTA + misuse-cases + assurance-cases as complements; "no work on unimagined failures" | Whether to keep numeric RPN/AP scoring or drop it (SW-FMEA drops it; automotive keeps AP). Pick per consequence level. |
| 2 KB/skill governance | Anthropic's progressive-disclosure load model; declared≠loaded is real and observed; OTel gives the span skeleton | **No standard governance layer exists.** Skill-as-governance-surface is an open RFC; OTel governance attributes are app-defined; tooling is nascent. |
| 3 Completeness | Conformance vs. completeness is canonical (SEI, 42010); coverage instruments (25010, arc42, Well-Architected) and review techniques (ATAM, Active Design Reviews) are mature | Little contested; the only judgment call is *which* taxonomy/checklist to adopt. |

## Confidence per major claim (load-bearing = verified citations only)

- **High** — FMEA structure, detection as scored axis, AIAG-VDA Action Priority + preventive/detection split (UCD Agile; fmea-training; NASA SWEHB; Sheridan; microTOOL — all verified).
- **High** — SW-FMEA lighter variant drops scoring, uses guidewords (sres.ai — verified).
- **High** — FMEA misses unimagined failures; misuse cases feed it (Alexander IEEE 2003; Sindre & Opdahl — verified).
- **High** — Misuse/abuse cases with prevents/detects + completeness check; OWASP lightweight protocol (verified). *Caveat:* "orphan misuses" anti-pattern source partially misattributed (see below).
- **High** — Anthropic skill loading: 3-level disclosure, `skills:` preload vs. runtime access, context budget/compaction caps, `/doctor` (Anthropic eng post; Claude Code docs — verified).
- **High** — declared≠loaded empirically observed (issues #46311, #57154, #39579 — verified, with one token-cap sub-claim mis-bundled, see below).
- **High** — Skill-as-governance-surface gap (Microsoft RFC #1609 — verified); ARC framework models monitoring/audit gaps as governable risks (arXiv 2512.22211 — verified); capability-identity gap + three requirements (arXiv 2603.14332 — verified); `ai-loadout` registry pattern (verified).
- **High** — Conformance vs. completeness; "concerns whether or not expressed as requirements"; "missing concerns most critical" (SEI TN-030; SEI DTIC training — verified); 42010 completeness; 25010 nine characteristics + comprehensiveness use; arc42 checklist + crosscutting + two-tier quality scenarios (verified).
- **High** — ATAM risk-discovery + utility tree (CMU/SEI-2000-TR-004 — verified; "we haven't decided that yet" phrasing unverified verbatim). Active Design Reviews (Parnas & Weiss — verified).
- **Medium** — OTel GenAI as the audit substrate: the *philosophy* and Development-stage/governance-gap points are verified (SentryML); the **specific attribute names** (`gen_ai.tool.definitions`, etc.) come from the official OTel spec, **not** the cited blog — attribute names need direct spec confirmation before you hard-code them.
- **Medium** — Assurance cases / GSN structure (Goals/Strategy/Solution, undeveloped node, completeness sub-goals): substance verified via Hawkins & Kelly pattern catalogue and NIST IR-7608; but see could-not-verify for the specific GSN-standard date and the "defeaters" mechanism.

## Could-not-verify — do NOT rely on these

1. **Claude Agent SDK `InstructionsLoaded` hook with `load_reason` field** (o-mega.ai). **REFUTED.** No such hook exists in the official SDK (21 events enumerated; this is not among them). Deferred MCP-schema loading is real but is a Claude Code opt-in, not an SDK default. *Do not build your audit on a non-existent SDK primitive.*
2. **"OMG SACM unifies GSN+CAE" and "defeaters surface gaps"** attributed to NIST IR-7608. **Unverified** — those terms don't appear in that 2009 doc (it predates SACM). The *defeaters* concept is real in the broader literature but needs a correct source. The directed-graph claims/arguments/evidence framing *is* verified.
3. **GSN Community Standard date "2015-03-01"** — wrong; the standard is November 2011 (FAA URL is a hosting mirror). The technical GSN content is verified; only the date/attribution is off.
4. **OTel GenAI specific attribute names** (SentryML blog) — not in that source; confirm against opentelemetry.io directly.
5. **"Orphan misuses" general claims** (Dundee paper) — the orphan-misuses point is verified; the bundled "negative inverse / mis-actor / beyond security to -ilities / test cases" framing belongs to Sindre & Opdahl, not that paper.
6. **Compaction token caps (5K/25K)** bundled under issue #39579 — that issue supports the first three skill-loading gaps but **not** the token-cap numbers; those are sourced to the context-window docs (which *do* verify them). Cite the docs, not the issue, for the caps.
7. **Databricks "industry consensus" + definition-drift** — the access-control/runtime-monitoring/registry thesis is verified, but it's one vendor's stance (not "consensus"), and its freshness story is about stale *data*, not stale agent *definitions*.

## Implications for your project

**(a) Author a rules+anti-patterns → failure-modes → good-state → detection catalog.** Build one table, one row per failure mode, with columns: *originating rule/anti-pattern (or "no rule — gap")* · *failure mode (use software guidewords)* · *cause* · *effect chain* · *what-good-looks-like* · *detection mechanism (linked to a real check/test/span)* · *Action Priority or High/Med/Low* · *remediation (owner + ticket)* · *re-review trigger*. Seed the failure-mode column with **misuse/abuse-case hunting** ("who/what would make this go wrong?") so you catch *unimagined* failures, not just the ones your existing rules imply. Keep it agile: scope per concern, rubric-before-workshop, link every detection cell to something executable, and add explicit re-review triggers. Critically, **add a row for "concern with no rule"** — make the gap class itself a catalog entry.

**(b) Add a knowledge-base lifecycle rule class that makes KB-load/usage gaps detectable.** Treat "which KB skill loads into which agent in which context" as a **crosscutting concern** (arc42 §8) with its own rule class — *declaration*, *load*, *use*. For each agent, declare expected skills; then audit empirically against the three states: emit your own **namespaced governance attributes** (e.g. `proj.skill.declared`, `proj.skill.loaded`, `proj.skill.used`, `skill_origin`) on agent/tool spans, since OTel won't give you these. Adopt the `ai-loadout` pattern — append-only JSONL of load/use events with **dead-entry detection (declared-but-never-loaded)**, **budget-drift**, and **routing-keyword overlap** checks — as the detection mechanism. Use `/context` and `/doctor` as the manual cross-check that frontmatter declarations actually loaded and that the description budget didn't silently evict keywords. This converts your past silent failure into a first-class, detectable rule violation.