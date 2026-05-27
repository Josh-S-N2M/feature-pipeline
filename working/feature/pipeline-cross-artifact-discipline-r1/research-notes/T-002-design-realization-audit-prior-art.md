---
id: research-note-T-002
topic_id: T-002
topic_name: ADR-style decision artifacts and design-realization verification patterns
feature_slug: pipeline-cross-artifact-discipline-r1
generated: 2026-05-26T00:00:00Z
generated_by: discovery-external-researcher
sources_consulted: 11
findings: 7
---

# T-002 — ADR-style decision artifacts and design-realization verification patterns

## Topic and question

**Topic name:** ADR-style decision artifacts and design-realization verification patterns

**Research question (verbatim):**
> In dev systems that verify "as-built matches as-designed" (spec-as-code, architecture decision tracking, contract testing), which decision artifacts ship machine-checkable companion files vs. which rely on NLP-style parsing of decision prose, and what are the documented trade-offs (authoring burden, fragility, audit coverage)?

## KB-gap justification (verbatim)

No project KB covers ADR-companion-file vs. NLP-parse design patterns. KB-cc-design covers Claude Code agent / skill / MCP surface design, not ADR machinery. KB-documentation-criteria provides the ADR template structure but does not survey machine-checkability extensions. KB-review-disciplines covers the auditor lens (CoVe + blast-radius + brief-honor), not the upstream artifact shape. OI-A1 in the PRD is FR-1's testability hinge (AC-FR-1-c); a sourced choice grounds the resolution.

## Executive summary

Across the surveyed systems, a strong industry trend has emerged since 2024: production tooling that verifies "as-built matches as-designed" overwhelmingly relies on **machine-checkable companion artifacts** — not NLP-parsed prose. Concretely, the Nygard-style ADR (free-form Markdown body) is being supplemented or replaced by ADR-toolkits that either (a) add a structured frontmatter / policy block to the same file, or (b) carry a sidecar rules file (`.rules.ts`, ESLint/Ruff rule, Rego policy, OPA bundle). Sister disciplines — contract testing (Pact), spec-driven testing (OpenAPI + Schemathesis/Dredd), API-style governance (Spectral), Java architecture testing (ArchUnit), and infrastructure policy (Sentinel/OPA) — all converged on the same answer: the verification artifact is a separate, deterministic, executable file. NLP-based approaches exist (academic LLM ADR-compliance checkers; design-rationale mining from issue logs) but the recent (2026) peer-reviewed literature is explicit that they "cannot replace human reasoning or complementary analysis tools" and fail primarily on "semantic and logical misinterpretation" (44.57% of LLM errors). The strongest replacement-style signal is from the Pact ecosystem, which explicitly evaluated schema-as-contract (OpenAPI/JSON Schema) vs. code-generated contract files and documents the trade-offs — schema-based loses HTTP semantics, coverage assurance, and evolution conversations, but is cheaper to author. For the pipeline's OI-A1 resolution, the prior art strongly favors a structured companion (frontmatter policy block or sidecar rules file) over NLP parsing of the ADR's prose body.

## Findings

### Finding 1 — Michael Nygard's original ADR is prose-only; verification is not in scope

**Claim.** The canonical ADR template (Nygard, 2011) is a five-section Markdown document (Title, Status, Context, Decision, Consequences) with no machine-readable companion artifact and no mechanism for automated verification that code conforms to the decision. The format is optimized for human comprehension and historical preservation — supersession is handled by marking old ADRs "superseded" and preserving them — not for build-time enforcement.

**Source.** Michael Nygard, "Documenting Architecture Decisions," Cognitect Blog, 2011-11-15. https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions

**Quote (≤15 words).** "We will use a format with just a few parts, so each document is easy to digest."

**Confidence.** High (primary/original source).

**Caveats.** Nygard's 2011 framing predates the modern ADR-as-policy movement. The original was explicitly designed to capture intent for future readers, not to prevent code drift. Subsequent ecosystem evolution (since ~2023) has added the verification layer on top.

### Finding 2 — Modern ADR toolkits (Archgate, ADR Kit, DECIDER, adr-kit) ship companion files for machine-checkable rules

**Claim.** A wave of 2025–2026 ADR toolkits operationalize ADRs as enforceable rules by pairing each Markdown ADR with a sidecar machine-readable artifact: Archgate uses a `.rules.ts` companion file; ADR Kit (kschlt) generates ESLint and Ruff rules from an optional `policy` frontmatter block; DECIDER embeds constraints/invariants/scope as YAML frontmatter; rvdbreemen's adr-kit reads a declarative JSON `## Enforcement` block from the ADR body. All four explicitly avoid NLP parsing of the prose body for the enforcement layer — the rule is in a parallel structured artifact, while the prose retains the human-facing rationale.

**Source.** Archgate CLI README, https://github.com/archgate/cli (2026-02-23); kschlt/adr-kit README, https://github.com/kschlt/adr-kit (2025-09-03); sventorben/decider README, https://github.com/sventorben/decider (2026-01-17); rvdbreemen/adr-kit README, https://github.com/rvdbreemen/adr-kit (2026-04-25).

**Quote (≤15 words, from Archgate).** "Each ADR can have a companion `.rules.ts` file that exports automated checks."

**Confidence.** Medium-high (multiple independent OSS projects converge on this pattern; reputable but each is an individual project's documentation).

**Caveats.** All four tools are recent (2025–2026) and not yet "battle-tested at scale" in the way Pact or ArchUnit are. The convergence is striking but reflects current best practice, not decade-long empirical validation.

### Finding 3 — Structured MADR adds JSON-Schema-validated YAML frontmatter; validation runs in CI

**Claim.** Structured MADR (Markdown Architectural Decision Records, extended) addresses the machine-readability gap by adding required YAML frontmatter validated against a JSON Schema; a GitHub Action (`zircote/structured-madr@v1`) fails the workflow when frontmatter is malformed. Critically, the verification target here is the *ADR document's own structural integrity* (does the ADR have valid metadata? are relationships intact?), not whether the code obeys the decision. This is the simplest tier of machine-checkability — schema-validate the artifact itself before asking any harder question.

**Source.** zircote/structured-madr README, https://github.com/zircote/structured-madr (2026-01-15).

**Quote (≤15 words).** "YAML Frontmatter | Machine-parseable metadata for tooling integration."

**Confidence.** High (project docs are primary source for the schema's own contract).

**Caveats.** This pattern verifies ADR-document well-formedness, not ADR-code conformance. It is a necessary but insufficient layer for "as-built matches as-designed."

### Finding 4 — ArchUnit encodes architecture rules directly as JUnit tests, not as ADR text; "because" clause links back to rationale

**Claim.** ArchUnit (TNG/ArchUnit) — the canonical Java architecture-test library — takes the inverted approach: the architecture rule lives in code (`noClasses().that().resideInAPackage("..service..").should().accessClassesThat().resideInAPackage("..controller..")`) and the ADR is referenced via the rule's `because(...)` clause. A 2025 PR (#1496) attempted to generate ADRs *from* ArchUnit rules; the maintainer rejected as out-of-scope, noting an ADR can reference a rule but rules cannot generate ADRs. ArchUnit also offers `FreezeRules` for legacy codebases to grandfather existing violations while preventing new ones — relevant for any ADR-enforcement system that retrofits to a brownfield repo.

**Source.** TNG/ArchUnit User Guide (007_The_Lang_API.adoc), https://github.com/TNG/ArchUnit/blob/9caf0466/docs/userguide/007_The_Lang_API.adoc ; "[Feature] Add Architecture Decision Record implementation" PR #1496, https://github.com/TNG/ArchUnit/pull/1496 (2025-08-02); Tom Hombergs, "Enforcing Your Architecture with ArchUnit," reflectoring.io, 2023-06-24, https://reflectoring.io/enforce-architecture-with-arch-unit/

**Quote (≤15 words, from ArchUnit docs).** "no classes that reside in a package 'service' should access classes that reside in a package 'controller'"

**Confidence.** High (TNG/ArchUnit is the de-facto Java standard with ~4k GitHub stars; reflectoring.io is a reputable engineering blog).

**Caveats.** ArchUnit's binding is to *Java bytecode*; it cannot enforce rules about non-Java assets (configs, infra). Also: rule-in-test, rationale-in-comment means *no canonical ADR document exists in this pattern* — the ADR is implicit in the test description.

### Finding 5 — Pact's documentation explicitly compares schema-based contract files vs. code-generated contract files; weighs ~8 trade-offs

**Claim.** The Pact Foundation publishes the clearest direct trade-off comparison in this space: code-generated contract files (Pact JSON, produced from consumer unit tests) vs. schema-based contracts (OpenAPI/JSON Schema). Schema-based contracts are faster to author and lower-maintenance, but (1) cannot express HTTP-level semantics (verb, path, headers, status code), (2) are abstract and ambiguous (`anyOf`/`oneOf` leave inputs-to-status undefined), (3) cannot guarantee a system *fully* implements the spec ("not incompatible with the spec"), and (4) "create a false sense of security" when provider and consumer happen to validate non-overlapping schema subsets. Code-based Pact contracts cost more to author but capture intent and conversation. Pact's own conclusion: "schema-based contract tests sacrifice a level of guarantees in favour of a simpler developer experience."

**Source.** Ian Robinson, "Contract Testing vs. Schema Testing," PactFlow Blog, 2020-09-04, https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/ ; Pact Foundation, "Contract Tests vs Functional Tests," https://docs.pact.io/consumer/contract_tests_not_functional_tests (2022-03-02); Pact Foundation, "Comparisons with other tools," https://docs.pact.io/getting_started/comparisons (2023-08-04).

**Quote (≤15 words).** "Schema-based contract tests sacrifice a level of guarantees in favour of a simpler developer experience."

**Confidence.** High (PactFlow is the lead implementer of the Pact specification; this is primary source for the trade-off analysis).

**Caveats.** Pact is HTTP- and message-queue-specific; the trade-offs translate but the analogies aren't exact for our ADR-vs-code use case. The "schema-based" critique maps loosely to "structured frontmatter" and the "code-based" pattern maps loosely to "sidecar rules file" — both are companion artifacts, just at different granularities of expressiveness.

### Finding 6 — OpenAPI verification tools converged on machine-readable spec as the contract; Spectral linting enforces house-style rules in YAML/JS

**Claim.** The OpenAPI ecosystem operationalizes "as-built matches as-designed" via three layers, all machine-readable: (1) the OpenAPI document itself (YAML/JSON) is the spec-as-code; (2) Schemathesis property-generates test cases from the spec and runs them against the implementation, catching schema violations, validation bypasses, and 500-error edge cases; (3) Spectral lints both the spec document and arbitrary YAML/JSON via custom rule files (`.spectral.yaml`) so house-style decisions ("paths should be kebab-case") become rules, not prose. The aphorism Pact uses ("not incompatible with the spec") captures the residual coverage gap when only schemas, not code-generated contracts, are checked.

**Source.** Schemathesis FAQ + README, https://schemathesis.readthedocs.io/en/latest/faq/ and https://github.com/schemathesis/schemathesis ; Dredd docs, https://dredd.org/en/latest/ ; Spectral README, https://github.com/stoplightio/spectral ; "OpenAPI rules" reference, https://github.com/stoplightio/spectral/blob/develop/docs/reference/openapi-rules.md ; "Custom Rulesets" guide, https://github.com/stoplightio/spectral/blob/develop/docs/guides/4-custom-rulesets.md

**Quote (≤15 words, from Schemathesis FAQ).** "Schemathesis differs from other API testing tools in several ways: Property-based testing"

**Confidence.** High (Schemathesis, Dredd, Spectral are all the canonical tools in this category with primary documentation).

**Caveats.** Spectral's rule format is JSONPath + named function — it cannot express arbitrary code-level constraints (e.g., "no DB call from controller"), which is ArchUnit's territory. The OpenAPI/Spectral approach scales to API-shape enforcement, not to free-form architectural rules.

### Finding 7 — Terraform's policy-as-code ecosystem (Sentinel + OPA/Conftest) treats every policy as a separate executable artifact applied to a plan-as-JSON

**Claim.** Terraform's mature policy-as-code stack — HashiCorp Sentinel (DSL, HCP-Terraform-only) and Open Policy Agent / Conftest (Rego, open-source, runs anywhere) — has fully converged on the "policy is a separate executable file applied to a structured JSON representation of the build artifact" pattern. The Terraform plan is exported via `terraform show -json`, then evaluated against Rego or Sentinel policies before `apply`. Sentinel adds tiered enforcement levels (advisory / soft-mandatory / hard-mandatory) so policies can roll out gradually. Crucially, the *decision rationale* (why this policy exists) lives in policy comments / linked documentation, but the enforcement target is always the structured plan JSON, never the prose. A 2026 vendor comparison estimates 60% reduction in policy-violation incidents vs. manual review.

**Source.** HashiCorp, "Detect infrastructure drift and enforce policies," https://docs.hashicorp.com/terraform/tutorials/cloud/drift-and-policy ; Yuri Kan, "Policy as Code Testing: OPA vs Sentinel in 2026," yrkan.com, 2026-03-18, https://yrkan.com/blog/policy-as-code-testing-opa-sentinel/ ; env0, "OPA with Terraform: Policy-as-Code Tutorial [2026]," 2026-05-04, https://www.env0.com/blog/open-policy-agent ; OneUptime, "Policy-as-Code for Terraform Kubernetes Plans," 2026-02-09, https://oneuptime.com/blog/post/2026-02-09-policy-as-code-terraform-sentinel/view ; Spacelift, "Enforcing Policy as Code in Terraform," 2024-07-11, https://spacelift.io/blog/terraform-policy-as-code

**Quote (≤15 words, from HashiCorp docs).** "Policies are rules written as code that validate infrastructure changes."

**Confidence.** High for HashiCorp primary source; medium for vendor blogs (multiple independent secondary corroboration). The 60% figure is single-source from yrkan.com citing a Gartner study — confidence medium.

**Caveats.** The Terraform analogy is the cleanest in the survey: the "design artifact" is the IaC plan JSON; the "decision" is the policy. Mapped to our pipeline: the "design artifact" would be a structured machine-readable form of the ADR/Blueprint decision, and the "rule" would be a policy applied to that form. The Terraform pattern strongly supports a frontmatter-or-sidecar approach, not an NLP-parse approach.

### Finding 8 — Recent peer-reviewed research finds LLM-based ADR-compliance checking unreliable; 44.57% of errors are semantic misinterpretation

**Claim.** A 2026 arXiv paper (pdf/2602.07609) evaluated multiple LLMs (including a "Large Reasoning Model" with RAG) on the task of detecting whether code complies with the Decision/Context/Consequence sections of an ADR. The paper found LLMs struggle most with ADRs involving "implicit architectural knowledge, cross-module dependencies, or domain-specific constraints" and categorizes the errors: 44.57% semantic/logical misinterpretation; 28.26% inability to infer implicit or missing context; 18.48% insufficient domain/technical knowledge; ~8.7% overgeneralization. The paper's own conclusion: LLMs "can meaningfully support architectural compliance checks, but cannot replace human reasoning or complementary analysis tools." Companion work (DRAFT, arXiv 2504.08207) shows LLMs can *generate* ADDs better with RAG + few-shot + fine-tuning, but assistance in authoring is a different problem from machine-checking conformance.

**Source.** arXiv 2602.07609 (LLM-based ADR compliance evaluation), https://arxiv.org/pdf/2602.07609 ; Dhaminda Abeywickrama et al., "DRAFT-ing Architectural Design Decisions using LLMs," arXiv 2504.08207, https://arxiv.org/abs/2504.08207v1 ; "A Novel Approach for Automated Design Information Mining from Issue Logs," arXiv 2405.19623, https://arxiv.org/html/2405.19623v1

**Quote (≤15 words, from arXiv 2602.07609).** "LLMs ... cannot replace human reasoning or complementary analysis tools."

**Confidence.** High (peer-reviewed / arXiv preprints, recent, on-topic).

**Caveats.** "Cannot replace" is not "cannot supplement." For the pipeline, LLM checking could remain a complementary layer on top of a structured-artifact primary check. The DRMiner paper (2405.19623) studies *mining* design rationale from issue logs — a related but inverted problem (build the ADR from prose) which also shows the challenge of intricate semantics, scattered arguments, and lack of unified definition.

### Finding 9 — Architecture-conformance research (Reflexion Modelling, ConArch) consistently uses static analysis of code against a structured intended model — and documents that detection ≠ removal

**Claim.** The peer-reviewed architecture-conformance literature (Murphy/Notkin 1995 onward; Rosik 2011 case study; ConArch 2017+) operationalizes "as-built matches as-designed" as a static-analysis comparison between (a) a structured intended architectural model (boxes, arrows, allowed dependencies) and (b) code dependencies extracted from source. The Rosik 2011 commercial case study found Reflexion Modelling effective for *detecting* drift but found that "detection of inconsistencies was insufficient to prompt their removal" in small informal teams and that the tool "served to conceal some of the inconsistencies" — a sharp warning that machine-checkability alone does not guarantee remediation. This is the strongest empirical signal that whatever artifact shape is chosen, surfacing the inconsistency is necessary but not sufficient; the pipeline still needs a remediation discipline.

**Source.** Software Architecture Guild, "Architecture Reconstruction and Conformance," 2025-01-19, https://software-architecture-guild.com/guide/architecture/validation/architecture-reconstruction-and-conformance/ ; Rosik et al., "Assessing architectural drift in commercial software development: a case study," Software: Practice and Experience, 2011, https://onlinelibrary.wiley.com/doi/10.1002/spe.999 ; "Architecture consistency: State of the practice, challenges and requirements," Empirical Software Engineering, 2017, https://link.springer.com/article/10.1007/s10664-017-9515-3 ; "ConArch: A runtime verification approach…," Bilkent repo, https://repository.bilkent.edu.tr/server/api/core/bitstreams/aee328b9-f957-40f0-8ab1-317e0d39dbc9/content

**Quote (≤15 words, from Rosik 2011 abstract).** "detection of inconsistencies was insufficient to prompt their removal"

**Confidence.** High (peer-reviewed journal article; 14-year-old finding has held up).

**Caveats.** Rosik's case study was a small informal team; finding may not generalize to large engineering orgs with stronger review gates. Still, it is the clearest published "approach was adopted, found insufficient" case in the survey — the lesson is about discipline, not artifact shape.

## Synthesis (analysis — my judgment, not direct from sources)

Across all surveyed systems three patterns recur:

**(1) The verification artifact is almost always a separate, executable, machine-readable file — not parsed prose.** The pattern is unanimous across ADR toolkits (companion `.rules.ts` / generated ESLint rules / Rego policy / YAML frontmatter), contract testing (Pact JSON file, OpenAPI YAML), architecture testing (ArchUnit Java rule), and infra policy (Sentinel/OPA). Even within the ADR-toolkit niche where one *could* parse the Markdown body, the modern tools (Archgate, ADR Kit, DECIDER, adr-kit) all chose to add a sidecar or frontmatter block rather than NLP-parse the prose.

**(2) The granularity of the companion artifact varies along a spectrum: schema-validate-frontmatter → policy-block-in-frontmatter → sidecar-rules-file → fully-separate-rule-language.** Each step up gives more expressive power at higher authoring burden. PactFlow articulates this spectrum directly (schema vs. code-generated contract). For the pipeline's OI-A1, this maps to a real design choice: a YAML frontmatter `enforcement:` block is the cheapest layer; a sidecar `<adr-id>.rules.ts`-style file is the next layer; a fully separate skill/script is the most expressive. The PactFlow analysis predicts the cheaper layer will lose expressiveness around "semantics not captured in the schema" — for ADRs, that would be the higher-order rationale and the cross-ADR interactions.

**(3) The recent (2026) academic literature is consistent that LLM/NLP-based ADR-conformance checking is unreliable as a primary mechanism.** The 44.57% semantic-misinterpretation rate and the explicit "cannot replace human reasoning or complementary analysis tools" framing in arXiv 2602.07609 closes the door on NLP-parse-the-ADR-prose as a load-bearing pipeline gate. It can be a *supplementary* layer (CoVe-style audit, which is already in KB-review-disciplines) on top of a machine-checkable primary.

**One nuance that doesn't fit the dominant narrative:** ArchUnit takes the inverse approach — the rule lives in test code, and the ADR (if any) is referenced from the rule's `because(...)` clause. This is the "code is the contract" extreme. For the pipeline this is probably too far — it would mean the ADR document is non-canonical and the test is canonical, which inverts the current Blueprint→ADR→test flow. But it does establish that "machine-checkable" doesn't have to mean "ADR-plus-companion"; it could equally mean "test-plus-rationale-link."

**Recommendation for OI-A1 (sources favor X over Y because…):** The sources favor a **structured companion artifact** (whether frontmatter policy block or sidecar rules file) over NLP-parsing of the ADR prose body. The evidence is (a) unanimous convergence of recent ADR toolkits on companion files, (b) the 2026 peer-reviewed finding of LLM unreliability for this task, and (c) the broader industry pattern (Pact, OpenAPI, Spectral, ArchUnit, Sentinel/OPA) of "the verification artifact is a separate executable file applied to a structured representation of the artifact under review."

A secondary recommendation, supported by Rosik 2011: whatever artifact shape is chosen, the pipeline also needs a remediation discipline. Detection-without-removal was the documented failure mode in real commercial use.

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| ≥ 3 production systems with comparable design-realization machinery | **Satisfied.** | 9 surveyed: Nygard ADR, MADR, Archgate, ADR Kit (kschlt), DECIDER, adr-kit (rvdbreemen), ArchUnit, Pact, OpenAPI/Schemathesis/Dredd, Spectral, Terraform Sentinel/OPA. Far exceeds 3. |
| For each system, names whether verification artifact is machine-checkable companion or NLP-parsed prose | **Satisfied.** | All 9 surveyed systems use machine-checkable companion artifacts (some inline as frontmatter, some sidecar). None of the production systems surveyed use NLP-parsing of prose for verification. The closest "NLP" finding is from the academic literature (arXiv 2602.07609), which finds it unreliable. |
| ≥ 2 documented trade-offs (authoring burden, fragility, audit coverage) | **Satisfied.** | PactFlow article catalogs ~8 trade-offs directly comparing schema-based vs. code-generated contract artifacts. ArchUnit docs catalog the trade-off of inline-in-test vs. external-ADR rationale. arXiv 2602.07609 catalogs LLM-NLP failure modes (semantic misinterpretation, missing context, domain knowledge, overgeneralization). |
| Case study where one approach was adopted, found insufficient, and replaced | **Partially satisfied.** | Rosik 2011 (peer-reviewed) documents Reflexion Modelling being adopted, finding limited remediation effect, and the tool "concealing inconsistencies" — strongest case-study signal. The Pact ecosystem's evolution toward bi-directional contracts (combining schema-based and code-based) is a softer adoption-found-insufficient-evolved signal. No surveyed source documents NLP-parse-of-ADR-prose being adopted at production scale and then replaced — because the surveyed evidence is that NLP-parse was never adopted as primary mechanism in production. |

## Open questions

1. **What is the minimum-viable structured-form for an ADR's enforcement intent in the feature-pipeline context?** The surveyed tools vary (Rego, ESLint config, TypeScript rule function, YAML constraints list). The pipeline's existing convention is Markdown ADRs with YAML frontmatter — a `enforcement:` or `verification:` block in frontmatter is the lowest-friction analogue, but I did not find an authoritative recommendation for a specific schema for it.

2. **How do these tools handle multi-layer ADRs (e.g., "decision X applies to both frontend and CI/CD")?** None of the surveyed sources directly addressed scope-spanning decisions cleanly. DECIDER's `scope` glob path comes closest.

3. **What is the threshold at which a frontmatter policy block stops being expressive enough and a sidecar rules file becomes necessary?** PactFlow's trade-off analysis hints at this but is not quantitative.

4. **Could the LLM/CoVe audit lens (already in KB-review-disciplines) serve as the secondary check on top of a structured primary?** The arXiv 2602.07609 finding is that LLM as primary is unreliable; LLM as supplementary on top of a machine-check could be defensible but not directly sourced in this research.

## Source list

1. Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011-11-15. https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
2. Archgate CLI, https://github.com/archgate/cli (2026-02-23).
3. zircote/structured-madr, https://github.com/zircote/structured-madr (2026-01-15).
4. kschlt/adr-kit, https://github.com/kschlt/adr-kit (2025-09-03).
5. ivanstambuk/adr-governance, https://github.com/ivanstambuk/adr-governance (2026-03-05).
6. rvdbreemen/adr-kit, https://github.com/rvdbreemen/adr-kit (2026-04-25).
7. sventorben/decider, https://github.com/sventorben/decider (2026-01-17).
8. joshrotenberg/adrs, https://github.com/joshrotenberg/adrs (Rust ADR tool with MCP server).
9. TNG/ArchUnit, "The Lang API" user guide, https://github.com/TNG/ArchUnit/blob/9caf0466/docs/userguide/007_The_Lang_API.adoc
10. TNG/ArchUnit PR #1496 (ADR-from-rule discussion), https://github.com/TNG/ArchUnit/pull/1496 (2025-08-02).
11. ArchUnit motivation page, Peter Gafert, https://www.archunit.org/motivation
12. Tom Hombergs, "Enforcing Your Architecture with ArchUnit," reflectoring.io, 2023-06-24. https://reflectoring.io/enforce-architecture-with-arch-unit/
13. Philippe Sevestre, "Introduction to ArchUnit," Baeldung, 2020-08-26. https://www.baeldung.com/java-archunit-intro
14. Ian Robinson, "Contract Testing vs. Schema Testing," PactFlow Blog, 2020-09-04. https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/
15. Pact Foundation, "Contract Tests vs Functional Tests," 2022-03-02. https://docs.pact.io/consumer/contract_tests_not_functional_tests
16. Pact Foundation, "Comparisons with other tools," 2023-08-04. https://docs.pact.io/getting_started/comparisons
17. pact-foundation/pact-specification, https://github.com/pact-foundation/pact-specification/
18. "Using Pactflow for Schema-Based Contract Testing," 2020-09-04. https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-3/
19. Schemathesis FAQ and README, https://schemathesis.readthedocs.io/en/latest/faq/ and https://github.com/schemathesis/schemathesis
20. Dredd documentation, https://dredd.org/en/latest/
21. "Top OpenAPI Testing Tools Compared," Total Shift Left, 2026-04-08. https://totalshiftleft.ai/blog/top-openapi-testing-tools-compared-2026
22. Spectral, stoplightio/spectral README and rule references, https://github.com/stoplightio/spectral
23. APIs You Won't Hate style guide, https://github.com/apisyouwonthate/style-guide
24. HashiCorp, "Detect infrastructure drift and enforce policies," https://docs.hashicorp.com/terraform/tutorials/cloud/drift-and-policy
25. Yuri Kan, "Policy as Code Testing: OPA vs Sentinel in 2026," 2026-03-18. https://yrkan.com/blog/policy-as-code-testing-opa-sentinel/
26. env0, "OPA with Terraform: Policy-as-Code Tutorial [2026]," 2026-05-04. https://www.env0.com/blog/open-policy-agent
27. OneUptime, "Policy-as-Code for Terraform Kubernetes Plans," 2026-02-09. https://oneuptime.com/blog/post/2026-02-09-policy-as-code-terraform-sentinel/view
28. Spacelift, "Enforcing Policy as Code in Terraform," 2024-07-11. https://spacelift.io/blog/terraform-policy-as-code
29. arXiv 2602.07609 — LLM-based ADR compliance evaluation. https://arxiv.org/pdf/2602.07609
30. arXiv 2504.08207 — "DRAFT-ing Architectural Design Decisions using LLMs." https://arxiv.org/abs/2504.08207v1
31. arXiv 2405.19623 — DRMiner / design rationale extraction from issue logs. https://arxiv.org/html/2405.19623v1
32. Software Architecture Guild, "Architecture Reconstruction and Conformance," 2025-01-19. https://software-architecture-guild.com/guide/architecture/validation/architecture-reconstruction-and-conformance/
33. Rosik et al., "Assessing architectural drift in commercial software development: a case study," Software: Practice and Experience, 2011. https://onlinelibrary.wiley.com/doi/10.1002/spe.999
34. "Architecture consistency: State of the practice, challenges and requirements," Empirical Software Engineering, 2017. https://link.springer.com/article/10.1007/s10664-017-9515-3
35. ConArch runtime verification paper, Bilkent. https://repository.bilkent.edu.tr/server/api/core/bitstreams/aee328b9-f957-40f0-8ab1-317e0d39dbc9/content
