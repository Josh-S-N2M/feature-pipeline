# Common Failures and Debugging

Cross-cutting symptoms that don't fit cleanly into one dimension. Read this when triaging "the skill exists but doesn't work."

## Contents

- Skill never triggers
- Skill triggers wrongly
- Skill loads but errors out
- Token-budget overflow
- Live change detection
- Scope collisions

## Skill never triggers

Symptom: user types something that should fire the skill; nothing happens.

Diagnose in this order:

1. **Is the skill listed?** Run `/skills` (Claude Code) or ask Claude "what skills do you have access to?". If the skill name isn't there, it was never discovered. Causes:
   - File isn't at the expected path. Personal: `~/.claude/skills/<name>/SKILL.md`. Project: `.claude/skills/<name>/SKILL.md`.
   - Filename is wrong. Must be exactly `SKILL.md` (uppercase).
   - YAML frontmatter failed to parse silently.
   - Plugin not activated.

2. **Is the YAML valid?** Run `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`. If that errors, the loader silently dropped the skill. Common causes:
   - Tab character anywhere in the frontmatter.
   - Missing closing `---`.
   - Unquoted colon in a value.
   - BOM at the start of the file.
   - Block scalar (`>` or `|`) reflowed by Prettier.

3. **Is the description doing its job?** This is responsible for ~90% of trigger failures with otherwise valid skills. Check `descriptions-and-triggering.md`.

4. **Is the description being truncated?** Default skill-listing budget is ~15K chars / ~4K tokens. If you have many skills with verbose descriptions, the tail gets cut and trigger keywords go missing. Set `SLASH_COMMAND_TOOL_CHAR_BUDGET=30000` (or higher) and retest.

5. **Did you restart the session?** Claude Code reads skills at session start. New skills don't appear in active sessions until restart (unless they're in a directory already being watched — see live change detection below).

6. **Scope collision.** A project-local `.claude/skills/foo/` overrides `~/.claude/skills/foo/`. If your updated personal skill isn't working, an older project version may be winning.

## Skill triggers wrongly

Symptom: skill fires on the wrong things, or fires too often.

Causes:

- **Description is too broad.** Add exclusion language ("NOT for X, Y, Z").
- **Description shares keywords with another skill that should win.** Make this skill's description more specific to its niche; consider what differentiates it from the competing skill.
- **Description matches a near-miss.** "Database query optimization" matches "I have a database question" even when it's not about queries. Tighten with verbs and contexts.

If a skill should never auto-trigger (workflows with side effects, deployments, etc.), set `disable-model-invocation: true`.

## Skill loads but errors out

Symptom: skill triggers, then halts mid-execution.

Causes:

- **Missing dependency.** The skill calls `npx`, `uv`, `python3 -m something` — but it's not installed in the user's environment. Document prerequisites in SKILL.md and add a fail-fast check at the top.
- **Missing environment variable.** Skill assumes the required env var is exported. Example pattern:
```audit-example -- common-failures catalog demonstrating credential-shaped string; documents what the auditor scanner detects
[ -z "$GITHUB_TOKEN" ] && { echo "ERROR: GITHUB_TOKEN not set"; exit 1; }
```
- **Reference Illusion.** SKILL.md links to a file like `references/<name>.md` which doesn't exist. Claude tries to read it and fails.
- **Path bugs.** Hardcoded `/home/user/...` instead of `${CLAUDE_SKILL_DIR}/...`. Use the substitution every time.
- **Permission issue (Windows/WSL).** `chmod -R 755` on the skill directory.

## Token-budget overflow

Symptom: skill descriptions are silently truncated, trigger keywords disappear from the last few skills loaded.

The default skill-listing character budget is ~15,000 characters / ~4,000 tokens. With more than 3–5 verbose skills, you run out.

Fixes:

- Raise the budget: `export SLASH_COMMAND_TOOL_CHAR_BUDGET=30000`.
- Shorten descriptions across all skills (the budget is shared).
- For low-priority skills, set `"name-only"` in `skillOverrides` (settings) so they list without descriptions.
- Trim each skill's description + when_to_use to under 1,536 chars (the per-skill cap regardless of overall budget).

When auditing, mention this in the report's notes section if the audited skill has a verbose description that contributes to budget pressure.

## Live change detection

Claude Code watches `~/.claude/skills/`, project `.claude/skills/`, and `--add-dir`-supplied `.claude/skills/` for file changes. Edits to existing files are picked up within the current session.

What requires a restart:

- Creating a top-level skills directory that didn't exist when the session started.
- Adding a new `--add-dir` directory.
- Plugin installations.

If a skill edit isn't taking effect, save the file and ask Claude "what skills do you have?" — that should refresh.

## Scope collisions

Skills load from multiple locations. When two have the same name, precedence is:

```
Enterprise (managed)  >  Personal (~/.claude/)  >  Project (.claude/)  >  Plugin (namespaced)
```

Plugin skills are namespaced (`plugin-name:skill-name`) and can't conflict.

The classic trap: an old `commit` skill in `.claude/skills/` (project) overrides your updated personal version at `~/.claude/skills/commit/`. The personal version never loads. Symptoms feel like "my edits aren't taking effect" but the actual cause is precedence.

When auditing, check for same-named skills at multiple scopes and note any collisions in the report.

## A debugging order to recommend

When the user is stuck:

1. `/skills` — is it listed?
2. If not: check path, filename, YAML.
3. If listed but not firing: check description verbs and contexts.
4. If firing but failing mid-run: check dependencies, environment, paths, broken references.
5. If firing wrongly: tighten description, add exclusions.
6. If many skills installed and the new one stopped working: check token budget overflow.

A skill audit can pre-empt most of these, but when an audit can't be done, this checklist gets a real user unstuck fast.
