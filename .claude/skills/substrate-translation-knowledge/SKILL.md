---
name: substrate-translation-knowledge
description: Knowledge skill loaded by synth-substrate. Carries three-option enumeration discipline, cost-modeling guidance, the loss-vs-pattern framing, and the protocol for consuming the substrate registry whose path is supplied by the orchestrator.
user-invocable: false
---

# Substrate Translation Knowledge

Loaded by `synth-substrate` via `skills: [substrate-translation-knowledge]`. Provides the three-option enumeration discipline that produces `05-substrate-map.json` from `04-decision-frames.json` plus the active substrate registry.

## Substrate registry loading

The substrate registry is **not bundled in this skill**. The orchestrator (the `synthesize` skill) selects the registry file based on `manifest.constraints.target_substrate` (see Step 5 of the synthesize skill body) and passes the resolved path into the Substrate phase prompt as `registry_path`. The registry physically lives under the orchestrator skill's `references/` directory, named `substrate-registry.md` for the default `claude_code` target, or `substrate-registry-<target>.md` for other substrates.

**Consumption protocol:**

1. Read `registry_path` from the prompt. If absent, refuse to emit and surface `AskUserQuestion` ("orchestrator did not supply registry_path; substrate phase cannot proceed").
2. `Read` the file at that path.
3. Parse the front-matter (`version:`, `target:`, `maintained_by:`, `review_cadence:`).
4. **Staleness gate (B-stale).** If `version:` header date is more than 90 days older than `manifest.started_at`, refuse to emit and surface `AskUserQuestion` to refresh.
5. **Target mismatch gate.** If front-matter `target:` does not match `manifest.constraints.target_substrate`, refuse to emit and surface `AskUserQuestion` (orchestrator likely passed the wrong file).
6. Use the registry's Section 2 primitive catalog when scoring `native` options and Section 3 unmappable patterns when scoring `substrate_change` options.

**Why this lives here, not in the orchestrator.** The orchestrator does the file selection (it knows `target_substrate`); the agent does the consumption (it knows what to do with the registry's content). Keeping the consumption protocol next to the three-option discipline and loss-vs-pattern framing — which depend on registry content — keeps related rules co-located.

**If a needed target-specific registry doesn't exist.** The orchestrator's Step 5 surfaces this. If it somehow reaches this agent anyway (`registry_path` points at a missing file), refuse to emit and surface `AskUserQuestion` to author the registry or change `target_substrate`.

## Three-option enumeration discipline

For **every** architectural decision in `04-decision-frames.json`, populate all three option keys in the corresponding `05-substrate-map.json` entry:

- `native` — implementation purely using primitives present in the substrate (per registry Section 2). Loss minimized; effort minimized when substrate has the primitive.
- `adapter` — implementation that wraps or simulates a missing primitive using available ones. Loss varies; effort moderate.
- `substrate_change` — recommendation to change the substrate (e.g., switch to a different framework or extend the substrate). Loss zero (preserves pattern fidelity); effort highest.

**Every decision has all three.** When an option is "n/a" (e.g., for a purely conceptual decision like "use a saga pattern"), populate with the literal string `"n/a"` in that option's `description` field. Do NOT silently elide options. Three-option enumeration check (B-3opt) refuses to write if any decision has fewer than three populated options.

## Loss-vs-pattern framing

The "loss" of an option captures what aspect of the original pattern is sacrificed when implemented in this substrate:

| Loss type | Meaning | Example |
|---|---|---|
| `none` | The substrate has the primitive directly | "Use Task tool for sub-agent invocation" — Claude Code has this |
| `static_typing` | Pattern relies on type-system enforcement; substrate validates dynamically | LangGraph TypedDict state ↔ Claude Code JSON Schema |
| `cycle_declaration` | Pattern relies on framework-declared cycles; substrate uses orchestrator counters | LangGraph `cycle: True` ↔ counter-based bounded retry |
| `replay_determinism` | Pattern assumes deterministic replay; substrate doesn't | Trace-replay testing ↔ tolerance-based smoke runs |
| `latency` | Pattern's latency profile differs (usually worse via adapter) | In-process call ↔ file-system-mediated handoff |
| `cost_model` | Per-invocation cost differs | Single LLM call ↔ multiple sub-agent invocations |
| `pattern_fidelity` | Conceptual pattern is partially preserved but materially different | "Multi-agent supervisor" ↔ "main agent + sub-agents" |

For each option, `loss_summary` field describes which losses apply and their severity. When all three options have unacceptable losses for the decision's context, set `recommended_option: null` and surface via `AskUserQuestion`.

## Hard-constraint downgrade

Read `manifest.constraints.hard_constraints[]`. For each option, check:
- Does this option violate any hard constraint?
- If yes, the option's `viable` field becomes `false` and a constraint violation note is added.

Example: hard_constraint = `vendor-locked:microsoft`. Option `native: "use Anthropic Claude Code"` is non-viable for this decision — flag and downgrade. The `recommended_option` then defaults to whichever viable option scores best on the cost model.

When all three options are non-viable due to constraints, set `recommended_option: null` and surface via `AskUserQuestion` with explicit message "Hard constraints make this decision unanswerable in <target_substrate>; consider relaxing constraints or changing target."

## Cost modeling per option

For each option, populate `cost`:
- `effort_weeks` — engineer-weeks to implement
- `runtime_overhead` — qualitative ("none", "minor", "significant") — describes per-invocation overhead in the running pipeline
- `maintenance_burden` — qualitative — describes ongoing operational cost
- `irreversibility_cost` — qualitative — when undoing this decision, what's the cost?

Effort estimates draw from the registry's primitive catalog: if a primitive exists, `native` is typically 1–2 weeks; if an adapter is needed, `adapter` is typically 3–6 weeks; `substrate_change` is typically 12+ weeks.

## Recommended option selection

When all three options are populated and viable:
1. Score each option as `(loss_severity × maintenance_burden × irreversibility_cost) ÷ pattern_fidelity_value`.
2. Filter out non-viable options (constraint violations).
3. Recommended option = lowest-cost viable option, **unless** the lowest-cost option has `loss_severity = high` AND another option has `loss_severity = none` with effort < 2× the lowest cost. In that case, prefer the lossless option.
4. When two options score within 20% of each other, set `recommended_option: null` and surface `AskUserQuestion` ("All three options are viable; recommend a human decision").

## Output contract

Write to `05-substrate-map.json`:
```json
{
  "mappings": [
    {
      "decision_id": "D-0001",
      "registry_version": "2026-04-30.1",
      "options": {
        "native":         { "description": "...", "loss_summary": [...], "viable": true,  "cost": {...}, "viable_explanation": "..." },
        "adapter":        { "description": "...", "loss_summary": [...], "viable": true,  "cost": {...}, "viable_explanation": "..." },
        "substrate_change": { "description": "n/a", "loss_summary": [], "viable": false, "cost": {...}, "viable_explanation": "..." }
      },
      "recommended_option": "native",
      "rationale": "..."
    }
  ]
}
```

`registry_version` is the active registry's `version:` header — propagated into per-ADR provenance footers (task-22).

## See also

- `references/examples.md` — 4–6 worked translations across substrates
- `references/anti-patterns.md` — silent option elision, recommending substrate-change without quantifying cost
