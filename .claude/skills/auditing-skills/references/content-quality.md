# Content Quality (Dimensions 3, 5, 10)

How the body of `SKILL.md` and reference files are written. Covers three related dimensions:

- **Dim 3: Token economy** — does every line earn its recurring token cost?
- **Dim 5: Instruction quality** — appropriate freedom level, consistent terms, concrete examples.
- **Dim 10: Agent-fit** — written for the AI consumer, not as human prose.

These overlap heavily. They share this file because the same paragraph of text can be wrong on all three at once.

## Contents

- The recurring-cost frame
- Concision: what to cut
- The three freedom levels
- Consistent terminology
- Examples over prose
- Time-sensitive content
- Agent-fit specifics
- Specific findings to look for

## The recurring-cost frame

Once invoked, `SKILL.md`'s rendered content enters Claude's context as a single message and stays for the rest of the session. Claude Code does not re-read the file on later turns. Auto-compaction keeps the first 5,000 tokens of each invoked skill, with a combined budget of 25,000 tokens across all invoked skills in a session.

Implication: every line in SKILL.md is paid for repeatedly, in every turn. A 50-token explanation of "what is YAML" costs 50 tokens × N turns. The default question for any line: *would Claude be meaningfully worse without this?*

## Concision: what to cut

Default assumption: Claude is already smart. Only add context Claude doesn't have.

Cut:

- **Definitions of well-known concepts.** "PDFs are documents that..." — Claude knows.
- **Marketing prose.** "Welcome to the amazing PDF skill!" — wastes tokens, signals to other tokens this is human-targeted writing.
- **Long *why* explanations.** State the rule. Add a brief rationale only if it changes behavior. "Use forward slashes" is enough; a paragraph about cross-platform path resolution isn't.
- **Encouragement and hedging.** "You might want to consider..." → "Use...". "It would be a good idea to..." → "Do...".
- **Triple repetition of the same point** in different words.

Keep:

- Imperative directives.
- Decision trees and conditionals.
- Examples (especially good/bad pairs).
- File paths and exact commands.
- The narrow specifics that vary across projects (like which library to use).

**Concrete test for a paragraph.** If you delete it, does Claude do something measurably wrong? If yes, keep. If no or "probably not," cut.

## The three freedom levels

Match instruction specificity to the task's fragility.

**High freedom** — multiple valid approaches, decisions depend on context.

```markdown
## Code review process

1. Analyze structure and organization.
2. Check for bugs and edge cases.
3. Suggest readability improvements.
4. Verify project conventions.
```

The model picks methods. Use for: analysis, judgment calls, exploration.

**Medium freedom** — preferred pattern exists, some variation OK.

```markdown
## Generate a chart

Use the project's plotting helper:

    python scripts/plot.py <data.csv> --output <name>.png

Adjust flags as needed for axis labels, color scheme, log scales.
```

A reasonable default with named knobs. Use for: scripted operations with parameters.

**Low freedom** — fragile, error-prone, exact sequence required.

```markdown
## Database migration

Run exactly:

    python scripts/migrate.py --verify --backup

Do not modify the command or add flags.
```

No wiggle room. Use for: destructive operations, security-sensitive flows, anything with strict ordering.

**Finding pattern.** A skill that prescribes a specific 47-step procedure for "explain how this works" is over-constrained — high-freedom task forced into low-freedom shape. A skill that says "deploy how you see fit" for a production deploy is under-constrained — fragile task left at high freedom. Both are MAJOR on dim 5.

## Consistent terminology

Pick one term and use it throughout. Mixing terms makes the model unsure whether you're talking about the same thing.

| Bad (mixed) | Good (consistent) |
|---|---|
| API endpoint, URL, route, path | API endpoint |
| field, box, control, element | field |
| extract, pull, get, retrieve, scrape | extract |
| skill, plugin, extension, addon | skill |

Audit by skimming for synonyms applied to the same concept. Three or more synonyms for the same noun is a MINOR. Inconsistency that creates ambiguity (e.g. "skill" vs "agent" used interchangeably for different things) is a MAJOR.

## Examples over prose

For anything where output quality matters (formats, styles, decisions), include examples — ideally good/bad pairs. One concrete example is worth a thousand words of description.

```markdown
## Commit message format

Good:
    feat(auth): add JWT validation middleware
    
    Validates tokens against the JWKS endpoint with a 5-minute cache.

Bad:
    fixed stuff
    
    fixed it
```

The model can pattern-match on examples in ways it can't on abstract rules. A skill that has rules without examples is harder to follow than one with both.

## Time-sensitive content

Don't include statements that go stale.

```markdown
# Bad
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.

# Good
Use the v2 API endpoint: api.example.com/v2/messages

## Old patterns

<details>
<summary>Legacy v1 (deprecated 2025-08)</summary>
The v1 endpoint was api.example.com/v1/messages, no longer supported.
</details>
```

The "old patterns" pattern keeps history available without cluttering the current path.

**Finding pattern.** Date-conditional instructions, hardcoded version numbers without rationale, or "as of [date]" qualifiers in the main body — all MINOR. If they affect a critical path (the wrong API call), MAJOR.

## Agent-fit specifics (dim 10)

The audited skill is consumed by an AI agent, not read by a human as documentation. These are agent-fit signals:

| Human-targeted (deduct) | Agent-targeted (good) |
|---|---|
| "Welcome to..." opener | Frontmatter, then directives |
| Long preamble explaining purpose | Standing instruction in 2 sentences |
| Decorative headers (icons, art) | Plain headers that scan |
| Tutorial walkthrough | Decision tree or numbered procedure |
| Marketing tone | Imperative |
| One example | Multiple contrasting examples |
| Screenshots | Code blocks and file-tree diagrams |
| "We hope you enjoy..." | (nothing) |

**Finding pattern.** Marketing tone or human-tutorial structure is MAJOR on dim 10. A welcome paragraph or unnecessary backstory is MINOR. Decorative emoji or section banners are NIT.

## Specific findings to look for

### BLOCKER findings

(Rare for these dimensions; almost always Major or Minor.)

### MAJOR findings

- SKILL.md > 500 lines (also dim 4).
- Multi-paragraph explanation of well-known concepts.
- Marketing tone or human-tutorial structure.
- Critical-path instruction includes a hardcoded date or version.
- Inconsistent terminology that creates ambiguity.
- Over-constrained or under-constrained for the task type.
- Decision-affecting rules with no examples.

### MINOR findings

- Welcome paragraph, backstory, or "About this skill" section.
- 3+ synonyms for the same concept.
- Time-sensitive language not in an "old patterns" section.
- Hedging and encouragement language ("might want to consider").
- Repeats the same point in different words.

### NIT findings

- Decorative emoji in section headers.
- Stylistic inconsistencies that don't affect meaning.

## Quick conciseness audit

Open SKILL.md. For each paragraph, ask: "If I cut this, would Claude do something different?" Mark the paragraphs where the answer is no. If those paragraphs total more than 20% of the file, dim 3 takes a MAJOR.
