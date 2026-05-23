---
name: kb-codebase-research
description: >-
  Discipline for analyzing an existing codebase during the Discovery Research
  stage. Covers GitNexus MCP traversal patterns, dependency inference,
  blast-radius previewing, structural archaeology (read what's there, not what
  you'd write), and the canonical output schema for codebase-analysis.json
  (per ADR-0018 + ADR-0038; schema v1.1.0 extended for blast-radius). Loaded by the
  discovery-codebase-researcher sub-agent. Pairs with KB-cc-platform for
  Claude Code primitives observed in the codebase and the per-layer design
  KBs for layer-specific conventions to look for.
allowed-tools: Read, Grep, Glob
---

# KB-codebase-research — Codebase Analysis Discipline

Discipline KB consumed by the `discovery-codebase-researcher` sub-agent during the Discovery Research stage. The sub-agent reads the existing codebase using GitNexus MCP (or the fallback `codebase-memory-mcp`), inferring structure, dependencies, and blast-radius for a proposed change, then writes `codebase-analysis.json` (canonical schema per ADR-0018 + ADR-0038; v1.1.0 extended for blast-radius preview) plus `codebase-analysis-report.md` (human-readable summary).

## Contents

- When this KB is loaded
- The sub-agent's responsibility
- Traversal patterns
- What to record
- The canonical output schema
- Common pitfalls
- When to load each reference file

## When this KB is loaded

This KB is loaded by:

- `discovery-codebase-researcher` (single sub-agent per pipeline run; sole consumer of this KB)

The sub-agent loads this KB at the start of Discovery Research and consults it throughout. Other sub-agents do NOT load this KB — they read the resulting `codebase-analysis.json` artifact.

## The sub-agent's responsibility

The `discovery-codebase-researcher` answers questions the rest of the pipeline needs:

- **What exists today?** Components, modules, services, key types, key files. The structural map.
- **What touches what?** Dependency graph at the file, module, and service level. Inferred from imports, calls, configuration references.
- **What's the blast radius of the proposed change?** Given the feature's likely touch points (from the PRD), which other parts of the codebase are downstream consumers? What tests cover them? What's the depth of coupling?
- **What conventions does the codebase already use?** Naming, file layout, error handling, logging, testing patterns. These constrain the design — new code should fit, not fight.
- **What anti-patterns or known issues exist?** Things to avoid touching; things that already need cleanup; areas that previous incidents have flagged.

The sub-agent does NOT:

- Design the feature. That's per-layer Design's job.
- Make architectural decisions. Surface them as questions for the composer.
- Modify the codebase. Read-only research.

## Traversal patterns

### Start from the proposed touch points

The PRD or Research Plan names the likely touch points (a service, a layer, a flow). Start there:

1. Identify the top N entry points (HTTP handlers, queue consumers, scheduled jobs) related to the feature.
2. For each entry point, traverse outward: what does it call? What does it write to? What does it depend on?
3. Bound the traversal at well-defined edges: bounded-context boundaries, layer boundaries, service-to-service calls.

### GitNexus MCP query patterns

GitNexus exposes Cypher queries against the code graph. Useful queries:

- **Who calls this function?**
  ```
  MATCH (caller)-[:CALLS]->(target {name: 'OrderService.cancel'})
  RETURN caller.file, caller.name
  ```
- **What modules import this?**
  ```
  MATCH (m:Module)-[:IMPORTS]->(target:Module {name: 'orders.domain'})
  RETURN m.name
  ```
- **What are the file's exported symbols?**
  ```
  MATCH (f:File {path: 'src/orders/service.ts'})-[:DEFINES]->(s)
  WHERE s.exported = true
  RETURN s.name, s.kind
  ```
- **What's the call depth from entry point X to module Y?**
  ```
  MATCH path = (entry {kind: 'http_handler', name: $entry})-[:CALLS*1..6]->(target {module: $module})
  RETURN length(path), path
  ORDER BY length(path) ASC
  LIMIT 5
  ```

For blast-radius preview: enumerate reverse-call dependents of the function or module the feature plans to modify. Capture the count, the names, and the test files that cover them (heuristic: `*.test.*` or `*.spec.*` in the same directory tree).

### Use codebase-memory-mcp as fallback

When GitNexus is degraded for the user's language stack (e.g., the language isn't supported, or the index is stale), fall back to `codebase-memory-mcp`. The sub-agent's output schema is the same regardless of which MCP supplied the data; only the `extraction_method` field varies.

### Use Read / Grep / Glob for ground truth

GitNexus and codebase-memory MCPs index code; they can lag. For high-confidence claims, verify against the file system: `Read` the file, `Grep` for the symbol, `Glob` to confirm the path exists.

## What to record

### Components

A component is a named, cohesive unit. Examples: a service, a module, a package. Recorded fields:

- `name`: human-readable name
- `path`: canonical path in the repo (or scope identifier for cross-repo)
- `layer`: one of {frontend, backend, api, query, database, iac, cicd, cc, codespaces} (per layer-taxonomy.md in KB-documentation-criteria)
- `language`: primary language(s)
- `framework`: primary framework(s) (e.g., "FastAPI", "Next.js", "Spring Boot")
- `entry_points`: list of public entry points (URLs, function names, etc.)
- `dependencies`: list of other components it depends on (by name)
- `notes`: anything qualitative that doesn't fit a field

### Dependencies (edges)

Each dependency edge:

- `from`: component name
- `to`: component name (or external-system identifier)
- `kind`: one of {import, call, http_call, message_publish, message_consume, db_read, db_write, config_reference, file_reference}
- `count`: how many instances of this edge (e.g., 12 separate places call OrderService.cancel)
- `representative_files`: 1-3 example file paths to look at
- `confidence`: high / medium / low (high = GitNexus + manual verification; medium = GitNexus only; low = inferred)

### Blast radius (per proposed touch point)

For each touch point named in the PRD or research plan:

- `touch_point`: the function / module / file being modified
- `direct_dependents`: components that directly call or import this
- `transitive_dependents`: components within N hops (configurable; default N=3)
- `test_files`: files that exercise the touch point or its dependents
- `hop_tier`: 1-hop (direct caller), 2-hop (caller of caller), 3+-hop. Surfaces concentration: a change with 50 1-hop dependents is structurally different from one with 50 5-hop dependents.

### Conventions observed

For each layer present in scope, capture:

- File-naming patterns (e.g., `*Repository.ts`, `*_service.py`)
- Module layout (where do tests live? where do migrations live? where do types live?)
- Error-handling idioms (exceptions / errors-as-values / mixed)
- Logging library and conventions
- Testing framework and patterns
- Other layer-specific norms

### Known issues / cleanup areas

- Existing TODO/FIXME concentrations
- Files mentioned in incident postmortems (if accessible)
- Modules flagged by linters or static analyzers (if results available)

## The canonical output schema

Per ADR-0018 + ADR-0038 (schema v1.1.0 extended for blast-radius). The sub-agent writes `codebase-analysis.json` matching this schema:

```json
{
  "schema_version": "1.1.0",
  "pipeline_run_id": "<run id>",
  "generated_at": "<ISO 8601>",
  "extraction_method": "gitnexus | codebase-memory-mcp | mixed",
  "scope": {
    "repo": "<owner/repo>",
    "branch": "<branch>",
    "commit": "<SHA>",
    "paths": ["src/orders/", "tests/orders/"]
  },
  "components": [
    {
      "name": "OrderService",
      "path": "src/orders/service.ts",
      "layer": "backend",
      "language": "typescript",
      "framework": "express",
      "entry_points": ["POST /orders", "POST /orders/:id/cancel"],
      "dependencies": ["OrderRepository", "PaymentClient"],
      "notes": "Active development; recent refactor for hex architecture."
    }
  ],
  "dependencies": [
    {
      "from": "OrderService",
      "to": "OrderRepository",
      "kind": "call",
      "count": 12,
      "representative_files": ["src/orders/service.ts", "src/orders/handlers.ts"],
      "confidence": "high"
    }
  ],
  "blast_radius": [
    {
      "touch_point": "OrderService.cancel",
      "direct_dependents": ["OrderHandler", "AdminOrderController"],
      "transitive_dependents_3_hop": ["OrderHandler", "AdminOrderController", "NotificationService", "AuditLogger", "WebhookEmitter"],
      "test_files": ["tests/orders/service.test.ts", "tests/orders/handlers.test.ts"],
      "hop_tier_distribution": {"1": 2, "2": 1, "3": 2}
    }
  ],
  "conventions": {
    "backend": {
      "file_naming": "*.service.ts / *.repository.ts / *.handler.ts",
      "module_layout": "src/<bounded-context>/ + tests/<bounded-context>/",
      "error_handling": "Result<T, AppError>-style errors-as-values",
      "logging": "pino, structured JSON",
      "testing": "Vitest, integration tests in tests/integration/"
    }
  },
  "known_issues": [
    {
      "description": "OrderService.cancel has TODO comment about idempotency.",
      "files": ["src/orders/service.ts:127"],
      "severity": "medium"
    }
  ],
  "open_questions_for_human": [
    {
      "question": "Is the legacy `cancellation.js` script still in production use?",
      "context": "Found references in CI but no recent commits.",
      "blocks": "discovery-research-completion"
    }
  ]
}
```

The sub-agent ALSO produces `codebase-analysis-report.md` — a human-readable summary of the same content, written for the user's review at the Discovery Research gate.

## Common pitfalls

- **Treating GitNexus output as ground truth without verification.** The index can lag. For high-stakes claims (especially blast-radius for the change), verify with `Read`/`Grep`.
- **Recording everything.** The output is noise if it captures every file in the repo. Scope to the PRD's likely touch points.
- **Inferring intent from code.** "This looks unused" is often wrong. Surface as an open question rather than recording as fact.
- **Skipping the conventions section.** The downstream per-layer designers need conventions to design with the codebase, not against it.
- **Confidence inflation.** Mark "low" when the only source is an inference. The downstream consumer adjusts trust accordingly.
- **Cross-cutting analysis missed.** A backend feature may touch the API layer (new endpoint), CI/CD (new deploy step), and the Database (migration). Capture all affected layers.

## When to load each reference file

This KB has no `references/` subdirectory at this stage — the discipline lives entirely in this SKILL.md. The canonical output schema is inlined here (rather than a separate JSON file in the skill) because the schema is the contract and SHOULD live next to the discipline.

Future expansion (after pilot use) may add a `references/` subdirectory covering:

- A deeper GitNexus Cypher cookbook with worked traversal examples.
- A comprehensive per-layer convention inspection checklist.

For now, the SKILL.md is the complete reference.
