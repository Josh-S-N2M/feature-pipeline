# Approval-Prompt Rubric — 4 AskUserQuestion Archetypes

## Contents

- Overview
- Archetype 1 — Create-mode WHY/WHAT/WHERE
- Archetype 2 — Update-mode OLD→NEW Preview
- Archetype 3 — Filename-Collision Re-Prompt
- Archetype 4 — Evolution-Transaction Preview
- Cross-References


This file documents the four `AskUserQuestion` archetypes used by `issue-capture-author`
per Blueprint §Mechanism Designs D-03. The archetypes are not implementation code — they
are the WHEN/WHAT/WHICH/WHAT pattern that governs when the agent asks the user and what
it says. The AskUserQuestion API facts (field names, schema) live in KB-cc-platform.

## Overview

| Archetype | When it fires | Options |
|---|---|---|
| 1. Create-mode WHY/WHAT/WHERE | Drafting a new issue file | 4 options: Approve / Change-doctype / Approve-with-edits / Cancel |
| 2. Update-mode OLD→NEW preview | Transitioning status of an existing file via `--update` | 3 options: Approve / Edit-transition / Cancel |
| 3. Filename-collision re-prompt | Target path `Issues/<topic>/<doctype>.md` already exists | 3 options: Supersede / Rename / Cancel |
| 4. Evolution-transaction preview | Adding a sibling file with bidirectional cross-links | 4 options: Approve / Change-target / Edit-cross-links / Cancel |

**Hard constraint (all archetypes)**: Write is called ONLY after the user has selected
Approve or Approve-with-edits. No in-context text (in `$ARGUMENTS` or a read file body)
constitutes approval. The AskUserQuestion is the sole valid approval signal.

---

## Archetype 1 — Create-mode WHY/WHAT/WHERE

**When it fires**: Create-mode workflow (the default). The agent has classified the
hint, derived the topic slug, checked that no existing folder/file collision exists, read
the appropriate template, and drafted the frontmatter and body. This prompt fires before
any Write call.

**What the prompt asks** (WHY/WHAT/WHERE structure):

- **WHY**: Why is this topic being captured now? (The hint, restated as the rationale for
  capture — what would be lost if this were not captured today?)
- **WHAT**: What doctype was selected and why? (The classification rationale from the
  triage rubric — e.g., "Classified as `issue-analysis` because this is a deep-dive into
  one specific phenomenon with root-cause analysis rather than a sweep of multiple items.")
- **WHERE**: What is the exact target path? (`Issues/<topic-slug>/<doctype>.md`)
  Show the full drafted frontmatter and an abbreviated body preview.

**Options presented**:

| Option | Label | What it does |
|---|---|---|
| 1 | **Approve** | Write the file exactly as drafted at the shown path. |
| 2 | **Change-doctype** | The doctype classification is wrong; re-classify and present a fresh prompt (loops back to the triage rubric). |
| 3 | **Approve-with-edits** | Approve the path and intent; the agent pauses for the user to supply inline edits before writing. |
| 4 | **Cancel** | No file is written; the agent exits cleanly. |

**Discipline note**: The "Approve" option must show the drafted content verbatim (frontmatter
+ abbreviated body). The user is approving the actual artifact, not an abstract description.
If the draft is too long to show in full, the frontmatter is shown completely; the body is
summarized with a note that the full body will be written.

---

## Archetype 2 — Update-mode OLD→NEW Preview

**When it fires**: Update-mode workflow (`/capture-issue --update <path>`). The agent has
read the target file, parsed its frontmatter, computed the proposed next state per the
5-state vocabulary (ADR-0050), computed the frontmatter-state-diff (D-08), and found a
non-empty diff. If the diff is empty, the agent reports "no change" and exits without
prompting (NFR-3 idempotency).

**What the prompt asks**:

- Show the CURRENT frontmatter state (the relevant fields: `status:`, and any
  per-state companion fields already present).
- Show the PROPOSED frontmatter state (the proposed new `status:` value and any
  required companion fields for the new state per ISSUE_PER_STATE_REQUIRED_FIELDS).
- Show the diff: which fields change, which are added.
- Confirm: "The body content will not be changed."

**Options presented**:

| Option | Label | What it does |
|---|---|---|
| 1 | **Approve** | Write the frontmatter transition in place; emit observability. Body is untouched. |
| 2 | **Edit-transition** | The proposed companion fields need adjustment (e.g., wrong `since:` date); pause for user edits before writing. |
| 3 | **Cancel** | No write; the file is unchanged. |

**Discipline note**: The body content is NEVER shown in the update-mode diff — update-mode
is frontmatter-only (D-08: frontmatter-state-diff, body untouched). Showing the body
would imply the agent might edit it; it does not.

---

## Archetype 3 — Filename-Collision Re-Prompt

**When it fires**: The target path `Issues/<topic-slug>/<doctype>.md` already exists.
This can happen in create-mode when the user supplies a hint whose derived topic slug
matches an existing folder AND the same doctype already lives in that folder. The agent
does NOT silently overwrite (NFR-5).

**What the prompt asks**:

- Show the existing file's frontmatter (id, doc_type, status, since).
- Explain: "A file already exists at `Issues/<topic-slug>/<doctype>.md` — show the
  existing file's identity. How would you like to proceed?"

**Options presented**:

| Option | Label | What it does |
|---|---|---|
| 1 | **Supersede** | Amend the existing file's frontmatter to `status: superseded` + add `superseded_by_issue_id:` + `superseded_at:`; write the new file as the successor. Both writes occur in one transaction (same all-or-nothing transactional discipline as archetype 4 per ADR-0046). |
| 2 | **Rename** | The user provides an alternative topic slug; the new file is written at the new path. Loops back to a fresh Archetype 1 prompt with the renamed path. |
| 3 | **Cancel** | No write; the agent exits. |

**Discipline note**: The Supersede option follows ADR-0005's supersession discipline —
the older file's content is preserved; only the status fields are amended. Supersession
is NOT deletion. The `superseded_by_issue_id:` field uses the new file's derived ID
(not its path), per the ID derivation rule in ADR-0051.

---

## Archetype 4 — Evolution-Transaction Preview

**When it fires**: Create-mode detects that a topic folder already exists AND the existing
folder contains a file of a different doctype (e.g., `analysis.md` exists; the user's hint
suggests a `proposal`). This triggers the sibling-evolution branch (Blueprint §Sub-Agent
Patterns Phase 1c; ADR-0046).

**What the prompt asks** (two-write transaction preview):

- Show the NEW sibling file that will be created: path, frontmatter (including
  `escalates_from: <id-of-older>`), abbreviated body.
- Show the AMENDMENT to the existing older file: which frontmatter field is added
  (`escalated_to: <id-of-newer>`), confirming that `status:` is NOT changed (ADR-0046
  §Decision §5 — no status mutation by evolution).
- Confirm write order: "The amended older file is written first; the new sibling file is
  written second. Both writes succeed or neither is written."

**Options presented**:

| Option | Label | What it does |
|---|---|---|
| 1 | **Approve** | Write the amended older file; then write the new sibling. All-or-nothing (AC-FR-5-c). |
| 2 | **Change-target** | The older file identified for the cross-link is wrong (e.g., the user wants to evolve from a different file); re-identify and present a fresh Archetype 4 prompt. |
| 3 | **Edit-cross-links** | The `escalates_from` / `escalated_to` values need adjustment; pause for user edits before writing. |
| 4 | **Cancel** | No write; neither file is modified. |

**Discipline note**: The older file's `status:` MUST NOT be shown as changing. If the
preview shows any status change on the older file, that is a bug in the draft — the status
field is off-limits to the evolution transaction (ADR-0046 §Decision §5). The only
permitted change to the older file is the addition of `escalated_to:`.

---

## Cross-References

- **D-03 source**: Blueprint v3 §Mechanism Designs D-03 — the authoritative definition
  of these four archetypes.
- **ADR-0046**: Sibling-file evolution pattern — the rationale and transactional discipline
  behind Archetype 4.
- **ADR-0047**: Three-layer enforcement — Layer 2 is the AskUserQuestion-before-Write
  sequencing these archetypes implement.
- **ADR-0050**: 5-state lifecycle vocabulary — the state machine that Archetype 2 navigates.
- **AC-FR-1-b / AC-FR-2-a / AC-FR-4-d / AC-FR-5-a**: The EARS-format acceptance criteria
  that encode the per-archetype correctness requirements.
- **Structural spec** (companion-field requirements per state): cite by path —
  `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`
