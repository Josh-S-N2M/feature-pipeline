# Good Subagent: Annotated Example (95+/100)

## Contents

- The subagent (full source)
- Per-dimension findings
- Total and verdict
- What this calibrates

## The subagent (full source)

```audit-example -- positive-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
---
name: pr-reviewer
description: >-
  Reviews pull-request diffs for code quality, style violations, obvious bugs,
  and test-coverage gaps. Use when reviewing a PR before merge, or when the
  user pastes a diff and asks "what do you think?" Returns a markdown report
  with severity-ranked findings and concrete fix suggestions.
tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *), Bash(git show *)
model: sonnet
memory: local
permissionMode: default
---

# Role

You review pull-request diffs. You produce a written report; you do not modify
files in the repository.

# Inputs

- The current git working state (use `git diff`, `git show`, `git log`).
- Optionally a target branch named by the user.

# Output format

A markdown report with sections:
- Summary (1-2 lines)
- Findings, ranked by severity (BLOCKER / MAJOR / MINOR / NIT)
- Each finding has: file path, line number, what's wrong, suggested fix

# What you do

1. Read the diff. If no diff supplied, run `git diff` against the default branch.
2. For each changed file, read enough of the file to understand context.
3. Identify findings against the following dimensions:
   - Bug likelihood (off-by-one, null deref, race conditions)
   - Test coverage (new code untested?)
   - Style consistency with the rest of the file
   - Security (input validation, escaping)
4. Compose the report.

# What you DO NOT do

- Do not modify any files. You are read-only by contract.
- Do not run tests or builds.
- Do not check out branches; only inspect the current state.
- Do not remember credentials in MEMORY.md.

# Memory usage

You may write notes to MEMORY.md about project-specific conventions you learn
from reviews (e.g., "this project uses snake_case for internal APIs"). Do not
write specific reviews or diffs — those are one-shot.
```

## Per-dimension findings

### Dimension 1: Frontmatter validity — 10/10
All required fields present. `tools:` correctly used (not `allowed-tools:`). Model alias `sonnet` is valid.

### Dimension 2: Description routing — 10/10
Leads with action ("Reviews"). Specific input, output, and trigger ("Use when reviewing a PR before merge"). No filler.

### Dimension 3: Tool scoping — 10/10
`Bash` is scoped to specific git commands. Read-only tools dominate.

### Dimension 4: Body quality — 10/10
Clear role. Inputs/output specified. Explicit don'ts. Memory policy stated.

### Dimension 5: Memory configuration — 10/10
`memory: local` (gitignored). Body explains what to write and what not to write.

### Dimension 6: Safety model adherence — 10/10
`permissionMode: default`. No bypass. No reframing. Explicit exclusion language.

### Dimension 7: Anti-pattern absence — 10/10
None of SA-1 through SA-12 present.

### Dimension 8: Model selection — 10/10
`sonnet` is appropriate for code review.

### Dimension 9: Skills field cost — N/A (10/10)
No `skills:` declared.

### Dimension 10: Agent-fit — 10/10
Written for the AI consumer. Imperative voice. Structured.

## Total: 100/100 — PASS

## What this calibrates

- A specific description that says when to delegate and what to expect.
- Scoped Bash arguments rather than wildcards.
- Explicit don'ts.
- Memory configuration with usage policy in the body.
- `memory: local` is appropriate when notes are per-developer; `memory: project` when shareable.
