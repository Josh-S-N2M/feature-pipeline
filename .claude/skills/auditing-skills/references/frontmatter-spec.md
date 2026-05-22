# Frontmatter Spec (Dimension 2)

The canonical reference for the YAML frontmatter at the top of every `SKILL.md`. Use this when scoring dimension 2.

## Contents

- The format
- Hard validation rules (BLOCKER if violated)
- Recognized fields (full table)
- Field-name confusion gotchas
- Common YAML traps
- Combined-text character cap

## The format

Every `SKILL.md` begins with YAML frontmatter between `---` delimiters on lines of their own:

```yaml
---
name: my-skill
description: What this skill does and when to use it.
---

# My Skill

(body...)
```

The opening `---` must be the very first line. The closing `---` must be on its own line. Whitespace before the opening `---` or a missing closing `---` causes a silent parse failure — the entire skill is dropped from Claude's available list.

## Hard validation rules (each is a BLOCKER)

These are checked deterministically by `scripts/validate_frontmatter.py`. Any violation is a BLOCKER on dimension 2.

1. The frontmatter must parse as valid YAML.
2. `name`, if present, must be ≤ 64 characters, lowercase letters + numbers + hyphens only.
3. `name` must not contain XML tags.
4. `name` must not contain the reserved words `anthropic` or `claude`.
5. `description`, if present, must be ≤ 1024 characters.
6. `description` must not be empty.
7. `description` must not contain XML tags.
8. The frontmatter must use spaces, not tabs (YAML spec).
9. String values containing colons must be quoted (`"value: with colon"`).

If `name` is omitted, the directory name is used. If `description` is omitted, the first paragraph of the body is used — but this is a MAJOR finding because relying on the body is fragile.

## Recognized fields

All fields except `description` are optional. Only fields in this table are recognized — anything else is silently ignored.

| Field | Type | Default | Notes |
|---|---|---|---|
| `name` | string | directory name | Slash command name |
| `description` | string | first body para | Triggers the skill; max 1024 chars |
| `when_to_use` | string | — | Appended to description in skill listing |
| `argument-hint` | string | — | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | string \| list | — | Named positional args for `$name` substitution |
| `disable-model-invocation` | bool | false | If true, only user can invoke (no auto-trigger) |
| `user-invocable` | bool | true | If false, hidden from `/` menu |
| `allowed-tools` | string \| list | — | Pre-approves tools while skill is active |
| `model` | string | — | Override model for this skill's turn |
| `effort` | string | — | low / medium / high / xhigh / max |
| `context` | string | — | Set to `fork` to run in subagent |
| `agent` | string | general-purpose | Subagent type when `context: fork` |
| `hooks` | object | — | Skill-scoped lifecycle hooks |
| `paths` | string \| list | — | Glob patterns that gate auto-loading |
| `shell` | string | bash | bash or powershell |
| `mcp-servers` | list | — | MCP servers required by the skill |
| `permission-mode` | string | — | Permission level applied during the skill |

## Field-name confusion gotchas (high-impact MAJORs)

These are silent failures that don't break parsing but break behavior. Always check.

**`tools:` instead of `allowed-tools:`** — The agent file format (`.claude/agents/*.md`) uses `tools:`. The skill format uses `allowed-tools:`. If a skill uses `tools:`, it's silently ignored and the field has no effect. There's a documented credential-hunting incident from this exact bug ([anthropics/claude-code#27099](https://github.com/anthropics/claude-code/issues/27099), Feb 2026). Score: BLOCKER on dim 2 + MAJOR on dim 8 (security).

**`triggers:` instead of `description` content** — Some early community guides recommended a `triggers:` array. The current spec doesn't recognize it. Trigger phrases go in the `description` itself.

**`tags:` or `categories:`** — Not recognized. Authors use these for organization but they have no effect on triggering.

**Typos:** `discription:`, `descripton:`, `descritpion:` — silently ignored, skill loses its description, becomes nearly impossible to trigger.

## Common YAML traps

- **Tabs in the frontmatter block.** YAML requires spaces. A tab anywhere causes parse failure.
- **Unquoted colons.** `description: Run tests: report results` — the second colon breaks parsing. Quote the whole value: `description: "Run tests: report results"`.
- **Unquoted apostrophes.** `description: Don't run tests` — the apostrophe is fine in YAML but breaks some parsers. Use double quotes when in doubt.
- **Block scalars (`>` or `|`) and Prettier.** A multi-line description using `>-` works in isolation but Prettier auto-formatters can reflow the text and break the loader. Prefer a single logical line, or add a `# prettier-ignore` comment above the block.
- **BOM (byte-order mark).** Some editors prepend a UTF-8 BOM. The frontmatter must start at byte 0 — a BOM breaks it.
- **Missing closing `---`.** The body becomes part of the YAML attempt, parser fails silently.

## Combined-text character cap

Description + when_to_use are concatenated and truncated at **1,536 characters** in the skill listing Claude sees. Beyond that, your trigger keywords get cut off and the skill stops firing.

If `description` + `when_to_use` together exceed 1,536 chars, that's a MAJOR — Claude can't see the tail of your text.

## Token-budget overflow (cross-cutting)

The skill listing (all skill names + descriptions combined) is also subject to a budget — default ~15,000 chars / ~4,000 tokens, controlled by `SLASH_COMMAND_TOOL_CHAR_BUDGET`. Past that, descriptions get silently truncated globally. This is not a finding against a single skill but worth flagging in the audit notes if the audited skill's description is verbose enough to push others over the limit.
