# Bad CLAUDE.md: Annotated Example (FAIL)

## Contents

- The file (full source)
- Per-dimension findings
- Total and verdict
- What this calibrates

A CLAUDE.md with multiple anti-patterns that scores around 35/100. Use for calibration of "is this finding really a finding?"

## The file (full source)

```audit-example -- negative-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
# About this project

This is a project we started a while back. We've been working on it for some
time now. The original idea was to build a system that does some things, and
we've added more features along the way. The team thinks we should probably
use modern best practices when we can.

We're considering moving to TypeScript at some point but we haven't decided
yet. For now we use JavaScript but we should think about whether to switch.
Some files use async, some don't. We should clean this up eventually.

## API keys

Our API key is sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz0
and we use it for the OpenAI integration. Don't share this.

## Setup

To set up the project, do `cd /home/alice/projects/our-project` and then
run `npm install`. You'll need Node 18 or newer. Or maybe 16. Or 20.
We're not sure which one.

## Workflow

As of August 2025, you should use the new API. Before August 2025, use the
old API. We migrated in August 2025. Maybe.

@docs/architecture.md
@docs/setup-guide.md
@/Users/bob/notes/private.md

## Rules

- Always use TypeScript.
- Never use TypeScript; we use JavaScript.
- Use 2 spaces for indentation.
- Use tabs for indentation.

#### Some extra section

##### Even deeper

###### Why are we nested this deep
```

## Why this scores ~35/100

### Dimension 1: Size & density — 7/10

44 lines — under 200, technically passes the size check. But the density is poor; much of it is aspirational filler.

### Dimension 2: @-import integrity — 0/10

**BLOCKER:** `@/Users/bob/notes/private.md` is outside the project. Won't resolve on other machines (AP-7 + import-related).
**MAJOR:** `@docs/architecture.md` may not exist (depends on actual project state).
**MAJOR:** `@docs/setup-guide.md` may not exist.

### Dimension 3: Content quality — 2/10

Multiple aspirational findings (AP-2):
**MINOR x 5:** "we should consider", "we should think about", "we should clean this up", "we're considering", "maybe".

### Dimension 4: Anti-pattern absence — 0/10

**MAJOR:** AP-4 contradiction — "Always use TypeScript" + "Never use TypeScript".
**MAJOR:** AP-4 contradiction — "2 spaces for indentation" + "tabs for indentation".
**MAJOR:** AP-3 stale dates — "August 2025" references with current date past that.
**MAJOR:** AP-7 machine-local path — `/home/alice/projects/our-project`.
**MAJOR:** AP-2 aspirational throughout.

### Dimension 6: Security — 0/10 → SECURITY-BLOCK

**BLOCKER (CRITICAL):** AP-6 literal API key value: `sk-proj-abc123...`. The skill detects this via the SEC-OPENAI pattern. Verdict overrides to SECURITY-BLOCK regardless of other scores.

### Dimension 7: Staleness — 4/10

**MINOR x 3:** Three "August 2025" hardcoded date references that are likely stale.

### Dimension 8: Structure — 4/10

**MINOR:** Heading depth reaches 6 (`######`) — AP-9 excessive nesting.

### Dimension 10: Layering interactions — 8/10

No rules files to compare against in this fixture.

## Total: ~35/100, override to **SECURITY-BLOCK**

The verdict is **SECURITY-BLOCK** because of the embedded API key. Even if every other dimension were 10/10, the credential exposure produces a hard stop.

## What this calibrates

This example demonstrates:

- Multiple AP-2 instances stack to MAJOR damage even with each being individually MINOR.
- Direct contradictions (AP-4) are MAJOR — each pair separately.
- A single AP-6 (credential exposure) is SECURITY-BLOCK regardless of the rest.
- The 200-line guideline isn't the only way to fail dim 1 — low density also costs.
- Heading nesting beyond 4 is AP-9.

The credential pattern shown above (`sk-proj-abc123...`) is intentionally placed inside the `audit-example` fence so the auditor's tests can verify the SEC-OPENAI detection. In a real CLAUDE.md, this would not be inside a fence; it would be operational content, and the marker check would not demote it. The anti-laundering check ensures real credentials don't escape detection even if wrapped in fences.
