# Workflows and Feedback Loops (Dimension 6)

How multi-step procedures should be expressed in a skill. Use this when scoring dimension 6.

## Contents

- When this dimension applies
- The numbered-steps pattern
- The checklist pattern
- The validator loop
- Plan-validate-execute
- Specific findings to look for

## When this dimension applies

Score dim 6 only for skills that involve multi-step procedures, batch operations, or any work where ordering matters. For pure reference / knowledge skills (e.g. "API conventions for our team"), this dimension is N/A — score 10 and note in the report.

Examples that need workflow structure:

- Deployment procedures
- Database migrations
- Form filling, document editing
- Test generation + run + analyze cycles
- Anything that mixes script execution with judgment

## The numbered-steps pattern

Multi-step procedures should be numbered, atomic, and verifiable. Not:

```markdown
First you'll want to look at the data, then think about whether the approach
makes sense, and finally implement it while making sure to test along the way.
```

But:

```markdown
1. Read the input file.
2. Identify the schema (run scripts/detect_schema.py).
3. Validate the schema against expected fields.
4. Apply transforms.
5. Write output to the configured path.
6. Verify the output (run scripts/verify.py).
```

Each step is one action. Each step's success or failure is checkable.

**Finding:** prose-form workflows (no numbering) for multi-step tasks: MAJOR. Numbered steps that are actually composite ("1. Set up everything" hiding 8 sub-steps): MINOR.

## The checklist pattern

For longer or harder workflows, give Claude a checklist to copy and check off as it works. This visibly tracks progress and prevents skipped steps.

```markdown
## PDF form filling workflow

Copy this checklist and check off each item as you complete it:

- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)

(then detail for each step below)
```

The checklist isn't decorative — it gets carried in Claude's response and serves as a working memory aid. For workflows >5 steps or that span multiple turns, the checklist pattern is recommended.

**Finding:** Workflow >5 steps with no checklist: MINOR. Workflow that spans multiple turns with no checklist: MAJOR (Claude tends to skip steps after summary/compaction).

## The validator loop

Quality-critical work benefits from an explicit validator → fix → repeat pattern. The structure:

```markdown
1. Make changes.
2. Run the validator.
3. If validation fails:
   - Read the error.
   - Fix the issue.
   - Re-run the validator.
4. Only proceed when validation passes.
5. Continue with the next step.
```

The validator can be a script (`pytest`, a schema check) or a reference document the agent compares against (style guide, checklist).

**Finding:** Critical-output skills (code generation, document editing, schema changes) without any validation step: MAJOR. With validation but no failure-handling guidance ("if it fails, ..."): MINOR.

## Plan-validate-execute

For batch operations, destructive changes, or anything with high blast radius, recommend the plan-validate-execute pattern:

1. **Plan** — Claude writes the intended changes to a structured intermediate file (e.g. `changes.json`).
2. **Validate** — a script checks the plan against constraints (referenced fields exist, no conflicting changes, required fields present).
3. **Execute** — only after validation passes, apply the changes.
4. **Verify** — confirm the result matches the plan.

This catches errors before they touch the original. It's the same pattern as a SQL `EXPLAIN` before `EXECUTE`.

**Finding:** Skills doing batch destructive operations without plan-validate-execute: MAJOR. With it, but skipping verify: MINOR.

## Specific findings to look for

### BLOCKER findings

- Workflow with destructive ordering ambiguity (e.g. "deploy and run migration in some order") with no explicit sequence: BLOCKER on dim 6.

### MAJOR findings

- Multi-step task expressed as prose paragraph instead of numbered steps.
- Workflow that spans multiple turns with no checklist (steps get skipped after compaction).
- Critical-output skills (code, schema, docs) with no validation step.
- Batch destructive operations without plan-validate-execute.
- Validation step exists but no guidance on what to do when it fails.

### MINOR findings

- Workflow >5 steps without a copy-the-checklist pattern.
- Composite steps that hide 5+ sub-steps under one number.
- "Run tests" without saying which tests, where, or how to interpret failures.
- Validation present but verbose enough to slow the loop unnecessarily.

### NIT findings

- Step phrasing inconsistent ("First", "2.", "Next, you should").
- Checklist uses different bullet styles in different sections.

## What "good" looks like

A workflow section earns full marks on dim 6 when:

- Steps are numbered and atomic.
- Critical operations have a validator.
- The validator failure path is explicit.
- Steps that span turns include a checklist.
- Destructive operations follow plan-validate-execute.
- The final step is a verification, not an execute.

A pure-reference skill ("API conventions for our team") with no workflow at all also earns full marks — N/A is fine, this dimension doesn't try to force workflows on skills that don't need them.
