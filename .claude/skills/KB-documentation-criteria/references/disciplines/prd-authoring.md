# PRD Authoring Discipline

The discipline used by `intake-prd-author` during PRD Authoring. Produces the PRD from the approved Intent Clarification document, with explicit avoidance of the three AI-PRD failure modes per claim C-R3-0014.

## Contents

- Inputs
- Outputs
- The three AI-PRD failure modes
- Stakeholder authoring discipline
- User story authoring with EARS
- Functional vs non-functional separation
- Layer Scope discipline
- Open items and undetermined items
- Honoring the Rationale Brief
- Interaction with the canonical template
- Output expectations

## Inputs

`intake-prd-author` receives:

| Input | Source | Purpose |
|---|---|---|
| Approved Intent Clarification doc | `intent-clarification.md` | Primary input — captures what the user wants |
| Rationale brief | Orchestrator-supplied | User-confirmed decisions from intake, scope posture, open items |
| KBs in scope | Per the rationale brief, at minimum `KB-documentation-criteria` | Templates and discipline |

`intake-prd-author` does NOT receive:

- Codebase analysis (that's Discovery Research output, which comes later)
- Prior Blueprints, ADRs, or Plans
- Synthesis output

The PRD is a business-requirements document. It asserts WHAT the feature must do, not HOW it will be built. Receiving design-time inputs would invite premature implementation thinking.

## Outputs

A single PRD file at `working/feature/<slug>/prd-v<N>.md`, conforming to `../templates/prd-template.md`.

The PRD is reviewed by `shared-document-reviewer` immediately after authoring (per ADR-0017 invocation point 2). Then it goes through the PRD Approval Gate (user). Only after both pass does the pipeline proceed to Discovery Planning.

## The three AI-PRD failure modes

AI-authored PRDs tend to fail in three specific ways. Each is a `critical` quality issue at Gate 1 review.

### Failure mode 1: Fabricated customer reactions

AI tends to invent stakeholder quotes that sound human-authored. Examples to avoid:

```markdown
"Our customers have been frustrated by the lack of a /healthz endpoint for years," — Sarah Chen, VP Engineering

User feedback: "I just wish the deploy pipeline could tell me when something's wrong without me having to dig through logs."
```

Both look authentic but are fabricated. The reviewer cannot verify them; the reader will treat them as real evidence. They become anchoring data for downstream decisions.

**Discipline:**

- Never invent stakeholder quotes.
- Never invent specific user feedback or research findings.
- When a stakeholder concern is real but unquoted (because the Intent Clarification recorded it without a direct quote), describe the concern in your own words: "The Intent Clarification captured the user's concern about deploy-pipeline observability gaps."

If the Intent Clarification doc contains a direct quote from the user, the PRD MAY carry it forward verbatim with attribution. That's quoting, not fabricating.

### Failure mode 2: Over-precise specs without rationale

AI tends to add specific numbers that sound rigorous but have no source. Examples to avoid:

```markdown
- The system shall respond with p95 latency under 47ms.
- The system shall support 10,847 concurrent users.
- Adoption is expected to reach 73% within 90 days.
```

Three problems:

1. The precise numbers (47ms, 10,847, 73%) imply analysis that didn't happen.
2. No rationale ties them to user value, system constraint, or competitive benchmark.
3. They become hard requirements the team must justify later — even though they were invented.

**Discipline:**

- Use round numbers (under 100ms, 10,000 users, 70%) unless precision has a documented source.
- Always attach a rationale to numeric requirements. "p95 < 200ms because the user perceives anything over 250ms as laggy in this interaction class" is acceptable. "p95 < 200ms" alone is not.
- For "expected adoption" or "estimated impact" statements, mark them explicitly as estimates: "Estimated adoption: ~50% within 90 days, based on similar feature rollouts in this codebase."

### Failure mode 3: Implementation suggestions in requirements

AI tends to slide implementation thinking into requirements. The PRD says WHAT, the Blueprint says HOW. Examples to avoid:

```markdown
- The system shall use Redis for session storage.
- The system shall implement a new microservice for billing.
- The system shall add a `refund_status` column to the `orders` table.
```

These are implementation choices, not requirements. They prejudge design decisions that belong in the Blueprint.

**Discipline:**

- State requirements as observable behaviors.
- If the user explicitly requested a specific implementation (e.g., "we want to use Redis specifically because that's what the rest of our stack uses"), record it in the PRD's Product Policy Decisions section, not in Functional Requirements.

Acceptable rewrites:

```markdown
- The system shall maintain session state across server restarts and instance migrations.
- The system shall process billing operations as a separable concern that can scale independently.
- The system shall record the refund status (pending / approved / rejected) for every refund request.
```

The Blueprint may then decide Redis is the right session store, that billing is a microservice, that `refund_status` lives in `orders`. The PRD doesn't constrain that.

## Stakeholder authoring discipline

The Stakeholder Inventory captures who has skin in the game. Per the template, each stakeholder has:

- **Role** — what they do in the organization
- **Interest** — what they care about for this feature
- **Influence** — how much weight their concerns carry on this decision

Discipline:

- List real roles, not fabricated ones. "Customer Support team" yes; "Maria from Customer Support, who manages 12 agents and processes 4,000 tickets/month" no.
- Interest is concrete and specific. "Wants the feature to be reliable" is vague; "wants visibility into deploy status so they can answer 'is this user affected?' tickets within 30 seconds" is specific.
- Influence is honest. Not every stakeholder has equal weight. If a stakeholder is consulted but doesn't gate the decision, say so.

## User story authoring with EARS

User Stories in the PRD have the classic shape:

```
As a <persona>, I want <capability> so that <outcome>.
```

But each User Story carries Acceptance Criteria in EARS format (per `ears-acceptance-criteria.md`):

```markdown
### US-1: Engineer can check deploy status from CLI

**As an** engineer on call, **I want** to check the deploy status of any service from the CLI **so that** I can answer "is X service deployed?" without opening the GitHub Actions UI.

**Acceptance Criteria:**

- [ ] AC-US-1-a: When the engineer runs `deploy-status <service>`, the system shall return the current deploy status within 2 seconds.
- [ ] AC-US-1-b: When the deploy status is not yet computable (e.g., the workflow is mid-run), the system shall return a `pending` state with the workflow run URL.
- [ ] AC-US-1-c: If the service name is unknown, then the system shall return a clear error listing the available service names.
```

Each FR can have multiple User Stories. Each User Story can have multiple ACs. The discipline:

- Persona is a role, not a person.
- Capability is concrete (a verb + object), not abstract.
- Outcome is observable.
- ACs follow EARS form (5 canonical patterns).

## Functional vs non-functional separation

The PRD template has separate sections for Functional Requirements (FRs) and Non-Functional Requirements (NFRs). The line:

| Functional | Non-functional |
|---|---|
| What the system does (behaviors, capabilities) | How the system behaves (performance, reliability, security, observability, accessibility) |
| Tested by feature behavior | Tested by cross-cutting characteristics |
| Examples: "creates an order," "sends a confirmation email" | Examples: "p95 latency under 200ms," "supports 1000 rps sustained" |

Both get ACs in EARS format. Both get IDs (`FR-N`, `NFR-N`). The separation is for clarity and for ensuring NFRs aren't lost in the noise of FRs.

If something feels like it could be either (e.g., "the system shall log every state-changing operation" — is that functional behavior or operational discipline?), default to NFR. The PRD is more useful when NFRs are surfaced explicitly.

## Layer Scope discipline

Per `../layer-taxonomy.md`, Layer Scope uses the 9 canonical engineering layers. Both PRD and Blueprint use the same 9.

Discipline:

- Check every layer the feature touches. Be conservative — under-checking causes scope creep at Design.
- Do NOT check layers as "might touch" — either it does or it doesn't.
- For layers that are out of scope, do NOT mark anything special. Unchecked = out of scope.
- If unsure whether a layer is touched (e.g., "I think the feature might need a DB schema change but I'm not certain"), surface as an open item, not as a layer check.

Layer Scope confirmation is part of the PRD Approval Gate. The user has final say.

## Open items and undetermined items

The template has an "Undetermined Items" section. Use it for:

- Decisions that depend on Discovery (e.g., "Whether to use existing rate-limit library X or introduce a new one — depends on Discovery findings about library X's maturity")
- Decisions deferred to Design (e.g., "Caching strategy — at the API layer or the Query layer? Defer to Design")
- Stakeholder questions not yet resolved (e.g., "Whether to expose this metric externally or keep internal — pending Product team input")

Items in this section propagate to the rationale brief for downstream sub-agents.

Discipline:

- Each item is a specific question, not a vague topic. "Caching strategy" → specifically what about the strategy?
- Each item has a forward pointer — which pipeline phase or stakeholder is expected to resolve it.
- Don't pad this section. Empty Undetermined Items is fine and common.

## Honoring the Rationale Brief

Per `../rationale-brief.md`, the PRD author honors the brief. For PRD authoring specifically:

- **User-confirmed decisions from Intent Clarification** are reflected in the PRD. Scope posture (in/out/undecided) maps directly to Layer Scope and Undetermined Items.
- **Open items from Intent Clarification** that this phase can resolve → resolved with rationale in the PRD body.
- **Open items that should defer further** → carried to the PRD's Undetermined Items section with a forward pointer.

The PRD should NOT re-litigate decisions confirmed at Intent Clarification. If the Intent Clarification says "Scope: out — multi-tenant isolation," the PRD does not propose multi-tenant features.

## Interaction with the canonical template

`../templates/prd-template.md` has the canonical structure. The discipline above applies to the SUBSTANCE that fills each section; the template provides the STRUCTURE.

Gate 0 (per `gate-0-1-procedure.md` in KB-review-disciplines) checks structural conformance to the template. Gate 1 checks substantive quality, with the AI-PRD failure modes above being prominent failure conditions.

## Anti-patterns

### Anti-pattern 1: "Reasonable" assumptions

```
The system shall handle errors gracefully.
```

Vague. What error? What does "gracefully" mean? Replace with specific EARS ACs covering the actual error classes.

### Anti-pattern 2: "TBD" everywhere

```
Performance requirements: TBD
Adoption target: TBD
Stakeholder list: TBD
```

If everything is TBD, the PRD isn't ready. Either resolve via Intent Clarification re-engagement or surface a structural issue to the user — don't ship a PRD that's mostly placeholders.

### Anti-pattern 3: PRD that reads like a design doc

```
## Implementation Approach

The system will be implemented in three phases. Phase 1 will introduce the database schema...
```

Implementation Approach belongs in the Blueprint, not the PRD. If the PRD has design-doc language, refactor.

### Anti-pattern 4: PRD that re-litigates Intent Clarification

```
## Scope reconsideration

Although the Intent Clarification specified that multi-tenant isolation is out of scope, we should consider...
```

Don't re-open decisions. If you genuinely believe the scope is wrong, surface to user via the orchestrator's AskUserQuestion, not by sneaking it into the PRD.

### Anti-pattern 5: ACs that aren't testable

```
- AC-FR-1-a: The system shall be user-friendly.
- AC-FR-1-b: The system shall handle edge cases.
```

Both fail the "what would I test?" check. Fix: name the specific behaviors per EARS discipline.

## Output expectations

A complete PRD has:

1. Valid frontmatter per `../shared-conventions.md`
2. `## Contents` checklist (per the template's structure)
3. `### Layer Scope` using the 9 canonical engineering layers (per `../layer-taxonomy.md`)
4. Stakeholder Inventory with real roles + concrete interests
5. User Stories with EARS-format ACs
6. Functional Requirements with EARS-format ACs and `FR-N` IDs
7. Non-Functional Requirements with EARS-format ACs and `NFR-N` IDs
8. Product Policy Decisions section (when stakeholders made user-confirmed choices that constrain design)
9. Success Criteria
10. Technical Considerations (high-level, not implementation)
11. Rollout Plan (high-level)
12. Undetermined Items (with forward pointers)
13. Appendix (when applicable)

Output goes to `working/feature/<slug>/prd-v<N>.md`. `shared-document-reviewer` is invoked immediately for Gate 0/1. After the reviewer approves, the PRD Approval Gate (user) decides whether the pipeline proceeds to Discovery Planning.
