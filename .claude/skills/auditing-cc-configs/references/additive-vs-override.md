# Additive vs Override Precedence

## Contents

- Why this matters
- Additive primitives
- Override primitives
- Hybrid: hooks plus settings precedence
- Implications for auditing

Different Claude Code primitives have different rules about what happens when the same thing is defined at multiple scopes. This matters because the wrong assumption produces dead rules, double-firing hooks, or confusion about which definition is actually in effect.

This reference is the authoritative answer for cross-file check X18 (same-named primitive at multiple scopes) and informs several others.

## Source

`code.claude.com/docs/en/skills`, `code.claude.com/docs/en/sub-agents`, `code.claude.com/docs/en/hooks`, `code.claude.com/docs/en/mcp`, `code.claude.com/docs/en/memory`. Last verified 2026-05.

## The semantic distinction

| Behavior | Meaning |
|---|---|
| **Additive** | All levels contribute. Duplicates double-fire or waste tokens. |
| **Override** | More specific scope wins. Lower-scope definition is dead (shadowed). |
| **Merge (mixed)** | Array fields merge; scalar fields override. |

## Per-primitive table

| Primitive | Behavior | Precedence (high → low) | Same-name collision result |
|---|---|---|---|
| **CLAUDE.md / rules** | Additive | All scopes contribute simultaneously | Token waste, possible contradiction |
| **Skills** | Override | managed > user > project | Lower scope dead |
| **Subagents** | Override | managed > CLI flag > project > user > plugin | Lower scope dead |
| **MCP servers** | Override | local > project > user | Lower scope dead |
| **Hooks** | Additive | All scopes contribute | Hook fires N times for N definitions |
| **Settings (scalar fields)** | Override | managed > CLI > local > project > user | Lower scope value not applied |
| **Settings (array fields like permissions.allow)** | Merge | (combined from all scopes) | Combined; deny still wins over any allow |
| **Permission deny rules** | Additive (and absolute) | All scopes contribute; cannot be overridden | All denies merged; any deny blocks regardless of allows |
| **Output styles** | Override | managed > user > project | Lower scope dead |
| **Auto memory** | N/A — single scope only | machine-local, per project (per worktree) | N/A |
| **Subagent memory** | Override by name | declared scope (user/project/local) is the only one | N/A — same name in different scopes is two different memories |

## Implications for the auditor

### For override primitives

When the same name appears at multiple scopes, the lower-precedence scope is **dead code**. The audit emits:

- **MINOR** finding: "Skill/subagent/MCP server `<name>` at <lower-scope> is shadowed by definition at <higher-scope>. Lower scope will never be used."
- If the lower-scope version has a SECURITY-BLOCK, escalate to MAJOR — even if it's dead, its presence in the repo may cause confusion or be activated by removing the higher-scope file.

### For additive primitives

Same content at multiple scopes wastes resources:

- **CLAUDE.md duplication**: MINOR. Same rule loaded twice means it counts against context budget twice. Also creates a maintenance burden — updating one without the other leads to drift.
- **Hook duplication**: MINOR–MAJOR. The hook fires multiple times. For idempotent logging hooks this is harmless; for state-modifying hooks it's a bug.
- **Permission deny duplication**: INFO. Harmless functionally (deny wins regardless), but signals the author may not understand the merge behavior.

### For settings (mixed)

The auditor must know which fields are arrays and which are scalars to predict the merge:

**Scalar fields (override):**
- `model`, `outputStyle`, `cleanupPeriodDays`, `includeCoAuthoredBy`, `apiKeyHelper`, `forceLoginUUID`, all the `disable*` lockdown knobs.

**Array fields (merge):**
- `permissions.allow`, `permissions.ask`, `permissions.deny`, `permissions.additionalDirectories`, `companyAnnouncements`.

**Object fields (deep merge for known sub-keys):**
- `permissions` (sub-fields merge per their own rules)
- `env` (key-by-key override at scalar level)
- `hooks` (additive — see hooks row)
- `statusLine` (override as a whole)

### Special case: permission deny is absolute

This is the cornerstone rule for the auditor's security posture.

> If a tool is denied at any level, no other level can allow it. A managed deny cannot be overridden by `--allowedTools`, and `--disallowedTools` can add restrictions beyond managed settings.

Implications:

- A `permissions.deny` rule in managed settings is the strongest possible guardrail in Claude Code.
- An `allow` rule at any level that is shadowed by a `deny` at any other level is **dead** — emit MINOR with note "Dead allow rule — superseded by deny at <other-scope>."
- Audit-suggested deny baselines (credentials, destructive bash) should be placed in managed settings if available; user-level is the next-best place.

### Special case: subagent precedence

Subagents have a more elaborate chain because the CLI flag `--agent <name>` injects a layer:

```
managed > CLI flag > project > user > plugin
```

The `--agent` flag is per-invocation, so a project subagent definition can be temporarily overridden for one session by a CLI flag. The auditor cannot detect runtime CLI flags; it only audits the on-disk state.

### Special case: skills vs commands

A skill at `.claude/skills/<name>/SKILL.md` and a command at `.claude/commands/<name>.md` share the same name. Per docs:

> Skills win when they share a name with a command.

The auditor emits MINOR when this collision exists: "Skill `<name>` shadows command `<name>`. Command will not be invoked. Consider removing the command file."

## What this means for cross-file check X18

X18 is the catch-all for same-name-multiple-scope problems. Its detection logic:

1. Build a set of all primitive definitions found across all scopes during the project audit.
2. Group by (primitive type, name).
3. For each group with size > 1:
   - If primitive is in the **override** category: emit MINOR for each shadowed (lower-scope) instance with the precedence-aware shadow reason.
   - If primitive is **additive** and the content is identical: emit MINOR ("redundant duplicate").
   - If primitive is **additive** and the content differs: emit INFO ("intentional layering") with a note explaining the additive semantics.

## Diagnostic commands

The user can verify the effective state at runtime:

- `/skills` — shows which skills are active (post-precedence).
- `/agents` — shows which subagents are active.
- `/mcp` — shows connected MCP servers.
- `/permissions` — shows the merged effective permission set.
- `/hooks` — shows all hooks that will fire (from all sources).
- `/memory` — shows CLAUDE.md, CLAUDE.local.md, and rules files currently loaded.

The audit report's "Next actions" section should remind the user to run these commands after applying fixes, since they're the ground truth.
