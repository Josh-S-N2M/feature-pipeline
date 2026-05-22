---
name: kb-general-coding-principles
description: >-
  Language-agnostic coding standards used to evaluate implementation
  samples that appear in design artifacts (per-layer Design sections,
  ADRs with code, shared-document-reviewer Gate 1 checks). Load when
  authoring or reviewing any document that contains a code block intended
  as design-time guidance rather than executable production code. Covers
  what a "good" sample looks like in a design context, what to redact,
  what to flag, and what counts as a violation severe enough to block
  document approval. NOT a style guide for production code — production
  style lives in the project's own conventions; this KB is the rubric for
  evaluating illustrative samples inside specs.
pedagogical_sections:
  - path: references/anti-patterns.md
    justification: "Anti-pattern reference catalog documenting code-quality findings the design-time sample evaluator flags"
  - path: references/secrets-rubric.md
    justification: "Secrets rubric reference catalog; documents credential patterns the auditor flags in code samples (DE-2 scanner)"
  - path: references/fabricated-api-detection.md
    justification: "Fabricated-API-detection reference catalog; documents non-existent API references the auditor surfaces"
---

# General Coding Principles (Design-Time Sample Evaluation)

This KB is the rubric used by per-layer designers when they produce illustrative code in a Design section, and by `shared-document-reviewer` when it evaluates those code blocks at Gate 1. It is **not** a production style guide — those live in the project under review.

The body below is the router. Use the matching reference file for in-depth criteria.

## When this KB is loaded

| Caller | When | Purpose |
|---|---|---|
| `design-frontend`, `design-backend`, `design-api`, `design-query`, `design-database`, `design-cicd`, `design-iac`, `design-codespaces`, `design-claude-code` | During per-layer Design | Authoring per-layer Design sections that include implementation samples |
| `design-composer` | During Design Composition | Composing cross-cutting samples and ADR code (rare) |
| `shared-document-reviewer` | On every reviewed document (per ADR-0017) | Gate 1 quality check on any code block in the document under review |

`shared-document-reviewer` references this KB explicitly via its `skills:` frontmatter field. Per-layer designers reference it via the same mechanism.

## The mental model: design-time samples vs production code

A code block in a design document is a **contract illustration**, not the deliverable. Its job:

- show the shape of a call, type, or schema
- anchor a decision rationale ("this option is rejected because…")
- demonstrate an integration point's signature

A reader should be able to compile mental expectations from the sample without needing it to run. Therefore the bar is different from production code:

| Production code bar | Design-sample bar |
|---|---|
| Compiles, lints clean, passes tests | Compiles **conceptually** — types and names check |
| Handles every edge case | Handles edge cases the spec calls out by name; others noted as `// elided` |
| Hides primitives behind abstractions | Allowed to be more primitive-leaning so the contract is obvious |
| No secrets, no shortcuts | Same — even harder, since samples may end up copy-pasted |

## What the rubric checks (10 dimensions)

The rubric below scores any code block in a document. A score below 80 raises an `important` issue; below 60 raises a `critical` issue. Score weights and thresholds are in `references/scoring.md`.

| # | Dimension | Quick check |
|---|---|---|
| 1 | **Names match contract** | Function/type/variable names match the surrounding prose and other sections of the same doc |
| 2 | **Types are explicit** | Argument and return types declared where the language supports it; ambiguous types named or commented |
| 3 | **Error contract visible** | Errors and exceptional paths are named in code or comment, not silently elided |
| 4 | **No fabricated APIs** | Calls to libraries/frameworks reference real methods with real signatures (verified against the dependency-realizability check) |
| 5 | **No copy-pasted secrets** | No real or realistic credentials, tokens, hostnames, internal URLs, real PII |
| 6 | **No hidden control flow** | No `eval`, dynamic require, monkey-patch, or reflection that hides what runs |
| 7 | **Idempotency stated** | When the sample shows a state-changing operation, idempotency expectation is explicit (idempotent / not / unspecified-and-OK) |
| 8 | **Concurrency posture stated** | When two callers could overlap, the sample says so (locking, transactional, or "single-writer assumed") |
| 9 | **Language matches project** | Sample language matches the layer's actual stack (per codebase analysis), or notes deliberate divergence |
| 10 | **Sample is minimal** | One block ≤ 40 lines, or split into named blocks of ≤ 40 lines each, with prose between |

## Routing

| If you need to… | Go to |
|---|---|
| Decide whether a specific block should pass review | `references/scoring.md` and `references/anti-patterns.md` |
| Know what counts as a fabricated API (Dimension 4) | `references/fabricated-api-detection.md` |
| Author a sample that demonstrates an error contract (Dimension 3) | `references/error-contract-patterns.md` |
| Author a sample for a layer whose stack is unknown until Discovery Research | `references/stack-unknown.md` |
| Check whether a secret-shaped string is actually safe | `references/secrets-rubric.md` |

## The non-negotiables (auto-fail dimensions)

Three failures bypass scoring and force `needs_revision`:

1. **Real credential present.** Any string matching credential shapes (AWS key prefixes `AKIA`/`ASIA`, GitHub PAT prefixes `ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`, Stripe `sk_live_`/`sk_test_`, bearer tokens with realistic length, JWT-shaped tokens with three base64 segments, private-key PEM headers). Detection rules in `references/secrets-rubric.md`.
2. **Fabricated dependency.** A method call into a real library that does not exist in any documented version of that library. Distinct from "library not in project yet" (acceptable) — this is "library is in project but the method shown does not exist."
3. **Code that would visibly execute against shared infrastructure.** A `curl` or SDK call to a real production URL, a `rm -rf` rooted at a real path, a workflow `run:` that writes to a real S3 bucket name. Even commented-out, these are confusing because samples get copied.

Any of those three: stop scoring, raise `critical` issue, recommend rewrite before any further review.

## Working with stack-unknown samples

The per-layer designers run during per-layer Design, after the codebase researcher has finished. Most of the time the stack is known (React vs Vue, Express vs FastAPI, Postgres vs MySQL). When it is genuinely unknown — typically a greenfield section of an existing codebase — the sample SHOULD:

- declare the language explicitly in the fence (` ```typescript`, ` ```python`)
- prefix the block with a one-line rationale: `# illustrative; final language TBD at integration time`
- avoid library-specific patterns; show plain language constructs

`references/stack-unknown.md` has the longer pattern.

## What this KB explicitly does NOT cover

- Tab vs space, line length, brace placement, naming case (camelCase vs snake_case) — these are project-specific; reviewer defers to the project's own linter/formatter config
- Performance micro-optimizations
- Security beyond the no-credential and no-fabricated-API rules (full security review is the reviewer's other checks, not this KB)
- Test code style — that lives in the per-layer test strategy, not in the design-time sample rubric

## Update discipline

When a per-layer designer needs a rule this KB doesn't cover, the resolution is:

1. If the rule belongs at a per-layer level → add to that layer's `KB-<layer>-design` skill, not here.
2. If the rule is genuinely cross-layer and code-block-specific → add to this KB via PR; bump version; note in change log below.
3. Never duplicate a rule across this KB and a per-layer KB — designate one canonical home.

## References (this skill's `references/` directory)

- `scoring.md` — the 10-dimension scoring rubric with weights and thresholds
- `anti-patterns.md` — common samples that look fine but fail one or more dimensions
- `fabricated-api-detection.md` — how to verify a library method actually exists
- `error-contract-patterns.md` — accepted ways to show error paths in a sample
- `stack-unknown.md` — pattern for samples whose final language is not yet decided
- `secrets-rubric.md` — credential-shape patterns and the no-real-secret rule

## Provenance

Status: Accepted — v1.0.0 (Phase 2 of feature-pipeline v4.3.0)
Predecessor: This KB carries forward language-agnostic content from the v4.2-era `coding-principles` knowledge skill, refactored to be specifically about design-time sample evaluation. The v4.2 skill had drifted toward general style-guide territory; this v4.3 version narrows the scope per ADR-0020's KB-consolidation discipline.
