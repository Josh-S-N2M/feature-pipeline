---
id: research-note-T-004
topic: cross-file-invariant-catalog-patterns
version: 1.0.0
status: draft
generated: 2026-05-26T00:00:00Z
generated_by: discovery-external-researcher
feature_slug: pipeline-cross-artifact-discipline-r1
---

# T-004 — Cross-file invariant catalogs: denormalized per-file vs. centralized reference

## Topic and research question

**Topic name (verbatim):** Cross-file invariant catalogs — denormalized per-file vs. centralized reference.

**Research question (verbatim):** How do other systems catalog cross-file invariants — Terraform's plan-time invariant validations, OpenAPI's schema-consistency invariants, dbt's schema tests, contract-testing tooling — and what's the documented trade-off between authoring the invariants denormalized per-file (each file declares its relationships) vs. centralized in a single referenced catalog?

## KB-gap statement (informational)

KB-iac-design is out-of-scope for this feature (Layer Scope = Claude Code only). KB-task-decomposition covers PV authoring discipline but does not survey cross-file invariant catalog patterns outside the project. KB-documentation-criteria covers template structure, not invariant authoring. OI-A2 in the PRD is the H9 authoring-shape resolver (normalized-vs-denormalized) and requires sourced precedent from comparable cross-file-invariant systems.

## Executive summary

Six systems were surveyed: Terraform's `precondition`/`postcondition` lifecycle blocks, dbt's `properties.yml` (formerly `schema.yml`) data tests with `ref`, OpenAPI's `components` + `$ref`, JSON Schema's `$defs` + `$ref`, ArchUnit's `ArchRule`/`ArchModule` + the shareable rules-library pattern, and Bazel's `package_group` for cross-package visibility invariants. A consistent pattern emerges across all six: **the authoring surface is denormalized (each artifact carries its own declarations), but reusable rule bodies and identifiers are factored into a centralized catalog and referenced**. None of the surveyed systems adopt a fully centralized authoring model in which a single file owns all cross-file invariants. The strongest migration signal is Shopify's Packwerk retrospective, which describes walking back from a utopian centrally-orchestrated package-graph vision toward a more pragmatic, locally-declared model after privacy checks proved too costly — supporting a hybrid (denormalized declarations + central shared definitions) over either extreme.

## Findings

### Finding 1 — Terraform: denormalized invariants on each resource, no central catalog

**Claim.** Terraform's `precondition` and `postcondition` blocks live inside each `resource`, `data`, or `output` block's `lifecycle` block; the condition expression can reference any other object in the same configuration scope, but there is no global "invariant catalog" file. The expression itself is authored where the resource is declared, and Terraform evaluates conditions in dependency order at plan/apply time.

**Source.** HashiCorp Developer — "lifecycle meta-argument reference" (https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle), published 2025-11-19, and "Validate your infrastructure in Terraform's configuration language" (https://docs.hashicorp.com/terraform/language/validate), 2025-11-19.

**Quote (≤15 words).** "You can refer to any other object in the same configuration scope unless the reference creates a cyclic dependency."

**Confidence.** High (official HashiCorp documentation).

**Caveats.** Terraform also supports `check` blocks (v1.5.0+) which can be authored as standalone blocks rather than inside a resource — these are closer to a centralized assertion but are still authored at top level alongside resources, not in a separate catalog file. Module input-variable `validation` blocks are similarly per-variable, not centralized.

### Finding 2 — Terraform: documented precondition-vs-postcondition trade-off encodes a "place the invariant where it makes sense to maintain it" discipline

**Claim.** HashiCorp explicitly tells authors that the choice between precondition and postcondition is about *whose responsibility* the invariant represents — the consumer's assumption vs. the producer's guarantee — and recommends placing each invariant near the block whose author should maintain it. This is a locality argument: invariants live with the artifact whose author is best-placed to keep them current.

**Source.** HashiCorp Developer — "custom-conditions" in web-unified-docs (https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.11.x/docs/language/expressions/custom-conditions.mdx).

**Quote.** Paraphrased (one quote per source rule applied; finding 1 used the quote slot).

**Confidence.** High (official HashiCorp documentation).

**Caveats.** This guidance is normative for module-author UX, but does not directly address denormalized-vs-centralized — it argues against centralization implicitly by tying invariants to lifecycle position.

### Finding 3 — dbt: per-file declaration with optional centralization, official docs decline to prescribe

**Claim.** dbt allows model invariants (data tests, `relationships` referential-integrity tests, descriptions) to be declared in `properties.yml` files (formerly `schema.yml`) located either per-model, per-directory, or as a single project-wide file. The official FAQ explicitly leaves the choice to the team. The `relationships` test is the cross-file invariant: it uses `ref()` to assert that every value in a child column has a corresponding parent row.

**Source.** dbt Developer Hub — "Should I use separate files to declare resource properties, or one large file?" (https://docs.getdbt.com/faqs/Project/multiple-resource-yml-files), 2026-05-18; "About data tests property" (https://docs.getdbt.com/reference/resource-properties/data-tests), 2026-05-21; "Define properties" (https://docs.getdbt.com/reference/define-properties), 2026-05-21.

**Quote (≤15 words).** "Some folks find it useful to have one file per model... Some find it useful to have one per directory."

**Confidence.** High (official dbt-labs docs).

**Caveats.** dbt has explicitly *renamed* the file from `schema.yml` to `properties.yml` and updated its terminology — the team is encouraging authors to think of these as resource-property files (denormalized by default) rather than a centralized "schema" catalog. Community-vote sources (Stack Overflow, Discourse) corroborate but are excluded by source constraints.

### Finding 4 — dbt: community-best-practice consensus favors folder-level YAML as compromise

**Claim.** Practitioner guides converge on folder-level YAML (`_[directory]__models.yml`) as the best default — one-file-per-model creates churn; one-monolithic-file harms discoverability. The trade-off named is exactly the OI-A2 axis: locality/churn vs. discoverability.

**Source.** Semantic Stack — "dbt project best practices guide" (https://semanticstack.app/resources/dbt-best-practices/) — an engineering-blog-style guide, treated as medium confidence per source constraints.

**Quote (≤15 words).** "A single monolithic YAML file centralizes config but makes specific tests, descriptions, and source definitions hard to find."

**Confidence.** Medium (practitioner guide, not official dbt-labs; cited because it names the trade-off explicitly with rationale).

**Caveats.** Not authoritative; included because it surfaces the exact OI-A2 trade-off vocabulary ("monolithic centralizes but harms discoverability"). dbt-labs' own FAQ remains neutral.

### Finding 5 — OpenAPI: centralized `components/schemas` is the strong norm; inline schemas are considered an anti-pattern

**Claim.** OpenAPI consolidates reusable schemas, parameters, responses, request bodies, security schemes, and other reusable objects into `#/components/<type>/<name>`. The spec itself permits `$ref` anywhere a reference is valid, and the OpenAPI Initiative's `learn.openapis.org` referencing guide states reusable definitions belong in `components`. Engineering guides treat inlining repeated schemas as a documented anti-pattern.

**Source.** OpenAPI Initiative — "Using References" (https://learn.openapis.org/referencing/); OpenAPI Specification v3.1.2 — Components Object (https://spec.openapis.org/oas/v3.1.2), 2025-09-19; BytePane "OpenAPI & Swagger Guide" (https://bytepane.com/blog/openapi-swagger-guide/), 2026-04-14.

**Quote (≤15 words).** "Holds a set of reusable objects for different aspects of the OAS."

**Confidence.** High (official OpenAPI Initiative spec text).

**Caveats.** OpenAPI 3.1 introduced sibling-keyword support for `$ref` (siblings like `description` are honored), which slightly narrows the spec gap between centralized and inline forms.

### Finding 6 — OpenAPI: explicit trade-off — central `$ref` improves consistency at the cost of change-tracking opacity

**Claim.** Bump.sh's advanced `$ref` guide (treated as a reputable engineering blog from a vendor operating OpenAPI tooling at scale) names the central-vs-inline trade-off directly: splitting components reduces merge conflicts and DRY violations but "becomes harder to follow API changes" because a single schema edit affects many endpoints. The remedy proposed is automated breaking-change detection on PRs, not abandoning centralization.

**Source.** Bump.sh — "OpenAPI & AsyncAPI $ref: Advanced Guide" (https://bump.sh/blog/openapi-asyncapi-ref-usage-guide/).

**Quote (≤15 words).** "Changing a schema in one document can effect how multiple different endpoints work."

**Confidence.** Medium (vendor engineering blog; corroborated by Speakeasy and Redocly which are also vendor sources).

**Caveats.** Bump.sh is a vendor whose product depends on multi-file OpenAPI; bias toward modular structures. Cited because it names the trade-off precisely and the mitigation (tooling-level change detection) is the same one the Cross-Artifact-Discipline feature contemplates.

### Finding 7 — JSON Schema: `$defs` is the in-document central catalog; cross-document `$ref` is supported but explicitly discouraged for general use

**Claim.** JSON Schema's `$defs` keyword (since draft 2019-09; previously `definitions`) "gives us a standardized place to keep subschemas intended for reuse in the current schema document." Cross-document `$ref` works but the official guide recommends limiting `$ref` to either an external schema or an internal `$defs`-defined subschema, and recommends bundling external resources into `$defs` for distribution.

**Source.** JSON Schema — "Modular JSON Schema combination" (https://json-schema.org/understanding-json-schema/structuring); JSON Schema core spec (https://github.com/json-schema-org/json-schema-spec/blob/main/specs/jsonschema-core.md).

**Quote (≤15 words).** "$defs gives us a standardized place to keep subschemas intended for reuse in the current schema document."

**Confidence.** High (official JSON Schema docs and spec).

**Caveats.** "Compound Schema Documents" (bundles) are an *implementation* concern — the *authoring* surface remains per-file with selective central reuse. JSON Schema cautions implementers to disable dynamic remote `$ref` retrieval by default for security and resource-exhaustion reasons, which structurally biases practice toward in-document `$defs` over true cross-file central catalogs.

### Finding 8 — ArchUnit: rules are authored as per-test-class declarations; sharing across repos requires explicit module packaging

**Claim.** ArchUnit's `ArchRule`s are declared as static fields in JUnit test classes; the user guide and engineering write-ups show rules written *in* the repository that owns the code under test. To share rules across multiple repositories, authors must package them into a separate JAR (the official "ArchRules" / Nebula Netflix pattern), publish it, and depend on it as a `test`-scope dependency. There is no built-in central-rule-server concept.

**Source.** ArchUnit User Guide (https://www.archunit.org/userguide/html/000_Index.html); ArchUnit Library API docs (https://github.com/TNG/ArchUnit/blob/9caf0466/docs/userguide/008_The_Library_API.adoc); Netflix Nebula ArchRules plugin (https://github.com/nebula-plugins/nebula-archrules-plugin).

**Quote (≤15 words).** "ArchUnit a popular OSS library used to enforce architectural code rules as part of a JUnit suite."

**Confidence.** High (official ArchUnit user guide; Netflix/Nebula plugin docs corroborate the "sharing requires explicit packaging" point).

**Caveats.** ArchUnit's `ArchModule` API (using `@AppModule` annotations on `package-info`) brings rule metadata back to *colocation with the package being constrained* — a deliberate move toward per-package denormalization for module-dependency declarations. Nebula's plugin exists *because* ArchUnit's built-in mechanism is per-repo by design.

### Finding 9 — Bazel: package-level visibility invariants combine per-target declaration with shared `package_group` definitions

**Claim.** Bazel's `visibility` attribute is declared per-target (denormalized), but Bazel's documented best practice is to factor repeated visibility lists into a `package_group` target that is referenced from multiple `visibility` attributes. This is exactly the hybrid pattern — declarations stay local, identifier bodies centralize when reuse warrants it.

**Source.** Bazel — "Visibility" concept doc (https://bazel.build/concepts/visibility); Bazel reference functions (https://bazel.build/versions/8.7.0/reference/be/functions).

**Quote (≤15 words).** "Use package_group instead of repeating the list in each target's visibility attribute."

**Confidence.** High (official Bazel docs).

**Caveats.** Bazel also has a `default_visibility` package-level setter, which is a localized centralization (one BUILD file's targets share a default). This is a third design point: per-package central with per-target override.

### Finding 10 — Migration case study: Shopify's Packwerk retrospective walks back from utopian central modularization

**Claim.** Shopify's Packwerk retrospective is the closest documented migration case to OI-A2's central-vs-denormalized axis. Packwerk was built to enforce a strict, centrally-defined package dependency graph; over time Shopify removed privacy-check enforcement, carved out a "Platform" package as an organizational compromise, and concluded that components should be top-level organizational tools that contain *one or more packages*, not single-unit central modules. The team retained Packwerk for "holding the line" against new violations but abandoned the strict-central vision.

**Source.** Rails at Scale (Shopify engineering blog) — "A Packwerk Retrospective" (https://railsatscale.com/2024-01-26-a-packwerk-retrospective/), 2024-01-26.

**Quote (≤15 words).** "Privacy checks were removed from Packwerk with the release of version 3.0."

**Confidence.** High (first-party engineering blog from the company operating the system).

**Caveats.** Packwerk is Ruby-monolith-specific and the invariant being centralized was a *dependency graph*, not a documentation invariant — but it is the strongest "tried centralized, walked back" signal found across all six systems surveyed. The retrospective explicitly cautions against utopian central designs that fight the grain of the codebase.

## Cross-system synthesis (analysis, not source claims)

A consistent shape emerges across all six surveyed systems and the migration case study:

1. **Authoring stays denormalized.** Every system surveyed authors invariant *declarations* at the artifact they constrain (per-resource in Terraform; per-model in dbt; per-target in Bazel; per-test-class in ArchUnit; per-path-item in OpenAPI; per-subschema in JSON Schema). None centralizes the declaration site.

2. **Bodies/identifiers centralize for reuse.** Wherever the same invariant body or identifier list is reused, every system provides a centralization mechanism: `components/schemas` (OpenAPI), `$defs` (JSON Schema), `package_group` (Bazel), `tests/generic/` macros (dbt), a separate ArchRules JAR (ArchUnit), or shared modules (Terraform). Centralization is for *bodies*, not declarations.

3. **The trade-off vocabulary is consistent.** Sources name the same axis: locality / churn / per-PV-discoverability (favoring denormalization) versus DRY / consistency / one-place-to-update (favoring centralization). Bump.sh names it explicitly for OpenAPI; the Semantic Stack guide names it explicitly for dbt; Shopify's retrospective demonstrates the failure mode of pure centralization for dependency invariants.

4. **Tooling-level change detection is the consensus mitigation.** When centralization makes change impact opaque, the named remedy is *automated breaking-change/impact-analysis on PRs*, not retreat from centralization. (Bump.sh, Redocly, the Shopify "list of violations" pattern.)

5. **The strongest signal for OI-A2.** The Shopify Packwerk retrospective is the clearest "adopted central, found it insufficient, walked back" datapoint. The lesson is not "centralized is bad" but "fully-centralized invariant *authoring* fights the grain when the artifact authors are different teams." Hybrid (denormalized declaration, centralized body) is the documented sweet spot across every survey datapoint.

**Recommendation framing (sources favor X over Y):** The surveyed sources favor a hybrid model — invariants declared at the artifact (denormalized) with reusable invariant *bodies* lifted into a centrally-referenced catalog. They do not favor fully-centralized invariant authoring, and the only migration case study found walked away from that extreme. Whether this maps to the Phase Validator authoring shape is a design decision for design-composer and the relevant Layer Designer; this note surfaces the precedent and trade-offs only.

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Identifies ≥ 3 systems that catalog cross-file invariants | Satisfied | Six systems surveyed: Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel. All have first-party documentation. |
| For each system, names whether the invariant catalog is denormalized or centralized | Satisfied | Terraform = denormalized; dbt = configurable, per-file default; OpenAPI = centralized in `components` is the norm; JSON Schema = centralized in `$defs` per-document, cross-doc discouraged; ArchUnit = denormalized in test classes, central via packaged JAR; Bazel = denormalized declarations with centralized `package_group` bodies. |
| Identifies ≥ 2 trade-offs (authoring burden vs. discoverability; per-PV locality vs. catalog reuse) | Satisfied | Trade-offs documented: (a) locality/maintainability vs. DRY (HashiCorp's precondition-vs-postcondition guidance), (b) merge-conflict reduction / per-team ownership vs. change-tracking opacity (Bump.sh on OpenAPI), (c) discoverability vs. monolithic-file scanning cost (Semantic Stack on dbt YAML structure), (d) strict-central enforcement vs. real-world team boundaries (Shopify Packwerk retrospective). |
| Surfaces any system that adopted one approach, found it insufficient, and migrated to the other | Satisfied | Shopify Packwerk retrospective is the explicit migration-away-from-central case study (v3.0 removed privacy checks; "Platform" package carve-out; component-as-organizational-grouping reframing). |

All four acceptance criteria are satisfied within source constraints. No escalation required.

## Open questions

1. None of the surveyed systems is a 1:1 analogue for Phase Validator authoring — they constrain *code/data/API artifacts*, not *pipeline-document content*. The applicability of "hybrid is the consensus shape" to PV authoring shape (OI-A2) is a design judgment, not a sourced claim.
2. The Shopify retrospective is about *dependency-graph* central enforcement, not *documentation invariant* central authoring; the failure modes may not transfer directly.
3. No primary-source migration case study was found going the *opposite* direction (denormalized → centralized) within source constraints. Absence of evidence is not evidence of absence; further targeted search of academic architecture-conformance literature could be commissioned if OI-A2 needs symmetric coverage.

## Source list (bibliography)

**Terraform / HashiCorp (official):**
- HashiCorp Developer, "lifecycle meta-argument reference", 2025-11-19 — https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle
- HashiCorp Developer, "Validate your infrastructure in Terraform's configuration language", 2025-11-19 — https://docs.hashicorp.com/terraform/language/validate
- HashiCorp Developer, "Validate modules with custom conditions" tutorial — https://developer.hashicorp.com/terraform/tutorials/configuration-language/custom-conditions
- HashiCorp Developer, "resource block reference" — https://developer.hashicorp.com/terraform/language/block/resource
- HashiCorp web-unified-docs, "custom-conditions.mdx" — https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.11.x/docs/language/expressions/custom-conditions.mdx

**dbt (official):**
- dbt Developer Hub, "Define properties", 2026-05-21 — https://docs.getdbt.com/reference/define-properties
- dbt Developer Hub, "About data tests property", 2026-05-21 — https://docs.getdbt.com/reference/resource-properties/data-tests
- dbt Developer Hub, "About ref function", 2026-05-18 — https://docs.getdbt.com/reference/dbt-jinja-functions/ref
- dbt Developer Hub, "Should I use separate files to declare resource properties, or one large file?", 2026-05-18 — https://docs.getdbt.com/faqs/Project/multiple-resource-yml-files
- dbt Developer Hub, "Writing custom generic data tests", 2026-05-21 — https://docs.getdbt.com/best-practices/writing-custom-generic-tests

**dbt (engineering-guide; medium-confidence):**
- Semantic Stack, "dbt project best practices guide" — https://semanticstack.app/resources/dbt-best-practices/

**OpenAPI Initiative (official):**
- OpenAPI Specification v3.1.2, 2025-09-19 — https://spec.openapis.org/oas/v3.1.2
- OpenAPI Initiative learn portal, "Using References" — https://learn.openapis.org/referencing/

**OpenAPI (vendor engineering blogs, medium-confidence):**
- Bump.sh, "OpenAPI & AsyncAPI $ref: Advanced Guide" — https://bump.sh/blog/openapi-asyncapi-ref-usage-guide/
- Speakeasy, "Components in OpenAPI best practices" — https://github.com/speakeasy-api/developer-docs/blob/main/openapi/components.mdx
- BytePane, "OpenAPI & Swagger Guide", 2026-04-14 — https://bytepane.com/blog/openapi-swagger-guide/

**JSON Schema (official):**
- JSON Schema, "Modular JSON Schema combination" — https://json-schema.org/understanding-json-schema/structuring
- JSON Schema core spec — https://github.com/json-schema-org/json-schema-spec/blob/main/specs/jsonschema-core.md
- Ajv validator docs, "Combining schemas" — https://github.com/ajv-validator/ajv/blob/HEAD/docs/guide/combining-schemas.md

**ArchUnit (official) and ecosystem:**
- ArchUnit User Guide — https://www.archunit.org/userguide/html/000_Index.html
- ArchUnit Library API docs — https://github.com/TNG/ArchUnit/blob/9caf0466/docs/userguide/008_The_Library_API.adoc
- Netflix Nebula ArchRules plugin — https://github.com/nebula-plugins/nebula-archrules-plugin

**Bazel (official):**
- Bazel, "Visibility" concept — https://bazel.build/concepts/visibility
- Bazel, "Repositories, workspaces, packages, and targets" — https://bazel.build/versions/9.1.0/concepts/build-ref
- Bazel, "Functions" reference — https://bazel.build/versions/8.7.0/reference/be/functions

**Migration case study (first-party engineering blog):**
- Rails at Scale (Shopify), "A Packwerk Retrospective", 2024-01-26 — https://railsatscale.com/2024-01-26-a-packwerk-retrospective/
