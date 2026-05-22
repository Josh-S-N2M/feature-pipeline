# Research plan — round 3 (revised after document-reviewer template review)

**Run-id:** feature-pipeline-design-r3-20260512
**Started:** 2026-05-12
**Cutoff:** 2026-02-12 → 2026-05-12 (90 days)
**Backends:** Context7, Exa, web_search/web_fetch as fallback

## Revision rationale

After reviewing the uploaded `document-reviewer` template, the original C4 (bundled-file skills) and C5 (large knowledge skill compaction) topics become moot — the existing `documentation-criteria` skill already holds templates in a working pattern. The reviewer template also surfaces two integration points (`code_verification` and `codebase_analysis` JSON inputs) that warrant their own research.

Net: drop 2 topics, add 2 topics, keep 6. Total still 8.

## Topic register

| ID | Topic | Backends | Rationale |
|---|---|---|---|
| C1 | EARS format — origins, adoption, AC quality measurement | Exa + academic | Q-v4-4: strict EARS for ACs; ground acceptance-testing-knowledge. |
| C2 | Multi-author document synthesis patterns in agentic systems — fan-out-fan-in for structured docs | Exa | Q-v4-3 inverted: per-layer fan-out into composer fan-in. Document parallel-agent authoring patterns. |
| C3 | Cross-layer dependency resolution in distributed design authoring — parallel reconciliation | Exa | Q-v4-10: assumption-based with composer reconciliation. Validate against parallel-architect coordination. |
| C6 | PRD authoring by AI agents — failure modes and structural patterns | Exa | Q-v4-1: synth-prd-author. Ground prd-authoring-knowledge with AI-PRD failure modes. |
| C7 | Document-driven vs JSON-driven stage handoff — tradeoffs | Exa | Pipeline moves toward documents at Intent Clarification, PRD, Blueprint. Surface tradeoffs. |
| C8 | Template-driven generation discipline — drift, conformance enforcement | Exa | Three templates must be followed precisely. Find measured drift rates and enforcement patterns. |
| C9 (NEW) | Document review integration with substantive critique — pre-handoff review patterns | Exa | document-reviewer fires "PROACTIVELY after PRD/Design Doc/work plan creation"; needs to compose with deeper architectural critique downstream. |
| C10 (NEW) | Codebase analysis output schemas — focusAreas, dataTransformationPipelines (referenced by document-reviewer) | Exa + web | document-reviewer expects `codebase_analysis` JSON with specific shape. Investigate whether standard convention or pipeline-bespoke; what should synth-codebase-researcher's output be. |

## Anti-scope

- Implementation skill bodies (research informs structure only)
- Re-research of round 1/2 topics
- Security review (separate scope)

## Anti-fabrication discipline

Source URI on every claim. Magnitudes flagged single-sourced if uncorroborated. Vendor incentive surfaced for vendor sources.

## Stopping rule

Per topic: 3 convergent sources OR 5 diminishing-returns searches. Round 2 budget: ~25 searches across 8 topics. Round 3 budget: same.

## Output

Small synthesis (~30 claims, 6-10 findings) grounding 8 new ADRs:

- ADR-0011: Adoption of `documentation-criteria` as canonical document skill (extend with three uploaded templates + Intent Clarification + Plan templates)
- ADR-0012: PRD generation as Stage 1.5 (synth-prd-author)
- ADR-0013: Adoption of uploaded Blueprint template
- ADR-0014: Adoption of uploaded ADR template + retroactive migration of ADRs 0001-0010 (Option A — full retrofit)
- ADR-0015: EARS-format acceptance criteria
- ADR-0016: Per-layer fan-out + composer fan-in for Stage 5 (with named sub-agent topology)
- ADR-0017: document-reviewer integration — invocation points (5 named), doc_type extensions (IntentClarification, Plan), integration with synth-architecture-auditor and synth-cross-artifact-auditor
- ADR-0018: synth-codebase-researcher output schema (codebase_analysis JSON shape matching document-reviewer expectations)

Plus a sub-decision (probably folded into ADR-0017 or noted in blueprint v4):
- Rename synth-critic-1 → synth-architecture-auditor
- Rename synth-critic-2 → synth-cross-artifact-auditor

Then blueprint v4 supersedes v3.

## Total ADR count after this round

- Pre-round-2: ADR-0001 through ADR-0006 (blueprint v2's set)
- Added round 2: ADR-0007 v2, ADR-0008, ADR-0009, ADR-0010 (blueprint v3's new set)
- Added round 3 (this plan): ADR-0011 through ADR-0018 (blueprint v4's new set)
- Total at blueprint v4: 18 ADRs (with ADR-0007 having v1+v2)

The ADR-0014 retroactive migration is part of this work — all 18 adopt your uploaded ADR template (Option A from Q-v4-5).
