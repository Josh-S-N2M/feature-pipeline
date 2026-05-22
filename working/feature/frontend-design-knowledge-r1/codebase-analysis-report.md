---
id: CA-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
companion_json: codebase-analysis.json
generated: 2026-05-20T23:05:00Z
generated_by: discovery-codebase-researcher
---

# Codebase Analysis: Frontend Design Knowledge Enhancement — Round 1

## Contents

- [x] Scope and method
- [x] Focus areas (6)
- [x] Convention findings
- [x] Blast-radius assessment
- [x] Layer scope verification
- [x] Notable findings for downstream stages

## Scope and method

This codebase analysis is for an unusual feature: the codebase under analysis IS the project itself (`.claude/skills/`, `.claude/agents/`). The research targets the existing frontend-design KB, the three existing platform KBs (which set the voice/depth/structure bar), the pedagogical-marker-spec, and the sub-agent frontmatter that preloads `KB-frontend-design`.

Extraction method: direct filesystem grep + read (no GitNexus needed for a self-contained `.claude/` analysis).

## Focus areas

**FA-001 — Existing `KB-frontend-design` content shape.** 3 files, 500 total lines, 0.8 code blocks per 100 lines (the lowest density of any KB in the project). 8 principles all backend-of-the-frontend (state, perf, errors, typing, framework grain) + accessibility-as-baseline. SKILL.md docstring explicitly says "no platform partner KB (frontend platforms vary widely)" — Option B-style or paired-pattern restructure must justify reversing this.

**FA-002 — Platform-KB pattern reference.** Three existing platforms (cc, github-actions, codespaces). Each is SKILL.md + 8-20 reference files organized topically. Code-block density 2.2-4.1 per 100 lines. Voice is consistently senior-engineer-handbook: declarative, opinionated, no padding, no tutorial framing. This is the bar `KB-cc-platform`'s `references/extensions.md` (548 lines) and `references/configuration.md` (260 lines) set.

**FA-003 — Pedagogical-marker-spec format.** The prior-session fix held — zero KBs carry `disable-model-invocation: true` in actual frontmatter. The 3 grep hits in KB-cc-design / KB-cc-platform / KB-github-actions-platform are all pedagogical body content describing when to USE the field (in KB-cc-design's `principles.md` it shows up in a YAML example block; in KB-cc-platform's `extensions.md` it's in a comparison table). This establishes the precedent FR-5 builds on: new anti-slop content can mention "AI slop" patterns by name with pedagogical markers, and the audit's Step 4 verification correctly disposes of them.

**FA-004 — Sub-agents preloading `KB-frontend-design`.** Exactly 2: `design-frontend.md` and `design-composer.md`. Their `skills:` lists are the FR-4 edit targets. Blast-radius bounded — no other agent file, no other KB SKILL.md prose, no orchestrator code references `KB-frontend-design` as a preload dependency. The grep matches in `KB-api-design`, `KB-documentation-criteria`, and `KB-frontend-design` itself are cross-references (e.g., `KB-api-design`'s "Pairs with `KB-frontend-design` (the consumer)"), not preload dependencies.

**FA-005 — KB structural and frontmatter conventions.** Codified in `KB-cc-design/references/patterns-and-anti-patterns.md` (the canonical KB-authoring discipline) and verified across all 17 existing KBs. SKILL.md frontmatter shape: `name` (kebab-case, `KB-` prefix per ADR-0019), `description` (multiline YAML), `allowed-tools` (Read/Grep/Glob baseline; platform KBs add Edit/Write/WebFetch). references/ directory holds H2-organized deep content. Every SKILL.md and every reference file leads with `## Contents`. Design KBs document a `## When this KB is loaded` subsection. Mature, well-policed by the existing `auditing-skills` checks.

**FA-006 — Anthropic's official `frontend-design` skill (external authoritative reference).** Surfaced during T-001 external research but worth recording here as a codebase observation: `/mnt/skills/public/frontend-design/SKILL.md` is Anthropic's canonical anti-slop discipline. It is NOT part of this project's `.claude/skills/` (it's a read-only Anthropic-managed skill mounted at session start). The new `KB-anti-slop-design` (or wherever per-layer Design places anti-slop) cites this as a primary source rather than re-deriving the content.

## Convention findings

For new KB authoring, the following conventions are settled and need not be re-decided at the per-layer Design stage:

1. **Frontmatter shape** — `name`, `description`, `allowed-tools` required; `disable-model-invocation` and `user-invocable` are tools for skill discoverability, not preload control. Knowledge-only KBs preloaded by sub-agents do NOT carry `disable-model-invocation: true`.
2. **Directory layout** — `KB-<name>/SKILL.md` + `KB-<name>/references/<topic>.md`. References are flat (no nested subdirectories under references/).
3. **`## Contents` checklist convention** — every SKILL.md and every reference file leads with `## Contents` enumerating the H2 sections (Gate 0 structural anchor).
4. **`## When this KB is loaded` subsection** — design KBs document which sub-agents preload them. Platform KBs may include this too.
5. **Code-block density convention** — design KBs cap at ~1 block per 100 lines (KB-frontend-design's 0.8 is the floor; other design KBs run 2.0-3.3). Platform KBs run 2.2-4.1. New design-side KBs should sit close to the existing KB-frontend-design density (per AC-FR-2-a/b authoring discipline).
6. **Voice and style** — declarative, opinionated, no tutorial framing. Tables for trade-offs, prose for discipline statements, code only where syntax IS the knowledge.

## Blast-radius assessment

Per the `potential_blast_radius_hints` in the JSON sibling:

- `design-frontend.md` `skills:` edit (FR-4-a): **low risk**. The frontmatter is the single point of preload control; no other agent references this list's specific contents.
- `design-composer.md` `skills:` edit (FR-4-b): **low risk**, same rationale.
- `KB-frontend-design/` content restructure (Option B): **medium risk**. Two agents preload from it; if the structural restructure splits content into sibling KBs, those agents' `skills:` lists must be updated atomically with the split. The plan-author and per-layer Design stage must order these tasks correctly.
- New `KB-storybook-platform/`: **low risk**. Greenfield; no existing references to update beyond adding it to the preload lists of agents that need Storybook knowledge.

## Layer scope verification

- **Claude Code / Project Filesystem** — in scope. All edits are `.claude/skills/*` and `.claude/agents/*`.
- All 8 other layers — out of scope. No file in `src/`, `tests/`, `.github/workflows/`, `infrastructure/`, etc. is touched. No application UI, no Backend service, no API contract change.

The PRD's Layer Scope declaration (Claude Code / Project Filesystem only) is consistent with the codebase reality.

## Notable findings for downstream stages

For **Synthesis** (consolidating Discovery outputs):

1. The existing `KB-frontend-design` is intentionally restrained on code (0.8 blocks per 100 lines). New content adopting prose-first discipline per FR-2 has a clear precedent and is a continuation, not a departure.
2. Anthropic's `frontend-design` skill (`/mnt/skills/public/frontend-design/SKILL.md`) is the most authoritative possible source for T-001. It explicitly names AI-slop signatures (Inter, Roboto, system fonts; purple-on-white gradients; predictable layouts; cookie-cutter design; convergence on common choices including Space Grotesk). The new anti-slop content can cite and extend this rather than re-derive.
3. The platform-KB pattern is mature and unambiguous; `KB-storybook-platform` slots in cleanly. The substantive question is depth (how many reference files; how much surface area to cover), not shape.

For **per-layer Design** (`design-claude-code` decides Option A vs B):

1. The existing `KB-frontend-design` docstring's explicit rejection of a paired-platform partner is a constraint the Designer must address head-on — either preserve it (Option A keeps `KB-frontend-design` as the single discipline KB; new content absorbed in) or revise it (Option B splits content into 4-5 sibling design KBs; the docstring's rejection becomes obsolete by virtue of the split itself).
2. Anti-slop placement is the orthogonal question: with the Anthropic `frontend-design` skill as the upstream reference, a sibling `KB-anti-slop-design` may be overkill if anti-slop content amounts to "see the Anthropic skill + project-specific calibration." A `references/anti-slop.md` inside whichever design KB owns the discipline thread may serve.
3. The platform-KB pattern's `## When this KB is loaded` discipline gives a clean structural template for `KB-storybook-platform`. Storybook is preloaded only when a Frontend-touching feature includes Storybook stories — not all Frontend-touching features.

For **Plan Authoring**:

1. The FR-4 edits are mechanical and bounded (2 agent files; each gets 1-N entries added to `skills:`). No ordering pitfalls.
2. The pedagogical-marker application (FR-5) is well-established; the spec at `pedagogical-marker-spec.md` carries through.
3. The `cc-audit` invocation at the end of execution (FR-5-b / NFR-2-a) follows the existing pattern; no new audit machinery needed.
