# Substrate Translation Examples

Worked translations across the three options for representative architectural decisions.

## D-0001: "Use multi-agent supervisor pattern"

```json
"options": {
  "native": {
    "description": "Orchestrator skill + sub-agents via Task tool. Supervisor logic lives in skills/synthesize/SKILL.md.",
    "loss_summary": ["pattern_fidelity"],
    "viable": true,
    "cost": {"effort_weeks": 2, "runtime_overhead": "minor", "maintenance_burden": "minor", "irreversibility_cost": "minor"},
    "viable_explanation": "Direct realization. Loss: framework-level supervisor abstractions are simulated rather than declared."
  },
  "adapter": {
    "description": "Use a Python orchestrator wrapper that calls the Claude API directly with structured prompts.",
    "loss_summary": ["latency", "cost_model", "pattern_fidelity"],
    "viable": false,
    "cost": {"effort_weeks": 8, "runtime_overhead": "significant", "maintenance_burden": "significant", "irreversibility_cost": "significant"},
    "viable_explanation": "Bypasses Claude Code's native orchestration; loses MEMORY.md, .memories/, hooks. Net cost > native."
  },
  "substrate_change": {
    "description": "Adopt LangGraph for orchestration; preserve Claude as LLM provider.",
    "loss_summary": [],
    "viable": true,
    "cost": {"effort_weeks": 16, "runtime_overhead": "minor", "maintenance_burden": "minor", "irreversibility_cost": "significant"},
    "viable_explanation": "Recovers cycle declaration, typed state, deterministic replay. High switching cost; only worth it if multiple decisions push this direction."
  }
}
```

Recommended: `native` (lowest cost; loss is acceptable for this pipeline).

## D-0002: "Cycle declaration for retry budgets"

```json
"options": {
  "native": {
    "description": "Orchestrator-side counter + checkpoint.json retries field; max_iterations cap.",
    "loss_summary": ["cycle_declaration"],
    "viable": true,
    "cost": {"effort_weeks": 0.5, "runtime_overhead": "none", "maintenance_burden": "minor", "irreversibility_cost": "none"},
    "viable_explanation": "Counter-based; equivalent correctness, manual termination."
  },
  "adapter": {
    "description": "n/a",
    "loss_summary": [],
    "viable": false,
    "cost": {"effort_weeks": 0, "runtime_overhead": "n/a", "maintenance_burden": "n/a", "irreversibility_cost": "n/a"},
    "viable_explanation": "n/a — counter is already the substrate's idiom."
  },
  "substrate_change": {
    "description": "Adopt LangGraph for declared-cycle support.",
    "loss_summary": [],
    "viable": true,
    "cost": {"effort_weeks": 16, "runtime_overhead": "minor", "maintenance_burden": "minor", "irreversibility_cost": "significant"},
    "viable_explanation": "Worth it only if cycle declaration is central to multiple decisions."
  }
}
```

Recommended: `native`. Three-option enumeration is honored even though `adapter` is "n/a".

## D-0003: All three viable, escalate

When `native`, `adapter`, and `substrate_change` all score within 20% on cost: `recommended_option: null`, surface AskUserQuestion with the three options' summaries.
