# Substrate Anti-patterns

## 1. Silent option elision

Producing a decision mapping with only `native` and `adapter` populated; substrate_change omitted.

**Discipline:** all three options every time. When substrate_change is genuinely n/a, populate with `description: "n/a"` and `viable: false`.

## 2. Recommending substrate_change without quantifying cost

`recommended_option: substrate_change` with `cost.effort_weeks: 4`.

**Discipline:** substrate_change is always high-cost (typically 12+ weeks). If cost looks low, you're underestimating.

## 3. Ignoring hard constraints

Recommending `native: "use Anthropic Claude Code"` when `hard_constraints: ["vendor-locked:microsoft"]`.

**Discipline:** read hard_constraints at task start; downgrade violating options to `viable: false`.

## 4. Auto-picking when all viable and close-cost

Picking one when all three options score within 20% of each other.

**Discipline:** `recommended_option: null` and AskUserQuestion. This is a human decision.

## 5. Stale registry

Using a registry whose `version:` is >90 days old.

**Discipline:** staleness gate refuses to emit. Surface AskUserQuestion to refresh.

## 6. Conflating loss with viability

Marking `viable: false` because of high `loss_summary` when costs are otherwise reasonable.

**Discipline:** `viable` captures *can this be implemented at all in this substrate, given constraints?* Loss is a separate axis. A high-loss option can still be viable; high loss means it scores worse, not zero.
