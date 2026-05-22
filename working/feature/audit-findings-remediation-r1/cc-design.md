---
feature_slug: audit-findings-remediation-r1
layer: claude-code
version: 1.0.0
status: complete
generated: 2026-05-21T18:35:00Z
generated_by: claude (acting as design-cc)
derived_from:
  - working/feature/audit-findings-remediation-r1/synthesis.md
  - working/feature/audit-findings-remediation-r1/codebase-analysis-report.md
  - working/feature/audit-findings-remediation-r1/prd-v1.md (v1.2.0)
companion_data: cc-dependencies.json
---

# Claude Code Layer Design — audit-findings-remediation-r1

## Layer scope

This is the **only** layer activated for this feature. All work lives under `.claude/`:

- `.claude/agents/` — 6 agent files for genuine defects + 29 agent files for SA-2 disposition + 2 agent files for FR-7-b enforcement extension
- `.claude/skills/auditing-*/scripts/` — auditor module changes (FR-7-b enforcement; FR-6 Stream 2 X9 recursive check; FR-4 SA-2 regex; FR-5 negation-aware bypass-approval regex; FR-12 deduplication)
- `.claude/skills/KB-*/` — KB content with retroactive marker upgrades (FR-8) + new mechanism-α spec + new categorization protocol
- `.claude/skills/KB-documentation-criteria/references/` — new spec files (mechanism-α; finding-categorization protocol)
- `.claude/skills/auditing-shared/` — NEW skill module for the deduplicated `pedagogical_marker_check.py` (resolves D-7)
- `working/feature/.../x9-verification/` — verification records for FR-6 Stream 1 (per U-4 recommendation)

## Decisions resolved

### D-1 — Mechanism α justification syntactic form: option (α-1) STRUCTURED FRONTMATTER + `--` FENCE

**Frontmatter form:**

```yaml
---
name: <skill-name>
description: ...
pedagogical_sections:
  - path: references/foo.md
    justification: "Documents credential patterns the auditor should look for; not real credentials. Reference catalog for auditing-cc-configs scanners."
  - path: examples/bad-mcp-config.md
    justification: "Negative-example MCP config showing the tool-poisoning attack pattern; demonstrates what the auditor's MCP scanner is detecting."
---
```

**Fence form (block-level marker inside any file):**

````markdown
Here's the pattern the auditor flags:

```audit-example -- credential-shaped string is illustrative; documents the pattern DE-2 detects
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

**Rationale:** Matches T-001's primary recommendation (structured frontmatter + `--` separator); machine-parseable for future tooling; aligns with ESLint/RuboCop convention.

**Backward compatibility:** Per FR-8, none. Existing `pedagogical_sections: [bare-list]` form is upgraded to structured-dict form retroactively.

### D-2 — Mechanism α enforcement location: option (D2-A) AUDITOR PRIMARY + (D2-B) REVIEWER SECONDARY

Primary enforcement in the deduplicated `pedagogical_marker_check.py` (post-FR-12 in `auditing-shared/scripts/`). Secondary enforcement via shared-document-reviewer's new `PedagogicalMarkerJustification` doc_type for review-cycle defense-in-depth.

**Auditor enforcement (primary):** When `pedagogical_marker_check.py` finds a `pedagogical_sections:` entry without a `justification:` key (or a fence block lacking ` -- <text>` after `audit-example`), the marker is rejected — the underlying finding surfaces at original severity. Implementation: parse the structured form; reject any entry missing `justification` OR with `justification` matching the boilerplate-rejection rule (D-3).

**Reviewer enforcement (secondary):** Adding `PedagogicalMarkerJustification` to shared-document-reviewer's doc_type taxonomy. When invoked, the reviewer parses the target's markers and confirms each has a non-boilerplate justification. Runs during normal review cycles; redundant with auditor enforcement but catches the case where someone bypasses the auditor.

**Rationale:** T-001 says all 5 ecosystems put enforcement in the linter (primary). The reviewer addition is cheap (one doc_type entry) and provides redundancy. Defense in depth aligns with intent constraint 3 ("no silent suppression").

### D-3 — Mechanism α minimum justification content: option (D3-Z) COMPOSITE RULE

Justification must satisfy ALL of:

1. **Length floor:** ≥ 5 words AND ≥ 30 characters.
2. **Banned-bare-word rejection:** justification consisting solely of one of {"pedagogical", "example", "illustrative", "documentation", "not real", "fake", "test"} (or trivial concatenations like "pedagogical example") is rejected.
3. **Substance requirement:** justification must reference EITHER (a) the content type being marked (e.g., "credential-shaped strings", "vulnerable URL examples", "intentional anti-pattern", "MCP poisoning examples") OR (b) the document's role (e.g., "anti-laundering catalog", "negative-example reference", "audit-pattern documentation"). The auditor MAY enforce this loosely via keyword presence; strict semantic check is out of scope.

Implementation:

```python
def justification_valid(j: str) -> bool:
    if len(j.split()) < 5 or len(j) < 30:
        return False
    norm = j.lower().strip().strip('"\'')
    BANNED_BARE = {"pedagogical", "example", "illustrative", "documentation",
                   "not real", "fake", "test", "pedagogical example",
                   "documentation example", "test example"}
    if norm in BANNED_BARE:
        return False
    # Substance requirement: keyword presence (loose)
    SUBSTANCE_KEYWORDS = ["credential", "url", "anti-pattern", "negative example",
                          "catalog", "reference", "pattern", "demonstration",
                          "audit", "scanner", "illustrative of", "documents"]
    if not any(kw in norm for kw in SUBSTANCE_KEYWORDS):
        return False
    return True
```

**Rationale:** Matches T-001's "WHY not WHAT" guidance and the project's intent constraint that markers carry deliberate disposition. Boilerplate "pedagogical" with no further content IS silent suppression and is rejected.

### D-4 — FR-4 SA-2 disposition: option (D4-iii) TIGHTEN REGEX + AUDIT DESCRIPTIONS

Primary fix: tighten the SA-2 `TRIGGER_PATTERNS` regex in `auditing-subagents/scripts/analyze_subagent.py` to cover the project's actual description style. Add these alternatives:

```python
TRIGGER_PATTERNS = [
    re.compile(r"\buse\s+(?:when|for|at)\b", re.I),           # existing + "use at"
    re.compile(r"\bwhen\s+\w+ing\b", re.I),                    # existing
    re.compile(r"\bdelegate\b", re.I),                          # existing
    re.compile(r"\bcalled?\s+when\b", re.I),                    # existing
    re.compile(r"\binvoke\s+when\b", re.I),                     # existing
    re.compile(r"\bat\s+the\s+\w+(?:\s+\w+)?\s+stage\b", re.I), # NEW: "at the X stage" / "at the X Y stage"
    re.compile(r"\bduring\s+(?:per-layer\s+|the\s+)?\w+\b", re.I), # NEW: "during per-layer Design" / "during X"
    re.compile(r"\bone\s+invocation\s+per\b", re.I),            # NEW: "one invocation per"
    re.compile(r"\bafter\s+\w+(?:-\w+)*\s+(?:passes|completes)\b", re.I), # NEW: "after X passes" / "after X-Y completes"
]
```

Secondary: audit the 29 flagged descriptions for any that genuinely lack delegation triggers (not just for the regex's purpose, but for the human reader's). Expected count: 0-2 (the regex extension covers ~all 29; rare edge cases get a one-line tweak).

**Negative test required (per AC-FR-4-b):** A test fixture with a description like "Helpful assistant for various tasks" must STILL fire SA-2 — the regex extension must not be so broad that it lets through truly content-free descriptions.

### D-5 — FR-5 bypass-approval disposition: option (regex fix PRIMARY; reword OPTIONAL)

Regex fix in `auditing-subagents/scripts/scan_subagent_body.py:38`. Replace:

```python
re.compile(r"\b(ignore|bypass|skip|override)\b.{0,30}(approval|prompt|permission|safety|check)\b", re.I),
```

With:

```python
re.compile(
    r"(?<!\bdo\snot\s)(?<!\bdo\snot\s\s)(?<!\bmust\snot\s)(?<!\bnever\s)"  # negation-aware lookbehind
    r"\b(ignore|bypass|skip|override)\b.{0,30}(approval|prompt|permission|safety|check)\b",
    re.I
),
```

Python regex lookbehinds must be fixed-width — the multi-line form above is illustrative. Implementation: two-pass. First find candidate matches; for each, examine the 30 characters preceding the match-start for one of the negation phrases ("do not", "do NOT", "must not", "must NOT", "never", "MUST NOT"). If present, skip the finding.

**Negative test (per AC-FR-5-d):** Fixture body containing "You do NOT skip the permission policy" — produces ZERO bypass-approval findings. Fixture body containing "skip the permission policy" — produces the BLOCKER. Both required.

No agent rewording. The negative-instruction phrasings are correct guardrails; "fixing" them by softening the language would teach the wrong discipline.

### D-6 — FR-6 Stream 2 X9 reformulation: option (D6-A) WIRE THE RECURSIVE CALL

Replace `check_X9_subagent_skills_security_block` in `cross_file_checks.py:622` with an implementation that:

1. For each subagent file with a `skills:` list (current behavior — unchanged)
2. For each preloaded skill: invoke `audit_skill.py <skill-path>` via subprocess (using the existing dispatcher pattern from `audit_project.py:51`)
3. Parse the audit result JSON; check verdict
4. Emit findings:
   - If audit produces `SECURITY-BLOCK` verdict → emit BLOCKER (with details about which skill failed and which check)
   - If audit produces `MAJOR` findings → emit MAJOR (referencing the failed skill)
   - If audit passes clean → emit no X9 finding (this is the "skill verified" silent-success case)
5. Cache result per (subagent, skill) pair within a single audit run to avoid duplicate subprocess invocations.

**Stream 1 separate deliverable:** Per AC-FR-6-b, each (subagent, skill) pair needs a one-time verification record. These records live at `working/feature/audit-findings-remediation-r1/x9-verification/<subagent-name>-<skill-name>.md` per U-4 (a). Content: skill name, audit-pass timestamp, verdict, brief notes if any MAJOR/MINOR findings were dispositioned manually.

**Improvement, not suppression** (per intent constraint 3 and AC-FR-6-c): The post-Stream-2 audit produces fewer X9 findings (0-3 vs current 29) AND each remaining finding carries actionable detail (which skill failed, which check). Strictly higher signal.

### D-7 — FR-12 deduplication architecture: option (D7-A) NEW `auditing-shared` SKILL MODULE

Create `.claude/skills/auditing-shared/`:

```
.claude/skills/auditing-shared/
  SKILL.md                                    # describes the module's role
  scripts/
    pedagogical_marker_check.py              # canonical implementation (post-FR-12)
    scan_memory_secrets.py                   # canonical (per AC-FR-12-e scan)
```

The canonical `pedagogical_marker_check.py` is the union of the three current copies:
- Base: `auditing-cc-configs/scripts/pedagogical_marker_check.py` (most-trafficked; called by triage_with_judge)
- Plus: the `f.get("location") or f.get("where")` defensive backward-compat from `auditing-skills` copy (per AC-FR-12-d, MUST be preserved)
- Plus: the new mechanism-α justification check (per AC-FR-7-b)

The three former call sites import the canonical:

```python
# auditing-cc-configs/scripts/triage_with_judge.py — was: from pedagogical_marker_check import ...
from auditing_shared.scripts.pedagogical_marker_check import apply_marker_triage

# auditing-skills/scripts/audit_skill.py — was: from pedagogical_marker_check import ...
from auditing_shared.scripts.pedagogical_marker_check import apply_marker_triage

# auditing-subagents/scripts/audit_subagent.py — was: from pedagogical_marker_check import ...
from auditing_shared.scripts.pedagogical_marker_check import apply_marker_triage
```

Python import-path note: `auditing_shared` would need to be importable. Since `.claude/skills/auditing-*/scripts/` isn't on the default Python path, the import works either via (a) PYTHONPATH manipulation in each caller, or (b) the scripts being invoked via subprocess (current dispatcher pattern) with the path resolved at invocation. Per F-004, the current pattern uses subprocess; the canonical script just needs to be findable via filesystem path. Implementation: each former-copy file becomes a 3-line shim that imports + re-exports from the canonical, OR each call site explicitly path-resolves the canonical (cleaner). Per-implementation detail; Plan stage picks.

**AC-FR-12-e scan:** Also deduplicate `scan_memory_secrets.py` (identical across `auditing-context-files/` and `auditing-subagents/`). Same pattern: canonical lives in `auditing-shared/scripts/`; the two former copies become shims OR their callers update imports.

### D-8 — Categorization-protocol document (FR-9): SHAPE

Document path: `.claude/skills/KB-documentation-criteria/references/disciplines/finding-categorization.md` (per AC-FR-9-a + Q-CC-4 recommendation).

Shape (one-page protocol):

```markdown
# Finding-Categorization Protocol

Disposition decision tree for cc-audit findings.

## Step 1 — Is this a real defect?

Read the finding. Read the cited file/line. Ask:
- Does the cited content actually do what the finding claims (e.g., does it actually pipe downloaded content to a shell, or is it an example of that pattern)?
- Is the cited path/reference resolvable to an actual file the reader can access (e.g., does the broken link target really exist somewhere or is it an illustrative path)?

If YES → real defect. Proceed to Step 3 (real-fix disposition).
If NO → false positive. Proceed to Step 2.

## Step 2 — Markerable or auditor-defect?

For a false positive, ask:
- Is the auditor's check sound, and only the SPECIFIC content matched is pedagogical? → Markerable (mechanism α, see pedagogical-marker-spec).
- Is the auditor's check itself flawed (e.g., regex matches negation, regex too narrow, scan doesn't account for project conventions)? → Auditor defect (improve, don't suppress, per intent constraint of audit-findings-remediation-r1).

If markerable → Step 4 (marker disposition).
If auditor-defect → Step 5 (auditor improvement disposition).

## Step 3 — Real-fix disposition

Categories: C (genuinely stale links), E wildcard-shell subset (declared tool too broad).
Action: repair the link / scope the tool / reword the body. Marker disposition is NEVER permitted.

## Step 4 — Marker disposition (mechanism α)

Action: add `pedagogical_sections:` entry (frontmatter) or `audit-example` fence wrap, WITH inline justification per mechanism α (see pedagogical-marker-justification-spec.md).

Justifications must satisfy:
- ≥ 5 words AND ≥ 30 characters
- Not solely a banned bare-word
- Reference either content type OR document role

## Step 5 — Auditor-improvement disposition

Categories: E bypass-approval subset (auditor false positive on negative instructions), F (X9 stub).
Action: improve the auditor (tighten regex; wire the real check; reformulate the finding output).
Surface as a scope-deviation per ADR-0029 if the improvement adds significant work not in current PRD scope.

## Calibration anchors (this feature's 6 categories)

| Cat | Example | Disposition chosen |
|---|---|---|
| A | `curl ... | sh` in KB-cc-platform/references/extensions.md (illustrating extension installation) | Marker (α) |
| B | `[plugin manifest](.claude/plugins/X.md)` link target doesn't exist locally | Marker (α) OR rewrite to backticked plain text |
| C | `[ADR](output/auth-research.md)` in synthesize/references/examples.md — `output/` files don't exist anywhere | Real fix: delete/repair |
| D | "Authors the Frontend Design subsection..." doesn't match SA-2 regex | Auditor improvement (regex tighten) |
| E (wildcard) | `tools: [Bash, ...]` unscoped | Real fix: `Bash(git diff:*)` |
| E (bypass) | "You do NOT skip the permission policy" — auditor reads as bypass instruction | Auditor improvement (regex negation-aware) |
| F | X9 informational | Auditor improvement (wire recursive check) + Stream 1 verification |

## Escalation criteria

- New finding type not covered by Cat A-F → escalate per ADR-0029 (surface, don't silently dispose)
- Disposition would shift PRD scope (e.g., 5+ findings → real fix instead of expected marker) → escalate
- Justification quality borderline → escalate; the user calibrates the rubric

Per ADR-0029, finding categorization itself is a stage decision that may surface deviations. Surface, don't absorb.
```

### Cross-cutting decisions

**Spec locations:**
- Mechanism-α spec at `.claude/skills/KB-documentation-criteria/references/pedagogical-marker-justification-spec.md` (per AC-FR-7-a; Q-CC-1 recommendation)
- Forward-pointer added to existing `auditing-cc-configs/references/pedagogical-marker-spec.md` (per Q-CC-1)
- Categorization-protocol at `.claude/skills/KB-documentation-criteria/references/disciplines/finding-categorization.md` (per Q-CC-4)

**Verification records location (U-4 resolution):** option (U4-a): `working/feature/audit-findings-remediation-r1/x9-verification/<subagent>-<skill>.md`. Out-of-scope: a permanent `audits/` directory.

## Architectural questions for design-composer (Q-CC-N)

- **Q-CC-1** (recommended above): New mechanism-α spec lives at `KB-documentation-criteria/references/pedagogical-marker-justification-spec.md`; forward-pointer added to existing `auditing-cc-configs/references/pedagogical-marker-spec.md`. Design-composer confirms or arbitrates.
- **Q-CC-2** (recommended above): D-2 option (D2-A) primary + (D2-B) secondary. Design-composer confirms.
- **Q-CC-3** (recommended above): D-7 option (D7-A) — new `auditing-shared` skill module. Design-composer confirms; if alternative is preferred (D7-B import shims), this design must be revised.
- **Q-CC-4** (recommended above): Categorization-protocol lives in `disciplines/` per the project's pattern. Design-composer confirms.
- **Q-CC-5** (new): The new `auditing-shared` skill module needs a `SKILL.md` describing its role. Does design-composer want the SKILL.md authored as part of this feature, or deferred to a follow-on? Recommendation: author it here (small; in scope for FR-12).
- **Q-CC-6** (new): D-3's substance-requirement keyword list is per-author judgment. Should design-composer add a process for extending the keyword list when a future legitimate marker uses a new content type? Recommendation: simple — keyword list lives in the spec; PRs to extend it are reviewed like any KB change.

## Implementation surface summary

| File / directory | Action | FR coverage |
|---|---|---|
| `.claude/skills/auditing-shared/` | NEW module | FR-12 |
| `.claude/skills/auditing-shared/SKILL.md` | NEW | FR-12 |
| `.claude/skills/auditing-shared/scripts/pedagogical_marker_check.py` | NEW canonical | FR-7-b, FR-12 |
| `.claude/skills/auditing-shared/scripts/scan_memory_secrets.py` | NEW canonical (per AC-FR-12-e) | FR-12 |
| `.claude/skills/auditing-cc-configs/scripts/pedagogical_marker_check.py` | DELETE or shim | FR-12 |
| `.claude/skills/auditing-skills/scripts/pedagogical_marker_check.py` | DELETE or shim | FR-12 |
| `.claude/skills/auditing-subagents/scripts/pedagogical_marker_check.py` | DELETE or shim | FR-12 |
| `.claude/skills/auditing-context-files/scripts/scan_memory_secrets.py` | DELETE or shim | FR-12-e |
| `.claude/skills/auditing-subagents/scripts/scan_memory_secrets.py` | DELETE or shim | FR-12-e |
| `.claude/skills/auditing-subagents/scripts/analyze_subagent.py` | EDIT — tighten SA-2 TRIGGER_PATTERNS | FR-4 |
| `.claude/skills/auditing-subagents/scripts/scan_subagent_body.py` | EDIT — negation-aware bypass-approval regex | FR-5 |
| `.claude/skills/auditing-cc-configs/scripts/cross_file_checks.py` | EDIT — replace X9 stub with recursive check | FR-6 Stream 2 |
| `.claude/skills/KB-documentation-criteria/references/pedagogical-marker-justification-spec.md` | NEW | FR-7-a |
| `.claude/skills/KB-documentation-criteria/references/disciplines/finding-categorization.md` | NEW | FR-9 |
| `.claude/skills/auditing-cc-configs/references/pedagogical-marker-spec.md` | EDIT — add forward-pointer | FR-7-a |
| `.claude/agents/shared-document-reviewer.md` | EDIT — add PedagogicalMarkerJustification doc_type | FR-7-b secondary |
| 9 KB SKILL.md files | EDIT — upgrade `pedagogical_sections:` from bare-list to structured form | FR-8 |
| 10+ KB reference files | EDIT — add `-- justification` to existing audit-example fences | FR-8 |
| `KB-visual-design/references/anti-slop.md` + type-color-space.md | EDIT — convert `<pedagogical-example>` HTML form to canonical fence form + justification | FR-8 |
| 32 affected KB files (Cat A+B markers) | EDIT — add new structured markers with justifications | FR-1, FR-2 |
| 18 affected files (Cat C real fixes) | EDIT — repair/delete stale refs | FR-3 |
| 3 agent files (discovery-codebase-researcher.md, review-architecture-auditor.md, shared-document-reviewer.md) | EDIT — scope Bash tool | FR-5-c |
| Up to 2 of 29 agent files (D-4 secondary audit) | EDIT — minor description tweaks if any genuinely lack triggering language | FR-4 |
| `working/feature/.../x9-verification/<agent>-<skill>.md` (×N) | NEW — Stream 1 verification records | FR-6 Stream 1 |

## Risks identified during per-layer Design

| Risk | Mitigation |
|---|---|
| Python lookbehind for D-5 negation-aware regex is fragile (lookbehinds must be fixed-width) | Implementation uses two-pass (find candidate then check preceding 30 chars), not a single regex. Tested via the negative-test fixture. |
| Import-path semantics for D-7 shims may break in subprocess invocations | Alternative is filesystem-path-resolved canonical (each call site path-imports). Plan stage picks based on implementation friction. |
| D-3 substance-keyword list is incomplete and rejects a legitimate new marker type later | Q-CC-6 flags this; spec includes a documented process for extending the keyword list. |
| AC-FR-12-e scan finds MORE duplications than `scan_memory_secrets.py` | Surface per ADR-0029; Plan absorbs into FR-12 or defers based on count. |
| D-4 regex extension is too broad and lets through truly content-free descriptions | Acceptance Tests must include negative cases (filler descriptions); D-4 secondary audit (manual check of 29) is the safety net. |

## Per-layer Design completion checklist

- [x] All 8 synthesis decisions resolved (D-1 through D-8) with rationale
- [x] 6 Q-CC-N items recorded for design-composer
- [x] Implementation surface enumerated (file-by-file)
- [x] No ADRs authored (per FR-5 — design-composer's exclusive responsibility)
- [x] No scope deviations introduced beyond those resolved upstream
- [x] Risks identified for downstream stages (Plan, Acceptance Tests, Cross-Artifact Audit)
- [x] Companion `cc-dependencies.json` describes inter-file dependencies for Plan stage's task ordering
