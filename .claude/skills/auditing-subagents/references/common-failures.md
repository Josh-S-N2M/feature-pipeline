# Common Failures — Subagents

## Contents

- The three memory concepts
- Silent failure: tools vs allowed-tools
- Silent failure: bypassPermissions in managed environment
- Silent failure: skills with disable-model-invocation
- Diagnostic flow

## The three memory concepts

See the coordinator skill's `references/common-failures.md`. Subagents own only #3 (subagent persistent memory).

## Silent failure: tools vs allowed-tools

The single most common subagent bug. Author writes `allowed-tools:` in subagent frontmatter, expecting it to scope the subagent's tools. Result: the field is ignored, subagent inherits parent's tools.

Symptom from user perspective: "My subagent can do things I didn't think I allowed."

Audit: BLOCKER on SA-1 detection.

## Silent failure: bypassPermissions in managed environment

A subagent declares `permissionMode: bypassPermissions`. The managed-settings has `disableBypassPermissionsMode: "disable"`. Result: the subagent's bypass is silently downgraded to default permissions, and the user sees prompts they didn't expect.

Symptom: "Why am I getting prompts when I set bypass?"

Audit: cross-file check X2 flags this as MAJOR (informational — managed wins).

## Silent failure: skills with disable-model-invocation

A subagent lists a skill in its `skills:` field. That skill has `disable-model-invocation: true`. Per Anthropic spec, such skills cannot be preloaded into subagents — the load is silently dropped.

Symptom: "The subagent doesn't seem to have the skill content I preloaded."

Audit: BLOCKER on SA-8 detection.

## Silent failure: memory directory not lazily created

A subagent declares `memory: project`. On first spawn, the runner creates `.claude/agent-memory/<name>/` and an empty MEMORY.md. If the subagent never writes to memory, the directory persists empty. This is INFO-level, not a finding — but if the user expected memory to "just work," it might be confusing.

## Silent failure: name collision shadows definition

A subagent definition with the same `<name>` exists at both project scope and user scope. Project wins; user-scope is dead.

Symptom: "I edited the user-scope file but Claude isn't picking it up."

Audit: cross-file check X18 emits MINOR.

## Silent failure: Wrong project-id for subagent memory

Subagent memory in `.claude/agent-memory/` is keyed by subagent name, not project-id. So a subagent named `foo` in two different projects shares its `.claude/agent-memory/foo/` if both projects use the same `<name>`. This is rare but worth noting.

Actually, no — project memory is per-project (relative path to `.claude/agent-memory/`). User memory at `~/.claude/agent-memory/foo/` IS shared across projects, by design.

Audit: AM-10 (cross-project bleed) is checked for user-scope memory only.

## Diagnostic flow for "subagent not being used"

1. `/agents` — is the subagent listed? If no, frontmatter parse failure.
2. Is its description specific enough? "Helps with code" won't get delegated to.
3. Is the description charge length under 1024 chars? Truncation at 1024 silently drops the trigger keywords.
4. Is the subagent shadowed by a higher-precedence definition with the same name?
5. If the body says "use the Bash tool" but `tools:` doesn't include Bash, the subagent will fail mid-task — not a delegation failure but a mid-execution failure.

## Diagnostic flow for "subagent did something unexpected"

1. `/agents` shows the subagent's effective config. Verify `tools:`, `permissionMode:`, `model:`.
2. Read the subagent body. Does it have exclusion language?
3. Is `permissionMode: bypassPermissions` in effect? (Check managed override via cross-file check X2.)
4. Does the body reference tools the subagent doesn't have? (Frontmatter-body mismatch — flagged as MAJOR.)
