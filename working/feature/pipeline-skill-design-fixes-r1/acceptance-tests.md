---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/pipeline-skill-design-fixes-r1/prd-v1.md
approved_at: 2026-05-21T05:25:00Z
gate_passed: 5
---

# Acceptance Tests — pipeline-skill-design-fixes-r1

## AC-1 (precondition documented)

**Procedure.** `grep -n 'Working-directory precondition\|cwd MUST equal\|ADR-0027' .claude/skills/recipe-feature-pipeline/SKILL.md`

**Pass condition.** Returns lines containing all three patterns.

## AC-2 (precondition verified)

**Procedure.** Read Stage 1 section of orchestrator SKILL.md. Confirm step 0 (or equivalent) names a precondition check for `.claude/` existence + halt instruction referencing ADR-0027.

**Pass condition.** Stage 1 begins with a precondition check.

## AC-3 (packager exists)

**Procedure.** `test -f .claude/agents/finalize-deliverable-packager.md && python3 -c "import yaml, re; content=open('.claude/agents/finalize-deliverable-packager.md').read(); m=re.match(r'^---\n(.*?)\n---', content, re.DOTALL); fm=yaml.safe_load(m.group(1)); print('name:', fm.get('name')); print('description present:', bool(fm.get('description'))); print('tools:', fm.get('tools')); print('skills:', fm.get('skills'))"`

**Pass condition.** File exists; frontmatter parses; `name == 'finalize-deliverable-packager'`; description, tools, skills all populated.

## AC-4 (packager scope documented)

**Procedure.** Read packager body. Verify presence of sections: Inputs, At task start, Procedure, Optional handoff drafting, Outputs, Failure modes, Related agents.

**Pass condition.** All sections present.

## AC-5 (orchestrator invokes packager)

**Procedure.** `grep -n 'finalize-deliverable-packager\|Stage 13\|Deliverable Packaging' .claude/skills/recipe-feature-pipeline/SKILL.md`

**Pass condition.** Returns lines documenting Stage 13 invocation of the packager.

## AC-6 (doc_type extended)

**Procedure.** `grep -n 'DeliverableArchive' .claude/agents/shared-document-reviewer.md`

**Pass condition.** Returns at least one line mentioning the new doc_type.

## AC-7 (validator integrated)

**Procedure.** Read packager body's "Procedure" section. Verify it includes invocation of `shared-document-reviewer` with `doc_type: DeliverableArchive`.

**Pass condition.** Invocation documented.

## AC-8 (spec exists)

**Procedure.** `test -f .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md && grep -c '^## Contents$' .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md`

**Pass condition.** File exists; `## Contents` H2 count == 1.

## AC-9 (spec covers scope classes)

**Procedure.** `grep -E '^### (FULL|MINOR|PATCH)' .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md | wc -l`

**Pass condition.** Returns 3 (one section per scope class).

## AC-10 (existing MINOR-scope archive validates)

**Procedure.** Manual enumeration of v4.4.2's `working/feature/frontend-design-knowledge-r1/` against the spec's MINOR expected-artifact list. Note: this is the original frontend-design-knowledge-r1 feature, which had FULL scope (Discovery + Synthesis + per-layer Design all executed). So validate as FULL not MINOR.

**Pass condition.** All required artifacts present; no MAJOR or BLOCKER findings.

## AC-11 (existing PATCH-scope archive validates)

**Procedure.** Manual enumeration of v4.4.2's `working/feature/audit-machinery-fixes-r1/` against the spec's PATCH expected-artifact list.

**Pass condition.** All required artifacts present; conditional skips justified per intent-clarification's `scope_class: PATCH` declaration.

## AC-12 (ADR-0028 authored)

**Procedure.** `test -f adrs/ADR-0028-skill-design-fixes-v4-5-0.md && python3 -c "import yaml, re; content=open('adrs/ADR-0028-skill-design-fixes-v4-5-0.md').read(); m=re.match(r'^---\n(.*?)\n---', content, re.DOTALL); fm=yaml.safe_load(m.group(1)); print('id:', fm.get('id')); print('status:', fm.get('status'))"`

**Pass condition.** File exists; `id: ADR-0028`; `status: accepted`.
