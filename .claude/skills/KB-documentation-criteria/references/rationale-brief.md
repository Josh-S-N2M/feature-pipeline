# Honoring the Rationale Brief

The discipline every sub-agent applies when its invocation prompt carries a rationale brief. Per ADR-0009, every sub-agent invocation in the feature-pipeline includes a brief; how the sub-agent treats that brief determines whether decisions and open items propagate correctly.

## Contents

- What the rationale brief is
- The two ways it's carried
- The four rules of honoring
- How each sub-agent type uses it
- What "violating the brief" looks like
- Interaction with the issues-ledger
- How `review-architecture-auditor` audits brief-honor

## What the rationale brief is

The rationale brief is a structured summary of:

1. **User-confirmed decisions** carried forward from prior phases of the pipeline (e.g., "User approved the per-layer fan-out during the Design phase")
2. **Open items** that are still pending user resolution (e.g., "Layer Scope checkboxes for Frontend and CI/CD pending user confirmation")
3. **Resolved issues** from prior iterations (e.g., "I-AA-002 resolved by adding Field Propagation Map")
4. **KB and ADR paths** in scope for this feature
5. **The current orchestrator state** (which phase the pipeline is in, what artifacts exist)

It is the orchestrator's mechanism for keeping every sub-agent in sync with the user's evolving intent.

## The two ways it's carried

The brief is delivered to a sub-agent in one of two ways:

### Inline in the invocation prompt

The orchestrator includes a `## Rationale brief` section in the prompt sent to the sub-agent. This is the typical case for short briefs.

```markdown
## Rationale brief

User-confirmed decisions:
- Feature slug: `add-healthz-endpoint`
- Layer Scope: API, Backend (confirmed at Intent Clarification gate)
- Existing observability stack: OpenTelemetry + Prometheus (codebase-discovered, no
  alternative considered per user direction)

Open items:
- Whether to expose `/healthz` publicly or auth-gate it (deferred to Design Composition;
  per-layer designers should NOT pre-decide)

ADRs in scope: ADR-0023 (existing health-check pattern; relevant precedent)
KBs in scope (in addition to your defaults): KB-backend-design, KB-api-design
```

### Referenced by file path

For longer briefs (typically when many prior decisions accumulated), the orchestrator writes the brief to disk and references it:

```markdown
## Rationale brief

See `working/feature/add-healthz-endpoint/rationale-brief.json` for the full brief.
```

In this case the sub-agent reads the JSON before doing any other work.

## The four rules of honoring

### Rule 1: Read the brief before producing any output

A sub-agent that emits its first content without having read the brief is violating Rule 1. The brief may explicitly forbid a default behavior, defer an open item, or point to a constraint that changes the work.

`shared-document-reviewer`'s Step 0 (Input Context Analysis) is partly designed to catch Rule 1 violations — when a document looks like its author didn't account for prior context.

### Rule 2: Decisions in the brief are binding

If the brief says "User approved per-layer fan-out," the sub-agent does NOT re-litigate that decision. It does NOT propose an alternative as the recommended option. It does NOT note "we could also consider..." (unless explicitly invited by the brief).

Binding decisions can be tactical (e.g., specific library choice) or strategic (e.g., entire pipeline structure). Both equally binding.

### Rule 3: Open items in the brief must be either resolved or explicitly deferred — never silently dropped

An open item the brief lists has three valid dispositions in the sub-agent's output:

| Disposition | When to use | What to do |
|---|---|---|
| **Resolved** | The sub-agent has enough information to decide. | Make the decision; record the rationale in the document; mark the open item as resolved in the output's `rationale_status` block. |
| **Deferred** | The sub-agent could decide but the question is better answered later (different phase, different stakeholder). | Explicitly defer with a clear rationale and a forward pointer (e.g., "Deferred to Plan Authoring; depends on phase boundaries"). |
| **Escalated** | The sub-agent cannot decide without user input. | Surface to the orchestrator; the orchestrator decides whether to AskUserQuestion or carry forward. |

Silently dropping is NEVER a valid disposition. If the sub-agent's output ignores the open item entirely, `review-architecture-auditor`'s brief-honor lens flags it as a `critical` completeness issue.

### Rule 4: Resolved issues in the brief stay resolved

If the brief lists a prior-iteration resolved issue (e.g., "I-AA-002 resolved by adding Field Propagation Map"), the sub-agent's output MUST NOT re-introduce the underlying problem. Re-surfacing previously-resolved issues is a Rule 4 violation — and the most common cause of iteration loops.

`review-architecture-auditor`'s brief-honor lens explicitly checks for this: each resolved-issue entry in the brief is located in the current document; if the resolution is absent or undone, a `critical` consistency issue is raised.

## How each sub-agent type uses the brief

### Authoring sub-agents (intake-prd-author, per-layer designers, design-composer, plan-author, test authors)

These produce documents. They:

1. Read the brief at the start.
2. Reflect each decision and open item in the document where appropriate. The document is the canonical record of how the brief was applied.
3. Include a `## Rationale Brief Reflection` (or equivalent named section) when the template provides one, summarizing how each item was handled.
4. For items resolved during this pass, propose updated brief contents in the sub-agent's output `metadata.brief_updates` so the orchestrator can amend the brief for downstream sub-agents.

### Review sub-agents (shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor)

These produce verdicts. They:

1. Read the brief at the start (Step 0).
2. Use the brief as ground truth for what the document under review is supposed to honor.
3. Surface brief-violations as issues with appropriate severity (Rule 4 violations and silently-dropped open items → `critical`; ambiguous handling → `important`).
4. Include a `prior_context_check` block in the output JSON when the brief carries prior open issues.

Review sub-agents do NOT modify the brief. They only assess against it.

### Finalize sub-agents (finalize-reconciler, finalize-task-decomposer)

These mediate between issues and authoring. They:

1. Read the brief and the latest issues.
2. Route work to the appropriate authoring sub-agent with an UPDATED brief that incorporates the new issues.
3. Treat the brief as the channel for keeping authoring sub-agents informed about cross-pass context.

## What "violating the brief" looks like

Concrete examples from real iteration loops in earlier pipeline versions:

### Decision contradiction

Brief: "User confirmed Frontend out of scope."
Document (Blueprint Backend Design): "Frontend will use the new endpoint via the existing client library."

Diagnosis: design-backend made an assumption about Frontend behavior despite Frontend being out of scope. Even if technically harmless, this is a brief violation because it presupposes Frontend changes the brief said were not in scope.

Severity: `important`/consistency. The fix is either to remove the Frontend reference or to re-open Layer Scope for user confirmation.

### Open-item silent drop

Brief: "Open: rate-limit policy for /healthz endpoint (pending user input)."
Document (Blueprint API Design): produces a full API section, says nothing about rate limiting.

Diagnosis: design-api ignored the open item. Even if rate limiting "isn't relevant to API design," the silent drop is the issue — the design needs an explicit acknowledgment that this concern is being handled elsewhere, or a deferred-with-rationale.

Severity: `critical`/completeness. The fix is to add a "Rate limiting" subsection that explicitly defers ("Deferred to Operational Policy section, pending user input") or escalates.

### Resolved-issue re-surfacing

Brief: "I-AA-002 resolved at Blueprint v1.1.0 by adding Field Propagation Map."
Document (Blueprint v1.3.0): no Field Propagation Map section.

Diagnosis: in a later iteration, design-composer regenerated the Blueprint without carrying the Field Propagation Map forward. The resolution was lost.

Severity: `critical`/consistency. The fix is to restore the Field Propagation Map. The orchestrator should ALSO investigate why composition lost the section — possibly a context-window or prompt-construction issue.

### Re-litigation of confirmed decision

Brief: "User approved per-layer fan-out as the design topology."
Document (Blueprint Architecture Overview): "Alternative: a monolithic design-author sub-agent that produces all Design sections in one pass."

Diagnosis: design-composer re-introduced an alternative the user already rejected. Even if framed as "considered and dismissed," this is a Rule 2 violation — confirmed decisions should not appear as alternatives at all.

Severity: `important`/consistency. The fix is to remove the alternative.

## Interaction with the issues-ledger

The brief and the issues-ledger overlap but are not the same:

| Concern | Source | When read |
|---|---|---|
| **Rationale brief** | Orchestrator-curated; current state of user-confirmed decisions and open items | Read by every sub-agent on every invocation |
| **Issues-ledger** | Reviewer-emitted; defects surfaced during reviews | Read by reviewers on subsequent iterations; by finalize-reconciler when routing work |

The brief is forward-looking ("here's what's been decided; here's what's open"). The ledger is backward-looking ("here are the defects found and their resolution status").

Resolved issues from the ledger are reflected in the brief as "Resolved: I-XX-NNN" entries — that's how reviewers know not to re-surface them.

## How `review-architecture-auditor` audits brief-honor

The Architecture Audit's brief-honor lens (the third of three lenses, after CoVe and blast-radius) explicitly checks each brief item:

1. **Load the brief snapshot** from the orchestrator's invocation prompt (or referenced file).
2. **Enumerate commitments.** Three categories:
   - User-confirmed decisions
   - Open items
   - Resolved issues
3. **For each commitment, locate the Blueprint's treatment.** Use Grep/section scan to find where the Blueprint addresses it.
4. **Classify the treatment** per the rules above. Emit an issue for each violation.

Output JSON includes a `metadata.brief_items_checked` field with the count, so downstream consumers know the audit was comprehensive.

The architectural-audit reference in `KB-review-disciplines` has the full procedure.
