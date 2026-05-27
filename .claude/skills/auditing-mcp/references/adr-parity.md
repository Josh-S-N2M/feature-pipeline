# OP-11 ADR Parity — Reference

## Purpose

`audit_op11_adr_parity.py` implements **OP-11**, which verifies that every server in
`.mcp.json` has a matching, non-deprecated row in ADR-0041's per-server invocation-form
table, and that the documented form matches the actual `.mcp.json` entry.

## Canonicalization and opaque-token algorithm

The comparison proceeds in two steps:

1. **Whitespace canonicalization.** All runs of whitespace in both strings are collapsed
   to a single space and leading/trailing whitespace is stripped. This makes indentation
   and line-wrapping differences invisible to the comparison.

2. **Opaque-token matching.** After canonicalization the strings are split into
   whitespace-separated tokens. Any token that fully matches `${...}` (an env-var
   placeholder, e.g. `${SERENA_VERSION}`, `${localEnv:TFE_TOKEN}`) is treated as an
   opaque token. Two opaque tokens compare equal regardless of the variable name they
   hold. This means the audit never needs to read the environment variables, satisfying
   NFR-7/NFR-8 (no credential access at audit time).

   Example: `.mcp.json` contains `serena start-mcp-server` and ADR-0041 documents
   ``serena start-mcp-server``. After stripping surrounding quotes and canonicalizing
   whitespace these compare as equal.

## Deprecated-row skip convention

ADR-0041 preserves historical rows for append-only audit-trail purposes (per ADR-0005).
A row whose **Form** cell contains the substring `[DEPRECATED INVOCATION FORM` is skipped
by OP-11. Such rows record superseded invocation forms or removed servers but do not
represent active `.mcp.json` entries.

Currently rows for the historical Serena invocation form, mcp-openapi-schema, and the
historical gitnexus row (removed 2026-05-27 per ADR-0066) carry this annotation. OP-11
therefore neither requires nor checks for these servers / superseded forms in `.mcp.json`.

When a server is removed from `.mcp.json`, annotate its ADR-0041 row with the marker to
prevent a spurious `absent-from-mcp-json` BLOCKER on the next OP-11 run.

## FR-6 diagnostic shape

When OP-11 exits 1 (at least one BLOCKER), it writes a structured plain-text diagnostic
to stderr containing the four FR-6 fields for each finding:

| Field | Content |
|---|---|
| Mechanism | `OP-11 .mcp.json ↔ ADR-0041 parity` |
| Artifact | Server name + finding field (`missing-in-adr-0041`, `absent-from-mcp-json`, or `invocation-form-mismatch`) |
| Rule violated | Human-readable description of the specific mismatch |
| Remedial hint | Whether to amend ADR-0041 or fix `.mcp.json` |

## Finding types

| Field value | Condition | Remediation |
|---|---|---|
| `missing-in-adr-0041` | Server in `.mcp.json` has no active ADR-0041 row | Add a row to ADR-0041's taxonomy table |
| `absent-from-mcp-json` | Active ADR-0041 row has no matching `.mcp.json` server | Add server to `.mcp.json`, or annotate ADR row as deprecated |
| `invocation-form-mismatch` | Forms don't match after canonicalize+opaque-token comparison | Align `.mcp.json` entry with ADR-0041 form, or amend ADR-0041 |

All finding severities are **BLOCKER**.
