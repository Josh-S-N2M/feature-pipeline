# `.claude/workflows/` — Workflow Portfolio (operating manual)

This directory holds the project's **dynamic-workflow** scripts and this manual. A workflow is a deterministic JavaScript script that orchestrates many fresh-context sub-agents under ordinary control flow (`parallel` / `pipeline` / phases). It is the design-time embodiment of the architecture's own thesis — *deterministic code governing probabilistic actors* — so each workflow maps to a substrate role: research feeds the **evidence** layer; critique is the **design-time sentinel** for the documents; the build workflows are the **producers**.

**How to run one.** Invoke the Workflow tool with `{name: "<name>", args: {...}}`, or as a `/<name>` slash command. Watch/▸ manage with `/workflows`. Runs are background + report findings; **report-only workflows write nothing** (safe under a write-freeze); **build-time workflows write code** (run only after the freeze lifts).

**Keep the portfolio small.** Proliferation is an anti-pattern (a workflow can spawn dozens of agents and burn tokens). Before adding one, give it a sharp *solves / does-not-solve* boundary — and check the "What is NOT a workflow" list below.

## Tool availability in the workflow-agent context (verified by probe)

A workflow-spawned agent reaches session MCP tools via ToolSearch (load-on-demand). Verified in this project's background context:

| Tool | Status | Note |
|---|---|---|
| Read · Bash · Write · Edit | ✅ available | built-ins, direct |
| `context7`, `exa`, built-in WebSearch | ✅ live | reachable, returning real results |
| Glob / Grep | ℹ️ deferred | load via ToolSearch, or use Bash (`ls`/`grep`) |
| **`serena`** | ⚠️ **needs init** | reachable, but a fresh agent has **no active project** — call **`mcp__serena__activate_project('feature-pipeline')`** before any serena symbol tool, else it errors "No active project". This is initialization, not connectivity/auth. |
| `claude.ai` servers (Gmail/QuickBooks/…) | ❔ may be absent | interactively-authenticated; can be missing in background runs. The portfolio does not use them. |

**Convention:** any workflow agent that uses serena symbol tools must `activate_project('feature-pipeline')` first (baked into `parallel-authoring` and `document-critique`). Research uses `exa`/`context7` (no serena); critique uses Read/Bash (serena optional); the build workflows use Read/Write/Edit/Bash.

---

## The portfolio at a glance

| # | File | Kind | Freeze-safe? | One-line job |
|---|---|---|---|---|
| 1 | `research-and-verify.js` | design-time | ✅ read-only | recency-filtered research with adversarial citation verification |
| 2 | `document-critique.js` | design-time | ✅ read-only | multi-lens, adversarially-verified conformance audit of the two docs |
| (3) | *(mode of #2)* | design-time | ✅ read-only | no-loss diff vs a prior version — pass `{prior:{...}}` to #2 |
| 4 | `parallel-authoring.js` | build-time | ❌ writes code | author independent code units in parallel, each verified |
| 5 | `migration-parallel-run.js` | build-time | ❌ runs migration | per-pipeline parallel-run diff + cutover-readiness (thin) |
| 6 | `technology-evaluation.js` | design-time | ✅ report-only | boundary-screen → score → verify a technology choice; drafts a decision record (spec: `technology-evaluation.DESIGN.md`) |

---

## 1. `research-and-verify`

- **Why.** We make non-trivial design recommendations that must rest on *recent authoritative consensus* — and single-pass research has produced fabricated/future-dated citations that slipped through unverified.
- **Problem it solves.** Breadth + recency + *claim trustworthiness*: a multi-angle sweep (official / community / technical) whose load-bearing citations are each independently verified to exist, be correctly dated, and actually support the claim.
- **What it does NOT solve.** It does not *decide* what to do with the findings (your judgment), does not verify *internal repo facts* (that's a critique lens), and does not keep the documents consistent. It produces evidence, not a decision.
- **How.** `parallel` sweep across angles → collect load-bearing claims → `parallel` adversarial verify each citation (default-distrust) → synthesise with confidence labels + an explicit could-not-verify list.
- **How it does NOT (misuse to avoid).** Don't wire its output straight into a doc edit — that removes the human judgment it exists to inform.
- **Where used / not.** Used: any design fork; repairing the architecture's Appendix D. Not: a fact already in the repo (direct read); a settled stdlib question.
- **When used / not.** Used: before a recommendation; before an ADR cites sources. Not: trivial/known facts; when the choice is taste, not evidence.
- **Args.** `{question: "...", today?: "recency note"}`.

## 2. `document-critique`

- **Why.** Our generation is strong; verification is ad-hoc and human-dependent. Mechanical drift, concept loss, category conflations, and arch↔plan misalignment have slipped through and been caught by luck or by the user.
- **Problem it solves.** Multi-lens, adversarially-verified review of the architecture + plan: internal consistency + cross-ref integrity; evidence traceability; category-conflation detection; arch↔plan linkage; one-plan coherence; technology-boundary compatibility (against Appendix F); a shallow citation-present-flagged check; and — in diff mode — concept loss vs a prior version.
- **What it does NOT solve.** It does not *fix* anything (report-only), does not *prioritise* the fixes for you, and does not do *deep* citation verification (that's #1 — this only checks citations are present and flagged).
- **How.** Decompose into lenses → `pipeline` (no barrier): each lens's findings start verifying as soon as that lens returns → each finding through an adversarial skeptic (survives only if un-refuted) → severity-rank → completeness critic.
- **How it does NOT (misuse to avoid).** Never auto-apply its findings — that buries a judgment call. It is the sentinel, not the producer.
- **Where used / not.** Used: the two documents (and any future doc). Not: mid-authoring; a one-line fix.
- **When used / not.** Used: after a substantive edit/reframe; before lifting the freeze; before an ADR. Not: after a typo.
- **Args.** `{arch?, plan?}` (default to the repo-root docs); `{prior:{arch, plan}}` enables **no-loss diff mode** (this is item #3 — a *mode*, not a separate workflow; run it only when a meaningful "before" version exists).

## 4. `parallel-authoring` — build-time

- **Why.** The plan's WS-1b (validators), WS-2 (scaffolding), WS-4 (KB bundles) author independent, schema-constrained units that can be authored in parallel and each corpus-tested as it lands.
- **Problem it solves.** Throughput on *independent* authoring units, each adversarially verified (corpus regression / smoke test) the moment it's written.
- **What it does NOT solve.** It does not handle *sequential, stateful* work (the orchestrator migration is a single-context Strangler-Fig job, not fan-out), and it does not replace human review of generated code.
- **How.** `pipeline(units, author-stage, verify-stage)` — no barrier; each unit authored then immediately verified. Units must target **distinct paths** so parallel writes never conflict (hence no worktree isolation, which would strand changes off the main tree).
- **How it does NOT (misuse to avoid).** Don't point it at units that share a file (split them or run sequentially); don't run it during a write-freeze.
- **Where / when used / not.** Used: WS-1b/WS-2/WS-4 independent units, **after the freeze lifts**. Not: WS-1f orchestrator migration; cross-unit shared state; during a freeze.
- **Args.** `{units:[{name, target_path, spec, verify_cmd}]}`.

## 5. `migration-parallel-run` — build-time (thin/borderline)

- **Why.** WS-1f / close-out migrate pipelines via Strangler-Fig + parallel-run: "for each pipeline, run both paths on a replay → diff → report."
- **Problem it solves.** Orchestrating the *per-pipeline iteration* of the parallel-run diff and collecting cutover-readiness.
- **What it does NOT solve / honest caveat.** The agent content is **thin** — it mostly runs the deterministic `parallel_run_diff.py`. It earns its keep only when iterating across **multiple** pipelines; for one pipeline, just run the script. Don't dress up a shell loop as an agent workflow.
- **Where / when used / not.** Used: multi-pipeline cutover, post-freeze. Not: a single pipeline; during a freeze.
- **Args.** `{pipelines:[...], diff_cmd?}`.

## 6. `technology-evaluation` — the decision arm

- **Why.** We pick technology by one-shot research that stops at "here's what the community uses" — the *evidence* step, not a *decision*. In AI/agent tooling the option set moves monthly, trade-offs go unweighed, and our architecture's boundaries (some tech *works* but doesn't *fit*) were never a filter. The portfolio had an evidence arm and an artifact-check arm but **no decision arm**.
- **Problem it solves.** Turns one open technology choice into a recorded, **boundary-filtered**, trade-off-scored decision with verified recent evidence and a built-in **re-evaluation trigger** so it can't silently rot. The boundary screen is a hard gate *before* scoring — a candidate that can't live in our constraints is eliminated cheaply, with the reason recorded.
- **What it does NOT solve.** It does not *decide for you* (human seam after Synthesize — you pick). It does not *write the ADR* (report-only; the draft becomes an ADR when the freeze lifts). It does not do *deep methodology* research on how to evaluate (that's a `research-and-verify` run). It is not for choices swappable behind a stable interface at low blast radius — those are plan-level picks, not boundaries.
- **How.** `Frame` (read the choice + `technology-boundaries.yaml` + `evaluation-rubric.yaml`) → `Enumerate` (parallel multi-angle discovery, seeded from the incumbent + last decision's candidates, dormant tail logged not dropped) → `Screen` (parallel; eliminate out-of-bounds; default-eliminate on uncertainty for hard boundaries) → `Score` (parallel; weighted anchored rubric, CoT-before-level, abstain allowed; totals computed deterministically in-script) → `Verify` (nested `research-and-verify` over the top 2–3 survivors' load-bearing claims) → `Synthesize` (rank + draft the decision record + the trigger).
- **How it does NOT (misuse to avoid).** Don't wire its draft straight into an ADR or a plan edit — that buries the human pick it exists to inform. Don't run it on a non-boundary choice. Don't skip the boundary screen to "save time" — it's the cheapest phase and kills most candidates.
- **Where used / not.** Used: the plan's provisional/owned technology choices (the observability backend pilot first); a fired re-evaluation trigger. Not: a settled stdlib pick; a choice with no boundary tension.
- **When used / not.** Used: when a provisional choice needs deciding, or its trigger fires. Not: mid-design brainstorming (that's conversation); a reversible low-blast-radius pick.
- **Canonical it reads.** `technology-boundaries.yaml` (the screen + fitness-function binding) and `evaluation-rubric.yaml` (profiles + criteria + anchors). Accessors in `canonical.py` are a WS-0 follow-on; until then agents Read the YAML directly (no inline copy — canonical-compliant in spirit).
- **Args.** `{decision:{role, plan_home, incumbent, prior_candidates?}, profile?, candidate_seeds?, max_candidates?, max_verify?, today?}`. Defaults to the observability-backend pilot.

---

## When to combine — and when not

"Combine" has three technical meanings; the rule differs for each.

| Mechanism | Combine when | Do NOT combine when |
|---|---|---|
| **Phases in one workflow** (`pipeline`/`parallel`) | Deterministic flow connects the steps **and** intermediate results need no human eyes (e.g. find→verify→synthesise inside #2) | A step's output needs a human decision before the next (split into two workflows with you in between) |
| **Nested `workflow()`** (one level deep) | A child is a reusable sub-step with no human seam (e.g. #2 calling a *shallow* citation check) | The child is expensive and you'd want to see its result first (don't nest *deep* #1 inside #2) |
| **Chained across turns** (you read results between) | The point is to keep you in the loop: research → *you pick* → critique → *you prioritise* → build | Never collapse a human decision out of the chain to "save a turn" |

**The concrete rules for this project:**
1. **#3 is folded into #2** (no-loss diff as a mode via `{prior}`) — same input, same cadence, no human seam.
2. **Do NOT fold #1 deeply into #2.** Deep citation verification is expensive and on a different cadence (research = when sourcing a decision; critique = after every edit). #2 does only a *shallow* "citations present + flagged" check and defers deep verification to a standalone #1 run.
3. **Never chain #2 → #4 without a human in between.** Critique findings must be human-prioritised before any build workflow acts — auto-fixing buries the judgment call.
4. **#1 nests inside #6** (`technology-evaluation`) as a single, cost-capped `Verify` run over the top 2–3 survivors' load-bearing claims — one level deep, not per-candidate. It still runs standalone for pure research. And **never chain #6 → an ADR/plan edit without the human pick** — #6 drafts; you decide.

---

## What is NOT a workflow (so we don't over-apply)

- **Document consolidation / merge** — single-context authoring needing one coherent voice + a fidelity check, not fan-out.
- **Rendering visuals, writing one ADR, a targeted edit** — single-context authoring.
- **Conversational design / recommendation** — judgment, not orchestration.
- **A single-pipeline migration** — just run `parallel_run_diff.py` (that's why #5 is gated on *multiple* pipelines).
- **Anything that writes outside an active write-freeze's allowlist.**

---

## Conventions for adding a workflow here

- `export const meta = {...}` must be a **pure literal** (name, description required; `whenToUse`, `phases` optional). State the *solves / does-not-solve* boundary in `description`/`whenToUse`.
- Read rules from `.claude/canonical` via `canonical.py`; no hardcoded constants (canonical-first, per the architecture).
- Use `schema` (plain JSON-Schema objects; no `oneOf`/`allOf`/`anyOf` at the top level) so findings return structured, not prose.
- Default to `pipeline` (no barrier); reach for `parallel` (a barrier) only when a stage genuinely needs all prior results at once.
- Mark each workflow **report-only** or **writes-code** in its `description`, and respect any active write-freeze.
- Add the new workflow to the table above with its sharp boundary.
