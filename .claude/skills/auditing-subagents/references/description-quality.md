# Description & Body Quality

## Contents

- Why descriptions matter (routing)
- The "ad copy" model
- What to test for
- Body content guidance

## Why descriptions matter

A subagent's `description:` is the only signal Claude uses to decide whether to **delegate** a task to that subagent. Like skill descriptions, subagent descriptions are read once at session start and again at delegation time.

A vague description ("helps with code") will never get delegated to. A specific description ("Reviews pull-request diffs for code quality, style, and obvious bugs") clearly signals what task this subagent handles.

## The "ad copy" model

A good description leads with the value proposition. The first sentence should let Claude decide whether to route a task here without reading the rest.

Bad:
```audit-example -- reference catalog with auditor-flagged anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
This agent is a helpful assistant that can help with various coding tasks. It uses
modern best practices and is designed to be friendly and efficient. The agent will
do its best to help you with your code.
```

Good:
```audit-example -- reference catalog with auditor-flagged anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
Reviews pull-request diffs for code quality, style violations, obvious bugs, and
test-coverage gaps. Use when reviewing a PR or before merging. Returns a markdown
report with severity-ranked findings.
```

The good description:
- Leads with action ("Reviews")
- States the input (PR diffs)
- States what it produces (markdown report)
- Says when to use it
- Avoids filler ("helpful", "modern best practices", "efficient")

## Audit checks

### Length
- < 50 characters → MAJOR — too short to convey intent
- 50–500 characters → ideal range
- 500–1024 characters → acceptable
- > 1024 characters → BLOCKER (the parser truncates)

### Triggering language
The description should contain at least one of: "use when", "use for", "when reviewing", "when checking", "delegate to ... when". MAJOR if absent — Claude has no signal for when to route here.

### Filler patterns
Flag any of:
- "helpful assistant"
- "various tasks"
- "do its best"
- "designed to be"
- "modern best practices"
- "leverages" without specific object
- "powerful" (subjective, doesn't help routing)

Each filler instance: MINOR.

### Self-reference
Don't say "this agent" or "the subagent" — those are weight. Just say what it does. MINOR.

### Concrete output
The description should hint at what the subagent produces — a report, a diff, a list of suggestions, a JSON object, etc. If absent, MINOR.

## Body content guidance

The body is the subagent's system prompt. The subagent reads the entire body at every spawn.

### Length
- < 50 lines → reasonable for a focused subagent
- 50–200 lines → typical for a complex subagent
- > 500 lines → MAJOR; subagent spawn cost is high

### Structure
A good subagent body:
- Defines the subagent's role and scope in 2–3 sentences
- Lists the operations it performs
- Lists the operations it must **not** perform
- Specifies the output format

### Common body anti-patterns

- **No exclusion language.** Body says what to do but never what to refuse. The subagent will attempt anything asked of it. MAJOR.
- **Aspirational language.** "should consider", "might want to" — see content-quality patterns. MINOR each.
- **Self-praise.** "You are an expert..." in the system prompt is harmless but signals novice authoring. NIT.
- **Output format ambiguity.** No specification of what the subagent returns. MINOR.
- **Tool name confusion.** Body says "use the WebFetch tool" but `tools:` doesn't include WebFetch. MAJOR — silent capability mismatch.

## Subagent vs skill descriptions

Both are ad copy. Subagents have a higher bar because:
- Delegation is more expensive (spawns a new context)
- The subagent runs autonomously after delegation
- A wrong delegation can be hard to detect

So subagent descriptions should be more specific about input/output than skill descriptions.
