# Descriptions and Triggering (Dimension 1)

The description is ~90% of trigger success. If a skill never fires, this is almost always why. Use this when scoring dimension 1.

## Contents

- Why descriptions dominate
- The five things a good description does
- Directive vs descriptive language
- The trigger-keyword test
- Length, point-of-view, and the 1,536-char cap
- Specific findings to look for

## Why descriptions dominate

At session start, Claude loads only the metadata (name + description) for every available skill. The body of `SKILL.md` doesn't load until Claude decides to invoke. That decision is made almost entirely from the description.

Field signal from late 2025 / early 2026: directive description language ("ALWAYS invoke when...") measurably outperforms descriptive language ("Helps with...") for autonomous triggering. Anthropic's own Skill Creator data shows improvements on 5 of 6 public skills tested.

## The five things a good description does

1. **Opens with a verb in third person, not first or second.** "Audits Claude Code skills..." — not "I audit..." or "You can use this to audit...". The description is injected into the system prompt; mixed point-of-view confuses skill selection.
2. **Names the object concretely.** "any Claude Code skill (a directory containing SKILL.md)" gives Claude a recognizable shape. "skill files" is too vague.
3. **Lists trigger verbs and contexts.** "ALWAYS invoke when reviewing, auditing, evaluating, scoring, vetting, fixing, improving..." — covers the natural ways a user might phrase the request.
4. **Includes common failure cues.** "when triaging 'why isn't my skill triggering'" — matches what frustrated users actually type.
5. **Tells the model what it gets back.** "Produces a standardized audit report with a 100-point score..." — makes the model prefer this skill over inventing its own approach.

## Directive vs descriptive language

| Descriptive (weak) | Directive (strong) |
|---|---|
| Helps with PDF processing | Extracts text and tables from PDFs. ALWAYS invoke when... |
| For code review tasks | Reviews code for bugs, security, performance. Use when reviewing PRs, diffs, or staged changes. |
| A skill for managing tests | Generates, runs, and analyzes tests. Invoke for any test-related work including writing new tests, debugging failures, or measuring coverage. |

Directive language reads as a command to the model, not a description to a human reader.

**Finding pattern.** If the description starts with "A skill that...", "Helps...", "For...", "Used for...", that's a MINOR. If it never includes trigger phrases or use contexts, that's a MAJOR.

## The trigger-keyword test

Read the description. Then ask: "What words would a user have to say for Claude to think this skill is relevant?" If you can't list 3+ likely trigger phrases without inventing them, the description is too vague.

Apply the inverse test too: "What near-miss phrases would falsely fire this skill?" If a "git commit helper" would fire on every mention of git (clone, status, log), that's a missing-exclusion problem (see anti-patterns.md).

## Length, point-of-view, and the 1,536-char cap

- **Hard cap:** description ≤ 1,024 characters (frontmatter spec).
- **Combined cap:** description + `when_to_use` ≤ 1,536 chars in the skill listing — past this, text gets truncated and trigger keywords are lost.
- **Sweet spot:** 200–600 characters. Short enough to be scannable in the listing, long enough to carry trigger verbs and contexts.
- **Point of view:** third person, always. "Audits..." not "I audit..." or "You can use this to audit...".
- **No XML tags** in the description (validation rule — would BLOCK).

## Specific findings to look for

### MAJOR findings

- Description starts with "Helps", "A skill for", "Used to", "For" — descriptive opener instead of directive.
- Description omits both "use when" and trigger verbs — Claude has nothing to match on.
- Description is in first person ("I help you...") or second person ("Use this to...").
- Description repeats the skill name without adding info ("PDF processor: processes PDFs").
- Description + when_to_use together exceed 1,536 characters (truncation).
- Description contains XML-style tags like `<context>` or `<task>`.

### MINOR findings

- Description is under 100 characters (probably too thin to carry triggers).
- Description over 800 characters when 400 would do (forces other skills' descriptions into the budget).
- Description uses inconsistent terms ("skill" vs "extension" vs "plugin" in the same paragraph).
- No mention of what the skill returns or produces.

### NIT

- Description ends with a period (some authors omit; either is fine but consistency within a project is nicer).
- Description is in title case rather than sentence case.

## Example fix templates

Use these as starting points when proposing fixes in the report.

**Vague → specific:**

```yaml
# Before
description: Helps with database stuff.

# After
description: >-
  Generates, applies, and rolls back database migrations from schema changes.
  Use when modifying models, adding columns, or when the user mentions migrations,
  schema changes, or "alter table". Supports Postgres, MySQL, SQLite. Generates
  paired up + down migrations.
```

**First person → third person:**

```yaml
# Before
description: I'll help you write better commit messages.

# After
description: >-
  Generates conventional commit messages by analyzing the staged diff. Use when
  the user asks for help committing, wants a commit message written, or types
  /commit. Returns a properly formatted message ready to paste.
```

## Special case: `disable-model-invocation: true`

When this is set, Claude won't auto-trigger. The description still matters for the `/skills` menu, but trigger keywords are less critical. Apply dimension 1 with a softer touch — the description should be clear and accurate but doesn't need exhaustive trigger phrases. Cap deductions at MAJOR.
