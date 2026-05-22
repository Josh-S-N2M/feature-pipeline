# Progressive Disclosure (Dimension 4)

How content should be split across files. The point is to keep `SKILL.md` lean while making detailed material available on demand. Use this when scoring dimension 4.

## Contents

- The three loading levels
- The 500-line rule
- One level deep
- The TOC rule
- Orphans
- Specific findings to look for

## The three loading levels

1. **Metadata** — `name` and `description` from frontmatter. Always loaded into Claude's context for every available skill.
2. **SKILL.md body** — Loaded the moment Claude invokes the skill. Stays in context for the rest of the session (subject to auto-compaction).
3. **Bundled files** — Reference files, scripts, assets. Read on demand via `Read` tool. Zero cost until accessed.

The pattern that exploits this: keep `SKILL.md` short and pointed; push detail into `references/` files that are read only when needed.

## The 500-line rule

`SKILL.md` body should be under 500 lines. Past that, it's almost always doing too much. Split into reference files.

Why 500? Because the body stays in context for the entire session after invocation. Every line is recurring token cost. A bloated body crowds out conversation history and other skills.

**Finding:**
- Body > 500 lines: MAJOR.
- Body > 1000 lines: BLOCKER (the file is doing the work that progressive disclosure was designed to avoid).
- Body 300–500 lines and could clearly be split: MINOR.

## One level deep

References should be one level deep from `SKILL.md`. Avoid:

```
SKILL.md → ref-A.md → ref-B.md → ref-C.md
```

When Claude follows nested references, it often previews with `head -100` or similar, ending up with incomplete content. Keep all reference files linked directly from `SKILL.md`.

```
SKILL.md ───→ ref-A.md
         ───→ ref-B.md
         ───→ ref-C.md
```

The script `lint_references.py` checks this deterministically. Any reference file linking to another reference file is a finding.

**Finding:**
- Reference file links to another reference file: MAJOR per occurrence.
- Reference depth ≥ 3: BLOCKER.

Cross-references between reference files for context (e.g. "see also security-checklist.md") are fine if SKILL.md also links to that file directly. The rule is about discovery paths, not all mentions.

## The TOC rule

Reference files longer than ~100 lines should include a navigable index near the top. Without one, Claude may partially read the file (`head -100`) and miss content.

The property is *navigable index near the top*, not a specific heading string. Any of these forms count:

- `## Contents`
- `## Table of contents`
- `## In this file` / `## In this document`
- `## On this page`
- `## What's here` / `## What's inside`
- `## Sections`
- `## Outline`

Pattern:

```markdown
# File title

Brief description of what this file covers and when to read it.

## Contents

- Section A
- Section B
- Section C

## Section A
...
```

The deterministic linter (`scripts/lint_references.py`) accepts all of the above heading variants at H2 or H3 level, case-insensitive. If you find a long file flagged for "no recognized table-of-contents heading," verify by inspecting the first 30 lines: if a clear navigable index is present under any reasonable heading, drop the finding and note the false positive in the report.

**Finding:**
- Reference file > 100 lines without TOC heading: MINOR.
- Reference file > 300 lines without TOC heading: MAJOR.

## Orphans

Files in the skill directory that aren't referenced from `SKILL.md` (or any reference file) are orphans. They consume disk and confuse maintainers but never reach Claude's context.

Two flavors:

1. **Forgotten files** — author created a file like `references/<name>.md` and never linked it. Usually a bug; the content should either be linked or deleted.
2. **Intentional bundles** — scripts in `scripts/` that are executed by paths in SKILL.md, or templates in `assets/` that are read by scripts. Not orphans even if they don't appear as Markdown links.

The `lint_references.py` script knows the difference: it considers a file "linked" if it appears as a Markdown link, a backticked path, or a path inside a `python ... script.py` execution string.

**Finding:**
- Markdown file in `references/` (e.g. `references/<name>.md`) that's never linked: MAJOR (missed loading opportunity).
- Script in `scripts/` that no instruction tells Claude to run: MAJOR (dead code).
- Asset/template never referenced: MINOR (probably intended for future use).

## Reference Illusion (related but separate — also dim 9)

The opposite of orphans: SKILL.md links to files that don't exist. Always a BLOCKER on dim 4 because the reference can't load. Often correlates with a security finding (a malicious skill might reference a "setup script" that gets created later via prompt injection).

The script `lint_references.py` catches this deterministically.

## Specific findings to look for

### BLOCKER findings

- SKILL.md references files that don't exist (Reference Illusion).
- Reference depth ≥ 3 (very nested).
- SKILL.md > 1000 lines.

### MAJOR findings

- SKILL.md > 500 lines.
- Reference file links to another reference file (depth-2 nesting).
- Markdown file in `references/` that's never linked from SKILL.md.
- Script in `scripts/` with no instruction to run it.
- Reference file > 300 lines without a TOC.

### MINOR findings

- SKILL.md 300–500 lines and could be split.
- Reference file 100–300 lines without TOC.
- Asset/template never referenced.
- Inconsistent linking style (mix of Markdown links and bare prose paths).

## Pattern: when to split

A SKILL.md grows past 500 lines because:

- A single dimension dominates (most often: a long catalog of examples or a long anti-pattern list).
- It's covering multiple domains (the Everything Skill anti-pattern — see anti-patterns.md).
- It hasn't been edited since the first draft.

Refactor:

1. Identify the single largest section.
2. Move it to `references/<topic>.md`.
3. Replace the section in SKILL.md with a one-paragraph summary plus a link.
4. Repeat until SKILL.md is back under the threshold.

If splitting one section doesn't help much, the skill is probably trying to do too many things — recommend splitting it into multiple skills.
