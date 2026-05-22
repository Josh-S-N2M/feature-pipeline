# Subagent Anti-Patterns

## Contents

- 13 named subagent anti-patterns (SA-1 through SA-13)
- 5 memory-specific anti-patterns (SAM-1 through SAM-5)
- Detection map

## How to read this catalog

Each pattern has ID, severity, symptom, why bad, fix. Severities follow the v2 rubric.

The dangerous-looking patterns shown in `audit-example` blocks are illustrative.

## Subagent definition anti-patterns

### SA-1: Wrong field name (`allowed-tools` instead of `tools`) — BLOCKER

Symptom: subagent file has `allowed-tools:` in frontmatter.

Why bad: `allowed-tools:` is the **skills** field. In a subagent file, it is silently ignored, and the subagent inherits the parent's full tool set — exactly the opposite of what the author wanted.

Fix: rename to `tools:`.

### SA-2: Vague description — MAJOR

Symptom: description like "A helpful assistant that can help with various tasks."

Why bad: Claude has no signal for when to delegate. The subagent will rarely be used.

Fix: lead with the action verb and the input/output. Include trigger language ("Use when ...").

### SA-3: Wildcard Bash — MAJOR

Symptom: `tools: Bash` (no scoping) or `tools: Bash(*)`.

Why bad: subagent has full shell access. Almost never required.

Fix: scope to specific commands — `Bash(git diff *)`, `Bash(npm test *)`, etc.

### SA-4: bypassPermissions with broad tools — BLOCKER (security_critical)

Symptom: `permissionMode: bypassPermissions` combined with `Write`, `Edit`, `Bash`, or `WebFetch` in `tools:`.

Why bad: subagent can perform destructive operations without user approval.

Fix: remove `bypassPermissions`. Use `default` or `plan`.

### SA-5: Over-tooled — MAJOR

Symptom: subagent declares many tools, but body only uses a few.

Why bad: principle of least privilege — extra tools are attack surface.

Fix: remove the unused tools.

### SA-6: Unrecognized model alias — MAJOR

Symptom: `model: gpt-4` or `model: my-fine-tune`.

Why bad: unrecognized values fall back to `inherit` silently. The subagent runs on the parent's model, not the intended one.

Fix: use `sonnet`, `opus`, `haiku`, `inherit`, or a full Claude model ID.

### SA-7: Skills list with SECURITY-BLOCK skill — BLOCKER

Symptom: subagent's `skills:` list includes a skill that the auditor has flagged SECURITY-BLOCK.

Why bad: the dangerous skill loads into the subagent's context on every spawn.

Fix: remove the skill. Cross-file check X9 catches this when both audits run.

### SA-8: Skills list with disable-model-invocation skill — BLOCKER

Symptom: subagent's `skills:` lists a skill with `disable-model-invocation: true`.

Why bad: such skills are silently dropped from subagent preload. The subagent claims to load it but doesn't.

Fix: remove from `skills:` list (or change the skill's `disable-model-invocation`).

### SA-9: Empty body — MAJOR

Symptom: frontmatter exists but body is empty or near-empty.

Why bad: subagent has no system prompt; behavior is undefined.

Fix: add a body that defines the subagent's role and constraints.

### SA-10: Body in description — MINOR

Symptom: description is 1000+ characters, contains numbered steps.

Why bad: description should be ad copy for routing, not the prompt.

Fix: move the prompt content to the body.

### SA-11: Cross-subagent write — BLOCKER

Symptom: subagent body instructs to write to `.claude/agents/*` or modify other subagents.

Why bad: cross-subagent attack vector.

Fix: remove the instruction. If a subagent legitimately manages other subagents, escalate to human review.

### SA-12: Over-broad WebFetch/WebSearch — MAJOR

Symptom: `WebFetch` or `WebSearch` in `tools:` with no body explanation of when/where to fetch.

Why bad: outbound network access risk.

Fix: scope `WebFetch(github.com)` to a specific domain, or remove. Document the use case in the body.

### SA-13: Skills field references non-existent skill — BLOCKER

Symptom: subagent's `skills:` array names a skill (e.g., `deep-reasoning`) but no `SKILL.md` exists at any discoverable location — neither project-scope (`.claude/skills/<name>/SKILL.md`) nor user-scope (`~/.claude/skills/<name>/SKILL.md`).

Why bad: Claude Code's skill-loader silently skips missing references at subagent-spawn time. The subagent's frontmatter advertises a capability it doesn't actually have. Downstream KBs that reference the subagent's `skills:` array (in "Loaded by X via …" prose) propagate the lie. Field-name confusion is also possible — particularly when an author intends to express reasoning depth via `skills: [deep-reasoning, …]`, where the correct fields are `model:` (sonnet/opus/haiku) and/or `effort:` (low/medium/high/xhigh/max).

Fix: pick one — (a) author the missing skill at `.claude/skills/<name>/SKILL.md`, (b) remove the name from the `skills:` array, or (c) correct the spelling if it's a typo for an existing skill. If the original intent was to set reasoning depth rather than to preload domain knowledge, use the `model:` and `effort:` fields instead.

## Subagent memory anti-patterns

### SAM-1: Credential capture — BLOCKER (security_critical)

Symptom: MEMORY.md in `.claude/agent-memory/<name>/` contains credential-shaped strings.

Why bad: subagent persisted a secret to disk.

Fix: remove + rotate. Tell the subagent not to remember credentials.

### SAM-2: Project-scope memory with machine-local content — MAJOR

Symptom: `memory: project` is committed; MEMORY.md contains `/home/...` or `/Users/...` paths.

Why bad: breaks for other contributors.

Fix: prune machine-local paths, or move memory to `local` scope.

### SAM-3: Local-scope memory not gitignored — MAJOR

Symptom: `memory: local` declared but `.gitignore` doesn't cover `.claude/agent-memory-local/`.

Why bad: local memory may leak to commits.

Fix: add `.claude/agent-memory-local/` to `.gitignore`.

### SAM-4: Memory declared but Write/Edit disallowed — BLOCKER

Symptom: `memory: <any>` set AND `disallowedTools:` contains Write or Edit.

Why bad: subagent can never update its memory. The directory will be created and immediately stale.

Fix: remove the conflict (one of the two must give).

### SAM-5: Cross-subagent contamination — MAJOR

Symptom: two subagents with the same name declared in different scopes both using `memory: project`.

Why bad: they share `.claude/agent-memory/<name>/` and accumulate content from both — confused state.

Fix: rename one of them.

## Detection map

| Pattern | Detected by |
|---|---|
| SA-1 | `scripts/validate_subagent_frontmatter.py` (env var AUDIT_TARGET_TYPE=subagent) |
| SA-2, SA-10 | `scripts/analyze_subagent.py` description-quality checks |
| SA-3, SA-5, SA-12 | `scripts/analyze_subagent.py` tools-discipline checks |
| SA-4, SA-11 | `scripts/scan_subagent_body.py` |
| SA-6 | `scripts/validate_subagent_frontmatter.py` model field check |
| SA-7, SA-8 | cross-file check X9 (requires concurrent skill audit) |
| SA-9 | `scripts/analyze_subagent.py` body-size check |
| SA-13 | `scripts/validate_subagent_frontmatter.py` skills-existence check |
| SAM-1 | `scripts/scan_memory_secrets.py` (shared with auditing-context-files) |
| SAM-2 | `scripts/check_subagent_memory.py` |
| SAM-3 | cross-file check X23 |
| SAM-4 | cross-file check X20 |
| SAM-5 | cross-file check X18 (same-name multiple-scope) |
