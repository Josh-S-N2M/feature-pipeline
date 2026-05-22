# Pedagogical-Marker Justification Specification — Mechanism α

**Version:** 1.0.0 (introduced v4.6.0)
**Status:** Canonical (per ADR-0030)
**Owner:** KB-documentation-criteria
**Cross-references:** ADR-0030 (this spec's parent decision), ADR-0031 (canonical implementation location), `../../auditing-cc-configs/references/pedagogical-marker-spec.md` (legacy spec, retained for context; see backward-compat note at end), feature `audit-findings-remediation-r1` PRD (the feature that authored this spec).

## Contents

1. Why mechanism α exists
2. Frontmatter form
3. Fence form
4. Justification validity rules
5. Auditor rejection behavior
6. Reviewer enforcement
7. Extension procedure for the substance-keyword list
8. Examples

---

## 1. Why mechanism α exists

Skills in the auditing-* family — and increasingly skills in adjacent KBs that document patterns the auditor flags (`KB-cc-platform`, `KB-github-actions-platform`, `KB-codespaces-platform`, etc.) — necessarily contain content that triggers the auditor's own scanners. Credential-shaped strings, prompt-injection examples, broken-by-design links, deliberate anti-patterns: all are pedagogical, but indistinguishable from operational content under naive scanning.

A pedagogical marker is a declaration that says "this content is illustrative, not operational; demote findings inside it." Without markers, every reference file becomes a noise generator.

But markers are dangerous. An author who wraps real malicious content (or a real broken link, or a real missing dependency) in a marker silences the scanner. The marker becomes a back-door suppression mechanism. This is the **silent-suppression problem**.

**Mechanism α solves the silent-suppression problem by requiring inline justification on every marker.** A marker without a justification is treated as if absent. The underlying finding surfaces at its original severity. The author who wants to suppress a finding must articulate why — in writing, in line with the marker — and that articulation is itself auditable.

The two failure modes mechanism α is designed to prevent:

| Failure mode | Without markers | With unjustified markers | With mechanism α |
|---|---|---|---|
| False positives on legitimate documentation | High (auditor flags every credential pattern, every example link, every anti-pattern) | Solved | Solved |
| Silent suppression of real findings | N/A | High (any author can wrap any finding) | Solved (marker without justification has no suppression effect) |

The trade-off mechanism α makes: authoring cost goes up (each marker requires a few words of justification), and the auditor gains a new finding class ("marker without justification" / "marker with invalid justification"). The trade-off is judged correct because the cost is bounded (a justification is typically one sentence) and the failure mode it prevents is high-impact (silent suppression of security-grade findings).

## 2. Frontmatter form

The frontmatter declaration is a structured dict. Each entry has a `path` and a `justification`.

```yaml
---
name: <skill-name>
description: <skill-description>
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "Documents credential string patterns the auditor's DE-2 scanner looks for; not real credentials. Reference catalog used for scanner training and auditor tests."
  - path: examples/bad-mcp-config.md
    justification: "Negative-example MCP config illustrating the tool-poisoning attack pattern; demonstrates what the auditor's MCP-X3 scanner detects."
---
```

### What's REJECTED

**Bare-list form** (no per-entry justification slot):

```yaml
pedagogical_sections:
  - references/credential-patterns.md
  - examples/bad-mcp-config.md
```

The auditor parses this form for backward-compat (so it knows a marker was intended), but treats every entry as having an invalid justification — i.e., every entry is rejected, and findings inside those files surface at original severity. Authors converting from the legacy form MUST migrate to structured-dict form per the FR-8 retroactive-upgrade procedure.

**Inline string justification** (single field, not per-entry):

```yaml
pedagogical_sections: ["references/credential-patterns.md", "examples/bad-mcp-config.md"]
justification: "These are examples."  # WRONG — applies to the marker, not per-entry
```

A marker can declare multiple paths; each must carry its own justification. Justifications are content-specific.

## 3. Fence form

Block-level pedagogical content uses a fenced code-block with the `audit-example` language tag and an inline `--` justification annotation.

````
```audit-example -- credential-shaped string is illustrative; documents the pattern DE-2 detects
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

The `--` separator and trailing text are part of the language line. The convention parallels ESLint comments (`// eslint-disable-line some-rule -- because <reason>`) and RuboCop (`# rubocop:disable Style/X -- because <reason>`), so the syntactic form is familiar and machine-parseable.

### Parsing rules

- Language line is split on the first `--` substring.
- Left of `--`: language tag (must be exactly `audit-example`).
- Right of `--`: justification text (subject to validity rules in section 4).
- Leading + trailing whitespace on both halves is stripped.
- The `--` MUST be surrounded by whitespace (` -- `, not `--`). This avoids ambiguity with content that legitimately includes `--` (e.g., shell long options).

### What's REJECTED

````
```audit-example -- specification reference with anti-pattern examples demonstrating credential-shaped string; documents what the auditor scanner detects
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

Bare fence, no `-- justification`. The auditor recognizes it as a marker-attempt (so it knows the author intended pedagogical framing), but treats it as having no justification — finding surfaces at original severity.

````
```audit-example --
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

`--` with empty justification. Rejected.

````
```pedagogical-example
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

Wrong language tag. The `pedagogical-example` form was used historically (notably v4.4.0 in `KB-visual-design/references/anti-slop.md` and `type-color-space.md`) and is NOT a recognized marker form. Authors using this form MUST migrate per the FR-8 retroactive-upgrade procedure.

````
<pedagogical-example>
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
</pedagogical-example>
````

HTML-tag form. Same status as `pedagogical-example` fence: historical, not recognized, must migrate.

## 4. Justification validity rules

A justification is valid if and only if **all three** conditions hold:

### Rule 1 — Length floor

Justification text MUST satisfy:
- Word count ≥ 5 words.
- Character count ≥ 30 characters.

Both floors apply; failing either rejects the justification.

Rationale: a justification under 5 words almost always reduces to one of the banned bare words (rule 2). The 30-character floor catches edge cases (e.g., "ok ok ok ok ok" — 5 words but no substance).

### Rule 2 — Not a banned bare word

A justification consisting solely of any one of the following tokens (or trivial concatenations + punctuation thereof) is REJECTED:

- `pedagogical`
- `example`
- `examples`
- `illustrative`
- `documentation`
- `not real`
- `fake`
- `test`
- `placeholder`
- `demo`
- `sample`

"Trivial concatenation" means a phrase like `"pedagogical example"`, `"illustrative documentation"`, `"a fake placeholder for the test"` — any composition of banned bare words with only whitespace, commas, periods, or articles ("a", "an", "the") between them.

Rationale: these words are TRUE of the marked content but contain no per-content information. Author saying "this is pedagogical" is restating that they marked it; the justification adds nothing.

Implementation: the canonical helper `justification_valid()` normalizes the justification (lowercase, strip non-alphanumeric), then checks if every token is in the banned-bare-word set or in the article set. If so, REJECT.

### Rule 3 — Substance requirement

A valid justification MUST reference at least ONE of:

- **(a) The content type.** Examples: "credential patterns", "vulnerable URL examples", "intentional anti-pattern", "prompt-injection payload", "deliberately broken link", "bad-config example", "exfiltration pattern", "negative example", "anti-laundering catalog", "scanner training fixture".
- **(b) The document's role.** Examples: "reference catalog", "scanner training data", "audit fixture", "anti-pattern demonstration", "negative-example reference", "test corpus", "regression-test fixture".
- **(c) The auditor check it documents.** Examples: "DE-2 scanner looks for this", "X9 cross-file pattern this demonstrates", "what M3 detects", references to specific finding-IDs.

Enforced via **keyword presence** against a controlled substance-keyword list. The list is canonical, maintained in `references/pedagogical-marker-justification-spec-substance-keywords.txt` (sibling file to this spec), and extended via the procedure in section 7.

A justification passing rule 3 ≠ a "good" justification — it's the minimum bar. Authors are encouraged to write specific, content-tied justifications even when shorter forms would pass.

### All three rules apply

A justification that passes rules 1 and 2 but fails rule 3 is REJECTED. A justification that passes rules 1 and 3 but fails rule 2 is REJECTED. Etc.

## 5. Auditor rejection behavior

When the auditor encounters a marker:

1. Parse the marker (frontmatter dict entry OR fence language line).
2. Extract the justification.
3. If absent: REJECT.
4. If present, run `justification_valid()` against the substance-keyword list:
   - Length floor (rule 1).
   - Banned-bare-word check (rule 2).
   - Substance keyword presence (rule 3).
5. If any rule fails: REJECT.

**On REJECT:**

The marker has **no suppression effect**. Findings inside the marked region (frontmatter path entry's file, OR fence's content block) are processed exactly as if the marker were not present. They surface at their original severity (BLOCKER, MAJOR, MINOR) into the audit report.

**Additionally**, the auditor emits a finding of its own:

- **Severity:** MAJOR.
- **Type:** "Marker without justification" OR "Marker with invalid justification".
- **Location:** the file + line of the marker.
- **What:** the marker text + reason for rejection (e.g., "bare-list form lacks per-entry justification", "justification too short (3 words)", "justification = 'pedagogical example' — banned bare-word phrase", "justification lacks substance keywords; consider referencing content type or auditor check ID").

This auditor-emitted finding is what drives authors to fix their markers. Without it, an invalid marker would be silently inert; with it, the audit run surfaces both the underlying finding AND the marker-quality finding, making the gap visible.

**On ACCEPT:**

The marker has its declared suppression effect. Findings inside the marked region are demoted (per pre-existing pedagogical-marker semantics). The auditor emits no marker-quality finding.

## 6. Reviewer enforcement

The auditor is the primary enforcement surface. The reviewer (`shared-document-reviewer.md`) is the secondary surface, invoked during review cycles when a target file may not yet have been scanned by the auditor.

A new `doc_type: PedagogicalMarkerJustification` is added to the reviewer's taxonomy. Its procedure:

1. Read the target file (path provided by invoker).
2. Parse all pedagogical markers (frontmatter dict entries + fence language lines).
3. For each marker, run the same validity rules as the auditor.
4. Emit findings for each invalid marker (same severity + format as auditor's).
5. Return findings to invoker (typically the review cycle's reconciler).

This is intentionally redundant with the auditor. The redundancy serves a specific case: a new document (e.g., a freshly-authored ADR or design doc) may pass through review BEFORE the next auditor run. The reviewer catches marker-quality issues in the review window.

The reviewer's enforcement is identical to the auditor's; mechanism α is the single discipline, not two.

## 7. Extension procedure for the substance-keyword list

The substance-keyword list (section 4, rule 3) is canonical and controlled. Adding a keyword to the list expands the set of justifications that pass rule 3. Removing one tightens the rule.

### Why control the list

If any author can add keywords ad-hoc, the rule degrades: a clever author adds "thing" to the list and then writes justifications containing only "thing", passing the rule but providing no substance. The list must be reviewed.

### Procedure to extend

1. **Open an issue or ADR** describing the proposed keyword + the use case that requires it.
2. **Demonstrate the use case** with at least one concrete file where (a) the marker is justified, (b) the author's natural justification phrasing uses the proposed keyword, (c) no existing keyword on the list captures the phrasing.
3. **Cross-check against banned-bare-word list** (rule 2): the proposed keyword must NOT be on the banned list and must NOT be a trivial restatement of one.
4. **Review-cycle approval**: the change requires at least one reviewer's approval (the role parallels Code Owner approval for a sensitive config file). Self-approval is not permitted.
5. **Update**: append the keyword to `references/pedagogical-marker-justification-spec-substance-keywords.txt`. Reference the issue/ADR in a comment alongside the new entry.
6. **Re-audit**: run the full project audit. Verify the change does not silently pass previously-rejected markers (it shouldn't, since the change only adds; but a deeper change like keyword removal requires this check).

### Procedure to tighten

Removing a keyword or restricting rule semantics requires the same procedure plus a migration plan (because previously-passing markers may newly fail).

### Why this section exists (OBS-3 traceability)

During PRD authoring, OBS-3 surfaced: "The substance-keyword list is the most likely place for the spec to be silently extended by an author trying to make their justification pass. Document the extension procedure to make this a deliberate, reviewed change." This section is the response.

## 8. Examples

### 8.1 Valid frontmatter justification

```yaml
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "Documents credential string patterns DE-2 scanner detects; reference catalog used for scanner training and auditor regression tests."
```

Rules check:
- Length: 17 words / 130 characters → passes rule 1.
- Banned bare words: "documents", "scanner", "reference catalog", etc. are not on the banned list → passes rule 2.
- Substance: "credential string patterns" (content type) + "DE-2 scanner" (auditor check ID) + "reference catalog" (document role) → passes rule 3 with three independent substance hooks.

### 8.2 Valid fence justification

````
```audit-example -- broken-by-design URL demonstrates the X-7 broken-link check; do not repair
https://example.invalid/not-a-real-page
```
````

Rules check:
- Length: 12 words / 75 characters → passes rule 1.
- Banned bare words: "broken-by-design", "URL", "demonstrates", "check" not on banned list → passes rule 2.
- Substance: "broken-by-design" (content type, intentional anti-pattern), "X-7 broken-link check" (auditor check ID) → passes rule 3.

### 8.3 INVALID — too short

```yaml
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "Example only."
```

Rules check:
- Length: 2 words / 13 characters → FAILS rule 1 (under 5 words AND under 30 chars).
- REJECT.

### 8.4 INVALID — banned bare-word phrase

```yaml
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "Pedagogical example illustration."
```

Rules check:
- Length: 3 words / 32 characters → fails rule 1 word floor (3 < 5).
- Even if rephrased to ≥ 5 words ("This is a pedagogical example illustration here"): every content word is a banned bare word → FAILS rule 2.
- REJECT.

### 8.5 INVALID — substance keyword absent

```yaml
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "This file contains some content that you should look at sometimes."
```

Rules check:
- Length: 12 words / 64 characters → passes rule 1.
- Banned bare words: none of the words are on the banned list → passes rule 2.
- Substance: "some content", "look at" — neither references content type, document role, nor auditor check → FAILS rule 3.
- REJECT.

### 8.6 INVALID — bare-list frontmatter

```yaml
pedagogical_sections:
  - references/credential-patterns.md
  - examples/bad-mcp-config.md
```

Parser recognizes the marker-intent (the key `pedagogical_sections:` is present), but no per-entry justification slot exists. REJECT every entry.

### 8.7 INVALID — bare fence

````
```audit-example -- specification reference with anti-pattern examples demonstrating credential-shaped string; documents what the auditor scanner detects
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

No `--` separator on the language line. REJECT. The underlying credential-string finding surfaces at original severity.

### 8.8 VALID — minimum-bar example

```yaml
pedagogical_sections:
  - path: references/anti-patterns.md
    justification: "Negative-example anti-pattern reference; documents what to avoid."
```

Rules check:
- Length: 7 words / 66 characters → passes rule 1.
- Banned: "negative-example", "anti-pattern reference", "what to avoid" — none banned → passes rule 2.
- Substance: "negative-example" (content type/document role hybrid), "anti-pattern reference" (document role) → passes rule 3.

This is the minimum acceptable bar. Authors are encouraged to write fuller justifications — but this one passes.

---

## Backward-compatibility note

The legacy spec at `../../auditing-cc-configs/references/pedagogical-marker-spec.md` predates mechanism α. It introduced the two-marker form (frontmatter + fence) and the anti-laundering rules, both of which mechanism α inherits. **This spec supersedes the legacy one** for the validity-of-justification dimension. The legacy spec is retained for historical context + carries a forward-pointer to this spec at the top of its file. Authors should read this spec; the legacy spec exists for context only.

The auditing-cc-configs scanner module previously called `pedagogical_marker_check.py` (3 separate copies across audit modules per the v4.5.0 baseline) is now consolidated into the canonical implementation at `../../auditing-shared/scripts/pedagogical_marker_check.py` per ADR-0031. Mechanism α is enforced in that canonical module.

## Change log

- **v1.0.0** — Initial release. Authored 2026-05-21 under feature `audit-findings-remediation-r1` (Plan §P1.1). Codifies ADR-0030.
