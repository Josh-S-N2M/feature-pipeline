# Anti-Pattern Catalog (Dimension 9)

The named anti-patterns. Each has a recognizable shape, a why-it's-wrong, and a fix template. Use this when scoring dimension 9.

## Contents

- The Reference Illusion
- Description Soup
- Template Theater
- The Everything Skill
- Orphaned Sections
- Tool Overload
- Missing Exclusions
- The Welcome Mat
- Punt-to-Claude
- Voodoo Constants

## The Reference Illusion

**Shape:** SKILL.md links to files that don't exist. For example, a markdown link with target `advanced.md` when no such file exists in the directory.

**Why wrong:** Claude tries to read it, gets an error, has to recover. Sometimes it hallucinates content for the missing file.

**Detect:** `lint_references.py` catches this deterministically.

**Fix:**
- Either create the file with real content, or
- Inline the content into SKILL.md, or
- Remove the broken reference.

**Severity:** BLOCKER (also flagged on dim 4).

## Description Soup

**Shape:** Description is so vague that Claude can't tell when to fire. "Helps with files." "For documentation tasks." "A useful skill."

**Why wrong:** Description is the trigger. Vague description → never triggers, or triggers on the wrong things.

**Detect:** Description has no trigger verbs, no concrete object, no use contexts.

**Fix template:**

```yaml
description: >-
  [What it does in 1 sentence with a concrete object.]
  Use when [the user does X, Y, or Z], when [common failure phrase], or when
  [domain-specific context]. Returns [output description].
```

**Severity:** MAJOR on dim 9 (often co-occurs with MAJOR on dim 1).

## Template Theater

**Shape:** Skill is 90% templates and example output, 10% actual instructions. Pages of "here's what the output looks like" but barely any "here's how to decide what to do."

**Why wrong:** Claude doesn't need templates of expected output — it needs decision logic. Templates are for humans who'll fill them in. Claude needs "if X then A; if Y then B."

**Detect:** Reference files that are mostly fenced code blocks of example output, with no surrounding decision tree.

**Fix:** Replace template-dominated content with decision trees and "when to use which pattern" guidance. Keep one or two short examples; cut the rest.

**Severity:** MAJOR.

## The Everything Skill

**Shape:** One skill that covers React, API design, CSS layout, database optimization, and deployment. Description tries to cover all of it: "Helps with frontend, backend, infra, and design."

**Why wrong:**

- Too broad to trigger correctly (matches everything, fires on too many things).
- Mixes concerns that have nothing to do with each other.
- Body is bloated because it's actually 5 skills welded together.
- Token economy suffers because the entire content loads when only one slice was needed.

**Detect:** Description lists 3+ unrelated domains. Body has top-level headers for unrelated topics.

**Fix:** Split into focused skills.

```
everything-skill/  →  react-performance/
                  →  api-design/
                  →  css-layout/
                  →  postgres-tuning/
                  →  deployment/
```

**Severity:** MAJOR. BLOCKER if the breadth makes it impossible to score the other dimensions coherently.

## Orphaned Sections

**Shape:** Skill has a file like `references/<name>.md` but SKILL.md never tells Claude when to read it. The file exists; the trigger doesn't.

**Why wrong:** Files Claude doesn't know about don't help. The content is invisible.

**Detect:** `lint_references.py` finds files in the skill dir that aren't linked from SKILL.md.

**Fix:** Add an explicit pointer from SKILL.md, like a "see references/database-antipatterns.md for X" line.

**Severity:** MAJOR per orphaned reference file. MINOR for orphaned assets/templates that are clearly intended for future use.

## Tool Overload

**Shape:** `allowed-tools` lists every tool under the sun. Skill is a documentation lookup but pre-approves `Bash`, `Write`, `Edit`, `WebFetch`.

**Why wrong:** Larger attack surface, more tokens spent on tool descriptions, easier for the skill to do something unintended.

**Detect:** `allowed-tools` lists tools the skill body never uses.

**Fix:**
- Read-only skill: `Read Grep Glob`
- File modifier: `Read Write Edit`
- Build/test integration: `Read Write Bash(npm:*) Bash(git:*)` (scoped)
- Avoid `Bash` unscoped unless genuinely needed.

**Severity:** MAJOR for unscoped `Bash` on a skill that doesn't need shell. MINOR for one or two extra tools.

## Missing Exclusions

**Shape:** Description triggers on a broad keyword without saying what's *not* in scope. "Database query optimization" — fires on every database question, including ones it can't handle (MongoDB queries when the skill is Postgres-only).

**Why wrong:** False activations waste context and produce bad answers.

**Fix template:**

```yaml
description: >-
  PostgreSQL query optimization. Use when the user has slow queries, EXPLAIN
  output, or index questions specific to Postgres. NOT for MySQL, MongoDB,
  schema design, or ORM-level issues.
```

The "NOT for..." clause is doing real work — it tells Claude when to *not* fire.

**Severity:** MINOR if the skill works but over-fires occasionally. MAJOR if the false-fire rate makes the skill counterproductive.

## The Welcome Mat

**Shape:** SKILL.md opens with "Welcome to the X skill! This skill will help you do amazing things with..." Marketing prose.

**Why wrong:** Wastes tokens (recurring cost). Signals to the model that this is human-targeted writing. Sets the wrong tone for the rest of the file.

**Detect:** Any opener that addresses Claude or the user directly with welcome/encouragement language.

**Fix:** Delete the opener. Start with the standing instruction or directive. The frontmatter description is the introduction.

**Severity:** MINOR (also flagged on dim 10 agent-fit).

## Punt-to-Claude

**Shape:** Scripts that fail on predictable error conditions and let Claude figure it out. Or instructions that say "decide based on the situation" without giving criteria.

**Why wrong:** Claude inherits work the script (or rule) should have handled. Inconsistent results across runs.

**Fix:** Handle predictable errors in the script. Provide explicit criteria in instructions.

**Severity:** MAJOR per significant occurrence (also dim 7 for scripts, dim 5 for instructions).

## Voodoo Constants

**Shape:** Numeric constants in scripts with no explanation. `TIMEOUT = 47`. `RETRIES = 5`.

**Why wrong:** Forces guessing. If the value needs adjusting, no one knows what's safe.

**Fix:** Add an inline comment explaining the value.

```python
# 30s covers slow networks; longer than typical SLO with margin.
REQUEST_TIMEOUT = 30
```

**Severity:** MINOR per occurrence (also dim 7).

## Quick scoring guide

A skill scores 10 on dim 9 when none of these are present.

Per occurrence:

- BLOCKER patterns (Reference Illusion): 10 points off, dimension floors at 0.
- MAJOR patterns (Description Soup, Template Theater, Everything Skill, Orphaned Sections, Tool Overload, Punt-to-Claude): 4 points off each, cap at 10 off.
- MINOR patterns (Missing Exclusions, Welcome Mat, Voodoo Constants): 2 points off each, cap at 10 off.

If multiple anti-patterns of the same severity hit, deduct each but don't double-penalize the same root cause across dimensions. Note the cross-dimension overlap in the report.
