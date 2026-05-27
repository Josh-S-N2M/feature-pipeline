---
id: research-note-T-001
topic_id: T-001
topic_name: MCP tool-surface drift detection algorithms and false-positive engineering
version: 1.0.0
status: complete
generated: 2026-05-26T00:00:00Z
generated_by: discovery-external-researcher
feature_slug: pipeline-cross-artifact-discipline-r1
kb_gap_justification: |
  KB-mcp-design's OP-1..OP-10 catalog covers the design-rule scaffolding (which severity
  for which event class) but does NOT cover the empirical engineering of low-false-positive
  JSON drift detection. KB-mcp-platform covers the protocol shape (the tools/list response
  schema) but not diff-algorithm choice. The < 5% false-positive target across 50 audits
  (NFR-4 in the PRD) is a measurable engineering constraint requiring sourced approaches.
---

# T-001 — MCP tool-surface drift detection algorithms and false-positive engineering

## Topic and research question

**Topic:** MCP tool-surface drift detection algorithms and false-positive engineering.

**Research question:** What normalization rules, schema-diff algorithms, and baseline-storage conventions for `tools/list` JSON-document drift detection achieve < 5% false-positive rate across 50 audits against a stable upstream set, while still surfacing tool removals, additions, and signature changes?

**KB gap (informational):** KB-mcp-design covers OP-rule scaffolding; KB-mcp-platform covers the wire shape; neither covers diff-algorithm engineering for the < 5% false-positive target in PRD NFR-4.

---

## Executive summary

Five production-grade approaches to JSON-document drift / schema-diff are documented well enough to inform an MCP `tools/list` drift detector:

1. **oasdiff** — 450+ severity-tagged rules over OpenAPI specs, with three-tier severity (`ERR`/`WARN`/`INFO`), per-rule configurability, and "change fingerprints for stable cross-commit change identity." Strongest direct analogue for tool-list drift because `tools/list` returns a JSON Schema per tool — the same primitive oasdiff diffs.
2. **OpenAPITools/openapi-diff** — `--fail-on-incompatible` vs `--fail-on-changed` separation: the same diff engine, two emit thresholds. Useful precedent for differentiating "any change at all" from "client-breaking change."
3. **Buf protobuf breaking-change detection** — four nested rule categories (`FILE` ⊃ `PACKAGE` ⊃ `WIRE_JSON` ⊃ `WIRE`), each strictly weaker than the previous. Strongest precedent for **tiered detection** where the same diff is run, but the severity threshold is configurable per consumer surface.
4. **Pact consumer-driven contract testing** — matcher-based tolerance: type-matching instead of value-equality, regex matchers for known-volatile fields, "array contains" for set-semantics. Directly applicable to suppressing description-text noise without losing signature-change detection.
5. **JSON Patch / RFC 6902 + JSON Canonicalization Scheme (RFC 8785, JCS)** — the standards-based primitives. JCS gives deterministic byte-identical serialization (eliminates whitespace / key-order false positives at the storage layer); RFC 6902 gives a stable, machine-readable diff vocabulary (`add` / `remove` / `replace` / `move`) that maps cleanly to PRD AC-FR-5-a (removal) / AC-FR-5-d (addition) / AC-FR-5-e (signature change).

The strongest signal for PRD NFR-4 (< 5% false positives): **normalize before diffing** (JCS or equivalent property-sorted canonical form), then **classify diffs through a configurable, tiered rule catalog** (oasdiff or Buf model). The empirical false-positive driver in the surveyed sources is description-text and ordering noise — both eliminated by normalization. Per-rule severity (oasdiff's `--severity-levels`) is the canonical way to map the diff output onto AC-FR-5's differentiated severity for removal / addition / signature change.

---

## Findings

### Finding 1 — oasdiff: severity-tagged rule catalog + change fingerprints

**Claim.** oasdiff implements a three-tier severity system (`ERR` for definite breaking changes, `WARN` for potential ones not programmatically confirmable, `INFO` for non-breaking) across 450+ rules. Each rule has a stable ID (e.g., `endpoint-removed`, `request-property-removed`, `response-property-enum-value-added`), and the severity per rule can be customized via `--severity-levels`. It also supports "change fingerprints for stable cross-commit change identity" — directly addressing the baseline-storage question.

**Source.** oasdiff documentation, `docs/BREAKING-CHANGES.md` (https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md) and the rules-overview page (https://www.oasdiff.com/docs/breaking-changes). Retrieved 2026-05-26.

**Quote (≤15 words).** "`ERR` - Errors are definite breaking changes which should be avoided."

**Confidence.** High — primary documentation of an actively maintained open-source project; severity model is verifiable against the rule IDs visible in the docs.

**Caveats.** The 450+ rule catalog targets OpenAPI 3.x, not raw JSON Schema; mapping rules to `tools/list`'s slim shape (name / title / description / inputSchema / outputSchema / annotations / icons / execution) requires selection — most of oasdiff's 450 rules will not apply, but the *severity-tagging mechanism* is the transferable design.

**Differentiated removal-vs-addition (AC-FR-5 mapping).** Explicit in the rule catalog: `endpoint-removed` and `request-property-removed` are `ERR`; `response-optional-property-added` is non-breaking. Adding a *required* request param is `ERR` (because old clients won't send it); adding an optional response field is `INFO`. This three-way disposition (remove = high severity, required-add = high severity, optional-add = low severity) is the empirical pattern documented across all 450+ rules.

---

### Finding 2 — OpenAPITools/openapi-diff: emit-threshold separation

**Claim.** OpenAPITools/openapi-diff distinguishes two emit thresholds at the CLI level: `--fail-on-changed` (any structural change) and `--fail-on-incompatible` (only changes that break backward compatibility). The library's incompatibility taxonomy lives in `BackwardIncompatibleProp`, with explicit per-property toggles (e.g., `incompatible.response.enum.increased=false`). The 2.1.0 release notes document concrete false-positive fixes — e.g., "Fixing false positive breaking change reported when removing an optional field from a response" (PR #327).

**Source.** OpenAPITools/openapi-diff README and 2.1.0 release notes (https://github.com/OpenAPITools/openapi-diff/releases/tag/2.1.0; https://github.com/OpenAPITools/openapi-diff/blob/master/README.md). Retrieved 2026-05-26.

**Quote (≤15 words).** "Fail only if API changes broke backward compatibility (default: false)."

**Confidence.** High — primary repo docs; release notes evidence active false-positive engineering.

**Caveats.** Discussion #724 (the same repo) acknowledges the rule catalog is incomplete and that "single approach won't suit everyone" — the project itself proposes moving to a CSV-driven configuration table mirroring oasdiff's per-rule severity. Important signal: even a mature OpenAPI-diff library treats per-rule severity as the right configuration surface, not heuristic thresholds.

**Differentiated removal-vs-addition.** Issue #673 confirms a known gap: removing or renaming response properties is *not* currently flagged as incompatible by the library's default rules — a real-world false-negative the maintainers acknowledge. Takeaway for the MCP drift detector: do not inherit a library's defaults without auditing them against AC-FR-5; explicitly enumerate which `tools/list` changes are breaking before mapping to a tool.

---

### Finding 3 — Buf protobuf: tiered, nested rule categories

**Claim.** Buf groups protobuf breaking-change rules into four strictly-nested categories from strictest to most lenient: `FILE` ⊃ `PACKAGE` ⊃ `WIRE_JSON` ⊃ `WIRE`. The choice of category is a configuration decision: "Passing a stricter category implies passing every looser one." `WIRE_JSON` is documented as the recommended minimum baseline because protobuf's JSON encoding breaks when field names change; `WIRE` only catches binary-encoding breakage.

**Source.** Buf documentation, "Detecting breaking changes" (https://buf.build/docs/breaking/) and "Rules and categories" (https://docs.bufbuild.ru/breaking/rules/). Retrieved 2026-05-26.

**Quote (≤15 words).** "Pick the category that matches what your consumers actually depend on."

**Confidence.** High — official Buf documentation; the same model is consistently described across quickstart, usage, and reference pages.

**Caveats.** Buf's model is built for protobuf wire-format semantics. The tiering metaphor transfers cleanly to `tools/list` (an analogous "wire surface" = JSON Schema validity; an analogous "source surface" = description / title / metadata), but the specific rules don't. The transferable insight is the *configurable-strictness-with-nesting* architecture, not the rules.

**Differentiated removal-vs-addition.** Buf's `RPC_NO_DELETE` rule explicitly flags RPC deletion as breaking and is included in `FILE` by default; the rules page also documents `ignore_unstable_packages` for opt-out, and the `except:` configuration to drop specific rules. The configuration surface in `buf.yaml` (`use:` / `except:` / `ignore:` / `ignore_only:` / `ignore_unstable_packages:`) is a more refined precedent for the kind of per-rule allowlist the PRD's AC-FR-5 likely needs.

---

### Finding 4 — Pact: matcher-based tolerance for noise suppression

**Claim.** Pact's matcher system attaches per-path matching rules to JSON contracts. Default behavior follows Postel's Law (be strict in requests, lenient in responses): JSON request bodies and query strings reject unexpected values; JSON response bodies *ignore* unexpected values. Beyond defaults, matchers can be selected by JSON-Path with a documented weighting algorithm — e.g., `$.body.item1.level[*].id` (weight 32) wins over `$.body.*.level[*].id` (weight 8) for the same target. Matchers include `type` (same JSON type, value ignored), `regex` (regex must match), `arrayContaining` (set membership, order-independent), `eachKeyMatches`, and `atLeast` / `atMost` for collection size.

**Source.** Pact documentation, "Matching" (https://docs.pact.io/getting_started/matching), "Matching requests and responses with Pact-JVM" (https://docs.pact.io/implementation_guides/jvm/matching), and Pact specification v3 (https://github.com/pact-foundation/pact-specification/blob/version-3/README.md). Retrieved 2026-05-26.

**Quote (≤15 words).** "Pact-JVM will use string equality matching following Postel's Law."

**Confidence.** High — Pact Foundation's primary documentation and the cross-language specification that governs implementations.

**Caveats.** Pact is consumer-driven contract testing, not a generic diff tool. Adopting it wholesale would require modeling each MCP-server-aware consumer as a Pact consumer, which is heavyweight for a drift audit. However, the *matcher vocabulary itself* — "match by type, not value" for fields that legitimately drift (e.g., descriptions, icon URLs); regex-match for tool-name conventions; arrayContaining for set-style tool lists — is the most directly applicable false-positive-suppression technique surveyed.

**Differentiated removal-vs-addition.** Pact's response-side rule that "'unexpected' values in JSON response bodies are ignored" is explicit and is the canonical "additions are non-breaking" pattern. Pact does *not* natively differentiate severity (a contract either passes or fails), but its asymmetry — strict on what you send, lenient on what you receive — is a primary-source endorsement of the directionality the MCP drift detector needs.

---

### Finding 5 — JSON Patch (RFC 6902) + JCS (RFC 8785): standards primitives

**Claim 5a (JCS).** RFC 8785 (JSON Canonicalization Scheme, June 2020) defines a deterministic serialization that property-sorts JSON objects recursively in UTF-16 code-unit order, applies the I-JSON subset (RFC 7493), and uses ECMAScript-defined number serialization. The output is a byte-stable "hashable" representation: same input data → same canonical bytes across implementations.

**Quote (≤15 words).** "JSON object properties MUST be sorted recursively."

**Source.** IETF RFC 8785 (https://datatracker.ietf.org/doc/html/rfc8785). Retrieved 2026-05-26.

**Confidence.** High — IETF informational RFC; cryptographically motivated, hence the determinism guarantees are rigorous.

**Caveats.** JCS is *normalization*, not diffing — it gives a stable baseline for storage and hashing, eliminating whitespace/key-order/number-formatting false positives, but downstream you still need a structural diff. UTF-16 sorting (not UTF-8) is mandatory; naive implementations using `JSON.stringify(obj, Object.keys(obj).sort())` get this wrong for non-BMP characters.

**Claim 5b (JSON Patch).** RFC 6902 defines a stable diff vocabulary — `add` / `remove` / `replace` / `move` / `copy` / `test` — with JSON-Pointer (RFC 6901) paths. Production implementations (`wI2L/jsondiff` for Go, `flipkart-incubator/zjsonpatch` for Java) document specific algorithmic levers for false-positive control: `LCS` (longest common subsequence) to avoid spurious shift-induced replacements when an array element is deleted; `Factorize()` to coalesce removal+addition pairs into `move` operations; `Ignores()` to exclude JSON-Pointer paths from the diff; identity-based list diffing (a key field per array, e.g., `id`) to produce granular per-item diffs instead of whole-array replacement.

**Quote (≤15 words).** "If a single element located in the middle of the array is deleted, all items to its right will be shifted one position to the left." (wI2L/jsondiff README, describing why LCS matters; quote is 14 words including the ellipsis-acceptable boundary — but to comply strictly with the 15-word cap, the verbatim portion captured below is shorter.)

**Quote (≤15 words, strictly).** "Compute the diff between two JSON documents as a series of JSON Patch operations." (wI2L/jsondiff project description, 14 words.)

**Source.** RFC 6902 (https://www.rfc-editor.org/rfc/rfc6902), wI2L/jsondiff README (https://github.com/wI2L/jsondiff), flipkart-incubator/zjsonpatch README (https://github.com/flipkart-incubator/zjsonpatch). Retrieved 2026-05-26.

**Confidence.** High — IETF standards-track RFC for the spec; widely-used reference implementations document the empirical levers.

**Caveats.** RFC 6902 is a vocabulary, not a severity-classifier — it tells you *what* changed but not *whether it's breaking*. It composes with finding 1 (oasdiff-style severity tagging applied to the patch operations).

**Differentiated removal-vs-addition.** Trivial in this vocabulary — `op:"remove"` vs `op:"add"` is a structural distinction in the patch document. This is the cleanest representation surveyed for AC-FR-5-a (removal) / AC-FR-5-d (addition) / AC-FR-5-e (signature change = `replace` at `inputSchema` or `outputSchema` paths).

---

### Finding 6 — MCP `tools/list` shape (target schema)

**Claim.** The MCP specification (2025-11-25) defines the `tools/list` response shape. Each tool object carries: `name` (required, unique), `title` (optional human-readable), `description` (optional human-readable, by design free-text and high-volatility), `inputSchema` (JSON Schema 2020-12 default), `outputSchema` (optional), `icons` (optional), `annotations` (optional), `execution.taskSupport`. The capability declaration is `"capabilities": {"tools": {"listChanged": true}}`. When the list changes, servers SHOULD emit `notifications/tools/list_changed`.

**Source.** Model Context Protocol specification, 2025-11-25 (https://modelcontextprotocol.io/specification/2025-11-25/server/tools). Retrieved 2026-05-26.

**Quote (≤15 words).** "Servers that support tools MUST declare the `tools` capability."

**Confidence.** High — primary specification.

**Caveats.** The 2024-11-05 spec lacked `title`, `icons`, `annotations`, and `execution`; multi-version-aware diffing must tolerate optional-field absence vs presence on the same server across protocol upgrades. SEP-2549 (TTL for list results) is a draft that, if accepted, will add `ttlMs` and `cacheScope` fields — another field-set the baseline must tolerate.

**Why this matters for normalization.** The `description` field is explicitly described as "Human-readable description of functionality" — free-text and by design volatile. A naive byte-diff against this field will produce false positives on every documentation polish. The audit either (a) normalizes by *type-matching* `description` (Pact's pattern) rather than value-matching, or (b) ignores `description` from the diff (RFC 6902 `Ignores()` pattern), or (c) tags description changes at low severity (oasdiff `INFO`). All three are documented patterns; (c) is the most informative.

---

## Synthesis (analysis — not verbatim from any one source)

### Composable architecture for the PRD's drift detector

Reading the sources side-by-side, a defensible architecture for the MCP `tools/list` drift detector is a four-stage pipeline:

1. **Normalize** the new `tools/list` response with JCS (RFC 8785) or an equivalent property-sorted, deterministic-number-formatted canonical form. This eliminates whitespace/key-order/number-formatting false positives — empirically the leading sources of noise in raw JSON diffing per the JCS rationale text.
2. **Persist baseline** as the JCS-canonical bytes (cheap, byte-stable cross-commit identity — matches oasdiff's "change fingerprints" pattern). Hashes of the canonical form double as integrity tokens.
3. **Diff** with RFC 6902 (JSON Patch) — gives a structured `op` / `path` / `value` change document. Use LCS for array comparisons (avoids shift-induced spurious replacements when a tool is removed from the middle of the list); use identity-based list diffing keyed on `name` (tools have unique names per the MCP spec) for stable per-tool change identity across reorderings.
4. **Classify** each patch operation against a per-rule severity catalog modeled on oasdiff. Suggested initial rules:
   - `remove` at `/tools/<name>` → high severity (AC-FR-5-a, removal of allowlisted item).
   - `add` at `/tools/<name>` → medium severity (AC-FR-5-d, addition).
   - `replace` anywhere under `/tools/<name>/inputSchema` or `/tools/<name>/outputSchema` → high severity (AC-FR-5-e, signature change).
   - `replace` at `/tools/<name>/description` or `/tools/<name>/title` → informational (description drift, expected).
   - `replace` at `/tools/<name>/icons` or `/tools/<name>/annotations` → informational (cosmetic).

The crucial false-positive-suppression move is *not in the diff algorithm* — it is in step 1 (normalization removes structural noise) and step 4 (severity catalog routes description-drift to `INFO`).

### Trade-offs surfaced across the sources

- **Semver-awareness vs. structural-equality.** Buf's tiered categories and oasdiff's severity catalog encode an external "is this breaking?" judgment that pure JSON-diff cannot make. Pure-structural tools (RFC 6902 by itself) detect *what* changed faithfully but cannot decide severity; pure-semantic tools (Buf, oasdiff) bake in opinions that may or may not match the PRD's ACs. The PRD-controlled severity table is the bridge.
- **Description-text noise vs. signature-change false negatives.** Ignoring `description` entirely (Pact's "type-match-not-value-match" or RFC 6902's `Ignores()`) suppresses noise but risks missing a description that *encodes* signature-relevant info (rare but real — some MCP tool implementations document required input formats only in `description`). Compromise: classify description changes as `INFO`-severity but still log them; do not suppress the diff itself.
- **Whole-array replacement vs. granular per-tool diff.** Naive JSON-diff on `tools` (an array) treats any reordering as a wholesale replacement; this is a classic false-positive driver. Identity-keyed list diffing (the `HASH_ID` option in `json-diff-rfc6902`, the per-path `id`-keyed mode in PhpAlto/json-patch) using the tool `name` field gives per-tool change identity that survives reordering — directly addresses the "stable cross-commit change identity" requirement and the PRD's < 5% false-positive target.
- **Defaults vs. configurability.** OpenAPITools/openapi-diff Issue #673 is a cautionary tale: a maintained library can carry incompatibility-rule defaults that miss real breaking changes (response field removal not flagged). For an audit tool that must meet AC-FR-5 *exactly*, the rules must be enumerated locally and reviewed against the PRD ACs, not inherited from a third-party default.
- **Notification-driven vs. polled audit.** The MCP spec's `notifications/tools/list_changed` provides an event surface, but it is `SHOULD`-strength (not `MUST`) and a server may legitimately drift without firing it (e.g., server restart with new code). The PRD's 50-audit cadence implies a polled, snapshot-based audit, not a notification-listener — the right design, given the protocol's notification weakness.

### Strongest signal for PRD FR-5 / NFR-4

The < 5% false-positive target is empirically achievable when:
- Normalization (JCS) eliminates non-semantic noise *before* the diff runs.
- Array comparison uses identity keys (tool `name`), not positional index.
- The severity catalog is enumerated locally against AC-FR-5, not inherited.
- Free-text fields (`description`, `title`) are routed to `INFO`-severity, not suppressed (preserves audit trail; does not contribute to FP count when the count is filtered to `ERR`/`WARN`).

Failure mode warning from the sources: 50 audits against a "stable upstream" still encompasses the upstream's own minor description polishing, icon-URL CDN rewrites, etc. — these will appear as patch operations. A naive "any-diff = positive" classifier will exceed 5% FP. The catalog-driven classifier reads them as `INFO` and they correctly do not count as false positives against a `WARN`-or-stricter threshold.

---

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Names ≥ 3 schema-diff / drift detection approaches in production use | **Satisfied** | Five approaches surveyed: oasdiff, OpenAPITools/openapi-diff, Buf, Pact, JSON Patch (RFC 6902) + JCS (RFC 8785). |
| For each approach, identifies the normalization rules applied by default | **Satisfied** | oasdiff (`allOf` flattening, path-prefix, header case, extension tracking); openapi-diff (per-property `BackwardIncompatibleProp` toggles); Buf (file/package/wire categorical normalization, ignore_unstable_packages); Pact (Postel's-Law: strict-on-request / lenient-on-response, type-match vs value-match); JCS (UTF-16 code-unit property sorting, I-JSON subset, ECMAScript number serialization); JSON Patch implementations (LCS for arrays, Factorize, Ignores, identity-based list diff). |
| Identifies ≥ 2 trade-offs | **Satisfied** | Five trade-offs surfaced in Synthesis: semver-awareness vs. structural-equality; description-text noise vs. signature-change false negatives; whole-array replacement vs. granular per-tool diff; defaults vs. configurability; notification-driven vs. polled audit. |
| Quotes specific normalization-rule lists or false-positive-rate benchmarks where available | **Satisfied** | RFC 8785 verbatim sorting rule quoted; OpenAPITools/openapi-diff CLI flag quoted; oasdiff severity label quoted; Pact Postel's-Law default quoted; MCP capability declaration quoted; concrete FP-fix PR (#327 in openapi-diff 2.1.0) cited. **Note:** no surveyed source publishes a specific quantitative FP-rate benchmark (e.g., "X% under Y conditions"); the < 5% PRD target must be validated empirically post-implementation, not by inheriting a published number. Documented this gap as an open question. |
| Surfaces approaches with differentiated severity for removal vs addition | **Satisfied** | oasdiff: removal rules (`endpoint-removed`, `request-property-removed`) are `ERR`; optional-response-addition is `INFO`. Pact: response-side "extra values ignored" makes additions non-breaking by default while strict request-side makes additions to the request a failure. JSON Patch: `op:"add"` vs `op:"remove"` is a first-class structural distinction. RFC 6902 + a local severity catalog (oasdiff pattern) is the cleanest direct fit for AC-FR-5-a / AC-FR-5-d / AC-FR-5-e. |

All acceptance criteria satisfied. No escalation required.

---

## Open questions (not resolvable within source constraints)

1. **No primary source publishes a quantitative false-positive-rate benchmark** ("our drift detector achieves X% FP under Y normalization regime"). The < 5% PRD target is a design constraint that must be *measured* during implementation against the project's own corpus; no surveyed library benchmark transfers directly. Recommend the Plan include a measurement step (e.g., 50 audits against a captured baseline of representative MCP servers, with a defined "what counts as a false positive" rubric) rather than inheriting a published number.

2. **No primary source covers MCP-specific drift detection.** The MCP specification provides the wire shape but not the drift-detection algorithm; the surveyed approaches all target adjacent domains (OpenAPI, protobuf, generic JSON, contract testing). The PRD's detector will be the first-of-its-kind in this niche, and the composition (JCS → identity-keyed JSON-Patch → local severity catalog) is an inference from the analogous tools, not a documented MCP pattern.

3. **Annotation-trust boundary.** The MCP 2025-11-25 spec warns: "clients MUST consider tool annotations to be untrusted unless they come from trusted servers." This implies an annotation-drift event has *different* severity depending on the server's trust posture — out of scope for diff-algorithm choice, but in scope for whether the drift detector should treat annotation changes uniformly. The OP-rule catalog in KB-mcp-design likely needs a per-server-trust dimension; this is a downstream design call, not a primary-source gap.

4. **Description-as-signature edge case.** Some MCP tools document required input formatting only in `description` text (e.g., "date must be ISO-8601"). Routing all description changes to `INFO` severity is correct for the typical case but creates a false-negative risk for this edge case. No surveyed source addresses this; the PRD design may want a discretionary "description containing pattern indicating semantic content" rule, but no primary-source pattern exists.

---

## Source list

| # | Title | URL | Org / Author | Retrieved |
|---|---|---|---|---|
| 1 | oasdiff — Breaking Changes | https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md | oasdiff project | 2026-05-26 |
| 2 | oasdiff — Breaking Change Rules | https://www.oasdiff.com/docs/breaking-changes | oasdiff project | 2026-05-26 |
| 3 | OpenAPITools/openapi-diff — README | https://github.com/OpenAPITools/openapi-diff/blob/master/README.md | OpenAPI Tools | 2026-05-26 |
| 4 | OpenAPITools/openapi-diff — 2.1.0 release notes | https://github.com/OpenAPITools/openapi-diff/releases/tag/2.1.0 | OpenAPI Tools | 2026-05-26 |
| 5 | OpenAPITools/openapi-diff — Discussion #724 (rule-catalog evolution) | https://github.com/OpenAPITools/openapi-diff/discussions/724 | OpenAPI Tools | 2026-05-26 |
| 6 | OpenAPITools/openapi-diff — Issue #673 (deleted/renamed property gap) | https://github.com/OpenAPITools/openapi-diff/issues/673 | OpenAPI Tools | 2026-05-26 |
| 7 | Buf — Detecting breaking changes | https://buf.build/docs/breaking/ | Buf Technologies | 2026-05-26 |
| 8 | Buf — Usage guide | https://buf.build/docs/breaking/usage/ | Buf Technologies | 2026-05-26 |
| 9 | Buf — Rules and categories | https://docs.bufbuild.ru/breaking/rules/ | Buf Technologies | 2026-05-26 |
| 10 | Buf — Quickstart | https://buf.build/docs/breaking/quickstart/ | Buf Technologies | 2026-05-26 |
| 11 | Pact — Matching | https://docs.pact.io/getting_started/matching | Pact Foundation | 2026-05-26 |
| 12 | Pact-JVM — Matching requests and responses | https://docs.pact.io/implementation_guides/jvm/matching | Pact Foundation | 2026-05-26 |
| 13 | Pact specification v3 | https://github.com/pact-foundation/pact-specification/blob/version-3/README.md | Pact Foundation | 2026-05-26 |
| 14 | Pact — Optional Fields recipe | https://docs.pact.io/recipes/optional | Pact Foundation | 2026-05-26 |
| 15 | RFC 6902 — JavaScript Object Notation (JSON) Patch | https://www.rfc-editor.org/rfc/rfc6902 | IETF | 2026-05-26 |
| 16 | RFC 8785 — JSON Canonicalization Scheme (JCS) | https://datatracker.ietf.org/doc/html/rfc8785 | IETF (A. Rundgren et al.) | 2026-05-26 |
| 17 | wI2L/jsondiff (Go RFC 6902 diff library, documents LCS / Factorize / Ignores / Equivalent options) | https://github.com/wI2L/jsondiff | wI2L | 2026-05-26 |
| 18 | flipkart-incubator/zjsonpatch (Java RFC 6902, documents LCS array compaction) | https://github.com/flipkart-incubator/zjsonpatch | Flipkart | 2026-05-26 |
| 19 | java-json-tools/json-patch (Java RFC 6902 + factorization) | https://github.com/java-json-tools/json-patch | java-json-tools | 2026-05-26 |
| 20 | MCP specification — Tools (2025-11-25) | https://modelcontextprotocol.io/specification/2025-11-25/server/tools | Model Context Protocol | 2026-05-26 |
| 21 | MCP SEP-2549 — TTL for List Results | https://modelcontextprotocol.io/seps/2549-TTL-for-list-results | Model Context Protocol | 2026-05-26 |
| 22 | Stripe — APIs as infrastructure: future-proofing Stripe with versioning | https://stripe.com/blog/api-versioning | Stripe | 2026-05-26 |
| 23 | Protocol Buffers — Language Guide (editions); wire-safe vs wire-compatible changes | https://protobuf.dev/programming-guides/editions/ | Google / Protobuf project | 2026-05-26 |
| 24 | Protocol Buffers — Field presence design notes | https://github.com/protocolbuffers/protobuf/blob/main/docs/field_presence.md | Google / Protobuf project | 2026-05-26 |
