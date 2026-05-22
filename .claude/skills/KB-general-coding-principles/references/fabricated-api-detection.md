# Detecting Fabricated APIs (Dimension 4)

## Contents

- The three failure shapes
- Verification protocol
- What counts as "fabricated"
- Common false-positives to avoid
- Time budget

The dimension-4 check: every external call in a design sample references a real method on a real library at a real signature.

This document gives the protocol for verifying. Per-layer designers run this before emitting; `shared-document-reviewer` runs it during Gate 1 dependency-realizability check.

## The three failure shapes

1. **The hallucinated method** — library is real and well-known, method does not exist. Most common AI-authoring failure mode.
2. **The wrong-library method** — method exists in library X but the sample puts it on library Y (cross-contamination from training data).
3. **The deprecated-removed method** — method existed in some past version but was removed; current docs do not mention it.

## Verification protocol

For each external call in the sample:

### Step 1: Identify the library and version

Source the version from the project, in this order:

1. `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, etc. — the dependency manifest under review
2. Codebase analysis JSON (Discovery Research output) — `dependencies.<lib>.version` if discovered
3. Project's CLAUDE.md if it pins versions
4. If genuinely undetermined → mark the sample as stack-unknown (see `stack-unknown.md`)

### Step 2: Check against authoritative source

Priority order:

1. **Context7 MCP** if available — `Context7:resolve-library-id` then `Context7:query-docs`. Fast, structured, current.
2. **WebFetch on the library's official docs** — `docs.<lib>.com`, GitHub README, or whatever the canonical source is for that library. Pin the URL to the version where possible.
3. **GitHub source tree** — `https://github.com/<org>/<lib>/blob/v<version>/...` to look at the actual exported surface
4. **WebSearch** as last resort if the above don't resolve

Do NOT trust the sample as-is just because it "looks right." The whole point of the check is that wrong-but-plausible is the failure mode.

### Step 3: Verify the exact signature

It's not enough that a method with the same name exists. Verify:

- **Argument names and order** — `requests.post(url, data, json)` is different from `requests.post(url, json, data)`
- **Argument types** — Python kwargs allow flexibility, but typed languages don't
- **Return type** — sample's downstream usage assumes a return shape; check it matches
- **Whether it's a method or function** — `pandas.DataFrame.merge(...)` vs `pandas.merge(df, ...)` are different APIs

### Step 4: Record the verification

In the document, the verification appears as a code-inspection-evidence entry (per Blueprint template's "Code Inspection Evidence" table) when the call is to existing code. For external libraries, the reference is to the docs URL or version-pinned source.

## What counts as "fabricated"

| Pattern | Verdict |
|---|---|
| Method does not exist in any version of the library | Fabricated — auto-fail |
| Method exists in a different library with the same name | Fabricated (cross-contaminated) — auto-fail |
| Method existed in v1.x, removed in v2.x, project is on v3 | Fabricated for this project — score 4 or below |
| Method exists but signature in sample is wrong | Not fabricated, but dimension 4 score 4–6; surface as `important` issue |
| Method exists, signature is correct, but deprecated with replacement | Score 7–9; recommend migration |
| Method exists, signature correct, current | Score 10 |

## Common false-positives to avoid

- **Builder/fluent chains** — `query.where(...).order_by(...).limit(...)` chains can chain methods that exist individually. Verify each, but don't reject the chain just because you can't find a single `where_order_by_limit` method.
- **Type-parameterized methods** — generic methods may not appear with the exact type parameter from the sample; check the underlying generic exists.
- **Re-exports** — many libraries re-export from sub-modules. `import { thing } from 'lib'` may be a re-export of `lib/internal/thing.ts`. Verify the re-export path.

## Time budget

This check is per-call, not per-sample. A sample with 3 external calls takes 3 verifications. Budget ~30 seconds per call when Context7 is available, ~2 minutes when WebFetch is the only option. If the total verification cost would exceed the document review's time budget, prioritize calls that:

1. Mutate state (writes, deletes, network calls)
2. Are load-bearing for the design's claimed behavior
3. Appear in multiple samples (one failure invalidates several illustrations)
